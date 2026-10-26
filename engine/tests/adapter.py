"""fixture 입력(04권 서술형, tests/CASES.md) → 엔진 입력(schema/input.schema.json) 변환.

fixture는 정본 사례를 서술 그대로 옮긴 형식이라 DB 형태 스키마와 다르다. 이 변환은 테스트 접착층이며
엔진 규칙을 바꾸지 않는다. 정본에 없는 값을 채워야 할 때는 notes에 남기고, 그 결과로 생긴 불일치는
OPEN_ISSUES.md에서 '입력 부족'으로 판정한다.
"""

import copy
import re

from core.money import D, floor_won

MONTH = "2026-09"  # fixture에 정산월이 없다 — 12월 · 6개월 강제 정산을 피하는 임의 월(노트 기록)
START = "2026-01-01"
END = "2027-12-31"


def apply_delta(inp, delta):
    """input_delta {"a.b": 값, "payees[0].x": 값} → 입력 사본에 덮어쓰기."""
    inp = copy.deepcopy(inp)
    for path, v in (delta or {}).items():
        toks = re.findall(r"[^.\[\]]+|\[\d+\]", path)
        cur = inp
        for i, t in enumerate(toks):
            last = i == len(toks) - 1
            key = int(t[1:-1]) if t.startswith("[") else t
            if last:
                cur[key] = v
            else:
                nxt = toks[i + 1]
                if isinstance(key, int):
                    cur = cur[key]
                else:
                    if not isinstance(cur.get(key), (dict, list)):
                        cur[key] = [] if nxt.startswith("[") else {}
                    cur = cur[key]
    return inp


def tax_attrs(p):
    """payee_tax_type 서술 → 국세청 과세유형 코드 · 법인 여부(테스트용 해석)."""
    text = f"{p.get('tax_type') or ''} {p.get('payee_tax_type') or ''}"
    first = (p.get("tax_type") or p.get("payee_tax_type") or "")
    if "프리랜서" in first or "개인 사업소득" in first:
        cd = None
    elif "면세" in first:
        cd = "04"
    elif "간이" in first:
        cd = "07" if "세금계산서" in first else "02"
    elif "일반과세" in first:
        cd = "01"
    else:
        cd = None
    return cd, "법인" in text


def per_pipeline(v, pl, default=None):
    if isinstance(v, dict):
        return v.get(pl, default)
    return v if v is not None else default


class Builder:
    def __init__(self, code):
        self.code = code
        self.notes = []
        self.data = {"settlement_month": MONTH, "rights_holders": [], "contracts": [], "rate_lines": [],
                     "lecture_instructors": [], "book_authors": [], "payee_splits": [], "support_fund_agreements": [],
                     "support_fund_agreement_targets": [], "support_fund_ledger_prev": [], "prepayments": [],
                     "order_items": [], "refund_lines": [], "pass_refund_deductions": [], "lumpsum_approvals": [],
                     "clawbacks": [], "carryover_ledger": []}
        self.n = 0
        self.note(f"정산월 {MONTH}(fixture에 없음 — 12월이 아닌 임의 월)")

    def note(self, s):
        if s not in self.notes:
            self.notes.append(s)

    def nid(self, p):
        self.n += 1
        return f"{p}-{self.n}"


