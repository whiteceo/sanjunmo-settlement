"""11단계 PAYOUT — 최소 지급 검증(V2 §8.3 표 L178 · 본문 L299~308, V1 §7.3 · §7.4, SPEC 14절).

판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액,
판정 금액 ≥ min_payout_limit 또는 강제 정산 트리거 → 지급 확정(기존 이월행 RESERVED 예정),
미달 → 당월 신규분 PRE_TAX 기초금액 이월(기존 POST_TAX · PRE_TAX 유지). 판정 기준 = VAT 포함 총액. 절사 없음.
"""

from .money import D, floor_won, floor_ten
from .tax import withhold_business, rates
from .pipeline import months_between

STEP = "PAYOUT"


def run(ctx):
    for c in ctx.contracts.values():
        end = c.closing_due(ctx.month)  # 계약 만료 · 해지 강제 지급도 끝난 달 + 지급 시차 N부터(v4.0.51)
        closed = bool(ctx.holder(c.holder_id).get("business_closed_yn"))
        limit = D(c.row.get("min_payout_limit") if c.row.get("min_payout_limit") is not None
                  else ctx.p("default_min_payout_limit"))
        for p in c.payees.values():
            payout_payee(ctx, c, p, end, closed, limit)
        cash_paid(ctx, c)
        apply_results(ctx, c)


def cash_paid(ctx, c):
    """지원금 원장 cash_paid_total: 실제 지급 이력 기준 — 지급 확정 시 P5.1 라인 세후액을 가산(예정, SPEC 8.3)."""
    for aid, row in c.support.items():
        month = D(0)
        for p in c.payees.values():
            if p.out["PAYOUT"].get("payout_confirmed_yn"):
                # 환불 · 공제로 음수가 된 라인은 지급 누계를 되돌리지 않는다(V2 8.3 5단계 '실제 지급 누계는 되돌리지 않으며')
                month += sum((max(D(0), ln.get("net_settle_line") or D(0)) for ln in p.lines
                              if ln["origin"] == "NEW" and ln["line_id"] == f"5.1:{aid}"), D(0))
        prev = row.get("cash_paid_total")
        if prev is None:
            ctx.issue("INPUT_MISSING", f"지원금 {aid} 전월 cash_paid_total 없음 — 0에서 누계", STEP, c.holder_id,
                      "V2 L213 · SPEC 8.3")
        total = D(prev) + month
        ctx.emit(STEP, "cash_paid_month", month, c, line=f"5.1:{aid}", agreement=aid,
                 formula="당월 지원금 현금 지급액 = 지급 확정된 P5.1 라인 세후 실정산액", ref="V2 L213 · V3 L65~67",
                 provisional=True, note="지급 확정 전 '예정' 값")
        ctx.emit(STEP, "cash_paid_total_after_payout", total, c, line=f"5.1:{aid}", agreement=aid,
                 inputs={"전월 cash_paid_total": prev, "당월 지급": month},
                 formula="cash_paid_total = 전월 누계 + 당월 지원금 현금 지급액(실제 지급 이력 기준)", ref="V2 L213",
                 provisional=True, note="지급 확정 전 '예정' 값")
        for led in ctx.ledgers["support_fund_ledger"]:
            if led["agreement_id"] == aid:
                led["cash_paid_total"] = total


