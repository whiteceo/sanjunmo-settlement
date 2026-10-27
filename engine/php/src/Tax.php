<?php
/**
 * 세무 판정 · 세액 계산(engine/TAX.md · tax_table.json, V2 11장 · §8.3 9단계 L260~283).
 *
 * classify(): TAX.md [A] 케이스 판정(위에서부터 먼저 맞는 것). matrix_case_id_hint가 있으면 그 값을 쓴다(테스트 고정값).
 * withholdBusiness() · withholdOther(): TAX.md [C] 원천징수 — 소득세 내림 → 지방소득세 내림(합산세율 금지),
 *   OTHER는 판정 단위 과세표준 기준.
 * vatOf(): TAX.md [B] 부가가치세 — VAT_EXCLUDED 10% 가산 / VAT_INCLUDED 100/110 역산.
 */

namespace SettleCalc;

use BcMath\Number;

final class Tax
{
    const SUPPLY_TO_FREELANCER_CASE = ['LECTURE_RS' => 'TX-02', 'SUPPORT_RS' => 'TX-02', 'ROYALTY' => 'TX-03',
        'BUYOUT' => 'TX-03', 'NONRECURRING' => 'TX-04'];
    const ROYALTY_LIKE = ['ROYALTY', 'BUYOUT'];
    const ACTIVE_BUSINESS = [null, '', '계속', 'ACTIVE', 'CONTINUING'];

    public static function isCorp(array $h): bool
    {
        return truthy(g($h, 'corp_no')) || truthy(g($h, 'corp_yn'));
    }

    /** hint가 'TX-02/TX-03'처럼 여럿이면 공급 성격으로 고른다. */
    public static function pickHint($hint, $supply): ?string
    {
        if (!truthy($hint)) {
            return null;
        }
        $cands = array_values(array_filter(array_map('trim', explode('/', str_replace(',', '/', pystr($hint)))),
            fn($x) => $x !== ''));
        if (count($cands) === 1) {
            return $cands[0];
        }
        $want = self::SUPPLY_TO_FREELANCER_CASE[$supply] ?? null;
        if ($want !== null && in_array($want, $cands, true)) {
            return $want;
        }
        if (in_array($supply, self::ROYALTY_LIKE, true) && in_array('TX-09', $cands, true)) {
            return 'TX-09';
        }
        return $cands[0] ?? null;
    }

