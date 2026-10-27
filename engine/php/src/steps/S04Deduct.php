<?php
/**
 * 4단계 DEDUCT — 환불 및 프로모션 공제(V2 §8.3 표 L171 · 본문 L196~203, V1 §5.1 L211 · §15, SPEC 7절).
 *
 * 공제 단가는 원 결제 건의 settlement_line_snapshot(당시 요율 · 지분율 · rate_type · 수취인 분할)으로 대칭 공제.
 *   net_1_1 = 보정 후 P1.1 − 환불 공제 − 옵션 B 분담 − 옵션 C 차감
 *   net_2_1 = P2.1 − 반품 차감,  net_2_2 = P2.2 − 위탁 반품 차감 + 1단계 위탁 전용 잔액
 *   support_deduct_total[agr] = refund_5_1 + optB_5_1 + optC_5_1 (원거래 확정 배분액 역참조, 미환불 확정액 한도)
 * 절사: 라인 월 합산 후 1회 floor(절대값 내림 후 부호 복원). P5.1 일반 환불 · 옵션 B는 원거래 단위 floor(V2 L201, Q-08).
 */

namespace SettleCalc;

use BcMath\Number;

final class S04Deduct
{
    const STEP = 'DEDUCT';

    private static array $acc = [];      // contract → category → Σ q4
    private static array $comps = [];    // tkey(contract, line label) → [component]
    private static array $sup = [];      // agreement → {refund_5_1, optB_5_1, optC_5_1, txs}
    private static array $consRet = [];  // contract → {sales, fee, vat}

    private static function ratioOf($rfRatio, $amount, $base): Number
    {
        if ($rfRatio !== null) {
            return pct($rfRatio);
        }
        if (truthy($base)) {
            return div(D($amount), D($base));
        }
        return D(0);
    }

    private static function &supOf($aid): array
    {
        $k = tkey($aid);
        if (!isset(self::$sup[$k])) {
            self::$sup[$k] = ['refund_5_1' => D(0), 'optB_5_1' => D(0), 'optC_5_1' => D(0), 'txs' => []];
        }
        return self::$sup[$k];
    }

    private static function accAdd($cid, string $cat, Number $v): void
    {
        $k = (string)$cid;
        self::$acc[$k][$cat] = add(self::$acc[$k][$cat] ?? D(0), $v);
    }

    private static function compAdd($cid, string $label, array $comp): void
    {
        self::$comps[tkey($cid, $label)][] = $comp;
    }

    public static function run(Context $ctx): void
    {
        self::$acc = self::$comps = self::$sup = self::$consRet = [];
        foreach ($ctx->input['refund_lines'] as $rf) {
            if (truthy(g($rf, 'voucher_id'))) { // 환불 사후 보정 전표(ADJ-*) — 반영 기준월 규칙(S-10)
                if (!self::voucherInDeduct($ctx, $rf)) {
                    continue;
                }
            } elseif (truthy(g($rf, 'refund_approved_date')) && month_of($rf['refund_approved_date']) !== $ctx->month) {
                continue;
            }
            if (truthy(g($rf, 'lecture_refund'))) {
                $rf = array_merge($rf, ['refund_amount' => self::lectureRefundAmount($ctx, $rf)]);
            }
            $rf = array_merge($rf, ['refund_amount' => self::cashBasis($ctx, $rf)]);
            foreach ((either(g($rf, 'snapshot'), [])) as $snap) {
                $c = $ctx->contract(g($snap, 'contract_id'));
                if (!$c) {
                    continue;
                }
                self::refundSnapshot($ctx, $c, $rf, $snap);
            }
        }
        foreach ($ctx->input['pass_refund_deductions'] as $pr) {
            if (truthy(g($pr, 'approved_date')) && month_of($pr['approved_date']) !== $ctx->month) {
                continue;
            }
            $opt = g($pr, 'option');
            foreach ((either(g($pr, 'snapshot'), [])) as $snap) {
                $c = $ctx->contract(either(g($snap, 'contract_id'), g($pr, 'contract_id')));
                if (!$c) {
                    continue;
                }
                self::passRefundSnapshot($ctx, $c, $pr, $opt, $snap);
            }
        }
        foreach ($ctx->contracts as $c) {
            self::finishContract($ctx, $c, self::$acc[(string)$c->id] ?? [], self::$consRet[(string)$c->id] ?? []);
        }
    }

    private static function nextMonth(string $m): string
    {
        $y = (int)substr($m, 0, 4);
        $mo = (int)substr($m, 5, 2);
        return sprintf('%d-%02d', $y + ($mo === 12 ? 1 : 0), ($mo % 12) + 1);
    }