def build(inp, code, base=None):
    """→ (엔진 입력 dict 또는 None, notes)"""
    special = SPECIAL.get(code)
    if special:
        return special(inp, code)
    if not isinstance(inp, dict) or not ("sales_lines" in inp or "milestones" in inp or "contract" in inp):
        return None, ["fixture 입력에 금액 · 계약 구조가 없음(정본 D행 서술만) — 계산 입력을 만들 수 없음"]
    b = Builder(code)
    d = b.data
    contract = inp.get("contract") or {}
    payees = inp.get("payees") or []
    psplit = contract.get("payee_split")
    internal = bool(inp.get("is_internal") or inp.get("rights_holder_type") == "INTERNAL")
    if internal:
        holder = "RH-INTERNAL"
    elif len(payees) == 1 and not psplit:
        holder = payees[0]["payee_id"]
    else:
        holder = "RH"
    cat_all = inp.get("income_category")
    hrow = {"rights_holder_id": holder, "rights_holder_type": inp.get("rights_holder_type"), "is_internal": internal,
            "is_resident": True, "payee_is_author": inp.get("payee_is_author"),
            "income_category": cat_all if isinstance(cat_all, str) else (per_pipeline(cat_all, "1.1") or None)}
    rows = {holder: hrow}
    for p in payees:
        r = rows.setdefault(p["payee_id"], {"rights_holder_id": p["payee_id"], "is_resident": True,
                                            "payee_is_author": inp.get("payee_is_author"),
                                            "income_category": hrow["income_category"]})
        cd, corp = tax_attrs(p)
        r.update(payee_tax_type=p.get("payee_tax_type"), tax_type_cd=cd, matrix_case_id_hint=p.get("matrix_case_id"),
                 vat_treatment=p.get("vat_treatment"))
        if corp:
            r["corp_no"] = "CORP"
        if p.get("matrix_case_id") == "TX-07" and not corp and p.get("tax_decision_status") == "DECIDED":
            r["withholding_decision"] = "NONE"
            b.note("TX-07 개인 일반과세 원천징수 비대상 — fixture 전제(세무 자문 확정 후)를 withholding_decision = NONE으로 입력")
    d["rights_holders"] = list(rows.values())
    cid = "C1"
    crow = {"contract_id": cid, "rights_holder_id": holder, "contract_status": "ACTIVE", "start_date": START,
            "current_end_date": END, "min_payout_limit": contract.get("min_payout_limit", 100000),
            "min_claim_limit": contract.get("min_claim_limit", -100000),
            "vat_treatment": next((p.get("vat_treatment") for p in payees if p.get("vat_treatment")), "VAT_EXCLUDED"),
            "refund_promo_burden_type": "A"}
    if contract.get("consignment_fee_rate") is not None:
        crow.update(consignment_fee_rate=contract["consignment_fee_rate"],
                    consignment_fee_type=contract.get("consignment_fee_type") or "NET_DEDUCT",
                    consignment_base_price_type=contract.get("consignment_base_price_type"))
    d["contracts"].append(crow)
    # 요율 라인
    rv = contract.get("rate_value")
    lines = inp.get("sales_lines") or []
    pipes = {str(s.get("pipeline_id") or ("1.1" if s.get("item_type") == "ONLINE_COURSE" else "")) for s in lines}
    mmg = contract.get("mmg_amount") or 0
    rates = {}
    if isinstance(rv, dict):
        for pl, v in rv.items():
            rates[pl] = D(v)
            d["rate_lines"].append({"contract_id": cid, "rate_type": "BASIC", "pipeline_id": pl, "rate_value": v,
                                    "mmg_amount": mmg if pl == "1.1" else None, "start_date": START,
                                    "end_basis": "CONTRACT_LINKED"})
        b.note("한 계약에 파이프라인별 요율(1.1 · 2.1) — rate_lines.pipeline_id(스키마 확장)로 입력")
    elif rv is not None:
        rates["*"] = D(rv)
        d["rate_lines"].append({"contract_id": cid, "rate_type": "BASIC", "rate_value": rv, "mmg_amount": mmg,
                                "start_date": START, "end_basis": "CONTRACT_LINKED"})
    elif "1.1" in pipes or mmg:
        rates["*"] = D(100)
        d["rate_lines"].append({"contract_id": cid, "rate_type": "BASIC", "rate_value": 100, "mmg_amount": mmg,
                                "start_date": START, "end_basis": "CONTRACT_LINKED"})
        b.note("요율 미제시 — R/S 금액을 그대로 쓰도록 BASIC 100% · 지분 100%로 환산")

    def rate(pl):
        return rates.get(pl, rates.get("*", D(100)))
    sf = contract.get("support_fund")
    if sf and sf.get("payment_method") == "REVENUE_SHARE":
        support_rs(b, sf, contract, cid, holder)
    elif sf:
        d["support_fund_agreements"].append({
            "agreement_id": "AGR-1", "contract_id": cid, "rights_holder_id": holder,
            "payment_method": sf.get("payment_method"), "offset_type": sf.get("offset_type"),
            "status": "ACTIVE", "income_category": hrow["income_category"] or "BUSINESS", "start_date": START,
            "end_basis": "CONTRACT_LINKED", "on_termination_policy": "NONE"})
    origin_paid = None
    if base:
        for s in base.get("sales_lines") or []:
            if str(s.get("pipeline_id")) == "1.1" and s.get("paid_amount"):
                origin_paid = D(s["paid_amount"])
    for i, s in enumerate(lines):
        pl = str(s.get("pipeline_id") or "")
        sup = s.get("book_supply_type") or s.get("book_supply_type_snapshot")
        if pl == "1.1" or s.get("item_type") == "ONLINE_COURSE":
            lecture_line(b, s, contract, cid, holder, rate("1.1"), i, origin_paid, inp)
        elif pl == "2.1" or sup == "OWN_PUBLISHED":
            book_line(b, s, contract, cid, holder, inp, i)
        elif pl == "2.2" or sup == "CONSIGNMENT":
            consign_line(b, s, contract, cid, holder, i)
        elif sup == "PURCHASED_RESALE":
            d["order_items"].append({"order_item_id": f"OI-{i}", "item_type": "BOOK", "book_sku_id": f"SKU-R{i}",
                                     "book_supply_type_snapshot": "PURCHASED_RESALE", "confirmed_qty": s.get("units"),
                                     "list_price": s.get("list_price"), "purchase_unit_cost": s.get("purchase_unit_cost"),
                                     "purchase_confirmed_at": f"{MONTH}-20"})
        elif pl == "2.3" or s.get("item_type") == "GOODS":
            d["order_items"].append({"order_item_id": f"OI-{i}", "item_type": "GOODS_ITEM",
                                     "goods_supply_type_snapshot": "DIRECT_SALE", "confirmed_qty": s.get("units"),
                                     "sale_price_incl_vat": s.get("sale_price_incl_vat"),
                                     "purchase_unit_cost": s.get("purchase_unit_cost"),
                                     "purchase_confirmed_at": f"{MONTH}-20"})
            b.note("상품 공급 형태 'PURCHASED_RESALE 또는 DIRECT_SALE' 미확정 — DIRECT_SALE로 입력(결과 동일)")
    for m in inp.get("milestones") or []:
        milestone(b, m, cid, holder, hrow)
    bal = contract.get("prepay_balance") or 0
    if bal:
        t = contract.get("prepayment_tax_type")
        if not t:
            t = "LOAN"
            b.note("선급금 세무 유형 미제시 — LOAN으로 입력(상계 0원이라 결과 무관)")
        d["prepayments"].append({"prepayment_id": "PP-1", "contract_id": cid, "offset_payee_id": holder,
                                 "prepayment_tax_type": t, "prepay_unoffset_balance": bal})
    for s in psplit or []:
        d["payee_splits"].append({"contract_id": cid, "rights_holder_id": holder, "payee_id": s["payee_id"],
                                  "split_ratio": s["split_ratio"], "start_date": START, "end_basis": "CONTRACT_LINKED"})
    carry = inp.get("carry_in") or {}
    for k, acct in (("PRE_TAX", "PRE_TAX"), ("POST_TAX", "POST_TAX"), ("CONSIGNMENT_ONLY", None)):
        if carry.get(k):
            d["carryover_ledger"].append({"ledger_id": f"L-{k}", "rights_holder_id": holder, "payee_id": holder,
                                          "contract_id": cid, "account_type": acct, "pipeline_id": "1.1",
                                          "consignment_balance_yn": acct is None, "carryover_amount": carry[k],
                                          "payout_reservation_status": "NONE", "extinguished_yn": False})
    return d, b.notes


