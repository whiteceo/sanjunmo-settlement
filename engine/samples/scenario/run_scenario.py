"""샘플 데이터 시나리오(scripts/qa/reports/review/SCENARIO.md 2절) 정산 금액 산출.

    python engine/samples/scenario/run_scenario.py

scenario.json(매니페스트) · inputs/*.json(엔진 입력) → 계산기 실행 → scenario_amounts.json · scenario_amounts.md.
- 권리자(정산서)마다 ADMN-SETT-002 statements 필드명 그대로인 `sett002` 객체와 수취인별 값을 낸다.
- 04권 케이스를 재사용한 권리자는 fixture를 원래 id로 돌린 결과(PASS 여부)와, id만 바꾼 시나리오 입력의 결과가
  값 하나하나 같은지로 `matches04`를 정한다.
"""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "tests"))

from adapter import apply_delta, build  # noqa: E402
from aliases import Index, resolve  # noqa: E402
from core import run_settlement  # noqa: E402
from core.money import D, to_json  # noqa: E402
from run_tests import evaluate, flatten, is_narrative, load_judgments, same  # noqa: E402

SETT002_KEYS = ["step1PreTaxCarry", "step1PostTaxWait", "step2LectureRs", "step2BookRoyalty", "step2SupportAccrued",
                "step3MmgSubsidy", "step4LectureDeduct", "step4SupportDeduct", "step5SupportConfirmed",
                "step6PrepayEligible", "step6PrepayOffset", "step7LumpSumAdd", "step8TaxableBaseSum", "step9VatAmount",
                "step9WithholdingTax", "step10PostTaxAdjust", "step11NetPayout", "payoutCategory"]


def n(x):
    return D(x) if x is not None else D(0)


def contract_of(result, holder, cid):
    for h in result["rights_holders"]:
        if h["rights_holder_id"] == holder:
            for c in h["contracts"]:
                if c["contract_id"] == cid:
                    return c
    return None


def sett002(c):
    s = c["steps"]
    pays = c["payees"]
    new = s.get("ACCRUAL", {}).get("new_lines", [])
    by_pl = lambda pl: sum((n(x["amount"]) for x in new if x["line_key"]["pipeline_id"] == pl), D(0))  # noqa: E731
    ded = s.get("DEDUCT", {})
    sup = s.get("SUPPORT_CAP") if isinstance(s.get("SUPPORT_CAP"), list) else []
    pre = s.get("PREPAY_OFFSET", {})
    cin = s.get("CARRY_IN", {})
    lump = s.get("LUMPSUM_ADD", {})
    t = lambda k: sum((n(p["TAX"].get(k)) for p in pays), D(0))  # noqa: E731
    cons = ded.get("consignment_return")
    confirmed = [p for p in pays if p["PAYOUT"].get("payout_confirmed_yn")]
    issued = [p for p in pays if p["CLAIM"].get("claim_issued_yn")]
    if confirmed:
        cat, net = "PAYOUT_TARGET", sum((n(p["PAYOUT"]["payout_amount"]) for p in pays), D(0))
    elif issued:
        cat, net = "CLAIM_ISSUED", sum((n(p["CLAIM"]["claim_negative_net"]) for p in pays), D(0))
    else:
        cat, net = "CARRYOVER_HOLD", sum((n(p["PAYOUT"].get("payout_judgement_amount")) for p in pays), D(0))
    out = {
        "step1PreTaxCarry": sum((n(r["carryover_amount"]) for r in cin.get("carry_pre_tax_pos", []) +
                                 cin.get("carry_pre_tax_neg", [])), D(0)),
        "step1PostTaxWait": sum((n(r["carryover_amount"]) for r in cin.get("carry_post_tax_pos", [])), D(0)),
        "step2LectureRs": by_pl("1.1"),
        "step2BookRoyalty": by_pl("2.1"),
        "step2SupportAccrued": by_pl("5.1"),
        "step3MmgSubsidy": n(s.get("MMG_ADJ", {}).get("mmg_subsidy")),
        "step4LectureDeduct": -(n(ded.get("refund_deduct_1_1")) + n(ded.get("optB_deduct_1_1")) +
                                n(ded.get("optC_deduct_1_1")) + n(ded.get("return_deduct_2_1"))),
        "step4SupportDeduct": -sum((n(r["total"]) for r in ded.get("support_deduct_total", [])), D(0)),
        "step5SupportConfirmed": sum((n(r["confirmed_amount"]) for r in sup), D(0)),
        "step6PrepayEligible": n(pre.get("offset_eligible_total")),
        "step6PrepayOffset": -n(pre.get("offset_amount")),
        "step7LumpSumAdd": n(lump.get("lumpsum_total")),
        "step8TaxableBaseSum": t("taxable_base_total"),
        "step9VatAmount": t("vat_total"),
        "step9WithholdingTax": t("withholding_total"),
        "step10PostTaxAdjust": sum((n(p["CLAIM"].get("net_after_return")) - n(p["TAX"].get("net_settle_amount")) +
                                    n(p["TAX"].get("consignment_settle_amount") if n(p["TAX"].get("consignment_settle_amount")) < 0 else 0)
                                    for p in pays), D(0)),
        "step11NetPayout": net,
        "payoutCategory": cat,
    }
    extra = {}
    cs = s.get("ACCRUAL", {}).get("consignment")
    if cs:  # 위탁(Pipeline 2.2): SETT-002 STMT-03 관례 — 판매대금 step2ConsignGross, 수수료 step4LectureDeduct, 수수료 부가세 step9VatAmount(음수)
        fee_vat = t("consignment_fee_vat")
        out["step2ConsignGross"] = n(cs["monthly_sales"])
        out["step4LectureDeduct"] = -n(cs["fee_supply"]) - (n(cons["sales_adjust"]) * -1 - n(cons["fee_supply_adjust"]) * -1 if cons else 0)
        out["step9VatAmount"] = -fee_vat
        extra["consignment"] = {"monthlySales": cs["monthly_sales"], "netBeforeFeeVat": cs["net_before_fee_vat"],
                                "feeSupply": cs["fee_supply"], "consignmentInput": cs["consignment_input"],
                                "feeVat": fee_vat, "consignmentSettleAmount": t("consignment_settle_amount"),
                                "returnAdjust": cons}
    return to_json(out), extra


