"""10단계 CLAIM — 반환 반영 · 청구 판정(V2 §8.3 표 L177 · 본문 L284~298, V1 §5.2 · §5.3 · §7.3, SPEC 13절).

1) 동일 계약 · 동일 수취인 + 반환 상계 동의가 연결된 전속계약금 반환만 1회 차감
2) 만료 · 해지 귀속월 · 미상계 선급금 잔액 > 0 → 미상계 선급금 청구 전환(비상계 보호분과 교차 상계 금지)
청구 대상 음수 = min(0, 반환 반영 후 순액) − 동의 없는 반환 − 미상계 청구 전환액,
청구 발행 = 음수 AND (|음수| > |min_claim_limit| OR 강제 청구 트리거).
지급 판정 전달액 = max(0, 반환 반영 후 순액) + 원귀속 PRE_TAX 세후 환산액.
"""
from collections import OrderedDict

from datetime import date

from . import adjust
from .money import D, floor_won, alloc_last_remainder

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
    sts = []
    for c in ctx.contracts.values():
        end = c.closing_due(ctx.month)  # 끝난 달 + 지급 시차 N 이후(v4.0.51)
        closed = bool(ctx.holder(c.holder_id).get("business_closed_yn"))
        limit = D(c.row.get("min_claim_limit") if c.row.get("min_claim_limit") is not None
                  else ctx.p("default_min_claim_limit"))
        for p in c.payees.values():
            sts.append((c, p, end, closed, limit, claim_payee(ctx, c, p, end, closed, limit)))
    payee_netting(ctx, sts)
    # 청구 기준 판정은 받는 사람(원 권리자 · 받는 사람)의 계약별 청구 음수 합으로(V2 §8.3 10단계, v4.0.53)
    # 계약이 둘 이상이면 판정 기준액은 그 달 유효한 계약 가운데 늦게 시작한 계약의 값(v4.0.53)
    gsum, glim = {}, {}
    for c, p, end, closed, limit, st in sts:
        k = (c.holder_id, st["pid"])
        # 청구 이월 행(지난달까지 청구 하한 미달로 넘긴 PRE_TAX −)은 그 달 새 음수가 있을 때만 청구 판정 합에 함께 넣음
        # (새 양수 지급 금액과는 합치지 않음, V2 §8.3 10단계, v4.0.62)
        st["claim_carry_in"] = [r for r in c.carry["pre_neg"] if r["payee_id"] == st["pid"] and not r.get("carry_line_origin")] \
            if st["cnn"] < 0 else []
        st["cnn_carry"] = sum((r["carryover_amount"] for r in st["claim_carry_in"]), D(0))
        gsum[k] = gsum.get(k, D(0)) + min(D(0), st["cnn"]) + st["cnn_carry"]
        s = str(c.row.get("start_date") or "")[:10]
        if s[:7] <= ctx.month and (k not in glim or s > glim[k][0]):
            glim[k] = (s, limit)
    for c, p, end, closed, limit, st in sts:
        k = (c.holder_id, st["pid"])
        claim_decide(ctx, c, p, end, closed, glim.get(k, (None, limit))[1], st, gsum[k])