def support_rs(b, sf, contract, cid, holder):
    d = b.data
    d["support_fund_agreements"].append({
        "agreement_id": "AGR-1", "contract_id": cid, "rights_holder_id": holder, "payment_method": "REVENUE_SHARE",
        "cap_type": sf.get("cap_type"), "total_cap_amount": sf.get("total_cap_amount"),
        "rate_basis": sf.get("rate_basis") or "SAME_AS_BASIC", "settlement_scope": sf.get("settlement_scope"),
        "offset_type": sf.get("offset_type"), "cap_restore_on_refund": sf.get("cap_restore_on_refund"),
        "status": sf.get("status"), "income_category": "BUSINESS", "start_date": START, "end_basis": "CONTRACT_LINKED",
        "on_termination_policy": "FORFEIT"})
    d["rate_lines"].append({"contract_id": cid, "rate_type": "SUPPORT", "agreement_id": "AGR-1",
                            "rate_value": sf.get("rate_value"), "start_date": START, "end_basis": "CONTRACT_LINKED"})
    own = contract.get("own_share_ratio")
    d["support_fund_agreement_targets"].append({"agreement_id": "AGR-1", "target_type": "LECTURE", "target_id": "LEC-0",
                                                "start_date": START, "end_basis": "CONTRACT_LINKED",
                                                "own_share_ratio": own})
    consumed = sf.get("cap_consumed_amount")
    if consumed is None and sf.get("remaining_cap") is not None and sf.get("total_cap_amount") is not None:
        consumed = D(sf["total_cap_amount"]) - D(sf["remaining_cap"])
    d["support_fund_ledger_prev"].append({"agreement_id": "AGR-1", "cap_consumed_amount": consumed,
                                          "confirmed_net_total": consumed, "cash_paid_total": None})
    b.note("지원금 전월 원장: confirmed_net_total 초깃값 미제시 — cap_consumed_amount와 같다고 입력, cash_paid_total 미제시")


