<?php
/**
 * 0단계 PIPELINE_IN — 상위 인입 파이프라인(V2 §8.3 1단계 L129~160, SPEC 3절).
 *
 * P1.1 강좌 R/S(Step 1~4) · P2.1 자사 발행 인세 · P2.2 위탁 · P2.3 일반 상품(자사 집계 전용) · 비인입 · P5.1 지원금 모수/발생.
 * 결과는 계약 라인(ContractState::$lines)의 new 값으로 2단계에 넘긴다.
 */

namespace SettleCalc;

use BcMath\Number;

final class S00PipelineIn
{
    const STEP = 'PIPELINE_IN';
    const SCOPE_1_1 = ['PIPELINE_1_1_ONLY', 'PIPELINE_1_1_2_1'];
    const SCOPE_2_1 = ['PIPELINE_2_1_ONLY', 'PIPELINE_1_1_2_1'];

    public static function run(Context $ctx): void
    {
        $month = $ctx->month;
        $ctx->basis = [];
        $items = $ctx->input['order_items'];
        $paid = self::step1Allocate($ctx, $items);
        $p11 = []; // contract_id → Σ rs_q4
        foreach ($items as $it) {
            $kind = g($it, 'item_type');
            if ($kind === 'LECTURE') {
                if (truthy(g($it, 'approved_at')) && month_of($it['approved_at']) !== $month) {
                    continue;
                }
                self::lectureRs($ctx, $it, $paid[(string)$it['order_item_id']] ?? D(g($it, 'paid_amount')), $p11);
            } elseif ($kind === 'BOOK') {
                if (truthy(g($it, 'purchase_confirmed_at')) && month_of($it['purchase_confirmed_at']) !== $month) {
                    continue;
                }
                $sup = g($it, 'book_supply_type_snapshot');
                if (in_array($sup, ['PURCHASED_RESALE', 'BUNDLED'], true) || !truthy($sup)) {
                    self::excludeBook($ctx, $it, $sup);
                }
            } elseif ($kind === 'GOODS_ITEM') {
                self::goods($ctx, $it);
            } else {
                $ctx->excluded_lines[] = ['ref_id' => g($it, 'order_item_id'), 'reason' => '정산 비인입 품목(' . pystr($kind) . ')',
                    'canon_ref' => 'V2 §8.3 1단계 L153~155'];
            }
        }
        // P1.1 Step 4 — 권리자 · 라인 월 합산 1회 내림(V2 L136)
        foreach ($p11 as $cid => $total) {
            $c = $ctx->contract($cid);
            $ln = self::line11($ctx, $c);
            $ln->new = $ctx->emit(self::STEP, 'p1_1_new', floor_won($total), $c, line: $ln->label, line_key: $ln->key(),
                inputs: ['Σ rs_q4' => $total], formula: '권리자별 월 합산 단계에서 1회 내림 절사',
                code: 'P1_1_new[line] = floor(Σ rs_q4)', before: $total, rounding: 'FLOOR_WON',
                ref: 'V2 §8.3 1단계 Step 4 L136 · §13.1 L566');
        }
        self::royalty21($ctx, array_values(array_filter($items, fn($it) => g($it, 'item_type') === 'BOOK'
            && g($it, 'book_supply_type_snapshot') === 'OWN_PUBLISHED' && self::inMonth($it, $month))));
        self::consignment22($ctx, array_values(array_filter($items, fn($it) => g($it, 'item_type') === 'BOOK'
            && g($it, 'book_supply_type_snapshot') === 'CONSIGNMENT' && self::inMonth($it, $month))));
        self::support51($ctx);
        self::lumpsumCollect($ctx);
    }

    private static function inMonth(array $it, string $month): bool
    {
        return !truthy(g($it, 'purchase_confirmed_at')) || month_of($it['purchase_confirmed_at']) === $month;
    }

    public static function line11(Context $ctx, ContractState $c): Line
    {
        $h = $ctx->holder($c->holder_id);
        return $c->line('1.1', '1.1', ['rate_type' => 'BASIC', 'income_category' => either(g($h, 'income_category'), 'BUSINESS'),
            'supply_nature' => 'LECTURE_RS']);
    }

    private static function &basis(Context $ctx, $aid): array
    {
        $k = (string)$aid;
        if (!isset($ctx->basis[$k])) {
            $ctx->basis[$k] = ['1.1' => D(0), '2.1' => D(0), 'own' => D(0)];
        }
        return $ctx->basis[$k];
    }

