"""2단계 ACCRUAL — 순 발생액 산출(V2 §8.3 표 L169 · 본문 L183~191, SPEC 5절).

당월 신규 발생액만 집계(환불 · 프로모션 미반영). 이월 합산값은 '이월 포함 세전 처리잔액'으로 따로 표기한다.
절사: 0단계 파이프라인이 라인별 1회 절사를 마친 값 — 추가 절사 없음.
"""

from .money import D

STEP = "ACCRUAL"
NAMES = {"1.1": "온라인 강좌 수익배분(Pipeline 1.1) 신규 R/S = 당월 발생 R/S 합계",
         "2.1": "자사 발행 도서 인세(Pipeline 2.1) 신규 인세액 = 당월 확정 인세액",
         "2.2": "위탁 도서 판매대금 정산(Pipeline 2.2) 신규 위탁 정산 입력액(NET_DEDUCT/GROSS_SETTLE 분기)",
         "5.1": "매출연동 개발지원금(Pipeline 5.1) 신규 지원금액(status = ACTIVE 약정 한정)"}


def run(ctx):
    for c in ctx.contracts.values():
        out = c.step_out(STEP)
        new_lines = []
        total = D(0)
        for ln in c.lines.values():
            if ln.pipeline_id not in NAMES:
                continue
            ctx.emit(STEP, "new_amount", ln.new, c, line=ln.label, line_key=ln.key(), agreement=ln.agreement_id,
                     inputs={"pipeline_id": ln.pipeline_id}, formula=NAMES[ln.pipeline_id],
                     code=f"new_{ln.pipeline_id.replace('.', '_')}[line]", ref="V2 §8.3 2단계 L185~188")
            new_lines.append({"line_key": ln.key(), "amount": ln.new})
            total += ln.new
        pre = sum(r["carryover_amount"] for r in c.carry["pre_pos"] + c.carry["pre_neg"])
        out["new_lines"] = new_lines
        ctx.emit(STEP, "pipeline_inflow", bool(new_lines), c, inputs={"lines": len(new_lines)},
                 formula="권리자 지급 엔진 인입 라인이 있는가(P2.3 · 비인입 도서 제외)", ref="V2 §8.3 1단계 L153~155")
        out["accrual_total"] = ctx.emit(
            STEP, "accrual_total", total, c, inputs={"lines": len(new_lines)},
            formula="당월 신규 세전 발생액 = P1.1 + P2.1 + P2.2 + P5.1", code="accrual_total = Σ new lines",
            ref="V2 §8.3 2단계 L189")
        out["pre_tax_balance_incl_carry"] = ctx.emit(
            STEP, "pre_tax_balance_incl_carry", total + pre, c, inputs={"당월 신규 세전 발생액": total, "세전 이월액": pre},
            formula="이월 포함 세전 처리잔액 = 당월 신규 세전 발생액 + 1단계 세전 이월액(표시 전용)",
            code="pre_tax_balance_incl_carry = accrual_total + Σcarry_pre_tax", ref="V2 §8.3 2단계 L190")
        mmg_basis = sum(ln.new for ln in c.lines_of("1.1"))
        out["mmg_basis_1_1"] = ctx.emit(
            STEP, "mmg_basis_1_1", mmg_basis, c, inputs={"P1.1 lines": len(c.lines_of("1.1"))},
            formula="MMG 판정용 순수 신규 수익 배분(R/S, 이월액 및 Pipeline 5.1 제외)", code="mmg_basis_1_1 = Σnew_1_1",
            ref="V2 §8.3 2단계 L191")
        own = [o for o in ctx.own_holder.values() if o["contract"] is c]
        if own:
            out["own_holder_output"] = ctx.emit(
                STEP, "own_holder_output", sum(o["distributable"] for o in own), c,
                inputs={"agreements": len(own)}, formula="자사 권리자 산출액(재원 한도 산정에만 사용, 발생액 아님)",
                ref="V2 §8.3 2단계 L188 · L159")
        if c.consignment:
            cs = c.consignment
            out["consignment"] = {k: cs[k] for k in ("monthly_sales", "net_before_fee_vat", "fee_supply",
                                                     "consignment_input")}
