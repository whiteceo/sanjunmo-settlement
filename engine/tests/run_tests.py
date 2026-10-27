"""fixture 회귀 테스트: engine/tests/fixtures/의 모든 케이스(+변형)를 계산해 정본 기대값과 비교.

    python engine/tests/run_tests.py [-k CASE-01] [-v] [--json out.json] [--html-dir out/]

흐름: fixture 입력 → tests/adapter.py(엔진 입력 스키마로) → 엔진 → tests/aliases.py(기대값 경로 → 출력 값) → 비교.
기대값은 말단까지 펼쳐 경로(' / ' 구분, 파이프라인 id '1.1'에 점이 있어서)로 비교한다.
  수치 · 불리언 · null 기대값: 반드시 일치해야 한다(불일치 = 차이).
  문자열 기대값(증빙 문구 · 설명): 같으면 일치, 다르거나 못 찾으면 '서술'(합격 판정에 넣지 않고 목록만).
판정
  PASS  수치 · 불리언 기대값 모두 일치      FAIL  차이 있음(처음 갈라진 단계 · 원인 판정 표시)
  ERROR 실행 오류                         HOLD  보류 — 정본이 기대값 확정 보류(HELD) · 금액 없는 규칙(QUALITATIVE)
                                               · 예시(ILLUSTRATIVE) · 일부만(PARTIAL), 또는 계산 입력 없음
차이 원인 판정은 tests/judgments.json(OPEN_ISSUES.md 근거)에서 읽는다.
"""

import argparse
import copy
import json
import sys
import traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "tests"))

from adapter import apply_delta, build  # noqa: E402
from aliases import MISSING, SEP, Index, resolve  # noqa: E402
from core import run_settlement  # noqa: E402
from core.money import D, eq, to_json  # noqa: E402
from core.steps import BY_CODE, step_no  # noqa: E402

FIXTURES = ENGINE / "tests" / "fixtures"
DECISIONS = ENGINE / "tests" / "decisions"  # 정본 결정(2026-10-27~) 회귀 — 엔진 입력 형식, 기대값은 정본 공식 수기 계산
JUDGMENTS = ENGINE / "tests" / "judgments.json"
HOLD_STATUSES = {"HELD", "QUALITATIVE", "ILLUSTRATIVE", "PARTIAL"}


def flatten(obj, prefix=()):
    if isinstance(obj, dict) and obj:
        out = {}
        for k, v in obj.items():
            out.update(flatten(v, prefix + (str(k),)))
        return out
    return {prefix: obj}


def expected_paths(exp):
    out = {}
    for top, body in (exp or {}).items():
        if not isinstance(body, dict):
            out[(top, "")] = body
            continue
        for path, v in flatten(body).items():
            out[(top, SEP.join(path))] = v
    return out


def is_narrative(ev):
    return isinstance(ev, str) or (isinstance(ev, list) and any(isinstance(x, str) for x in ev))


def same(cv, ev, tol=0):
    if ev is None:
        return cv is None
    if isinstance(ev, bool) or isinstance(cv, bool):
        return isinstance(cv, bool) and isinstance(ev, bool) and cv is ev
    if isinstance(ev, (int, float)):
        try:
            return eq(cv, ev, tol)
        except Exception:
            return False
    return cv == ev


def load_judgments():
    if JUDGMENTS.exists():
        return json.loads(JUDGMENTS.read_text(encoding="utf-8"))
    return {}


def judge(judg, code, top, path):
    """judgments.json: {케이스 코드: {"top / path" 또는 "top" 또는 "*": {"cause", "issue"}}}"""
    j = judg.get(code) or {}
    for k in (f"{top}{SEP}{path}" if path else top, top, "*"):
        if k in j:
            return j[k]
    return None


