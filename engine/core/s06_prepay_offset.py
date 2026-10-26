"""6단계 PREPAY_OFFSET — 선급금 상계(V2 §8.3 표 L173 · 본문 L215~236, V1 §5.3 · §7.1, SPEC 9절).

적격 세전액(동일 계약 · 원 권리자 라인만) = max(0, P1.1 순수신규 − 4단계 P1.1 공제) + max(0, P2.1 순액)
  + max(0, CONDITIONAL P5.1 확정액) + CONDITIONAL 일시 · 분할 지원금 + CONDITIONAL 종료 일시정산.
상계 가능액 = 적격 세전액 − 예상 원천세(LOAN) / 0(EARNED), 당월 상계액 = min(상계 가능액, 미상계 잔액).
라인별 안분: 적격액 오름차순(동률 시 P1.1 뒤) 선행 floor, 최대 라인 역산(V2 L232~233 · 13.3 L579). 차감은 8단계.
"""

from .money import D, floor_won
from .tax import estimate_withholding

STEP = "PREPAY_OFFSET"


def attrs(ln):
    return {"label": ln.label, "pipeline_id": ln.pipeline_id, "supply_nature": ln.supply_nature,
            "income_category": ln.income_category, "income_clause": ln.income_clause,
            "tax_threshold_unit_key": ln.tax_threshold_unit_key, "payee_is_author": ln.payee_is_author}


def eligible_lines(ctx, c):
    out = []
    for ln in c.lines.values():
        if ln.fixed_payee:  # 다른 수취인 금액 제외(L225)
            continue
        if ln.pipeline_id == "1.1":
            e = max(D(0), ln.net - ln.mmg_subsidy)
            why = "max(0, P1.1 순수신규 − 4단계 P1.1 공제) = max(0, net_1_1 − mmg_subsidy)"
        elif ln.pipeline_id == "2.1":
            e = max(D(0), ln.net)
            why = "max(0, P2.1 순액)"
        elif ln.pipeline_id == "5.1" and ln.offset_type == "CONDITIONAL":
            e = max(D(0), ln.net)
            why = "max(0, 상계허용 P5.1 확정액)"
        elif ln.pipeline_id == "LUMPSUM" and getattr(ln, "conditional", False):
            e = ln.net
            why = "상계허용 일시 · 분할 지원금 / 종료 일시정산"
        else:
            continue
        ln.eligible = e
        out.append((ln, e, why))
    return out


def run(ctx):
    for c in ctx.contracts.values():
        pre = [p for p in ctx.input["prepayments"] if p["contract_id"] == c.id]
        out = c.step_out(STEP)
        if not pre:
            out["applicable"] = ctx.emit(STEP, "applicable", False, c, formula="선급금 원장 없음 — 6단계 생략",
                                         ref="V1 §5.3")
            out["offset_amount"] = ctx.emit(STEP, "offset_amount", D(0), c, formula="선급금 원장 없음 — 당월 상계액 0원",
                                            ref="V2 §8.3 6단계")
            continue
        if len(pre) > 1:
            ctx.warn("PREPAY_MULTI", f"{c.id} 선급금 원장 {len(pre)}건 — 잔액 합산", "V1 L319")
        types = {p["prepayment_tax_type"] for p in pre}
        if len(types) > 1:
            ctx.stop("INPUT_ERROR", "PREPAY_TAX_TYPE_MIXED", f"{c.id} 선급금 세무 유형 혼재 금지", "V1 L319")
        if any(s["contract_id"] == c.id for s in ctx.input["payee_splits"]):
            ctx.stop("INPUT_ERROR", "PREPAY_WITH_PAYEE_SPLIT", f"{c.id} 선급금과 수취인 분할 동시 존재 금지", "V1 L323")
        ptype = pre[0]["prepayment_tax_type"]
        bal = sum(D(p["prepay_unoffset_balance"]) for p in pre)
        payee = pre[0].get("offset_payee_id") or c.holder_id
        c.prepay = {"type": ptype, "balance": bal, "payee": payee, "rows": pre}
        out["applicable"] = ctx.emit(STEP, "applicable", True, c, inputs={"prepayment_tax_type": ptype})
        out["prepayment_tax_type"] = ptype
        out["prepay_balance_before"] = ctx.emit(STEP, "prepay_balance_before", bal, c,
                                                formula="미상계 선급금 잔액(전월 말)", ref="V1 §5.3")
        compute(ctx, c, first=True)


