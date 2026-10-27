<?php
/**
 * 10 CLAIM · 11 PAYOUT · 12 CLOSE_CHECK · 13 PASS_REFUND_PAYOUT.
 *
 * 10 CLAIM(V2 §8.3 표 L177 · 본문 L284~298, V1 §5.2 · §5.3 · §7.3, SPEC 13절):
 *   청구 대상 음수 = min(0, 반환 반영 후 순액) − 동의 없는 반환 − 미상계 청구 전환액,
 *   청구 발행 = 음수 AND (|음수| > |min_claim_limit| OR 강제 청구 트리거).
 *   지급 판정 전달액 = max(0, 반환 반영 후 순액) + 원귀속 PRE_TAX 세후 환산액.
 * 11 PAYOUT(V2 §8.3 표 L178 · 본문 L299~308, V1 §7.3 · §7.4, SPEC 14절):
 *   판정 금액 = 당월 지급채무 순액 + POST_TAX 지급대기액, ≥ min_payout_limit 또는 강제 정산 → 지급 확정, 미달 → 이월.
 * 12 CLOSE_CHECK(V1 §7.4 L588~595, SPEC 15.1): 이월 연속성 등식 3종. 하나라도 불일치하면 마감 차단.
 * 13 PASS_REFUND_PAYOUT(통합 설계서 S6 합격환급 L438~446, S-02 · S-14): 합격환급금 수강생 지급(권리자 정산 밖).
 */

namespace SettleCalc;

use BcMath\Number;

final class S10Claim
{
    const STEP = 'CLAIM';

    private static function days($a, $b): int
    {
        $da = new \DateTimeImmutable(head(pystr($a), 10));
        $db = new \DateTimeImmutable(head(pystr($b), 10));
        return (int)$da->diff($db)->format('%r%a');
    }

