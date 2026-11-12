"""9단계 TAX — 세무 판정 · 원천세 · VAT · 실정산액(V2 §8.3 표 L176 · 본문 L260~283 · 11장, TAX.md, SPEC 12절).

라인별: 케이스 판정(TAX.md [A]) → VAT([B]) → 원천징수([C], OTHER는 판정 단위 과세표준) → 라인 실정산액.
payee별 9단계 실정산액 = (당월 신규 세전 지급액 − 당월 신규 원천징수세액 + 당월 부가가치세) + 위탁 실정산액(L282).
원귀속 PRE_TAX 세후 환산액 = 기초금액 − 해당 원귀속분 원천징수세액(L271).
끝에 6단계 재검증: 상계 적격 라인 현금 가용액 < 상계액이면 상계액 축소 후 8 · 9단계 재계산(L228 · L231, Q-13 잠정).
"""

from collections import OrderedDict

from .money import D, alloc_last_remainder, alloc_offset_first, floor_won
from .tax import classify, vat_of, withhold_business, withhold_other

STEP = "TAX"
PAYABLE = ("NEW", "ADJUSTMENT")  # 당월 신규 + 전월 정산 조정(세금 계산 직전 인입)


def run(ctx):
    # 사업소득 원천세는 원 권리자 · 받는 사람 단위로 계약을 넘어 합산하므로(V2 §8.3 9단계, v4.0.48)
    # 모든 계약의 라인 세무를 먼저 정하고 → 사업소득 합산 → 라인 실정산액 · 합계 → 상계 재검증 순서로 돈다.
    for c in ctx.contracts.values():
        tax_contract(ctx, c)
    business_all(ctx)
    for c in ctx.contracts.values():
        finish_contract(ctx, c)
    for c in ctx.contracts.values():
        revalidate_offset(ctx, c)


def vat_treatment(ctx, c, pid):
    return ctx.holder(pid).get("vat_treatment") or c.row.get("vat_treatment") or "VAT_EXCLUDED"


def tax_contract(ctx, c):
    for p in c.payees.values():
        tax_payee(ctx, c, p)


def finish_contract(ctx, c):
    for p in c.payees.values():
        finish_payee(ctx, c, p)


def is_open_negative(x):
    """원거래 달 미마감 음수 라인(당월 신규 라인의 환불 공제 초과분) — 별개 채권의 상계가 아니라 대가의 감소(v4.0.48)."""
    return ((x["origin"] == "NEW" or (x["origin"] == "CARRY_PRE_TAX" and x.get("carry_line_origin") == "NEW"))
            and (x.get("pending_negative_base") or D(0)) < 0)


def net_negatives(pos, negs):
    """양수 과세표준과 미마감 음수를 합산. 합계 > 0이면 양수 라인 과세표준을 합계로 다시 배분하고 음수는 소멸,
    합계 ≤ 0이면 양수 라인 과세표준 0 · 남은 음수를 음수 라인에 배분(이월). → (양수 합, 음수 합, 합계)"""
    ptot = sum((x["taxable_base"] for x in pos), D(0))
    ntot = sum((x["pending_negative_base"] for x in negs), D(0))
    net = ptot + ntot
    if net > 0:
        for x, b in zip(pos, alloc_last_remainder(net, [x["taxable_base"] for x in pos])):
            x["taxable_base"] = b
        for x in negs:
            x["pending_negative_base"] = None
    else:
        for x in pos:
            x["taxable_base"] = D(0)
        for x, r in zip(negs, alloc_last_remainder(net, [x["pending_negative_base"] for x in negs])):
            x["pending_negative_base"] = r
    return ptot, ntot, net


