"""세무 판정 · 세액 계산(engine/TAX.md · tax_table.json, V2 11장 · §8.3 9단계 L260~283).

classify(): TAX.md [A] 케이스 판정(위에서부터 먼저 맞는 것). matrix_case_id_hint가 있으면 그 값을 쓴다(테스트 고정값).
withhold(): TAX.md [C] 원천징수 — 소득세 내림 → 지방소득세 내림(합산세율 금지), OTHER는 판정 단위 과세표준 기준.
vat(): TAX.md [B] 부가가치세 — VAT_EXCLUDED 10% 가산 / VAT_INCLUDED 100/110 역산.
"""

from .money import D, floor_won

SUPPLY_TO_FREELANCER_CASE = {"LECTURE_RS": "TX-02", "SUPPORT_RS": "TX-02", "ROYALTY": "TX-03", "BUYOUT": "TX-03",
                             "NONRECURRING": "TX-04"}
ROYALTY_LIKE = {"ROYALTY", "BUYOUT"}
ACTIVE_BUSINESS = {None, "", "계속", "ACTIVE", "CONTINUING"}


def is_corp(h):
    return bool(h.get("corp_no") or h.get("corp_yn"))


def pick_hint(hint, supply):
    """hint가 'TX-02/TX-03'처럼 여럿이면 공급 성격으로 고른다."""
    if not hint:
        return None
    cands = [x.strip() for x in str(hint).replace(",", "/").split("/") if x.strip()]
    if len(cands) == 1:
        return cands[0]
    want = SUPPLY_TO_FREELANCER_CASE.get(supply)
    if want in cands:
        return want
    if supply in ROYALTY_LIKE and "TX-09" in cands:
        return "TX-09"
    return cands[0]


def classify(ctx, payee_id, line):
    """→ {case, status, reason, withholding(APPLY/NONE/UNDETERMINED/OUT_OF_SCOPE), vat(rule), table(case row)}"""
    h = ctx.holder(payee_id)
    t = ctx.tax_table["cases"]
    supply = line.get("supply_nature")
    pipeline = line.get("pipeline_id")
    res = {"case": None, "status": "PENDING_REVIEW", "reason": "", "withholding": None, "vat": None}

    def done(case, status, reason, withholding=None):
        row = t.get(case) or {}
        wh = withholding or row.get("withholding")
        res.update(case=case, status=status, reason=reason, withholding=wh, vat=row.get("vat"), table=row)
        return res

    hint = pick_hint(h.get("matrix_case_id_hint"), supply)
    decision = h.get("withholding_decision")  # [신규 명명] 자문 확정 결과(NONE/APPLY) — TAX.md 확인 필요 2 · 3
    # 1. 자사 권리자
    if h.get("is_internal"):
        return done("TX-13" if pipeline == "2.3" else "TX-01", "DECIDED", "is_internal = true")
    # 2. 재화(도서) 공급
    if supply == "BOOK_GOODS" or pipeline in ("2.2", "2.3"):
        if hint == "TX-12":
            return done("TX-12", "PENDING_REVIEW", "미등록 개인 도서 공급자(예외 승인 심사 대기)")
        if pipeline == "2.3":
            return done("TX-13", "DECIDED", "일반 과세 재화")
        return done("TX-11", "DECIDED", "공급 성격이 재화(도서) — 수취인 지위보다 먼저 TX-11")
    # 3. NULL 보류 조건
    holds = []
    if h.get("main_work_external_labor"):
        holds.append("main_work_external_labor = true")
    if h.get("is_resident") is False:
        holds.append("is_resident = false(TX-10 격리)")
    if h.get("business_status") not in ACTIVE_BUSINESS:
        holds.append(f"business_status = {h.get('business_status')}")
    if h.get("tax_type_cd") == "03":
        holds.append("tax_type_cd = 03")
    if not line.get("income_category") and hint not in ("TX-07", "TX-08", "TX-09", "TX-05", "TX-06"):
        holds.append("income_category 미지정")
    if line.get("income_category") == "OTHER" and not line.get("income_clause"):
        holds.append("OTHER and income_clause 미지정")
    if holds:
        res.update(case=None, status="PENDING_REVIEW", reason=" · ".join(holds), withholding=None, vat=None, table={})
        return res
    # 4~6. 케이스(테스트 고정값 우선)
    if hint:
        case = hint
        src = "matrix_case_id_hint"
    elif not h.get("tax_type_cd"):
        case = SUPPLY_TO_FREELANCER_CASE.get(supply)
        src = "개인 프리랜서 공급 성격 판정(TAX.md 확인 필요 1)"
        if not case:
            res.update(reason=f"공급 성격 {supply} 판정 불가", table={})
            return res
    else:
        m = ctx.tax_table["tax_type_cd_map"].get(h["tax_type_cd"]) or {}
        case = m.get("case")
        src = f"tax_type_cd {h['tax_type_cd']}"
        if case == "TX-07" and is_corp(h) and supply in ROYALTY_LIKE:
            case = "TX-09"
        if not case or m.get("status") == "PENDING_REVIEW":
            res.update(case=None, reason=f"{src} — 후보 판정 보류", table={})
            return res
    if case in ("TX-02", "TX-03", "TX-04", "TX-09", "TX-01", "TX-11", "TX-13"):
        return done(case, "DECIDED", src)
    if case == "TX-10":
        res.update(case=None, reason="비거주자(12장, 1차 오픈 격리)", table={})
        return res
    if case == "TX-12":
        return done(case, "PENDING_REVIEW", "미등록 개인 도서 공급자")
    if case == "TX-07" and is_corp(h):
        return done(case, "DECIDED", f"{src} · 법인(원천징수 대상 아님)", "NONE")
    # TX-05 · TX-06 · TX-07(개인) · TX-08: 원천징수 판정 기준 공백(TAX.md 확인 필요 2) — 자문 결과 입력이 있을 때만 확정
    if decision in ("NONE", "APPLY"):
        return done(case, "DECIDED", f"{src} · 자문 확정 입력 withholding_decision = {decision}", decision)
    return done(case, "PENDING_REVIEW", f"{src} · 원천징수 판정 기준 공백(TAX.md 확인 필요 2 · 3)", "UNDETERMINED")