    private static function clawbackAmount(Context $ctx, ContractState $c, array $cb, array $kw): Number
    {
        if (g($cb, 'clawback_amount') !== null) {
            return $ctx->emit(self::STEP, 'clawback_amount', D($cb['clawback_amount']), $c, ...$kw, inputs: ['입력' => 'clawback_amount'],
                formula: '확정 반환액(세후, 입력값)', ref: 'V1 §5.2 L247~249');
        }
        $total = self::days($cb['obligation_start_date'], $cb['obligation_end_date']) + 1;
        $remain = self::days($cb['termination_date'], $cb['obligation_end_date']);
        $raw = div(mul(D($cb['paid_signing_bonus_net']), $remain), $total);
        return $ctx->emit(self::STEP, 'clawback_amount', floor_won($raw), $c, ...$kw,
            inputs: ['세후 실지급액' => $cb['paid_signing_bonus_net'], '잔여 일수' => $remain, '총 의무 일수' => $total],
            formula: '일할 반환액 = 내림(세후 실지급액 × 잔여 일수 / 총 의무 일수)(해지일 당일은 복무 일수에 포함)',
            code: 'clawback = floor(paid_net × remaining_days / total_days)', before: $raw, rounding: 'FLOOR_WON',
            ref: 'V1 §5.2 L248~249');
    }

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $end = $c->endInMonth($ctx->month);
            $closed = truthy(g($ctx->holder($c->holder_id), 'business_closed_yn'));
            $limit = D(g($c->row, 'min_claim_limit') !== null ? g($c->row, 'min_claim_limit') : $ctx->p('default_min_claim_limit'));
            foreach ($c->payees as $p) {
                self::claimPayee($ctx, $c, $p, $end, $closed, $limit);
            }
        }
    }

    private static function claimPayee(Context $ctx, ContractState $c, PayeeState $p, bool $end, bool $closed, Number $limit): void
    {
        $pid = $p->payee_id;
        $kw = ['payee' => $pid];
        $t = $p->out['TAX'];
        $o = &$p->out['CLAIM'];
        $net = either($t['net_settle_amount'] ?? null, D(0));
        $cons = either($t['consignment_settle_amount'] ?? null, D(0));
        $consRows = [];
        if ($cons < 0) { // 위탁 라인 음수: 청구 판정 대상 아님 → 위탁 전용 잔액(L298)
            $net = sub($net, $cons);
            $consRows[] = ['ledger_id' => null, 'action' => 'NEW', 'rights_holder_id' => $c->holder_id, 'payee_id' => $pid,
                'contract_id' => $c->id, 'origin_month' => $ctx->month, 'account_type' => null, 'pipeline_id' => '2.2',
                'consignment_balance_yn' => true, 'carryover_reason' => '위탁 반품 초과',
                'carryover_amount' => $cons, 'payout_reservation_status' => 'NONE', 'extinguished_yn' => false];
            $ctx->emit(self::STEP, 'consignment_balance_new', $cons, $c, ...$kw,
                formula: '위탁 라인 음수 — 청구 판정 대상 아님, 미지급분은 위탁 전용 잔액(과세표준 · 세전 계정 적재 금지)',
                ref: 'V2 §8.3 10단계 L298 · V1 §7.4', provisional: true, note: '미지급/기지급 구분 입력 없음 — 전액 미지급분으로 처리');
        }
        $cbs = array_values(array_filter($ctx->input['clawbacks'], fn($cb) => $cb['contract_id'] === $c->id && $cb['payee_id'] === $pid));
        $cbConsent = D(0);
        $cbOther = D(0);
        foreach ($cbs as $cb) {
            $amt = self::clawbackAmount($ctx, $c, $cb, array_merge($kw, ['ref_id' => g($cb, 'clawback_id')]));
            if (truthy(g($cb, 'clawback_offset_consent_yn'))) {
                $cbConsent = add($cbConsent, $amt);
            } else {
                $cbOther = add($cbOther, $amt);
            }
        }
        $o['clawback_amount'] = add($cbConsent, $cbOther);
        $o['clawback_offset_consent_yn'] = truthy($cbConsent);
        $post = array_values(array_filter(Adjust::monthAdjustments($ctx), fn($a) => Adjust::mode($ctx) === 'apply'
            && g($a, 'contract_id') === $c->id && either(g($a, 'payee_id'), $c->holder_id) === $pid
            && Adjust::account($a) === 'POST_TAX'));
        $postPos = dsum(array_map(fn($a) => D($a['adj_amount']), array_filter($post, fn($a) => D($a['adj_amount']) > 0)));
        $postNeg = neg(dsum(array_map(fn($a) => D($a['adj_amount']), array_filter($post, fn($a) => D($a['adj_amount']) < 0))));
        foreach ($post as $a) {
            $ctx->emit(self::STEP, 'post_tax_adjustment', D($a['adj_amount']), $c, payee: $pid, line: 'ADJ:' . pystr(g($a, 'adj_id')),
                ref_id: g($a, 'adj_id'), inputs: ['origin_month' => g($a, 'origin_month'), 'adj_reason_code' => g($a, 'adj_reason_code')],
                formula: '전월 정산 조정(세후) — 양수는 당월 지급채무에 가산, 음수는 세후 반환채권(청구 음수 항, 자동 상계 없음)',
                ref: 'V2 §10.1 L353 · §10.2 · 2026-10-27 white 결정(SPEC Q-23 해소) · Q-19');
        }
        $after = $ctx->emit(self::STEP, 'net_after_return', add(sub($net, $cbConsent), $postPos), $c, ...$kw,
            inputs: ['9단계 실정산액(위탁 음수 제외)' => $net, '동의 연결 전속계약금 반환' => $cbConsent,
                '세후 조정(+)' => $postPos],
            formula: '동일 계약 · 동일 수취인 + 반환 상계 동의가 연결된 경우만 1회 차감, 세후 전월 정산 조정(+) 가산',
            code: 'net_after_return = net_settle_amount − (clawback if consent else 0) + post_tax_adj(+)',
            ref: 'V2 §8.3 10단계 1) L286 · §10.2');
        $unoffset = D(0);
        $pp = $c->prepay;
        if ($pp && $pid === $pp['payee'] && $end && ($c->prepay_balance_after ?? D(0)) > 0 && !truthy(g($c->row, 'successor_transfer_yn'))) {
            if ($pp['type'] === 'LOAN') {
                $unoffset = $c->prepay_balance_after;
                $f = '대여금(LOAN): 미상계 원금 전액 청구 전환';
            } else {
                $v = g($pp['rows'][0], 'earned_unoffset_post_tax_amount');
                if ($v === null) {
                    $ctx->stop('INPUT_ERROR', 'EARNED_UNOFFSET_MISSING',
                        pystr($c->id) . ' 소득 선지급 만료 · 해지 세후 미상계 상당액 입력 필요(산식 정본 없음)', 'SPEC Q-18');
                }
                $unoffset = D($v);
                $f = '소득 선지급(EARNED): 세후 미상계 상당액(입력값, 산식 정본 없음 — Q-18)';
            }
            $ctx->emit(self::STEP, 'unoffset_prepay_claim', $unoffset, $c, ...$kw,
                inputs: ['6단계 후 미상계 잔액' => $c->prepay_balance_after, '만료 · 해지 귀속월' => $end],
                formula: $f . ' — 비상계 보호 지급액과 자동 교차 상계 금지', ref: 'V2 §8.3 10단계 2) L287 · V1 L328',
                provisional: $pp['type'] === 'EARNED', note: $pp['type'] === 'EARNED' ? 'Q-18' : '');
        }
        $o['unoffset_prepay_claim'] = $unoffset;
        $returns = dsum(array_map(fn($r) => $r['post_tax_amount'], array_filter($c->return_claims, fn($r) => $r['payee_id'] === $pid)));
        $returns = add($returns, neg(dsum(array_map(fn($r) => $r['carryover_amount'],
            array_filter($c->carry['post_neg'], fn($r) => $r['payee_id'] === $pid)))));
        $returns = add($returns, $postNeg); // 세후 전월 정산 조정(−)
        if (truthy($returns)) {
            $ctx->issue('CANON_GAP', '기지급 소득 반환채권 · 전월 POST_TAX(−)의 10단계 차감 위치 정본 없음 — 청구 음수 항에 가산',
                self::STEP, $c->holder_id, 'V2 L286~289', 'Q-19');
        }
        $o['return_claims_applied'] = $ctx->emit(self::STEP, 'return_claims_applied', $returns, $c, ...$kw,
            formula: '기지급 소득 반환채권 + 전월 세후 반환채권(청구 음수 항에 가산 — 잠정)',
            ref: 'V2 L295', provisional: truthy($returns), note: truthy($returns) ? 'Q-19' : '');
        $cnn = sub(sub(sub(dmin(D(0), $after), $cbOther), $unoffset), $returns);
        $o['net_after_return'] = $after;
        $o['claim_negative_net'] = $ctx->emit(self::STEP, 'claim_negative_net', $cnn, $c, ...$kw,
            inputs: ['min(0, 반환 반영 후 순액)' => dmin(D(0), $after), '동의 없는 반환' => $cbOther, '미상계 청구 전환액' => $unoffset,
                '반환채권' => $returns],
            formula: '청구 대상 음수 = min(0, 반환 반영 후 순액) − 상계 동의 없는 반환 − 미상계 선급금 청구 전환액',
            code: 'claim_negative_net = min(0, net_after_return) − clawback_no_consent − unoffset_claim − returns',
            ref: 'V2 §8.3 10단계 L288');
        $force = $end || $closed;
        $o['force_claim'] = $ctx->emit(self::STEP, 'force_claim', $force, $c, ...$kw,
            inputs: ['만료 · 해지 귀속월' => $end, '폐업' => $closed],
            formula: '강제 청구 트리거 = 계약 만료 · 해지 귀속월 또는 폐업 확인', ref: 'V2 L292 · V1 L568');
        $issued = $cnn < 0 && (dabs($cnn) > dabs($limit) || $force);
        $o['claim_issued_yn'] = $ctx->emit(self::STEP, 'claim_issued_yn', $issued, $c, ...$kw,
            inputs: ['청구 대상 음수' => $cnn, 'min_claim_limit' => $limit, '강제' => $force],
            formula: '음수 < 0 AND (|음수| > |min_claim_limit| OR 강제 청구 트리거)',
            code: 'claim_issued = cnn < 0 and (abs(cnn) > abs(limit) or force)',
            ref: 'V2 §8.3 표 10단계 L177 · L292 · V1 L570');
        if ($cnn < 0) {
            $ctx->emit(self::STEP, 'abs_le_min_claim_limit', dabs($cnn) <= dabs($limit), $c, ...$kw,
                inputs: ['청구 대상 음수' => $cnn, 'min_claim_limit' => $limit],
                formula: '|음수| ≤ |min_claim_limit|(같으면 이월)', ref: 'V1 §7.3 L570 · SPEC 15.2');
        }
        $o['claim_amount'] = $ctx->emit(self::STEP, 'claim_amount', $issued ? neg($cnn) : D(0), $c, ...$kw,
            formula: '청구 · 반환채권 확정액', ref: 'V2 L292');
        $o['claim_evaluated'] = $ctx->emit(self::STEP, 'claim_evaluated', $cnn < 0, $c, ...$kw,
            formula: '청구 판정 대상(청구 대상 음수 < 0)', ref: 'V2 §8.3 10단계');
        $carry = [];
        if ($cnn < 0 && !$issued) {
            $negNew = dmin(D(0), $after);
            $lines = array_values(array_filter($p->lines, fn($l) => in_array($l['origin'], ['NEW', 'ADJUSTMENT'], true)));
            $keyLn = $lines ? min_by($lines, fn($x) => $x['pre_tax_payable']) : null;
            if ($negNew < 0) {
                $carry[] = self::carryRow($ctx, $c, $pid, 'PRE_TAX', $negNew, $keyLn, '청구 이월(원거래 지급 · 세무 경로 미확정)');
            }
            $post = sub($cnn, $negNew);
            if ($post < 0) {
                $carry[] = self::carryRow($ctx, $c, $pid, 'POST_TAX', $post, $keyLn, '청구 이월(기지급 반환채권 · 전속계약금 반환)');
            }
            foreach ($carry as $r) {
                $ctx->emit(self::STEP, 'claim_carry', $r['carryover_amount'], $c, payee: $pid, line: pystr($r['pipeline_id']),
                    inputs: ['account_type' => $r['account_type']],
                    formula: '정상 유지 계약의 소액 음수: 청구서 미발행, 이월 원장에 청구 이월(계정은 세무 상태로)',
                    ref: 'V2 L294~295 · V1 L572');
            }
            $r0 = $carry[0];
            $ctx->emit(self::STEP, 'claim_carry_type', '청구 이월', $c, ...$kw, formula: '이월 사유', ref: 'V1 L572');
            $ctx->emit(self::STEP, 'claim_carry_account_type', $r0['account_type'], $c, ...$kw, formula: '이월 계정(세무 상태)', ref: 'V2 L295');
            $ctx->emit(self::STEP, 'claim_carry_pipeline_id', $r0['pipeline_id'], $c, ...$kw, formula: '이월 행 정산 입력 구분', ref: 'V1 §7.4');
            $ctx->emit(self::STEP, 'claim_carry_income_category', $r0['income_category'], $c, ...$kw, formula: '이월 행 소득 구분',
                ref: 'V1 §7.4');
        }
        $o['claim_carry_rows'] = $carry;
        $o['consignment_balance_rows'] = $consRows;
        $o['december_review_flag'] = (bool)$carry && str_ends_with($ctx->month, '-12');
        $ch = [];
        foreach ($p->lines as $l) {
            foreach ((either(g($l, 'correction_channels'), [])) as $x) {
                $ch[] = $x;
            }
        }
        if ($issued && $ch) {
            $ctx->emit(self::STEP, 'correction_channel', $ch[0], $c, ...$kw, formula: '반환 · 정정 채널(matrix_case_id → 10.4 채널)',
                ref: 'V2 L290 · §10.4');
        }
        $carryAt = either($t['carry_pre_tax_after_tax_total'] ?? null, D(0));
        $payable = add(dmax(D(0), $after), $carryAt);
        $o['payable_net_for_payout'] = $ctx->emit(self::STEP, 'payable_net_for_payout', $payable, $c, ...$kw,
            inputs: ['max(0, 반환 반영 후 순액)' => dmax(D(0), $after), '원귀속 PRE_TAX 세후 환산액' => $t['carry_pre_tax_after_tax_total'] ?? null],
            formula: '지급 판정 전달 당월 지급채무 순액 = max(0, 반환 반영 후 순액) + 원귀속 PRE_TAX 세후 환산액',
            code: 'payable_net_for_payout = max(0, net_after_return) + Σcarry_pre_tax_after_tax', ref: 'V2 §8.3 10단계 L289');
        $o['protected_crossed_with_claim'] = $ctx->emit(self::STEP, 'protected_crossed_with_claim',
            $payable < either($t['net_settle_protected'] ?? null, D(0)) && $unoffset > 0, $c, ...$kw,
            formula: '미상계 선급금 청구 전환액이 비상계 보호 지급액과 교차 상계되었는가(되면 안 됨)', ref: 'V2 L287 · D-11');
        $o['prepay_ledger_status_on_lock'] = $unoffset > 0 ? 'CLAIMED_ON_TERMINATION' : null;
        if ($unoffset > 0) {
            $ctx->emit(self::STEP, 'prepay_ledger_status_on_lock', 'CLAIMED_ON_TERMINATION', $c, ...$kw,
                formula: '만료 · 해지 미상계 잔액 → 청구 전환, 마감 시 CLAIMED_ON_TERMINATION 0원 종결', ref: 'V1 L328');
            $ctx->emit(self::STEP, 'prepay_ledger_balance_after', D(0), $c, ...$kw, formula: '청구 전환 후 선급금 원장 잔액(마감 시)',
                ref: 'V1 L328');
        }
        if ($pp && $pid === $pp['payee']) {
            $ctx->ledgers['prepayment_ledger'][] = [
                'contract_id' => $c->id, 'offset_amount' => $pp['amount'] ?? D(0),
                'balance_after' => $unoffset > 0 ? D(0) : $c->prepay_balance_after,
                'status' => $unoffset > 0 ? 'CLAIMED_ON_TERMINATION' : null];
        }
        unset($o);
    }

    private static function carryRow(Context $ctx, ContractState $c, $pid, string $account, Number $amount, ?array $ln, string $reason): array
    {
        $key = either(g($ln ?? [], 'line_key'), []);
        return ['ledger_id' => null, 'action' => 'NEW', 'rights_holder_id' => $c->holder_id, 'payee_id' => $pid, 'contract_id' => $c->id,
            'origin_month' => $ctx->month, 'account_type' => $account, 'pipeline_id' => either(g($key, 'pipeline_id'), 'MIXED'),
            'consignment_balance_yn' => false, 'income_category' => g($key, 'income_category'),
            'income_clause' => g($key, 'income_clause'), 'tax_threshold_unit_key' => g($key, 'tax_threshold_unit_key'),
            'carryover_reason' => $reason, 'carryover_amount' => $amount, 'first_occurred_month' => $ctx->month,
            'first_payable_confirmed_month' => null, 'payout_reservation_status' => 'NONE', 'extinguished_yn' => false];
    }
}