def business_all(ctx, holder=None):
    """사업소득 원천세: 원 권리자 · 받는 사람 · 지급일 · 소득 구분 단위로 계약을 넘어 양수 · 미마감 음수 라인을 합산,
    합계 > 0이면 1회 계산(10원 미만 내림) · 라인 비율 배분, 합계 ≤ 0이면 0원 · 남은 음수 이월
    (V2 §8.3 9단계 · §13.1, 소득세법 제127조 제1항 · 시행령 제51조 제3항 · 제213조 제1항, v4.0.36 · v4.0.48)."""
    groups = OrderedDict()
    for (cid, pid), (c, p, biz) in (getattr(ctx, "biz_reg", None) or {}).items():
        if holder is not None and c.holder_id != holder:
            continue
        groups.setdefault((c.holder_id, pid), []).extend((c, x) for x in biz)
    for (h, pid), items in groups.items():
        negs = [(c, x) for c, x in items if is_open_negative(x)]
        pos = [(c, x) for c, x in items if not is_open_negative(x)]
        if negs:
            c0 = items[-1][0]
            ptot, ntot, net = net_negatives([x for _, x in pos], [x for _, x in negs])
            ctx.emit(STEP, "business_net_base", max(net, D(0)), c0, payee=pid,
                     inputs={"양수 과세표준 합": ptot, "미마감 원거래 음수 합": ntot, "합계": net,
                             "계약": sorted({c.id for c, _ in items})},
                     formula="사업소득 과세표준 = max(0, 양수 과세표준 합 + 미마감 원거래 음수 합) — 계약이 달라도 합산, 0 이하면 원천세 0 · 남은 음수 이월",
                     ref="V2 §8.3 9단계 · 소득세법 제24조 제1항 · 제127조 제1항 · 시행령 제51조 제3항 제1호의2 · 제213조 제1항 (v4.0.48)")
            if net < 0:
                ctx.emit(STEP, "business_negative_carry", net, c0, payee=pid, inputs={"합계": net},
                         formula="합계 0 이하 — 원천세 0, 남은 음수는 10단계 청구 판정으로(기준 이내면 세전 청구 이월, 새 양수와 합치지 않음, v4.0.72)", ref="V2 §8.3 9단계 (v4.0.48)")
        w = withhold_business(ctx, sum((x["taxable_base"] for _, x in pos), D(0)))
        bases = [x["taxable_base"] for _, x in pos]
        offs = [(x.get("offset_amount") or D(0)) > 0 for _, x in pos]  # 상계 라인을 앞에(끝수는 상계 없는 라인, v4.0.75)
        its = alloc_offset_first(w["income_tax"], bases, offs)
        lts = alloc_offset_first(w["local_income_tax"], bases, offs)
        for (c, x), it, lt in zip(pos, its, lts):
            set_withholding(ctx, c, x, dict(payee=pid, line=x["line_id"], line_key=x["line_key"]),
                            dict(w, income_tax=it, local_income_tax=lt), "BUSINESS")
        for c, x in negs:
            set_withholding(ctx, c, x, dict(payee=pid, line=x["line_id"], line_key=x["line_key"]),
                            dict(w, income_tax=D(0), local_income_tax=D(0)), "BUSINESS")


