"""정산 단계 실행기와 계산 상태.

입력 dict(input.schema.json, 한 정산월) → 0~12단계 모듈을 SPEC 2절 순서대로 실행 → 출력 dict(output.schema.json).
단계 모듈은 run(ctx) 하나만 가진다. 단계 사이 값은 ContractState · PayeeState에 담아 넘긴다.
"""

import calendar
import importlib
import json
from collections import OrderedDict
from pathlib import Path

from .money import D, to_json
from .steps import STEPS
from .trace import Trace

ENGINE_VERSION = "1.0.0"
CANON_VERSION = "정본 v4.0.x · main 2026-10-26(SPEC.md 기준)"
TAX_TABLE = Path(__file__).resolve().parents[1] / "tax_table.json"

# V3 부록 B 기본값(SPEC 12.1 · 15.2). 입력 params가 있으면 덮어쓴다.
DEFAULT_PARAMS = {
    "default_min_payout_limit": 100000,
    "default_min_claim_limit": -100000,
    "payout_threshold_basis": "VAT_INCLUDED",
    "default_weight_seconds": 60,
    "other_income_min_tax_amount": 50000,
    "local_income_tax_rate": "0.10",
    "small_amount_exemption_limit": 1000,
    "local_tax_small_exemption_apply_yn": False,
    "carryover_force_settle_month": 12,
    "carryover_max_months": 6,
    "manual_adj_approval_threshold": 1000000,
    "support_fund_mmg_include_yn": False,
    "adj_two_step_approval_yn": False,  # 1차 오픈 재무 담당자 단독 확정(V2 §10.3 · D-SETT-01), 2차에 true
    "month_closed_at": {},  # {귀속월: 마감 일시} — 보정 전표 반영 기준월 판정(V2 §10.2 · S-10)
}

LIST_KEYS = ["pass_refund_payouts", "rights_holders", "contracts", "rate_lines", "lecture_instructors", "book_authors", "payee_splits",
             "support_fund_agreements", "support_fund_agreement_targets", "support_fund_ledger_prev",
             "prepayments", "order_items", "orders", "refund_lines", "pass_refund_deductions",
             "lumpsum_approvals", "clawbacks", "carryover_ledger", "carryover_prev_end_balances",
             "adjustments", "payout_results"]


class EngineStop(Exception):
    """입력 오류 · 마감 월 — 계산 중단."""

    def __init__(self, status, code, message, ref=""):
        super().__init__(message)
        self.status, self.code, self.message, self.ref = status, code, message, ref


# ---------------------------------------------------------------- 날짜 · 기간

def month_of(d):
    return str(d)[:7] if d else None


def month_first(m):
    return f"{m}-01"


def month_last(m):
    y, mo = int(m[:4]), int(m[5:7])
    return f"{m}-{calendar.monthrange(y, mo)[1]:02d}"


def months_between(a, b):
    """월 차이 b − a (YYYY-MM)."""
    return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])


def period_end(row, contract_row):
    """유효 종료일: FIXED_DATE면 end_date, CONTRACT_LINKED면 계약 current_end_date(V1 §5.1 L210)."""
    if row.get("end_basis") == "CONTRACT_LINKED":
        return (contract_row or {}).get("current_end_date")
    return row.get("end_date")


def valid_on(row, date, contract_row=None):
    """date가 row의 [start_date, 유효 종료일] 안인가. 날짜가 없으면 통과."""
    if not date:
        return True
    s = row.get("start_date")
    e = period_end(row, contract_row)
    return (not s or str(s) <= str(date)) and (not e or str(date) <= str(e))


# ---------------------------------------------------------------- 상태