final class S11Payout
{
    const STEP = 'PAYOUT';

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $end = $c->endInMonth($ctx->month);
            $closed = truthy(g($ctx->holder($c->holder_id), 'business_closed_yn'));
            $limit = D(g($c->row, 'min_payout_limit') !== null ? g($c->row, 'min_payout_limit') : $ctx->p('default_min_payout_limit'));
            foreach ($c->payees as $p) {
                self::payoutPayee($ctx, $c, $p, $end, $closed, $limit);
            }
            self::cashPaid($ctx, $c);
            self::applyResults($ctx, $c);
        }
    }

    /** 지원금 원장 cash_paid_total: 실제 지급 이력 기준 — 지급 확정 시 P5.1 라인 세후액을 가산(예정, SPEC 8.3). */
    private static function cashPaid(Context $ctx, ContractState $c): void
    {
        foreach ($c->support as $row) {
            $aid = $row['agreement_id'];
            $month = D(0);
            foreach ($c->payees as $p) {
                if (truthy($p->out['PAYOUT']['payout_confirmed_yn'] ?? null)) {
                    // 환불 · 공제로 음수가 된 라인은 지급 누계를 되돌리지 않는다(V2 8.3 5단계 '실제 지급 누계는 되돌리지 않으며')
                    $month = add($month, dsum(array_map(fn($l) => dmax(D(0), either(g($l, 'net_settle_line'), D(0))),
                        array_filter($p->lines, fn($l) => $l['origin'] === 'NEW' && $l['line_id'] === '5.1:' . pystr($aid)))));
                }
            }
            $prev = g($row, 'cash_paid_total');
            if ($prev === null) {
                $ctx->issue('INPUT_MISSING', '지원금 ' . pystr($aid) . ' 전월 cash_paid_total 없음 — 0에서 누계', self::STEP, $c->holder_id,
                    'V2 L213 · SPEC 8.3');
            }
            $total = add(D($prev), $month);
            $ctx->emit(self::STEP, 'cash_paid_month', $month, $c, line: '5.1:' . pystr($aid), agreement: $aid,
                formula: "당월 지원금 현금 지급액 = 지급 확정된 P5.1 라인 세후 실정산액", ref: 'V2 L213 · V3 L65~67',
                provisional: true, note: "지급 확정 전 '예정' 값");
            $ctx->emit(self::STEP, 'cash_paid_total_after_payout', $total, $c, line: '5.1:' . pystr($aid), agreement: $aid,
                inputs: ['전월 cash_paid_total' => $prev, '당월 지급' => $month],
                formula: 'cash_paid_total = 전월 누계 + 당월 지원금 현금 지급액(실제 지급 이력 기준)', ref: 'V2 L213',
                provisional: true, note: "지급 확정 전 '예정' 값");
            foreach ($ctx->ledgers['support_fund_ledger'] as &$led) {
                if ($led['agreement_id'] === $aid) {
                    $led['cash_paid_total'] = $total;
                }
            }
            unset($led);
        }
    }

    private static function payoutPayee(Context $ctx, ContractState $c, PayeeState $p, bool $end, bool $closed, Number $limit): void
    {
        $pid = $p->payee_id;
        $kw = ['payee' => $pid];
        $o = &$p->out['PAYOUT'];
        $payable = either($p->out['CLAIM']['payable_net_for_payout'] ?? null, D(0));
        $prePos = array_values(array_filter($c->carry['pre_pos'], fn($r) => $r['payee_id'] === $pid));
        $postPos = array_values(array_filter($c->carry['post_pos'], fn($r) => $r['payee_id'] === $pid));
        $postTotal = dsum(array_map(fn($r) => $r['carryover_amount'], $postPos));
        $reasons = [];
        $firsts = [];
        foreach (array_merge($prePos, $postPos) as $r) {
            if (truthy(g($r, 'first_payable_confirmed_month'))) {
                $firsts[] = $r['first_payable_confirmed_month'];
            }
        }
        if ($firsts) {
            $mn = $firsts[0];
            foreach ($firsts as $f) {
                if (pycmp($f, $mn) < 0) {
                    $mn = $f;
                }
            }
        }
        if ($firsts && months_between(head(pystr($mn), 7), $ctx->month) >= (int)$ctx->p('carryover_max_months')) {
            $reasons[] = 'SIX_MONTHS';
            $ctx->issue('CANON_GAP', '6개월 경과 산정 — 월 차이 ≥ 6으로 판정(잠정)', self::STEP, $c->holder_id, 'V1 L562', 'Q-20');
        }
        if ((int)substr($ctx->month, 5, 2) === (int)$ctx->p('carryover_force_settle_month')) {
            $reasons[] = 'DECEMBER';
        }
        if ($end) {
            $reasons[] = 'CONTRACT_END';
        }
        if ($closed) {
            $reasons[] = 'BUSINESS_CLOSED';
        }
        $force = (bool)$reasons;
        $evaluated = $payable > 0 || (bool)$prePos || (bool)$postPos || $force;
        $judge = $ctx->emit(self::STEP, 'payout_judgement_amount', add($payable, $postTotal), $c, ...$kw,
            inputs: ['당월 지급채무 순액' => $payable, 'POST_TAX 지급대기액' => $postTotal],
            formula: '판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액(VAT 포함 총액 기준)',
            code: 'judgement = payable_net_for_payout + Σcarry_post_tax_pos', ref: 'V2 §8.3 11단계 L302 · L304');
        $internal = truthy(g($ctx->holder($pid), 'is_internal'));
        $confirmed = $evaluated && ($judge >= $limit || $force);
        $o = array_merge($o, ['evaluated' => $evaluated, 'carry_post_tax_pos_total' => $postTotal, 'payout_judgement_amount' => $judge,
            'min_payout_limit' => $limit, 'force_settle' => $force, 'force_settle_reasons' => $reasons,
            'payout_threshold_basis' => $ctx->p('payout_threshold_basis'), 'excluded_from_bulk_transfer' => $internal]);
        $ctx->emit(self::STEP, 'evaluated', $evaluated, $c, ...$kw,
            inputs: ['지급채무 순액 > 0' => $payable > 0, '이월 대기' => (bool)($prePos || $postPos), '강제' => $force],
            formula: '평가 대상 = 지급채무 순액 > 0 또는 PRE_TAX · POST_TAX 지급 대기 또는 강제 정산 트리거', ref: 'V2 L300');
        $ctx->emit(self::STEP, 'force_settle', $force, $c, ...$kw, inputs: ['reasons' => $reasons],
            formula: '강제 정산 = 최초 지급 대상 확정 후 6개월 경과 · 12월 · 계약 만료 · 해지 · 폐업', ref: 'V1 L561~565');
        $o['payout_confirmed_yn'] = $ctx->emit(self::STEP, 'payout_confirmed_yn', $confirmed, $c, ...$kw,
            inputs: ['판정 금액' => $judge, 'min_payout_limit' => $limit, '강제' => $force],
            formula: '판정 금액 ≥ min_payout_limit 또는 강제 정산 트리거 → 지급 확정(같으면 지급)',
            code: 'payout_confirmed = judgement >= min_payout_limit or force_settle',
            ref: 'V2 §8.3 표 11단계 L178 · V1 §7.3');
        $o['payout_amount'] = $ctx->emit(self::STEP, 'payout_amount', $confirmed ? $judge : D(0), $c, ...$kw,
            formula: '지급 확정액(대량이체 리스트, 부가세 · 원천세 · 상계 재가감 금지)', ref: 'V2 L303');
        $ctx->emit(self::STEP, 'excluded_from_bulk_transfer', $internal, $c, ...$kw,
            formula: '자사 권리자(TX-01)는 증빙 · 대량이체 제외', ref: 'V2 L280 · TAX.md TX-01');
        $rows = [];
        if ($confirmed) {
            foreach (array_merge($prePos, $postPos) as $r) {
                $rows[] = array_merge($r, ['action' => 'RESERVE', 'payout_reservation_status' => 'RESERVED']);
            }
        } elseif ($evaluated) {
            foreach ($p->lines as $ln) {
                if (in_array($ln['origin'], ['NEW', 'ADJUSTMENT'], true) && $ln['pre_tax_payable'] > 0) {
                    $key = $ln['line_key'];
                    $rows[] = ['ledger_id' => null, 'action' => 'NEW', 'rights_holder_id' => $c->holder_id, 'payee_id' => $pid,
                        'contract_id' => $c->id, 'origin_month' => $ctx->month, 'account_type' => 'PRE_TAX',
                        'pipeline_id' => g($key, 'pipeline_id'), 'consignment_balance_yn' => false,
                        'income_category' => g($key, 'income_category'), 'income_clause' => g($key, 'income_clause'),
                        'tax_threshold_unit_key' => g($key, 'tax_threshold_unit_key'),
                        'carryover_reason' => '지급 하한 미달', 'carryover_amount' => $ln['pre_tax_payable'],
                        'components' => ['split_amount' => $ln['split_amount'], 'offset_amount' => $ln['offset_amount'],
                            'vat_amount' => g($ln, 'vat_amount')],
                        'first_occurred_month' => $ctx->month, 'first_payable_confirmed_month' => null,
                        'payout_reservation_status' => 'NONE', 'extinguished_yn' => false];
                }
            }
            foreach (array_merge($prePos, $postPos) as $r) {
                $rows[] = array_merge($r, ['action' => 'KEEP']);
            }
            foreach ($rows as $r) {
                if ($r['action'] === 'NEW') {
                    $ctx->issue('CANON_GAP', '지급 이월 적재 구성요소(VAT · 상계) 보존 방식 정본 없음 — 라인별 세전 기초금액 + 구성요소',
                        self::STEP, $c->holder_id, 'V2 L305', 'Q-21');
                    break;
                }
            }
        }
        $load = dsum(array_map(fn($r) => $r['carryover_amount'], array_filter($rows, fn($r) => $r['action'] === 'NEW')));
        $ctx->emit(self::STEP, 'carry_load', $load, $c, ...$kw, formula: '지급 이월 신규 적재액(PRE_TAX 기초금액)', ref: 'V2 L305',
            provisional: truthy($load), note: truthy($load) ? 'Q-21' : '');
        $o['payout_carry_rows'] = $rows;
        $o['carry_load'] = $load;
        unset($o);
    }

    /** 마감 후 대량이체 결과(있을 때만): 성공 → SETTLED, 실패 → RESERVED → NONE + 지급 실패 이월(V1 L589, D-13). */
    private static function applyResults(Context $ctx, ContractState $c): void
    {
        foreach ($ctx->input['payout_results'] as $res) {
            foreach ((either(g($res, 'ledger_ids'), [])) as $lid) {
                $r = null;
                foreach ($ctx->input['carryover_ledger'] as $x) {
                    if (g($x, 'ledger_id') === $lid && $x['contract_id'] === $c->id) {
                        $r = $x;
                        break;
                    }
                }
                if (!$r) {
                    continue;
                }
                $act = $res['result'] === 'SUCCESS' ? 'SETTLE' : 'RELEASE';
                $ctx->ledgers['carryover_ledger'][] = array_merge($r, ['action' => $act,
                    'payout_reservation_status' => $act === 'SETTLE' ? 'SETTLED' : 'NONE',
                    'extinguished_yn' => $act === 'SETTLE', 'extinguished_month' => $act === 'SETTLE' ? $ctx->month : null]);
                $ctx->emit(self::STEP, 'payout_result', $act, $c, payee: g($res, 'payee_id'), ref_id: $lid,
                    formula: '이체 성공 → SETTLED(소멸) / 실패 → RESERVED → NONE 해제(차월 기초 세전 이월 잔액에 자동 복귀)',
                    ref: 'V1 L589 · L591');
            }
        }
    }
}

