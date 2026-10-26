"""0단계 PIPELINE_IN — 상위 인입 파이프라인(V2 §8.3 1단계 L129~160, SPEC 3절).

P1.1 강좌 R/S(Step 1~4) · P2.1 자사 발행 인세 · P2.2 위탁 · P2.3 일반 상품(자사 집계 전용) · 비인입 · P5.1 지원금 모수/발생.
결과는 계약 라인(ContractState.lines)의 new 값으로 2단계에 넘긴다.
"""

from collections import OrderedDict, defaultdict

from .money import D, alloc_last_remainder, floor_won, pct, q4
from .pipeline import month_of, valid_on

STEP = "PIPELINE_IN"
SCOPE_1_1 = {"PIPELINE_1_1_ONLY", "PIPELINE_1_1_2_1"}
SCOPE_2_1 = {"PIPELINE_2_1_ONLY", "PIPELINE_1_1_2_1"}


def run(ctx):
    month = ctx.month
    ctx.basis = defaultdict(lambda: {"1.1": D(0), "2.1": D(0), "own": D(0)})  # agreement_id → 지원금 모수 · 자사 산출액
    items = ctx.input["order_items"]
    paid = step1_allocate(ctx, items)
    p11 = defaultdict(lambda: D(0))  # contract_id → Σ rs_q4
    for it in items:
        kind = it.get("item_type")
        if kind == "LECTURE":
            if it.get("approved_at") and month_of(it["approved_at"]) != month:
                continue
            lecture_rs(ctx, it, paid.get(it["order_item_id"], D(it.get("paid_amount"))), p11)
        elif kind == "BOOK":
            if it.get("purchase_confirmed_at") and month_of(it["purchase_confirmed_at"]) != month:
                continue
            sup = it.get("book_supply_type_snapshot")
            if sup in ("PURCHASED_RESALE", "BUNDLED") or not sup:
                exclude_book(ctx, it, sup)
        elif kind == "GOODS_ITEM":
            goods(ctx, it)
        else:
            ctx.excluded_lines.append({"ref_id": it.get("order_item_id"), "reason": f"정산 비인입 품목({kind})",
                                       "canon_ref": "V2 §8.3 1단계 L153~155"})
    # P1.1 Step 4 — 권리자 · 라인 월 합산 1회 내림(V2 L136)
    for cid, total in p11.items():
        c = ctx.contract(cid)
        ln = line_1_1(ctx, c)
        ln.new = ctx.emit(STEP, "p1_1_new", floor_won(total), c, line=ln.label, line_key=ln.key(),
                          inputs={"Σ rs_q4": total}, formula="권리자별 월 합산 단계에서 1회 내림 절사",
                          code="P1_1_new[line] = floor(Σ rs_q4)", before=total, rounding="FLOOR_WON",
                          ref="V2 §8.3 1단계 Step 4 L136 · §13.1 L566")
    royalty_2_1(ctx, [it for it in items if it.get("item_type") == "BOOK"
                      and it.get("book_supply_type_snapshot") == "OWN_PUBLISHED" and in_month(it, month)])
    consignment_2_2(ctx, [it for it in items if it.get("item_type") == "BOOK"
                          and it.get("book_supply_type_snapshot") == "CONSIGNMENT" and in_month(it, month)])
    support_5_1(ctx)
    lumpsum_collect(ctx)


def in_month(it, month):
    return not it.get("purchase_confirmed_at") or month_of(it["purchase_confirmed_at"]) == month


def line_1_1(ctx, c):
    h = ctx.holder(c.holder_id)
    return c.line("1.1", "1.1", rate_type="BASIC", income_category=h.get("income_category") or "BUSINESS",
                  supply_nature="LECTURE_RS")


# ------------------------------------------------------------------ P1.1

