"""금액 · 절사 도구(정산 02권 13장, SPEC 0절 의사코드 규약).

- 계산은 모두 Decimal(float 금지).
- floor(x) = 원 단위 내림, 음수는 절대값 내림 후 부호 복원(V2 §13.1 L569) = ROUND_DOWN(0 방향).
- q4(x) = 소수 4자리 보존(DECIMAL(18,4), V2 §13.1 L565). 4자리 밖은 버림(SPEC Q-01 잠정).
- alloc_last_remainder = 13.2 총액 역산: 선행 항목 floor, 마지막 항목 = 총액 − Σ선행(V2 §13.2 L573).
"""

from decimal import ROUND_DOWN, Decimal

Q4 = Decimal("0.0001")
Q0 = Decimal("1")
ZERO = Decimal(0)
HUNDRED = Decimal(100)


def D(x):
    """입력값 → Decimal. None은 0. float은 repr을 거쳐 받는다."""
    if x is None or x == "":
        return Decimal(0)
    if isinstance(x, Decimal):
        return x
    if isinstance(x, bool):
        return Decimal(int(x))
    if isinstance(x, float):
        return Decimal(repr(x))
    return Decimal(str(x))


def Dn(x):
    """None은 None으로 두는 Decimal 변환."""
    return None if x is None or x == "" else D(x)


def q4(x):
    """중간값 소수 4자리 보존. 넘는 자리는 버림(SPEC Q-01 잠정)."""
    return D(x).quantize(Q4, rounding=ROUND_DOWN)


def floor_won(x):
    """원 단위 내림 — 음수는 절대값 내림 후 부호 복원(V2 §13.1 L569)."""
    return D(x).quantize(Q0, rounding=ROUND_DOWN)


def pct(x):
    """백분율 수치(50 = 50%) → 비율."""
    return D(x) / HUNDRED


def alloc_last_remainder(total, weights):
    """13.2 총액 역산. weights는 이미 13.3 정렬된 [가중치]. 반환: [배분액]."""
    total = D(total)
    if not weights:
        return []
    den = sum(D(w) for w in weights)
    out = []
    for w in weights[:-1]:
        out.append(floor_won(total * D(w) / den) if den else Decimal(0))
    out.append(total - sum(out))
    return out


def to_json(x):
    """Decimal → JSON 값. 정수면 int, 소수면 문자열(정밀도 보존)."""
    if isinstance(x, Decimal):
        if x == x.to_integral_value():
            return int(x)
        return format(x.normalize(), "f")
    if isinstance(x, dict):
        return {k: to_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_json(v) for v in x]
    return x


def eq(a, b, tol=0):
    """두 금액이 허용 오차 안에서 같은가(대조 · 테스트용)."""
    if a is None or b is None:
        return a is None and b is None
    try:
        return abs(D(a) - D(b)) <= D(tol)
    except Exception:
        return str(a) == str(b)