final class S12CloseCheck
{
    const STEP = 'CLOSE_CHECK';

    public static function run(Context $ctx): void
    {
        self::pendingAdjustments($ctx);
        $prevGiven = [];
        foreach ($ctx->input['carryover_prev_end_balances'] as $r) {
            $prevGiven[tkey($r['account_type'], $r['key'])] = D($r['amount']);
        }
        foreach ($ctx->contracts as $c) {
            $state = []; // ledger_id → [acct, key, amount](당월 말 상태)
            $prev = [];
            $bump = function (array &$m, $acct, $key, Number $v) {
                $k = tkey($acct, $key);
                $m[$k] = add($m[$k] ?? D(0), $v);
            };
            foreach ($ctx->input['carryover_ledger'] as $r) {
                if ($r['contract_id'] !== $c->id || truthy(g($r, 'extinguished_yn'))
                    || either(g($r, 'payout_reservation_status'), 'NONE') !== 'NONE') {
                    continue;
                }
                $acct = truthy(g($r, 'consignment_balance_yn')) ? 'CONSIGNMENT' : g($r, 'account_type');
                $key = $acct === 'CONSIGNMENT' ? $c->id : either(either(g($r, 'payee_id'), g($r, 'rights_holder_id')), $c->holder_id);
                $bump($prev, $acct, $key, D($r['carryover_amount']));
                $state[tkey($r['ledger_id'])] = [$acct, $key, D($r['carryover_amount'])];
            }
            $new = [];
            $ext = [];
            $rowsNew = [];
            foreach ($c->payees as $p) {
                foreach (array_merge($p->out['PAYOUT']['payout_carry_rows'] ?? [], $p->out['CLAIM']['claim_carry_rows'] ?? []) as $r) {
                    $acct = $r['account_type'];
                    if ($r['action'] === 'NEW') {
                        $bump($new, $acct, $r['payee_id'], $r['carryover_amount']);
                        $rowsNew[] = [$acct, $r['payee_id'], $r['carryover_amount']];
                    } elseif ($r['action'] === 'RESERVE') {
                        $bump($ext, $acct, $r['payee_id'], $r['carryover_amount']);
                        unset($state[tkey(g($r, 'ledger_id'))]);
                    }
                    $ctx->ledgers['carryover_ledger'][] = $r;
                }
                foreach ($p->out['CLAIM']['consignment_balance_rows'] ?? [] as $r) {
                    $bump($new, 'CONSIGNMENT', $c->id, $r['carryover_amount']);
                    $rowsNew[] = ['CONSIGNMENT', $c->id, $r['carryover_amount']];
                    $ctx->ledgers['carryover_ledger'][] = $r;
                }
            }
            if ($c->carry['cons_rows']) { // 위탁 전용 잔액은 4단계에서 전액 상쇄 투입 — 원잔액 부호 그대로 변동 기록(D-8)
                $bump($ext, 'CONSIGNMENT', $c->id, $c->carry['cons']);
                foreach ($c->carry['cons_rows'] as $r) {
                    unset($state[tkey(g($r, 'ledger_id'))]);
                    $ctx->ledgers['carryover_ledger'][] = array_merge($r, ['action' => 'REDUCE', 'extinguished_yn' => true,
                        'extinguished_month' => $ctx->month]);
                }
            }
            $end = [];
            foreach ($state as [$acct, $key, $amt]) {
                $bump($end, $acct, $key, $amt);
            }
            foreach ($rowsNew as [$acct, $key, $amt]) {
                $bump($end, $acct, $key, $amt);
            }
            $keys = array_unique(array_merge(array_keys($prev), array_keys($new), array_keys($ext), array_keys($end)));
            $keys = sort_by($keys, function ($k) {
                [$a, $b] = untkey($k);
                return [pystr($a), pystr($b)];
            });
            foreach ($keys as $k) {
                [$acct, $key] = untkey($k);
                $pe = $prevGiven[$k] ?? ($prev[$k] ?? D(0));
                [$n, $x, $e] = [$new[$k] ?? D(0), $ext[$k] ?? D(0), $end[$k] ?? D(0)];
                $ok = bccomp(sub(add($pe, $n), $x)->value, $e->value, WORK) === 0;
                $ctx->continuity[] = ['account_type' => $acct, 'key' => $key, 'prev_end' => $pe, 'new' => $n, 'extinguished' => $x,
                    'end' => $e, 'ok' => $ok];
                $ctx->emit(self::STEP, 'continuity_' . pystr($acct), $e, $c, payee: $acct === 'CONSIGNMENT' ? null : $key, line: $acct,
                    inputs: ['전월 말' => $pe, '당월 신규' => $n, '당월 소멸 · 변동' => $x, '당월 말(원장 갱신 결과)' => $e, 'ok' => $ok],
                    formula: '전월 말 잔액 + 당월 신규 − 당월 소멸(위탁은 원잔액 부호 변동) = 당월 말 잔액',
                    code: 'prev_end + new − extinguished == end', ref: 'V1 §7.4 L588~595');
                $ctx->emit(self::STEP, 'continuity_' . pystr($acct) . '_ok', $ok, $c, payee: $acct === 'CONSIGNMENT' ? null : $key, line: $acct,
                    formula: '이월 연속성 등식 일치(불일치면 마감 차단)', ref: 'V1 §7.4 L588~595');
                if ($acct === 'CONSIGNMENT') {
                    $ctx->emit(self::STEP, 'consignment_movement', $x, $c, line: $acct,
                        formula: '위탁 상쇄 · 정정 변동(제거되는 원잔액의 부호 그대로)', ref: 'V1 §7.4 · V4 D-8 L290');
                }
            }
        }
    }