def payout_payee(ctx, c, p, end, closed, limit):
    pid = p.payee_id
    kw = dict(payee=pid)
    o = p.out["PAYOUT"]
    payable = p.out["CLAIM"].get("payable_net_for_payout") or D(0)
    pre_pos = [r for r in c.carry["pre_pos"] if r["payee_id"] == pid]
    # 최소 지급 미달로 양수 줄과 함께 넘어온 음수 줄 — 양수 줄과 같이 지급 · 이월(v4.0.60 정본 공백 보완)
    pre_neg_with = [r for r in c.carry["pre_neg"] if r["payee_id"] == pid and r.get("carry_line_origin")]
    post_pos = [r for r in c.carry["post_pos"] if r["payee_id"] == pid]
    post_total = sum((r["carryover_amount"] for r in post_pos), D(0))
    reasons = []
    firsts = [r.get("first_payable_confirmed_month") for r in pre_pos + post_pos if r.get("first_payable_confirmed_month")]
    if firsts and months_between(str(min(firsts))[:7], ctx.month) >= int(ctx.p("carryover_max_months")):
        reasons.append("SIX_MONTHS")
        ctx.issue("CANON_GAP", "6개월 경과 산정 — 월 차이 ≥ 6으로 판정(잠정)", STEP, c.holder_id, "V1 L562", "Q-20")
    if int(ctx.month[5:7]) == int(ctx.p("carryover_force_settle_month")):
        reasons.append("DECEMBER")
    if end:
        reasons.append("CONTRACT_END")
    if closed:
        reasons.append("BUSINESS_CLOSED")
    designated = bool(ctx.holder(pid).get("carry_designated_yn"))  # 운영자 이월 지정 후 재배치(v4.0.43)
    hold = bool(ctx.holder(pid).get("payout_hold_yn")) or designated
    if hold:
        reasons = []  # 지급 보류 · 운영자 이월 지정 수취인은 강제 정산 없이 세전 이월(v4.0.39 · v4.0.43)
    force = bool(reasons)
    evaluated = payable > 0 or bool(pre_pos) or bool(post_pos) or force
    judge = ctx.emit(STEP, "payout_judgement_amount", payable + post_total, c, **kw,
                     inputs={"당월 지급채무 순액": payable, "POST_TAX 지급대기액": post_total},
                     formula="판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액(VAT 포함 총액 기준)",
                     code="judgement = payable_net_for_payout + Σcarry_post_tax_pos", ref="V2 §8.3 11단계 L302 · L304")
    internal = bool(ctx.holder(pid).get("is_internal"))
    confirmed = evaluated and (judge >= limit or force) and not hold
    o.update(evaluated=evaluated, carry_post_tax_pos_total=post_total, payout_judgement_amount=judge,
             min_payout_limit=limit, force_settle=force, force_settle_reasons=reasons,
             payout_threshold_basis=ctx.p("payout_threshold_basis"), excluded_from_bulk_transfer=internal)
    ctx.emit(STEP, "evaluated", evaluated, c, **kw,
             inputs={"지급채무 순액 > 0": payable > 0, "이월 대기": bool(pre_pos or post_pos), "강제": force},
             formula="평가 대상 = 지급채무 순액 > 0 또는 PRE_TAX · POST_TAX 지급 대기 또는 강제 정산 트리거", ref="V2 L300")
    ctx.emit(STEP, "force_settle", force, c, **kw, inputs={"reasons": reasons},
             formula="강제 정산 = 최초 지급 대상 확정 후 6개월 경과 · 12월 · 계약 만료 · 해지 · 폐업", ref="V1 L561~565")
    o["payout_confirmed_yn"] = ctx.emit(STEP, "payout_confirmed_yn", confirmed, c, **kw,
                                        inputs={"판정 금액": judge, "min_payout_limit": limit, "강제": force},
                                        formula="판정 금액 ≥ min_payout_limit 또는 강제 정산 트리거 → 지급 확정(같으면 지급)",
                                        code="payout_confirmed = judgement >= min_payout_limit or force_settle",
                                        ref="V2 §8.3 표 11단계 L178 · V1 §7.3")
    o["payout_amount"] = ctx.emit(STEP, "payout_amount", judge if confirmed else D(0), c, **kw,
                                  formula="지급 확정액(대량이체 리스트, 부가세 · 원천세 · 상계 재가감 금지)", ref="V2 L303")
    ctx.emit(STEP, "excluded_from_bulk_transfer", internal, c, **kw,
             formula="자사 권리자(TX-01)는 증빙 · 대량이체 제외", ref="V2 L280 · TAX.md TX-01")
    rows = []
    if confirmed:
        for r in pre_pos + pre_neg_with + post_pos:
            rows.append(dict(r, action="RESERVE", payout_reservation_status="RESERVED"))
    elif evaluated:
        # 그 달 순액이 양수면 줄을 고르지 않고 음수 줄까지 모두 이월(음수만 빠져 다음 달 더 지급되는 일 방지,
        # V1 §7.3 · V2 §8.3 11단계, v4.0.60 정본 공백 보완). 순액이 0 이하면 음수는 10단계 청구 경로로 감.
        net_pos = (p.out["CLAIM"].get("net_after_return") or D(0)) > 0
        for ln in p.lines:
            if ln["origin"] in ("NEW", "ADJUSTMENT") and (ln["pre_tax_payable"] > 0 or (net_pos and ln["pre_tax_payable"] < 0)):
                key = ln["line_key"]
                if (ln.get("offset_amount") or D(0)) > 0 and not hold:
                    carry_amt, extra = offset_carry(ctx, c, p, pid, ln)
                else:
                    carry_amt, extra = ln["pre_tax_payable"], {}
                rows.append({"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid,
                             "contract_id": c.id, "origin_month": ctx.month, "account_type": "PRE_TAX",
                             "pipeline_id": key.get("pipeline_id"), "consignment_balance_yn": False,
                             # 전월 정산 조정 줄은 소득 구분이 라인 키가 아니라 라인에 있음 — 라인 값으로 보충(v4.0.60)
                             "income_category": key.get("income_category") or ln.get("income_category"),
                             "income_clause": key.get("income_clause") or ln.get("income_clause"),
                             "tax_threshold_unit_key": key.get("tax_threshold_unit_key") or ln.get("tax_threshold_unit_key"),
                             "carryover_reason": ("운영자 이월 지정" if designated else "지급 보류") if hold else "지급 하한 미달",
                             "carryover_amount": carry_amt,
                             "components": dict({"split_amount": ln["split_amount"], "offset_amount": ln["offset_amount"],
                                                 "vat_amount": ln.get("vat_amount")}, **extra.get("components", {})),
                             "first_occurred_month": ctx.month, "first_payable_confirmed_month": None,
                             "payout_reservation_status": "NONE", "extinguished_yn": False,
                             "carry_line_origin": ln["origin"],
                             **{k: v for k, v in extra.items() if k != "components"}})
        for r in pre_pos + pre_neg_with + post_pos:
            rows.append(dict(r, action="KEEP"))
        if any(r["action"] == "NEW" for r in rows):
            ctx.issue("CANON_GAP", "지급 이월 적재 구성요소(VAT · 상계) 보존 방식 정본 없음 — 라인별 세전 기초금액 + 구성요소",
                      STEP, c.holder_id, "V2 L305", "Q-21")
    load = sum((r["carryover_amount"] for r in rows if r["action"] == "NEW"), D(0))
    ctx.emit(STEP, "carry_load", load, c, **kw, formula="지급 이월 신규 적재액(PRE_TAX 기초금액)", ref="V2 L305",
             provisional=bool(load), note="Q-21" if load else "")
    o["payout_carry_rows"] = rows
    o["carry_load"] = load


