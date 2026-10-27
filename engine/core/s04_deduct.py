"""4단계 DEDUCT — 환불 및 프로모션 공제(V2 §8.3 표 L171 · 본문 L196~203, V1 §5.1 L211 · §15, SPEC 7절).

공제 단가는 원 결제 건의 settlement_line_snapshot(당시 요율 · 지분율 · rate_type · 수취인 분할)으로 대칭 공제.
  net_1_1 = 보정 후 P1.1 − 환불 공제 − 옵션 B 분담 − 옵션 C 차감
  net_2_1 = P2.1 − 반품 차감,  net_2_2 = P2.2 − 위탁 반품 차감 + 1단계 위탁 전용 잔액
  support_deduct_total[agr] = refund_5_1 + optB_5_1 + optC_5_1 (원거래 확정 배분액 역참조, 미환불 확정액 한도)
절사: 라인 월 합산 후 1회 floor(절대값 내림 후 부호 복원). P5.1 일반 환불 · 옵션 B는 원거래 단위 floor(V2 L201, Q-08).
"""

from collections import OrderedDict, defaultdict

from .money import D, alloc_last_remainder, floor_won, pct, q4
from .pipeline import month_of

STEP = "DEDUCT"


def ratio_of(rf_ratio, amount, base):
    if rf_ratio is not None:
        return pct(rf_ratio)
    if base:
        return D(amount) / D(base)
    return D(0)


def run(ctx):
    acc = defaultdict(lambda: defaultdict(lambda: D(0)))  # contract → category → Σ q4
    comps = defaultdict(list)  # (contract, line label) → [component]
    sup = defaultdict(lambda: {"refund_5_1": D(0), "optB_5_1": D(0), "optC_5_1": D(0), "txs": []})
    cons_ret = defaultdict(lambda: defaultdict(lambda: D(0)))

    for rf in ctx.input["refund_lines"]:
        if rf.get("voucher_id"):  # 환불 사후 보정 전표(ADJ-*) — 반영 기준월 규칙(S-10)
            if not voucher_in_deduct(ctx, rf):
                continue
        elif rf.get("refund_approved_date") and month_of(rf["refund_approved_date"]) != ctx.month:
            continue
        if rf.get("lecture_refund"):
            rf = dict(rf, refund_amount=lecture_refund_amount(ctx, rf))
        rf = dict(rf, refund_amount=cash_basis(ctx, rf))
        for snap in rf.get("snapshot") or []:
            c = ctx.contract(snap.get("contract_id"))
            if not c:
                continue
            refund_snapshot(ctx, c, rf, snap, acc, comps, sup, cons_ret)

    for pr in ctx.input["pass_refund_deductions"]:
        if pr.get("approved_date") and month_of(pr["approved_date"]) != ctx.month:
            continue
        opt = pr.get("option")
        for snap in pr.get("snapshot") or []:
            c = ctx.contract(snap.get("contract_id") or pr.get("contract_id"))
            if not c:
                continue
            pass_refund_snapshot(ctx, c, pr, opt, snap, acc, comps, sup)

    for c in ctx.contracts.values():
        finish_contract(ctx, c, acc[c.id], comps, sup, cons_ret[c.id])


def next_month(m):
    y, mo = int(m[:4]), int(m[5:7])
    return f"{y + (mo == 12)}-{(mo % 12) + 1:02d}"


def voucher_applied_month(ctx, rf):
    """보정 전표 반영 기준월 = 승인 시점에 마감되지 않은 가장 이른 귀속월(원 발생월부터, V2 §10.2 L365 · S-10).
    마감 시각은 params.month_closed_at {월: 마감 일시}(없으면 미마감)."""
    origin = str(rf.get("origin_month") or month_of(rf.get("approved_at") or rf.get("refund_approved_date")))[:7]
    approved = str(rf.get("approved_at") or rf.get("refund_approved_date") or "")
    closed = ctx.p("month_closed_at") or {}
    m = origin
    while m < approved[:7]:
        at = closed.get(m)
        if at and str(at) <= approved:
            m = next_month(m)
        else:
            break
    return origin, m