def lecture_line(b, s, contract, cid, holder, rate, i, origin_paid, inp):
    d = b.data
    share = D(s.get("share_ratio") or contract.get("share_ratio") or 100)
    if "paid_amount" in s:
        paid = D(s["paid_amount"])
    else:
        rs = s.get("new_rs_amount", s.get("settled_rs_amount"))
        paid = D(rs) * 10000 / (rate * share)
        b.note("실결제액 미제시(R/S 금액만) — 실결제액 = R/S ÷ (요율 × 지분)으로 역산")
    lec = "LEC-0" if i == 0 else f"LEC-{i}"
    d["order_items"].append({"order_item_id": f"OI-{i}", "item_type": "LECTURE", "product_id": lec,
                             "paid_amount": paid, "allocation_applied": True, "approved_at": f"{MONTH}-15",
                             "lectures": [{"lecture_id": lec, "lecture_base_amount": paid}]})
    d["lecture_instructors"].append({"lecture_id": lec, "rights_holder_id": holder, "contract_id": cid,
                                     "share_ratio": share, "start_date": START, "end_basis": "CONTRACT_LINKED"})
    refund = s.get("refund_amount") or 0
    state = s.get("origin_payment_state")
    if s.get("refund_deduct_amount"):
        refund = D(s["refund_deduct_amount"]) * 10000 / (rate * share)
        b.note("환불 공제액만 제시 — 환불 기준금 = 공제액 ÷ (요율 × 지분)으로 역산")
    if not refund:
        return
    if state in (None, "UNCONFIRMED"):
        b.note("원거래 지급 상태 미제시 · 미확정 — UNPAID(미지급 대가 감액)로 입력")
    origin = D(paid) if paid else origin_paid
    snaps = [{"settlement_line_id": f"SL-{i}", "contract_id": cid, "rights_holder_id": holder, "pipeline_id": "1.1",
              "rate_type": "BASIC", "rate_value": rate, "share_ratio": share, "base_amount": origin,
              "payment_state": "UNPAID"}]
    if inp.get("origin_confirmed_5_1"):
        snaps.append({"settlement_line_id": f"SL-{i}-S", "contract_id": cid, "rights_holder_id": holder,
                      "pipeline_id": "1.1", "rate_type": "SUPPORT", "agreement_id": "AGR-1",
                      "base_amount": origin, "confirmed_alloc_amount": inp["origin_confirmed_5_1"],
                      "unrefunded_amount": inp["origin_confirmed_5_1"], "payment_state": "UNPAID"})
        b.note("환불 원거래 = 본 케이스(기본형) 결제 — 원거래 결제액 · 지원금 확정 배분액을 기본형 값으로 입력")
    d["refund_lines"].append({"refund_id": f"RF-{i}", "order_item_id": f"OI-ORIGIN-{i}",
                              "refund_approved_date": f"{MONTH}-25", "refund_amount": refund, "snapshot": snaps})