def payee_rows(c):
    rows = []
    for p in c["payees"]:
        t, cl, po = p["TAX"], p["CLAIM"], p["PAYOUT"]
        if not p["lines"]:
            continue
        pending = [ln["line_id"] for ln in p["lines"] if ln.get("tax_decision_status") == "PENDING_REVIEW"]
        rows.append(to_json({
            "payeeId": p["payee_id"],
            "matrixCaseIds": t.get("matrix_case_ids"),
            "taxDecisionPendingLines": pending,
            "splitAmount": t.get("split_amount_total"), "prepayOffset": t.get("offset_amount_total"),
            "preTaxPayable": t.get("pre_tax_payable_total"), "taxableBase": t.get("taxable_base_total"),
            "vat": t.get("vat_total"), "incomeTax": t.get("income_tax_total"),
            "localIncomeTax": t.get("local_income_tax_total"), "withholdingTotal": t.get("withholding_total"),
            "netSettleAmount": t.get("net_settle_amount"), "netSettleProtected": t.get("net_settle_protected"),
            "carryPreTaxAfterTax": t.get("carry_pre_tax_after_tax_total"),
            "netAfterReturn": cl.get("net_after_return"), "claimNegativeNet": cl.get("claim_negative_net"),
            "claimIssued": cl.get("claim_issued_yn"), "claimAmount": cl.get("claim_amount"),
            "unoffsetPrepayClaim": cl.get("unoffset_prepay_claim"),
            "payableNetForPayout": cl.get("payable_net_for_payout"),
            "payoutJudgementAmount": po.get("payout_judgement_amount"), "payoutConfirmed": po.get("payout_confirmed_yn"),
            "payoutAmount": po.get("payout_amount"), "carryLoad": po.get("carry_load"),
            "excludedFromBulkTransfer": po.get("excluded_from_bulk_transfer"),
            "lines": [{k: ln.get(k) for k in ("line_id", "origin", "matrix_case_id", "tax_decision_status", "split_amount",
                                             "offset_amount", "pre_tax_payable", "taxable_base", "vat_amount", "income_tax",
                                             "local_income_tax", "deemed_expense", "other_income_amount",
                                             "threshold_exempt_yn", "net_settle_line", "after_tax_amount")}
                      for ln in p["lines"]],
        }))
    return rows