    /** 보정 전표 반영 기준월 = 승인 시점에 마감되지 않은 가장 이른 귀속월(원 발생월부터, V2 §10.2 L365 · S-10). */
    private static function voucherAppliedMonth(Context $ctx, array $rf): array
    {
        $origin = head(pystr(either(g($rf, 'origin_month'),
            month_of(either(g($rf, 'approved_at'), g($rf, 'refund_approved_date'))))), 7);
        $approved = pystr(either(either(g($rf, 'approved_at'), g($rf, 'refund_approved_date')), ''));
        $closed = either($ctx->p('month_closed_at'), []);
        $m = $origin;
        while (strcmp($m, substr($approved, 0, 7)) < 0) {
            $at = $closed[$m] ?? null;
            if (truthy($at) && strcmp(pystr($at), $approved) <= 0) {
                $m = self::nextMonth($m);
            } else {
                break;
            }
        }
        return [$origin, $m];
    }

    /** 원 발생월이 미마감이면 그 달 4단계에 합산, 마감됐으면 진행 중인 달의 수동 조정 라인(마감 월 재개 없음). */
    private static function voucherInDeduct(Context $ctx, array $rf): bool
    {
        [$origin, $applied] = self::voucherAppliedMonth($ctx, $rf);
        $snap = (either(g($rf, 'snapshot'), [[]]))[0];
        $c = $ctx->contract(g($snap, 'contract_id'));
        $route = $applied === $origin ? 'DEDUCT' : 'MANUAL_ADJUSTMENT';
        if ($applied !== $ctx->month) {
            return false;
        }
        $mc = [];
        foreach ((either($ctx->p('month_closed_at'), [])) as $k => $v) {
            if (strcmp((string)$k, $origin) >= 0) {
                $mc[$k] = $v;
            }
        }
        $ctx->emit(self::STEP, 'voucher_applied_month', $applied, $c, ref_id: $rf['voucher_id'],
            inputs: ['origin_month' => $origin, 'approved_at' => either(g($rf, 'approved_at'), g($rf, 'refund_approved_date')),
                'month_closed_at' => new Obj($mc)],
            formula: '보정 전표 반영 기준월 = 승인 시점에 마감되지 않은 가장 이른 귀속월(원 발생월 보존) — 원 발생월 미마감이면 '
                . '그 달 4단계 DEDUCT, 마감됐으면 진행 중인 달의 정산 수동 조정 라인',
            code: 'applied_month = first m ≥ origin_month with closed_at(m) is None or > approved_at',
            ref: 'V2 §10.2 L365 · 통합 설계서 RFD-003-S2 L370 · S-10(2026-10-27)');
        $ctx->emit(self::STEP, 'voucher_route', $route, $c, ref_id: $rf['voucher_id'], formula: '보정 전표 반영 경로',
            ref: 'V2 §10.2 L365');
        if ($route === 'DEDUCT') {
            return true;
        }
        // 마감된 원 발생월 → 진행 중인 달의 전월 정산 조정 라인: 원거래 스냅샷 대칭 R/S 공제액을 세전 음수 조정으로
        $refund = truthy(g($rf, 'lecture_refund')) ? self::lectureRefundAmount($ctx, $rf) : D(g($rf, 'refund_amount'));
        $rf = array_merge($rf, ['refund_amount' => $refund]);
        $base = self::cashBasis($ctx, $rf);
        foreach ((either(g($rf, 'snapshot'), [])) as $s) {
            if (either(g($s, 'rate_type'), 'BASIC') !== 'BASIC') {
                continue;
            }
            $raw = mul(mul($base, pct(g($s, 'share_ratio'))), pct(g($s, 'rate_value')));
            $amt = $ctx->emit(self::STEP, 'voucher_adjustment_amount', neg(floor_won(q4($raw))), $c, ref_id: $rf['voucher_id'],
                inputs: ['환불 현금분' => $base, 'snap.share_ratio' => g($s, 'share_ratio'), 'snap.rate_value' => g($s, 'rate_value')],
                formula: '마감된 달의 보정 전표 → 진행 중인 달 전월 정산 조정(세전): −내림(환불 현금분 × 원거래 지분 × 원거래 요율)',
                code: 'adj = −floor(q4(cash_basis × share × rate))', before: neg($raw), rounding: 'ABS_FLOOR_SIGN',
                ref: 'V2 §10.1 L353 · §10.2 L365 · S-10 · 2026-10-27 white 결정(조정 라인은 세금 계산 직전)');
            $ctx->auto_adjustments[] = [
                'adj_id' => $rf['voucher_id'], 'source' => 'REFUND_VOUCHER', 'contract_id' => g($s, 'contract_id'),
                'payee_id' => g($s, 'rights_holder_id'), 'snapshot_payee_splits' => either(g($s, 'payee_splits'), []),
                'origin_month' => $origin, 'applied_month' => $applied, 'adj_reason_code' => 'REFUND_OMIT',
                'adj_amount' => $amt, 'account_type' => 'PRE_TAX', 'pipeline_id' => pystr(either(g($s, 'pipeline_id'), '1.1')),
                'refund_amount' => $refund];
        }
        return false;
    }