def voucher_in_deduct(ctx, rf):
    """원 발생월이 미마감이면 그 달 4단계에 합산, 마감됐으면 진행 중인 달의 수동 조정 라인(마감 월 재개 없음)."""
    origin, applied = voucher_applied_month(ctx, rf)
    snap = (rf.get("snapshot") or [{}])[0]
    c = ctx.contract(snap.get("contract_id"))
    route = "DEDUCT" if applied == origin else "MANUAL_ADJUSTMENT"
    if applied != ctx.month:
        return False
    ctx.emit(STEP, "voucher_applied_month", applied, c, ref_id=rf["voucher_id"],
             inputs={"origin_month": origin, "approved_at": rf.get("approved_at") or rf.get("refund_approved_date"),
                     "month_closed_at": {k: v for k, v in (ctx.p("month_closed_at") or {}).items() if k >= origin}},
             formula="보정 전표 반영 기준월 = 승인 시점에 마감되지 않은 가장 이른 귀속월(원 발생월 보존) — 원 발생월 미마감이면 "
                     "그 달 4단계 DEDUCT, 마감됐으면 진행 중인 달의 정산 수동 조정 라인",
             code="applied_month = first m ≥ origin_month with closed_at(m) is None or > approved_at",
             ref="V2 §10.2 L365 · 통합 설계서 RFD-003-S2 L370 · S-10(2026-10-27)")
    ctx.emit(STEP, "voucher_route", route, c, ref_id=rf["voucher_id"], formula="보정 전표 반영 경로",
             ref="V2 §10.2 L365")
    if route == "DEDUCT":
        return True
    # 마감된 원 발생월 → 진행 중인 달의 전월 정산 조정 라인: 원거래 스냅샷 대칭 R/S 공제액을 세전 음수 조정으로
    refund = lecture_refund_amount(ctx, rf) if rf.get("lecture_refund") else D(rf.get("refund_amount"))
    rf = dict(rf, refund_amount=refund)
    base = cash_basis(ctx, rf)
    for s in rf.get("snapshot") or []:
        if (s.get("rate_type") or "BASIC") != "BASIC":
            continue
        raw = base * pct(s.get("share_ratio")) * pct(s.get("rate_value"))
        amt = ctx.emit(STEP, "voucher_adjustment_amount", -floor_won(q4(raw)), c, ref_id=rf["voucher_id"],
                       inputs={"환불 현금분": base, "snap.share_ratio": s.get("share_ratio"), "snap.rate_value": s.get("rate_value")},
                       formula="마감된 달의 보정 전표 → 진행 중인 달 전월 정산 조정(세전): −내림(환불 현금분 × 원거래 지분 × 원거래 요율)",
                       code="adj = −floor(q4(cash_basis × share × rate))", before=-raw, rounding="ABS_FLOOR_SIGN",
                       ref="V2 §10.1 L353 · §10.2 L365 · S-10 · 2026-10-27 white 결정(조정 라인은 세금 계산 직전)")
        ctx.auto_adjustments.append({
            "adj_id": rf["voucher_id"], "source": "REFUND_VOUCHER", "contract_id": s.get("contract_id"),
            "payee_id": s.get("rights_holder_id"), "snapshot_payee_splits": s.get("payee_splits") or [],
            "origin_month": origin, "applied_month": applied, "adj_reason_code": "REFUND_OMIT",
            "adj_amount": amt, "account_type": "PRE_TAX", "pipeline_id": str(s.get("pipeline_id") or "1.1"),
            "refund_amount": refund})
    return False


def restored_points(rf, refund):
    """포인트를 쓴 강좌 라인: 복원 포인트 = 내림(라인 사용 포인트 × 환불액 ÷ 라인 결제액)(통합 설계서 RFD-002 L365)."""
    lr = rf.get("lecture_refund") or {}
    if lr.get("point_used"):
        paid = D(lr["paid_amount"])
        return floor_won(D(lr["point_used"]) * refund / paid) if paid else D(0)
    return D(rf.get("refund_point_amount") or 0)