def fixture_check(entry):
    """04권 fixture를 원래 id로 돌려 PASS 여부, 시나리오 입력 결과와 값 비교."""
    f = entry["fixture"]
    fx = json.loads((ENGINE / "tests" / "fixtures" / f["file"]).read_text(encoding="utf-8"))
    base = fx["input"]
    if "variant" in f:
        v = fx["variants"][f["variant"]]
        inp = v["input"] if "input" in v else apply_delta(base, v.get("input_delta"))
        exp, status, code, title = v["expected"], v.get("expected_status"), v["code"], v["title"]
    else:
        inp, exp, status, code, title = base, fx["expected"], fx["expected_status"], fx["case"], fx["title"]
    case, fres = evaluate({"code": code, "title": title, "ref": fx.get("canon_ref"), "status": status, "input": inp,
                           "expected": exp, "tol": 0, "file": f["file"]}, load_judgments())
    return case, fres


def renamed_values(result, ids):
    """values를 비교용 집합으로. ids의 옛 id를 단어 단위로 새 id로 바꾼다(복합 문자열 'P1:100' · 'C1+SKU' 포함)."""
    pats = [(re.compile(r"(?<![\w-])" + re.escape(a) + r"(?![\w-])"), b) for a, b in ids.items()]

    def r(x):
        if isinstance(x, str):
            for pat, b in pats:
                x = pat.sub(b, x)
        return x
    empty = {(c["contract_id"], p["payee_id"]) for h in result["rights_holders"] for c in h["contracts"]
             for p in c["payees"] if not p["lines"]}  # 라인 없는 수취인(분할 계약의 권리자 자리) 행은 비교에서 뺀다
    return {tuple(r(v[k]) for k in ("rights_holder_id", "contract_id", "payee_id", "line_id", "step_code", "field"))
            + (r(json.dumps(v["value"], ensure_ascii=False)),) for v in result["values"]
            if (v["contract_id"], v["payee_id"]) not in empty}


SCREEN = ENGINE.parent / "prototype_clean" / "ADMN-SETT-002_baseline.html"


def screen_statements():
    """현재 ADMN-SETT-002 statements(읽기 전용) → {payeeId: {필드: 값}}. 화면과 계산기 값 차이 표에만 쓴다."""
    if not SCREEN.exists():
        return {}
    src = SCREEN.read_text(encoding="utf-8")
    out = {}
    for blk in re.split(r'\n\s*\{\s*\n\s*id: "STMT-', src)[1:]:
        m = re.search(r'payeeId: "([^"]+)"', blk)
        if not m:
            continue
        head = blk.split("diffReasonNote")[0]
        row = {k: int(v) for k, v in re.findall(r"(step\w+): (-?\d+)", head)}
        cat = re.search(r'payoutCategory: "([A-Z_]+)"', head)
        row["payoutCategory"] = cat.group(1) if cat else None
        out[m.group(1)] = row
    return out


def run_alternative(data, alt):
    data = json.loads(json.dumps(data))
    for k, v in (alt.get("set_holder") or {}).items():
        data["rights_holders"][0][k] = v
    return run_settlement(data)


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "예" if v else "아니오"
    if isinstance(v, int) or (isinstance(v, str) and re.fullmatch(r"-?\d+", v)):
        return f"{int(v):,}"
    return str(v)