def tax_payee(ctx, c, p):
    pid = p.payee_id
    treat = vat_treatment(ctx, c, pid)
    units = OrderedDict()  # (origin, unit key, clause) → [lines]  — OTHER 판정 단위
    biz = []  # BUSINESS 원천징수 라인 — 받는 사람 단위 합산(v4.0.36)
    for ln in p.lines:
        for k in ("deemed_expense", "other_income_amount", "threshold_exempt_yn", "small_amount_exempt_yn",
                  "after_tax_amount", "consignment_fee_vat"):
            ln.setdefault(k, None)
    for ln in p.lines:
        kw = dict(payee=pid, line=ln["line_id"], line_key=ln["line_key"])
        if ln["origin"] == "CONSIGNMENT":
            consignment(ctx, c, p, ln, kw)
            continue
        if ln["origin"] == "CARRY_PRE_TAX" and ln["pre_tax_payable"] < 0 and not ln.get("carry_with_positive"):
            # 청구 하한 미달 이월 행 — 세무 판정 · 지급 계산에 넣지 않고 원장에만 유지(판정 보류로 마감을 막지 않음, v4.0.61)
            ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = D(0)
            continue
        cl = classify(ctx, pid, ln)
        tbl = cl.get("table") or {}
        ln["matrix_case_id"] = cl["case"]
        ln["tax_decision_status"] = cl["status"]
        ln["correction_channels"] = [str(x) for x in (tbl.get("correction_channels") or [])]
        ln["evidence_type"] = tbl.get("evidence_type")
        ln["withholding_rule"] = cl["withholding"]
        ctx.emit(STEP, "matrix_case_id", cl["case"], c, **kw,
                 inputs={"payee_tax_type": ctx.holder(pid).get("payee_tax_type"), "supply_nature": ln["supply_nature"],
                         "income_category": ln["income_category"], "hint": ctx.holder(pid).get("matrix_case_id_hint")},
                 formula="TX-01~13 판정(자사 → 재화 → NULL 보류 → 프리랜서 공급 성격 → tax_type_cd → 보류 후보)",
                 code="classify(payee, line)", ref="V2 §11.1 L407~412 · TAX.md [A]",
                 provisional=cl["status"] != "DECIDED", note=cl["reason"])
        ctx.emit(STEP, "tax_decision_status", cl["status"], c, **kw, formula="DECIDED만 마감 허용(PENDING_REVIEW는 차단)",
                 ref="V2 §11.1 L411")
        if cl["status"] != "DECIDED":
            ctx.issue("CANON_GAP", f"{pid} {ln['line_id']} 세무 판정 보류: {cl['reason']}", STEP, c.holder_id,
                      "TAX.md 확인 필요 2 · 3", "TAX-2")
        # [B] VAT — 케이스가 정해졌으면 VAT 규칙은 확정(원천징수만 보류일 수 있음).
        # 공급가액은 상계 전 금액(분할액) 기준: V2 L264 '공급가액 = 세전 지급액(상계 전 공급가액 기준)'(Q-17 해소 2026-10-26)
        pre = ln["pre_tax_payable"]
        base = ln["split_amount"]
        if ln["origin"] in PAYABLE and cl["vat"]:
            supply, vat, _, raw = vat_of(cl["vat"], treat, base)
        else:
            supply, vat, raw = pre, D(0), None
        applied = pre if treat == "VAT_INCLUDED" or cl["vat"] != "TAXABLE_10" else pre + vat
        ln["supply_amount"], ln["vat_amount"], ln["vat_applied_amount"] = supply, vat, applied
        ln["vat_treatment"] = treat if cl["vat"] == "TAXABLE_10" else None
        if ln["origin"] in PAYABLE:
            ctx.emit(STEP, "vat_amount", vat, c, **kw, inputs={"vat rule": cl["vat"], "vat_treatment": treat,
                                                               "상계 전 공급가액(분할액)": base, "세전 지급액(상계 후)": pre},
                     formula=("VAT_EXCLUDED: 공급가액 = 세전 지급액(상계 전 공급가액 기준), 부가세 = 내림(공급가액 × 10%) / "
                              "VAT_INCLUDED: 공급가액 = 내림(총액 × 100/110), 부가세 = 총액 − 공급가액"
                              if cl["vat"] == "TAXABLE_10" else f"VAT {cl['vat']} — 가산 없음"),
                     code="vat_of(rule, treatment, split_amount)", before=raw,
                     rounding="FLOOR_WON" if raw is not None else "NONE", ref="V2 §8.3 9단계 L263~265 · TAX.md [B]")
            ctx.emit(STEP, "supply_amount", supply, c, **kw, formula="공급가액(상계 전)", ref="V2 L264")
            ctx.emit(STEP, "vat_applied_amount", applied, c, **kw,
                     formula="부가세 반영 후 정산액 = 세전 지급액 + 부가세(VAT_INCLUDED는 총액, 가산 없음)", ref="V2 L263~265")
        # [C] 원천징수
        ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = None
        if cl["status"] != "DECIDED" or cl["withholding"] != "APPLY":
            if cl["status"] == "DECIDED":
                ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = D(0)
                ctx.emit(STEP, "withholding_total", D(0), c, **kw, inputs={"withholding": cl["withholding"]},
                         formula=f"{cl['case']} 원천징수 없음", ref="TAX.md [C] · V2 11.2")
            continue
        if ln["taxable_base"] is None:
            ln["income_tax"] = ln["local_income_tax"] = ln["withholding_total"] = D(0)
            continue
        if ln["income_category"] == "OTHER":
            # 지난달 원 건의 정정분은 원 건과 한 건으로 판정(원 건별로 묶음, v4.0.45)
            # 상계한 달 미달 이월분도 같은 방식(v4.0.59)
            om = (ln.get("origin_month") if ln["origin"] in ("ADJUSTMENT", "CARRY_PRE_TAX") and ln.get("origin_unit_base") is not None
                  else None)
            units.setdefault((ln["origin"], ln["tax_threshold_unit_key"], ln["income_clause"], om), []).append(ln)
            continue
        biz.append(ln)
    # 사업소득은 계약을 넘어 원 권리자 · 받는 사람 단위로 business_all에서 1회 계산(v4.0.48)
    reg = getattr(ctx, "biz_reg", None)
    if reg is None:
        reg = ctx.biz_reg = OrderedDict()
    reg[(c.id, pid)] = (c, p, biz)
    for (origin, unit, clause, om), lines in units.items():
        u = sum(x["taxable_base"] for x in lines)
        kw = dict(payee=pid, line=lines[-1]["line_id"], line_key=lines[-1]["line_key"])
        negs = [x for x in lines if is_open_negative(x)]
        if negs:
            # 기타소득은 판정 단위(건) 안에서만 미마감 음수를 합산, 다른 계약의 음수는 합치지 않음(v4.0.48)
            pos = [x for x in lines if not is_open_negative(x)]
            ptot, ntot, net = net_negatives(pos, negs)
            ctx.emit(STEP, "other_unit_net_base", max(net, D(0)), c, **kw,
                     inputs={"양수 과세표준 합": ptot, "미마감 원거래 음수 합": ntot, "합계": net, "unit": unit},
                     formula="기타소득 판정 단위 과세표준 = max(0, 양수 합 + 같은 판정 단위의 미마감 음수 합), 0 이하면 남은 음수 이월",
                     ref="V2 §8.3 9단계 · 소득세법 제84조 · 집행기준 84-0-1 (v4.0.48)")
            u = sum(x["taxable_base"] for x in lines)
        if om:
            # 원 건 + 정정분 합계로 과세최저한 판정, 이미 뗀 세액을 뺀 차액을 정정분 지급 때 징수
            # (소득세법 제84조 제3호, 소득세 집행기준 84-0-1 ②, V2 §8.3 9단계, v4.0.45)
            f0 = lines[0]
            ob = D(f0["origin_unit_base"])
            w0 = withhold_other(ctx, ob, clause)
            wt = withhold_other(ctx, u + ob, clause)
            oit = D(f0["origin_unit_income_tax"]) if f0.get("origin_unit_income_tax") is not None else w0["income_tax"]
            olt = D(f0["origin_unit_local_tax"]) if f0.get("origin_unit_local_tax") is not None else w0["local_income_tax"]
            de = wt["deemed_expense"] - w0["deemed_expense"]
            w = dict(wt, deemed_expense=de, other_income_amount=u - de,
                     income_tax=max(D(0), wt["income_tax"] - oit), local_income_tax=max(D(0), wt["local_income_tax"] - olt))
            ctx.emit(STEP, "origin_merged_income_tax", w["income_tax"], c, **kw,
                     inputs={"원 건 과세표준": ob, "정정분 과세표준": u, "합계 소득세": wt["income_tax"], "원 건 기징수 소득세": oit,
                             "합계 지방소득세": wt["local_income_tax"], "원 건 기징수 지방소득세": olt, "원 건 귀속월": om},
                     formula="정정분 세액 = max(0, 합계 기준 세액 − 원 건에서 이미 뗀 세액), 필요경비 = 합계 필요경비 − 원 건 필요경비",
                     ref="V2 §8.3 9단계 · 소득세법 제84조 제3호 · 집행기준 84-0-1 (v4.0.45)")
            if wt["income_tax"] < oit or wt["local_income_tax"] < olt:
                ctx.issue("CANON_GAP", f"감액 정정으로 합계 세액이 원 건 기징수 세액보다 작음 — 차액 환급은 정정 채널 3-a(원 건 귀속월 {om})",
                          STEP, c.holder_id, "V2 §10.4 채널 3-a")
        else:
            w = withhold_other(ctx, u, clause)
        ctx.emit(STEP, "deemed_expense", w["deemed_expense"], c, **kw,
                 inputs={"판정 단위 과세표준": u, "의제율": w["deemed_rate"], "unit": unit},
                 formula="필요경비 = 내림(판정 단위 과세표준 × 의제율)", code="deemed = floor(U × deemed_rate)",
                 before=w["deemed_raw"], rounding="FLOOR_WON", ref="V2 §8.3 9단계 L275~276")
        ctx.emit(STEP, "other_income_amount", w["other_income_amount"], c, **kw, inputs={"U": u, "필요경비": w["deemed_expense"]},
                 formula="기타소득금액 = 과세표준 − 필요경비", ref="V2 L276")
        ctx.emit(STEP, "threshold_exempt_yn", w["threshold_exempt_yn"], c, **kw,
                 inputs={"기타소득금액": w["other_income_amount"], "과세최저한": ctx.p("other_income_min_tax_amount")},
                 formula="기타소득금액 ≤ 50,000원이면 소득세 · 지방소득세 0원(판정 단위 = tax_threshold_unit_key)",
                 ref="V2 L277~278 · V1 L436")
        offs = [(x.get("offset_amount") or D(0)) > 0 for x in lines]  # 상계 라인을 앞에(끝수는 상계 없는 라인, v4.0.75)
        its = alloc_offset_first(w["income_tax"], [x["taxable_base"] for x in lines], offs)
        lts = alloc_offset_first(w["local_income_tax"], [x["taxable_base"] for x in lines], offs)
        # 필요경비 · 기타소득금액은 라인에 나눠 저장(과세표준 비율, 끝수는 마지막 라인, V2 §13.1, v4.0.44)
        des = alloc_last_remainder(w["deemed_expense"], [x["taxable_base"] for x in lines])
        filing(ctx, c, pid, lines[-1], clause)
        for x, it, lt, de in zip(lines, its, lts, des):
            x.update(deemed_expense=de, other_income_amount=x["taxable_base"] - de,
                     threshold_exempt_yn=w["threshold_exempt_yn"], small_amount_exempt_yn=w["small_amount_exempt_yn"])
            set_withholding(ctx, c, x, dict(payee=pid, line=x["line_id"], line_key=x["line_key"]),
                            dict(w, income_tax=it, local_income_tax=lt), "OTHER")


