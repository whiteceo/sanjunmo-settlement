"""1단계 CARRY_IN — 전월 이월 승계(V2 §8.3 표 L168 · 본문 L180~182, SPEC 4절).

미소멸(extinguished_yn = false) · 예약 없음(payout_reservation_status = NONE) 행을 1회만 조회해
PRE_TAX(+/−) · POST_TAX(+/−) · 위탁 전용 잔액으로 분리 전달한다. 재분할 · 재투입 금지, 절사 없음.
"""

from .money import D

STEP = "CARRY_IN"


def run(ctx):
    for r in ctx.input["carryover_ledger"]:
        c = ctx.contract(r["contract_id"])
        if not c:
            continue
        if r.get("extinguished_yn") or (r.get("payout_reservation_status") or "NONE") != "NONE":
            continue
        amt = D(r["carryover_amount"])
        row = dict(r, carryover_amount=amt, payee_id=r.get("payee_id") or r.get("rights_holder_id") or c.holder_id)
        if r.get("consignment_balance_yn"):
            c.carry["cons"] += amt
            c.carry["cons_rows"].append(row)
            kind = "consignment_balance"
        elif r.get("account_type") == "PRE_TAX":
            # 세전 0원 + 이월 부가세 행은 지급 대기(양수) 쪽 — 지급하는 달에 부가세를 함께 지급(v4.0.71 보완)
            pos = amt > 0 or (amt == 0 and D((r.get("components") or {}).get("carry_vat") or 0) > 0)
            kind = "carry_pre_tax_pos" if pos else "carry_pre_tax_neg"
            c.carry["pre_pos" if pos else "pre_neg"].append(row)
        elif r.get("account_type") == "POST_TAX":
            kind = "carry_post_tax_pos" if amt > 0 else "carry_post_tax_neg"
            c.carry["post_pos" if amt > 0 else "post_neg"].append(row)
        else:
            ctx.issue("INPUT_MISSING", f"이월 행 {r.get('ledger_id')} 계정 구분 없음", STEP, c.holder_id, "V1 §7.4 L580")
            continue
        ctx.emit(STEP, kind, amt, c, payee=row["payee_id"], line=str(r.get("pipeline_id") or ""),
                 ref_id=r.get("ledger_id"),
                 inputs={"account_type": r.get("account_type"), "consignment_balance_yn": r.get("consignment_balance_yn"),
                         "origin_month": r.get("origin_month")},
                 formula="확정 귀속 잔액을 PRE_TAX(+/−) · POST_TAX(+/−) · 위탁 전용 잔액으로 분리하여 전달(재분할 · 재투입 금지)",
                 code="rows = carryover_ledger.filter(extinguished_yn == false, payout_reservation_status == NONE)",
                 ref="V2 §8.3 1단계 L180~181", output=False)
    for c in ctx.contracts.values():
        k = c.carry
        out = c.step_out(STEP)
        out["carry_pre_tax_pos"] = list(k["pre_pos"])  # 4단계 직접 감액이 이월 행을 바꿔도 1단계 결과는 입력 그대로(v4.0.81)
        out["carry_pre_tax_neg"] = k["pre_neg"]
        out["carry_post_tax_pos"] = k["post_pos"]
        out["carry_post_tax_neg"] = k["post_neg"]
        out["consignment_balance"] = ctx.emit(STEP, "consignment_balance", k["cons"], c,
                                              inputs={"rows": len(k["cons_rows"])},
                                              formula="위탁 전용 잔액(동일 위탁 계약의 4단계 P2.2 상쇄 전용)",
                                              ref="V2 §8.3 1단계 L182 · V1 §7.4")
        total = sum(r["carryover_amount"] for key in ("pre_pos", "pre_neg", "post_pos", "post_neg")
                    for r in k[key]) + k["cons"]
        out["carry_total"] = ctx.emit(STEP, "carry_total", total, c,
                                      inputs={"PRE_TAX+": sum(r["carryover_amount"] for r in k["pre_pos"]),
                                              "PRE_TAX−": sum(r["carryover_amount"] for r in k["pre_neg"]),
                                              "POST_TAX+": sum(r["carryover_amount"] for r in k["post_pos"]),
                                              "POST_TAX−": sum(r["carryover_amount"] for r in k["post_neg"]),
                                              "위탁 전용": k["cons"]},
                                      formula="이월 구분별 전달 배열 합계(표시용)", code="Σ carry rows",
                                      ref="V2 §8.3 1단계 L168")