def cash_basis(ctx, rf):
    """권리자 R/S 공제 기준 = 환불액 중 현금분(포인트 복원분 제외) — R/S 모수가 포인트 할인을 뺀 실결제액이라 대칭
    (V2 §8.3 1단계 Step 1 L133 · §8.1, 2026-10-27 white 결정)."""
    if rf.get("refund_amount") is None:  # 수량 기준 반품(위탁 · 도서)은 금액 없이 들어온다
        return None
    refund = D(rf.get("refund_amount"))
    pts = restored_points(rf, refund)
    if not pts:
        return refund
    snap = (rf.get("snapshot") or [{}])[0]
    c = ctx.contract(snap.get("contract_id"))
    return ctx.emit(STEP, "refund_cash_basis", refund - pts, c, ref_id=rf.get("voucher_id") or rf.get("refund_id"),
                    inputs={"환불액": refund, "복원 포인트": pts,
                            "라인 사용 포인트": (rf.get("lecture_refund") or {}).get("point_used")},
                    formula="권리자 R/S 공제 기준 = 환불액 − 복원 포인트(복원 포인트 = 내림(라인 사용 포인트 × 환불액 ÷ 라인 결제액)) — "
                            "R/S 모수가 쿠폰 · 포인트 할인을 뺀 실결제액이므로 공제도 현금분만",
                    code="cash_basis = refund − floor(point_used × refund / line_paid)", rounding="FLOOR_WON",
                    ref="V2 §8.3 1단계 Step 1 L133 · 통합 설계서 RFD-002 L365 · white 결정(2026-10-27)")


def lecture_refund_amount(ctx, rf):
    """인강 환불액(통합 설계서 RFD-002 L364~365, D-ORD-03 · 평생교육법 시행령 별표 3 비고 4).
    7일 이내 + 2강 이하 수강(맛보기 제외) → 전액, 그 밖 → 내림(강좌 실결제액 × (전체 회차 − 학습 회차) ÷ 전체 회차),
    원 수강기간이 끝난 강좌 → 0. 회차를 1초라도 재생하면 학습 회차(입력 learned_sessions가 이미 그 기준)."""
    lr = rf["lecture_refund"]
    paid = D(lr["paid_amount"])
    total = D(lr["total_sessions"])
    learned = D(lr["learned_sessions"])
    days = lr.get("days_since_payment")
    snap = (rf.get("snapshot") or [{}])[0]
    c = ctx.contract(snap.get("contract_id"))
    kw = dict(ref_id=rf.get("voucher_id") or rf.get("refund_id"),
              inputs={"강좌 실결제액": paid, "전체 회차": total, "학습 회차": learned, "결제 후 경과일": days,
                      "원 수강기간 종료": bool(lr.get("course_period_ended"))},
              ref="통합 설계서 RFD-002 L364~365 · D-ORD-03(2026-10-27) · 평생교육법 시행령 별표 3 비고 4")
    if lr.get("course_period_ended"):
        return ctx.emit(STEP, "lecture_refund_amount", D(0), c, **kw, formula="원 수강기간이 끝난 강좌는 반환하지 않는다",
                        code="refund = 0")
    if days is not None and D(days) <= 7 and learned <= 2:
        return ctx.emit(STEP, "lecture_refund_amount", paid, c, **kw,
                        formula="결제일로부터 7일 이내이면서 맛보기 제외 2강 이하 수강 → 실결제액 100% 환불",
                        code="refund = paid_amount")
    raw = paid * (total - learned) / total if total else D(0)
    return ctx.emit(STEP, "lecture_refund_amount", floor_won(raw), c, **kw,
                    formula="환불액 = 강좌 실결제액 × (전체 회차 − 학습 회차) ÷ 전체 회차(원 단위 절사)",
                    code="refund = floor(paid × (total − learned) / total)", before=raw, rounding="FLOOR_WON")