def step1_allocate(ctx, items):
    """Step 1 패키지 혜택 소급 안분(V2 §8.1 L98~100 · §8.3 L133 · 13.3 L577).

    순수 강좌 결제 풀(강좌 정가 합 − 쿠폰 · 포인트 할인; 교재 · 배송비는 이 주문 행에 넣지 않는다)을 강좌 정가 비율로
    내림 안분하고, 정렬(강좌 정가 내림차순 → product_id 오름차순)의 마지막 행이 잔여 차액을 받는다.
    """
    out = {}
    orders = {o["order_id"]: o for o in ctx.input["orders"]}
    by_order = defaultdict(list)
    for it in items:
        if it.get("item_type") == "LECTURE" and not it.get("allocation_applied") and it.get("order_id") in orders:
            by_order[it["order_id"]].append(it)
    for oid, rows in by_order.items():
        disc = D(orders[oid]["discount_total"])
        rows = sorted(rows, key=lambda r: (-D(r.get("list_price")), str(r.get("product_id"))))
        lists = [D(r.get("list_price")) for r in rows]
        pool = sum(lists) - disc
        paid = alloc_last_remainder(pool, lists)
        for i, (r, p) in enumerate(zip(rows, paid)):
            last = i == len(rows) - 1
            raw = pool * lists[i] / sum(lists) if sum(lists) else D(0)
            out[r["order_item_id"]] = ctx.emit(
                STEP, "paid_amount", p, holder=None, line="1.1", ref_id=r["order_item_id"],
                inputs={"순수 강좌 결제 풀": pool, "해당 강좌 정가": lists[i], "패키지 내 강좌 정가 합계": sum(lists),
                        "쿠폰 · 포인트 할인": disc},
                formula=("마지막 강좌 라인 = 순수 강좌 결제 풀 − 선행 강좌 합계(잔여 차액)" if last else
                         "개별 강좌 실결제액 = 내림( 순수 강좌 결제 풀 × (해당 강좌 정가 / 패키지 내 강좌 정가 합계) )"),
                code="paid = alloc_last_remainder(pool, list_price 비율), pool = Σlist_price − discount_total",
                before=None if last else raw, rounding="ALLOC_LAST_REMAINDER" if last else "FLOOR_WON",
                ref="V2 §8.1 L98~100 · §8.3 1단계 Step 1 L133 · §13.3 L577", output=False)
    return out


def lecture_rs(ctx, it, paid, p11):
    lectures = it.get("lectures") or [{"lecture_id": it.get("product_id"), "lecture_base_amount": paid}]
    if any(lec.get("lecture_base_amount") is None for lec in lectures):
        w = [D(lec.get("runtime_seconds") or 0) or D(ctx.p("default_weight_seconds")) for lec in lectures]
        tw = sum(w)
        for lec, wi in zip(lectures, w):
            base = q4(paid * wi / tw) if tw else D(0)
            lec = dict(lec)
            lec["lecture_base_amount"] = ctx.emit(
                STEP, "lecture_base_amount", base, line="1.1", ref_id=lec["lecture_id"],
                inputs={"paid_amount": paid, "weight": wi, "Σweight": tw},
                formula="강좌 실결제액을 하위 강의 동영상 원본 러닝타임 가중치로 분할(러닝타임 0초는 기본 가중치)",
                code="lecture_base[i] = q4(paid_amount × w_i / Σw)", before=paid * wi / tw if tw else 0,
                rounding="Q4", ref="V2 §8.3 1단계 Step 2 L134", provisional=True, note="Q-01 · Q-03", output=False)
            one_lecture(ctx, it, lec, p11)
        return
    for lec in lectures:
        one_lecture(ctx, it, lec, p11)