def apply_results(ctx, c):
    """마감 후 대량이체 결과(있을 때만): 성공 → SETTLED, 실패 → RESERVED → NONE + 지급 실패 이월(V1 L589, D-13)."""
    for res in ctx.input["payout_results"]:
        for lid in res.get("ledger_ids") or []:
            r = next((x for x in ctx.input["carryover_ledger"] if x.get("ledger_id") == lid and x["contract_id"] == c.id), None)
            if not r:
                continue
            act = "SETTLE" if res["result"] == "SUCCESS" else "RELEASE"
            ctx.ledgers["carryover_ledger"].append(dict(r, action=act,
                                                        payout_reservation_status="SETTLED" if act == "SETTLE" else "NONE",
                                                        extinguished_yn=act == "SETTLE",
                                                        extinguished_month=ctx.month if act == "SETTLE" else None))
            ctx.emit(STEP, "payout_result", act, c, payee=res.get("payee_id"), ref_id=lid,
                     formula="이체 성공 → SETTLED(소멸) / 실패 → RESERVED → NONE 해제(차월 기초 세전 이월 잔액에 자동 복귀)",
                     ref="V1 L589 · L591")


def other_tax_no_threshold(ctx, g, clause):
    """기타소득 세액(상계한 달 확정분 — 판정 단위는 원 거래 한 건이라 과세최저한은 지급하는 달에 합쳐 판정):
    필요경비 = 내림(g × 의제율), 소득세 = 10원 미만 내림((g − 필요경비) × 20%), 지방소득세 = 10원 미만 내림(소득세 × 10%)."""
    rate, deemed_rate, _, _ = rates(ctx, None, "OTHER", clause)
    de = floor_won(g * deemed_rate)
    it = floor_ten((g - de) * rate)
    lt = floor_ten(it * D(str(ctx.p("local_income_tax_rate"))))
    return {"income_tax": it, "local_income_tax": lt, "deemed_expense": de}


def gross_for(ctx, net, taxf=None):
    """원천세를 뗀 뒤 금액이 net 이상이 되는 가장 작은 세전 금액(10원 미만 내림 순차 계산)."""
    taxf = taxf or (lambda g: withhold_business(ctx, g))
    lo, hi = D(net), D(net) * 2
    while lo < hi:
        mid = (lo + hi) // 2
        w = taxf(mid)
        if mid - w["income_tax"] - w["local_income_tax"] >= net:
            hi = mid
        else:
            lo = mid + 1
    return lo