def write_md(out, questions):
    L = ["# 샘플 데이터 시나리오 정산 금액 (계산기 산출)", "",
         f"> 정산월 {out['settlement_month']} · 엔진 {out['engine_version']} · 생성: `python engine/samples/scenario/run_scenario.py`"
         " (입력 `inputs/*.json`, 매니페스트 `scenario.json`). 설계: `scripts/qa/reports/review/SCENARIO.md` 2절.",
         "> 04권 일치 = 04권 fixture를 원래 id로 돌려 PASS이고, 권리자 id로 바꾼 시나리오 입력의 결과가 값 하나하나 같음.",
         "> 금액 단위 원. 화면 작업자는 `scenario_amounts.json`의 `sett002`를 ADMN-SETT-002 statements에 그대로 옮긴다.", "",
         "## 1. 요약", "",
         "| 권리자 | 케이스 | 과세표준 합 | 선급금 상계 | 소득세 | 지방세 | 부가세 | 실지급(청구는 음수) | 판정 | 04권 일치 | 확인 필요 |",
         "| :--- | :--- | --: | --: | --: | --: | --: | --: | :--- | :-: | :--- |"]
    for h in out["holders"]:
        s = h["sett002"]
        it = sum(int(p.get("incomeTax") or 0) for p in h["payees"])
        lt = sum(int(p.get("localIncomeTax") or 0) for p in h["payees"])
        pend = " (보류)" if any(p["taxDecisionPendingLines"] for p in h["payees"]) else ""
        qs = ", ".join(q["id"] for q in questions if h["holderId"] in q["holders"])
        m04 = {True: "일치", False: "불일치", None: "— (계산기 값)"}[h["matches04"]]
        L.append(f"| {h['holderName']} {h['holderId']} | {h['case']} | {fmt(s['step8TaxableBaseSum'])} "
                 f"| {fmt(s['step6PrepayOffset'])} | {fmt(it)}{pend} | {fmt(lt)}{pend} | {fmt(s['step9VatAmount'])} "
                 f"| {fmt(s['step11NetPayout'])} | {s['payoutCategory']} | {m04} | {qs} |")
    L += ["", "## 2. ADMN-SETT-002 statements 값(`sett002`)", "",
          "| 권리자 | " + " | ".join(k.replace("step", "") for k in SETT002_KEYS) + " |",
          "| :--- | " + " | ".join("--:" for _ in SETT002_KEYS) + " |"]
    for h in out["holders"]:
        L.append(f"| {h['holderId']} | " + " | ".join(fmt(h["sett002"][k]) for k in SETT002_KEYS) + " |")
    L += ["", "- 해당 없는 단계는 0. `step4*` · `step6PrepayOffset` · 청구는 음수(화면 관례).",
          "- `step10PostTaxAdjust` = 10단계 세후 차감(반환 상계 동의된 전속계약금 반환 등) = 반환 반영 후 순액 − 9단계 실정산액.",
          "- `step11NetPayout`: PAYOUT_TARGET = 지급 확정액, CARRYOVER_HOLD = 판정 금액(지급하지 않고 이월), CLAIM_ISSUED = 청구 대상 음수.",
          "- 위탁(Case 10)은 SETT-002 STMT-03 관례: `step2ConsignGross` = 월 판매대금, `step4LectureDeduct` = −위탁 수수료 공급가액,"
          " `step9VatAmount` = −수수료 부가세. 엔진 원값은 json의 `consignment` 키.",
          "- 정산서 1건에 지급과 청구가 같이 있으면(이중도) 판정은 PAYOUT_TARGET, 청구액은 수취인 행 `claimAmount` · `unoffsetPrepayClaim`.",
          "- 세무 판정 보류(PENDING_REVIEW) 수취인은 원천세를 산출하지 않는다 — `step9WithholdingTax` 0은 '보류'라는 뜻(1절 '(보류)').", "",
          "## 3. 현재 SETT-002와 다른 값", "",
          "| 권리자 | 필드 | 현재 화면 | 계산기 |", "| :--- | :--- | --: | --: |"]
    rows = [(h["holderId"], k, a, b) for h in out["holders"] for k, (a, b) in (h.get("screenDiff") or {}).items()]
    L += [f"| {hid} | {k} | {fmt(a)} | {fmt(b)} |" for hid, k, a, b in rows] or ["| — | — | — | — |"]
    L += ["", "화면에 정산서가 아직 없는 권리자(박보건 · 최지도 · 김안전 · 이건설 · 안전기술출판 · 이안전 · 고 박위생)는 비교하지 않았다.", "",
          "## 4. 권리자별 상세", ""]
    for h in out["holders"]:
        L += [f"### {h['holderName']} {h['holderId']} · {h['contractId']} — {h['case']}", ""]
        c4 = h.get("check04")
        if c4:
            same = f", 시나리오 입력 결과 동일 {fmt(c4['sameAsFixtureRun'])}" if "sameAsFixtureRun" in c4 else ""
            narr = f", 서술 {c4['narrative']}" if c4["narrative"] else ""
            L.append(f"- 04권: fixture `{c4['fixture']}` {c4['code']} {c4['fixtureResult']}"
                     f" (기대값 {c4['matched']}/{c4['expectedCount']} 일치{narr}){same}")
            if c4.get("note"):
                L.append(f"- {c4['note']}")
        L += [f"- 입력: {x}" for x in h["notes"]]
        L += ["", "| 수취인 | 케이스 | 분할액 | 상계 | 세전 지급액 | 과세표준 | 부가세 | 소득세 | 지방세 | 9단계 실정산 | 청구 | 판정 금액 | 지급 | 이월 적재 |",
              "| :--- | :--- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |"]
        for p in h["payees"]:
            pend = " 보류" if p["taxDecisionPendingLines"] else ""
            L.append(f"| {p['payeeId']} | {'/'.join(p['matrixCaseIds'] or [])}{pend} | {fmt(p['splitAmount'])} "
                     f"| {fmt(p['prepayOffset'])} | {fmt(p['preTaxPayable'])} | {fmt(p['taxableBase'])} | {fmt(p['vat'])} "
                     f"| {fmt(p['incomeTax'])} | {fmt(p['localIncomeTax'])} | {fmt(p['netSettleAmount'])} "
                     f"| {fmt(p['claimAmount'])} | {fmt(p['payoutJudgementAmount'])} | {fmt(p['payoutAmount'])} "
                     f"| {fmt(p['carryLoad'])} |")
        for sl in h.get("supportLedger", []):
            st = f" · 상태 {sl['status_change']}" if sl.get("status_change") else ""
            L.append(f"- 지원금 원장 {sl['agreement_id']}: 발생 {fmt(sl['accrued_amount'])} · 확정 {fmt(sl['confirmed_amount'])}"
                     f" · 순누계 {fmt(sl['confirmed_net_total'])} · 소진 {fmt(sl['cap_consumed_amount'])}"
                     f" · 잔여 한도 {fmt(sl['remaining_cap'])} · 지급 누계 {fmt(sl['cash_paid_total'])}{st}")
        for pl in h.get("prepaymentLedger", []):
            L.append(f"- 선급금: 상계 {fmt(pl['offset_amount'])} · 잔액 {fmt(pl['balance_after'])}"
                     f"{' · ' + pl['status'] if pl.get('status') else ''}")
        for cr in h.get("carryoverRows", []):
            if cr.get("action") in ("NEW", "RESERVE", "REDUCE"):
                L.append(f"- 이월 원장 {cr['action']}: {cr.get('account_type') or '위탁 전용'} {fmt(cr['carryover_amount'])}"
                         f" ({cr.get('carryover_reason') or ''}, 수취인 {cr.get('payee_id')})")
        for a in h.get("alternatives", []):
            s = a["sett002"]
            L.append(f"- 대안 — {a['label']}: 원천세 {fmt(s['step9WithholdingTax'])} · 상계 {fmt(s['step6PrepayOffset'])}"
                     f" · 실지급 {fmt(s['step11NetPayout'])} ({s['payoutCategory']})")
        L.append("")
    L += ["## 5. 확인 필요", "", "| 번호 | 권리자 | 구분 | 내용 |", "| :--- | :--- | :--- | :--- |"]
    L += [f"| {q['id']} | {', '.join(q['holders'])} | {q['kind']} | {q['text']} |" for q in questions]
    L.append("")
    (HERE / "scenario_amounts.md").write_text("\n".join(L), encoding="utf-8")