    /** → [case, status, reason, withholding(APPLY/NONE/UNDETERMINED/OUT_OF_SCOPE), vat(rule), table(case row)] */
    public static function classify(Context $ctx, $payeeId, array $line): array
    {
        $h = $ctx->holder($payeeId);
        $t = $ctx->tax_table['cases'];
        $supply = g($line, 'supply_nature');
        $pipeline = g($line, 'pipeline_id');
        $res = ['case' => null, 'status' => 'PENDING_REVIEW', 'reason' => '', 'withholding' => null, 'vat' => null];
        $done = function ($case, $status, $reason, $withholding = null) use ($t, &$res) {
            $row = $t[$case] ?? [];
            $wh = either($withholding, g($row, 'withholding'));
            $res = array_merge($res, ['case' => $case, 'status' => $status, 'reason' => $reason, 'withholding' => $wh,
                'vat' => g($row, 'vat'), 'table' => $row]);
            return $res;
        };
        $hint = self::pickHint(g($h, 'matrix_case_id_hint'), $supply);
        $decision = g($h, 'withholding_decision'); // [신규 명명] 자문 확정 결과(NONE/APPLY) — TAX.md 확인 필요 2 · 3
        // 1. 자사 권리자
        if (truthy(g($h, 'is_internal'))) {
            return $done($pipeline === '2.3' ? 'TX-13' : 'TX-01', 'DECIDED', 'is_internal = true');
        }
        // 2. 재화(도서) 공급
        if ($supply === 'BOOK_GOODS' || in_array($pipeline, ['2.2', '2.3'], true)) {
            if ($hint === 'TX-12') {
                return $done('TX-12', 'PENDING_REVIEW', '미등록 개인 도서 공급자(예외 승인 심사 대기)');
            }
            if ($pipeline === '2.3') {
                return $done('TX-13', 'DECIDED', '일반 과세 재화');
            }
            return $done('TX-11', 'DECIDED', '공급 성격이 재화(도서) — 수취인 지위보다 먼저 TX-11');
        }
        // 3. NULL 보류 조건
        $holds = [];
        if (truthy(g($h, 'main_work_external_labor'))) {
            $holds[] = 'main_work_external_labor = true';
        }
        if (g($h, 'is_resident') === false) {
            $holds[] = 'is_resident = false(TX-10 격리)';
        }
        if (!in_array(g($h, 'business_status'), self::ACTIVE_BUSINESS, true)) {
            $holds[] = 'business_status = ' . pystr(g($h, 'business_status'));
        }
        if (g($h, 'tax_type_cd') === '03') {
            $holds[] = 'tax_type_cd = 03';
        }
        if (!truthy(g($line, 'income_category')) && !in_array($hint, ['TX-07', 'TX-08', 'TX-09', 'TX-05', 'TX-06'], true)) {
            $holds[] = 'income_category 미지정';
        }
        if (g($line, 'income_category') === 'OTHER' && !truthy(g($line, 'income_clause'))) {
            $holds[] = 'OTHER and income_clause 미지정';
        }
        if ($holds) {
            return array_merge($res, ['case' => null, 'status' => 'PENDING_REVIEW', 'reason' => implode(' · ', $holds),
                'withholding' => null, 'vat' => null, 'table' => []]);
        }
        // 4~6. 케이스(테스트 고정값 우선)
        if (truthy($hint)) {
            $case = $hint;
            $src = 'matrix_case_id_hint';
        } elseif (!truthy(g($h, 'tax_type_cd'))) {
            $case = self::SUPPLY_TO_FREELANCER_CASE[$supply] ?? null;
            $src = '개인 프리랜서 공급 성격 판정(TAX.md 확인 필요 1)';
            if (!truthy($case)) {
                return array_merge($res, ['reason' => '공급 성격 ' . pystr($supply) . ' 판정 불가', 'table' => []]);
            }
        } else {
            $m = either($ctx->tax_table['tax_type_cd_map'][(string)$h['tax_type_cd']] ?? null, []);
            $case = g($m, 'case');
            $src = 'tax_type_cd ' . pystr($h['tax_type_cd']);
            if ($case === 'TX-07' && self::isCorp($h) && in_array($supply, self::ROYALTY_LIKE, true)) {
                $case = 'TX-09';
            }
            if (!truthy($case) || g($m, 'status') === 'PENDING_REVIEW') {
                return array_merge($res, ['case' => null, 'reason' => $src . ' — 후보 판정 보류', 'table' => []]);
            }
        }
        if (in_array($case, ['TX-02', 'TX-03', 'TX-04', 'TX-09', 'TX-01', 'TX-11', 'TX-13'], true)) {
            return $done($case, 'DECIDED', $src);
        }
        if ($case === 'TX-10') {
            return array_merge($res, ['case' => null, 'reason' => '비거주자(12장, 1차 오픈 격리)', 'table' => []]);
        }
        if ($case === 'TX-12') {
            return $done($case, 'PENDING_REVIEW', '미등록 개인 도서 공급자');
        }
        if ($case === 'TX-07' && self::isCorp($h)) {
            return $done($case, 'DECIDED', $src . ' · 법인(원천징수 대상 아님)', 'NONE');
        }
        // TX-05 · TX-06 · TX-07(개인) · TX-08: 원천징수 판정 기준 공백(TAX.md 확인 필요 2) — 자문 결과 입력이 있을 때만 확정
        if (in_array($decision, ['NONE', 'APPLY'], true)) {
            return $done($case, 'DECIDED', $src . ' · 자문 확정 입력 withholding_decision = ' . $decision, $decision);
        }
        return $done($case, 'PENDING_REVIEW', $src . ' · 원천징수 판정 기준 공백(TAX.md 확인 필요 2 · 3)', 'UNDETERMINED');
    }

    /** → [소득세율, 의제율, 과세최저한 적용, 소액부징수 적용] */
    public static function rates(Context $ctx, $incomeCategory, $clause): array
    {
        $p = $ctx->tax_table['parameters'];
        if ($incomeCategory === 'OTHER') {
            return [D(pystr($p['income_tax_rate']['OTHER'])), D(pystr($p['deemed_expense_rate'][(string)$clause] ?? 0)), true, true];
        }
        return [D(pystr($p['income_tax_rate']['BUSINESS'])), null, false, false];
    }