def evaluate(fx_case, judg):
    code, status = fx_case["code"], fx_case["status"]
    case = {"case_id": code, "title": fx_case["title"], "ref": fx_case["ref"], "expected_status": status,
            "file": fx_case["file"], "result": None, "diffs": [], "narrative": [], "matched": 0,
            "first_divergence": None, "adapter_notes": [], "issues": [], "engine_status": None}
    hold = status in HOLD_STATUSES
    if fx_case.get("engine_input"):
        data, notes = copy.deepcopy(fx_case["input"]), []
    else:
        data, notes = build(fx_case["input"], code, fx_case.get("base"))
    case["adapter_notes"] = notes
    want = expected_paths(fx_case["expected"])
    case["expected_count"] = len(want)
    if data is None:
        case["result"] = "HOLD"
        case["hold_reason"] = "계산 입력 없음(" + "; ".join(notes) + ")"
        return case, None
    try:
        result = run_settlement(data)
    except Exception as ex:
        case["result"] = "ERROR"
        case["error"] = "".join(traceback.format_exception(ex)[-3:]).strip()
        return case, None
    case["engine_status"] = result["status"]
    case["issues"] = result["issues"]
    ix = Index(result)
    for (top, path), ev in want.items():
        cv, where = resolve(ix, top, path) if path else (MISSING, "")
        found = cv is not MISSING
        cvj = to_json(cv) if found else None
        if found and same(cv, ev, fx_case.get("tol", 0)):
            case["matched"] += 1
            continue
        row = {"step_no": step_no(top), "step_code": top, "aux": top not in BY_CODE, "path": path,
               "expected": ev, "calc": cvj, "found": found, "engine_field": where}
        if is_narrative(ev):
            case["narrative"].append(row)
            continue
        try:
            row["diff"] = to_json(D(cv) - D(ev)) if found and not isinstance(ev, bool) and ev is not None else None
        except Exception:
            row["diff"] = None
        j = judge(judg, code, top, path)
        row["cause"] = (j or {}).get("cause", "보류" if hold else "미판정")
        row["issue"] = (j or {}).get("issue")
        case["diffs"].append(row)
    case["diffs"].sort(key=lambda d: (d["step_no"], d["path"]))
    if case["diffs"]:
        case["first_divergence"] = case["diffs"][0]
    if hold:
        case["result"] = "HOLD"
        case["hold_reason"] = f"정본 상태 {status}"
    else:
        case["result"] = "FAIL" if case["diffs"] else "PASS"
    return case, result


def load_cases(path):
    fx = json.loads(path.read_text(encoding="utf-8"))
    engine_form = "engine_input" in fx  # tests/decisions: 엔진 입력 스키마 그대로(어댑터 없음)
    key = "engine_input" if engine_form else "input"
    base = {"code": fx.get("case", path.stem), "title": fx.get("title"), "ref": fx.get("canon_ref"),
            "status": fx.get("expected_status"), "input": fx[key], "expected": fx.get("expected"),
            "tol": fx.get("tolerance", 0), "file": path.name, "engine_input": engine_form}
    yield base
    for v in fx.get("variants", []) or []:
        inp = copy.deepcopy(v["input"]) if "input" in v else apply_delta(base["input"], v.get("input_delta"))
        yield {"code": v.get("code"), "title": v.get("title"), "ref": base["ref"],
               "status": v.get("expected_status", base["status"]), "input": inp, "expected": v.get("expected"),
               "tol": v.get("tolerance", base["tol"]), "file": path.name, "base": base["input"],
               "engine_input": engine_form}
    for r in fx.get("reference_examples", []) or []:
        yield {"code": r.get("code"), "title": r.get("title"), "ref": r.get("canon_ref", base["ref"]),
               "status": r.get("expected_status", "ILLUSTRATIVE"), "input": r.get("input"),
               "expected": r.get("expected"), "tol": 0, "file": path.name}


