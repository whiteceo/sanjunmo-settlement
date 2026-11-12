"""11단계 PAYOUT — 최소 지급 검증(V2 §8.3 표 L178 · 본문 L299~308, V1 §7.3 · §7.4, SPEC 14절).

판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액,
판정 금액 ≥ min_payout_limit 또는 강제 정산 트리거 → 지급 확정(기존 이월행 RESERVED 예정),
미달 → 당월 신규분 PRE_TAX 기초금액 이월(기존 POST_TAX · PRE_TAX 유지). 판정 기준 = VAT 포함 총액. 절사 없음.
"""

from .money import D, floor_won, floor_ten
from .s10_claim import offsettable
from .tax import withhold_business, rates
from .pipeline import months_between

STEP = "PAYOUT"


def run(ctx):
    ctx.payout_groups = group_decisions(ctx)
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


def modified_invoice_notice(ctx, c, p, pid, pre_pos, kw):
    """이월 부가세가 붙은 이월 행의 원거래(같은 계약 · 원 결제월)가 미지급 환불로 줄면 부가세도 공급가액과 같은 비율로 줄이고,
    수정세금계산서는 사람이 발행하므로 정산서 · 정산 내역에 '수정세금계산서 발행 필요' 알림을 남긴다
    (V2 §8.3 11단계, 부가가치세법 제32조 제7항 · 시행령 제70조 제1항 제3호, v4.0.80)."""
    notes = []
    for r in pre_pos:
        dr = r.get("refund_direct_reduction") or {}
        if not dr or D(dr.get("carry_vat_before") or 0) <= 0:
            continue
        # 알림 금액은 환불 전체(이월 행에서 줄인 몫 + 넘어서 청구 · 반환채권으로 간 몫, v4.0.82)
        notes.append({"ledger_id": r.get("ledger_id"), "origin_month": r.get("origin_month"), "original_supply": dr["original_supply"],
                      "original_vat": dr["original_vat"], "reduced_supply": dr["supply"] + D(dr.get("excess_supply") or 0),
                      "reduced_vat": dr["vat"] + D(dr.get("excess_vat") or 0),
                      "carry_reduced_supply": dr["supply"], "carry_reduced_vat": dr["vat"],
                      "excess_supply": D(dr.get("excess_supply") or 0), "excess_vat": D(dr.get("excess_vat") or 0),
                      "carry_vat_after": D((r.get("components") or {}).get("carry_vat") or 0)})
    p.out["PAYOUT"]["modified_invoice_notices"] = notes
    if notes:
        ctx.emit(STEP, "modified_invoice_required", True, c, **kw, inputs={"알림": notes},
                 formula="이월 부가세 행의 원거래가 환불로 줄어 부가세도 같은 비율로 줄임 — 수정세금계산서는 사람이 발행, 정산서 · 정산 내역에 알림"
                         "(원거래 세금계산서 공급한 달 · 공급가액 · 부가세와 줄어든 공급가액 · 부가세)",
                 ref="V2 §8.3 11단계 · 부가가치세법 제32조 제7항 · 시행령 제70조 제1항 제3호 (v4.0.80)")