    // ------------------------------------------------------------------ P1.1

    /**
     * Step 1 패키지 혜택 소급 안분(V2 §8.1 L98~100 · §8.3 L133 · 13.3 L577).
     * 순수 강좌 결제 풀(강좌 정가 합 − 쿠폰 · 포인트 할인)을 강좌 정가 비율로 내림 안분하고,
     * 정렬(강좌 정가 내림차순 → product_id 오름차순)의 마지막 행이 잔여 차액을 받는다.
     */
    private static function step1Allocate(Context $ctx, array $items): array
    {
        $out = [];
        $orders = [];
        foreach ($ctx->input['orders'] as $o) {
            $orders[(string)$o['order_id']] = $o;
        }
        $byOrder = [];
        foreach ($items as $it) {
            if (g($it, 'item_type') === 'LECTURE' && !truthy(g($it, 'allocation_applied'))
                && g($it, 'order_id') !== null && isset($orders[(string)$it['order_id']])) {
                $byOrder[(string)$it['order_id']][] = $it;
            }
        }
        foreach ($byOrder as $oid => $rows) {
            $disc = D($orders[$oid]['discount_total']);
            $rows = sort_by($rows, fn($r) => [neg(D(g($r, 'list_price'))), pystr(g($r, 'product_id'))]);
            $lists = array_map(fn($r) => D(g($r, 'list_price')), $rows);
            $sl = dsum($lists);
            $pool = sub($sl, $disc);
            $paid = alloc_last_remainder($pool, $lists);
            foreach ($rows as $i => $r) {
                $p = $paid[$i];
                $last = $i === count($rows) - 1;
                $raw = !is_zero($sl) ? div(mul($pool, $lists[$i]), $sl) : D(0);
                $out[(string)$r['order_item_id']] = $ctx->emit(self::STEP, 'paid_amount', $p, holder: null, line: '1.1',
                    ref_id: $r['order_item_id'],
                    inputs: ['순수 강좌 결제 풀' => $pool, '해당 강좌 정가' => $lists[$i], '패키지 내 강좌 정가 합계' => $sl,
                        '쿠폰 · 포인트 할인' => $disc],
                    formula: $last ? '마지막 강좌 라인 = 순수 강좌 결제 풀 − 선행 강좌 합계(잔여 차액)'
                        : '개별 강좌 실결제액 = 내림( 순수 강좌 결제 풀 × (해당 강좌 정가 / 패키지 내 강좌 정가 합계) )',
                    code: 'paid = alloc_last_remainder(pool, list_price 비율), pool = Σlist_price − discount_total',
                    before: $last ? null : $raw, rounding: $last ? 'ALLOC_LAST_REMAINDER' : 'FLOOR_WON',
                    ref: 'V2 §8.1 L98~100 · §8.3 1단계 Step 1 L133 · §13.3 L577', output: false);
            }
        }
        return $out;
    }

    private static function lectureRs(Context $ctx, array $it, Number $paid, array &$p11): void
    {
        $lectures = either(g($it, 'lectures'), [['lecture_id' => g($it, 'product_id'), 'lecture_base_amount' => $paid]]);
        $anyNull = false;
        foreach ($lectures as $lec) {
            if (g($lec, 'lecture_base_amount') === null) {
                $anyNull = true;
            }
        }
        if ($anyNull) {
            $w = array_map(function ($lec) use ($ctx) {
                $x = D(either(g($lec, 'runtime_seconds'), 0));
                return truthy($x) ? $x : D($ctx->p('default_weight_seconds'));
            }, $lectures);
            $tw = dsum($w);
            foreach ($lectures as $i => $lec) {
                $wi = $w[$i];
                $base = truthy($tw) ? q4(div(mul($paid, $wi), $tw)) : D(0);
                $lec['lecture_base_amount'] = $ctx->emit(self::STEP, 'lecture_base_amount', $base, line: '1.1',
                    ref_id: $lec['lecture_id'], inputs: ['paid_amount' => $paid, 'weight' => $wi, 'Σweight' => $tw],
                    formula: '강좌 실결제액을 하위 강의 동영상 원본 러닝타임 가중치로 분할(러닝타임 0초는 기본 가중치)',
                    code: 'lecture_base[i] = q4(paid_amount × w_i / Σw)',
                    before: truthy($tw) ? div(mul($paid, $wi), $tw) : 0,
                    rounding: 'Q4', ref: 'V2 §8.3 1단계 Step 2 L134', provisional: true, note: 'Q-01 · Q-03', output: false);
                self::oneLecture($ctx, $it, $lec, $p11);
            }
            return;
        }
        foreach ($lectures as $lec) {
            self::oneLecture($ctx, $it, $lec, $p11);
        }
    }