class Line:
    """계약 단위 정산 라인(SPEC 1절 라인 키)."""

    def __init__(self, label, contract_id, pipeline_id, **kw):
        self.label = label
        self.contract_id = contract_id
        self.pipeline_id = pipeline_id
        self.rate_type = kw.get("rate_type")
        self.agreement_id = kw.get("agreement_id")
        self.approval_id = kw.get("approval_id")
        self.income_category = kw.get("income_category")
        self.income_clause = kw.get("income_clause")
        self.tax_threshold_unit_key = kw.get("tax_threshold_unit_key")
        self.payee_is_author = kw.get("payee_is_author")
        self.supply_nature = kw.get("supply_nature")
        self.offset_type = kw.get("offset_type")
        self.item_kind = kw.get("item_kind")
        self.fixed_payee = kw.get("fixed_payee")  # Q-15: 약정 · 승인 원장 수취인(권리자와 다르면 단독 귀속)
        self.protected = kw.get("protected", False)  # 상계 비대상 보호분(SPEC 12.1)
        self.new = D(0)  # 2단계 신규 세전액
        self.deduct_components = []  # 4단계 공제 구성요소(음수 금액, 원거래 수취인 분할 보존)
        self.adjusted = None  # 3단계 보정 후 금액(P1.1)
        self.mmg_subsidy = D(0)  # 3단계 MMG 보전금(보정 대상 P1.1 라인)
        self.net = None  # 4 · 5단계 후 세전 순액(분할 대상)
        self.offset = D(0)  # 6단계 라인별 상계 배분
        self.eligible = D(0)  # 6단계 상계 적격액

    def key(self):
        return {"contract_id": self.contract_id, "pipeline_id": self.pipeline_id, "rate_type": self.rate_type,
                "agreement_id": self.agreement_id, "approval_id": self.approval_id,
                "income_category": self.income_category, "income_clause": self.income_clause,
                "tax_threshold_unit_key": self.tax_threshold_unit_key}


class PayeeState:
    def __init__(self, payee_id):
        self.payee_id = payee_id
        self.lines = []  # 8 · 9단계 payee × 라인 결과(dict, output.schema payees[].lines[])
        self.out = {"TAX": {}, "CLAIM": {}, "PAYOUT": {}}


class ContractState:
    def __init__(self, row):
        self.row = row
        self.id = row["contract_id"]
        self.holder_id = row["rights_holder_id"]
        self.lines = OrderedDict()
        self.out = OrderedDict()
        self.payees = OrderedDict()
        self.carry = {"pre_pos": [], "pre_neg": [], "post_pos": [], "post_neg": [], "cons": D(0), "cons_rows": []}
        self.return_claims = []
        self.prepay = None  # 선급금 원장 행
        self.prepay_balance_after = None
        self.splits = []  # 8단계에 쓴 payee_splits
        self.consignment = None  # P2.2 인입 결과
        self.mmg_subsidy = D(0)
        self.support = OrderedDict()  # agreement_id → 5단계 결과
        self.lumpsum_rows = []  # 7단계 승인 행

    def line(self, label, pipeline_id, **kw):
        if label not in self.lines:
            self.lines[label] = Line(label, self.id, pipeline_id, **kw)
        return self.lines[label]

    def lines_of(self, pipeline_id):
        return [ln for ln in self.lines.values() if ln.pipeline_id == pipeline_id]

    def payee(self, payee_id):
        if payee_id not in self.payees:
            self.payees[payee_id] = PayeeState(payee_id)
        return self.payees[payee_id]

    def step_out(self, code):
        return self.out.setdefault(code, {})

    def end_in_month(self, month):
        """만료 · 해지 귀속월이 당월인가(V2 L287 · SPEC 13.2)."""
        for k in ("termination_date", "current_end_date"):
            if self.row.get(k) and month_of(self.row[k]) == month:
                return True
        return False