def offset_carry(ctx, c, p, pid, ln):
    """상계한 달에 최종 정산금액이 최소 지급 미달로 이월될 때(V1 §7.3 · V2 §8.3 11단계, v4.0.56 · v4.0.59).
    상계한 금액은 그 달 지급으로 확정하고, 상계액이 세금 · 부가세를 정리한 뒤 금액이 되도록 그 달 확정분을 역산한다.
    → (이월 세전 금액, 이월 행에 덧붙일 칸)
    - 사업소득 대여금: 원천세를 떼면 상계액이 되는 세전 금액을 그 달 확정 · 원천징수, 나머지 세전 이월
    - 기타소득 대여금: 같은 역산(과세최저한은 이 달에 따로 보지 않음). 이월 행에 그 달 확정분 · 뗀 세액을 남겨
      지급하는 달에 원 거래 한 건으로 합쳐 판정하고 차액만 뗀다(9단계 '지난달 원 건의 정정분'과 같은 방식)
    - 원천징수 없는 부가세 별도(VAT_EXCLUDED): 상계액 = 공급가액 + 부가세가 되도록 공급가액 = 내림(상계액 × 100/110),
      나머지 공급가액 이월, 남은 부가세는 이월 행에 남겨 지급하는 달에 붙임(세금계산서는 그 달 전체로 발행)
    - 소득 선지급(EARNED): 상계액이 과세표준에서 이미 빠져 그 달 원천징수 없음"""
    kw = dict(payee=pid, line=ln["line_id"], line_key=ln["line_key"])
    off = ln["offset_amount"]
    extra = {}
    loan = bool(c.prepay and c.prepay.get("type") == "LOAN")
    applies = ln.get("withholding_rule") == "APPLY" and ln.get("tax_decision_status") == "DECIDED"
    other = ln.get("income_category") == "OTHER"
    if loan and applies:
        if other:
            taxf = lambda g: other_tax_no_threshold(ctx, g, ln.get("income_clause"))
        else:
            taxf = lambda g: withhold_business(ctx, g)
        g = gross_for(ctx, off, taxf)
        w = taxf(g)
        ln["taxable_base"], ln["income_tax"], ln["local_income_tax"] = g, w["income_tax"], w["local_income_tax"]
        ln["withholding_total"] = w["income_tax"] + w["local_income_tax"]
        carry = ln["split_amount"] - g
        if other:
            ln.update(deemed_expense=w["deemed_expense"], other_income_amount=g - w["deemed_expense"],
                      threshold_exempt_yn=False, small_amount_exempt_yn=False)
            extra = {"origin_unit_base": g, "origin_unit_income_tax": w["income_tax"],
                     "origin_unit_local_tax": w["local_income_tax"]}
        ctx.emit(STEP, "offset_paid_gross", g, c, **kw,
                 inputs={"상계액": off, "소득세": w["income_tax"], "지방소득세": w["local_income_tax"]},
                 formula="대여금 상계분 그 달 지급 확정 세전액 = 원천세를 떼면 상계액이 되는 세전 금액"
                         + ("(기타소득: 과세최저한은 지급하는 달에 원 거래 한 건으로 합쳐 판정)" if other else ""),
                 ref="V2 §8.3 11단계 (v4.0.56 · v4.0.59)")
    elif loan and not applies and (ln.get("vat_amount") or D(0)) > 0 and ln.get("vat_treatment") != "VAT_INCLUDED":
        supply = floor_won(off * 100 / D(110))
        vat_paid = off - supply
        carry = ln["split_amount"] - supply
        extra = {"components": {"carry_vat": ln["vat_amount"] - vat_paid}}
        ctx.emit(STEP, "offset_paid_gross", supply, c, **kw,
                 inputs={"상계액": off, "그 달 공급가액": supply, "그 달 부가세": vat_paid, "이월 부가세": ln["vat_amount"] - vat_paid},
                 formula="부가세 별도 라인 상계분 = 공급가액 내림(상계액 × 100/110) + 부가세(상계액 − 공급가액), 남은 공급가액 · 부가세 이월",
                 ref="V2 §8.3 11단계 (v4.0.59)")
    elif loan:
        carry = ln["pre_tax_payable"]
    else:
        ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = D(0)
        carry = ln["pre_tax_payable"]
    for f in ("taxable_base", "income_tax", "local_income_tax", "withholding_total"):
        ctx.emit("TAX", f, ln[f], c, **kw, formula="상계한 달 미달 이월 — 그 달 원천징수는 상계분만(11단계에서 다시 정함)",
                 ref="V2 §8.3 11단계 (v4.0.56)")
    from .s09_tax import totals
    totals(ctx, c, p)  # 받는 사람 세액 합계를 상계분 기준으로 다시 냄
    ctx.emit(STEP, "offset_month_carry_pre_tax", carry, c, **kw, inputs={"분할액": ln["split_amount"], "상계액": off},
             formula="상계 뒤 최종 정산금액이 최소 지급 미달 — 상계분은 그 달 지급 확정, 나머지는 세전 이월(원천세는 지급하는 달)",
             ref="V1 §7.3 · V2 §8.3 11단계 (v4.0.56)")
    return carry, extra