def finish_payee(ctx, c, p):
    pid = p.payee_id
    for ln in p.lines:
        if ln["origin"] in PAYABLE:
            wt = ln.get("withholding_total") or D(0)
            add_vat = ln["vat_amount"] if ln.get("vat_treatment") != "VAT_INCLUDED" else D(0)
            ln["net_settle_line"] = ln["pre_tax_payable"] - wt + add_vat
            ctx.emit(STEP, "net_settle_line", ln["net_settle_line"], c, payee=pid, line=ln["line_id"],
                     inputs={"세전 지급액": ln["pre_tax_payable"], "원천징수세액": wt, "부가세(가산분)": add_vat},
                     formula="라인 실정산액 = 세전 지급액 − 원천징수세액 + 부가가치세(VAT_INCLUDED는 가산 없음)",
                     ref="V2 §8.3 9단계 L282 · TAX.md 확인 필요 5", provisional=ln.get("vat_treatment") == "VAT_INCLUDED",
                     note="TAX-5" if ln.get("vat_treatment") == "VAT_INCLUDED" else "")
        elif ln["origin"] == "CARRY_PRE_TAX" and (ln["taxable_base"] is not None or ln.get("carry_with_positive")):
            wt = ln.get("withholding_total") or D(0)
            cv = ln.get("carry_vat_amount") or D(0)
            ln["after_tax_amount"] = ln["pre_tax_payable"] - wt + cv
            ctx.emit(STEP, "carry_pre_tax_after_tax", ln["after_tax_amount"], c, payee=pid, line=ln["line_id"],
                     inputs={"기초금액": ln["pre_tax_payable"], "원천징수세액": wt, "이월 부가세": cv},
                     formula="원귀속 PRE_TAX 세후 환산액 = 기초금액 − 해당 원귀속분 원천징수세액 + 이월된 부가세(상계한 달 미달 이월분)",
                     ref="V2 L271 · L282 · §8.3 11단계 (v4.0.59)")
    totals(ctx, c, p)