    /** 포인트를 쓴 강좌 라인: 복원 포인트 = 내림(라인 사용 포인트 × 환불액 ÷ 라인 결제액)(통합 설계서 RFD-002 L365). */
    private static function restoredPoints(array $rf, Number $refund): Number
    {
        $lr = either(g($rf, 'lecture_refund'), []);
        if (truthy(g($lr, 'point_used'))) {
            $paid = D($lr['paid_amount']);
            return truthy($paid) ? floor_won(div(mul(D($lr['point_used']), $refund), $paid)) : D(0);
        }
        return D(either(g($rf, 'refund_point_amount'), 0));
    }

    /**
     * 권리자 R/S 공제 기준 = 환불액 중 현금분(포인트 복원분 제외) — R/S 모수가 포인트 할인을 뺀 실결제액이라 대칭
     * (V2 §8.3 1단계 Step 1 L133 · §8.1, 2026-10-27 white 결정).
     */
    private static function cashBasis(Context $ctx, array $rf): ?Number
    {
        if (g($rf, 'refund_amount') === null) { // 수량 기준 반품(위탁 · 도서)은 금액 없이 들어온다
            return null;
        }
        $refund = D(g($rf, 'refund_amount'));
        $pts = self::restoredPoints($rf, $refund);
        if (!truthy($pts)) {
            return $refund;
        }
        $snap = (either(g($rf, 'snapshot'), [[]]))[0];
        $c = $ctx->contract(g($snap, 'contract_id'));
        return $ctx->emit(self::STEP, 'refund_cash_basis', sub($refund, $pts), $c, ref_id: either(g($rf, 'voucher_id'), g($rf, 'refund_id')),
            inputs: ['환불액' => $refund, '복원 포인트' => $pts,
                '라인 사용 포인트' => g(either(g($rf, 'lecture_refund'), []), 'point_used')],
            formula: '권리자 R/S 공제 기준 = 환불액 − 복원 포인트(복원 포인트 = 내림(라인 사용 포인트 × 환불액 ÷ 라인 결제액)) — '
                . 'R/S 모수가 쿠폰 · 포인트 할인을 뺀 실결제액이므로 공제도 현금분만',
            code: 'cash_basis = refund − floor(point_used × refund / line_paid)', rounding: 'FLOOR_WON',
            ref: 'V2 §8.3 1단계 Step 1 L133 · 통합 설계서 RFD-002 L365 · white 결정(2026-10-27)');
    }

    /**
     * 인강 환불액(통합 설계서 RFD-002 L364~365, D-ORD-03 · 평생교육법 시행령 별표 3 비고 4).
     * 7일 이내 + 2강 이하 수강(맛보기 제외) → 전액, 그 밖 → 내림(강좌 실결제액 × (전체 회차 − 학습 회차) ÷ 전체 회차),
     * 원 수강기간이 끝난 강좌 → 0.
     */
    private static function lectureRefundAmount(Context $ctx, array $rf): Number
    {
        $lr = $rf['lecture_refund'];
        $paid = D($lr['paid_amount']);
        $total = D($lr['total_sessions']);
        $learned = D($lr['learned_sessions']);
        $days = g($lr, 'days_since_payment');
        $snap = (either(g($rf, 'snapshot'), [[]]))[0];
        $c = $ctx->contract(g($snap, 'contract_id'));
        $kw = ['ref_id' => either(g($rf, 'voucher_id'), g($rf, 'refund_id')),
            'inputs' => ['강좌 실결제액' => $paid, '전체 회차' => $total, '학습 회차' => $learned, '결제 후 경과일' => $days,
                '원 수강기간 종료' => truthy(g($lr, 'course_period_ended'))],
            'ref' => '통합 설계서 RFD-002 L364~365 · D-ORD-03(2026-10-27) · 평생교육법 시행령 별표 3 비고 4'];
        if (truthy(g($lr, 'course_period_ended'))) {
            return $ctx->emit(self::STEP, 'lecture_refund_amount', D(0), $c, ...$kw, formula: '원 수강기간이 끝난 강좌는 반환하지 않는다',
                code: 'refund = 0');
        }
        if ($days !== null && D($days) <= 7 && $learned <= 2) {
            return $ctx->emit(self::STEP, 'lecture_refund_amount', $paid, $c, ...$kw,
                formula: '결제일로부터 7일 이내이면서 맛보기 제외 2강 이하 수강 → 실결제액 100% 환불',
                code: 'refund = paid_amount');
        }
        $raw = truthy($total) ? div(mul($paid, sub($total, $learned)), $total) : D(0);
        return $ctx->emit(self::STEP, 'lecture_refund_amount', floor_won($raw), $c, ...$kw,
            formula: '환불액 = 강좌 실결제액 × (전체 회차 − 학습 회차) ÷ 전체 회차(원 단위 절사)',
            code: 'refund = floor(paid × (total − learned) / total)', before: $raw, rounding: 'FLOOR_WON');
    }

