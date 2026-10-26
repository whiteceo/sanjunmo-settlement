"""단계 추적 기록(trace) — output.schema.json #trace_row 규격(SPEC 15.10).

계산 결과 값은 모두 trace 한 줄로 남고, 출력 값 목록(values)은 trace에서 뽑는다.
한 줄 = 범위(권리자 · 계약 · 수취인 · 라인 · 약정 · 원거래) · 입력값 · 적용 수식(정본 표기) · 의사코드 ·
       절사 전 값 · 절사 방식 · 결과값 · 정본 근거 · 잠정 여부(SPEC 16절 질문 번호).
"""

from .money import to_json
from .steps import BY_CODE


class Trace:
    def __init__(self):
        self.entries = []

    def add(self, step, field, value, *, holder=None, contract=None, payee=None, line=None,
            agreement=None, ref_id=None, line_key=None, inputs=None, formula="", code="",
            before=None, rounding="NONE", ref="", provisional=False, note=None, output=True):
        s = BY_CODE[step]
        e = {
            "seq": len(self.entries) + 1,
            "step": s.no,
            "step_code": s.code,
            "scope": {"rights_holder_id": holder, "contract_id": contract, "payee_id": payee,
                      "line_id": line, "line_key": line_key, "agreement_id": agreement, "ref_id": ref_id},
            "field": field,
            "inputs": to_json(dict(inputs or {})),
            "formula": formula,
            "formula_code": code,
            "before_rounding": to_json(before),
            "rounding": rounding,
            "result": to_json(value),
            "canon_ref": ref or s.ref,
            "provisional": bool(provisional),
            "note": note or "",
            "output": output,
        }
        self.entries.append(e)
        return value

    def values(self):
        """출력 값 목록(대조 · 테스트 기준). 키 = (권리자, 계약, 수취인, 라인, 단계, 필드)."""
        out = []
        for e in self.entries:
            if not e["output"]:
                continue
            sc = e["scope"]
            out.append({"rights_holder_id": sc["rights_holder_id"], "contract_id": sc["contract_id"],
                        "payee_id": sc["payee_id"], "line_id": sc["line_id"], "step_code": e["step_code"],
                        "field": e["field"], "value": e["result"]})
        return out
