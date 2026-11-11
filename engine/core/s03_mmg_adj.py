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


def prorate(ctx, c):
    """첫 달 · 끝 달 일할(V1 §5.3 · V2 §8.3 3단계, v4.0.38): 내림(MMG × 그 달 계약 일수 ÷ 그 달 일수). → (금액, 일수, 그 달 일수, 부분 여부)"""
    y, m = int(ctx.month[:4]), int(ctx.month[5:7])
    dim = calendar.monthrange(y, m)[1]
    first, last = date(y, m, 1), date(y, m, dim)
    s = _d(c.row.get("start_date")) or first
    ends = [x for x in (_d(c.row.get("termination_date")), _d(c.row.get("current_end_date"))) if x]
    e = min(ends) if ends else last
    lo, hi = max(s, first), min(e, last)
    # 승계 · 재계약은 등록된 계약 기간만 본다 — 계약 사이 연결을 추론하지 않음(V2 §8.3 3단계, v4.0.48)
    # 달 중간에 보장액(요율 라인)이 바뀌면 구간별 보장액 × 날수를 더한 뒤 그 달 일수로 나눠 한 번 내림(v4.0.51)
    tot, days, amts, d = D(0), 0, set(), lo
    while d <= hi:
        rl = ctx.rate(c.id, "BASIC", d.isoformat(), pipeline_id="1.1")
        a = D((rl or {}).get("mmg_amount"))
        if a > 0:
            tot += a
            days += 1
            amts.add(a)
        d = date.fromordinal(d.toordinal() + 1)
    if days == 0:
        return None
    if days >= dim and len(amts) == 1:
        return amts.pop(), dim, dim, False
    return floor_won(tot / D(dim)), days, dim, True


def run(ctx):
    prorated = {}
    for c in ctx.contracts.values():
        r = prorate(ctx, c)
        if r:
            prorated[c.id] = r
    # 달 중간 재계약 · 승계 달도 계약마다 자기 일할 보장액과 자기 R/S만 비교(계약주의, V2 §8.3 3단계, v4.0.49)
    for c in ctx.contracts.values():
        out = c.step_out(STEP)
        lines = c.lines_of("1.1")
        mmg, days, dim, partial = prorated.get(c.id, (D(0), 0, 0, False))
        if partial:
            ctx.emit(STEP, "mmg_prorated", mmg, c, inputs={"그 달 계약 일수": days, "그 달 일수": dim},
                     formula="첫 달 · 끝 달 월 보장액 = 내림(월 보장액 × 그 달 계약 일수 ÷ 그 달 일수)", ref="V2 §8.3 3단계 · V1 §5.3 (v4.0.38)")
        applicable = bool(lines) or mmg > 0
        out["applicable"] = ctx.emit(STEP, "applicable", applicable, c, inputs={"P1.1 lines": len(lines), "mmg": mmg},
                                     formula="MMG는 온라인 강좌 특약 — Pipeline 1.1에만 적용", ref="V2 §8.3 3단계 L193")
        if not applicable:
            continue
        basis = sum(ln.new for ln in lines)
        if mmg > 0 and basis < mmg:
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