def run_all(fixtures=None, k=None, html_dir=None):
    judg = load_judgments()
    cases = []
    dirs = [Path(fixtures)] if fixtures else [FIXTURES, DECISIONS]
    for f in [f for d in dirs for f in sorted(d.glob("*.json"))]:
        for c in load_cases(f):
            if k and k not in f.name and k not in str(c["code"]):
                continue
            case, result = evaluate(c, judg)
            cases.append(case)
            if html_dir and result:
                from report import render_html
                out = Path(html_dir) / f"{case['case_id']}.html"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(render_html(result, f"{case['case_id']} {case['title'] or ''}", case=case),
                               encoding="utf-8")
    return cases


def tally(cases):
    keys = ("PASS", "FAIL", "ERROR", "HOLD")
    t = {s: sum(1 for c in cases if c["result"] == s) for s in keys}
    causes = {}
    for c in cases:
        if c["result"] != "FAIL":
            continue
        for d in c["diffs"]:
            causes[d["cause"]] = causes.get(d["cause"], 0) + 1
    return t, causes


def main(argv=None):
    ap = argparse.ArgumentParser(description="fixture 회귀 테스트")
    ap.add_argument("-k", help="파일 이름 또는 케이스 코드에 이 문자열이 든 것만")
    ap.add_argument("--fixtures", help="한 폴더만(기본: tests/fixtures + tests/decisions)")
    ap.add_argument("--json", help="결과 JSON 저장 경로")
    ap.add_argument("--html-dir", help="케이스별 단계표 HTML 저장 폴더")
    ap.add_argument("--verbose", "-v", action="store_true", help="차이 · 서술 기대값 전부 출력")
    args = ap.parse_args(argv)

    cases = run_all(args.fixtures, args.k, args.html_dir)
    if not cases:
        print(f"fixture 없음: {args.fixtures or FIXTURES}")
        return 2
    for case in cases:
        line = (f"[{case['result']:5}] {case['case_id']} ({case['expected_status']}) {case['title'] or ''}"
                f"  — 일치 {case['matched']}/{case['expected_count']}")
        if case["narrative"]:
            line += f" · 서술 {len(case['narrative'])}"
        if case["result"] == "ERROR":
            line += f"\n        {case['error']}"
        elif case["first_divergence"]:
            d = case["first_divergence"]
            where = f"{d['step_no']} {d['step_code']}" if not d["aux"] else f"보조 {d['step_code']}"
            line += (f"\n        처음 갈라진 단계 {where} › {d['path']}: 기대 {d['expected']} · 계산 "
                     f"{d['calc'] if d['found'] else '(없음)'} [{d['cause']}{' ' + d['issue'] if d.get('issue') else ''}]")
        if case["result"] == "HOLD" and case.get("hold_reason"):
            line += f"\n        보류 사유: {case['hold_reason']}"
        print(line)
        if args.verbose or case["result"] == "FAIL":
            for d in case["diffs"][(0 if args.verbose else 1):]:
                print(f"        {d['step_no']:>2} {d['step_code']:<13} {d['path']}: 기대 {d['expected']} · 계산 "
                      f"{d['calc'] if d['found'] else '(없음)'} ← {d['engine_field']} [{d['cause']}]")
        if args.verbose:
            for d in case["narrative"]:
                print(f"        서술 {d['step_code']} › {d['path']}: 기대 {d['expected']!r} · 계산 {d['calc']!r}")
            for n in case["adapter_notes"]:
                print(f"        입력 변환: {n}")
    t, causes = tally(cases)
    gated = t["PASS"] + t["FAIL"] + t["ERROR"]
    print(f"\n합계 {len(cases)} · 판정 대상 {gated}: PASS {t['PASS']} · FAIL {t['FAIL']} · ERROR {t['ERROR']}"
          f" · 보류(HOLD) {t['HOLD']}")
    if causes:
        print("FAIL 차이 원인: " + " · ".join(f"{k} {v}" for k, v in sorted(causes.items())))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps({"tally": t, "causes": causes, "cases": cases}, ensure_ascii=False,
                                              indent=2, default=str), encoding="utf-8")
    return 0 if t["FAIL"] == 0 and t["ERROR"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
