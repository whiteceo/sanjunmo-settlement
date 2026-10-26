"""fixture 기대값 경로 → 엔진 출력 값 찾기(테스트 접착층).

fixture의 기대값 이름(04권 서술을 옮긴 이름)과 엔진 출력 필드(SPEC · output.schema.json)가 다르므로 여기서 잇는다.
규칙: SYN(동의어) → 일반 규칙(앞 마디가 수취인 · 파이프라인이면 범위로) → 특수 해석 순.
"""

from core.money import D

SEP = " / "
MISSING = object()

SYN = {
    ("ACCRUAL", "accrued_amount"): ("ACCRUAL", "new_amount"),
    ("ACCRUAL", "total_pretax_accrual"): ("ACCRUAL", "accrual_total"),
    ("ACCRUAL", "new_pretax"): ("ACCRUAL", "accrual_total"),
    ("ACCRUAL", "payee_pretax_accrual"): ("ACCRUAL", "accrual_total"),
    ("ACCRUAL", "own_rights_holder_output"): ("ACCRUAL", "own_holder_output"),
    ("ACCRUAL", "gross_sales"): ("PIPELINE_IN", "monthly_sales"),
    ("ACCRUAL", "consignment_net_before_fee_vat"): ("PIPELINE_IN", "net_before_fee_vat"),
    ("ACCRUAL", "fee_supply"): ("PIPELINE_IN", "fee_supply"),
    ("ACCRUAL", "fee_vat"): ("TAX", "consignment_fee_vat"),
    ("MMG_ADJ", "mmg_subsidy_ledger_entry"): ("MMG_ADJ", "mmg_subsidy"),
    ("MMG_ADJ", "mmg_basis_1_1"): ("ACCRUAL", "mmg_basis_1_1"),
    ("DEDUCT", "deduct_amount"): ("DEDUCT", "deduct_total"),
    ("DEDUCT", "total_pretax_accrual"): ("DEDUCT", "net_total"),
    ("DEDUCT", "refund_deduct"): ("DEDUCT", "refund_deduct_1_1"),
    ("DEDUCT", "1.1_net_pretax"): ("DEDUCT", "net_1_1"),
    ("DEDUCT", "1.1_net"): ("DEDUCT", "net_1_1"),
    ("DEDUCT", "5.1_net"): ("DEDUCT", "net_5_1"),
    ("DEDUCT", "1.1_refund_deduct"): ("DEDUCT", "refund_deduct_1_1"),
    ("DEDUCT", "5.1_refund_deduct"): ("DEDUCT", "refund_5_1"),
    ("DEDUCT", "net_deduct_method_payout_adjust"): ("DEDUCT", "net_deduct_payout_adjust"),
    ("DEDUCT", "gross_settle_method_sales_adjust"): ("DEDUCT", "gross_settle_sales_adjust"),
    ("DEDUCT", "gross_settle_method_separate_claim"): ("DEDUCT", "gross_settle_separate_claim"),
    ("SUPPORT_CAP", "agreement_status"): ("SUPPORT_CAP", "status_after"),
    ("SUPPORT_CAP", "cap_consumed_restored"): ("SUPPORT_CAP", "restore_amount"),
    ("SUPPORT_CAP", "excess_expired"): ("SUPPORT_CAP", "expired_excess"),
    ("SUPPORT_CAP", "option_b_deduct"): ("DEDUCT", "optB_5_1"),
    ("SUPPORT_CAP", "payable_confirmed"): ("SUPPORT_CAP", "confirmed_amount"),
    ("SUPPORT_CAP", "remaining_cap_after_restore"): ("SUPPORT_CAP", "remaining_cap"),
    ("SUPPORT_CAP", "option_b_deduct_absorbed_by_excess_expiry"): ("SUPPORT_CAP", "deduct_absorbed_by_expiry"),
    ("SUPPORT_CAP", "cash_paid_total_after_payout"): ("PAYOUT", "cash_paid_total_after_payout"),
    ("PREPAY_OFFSET", "offset_target_pretax"): ("PREPAY_OFFSET", "offset_eligible_total"),
    ("PREPAY_OFFSET", "offset_eligible_pretax"): ("PREPAY_OFFSET", "offset_eligible_total"),
    ("PREPAY_OFFSET", "offsettable"): ("PREPAY_OFFSET", "offset_capacity"),
    ("PREPAY_OFFSET", "taxable_base_deduct_flag"): ("PREPAY_OFFSET", "taxable_reduction_flag"),
    ("LUMPSUM_ADD", "lumpsum"): ("LUMPSUM_ADD", "lumpsum_total"),
    ("PAYEE_SPLIT", "split_amount"): ("TAX", "split_amount_total"),
    ("PAYEE_SPLIT", "attributed_offset"): ("TAX", "offset_amount_total"),
    ("PAYEE_SPLIT", "pretax_payable"): ("TAX", "pre_tax_payable_total"),
    ("PAYEE_SPLIT", "taxable_base"): ("TAX", "taxable_base_total"),
    ("TAX", "income_tax"): ("TAX", "income_tax_total"),
    ("TAX", "local_income_tax"): ("TAX", "local_income_tax_total"),
    ("TAX", "total_withholding"): ("TAX", "withholding_total"),
    ("TAX", "withholding"): ("TAX", "withholding_total"),
    ("TAX", "net_payable"): ("TAX", "net_settle_amount"),
    ("TAX", "vat"): ("TAX", "vat_total"),
    ("TAX", "payable_total_incl_vat"): ("TAX", "vat_applied_total"),
    ("TAX", "invoice"): ("TAX", "evidence_type"),
    ("TAX", "evidence"): ("TAX", "evidence_type"),
    ("TAX", "settlement_input_amount"): ("PAYEE_SPLIT", "consignment_net"),
    ("TAX", "fee_vat_deduction"): ("TAX", "consignment_fee_vat"),
    ("TAX", "final_payout"): ("TAX", "consignment_settle_amount"),
    ("CLAIM", "claim_condition_met"): ("CLAIM", "claim_issued_yn"),
    ("CLAIM", "receivable_confirmed"): ("CLAIM", "claim_issued_yn"),
    ("CLAIM", "negative_invoice_issued_immediately"): ("CLAIM", "claim_issued_yn"),
    ("CLAIM", "claim_issued"): ("CLAIM", "claim_issued_yn"),
    ("CLAIM", "formal_claim_amount"): ("CLAIM", "claim_amount"),
    ("CLAIM", "forced_claim_trigger"): ("CLAIM", "force_claim"),
    ("CLAIM", "prepay_ledger_after"): ("CLAIM", "prepay_ledger_balance_after"),
    ("CLAIM", "prepay_ledger_status"): ("CLAIM", "prepay_ledger_status_on_lock"),
    ("CLAIM", "carry_amount"): ("CLAIM", "claim_carry"),
    ("PAYOUT", "payout_confirmed"): ("PAYOUT", "payout_confirmed_yn"),
    ("PAYOUT", "prepay_balance_after"): ("PREPAY_OFFSET", "prepay_balance_after"),
    ("PAYOUT", "external_payout"): ("PAYOUT", "payout_amount"),
    ("PAYOUT", "support_fund_net_payout"): ("PAYOUT", "payout_amount"),
    ("PAYOUT", "bypassed_in_transfer_and_evidence_loop"): ("PAYOUT", "excluded_from_bulk_transfer"),
    ("PAYOUT", "offset_with_unoffset_prepay"): ("CLAIM", "protected_crossed_with_claim"),
    ("PAYOUT", "closing_balance"): ("CLOSE_CHECK", "continuity_CONSIGNMENT"),
    ("PAYOUT", "offset_and_correction_movement_sign"): ("CLOSE_CHECK", "consignment_movement"),
    ("OWN_HOLDER", "distributable"): ("ACCRUAL", "own_holder_output"),
    ("OWN_HOLDER", "support_paid_to_instructor"): ("SUPPORT_CAP", "confirmed_amount"),
    ("OWN_HOLDER", "own_remaining"): ("SUPPORT_CAP", "own_remaining"),
    ("PLATFORM_COST", "mmg_subsidy"): ("MMG_ADJ", "mmg_subsidy"),
    ("PLATFORM_COST", "non_deductible_input_vat"): ("TAX", "non_deductible_input_vat"),
    ("REVENUE", "own_sales_recognized"): ("PIPELINE_IN", "own_sales_amount"),
    ("TAX", "min_tax_exempt"): ("TAX", "threshold_exempt_yn"),
    ("TAX", "total"): ("TAX", "withholding_total"),
    ("ACCRUAL_DEDUCT", "comparison_arithmetic_net"): ("DEDUCT", "net_total"),
    ("ACCRUAL_DEDUCT", "monthly_net"): ("DEDUCT", "net_total"),
    ("CLAIM", "abs_net_le_min_claim_limit"): ("CLAIM", "abs_le_min_claim_limit"),
    ("CLAIM", "carryover_type"): ("CLAIM", "claim_carry_type"),
    ("CLAIM", "carry_pipeline_id"): ("CLAIM", "claim_carry_pipeline_id"),
    ("CLAIM", "income_category"): ("CLAIM", "claim_carry_income_category"),
    ("RECEIPT", "withholding_receipt_issue"): ("TAX", "withholding_receipt_issue"),
    ("RECEIPT", "simplified_statement_monthly"): ("TAX", "simplified_statement_monthly"),
    ("RECEIPT", "annual_statement_due"): ("TAX", "annual_statement_due"),
}
# 수치를 바로 계산해 내는 파생 별칭: (top, field) → (step, field, 변환)
DERIVED = {
    ("MMG_ADJ", "adjusted"): ("MMG_ADJ", "mmg_subsidy", lambda v: D(v) > 0),
    ("MMG_ADJ", "excluded"): ("MMG_ADJ", "applicable", lambda v: not v),
    ("SUPPORT_CAP", "excluded"): ("SUPPORT_CAP", "applicable", lambda v: not v),
    ("PREPAY_OFFSET", "excluded"): ("PREPAY_OFFSET", "applicable", lambda v: not v),
    ("PREPAY_OFFSET", "executed"): ("PREPAY_OFFSET", "offset_amount", lambda v: D(v) > 0),
    ("CLAIM", "excluded"): ("CLAIM", "claim_evaluated", lambda v: not v),
    ("CLAIM", "unoffset_prepay"): ("CLAIM", "unoffset_prepay_claim", lambda v: -D(v)),
    ("CLAIM", "carry"): ("CLAIM", "claim_carry", lambda v: v is not None and D(v) != 0),
    ("PAYOUT", "excluded_from_payout_evaluation"): ("PAYOUT", "evaluated", lambda v: not v),
    ("PAYEE_SPLIT", "consignor_sole"): ("PAYEE_SPLIT", "consignor_sole", lambda v: v),
    ("ACCRUAL", "pipeline_inflow"): ("ACCRUAL", "pipeline_inflow", lambda v: v),
    ("TAX", "withholding_called"): ("TAX", "withholding_called", lambda v: v),
}
INTERNAL_ONLY = {("TAX", "supply_amount"): "supply_amount", ("TAX", "vat"): "vat_amount", ("TAX", "vat_rate"): "vat_rate",
                 ("TAX", "matrix_case_id"): "matrix_case_id", ("TAX", "withholding_called"): "withholding_called",
                 ("COST", "purchase_payable_ap"): "purchase_payable_ap",
                 ("COST", "in_ADMN_SETT_002_list"): "in_settlement_statement",
                 ("EVIDENCE", "channel"): "correction_channel", ("EVIDENCE", "correction_channel"): "correction_channel",
                 ("PAYOUT", "payout_amount"): "payout_amount"}