    private static function oneLecture(Context $ctx, array $it, array $lec, array &$p11): void
    {
        $date = head(pystr(either(g($it, 'approved_at'), '')), 10);
        $date = $date === '' ? null : $date;
        $base = q4($lec['lecture_base_amount']);
        foreach ($ctx->input['lecture_instructors'] as $m) {
            if ($m['lecture_id'] !== $lec['lecture_id']) {
                continue;
            }
            $c = $ctx->contract($m['contract_id']);
            if (!$c || !valid_on($m, $date, $c->row) || !valid_on(['start_date' => g($c->row, 'start_date'),
                    'end_date' => g($c->row, 'current_end_date')], $date)) {
                $ctx->excluded_lines[] = ['ref_id' => pystr($it['order_item_id']) . '/' . pystr($lec['lecture_id']) . '/'
                    . pystr($m['rights_holder_id']), 'reason' => '유효 매핑 밖(미매핑 · 정산 0원)', 'canon_ref' => 'V1 §4.2 L177~178'];
                continue;
            }
            $rl = $ctx->rate($c->id, 'BASIC', $date, '1.1');
            if (!$rl) {
                $ctx->issue('INPUT_MISSING', pystr($c->id) . ' BASIC 요율 라인 없음 — P1.1 0원', self::STEP, $c->holder_id, 'V2 L135');
                continue;
            }
            $raw = mul(mul($base, pct($m['share_ratio'])), pct($rl['rate_value']));
            $rs = q4($raw);
            self::line11($ctx, $c);
            $k = (string)$c->id;
            $p11[$k] = add($p11[$k] ?? D(0), $ctx->emit(self::STEP, 'rs_q4', $rs, $c, line: '1.1',
                ref_id: pystr($it['order_item_id']) . '/' . pystr($lec['lecture_id']),
                inputs: ['강의 기준금' => $base, '권리자 지분율' => $m['share_ratio'], '계약 요율' => $rl['rate_value']],
                formula: '강의 기준금 × 권리자 지분율 × 계약 요율(강의 레벨 소수점 4자리 유지)',
                code: 'rs_q4 = q4(lecture_base × share_ratio/100 × basic_rate/100)', before: $raw, rounding: 'Q4',
                ref: 'V2 §8.3 1단계 Step 3 · 4 L135~136', output: false));
        }
        // P5.1 모수(강의 대상) — 자사 지분율을 곱하지 않는다(V2 L159)
        foreach ($ctx->input['support_fund_agreement_targets'] as $t) {
            if ($t['target_type'] === 'LECTURE' && $t['target_id'] === $lec['lecture_id'] && valid_on($t, $date)) {
                self::addBasis($ctx, $t, '1.1', $base);
            }
        }
    }

    private static function findAgreement(Context $ctx, $aid): ?array
    {
        foreach ($ctx->input['support_fund_agreements'] as $a) {
            if ($a['agreement_id'] === $aid) {
                return $a;
            }
        }
        return null;
    }

    private static function addBasis(Context $ctx, array $t, string $pipeline, Number $base): void
    {
        $agr = self::findAgreement($ctx, $t['agreement_id']);
        if (!$agr || g($agr, 'payment_method') !== 'REVENUE_SHARE') {
            return;
        }
        $scope = either(g($agr, 'settlement_scope'), 'PIPELINE_1_1_ONLY');
        if (($pipeline === '1.1' && !in_array($scope, self::SCOPE_1_1, true))
            || ($pipeline === '2.1' && !in_array($scope, self::SCOPE_2_1, true))) {
            return;
        }
        $own = g($t, 'own_share_ratio');
        if ($own !== null && D($own) <= 0) {
            $ctx->emit(self::STEP, 'support_basis_skipped', $base, holder: $agr['rights_holder_id'],
                contract: $agr['contract_id'], agreement: $agr['agreement_id'], ref_id: $t['target_id'],
                inputs: ['own_share_ratio' => $own],
                formula: "자사 지분 0% 구간은 발생 0원 · 상태 ACTIVE 유지 · '자사 지분 없음으로 미발생'",
                ref: 'V1 L274', output: false);
            return;
        }
        $b = &self::basis($ctx, $agr['agreement_id']);
        $b[$pipeline] = add($b[$pipeline], $base);
        if ($own !== null) {
            $b['own'] = add($b['own'], q4(mul($base, pct($own))));
        }
    }