def refund_snapshot(ctx, c, rf, snap, acc, comps, sup, cons_ret):
    pl = str(snap.get("pipeline_id"))
    rt = snap.get("rate_type") or "BASIC"
    ref = rf.get("refund_id")
    if rt == "SUPPORT":
        ratio = ratio_of(rf.get("refund_ratio"), rf.get("refund_amount"), snap.get("base_amount"))
        alloc = D(snap.get("confirmed_alloc_amount"))
        unref = D(snap.get("unrefunded_amount") if snap.get("unrefunded_amount") is not None else alloc)
        raw = alloc * ratio
        amt = min(floor_won(raw), unref)
        aid = snap.get("agreement_id")
        s = sup[aid]
        s["refund_5_1"] += ctx.emit(
            STEP, "refund_5_1_tx", amt, c, line=f"5.1:{aid}", agreement=aid, ref_id=ref,
            inputs={"원거래 지원금 확정 배분액": alloc, "환불 비율": ratio, "원거래 미환불 확정액": unref},
            formula="원거래 정산 스냅샷의 지원금 확정 배분액 역참조(각 원거래 미환불 확정액 한도), 당월 요율로 재산정 금지",
            code="refund_5_1 = min(floor(support_confirmed_alloc × refund_ratio), unrefunded_support_confirmed)",
            before=raw, rounding="FLOOR_WON", ref="V2 §8.3 4단계 L201", output=False)
        s["txs"].append({"ref_id": ref, "deduct_5_1": amt, "unrefunded": unref})
        comps[(c.id, f"5.1:{aid}")].append(component(ref, "refund", amt, snap, c))
        return
    if pl == "2.2":
        ratio = ratio_of(rf.get("refund_ratio"), None, None) if rf.get("refund_ratio") is not None else (
            D(rf.get("refund_qty")) / D(snap.get("confirmed_qty")) if snap.get("confirmed_qty") else D(0))
        sales = D(rf["refund_amount"]) if rf.get("refund_amount") is not None else floor_won(D(snap.get("base_amount")) * ratio)
        fee = floor_won(D(snap.get("fee_supply_alloc")) * ratio)
        vat = floor_won(D(snap.get("fee_vat_alloc")) * ratio)
        r = cons_ret[c.id]
        r["sales"] += sales
        r["fee"] += fee
        r["vat"] += vat
        ctx.emit(STEP, "consignment_return_tx", -sales, c, line="2.2", ref_id=ref,
                 inputs={"반품 비율": ratio, "원 판매대금": snap.get("base_amount"),
                         "원 배분 수수료 공급가액": snap.get("fee_supply_alloc"), "원 배분 수수료 부가세": snap.get("fee_vat_alloc"),
                         "수수료 조정": -fee, "수수료 부가세 조정": -vat},
                 formula="원판매에 확정 · 배분된 판매대금 · 수수료 공급가액 · 수수료 부가세를 각각 참조해 반대 부호로 조정",
                 code="sales_adj = −base × ratio; fee_adj = −floor(fee_alloc × ratio); vat_adj = −floor(vat_alloc × ratio)",
                 rounding="ABS_FLOOR_SIGN", ref="V1 §6.6 L509 · V4 Case 10-B L253", output=False)
        return
    share, rate = snap.get("share_ratio"), snap.get("rate_value")
    if pl == "2.1":
        base = D(rf["refund_amount"]) if rf.get("refund_amount") is not None else (
            D(snap.get("base_amount")) * D(rf.get("refund_qty")) / D(snap.get("confirmed_qty") or 1))
        cat = "return_2_1"
        formula = "자사 발행 도서 인세 반품 차감 — 원 판매 확정 시점의 정가 · 요율 · 지분율 스냅샷"
        cref = "V1 §6.3 L430 · V2 L199"
    else:
        base = D(rf.get("refund_amount"))
        cat = "refund_1_1"
        formula = "환불 공제 = 환불 기준금 × 원거래 스냅샷 지분율 × 원거래 스냅샷 요율(대칭 공제)"
        cref = "V1 §5.1 L211 · V2 L198 · L202"
    raw = base * pct(share) * pct(rate)
    amt = q4(raw)
    acc[c.id][cat] += ctx.emit(STEP, f"{cat}_tx", amt, c, line=pl, ref_id=ref,
                               inputs={"환불 기준금": base, "snap.share_ratio": share, "snap.rate_value": rate,
                                       "payment_state": snap.get("payment_state")},
                               formula=formula, code="q4(refund_base × snap.share_ratio/100 × snap.rate_value/100)",
                               before=raw, rounding="Q4", ref=cref, output=False)
    comps[(c.id, pl)].append(component(ref, cat, amt, snap, c))