def one_lecture(ctx, it, lec, p11):
    date = str(it.get("approved_at") or "")[:10] or None
    base = q4(lec["lecture_base_amount"])
    maps = [m for m in ctx.input["lecture_instructors"] if m["lecture_id"] == lec["lecture_id"]]
    for m in maps:
        c = ctx.contract(m["contract_id"])
        if not c or not valid_on(m, date, c.row) or not valid_on({"start_date": c.row.get("start_date"),
                                                                    "end_date": c.row.get("current_end_date")}, date):
            ctx.excluded_lines.append({"ref_id": f"{it['order_item_id']}/{lec['lecture_id']}/{m['rights_holder_id']}",
                                       "reason": "유효 매핑 밖(미매핑 · 정산 0원)", "canon_ref": "V1 §4.2 L177~178"})
            continue
        rl = ctx.rate(c.id, "BASIC", date, pipeline_id="1.1")
        if not rl:
            ctx.issue("INPUT_MISSING", f"{c.id} BASIC 요율 라인 없음 — P1.1 0원", STEP, c.holder_id, "V2 L135")
            continue
        raw = base * pct(m["share_ratio"]) * pct(rl["rate_value"])
        rs = q4(raw)
        line_1_1(ctx, c)
        p11[c.id] += ctx.emit(
            STEP, "rs_q4", rs, c, line="1.1", ref_id=f"{it['order_item_id']}/{lec['lecture_id']}",
            inputs={"강의 기준금": base, "권리자 지분율": m["share_ratio"], "계약 요율": rl["rate_value"]},
            formula="강의 기준금 × 권리자 지분율 × 계약 요율(강의 레벨 소수점 4자리 유지)",
            code="rs_q4 = q4(lecture_base × share_ratio/100 × basic_rate/100)", before=raw, rounding="Q4",
            ref="V2 §8.3 1단계 Step 3 · 4 L135~136", output=False)
    # P5.1 모수(강의 대상) — 자사 지분율을 곱하지 않는다(V2 L159)
    for t in ctx.input["support_fund_agreement_targets"]:
        if t["target_type"] == "LECTURE" and t["target_id"] == lec["lecture_id"] and valid_on(t, date):
            add_basis(ctx, t, "1.1", base)


def add_basis(ctx, t, pipeline, base):
    agr = next((a for a in ctx.input["support_fund_agreements"] if a["agreement_id"] == t["agreement_id"]), None)
    if not agr or agr.get("payment_method") != "REVENUE_SHARE":
        return
    scope = agr.get("settlement_scope") or "PIPELINE_1_1_ONLY"
    if (pipeline == "1.1" and scope not in SCOPE_1_1) or (pipeline == "2.1" and scope not in SCOPE_2_1):
        return
    own = t.get("own_share_ratio")
    if own is not None and D(own) <= 0:
        ctx.emit(STEP, "support_basis_skipped", base, holder=agr["rights_holder_id"], contract=agr["contract_id"],
                 agreement=agr["agreement_id"], ref_id=t["target_id"], inputs={"own_share_ratio": own},
                 formula="자사 지분 0% 구간은 발생 0원 · 상태 ACTIVE 유지 · '자사 지분 없음으로 미발생'",
                 ref="V1 L274", output=False)
        return
    b = ctx.basis[agr["agreement_id"]]
    b[pipeline] += base
    if own is not None:
        b["own"] += q4(base * pct(own))


# ------------------------------------------------------------------ P2.1

