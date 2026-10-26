"""정본 위치 색인 생성 — 화면 코드별로 정본 · screen_spec 문서 › 절 › 줄을 모은다.

출력: scripts/qa/reports/review/canon_index.md (작업 로그 · 개정 이력 제외)
사용: python scripts/qa/build_canon_index.py
정본 문서가 바뀌어 줄 번호가 밀리면 다시 돌린다(작업자는 이 색인으로 위치를 찾아 그 근처만 읽는다).
"""
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "scripts", "qa", "reports", "review", "canon_index.md")

PREFIX = "USER|ORD|RFD|SETT|INST|BOOK|PROD|PROM|BRD|CONF|DASH|STAT|LOGIN|VEND|PTNR"
CODE = re.compile(r"(?<![A-Z0-9-])(?:ADMN-)?(" + PREFIX + r")-(\d{3})(?![0-9])")
HEAD = re.compile(r"^\s*(#{1,6})\s+(.*)$")
# 개정 이력 표 행 · 작업 로그 표 행
SKIP_ROW = re.compile(r"^\|\s*\**v\d+\.\d+|^\|\s*20\d\d-\d\d-\d\d\s*\|")


def sources():
    yield os.path.join(ROOT, "README.md")
    yield os.path.join(ROOT, "PROJECT_STATE.md")
    docs = os.path.join(ROOT, "docs")
    for f in sorted(os.listdir(docs)):
        if f.endswith(".md"):
            yield os.path.join(docs, f)
    spec = os.path.join(docs, "screen_spec")
    for f in sorted(os.listdir(spec)):
        if f.endswith(".md") and f[:2].isdigit():
            yield os.path.join(spec, f)


def clean_head(t):
    t = re.sub(r"[*`]", "", t).strip()
    return t[:60]


def main():
    idx = defaultdict(lambda: defaultdict(list))  # code -> (doc, head) -> [lines]
    order = defaultdict(list)
    for path in sources():
        name = os.path.basename(path)
        head = ""
        skip_section = False
        with open(path, encoding="utf-8") as fh:
            for no, line in enumerate(fh, 1):
                m = HEAD.match(line)
                if m:
                    head = clean_head(m.group(2))
                    skip_section = ("작업 로그" in head) or ("개정 이력" in head) or ("Revision" in head)
                    continue
                if skip_section or SKIP_ROW.match(line):
                    continue
                for c in CODE.finditer(line):
                    code = f"{c.group(1)}-{c.group(2)}"
                    key = (name, head)
                    if key not in idx[code]:
                        order[code].append(key)
                    if no not in idx[code][key]:
                        idx[code][key].append(no)
    L = ["# 화면 코드별 정본 위치 색인 (자동 생성 · 작업 로그·개정 이력 제외)",
         "문서 › 절 : 줄. 이 줄 근처만 읽는다. 우선순위 README·PROJECT_STATE 1절 > 통합설계서·정산 00~04 > screen_spec(참고). 생성: `python scripts/qa/build_canon_index.py`", ""]
    for code in sorted(idx):
        L.append(f"## {code}")
        for key in order[code]:
            lines = idx[code][key]
            shown = ",".join(str(n) for n in lines[:8]) + (f" 외 {len(lines) - 8}" if len(lines) > 8 else "")
            L.append(f"- {key[0]} › {key[1] or '(머리말)'} : {shown}")
        L.append("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"[canon_index] 화면 코드 {len(idx)}개 → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
