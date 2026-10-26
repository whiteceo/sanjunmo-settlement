"""8단계 PAYEE_SPLIT — 수취인 분할(V2 §8.3 표 L175 · 본문 L245~259, V1 §4.1~4.3, V2 13.2~13.4, SPEC 11절).

신규분: 라인별 내림(세전액 × split_ratio), 마지막 수취인(split_ratio↓ · payee_id↑) 총액 역산.
원거래 귀속 공제분: 원 결제 시점 분할 비율(snapshot_payee_splits)로 같은 규칙 — 재분할 금지.
비분할: 선급금 상계액(원 권리자) · 이월액(원장 수취인) · P2.2(위탁자 단독 패스스루).
당월 세전 지급액 = 분할액 − 상계액, 과세표준 = 분할액(LOAN · 없음) / 분할액 − 상계액(EARNED), 음수는 보류.
"""

from collections import OrderedDict

from .money import D, floor_won
from .pipeline import month_last, valid_on

STEP = "PAYEE_SPLIT"


def run(ctx):
    for c in ctx.contracts.values():
        split_contract(ctx, c)


def splits_for(ctx, c):
    date = month_last(ctx.month)
    rows = [s for s in ctx.input["payee_splits"] if s["contract_id"] == c.id
            and s.get("rights_holder_id", c.holder_id) == c.holder_id and valid_on(s, date, c.row)]
    if not rows:
        return [{"payee_id": c.holder_id, "split_ratio": D(100)}], True
    return [{"payee_id": s["payee_id"], "split_ratio": D(s["split_ratio"])} for s in rows], False


def split_amount(amount, splits):
    order = sorted(splits, key=lambda s: (-D(s["split_ratio"]), s["payee_id"]))
    out = OrderedDict()
    acc = D(0)
    for i, s in enumerate(order):
        if i < len(order) - 1:
            out[s["payee_id"]] = floor_won(amount * D(s["split_ratio"]) / 100)
            acc += out[s["payee_id"]]
        else:
            out[s["payee_id"]] = amount - acc
    return out, order


