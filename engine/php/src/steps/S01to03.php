<?php
/**
 * 1단계 CARRY_IN · 2단계 ACCRUAL · 3단계 MMG_ADJ.
 *
 * 1 CARRY_IN(V2 §8.3 표 L168 · 본문 L180~182, SPEC 4절): 미소멸 · 예약 없음 행을 1회만 조회해
 *   PRE_TAX(+/−) · POST_TAX(+/−) · 위탁 전용 잔액으로 분리 전달한다. 재분할 · 재투입 금지, 절사 없음.
 * 2 ACCRUAL(V2 §8.3 표 L169 · 본문 L183~191, SPEC 5절): 당월 신규 발생액만 집계(환불 · 프로모션 미반영).
 * 3 MMG_ADJ(V2 §8.3 표 L170 · 본문 L192~195, V1 §5.3 · §15.2, SPEC 6절):
 *   P1.1 순수 신규 R/S < MMG 이면 보정 후 P1.1 = MMG, MMG 보전금 = MMG − 순수 신규 R/S(mmg_subsidy_ledger 격리).
 */

namespace SettleCalc;

final class S01CarryIn
{
    const STEP = 'CARRY_IN';

    public static function run(Context $ctx): void
    {
        foreach ($ctx->input['carryover_ledger'] as $r) {
            $c = $ctx->contract($r['contract_id']);
            if (!$c) {
                continue;
            }
            if (truthy(g($r, 'extinguished_yn')) || either(g($r, 'payout_reservation_status'), 'NONE') !== 'NONE') {
                continue;
            }
            $amt = D($r['carryover_amount']);
            $row = array_merge($r, ['carryover_amount' => $amt,
                'payee_id' => either(either(g($r, 'payee_id'), g($r, 'rights_holder_id')), $c->holder_id)]);
            if (truthy(g($r, 'consignment_balance_yn'))) {
                $c->carry['cons'] = add($c->carry['cons'], $amt);
                $c->carry['cons_rows'][] = $row;
                $kind = 'consignment_balance';
            } elseif (g($r, 'account_type') === 'PRE_TAX') {
                $kind = $amt > 0 ? 'carry_pre_tax_pos' : 'carry_pre_tax_neg';
                $c->carry[$amt > 0 ? 'pre_pos' : 'pre_neg'][] = $row;
            } elseif (g($r, 'account_type') === 'POST_TAX') {
                $kind = $amt > 0 ? 'carry_post_tax_pos' : 'carry_post_tax_neg';
                $c->carry[$amt > 0 ? 'post_pos' : 'post_neg'][] = $row;
            } else {
                $ctx->issue('INPUT_MISSING', '이월 행 ' . pystr(g($r, 'ledger_id')) . ' 계정 구분 없음', self::STEP, $c->holder_id,
                    'V1 §7.4 L580');
                continue;
            }
            $ctx->emit(self::STEP, $kind, $amt, $c, payee: $row['payee_id'], line: pystr(either(g($r, 'pipeline_id'), '')),
                ref_id: g($r, 'ledger_id'),
                inputs: ['account_type' => g($r, 'account_type'), 'consignment_balance_yn' => g($r, 'consignment_balance_yn'),
                    'origin_month' => g($r, 'origin_month')],
                formula: '확정 귀속 잔액을 PRE_TAX(+/−) · POST_TAX(+/−) · 위탁 전용 잔액으로 분리하여 전달(재분할 · 재투입 금지)',
                code: 'rows = carryover_ledger.filter(extinguished_yn == false, payout_reservation_status == NONE)',
                ref: 'V2 §8.3 1단계 L180~181', output: false);
        }
        foreach ($ctx->contracts as $c) {
            $k = $c->carry;
            $out = &$c->stepOut(self::STEP);
            $out['carry_pre_tax_pos'] = $k['pre_pos'];
            $out['carry_pre_tax_neg'] = $k['pre_neg'];
            $out['carry_post_tax_pos'] = $k['post_pos'];
            $out['carry_post_tax_neg'] = $k['post_neg'];
            $out['consignment_balance'] = $ctx->emit(self::STEP, 'consignment_balance', $k['cons'], $c,
                inputs: ['rows' => count($k['cons_rows'])],
                formula: '위탁 전용 잔액(동일 위탁 계약의 4단계 P2.2 상쇄 전용)', ref: 'V2 §8.3 1단계 L182 · V1 §7.4');
            $sumOf = fn($rows) => dsum(array_map(fn($r) => $r['carryover_amount'], $rows));
            $all = array_merge($k['pre_pos'], $k['pre_neg'], $k['post_pos'], $k['post_neg']);
            $total = add($sumOf($all), $k['cons']);
            $out['carry_total'] = $ctx->emit(self::STEP, 'carry_total', $total, $c,
                inputs: ['PRE_TAX+' => $sumOf($k['pre_pos']), 'PRE_TAX−' => $sumOf($k['pre_neg']),
                    'POST_TAX+' => $sumOf($k['post_pos']), 'POST_TAX−' => $sumOf($k['post_neg']), '위탁 전용' => $k['cons']],
                formula: '이월 구분별 전달 배열 합계(표시용)', code: 'Σ carry rows', ref: 'V2 §8.3 1단계 L168');
            unset($out);
        }
    }
}