    // ------------------------------------------------------------------ P2.1

    private static function royalty21(Context $ctx, array $items): void
    {
        $bySku = [];
        $skuVal = [];
        foreach ($items as $it) {
            $k = tkey(g($it, 'book_sku_id'));
            $bySku[$k][] = $it;
            $skuVal[$k] = g($it, 'book_sku_id');
        }
        foreach ($bySku as $k => $rows) {
            $sku = $skuVal[$k];
            $date = head(pystr(either(g($rows[0], 'purchase_confirmed_at'), '')), 10);
            $date = $date === '' ? null : $date;
            $authors = [];
            foreach ($ctx->input['book_authors'] as $a) {
                $c = $ctx->contract($a['contract_id']);
                if ($a['book_sku_id'] === $sku && $c && valid_on($a, $date, $c->row)) {
                    $rl = $ctx->rate($c->id, 'BASIC', $date, '2.1');
                    if (!$rl) {
                        $ctx->issue('INPUT_MISSING', pystr($c->id) . ' 인세 BASIC 요율 없음', self::STEP, $c->holder_id, 'V1 §6.3');
                        continue;
                    }
                    $authors[] = [$a, $c, D($rl['rate_value'])];
                }
            }
            $linesQ4 = array_map(fn($r) => q4(mul(D(g($r, 'confirmed_qty')), D(g($r, 'royalty_base_price')))), $rows);
            $gross = dsum($linesQ4);
            foreach ($ctx->input['support_fund_agreement_targets'] as $t) {
                if ($t['target_type'] === 'BOOK_SKU' && $t['target_id'] === $sku && valid_on($t, $date)) {
                    self::addBasis($ctx, $t, '2.1', $gross); // 확정 부수 × 약정 기준가(V1 L273)
                }
            }
            if (!$authors) {
                continue;
            }
            $rates = array_unique(array_map(fn($x) => strip_zeros($x[2]->value), $authors));
            if (count($rates) === 1) {
                $rate = $authors[0][2];
                $raw = dsum(array_map(fn($x) => q4(mul($x, pct($rate))), $linesQ4));
                $total = floor_won($raw);
                $ctx->emit(self::STEP, 'sku_royalty_total', $total, holder: null, ref_id: $sku, line: '2.1',
                    inputs: ['Σ 확정 부수 × 인세 기준가' => $gross, '인세 기본요율' => $rate],
                    formula: 'SKU별 당월 인세 총액 = 내림( Σ( 당월 확정 부수 × 인세 기준가 × (인세 기본요율 / 100) ) )',
                    code: 'sku_total = floor(Σ q4(qty × price × rate/100))', before: $raw, rounding: 'FLOOR_WON',
                    ref: 'V2 §8.3 1단계 L139 · V1 §6.3 L433', output: false);
                $order = sort_by($authors, fn($x) => [neg(D($x[0]['share_ratio'])), $x[0]['rights_holder_id']]);
                $shares = array_map(fn($x) => D($x[0]['share_ratio']), $order);
                $ssum = dsum($shares);
                if (bccomp($ssum->value, '100', WORK) === 0) {
                    $amts = alloc_last_remainder($total, $shares);
                } else { // 등록 저자 지분 합이 100이 아니면 역산 잔여를 저자에게 몰지 않는다
                    $amts = array_map(fn($s) => floor_won(mul($total, pct($s))), $shares);
                    $ctx->issue('CANON_GAP', 'SKU ' . pystr($sku) . ' 저자 지분 합 ' . $ssum->value . '% ≠ 100 — 저자별 floor(총액 × 지분)',
                        self::STEP, null, 'V1 L434');
                }
                foreach ($order as $i => [$a, $c, $_]) {
                    self::addRoyalty($ctx, $a, $c, $sku, $amts[$i], $total, 'ALLOC_LAST_REMAINDER',
                        '공동 저자 총액 역산 배분(지분 내림차순 → rights_holder_id 오름차순, 마지막 잔여)',
                        'royalty[author] = alloc_last_remainder(sku_total, w=share_ratio)');
                }
            } else {
                foreach ($authors as [$a, $c, $rate]) {
                    $raw = dsum(array_map(fn($x) => q4(mul(mul($x, pct($rate)), pct($a['share_ratio']))), $linesQ4));
                    self::addRoyalty($ctx, $a, $c, $sku, floor_won($raw), $raw, 'FLOOR_WON',
                        '요율 · 기준선이 다르면 저자별로 내림( Σ( 부수 × 기준가 × 요율 × 지분율 ) )',
                        'royalty[author] = floor(Σ q4(line × rate × share))');
                }
            }
        }
    }

