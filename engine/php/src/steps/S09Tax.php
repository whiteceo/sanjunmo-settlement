<?php
/**
 * 9단계 TAX — 세무 판정 · 원천세 · VAT · 실정산액(V2 §8.3 표 L176 · 본문 L260~283 · 11장, TAX.md, SPEC 12절).
 *
 * 라인별: 케이스 판정(TAX.md [A]) → VAT([B]) → 원천징수([C], OTHER는 판정 단위 과세표준) → 라인 실정산액.
 * payee별 9단계 실정산액 = (당월 신규 세전 지급액 − 당월 신규 원천징수세액 + 당월 부가가치세) + 위탁 실정산액(L282).
 * 원귀속 PRE_TAX 세후 환산액 = 기초금액 − 해당 원귀속분 원천징수세액(L271).
 * 끝에 6단계 재검증: 상계 적격 라인 현금 가용액 < 상계액이면 상계액 축소 후 8 · 9단계 재계산(L228 · L231, Q-13 잠정).
 */

namespace SettleCalc;

use BcMath\Number;

final class S09Tax
{
    const STEP = 'TAX';
    const PAYABLE = ['NEW', 'ADJUSTMENT']; // 당월 신규 + 전월 정산 조정(세금 계산 직전 인입)

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            self::taxContract($ctx, $c);
            self::revalidateOffset($ctx, $c);
        }
    }

    private static function vatTreatment(Context $ctx, ContractState $c, $pid)
    {
        return either(either(g($ctx->holder($pid), 'vat_treatment'), g($c->row, 'vat_treatment')), 'VAT_EXCLUDED');
    }

    private static function taxContract(Context $ctx, ContractState $c): void
    {
        foreach ($c->payees as $p) {
            self::taxPayee($ctx, $c, $p);
        }
    }

    private static function taxPayee(Context $ctx, ContractState $c, PayeeState $p): void
    {
        $pid = $p->payee_id;
        $treat = self::vatTreatment($ctx, $c, $pid);
        $units = []; // tkey(origin, unit key, clause) → [line index]  — OTHER 판정 단위
        foreach ($p->lines as &$ln) {
            foreach (['deemed_expense', 'other_income_amount', 'threshold_exempt_yn', 'small_amount_exempt_yn',
                         'after_tax_amount', 'consignment_fee_vat'] as $k) {
                if (!array_key_exists($k, $ln)) {
                    $ln[$k] = null;
                }
            }
        }
        unset($ln);
        foreach ($p->lines as $i => &$ln) {
            $kw = ['payee' => $pid, 'line' => $ln['line_id'], 'line_key' => $ln['line_key']];
            if ($ln['origin'] === 'CONSIGNMENT') {
                self::consignment($ctx, $c, $ln, $kw);
                continue;
            }
            $cl = Tax::classify($ctx, $pid, $ln);
            $tbl = either(g($cl, 'table'), []);
            $ln['matrix_case_id'] = $cl['case'];
            $ln['tax_decision_status'] = $cl['status'];
            $ln['correction_channels'] = array_map('SettleCalc\pystr', either(g($tbl, 'correction_channels'), []));
            $ln['evidence_type'] = g($tbl, 'evidence_type');
            $ln['withholding_rule'] = $cl['withholding'];
            $ctx->emit(self::STEP, 'matrix_case_id', $cl['case'], $c, ...$kw,
                inputs: ['payee_tax_type' => g($ctx->holder($pid), 'payee_tax_type'), 'supply_nature' => $ln['supply_nature'],
                    'income_category' => $ln['income_category'], 'hint' => g($ctx->holder($pid), 'matrix_case_id_hint')],
                formula: 'TX-01~13 판정(자사 → 재화 → NULL 보류 → 프리랜서 공급 성격 → tax_type_cd → 보류 후보)',
                code: 'classify(payee, line)', ref: 'V2 §11.1 L407~412 · TAX.md [A]',
                provisional: $cl['status'] !== 'DECIDED', note: $cl['reason']);
            $ctx->emit(self::STEP, 'tax_decision_status', $cl['status'], $c, ...$kw, formula: 'DECIDED만 마감 허용(PENDING_REVIEW는 차단)',
                ref: 'V2 §11.1 L411');
            if ($cl['status'] !== 'DECIDED') {
                $ctx->issue('CANON_GAP', pystr($pid) . ' ' . $ln['line_id'] . ' 세무 판정 보류: ' . $cl['reason'], self::STEP, $c->holder_id,
                    'TAX.md 확인 필요 2 · 3', 'TAX-2');
            }
            // [B] VAT — 공급가액은 상계 전 금액(분할액) 기준(V2 L264, Q-17 해소 2026-10-26)
            $pre = $ln['pre_tax_payable'];
            $base = $ln['split_amount'];
            if (in_array($ln['origin'], self::PAYABLE, true) && truthy($cl['vat'])) {
                [$supply, $vat, $_, $raw] = Tax::vatOf($cl['vat'], $treat, $base);
            } else {
                [$supply, $vat, $raw] = [$pre, D(0), null];
            }
            $applied = ($treat === 'VAT_INCLUDED' || $cl['vat'] !== 'TAXABLE_10') ? $pre : add($pre, $vat);
            [$ln['supply_amount'], $ln['vat_amount'], $ln['vat_applied_amount']] = [$supply, $vat, $applied];
            $ln['vat_treatment'] = $cl['vat'] === 'TAXABLE_10' ? $treat : null;
            if (in_array($ln['origin'], self::PAYABLE, true)) {
                $ctx->emit(self::STEP, 'vat_amount', $vat, $c, ...$kw, inputs: ['vat rule' => $cl['vat'], 'vat_treatment' => $treat,
                    '상계 전 공급가액(분할액)' => $base, '세전 지급액(상계 후)' => $pre],
                    formula: $cl['vat'] === 'TAXABLE_10' ? 'VAT_EXCLUDED: 공급가액 = 세전 지급액(상계 전 공급가액 기준), 부가세 = 내림(공급가액 × 10%) / '
                        . 'VAT_INCLUDED: 공급가액 = 내림(총액 × 100/110), 부가세 = 총액 − 공급가액' : 'VAT ' . pystr($cl['vat']) . ' — 가산 없음',
                    code: 'vat_of(rule, treatment, split_amount)', before: $raw,
                    rounding: $raw !== null ? 'FLOOR_WON' : 'NONE', ref: 'V2 §8.3 9단계 L263~265 · TAX.md [B]');
                $ctx->emit(self::STEP, 'supply_amount', $supply, $c, ...$kw, formula: '공급가액(상계 전)', ref: 'V2 L264');
                $ctx->emit(self::STEP, 'vat_applied_amount', $applied, $c, ...$kw,
                    formula: '부가세 반영 후 정산액 = 세전 지급액 + 부가세(VAT_INCLUDED는 총액, 가산 없음)', ref: 'V2 L263~265');
            }
            // [C] 원천징수
            $ln['income_tax'] = $ln['local_income_tax'] = $ln['withholding_total'] = null;
            if ($cl['status'] !== 'DECIDED' || $cl['withholding'] !== 'APPLY') {
                if ($cl['status'] === 'DECIDED') {
                    $ln['income_tax'] = $ln['local_income_tax'] = $ln['withholding_total'] = D(0);
                    $ctx->emit(self::STEP, 'withholding_total', D(0), $c, ...$kw, inputs: ['withholding' => $cl['withholding']],
                        formula: pystr($cl['case']) . ' 원천징수 없음', ref: 'TAX.md [C] · V2 11.2');
                }
                continue;
            }
            if ($ln['taxable_base'] === null) {
                $ln['income_tax'] = $ln['local_income_tax'] = $ln['withholding_total'] = D(0);
                continue;
            }
            if ($ln['income_category'] === 'OTHER') {
                $units[tkey($ln['origin'], $ln['tax_threshold_unit_key'], $ln['income_clause'])][] = $i;
                continue;
            }
            $w = Tax::withholdBusiness($ctx, $ln['taxable_base']);
            self::setWithholding($ctx, $c, $ln, $kw, $w, 'BUSINESS');
        }
        unset($ln);
        foreach ($units as $k => $idx) {
            [$origin, $unit, $clause] = untkey($k);
            $u = dsum(array_map(fn($i) => $p->lines[$i]['taxable_base'], $idx));
            $w = Tax::withholdOther($ctx, $u, $clause);
            $lastI = $idx[count($idx) - 1];
            $kw = ['payee' => $pid, 'line' => $p->lines[$lastI]['line_id'], 'line_key' => $p->lines[$lastI]['line_key']];
            $ctx->emit(self::STEP, 'deemed_expense', $w['deemed_expense'], $c, ...$kw,
                inputs: ['판정 단위 과세표준' => $u, '의제율' => $w['deemed_rate'], 'unit' => $unit],
                formula: '필요경비 = 내림(판정 단위 과세표준 × 의제율)', code: 'deemed = floor(U × deemed_rate)',
                before: $w['deemed_raw'], rounding: 'FLOOR_WON', ref: 'V2 §8.3 9단계 L275~276');
            $ctx->emit(self::STEP, 'other_income_amount', $w['other_income_amount'], $c, ...$kw,
                inputs: ['U' => $u, '필요경비' => $w['deemed_expense']], formula: '기타소득금액 = 과세표준 − 필요경비', ref: 'V2 L276');
            $ctx->emit(self::STEP, 'threshold_exempt_yn', $w['threshold_exempt_yn'], $c, ...$kw,
                inputs: ['기타소득금액' => $w['other_income_amount'], '과세최저한' => $ctx->p('other_income_min_tax_amount')],
                formula: '기타소득금액 ≤ 50,000원이면 소득세 · 지방소득세 0원(판정 단위 = tax_threshold_unit_key)',
                ref: 'V2 L277~278 · V1 L436');
            if (count($idx) > 1) {
                $ctx->issue('CANON_GAP', '판정 단위 ' . pystr($unit) . '에 라인 ' . count($idx) . '개 — 단위 세액 라인 배분 정본 없음(총액 역산)',
                    self::STEP, $c->holder_id, 'TAX.md 확인 필요 4', 'TAX-4');
            }
            $bases = array_map(fn($i) => $p->lines[$i]['taxable_base'], $idx);
            $its = alloc_last_remainder($w['income_tax'], $bases);
            $lts = alloc_last_remainder($w['local_income_tax'], $bases);
            self::filing($ctx, $c, $pid, $p->lines[$lastI], $clause);
            foreach ($idx as $j => $i) {
                $x = &$p->lines[$i];
                $x = array_merge($x, ['deemed_expense' => $w['deemed_expense'], 'other_income_amount' => $w['other_income_amount'],
                    'threshold_exempt_yn' => $w['threshold_exempt_yn'], 'small_amount_exempt_yn' => $w['small_amount_exempt_yn']]);
                self::setWithholding($ctx, $c, $x, ['payee' => $pid, 'line' => $x['line_id'], 'line_key' => $x['line_key']],
                    array_merge($w, ['income_tax' => $its[$j], 'local_income_tax' => $lts[$j]]), 'OTHER');
                unset($x);
            }
        }
        foreach ($p->lines as &$ln) {
            if (in_array($ln['origin'], self::PAYABLE, true)) {
                $wt = either(g($ln, 'withholding_total'), D(0));
                $addVat = g($ln, 'vat_treatment') !== 'VAT_INCLUDED' ? $ln['vat_amount'] : D(0);
                $ln['net_settle_line'] = add(sub($ln['pre_tax_payable'], $wt), $addVat);
                $inc = g($ln, 'vat_treatment') === 'VAT_INCLUDED';
                $ctx->emit(self::STEP, 'net_settle_line', $ln['net_settle_line'], $c, payee: $pid, line: $ln['line_id'],
                    inputs: ['세전 지급액' => $ln['pre_tax_payable'], '원천징수세액' => $wt, '부가세(가산분)' => $addVat],
                    formula: '라인 실정산액 = 세전 지급액 − 원천징수세액 + 부가가치세(VAT_INCLUDED는 가산 없음)',
                    ref: 'V2 §8.3 9단계 L282 · TAX.md 확인 필요 5', provisional: $inc, note: $inc ? 'TAX-5' : '');
            } elseif ($ln['origin'] === 'CARRY_PRE_TAX' && $ln['taxable_base'] !== null) {
                $wt = either(g($ln, 'withholding_total'), D(0));
                $ln['after_tax_amount'] = sub($ln['pre_tax_payable'], $wt);
                $ctx->emit(self::STEP, 'carry_pre_tax_after_tax', $ln['after_tax_amount'], $c, payee: $pid, line: $ln['line_id'],
                    inputs: ['기초금액' => $ln['pre_tax_payable'], '원천징수세액' => $wt],
                    formula: '원귀속 PRE_TAX 세후 환산액 = 기초금액 − 해당 원귀속분 원천징수세액', ref: 'V2 L271 · L282');
            }
        }
        unset($ln);
        self::totals($ctx, $c, $p);
    }

    /** 기타소득 신고 · 증빙 의무(tax_table.json 케이스 분기 — TX-03 C15 · C05 / TX-04 C19 · C17). */
    private static function filing(Context $ctx, ContractState $c, $pid, array $ln, $clause): void
    {
        $case = either($ctx->tax_table['cases'][(string)g($ln, 'matrix_case_id')] ?? null, []);
        $br = either((either(g($case, 'branches'), []))[(string)$clause] ?? null, []);
        if (!$br) {
            return;
        }
        $kw = ['payee' => $pid, 'line' => $ln['line_id']];
        $issue = truthy(g($br, 'receipt_issue')) || str_contains(pystr(either(g($case, 'evidence_type'), '')), '원천징수영수증');
        $ctx->emit(self::STEP, 'withholding_receipt_issue', $issue, $c, ...$kw,
            inputs: ['branch' => $clause, 'receipt_issue' => g($br, 'receipt_issue')],
            formula: '원천징수영수증 발급(기타소득 예외 분기는 금액 무관 발급)', ref: 'V2 §11.2 TX-03 · tax_table.json');
        $ctx->emit(self::STEP, 'simplified_statement_monthly', truthy(g($br, 'simplified_statement_yn')), $c, ...$kw,
            formula: '간이지급명세서 매월 제출 대상 여부', ref: 'V2 §11.2 TX-03 · TX-04 · tax_table.json');
        if (truthy(g($br, 'annual_statement_deadline'))) {
            $ctx->emit(self::STEP, 'annual_statement_due', $br['annual_statement_deadline'], $c, ...$kw,
                formula: '기타소득 지급명세서 연 1회 제출 기한', ref: 'V2 §11.2 TX-03 · tax_table.json');
        }
    }

    private static function setWithholding(Context $ctx, ContractState $c, array &$ln, array $kw, array $w, string $cat): void
    {
        [$ln['income_tax'], $ln['local_income_tax']] = [$w['income_tax'], $w['local_income_tax']];
        $ln['withholding_total'] = add($w['income_tax'], $w['local_income_tax']);
        $fIt = $cat === 'BUSINESS' ? '소득세 = 내림(과세표준 × 3%)' : '소득세 = 내림(기타소득금액 × 20%), 소득세 < 1,000원이면 0(소액부징수)';
        $ctx->emit(self::STEP, 'income_tax', $w['income_tax'], $c, ...$kw, inputs: ['과세표준' => $ln['taxable_base'], '소득 구분' => $cat],
            formula: $fIt, code: 'income_tax = floor(base × rate)', before: $w['it_raw'], rounding: 'FLOOR_WON',
            ref: 'V2 §8.3 9단계 L268~270 · §13.1 L568');
        $ctx->emit(self::STEP, 'local_income_tax', $w['local_income_tax'], $c, ...$kw, inputs: ['소득세' => $w['income_tax']],
            formula: '지방소득세 = 내림(소득세 × 10%)(합산세율 금지, 순차 2단)', code: 'local = floor(income_tax × 0.10)',
            before: $w['lt_raw'], rounding: 'FLOOR_WON', ref: 'V2 §8.3 9단계 L269~271');
        $ctx->emit(self::STEP, 'withholding_total', $ln['withholding_total'], $c, ...$kw,
            inputs: ['소득세' => $w['income_tax'], '지방소득세' => $w['local_income_tax']], formula: '라인 총 원천징수세액',
            ref: 'V2 L271');
        if (truthy($ln['taxable_base'])) {
            $rate = quantize_half_even(div(mul($ln['withholding_total'], 100), $ln['taxable_base']), 2);
            $ln['effective_rate_pct'] = $rate;
            $ctx->emit(self::STEP, 'effective_rate_pct', $rate, $c, ...$kw, formula: '실효세율(검증 참고값, 계산에 쓰지 않음)',
                ref: 'TAX.md TX-02 · TX-03');
        }
    }

    private static function consignment(Context $ctx, ContractState $c, array &$ln, array $kw): void
    {
        $cs = $c->consignment ?? [];
        $ret = $c->consignment_return ?? [];
        $feeNet = sub(D(g($cs, 'fee_supply')), D(g($ret, 'fee')));
        $raw = mul($feeNet, D('0.10'));
        $feeVat = floor_won($raw);
        $ftype = either(either(g($ret, 'fee_type'), g($cs, 'consignment_fee_type')), 'NET_DEDUCT');
        $settle = $ftype === 'NET_DEDUCT' ? sub($ln['pre_tax_payable'], $feeVat) : $ln['pre_tax_payable'];
        $ln = array_merge($ln, ['matrix_case_id' => 'TX-11', 'tax_decision_status' => 'DECIDED', 'income_tax' => D(0),
            'local_income_tax' => D(0), 'withholding_total' => D(0), 'vat_amount' => D(0), 'supply_amount' => $ln['pre_tax_payable'],
            'vat_applied_amount' => $ln['pre_tax_payable'], 'consignment_fee_vat' => $feeVat, 'consignment_settle_amount' => $settle,
            'net_settle_line' => $settle, 'withholding_rule' => 'NONE',
            'evidence_type' => $ctx->tax_table['cases']['TX-11']['evidence_type'],
            'correction_channels' => array_map('SettleCalc\pystr', $ctx->tax_table['cases']['TX-11']['correction_channels']),
            'fee_supply_net' => $feeNet, 'consignment_fee_type' => $ftype]);
        $ctx->emit(self::STEP, 'matrix_case_id', 'TX-11', $c, ...$kw, formula: '도서 재화 공급(위탁) — 원천징수 미호출 · 과세표준 미생성',
            ref: 'V2 §11.2 TX-11 L494~504');
        $ctx->emit(self::STEP, 'consignment_fee_vat', $feeVat, $c, ...$kw,
            inputs: ['월 수수료 공급가액' => g($cs, 'fee_supply'), '반품 수수료 조정' => neg(D(g($ret, 'fee'))),
                '당월 순 위탁 수수료 공급가액' => $feeNet],
            formula: '위탁 수수료 부가세 = 내림(당월 순 위탁 수수료 공급가액 × 10%)', code: 'fee_vat = floor(fee_supply_net × 0.10)',
            before: $raw, rounding: 'FLOOR_WON', ref: 'V2 §8.3 9단계 L266');
        $ctx->emit(self::STEP, 'consignment_settle_amount', $settle, $c, ...$kw,
            inputs: ['4단계 순 위탁 정산액' => $ln['pre_tax_payable'], '수수료 부가세' => $feeVat, 'consignment_fee_type' => $ftype],
            formula: 'NET_DEDUCT: 위탁 실정산액 = 순 위탁 정산액 − 수수료 부가세 / GROSS_SETTLE: = 순 위탁 정산액(별도 청구)',
            code: 'settle = net_2_2 − fee_vat if NET_DEDUCT else net_2_2', ref: 'V2 §8.3 9단계 L266 · L282');
    }

    private static function totals(Context $ctx, ContractState $c, PayeeState $p): void
    {
        if (!$p->lines) { // 세무 대상 라인 없음(예: 자사 집계 전용) — 합계를 내지 않는다
            return;
        }
        $new = array_values(array_filter($p->lines, fn($l) => in_array($l['origin'], self::PAYABLE, true)));
        $cons = array_values(array_filter($p->lines, fn($l) => $l['origin'] === 'CONSIGNMENT'));
        $carry = array_values(array_filter($p->lines, fn($l) => $l['origin'] === 'CARRY_PRE_TAX' && g($l, 'after_tax_amount') !== null));
        $t = &$p->out['TAX'];
        $col = fn(array $rows, string $k) => array_map(fn($l) => $l[$k], $rows);
        $tbs = array_values(array_filter($col($new, 'taxable_base'), fn($x) => $x !== null));
        $t['pre_tax_payable_total'] = dsum($col($new, 'pre_tax_payable'));
        $t['split_amount_total'] = dsum($col($new, 'split_amount'));
        $t['offset_amount_total'] = dsum($col($new, 'offset_amount'));
        $t['taxable_base_total'] = $tbs ? dsum($tbs) : null;
        $t['vat_total'] = dsum($col($new, 'vat_amount'));
        $t['vat_applied_total'] = dsum($col($new, 'vat_applied_amount'));
        $t['income_tax_total'] = dsum(array_map(fn($l) => either(g($l, 'income_tax'), D(0)), $new));
        $t['local_income_tax_total'] = dsum(array_map(fn($l) => either(g($l, 'local_income_tax'), D(0)), $new));
        $t['withholding_total'] = add($t['income_tax_total'], $t['local_income_tax_total']);
        $t['consignment_fee_vat'] = $cons ? dsum($col($cons, 'consignment_fee_vat')) : null;
        $t['consignment_settle_amount'] = dsum($col($cons, 'consignment_settle_amount'));
        $t['net_settle_amount'] = add(dsum($col($new, 'net_settle_line')), $t['consignment_settle_amount']);
        $prot = D(0);
        foreach ($new as $ln) {
            if (truthy($ln['protected_amount']) && truthy($ln['pre_tax_payable'])) {
                $prot = add($prot, floor_won(div(mul($ln['net_settle_line'], $ln['protected_amount']), $ln['pre_tax_payable'])));
            }
        }
        $t['net_settle_protected'] = $prot;
        $t['net_settle_offsettable'] = sub($t['net_settle_amount'], $prot);
        $t['carry_pre_tax_after_tax_total'] = dsum($col($carry, 'after_tax_amount'));
        $t['pending_review_lines'] = count(array_filter($p->lines, fn($l) => g($l, 'tax_decision_status') === 'PENDING_REVIEW'));
        $t['withholding_called'] = false;
        foreach ($p->lines as $l) {
            if (g($l, 'withholding_rule') === 'APPLY' && g($l, 'tax_decision_status') === 'DECIDED') {
                $t['withholding_called'] = true;
            }
        }
        $cases = array_values(array_filter(array_map(fn($l) => g($l, 'matrix_case_id'), $p->lines), fn($x) => truthy($x)));
        $uniq = array_values(array_unique($cases));
        sort($uniq, SORT_STRING);
        $t['matrix_case_ids'] = $uniq;
        $ev = array_values(array_unique(array_filter(array_map(fn($l) => g($l, 'evidence_type'), $p->lines), fn($x) => truthy($x))));
        sort($ev, SORT_STRING);
        $t['evidence_types'] = $ev;
        $t['non_deductible_input_vat'] = dsum(array_map(fn($l) => $l['vat_amount'], array_filter($new,
            fn($l) => in_array(g($l, 'matrix_case_id'), ['TX-06', 'TX-07', 'TX-09'], true))));
        $pid = $p->payee_id;
        $fm = ['net_settle_amount' => 'payee별 당월 9단계 실정산액 = (당월 신규 세전 지급액 − 당월 신규 원천징수세액 + 당월 부가가치세) + 위탁 실정산액',
            'net_settle_protected' => '비상계 보호분(MMG 보전금 · 비상계 지원금 · 비정기 약정금의 세후 해당액) — 라인 세후액 비례',
            'non_deductible_input_vat' => 'TX-06 · 07 · 09 지급 VAT(매입세액 불공제 원가 — 계정 구분만)'];
        $rf = ['net_settle_amount' => 'V2 §8.3 9단계 L282', 'net_settle_protected' => 'V2 L282~283', 'non_deductible_input_vat' => 'TAX.md TX-07'];
        foreach (['pre_tax_payable_total', 'split_amount_total', 'offset_amount_total', 'taxable_base_total', 'vat_total',
                     'vat_applied_total', 'income_tax_total', 'local_income_tax_total', 'withholding_total',
                     'consignment_fee_vat', 'consignment_settle_amount', 'net_settle_amount', 'net_settle_protected',
                     'net_settle_offsettable', 'carry_pre_tax_after_tax_total', 'withholding_called', 'non_deductible_input_vat'] as $k) {
            $ctx->emit(self::STEP, $k, $t[$k], $c, payee: $pid, formula: $fm[$k] ?? 'payee 합계', ref: $rf[$k] ?? 'V2 §8.3 9단계',
                provisional: $k === 'net_settle_protected', note: $k === 'net_settle_protected' ? 'Q-16' : '');
        }
        if ($cases) {
            $ctx->emit(self::STEP, 'matrix_case_id', count($uniq) === 1 ? $cases[0] : implode('/', $uniq), $c, payee: $pid,
                formula: "payee 세무 케이스(라인 케이스가 여럿이면 '/' 연결)", ref: 'V2 §11.1');
        }
        if ($t['evidence_types']) {
            $ctx->emit(self::STEP, 'evidence_type', implode(' + ', $t['evidence_types']), $c, payee: $pid, formula: '증빙(tax_table.json)',
                ref: 'TAX.md 1절');
        }
        $ch = [];
        foreach ($p->lines as $l) {
            foreach ((either(g($l, 'correction_channels'), [])) as $x) {
                $ch[] = $x;
            }
        }
        if ($ch) {
            $ctx->emit(self::STEP, 'correction_channel', $ch[0], $c, payee: $pid, formula: '정정 채널(tax_table.json)', ref: 'V2 §10.4');
        }
        unset($t);
    }

    /** 6단계 9단계 재검증 — '계산상 현금 가용액'이 회수액보다 작으면 회수액 축소(V2 L228 · L231, Q-13 잠정). */
    private static function revalidateOffset(Context $ctx, ContractState $c): void
    {
        $pp = $c->prepay;
        if (!$pp || !truthy(g($pp, 'amount'))) {
            return;
        }
        $payee = $c->payees[(string)$pp['payee']] ?? null;
        if (!$payee) {
            return;
        }
        $elig = [];
        foreach ($c->lines as $l) {
            if ($l->eligible > 0) {
                $elig[] = $l->label;
            }
        }
        $cash = dsum(array_map(fn($l) => sub($l['split_amount'], either(g($l, 'withholding_total'), D(0))),
            array_filter($payee->lines, fn($l) => $l['origin'] === 'NEW' && in_array($l['line_id'], $elig, true))));
        $ctx->emit(self::STEP, 'cash_avail_offset_lines', $cash, $c, payee: $pp['payee'], inputs: ['상계액' => $pp['amount']],
            formula: '상계 적격 라인 계산상 현금 가용액 = Σ(분할액 − 라인 원천세)', code: 'cash_avail = Σ(split − withholding)',
            ref: 'V2 §8.3 6단계 L228', provisional: true, note: 'Q-13');
        if ($cash >= $pp['amount']) {
            return;
        }
        $ctx->issue('CANON_GAP', pystr($c->id) . ' 상계액 ' . $pp['amount']->value . ' > 현금 가용액 ' . $cash->value . ' — 상계액 축소(잠정 산식)',
            self::STEP, $c->holder_id, 'V2 L228 · L231', 'Q-13');
        S06PrepayOffset::compute($ctx, $c, false, dmax(D(0), $cash));
        S08PayeeSplit::splitContract($ctx, $c);
        self::taxContract($ctx, $c);
    }
}