def royalty_2_1(ctx, items):
    by_sku = OrderedDict()
    for it in items:
        by_sku.setdefault(it.get("book_sku_id"), []).append(it)
    for sku, rows in by_sku.items():
        date = str(rows[0].get("purchase_confirmed_at") or "")[:10] or None
        authors = []
        for a in ctx.input["book_authors"]:
            c = ctx.contract(a["contract_id"])
            if a["book_sku_id"] == sku and c and valid_on(a, date, c.row):
                rl = ctx.rate(c.id, "BASIC", date, pipeline_id="2.1")
                if not rl:
                    ctx.issue("INPUT_MISSING", f"{c.id} 인세 BASIC 요율 없음", STEP, c.holder_id, "V1 §6.3")
                    continue
                authors.append((a, c, D(rl["rate_value"])))
        lines_q4 = [q4(D(r.get("confirmed_qty")) * D(r.get("royalty_base_price")) ) for r in rows]
        gross = sum(lines_q4)
        for t in ctx.input["support_fund_agreement_targets"]:
            if t["target_type"] == "BOOK_SKU" and t["target_id"] == sku and valid_on(t, date):
                add_basis(ctx, t, "2.1", gross)  # 확정 부수 × 약정 기준가(V1 L273)
        if not authors:
            continue
        same = len({rt for _, _, rt in authors}) == 1
        if same:
            rate = authors[0][2]
            raw = sum(q4(x * pct(rate)) for x in lines_q4)
            total = floor_won(raw)
            ctx.emit(STEP, "sku_royalty_total", total, holder=None, ref_id=sku, line="2.1",
                     inputs={"Σ 확정 부수 × 인세 기준가": gross, "인세 기본요율": rate},
                     formula="SKU별 당월 인세 총액 = 내림( Σ( 당월 확정 부수 × 인세 기준가 × (인세 기본요율 / 100) ) )",
                     code="sku_total = floor(Σ q4(qty × price × rate/100))", before=raw, rounding="FLOOR_WON",
                     ref="V2 §8.3 1단계 L139 · V1 §6.3 L433", output=False)
            order = sorted(authors, key=lambda x: (-D(x[0]["share_ratio"]), x[0]["rights_holder_id"]))
            shares = [D(a["share_ratio"]) for a, _, _ in order]
            if sum(shares) == 100:
                amts = alloc_last_remainder(total, shares)
            else:  # 등록 저자 지분 합이 100이 아니면 역산 잔여를 저자에게 몰지 않는다
                amts = [floor_won(total * pct(s)) for s in shares]
                ctx.issue("CANON_GAP", f"SKU {sku} 저자 지분 합 {sum(shares)}% ≠ 100 — 저자별 floor(총액 × 지분)",
                          STEP, None, "V1 L434")
            for (a, c, _), amt in zip(order, amts):
                add_royalty(ctx, a, c, sku, amt, total, "ALLOC_LAST_REMAINDER",
                            "공동 저자 총액 역산 배분(지분 내림차순 → rights_holder_id 오름차순, 마지막 잔여)",
                            "royalty[author] = alloc_last_remainder(sku_total, w=share_ratio)")
        else:
            for a, c, rate in authors:
                raw = sum(q4(x * pct(rate) * pct(a["share_ratio"])) for x in lines_q4)
                add_royalty(ctx, a, c, sku, floor_won(raw), raw, "FLOOR_WON",
                            "요율 · 기준선이 다르면 저자별로 내림( Σ( 부수 × 기준가 × 요율 × 지분율 ) )",
                            "royalty[author] = floor(Σ q4(line × rate × share))")


def add_royalty(ctx, a, c, sku, amt, before, rounding, formula, code):
    h = ctx.holder(c.holder_id)
    cat = a.get("income_category") or h.get("income_category") or "BUSINESS"
    if cat == "OTHER":
        unit = f"{c.id}+{sku}"
        label = f"2.1:{sku}"
        ln = c.line(label, "2.1", rate_type="BASIC", income_category="OTHER", income_clause=a.get("income_clause"),
                    tax_threshold_unit_key=unit, payee_is_author=h.get("payee_is_author"), supply_nature="ROYALTY")
    else:
        ln = c.line("2.1", "2.1", rate_type="BASIC", income_category=cat, supply_nature="ROYALTY")
    ln.new += ctx.emit(STEP, "p2_1_royalty", amt, c, line=ln.label, ref_id=sku, line_key=ln.key(),
                       inputs={"share_ratio": a["share_ratio"], "basis": before}, formula=formula, code=code,
                       rounding=rounding, ref="V1 §6.3 L433~436 · V2 §13.3 L580")


# ------------------------------------------------------------------ P2.2

