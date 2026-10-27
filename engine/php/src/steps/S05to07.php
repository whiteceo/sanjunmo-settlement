<?php
/**
 * 5단계 SUPPORT_CAP · 6단계 PREPAY_OFFSET · 7단계 LUMPSUM_ADD.
 *
 * 5 SUPPORT_CAP(V2 §8.3 표 L172 · 본문 L204~214, V1 §5.2, SPEC 8절):
 *   CAPPED: 복원 후 한도 = 총한도 − 소진액 + 복원액, 신규 확정액 = min(신규 발생액, 복원 후 한도),
 *           지급 대상 확정액 = 신규 확정액 − 4단계 P5.1 공제액. 누계는 전월 말 원장(prev)에 당월분만 반영.
 *   UNLIMITED: 확정액 = 신규 발생액 − 공제액(한도 판정 · 소진액 · COMPLETED 전이 생략). 절사 없음.
 * 6 PREPAY_OFFSET(V2 §8.3 표 L173 · 본문 L215~236, V1 §5.3 · §7.1, SPEC 9절):
 *   적격 세전액(동일 계약 · 원 권리자 라인만) → 상계 가능액 = 적격 세전액 − 예상 원천세(LOAN) / 0(EARNED),
 *   당월 상계액 = min(상계 가능액, 미상계 잔액). 라인별 안분: 적격액 오름차순(동률 시 P1.1 뒤) 선행 floor, 최대 라인 역산.
 * 7 LUMPSUM_ADD(V2 §8.3 표 L174 · 본문 L237~244, SPEC 10절): 당월 귀속 · 승인 비정기 가산금. 절사 없음.
 */

namespace SettleCalc;

use BcMath\Number;

final class S05SupportCap
{
    const STEP = 'SUPPORT_CAP';

    public static function run(Context $ctx): void
    {
        $prevRows = [];
        foreach ($ctx->input['support_fund_ledger_prev'] as $r) {
            $prevRows[tkey($r['agreement_id'])] = $r;
        }
        $agrs = [];
        foreach ($ctx->input['support_fund_agreements'] as $a) {
            $agrs[tkey($a['agreement_id'])] = $a;
        }
        foreach ($ctx->contracts as $c) {
            $rows = [];
            $lines = $c->linesOf('5.1');
            $c->stepOut(self::STEP);
            $ctx->emit(self::STEP, 'applicable', (bool)$lines, $c, inputs: ['P5.1 agreements' => count($lines)],
                formula: '매출연동 개발지원금(Pipeline 5.1) 약정이 있는 계약만 5단계 적용', ref: 'V2 §8.3 5단계 L204');
            foreach ($lines as $ln) {
                $agr = $agrs[tkey($ln->agreement_id)];
                $prev = $prevRows[tkey($ln->agreement_id)] ?? [];
                $rows[] = self::oneAgreement($ctx, $c, $ln, $agr, $prev);
            }
            $c->out[self::STEP] = $rows;
        }
    }