def main():
    man = json.loads((HERE / "scenario.json").read_text(encoding="utf-8"))
    cache = {}
    holders = []
    screens = screen_statements()
    for e in man["holders"]:
        if e["input"] not in cache:
            data = json.loads((HERE / "inputs" / e["input"]).read_text(encoding="utf-8"))
            cache[e["input"]] = run_settlement(data)
        res = cache[e["input"]]
        c = contract_of(res, e["holderId"], e["contractId"])
        s002, extra = sett002(c)
        row = {"holderId": e["holderId"], "holderName": e.get("holderName"), "contractId": e["contractId"],
               "case": e["case"], "input": f"inputs/{e['input']}", "engineStatus": res["status"],
               "matches04": None, "sett002": s002, **extra, "payees": payee_rows(c),
               "steps": to_json(c["steps"]),
               "supportLedger": [x for x in res["ledgers"]["support_fund_ledger"]
                                 if any(a.get("agreement_id") == x["agreement_id"]
                                        for a in (c["steps"].get("SUPPORT_CAP") or []))],
               "carryoverRows": [x for x in res["ledgers"]["carryover_ledger"] if x.get("contract_id") == e["contractId"]],
               "prepaymentLedger": [x for x in res["ledgers"]["prepayment_ledger"] if x["contract_id"] == e["contractId"]],
               "continuity": [x for x in res["continuity"] if x["key"] in [e["contractId"]] + [p["payeeId"] for p in payee_rows(c)]],
               "issues": [i for i in res["issues"] if i.get("rights_holder_id") in (None, e["holderId"])],
               "notes": e.get("notes", [])}
        if "fixture" in e:
            case, fres = fixture_check(e)
            check = {"fixture": e["fixture"]["file"], "code": case["case_id"], "fixtureResult": case["result"],
                     "matched": case["matched"], "expectedCount": case["expected_count"],
                     "narrative": len(case["narrative"]),
                     "diffs": [{k: d[k] for k in ("step_code", "path", "expected", "calc")} for d in case["diffs"]]}
            if e["fixture"].get("combined"):
                ix = Index(res)
                case9 = []
                for top, body in json.loads((ENGINE / "tests" / "fixtures" / e["fixture"]["file"]).read_text(
                        encoding="utf-8"))["expected"].items():
                    for path, ev in flatten(body).items():
                        if is_narrative(ev):
                            continue
                        cv, _ = resolve(ix, top, " / ".join(path))
                        if not same(cv, ev):
                            case9.append({"step_code": top, "path": " / ".join(path), "expected": ev, "calc": to_json(cv)})
                d9 = []
                sc = (c["steps"].get("SUPPORT_CAP") or [{}])[0]
                dd = {r["agreement_id"]: r for r in c["steps"]["DEDUCT"]["support_deduct_total"]}
                got = dict(sc, optB_5_1=dd.get(sc.get("agreement_id"), {}).get("optB_5_1"))
                for k, v in e["d9_expected"].items():
                    if D(got.get(k) or 0) != D(v):
                        d9.append({"field": k, "expected": v, "calc": to_json(got.get(k))})
                check["combinedCase9Diffs"] = case9
                check["d9Diffs"] = d9
                row["matches04"] = not d9 and all(x["path"] in ("expired_excess", "5.1_net") for x in case9)
                check["note"] = ("Case 9 기대값과 다른 곳은 D-9 합격환급 옵션 B를 더해서 생긴 2개뿐: 4단계 P5.1 공제 후 금액 "
                                 "400,000 → 300,000(옵션 B 100,000 공제), 한도 초과 소멸 250,000 → 150,000(복원 100,000이 같은 달 "
                                 "한도에 더해짐). 지원금 확정액 150,000 · 세액 · 실지급 등 나머지 Case 9 값과 D-9 값은 모두 같음")
            else:
                same_vals = renamed_values(fres, e["fixture"]["ids"]) == renamed_values(res, {}) if fres else False
                check["sameAsFixtureRun"] = same_vals
                row["matches04"] = case["result"] == "PASS" and same_vals
            row["check04"] = check
        for alt in e.get("alternatives", []):
            ares = run_alternative(json.loads((HERE / "inputs" / e["input"]).read_text(encoding="utf-8")), alt)
            a002, _ = sett002(contract_of(ares, e["holderId"], e["contractId"]))
            row.setdefault("alternatives", []).append({"label": alt["label"], "engineStatus": ares["status"],
                                                       "sett002": a002})
        scr = screens.get(e["holderId"])
        if scr:
            row["screenDiff"] = {k: (scr.get(k), row["sett002"].get(k)) for k in SETT002_KEYS + ["step2ConsignGross"]
                                 if k in scr and str(scr.get(k)) != str(row["sett002"].get(k))}
        holders.append(row)
    out = {"settlement_month": man["settlement_month"], "engine_version": next(iter(cache.values()))["engine_version"],
           "generated_by": "engine/samples/scenario/run_scenario.py", "holders": holders,
           "open_questions": man.get("open_questions", [])}
    out = to_json(out)
    (HERE / "scenario_amounts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(out, out["open_questions"])
    for h in holders:
        s = h["sett002"]
        print(f"{h['holderId']:<8} {h['case']:<28} 04권 {str(h['matches04']):<5} 세전 {s['step8TaxableBaseSum']:>11,} "
              f"상계 {s['step6PrepayOffset']:>11,} 원천세 {s['step9WithholdingTax']:>8,} 부가세 {s['step9VatAmount']:>8,} "
              f"→ {s['step11NetPayout']:>11,} {s['payoutCategory']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
