"""JSON ↔ CSV 변환(스키마와 무관한 표 단위 변환).

입력 JSON = { 스칼라 필드..., "<표 이름>": [ {컬럼: 값}, ... ], ... }
CSV 폴더 = <표 이름>.csv 파일 여럿 + _meta.json(스칼라 필드).
CSV는 UTF-8 BOM(엑셀 호환)으로 쓰고, 읽을 때 BOM 유무 모두 받는다.
"""

import csv
import json
from pathlib import Path

META = "_meta.json"


def _cell(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return v


def write_table(path, rows, columns=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = []
        for r in rows:
            for k in r:
                if k not in columns:
                    columns.append(k)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(r.get(k)) for k in columns})


def parse_cell(v):
    """빈 칸 → None, true/false → bool, [..]/{..} → JSON(중첩 배열 · 객체), 그 밖은 문자열(금액은 엔진이 Decimal로 읽음)."""
    if v is None or v == "":
        return None
    if v in ("true", "false"):
        return v == "true"
    if v[:1] in "[{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def read_table(path):
    """CSV → 행 목록."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [{k: parse_cell(v) for k, v in r.items()} for r in csv.DictReader(f)]


def json_to_csv_dir(data, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {}
    for k, v in data.items():
        if isinstance(v, list) and all(isinstance(r, dict) for r in v):
            write_table(out_dir / f"{k}.csv", v)
        else:
            meta[k] = v
    (out_dir / META).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def csv_dir_to_json(in_dir):
    in_dir = Path(in_dir)
    data = {}
    meta = in_dir / META
    if meta.exists():
        data.update(json.loads(meta.read_text(encoding="utf-8")))
    for p in sorted(in_dir.glob("*.csv")):
        data[p.stem] = read_table(p)
    return data