def payee_netting(ctx, sts):
    """받는 사람 단위 순액(V2 §8.3 10단계, v4.0.55): 같은 원 권리자 · 받는 사람의 그 달 새 금액(계약별 반환 반영 후 순액)끼리만
    합산한다. 반환채권 · 선급금 청구 전환액 · 이월 잔액(지급 · 청구)은 넣지 않는다. 합이 0 이상이면 음수 계약을 0으로 지우고
    양수 계약의 지급액을 양수 비율로 줄이며, 합이 0 미만이면 양수 계약을 0으로 지우고 음수 계약의 음수를 음수 비율로 줄인다."""
    groups = OrderedDict()
    for row in sts:
        c, st = row[0], row[5]
        groups.setdefault((c.holder_id, st["pid"]), []).append(row)
    for (hid, pid), rows in groups.items():
        pos = [r for r in rows if r[5]["after"] > 0]
        neg = [r for r in rows if r[5]["after"] < 0]
        if not pos or not neg:
            continue
        total = sum((r[5]["after"] for r in rows), D(0))
        if total >= 0:
            shares = alloc_last_remainder(total, [r[5]["after"] for r in pos])
            new = {id(r): s for r, s in zip(pos, shares)}
            new.update({id(r): D(0) for r in neg})
        else:
            shares = alloc_last_remainder(total, [r[5]["after"] for r in neg])
            new = {id(r): s for r, s in zip(neg, shares)}
            new.update({id(r): D(0) for r in pos})
        for r in rows:
            c, st = r[0], r[5]
            old = st["after"]
            nv = new.get(id(r), old)
            st["cnn"] = st["cnn"] - min(D(0), old) + min(D(0), nv)
            st["after"] = nv
            ctx.emit(STEP, "payee_netting_after", nv, c, **st["kw"],
                     inputs={"이 계약 그 달 새 금액(반환 반영 후 순액)": old, "받는 사람 순액 합": total,
                             "계약": sorted({x[0].id for x in rows})},
                     formula="받는 사람 순액: 그 달 새 금액끼리만 계약을 넘어 합산(반환채권 · 선급금 청구 전환 · 이월 제외) — 합 ≥ 0이면 음수 계약 0 · 양수 계약에 합 배분, 합 < 0이면 양수 계약 0 · 음수 계약에 합 배분",
                     ref="V2 §8.3 10단계 · 9.1절 정산서 (v4.0.55)")


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
    post = [a for a in adjust.month_adjustments(ctx) if adjust.mode(ctx) == "apply" and a.get("contract_id") == c.id
            and (a.get("payee_id") or c.holder_id) == pid and adjust.account(a) == "POST_TAX"]
    post_pos = sum((D(a["adj_amount"]) for a in post if D(a["adj_amount"]) > 0), D(0))
    post_neg = -sum((D(a["adj_amount"]) for a in post if D(a["adj_amount"]) < 0), D(0))
    for a in post:
        ctx.emit(STEP, "post_tax_adjustment", D(a["adj_amount"]), c, **kw, line=f"ADJ:{a.get('adj_id')}",
                 ref_id=a.get("adj_id"), inputs={"origin_month": a.get("origin_month"), "adj_reason_code": a.get("adj_reason_code")},
                 formula="전월 정산 조정(세후) — 양수는 당월 지급채무에 가산, 음수는 세후 반환채권(청구 음수 항, 자동 상계 없음)",
                 ref="V2 §10.1 L353 · §10.2 · 2026-10-27 white 결정(SPEC Q-23 해소) · Q-19")
    after = ctx.emit(STEP, "net_after_return", net - cb_consent + post_pos, c, **kw,
                     inputs={"9단계 실정산액(위탁 음수 제외)": net, "동의 연결 전속계약금 반환": cb_consent,
                             "세후 조정(+)": post_pos},
                     formula="동일 계약 · 동일 수취인 + 반환 상계 동의가 연결된 경우만 1회 차감, 세후 전월 정산 조정(+) 가산",
                     code="net_after_return = net_settle_amount − (clawback if consent else 0) + post_tax_adj(+)",
                     ref="V2 §8.3 10단계 1) L286 · §10.2")
    unoffset = D(0)
    pp = c.prepay
    # 보류 · 운영자 이월 지정으로 상계를 미룬 달은 청구 전환도 풀린 달로 미룸(상계 후 남은 잔액만 청구, V1 §5.3 · V2 §8.3 10단계, v4.0.46)
    hd = ctx.holder(pid)
    held = bool(hd.get("payout_hold_yn") or hd.get("carry_designated_yn"))
    deferred_in = bool(pp) and any(r.get("claim_conversion_deferred_yn") for r in pp["rows"])
    due = end or deferred_in
    if pp and pid == pp["payee"] and due and held and (c.prepay_balance_after or 0) > 0:
        ctx.emit(STEP, "unoffset_prepay_claim_deferred", c.prepay_balance_after, c, **kw,
                 inputs={"6단계 후 미상계 잔액": c.prepay_balance_after, "보류 · 이월 지정": True},
                 formula="보류 · 운영자 이월 지정 수취인은 청구 전환을 풀린 달로 미룸(claim_conversion_deferred_yn), 그 달 상계 후 잔액만 청구",
                 ref="V1 §5.3 · V2 §8.3 10단계 2) (v4.0.46)")
    if pp and pid == pp["payee"] and due and not held and (c.prepay_balance_after or 0) > 0:
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
    returns += post_neg  # 세후 전월 정산 조정(−)
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
    return dict(o=o, cnn=cnn, kw=kw, pid=pid, after=after, t=t, unoffset=unoffset, pp=pp, cons_rows=cons_rows)