def filing(ctx, c, pid, ln, clause):
    """기타소득 신고 · 증빙 의무(tax_table.json 케이스 분기 — TX-03 C15 · C05 / TX-04 C19 · C17)."""
    case = ctx.tax_table["cases"].get(ln.get("matrix_case_id")) or {}
    br = (case.get("branches") or {}).get(clause) or {}
    if not br:
        return
    kw = dict(payee=pid, line=ln["line_id"])
    issue = bool(br.get("receipt_issue")) or "원천징수영수증" in str(case.get("evidence_type") or "")
    ctx.emit(STEP, "withholding_receipt_issue", issue, c, **kw, inputs={"branch": clause, "receipt_issue": br.get("receipt_issue")},
             formula="원천징수영수증 발급(기타소득 예외 분기는 금액 무관 발급)", ref="V2 §11.2 TX-03 · tax_table.json")
    ctx.emit(STEP, "simplified_statement_monthly", bool(br.get("simplified_statement_yn")), c, **kw,
             formula="간이지급명세서 매월 제출 대상 여부", ref="V2 §11.2 TX-03 · TX-04 · tax_table.json")
    if br.get("annual_statement_deadline"):
        ctx.emit(STEP, "annual_statement_due", br["annual_statement_deadline"], c, **kw,
                 formula="기타소득 지급명세서 연 1회 제출 기한", ref="V2 §11.2 TX-03 · tax_table.json")


