r"""PHP판 ↔ 파이썬판 전건 대조(엔진 출력 JSON 전체: values · trace · 수취인 · 원장 · 이월 연속성 · issues).

    python engine/php/tests/parity.py [--php "php"]

입력: 04권 fixture(+변형) · 정본 결정 회귀 · 샘플 · 시나리오 입력을 엔진 입력으로 바꿔 engine/out/parity/에 쓰고,
파이썬판과 PHP판으로 각각 계산해 비교한다. PHP는 --php로 실행 파일을 주거나(PHP 8.4 + bcmath),
생략하면 php-wasm(node, D:\Work\_tools\phpwasm에 @php-wasm/node 설치)으로 phprun.mjs를 돌린다.
차이가 있으면 첫 8곳을 찍고 종료 코드 1.
"""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "tests"))

from adapter import build  # noqa: E402
from core import run_settlement  # noqa: E402
from run_tests import DECISIONS, FIXTURES, load_cases  # noqa: E402

OUT = ENGINE / "out" / "parity"
PHPWASM = Path(r"D:\Work\_tools\phpwasm")


def inputs():
    yield "sample", json.loads((ENGINE / "samples/sample/input.json").read_text(encoding="utf-8"))
    for p in sorted((ENGINE / "samples/scenario/inputs").glob("*.json")):
        yield "sc_" + p.stem, json.loads(p.read_text(encoding="utf-8"))
    for d in (FIXTURES, DECISIONS):
        for p in sorted(d.glob("*.json")):
            for fc in load_cases(p):
                data = copy.deepcopy(fc["input"]) if fc.get("engine_input") else build(fc["input"], fc["code"], fc.get("base"))[0]
                if data is not None:
                    yield "fx_" + fc["code"].replace("/", "_"), data


def norm(x):
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items()} if x else []
    if isinstance(x, list):
        return [norm(v) for v in x] if x else []
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def diff(a, b, path, out):
    if len(out) >= 8:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in list(a) + [k for k in b if k not in a]:
            if k not in a or k not in b:
                out.append(f"{path}/{k}: {'PHP에 없음' if k not in b else 'PHP에만 있음'}")
            else:
                diff(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: 길이 py {len(a)} · php {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: py {json.dumps(a, ensure_ascii=False)[:120]} | php {json.dumps(b, ensure_ascii=False)[:120]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--php", help="PHP 8.4 실행 파일(생략 시 php-wasm)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.json"):
        f.unlink()
    names = []
    for name, data in inputs():
        data = json.loads(json.dumps(data, default=str))
        (OUT / f"{name}.in.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        (OUT / f"{name}.py.json").write_text(json.dumps(run_settlement(copy.deepcopy(data)), ensure_ascii=False), encoding="utf-8")
        names.append(name)
    cmd = ([args.php, str(HERE / "run_cases.php"), str(OUT)] if args.php else
           ["node", str(HERE / "phprun.mjs"), str(HERE / "run_cases.php"), str(OUT)])
    env_cwd = None if args.php else str(PHPWASM)
    r = subprocess.run(cmd, cwd=env_cwd, capture_output=True, text=True, encoding="utf-8")
    if r.stdout.strip():
        print(r.stdout.strip())
    bad = 0
    for name in names:
        pf = OUT / f"{name}.php.json"
        if not pf.exists():
            bad += 1
            print("PHP 결과 없음", name)
            continue
        out = []
        diff(norm(json.loads((OUT / f"{name}.py.json").read_text(encoding="utf-8"))), norm(json.loads(pf.read_text(encoding="utf-8"))), "", out)
        if out:
            bad += 1
            print("차이", name)
            for o in out:
                print("   ", o)
    print(f"대조 {len(names)}건 · 일치 {len(names) - bad} · 차이 {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
