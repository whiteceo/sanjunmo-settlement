<?php
/**
 * 8단계 PAYEE_SPLIT — 수취인 분할(V2 §8.3 표 L175 · 본문 L245~259, V1 §4.1~4.3, V2 13.2~13.4, SPEC 11절).
 *
 * 신규분: 라인별 내림(세전액 × split_ratio), 마지막 수취인(split_ratio↓ · payee_id↑) 총액 역산.
 * 원거래 귀속 공제분: 원 결제 시점 분할 비율(snapshot_payee_splits)로 같은 규칙 — 재분할 금지.
 * 비분할: 선급금 상계액(원 권리자) · 이월액(원장 수취인) · P2.2(위탁자 단독 패스스루).
 * 당월 세전 지급액 = 분할액 − 상계액, 과세표준 = 분할액(LOAN · 없음) / 분할액 − 상계액(EARNED), 음수는 보류.
 */

namespace SettleCalc;

use BcMath\Number;

final class S08PayeeSplit
{
    const STEP = 'PAYEE_SPLIT';

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            self::splitContract($ctx, $c);
        }
    }

    private static function splitsFor(Context $ctx, ContractState $c): array
    {
        $date = month_last($ctx->month);
        $rows = array_values(array_filter($ctx->input['payee_splits'], fn($s) => $s['contract_id'] === $c->id
            && g($s, 'rights_holder_id', $c->holder_id) === $c->holder_id && valid_on($s, $date, $c->row)));
        if (!$rows) {
            return [[['payee_id' => $c->holder_id, 'split_ratio' => D(100)]], true];
        }
        return [array_map(fn($s) => ['payee_id' => $s['payee_id'], 'split_ratio' => D($s['split_ratio'])], $rows), false];
    }

    /** @return array{0: array<int, array{0: mixed, 1: Number}>, 1: array} [[payee, 금액] 목록, 정렬된 분할] */
    private static function splitAmount(Number $amount, array $splits): array
    {
        $order = sort_by($splits, fn($s) => [neg(D($s['split_ratio'])), $s['payee_id']]);
        $out = [];
        $acc = D(0);
        $n = count($order);
        foreach ($order as $i => $s) {
            if ($i < $n - 1) {
                $v = floor_won(div(mul($amount, D($s['split_ratio'])), 100));
                $acc = add($acc, $v);
            } else {
                $v = sub($amount, $acc);
            }
            $out = self::put($out, $s['payee_id'], $v, true);
        }
        return [$out, $order];
    }

    /** 순서 있는 payee → 금액 목록(파이썬 OrderedDict). replace=true면 덮어쓰기, 아니면 더하기. */
    private static function put(array $pairs, $pid, Number $v, bool $replace = false): array
    {
        foreach ($pairs as $i => [$p, $a]) {
            if ($p === $pid) {
                $pairs[$i][1] = $replace ? $v : add($a, $v);
                return $pairs;
            }
        }
        $pairs[] = [$pid, $v];
        return $pairs;
    }

    public static function splitContract(Context $ctx, ContractState $c): void
    {
        $c->payees = [];
        $out = &$c->stepOut(self::STEP);
        [$splits, $default] = self::splitsFor($ctx, $c);
        $c->splits = $splits;
        $out['splits_used'] = $splits;
        $ctx->emit(self::STEP, 'splits_used', implode(', ', array_map(fn($s) => pystr($s['payee_id']) . ':' . pystr($s['split_ratio']),
            $splits)), $c, inputs: ['default' => $default],
            formula: '유효 payee_splits(없으면 권리자 단독 100%)', ref: 'V2 §8.3 8단계 L258');
        $lump = dsum(array_map(fn($l) => $l->net, $c->linesOf('LUMPSUM')));
        $base = add(dsum(array_map(fn($l) => $l->net, array_filter($c->lines,
            fn($l) => in_array($l->pipeline_id, ['1.1', '2.1', '5.1'], true)))), $lump);
        $out['payee_split_base'] = $ctx->emit(self::STEP, 'payee_split_base', $base, $c,
            inputs: ['Σnet_1_1 + Σnet_2_1 + Σconfirmed(5.1)' => sub($base, $lump), 'lumpsum_total' => $lump],
            formula: '수취인 분할 기준액 = P1.1 순액 + P2.1 순액 + P5.1 확정액 + 7단계 비정기 가산금(상계 · 이월 · 반환 · P2.2 제외, 표시용)',
            code: 'payee_split_base = Σnet_1_1 + Σnet_2_1 + Σconfirmed_amount + lumpsum_total', ref: 'V2 §8.3 8단계 L247');
        unset($out);
        $prepay = $c->prepay ?? [];
        $offsetPayee = g($prepay, 'payee');
        $ptype = g($prepay, 'type');
        $c->payee($c->holder_id);
        foreach ($splits as $s) {
            $c->payee($s['payee_id']);
        }
        foreach ($c->lines as $ln) {
            if ($ln->pipeline_id === '2.2') {
                self::consignmentLine($ctx, $c, $ln);
                continue;
            }
            if (!in_array($ln->pipeline_id, ['1.1', '2.1', '5.1', 'LUMPSUM'], true)) {
                continue;
            }
            $pieces = []; // [payee, 분할액]
            if ($ln->pipeline_id === '1.1') {
                $newAmt = $ln->adjusted !== null ? $ln->adjusted : $ln->new;
            } elseif ($ln->pipeline_id === '5.1') {
                $newAmt = $ln->new_confirmed ?? $ln->new;
            } else {
                $newAmt = $ln->pipeline_id === '2.1' ? $ln->new : $ln->net;
            }
            if (truthy($ln->fixed_payee)) {
                $parts = [[$ln->fixed_payee, $newAmt]];
                $ctx->issue('CANON_GAP', $ln->label . ' 약정 · 승인 원장 수취인 ' . pystr($ln->fixed_payee) . ' 단독 귀속', self::STEP,
                    $c->holder_id, 'V1 L288 · L234 · V2 L247', 'Q-15');
            } else {
                [$parts, $_] = self::splitAmount($newAmt, $splits);
            }
            foreach ($parts as [$pid, $a]) {
                $pieces = self::put($pieces, $pid, $a);
                $sr = null;
                foreach ($splits as $s) {
                    if ($s['payee_id'] === $pid) {
                        $sr = $s['split_ratio'];
                        break;
                    }
                }
                $ctx->emit(self::STEP, 'split_new', $a, $c, payee: $pid, line: $ln->label, line_key: $ln->key(),
                    inputs: ['라인 신규 세전액' => $newAmt, 'split_ratio' => $sr],
                    formula: '라인별 내림(세전액 × split_ratio), 마지막 수취인 총액 역산(split_ratio 내림차순 → payee_id 오름차순)',
                    code: 'split[p] = floor(line.amount × p.split_ratio/100); split[last] = amount − Σ선행',
                    rounding: 'ALLOC_LAST_REMAINDER', ref: 'V2 §8.3 8단계 L248 · §13.3 L578',
                    provisional: truthy($ln->fixed_payee), note: truthy($ln->fixed_payee) ? 'Q-15' : '', output: false);
            }
            foreach ($ln->deduct_components as $comp) {
                if ($ln->pipeline_id !== '5.1' && $comp['path'] !== 'UNPAID_REDUCTION') {
                    continue;
                }
                $snap = truthy($comp['snapshot_payee_splits']) ? $comp['snapshot_payee_splits'] : null;
                $use = $snap ? array_map(fn($s) => ['payee_id' => $s['payee_id'], 'split_ratio' => D($s['split_ratio'])], $snap) : $splits;
                if (!$snap && !$default) {
                    $ctx->issue('INPUT_MISSING', '원거래 ' . pystr($comp['ref_id']) . ' 스냅샷 수취인 분할 없음 — 현재 분할 사용', self::STEP,
                        $c->holder_id, 'V1 L211');
                }
                [$parts, $_] = self::splitAmount($comp['amount'], $use);
                foreach ($parts as [$pid, $a]) {
                    $c->payee($pid);
                    $pieces = self::put($pieces, $pid, $a);
                    $ctx->emit(self::STEP, 'split_deduct_snapshot', $a, $c, payee: $pid, line: $ln->label, ref_id: $comp['ref_id'],
                        inputs: ['공제 구성요소' => $comp['amount'],
                            '원거래 분할' => array_map(fn($u) => pystr($u['payee_id']) . ':' . pystr($u['split_ratio']), $use)],
                        formula: '원거래 귀속 환불 · 반환 라인은 원 결제 시점 분할 비율로 수취인별 음수 배분(재분할 금지)',
                        code: 'split_snapshot = alloc(comp.amount, snapshot_payee_splits)', rounding: 'ALLOC_LAST_REMAINDER',
                        ref: 'V2 §8.3 8단계 L249 · V1 L211 · V4 D-1', provisional: count($use) > 1,
                        note: count($use) > 1 ? 'Q-14' : '', output: false);
                }
            }
            foreach ($pieces as [$pid, $amt]) {
                self::addLine($ctx, $c, $ln, $pid, $amt, $offsetPayee, $ptype);
            }
        }
        self::carryLines($ctx, $c);
        self::adjustmentLines($ctx, $c);
    }

    /**
     * 전월 정산 조정 라인(세전 · 위탁)을 세금 계산 직전에 비분할 라인으로 붙인다(V2 §10.1 L353 · §10.2,
     * 2026-10-27 white 결정 — SPEC Q-23 해소). 수취인은 조정 레코드의 payee_id(원거래 분할이 있으면 그 비율).
     */
    private static function adjustmentLines(Context $ctx, ContractState $c): void
    {
        if (Adjust::mode($ctx) !== 'apply') {
            return;
        }
        foreach (Adjust::monthAdjustments($ctx) as $a) {
            if (g($a, 'contract_id') !== $c->id || Adjust::account($a) === 'POST_TAX') {
                continue;
            }
            $amt = D($a['adj_amount']);
            $splits = array_map(fn($s) => ['payee_id' => $s['payee_id'], 'split_ratio' => D($s['split_ratio'])],
                either(g($a, 'snapshot_payee_splits'), []));
            $parts = $splits ? self::splitAmount($amt, $splits)[0] : [[either(g($a, 'payee_id'), $c->holder_id), $amt]];
            $pl = pystr(either(g($a, 'pipeline_id'), 'MIXED'));
            $goods = Adjust::account($a) === 'CONSIGNMENT';
            $h = $ctx->holder(either(g($a, 'payee_id'), $c->holder_id));
            foreach ($parts as [$pid, $part]) {
                $p = $c->payee($pid);
                $neg = $part < 0;
                $row = ['line_id' => 'ADJ:' . pystr(g($a, 'adj_id')), 'adj_id' => g($a, 'adj_id'), 'origin' => 'ADJUSTMENT',
                    'line_key' => ['contract_id' => $c->id, 'pipeline_id' => $pl, 'income_category' => g($a, 'income_category'),
                        'income_clause' => g($a, 'income_clause'), 'tax_threshold_unit_key' => g($a, 'tax_threshold_unit_key')],
                    'pipeline_id' => $pl, 'supply_nature' => Adjust::PIPE_SUPPLY[$pl] ?? 'NONRECURRING',
                    'income_category' => $goods ? null : either(either(g($a, 'income_category'), g($h, 'income_category')), 'BUSINESS'),
                    'income_clause' => g($a, 'income_clause'), 'tax_threshold_unit_key' => g($a, 'tax_threshold_unit_key'),
                    'split_amount' => $part, 'offset_amount' => D(0), 'pre_tax_payable' => $part,
                    'taxable_base' => $goods ? null : ($neg ? D(0) : $part),
                    'pending_negative_base' => ($neg && !$goods) ? $part : null, 'protected_yn' => false,
                    'protected_amount' => D(0), 'origin_month' => g($a, 'origin_month'), 'adj_reason_code' => g($a, 'adj_reason_code')];
                $p->lines[] = $row;
                $ctx->emit(self::STEP, 'adjustment_line', $part, $c, payee: $pid, line: $row['line_id'], ref_id: g($a, 'adj_id'),
                    inputs: ['adj_amount' => $amt, 'account' => Adjust::account($a), 'origin_month' => g($a, 'origin_month'),
                        'adj_reason_code' => g($a, 'adj_reason_code'),
                        '원거래 분할' => array_map(fn($s) => pystr($s['payee_id']) . ':' . pystr($s['split_ratio']), $splits)],
                    formula: $goods ? '전월 정산 조정(위탁) — 위탁 정산액에 가산, 과세표준 미생성'
                        : '전월 정산 조정(세전) — 세금 계산 직전 비분할 라인으로 붙여 9단계에서 원천세 · VAT 계산'
                        . ($neg ? ' · 음수는 과세표준 보류(pending_negative_base)' : ''),
                    code: 'payee_line(origin = ADJUSTMENT, pre_tax_payable = adj_amount)',
                    ref: 'V2 §10.1 L353 · §10.2 L362~366 · 2026-10-27 white 결정(SPEC Q-23 해소)');
            }
        }
    }

    private static function addLine(Context $ctx, ContractState $c, Line $ln, $pid, Number $amt, $offsetPayee, $ptype): void
    {
        $p = $c->payee($pid);
        $off = $pid === $offsetPayee ? $ln->offset : D(0);
        $pre = sub($amt, $off);
        if ($ptype === 'EARNED') {
            $tb = sub($amt, $off);
            $tbCode = 'taxable_base = split − offset (EARNED)';
        } else {
            $tb = $amt;
            $tbCode = 'taxable_base = split (LOAN · 선급금 없음)';
        }
        $pending = null;
        if ($tb < 0) {
            [$pending, $tb] = [$tb, D(0)];
        }
        $prot = D(0);
        if ($ln->protected) {
            $prot = dmax(D(0), $pre);
        } elseif ($ln->pipeline_id === '1.1' && $ln->mmg_subsidy > 0) {
            $share = truthy($ln->adjusted) ? div(mul($ln->mmg_subsidy, $amt), $ln->adjusted) : D(0);
            $prot = dmin(dmax(D(0), floor_won($share)), dmax(D(0), $pre));
        }
        $row = ['line_id' => $ln->label, 'line_key' => $ln->key(), 'origin' => 'NEW', 'pipeline_id' => $ln->pipeline_id,
            'supply_nature' => $ln->supply_nature, 'income_category' => $ln->income_category, 'income_clause' => $ln->income_clause,
            'tax_threshold_unit_key' => $ln->tax_threshold_unit_key, 'payee_is_author' => $ln->payee_is_author,
            'split_amount' => $amt, 'offset_amount' => $off, 'pre_tax_payable' => $pre, 'taxable_base' => $tb,
            'pending_negative_base' => $pending, 'protected_yn' => $prot > 0, 'protected_amount' => $prot];
        $p->lines[] = $row;
        $kw = ['payee' => $pid, 'line' => $ln->label, 'line_key' => $ln->key()];
        $ctx->emit(self::STEP, 'split_amount', $amt, $c, ...$kw, formula: 'payee별 분할액(신규분 + 원거래 귀속 공제분)',
            ref: 'V2 §8.3 8단계 L248~249');
        $ctx->emit(self::STEP, 'offset_amount', $off, $c, ...$kw, inputs: ['offset_payee_id' => $offsetPayee, '라인 상계 배분' => $ln->offset],
            formula: '선급금 상계액은 원 권리자 단일 수취인 귀속(비분할)', ref: 'V2 L234 · V2 §13.4 L589');
        $ctx->emit(self::STEP, 'pre_tax_payable', $pre, $c, ...$kw, inputs: ['분할액' => $amt, '상계액' => $off],
            formula: '당월 세전 지급액 = 분할액 − 상계액', code: 'pre_tax_payable = split − offset', ref: 'V2 §8.3 8단계 L251');
        $ctx->emit(self::STEP, 'taxable_base', $tb, $c, ...$kw, inputs: ['분할액' => $amt, '상계액' => $off, 'prepayment_tax_type' => $ptype],
            formula: '대여금(LOAN): 과세표준 = 분할액 / 소득 선지급(EARNED): 과세표준 = 분할액 − 상계액 / 음수는 보류',
            code: $tbCode, ref: 'V2 §8.3 8단계 L253~254 · 9단계 L281');
        if ($pending !== null) {
            $ctx->emit(self::STEP, 'pending_negative_base', $pending, $c, ...$kw,
                formula: '음수 과세표준은 원천세 미산출 · 보류(pending_negative_base)', ref: 'V2 L281');
        }
        if (truthy($prot)) {
            $ctx->emit(self::STEP, 'protected_amount', $prot, $c, ...$kw, inputs: ['mmg_subsidy' => $ln->mmg_subsidy, 'protected' => $ln->protected],
                formula: '선급금 상계 비대상 보호분(MMG 보전금 몫 · NON_OFFSET 지원금 · 비정기 약정금)',
                ref: 'V2 L282~283 · SPEC 12.1', provisional: $ln->pipeline_id === '1.1', note: $ln->pipeline_id === '1.1' ? 'Q-16' : '');
        }
    }

    private static function consignmentLine(Context $ctx, ContractState $c, Line $ln): void
    {
        $pid = $c->holder_id;
        $p = $c->payee($pid);
        $p->lines[] = ['line_id' => $ln->label, 'line_key' => $ln->key(), 'origin' => 'CONSIGNMENT', 'pipeline_id' => '2.2',
            'supply_nature' => 'BOOK_GOODS', 'income_category' => null, 'income_clause' => null, 'tax_threshold_unit_key' => null,
            'split_amount' => $ln->net, 'offset_amount' => D(0), 'pre_tax_payable' => $ln->net, 'taxable_base' => null,
            'pending_negative_base' => null, 'protected_yn' => false, 'protected_amount' => D(0)];
        $ctx->emit(self::STEP, 'consignment_net', $ln->net, $c, payee: $pid, line: '2.2',
            formula: 'P2.2는 분할하지 않고 위탁자 단독 수취인에게 패스스루(과세표준 미생성)',
            ref: 'V2 §8.3 8단계 L250 · L256 · V1 L170');
        $ctx->emit(self::STEP, 'consignor_sole', true, $c, payee: $pid, line: '2.2', formula: '위탁 분할 금지(복수 위탁자는 계약 분리)',
            ref: 'V1 L170');
    }

    private static function carryLines(Context $ctx, ContractState $c): void
    {
        foreach (array_merge($c->carry['pre_pos'], $c->carry['pre_neg']) as $r) {
            $pid = $r['payee_id'];
            $p = $c->payee($pid);
            $amt = $r['carryover_amount'];
            $neg = $amt < 0;
            $plStr = pystr(g($r, 'pipeline_id'));
            $row = ['line_id' => 'CARRY:' . pystr(g($r, 'ledger_id')), 'ledger_id' => g($r, 'ledger_id'),
                'line_key' => ['contract_id' => $c->id, 'pipeline_id' => g($r, 'pipeline_id'),
                    'income_category' => g($r, 'income_category'), 'income_clause' => g($r, 'income_clause'),
                    'tax_threshold_unit_key' => g($r, 'tax_threshold_unit_key')],
                'origin' => 'CARRY_PRE_TAX', 'pipeline_id' => $plStr,
                'supply_nature' => ['1.1' => 'LECTURE_RS', '2.1' => 'ROYALTY', '5.1' => 'SUPPORT_RS'][$plStr] ?? 'NONRECURRING',
                'income_category' => g($r, 'income_category'), 'income_clause' => g($r, 'income_clause'),
                'tax_threshold_unit_key' => g($r, 'tax_threshold_unit_key'), 'split_amount' => $amt, 'offset_amount' => D(0),
                'pre_tax_payable' => $amt, 'taxable_base' => $neg ? null : $amt,
                'pending_negative_base' => $neg ? $amt : null, 'protected_yn' => false, 'protected_amount' => D(0),
                'first_payable_confirmed_month' => g($r, 'first_payable_confirmed_month'),
                'first_occurred_month' => g($r, 'first_occurred_month')];
            $p->lines[] = $row;
            $ctx->emit(self::STEP, 'carry_pre_tax_line', $amt, $c, payee: $pid, line: $row['line_id'], ref_id: g($r, 'ledger_id'),
                formula: !$neg ? '원귀속 세전 이월 세전 지급액 = 원귀속 세전 미지급 소득 기초금액(현재 분할 비율 미적용)'
                    : '세전 미확정 조정액 — 확정 전 과세표준 합산 금지(pending_negative_base)',
                ref: 'V2 §8.3 8단계 L257 · V4 D-3');
        }
    }
}