    private static function addRoyalty(Context $ctx, array $a, ContractState $c, $sku, Number $amt, $before,
                                       string $rounding, string $formula, string $code): void
    {
        $h = $ctx->holder($c->holder_id);
        $cat = either(either(g($a, 'income_category'), g($h, 'income_category')), 'BUSINESS');
        if ($cat === 'OTHER') {
            $unit = pystr($c->id) . '+' . pystr($sku);
            $label = '2.1:' . pystr($sku);
            $ln = $c->line($label, '2.1', ['rate_type' => 'BASIC', 'income_category' => 'OTHER',
                'income_clause' => g($a, 'income_clause'), 'tax_threshold_unit_key' => $unit,
                'payee_is_author' => g($h, 'payee_is_author'), 'supply_nature' => 'ROYALTY']);
        } else {
            $ln = $c->line('2.1', '2.1', ['rate_type' => 'BASIC', 'income_category' => $cat, 'supply_nature' => 'ROYALTY']);
        }
        $ln->new = add($ln->new, $ctx->emit(self::STEP, 'p2_1_royalty', $amt, $c, line: $ln->label, ref_id: $sku,
            line_key: $ln->key(), inputs: ['share_ratio' => $a['share_ratio'], 'basis' => $before], formula: $formula,
            code: $code, rounding: $rounding, ref: 'V1 §6.3 L433~436 · V2 §13.3 L580'));
    }

    // ------------------------------------------------------------------ P2.2

    private static function consignment22(Context $ctx, array $items): void
    {
        $byContract = [];
        $cids = [];
        foreach ($items as $it) {
            $a = null;
            foreach ($ctx->input['book_authors'] as $x) {
                if ($x['book_sku_id'] === g($it, 'book_sku_id')) {
                    $a = $x;
                    break;
                }
            }
            if (!$a) {
                $ctx->issue('INPUT_MISSING', '위탁 품목 ' . pystr($it['order_item_id']) . '의 위탁 계약 매핑 없음', self::STEP);
                continue;
            }
            $k = (string)$a['contract_id'];
            $byContract[$k][] = $it;
            $cids[$k] = $a['contract_id'];
        }
        foreach ($byContract as $k => $rows) {
            $c = $ctx->contract($cids[$k]);
            $feeRate = pct(either(g($c->row, 'consignment_fee_rate'), 0));
            $sales = D(0);
            $netRaw = D(0);
            foreach ($rows as $r) {
                $price = D(g($r, 'consignment_price') !== null ? g($r, 'consignment_price') : g($r, 'list_price'));
                $amt = mul(D(g($r, 'confirmed_qty')), $price);
                $sales = add($sales, $amt);
                $netRaw = add($netRaw, mul($amt, sub(1, $feeRate)));
            }
            $net = floor_won($netRaw);
            $fee = sub($sales, $net);
            $ftype = either(g($c->row, 'consignment_fee_type'), 'NET_DEDUCT');
            $inp = $ftype === 'NET_DEDUCT' ? $net : $sales;
            $c->consignment = ['monthly_sales' => $sales, 'net_before_fee_vat' => $net, 'fee_supply' => $fee,
                'consignment_input' => $inp, 'consignment_fee_type' => $ftype];
            $ctx->emit(self::STEP, 'monthly_sales', $sales, $c, line: '2.2', inputs: ['Σ 확정 부수 × 위탁 판매가' => $sales],
                formula: '월 판매대금 = 합계( 당월 확정 부수 × 위탁 판매가 )', code: 'monthly_sales = Σ(qty × price)',
                ref: 'V2 §8.3 1단계 L144 · V1 §6.6 L495');
            $ctx->emit(self::STEP, 'net_before_fee_vat', $net, $c, line: '2.2', inputs: ['월 판매대금' => $sales, '위탁 수수료율' => $feeRate],
                formula: '수수료 부가세 차감 전 위탁 순액 = 내림( 합계( 당월 확정 부수 × 위탁 판매가 × (1 − 위탁 수수료율) ) )',
                code: 'net = floor(Σ qty × price × (1 − fee_rate))', before: $netRaw, rounding: 'FLOOR_WON',
                ref: 'V2 §8.3 1단계 L145 · V1 L496');
            $ctx->emit(self::STEP, 'fee_supply', $fee, $c, line: '2.2', inputs: ['월 판매대금' => $sales, '위탁 순액' => $net],
                formula: '위탁 수수료 공급가액 = 월 판매대금 − 수수료 부가세 차감 전 위탁 순액', code: 'fee = sales − net',
                ref: 'V2 §8.3 1단계 L146 · V1 L498(별도 절사 금지)');
            $ln = $c->line('2.2', '2.2', ['supply_nature' => 'BOOK_GOODS']);
            $ln->new = $ctx->emit(self::STEP, 'consignment_input', $inp, $c, line: '2.2', inputs: ['consignment_fee_type' => $ftype],
                formula: 'NET_DEDUCT면 수수료 부가세 차감 전 위탁 순액, GROSS_SETTLE이면 월 판매대금 전액',
                code: 'consignment_input = net if NET_DEDUCT else sales', ref: 'V2 §8.3 1단계 L147');
        }
    }