    private static function refundSnapshot(Context $ctx, ContractState $c, array $rf, array $snap): void
    {
        $pl = pystr(g($snap, 'pipeline_id'));
        $rt = either(g($snap, 'rate_type'), 'BASIC');
        $ref = g($rf, 'refund_id');
        if ($rt === 'SUPPORT') {
            $ratio = self::ratioOf(g($rf, 'refund_ratio'), g($rf, 'refund_amount'), g($snap, 'base_amount'));
            $alloc = D(g($snap, 'confirmed_alloc_amount'));
            $unref = D(g($snap, 'unrefunded_amount') !== null ? g($snap, 'unrefunded_amount') : $alloc);
            $raw = mul($alloc, $ratio);
            $amt = dmin(floor_won($raw), $unref);
            $aid = g($snap, 'agreement_id');
            $s = &self::supOf($aid);
            $s['refund_5_1'] = add($s['refund_5_1'], $ctx->emit(self::STEP, 'refund_5_1_tx', $amt, $c, line: '5.1:' . pystr($aid),
                agreement: $aid, ref_id: $ref,
                inputs: ['원거래 지원금 확정 배분액' => $alloc, '환불 비율' => $ratio, '원거래 미환불 확정액' => $unref],
                formula: '원거래 정산 스냅샷의 지원금 확정 배분액 역참조(각 원거래 미환불 확정액 한도), 당월 요율로 재산정 금지',
                code: 'refund_5_1 = min(floor(support_confirmed_alloc × refund_ratio), unrefunded_support_confirmed)',
                before: $raw, rounding: 'FLOOR_WON', ref: 'V2 §8.3 4단계 L201', output: false));
            $s['txs'][] = ['ref_id' => $ref, 'deduct_5_1' => $amt, 'unrefunded' => $unref];
            unset($s);
            self::compAdd($c->id, '5.1:' . pystr($aid), self::component($ref, 'refund', $amt, $snap, $c));
            return;
        }
        if ($pl === '2.2') {
            if (g($rf, 'refund_ratio') !== null) {
                $ratio = self::ratioOf(g($rf, 'refund_ratio'), null, null);
            } else {
                $ratio = truthy(g($snap, 'confirmed_qty')) ? div(D(g($rf, 'refund_qty')), D(g($snap, 'confirmed_qty'))) : D(0);
            }
            $sales = g($rf, 'refund_amount') !== null ? D($rf['refund_amount']) : floor_won(mul(D(g($snap, 'base_amount')), $ratio));
            $fee = floor_won(mul(D(g($snap, 'fee_supply_alloc')), $ratio));
            $vat = floor_won(mul(D(g($snap, 'fee_vat_alloc')), $ratio));
            $k = (string)$c->id;
            $r = self::$consRet[$k] ?? ['sales' => D(0), 'fee' => D(0), 'vat' => D(0)];
            $r['sales'] = add($r['sales'], $sales);
            $r['fee'] = add($r['fee'], $fee);
            $r['vat'] = add($r['vat'], $vat);
            self::$consRet[$k] = $r;
            $ctx->emit(self::STEP, 'consignment_return_tx', neg($sales), $c, line: '2.2', ref_id: $ref,
                inputs: ['반품 비율' => $ratio, '원 판매대금' => g($snap, 'base_amount'),
                    '원 배분 수수료 공급가액' => g($snap, 'fee_supply_alloc'), '원 배분 수수료 부가세' => g($snap, 'fee_vat_alloc'),
                    '수수료 조정' => neg($fee), '수수료 부가세 조정' => neg($vat)],
                formula: '원판매에 확정 · 배분된 판매대금 · 수수료 공급가액 · 수수료 부가세를 각각 참조해 반대 부호로 조정',
                code: 'sales_adj = −base × ratio; fee_adj = −floor(fee_alloc × ratio); vat_adj = −floor(vat_alloc × ratio)',
                rounding: 'ABS_FLOOR_SIGN', ref: 'V1 §6.6 L509 · V4 Case 10-B L253', output: false);
            return;
        }
        $share = g($snap, 'share_ratio');
        $rate = g($snap, 'rate_value');
        if ($pl === '2.1') {
            $base = g($rf, 'refund_amount') !== null ? D($rf['refund_amount'])
                : div(mul(D(g($snap, 'base_amount')), D(g($rf, 'refund_qty'))), D(either(g($snap, 'confirmed_qty'), 1)));
            $cat = 'return_2_1';
            $formula = '자사 발행 도서 인세 반품 차감 — 원 판매 확정 시점의 정가 · 요율 · 지분율 스냅샷';
            $cref = 'V1 §6.3 L430 · V2 L199';
        } else {
            $base = D(g($rf, 'refund_amount'));
            $cat = 'refund_1_1';
            $formula = '환불 공제 = 환불 기준금 × 원거래 스냅샷 지분율 × 원거래 스냅샷 요율(대칭 공제)';
            $cref = 'V1 §5.1 L211 · V2 L198 · L202';
        }
        $raw = mul(mul($base, pct($share)), pct($rate));
        $amt = q4($raw);
        self::accAdd($c->id, $cat, $ctx->emit(self::STEP, $cat . '_tx', $amt, $c, line: $pl, ref_id: $ref,
            inputs: ['환불 기준금' => $base, 'snap.share_ratio' => $share, 'snap.rate_value' => $rate,
                'payment_state' => g($snap, 'payment_state')],
            formula: $formula, code: 'q4(refund_base × snap.share_ratio/100 × snap.rate_value/100)',
            before: $raw, rounding: 'Q4', ref: $cref, output: false));
        self::compAdd($c->id, $pl, self::component($ref, $cat, $amt, $snap, $c));
    }