def book_line(b, s, contract, cid, holder, inp, i):
    d = b.data
    sku = f"SKU-{i}"
    d["order_items"].append({"order_item_id": f"OI-{i}", "item_type": "BOOK", "book_sku_id": sku,
                             "book_supply_type_snapshot": "OWN_PUBLISHED", "confirmed_qty": s.get("units"),
                             "royalty_base_price": s.get("list_price"), "purchase_confirmed_at": f"{MONTH}-20"})
    cat = per_pipeline(inp.get("income_category"), "2.1", "BUSINESS")
    clause = per_pipeline(contract.get("income_clause"), "2.1")
    d["book_authors"].append({"book_sku_id": sku, "rights_holder_id": holder, "contract_id": cid, "share_ratio": 100,
                              "start_date": START, "end_basis": "CONTRACT_LINKED", "income_category": cat,
                              "income_clause": clause})


def consign_line(b, s, contract, cid, holder, i):
    d = b.data
    sku = f"SKU-{i}"
    qty, price = D(s.get("units")), D(s.get("list_price"))
    d["order_items"].append({"order_item_id": f"OI-{i}", "item_type": "BOOK", "book_sku_id": sku,
                             "book_supply_type_snapshot": "CONSIGNMENT", "confirmed_qty": qty, "consignment_price": price,
                             "purchase_confirmed_at": f"{MONTH}-20"})
    d["book_authors"].append({"book_sku_id": sku, "rights_holder_id": holder, "contract_id": cid, "share_ratio": 100,
                              "start_date": START, "end_basis": "CONTRACT_LINKED"})
    b.note("위탁 판매가 = fixture list_price(정산 기준가 PAID_AMOUNT 실결제액 미제시)")
    ret = s.get("return_units") or 0
    if ret:
        sales = qty * price
        rate = D(contract.get("consignment_fee_rate") or 0) / 100
        fee = sales - floor_won(sales * (1 - rate))
        d["refund_lines"].append({"refund_id": f"RF-{i}", "order_item_id": f"OI-{i}", "refund_approved_date": f"{MONTH}-28",
                                  "refund_qty": ret,
                                  "snapshot": [{"contract_id": cid, "rights_holder_id": holder, "pipeline_id": "2.2",
                                                "base_amount": sales, "confirmed_qty": qty, "fee_supply_alloc": fee,
                                                "fee_vat_alloc": floor_won(fee * D("0.1")),
                                                "consignment_fee_type": contract.get("consignment_fee_type")}]})
        b.note("반품 원판매 = 같은 달 확정분(80권) — 원판매 배분 수수료 · 수수료 부가세를 같은 달 값으로 입력")


def milestone(b, m, cid, holder, hrow):
    d = b.data
    t = m.get("milestone_type")
    mid = b.nid("M")
    if t in ("EXCLUSIVE_CONTRACT_FEE", "SUPPORT_FUND_LUMP"):
        kind = "SIGNING_BONUS" if t == "EXCLUSIVE_CONTRACT_FEE" else "SUPPORT_LUMP_SUM"
        d["lumpsum_approvals"].append({"milestone_id": mid, "contract_id": cid, "rights_holder_id": holder,
                                       "item_kind": kind, "agreement_id": "AGR-1" if kind == "SUPPORT_LUMP_SUM" else None,
                                       "offset_type": m.get("offset_type"), "amount": m["approved_amount"],
                                       "target_month": MONTH, "approval_status": "APPROVED",
                                       "income_category": hrow.get("income_category") or "BUSINESS"})
    elif t == "EXCLUSIVE_FEE_RETURN":
        d["clawbacks"].append({"clawback_id": mid, "contract_id": cid, "payee_id": holder,
                               "clawback_amount": m["after_tax_prorated_return_amount"],
                               "clawback_offset_consent_yn": True})
        b.note("전속계약금 반환 '청구 선반영' — 반환 상계 동의 연결(clawback_offset_consent_yn = true)로 입력")


# ---------------------------------------------------------------- 부록 D 수치 케이스

