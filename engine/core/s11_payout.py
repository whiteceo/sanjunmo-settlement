"""11단계 PAYOUT — 최소 지급 검증(V2 §8.3 표 L178 · 본문 L299~308, V1 §7.3 · §7.4, SPEC 14절).

판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액,
판정 금액 ≥ min_payout_limit 또는 강제 정산 트리거 → 지급 확정(기존 이월행 RESERVED 예정),
미달 → 당월 신규분 PRE_TAX 기초금액 이월(기존 POST_TAX · PRE_TAX 유지). 판정 기준 = VAT 포함 총액. 절사 없음.
"""

from .money import D
from .pipeline import months_between

STEP = "PAYOUT"


def run(ctx):
    for c in ctx.contracts.values():
        end = c.end_in_month(ctx.month)
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
    force = bool(reasons)
    evaluated = payable > 0 or bool(pre_pos) or bool(post_pos) or force
    judge = ctx.emit(STEP, "payout_judgement_amount", payable + post_total, c, **kw,
                     inputs={"당월 지급채무 순액": payable, "POST_TAX 지급대기액": post_total},
                     formula="판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액(VAT 포함 총액 기준)",
                     code="judgement = payable_net_for_payout + Σcarry_post_tax_pos", ref="V2 §8.3 11단계 L302 · L304")
    internal = bool(ctx.holder(pid).get("is_internal"))
    confirmed = evaluated and (judge >= limit or force)
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
        for r in pre_pos + post_pos:
            rows.append(dict(r, action="RESERVE", payout_reservation_status="RESERVED"))
    elif evaluated:
        for ln in p.lines:
            if ln["origin"] in ("NEW", "ADJUSTMENT") and ln["pre_tax_payable"] > 0:
                key = ln["line_key"]
                rows.append({"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid,
                             "contract_id": c.id, "origin_month": ctx.month, "account_type": "PRE_TAX",
                             "pipeline_id": key.get("pipeline_id"), "consignment_balance_yn": False,
                             "income_category": key.get("income_category"), "income_clause": key.get("income_clause"),
                             "tax_threshold_unit_key": key.get("tax_threshold_unit_key"),
                             "carryover_reason": "지급 하한 미달", "carryover_amount": ln["pre_tax_payable"],
                             "components": {"split_amount": ln["split_amount"], "offset_amount": ln["offset_amount"],
                                            "vat_amount": ln.get("vat_amount")},
                             "first_occurred_month": ctx.month, "first_payable_confirmed_month": None,
                             "payout_reservation_status": "NONE", "extinguished_yn": False})
        for r in pre_pos + post_pos:
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
