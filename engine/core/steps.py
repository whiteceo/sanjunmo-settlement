"""단계 목록(단계 번호 · 스텝 코드 · 이름 · 정본 근거). SPEC.md 2절 · output.schema.json #step_code 기준.

0 PIPELINE_IN(상위 인입)과 12 CLOSE_CHECK(마감 검증)는 표시 · 추적용 앞뒤 단계다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    no: int
    code: str
    name: str
    ref: str  # 정본 근거(SPEC 표기)
    module: str  # engine.core 아래 단계 모듈 이름


STEPS = [
    Step(0, "PIPELINE_IN", "상위 인입 파이프라인", "V2 §8.3 1단계 L129~160 · SPEC 3절", "s00_pipeline_in"),
    Step(1, "CARRY_IN", "전월 이월 승계", "V2 §8.3 1단계 L168 · L180~182 · SPEC 4절", "s01_carry_in"),
    Step(2, "ACCRUAL", "순 발생액 산출", "V2 §8.3 2단계 L169 · L183~191 · SPEC 5절", "s02_accrual"),
    Step(3, "MMG_ADJ", "월 보장액 보정", "V2 §8.3 3단계 L170 · L192~195 · SPEC 6절", "s03_mmg_adj"),
    Step(4, "DEDUCT", "환불 및 프로모션 공제", "V2 §8.3 4단계 L171 · L196~203 · SPEC 7절", "s04_deduct"),
    Step(5, "SUPPORT_CAP", "지원금 한도 · 순누계", "V2 §8.3 5단계 L172 · L204~214 · SPEC 8절", "s05_support_cap"),
    Step(6, "PREPAY_OFFSET", "선급금 상계", "V2 §8.3 6단계 L173 · L215~236 · SPEC 9절", "s06_prepay_offset"),
    Step(7, "LUMPSUM_ADD", "비정기 가산", "V2 §8.3 7단계 L174 · L237~244 · SPEC 10절", "s07_lumpsum_add"),
    Step(8, "PAYEE_SPLIT", "수취인 분할", "V2 §8.3 8단계 L175 · L245~259 · SPEC 11절", "s08_payee_split"),
    Step(9, "TAX", "세무 판정 · 원천세", "V2 §8.3 9단계 L176 · L260~283 · 11장 · TAX.md", "s09_tax"),
    Step(10, "CLAIM", "반환 반영 · 청구 판정", "V2 §8.3 10단계 L177 · L284~298 · SPEC 13절", "s10_claim"),
    Step(11, "PAYOUT", "최소 지급 검증", "V2 §8.3 11단계 L178 · L299~308 · SPEC 14절", "s11_payout"),
    Step(12, "CLOSE_CHECK", "마감 검증(이월 연속성)", "V1 §7.4 L588~595 · SPEC 15.1", "s12_close_check"),
    Step(13, "PASS_REFUND_PAYOUT", "합격환급 수강생 지급(권리자 정산 밖)", "통합 설계서 S6 L438~446 · S-02 · S-14",
         "s13_pass_refund_payout"),
]

BY_CODE = {s.code: s for s in STEPS}
BY_NO = {s.no: s for s in STEPS}


def step_no(code):
    """스텝 코드 → 단계 번호. 모르는 코드는 99(맨 뒤 정렬)."""
    s = BY_CODE.get(code)
    return s.no if s else 99