def split_contract(ctx, c):
    c.payees.clear()
    out = c.step_out(STEP)
    splits, default = splits_for(ctx, c)
    c.splits = splits
    out["splits_used"] = splits
    ctx.emit(STEP, "splits_used", ", ".join(f"{s['payee_id']}:{s['split_ratio']}" for s in splits), c,
             inputs={"default": default},
             formula="유효 payee_splits(없으면 권리자 단독 100%)", ref="V2 §8.3 8단계 L258")
    lump = sum(ln.net for ln in c.lines_of("LUMPSUM"))
    base = sum(ln.net for ln in c.lines.values() if ln.pipeline_id in ("1.1", "2.1", "5.1")) + lump
    out["payee_split_base"] = ctx.emit(
        STEP, "payee_split_base", base, c, inputs={"Σnet_1_1 + Σnet_2_1 + Σconfirmed(5.1)": base - lump, "lumpsum_total": lump},
        formula="수취인 분할 기준액 = P1.1 순액 + P2.1 순액 + P5.1 확정액 + 7단계 비정기 가산금(상계 · 이월 · 반환 · P2.2 제외, 표시용)",
        code="payee_split_base = Σnet_1_1 + Σnet_2_1 + Σconfirmed_amount + lumpsum_total", ref="V2 §8.3 8단계 L247")
    prepay = c.prepay or {}
    offset_payee = prepay.get("payee")
    ptype = prepay.get("type")
    ctx.payee_holder_seen = getattr(ctx, "payee_holder_seen", set())
    c.payee(c.holder_id)
    for s in splits:
        c.payee(s["payee_id"])
    for ln in c.lines.values():
        if ln.pipeline_id == "2.2":
            consignment_line(ctx, c, ln)
            continue
        if ln.pipeline_id not in ("1.1", "2.1", "5.1", "LUMPSUM"):
            continue
        pieces = OrderedDict()  # payee → 분할액
        if ln.pipeline_id == "1.1":
            new_amt = ln.adjusted if ln.adjusted is not None else ln.new
        elif ln.pipeline_id == "5.1":
            new_amt = getattr(ln, "new_confirmed", ln.new)
        else:
            new_amt = ln.new if ln.pipeline_id == "2.1" else ln.net
        if ln.fixed_payee:
            parts = OrderedDict([(ln.fixed_payee, new_amt)])
            ctx.issue("CANON_GAP", f"{ln.label} 약정 · 승인 원장 수취인 {ln.fixed_payee} 단독 귀속", STEP, c.holder_id,
                      "V1 L288 · L234 · V2 L247", "Q-15")
        else:
            parts, order = split_amount(new_amt, splits)
        for pid, a in parts.items():
            pieces[pid] = pieces.get(pid, D(0)) + a
            ctx.emit(STEP, "split_new", a, c, payee=pid, line=ln.label, line_key=ln.key(),
                     inputs={"라인 신규 세전액": new_amt, "split_ratio": next((s["split_ratio"] for s in splits
                                                                             if s["payee_id"] == pid), None)},
                     formula="라인별 내림(세전액 × split_ratio), 마지막 수취인 총액 역산(split_ratio 내림차순 → payee_id 오름차순)",
                     code="split[p] = floor(line.amount × p.split_ratio/100); split[last] = amount − Σ선행",
                     rounding="ALLOC_LAST_REMAINDER", ref="V2 §8.3 8단계 L248 · §13.3 L578",
                     provisional=bool(ln.fixed_payee), note="Q-15" if ln.fixed_payee else "", output=False)
        comps = ln.deduct_components if ln.pipeline_id != "5.1" else ln.deduct_components
        for comp in comps:
            if ln.pipeline_id != "5.1" and comp["path"] != "UNPAID_REDUCTION":
                continue
            snap = comp["snapshot_payee_splits"] or None
            use = [{"payee_id": s["payee_id"], "split_ratio": D(s["split_ratio"])} for s in snap] if snap else splits
            if not snap and not default:
                ctx.issue("INPUT_MISSING", f"원거래 {comp['ref_id']} 스냅샷 수취인 분할 없음 — 현재 분할 사용", STEP,
                          c.holder_id, "V1 L211")
            parts, _ = split_amount(comp["amount"], use)
            for pid, a in parts.items():
                c.payee(pid)
                pieces[pid] = pieces.get(pid, D(0)) + a
                ctx.emit(STEP, "split_deduct_snapshot", a, c, payee=pid, line=ln.label, ref_id=comp["ref_id"],
                         inputs={"공제 구성요소": comp["amount"], "원거래 분할": [f"{u['payee_id']}:{u['split_ratio']}" for u in use]},
                         formula="원거래 귀속 환불 · 반환 라인은 원 결제 시점 분할 비율로 수취인별 음수 배분(재분할 금지)",
                         code="split_snapshot = alloc(comp.amount, snapshot_payee_splits)", rounding="ALLOC_LAST_REMAINDER",
                         ref="V2 §8.3 8단계 L249 · V1 L211 · V4 D-1", provisional=len(use) > 1,
                         note="Q-14" if len(use) > 1 else "", output=False)
        for pid, amt in pieces.items():
            add_line(ctx, c, ln, pid, amt, offset_payee, ptype)
    carry_lines(ctx, c)


def add_line(ctx, c, ln, pid, amt, offset_payee, ptype):
    p = c.payee(pid)
    off = ln.offset if pid == offset_payee else D(0)
    pre = amt - off
    if ptype == "EARNED":
        tb = amt - off
        tb_code = "taxable_base = split − offset (EARNED)"
    else:
        tb = amt
        tb_code = "taxable_base = split (LOAN · 선급금 없음)"
    pending = None
    if tb < 0:
        pending, tb = tb, D(0)
    prot = D(0)
    if ln.protected:
        prot = max(D(0), pre)
    elif ln.pipeline_id == "1.1" and ln.mmg_subsidy > 0:
        share = ln.mmg_subsidy * amt / ln.adjusted if ln.adjusted else D(0)
        prot = min(max(D(0), floor_won(share)), max(D(0), pre))
    row = {"line_id": ln.label, "line_key": ln.key(), "origin": "NEW", "pipeline_id": ln.pipeline_id,
           "supply_nature": ln.supply_nature, "income_category": ln.income_category, "income_clause": ln.income_clause,
           "tax_threshold_unit_key": ln.tax_threshold_unit_key, "payee_is_author": ln.payee_is_author,
           "split_amount": amt, "offset_amount": off, "pre_tax_payable": pre, "taxable_base": tb,
           "pending_negative_base": pending, "protected_yn": prot > 0, "protected_amount": prot}
    p.lines.append(row)
    kw = dict(payee=pid, line=ln.label, line_key=ln.key())
    ctx.emit(STEP, "split_amount", amt, c, **kw, formula="payee별 분할액(신규분 + 원거래 귀속 공제분)",
             ref="V2 §8.3 8단계 L248~249")
    ctx.emit(STEP, "offset_amount", off, c, **kw, inputs={"offset_payee_id": offset_payee, "라인 상계 배분": ln.offset},
             formula="선급금 상계액은 원 권리자 단일 수취인 귀속(비분할)", ref="V2 L234 · V2 §13.4 L589")
    ctx.emit(STEP, "pre_tax_payable", pre, c, **kw, inputs={"분할액": amt, "상계액": off},
             formula="당월 세전 지급액 = 분할액 − 상계액", code="pre_tax_payable = split − offset", ref="V2 §8.3 8단계 L251")
    ctx.emit(STEP, "taxable_base", tb, c, **kw, inputs={"분할액": amt, "상계액": off, "prepayment_tax_type": ptype},
             formula="대여금(LOAN): 과세표준 = 분할액 / 소득 선지급(EARNED): 과세표준 = 분할액 − 상계액 / 음수는 보류",
             code=tb_code, ref="V2 §8.3 8단계 L253~254 · 9단계 L281")
    if pending is not None:
        ctx.emit(STEP, "pending_negative_base", pending, c, **kw,
                 formula="음수 과세표준은 원천세 미산출 · 보류(pending_negative_base)", ref="V2 L281")
    if prot:
        ctx.emit(STEP, "protected_amount", prot, c, **kw, inputs={"mmg_subsidy": ln.mmg_subsidy, "protected": ln.protected},
                 formula="선급금 상계 비대상 보호분(MMG 보전금 몫 · NON_OFFSET 지원금 · 비정기 약정금)",
                 ref="V2 L282~283 · SPEC 12.1", provisional=ln.pipeline_id == "1.1", note="Q-16" if ln.pipeline_id == "1.1" else "")