    private static function oneAgreement(Context $ctx, ContractState $c, Line $ln, array $agr, array $prev): array
    {
        $aid = $agr['agreement_id'];
        $kw = ['line' => $ln->label, 'agreement' => $aid];
        $new = $ln->new;
        $deduct = $ln->support_deduct;
        $status0 = g($agr, 'status');
        $capType = either(g($agr, 'cap_type'), 'CAPPED');
        if (!$prev) {
            $ctx->issue('INPUT_MISSING', '지원금 ' . pystr($aid) . ' 전월 말 원장(support_fund_ledger_prev) 없음 — 누계 0에서 시작',
                self::STEP, $c->holder_id, 'V2 §10.1 L356');
        }
        $pConsumed = D(g($prev, 'cap_consumed_amount'));
        $pNet = D(g($prev, 'confirmed_net_total'));
        $pCash = g($prev, 'cash_paid_total');
        $lumpSettle = dsum(array_map(fn($r) => D($r['amount']), array_filter($c->lumpsum_rows,
            fn($r) => g($r, 'item_kind') === 'LUMP_SETTLE' && g($r, 'agreement_id') === $aid)));
        $row = ['agreement_id' => $aid, 'cap_type' => $capType, 'accrued_amount' => $new, 'status_before' => $status0];
        if ($capType === 'UNLIMITED') {
            $confirmed = $ctx->emit(self::STEP, 'confirmed_amount', sub($new, $deduct), $c, ...$kw,
                inputs: ['신규 발생액' => $new, '4단계 P5.1 공제액' => $deduct],
                formula: 'UNLIMITED: 지급 대상 확정액 = 신규 발생액 − 4단계 P5.1 공제액(한도 판정 생략)',
                code: 'confirmed_amount = new_5_1 − deduct', ref: 'V2 §8.3 5단계 L205 · SPEC 8.2');
            $netTotal = $ctx->emit(self::STEP, 'confirmed_net_total', sub(add($pNet, $new), $deduct), $c, ...$kw,
                inputs: ['전월 순누계' => $pNet, '신규' => $new, '공제' => $deduct],
                formula: '확정액 순누계 = 전월 순누계 + 당월 신규 확정 − 공제', ref: 'V2 L213 · SPEC 8.2');
            $row = array_merge($row, ['restore_amount' => D(0), 'avail_cap' => null, 'new_confirmed' => $new,
                'expired_excess' => D(0), 'confirmed_amount' => $confirmed, 'confirmed_net_total' => $netTotal,
                'cap_consumed_amount' => null, 'remaining_cap' => null, 'lump_settle_applied' => $lumpSettle,
                'status_after' => $status0]);
        } else {
            $totalCap = D(g($agr, 'total_cap_amount'));
            $txs = $ln->support_txs ?? [];
            $restore = D(0);
            if (truthy(g($agr, 'cap_restore_on_refund'))) {
                $restore = dsum(array_map(fn($t) => dmin($t['deduct_5_1'], $t['unrefunded']), $txs));
            }
            $restore = $ctx->emit(self::STEP, 'restore_amount', $restore, $c, ...$kw,
                inputs: ['cap_restore_on_refund' => g($agr, 'cap_restore_on_refund'),
                    '원거래별 공제액' => array_map(fn($t) => $t['deduct_5_1'], $txs)],
                formula: '승인된 한도 복원액 = Σ min(원거래 공제액, 원거래 미환불 확정액)(cap_restore_on_refund일 때)',
                code: 'restore = Σ_tx min(tx.deduct_5_1, tx.unrefunded) if cap_restore_on_refund else 0',
                ref: 'V2 §8.3 5단계 1) L207~208', provisional: true, note: 'Q-24(자동 복원)');
            $avail = $ctx->emit(self::STEP, 'avail_cap', add(sub($totalCap, $pConsumed), $restore), $c, ...$kw,
                inputs: ['총한도' => $totalCap, '전월 소진액' => $pConsumed, '복원액' => $restore],
                formula: '복원 후 한도 = 총한도 − 소진액 + 복원액(cash_paid_total 사용 금지)',
                code: 'avail_cap = total_cap_amount − prev.cap_consumed_amount + restore',
                ref: 'V2 §8.3 표 5단계 L172 · 본문 2) L208');
            $active = $status0 === 'ACTIVE';
            $newConf = $ctx->emit(self::STEP, 'new_confirmed', $active ? dmin($new, $avail) : D(0), $c, ...$kw,
                inputs: ['신규 발생액' => $new, '복원 후 한도' => $avail, 'status' => $status0],
                formula: '신규 확정액 = min(신규 발생액, 복원 후 한도)(순수 신규에 한도 먼저)',
                code: 'new_confirmed = min(new_5_1, avail_cap) if status == ACTIVE else 0',
                ref: 'V2 §8.3 표 5단계 L172 · 본문 3) L209', provisional: !$active, note: $active ? '' : 'Q-25(월초 상태)');
            $excess = $ctx->emit(self::STEP, 'expired_excess', sub($new, $newConf), $c, ...$kw,
                inputs: ['신규 발생액' => $new, '신규 확정액' => $newConf],
                formula: '한도 초과분은 이월 없이 소멸', code: 'expired_excess = new_5_1 − new_confirmed',
                ref: 'V4 Case 9 L232 · V2 L209');
            $neg = sub($newConf, $deduct) < 0;
            $confirmed = $ctx->emit(self::STEP, 'confirmed_amount', sub($newConf, $deduct), $c, ...$kw,
                inputs: ['신규 확정액' => $newConf, '4단계 P5.1 공제액' => $deduct],
                formula: '지급 대상 확정액 = 신규 확정액 − 4단계 P5.1 공제액',
                code: 'confirmed_amount = new_confirmed − deduct', ref: 'V2 §8.3 표 5단계 L172 · 4) L210',
                provisional: $neg, note: $neg ? 'Q-11' : '');
            $consumed = $ctx->emit(self::STEP, 'cap_consumed_amount', add(sub(add($pConsumed, $newConf), $restore), $lumpSettle), $c, ...$kw,
                inputs: ['전월 소진액' => $pConsumed, '신규 확정액' => $newConf, '복원액' => $restore,
                    'LUMP_SETTLE 승인액' => $lumpSettle],
                formula: '소진액 = 전월 소진액 + 신규 확정액 − 복원액 + 종료 승인액(LUMP_SETTLE)',
                code: 'cap_consumed = prev + new_confirmed − restore + lump_settle_applied',
                ref: 'V2 §8.3 5단계 5) L211');
            $netTotal = $ctx->emit(self::STEP, 'confirmed_net_total', sub(add($pNet, $newConf), $deduct), $c, ...$kw,
                inputs: ['전월 순누계' => $pNet, '신규 확정액' => $newConf, '공제' => $deduct],
                formula: '확정액 순누계 = 전월 순누계 + 신규 확정액 − 공제액(복원 옵션과 무관)',
                code: 'confirmed_net_total = prev + new_confirmed − deduct', ref: 'V2 §8.3 5단계 5) L211');
            $remaining = $ctx->emit(self::STEP, 'remaining_cap', sub($totalCap, $consumed), $c, ...$kw,
                inputs: ['총한도' => $totalCap, '소진액' => $consumed],
                formula: '잔여 한도 = 총한도 − 소진액', code: 'remaining_cap = total_cap_amount − cap_consumed',
                ref: 'V1 §15.4 · V3 L65~67');
            $status1 = $status0;
            $end = period_end($agr, $c->row);
            if ($remaining <= 0 && $status0 === 'ACTIVE') {
                $status1 = 'COMPLETED';
            } elseif ($status0 === 'COMPLETED' && $remaining > 0 && (!truthy($end) || strcmp($ctx->month, (string)month_of($end)) <= 0)) {
                $status1 = 'ACTIVE';
            }
            $ctx->emit(self::STEP, 'status_after', $status1, $c, ...$kw, inputs: ['status_before' => $status0, 'remaining_cap' => $remaining],
                formula: '잔여 한도 0 → COMPLETED(차월 신규 중단) / COMPLETED이고 복원으로 잔여 > 0이며 종료월 이내 → ACTIVE',
                ref: 'V2 §8.3 5단계 L211~212');
            if (in_array($status0, ['EXPIRED', 'TERMINATED'], true)) {
                $status1 = $status0;
            }
            $row = array_merge($row, ['restore_amount' => $restore, 'avail_cap' => $avail, 'new_confirmed' => $newConf,
                'expired_excess' => $excess, 'confirmed_amount' => $confirmed, 'confirmed_net_total' => $netTotal,
                'cap_consumed_amount' => $consumed, 'remaining_cap' => $remaining, 'lump_settle_applied' => $lumpSettle,
                'status_after' => $status1]);
        }
        $ctx->emit(self::STEP, 'deduct_absorbed_by_expiry', bccomp(sub($row['new_confirmed'], $row['confirmed_amount'])->value,
                $deduct->value, WORK) !== 0, $c, ...$kw,
            inputs: ['신규 확정액' => $row['new_confirmed'], '확정액' => $row['confirmed_amount'], '공제' => $deduct],
            formula: '공제액이 한도 초과 소멸분에 흡수되지 않고 별도 차감되었는가(C-01 한도 캡 흡수 방지)',
            ref: 'V2 L160 · §15.1');
        $row['cash_paid_total'] = $pCash;
        $own = $ctx->own_holder[(string)$aid] ?? null;
        if ($own) {
            $row['own_distributable'] = $own['distributable'];
            $row['own_remaining'] = $ctx->emit(self::STEP, 'own_remaining', sub($own['distributable'], $row['confirmed_amount']), $c, ...$kw,
                inputs: ['자사 배분가능액' => $own['distributable'], '지원금 확정액' => $row['confirmed_amount']],
                formula: '자사 최종 잔여액 = 자사 배분가능액 − 지원금 확정액 합계',
                code: 'own_remaining = own_distributable − confirmed_amount', ref: 'V1 L262~264');
            if ($row['confirmed_amount'] > $own['distributable']) {
                $ctx->warn('SUPPORT_OVER_OWN', pystr($aid) . ' 지원금 확정액이 자사 배분가능액을 넘음', 'V1 L264');
            }
        }
        $ln->net = $row['confirmed_amount'];
        $ln->new_confirmed = $row['new_confirmed'];
        $c->support[tkey($aid)] = $row;
        $ctx->ledgers['support_fund_ledger'][] = [
            'agreement_id' => $aid, 'target_month' => $ctx->month, 'accrued_amount' => $new,
            'confirmed_amount' => $row['confirmed_amount'], 'confirmed_net_total' => $row['confirmed_net_total'],
            'cap_consumed_amount' => $row['cap_consumed_amount'], 'cash_paid_total' => $pCash,
            'remaining_cap' => $row['remaining_cap'],
            'status_change' => $row['status_after'] === $status0 ? null : pystr($status0) . '->' . pystr($row['status_after']),
            'settlement_line_id' => null];
        return $row;
    }
}