def rates(ctx, case_row, income_category, clause):
    """→ (소득세율, 의제율, 과세최저한 적용, 소액부징수 적용)"""
    p = ctx.tax_table["parameters"]
    if income_category == "OTHER":
        return (D(str(p["income_tax_rate"]["OTHER"])), D(str(p["deemed_expense_rate"].get(clause, 0))), True, True)
    return (D(str(p["income_tax_rate"]["BUSINESS"])), None, False, False)


def withhold_business(ctx, base):
    """사업소득: 소득세 = 내림(과세표준 × 3%), 지방소득세 = 내림(소득세 × 10%). 소액부징수 제외."""
    it_raw = base * rates(ctx, None, "BUSINESS", None)[0]
    it = floor_won(it_raw)
    lt_raw = it * D(str(ctx.p("local_income_tax_rate")))
    lt = floor_won(lt_raw)
    return {"income_tax": it, "local_income_tax": lt, "it_raw": it_raw, "lt_raw": lt_raw}


def withhold_other(ctx, unit_base, clause):
    """기타소득(판정 단위): 필요경비 = 내림(U × 의제율), 기타소득금액 = U − 필요경비, ≤ 50,000이면 0,
    소득세 = 내림(기타소득금액 × 20%), 지방 = 내림(소득세 × 10%), 소득세 < 1,000이면 0(소액부징수)."""
    rate, deemed_rate, _, _ = rates(ctx, None, "OTHER", clause)
    deemed_raw = unit_base * deemed_rate
    deemed = floor_won(deemed_raw)
    amt = unit_base - deemed
    exempt = amt <= D(ctx.p("other_income_min_tax_amount"))
    if exempt:
        it = lt = D(0)
        it_raw = lt_raw = D(0)
    else:
        it_raw = amt * rate
        it = floor_won(it_raw)
        lt_raw = it * D(str(ctx.p("local_income_tax_rate")))
        lt = floor_won(lt_raw)
    small = (not exempt) and it < D(ctx.p("small_amount_exemption_limit"))
    if small:
        it = lt = D(0)
    return {"deemed_expense": deemed, "deemed_raw": deemed_raw, "other_income_amount": amt, "threshold_exempt_yn": exempt,
            "small_amount_exempt_yn": small, "income_tax": it, "local_income_tax": lt, "it_raw": it_raw, "lt_raw": lt_raw,
            "deemed_rate": deemed_rate, "rate": rate}


def vat_of(rule, treatment, amount):
    """→ (공급가액, 부가세, 부가세 반영 후 정산액, 절사 전)"""
    if rule != "TAXABLE_10":
        return amount, D(0), amount, None
    if treatment == "VAT_INCLUDED":
        raw = amount * 100 / 110
        supply = floor_won(raw)
        return supply, amount - supply, amount, raw
    raw = amount * D("0.10")
    v = floor_won(raw)
    return amount, v, amount + v, raw


def estimate_withholding(ctx, payee_id, items):
    """6단계 LOAN 상계용 원천세 상당액(9단계와 같은 순차 산식, V2 L227). items = [(line_attrs, amount)].
    → (합계, 소득세 합계, 지방세 합계, 라인별 [(label, 소득세, 지방세)])"""
    per = []
    units = {}
    for attrs, amt in items:
        cl = classify(ctx, payee_id, attrs)
        if cl["withholding"] not in ("APPLY",) or amt <= 0:
            per.append((attrs["label"], D(0), D(0)))
            continue
        if attrs.get("income_category") == "OTHER":
            units.setdefault((attrs.get("tax_threshold_unit_key"), attrs.get("income_clause")), []).append((attrs, amt))
            continue
        w = withhold_business(ctx, amt)
        per.append((attrs["label"], w["income_tax"], w["local_income_tax"]))
    for (unit, clause), rows in units.items():
        w = withhold_other(ctx, sum(a for _, a in rows), clause)
        per.append((rows[-1][0]["label"], w["income_tax"], w["local_income_tax"]))
        for attrs, _ in rows[:-1]:
            per.append((attrs["label"], D(0), D(0)))
    it = sum(x[1] for x in per)
    lt = sum(x[2] for x in per)
    return it + lt, it, lt, per