    // ------------------------------------------------------------------ P2.3 · 비인입

    private static function goods(Context $ctx, array $it): void
    {
        if (truthy(g($it, 'purchase_confirmed_at')) && month_of($it['purchase_confirmed_at']) !== $ctx->month) {
            return;
        }
        $qty = D(g($it, 'confirmed_qty'));
        $price = D(g($it, 'sale_price_incl_vat') !== null ? g($it, 'sale_price_incl_vat') : g($it, 'list_price'));
        $total = mul($qty, $price);
        $raw = div(mul($total, 100), 110);
        $supply = floor_won($raw);
        $vat = sub($total, $supply);
        $ctx->emit(self::STEP, 'p2_3_supply_amount', $supply, ref_id: $it['order_item_id'], line: '2.3',
            inputs: ['Σ 확정 수량 × 부가가치세 포함 판매가' => $total],
            formula: '공급가액 = 내림( Σ( 당월 확정 수량 × 부가가치세 포함 판매가 ) × 100 / 110 )',
            code: 'supply = floor(Σ × 100/110)', before: $raw, rounding: 'FLOOR_WON', ref: 'V2 §8.3 1단계 L151');
        $ctx->emit(self::STEP, 'p2_3_vat_amount', $vat, ref_id: $it['order_item_id'], line: '2.3',
            inputs: ['판매대금' => $total, '공급가액' => $supply], formula: '부가가치세 = Σ 판매대금 − 공급가액(총액 역산)',
            code: 'vat = total − supply', ref: 'V2 §8.3 1단계 L151 · 13장');
        $row = ['ref_id' => $it['order_item_id'], 'pipeline_id' => '2.3', 'matrix_case_id' => 'TX-13',
            'goods_supply_type' => g($it, 'goods_supply_type_snapshot'), 'sales_total' => $total, 'supply_amount' => $supply,
            'vat_amount' => $vat, 'vat_rate' => 10, 'withholding_called' => false, 'payout_amount' => 0,
            'in_settlement_statement' => false, 'correction_channel' => 1,
            'evidence_type' => $ctx->tax_table['cases']['TX-13']['evidence_type'],
            'canon_ref' => 'V2 §8.3 1단계 L148~152 · TAX.md TX-13'];
        if (g($it, 'purchase_unit_cost') !== null) {
            $row['purchase_amount'] = mul($qty, D($it['purchase_unit_cost']));
        }
        $ctx->internal_only[] = $row;
    }

