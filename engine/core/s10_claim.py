"""10단계 CLAIM — 반환 반영 · 청구 판정(V2 §8.3 표 L177 · 본문 L284~298, V1 §5.2 · §5.3 · §7.3, SPEC 13절).

1) 동일 계약 · 동일 수취인 + 반환 상계 동의가 연결된 전속계약금 반환만 1회 차감
2) 만료 · 해지 귀속월 · 미상계 선급금 잔액 > 0 · 승계 미이관 → 미상계 선급금 청구 전환(비상계 보호분과 교차 상계 금지)
청구 대상 음수 = min(0, 반환 반영 후 순액) − 동의 없는 반환 − 미상계 청구 전환액,
청구 발행 = 음수 AND (|음수| > |min_claim_limit| OR 강제 청구 트리거).
지급 판정 전달액 = max(0, 반환 반영 후 순액) + 원귀속 PRE_TAX 세후 환산액.
"""

from datetime import date

from .money import D, floor_won

STEP = "CLAIM"


def days(a, b):
    return (date.fromisoformat(str(b)[:10]) - date.fromisoformat(str(a)[:10])).days


def clawback_amount(ctx, c, cb, kw):
    if cb.get("clawback_amount") is not None:
        return ctx.emit(STEP, "clawback_amount", D(cb["clawback_amount"]), c, **kw, inputs={"입력": "clawback_amount"},
                        formula="확정 반환액(세후, 입력값)", ref="V1 §5.2 L247~249")
    total = days(cb["obligation_start_date"], cb["obligation_end_date"]) + 1
    remain = days(cb["termination_date"], cb["obligation_end_date"])
    raw = D(cb["paid_signing_bonus_net"]) * remain / total
    return ctx.emit(STEP, "clawback_amount", floor_won(raw), c, **kw,
                    inputs={"세후 실지급액": cb["paid_signing_bonus_net"], "잔여 일수": remain, "총 의무 일수": total},
                    formula="일할 반환액 = 내림(세후 실지급액 × 잔여 일수 / 총 의무 일수)(해지일 당일은 복무 일수에 포함)",
                    code="clawback = floor(paid_net × remaining_days / total_days)", before=raw, rounding="FLOOR_WON",
                    ref="V1 §5.2 L248~249")


def run(ctx):
    for c in ctx.contracts.values():
        end = c.end_in_month(ctx.month)
        closed = bool(ctx.holder(c.holder_id).get("business_closed_yn"))
        limit = D(c.row.get("min_claim_limit") if c.row.get("min_claim_limit") is not None
                  else ctx.p("default_min_claim_limit"))
        for p in c.payees.values():
            claim_payee(ctx, c, p, end, closed, limit)