final class S06PrepayOffset
{
    const STEP = 'PREPAY_OFFSET';

    public static function attrs(Line $ln): array
    {
        return ['label' => $ln->label, 'pipeline_id' => $ln->pipeline_id, 'supply_nature' => $ln->supply_nature,
            'income_category' => $ln->income_category, 'income_clause' => $ln->income_clause,
            'tax_threshold_unit_key' => $ln->tax_threshold_unit_key, 'payee_is_author' => $ln->payee_is_author];
    }

    /** @return array<int, array{0: Line, 1: Number, 2: string}> */
    private static function eligibleLines(Context $ctx, ContractState $c): array
    {
        $out = [];
        foreach ($c->lines as $ln) {
            if (truthy($ln->fixed_payee)) { // 다른 수취인 금액 제외(L225)
                continue;
            }
            if ($ln->pipeline_id === '1.1') {
                $e = dmax(D(0), sub($ln->net, $ln->mmg_subsidy));
                $why = 'max(0, P1.1 순수신규 − 4단계 P1.1 공제) = max(0, net_1_1 − mmg_subsidy)';
            } elseif ($ln->pipeline_id === '2.1') {
                $e = dmax(D(0), $ln->net);
                $why = 'max(0, P2.1 순액)';
            } elseif ($ln->pipeline_id === '5.1' && $ln->offset_type === 'CONDITIONAL') {
                $e = dmax(D(0), $ln->net);
                $why = 'max(0, 상계허용 P5.1 확정액)';
            } elseif ($ln->pipeline_id === 'LUMPSUM' && $ln->conditional) {
                $e = $ln->net;
                $why = '상계허용 일시 · 분할 지원금 / 종료 일시정산';
            } else {
                continue;
            }
            $ln->eligible = $e;
            $out[] = [$ln, $e, $why];
        }
        return $out;
    }

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $pre = array_values(array_filter($ctx->input['prepayments'], fn($p) => $p['contract_id'] === $c->id));
            $out = &$c->stepOut(self::STEP);
            if (!$pre) {
                $out['applicable'] = $ctx->emit(self::STEP, 'applicable', false, $c, formula: '선급금 원장 없음 — 6단계 생략',
                    ref: 'V1 §5.3');
                $out['offset_amount'] = $ctx->emit(self::STEP, 'offset_amount', D(0), $c, formula: '선급금 원장 없음 — 당월 상계액 0원',
                    ref: 'V2 §8.3 6단계');
                unset($out);
                continue;
            }
            if (count($pre) > 1) {
                $ctx->warn('PREPAY_MULTI', pystr($c->id) . ' 선급금 원장 ' . count($pre) . '건 — 잔액 합산', 'V1 L319');
            }
            $types = array_unique(array_map(fn($p) => $p['prepayment_tax_type'], $pre));
            if (count($types) > 1) {
                $ctx->stop('INPUT_ERROR', 'PREPAY_TAX_TYPE_MIXED', pystr($c->id) . ' 선급금 세무 유형 혼재 금지', 'V1 L319');
            }
            foreach ($ctx->input['payee_splits'] as $s) {
                if ($s['contract_id'] === $c->id) {
                    $ctx->stop('INPUT_ERROR', 'PREPAY_WITH_PAYEE_SPLIT', pystr($c->id) . ' 선급금과 수취인 분할 동시 존재 금지', 'V1 L323');
                }
            }
            $ptype = $pre[0]['prepayment_tax_type'];
            $bal = dsum(array_map(fn($p) => D($p['prepay_unoffset_balance']), $pre));
            $payee = either(g($pre[0], 'offset_payee_id'), $c->holder_id);
            $c->prepay = ['type' => $ptype, 'balance' => $bal, 'payee' => $payee, 'rows' => $pre];
            $out['applicable'] = $ctx->emit(self::STEP, 'applicable', true, $c, inputs: ['prepayment_tax_type' => $ptype]);
            $out['prepayment_tax_type'] = $ptype;
            $out['prepay_balance_before'] = $ctx->emit(self::STEP, 'prepay_balance_before', $bal, $c,
                formula: '미상계 선급금 잔액(전월 말)', ref: 'V1 §5.3');
            unset($out);
            self::compute($ctx, $c, true);
        }
    }

    /** 1차 산정(first) 또는 9단계 재검증 후 상계액 축소(cap). */
    public static function compute(Context $ctx, ContractState $c, bool $first, ?Number $cap = null): void
    {
        $out = &$c->stepOut(self::STEP);
        $pp = $c->prepay;
        $el = self::eligibleLines($ctx, $c);
        $total = dsum(array_map(fn($x) => $x[1], $el));
        if ($first) {
            foreach ($el as [$ln, $e, $why]) {
                $ctx->emit(self::STEP, 'offset_eligible', $e, $c, line: $ln->label, line_key: $ln->key(), inputs: ['net' => $ln->net],
                    formula: $why, ref: 'V2 §8.3 6단계 L218~222');
            }
            $inp = [];
            foreach ($el as [$ln, $e, $_]) {
                $inp[$ln->label] = $e;
            }
            $out['offset_eligible_total'] = $ctx->emit(self::STEP, 'offset_eligible_total', $total, $c, inputs: $inp,
                formula: '적격 세전액 = P1.1 + P2.1 + 상계허용 P5.1 + 상계허용 일시 · 분할 지원금 + 상계허용 종료 일시정산(동일 계약)',
                code: 'offset_eligible_total = e_1_1 + e_2_1 + e_5_1 + e_inst + e_ls', ref: 'V2 §8.3 6단계 L223');
            if ($pp['type'] === 'LOAN') {
                [$wsum, $it, $lt, $per] = Tax::estimateWithholding($ctx, $pp['payee'],
                    array_map(fn($x) => [self::attrs($x[0]), $x[1]], $el));
                $note = '';
            } else {
                [$wsum, $it, $lt, $per] = [D(0), D(0), D(0), []];
                $note = 'EARNED — 원천세 상당액 차감 없음';
            }
            $out['offset_withholding_equiv'] = $ctx->emit(self::STEP, 'offset_withholding_equiv', $wsum, $c,
                inputs: ['prepayment_tax_type' => $pp['type'], '소득세' => $it, '지방소득세' => $lt],
                formula: '상계 대상 원천세 상당액 — 9단계와 같은 순차 산식(소득세 내림 → 지방소득세 내림), 비대상 라인 0원',
                code: 'TAX.estimate_withholding(eligible_lines) if LOAN else 0', ref: 'V2 §8.3 6단계 L227~228', note: $note);
            $ctx->emit(self::STEP, 'offset_withholding_income_tax', $it, $c, formula: '상계 대상 원천세 상당액 중 소득세', ref: 'V2 L227');
            $ctx->emit(self::STEP, 'offset_withholding_local_tax', $lt, $c, formula: '상계 대상 원천세 상당액 중 지방소득세', ref: 'V2 L227');
            $capacity = sub($total, $wsum);
            $out['offset_capacity'] = $ctx->emit(self::STEP, 'offset_capacity', $capacity, $c,
                inputs: ['적격 세전액' => $total, '원천세 상당액' => $wsum],
                formula: '상계 가능액 = 상계 대상 세전액 − 상계 대상 원천세 상당액',
                code: 'offset_capacity = offset_eligible_total − offset_withholding_equiv', ref: 'V2 §8.3 6단계 L229');
            $amount = $capacity > 0 ? dmin($capacity, $pp['balance']) : D(0);
            $out['offset_amount_initial'] = $ctx->emit(self::STEP, 'offset_amount_initial', $amount, $c,
                inputs: ['상계 가능액' => $capacity, '미상계 잔액' => $pp['balance']],
                formula: '상계 가능액 ≤ 0이면 상계 0원 · 잔액 유지, 아니면 당월 상계액 = min(상계 가능액, 미상계 선급금 잔액)',
                code: 'offset_amount = min(offset_capacity, prepay_unoffset_balance) if capacity > 0 else 0',
                ref: 'V2 §8.3 6단계 L230~231');
            $out['taxable_reduction_flag'] = $ctx->emit(self::STEP, 'taxable_reduction_flag', $pp['type'] === 'EARNED', $c,
                inputs: ['prepayment_tax_type' => $pp['type']],
                formula: '소득 선지급(EARNED)이면 과세표준 차감, 대여금(LOAN)이면 과세표준 유지', ref: 'V2 §8.3 6단계 L235');
        } else {
            $amount = $cap;
        }
        self::allocate($ctx, $c, $el, $amount, !$first);
        $out['offset_amount'] = $ctx->emit(self::STEP, 'offset_amount', $amount, $c, inputs: ['1차 산정' => $out['offset_amount_initial'] ?? null],
            formula: "당월 상계액(예정) — 9단계 재검증 후 값", ref: 'V2 §8.3 6단계 L228 · L231',
            provisional: !$first, note: !$first ? 'Q-13(현금 가용액 산식)' : '');
        $after = sub($pp['balance'], $amount);
        $out['prepay_balance_after'] = $ctx->emit(self::STEP, 'prepay_balance_after', $after, $c,
            inputs: ['잔액' => $pp['balance'], '상계액' => $amount],
            formula: "갱신 예정 선급금 잔액 = 미상계 잔액 − 당월 상계액(Locked 전 '예정')", ref: 'V1 §7.1 L531');
        $out['offset_eligible_lines'] = array_map(fn($x) => ['line_key' => $x[0]->key(), 'eligible' => $x[1],
            'offset' => $x[0]->offset], $el);
        $c->prepay_balance_after = $after;
        $c->prepay['amount'] = $amount;
        unset($out);
    }

    private static function allocate(Context $ctx, ContractState $c, array $el, Number $amount, bool $revalidated = false): void
    {
        foreach ($c->lines as $ln) {
            $ln->offset = D(0);
        }
        $pos = array_values(array_filter(array_map(fn($x) => [$x[0], $x[1]], $el), fn($x) => $x[1] > 0));
        if (!$pos || $amount <= 0) {
            return;
        }
        $den = dsum(array_map(fn($x) => $x[1], $pos));
        $order = sort_by($pos, fn($x) => [$x[1], $x[0]->pipeline_id === '1.1' ? 1 : 0, $x[0]->pipeline_id,
            pystr(either(either($x[0]->agreement_id, $x[0]->approval_id), '')), $x[0]->label]);
        $acc = D(0);
        $n = count($order);
        foreach ($order as $i => [$ln, $e]) {
            if ($i < $n - 1) {
                $raw = div(mul($amount, $e), $den);
                $ln->offset = floor_won($raw);
                $acc = add($acc, $ln->offset);
                [$rounding, $before] = ['FLOOR_WON', $raw];
            } else {
                $ln->offset = sub($amount, $acc);
                [$rounding, $before] = ['ALLOC_LAST_REMAINDER', null];
            }
            $ctx->emit(self::STEP, 'offset_alloc', $ln->offset, $c, line: $ln->label, line_key: $ln->key(),
                inputs: ['당월 상계액' => $amount, '라인 적격액' => $e, '적격액 합계' => $den],
                formula: '적격액 오름차순(동률이면 P1.1을 뒤로) 선행 내림, 적격액 최대 라인이 잔여 차액',
                code: 'offset[l] = floor(offset_amount × eligible_l / Σeligible); last = amount − Σ선행',
                before: $before, rounding: $rounding, ref: 'V2 §8.3 6단계 L232~233 · §13.3 L579',
                provisional: $revalidated, note: $revalidated ? '9단계 재검증 후 재안분' : '');
        }
    }
}