    private static function passRefundSnapshot(Context $ctx, ContractState $c, array $pr, $opt, array $snap): void
    {
        $rt = either(g($snap, 'rate_type'), 'BASIC');
        $ref = g($pr, 'pass_refund_id');
        if ($opt === 'A' || $opt === null) {
            $ctx->emit(self::STEP, 'option_a', D(0), $c, ref_id: $ref, inputs: ['option' => 'A'],
                formula: '옵션 A 플랫폼 전액 부담 — R/S 모수 · MMG 모수 영향 없음, 재연산 없음',
                ref: 'V1 §15.1 L602~604', output: false);
            return;
        }
        if ($rt === 'SUPPORT') {
            $alloc = D(g($snap, 'confirmed_alloc_amount'));
            $unref = D(g($snap, 'unrefunded_amount') !== null ? g($snap, 'unrefunded_amount') : $alloc);
            $aid = g($snap, 'agreement_id');
            if ($opt === 'B') {
                $raw = mul($alloc, pct(either(g($pr, 'optB_burden_ratio'), 0)));
                $amt = dmin(floor_won($raw), $unref);
                [$key, $rnd, $note] = ['optB_5_1', 'FLOOR_WON', ''];
                $code = 'optB_5_1 = min(floor(alloc × optB_burden_ratio), unrefunded)';
            } else {
                $raw = mul($alloc, pct(either(g($pr, 'optC_cancel_ratio'), 100)));
                $amt = dmin(q4($raw), $unref);
                [$key, $rnd, $note] = ['optC_5_1', 'Q4', 'Q-08: 옵션 C는 정본에 내림 없음 — q4 유지 후 라인 합산 floor'];
                $code = 'optC_5_1 = min(alloc × optC_cancel_ratio, unrefunded)';
            }
            $s = &self::supOf($aid);
            $s[$key] = add($s[$key], $ctx->emit(self::STEP, $key . '_tx', $amt, $c, line: '5.1:' . pystr($aid), agreement: $aid,
                ref_id: $ref, inputs: ['원거래 지원금 확정 배분액' => $alloc, '원거래 미환불 확정액' => $unref, 'option' => $opt],
                formula: '합격 환급반 옵션 B · C 지원금 차감 — 원거래 지원금 확정 배분액 한도 역참조',
                code: $code, before: $raw, rounding: $rnd, ref: 'V2 L201 · V1 §15.3 L625',
                provisional: $opt === 'C', note: $note, output: false));
            $s['txs'][] = ['ref_id' => $ref, 'deduct_5_1' => $amt, 'unrefunded' => $unref];
            unset($s);
            self::compAdd($c->id, '5.1:' . pystr($aid), self::component($ref, $key, $amt, $snap, $c));
            return;
        }
        $base = D(g($pr, 'refund_amount'));
        $raw = mul(mul($base, pct(g($snap, 'share_ratio'))), pct(g($snap, 'rate_value')));
        $amt = q4($raw);
        $cat = $opt === 'B' ? 'optB_1_1' : 'optC_1_1';
        self::accAdd($c->id, $cat, $ctx->emit(self::STEP, $cat . '_tx', $amt, $c, line: '1.1', ref_id: $ref,
            inputs: ['환급금' => $base, 'snap.share_ratio' => g($snap, 'share_ratio'), 'snap.rate_value' => g($snap, 'rate_value')],
            formula: $opt === 'B' ? '합격 환급반 옵션 B — 환급금을 계약상 R/S 지분율과 같은 비율로 분담'
                : '합격 환급반 옵션 C — 원 매출 취소로 간주, 결제액 기준 R/S 스냅샷 대칭 공제',
            code: 'q4(refund_amount × snap.share_ratio/100 × snap.rate_value/100)', before: $raw, rounding: 'Q4',
            ref: 'V1 §15.1 L605~607 · §15.3 L625', note: $opt === 'B' ? 'Q-09 총괄 해석 채택(2026-10-26)' : '',
            output: false));
        self::compAdd($c->id, '1.1', self::component($ref, $cat, $amt, $snap, $c));
    }

    private static function component($ref, string $cat, Number $amt, array $snap, ContractState $c): array
    {
        $state = either(g($snap, 'payment_state'), 'UNPAID');
        return ['ref_id' => $ref, 'category' => $cat, 'weight' => D($amt), 'payment_state' => $state,
            'snapshot_payee_splits' => either(g($snap, 'payee_splits'), []),
            'paid_return_post_tax_amount' => g($snap, 'paid_return_post_tax_amount'),
            'paid_portion_amount' => g($snap, 'paid_portion_amount'),
            'unpaid_portion_amount' => g($snap, 'unpaid_portion_amount'),
            'matrix_case_id' => g($snap, 'matrix_case_id'), 'payee_id' => either(g($snap, 'rights_holder_id'), $c->holder_id)];
    }