    private static function excludeBook(Context $ctx, array $it, $sup): void
    {
        $ctx->excluded_lines[] = ['ref_id' => g($it, 'order_item_id'),
            'reason' => '도서 공급 형태 ' . (truthy($sup) ? pystr($sup) : '미지정') . ' — 정산 입력 파이프라인 비인입',
            'canon_ref' => 'V2 §8.3 1단계 L153~155'];
        if ($sup === 'PURCHASED_RESALE') {
            $qty = D(g($it, 'confirmed_qty'));
            $row = ['ref_id' => g($it, 'order_item_id'), 'pipeline_id' => null, 'kind' => 'PURCHASED_RESALE',
                'own_sales_amount' => mul($qty, D(g($it, 'list_price'))), 'payout_amount' => 0,
                'in_settlement_statement' => false, 'matrix_case_id' => 'TX-11',
                'correction_channel' => 4, 'evidence_type' => $ctx->tax_table['cases']['TX-11']['evidence_type'],
                'canon_ref' => 'V2 §8.3 1단계 L153~155(매출 집계 · 매입채무 경로) · TAX.md TX-11'];
            if (g($it, 'purchase_unit_cost') !== null) {
                $row['purchase_payable_ap'] = mul($qty, D($it['purchase_unit_cost']));
            }
            $ctx->emit(self::STEP, 'own_sales_amount', $row['own_sales_amount'], ref_id: g($it, 'order_item_id'),
                inputs: ['confirmed_qty' => $qty, 'list_price' => g($it, 'list_price')],
                formula: '매입 재판매 도서는 권리자 지급 엔진 비인입 — 자사 매출 · 매입채무(AP) 경로로만',
                ref: 'V2 §8.3 1단계 L153~155');
            $ctx->internal_only[] = $row;
        }
    }

    // ------------------------------------------------------------------ P5.1

    private static function support51(Context $ctx): void
    {
        foreach ($ctx->input['support_fund_agreements'] as $agr) {
            if (g($agr, 'payment_method') !== 'REVENUE_SHARE') {
                continue;
            }
            $c = $ctx->contract($agr['contract_id']);
            if (!$c) {
                continue;
            }
            $aid = $agr['agreement_id'];
            $b = self::basis($ctx, $aid);
            $basis = add($b['1.1'], $b['2.1']);
            $rl = $ctx->rate($c->id, 'SUPPORT', null, null, $aid);
            $rate = $rl ? D($rl['rate_value']) : D(0);
            if (!$rl) {
                $ctx->issue('INPUT_MISSING', '지원금 ' . pystr($aid) . ' SUPPORT 요율 라인 없음', self::STEP, $c->holder_id, 'V2 L135');
            }
            $h = $ctx->holder($c->holder_id);
            $payee = g($agr, 'payee_id');
            $ln = $c->line('5.1:' . pystr($aid), '5.1', ['rate_type' => 'SUPPORT', 'agreement_id' => $aid,
                'income_category' => either(either(g($agr, 'income_category'), g($h, 'income_category')), 'BUSINESS'),
                'income_clause' => g($agr, 'income_clause'), 'supply_nature' => 'SUPPORT_RS',
                'offset_type' => g($agr, 'offset_type'), 'protected' => g($agr, 'offset_type') === 'NON_OFFSET',
                'fixed_payee' => (truthy($payee) && $payee !== $c->holder_id) ? $payee : null]);
            $raw = mul($basis, pct($rate));
            $new = floor_won($raw);
            $ctx->emit(self::STEP, 'support_basis', $basis, $c, line: $ln->label, agreement: $aid,
                inputs: ['P1.1 기준금' => $b['1.1'], 'P2.1 부수 × 약정 기준가' => $b['2.1'],
                    'settlement_scope' => g($agr, 'settlement_scope')],
                formula: '요율 기준 모수(rate_basis) 금액 — 자사 지분율을 추가로 곱하지 않음',
                code: 'basis = Σ_{targets ∩ scope} rate_basis_amount', rounding: 'Q4', ref: 'V2 §8.3 1단계 L159 · V1 L273');
            $status = g($agr, 'status');
            if ($status !== 'ACTIVE') {
                $newEff = D(0);
                $note = '약정 상태 ' . pystr($status) . ' — 신규 발생 산출 대상 아님(공제 · 복원만 4 · 5단계 인입)';
            } else {
                $newEff = $new;
                $note = '';
            }
            $ln->new = $ctx->emit(self::STEP, 'support_new', $newEff, $c, line: $ln->label, agreement: $aid, line_key: $ln->key(),
                inputs: ['요율 기준 모수' => $basis, '지원금 요율' => $rate, 'status' => $status],
                formula: '매출연동 개발지원금 당월 신규 발생액 = 내림( 당월 지원금 모수 × (지원금 요율 / 100) )',
                code: 'support_new = floor(basis × support_rate/100) if status == ACTIVE else 0',
                before: $raw, rounding: 'FLOOR_WON', ref: 'V2 §8.3 1단계 L160 · 2단계 L188',
                note: $note, provisional: $status !== 'ACTIVE');
            if (truthy($b['2.1']) && truthy($b['1.1']) && truthy($newEff)) {
                $part21 = floor_won(div(mul($newEff, $b['2.1']), $basis));
                $ctx->emit(self::STEP, 'support_part_2_1', $part21, $c, line: $ln->label, agreement: $aid,
                    inputs: ['support_new' => $newEff, 'basis_2_1' => $b['2.1'], 'basis' => $basis],
                    formula: '복수 파이프라인: P2.1 몫을 먼저 내림, 잔여 차액을 P1.1에 귀속',
                    code: 'part_2_1 = floor(support_new × basis_2_1 / basis)', rounding: 'FLOOR_WON',
                    ref: 'V2 §13.3 L581');
                $ctx->emit(self::STEP, 'support_part_1_1', sub($newEff, $part21), $c, line: $ln->label, agreement: $aid,
                    inputs: ['support_new' => $newEff, 'part_2_1' => $part21], formula: 'P1.1 몫 = 신규 발생액 − P2.1 몫',
                    code: 'part_1_1 = support_new − part_2_1', ref: 'V2 §13.3 L581');
            }
            $own = $b['own'];
            $ctx->own_holder[(string)$aid] = ['contract' => $c, 'distributable' => floor_won($own), 'basis' => $basis];
            $ctx->emit(self::STEP, 'own_holder_output', floor_won($own), $c, line: $ln->label, agreement: $aid,
                inputs: ['요율 기준 모수' => $basis], before: $own, rounding: 'FLOOR_WON',
                formula: '자사 권리자 산출액 = 요율 기준 모수 × 자사 1계층 지분율(자사 BASIC 100%) — 발생액 아님, 재원 한도',
                code: 'own = Σ base × own_share_ratio/100', ref: 'V2 L159 · V1 L262~264',
                provisional: true, note: '절사 위치 정본 없음(표시용 내림)');
        }
    }