def claim_decide(ctx, c, p, end, closed, limit, st, gsum):
    o, cnn, kw, pid, after, t, unoffset, pp, cons_rows = (
        st[k] for k in ("o", "cnn", "kw", "pid", "after", "t", "unoffset", "pp", "cons_rows"))
    force = end or closed
    o["force_claim"] = ctx.emit(STEP, "force_claim", bool(force), c, **kw,
                                inputs={"끝난 달 + 지급 시차 이후": end, "폐업": closed},
                                formula="강제 청구 트리거 = 대상월 ≥ 끝난 달 + 지급 시차 N(종료 뒤 환불 포함) 또는 폐업 확인", ref="V2 L292 · V1 L568 · v4.0.51")
    issued = cnn < 0 and (abs(gsum) > abs(limit) or force)
    cin, ccarry = st.get("claim_carry_in") or [], st.get("cnn_carry") or D(0)
    if cin:
        ctx.emit(STEP, "claim_carry_merged", ccarry, c, **kw,
                 inputs={"그 달 새 청구 대상 음수": cnn, "청구 이월 행": [r.get("ledger_id") for r in cin]},
                 formula="그 달 새 음수가 있으면 청구 이월 행을 청구 판정 합에 함께 넣음 — 청구하면 함께 청구 · 이월 행 소멸, 기준 이내면 이월 행 유지",
                 ref="V2 §8.3 10단계 (v4.0.62)")
    o["claim_issued_yn"] = ctx.emit(STEP, "claim_issued_yn", issued, c, **kw,
                                    inputs={"청구 대상 음수": cnn, "받는 사람 청구 음수 합": gsum, "min_claim_limit": limit, "강제": force},
                                    formula="음수 < 0 AND (|받는 사람의 계약별 청구 음수 합| > |min_claim_limit| OR 이 계약의 강제 청구 트리거)",
                                    code="claim_issued = cnn < 0 and (abs(payee_claim_negative_sum) > abs(limit) or force)",
                                    ref="V2 §8.3 표 10단계 L177 · L292 · V1 L570 · v4.0.53")
    if cnn < 0:
        ctx.emit(STEP, "payee_claim_negative_sum", gsum, c, **kw,
                 formula="받는 사람(원 권리자 · 받는 사람)의 그 달 계약별 청구 대상 음수 합", ref="V2 §8.3 10단계 (v4.0.53)")
        ctx.emit(STEP, "abs_le_min_claim_limit", abs(gsum) <= abs(limit), c, **kw,
                 inputs={"받는 사람 청구 음수 합": gsum, "min_claim_limit": limit},
                 formula="|음수| ≤ |min_claim_limit|(같으면 이월)", ref="V1 §7.3 L570 · SPEC 15.2")
    o["claim_carry_settled"] = [r.get("ledger_id") for r in cin] if issued else []
    o["claim_amount"] = ctx.emit(STEP, "claim_amount", -(cnn + ccarry) if issued else D(0), c, **kw,
                                 formula="청구 · 반환채권 확정액", ref="V2 L292")
    o["claim_evaluated"] = ctx.emit(STEP, "claim_evaluated", cnn < 0, c, **kw,
                                    formula="청구 판정 대상(청구 대상 음수 < 0)", ref="V2 §8.3 10단계")
    carry = []
    if cnn < 0 and not issued:
        neg_new = min(D(0), after)
        lines = [ln for ln in p.lines if ln["origin"] in ("NEW", "ADJUSTMENT")]
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