def withholding_refund_notice(ctx, c, p, pid, confirmed, kw):
    """이미 지급한 달의 정정(세전 −, 전월 정산 조정 · 그런 달에서 온 청구 이월)을 지급에서 세전으로 빼거나 청구로 확정한 달에는,
    원 귀속월 수정신고로 돌려받는 원천세를 권리자에게 돌려준다 — 그 금액을 알림으로 남김(V2 §10.4 채널 3-a · 8.3절 10단계, v4.0.86).
    예: 기지급 달 정정 −50,000(사업소득 3.3%) → 1,650."""
    realized = confirmed or bool(p.out["CLAIM"].get("claim_issued_yn"))
    if not realized:
        p.out["PAYOUT"]["withholding_refund_to_payee"] = D(0)
        return
    amt = D(0)
    for ln in p.lines:
        neg = (ln.get("pre_tax_payable") or D(0)) < 0
        if not neg or ln.get("tax_decision_status") == "PENDING_REVIEW":
            continue
        if ln["origin"] == "ADJUSTMENT" or (ln["origin"] == "CARRY_PRE_TAX" and ln.get("carry_line_origin") == "ADJUSTMENT"):
            amt += -ln["pre_tax_payable"]
    refund = D(0)
    if amt > 0:
        from .tax import classify
        h = ctx.holder(pid)
        cl = classify(ctx, pid, {"supply_nature": "LECTURE_RS", "pipeline_id": "1.1", "income_category": h.get("income_category"),
                                 "income_clause": h.get("income_clause")})
        if cl.get("withholding") == "APPLY":
            w = withhold_business(ctx, amt) if h.get("income_category") != "OTHER" else None
            if w:
                refund = w["income_tax"] + w["local_income_tax"]
    p.out["PAYOUT"]["withholding_refund_to_payee"] = refund
    if refund:
        ctx.emit(STEP, "withholding_refund_to_payee", refund, c, **kw, inputs={"세전으로 뺀 기지급 달 정정": amt},
                 formula="이미 지급한 달의 정정을 세전으로 뺀 달 — 원 귀속월 수정신고로 돌려받는 원천세를 권리자에게 돌려줌(환급 뒤 세후 정정(+)로 지급)",
                 ref="V2 §10.4 채널 3-a · §8.3 10단계 (v4.0.86)")


def limit_of(ctx, c):
    return D(c.row.get("min_payout_limit") if c.row.get("min_payout_limit") is not None else ctx.p("default_min_payout_limit"))


def group_decisions(ctx):
    """받는 사람 순액 묶음(10단계에서 음수를 지운 묶음)의 지급 판정: 묶음 합 ≥ 최소 지급액(그 달 유효한 계약 가운데 늦게 시작한
    계약의 값) 또는 묶음 안 강제 정산 트리거면 묶음 전체 지급, 아니면 묶음 전체 이월(음수 줄 포함, V2 §8.3 10 · 11단계, v4.0.76)."""
    groups = {}
    for c in ctx.contracts.values():
        for p in c.payees.values():
            k = p.out["CLAIM"].get("netting_group")
            if k:
                groups.setdefault(k, []).append((c, p))
    out = {}
    for k, mem in groups.items():
        total, force, lim = D(0), False, None
        for c, p in mem:
            pid = p.payee_id
            post_total = sum((r["carryover_amount"] for r in c.carry["post_pos"] if r["payee_id"] == pid), D(0))
            total += (p.out["CLAIM"].get("payable_net_for_payout") or D(0)) + post_total
            pre_pos = [r for r in c.carry["pre_pos"] if r["payee_id"] == pid]
            post_pos = [r for r in c.carry["post_pos"] if r["payee_id"] == pid]
            end = c.closing_due(ctx.month)
            closed = bool(ctx.holder(c.holder_id).get("business_closed_yn"))
            force = force or bool(force_reasons(ctx, c, p, end, closed, pre_pos, post_pos, quiet=True))
            s = str(c.row.get("start_date") or "")[:10]
            if s[:7] <= ctx.month and (lim is None or s > lim[0]):
                lim = (s, limit_of(ctx, c))
        limit = lim[1] if lim else limit_of(ctx, mem[0][0])
        hold = bool(ctx.holder(k[1]).get("payout_hold_yn")) or bool(ctx.holder(k[1]).get("carry_designated_yn"))
        neg = any(p.out["CLAIM"].get("netting_group_neg") for _, p in mem)
        settle = neg and any(p.out["CLAIM"].get("claim_issued_yn") for _, p in mem)
        out[k] = dict(total=total, limit=limit, force=force, hold=hold, contracts=sorted({c.id for c, _ in mem}),
                      confirmed=(not neg) and (total >= limit or force) and not hold, claim_settle=settle)
    return out