    /** 사업소득: 소득세 = 내림(과세표준 × 3%), 지방소득세 = 내림(소득세 × 10%). 소액부징수 제외. */
    public static function withholdBusiness(Context $ctx, Number $base): array
    {
        $itRaw = mul($base, self::rates($ctx, 'BUSINESS', null)[0]);
        $it = floor_won($itRaw);
        $ltRaw = mul($it, D(pystr($ctx->p('local_income_tax_rate'))));
        $lt = floor_won($ltRaw);
        return ['income_tax' => $it, 'local_income_tax' => $lt, 'it_raw' => $itRaw, 'lt_raw' => $ltRaw];
    }

    /**
     * 기타소득(판정 단위): 필요경비 = 내림(U × 의제율), 기타소득금액 = U − 필요경비, ≤ 50,000이면 0,
     * 소득세 = 내림(기타소득금액 × 20%), 지방 = 내림(소득세 × 10%), 소득세 < 1,000이면 0(소액부징수).
     */
    public static function withholdOther(Context $ctx, Number $unitBase, $clause): array
    {
        [$rate, $deemedRate] = self::rates($ctx, 'OTHER', $clause);
        $deemedRaw = mul($unitBase, $deemedRate);
        $deemed = floor_won($deemedRaw);
        $amt = sub($unitBase, $deemed);
        $exempt = $amt <= D($ctx->p('other_income_min_tax_amount'));
        if ($exempt) {
            $it = $lt = D(0);
            $itRaw = $ltRaw = D(0);
        } else {
            $itRaw = mul($amt, $rate);
            $it = floor_won($itRaw);
            $ltRaw = mul($it, D(pystr($ctx->p('local_income_tax_rate'))));
            $lt = floor_won($ltRaw);
        }
        $small = !$exempt && $it < D($ctx->p('small_amount_exemption_limit'));
        if ($small) {
            $it = $lt = D(0);
        }
        return ['deemed_expense' => $deemed, 'deemed_raw' => $deemedRaw, 'other_income_amount' => $amt,
            'threshold_exempt_yn' => $exempt, 'small_amount_exempt_yn' => $small, 'income_tax' => $it,
            'local_income_tax' => $lt, 'it_raw' => $itRaw, 'lt_raw' => $ltRaw, 'deemed_rate' => $deemedRate, 'rate' => $rate];
    }

    /** → [공급가액, 부가세, 부가세 반영 후 정산액, 절사 전] */
    public static function vatOf($rule, $treatment, Number $amount): array
    {
        if ($rule !== 'TAXABLE_10') {
            return [$amount, D(0), $amount, null];
        }
        if ($treatment === 'VAT_INCLUDED') {
            $raw = div(mul($amount, 100), 110);
            $supply = floor_won($raw);
            return [$supply, sub($amount, $supply), $amount, $raw];
        }
        $raw = mul($amount, D('0.10'));
        $v = floor_won($raw);
        return [$amount, $v, add($amount, $v), $raw];
    }

    /**
     * 6단계 LOAN 상계용 원천세 상당액(9단계와 같은 순차 산식, V2 L227). items = [[line_attrs, amount]].
     * → [합계, 소득세 합계, 지방세 합계, 라인별 [[label, 소득세, 지방세]]]
     */
    public static function estimateWithholding(Context $ctx, $payeeId, array $items): array
    {
        $per = [];
        $units = [];
        foreach ($items as [$attrs, $amt]) {
            $cl = self::classify($ctx, $payeeId, $attrs);
            if ($cl['withholding'] !== 'APPLY' || $amt <= 0) {
                $per[] = [$attrs['label'], D(0), D(0)];
                continue;
            }
            if (g($attrs, 'income_category') === 'OTHER') {
                $units[tkey(g($attrs, 'tax_threshold_unit_key'), g($attrs, 'income_clause'))][] = [$attrs, $amt];
                continue;
            }
            $w = self::withholdBusiness($ctx, $amt);
            $per[] = [$attrs['label'], $w['income_tax'], $w['local_income_tax']];
        }
        foreach ($units as $k => $rows) {
            [$unit, $clause] = untkey($k);
            $w = self::withholdOther($ctx, dsum(array_map(fn($x) => $x[1], $rows)), $clause);
            $per[] = [$rows[count($rows) - 1][0]['label'], $w['income_tax'], $w['local_income_tax']];
            foreach (array_slice($rows, 0, -1) as [$attrs, $_]) {
                $per[] = [$attrs['label'], D(0), D(0)];
            }
        }
        $it = dsum(array_map(fn($x) => $x[1], $per));
        $lt = dsum(array_map(fn($x) => $x[2], $per));
        return [add($it, $lt), $it, $lt, $per];
    }
}
