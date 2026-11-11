"""3단계 MMG_ADJ — 월 보장액 보정(V2 §8.3 표 L170 · 본문 L192~195, V1 §5.3 · §15.2, SPEC 6절).

P1.1 순수 신규 R/S < MMG 이면 보정 후 P1.1 = MMG, MMG 보전금 = MMG − 순수 신규 R/S(mmg_subsidy_ledger 격리).
판정 모수에서 환불 · 옵션 B/C · 이월 · P5.1 제외. 차감은 4단계. 절사 없음.
"""

import calendar
from datetime import date

from .money import D, floor_won

STEP = "MMG_ADJ"


def _d(s):
    return date.fromisoformat(str(s)[:10]) if s else None


def prorate(ctx, c, mmg):
    """첫 달 · 끝 달 일할(V1 §5.3 · V2 §8.3 3단계, v4.0.38): 내림(MMG × 그 달 계약 일수 ÷ 그 달 일수). → (금액, 일수, 그 달 일수, 부분 여부)"""
    y, m = int(ctx.month[:4]), int(ctx.month[5:7])
    dim = calendar.monthrange(y, m)[1]
    first, last = date(y, m, 1), date(y, m, dim)
    s = _d(c.row.get("start_date")) or first
    ends = [x for x in (_d(c.row.get("termination_date")), _d(c.row.get("current_end_date"))) if x]
    e = min(ends) if ends else last
    lo, hi = max(s, first), min(e, last)
    days = (hi - lo).days + 1 if hi >= lo else 0
    # 승계 계약이 유효한 날은 앞 계약의 보장에서 뺀다 — 승계 계약이 먼저 끝나면 다음 날부터 다시 선다
    # (작성 중 · 시작 전 해지된 승계 계약은 빼지 않음, v4.0.44 · v4.0.46)
    for o in ctx.contracts.values():
        if o.id == c.id or o.holder_id != c.holder_id or o.row.get("contract_status") == "DRAFT":
            continue
        os_ = _d(o.row.get("start_date"))
        oends = [x for x in (_d(o.row.get("termination_date")), _d(o.row.get("current_end_date"))) if x]
        oe = min(oends) if oends else last
        if not os_ or os_ <= s or oe < os_:
            continue
        a, b = max(os_, lo), min(oe, hi)
        if b >= a:
            days -= (b - a).days + 1
    if days >= dim:
        return mmg, dim, dim, False
    return floor_won(mmg * D(days) / D(dim)), days, dim, True