final class S07LumpsumAdd
{
    const STEP = 'LUMPSUM_ADD';
    const KIND = ['SIGNING_BONUS' => '전속계약금', 'SUPPORT_LUMP_SUM' => '일시 지원금', 'SUPPORT_INSTALLMENT' => '분할 지원금',
        'BUYOUT' => '매절 대금', 'FIXED_FEE' => '정액 수당', 'LUMP_SETTLE' => '종료 일시정산'];

    public static function run(Context $ctx): void
    {
        foreach ($ctx->contracts as $c) {
            $out = &$c->stepOut(self::STEP);
            $rows = [];
            $total = D(0);
            foreach ($c->linesOf('LUMPSUM') as $ln) {
                $ctx->emit(self::STEP, 'lumpsum_line', $ln->net, $c, line: $ln->label, line_key: $ln->key(), ref_id: $ln->approval_id,
                    inputs: ['item_kind' => $ln->item_kind, 'offset_type' => $ln->offset_type,
                        'income_category' => $ln->income_category, 'income_clause' => $ln->income_clause],
                    formula: '승인 비정기 약정금(' . (self::KIND[$ln->item_kind] ?? pystr($ln->item_kind)) . ') — 라인별 소득 구분 유지',
                    ref: 'V2 §8.3 7단계 L239 · L242');
                $rows[] = ['milestone_id' => $ln->approval_id, 'item_kind' => $ln->item_kind, 'line_key' => $ln->key(),
                    'amount' => $ln->net, 'payee_id' => $ln->fixed_payee];
                $total = add($total, $ln->net);
            }
            $out['lines'] = $rows;
            $out['lumpsum_total'] = $ctx->emit(self::STEP, 'lumpsum_total', $total, $c, inputs: ['items' => count($rows)],
                formula: '비정기 가산금 = 전속계약금 + 일시 · 분할 지원금 + 매절 대금 + 정액 수당 + 종료 일시정산(LUMP_SETTLE)',
                code: 'lumpsum_total = Σ approvals(target_month = 정산월, APPROVED)', ref: 'V2 §8.3 7단계 L239');
            $n11 = dsum(array_map(fn($l) => $l->net, $c->linesOf('1.1')));
            $n21 = dsum(array_map(fn($l) => $l->net, $c->linesOf('2.1')));
            $s51 = dsum(array_map(fn($l) => $l->net, $c->linesOf('5.1')));
            $out['pre_split_supply'] = $ctx->emit(self::STEP, 'pre_split_supply', add(add(add($n11, $n21), $s51), $total), $c,
                inputs: ['Σnet_1_1' => $n11, 'Σnet_2_1' => $n21, 'Σconfirmed_amount(5.1)' => $s51, 'lumpsum_total' => $total],
                formula: '분할 전 정산 공급가액(상계 전) = P1.1 순액 + P2.1 순액 + P5.1 확정액 + 비정기 가산금',
                code: 'pre_split_supply = Σnet_1_1 + Σnet_2_1 + Σconfirmed_5_1 + lumpsum_total',
                ref: 'V2 §8.3 7단계 L244 · V4 Case 1 L41 · Case 3 L94');
            foreach ($ctx->input['clawbacks'] as $cb) {
                if ($cb['contract_id'] === $c->id) {
                    $ctx->emit(self::STEP, 'clawback_deferred', true, $c,
                        formula: '전속계약금 반환액은 세후 항목 — 7단계에서 차감하지 않고 10단계에서 1회', ref: 'V2 L243', output: false);
                    break;
                }
            }
            unset($out);
        }
    }
}
