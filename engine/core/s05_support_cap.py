"""5단계 SUPPORT_CAP — 지원금 한도 · 순누계(V2 §8.3 표 L172 · 본문 L204~214, V1 §5.2, SPEC 8절).

CAPPED: 복원 후 한도 = 총한도 − 소진액 + 복원액, 신규 확정액 = min(신규 발생액, 복원 후 한도),
        지급 대상 확정액 = 신규 확정액 − 4단계 P5.1 공제액. 누계는 전월 말 원장(prev)에 당월분만 반영.
UNLIMITED: 확정액 = 신규 발생액 − 공제액(한도 판정 · 소진액 · COMPLETED 전이 생략).
절사 없음.
"""

from .money import D
from .pipeline import month_of, period_end

STEP = "SUPPORT_CAP"


def run(ctx):
    prev_rows = {r["agreement_id"]: r for r in ctx.input["support_fund_ledger_prev"]}
    agrs = {a["agreement_id"]: a for a in ctx.input["support_fund_agreements"]}
    for c in ctx.contracts.values():
        rows = []
        lines = c.lines_of("5.1")
        c.step_out(STEP)
        ctx.emit(STEP, "applicable", bool(lines), c, inputs={"P5.1 agreements": len(lines)},
                 formula="매출연동 개발지원금(Pipeline 5.1) 약정이 있는 계약만 5단계 적용", ref="V2 §8.3 5단계 L204")
        for ln in lines:
            agr = agrs[ln.agreement_id]
            prev = prev_rows.get(ln.agreement_id) or {}
            rows.append(one_agreement(ctx, c, ln, agr, prev))
        c.out[STEP] = rows