final class S02Accrual
{
    const STEP = 'ACCRUAL';
    const NAMES = ['1.1' => '온라인 강좌 수익배분(Pipeline 1.1) 신규 R/S = 당월 발생 R/S 합계',
        '2.1' => '자사 발행 도서 인세(Pipeline 2.1) 신규 인세액 = 당월 확정 인세액',
        '2.2' => '위탁 도서 판매대금 정산(Pipeline 2.2) 신규 위탁 정산 입력액(NET_DEDUCT/GROSS_SETTLE 분기)',
        '5.1' => '매출연동 개발지원금(Pipeline 5.1) 신규 지원금액(status = ACTIVE 약정 한정)'];

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $out = &$c->stepOut(self::STEP);
            $newLines = [];
            $total = D(0);
            foreach ($c->lines as $ln) {
                if (!isset(self::NAMES[$ln->pipeline_id])) {
                    continue;
                }
                $ctx->emit(self::STEP, 'new_amount', $ln->new, $c, line: $ln->label, line_key: $ln->key(), agreement: $ln->agreement_id,
                    inputs: ['pipeline_id' => $ln->pipeline_id], formula: self::NAMES[$ln->pipeline_id],
                    code: 'new_' . str_replace('.', '_', $ln->pipeline_id) . '[line]', ref: 'V2 §8.3 2단계 L185~188');
                $newLines[] = ['line_key' => $ln->key(), 'amount' => $ln->new];
                $total = add($total, $ln->new);
            }
            $pre = dsum(array_map(fn($r) => $r['carryover_amount'], array_merge($c->carry['pre_pos'], $c->carry['pre_neg'])));
            $out['new_lines'] = $newLines;
            $ctx->emit(self::STEP, 'pipeline_inflow', (bool)$newLines, $c, inputs: ['lines' => count($newLines)],
                formula: '권리자 지급 엔진 인입 라인이 있는가(P2.3 · 비인입 도서 제외)', ref: 'V2 §8.3 1단계 L153~155');
            $out['accrual_total'] = $ctx->emit(self::STEP, 'accrual_total', $total, $c, inputs: ['lines' => count($newLines)],
                formula: '당월 신규 세전 발생액 = P1.1 + P2.1 + P2.2 + P5.1', code: 'accrual_total = Σ new lines',
                ref: 'V2 §8.3 2단계 L189');
            $out['pre_tax_balance_incl_carry'] = $ctx->emit(self::STEP, 'pre_tax_balance_incl_carry', add($total, $pre), $c,
                inputs: ['당월 신규 세전 발생액' => $total, '세전 이월액' => $pre],
                formula: '이월 포함 세전 처리잔액 = 당월 신규 세전 발생액 + 1단계 세전 이월액(표시 전용)',
                code: 'pre_tax_balance_incl_carry = accrual_total + Σcarry_pre_tax', ref: 'V2 §8.3 2단계 L190');
            $l11 = $c->linesOf('1.1');
            $mmgBasis = dsum(array_map(fn($l) => $l->new, $l11));
            $out['mmg_basis_1_1'] = $ctx->emit(self::STEP, 'mmg_basis_1_1', $mmgBasis, $c, inputs: ['P1.1 lines' => count($l11)],
                formula: 'MMG 판정용 순수 신규 수익 배분(R/S, 이월액 및 Pipeline 5.1 제외)', code: 'mmg_basis_1_1 = Σnew_1_1',
                ref: 'V2 §8.3 2단계 L191');
            $own = array_values(array_filter($ctx->own_holder, fn($o) => $o['contract'] === $c));
            if ($own) {
                $out['own_holder_output'] = $ctx->emit(self::STEP, 'own_holder_output',
                    dsum(array_map(fn($o) => $o['distributable'], $own)), $c,
                    inputs: ['agreements' => count($own)], formula: '자사 권리자 산출액(재원 한도 산정에만 사용, 발생액 아님)',
                    ref: 'V2 §8.3 2단계 L188 · L159');
            }
            if ($c->consignment) {
                $cs = $c->consignment;
                $out['consignment'] = ['monthly_sales' => $cs['monthly_sales'], 'net_before_fee_vat' => $cs['net_before_fee_vat'],
                    'fee_supply' => $cs['fee_supply'], 'consignment_input' => $cs['consignment_input']];
            }
            unset($out);
        }
    }
}