def d08(inp, code):
    b = Builder(code)
    d = b.data
    d["rights_holders"].append({"rights_holder_id": "CONSIGNOR", "is_resident": True})
    d["contracts"].append({"contract_id": "C1", "rights_holder_id": "CONSIGNOR", "contract_status": "ACTIVE",
                           "start_date": START, "current_end_date": END, "consignment_fee_rate": 25,
                           "consignment_fee_type": "NET_DEDUCT"})
    d["carryover_ledger"].append({"ledger_id": "L-CONS", "rights_holder_id": "CONSIGNOR", "payee_id": "CONSIGNOR",
                                  "contract_id": "C1", "account_type": None, "pipeline_id": "2.2",
                                  "consignment_balance_yn": True, "carryover_amount": inp["consignment_balance"],
                                  "payout_reservation_status": "NONE", "extinguished_yn": False})
    b.note("'전액 상쇄'에 필요한 당월 위탁 순액(양수) 미제시 — 당월 위탁 판매 없음으로 입력")
    return d, b.notes


def d09(inp, code):
    b = Builder(code)
    d = b.data
    sf = inp["support_fund"]
    d["rights_holders"].append({"rights_holder_id": "H", "is_resident": True, "income_category": "BUSINESS"})
    d["contracts"].append({"contract_id": "C1", "rights_holder_id": "H", "contract_status": "ACTIVE", "start_date": START,
                           "current_end_date": END, "refund_promo_burden_type": inp.get("refund_promo_burden_type")})
    d["rate_lines"].append({"contract_id": "C1", "rate_type": "BASIC", "rate_value": 0, "start_date": START,
                            "end_basis": "CONTRACT_LINKED"})
    d["rate_lines"].append({"contract_id": "C1", "rate_type": "SUPPORT", "agreement_id": "AGR-1", "rate_value": 10,
                            "start_date": START, "end_basis": "CONTRACT_LINKED"})
    basis = D(sf["accrued_amount"]) * 10
    d["order_items"].append({"order_item_id": "OI-0", "item_type": "LECTURE", "paid_amount": basis,
                             "allocation_applied": True, "approved_at": f"{MONTH}-15",
                             "lectures": [{"lecture_id": "LEC-0", "lecture_base_amount": basis}]})
    d["lecture_instructors"].append({"lecture_id": "LEC-0", "rights_holder_id": "H", "contract_id": "C1",
                                     "share_ratio": 100, "start_date": START})
    d["support_fund_agreements"].append({"agreement_id": "AGR-1", "contract_id": "C1", "rights_holder_id": "H",
                                         "payment_method": "REVENUE_SHARE", "cap_type": "CAPPED",
                                         "total_cap_amount": sf["remaining_cap"], "rate_basis": "SAME_AS_BASIC",
                                         "settlement_scope": "PIPELINE_1_1_ONLY", "offset_type": "NON_OFFSET",
                                         "cap_restore_on_refund": True, "status": "ACTIVE",
                                         "income_category": "BUSINESS", "start_date": START})
    d["support_fund_agreement_targets"].append({"agreement_id": "AGR-1", "target_type": "LECTURE",
                                                "target_id": "LEC-0", "start_date": START})
    d["support_fund_ledger_prev"].append({"agreement_id": "AGR-1", "cap_consumed_amount": 0, "confirmed_net_total": 0})
    d["pass_refund_deductions"].append({"pass_refund_id": "PR-1", "contract_id": "C1", "option": "B",
                                        "approved_date": f"{MONTH}-25", "refund_amount": 0,
                                        "optB_burden_ratio": inp.get("burden_ratio"),
                                        "snapshot": [{"contract_id": "C1", "rights_holder_id": "H", "pipeline_id": "1.1",
                                                      "rate_type": "SUPPORT", "agreement_id": "AGR-1",
                                                      "confirmed_alloc_amount": sf["origin_confirmed_amount"],
                                                      "unrefunded_amount": sf["origin_confirmed_amount"]}]})
    b.note("신규 발생 40만 = 모수 400만 × 지원금 요율 10%로 입력(요율 · 모수 미제시), 기본 R/S는 0%로 분리")
    b.note("잔여 한도 15만 = 총한도 15만 · 전월 소진 0으로 입력(총한도 · 소진액 미제시), 한도 복원 사용(cap_restore_on_refund)")
    b.note("옵션 B의 강의 R/S 분담 금액 미제시 — 지원금 분담만 입력")
    return d, b.notes