def force_reasons(ctx, c, p, end, closed, pre_pos, post_pos, quiet=False):
    reasons = []
    firsts = [r.get("first_payable_confirmed_month") for r in pre_pos + post_pos if r.get("first_payable_confirmed_month")]
    if firsts and months_between(str(min(firsts))[:7], ctx.month) >= int(ctx.p("carryover_max_months")):
        reasons.append("SIX_MONTHS")
        if not quiet:
            ctx.issue("CANON_GAP", "6개월 경과 산정 — 월 차이 ≥ 6으로 판정(잠정)", STEP, c.holder_id, "V1 L562", "Q-20")
    if int(ctx.month[5:7]) == int(ctx.p("carryover_force_settle_month")):
        reasons.append("DECEMBER")
    if end:
        reasons.append("CONTRACT_END")
    if closed:
        reasons.append("BUSINESS_CLOSED")
    if p.out["CLAIM"].get("netting_force") and not end and not closed:
        reasons.append("NETTED_WITH_ENDED")  # 끝난 계약과 순액을 낸 묶음 — 그달 함께 지급(v4.0.74)
    pid = p.payee_id
    if bool(ctx.holder(pid).get("payout_hold_yn")) or bool(ctx.holder(pid).get("carry_designated_yn")):
        reasons = []
    return reasons


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
    reasons = force_reasons(ctx, c, p, end, closed, pre_pos, post_pos)
    grp = (getattr(ctx, "payout_groups", None) or {}).get(p.out["CLAIM"].get("netting_group"))
    designated = bool(ctx.holder(pid).get("carry_designated_yn"))  # 운영자 이월 지정 후 재배치(v4.0.43)
    hold = bool(ctx.holder(pid).get("payout_hold_yn")) or designated
    # 지급 보류 · 운영자 이월 지정 수취인은 강제 정산 없이 세전 이월(v4.0.39 · v4.0.43) — force_reasons에서 비움
    force = bool(reasons)
    evaluated = payable > 0 or bool(pre_pos) or bool(post_pos) or force or bool(grp)
    judge = ctx.emit(STEP, "payout_judgement_amount", payable + post_total, c, **kw,
                     inputs={"당월 지급채무 순액": payable, "POST_TAX 지급대기액": post_total},
                     formula="판정 금액 = 당월 지급채무 순액(원귀속 PRE_TAX 세후액 포함) + POST_TAX 지급대기액(VAT 포함 총액 기준)",
                     code="judgement = payable_net_for_payout + Σcarry_post_tax_pos", ref="V2 §8.3 11단계 L302 · L304")
    internal = bool(ctx.holder(pid).get("is_internal"))
    confirmed = evaluated and (judge >= limit or force) and not hold
    if grp:
        confirmed = grp["confirmed"]
        ctx.emit(STEP, "payout_group_judgement", grp["confirmed"], c, **kw,
                 inputs={"묶음 계약": grp["contracts"], "묶음 판정 금액 합": grp["total"], "최소 지급액(늦게 시작한 계약)": grp["limit"],
                         "묶음 안 강제 정산": grp["force"], "보류": grp["hold"]},
                 formula="받는 사람 순액 묶음은 묶음 합으로 지급 판정 — 지급이면 묶음 전체 지급, 미달이면 음수 줄까지 묶음 전체 이월",
                 ref="V2 §8.3 10 · 11단계 받는 사람 순액 (v4.0.76)")
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
    cbc = p.out["CLAIM"].get("clawback_consent_amount") or D(0)
    if cbc:
        # 전속계약금 반환은 실제 지급하는 달에만 빼고 그 달 반환채권 잔액을 줄임 — 보류 · 미달 이월 달은 미룸(이월 행은
        # 반환을 빼기 전 세전 금액). 순액이 음수로 넘어간 달은 청구 판정으로 넘어갔으므로 회수로 봄(V2 §8.3 10단계 1), v4.0.77)
        held = bool(p.out["CLAIM"].get("clawback_hold_deferred"))
        rec = cbc if not held and (confirmed or (p.out["CLAIM"].get("net_after_return") or D(0)) < 0) else D(0)
        o["clawback_recovered"] = ctx.emit(STEP, "clawback_recovered", rec, c, **kw,
                                           inputs={"동의 연결 전속계약금 반환": cbc, "지급 확정": confirmed, "보류로 미룸": held},
                                           formula="그 달 회수한 전속계약금 반환 = 지급 확정(또는 청구 판정으로 넘어감)이면 반환액, 보류 · 미달 이월이면 0",
                                           ref="V2 §8.3 10단계 1) (v4.0.77)")
        o["clawback_deferred"] = ctx.emit(STEP, "clawback_deferred", cbc - rec, c, **kw,
                                          formula="미룬 전속계약금 반환 = 반환액 − 그 달 회수액 — 반환채권 잔액에 그대로 남아 다음 지급하는 달에 뺌",
                                          ref="V2 §8.3 10단계 1) · 11단계 (v4.0.77)")
    modified_invoice_notice(ctx, c, p, pid, pre_pos, kw)
    withholding_refund_notice(ctx, c, p, pid, confirmed, kw)
    roff = p.out["CLAIM"].get("return_offset") or D(0)
    deferred_return = (p.out["CLAIM"].get("return_offset_new") or D(0)) if roff and not confirmed else D(0)
    if deferred_return:
        ctx.emit(STEP, "return_offset_deferred", deferred_return, c, **kw,
                 formula="그 달 지급하지 않으면(미달 · 보류) 반환채권 상계를 미루고 세후 청구 이월로 남김(이월 행은 상계 전 세전 금액)",
                 ref="V2 §8.3 10 · 11단계 (v4.0.84)")
    o["payout_amount"] = ctx.emit(STEP, "payout_amount", judge if confirmed else D(0), c, **kw,
                                  formula="지급 확정액(대량이체 리스트, 부가세 · 원천세 · 상계 재가감 금지)", ref="V2 L303")
    ctx.emit(STEP, "excluded_from_bulk_transfer", internal, c, **kw,
             formula="자사 권리자(TX-01)는 증빙 · 대량이체 제외", ref="V2 L280 · TAX.md TX-01")
    rows = []
    if grp and grp.get("claim_settle"):
        # 묶음 순액 음수를 청구로 확정 — 묶음 이월 행은 청구에 들어갔으므로 소멸, 그 달 줄은 이월하지 않음(v4.0.80)
        for r in pre_pos + pre_neg_with + post_pos:
            if r.get("netting_carry"):
                rows.append(dict(r, action="SETTLE", payout_reservation_status="SETTLED", extinguished_yn=True,
                                 extinguished_month=ctx.month, carryover_reason_note="받는 사람 순액 청구로 소멸"))
            else:
                rows.append(dict(r, action="KEEP"))
    elif confirmed:
        for r in pre_pos + pre_neg_with + post_pos:
            rows.append(dict(r, action="RESERVE", payout_reservation_status="RESERVED"))
    elif evaluated:
        # 그 달 순액이 양수면 줄을 고르지 않고 음수 줄까지 모두 이월(음수만 빠져 다음 달 더 지급되는 일 방지,
        # V1 §7.3 · V2 §8.3 11단계, v4.0.60 정본 공백 보완). 순액이 0 이하면 음수는 10단계 청구 경로로 감.
        net_pos = (p.out["CLAIM"].get("net_after_return") or D(0)) > 0 or bool(grp)  # 순액 묶음이면 음수 계약 줄도(v4.0.76)
        for ln in p.lines:
            if ln.get("tax_decision_status") == "PENDING_REVIEW":
                continue  # 세무 판정 보류 라인은 아래에서 따로 이월(v4.0.82)
            # 상계가 분할액을 전부 지운 부가세 별도 라인(세전 0)도 그 달 부가세를 이월 행으로 넘김(V2 §8.3 11단계, v4.0.82)
            vat_only = (ln.get("offset_amount") or D(0)) > 0 and (ln.get("vat_amount") or D(0)) > 0 and ln["pre_tax_payable"] == 0
            if ln["origin"] in ("NEW", "ADJUSTMENT") and (ln["pre_tax_payable"] > 0 or (net_pos and ln["pre_tax_payable"] < 0) or vat_only):
                key = ln["line_key"]
                if (ln.get("offset_amount") or D(0)) > 0 and not hold:
                    carry_amt, extra = offset_carry(ctx, c, p, pid, ln)
                else:
                    carry_amt, extra = ln["pre_tax_payable"], {}
                    # 부가세 별도 과세사업자의 미달 · 보류 이월: 공급한 달에 확정된 부가세를 이월분에 붙여 지급하는 달에 함께 지급
                    # (다시 매기지 않음, 세금계산서는 공급한 달 전체 — 이월 부가세 원칙을 상계 없는 이월에도 적용, V2 §8.3 11단계, v4.0.87)
                    vat = ln.get("vat_amount") or D(0)
                    if vat > 0 and ln.get("vat_treatment") != "VAT_INCLUDED" and carry_amt > 0:
                        extra = {"components": {"carry_vat": vat, "invoice_supply": ln["split_amount"], "invoice_vat": vat}}
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
                                                 "vat_amount": ln.get("vat_amount"),
                                                 # 보호분(상계 비대상) — 다음 달 6단계 상계 대상에서 뺌(v4.0.63)
                                                 "protected_amount": min(max(D(0), ln.get("protected_amount") or D(0)),
                                                                         max(D(0), carry_amt))},
                                            **extra.get("components", {})),
                             "first_occurred_month": ctx.month, "first_payable_confirmed_month": None,
                             "payout_reservation_status": "NONE", "extinguished_yn": False,
                             "carry_line_origin": ln["origin"],
                             **({"netting_carry": True} if grp else {}),
                             **{k: v for k, v in extra.items() if k != "components"}})
        # 이번 달 6단계에서 상계한 세전 이월 행이 다시 최소 지급 미달이면: 상계분은 그 달 확정, 원래 행은 소멸 · 남은 금액만 새로 이월
        offset_ids = set()
        if not hold:
            for ln in p.lines:
                if ln["origin"] == "CARRY_PRE_TAX" and (ln.get("offset_amount") or D(0)) > 0:
                    r0 = next((r for r in pre_pos if r.get("ledger_id") == ln.get("ledger_id")), None)
                    if not r0:
                        continue
                    rest, extra = offset_carry(ctx, c, p, pid, ln)
                    offset_ids.add(r0.get("ledger_id"))
                    rows.append(dict(r0, action="SETTLE", payout_reservation_status="SETTLED", extinguished_yn=True,
                                     extinguished_month=ctx.month, carryover_reason_note="선급금 상계 후 남은 금액 새로 이월"))
                    cvat = D((dict(r0.get("components") or {}, **extra.get("components", {}))).get("carry_vat") or 0)
                    # 세전 잔액이 0이어도 이월 부가세가 남으면 행을 새로 적어 지급하는 달에 함께 지급(V2 §8.3 11단계, v4.0.71 보완)
                    if rest > 0 or cvat > 0:
                        comp = dict(r0.get("components") or {})
                        comp.update(split_amount=rest, offset_amount=D(0),
                                    protected_amount=min(D(comp.get("protected_amount") or 0), rest), **extra.get("components", {}))
                        rows.append(dict(r0, ledger_id=None, action="NEW", origin_month=r0.get("origin_month"), carryover_reason="지급 하한 미달",
                                         carryover_amount=rest, components=comp,
                                         **{k: v for k, v in extra.items() if k != "components"}))
        for r in pre_pos + pre_neg_with + post_pos:
            if r.get("ledger_id") in offset_ids:
                continue
            rows.append(dict(r, action="KEEP"))
        if any(r["action"] == "NEW" for r in rows):
            ctx.issue("CANON_GAP", "지급 이월 적재 구성요소(VAT · 상계) 보존 방식 정본 없음 — 라인별 세전 기초금액 + 구성요소",
                      STEP, c.holder_id, "V2 L305", "Q-21")
    # 세무 판정 보류 라인: 지급 · 청구 판정과 상관없이 그 금액만 '세무 판정 보류' 사유로 세전 이월, 판정이 확정되면 다음 달 지급
    # (마감은 막지 않음, V2 11.3절 · 마감 허용 조건, 2026-11-04 white 결정 60, v4.0.82)
    for ln in p.lines:
        if ln["origin"] in ("NEW", "ADJUSTMENT") and ln.get("tax_decision_status") == "PENDING_REVIEW" and ln["pre_tax_payable"]:
            key = ln["line_key"]
            rows.append({"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid,
                         "contract_id": c.id, "origin_month": ctx.month, "account_type": "PRE_TAX",
                         "pipeline_id": key.get("pipeline_id"), "consignment_balance_yn": False,
                         "income_category": key.get("income_category") or ln.get("income_category"),
                         "income_clause": key.get("income_clause") or ln.get("income_clause"),
                         "tax_threshold_unit_key": key.get("tax_threshold_unit_key") or ln.get("tax_threshold_unit_key"),
                         "carryover_reason": "세무 판정 보류", "carryover_amount": ln["pre_tax_payable"],
                         "components": {"split_amount": ln["split_amount"], "offset_amount": ln["offset_amount"],
                                        "vat_amount": ln.get("vat_amount"),
                                        "protected_amount": min(max(D(0), ln.get("protected_amount") or D(0)), max(D(0), ln["pre_tax_payable"]))},
                         "first_occurred_month": ctx.month, "first_payable_confirmed_month": None,
                         "payout_reservation_status": "NONE", "extinguished_yn": False, "carry_line_origin": ln["origin"]})
            ctx.emit(STEP, "pending_review_carry", ln["pre_tax_payable"], c, **kw, line=ln["line_id"],
                     inputs={"판정 보류 사유": ln.get("matrix_case_id")},
                     formula="세무 판정 보류 라인 — 그 금액만 '세무 판정 보류' 사유로 세전 이월, 마감 진행",
                     ref="V2 11.3절 판정 보류 상태 (v4.0.82)")
    if deferred_return:
        rows.append({"ledger_id": None, "action": "NEW", "rights_holder_id": c.holder_id, "payee_id": pid, "contract_id": c.id,
                     "origin_month": ctx.month, "account_type": "POST_TAX", "pipeline_id": None, "consignment_balance_yn": False,
                     "income_category": None, "income_clause": None, "tax_threshold_unit_key": None,
                     "carryover_reason": "청구 이월(기지급 반환채권 — 지급하지 않은 달이라 상계 미룸)", "carryover_amount": -deferred_return,
                     "components": {}, "first_occurred_month": ctx.month, "first_payable_confirmed_month": None,
                     "payout_reservation_status": "NONE", "extinguished_yn": False})
    # 청구 하한 미달 이월 행(10단계 PRE_TAX −) — 다음 달 새 금액과 합치지 않고 원장에 그대로 남김.
    # 합칠 때는 운영자 수동 대체 전표(V2 §8.3 10단계, v4.0.61 정본 공백 보완)
    # 그 달 새 음수와 함께 청구한 청구 이월 행은 소멸(청구로 넘어감, v4.0.62)
    merged = set(p.out["CLAIM"].get("claim_carry_settled") or [])
    # 받을 돈 상계 원칙(v4.0.85): 세전 청구 이월 행 · 상계 대상 세후 반환채권 행은 그 달 순액에 들어갔으므로
    # 그 달 양수 줄을 이월하는 달(미달 · 보류)에는 그대로 두고(KEEP), 그 밖에는 소멸(지급에서 상계 · 청구 확정 · 새 청구 이월로 넘어감).
    # 상계 대상이 아닌 세후 행은 종전대로 새 음수 · 강제 청구 달에 청구로 합칠 때만 소멸(v4.0.62 · v4.0.69)
    carried_pos = any(r["action"] == "NEW" and r["carryover_amount"] > 0 for r in rows)
    issued = bool(p.out["CLAIM"].get("claim_issued_yn"))
    for r in c.carry["pre_neg"] + c.carry["post_neg"]:
        if r["payee_id"] != pid or r.get("carry_line_origin"):
            continue
        in_net = r["account_type"] == "PRE_TAX" or offsettable(r)
        if r.get("ledger_id") in merged or (in_net and (issued or not carried_pos)):
            note = "그 달 새 음수와 함께 청구" if r.get("ledger_id") in merged else (
                "받을 돈 상계 — 그 달 청구로 확정" if issued else "받을 돈 상계 — 그 달 지급액과 상계 · 남은 금액은 새 청구 이월")
            rows.append(dict(r, action="SETTLE", payout_reservation_status="SETTLED", extinguished_yn=True,
                             extinguished_month=ctx.month, carryover_reason_note=note))
        else:
            rows.append(dict(r, action="KEEP"))
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
        extra = {"components": {"carry_vat": ln["vat_amount"] - vat_paid, "invoice_supply": ln["split_amount"], "invoice_vat": ln["vat_amount"]}}
        ctx.emit(STEP, "offset_paid_gross", supply, c, **kw,
                 inputs={"상계액": off, "그 달 공급가액": supply, "그 달 부가세": vat_paid, "이월 부가세": ln["vat_amount"] - vat_paid},
                 formula="부가세 별도 라인 상계분 = 공급가액 내림(상계액 × 100/110) + 부가세(상계액 − 공급가액), 남은 공급가액 · 부가세 이월",
                 ref="V2 §8.3 11단계 (v4.0.59)")
    elif loan:
        carry = ln["pre_tax_payable"]
    else:
        ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = D(0)
        carry = ln["pre_tax_payable"]
        # 소득 선지급(EARNED) + 부가세 별도: 공급한 달에 확정된 부가세는 이월분에 붙여 지급하는 달에 지급(다시 매기지 않음, v4.0.71)
        vat = ln.get("vat_amount") or D(0)
        if vat > 0 and ln.get("vat_treatment") != "VAT_INCLUDED":
            extra = {"components": {"carry_vat": vat, "invoice_supply": ln["split_amount"], "invoice_vat": vat}}
            ctx.emit(STEP, "offset_month_carry_vat", vat, c, **kw, inputs={"그 달 부가세": vat, "세전 이월": carry},
                     formula="소득 선지급 상계 달 미달 이월 — 세전 잔액은 이월, 공급한 달에 확정된 부가세는 이월분에 붙여 지급(세금계산서는 공급한 달 전체)",
                     ref="V2 §8.3 11단계 (v4.0.71)")
    for f in ("taxable_base", "income_tax", "local_income_tax", "withholding_total"):
        ctx.emit("TAX", f, ln[f], c, **kw, formula="상계한 달 미달 이월 — 그 달 원천징수는 상계분만(11단계에서 다시 정함)",
                 ref="V2 §8.3 11단계 (v4.0.56)")
    from .s09_tax import totals
    totals(ctx, c, p)  # 받는 사람 세액 합계를 상계분 기준으로 다시 냄
    ctx.emit(STEP, "offset_month_carry_pre_tax", carry, c, **kw, inputs={"분할액": ln["split_amount"], "상계액": off},
             formula="상계 뒤 최종 정산금액이 최소 지급 미달 — 상계분은 그 달 지급 확정, 나머지는 세전 이월(원천세는 지급하는 달)",
             ref="V1 §7.3 · V2 §8.3 11단계 (v4.0.56)")
    return carry, extra