def set_withholding(ctx, c, ln, kw, w, cat):
    ln["income_tax"], ln["local_income_tax"] = w["income_tax"], w["local_income_tax"]
    ln["withholding_total"] = w["income_tax"] + w["local_income_tax"]
    if cat == "BUSINESS":
        f_it = "소득세 = 내림(과세표준 × 3%)"
    else:
        f_it = "소득세 = 내림(기타소득금액 × 20%), 소득세 < 1,000원이면 0(소액부징수)"
    ctx.emit(STEP, "income_tax", w["income_tax"], c, **kw, inputs={"과세표준": ln["taxable_base"], "소득 구분": cat},
             formula=f_it, code="income_tax = floor(base × rate)", before=w["it_raw"], rounding="FLOOR_WON",
             ref="V2 §8.3 9단계 L268~270 · §13.1 L568")
    ctx.emit(STEP, "local_income_tax", w["local_income_tax"], c, **kw, inputs={"소득세": w["income_tax"]},
             formula="지방소득세 = 내림(소득세 × 10%)(합산세율 금지, 순차 2단)", code="local = floor(income_tax × 0.10)",
             before=w["lt_raw"], rounding="FLOOR_WON", ref="V2 §8.3 9단계 L269~271")
    ctx.emit(STEP, "withholding_total", ln["withholding_total"], c, **kw,
             inputs={"소득세": w["income_tax"], "지방소득세": w["local_income_tax"]}, formula="라인 총 원천징수세액",
             ref="V2 L271")
    if ln["taxable_base"]:
        rate = (ln["withholding_total"] * 100 / ln["taxable_base"]).quantize(D("0.01"))
        ln["effective_rate_pct"] = rate
        ctx.emit(STEP, "effective_rate_pct", rate, c, **kw, formula="실효세율(검증 참고값, 계산에 쓰지 않음)",
                 ref="TAX.md TX-02 · TX-03")


