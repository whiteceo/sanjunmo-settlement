"""7단계 LUMPSUM_ADD — 비정기 가산(V2 §8.3 표 L174 · 본문 L237~244, V1 §5.1 · §5.2 · §7.2, SPEC 10절).

비정기 가산금 = 전속계약금 + 일시 · 분할 지원금 + 매절 대금 + 정액 수당 + 종료 일시정산(LUMP_SETTLE).
당월 귀속(target_month = 정산월) · 검수 승인(APPROVED) 항목만. 라인별 소득 구분 유지. 절사 없음.
라인은 0단계에서 만들어 두었다(6단계 상계 적격 판단에 필요).
"""

from .money import D

STEP = "LUMPSUM_ADD"
KIND = {"SIGNING_BONUS": "전속계약금", "SUPPORT_LUMP_SUM": "일시 지원금", "SUPPORT_INSTALLMENT": "분할 지원금",
        "BUYOUT": "매절 대금", "FIXED_FEE": "정액 수당", "LUMP_SETTLE": "종료 일시정산"}


def run(ctx):
    for c in ctx.contracts.values():
        out = c.step_out(STEP)
        rows = []
        total = D(0)
        for ln in c.lines_of("LUMPSUM"):
            ctx.emit(STEP, "lumpsum_line", ln.net, c, line=ln.label, line_key=ln.key(), ref_id=ln.approval_id,
                     inputs={"item_kind": ln.item_kind, "offset_type": ln.offset_type,
                             "income_category": ln.income_category, "income_clause": ln.income_clause},
                     formula=f"승인 비정기 약정금({KIND.get(ln.item_kind, ln.item_kind)}) — 라인별 소득 구분 유지",
                     ref="V2 §8.3 7단계 L239 · L242")
            rows.append({"milestone_id": ln.approval_id, "item_kind": ln.item_kind, "line_key": ln.key(),
                         "amount": ln.net, "payee_id": ln.fixed_payee})
            total += ln.net
        out["lines"] = rows
        out["lumpsum_total"] = ctx.emit(
            STEP, "lumpsum_total", total, c, inputs={"items": len(rows)},
            formula="비정기 가산금 = 전속계약금 + 일시 · 분할 지원금 + 매절 대금 + 정액 수당 + 종료 일시정산(LUMP_SETTLE)",
            code="lumpsum_total = Σ approvals(target_month = 정산월, APPROVED)", ref="V2 §8.3 7단계 L239")
        n11 = sum(ln.net for ln in c.lines_of("1.1"))
        n21 = sum(ln.net for ln in c.lines_of("2.1"))
        s51 = sum(ln.net for ln in c.lines_of("5.1"))
        out["pre_split_supply"] = ctx.emit(
            STEP, "pre_split_supply", n11 + n21 + s51 + total, c,
            inputs={"Σnet_1_1": n11, "Σnet_2_1": n21, "Σconfirmed_amount(5.1)": s51, "lumpsum_total": total},
            formula="분할 전 정산 공급가액(상계 전) = P1.1 순액 + P2.1 순액 + P5.1 확정액 + 비정기 가산금",
            code="pre_split_supply = Σnet_1_1 + Σnet_2_1 + Σconfirmed_5_1 + lumpsum_total",
            ref="V2 §8.3 7단계 L244 · V4 Case 1 L41 · Case 3 L94")
        if any(cb["contract_id"] == c.id for cb in ctx.input["clawbacks"]):
            ctx.emit(STEP, "clawback_deferred", True, c,
                     formula="전속계약금 반환액은 세후 항목 — 7단계에서 차감하지 않고 10단계에서 1회", ref="V2 L243",
                     output=False)
