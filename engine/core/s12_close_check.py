"""12 CLOSE_CHECK — 이월 연속성 등식 3종(V1 §7.4 L588~595, SPEC 15.1). 하나라도 불일치하면 마감 차단.

PRE_TAX : 전월 말 + 당월 신규 − 당월 소멸(RESERVED · 상계 확정) == 당월 말
POST_TAX: 전월 말 + 당월 신규 − 당월 소멸(RESERVED · 회수 · 상계 확정) == 당월 말
위탁 전용(계약별): 전월 말 + 당월 신규 − 상쇄 · 정정 변동(원잔액 부호) == 당월 말
당월 말은 원장 행을 실제로 갱신한 결과의 합계로 따로 계산해 등식과 대조한다.
"""

from collections import defaultdict

from .money import D

STEP = "CLOSE_CHECK"


def run(ctx):
    pending_adjustments(ctx)
    prev_given = {(r["account_type"], r["key"]): D(r["amount"]) for r in ctx.input["carryover_prev_end_balances"]}
    for c in ctx.contracts.values():
        state = {}  # ledger_id → 행(당월 말 상태)
        prev = defaultdict(lambda: D(0))
        for r in ctx.input["carryover_ledger"]:
            if r["contract_id"] != c.id or r.get("extinguished_yn") or (r.get("payout_reservation_status") or "NONE") != "NONE":
                continue
            acct = "CONSIGNMENT" if r.get("consignment_balance_yn") else r.get("account_type")
            key = c.id if acct == "CONSIGNMENT" else (r.get("payee_id") or r.get("rights_holder_id") or c.holder_id)
            prev[(acct, key)] += D(r["carryover_amount"])
            state[r["ledger_id"]] = (acct, key, D(r["carryover_amount"]))
        new = defaultdict(lambda: D(0))
        ext = defaultdict(lambda: D(0))
        rows_new = []
        for p in c.payees.values():
            for r in p.out["PAYOUT"].get("payout_carry_rows", []) + p.out["CLAIM"].get("claim_carry_rows", []):
                acct = r["account_type"]
                key = (acct, r["payee_id"])
                if r["action"] == "NEW":
                    new[key] += r["carryover_amount"]
                    rows_new.append((acct, r["payee_id"], r["carryover_amount"]))
                elif r["action"] == "RESERVE":
                    ext[key] += r["carryover_amount"]
                    state.pop(r.get("ledger_id"), None)
                ctx.ledgers["carryover_ledger"].append(r)
            for r in p.out["CLAIM"].get("consignment_balance_rows", []):
                new[("CONSIGNMENT", c.id)] += r["carryover_amount"]
                rows_new.append(("CONSIGNMENT", c.id, r["carryover_amount"]))
                ctx.ledgers["carryover_ledger"].append(r)
        if c.carry["cons_rows"]:  # 위탁 전용 잔액은 4단계에서 전액 상쇄 투입 — 원잔액 부호 그대로 변동 기록(D-8)
            ext[("CONSIGNMENT", c.id)] += c.carry["cons"]
            for r in c.carry["cons_rows"]:
                state.pop(r.get("ledger_id"), None)
                ctx.ledgers["carryover_ledger"].append(dict(r, action="REDUCE", extinguished_yn=True,
                                                            extinguished_month=ctx.month))
        end = defaultdict(lambda: D(0))
        for acct, key, amt in state.values():
            end[(acct, key)] += amt
        for acct, key, amt in rows_new:
            end[(acct, key)] += amt
        keys = set(prev) | set(new) | set(ext) | set(end)
        for acct, key in sorted(keys, key=lambda x: (str(x[0]), str(x[1]))):
            pe = prev_given.get((acct, key), prev[(acct, key)])
            n, x, e = new[(acct, key)], ext[(acct, key)], end[(acct, key)]
            ok = pe + n - x == e
            row = {"account_type": acct, "key": key, "prev_end": pe, "new": n, "extinguished": x, "end": e, "ok": ok}
            ctx.continuity.append(row)
            ctx.emit(STEP, f"continuity_{acct}", e, c, payee=None if acct == "CONSIGNMENT" else key, line=acct,
                     inputs={"전월 말": pe, "당월 신규": n, "당월 소멸 · 변동": x, "당월 말(원장 갱신 결과)": e, "ok": ok},
                     formula="전월 말 잔액 + 당월 신규 − 당월 소멸(위탁은 원잔액 부호 변동) = 당월 말 잔액",
                     code="prev_end + new − extinguished == end", ref="V1 §7.4 L588~595")
            ctx.emit(STEP, f"continuity_{acct}_ok", ok, c, payee=None if acct == "CONSIGNMENT" else key, line=acct,
                     formula="이월 연속성 등식 일치(불일치면 마감 차단)", ref="V1 §7.4 L588~595")
            if acct == "CONSIGNMENT":
                ctx.emit(STEP, "consignment_movement", x, c, line=acct,
                         formula="위탁 상쇄 · 정정 변동(제거되는 원잔액의 부호 그대로)", ref="V1 §7.4 · V4 D-8 L290")


def pending_adjustments(ctx):
    """마감 후 조정 라인(V2 §10.2 L362): 인입 단계가 정본에 없다(SPEC Q-23) — 기본 hold는 계산에 넣지 않고 출력만."""
    mode = ctx.input.get("adjustment_mode") or "hold"
    if not ctx.input["adjustments"]:
        return
    if mode != "hold":
        ctx.issue("CANON_GAP", "adjustment_mode = provisional은 구현하지 않음 — hold로 처리", STEP, None,
                  "V2 §10.1 L351 · §10.2 L362", "Q-23")
    th = ctx.p("manual_adj_approval_threshold")
    for a in ctx.input["adjustments"]:
        row = dict(a, requires_second_approval=th is not None and abs(D(a["adj_amount"])) > D(th))
        ctx.pending_adjustments.append(row)
        ctx.trace.add(STEP, "pending_adjustment", D(a["adj_amount"]), holder=None, contract=a.get("contract_id"),
                      payee=a.get("payee_id"), ref_id=a.get("adj_id"),
                      inputs={"origin_month": a.get("origin_month"), "account_type": a.get("account_type"),
                              "adj_reason_code": a.get("adj_reason_code")},
                      formula="마감 후 조정 라인 — 1~11단계 인입 위치 정본 없음, 계산 제외 · 출력만(hold)",
                      ref="V2 §10.2 L362 · SPEC 15.8", provisional=True, note="Q-23", output=False)