PIPES = {"1.1", "2.1", "2.2", "2.3", "5.1"}


class Index:
    def __init__(self, result):
        self.result = result
        last = {}
        for v in result.get("values", []):
            k = (v["rights_holder_id"], v["contract_id"], v["payee_id"], v["line_id"], v["step_code"], v["field"])
            last[k] = v  # 재검증 등으로 같은 키가 다시 나오면 마지막 값
        self.vals = list(last.values())
        self.payees = {v["payee_id"] for v in self.vals if v["payee_id"]}

    def get(self, step, field, payee=None, line=None):
        rows = [v for v in self.vals if v["step_code"] == step and v["field"] == field
                and (payee is None or v["payee_id"] == payee)
                and (line is None or v["line_id"] == line or str(v["line_id"] or "").startswith(line + ":"))]
        if not rows:
            return MISSING
        if line is None and any(r["line_id"] is None for r in rows):
            rows = [r for r in rows if r["line_id"] is None]  # 합계 행이 있으면 라인 행보다 우선
        vals = [r["value"] for r in rows]
        if len(vals) == 1 or all(x == vals[0] for x in vals):
            return vals[0]
        if all(isinstance(x, (int, str)) and not isinstance(x, bool) and _num(x) for x in vals):
            return sum(D(x) for x in vals)
        if all(isinstance(x, bool) for x in vals):
            return all(vals)
        return MISSING