class Context:
    def __init__(self, data):
        self.input = {k: v for k, v in data.items()}
        for k in LIST_KEYS:
            self.input[k] = list(self.input.get(k) or [])
        self.month = str(data.get("settlement_month") or "")[:7]
        self.params = dict(DEFAULT_PARAMS)
        self.params.update({k: v for k, v in (data.get("params") or {}).items() if v is not None})
        self.tax_table = json.loads(TAX_TABLE.read_text(encoding="utf-8"))
        self.trace = Trace()
        self.errors = []
        self.warnings = []
        self.issues = []  # 계산 중 쓴 잠정 규칙 · 입력 부족(SPEC 16절 질문 번호)
        self.holders = OrderedDict((h["rights_holder_id"], h) for h in self.input["rights_holders"])
        self.contracts = OrderedDict((c["contract_id"], ContractState(c)) for c in self.input["contracts"])
        self.internal_only = []
        self.excluded_lines = []
        self.pending_adjustments = []
        self.continuity = []
        self.ledgers = {"support_fund_ledger": [], "mmg_subsidy_ledger": [], "carryover_ledger": [],
                        "prepayment_ledger": []}
        self.own_holder = OrderedDict()  # agreement_id → 자사 재원 검증
        self.pass_refund_payouts = []  # 13 합격환급 수강생 지급

    # -- 조회
    def holder(self, hid):
        return self.holders.get(hid) or {"rights_holder_id": hid}

    def contract(self, cid):
        return self.contracts.get(cid)

    def rate(self, contract_id, rate_type, date=None, pipeline_id=None, agreement_id=None):
        """요율 라인 조회(V2 L135 · V1 L210). pipeline_id는 같은 계약에 파이프라인별 요율이 있을 때(스키마 확장)."""
        c = self.contract(contract_id)
        rows = [r for r in self.input["rate_lines"] if r["contract_id"] == contract_id and r["rate_type"] == rate_type
                and (agreement_id is None or r.get("agreement_id") == agreement_id)
                and valid_on(r, date, c.row if c else None)]
        if pipeline_id is not None:
            exact = [r for r in rows if r.get("pipeline_id") == pipeline_id]
            rows = exact or [r for r in rows if not r.get("pipeline_id")]
        if len(rows) > 1:
            self.warn("RATE_LINE_OVERLAP", f"{contract_id} {rate_type} 유효 요율 라인이 {len(rows)}건 — 첫 행 사용",
                      "V1 §5.1 L210")
        return rows[0] if rows else None

    # -- 기록
    def emit(self, step, field, value, c=None, payee=None, line=None, **kw):
        holder = kw.pop("holder", c.holder_id if c else None)
        contract = kw.pop("contract", c.id if c else None)
        return self.trace.add(step, field, value, holder=holder, contract=contract, payee=payee, line=line, **kw)

    def warn(self, code, message, ref=""):
        self.warnings.append({"code": code, "message": message, "canon_ref": ref})

    def issue(self, kind, message, step=None, holder=None, ref=None, q=None):
        """kind: INPUT_MISSING · CANON_GAP(잠정 규칙 사용) · CANON_CONFLICT."""
        item = {"kind": kind, "step_code": step, "rights_holder_id": holder, "message": message,
                "ref": ref, "question": q}
        if item not in self.issues:
            self.issues.append(item)

    def stop(self, status, code, message, ref=""):
        raise EngineStop(status, code, message, ref)

    def p(self, name):
        return self.params.get(name)


def run_settlement(data):
    ctx = Context(data)
    status = "OK"
    try:
        if data.get("locked"):
            ctx.stop("LOCKED_MONTH", "LOCKED_MONTH", "마감된 정산월 — 마감 취소 금지, 차월 조정 라인으로", "V2 §10.1 L350")
        for s in STEPS:
            importlib.import_module(f"{__package__}.{s.module}").run(ctx)
        if any(ln.get("tax_decision_status") == "PENDING_REVIEW"
               for c in ctx.contracts.values() for p in c.payees.values() for ln in p.lines):
            status = "BLOCKED_PENDING_REVIEW"
    except EngineStop as ex:
        status = ex.status
        ctx.errors.append({"code": ex.code, "message": ex.message, "canon_ref": ex.ref})
    return build_output(ctx, status, data)


def build_output(ctx, status, data):
    holders = OrderedDict()
    for c in ctx.contracts.values():
        h = holders.setdefault(c.holder_id, {"rights_holder_id": c.holder_id,
                                             "is_internal": bool(ctx.holder(c.holder_id).get("is_internal")),
                                             "contracts": []})
        h["contracts"].append({
            "contract_id": c.id,
            "steps": c.out,
            "payees": [{"payee_id": p.payee_id, "lines": p.lines, **p.out} for p in c.payees.values()],
        })
    return to_json({
        "settlement_month": ctx.month,
        "engine_version": ENGINE_VERSION,
        "canon_version": CANON_VERSION,
        "run_reason": data.get("run_reason"),
        "status": status,
        "errors": ctx.errors,
        "warnings": ctx.warnings,
        "rights_holders": list(holders.values()),
        "ledgers": ctx.ledgers,
        "continuity": ctx.continuity,
        "internal_only": ctx.internal_only,
        "excluded_lines": ctx.excluded_lines,
        "pending_adjustments": ctx.pending_adjustments,
        "pass_refund_payouts": ctx.pass_refund_payouts,
        "issues": ctx.issues,
        "steps": [{"no": s.no, "code": s.code, "name": s.name, "ref": s.ref} for s in STEPS],
        "values": ctx.trace.values(),
        "trace": ctx.trace.entries,
    })

