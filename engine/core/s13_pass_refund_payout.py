"""13 PASS_REFUND_PAYOUT — 합격환급금 수강생 지급(권리자 정산 1~11단계 밖, 통합 설계서 S6 합격환급 L438~446).

환급 기준 모수 = 패키지 실결제액 − 포함 교재 실결제액(최대 10% 기본할인가) − 배송비(L444).
기타소득 원천징수(S-02 · 2026-10-27): 필요경비 의제 없음 → 기타소득금액 = 환급금, 건별 5만 원 이하면 과세최저한 0원
(소득세법 제84조), 소득세 = 내림(× 20%) → 지방소득세 = 내림(소득세 × 10%). 주민등록번호는 항상 받고(번호만 · 암호화),
과세최저한 이하 건은 지급명세서 제출 면제(시행령 제214조 ① 3호 · 시행규칙 제97조).
환급 판정 진도율은 결제 시점 주문 라인에 박제한 값(S-14 — 판매 후 기준 변경 소급 없음).
권리자 정산서의 옵션 B · C 공제는 4단계(DEDUCT)에서 따로 처리한다.
"""

from .money import D, floor_won

STEP = "PASS_REFUND_PAYOUT"
REF = "통합 설계서 S6 L438~446 · S-02 · S-14(2026-10-27) · 소득세법 제21조 · 제84조 · 제164조"


def run(ctx):
    rows = []
    for r in ctx.input["pass_refund_payouts"]:
        rows.append(one(ctx, r))
    ctx.pass_refund_payouts = rows


def one(ctx, r):
    pid, sid = r["pass_refund_id"], r.get("student_id")
    kw = dict(holder=None, contract=None, payee=sid, line=pid, ref_id=r.get("order_id"))
    pkg, book, ship = D(r.get("package_paid_amount")), D(r.get("book_paid_amount")), D(r.get("shipping_fee"))
    base = ctx.emit(STEP, "refund_base", pkg - book - ship, **kw,
                    inputs={"패키지 실결제액": pkg, "포함 교재 실결제액": book, "배송비": ship},
                    formula="환급 기준 모수 = 패키지 실결제액 − 포함 교재 실결제액(최대 10% 기본할인가) − 배송비",
                    code="refund_base = package_paid − book_paid − shipping", ref="통합 설계서 S6 L444")
    snap = r.get("target_progress_rate_snapshot")
    progress = r.get("progress_rate")
    eligible = None
    if snap is not None and progress is not None:
        eligible = D(progress) >= D(snap)
        ctx.emit(STEP, "progress_eligible", eligible, **kw,
                 inputs={"진도율": progress, "결제 시점 목표 진도율(박제)": snap,
                         "현재 상품 설정(참고, 판정에 쓰지 않음)": r.get("current_target_progress_rate")},
                 formula="환급 판정은 결제 승인 시점에 주문 라인에 박제한 목표 진도율 기준 — 판매 후 설정 변경은 소급하지 않음",
                 code="eligible = progress_rate >= target_progress_rate_snapshot",
                 ref="통합 설계서 L251 · L438 · S-14(2026-10-27)")
    exempt = base <= D(ctx.p("other_income_min_tax_amount"))
    ctx.emit(STEP, "threshold_exempt_yn", exempt, **kw,
             inputs={"기타소득금액(필요경비 의제 없음)": base, "과세최저한": ctx.p("other_income_min_tax_amount")},
             formula="기타소득금액(= 환급금, 필요경비 의제 없음) 건별 5만 원 이하면 과세최저한 비과세",
             ref="통합 설계서 L444 · 소득세법 제84조")
    if exempt:
        it = lt = D(0)
        it_raw = lt_raw = None
    else:
        it_raw = base * D("0.20")
        it = floor_won(it_raw)
        lt_raw = it * D(str(ctx.p("local_income_tax_rate")))
        lt = floor_won(lt_raw)
    ctx.emit(STEP, "income_tax", it, **kw, inputs={"기타소득금액": base},
             formula="소득세 = 내림(기타소득금액 × 20%)", code="floor(base × 0.20)", before=it_raw,
             rounding="FLOOR_WON" if it_raw is not None else "NONE", ref=REF)
    ctx.emit(STEP, "local_income_tax", lt, **kw, inputs={"소득세": it},
             formula="지방소득세 = 내림(소득세 × 10%)(합산 22% 한 번에 곱하지 않음)", code="floor(income_tax × 0.10)",
             before=lt_raw, rounding="FLOOR_WON" if lt_raw is not None else "NONE", ref=REF)
    net = ctx.emit(STEP, "net_payout", base - it - lt, **kw, inputs={"환급금": base, "원천세": it + lt},
                   formula="세후 실지급액 = 환급금 − 기타소득세(소득세 + 지방소득세)", ref=REF)
    ctx.emit(STEP, "rrn_required", True, **kw, formula="주민등록번호는 신청 때 항상 받는다(번호만 · 암호화 보관)",
             ref="통합 설계서 L440 · S-02(2026-10-27)")
    stmt = ctx.emit(STEP, "payment_statement_required", not exempt, **kw,
                    formula="기타소득 지급명세서 제출 — 과세최저한으로 과세되지 않은 건은 면제",
                    ref="소득세법 제164조 · 시행령 제214조 ① 3호 · 시행규칙 제97조 · S-02")
    ok_rrn = bool(r.get("rrn_entered")) and bool(r.get("rrn_matched", True))
    status = "APPROVABLE" if ok_rrn and eligible is not False else "SUPPLEMENT_REQUEST" if not ok_rrn else "REJECT"
    ctx.emit(STEP, "review_status", status, **kw,
             inputs={"주민번호 입력": r.get("rrn_entered"), "본인인증 대조": r.get("rrn_matched"), "진도율 충족": eligible},
             formula="주민등록번호 미입력 · 대조 불일치는 [보완 요청], 진도율 기준 미달은 [반려], 그 밖은 승인 가능",
             ref="통합 설계서 L440~441 · S-02 · S-03 · S-21")
    return {"pass_refund_id": pid, "student_id": sid, "refund_base": base, "progress_eligible": eligible,
            "threshold_exempt_yn": exempt, "income_tax": it, "local_income_tax": lt, "withholding_total": it + lt,
            "net_payout": net, "rrn_required": True, "payment_statement_required": stmt, "review_status": status}