def consignment(ctx, c, p, ln, kw):
    cs = c.consignment or {}
    ret = getattr(c, "consignment_return", None) or {}
    fee_net = D(cs.get("fee_supply")) - D(ret.get("fee"))
    raw = fee_net * D("0.10")
    fee_vat = floor_won(raw)
    ftype = ret.get("fee_type") or cs.get("consignment_fee_type") or "NET_DEDUCT"
    settle = ln["pre_tax_payable"] - fee_vat if ftype == "NET_DEDUCT" else ln["pre_tax_payable"]
    ln.update(matrix_case_id="TX-11", tax_decision_status="DECIDED", income_tax=D(0), local_income_tax=D(0),
              withholding_total=D(0), vat_amount=D(0), supply_amount=ln["pre_tax_payable"],
              vat_applied_amount=ln["pre_tax_payable"], consignment_fee_vat=fee_vat, consignment_settle_amount=settle,
              net_settle_line=settle, withholding_rule="NONE",
              evidence_type=ctx.tax_table["cases"]["TX-11"]["evidence_type"],
              correction_channels=[str(x) for x in ctx.tax_table["cases"]["TX-11"]["correction_channels"]],
              fee_supply_net=fee_net, consignment_fee_type=ftype)
    ctx.emit(STEP, "matrix_case_id", "TX-11", c, **kw, formula="도서 재화 공급(위탁) — 원천징수 미호출 · 과세표준 미생성",
             ref="V2 §11.2 TX-11 L494~504")
    ctx.emit(STEP, "consignment_fee_vat", fee_vat, c, **kw,
             inputs={"월 수수료 공급가액": cs.get("fee_supply"), "반품 수수료 조정": -D(ret.get("fee")),
                     "당월 순 위탁 수수료 공급가액": fee_net},
             formula="위탁 수수료 부가세 = 내림(당월 순 위탁 수수료 공급가액 × 10%)", code="fee_vat = floor(fee_supply_net × 0.10)",
             before=raw, rounding="FLOOR_WON", ref="V2 §8.3 9단계 L266")
    ctx.emit(STEP, "consignment_settle_amount", settle, c, **kw,
             inputs={"4단계 순 위탁 정산액": ln["pre_tax_payable"], "수수료 부가세": fee_vat, "consignment_fee_type": ftype},
             formula="NET_DEDUCT: 위탁 실정산액 = 순 위탁 정산액 − 수수료 부가세 / GROSS_SETTLE: = 순 위탁 정산액(별도 청구)",
             code="settle = net_2_2 − fee_vat if NET_DEDUCT else net_2_2", ref="V2 §8.3 9단계 L266 · L282")


def totals(ctx, c, p):
    if not p.lines:  # 세무 대상 라인 없음(예: 자사 집계 전용) — 합계를 내지 않는다
        return
    new = [ln for ln in p.lines if ln["origin"] in PAYABLE]
    cons = [ln for ln in p.lines if ln["origin"] == "CONSIGNMENT"]
    carry = [ln for ln in p.lines if ln["origin"] == "CARRY_PRE_TAX" and ln.get("after_tax_amount") is not None]
    t = p.out["TAX"]
    tbs = [ln["taxable_base"] for ln in new if ln["taxable_base"] is not None]
    t["pre_tax_payable_total"] = sum((ln["pre_tax_payable"] for ln in new), D(0))
    t["split_amount_total"] = sum((ln["split_amount"] for ln in new), D(0))
    t["offset_amount_total"] = sum((ln["offset_amount"] for ln in new), D(0))
    t["taxable_base_total"] = sum(tbs, D(0)) if tbs else None
    t["vat_total"] = sum((ln["vat_amount"] for ln in new), D(0))
    t["vat_applied_total"] = sum((ln["vat_applied_amount"] for ln in new), D(0))
    t["income_tax_total"] = sum((ln.get("income_tax") or D(0) for ln in new), D(0))
    t["local_income_tax_total"] = sum((ln.get("local_income_tax") or D(0) for ln in new), D(0))
    t["withholding_total"] = t["income_tax_total"] + t["local_income_tax_total"]
    t["consignment_fee_vat"] = sum((ln["consignment_fee_vat"] for ln in cons), D(0)) if cons else None
    t["consignment_settle_amount"] = sum((ln["consignment_settle_amount"] for ln in cons), D(0))
    t["net_settle_amount"] = sum((ln["net_settle_line"] for ln in new), D(0)) + t["consignment_settle_amount"]
    prot = D(0)
    for ln in new:
        if ln["protected_amount"] and ln["pre_tax_payable"]:
            prot += floor_won(ln["net_settle_line"] * ln["protected_amount"] / ln["pre_tax_payable"])
    t["net_settle_protected"] = prot
    t["net_settle_offsettable"] = t["net_settle_amount"] - prot
    t["carry_pre_tax_after_tax_total"] = sum((ln["after_tax_amount"] for ln in carry), D(0))
    t["pending_review_lines"] = sum(1 for ln in p.lines if ln.get("tax_decision_status") == "PENDING_REVIEW")
    t["withholding_called"] = any(ln.get("withholding_rule") == "APPLY" and ln.get("tax_decision_status") == "DECIDED"
                                  for ln in p.lines)
    cases = [ln.get("matrix_case_id") for ln in p.lines if ln.get("matrix_case_id")]
    t["matrix_case_ids"] = sorted(set(cases))
    t["evidence_types"] = sorted({ln.get("evidence_type") for ln in p.lines if ln.get("evidence_type")})
    t["non_deductible_input_vat"] = sum((ln["vat_amount"] for ln in new if ln.get("matrix_case_id") in
                                         ("TX-06", "TX-07", "TX-09")), D(0))
    pid = p.payee_id
    for k in ("pre_tax_payable_total", "split_amount_total", "offset_amount_total", "taxable_base_total", "vat_total",
              "vat_applied_total", "income_tax_total", "local_income_tax_total", "withholding_total",
              "consignment_fee_vat", "consignment_settle_amount", "net_settle_amount", "net_settle_protected",
              "net_settle_offsettable", "carry_pre_tax_after_tax_total", "withholding_called", "non_deductible_input_vat"):
        ctx.emit(STEP, k, t[k], c, payee=pid, formula={
            "net_settle_amount": "payee별 당월 9단계 실정산액 = (당월 신규 세전 지급액 − 당월 신규 원천징수세액 + 당월 부가가치세) + 위탁 실정산액",
            "net_settle_protected": "비상계 보호분(MMG 보전금 · 비상계 지원금 · 비정기 약정금의 세후 해당액) — 라인 세후액 비례",
            "non_deductible_input_vat": "TX-06 · 07 · 09 지급 VAT(매입세액 불공제 원가 — 계정 구분만)",
        }.get(k, "payee 합계"), ref={"net_settle_amount": "V2 §8.3 9단계 L282",
                                    "net_settle_protected": "V2 L282~283", "non_deductible_input_vat": "TAX.md TX-07"}
                 .get(k, "V2 §8.3 9단계"), provisional=k == "net_settle_protected",
                 note="Q-16" if k == "net_settle_protected" else "")
    if cases:
        ctx.emit(STEP, "matrix_case_id", cases[0] if len(set(cases)) == 1 else "/".join(sorted(set(cases))), c, payee=pid,
                 formula="payee 세무 케이스(라인 케이스가 여럿이면 '/' 연결)", ref="V2 §11.1")
    if t["evidence_types"]:
        ctx.emit(STEP, "evidence_type", " + ".join(t["evidence_types"]), c, payee=pid, formula="증빙(tax_table.json)",
                 ref="TAX.md 1절")
    ch = [x for ln in p.lines for x in (ln.get("correction_channels") or [])]
    if ch:
        ctx.emit(STEP, "correction_channel", ch[0], c, payee=pid, formula="정정 채널(tax_table.json)", ref="V2 §10.4")