    /** 공제 총액을 원거래 구성요소에 배분하고 지급 상태로 경로 분리(V2 L197, SPEC 7.4 잠정). */
    private static function splitPaths(Context $ctx, ContractState $c, array $compsLine, Number $total): array
    {
        $compsLine = sort_by($compsLine, fn($x) => pystr($x['ref_id']));
        $allocs = $compsLine ? alloc_last_remainder($total, array_map(fn($x) => $x['weight'], $compsLine)) : [];
        $unpaidTotal = D(0);
        $out = [];
        foreach ($compsLine as $i => $comp) {
            $amt = $allocs[$i];
            $st = $comp['payment_state'];
            if ($st === 'PAID') {
                $parts = [['PAID_RETURN', $amt]];
            } elseif ($st === 'PARTIAL') {
                $pp = D($comp['paid_portion_amount']);
                $up = D($comp['unpaid_portion_amount']);
                $den = add($pp, $up);
                $unpaid = truthy($den) ? floor_won(div(mul($amt, $up), $den)) : $amt;
                $parts = [['UNPAID_REDUCTION', $unpaid], ['PAID_RETURN', sub($amt, $unpaid)]];
            } else {
                $parts = [['UNPAID_REDUCTION', $amt]];
            }
            foreach ($parts as [$path, $a]) {
                if (!truthy($a)) {
                    continue;
                }
                $out[] = array_merge($comp, ['path' => $path, 'amount' => neg($a)]);
                if ($path === 'UNPAID_REDUCTION') {
                    $unpaidTotal = add($unpaidTotal, $a);
                } else {
                    $c->return_claims[] = ['ref_id' => $comp['ref_id'], 'payee_id' => $comp['payee_id'],
                        'post_tax_amount' => D(g($comp, 'paid_return_post_tax_amount')),
                        'pre_tax_amount' => $a, 'matrix_case_id' => $comp['matrix_case_id']];
                    $ctx->issue('CANON_GAP', '기지급 소득 반환 경로 금액 산식 미확정 — 라인 차감 제외, 세후 반환채권 후보로 10단계 전달',
                        self::STEP, $c->holder_id, 'V2 L197 · V4 Case 4 L113', 'Q-10');
                }
            }
        }
        return [$out, $unpaidTotal];
    }