def consignment_line(ctx, c, ln):
    pid = c.holder_id
    p = c.payee(pid)
    row = {"line_id": ln.label, "line_key": ln.key(), "origin": "CONSIGNMENT", "pipeline_id": "2.2",
           "supply_nature": "BOOK_GOODS", "income_category": None, "income_clause": None, "tax_threshold_unit_key": None,
           "split_amount": ln.net, "offset_amount": D(0), "pre_tax_payable": ln.net, "taxable_base": None,
           "pending_negative_base": None, "protected_yn": False, "protected_amount": D(0)}
    p.lines.append(row)
    ctx.emit(STEP, "consignment_net", ln.net, c, payee=pid, line="2.2",
             formula="P2.2는 분할하지 않고 위탁자 단독 수취인에게 패스스루(과세표준 미생성)",
             ref="V2 §8.3 8단계 L250 · L256 · V1 L170")
    ctx.emit(STEP, "consignor_sole", True, c, payee=pid, line="2.2", formula="위탁 분할 금지(복수 위탁자는 계약 분리)",
             ref="V1 L170")


def carry_lines(ctx, c):
    for r in c.carry["pre_pos"] + c.carry["pre_neg"]:
        pid = r["payee_id"]
        p = c.payee(pid)
        amt = r["carryover_amount"]
        neg = amt < 0
        row = {"line_id": f"CARRY:{r.get('ledger_id')}", "ledger_id": r.get("ledger_id"),
               "line_key": {"contract_id": c.id, "pipeline_id": r.get("pipeline_id"),
                            "income_category": r.get("income_category"), "income_clause": r.get("income_clause"),
                            "tax_threshold_unit_key": r.get("tax_threshold_unit_key")},
               "origin": "CARRY_PRE_TAX", "pipeline_id": str(r.get("pipeline_id")),
               "supply_nature": {"1.1": "LECTURE_RS", "2.1": "ROYALTY", "5.1": "SUPPORT_RS"}.get(str(r.get("pipeline_id")),
                                                                                                "NONRECURRING"),
               "income_category": r.get("income_category"), "income_clause": r.get("income_clause"),
               "tax_threshold_unit_key": r.get("tax_threshold_unit_key"), "split_amount": amt, "offset_amount": D(0),
               "pre_tax_payable": amt, "taxable_base": None if neg else amt,
               "pending_negative_base": amt if neg else None, "protected_yn": False, "protected_amount": D(0),
               "first_payable_confirmed_month": r.get("first_payable_confirmed_month"),
               "first_occurred_month": r.get("first_occurred_month")}
        p.lines.append(row)
        ctx.emit(STEP, "carry_pre_tax_line", amt, c, payee=pid, line=row["line_id"], ref_id=r.get("ledger_id"),
                 formula=("원귀속 세전 이월 세전 지급액 = 원귀속 세전 미지급 소득 기초금액(현재 분할 비율 미적용)" if not neg
                          else "세전 미확정 조정액 — 확정 전 과세표준 합산 금지(pending_negative_base)"),
                 ref="V2 §8.3 8단계 L257 · V4 D-3")