def one_agreement(ctx, c, ln, agr, prev):
    aid = agr["agreement_id"]
    kw = dict(line=ln.label, agreement=aid)
    new = ln.new
    deduct = ln.support_deduct
    status0 = agr.get("status")
    cap_type = agr.get("cap_type") or "CAPPED"
    if not prev:
        ctx.issue("INPUT_MISSING", f"지원금 {aid} 전월 말 원장(support_fund_ledger_prev) 없음 — 누계 0에서 시작",
                  STEP, c.holder_id, "V2 §10.1 L356")
    p_consumed = D(prev.get("cap_consumed_amount"))
    p_net = D(prev.get("confirmed_net_total"))
    p_cash = prev.get("cash_paid_total")
    lump_settle = sum(D(r["amount"]) for r in c.lumpsum_rows
                      if r.get("item_kind") == "LUMP_SETTLE" and r.get("agreement_id") == aid)
    row = {"agreement_id": aid, "cap_type": cap_type, "accrued_amount": new, "status_before": status0}
    if cap_type == "UNLIMITED":
        confirmed = ctx.emit(STEP, "confirmed_amount", new - deduct, c, **kw,
                             inputs={"신규 발생액": new, "4단계 P5.1 공제액": deduct},
                             formula="UNLIMITED: 지급 대상 확정액 = 신규 발생액 − 4단계 P5.1 공제액(한도 판정 생략)",
                             code="confirmed_amount = new_5_1 − deduct", ref="V2 §8.3 5단계 L205 · SPEC 8.2")
        net_total = ctx.emit(STEP, "confirmed_net_total", p_net + new - deduct, c, **kw,
                             inputs={"전월 순누계": p_net, "신규": new, "공제": deduct},
                             formula="확정액 순누계 = 전월 순누계 + 당월 신규 확정 − 공제", ref="V2 L213 · SPEC 8.2")
        row.update(restore_amount=D(0), avail_cap=None, new_confirmed=new, expired_excess=D(0),
                   confirmed_amount=confirmed, confirmed_net_total=net_total, cap_consumed_amount=None,
                   remaining_cap=None, lump_settle_applied=lump_settle, status_after=status0)
    else:
        total_cap = D(agr.get("total_cap_amount"))
        restore = D(0)
        if agr.get("cap_restore_on_refund"):
            restore = sum(min(t["deduct_5_1"], t["unrefunded"]) for t in getattr(ln, "support_txs", []))
        restore = ctx.emit(STEP, "restore_amount", restore, c, **kw,
                           inputs={"cap_restore_on_refund": agr.get("cap_restore_on_refund"),
                                   "원거래별 공제액": [t["deduct_5_1"] for t in getattr(ln, "support_txs", [])]},
                           formula="승인된 한도 복원액 = Σ min(원거래 공제액, 원거래 미환불 확정액)(cap_restore_on_refund일 때)",
                           code="restore = Σ_tx min(tx.deduct_5_1, tx.unrefunded) if cap_restore_on_refund else 0",
                           ref="V2 §8.3 5단계 1) L207~208", provisional=True, note="Q-24(자동 복원)")
        avail = ctx.emit(STEP, "avail_cap", total_cap - p_consumed + restore, c, **kw,
                         inputs={"총한도": total_cap, "전월 소진액": p_consumed, "복원액": restore},
                         formula="복원 후 한도 = 총한도 − 소진액 + 복원액(cash_paid_total 사용 금지)",
                         code="avail_cap = total_cap_amount − prev.cap_consumed_amount + restore",
                         ref="V2 §8.3 표 5단계 L172 · 본문 2) L208")
        active = status0 == "ACTIVE"
        new_conf = ctx.emit(STEP, "new_confirmed", min(new, avail) if active else D(0), c, **kw,
                            inputs={"신규 발생액": new, "복원 후 한도": avail, "status": status0},
                            formula="신규 확정액 = min(신규 발생액, 복원 후 한도)(순수 신규에 한도 먼저)",
                            code="new_confirmed = min(new_5_1, avail_cap) if status == ACTIVE else 0",
                            ref="V2 §8.3 표 5단계 L172 · 본문 3) L209", provisional=not active,
                            note="" if active else "Q-25(월초 상태)")
        excess = ctx.emit(STEP, "expired_excess", new - new_conf, c, **kw,
                          inputs={"신규 발생액": new, "신규 확정액": new_conf},
                          formula="한도 초과분은 이월 없이 소멸", code="expired_excess = new_5_1 − new_confirmed",
                          ref="V4 Case 9 L232 · V2 L209")
        confirmed = ctx.emit(STEP, "confirmed_amount", new_conf - deduct, c, **kw,
                             inputs={"신규 확정액": new_conf, "4단계 P5.1 공제액": deduct},
                             formula="지급 대상 확정액 = 신규 확정액 − 4단계 P5.1 공제액",
                             code="confirmed_amount = new_confirmed − deduct", ref="V2 §8.3 표 5단계 L172 · 4) L210",
                             provisional=new_conf - deduct < 0, note="Q-11" if new_conf - deduct < 0 else "")
        consumed = ctx.emit(STEP, "cap_consumed_amount", p_consumed + new_conf - restore + lump_settle, c, **kw,
                            inputs={"전월 소진액": p_consumed, "신규 확정액": new_conf, "복원액": restore,
                                    "LUMP_SETTLE 승인액": lump_settle},
                            formula="소진액 = 전월 소진액 + 신규 확정액 − 복원액 + 종료 승인액(LUMP_SETTLE)",
                            code="cap_consumed = prev + new_confirmed − restore + lump_settle_applied",
                            ref="V2 §8.3 5단계 5) L211")
        net_total = ctx.emit(STEP, "confirmed_net_total", p_net + new_conf - deduct, c, **kw,
                             inputs={"전월 순누계": p_net, "신규 확정액": new_conf, "공제": deduct},
                             formula="확정액 순누계 = 전월 순누계 + 신규 확정액 − 공제액(복원 옵션과 무관)",
                             code="confirmed_net_total = prev + new_confirmed − deduct", ref="V2 §8.3 5단계 5) L211")
        remaining = ctx.emit(STEP, "remaining_cap", total_cap - consumed, c, **kw,
                             inputs={"총한도": total_cap, "소진액": consumed},
                             formula="잔여 한도 = 총한도 − 소진액", code="remaining_cap = total_cap_amount − cap_consumed",
                             ref="V1 §15.4 · V3 L65~67")
        status1 = status0
        end = period_end(agr, c.row)
        if remaining <= 0 and status0 == "ACTIVE":
            status1 = "COMPLETED"
        elif status0 == "COMPLETED" and remaining > 0 and (not end or ctx.month <= month_of(end)):
            status1 = "ACTIVE"
        ctx.emit(STEP, "status_after", status1, c, **kw, inputs={"status_before": status0, "remaining_cap": remaining},
                 formula="잔여 한도 0 → COMPLETED(차월 신규 중단) / COMPLETED이고 복원으로 잔여 > 0이며 종료월 이내 → ACTIVE",
                 ref="V2 §8.3 5단계 L211~212")
        if status0 in ("EXPIRED", "TERMINATED"):
            status1 = status0
        row.update(restore_amount=restore, avail_cap=avail, new_confirmed=new_conf, expired_excess=excess,
                   confirmed_amount=confirmed, confirmed_net_total=net_total, cap_consumed_amount=consumed,
                   remaining_cap=remaining, lump_settle_applied=lump_settle, status_after=status1)
    ctx.emit(STEP, "deduct_absorbed_by_expiry", (row["new_confirmed"] - row["confirmed_amount"]) != deduct, c, **kw,
             inputs={"신규 확정액": row["new_confirmed"], "확정액": row["confirmed_amount"], "공제": deduct},
             formula="공제액이 한도 초과 소멸분에 흡수되지 않고 별도 차감되었는가(C-01 한도 캡 흡수 방지)",
             ref="V2 L160 · §15.1")
    row["cash_paid_total"] = p_cash
    own = ctx.own_holder.get(aid)
    if own:
        row["own_distributable"] = own["distributable"]
        row["own_remaining"] = ctx.emit(STEP, "own_remaining", own["distributable"] - row["confirmed_amount"], c, **kw,
                                        inputs={"자사 배분가능액": own["distributable"], "지원금 확정액": row["confirmed_amount"]},
                                        formula="자사 최종 잔여액 = 자사 배분가능액 − 지원금 확정액 합계",
                                        code="own_remaining = own_distributable − confirmed_amount", ref="V1 L262~264")
        if row["confirmed_amount"] > own["distributable"]:
            ctx.warn("SUPPORT_OVER_OWN", f"{aid} 지원금 확정액이 자사 배분가능액을 넘음", "V1 L264")
    ln.net = row["confirmed_amount"]
    ln.new_confirmed = row["new_confirmed"]
    c.support[aid] = row
    ctx.ledgers["support_fund_ledger"].append({
        "agreement_id": aid, "target_month": ctx.month, "accrued_amount": new, "confirmed_amount": row["confirmed_amount"],
        "confirmed_net_total": row["confirmed_net_total"], "cap_consumed_amount": row["cap_consumed_amount"],
        "cash_paid_total": p_cash, "remaining_cap": row["remaining_cap"],
        "status_change": None if row["status_after"] == status0 else f"{status0}->{row['status_after']}",
        "settlement_line_id": None})
    return row