    private static function finishContract(Context $ctx, ContractState $c, array $acc, array $ret): void
    {
        $out = &$c->stepOut(self::STEP);
        $cats = [];
        foreach ([['refund_1_1', 'refund_deduct_1_1', 'V2 L198'], ['optB_1_1', 'optB_deduct_1_1', 'V1 L605'],
                     ['optC_1_1', 'optC_deduct_1_1', 'V1 L606'], ['return_2_1', 'return_deduct_2_1', 'V2 L199']] as [$cat, $name, $cref]) {
            $raw = $acc[$cat] ?? D(0);
            $cats[$cat] = $ctx->emit(self::STEP, $name, floor_won($raw), $c, line: $cat === 'return_2_1' ? '2.1' : '1.1',
                inputs: ['Σ q4' => $raw], formula: '공제액은 라인별 월 합산 후 1회 내림(절대값 내림 후 부호 복원)',
                code: $name . ' = floor(Σ q4)', before: $raw, rounding: 'ABS_FLOOR_SIGN',
                ref: $cref . ' · §13.1 L566 · L569', note: 'Q-26');
            $out[$name] = $cats[$cat];
        }
        $componentsOut = [];
        $netLines = [];
        $comps = fn(string $label) => self::$comps[tkey($c->id, $label)] ?? [];
        // P1.1
        $l11 = $c->linesOf('1.1');
        if (!$l11 && (truthy($cats['refund_1_1']) || truthy($cats['optB_1_1']) || truthy($cats['optC_1_1']))) {
            $ln = S00PipelineIn::line11($ctx, $c);
            $ln->adjusted = D(0);
            $l11 = [$ln];
        }
        foreach ($l11 as $ln) {
            $dTotal = $ln === $l11[0] ? add(add($cats['refund_1_1'], $cats['optB_1_1']), $cats['optC_1_1']) : D(0);
            [$rows, $unpaid] = truthy($dTotal) ? self::splitPaths($ctx, $c, $comps($ln->label), $dTotal) : [[], D(0)];
            $ln->deduct_components = $rows;
            $componentsOut = array_merge($componentsOut, $rows);
            $adj = $ln->adjusted !== null ? $ln->adjusted : $ln->new;
            $ln->net = $ctx->emit(self::STEP, 'net_1_1', sub($adj, $unpaid), $c, line: $ln->label, line_key: $ln->key(),
                inputs: ['보정 후 P1.1' => $adj, '환불 공제' => $cats['refund_1_1'], '옵션 B 분담' => $cats['optB_1_1'],
                    '옵션 C 차감' => $cats['optC_1_1'], '기지급 반환 경로 분리액' => sub($dTotal, $unpaid)],
                formula: 'P1.1 순 강의료 = 보정 후 P1.1 세전액 − 당월 강의 환불 공제액 − 합격 환급반 옵션 B 분담액 − 옵션 C 매출 취소 차감액',
                code: 'net_1_1 = adjusted_1_1 − refund − optB − optC (미지급 감액분)', ref: 'V2 §8.3 4단계 L198');
            $ln->deduct_1_1 = $dTotal;
            $netLines[] = ['line_key' => $ln->key(), 'amount' => $ln->net];
        }
        // P2.1
        foreach ($c->linesOf('2.1') as $i => $ln) {
            $dTotal = $i === 0 ? $cats['return_2_1'] : D(0);
            [$rows, $unpaid] = truthy($dTotal) ? self::splitPaths($ctx, $c, $comps('2.1'), $dTotal) : [[], D(0)];
            $ln->deduct_components = $rows;
            $componentsOut = array_merge($componentsOut, $rows);
            $ln->net = $ctx->emit(self::STEP, 'net_2_1', sub($ln->new, $unpaid), $c, line: $ln->label, line_key: $ln->key(),
                inputs: ['P2.1 신규 인세액' => $ln->new, '당월 도서 반품 차감액' => $dTotal],
                formula: 'P2.1 순 인세액 = P2.1 신규 인세액 − 당월 도서 반품 차감액',
                code: 'net_2_1 = new_2_1 − return_deduct_2_1', ref: 'V2 §8.3 4단계 L199');
            $netLines[] = ['line_key' => $ln->key(), 'amount' => $ln->net];
        }
        // P2.2
        if ($c->consignment !== null || $ret || truthy($c->carry['cons'])) {
            $ftype = either(either(g($c->consignment ?? [], 'consignment_fee_type'), g($c->row, 'consignment_fee_type')), 'NET_DEDUCT');
            $ln = $c->line('2.2', '2.2', ['supply_nature' => 'BOOK_GOODS']);
            [$sales, $fee, $vat] = [$ret['sales'] ?? D(0), $ret['fee'] ?? D(0), $ret['vat'] ?? D(0)];
            $rdeduct = $ftype === 'NET_DEDUCT' ? sub($sales, $fee) : $sales;
            $out['return_deduct_2_2'] = $ctx->emit(self::STEP, 'return_deduct_2_2', $rdeduct, $c, line: '2.2',
                inputs: ['반품 판매대금' => $sales, '반품 수수료 공급가액' => $fee, 'consignment_fee_type' => $ftype],
                formula: '위탁 반품 차감액(수수료 부가세 차감 전 위탁 순액 기준, 수수료 부가세 조정은 9단계)',
                code: 'return_deduct_2_2 = sales_adj − fee_adj (NET_DEDUCT) | sales_adj (GROSS_SETTLE)',
                ref: 'V2 L200 · V1 L501', provisional: true, note: 'Q-07');
            $cons = $c->carry['cons'];
            $out['consignment_balance_applied'] = $cons;
            $ln->net = $ctx->emit(self::STEP, 'net_2_2', add(sub($ln->new, $rdeduct), $cons), $c, line: '2.2', line_key: $ln->key(),
                inputs: ['P2.2 신규 위탁 정산 입력액' => $ln->new, '당월 위탁 도서 반품 차감액' => $rdeduct,
                    '1단계 위탁 전용 잔액' => $cons],
                formula: 'P2.2 순 위탁 정산액 = 신규 위탁 정산 입력액 − 당월 위탁 도서 반품 차감액 + 1단계 위탁 전용 잔액',
                code: 'net_2_2 = new_2_2 − return_deduct_2_2 + consignment_balance', ref: 'V2 §8.3 4단계 L200');
            $c->consignment_return = ['sales' => $sales, 'fee' => $fee, 'vat' => $vat, 'fee_type' => $ftype];
            if (truthy($sales)) {
                $retOut = [
                    'sales_adjust' => neg($sales), 'fee_supply_adjust' => neg($fee), 'fee_vat_adjust' => neg($vat),
                    'net_deduct_payout_adjust' => add(add(neg($sales), $fee), $vat),
                    'gross_settle_sales_adjust' => neg($sales), 'gross_settle_separate_claim' => neg(add($fee, $vat))];
                $fm = ['net_deduct_payout_adjust' => 'NET_DEDUCT 지급 조정 = −판매대금 − (−수수료 공급가액) − (−수수료 부가세)',
                    'gross_settle_separate_claim' => 'GROSS_SETTLE 별도 청구 조정 = −(수수료 공급가액 + 수수료 부가세)'];
                foreach ($retOut as $k => $v) {
                    $ctx->emit(self::STEP, $k, $v, $c, line: '2.2', inputs: ['반품 판매대금' => $sales, '수수료' => $fee, '수수료 부가세' => $vat],
                        formula: $fm[$k] ?? '원판매 배분액 대칭 조정', ref: 'V1 §6.6 L509 · V4 Case 10-B L253');
                }
                $out['consignment_return'] = $retOut;
            }
            $netLines[] = ['line_key' => $ln->key(), 'amount' => $ln->net];
        }
        // P5.1
        $sd = [];
        foreach ($c->linesOf('5.1') as $ln) {
            $s = self::$sup[tkey($ln->agreement_id)] ?? ['refund_5_1' => D(0), 'optB_5_1' => D(0), 'optC_5_1' => D(0), 'txs' => []];
            $optc = floor_won($s['optC_5_1']);
            $total = add(add($s['refund_5_1'], $s['optB_5_1']), $optc);
            $ln->support_deduct = $total;
            $ln->support_txs = $s['txs'];
            [$rows, $_] = truthy($total) ? self::splitPaths($ctx, $c, $comps($ln->label), $total) : [[], D(0)];
            $ln->deduct_components = $rows;
            $componentsOut = array_merge($componentsOut, $rows);
            $row = ['agreement_id' => $ln->agreement_id, 'refund_5_1' => $s['refund_5_1'], 'optB_5_1' => $s['optB_5_1'],
                'optC_5_1' => $optc, 'total' => $total];
            $ctx->emit(self::STEP, 'refund_5_1', $s['refund_5_1'], $c, line: $ln->label, agreement: $ln->agreement_id,
                formula: '일반 환불 지원금 공제(원거래 단위 내림 합계)', ref: 'V2 L201');
            $ctx->emit(self::STEP, 'optB_5_1', $s['optB_5_1'], $c, line: $ln->label, agreement: $ln->agreement_id,
                formula: '옵션 B 지원금 공제(원거래 단위 내림 합계)', ref: 'V2 L201');
            $ctx->emit(self::STEP, 'optC_5_1', $optc, $c, line: $ln->label, agreement: $ln->agreement_id, before: $s['optC_5_1'],
                rounding: 'ABS_FLOOR_SIGN', formula: '옵션 C 지원금 차감(라인 합산 후 내림)', ref: 'V2 L201',
                provisional: true, note: 'Q-08');
            $ctx->emit(self::STEP, 'support_deduct_total', $total, $c, line: $ln->label, agreement: $ln->agreement_id,
                inputs: ['refund_5_1' => $s['refund_5_1'], 'optB_5_1' => $s['optB_5_1'], 'optC_5_1' => $optc],
                formula: 'P5.1 공제 합계 = 일반 환불 + 옵션 B + 옵션 C(4단계 산출 → 5단계 반영)',
                code: 'support_deduct_total[agr] = refund_5_1 + optB_5_1 + optC_5_1', ref: 'V2 §8.3 4단계 L201');
            $ctx->emit(self::STEP, 'net_5_1', sub($ln->new, $total), $c, line: $ln->label, agreement: $ln->agreement_id,
                inputs: ['P5.1 신규 발생액' => $ln->new, 'P5.1 공제 합계' => $total],
                formula: 'P5.1 공제 후 금액(표시용 — 한도 적용 전 모수에서 차감하지 않고 5단계에서 반영)',
                code: 'new_5_1 − support_deduct_total', ref: 'V2 L158 · L201', provisional: true,
                note: '표시용 파생값(5단계 확정액과 다름)');
            $sd[] = $row;
        }
        $out['support_deduct_total'] = $sd;
        $out['deduct_components'] = array_map(fn($r) => ['ref_id' => $r['ref_id'], 'line_key' => null, 'path' => $r['path'],
            'amount' => $r['amount'], 'snapshot_payee_splits' => $r['snapshot_payee_splits']], $componentsOut);
        $out['return_claims'] = $c->return_claims;
        $out['net_lines'] = $netLines;
        $deductTotal = add(add(dsum(array_values($cats)), dsum(array_map(fn($r) => $r['total'], $sd))),
            either($out['return_deduct_2_2'] ?? null, D(0)));
        $out['deduct_total'] = $ctx->emit(self::STEP, 'deduct_total', $deductTotal, $c, inputs: $cats,
            formula: '당월 공제 합계(표시용)', code: 'Σ 공제', ref: 'V2 §8.3 4단계');
        $netTotal = add(dsum(array_map(fn($x) => $x['amount'], $netLines)),
            dsum(array_map(fn($l) => sub($l->new, $l->support_deduct), $c->linesOf('5.1'))));
        $out['net_total'] = $ctx->emit(self::STEP, 'net_total', $netTotal, $c, inputs: ['lines' => count($netLines)],
            formula: '공제 후 라인별 세전 순액 합계(표시용, P5.1은 공제 후 발생액)', code: 'Σ net lines',
            ref: 'V2 §8.3 표 4단계 L171');
        unset($out);
    }
}