def pass_refund_snapshot(ctx, c, pr, opt, snap, acc, comps, sup):
    rt = snap.get("rate_type") or "BASIC"
    ref = pr.get("pass_refund_id")
    if opt == "A" or opt is None:
        ctx.emit(STEP, "option_a", D(0), c, ref_id=ref, inputs={"option": "A"},
                 formula="옵션 A 플랫폼 전액 부담 — R/S 모수 · MMG 모수 영향 없음, 재연산 없음",
                 ref="V1 §15.1 L602~604", output=False)
        return
    if rt == "SUPPORT":
        alloc = D(snap.get("confirmed_alloc_amount"))
        unref = D(snap.get("unrefunded_amount") if snap.get("unrefunded_amount") is not None else alloc)
        aid = snap.get("agreement_id")
        s = sup[aid]
        if opt == "B":
            raw = alloc * pct(pr.get("optB_burden_ratio") or 0)
            amt = min(floor_won(raw), unref)
            key, rnd, note = "optB_5_1", "FLOOR_WON", ""
            code = "optB_5_1 = min(floor(alloc × optB_burden_ratio), unrefunded)"
        else:
            raw = alloc * pct(pr.get("optC_cancel_ratio") or 100)
            amt = min(q4(raw), unref)
            key, rnd, note = "optC_5_1", "Q4", "Q-08: 옵션 C는 정본에 내림 없음 — q4 유지 후 라인 합산 floor"
            code = "optC_5_1 = min(alloc × optC_cancel_ratio, unrefunded)"
        s[key] += ctx.emit(STEP, f"{key}_tx", amt, c, line=f"5.1:{aid}", agreement=aid, ref_id=ref,
                           inputs={"원거래 지원금 확정 배분액": alloc, "원거래 미환불 확정액": unref, "option": opt},
                           formula="합격 환급반 옵션 B · C 지원금 차감 — 원거래 지원금 확정 배분액 한도 역참조",
                           code=code, before=raw, rounding=rnd, ref="V2 L201 · V1 §15.3 L625",
                           provisional=opt == "C", note=note, output=False)
        s["txs"].append({"ref_id": ref, "deduct_5_1": amt, "unrefunded": unref})
        comps[(c.id, f"5.1:{aid}")].append(component(ref, key, amt, snap, c))
        return
    base = D(pr.get("refund_amount"))
    raw = base * pct(snap.get("share_ratio")) * pct(snap.get("rate_value"))
    amt = q4(raw)
    cat = "optB_1_1" if opt == "B" else "optC_1_1"
    acc[c.id][cat] += ctx.emit(
        STEP, f"{cat}_tx", amt, c, line="1.1", ref_id=ref,
        inputs={"환급금": base, "snap.share_ratio": snap.get("share_ratio"), "snap.rate_value": snap.get("rate_value")},
        formula=("합격 환급반 옵션 B — 환급금을 계약상 R/S 지분율과 같은 비율로 분담" if opt == "B"
                 else "합격 환급반 옵션 C — 원 매출 취소로 간주, 결제액 기준 R/S 스냅샷 대칭 공제"),
        code="q4(refund_amount × snap.share_ratio/100 × snap.rate_value/100)", before=raw, rounding="Q4",
        ref="V1 §15.1 L605~607 · §15.3 L625", note="Q-09 총괄 해석 채택(2026-10-26)" if opt == "B" else "",
        output=False)
    comps[(c.id, "1.1")].append(component(ref, cat, amt, snap, c))


def component(ref, cat, amt, snap, c):
    state = snap.get("payment_state") or "UNPAID"
    return {"ref_id": ref, "category": cat, "weight": D(amt), "payment_state": state,
            "snapshot_payee_splits": snap.get("payee_splits") or [],
            "paid_return_post_tax_amount": snap.get("paid_return_post_tax_amount"),
            "paid_portion_amount": snap.get("paid_portion_amount"),
            "unpaid_portion_amount": snap.get("unpaid_portion_amount"),
            "matrix_case_id": snap.get("matrix_case_id"), "payee_id": snap.get("rights_holder_id") or c.holder_id}