def consignment_2_2(ctx, items):
    by_contract = OrderedDict()
    for it in items:
        a = next((a for a in ctx.input["book_authors"] if a["book_sku_id"] == it.get("book_sku_id")), None)
        if not a:
            ctx.issue("INPUT_MISSING", f"위탁 품목 {it['order_item_id']}의 위탁 계약 매핑 없음", STEP)
            continue
        by_contract.setdefault(a["contract_id"], []).append(it)
    for cid, rows in by_contract.items():
        c = ctx.contract(cid)
        fee_rate = pct(c.row.get("consignment_fee_rate") or 0)
        sales = D(0)
        net_raw = D(0)
        for r in rows:
            price = D(r.get("consignment_price") if r.get("consignment_price") is not None else r.get("list_price"))
            amt = D(r.get("confirmed_qty")) * price
            sales += amt
            net_raw += amt * (1 - fee_rate)
        net = floor_won(net_raw)
        fee = sales - net
        ftype = c.row.get("consignment_fee_type") or "NET_DEDUCT"
        inp = net if ftype == "NET_DEDUCT" else sales
        c.consignment = {"monthly_sales": sales, "net_before_fee_vat": net, "fee_supply": fee,
                         "consignment_input": inp, "consignment_fee_type": ftype}
        ctx.emit(STEP, "monthly_sales", sales, c, line="2.2", inputs={"Σ 확정 부수 × 위탁 판매가": sales},
                 formula="월 판매대금 = 합계( 당월 확정 부수 × 위탁 판매가 )", code="monthly_sales = Σ(qty × price)",
                 ref="V2 §8.3 1단계 L144 · V1 §6.6 L495")
        ctx.emit(STEP, "net_before_fee_vat", net, c, line="2.2", inputs={"월 판매대금": sales, "위탁 수수료율": fee_rate},
                 formula="수수료 부가세 차감 전 위탁 순액 = 내림( 합계( 당월 확정 부수 × 위탁 판매가 × (1 − 위탁 수수료율) ) )",
                 code="net = floor(Σ qty × price × (1 − fee_rate))", before=net_raw, rounding="FLOOR_WON",
                 ref="V2 §8.3 1단계 L145 · V1 L496")
        ctx.emit(STEP, "fee_supply", fee, c, line="2.2", inputs={"월 판매대금": sales, "위탁 순액": net},
                 formula="위탁 수수료 공급가액 = 월 판매대금 − 수수료 부가세 차감 전 위탁 순액", code="fee = sales − net",
                 ref="V2 §8.3 1단계 L146 · V1 L498(별도 절사 금지)")
        ln = c.line("2.2", "2.2", supply_nature="BOOK_GOODS")
        ln.new = ctx.emit(STEP, "consignment_input", inp, c, line="2.2", inputs={"consignment_fee_type": ftype},
                          formula="NET_DEDUCT면 수수료 부가세 차감 전 위탁 순액, GROSS_SETTLE이면 월 판매대금 전액",
                          code="consignment_input = net if NET_DEDUCT else sales", ref="V2 §8.3 1단계 L147")


# ------------------------------------------------------------------ P2.3 · 비인입

def goods(ctx, it):
    if it.get("purchase_confirmed_at") and month_of(it["purchase_confirmed_at"]) != ctx.month:
        return
    qty = D(it.get("confirmed_qty"))
    price = D(it.get("sale_price_incl_vat") if it.get("sale_price_incl_vat") is not None else it.get("list_price"))
    total = qty * price
    raw = total * 100 / 110
    supply = floor_won(raw)
    vat = total - supply
    ctx.emit(STEP, "p2_3_supply_amount", supply, ref_id=it["order_item_id"], line="2.3",
             inputs={"Σ 확정 수량 × 부가가치세 포함 판매가": total},
             formula="공급가액 = 내림( Σ( 당월 확정 수량 × 부가가치세 포함 판매가 ) × 100 / 110 )",
             code="supply = floor(Σ × 100/110)", before=raw, rounding="FLOOR_WON", ref="V2 §8.3 1단계 L151")
    ctx.emit(STEP, "p2_3_vat_amount", vat, ref_id=it["order_item_id"], line="2.3",
             inputs={"판매대금": total, "공급가액": supply}, formula="부가가치세 = Σ 판매대금 − 공급가액(총액 역산)",
             code="vat = total − supply", ref="V2 §8.3 1단계 L151 · 13장")
    row = {"ref_id": it["order_item_id"], "pipeline_id": "2.3", "matrix_case_id": "TX-13",
           "goods_supply_type": it.get("goods_supply_type_snapshot"), "sales_total": total, "supply_amount": supply,
           "vat_amount": vat, "vat_rate": 10, "withholding_called": False, "payout_amount": 0,
           "in_settlement_statement": False, "correction_channel": 1,
           "evidence_type": ctx.tax_table["cases"]["TX-13"]["evidence_type"],
           "canon_ref": "V2 §8.3 1단계 L148~152 · TAX.md TX-13"}
    if it.get("purchase_unit_cost") is not None:
        row["purchase_amount"] = qty * D(it["purchase_unit_cost"])
    ctx.internal_only.append(row)