def revalidate_offset(ctx, c):
    """6단계 9단계 재검증 — '계산상 현금 가용액'이 회수액보다 작으면 회수액 축소(V2 L228 · L231, Q-13 잠정)."""
    pp = c.prepay
    if not pp or not pp.get("amount"):
        return
    from . import s06_prepay_offset, s08_payee_split
    payee = c.payees.get(pp["payee"])
    if not payee:
        return
    elig = {ln.label for ln in c.lines.values() if ln.eligible > 0}
    elig |= {ln.label for ln in (getattr(c, "carry_offset", None) or {}).values() if ln.eligible > 0}
    cash = sum(ln["split_amount"] - (ln.get("withholding_total") or D(0)) for ln in payee.lines
               if ln["origin"] in ("NEW", "CARRY_PRE_TAX") and ln["line_id"] in elig)
    ctx.emit(STEP, "cash_avail_offset_lines", cash, c, payee=pp["payee"], inputs={"상계액": pp["amount"]},
             formula="상계 적격 라인 계산상 현금 가용액 = Σ(분할액 − 라인 원천세)", code="cash_avail = Σ(split − withholding)",
             ref="V2 §8.3 6단계 L228", provisional=True, note="Q-13")
    if cash >= pp["amount"]:
        return
    ctx.issue("CANON_GAP", f"{c.id} 상계액 {pp['amount']} > 현금 가용액 {cash} — 상계액 축소(잠정 산식)", STEP, c.holder_id,
              "V2 L228 · L231", "Q-13")
    s06_prepay_offset.compute(ctx, c, first=False, cap=max(D(0), cash))
    s08_payee_split.split_contract(ctx, c)
    tax_contract(ctx, c)
    business_all(ctx, holder=c.holder_id)
    for cc in ctx.contracts.values():
        if cc.holder_id == c.holder_id:
            finish_contract(ctx, cc)