def split_paths(ctx, c, comps_line, total):
    """공제 총액을 원거래 구성요소에 배분하고 지급 상태로 경로 분리(V2 L197, SPEC 7.4 잠정)."""
    comps_line = sorted(comps_line, key=lambda x: str(x["ref_id"]))
    allocs = alloc_last_remainder(total, [x["weight"] for x in comps_line]) if comps_line else []
    unpaid_total = D(0)
    out = []
    for comp, amt in zip(comps_line, allocs):
        st = comp["payment_state"]
        if st == "PAID":
            parts = [("PAID_RETURN", amt)]
        elif st == "PARTIAL":
            pp, up = D(comp["paid_portion_amount"]), D(comp["unpaid_portion_amount"])
            unpaid = floor_won(amt * up / (pp + up)) if (pp + up) else amt
            parts = [("UNPAID_REDUCTION", unpaid), ("PAID_RETURN", amt - unpaid)]
        else:
            parts = [("UNPAID_REDUCTION", amt)]
        for path, a in parts:
            if not a:
                continue
            row = dict(comp, path=path, amount=-a)
            out.append(row)
            if path == "UNPAID_REDUCTION":
                unpaid_total += a
            else:
                c.return_claims.append({"ref_id": comp["ref_id"], "payee_id": comp["payee_id"],
                                        "post_tax_amount": D(comp.get("paid_return_post_tax_amount")),
                                        "pre_tax_amount": a, "matrix_case_id": comp["matrix_case_id"]})
                ctx.issue("CANON_GAP", "기지급 소득 반환 경로 금액 산식 미확정 — 라인 차감 제외, 세후 반환채권 후보로 10단계 전달",
                          STEP, c.holder_id, "V2 L197 · V4 Case 4 L113", "Q-10")
    return out, unpaid_total


