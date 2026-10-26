"""계산기 결과 vs 개발 시스템 결과 대조.

    python engine/compare.py --input in.json --dev dev.csv --map map.json [--html diff.html] [--csv diff.csv] [--json diff.json]
    python engine/compare.py --calc calc_out.json --dev dev.json --map map.json ...

--input이면 계산기를 그 자리에서 돌리고, --calc면 이미 돌린 run.py 출력 JSON을 쓴다.
개발 출력 형식은 매핑 설정 파일(--map)로 맞춘다 — 형식은 engine/README.md '대조 매핑' 절.
권리자별로 단계 번호가 가장 작은 차이(계약 · 수취인 무관)를 '처음 갈라진 단계'로 표시한다.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import run_settlement  # noqa: E402
from core.csvio import read_table, write_table  # noqa: E402
from core.money import D, eq, to_json  # noqa: E402
from core.steps import BY_CODE, BY_NO, step_no  # noqa: E402

KEYS = ("rights_holder_id", "contract_id", "payee_id", "line_id")


def _dig(obj, path):
    for p in [x for x in (path or "").split(".") if x]:
        obj = obj[p]
    return obj


def load_dev_rows(path, cfg):
    fmt = cfg.get("dev_format") or ("json" if str(path).lower().endswith(".json") else "csv")
    if fmt == "csv":
        return read_table(path)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _dig(data, cfg.get("json_rows"))


def _norm_step(v, alias):
    """개발 쪽 단계 표기(번호 · 코드 · 별칭) → 스텝 코드."""
    if v is None:
        return None
    v = str(v).strip()
    if v in alias:
        v = alias[v]
    if v.isdigit() and int(v) in BY_NO:
        return BY_NO[int(v)].code
    return v.upper()


def dev_values(rows, cfg):
    """개발 행 → {(권리자, 수취인, 라인, 단계, 필드): (값, 개발 컬럼)}."""
    keys = cfg.get("keys", {})
    id_alias = cfg.get("id_alias", {})
    out = {}

    def key_of(r):
        k = []
        for name in KEYS:
            col = keys.get(name)
            v = r.get(col) if col else None
            v = None if v in ("", None) else str(v)
            v = id_alias.get(name, {}).get(v, v)
            k.append(v)
        return tuple(k)

    if cfg.get("layout", "wide") == "wide":
        for r in rows:
            base = key_of(r)
            for col, tgt in cfg.get("columns", {}).items():
                if col not in r:
                    continue
                v = r[col]
                out[base + (tgt["step_code"], tgt["field"])] = (None if v in ("", None) else v, col)
    else:
        lc = cfg["long"]
        alias = lc.get("step_alias", {})
        falias = lc.get("field_alias", {})
        for r in rows:
            step = _norm_step(r.get(lc["step_code"]), alias)
            field = r.get(lc["field"])
            field = falias.get(field, field)
            v = r.get(lc["value"])
            out[key_of(r) + (step, field)] = (None if v in ("", None) else v, lc["value"])
    return out


def calc_values(result):
    """계산기 values → {(권리자, 계약, 수취인, 라인, 단계, 필드): 값}. 같은 키가 다시 나오면(재검증) 마지막 값."""
    out = {}
    for v in result["values"]:
        out[tuple(v.get(k) for k in KEYS) + (v["step_code"], v["field"])] = v["value"]
    return out


def calc_lookup(calc, key):
    """개발 키에 계약 · 라인이 없으면(None) 그 축은 가리지 않고 찾는다. 라인 없는 합계 행이 있으면 그것을,
    없으면 라인 행들을 합친다(수치 합)."""
    if key in calc:
        return True, calc[key]
    holder, contract, payee, line, step, field = key
    hits = [(k, v) for k, v in calc.items() if k[0] == holder and k[2] == payee and k[4] == step and k[5] == field
            and (contract is None or k[1] == contract) and (line is None or k[3] == line)]
    if line is None and any(k[3] is None for k, _ in hits):
        hits = [(k, v) for k, v in hits if k[3] is None]
    vals = [v for _, v in hits]
    if not vals:
        return False, None
    if len(vals) == 1 or all(v == vals[0] for v in vals):
        return True, vals[0]
    try:
        return True, to_json(sum(D(v) for v in vals))
    except Exception:
        return True, vals[-1]


def compare(result, dev, cfg):
    tol = cfg.get("tolerance", 0)
    calc = calc_values(result)
    rows = []
    for k, (d, col) in dev.items():
        found, c = calc_lookup(calc, k)
        if not found:
            status = "CALC_MISSING"
        else:
            status = "OK" if eq(c, d, tol) else "DIFF"
        rows.append(row_of(k, c, d, status, col))
    if cfg.get("include_calc_only"):
        for k, c in calc.items():
            if k not in dev and (k[:1] + (None,) + k[2:]) not in dev:
                rows.append(row_of(k, c, None, "DEV_MISSING", None))
    rows.sort(key=lambda r: (str(r["rights_holder_id"]), r["step_no"], str(r["contract_id"] or ""),
                             str(r["payee_id"] or ""), str(r["line_id"] or ""), r["field"]))
    groups = defaultdict(list)
    for r in rows:
        groups[r["rights_holder_id"]].append(r)  # 권리자 단위: 계약 · 수취인 행을 함께 보고 가장 앞 단계를 찾는다
    out_groups = []
    for holder, rs in groups.items():
        bad = [r for r in rs if r["status"] in ("DIFF", "CALC_MISSING")]
        fd = None
        if bad:
            n = min(r["step_no"] for r in bad)
            first = [r for r in bad if r["step_no"] == n]
            fd = {"step_no": n, "step_code": first[0]["step_code"],
                  "step_name": BY_CODE[first[0]["step_code"]].name if first[0]["step_code"] in BY_CODE else None,
                  "fields": sorted({r["field"] for r in first}), "rows": first}
        out_groups.append({"rights_holder_id": holder, "payee_id": None, "first_divergence": fd, "rows": rs})
    cnt = defaultdict(int)
    for r in rows:
        cnt[r["status"]] += 1
    summary = {"compared": len(rows), "ok": cnt["OK"], "diff": cnt["DIFF"],
               "calc_missing": cnt["CALC_MISSING"], "dev_missing": cnt["DEV_MISSING"], "tolerance": tol,
               "diverged_groups": sum(1 for g in out_groups if g["first_divergence"])}
    return {"summary": summary, "groups": out_groups, "rows": rows}


def row_of(k, c, d, status, col):
    holder, contract, payee, line, step, field = k
    try:
        diff = to_json(D(d) - D(c)) if status == "DIFF" else None
    except Exception:
        diff = None
    return {"rights_holder_id": holder, "contract_id": contract, "payee_id": payee, "line_id": line,
            "step_no": step_no(step), "step_code": step, "field": field, "calc": c, "dev": d, "diff": diff,
            "status": status, "dev_column": col}


def main(argv=None):
    ap = argparse.ArgumentParser(description="계산기 결과 vs 개발 결과 대조")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="계산기 입력 JSON(이 자리에서 계산)")
    src.add_argument("--calc", help="이미 계산한 run.py 출력 JSON")
    ap.add_argument("--dev", required=True, help="개발 시스템 출력(CSV/JSON)")
    ap.add_argument("--map", required=True, help="컬럼 매핑 설정 JSON")
    ap.add_argument("--html", help="대조 HTML")
    ap.add_argument("--csv", help="차이 표 CSV")
    ap.add_argument("--json", help="대조 결과 JSON")
    args = ap.parse_args(argv)

    cfg = json.loads(Path(args.map).read_text(encoding="utf-8"))
    if args.input:
        result = run_settlement(json.loads(Path(args.input).read_text(encoding="utf-8")))
    else:
        result = json.loads(Path(args.calc).read_text(encoding="utf-8"))
    dev = dev_values(load_dev_rows(args.dev, cfg), cfg)
    cmp = compare(result, dev, cfg)

    if args.csv:
        write_table(args.csv, cmp["rows"])
    if args.json:
        Path(args.json).write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html:
        from report import render_compare_html
        Path(args.html).parent.mkdir(parents=True, exist_ok=True)
        Path(args.html).write_text(render_compare_html(cmp, result), encoding="utf-8")

    s = cmp["summary"]
    print(f"비교 {s['compared']}건 · 일치 {s['ok']} · 차이 {s['diff']} · 계산기 값 없음 {s['calc_missing']}"
          f" · 개발 값 없음 {s['dev_missing']} · 갈라진 권리자 {s['diverged_groups']}")
    for g in cmp["groups"]:
        fd = g["first_divergence"]
        if not fd:
            continue
        r = fd["rows"][0]
        print(f"  {g['rights_holder_id']} (수취인 {r['payee_id'] or '-'}): 처음 갈라진 단계 {fd['step_no']} {fd['step_code']}"
              f" — {r['field']}{'(' + r['line_id'] + ')' if r['line_id'] else ''} 계산기 {r['calc']} · 개발 {r['dev']}")
    return 1 if s["diverged_groups"] else 0


if __name__ == "__main__":
    sys.exit(main())
