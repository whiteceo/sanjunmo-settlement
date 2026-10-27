"""PHP판 계산기 웹 페이지 만들기.

    python engine/php/web/build_web.py

template.html에 PHP 소스(engine/php/src) · 한국어 업무 용어(labels.json) · 입력 스키마 · tax_table.json · 예시 입력(샘플 · 시나리오 · 04권 Case · 부록 D · 정본 결정)과
같은 입력의 파이썬 판 계산 값(values, 페이지에서 PHP 결과와 대조)을 넣어 engine/out/web/index.html을 만든다.
브라우저용 PHP 8.4(php-wasm 3.1.57) wasm은 gzip해서 index.html 옆에 둔다(내려받기는 처음 한 번, --wasm-dir로 재사용).
"""

import argparse
import copy
import gzip
import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "tests"))

from adapter import build  # noqa: E402
from core import run_settlement  # noqa: E402
from run_tests import DECISIONS, FIXTURES, load_cases  # noqa: E402

PHPWASM = "3.1.57"
WASM_URL = "https://cdn.jsdelivr.net/npm/@php-wasm/web-8-4@{v}/{kind}/8_4_25/php_8_4.wasm"
GROUPS = [("sample", "샘플"), ("scenario", "시나리오 권리자"), ("case", "04권 Case"), ("appendix", "04권 부록 D"),
          ("decision", "정본 결정 회귀")]


def plain(data):
    return json.loads(json.dumps(data, default=str))


def examples():
    out = []

    def add(group, key, label, data):
        data = plain(data)
        res = run_settlement(copy.deepcopy(data))
        out.append({"group": group, "key": key, "label": label, "input": data, "py_values": res["values"],
                    "py_status": res["status"]})

    add("sample", "sample", "샘플 입력(가상 값, 2026-09)", json.loads((ENGINE / "samples/sample/input.json").read_text(encoding="utf-8")))
    for p in sorted((ENGINE / "samples/scenario/inputs").glob("*.json")):
        add("scenario", "sc_" + p.stem, p.stem, json.loads(p.read_text(encoding="utf-8")))
    for d in (FIXTURES, DECISIONS):
        for p in sorted(d.glob("*.json")):
            for fc in load_cases(p):
                data = copy.deepcopy(fc["input"]) if fc.get("engine_input") else build(fc["input"], fc["code"], fc.get("base"))[0]
                if data is None:
                    continue
                code = fc["code"]
                group = "decision" if code.startswith("DEC-") else "case" if code.startswith("CASE-") else "appendix"
                add(group, code, f"{code} {fc.get('title') or ''}".strip(), data)
    return out


def php_sources():
    files = {}
    root = ENGINE / "php"
    for p in [root / "engine.php", *sorted((root / "src").rglob("*.php"))]:
        files["php/" + p.relative_to(root).as_posix()] = p.read_text(encoding="utf-8")
    files["tax_table.json"] = (ENGINE / "tax_table.json").read_text(encoding="utf-8")
    return files


def wasm(out_dir, cache):
    for kind in ("jspi", "asyncify"):
        dst = out_dir / f"php_{kind}.gz.wasm"  # gzip 내용 · 서빙 형식 때문에 .wasm 이름
        src = (Path(cache) / f"php_{kind}.wasm.gz") if cache else None
        if src and src.exists():
            dst.write_bytes(src.read_bytes())
            continue
        raw = urllib.request.urlopen(WASM_URL.format(v=PHPWASM, kind=kind)).read()
        dst.write_bytes(gzip.compress(raw, 9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ENGINE / "out" / "web"))
    ap.add_argument("--wasm-dir", help="이미 받아 둔 php_<jspi|asyncify>.wasm.gz 폴더")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ex = examples()
    payload = {"phpwasm": PHPWASM, "groups": GROUPS, "examples": ex, "sources": php_sources(),
               "labels": json.loads((HERE / "labels.json").read_text(encoding="utf-8")),
               "schema": json.loads((ENGINE / "schema/input.schema.json").read_text(encoding="utf-8"))}
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    page = (HERE / "template.html").read_text(encoding="utf-8").replace("/*__PAYLOAD__*/null", blob)
    (out / "index.html").write_text(page, encoding="utf-8")
    wasm(out, args.wasm_dir)
    print(f"{out / 'index.html'} · 예시 {len(ex)}건 · {len(page.encode('utf-8')) // 1024}KB")


if __name__ == "__main__":
    main()