def exclude_book(ctx, it, sup):
    ctx.excluded_lines.append({"ref_id": it.get("order_item_id"),
                               "reason": f"도서 공급 형태 {sup or '미지정'} — 정산 입력 파이프라인 비인입",
                               "canon_ref": "V2 §8.3 1단계 L153~155"})
    if sup == "PURCHASED_RESALE":
        qty = D(it.get("confirmed_qty"))
        row = {"ref_id": it.get("order_item_id"), "pipeline_id": None, "kind": "PURCHASED_RESALE",
               "own_sales_amount": qty * D(it.get("list_price")), "payout_amount": 0,
               "in_settlement_statement": False, "matrix_case_id": "TX-11",
               "correction_channel": 4, "evidence_type": ctx.tax_table["cases"]["TX-11"]["evidence_type"],
               "canon_ref": "V2 §8.3 1단계 L153~155(매출 집계 · 매입채무 경로) · TAX.md TX-11"}
        if it.get("purchase_unit_cost") is not None:
            row["purchase_payable_ap"] = qty * D(it["purchase_unit_cost"])
        ctx.emit(STEP, "own_sales_amount", row["own_sales_amount"], ref_id=it.get("order_item_id"),
                 inputs={"confirmed_qty": qty, "list_price": it.get("list_price")},
                 formula="매입 재판매 도서는 권리자 지급 엔진 비인입 — 자사 매출 · 매입채무(AP) 경로로만",
                 ref="V2 §8.3 1단계 L153~155")
        ctx.internal_only.append(row)


# ------------------------------------------------------------------ P5.1

def support_5_1(ctx):
    for agr in ctx.input["support_fund_agreements"]:
        if agr.get("payment_method") != "REVENUE_SHARE":
            continue
        c = ctx.contract(agr["contract_id"])
        if not c:
            continue
        aid = agr["agreement_id"]
        b = ctx.basis[aid]
        basis = b["1.1"] + b["2.1"]
        rl = ctx.rate(c.id, "SUPPORT", None, agreement_id=aid)
        rate = D(rl["rate_value"]) if rl else D(0)
        if not rl:
            ctx.issue("INPUT_MISSING", f"지원금 {aid} SUPPORT 요율 라인 없음", STEP, c.holder_id, "V2 L135")
        h = ctx.holder(c.holder_id)
        payee = agr.get("payee_id")
        ln = c.line(f"5.1:{aid}", "5.1", rate_type="SUPPORT", agreement_id=aid,
                    income_category=agr.get("income_category") or h.get("income_category") or "BUSINESS",
                    income_clause=agr.get("income_clause"), supply_nature="SUPPORT_RS",
                    offset_type=agr.get("offset_type"), protected=agr.get("offset_type") == "NON_OFFSET",
                    fixed_payee=payee if payee and payee != c.holder_id else None)
        raw = basis * pct(rate)
        new = floor_won(raw)
        ctx.emit(STEP, "support_basis", basis, c, line=ln.label, agreement=aid,
                 inputs={"P1.1 기준금": b["1.1"], "P2.1 부수 × 약정 기준가": b["2.1"],
                         "settlement_scope": agr.get("settlement_scope")},
                 formula="요율 기준 모수(rate_basis) 금액 — 자사 지분율을 추가로 곱하지 않음",
                 code="basis = Σ_{targets ∩ scope} rate_basis_amount", rounding="Q4", ref="V2 §8.3 1단계 L159 · V1 L273")
        status = agr.get("status")
        if status != "ACTIVE":
            new_eff = D(0)
            note = f"약정 상태 {status} — 신규 발생 산출 대상 아님(공제 · 복원만 4 · 5단계 인입)"
        else:
            new_eff = new
            note = ""
        ln.new = ctx.emit(STEP, "support_new", new_eff, c, line=ln.label, agreement=aid, line_key=ln.key(),
                          inputs={"요율 기준 모수": basis, "지원금 요율": rate, "status": status},
                          formula="매출연동 개발지원금 당월 신규 발생액 = 내림( 당월 지원금 모수 × (지원금 요율 / 100) )",
                          code="support_new = floor(basis × support_rate/100) if status == ACTIVE else 0",
                          before=raw, rounding="FLOOR_WON", ref="V2 §8.3 1단계 L160 · 2단계 L188",
                          note=note, provisional=status != "ACTIVE", )
        if b["2.1"] and b["1.1"] and new_eff:
            part21 = floor_won(new_eff * b["2.1"] / basis)
            ctx.emit(STEP, "support_part_2_1", part21, c, line=ln.label, agreement=aid,
                     inputs={"support_new": new_eff, "basis_2_1": b["2.1"], "basis": basis},
                     formula="복수 파이프라인: P2.1 몫을 먼저 내림, 잔여 차액을 P1.1에 귀속",
                     code="part_2_1 = floor(support_new × basis_2_1 / basis)", rounding="FLOOR_WON",
                     ref="V2 §13.3 L581")
            ctx.emit(STEP, "support_part_1_1", new_eff - part21, c, line=ln.label, agreement=aid,
                     inputs={"support_new": new_eff, "part_2_1": part21}, formula="P1.1 몫 = 신규 발생액 − P2.1 몫",
                     code="part_1_1 = support_new − part_2_1", ref="V2 §13.3 L581")
        own = b["own"]
        ctx.own_holder[aid] = {"contract": c, "distributable": floor_won(own), "basis": basis}
        ctx.emit(STEP, "own_holder_output", floor_won(own), c, line=ln.label, agreement=aid,
                 inputs={"요율 기준 모수": basis}, before=own, rounding="FLOOR_WON",
                 formula="자사 권리자 산출액 = 요율 기준 모수 × 자사 1계층 지분율(자사 BASIC 100%) — 발생액 아님, 재원 한도",
                 code="own = Σ base × own_share_ratio/100", ref="V2 L159 · V1 L262~264",
                 provisional=True, note="절사 위치 정본 없음(표시용 내림)")