    /**
     * 전월 정산 조정 라인 기록(V2 §10.2). 기본 apply = 8단계(세전 · 위탁) · 10단계(세후)에서 이미 계산에 넣었다
     * (2026-10-27 white 결정, SPEC Q-23 해소) → applied_adjustments. hold면 계산에 넣지 않고 pending_adjustments로만.
     */
    private static function pendingAdjustments(Context $ctx): void
    {
        $mode = Adjust::mode($ctx);
        $rows = Adjust::monthAdjustments($ctx);
        if (!$rows) {
            return;
        }
        $th = $ctx->p('manual_adj_approval_threshold');
        $twoStep = truthy($ctx->p('adj_two_step_approval_yn')); // 1차 오픈 false(D-SETT-01) — 2차 릴리스에서 금액 구간별 2단계 승인
        foreach ($rows as $a) {
            $over = $th !== null && dabs(D($a['adj_amount'])) > D($th);
            $row = array_merge($a, ['requires_second_approval' => $twoStep && $over,
                'approval_mode' => $twoStep ? 'TWO_STEP' : 'SINGLE_FINANCE_1ST',
                'applied_step' => $mode === 'apply' ? (Adjust::account($a) === 'POST_TAX' ? 'CLAIM' : 'PAYEE_SPLIT') : null]);
            if ($mode === 'apply') {
                $ctx->applied_adjustments[] = $row;
            } else {
                $ctx->pending_adjustments[] = $row;
            }
            $ctx->trace->add(self::STEP, 'requires_second_approval', $row['requires_second_approval'], holder: null,
                contract: g($a, 'contract_id'), payee: g($a, 'payee_id'), line: g($a, 'adj_id'), ref_id: g($a, 'adj_id'),
                inputs: ['adj_amount' => $a['adj_amount'], 'manual_adj_approval_threshold' => $th,
                    '임계액 초과' => $over, 'adj_two_step_approval_yn' => $twoStep],
                formula: '1차 오픈: 금액과 관계없이 재무 담당자 단독 확정 / 2차: 임계액 초과 시 재무 책임자 2차 승인',
                code: 'requires_second_approval = adj_two_step_approval_yn and |adj_amount| > threshold',
                ref: 'V2 §10.3 L370~371 · D-SETT-01(2026-10-27)');
            if ($mode !== 'apply') {
                $ctx->trace->add(self::STEP, 'pending_adjustment', D($a['adj_amount']), holder: null, contract: g($a, 'contract_id'),
                    payee: g($a, 'payee_id'), ref_id: g($a, 'adj_id'),
                    inputs: ['origin_month' => g($a, 'origin_month'), 'account_type' => g($a, 'account_type'),
                        'adj_reason_code' => g($a, 'adj_reason_code')],
                    formula: 'adjustment_mode = hold — 전월 정산 조정 라인을 계산에 넣지 않고 출력만',
                    ref: 'V2 §10.2 L362', output: false);
            }
        }
    }
}