def finish_contract(ctx, c, acc, comps, sup, ret):
    out = c.step_out(STEP)
    cats = OrderedDict()
    for cat, name, cref in (("refund_1_1", "refund_deduct_1_1", "V2 L198"), ("optB_1_1", "optB_deduct_1_1", "V1 L605"),
                            ("optC_1_1", "optC_deduct_1_1", "V1 L606"), ("return_2_1", "return_deduct_2_1", "V2 L199")):
        raw = acc.get(cat, D(0))
        cats[cat] = ctx.emit(STEP, name, floor_won(raw), c, line="2.1" if cat == "return_2_1" else "1.1",
                             inputs={"Σ q4": raw}, formula="공제액은 라인별 월 합산 후 1회 내림(절대값 내림 후 부호 복원)",
                             code=f"{name} = floor(Σ q4)", before=raw, rounding="ABS_FLOOR_SIGN",
                             ref=f"{cref} · §13.1 L566 · L569", note="Q-26")
        out[name] = cats[cat]
    components_out = []
    net_lines = []
    # P1.1
    l11 = c.lines_of("1.1")
    if not l11 and (cats["refund_1_1"] or cats["optB_1_1"] or cats["optC_1_1"]):
        from .s00_pipeline_in import line_1_1
        ln = line_1_1(ctx, c)
        ln.adjusted = D(0)
        l11 = [ln]
    for ln in l11:
        d_total = cats["refund_1_1"] + cats["optB_1_1"] + cats["optC_1_1"] if ln is l11[0] else D(0)
        rows, unpaid = split_paths(ctx, c, comps.get((c.id, ln.label), []), d_total) if d_total else ([], D(0))
        ln.deduct_components = rows
        components_out += rows
        adj = ln.adjusted if ln.adjusted is not None else ln.new
        ln.net = ctx.emit(STEP, "net_1_1", adj - unpaid, c, line=ln.label, line_key=ln.key(),
                          inputs={"보정 후 P1.1": adj, "환불 공제": cats["refund_1_1"], "옵션 B 분담": cats["optB_1_1"],
                                  "옵션 C 차감": cats["optC_1_1"], "기지급 반환 경로 분리액": d_total - unpaid},
                          formula="P1.1 순 강의료 = 보정 후 P1.1 세전액 − 당월 강의 환불 공제액 − 합격 환급반 옵션 B 분담액 − 옵션 C 매출 취소 차감액",
                          code="net_1_1 = adjusted_1_1 − refund − optB − optC (미지급 감액분)", ref="V2 §8.3 4단계 L198")
        ln.deduct_1_1 = d_total
        net_lines.append({"line_key": ln.key(), "amount": ln.net})
    # P2.1
    for i, ln in enumerate(c.lines_of("2.1")):
        d_total = cats["return_2_1"] if i == 0 else D(0)
        rows, unpaid = split_paths(ctx, c, comps.get((c.id, "2.1"), []), d_total) if d_total else ([], D(0))
        ln.deduct_components = rows
        components_out += rows
        ln.net = ctx.emit(STEP, "net_2_1", ln.new - unpaid, c, line=ln.label, line_key=ln.key(),
                          inputs={"P2.1 신규 인세액": ln.new, "당월 도서 반품 차감액": d_total},
                          formula="P2.1 순 인세액 = P2.1 신규 인세액 − 당월 도서 반품 차감액",
                          code="net_2_1 = new_2_1 − return_deduct_2_1", ref="V2 §8.3 4단계 L199")
        net_lines.append({"line_key": ln.key(), "amount": ln.net})
    # P2.2
    if c.consignment is not None or ret or c.carry["cons"]:
        ftype = (c.consignment or {}).get("consignment_fee_type") or c.row.get("consignment_fee_type") or "NET_DEDUCT"
        ln = c.line("2.2", "2.2", supply_nature="BOOK_GOODS")
        sales, fee, vat = ret.get("sales", D(0)), ret.get("fee", D(0)), ret.get("vat", D(0))
        rdeduct = sales - fee if ftype == "NET_DEDUCT" else sales
        out["return_deduct_2_2"] = ctx.emit(
            STEP, "return_deduct_2_2", rdeduct, c, line="2.2",
            inputs={"반품 판매대금": sales, "반품 수수료 공급가액": fee, "consignment_fee_type": ftype},
            formula="위탁 반품 차감액(수수료 부가세 차감 전 위탁 순액 기준, 수수료 부가세 조정은 9단계)",
            code="return_deduct_2_2 = sales_adj − fee_adj (NET_DEDUCT) | sales_adj (GROSS_SETTLE)",
            ref="V2 L200 · V1 L501", provisional=True, note="Q-07")
        cons = c.carry["cons"]
        out["consignment_balance_applied"] = cons
        ln.net = ctx.emit(STEP, "net_2_2", ln.new - rdeduct + cons, c, line="2.2", line_key=ln.key(),
                          inputs={"P2.2 신규 위탁 정산 입력액": ln.new, "당월 위탁 도서 반품 차감액": rdeduct,
                                  "1단계 위탁 전용 잔액": cons},
                          formula="P2.2 순 위탁 정산액 = 신규 위탁 정산 입력액 − 당월 위탁 도서 반품 차감액 + 1단계 위탁 전용 잔액",
                          code="net_2_2 = new_2_2 − return_deduct_2_2 + consignment_balance", ref="V2 §8.3 4단계 L200")
        c.consignment_return = {"sales": sales, "fee": fee, "vat": vat, "fee_type": ftype}
        if sales:
            ret_out = {
                "sales_adjust": -sales, "fee_supply_adjust": -fee, "fee_vat_adjust": -vat,
                "net_deduct_payout_adjust": -sales + fee + vat,
                "gross_settle_sales_adjust": -sales, "gross_settle_separate_claim": -(fee + vat)}
            for k, v in ret_out.items():
                ctx.emit(STEP, k, v, c, line="2.2", inputs={"반품 판매대금": sales, "수수료": fee, "수수료 부가세": vat},
                         formula={"net_deduct_payout_adjust": "NET_DEDUCT 지급 조정 = −판매대금 − (−수수료 공급가액) − (−수수료 부가세)",
                                  "gross_settle_separate_claim": "GROSS_SETTLE 별도 청구 조정 = −(수수료 공급가액 + 수수료 부가세)"}
                         .get(k, "원판매 배분액 대칭 조정"), ref="V1 §6.6 L509 · V4 Case 10-B L253")
            out["consignment_return"] = ret_out
        net_lines.append({"line_key": ln.key(), "amount": ln.net})
    # P5.1
    sd = []
    for ln in c.lines_of("5.1"):
        s = sup.get(ln.agreement_id) or {"refund_5_1": D(0), "optB_5_1": D(0), "optC_5_1": D(0), "txs": []}
        optc = floor_won(s["optC_5_1"])
        total = s["refund_5_1"] + s["optB_5_1"] + optc
        ln.support_deduct = total
        ln.support_txs = s["txs"]
        rows, _ = split_paths(ctx, c, comps.get((c.id, ln.label), []), total) if total else ([], D(0))
        ln.deduct_components = rows
        components_out += rows
        row = {"agreement_id": ln.agreement_id, "refund_5_1": s["refund_5_1"], "optB_5_1": s["optB_5_1"],
               "optC_5_1": optc, "total": total}
        ctx.emit(STEP, "refund_5_1", s["refund_5_1"], c, line=ln.label, agreement=ln.agreement_id,
                 formula="일반 환불 지원금 공제(원거래 단위 내림 합계)", ref="V2 L201")
        ctx.emit(STEP, "optB_5_1", s["optB_5_1"], c, line=ln.label, agreement=ln.agreement_id,
                 formula="옵션 B 지원금 공제(원거래 단위 내림 합계)", ref="V2 L201")
        ctx.emit(STEP, "optC_5_1", optc, c, line=ln.label, agreement=ln.agreement_id, before=s["optC_5_1"],
                 rounding="ABS_FLOOR_SIGN", formula="옵션 C 지원금 차감(라인 합산 후 내림)", ref="V2 L201",
                 provisional=True, note="Q-08")
        ctx.emit(STEP, "support_deduct_total", total, c, line=ln.label, agreement=ln.agreement_id,
                 inputs={"refund_5_1": s["refund_5_1"], "optB_5_1": s["optB_5_1"], "optC_5_1": optc},
                 formula="P5.1 공제 합계 = 일반 환불 + 옵션 B + 옵션 C(4단계 산출 → 5단계 반영)",
                 code="support_deduct_total[agr] = refund_5_1 + optB_5_1 + optC_5_1", ref="V2 §8.3 4단계 L201")
        ctx.emit(STEP, "net_5_1", ln.new - total, c, line=ln.label, agreement=ln.agreement_id,
                 inputs={"P5.1 신규 발생액": ln.new, "P5.1 공제 합계": total},
                 formula="P5.1 공제 후 금액(표시용 — 한도 적용 전 모수에서 차감하지 않고 5단계에서 반영)",
                 code="new_5_1 − support_deduct_total", ref="V2 L158 · L201", provisional=True,
                 note="표시용 파생값(5단계 확정액과 다름)")
        sd.append(row)
    out["support_deduct_total"] = sd
    out["deduct_components"] = [{"ref_id": r["ref_id"], "line_key": None, "path": r["path"], "amount": r["amount"],
                                 "snapshot_payee_splits": r["snapshot_payee_splits"]} for r in components_out]
    out["return_claims"] = c.return_claims
    out["net_lines"] = net_lines
    deduct_total = sum(cats.values()) + sum(r["total"] for r in sd) + (out.get("return_deduct_2_2") or D(0))
    out["deduct_total"] = ctx.emit(STEP, "deduct_total", deduct_total, c, inputs={k: v for k, v in cats.items()},
                                   formula="당월 공제 합계(표시용)", code="Σ 공제", ref="V2 §8.3 4단계")
    net_total = sum(x["amount"] for x in net_lines) + sum(ln.new - ln.support_deduct for ln in c.lines_of("5.1"))
    out["net_total"] = ctx.emit(STEP, "net_total", net_total, c, inputs={"lines": len(net_lines)},
                                formula="공제 후 라인별 세전 순액 합계(표시용, P5.1은 공제 후 발생액)", code="Σ net lines",
                                ref="V2 §8.3 표 4단계 L171")