def d10(inp, code):
    fx = {"contract": dict(inp["contract"], prepayment_tax_type=None), "sales_lines": inp["sales_lines"],
          "payees": [], "income_category": "BUSINESS"}
    d, notes = build(fx, "D-10-generic")
    return d, notes + ["선급금 세무 유형 · 권리자 세무 케이스 미제시 — LOAN · 개인 프리랜서로 입력(상계 0원이라 결과 무관)"]


def d11(inp, code):
    b = Builder(code)
    d = b.data
    net = D(inp["support_fund"]["net_payable"])
    gross = net * 1000 / 967
    if gross != gross.to_integral_value():
        gross = floor_won(gross)
    d["rights_holders"].append({"rights_holder_id": "H", "is_resident": True, "income_category": "BUSINESS",
                                "matrix_case_id_hint": "TX-04"})
    d["contracts"].append({"contract_id": "C1", "rights_holder_id": "H", "contract_status": "TERMINATED",
                           "start_date": START, "current_end_date": f"{MONTH}-30", "termination_date": f"{MONTH}-30",
                           "min_claim_limit": inp.get("min_claim_limit", -100000), "min_payout_limit": 100000})
    d["support_fund_agreements"].append({"agreement_id": "AGR-1", "contract_id": "C1", "rights_holder_id": "H",
                                         "payment_method": "LUMP_SUM", "offset_type": "NON_OFFSET",
                                         "status": "ACTIVE", "income_category": "BUSINESS", "start_date": START})
    d["lumpsum_approvals"].append({"milestone_id": "M-1", "contract_id": "C1", "rights_holder_id": "H",
                                   "item_kind": "SUPPORT_LUMP_SUM", "agreement_id": "AGR-1", "offset_type": "NON_OFFSET",
                                   "amount": gross, "target_month": MONTH, "approval_status": "APPROVED",
                                   "income_category": "BUSINESS"})
    d["prepayments"].append({"prepayment_id": "PP-1", "contract_id": "C1", "offset_payee_id": "H",
                             "prepayment_tax_type": "LOAN", "prepay_unoffset_balance": abs(D(inp["unoffset_prepay"]))})
    b.note(f"세전 지원금 미제시 — 세후 {net}를 사업소득 3.3%로 역산한 {gross}로 입력(Case 6과 같은 값)")
    b.note("선급금 세무 유형 미제시 — LOAN(원금 청구)으로 입력, 해지일 = 정산월 말일")
    return d, b.notes


def d14(inp, code):
    b = Builder(code)
    d = b.data
    d["rights_holders"].append({"rights_holder_id": "H", "is_resident": True, "income_category": "BUSINESS",
                                "tax_type_cd": "01", "matrix_case_id_hint": "TX-07", "withholding_decision": "NONE",
                                "vat_treatment": "VAT_INCLUDED"})
    d["contracts"].append({"contract_id": "C1", "rights_holder_id": "H", "contract_status": "ACTIVE",
                           "start_date": START, "current_end_date": END, "vat_treatment": "VAT_INCLUDED"})
    d["lumpsum_approvals"].append({"milestone_id": "M-1", "contract_id": "C1", "rights_holder_id": "H",
                                   "item_kind": "FIXED_FEE", "amount": inp["total_incl_vat"], "target_month": MONTH,
                                   "approval_status": "APPROVED", "income_category": "BUSINESS"})
    b.note("수취인 케이스 'TX-06 또는 TX-07' — TX-07(원천징수 비대상 전제)로 입력, 총액 라인 성격 미제시 — 정액 수당으로 입력")
    b.note("기타소득 SKU 2건: 과세표준(수입금액) · 소득 조항 · TX-06/07 수취인의 기타소득 판정 근거 미제시 — 입력하지 않음")
    return d, b.notes


SPECIAL = {"D-08": d08, "D-09": d09, "D-10": d10, "D-11": d11, "D-14": d14}