def lumpsum_collect(ctx):
    """7단계 승인 항목을 미리 모은다(6단계 상계 적격 판단에 CONDITIONAL 일시 · 분할 지원금이 필요, V2 L222)."""
    for r in ctx.input["lumpsum_approvals"]:
        c = ctx.contract(r["contract_id"])
        if not c:
            continue
        if (r.get("approval_status") or "APPROVED") != "APPROVED" or str(r.get("target_month"))[:7] != ctx.month:
            continue
        c.lumpsum_rows.append(r)
        h = ctx.holder(c.holder_id)
        kind = r.get("item_kind")
        cat = r.get("income_category") or h.get("income_category")
        mid = r["milestone_id"]
        offset_type = r.get("offset_type")
        if kind == "LUMP_SETTLE" and not offset_type:
            agr = next((a for a in ctx.input["support_fund_agreements"] if a["agreement_id"] == r.get("agreement_id")), {})
            offset_type = agr.get("offset_type")
        conditional = kind in ("SUPPORT_LUMP_SUM", "SUPPORT_INSTALLMENT", "LUMP_SETTLE") and offset_type == "CONDITIONAL"
        payee = r.get("payee_id")
        ln = c.line(f"LUMPSUM:{mid}", "LUMPSUM", approval_id=mid, agreement_id=r.get("agreement_id"),
                    income_category=cat, income_clause=r.get("income_clause"),
                    tax_threshold_unit_key=r.get("tax_threshold_unit_key") or (f"{c.id}+{mid}" if cat == "OTHER" else None),
                    payee_is_author=r.get("payee_is_author"), item_kind=kind, offset_type=offset_type,
                    supply_nature="BUYOUT" if kind == "BUYOUT" else "NONRECURRING", protected=not conditional,
                    fixed_payee=payee if payee and payee != c.holder_id else None)
        ln.new = ln.net = D(r["amount"])
        ln.conditional = conditional