def claim_payee(ctx, c, p, end, closed, limit):
    pid = p.payee_id
    kw = dict(payee=pid)
    t = p.out["TAX"]
    o = p.out["CLAIM"]
    net = t.get("net_settle_amount") or D(0)
    cons = t.get("consignment_settle_amount") or D(0)
    cons_rows = []
    if cons < 0:  # 위탁 라인 음수: 청구 판정 대상 아님 → 위탁 전용 잔액(L298)
        net -= cons
        cons_rows.append({"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid,
                          "contract_id": c.id, "origin_month": ctx.month, "account_type": None, "pipeline_id": "2.2",
                          "consignment_balance_yn": True, "carryover_reason": "위탁 반품 초과",
                          "carryover_amount": cons, "payout_reservation_status": "NONE", "extinguished_yn": False})
        ctx.emit(STEP, "consignment_balance_new", cons, c, **kw,
                 formula="위탁 라인 음수 — 청구 판정 대상 아님, 미지급분은 위탁 전용 잔액(과세표준 · 세전 계정 적재 금지)",
                 ref="V2 §8.3 10단계 L298 · V1 §7.4", provisional=True, note="미지급/기지급 구분 입력 없음 — 전액 미지급분으로 처리")
    cbs = [cb for cb in ctx.input["clawbacks"] if cb["contract_id"] == c.id and cb["payee_id"] == pid]
    cb_consent = D(0)
    cb_other = D(0)
    for cb in cbs:
        amt = clawback_amount(ctx, c, cb, dict(kw, ref_id=cb.get("clawback_id")))
        if cb.get("clawback_offset_consent_yn"):
            cb_consent += amt
        else:
            cb_other += amt
    o["clawback_amount"] = cb_consent + cb_other
    o["clawback_offset_consent_yn"] = bool(cb_consent)
    after = ctx.emit(STEP, "net_after_return", net - cb_consent, c, **kw,
                     inputs={"9단계 실정산액(위탁 음수 제외)": net, "동의 연결 전속계약금 반환": cb_consent},
                     formula="동일 계약 · 동일 수취인 + 반환 상계 동의가 연결된 경우만 1회 차감",
                     code="net_after_return = net_settle_amount − (clawback if consent else 0)", ref="V2 §8.3 10단계 1) L286")
    unoffset = D(0)
    pp = c.prepay
    if pp and pid == pp["payee"] and end and (c.prepay_balance_after or 0) > 0 and not c.row.get("successor_transfer_yn"):
        if pp["type"] == "LOAN":
            unoffset = c.prepay_balance_after
            f = "대여금(LOAN): 미상계 원금 전액 청구 전환"
        else:
            v = pp["rows"][0].get("earned_unoffset_post_tax_amount")
            if v is None:
                ctx.stop("INPUT_ERROR", "EARNED_UNOFFSET_MISSING",
                         f"{c.id} 소득 선지급 만료 · 해지 세후 미상계 상당액 입력 필요(산식 정본 없음)", "SPEC Q-18")
            unoffset = D(v)
            f = "소득 선지급(EARNED): 세후 미상계 상당액(입력값, 산식 정본 없음 — Q-18)"
        ctx.emit(STEP, "unoffset_prepay_claim", unoffset, c, **kw,
                 inputs={"6단계 후 미상계 잔액": c.prepay_balance_after, "만료 · 해지 귀속월": end},
                 formula=f + " — 비상계 보호 지급액과 자동 교차 상계 금지", ref="V2 §8.3 10단계 2) L287 · V1 L328",
                 provisional=pp["type"] == "EARNED", note="Q-18" if pp["type"] == "EARNED" else "")
    o["unoffset_prepay_claim"] = unoffset
    returns = sum((r["post_tax_amount"] for r in c.return_claims if r["payee_id"] == pid), D(0))
    returns += -sum((r["carryover_amount"] for r in c.carry["post_neg"] if r["payee_id"] == pid), D(0))
    if returns:
        ctx.issue("CANON_GAP", "기지급 소득 반환채권 · 전월 POST_TAX(−)의 10단계 차감 위치 정본 없음 — 청구 음수 항에 가산",
                  STEP, c.holder_id, "V2 L286~289", "Q-19")
    o["return_claims_applied"] = ctx.emit(STEP, "return_claims_applied", returns, c, **kw,
                                          formula="기지급 소득 반환채권 + 전월 세후 반환채권(청구 음수 항에 가산 — 잠정)",
                                          ref="V2 L295", provisional=bool(returns), note="Q-19" if returns else "")
    cnn = min(D(0), after) - cb_other - unoffset - returns
    o["net_after_return"] = after
    o["claim_negative_net"] = ctx.emit(
        STEP, "claim_negative_net", cnn, c, **kw,
        inputs={"min(0, 반환 반영 후 순액)": min(D(0), after), "동의 없는 반환": cb_other, "미상계 청구 전환액": unoffset,
                "반환채권": returns},
        formula="청구 대상 음수 = min(0, 반환 반영 후 순액) − 상계 동의 없는 반환 − 미상계 선급금 청구 전환액",
        code="claim_negative_net = min(0, net_after_return) − clawback_no_consent − unoffset_claim − returns",
        ref="V2 §8.3 10단계 L288")
    force = end or closed
    o["force_claim"] = ctx.emit(STEP, "force_claim", bool(force), c, **kw,
                                inputs={"만료 · 해지 귀속월": end, "폐업": closed},
                                formula="강제 청구 트리거 = 계약 만료 · 해지 귀속월 또는 폐업 확인", ref="V2 L292 · V1 L568")
    issued = cnn < 0 and (abs(cnn) > abs(limit) or force)
    o["claim_issued_yn"] = ctx.emit(STEP, "claim_issued_yn", issued, c, **kw,
                                    inputs={"청구 대상 음수": cnn, "min_claim_limit": limit, "강제": force},
                                    formula="음수 < 0 AND (|음수| > |min_claim_limit| OR 강제 청구 트리거)",
                                    code="claim_issued = cnn < 0 and (abs(cnn) > abs(limit) or force)",
                                    ref="V2 §8.3 표 10단계 L177 · L292 · V1 L570")
    if cnn < 0:
        ctx.emit(STEP, "abs_le_min_claim_limit", abs(cnn) <= abs(limit), c, **kw,
                 inputs={"청구 대상 음수": cnn, "min_claim_limit": limit},
                 formula="|음수| ≤ |min_claim_limit|(같으면 이월)", ref="V1 §7.3 L570 · SPEC 15.2")
    o["claim_amount"] = ctx.emit(STEP, "claim_amount", -cnn if issued else D(0), c, **kw,
                                 formula="청구 · 반환채권 확정액", ref="V2 L292")
    o["claim_evaluated"] = ctx.emit(STEP, "claim_evaluated", cnn < 0, c, **kw,
                                    formula="청구 판정 대상(청구 대상 음수 < 0)", ref="V2 §8.3 10단계")
    carry = []
    if cnn < 0 and not issued:
        neg_new = min(D(0), after)
        lines = [ln for ln in p.lines if ln["origin"] == "NEW"]
        key_ln = min(lines, key=lambda x: x["pre_tax_payable"]) if lines else None
        if neg_new < 0:
            carry.append(carry_row(ctx, c, pid, "PRE_TAX", neg_new, key_ln, "청구 이월(원거래 지급 · 세무 경로 미확정)"))
        post = cnn - neg_new
        if post < 0:
            carry.append(carry_row(ctx, c, pid, "POST_TAX", post, key_ln, "청구 이월(기지급 반환채권 · 전속계약금 반환)"))
        for r in carry:
            ctx.emit(STEP, "claim_carry", r["carryover_amount"], c, **kw, line=str(r["pipeline_id"]),
                     inputs={"account_type": r["account_type"]},
                     formula="정상 유지 계약의 소액 음수: 청구서 미발행, 이월 원장에 청구 이월(계정은 세무 상태로)",
                     ref="V2 L294~295 · V1 L572")
        r0 = carry[0]
        ctx.emit(STEP, "claim_carry_type", "청구 이월", c, **kw, formula="이월 사유", ref="V1 L572")
        ctx.emit(STEP, "claim_carry_account_type", r0["account_type"], c, **kw, formula="이월 계정(세무 상태)", ref="V2 L295")
        ctx.emit(STEP, "claim_carry_pipeline_id", r0["pipeline_id"], c, **kw, formula="이월 행 정산 입력 구분", ref="V1 §7.4")
        ctx.emit(STEP, "claim_carry_income_category", r0["income_category"], c, **kw, formula="이월 행 소득 구분",
                 ref="V1 §7.4")
    o["claim_carry_rows"] = carry
    o["consignment_balance_rows"] = cons_rows
    o["december_review_flag"] = bool(carry) and ctx.month.endswith("-12")
    ch = [x for ln in p.lines for x in (ln.get("correction_channels") or [])]
    if issued and ch:
        ctx.emit(STEP, "correction_channel", ch[0], c, **kw, formula="반환 · 정정 채널(matrix_case_id → 10.4 채널)",
                 ref="V2 L290 · §10.4")
    payable = max(D(0), after) + (t.get("carry_pre_tax_after_tax_total") or D(0))
    o["payable_net_for_payout"] = ctx.emit(
        STEP, "payable_net_for_payout", payable, c, **kw,
        inputs={"max(0, 반환 반영 후 순액)": max(D(0), after), "원귀속 PRE_TAX 세후 환산액": t.get("carry_pre_tax_after_tax_total")},
        formula="지급 판정 전달 당월 지급채무 순액 = max(0, 반환 반영 후 순액) + 원귀속 PRE_TAX 세후 환산액",
        code="payable_net_for_payout = max(0, net_after_return) + Σcarry_pre_tax_after_tax", ref="V2 §8.3 10단계 L289")
    o["protected_crossed_with_claim"] = ctx.emit(
        STEP, "protected_crossed_with_claim", payable < (t.get("net_settle_protected") or D(0)) and unoffset > 0, c, **kw,
        formula="미상계 선급금 청구 전환액이 비상계 보호 지급액과 교차 상계되었는가(되면 안 됨)", ref="V2 L287 · D-11")
    o["prepay_ledger_status_on_lock"] = "CLAIMED_ON_TERMINATION" if unoffset > 0 else None
    if unoffset > 0:
        ctx.emit(STEP, "prepay_ledger_status_on_lock", "CLAIMED_ON_TERMINATION", c, **kw,
                 formula="만료 · 해지 미상계 잔액 → 청구 전환, 마감 시 CLAIMED_ON_TERMINATION 0원 종결", ref="V1 L328")
        ctx.emit(STEP, "prepay_ledger_balance_after", D(0), c, **kw, formula="청구 전환 후 선급금 원장 잔액(마감 시)",
                 ref="V1 L328")
    if pp and pid == pp["payee"]:
        ctx.ledgers["prepayment_ledger"].append({
            "contract_id": c.id, "offset_amount": pp.get("amount", D(0)),
            "balance_after": D(0) if unoffset > 0 else c.prepay_balance_after,
            "status": "CLAIMED_ON_TERMINATION" if unoffset > 0 else None})


def carry_row(ctx, c, pid, account, amount, ln, reason):
    key = (ln or {}).get("line_key") or {}
    return {"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid, "contract_id": c.id,
            "origin_month": ctx.month, "account_type": account, "pipeline_id": key.get("pipeline_id") or "MIXED",
            "consignment_balance_yn": False, "income_category": key.get("income_category"),
            "income_clause": key.get("income_clause"), "tax_threshold_unit_key": key.get("tax_threshold_unit_key"),
            "carryover_reason": reason, "carryover_amount": amount, "first_occurred_month": ctx.month,
            "first_payable_confirmed_month": None, "payout_reservation_status": "NONE", "extinguished_yn": False}
