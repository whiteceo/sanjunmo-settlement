"""정산엔진 기준 계산기 실행.

    python engine/run.py --input in.json --out out.json [--csv out_csv/] [--html report.html]
    python engine/run.py --input-csv in_csv/ --out out.json
    python engine/run.py --input in.json --to-csv in_csv/      (입력 JSON → CSV 폴더 변환만)

출력 JSON = output.schema.json(권리자 → 계약 → 단계 · 수취인) + values(권리자 · 계약 · 수취인 · 라인 · 단계 · 필드 단위
결과값, 대조 · 테스트 기준) + trace(값마다 입력 · 수식 · 절사 전/후 · 정본 근거 · 잠정 여부) + issues(잠정 규칙 · 입력 부족).
"""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import run_settlement  # noqa: E402
from core.csvio import csv_dir_to_json, json_to_csv_dir, write_table  # noqa: E402

TRACE_COLS = ["seq", "step", "step_code", "rights_holder_id", "contract_id", "payee_id", "line_id", "agreement_id",
              "ref_id", "field", "inputs", "formula", "formula_code", "before_rounding", "rounding", "result",
              "canon_ref", "provisional", "note", "output"]


def load_input(args):
    if args.input_csv:
        return csv_dir_to_json(args.input_csv)
    return json.loads(Path(args.input).read_text(encoding="utf-8"))


def write_result_csv(result, out_dir):
    out_dir = Path(out_dir)
    write_table(out_dir / "values.csv", result["values"])
    write_table(out_dir / "trace.csv", [dict(e, **{k: v for k, v in e["scope"].items() if k != "line_key"})
                                        for e in result["trace"]], TRACE_COLS)
    write_table(out_dir / "continuity.csv", result["continuity"],
                ["account_type", "key", "prev_end", "new", "extinguished", "end", "ok"])
    write_table(out_dir / "issues.csv", result["issues"],
                ["kind", "question", "step_code", "rights_holder_id", "message", "ref"])
    payees = []
    for h in result["rights_holders"]:
        for c in h["contracts"]:
            for p in c["payees"]:
                row = {"rights_holder_id": h["rights_holder_id"], "contract_id": c["contract_id"], "payee_id": p["payee_id"]}
                for blk in ("TAX", "CLAIM", "PAYOUT"):
                    for k, v in p.get(blk, {}).items():
                        if not isinstance(v, (list, dict)):
                            row[f"{blk}.{k}"] = v
                payees.append(row)
    write_table(out_dir / "payees.csv", payees)


def main(argv=None):
    ap = argparse.ArgumentParser(description="정산엔진 기준 계산기(정본 02권 8.3절 1~11단계)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="입력 JSON")
    src.add_argument("--input-csv", help="입력 CSV 폴더(<표>.csv + _meta.json)")
    ap.add_argument("--out", help="출력 JSON 경로(생략 시 화면 요약만)")
    ap.add_argument("--csv", help="출력 CSV 폴더(values · trace · payees · continuity · issues)")
    ap.add_argument("--html", help="권리자별 단계표 HTML 보고서 경로")
    ap.add_argument("--to-csv", help="계산하지 않고 입력 JSON을 CSV 폴더로 변환")
    args = ap.parse_args(argv)

    data = load_input(args)
    if args.to_csv:
        json_to_csv_dir(data, args.to_csv)
        print(f"입력 CSV 변환: {args.to_csv}")
        return 0

    result = run_settlement(data)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.csv:
        write_result_csv(result, args.csv)
    if args.html:
        from report import render_html
        Path(args.html).parent.mkdir(parents=True, exist_ok=True)
        Path(args.html).write_text(render_html(result), encoding="utf-8")

    bad = [c for c in result["continuity"] if not c["ok"]]
    prov = sum(1 for e in result["trace"] if e.get("provisional"))
    print(f"정산월 {result['settlement_month']} · 상태 {result['status']} · 값 {len(result['values'])}건"
          f" · trace {len(result['trace'])}줄(잠정 {prov}) · 이월 연속성 불일치 {len(bad)}건"
          f" · 확인 필요 {len(result['issues'])}건 · 오류 {len(result['errors'])}건")
    for e in result["errors"]:
        print(f"  오류 {e['code']}: {e['message']}")
    return 1 if bad or result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