def compute(ctx, c, first, cap=None):
    """1차 산정(first) 또는 9단계 재검증 후 상계액 축소(cap)."""
    out = c.step_out(STEP)
    pp = c.prepay
    el = eligible_lines(ctx, c)
    total = sum(e for _, e, _ in el)
    if first:
        for ln, e, why in el:
            ctx.emit(STEP, "offset_eligible", e, c, line=ln.label, line_key=ln.key(), inputs={"net": ln.net},
                     formula=why, ref="V2 §8.3 6단계 L218~222")
        out["offset_eligible_total"] = ctx.emit(
            STEP, "offset_eligible_total", total, c, inputs={ln.label: e for ln, e, _ in el},
            formula="적격 세전액 = P1.1 + P2.1 + 상계허용 P5.1 + 상계허용 일시 · 분할 지원금 + 상계허용 종료 일시정산(동일 계약)",
            code="offset_eligible_total = e_1_1 + e_2_1 + e_5_1 + e_inst + e_ls", ref="V2 §8.3 6단계 L223")
        if pp["type"] == "LOAN":
            wsum, it, lt, per = estimate_withholding(ctx, pp["payee"], [(attrs(ln), e) for ln, e, _ in el])
            note = ""
        else:
            wsum, it, lt, per = D(0), D(0), D(0), []
            note = "EARNED — 원천세 상당액 차감 없음"
        out["offset_withholding_equiv"] = ctx.emit(
            STEP, "offset_withholding_equiv", wsum, c, inputs={"prepayment_tax_type": pp["type"], "소득세": it, "지방소득세": lt},
            formula="상계 대상 원천세 상당액 — 9단계와 같은 순차 산식(소득세 내림 → 지방소득세 내림), 비대상 라인 0원",
            code="TAX.estimate_withholding(eligible_lines) if LOAN else 0", ref="V2 §8.3 6단계 L227~228", note=note)
        ctx.emit(STEP, "offset_withholding_income_tax", it, c, formula="상계 대상 원천세 상당액 중 소득세", ref="V2 L227")
        ctx.emit(STEP, "offset_withholding_local_tax", lt, c, formula="상계 대상 원천세 상당액 중 지방소득세", ref="V2 L227")
        capacity = total - wsum
        out["offset_capacity"] = ctx.emit(STEP, "offset_capacity", capacity, c,
                                          inputs={"적격 세전액": total, "원천세 상당액": wsum},
                                          formula="상계 가능액 = 상계 대상 세전액 − 상계 대상 원천세 상당액",
                                          code="offset_capacity = offset_eligible_total − offset_withholding_equiv",
                                          ref="V2 §8.3 6단계 L229")
        amount = min(capacity, pp["balance"]) if capacity > 0 else D(0)
        out["offset_amount_initial"] = ctx.emit(
            STEP, "offset_amount_initial", amount, c, inputs={"상계 가능액": capacity, "미상계 잔액": pp["balance"]},
            formula="상계 가능액 ≤ 0이면 상계 0원 · 잔액 유지, 아니면 당월 상계액 = min(상계 가능액, 미상계 선급금 잔액)",
            code="offset_amount = min(offset_capacity, prepay_unoffset_balance) if capacity > 0 else 0",
            ref="V2 §8.3 6단계 L230~231")
        out["taxable_reduction_flag"] = ctx.emit(
            STEP, "taxable_reduction_flag", pp["type"] == "EARNED", c, inputs={"prepayment_tax_type": pp["type"]},
            formula="소득 선지급(EARNED)이면 과세표준 차감, 대여금(LOAN)이면 과세표준 유지", ref="V2 §8.3 6단계 L235")
    else:
        amount = cap
    allocate(ctx, c, el, amount, revalidated=not first)
    out["offset_amount"] = ctx.emit(STEP, "offset_amount", amount, c, inputs={"1차 산정": out.get("offset_amount_initial")},
                                    formula="당월 상계액(예정) — 9단계 재검증 후 값", ref="V2 §8.3 6단계 L228 · L231",
                                    provisional=not first, note="Q-13(현금 가용액 산식)" if not first else "")
    after = pp["balance"] - amount
    out["prepay_balance_after"] = ctx.emit(STEP, "prepay_balance_after", after, c,
                                           inputs={"잔액": pp["balance"], "상계액": amount},
                                           formula="갱신 예정 선급금 잔액 = 미상계 잔액 − 당월 상계액(Locked 전 '예정')",
                                           ref="V1 §7.1 L531")
    out["offset_eligible_lines"] = [{"line_key": ln.key(), "eligible": e, "offset": ln.offset} for ln, e, _ in el]
    c.prepay_balance_after = after
    c.prepay["amount"] = amount


def allocate(ctx, c, el, amount, revalidated=False):
    for ln in c.lines.values():
        ln.offset = D(0)
    pos = [(ln, e) for ln, e, _ in el if e > 0]
    if not pos or amount <= 0:
        return
    den = sum(e for _, e in pos)
    order = sorted(pos, key=lambda x: (x[1], 1 if x[0].pipeline_id == "1.1" else 0, x[0].pipeline_id,
                                       str(x[0].agreement_id or x[0].approval_id or ""), x[0].label))
    acc = D(0)
    for i, (ln, e) in enumerate(order):
        if i < len(order) - 1:
            raw = amount * e / den
            ln.offset = floor_won(raw)
            acc += ln.offset
            rounding, before = "FLOOR_WON", raw
        else:
            ln.offset = amount - acc
            rounding, before = "ALLOC_LAST_REMAINDER", None
        ctx.emit(STEP, "offset_alloc", ln.offset, c, line=ln.label, line_key=ln.key(),
                 inputs={"당월 상계액": amount, "라인 적격액": e, "적격액 합계": den},
                 formula="적격액 오름차순(동률이면 P1.1을 뒤로) 선행 내림, 적격액 최대 라인이 잔여 차액",
                 code="offset[l] = floor(offset_amount × eligible_l / Σeligible); last = amount − Σ선행",
                 before=before, rounding=rounding, ref="V2 §8.3 6단계 L232~233 · §13.3 L579",
                 provisional=revalidated, note="9단계 재검증 후 재안분" if revalidated else "")