    /** 7단계 승인 항목을 미리 모은다(6단계 상계 적격 판단에 CONDITIONAL 일시 · 분할 지원금이 필요, V2 L222). */
    private static function lumpsumCollect(Context $ctx): void
    {
        foreach ($ctx->input['lumpsum_approvals'] as $r) {
            $c = $ctx->contract($r['contract_id']);
            if (!$c) {
                continue;
            }
            if (either(g($r, 'approval_status'), 'APPROVED') !== 'APPROVED' || head(pystr(g($r, 'target_month')), 7) !== $ctx->month) {
                continue;
            }
            $c->lumpsum_rows[] = $r;
            $h = $ctx->holder($c->holder_id);
            $kind = g($r, 'item_kind');
            $cat = either(g($r, 'income_category'), g($h, 'income_category'));
            $mid = $r['milestone_id'];
            $offsetType = g($r, 'offset_type');
            if ($kind === 'LUMP_SETTLE' && !truthy($offsetType)) {
                $agr = self::findAgreement($ctx, g($r, 'agreement_id')) ?? [];
                $offsetType = g($agr, 'offset_type');
            }
            $conditional = in_array($kind, ['SUPPORT_LUMP_SUM', 'SUPPORT_INSTALLMENT', 'LUMP_SETTLE'], true)
                && $offsetType === 'CONDITIONAL';
            $payee = g($r, 'payee_id');
            $ln = $c->line('LUMPSUM:' . pystr($mid), 'LUMPSUM', ['approval_id' => $mid, 'agreement_id' => g($r, 'agreement_id'),
                'income_category' => $cat, 'income_clause' => g($r, 'income_clause'),
                'tax_threshold_unit_key' => either(g($r, 'tax_threshold_unit_key'),
                    $cat === 'OTHER' ? pystr($c->id) . '+' . pystr($mid) : null),
                'payee_is_author' => g($r, 'payee_is_author'), 'item_kind' => $kind, 'offset_type' => $offsetType,
                'supply_nature' => $kind === 'BUYOUT' ? 'BUYOUT' : 'NONRECURRING', 'protected' => !$conditional,
                'fixed_payee' => (truthy($payee) && $payee !== $c->holder_id) ? $payee : null]);
            $ln->new = $ln->net = D($r['amount']);
            $ln->conditional = $conditional;
        }
    }
}