def run(ctx):
    prorated = {}
    for c in ctx.contracts.values():
        rl = ctx.rate(c.id, "BASIC", f"{ctx.month}-01", pipeline_id="1.1") or ctx.rate(c.id, "BASIC", None, "1.1")
        full = D((rl or {}).get("mmg_amount"))
        if full > 0:
            prorated[c.id] = prorate(ctx, c, full)
    # 달 중간 재계약 달: 같은 권리자의 일할 계약이 둘 이상이면 일할 보장액 합 · R/S 합으로 한 번 판정, 보전금은 일할액이 큰 계약(v4.0.41)
    groups = {}
    for c in ctx.contracts.values():
        if c.id in prorated and prorated[c.id][3]:
            groups.setdefault(c.holder_id, []).append(c)
    merged = {}
    for hid, cs in groups.items():
        if len(cs) > 1:
            big = max(cs, key=lambda x: (prorated[x.id][0], -(_d(x.row.get("start_date")) or date.min).toordinal(), x.id))  # 같으면 앞 계약(v4.0.44)
            tot_mmg = sum(prorated[x.id][0] for x in cs)
            tot_basis = sum(sum(ln.new for ln in x.lines_of("1.1")) for x in cs)
            for x in cs:
                merged[x.id] = (big.id, tot_mmg, tot_basis)
    for c in ctx.contracts.values():
        out = c.step_out(STEP)
        lines = c.lines_of("1.1")
        mmg, days, dim, partial = prorated.get(c.id, (D(0), 0, 0, False))
        if partial:
            ctx.emit(STEP, "mmg_prorated", mmg, c, inputs={"그 달 계약 일수": days, "그 달 일수": dim},
                     formula="첫 달 · 끝 달 월 보장액 = 내림(월 보장액 × 그 달 계약 일수 ÷ 그 달 일수)", ref="V2 §8.3 3단계 · V1 §5.3 (v4.0.38)")
        if c.id in merged:
            big, tot_mmg, tot_basis = merged[c.id]
            sub = max(D(0), tot_mmg - tot_basis) if c.id == big else D(0)
            ctx.emit(STEP, "mmg_recontract_merged", sub, c, inputs={"일할 보장액 합": tot_mmg, "R/S 합": tot_basis, "보전 원장 계약": big},
                     formula="재계약 달: 두 계약 일할 보장액 합 vs 권리자 R/S 합 1회 판정, 보전금은 일할액이 큰 계약", ref="V2 §8.3 3단계 (v4.0.41)")
            mmg = (sum(ln.new for ln in lines) + sub) if sub > 0 else D(0)
        applicable = bool(lines) or mmg > 0
        out["applicable"] = ctx.emit(STEP, "applicable", applicable, c, inputs={"P1.1 lines": len(lines), "mmg": mmg},
                                     formula="MMG는 온라인 강좌 특약 — Pipeline 1.1에만 적용", ref="V2 §8.3 3단계 L193")
        if not applicable:
            continue
        basis = sum(ln.new for ln in lines)
        if c.id in merged and mmg == 0:
            adjusted, subsidy = basis, D(0)
        elif mmg > 0 and basis < mmg:
            adjusted, subsidy = mmg, mmg - basis
        else:
            adjusted, subsidy = basis, D(0)
        if lines and len(lines) > 1:
            ctx.issue("CANON_GAP", f"{c.id} P1.1 라인 {len(lines)}개 — 보전금 귀속 라인 정본 없음(금액 최대 라인)",
                      STEP, c.holder_id, "V2 L192~193", "Q-06")
        target = max(lines, key=lambda x: (x.new, x.label)) if lines else None
        if target is None and subsidy > 0:  # 매출 0원 계약도 보장 대상이면 P1.1 라인을 만든다
            from .s00_pipeline_in import line_1_1
            target = line_1_1(ctx, c)
        if target is not None:
            target.mmg_subsidy = subsidy
        c.mmg_subsidy = subsidy
        flag = subsidy > 0 and any(p.get("option") in ("B", "C") for p in ctx.input["pass_refund_deductions"]
                                   if p.get("contract_id") == c.id)
        out["mmg_amount"] = mmg
        out["adjusted_1_1"] = ctx.emit(
            STEP, "adjusted_1_1", adjusted, c, line="1.1",
            inputs={"P1.1 순수 신규 R/S": basis, "월 보장액(MMG)": mmg},
            formula="P1.1 순수 신규 R/S < MMG 시 보정 후 P1.1 = MMG",
            code="adjusted_1_1 = mmg if mmg > 0 and mmg_basis_1_1 < mmg else mmg_basis_1_1",
            ref="V2 §8.3 3단계 L193")
        out["mmg_subsidy"] = ctx.emit(
            STEP, "mmg_subsidy", subsidy, c, line="1.1", inputs={"MMG": mmg, "P1.1 순수 신규 R/S": basis},
            formula="MMG 보전금 = MMG − P1.1 순수 신규 R/S(mmg_subsidy_ledger 격리)",
            code="mmg_subsidy = mmg − mmg_basis_1_1", ref="V2 §8.3 3단계 L193",
            provisional=len(lines) > 1, note="Q-06" if len(lines) > 1 else "")
        out["mmg_promo_overlap_flag"] = ctx.emit(
            STEP, "mmg_promo_overlap_flag", flag, c, inputs={"mmg_subsidy": subsidy},
            formula="옵션 B 및 옵션 C 차감이 동시 발생하면 재무 확인 플래그(연산 차단 없음)", ref="V2 L194 · V1 L617")
        if subsidy > 0:
            ctx.ledgers["mmg_subsidy_ledger"].append({"contract_id": c.id, "target_month": ctx.month,
                                                       "mmg_subsidy": subsidy})
        cap = c.row.get("mmg_annual_cap")
        if cap is not None and subsidy > D(cap):
            ctx.warn("MMG_ANNUAL_CAP", f"{c.id} MMG 보전금 {subsidy} > 연간 상한 {cap} — 재무 승인 대상", "V1 L339")
            ctx.issue("CANON_GAP", "MMG 연간 상한 초과분 처리 정본 없음 — 금액 그대로", STEP, c.holder_id, "V1 L339", "Q-05")
        for ln in c.lines_of("1.1"):
            ln.adjusted = ln.new + (subsidy if ln is target else D(0))