final class S13PassRefundPayout
{
    const STEP = 'PASS_REFUND_PAYOUT';
    const REF = '통합 설계서 S6 L438~446 · S-02 · S-14(2026-10-27) · 소득세법 제21조 · 제84조 · 제164조';

    public static function run(Context $ctx): void
    {
        $rows = [];
        foreach ($ctx->input['pass_refund_payouts'] as $r) {
            $rows[] = self::one($ctx, $r);
        }
        $ctx->pass_refund_payouts = $rows;
    }

    private static function one(Context $ctx, array $r): array
    {
        [$pid, $sid] = [$r['pass_refund_id'], g($r, 'student_id')];
        $kw = ['holder' => null, 'contract' => null, 'payee' => $sid, 'line' => $pid, 'ref_id' => g($r, 'order_id')];
        [$pkg, $book, $ship] = [D(g($r, 'package_paid_amount')), D(g($r, 'book_paid_amount')), D(g($r, 'shipping_fee'))];
        $base = $ctx->emit(self::STEP, 'refund_base', sub(sub($pkg, $book), $ship), ...$kw,
            inputs: ['패키지 실결제액' => $pkg, '포함 교재 실결제액' => $book, '배송비' => $ship],
            formula: '환급 기준 모수 = 패키지 실결제액 − 포함 교재 실결제액(최대 10% 기본할인가) − 배송비',
            code: 'refund_base = package_paid − book_paid − shipping', ref: '통합 설계서 S6 L444');
        $snap = g($r, 'target_progress_rate_snapshot');
        $progress = g($r, 'progress_rate');
        $eligible = null;
        if ($snap !== null && $progress !== null) {
            $eligible = D($progress) >= D($snap);
            $ctx->emit(self::STEP, 'progress_eligible', $eligible, ...$kw,
                inputs: ['진도율' => $progress, '결제 시점 목표 진도율(박제)' => $snap,
                    '현재 상품 설정(참고, 판정에 쓰지 않음)' => g($r, 'current_target_progress_rate')],
                formula: '환급 판정은 결제 승인 시점에 주문 라인에 박제한 목표 진도율 기준 — 판매 후 설정 변경은 소급하지 않음',
                code: 'eligible = progress_rate >= target_progress_rate_snapshot',
                ref: '통합 설계서 L251 · L438 · S-14(2026-10-27)');
        }
        $exempt = $base <= D($ctx->p('other_income_min_tax_amount'));
        $ctx->emit(self::STEP, 'threshold_exempt_yn', $exempt, ...$kw,
            inputs: ['기타소득금액(필요경비 의제 없음)' => $base, '과세최저한' => $ctx->p('other_income_min_tax_amount')],
            formula: '기타소득금액(= 환급금, 필요경비 의제 없음) 건별 5만 원 이하면 과세최저한 비과세',
            ref: '통합 설계서 L444 · 소득세법 제84조');
        if ($exempt) {
            $it = $lt = D(0);
            $itRaw = $ltRaw = null;
        } else {
            $itRaw = mul($base, D('0.20'));
            $it = floor_won($itRaw);
            $ltRaw = mul($it, D(pystr($ctx->p('local_income_tax_rate'))));
            $lt = floor_won($ltRaw);
        }
        $ctx->emit(self::STEP, 'income_tax', $it, ...$kw, inputs: ['기타소득금액' => $base],
            formula: '소득세 = 내림(기타소득금액 × 20%)', code: 'floor(base × 0.20)', before: $itRaw,
            rounding: $itRaw !== null ? 'FLOOR_WON' : 'NONE', ref: self::REF);
        $ctx->emit(self::STEP, 'local_income_tax', $lt, ...$kw, inputs: ['소득세' => $it],
            formula: '지방소득세 = 내림(소득세 × 10%)(합산 22% 한 번에 곱하지 않음)', code: 'floor(income_tax × 0.10)',
            before: $ltRaw, rounding: $ltRaw !== null ? 'FLOOR_WON' : 'NONE', ref: self::REF);
        $net = $ctx->emit(self::STEP, 'net_payout', sub(sub($base, $it), $lt), ...$kw, inputs: ['환급금' => $base, '원천세' => add($it, $lt)],
            formula: '세후 실지급액 = 환급금 − 기타소득세(소득세 + 지방소득세)', ref: self::REF);
        $ctx->emit(self::STEP, 'income_clause', 'C17', ...$kw,
            formula: '합격환급금 = 기타소득 사례금(소득세법 제21조 제1항 제17호) — 필요경비 의제 없음, 소득세 20%',
            ref: '소득세법 제21조 ① 17호 · white 결정(2026-10-27) · tax_table.json C17');
        $ctx->emit(self::STEP, 'statement_form', '기타소득 지급명세서(연 1회, 다음 해 2월 말일) — 간이지급명세서 대상 아님', ...$kw,
            formula: 'C17은 간이지급명세서 대상 아님, 기타소득 지급명세서 연 1회', ref: 'TAX.md TX-04 C17 · L57');
        $ctx->emit(self::STEP, 'rrn_required', true, ...$kw, formula: '주민등록번호는 신청 때 항상 받는다(번호만 · 암호화 보관)',
            ref: '통합 설계서 L440 · S-02(2026-10-27)');
        $stmt = $ctx->emit(self::STEP, 'payment_statement_required', !$exempt, ...$kw,
            formula: '기타소득 지급명세서 제출 — 과세최저한으로 과세되지 않은 건은 면제',
            ref: '소득세법 제164조 · 시행령 제214조 ① 3호 · 시행규칙 제97조 · S-02');
        $okRrn = truthy(g($r, 'rrn_entered')) && truthy(g($r, 'rrn_matched', true));
        $status = ($okRrn && $eligible !== false) ? 'APPROVABLE' : (!$okRrn ? 'SUPPLEMENT_REQUEST' : 'REJECT');
        $ctx->emit(self::STEP, 'review_status', $status, ...$kw,
            inputs: ['주민번호 입력' => g($r, 'rrn_entered'), '본인인증 대조' => g($r, 'rrn_matched'), '진도율 충족' => $eligible],
            formula: '주민등록번호 미입력 · 대조 불일치는 [보완 요청], 진도율 기준 미달은 [반려], 그 밖은 승인 가능',
            ref: '통합 설계서 L440~441 · S-02 · S-03 · S-21');
        return ['pass_refund_id' => $pid, 'student_id' => $sid, 'income_clause' => 'C17', 'refund_base' => $base, 'progress_eligible' => $eligible,
            'threshold_exempt_yn' => $exempt, 'income_tax' => $it, 'local_income_tax' => $lt, 'withholding_total' => add($it, $lt),
            'net_payout' => $net, 'rrn_required' => true, 'payment_statement_required' => $stmt, 'review_status' => $status];
    }
}