final class S03MmgAdj
{
    const STEP = 'MMG_ADJ';

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $out = &$c->stepOut(self::STEP);
            $lines = $c->linesOf('1.1');
            $rl = $ctx->rate($c->id, 'BASIC', $ctx->month . '-01', '1.1') ?? $ctx->rate($c->id, 'BASIC', null, '1.1');
            $mmg = D(g($rl ?? [], 'mmg_amount'));
            $applicable = (bool)$lines || $mmg > 0;
            $out['applicable'] = $ctx->emit(self::STEP, 'applicable', $applicable, $c, inputs: ['P1.1 lines' => count($lines), 'mmg' => $mmg],
                formula: 'MMG는 온라인 강좌 특약 — Pipeline 1.1에만 적용', ref: 'V2 §8.3 3단계 L193');
            if (!$applicable) {
                unset($out);
                continue;
            }
            $basis = dsum(array_map(fn($l) => $l->new, $lines));
            if ($mmg > 0 && $basis < $mmg) {
                [$adjusted, $subsidy] = [$mmg, sub($mmg, $basis)];
            } else {
                [$adjusted, $subsidy] = [$basis, D(0)];
            }
            if ($lines && count($lines) > 1) {
                $ctx->issue('CANON_GAP', pystr($c->id) . ' P1.1 라인 ' . count($lines) . '개 — 보전금 귀속 라인 정본 없음(금액 최대 라인)',
                    self::STEP, $c->holder_id, 'V2 L192~193', 'Q-06');
            }
            $target = $lines ? max_by($lines, fn($x) => [$x->new, $x->label]) : null;
            if ($target === null && $subsidy > 0) { // 매출 0원 계약도 보장 대상이면 P1.1 라인을 만든다
                $target = S00PipelineIn::line11($ctx, $c);
            }
            if ($target !== null) {
                $target->mmg_subsidy = $subsidy;
            }
            $c->mmg_subsidy = $subsidy;
            $flag = false;
            if ($subsidy > 0) {
                foreach ($ctx->input['pass_refund_deductions'] as $p) {
                    if (g($p, 'contract_id') === $c->id && in_array(g($p, 'option'), ['B', 'C'], true)) {
                        $flag = true;
                    }
                }
            }
            $out['mmg_amount'] = $mmg;
            $out['adjusted_1_1'] = $ctx->emit(self::STEP, 'adjusted_1_1', $adjusted, $c, line: '1.1',
                inputs: ['P1.1 순수 신규 R/S' => $basis, '월 보장액(MMG)' => $mmg],
                formula: 'P1.1 순수 신규 R/S < MMG 시 보정 후 P1.1 = MMG',
                code: 'adjusted_1_1 = mmg if mmg > 0 and mmg_basis_1_1 < mmg else mmg_basis_1_1', ref: 'V2 §8.3 3단계 L193');
            $out['mmg_subsidy'] = $ctx->emit(self::STEP, 'mmg_subsidy', $subsidy, $c, line: '1.1',
                inputs: ['MMG' => $mmg, 'P1.1 순수 신규 R/S' => $basis],
                formula: 'MMG 보전금 = MMG − P1.1 순수 신규 R/S(mmg_subsidy_ledger 격리)',
                code: 'mmg_subsidy = mmg − mmg_basis_1_1', ref: 'V2 §8.3 3단계 L193',
                provisional: count($lines) > 1, note: count($lines) > 1 ? 'Q-06' : '');
            $out['mmg_promo_overlap_flag'] = $ctx->emit(self::STEP, 'mmg_promo_overlap_flag', $flag, $c, inputs: ['mmg_subsidy' => $subsidy],
                formula: '옵션 B 및 옵션 C 차감이 동시 발생하면 재무 확인 플래그(연산 차단 없음)', ref: 'V2 L194 · V1 L617');
            if ($subsidy > 0) {
                $ctx->ledgers['mmg_subsidy_ledger'][] = ['contract_id' => $c->id, 'target_month' => $ctx->month,
                    'mmg_subsidy' => $subsidy];
            }
            $cap = g($c->row, 'mmg_annual_cap');
            if ($cap !== null && $subsidy > D($cap)) {
                $ctx->warn('MMG_ANNUAL_CAP', pystr($c->id) . ' MMG 보전금 ' . $subsidy->value . ' > 연간 상한 ' . pystr($cap) . ' — 재무 승인 대상', 'V1 L339');
                $ctx->issue('CANON_GAP', 'MMG 연간 상한 초과분 처리 정본 없음 — 금액 그대로', self::STEP, $c->holder_id, 'V1 L339', 'Q-05');
            }
            foreach ($c->linesOf('1.1') as $ln) {
                $ln->adjusted = add($ln->new, $ln === $target ? $subsidy : D(0));
            }
            unset($out);
        }
    }
}
