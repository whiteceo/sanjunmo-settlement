"""전월 정산 조정 라인(마감 후 정정) — 차월 정산서 반영(V2 §10.1 L353 · §10.2).

인입 위치(2026-10-27 white 결정, SPEC Q-23 해소): 세금 계산 직전.
  PRE_TAX(세전, 원천징수 미성립분 정정) · 위탁(2.2) → 8단계 뒤 비분할 라인(origin = ADJUSTMENT) → 9단계에서 원천세 · VAT
  POST_TAX(세후, 원천징수 성립분) → 10단계: 양수는 지급채무에 가산, 음수는 반환채권(청구 음수 항, 자동 상계 없음 — Q-19와 같음)
adjustment_mode = "hold"이면 예전처럼 계산에 넣지 않고 pending_adjustments로만 낸다.
"""

PIPE_SUPPLY = {"1.1": "LECTURE_RS", "2.1": "ROYALTY", "5.1": "SUPPORT_RS", "2.2": "BOOK_GOODS", "LUMPSUM": "NONRECURRING"}


def mode(ctx):
    """apply(기본) · provisional(예전 잠정안 이름, apply와 같음) → 반영, hold → 보류."""
    return "hold" if ctx.input.get("adjustment_mode") == "hold" else "apply"


def month_adjustments(ctx):
    """이 정산월에 반영할 조정(입력 adjustments의 applied_month = 정산월 + 보정 전표 자동 조정)."""
    rows = [a for a in ctx.input["adjustments"] if str(a.get("applied_month") or ctx.month)[:7] == ctx.month]
    return rows + list(getattr(ctx, "auto_adjustments", []))


def account(a):
    if str(a.get("pipeline_id")) == "2.2" or a.get("consignment_balance_yn"):
        return "CONSIGNMENT"
    return a.get("account_type") or "PRE_TAX"