def _num(x):
    try:
        D(x)
        return True
    except Exception:
        return False


def resolve(result, top, path):
    """→ (값 또는 MISSING, 설명)"""
    ix = result if isinstance(result, Index) else Index(result)
    segs = path.split(SEP)
    field = segs[-1]
    scope = segs[:-1]
    payee = next((s for s in scope if s in ix.payees), None)
    line = next((s for s in scope if s in PIPES), None)
    # '세무 항목 / 파이프라인'(예: taxable_base / 2.1, offset_by_pipeline / 1.1)
    if field in PIPES and scope:
        line, field = field, scope[-1]
        if field == "offset_by_pipeline":
            return ix.get("PREPAY_OFFSET", "offset_alloc", line=line), "PREPAY_OFFSET.offset_alloc"
        if field == "pretax_payable":
            return ix.get("PAYEE_SPLIT", "pre_tax_payable", line=line), "PAYEE_SPLIT.pre_tax_payable"
        if field == "taxable_base":
            return ix.get("PAYEE_SPLIT", "taxable_base", line=line), "PAYEE_SPLIT.taxable_base"
    if top == "MMG_ADJ" and field in PIPES and not scope:
        return ix.get("MMG_ADJ", "adjusted_1_1"), "MMG_ADJ.adjusted_1_1"
    if top == "PREPAY_OFFSET" and scope[:1] == ["withholding_equivalent"]:
        f = {"income_tax": "offset_withholding_income_tax", "local_income_tax": "offset_withholding_local_tax",
             "total": "offset_withholding_equiv"}[field]
        return ix.get("PREPAY_OFFSET", f), f"PREPAY_OFFSET.{f}"
    if top == "SUPPORT_CAP" and scope[:1] == ["support_fund_ledger"]:
        if field == "accrued_amount":
            return ix.get("ACCRUAL", "new_amount", line="5.1"), "ACCRUAL.new_amount(5.1)"
        return ix.get("SUPPORT_CAP", field), f"SUPPORT_CAP.{field}"
    if top == "PAYEE_SPLIT" and field == "pretax_payable" and scope[-1:] == ["pretax_payable"]:
        pass
    if top == "PAYEE_SPLIT" and path == f"pretax_payable{SEP}total":
        return ix.get("TAX", "pre_tax_payable_total"), "TAX.pre_tax_payable_total"
    if top == "TAX" and scope[:1] == ["vat_split"]:
        f = {"supply": "supply_amount", "vat": "vat_amount"}[field]
        return ix.get("TAX", f), f"TAX.{f}"
    # 라인 단위 세무 항목(TAX › 1.1 / income_tax)
    if top == "TAX" and line:
        f = {"total": "withholding_total", "min_tax_exempt": "threshold_exempt_yn"}.get(field, field)
        step = "PAYEE_SPLIT" if f == "taxable_base" else "TAX"
        return ix.get(step, f, payee=payee, line=line), f"{step}.{f}({line})"
    if top == "PAYEE_SPLIT" and payee:
        return ix.get("PAYEE_SPLIT", field, payee=payee), f"PAYEE_SPLIT.{field}({payee})"
    if (top, field) in DERIVED:
        step, f, fn = DERIVED[(top, field)]
        v = ix.get(step, f, payee=payee, line=line)
        if v is MISSING and (top, field) in (("CLAIM", "carry"),):
            return False, "CLAIM.claim_carry(없음)"
        if v is not MISSING or (top, field) not in INTERNAL_ONLY:
            return (MISSING if v is MISSING else fn(v)), f"{step}.{f}→파생"
    else:
        step, f = SYN.get((top, field), (top, field))
        v = ix.get(step, f, payee=payee, line=line)
    if v is MISSING and (top, field) in INTERNAL_ONLY:
        rows = [r for r in ix.result.get("internal_only", []) if INTERNAL_ONLY[(top, field)] in r]
        if rows:
            vals = [r[INTERNAL_ONLY[(top, field)]] for r in rows]
            v = vals[0] if len(set(map(str, vals))) == 1 else sum(D(x) for x in vals)
            return v, f"internal_only.{INTERNAL_ONLY[(top, field)]}"
    return v, f"{step}.{f}" + (f"({payee or line})" if (payee or line) else "")
