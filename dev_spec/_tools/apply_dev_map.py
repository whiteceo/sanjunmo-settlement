"""prototype_clean 화면을 복사해 개발 이름을 입힌 prototype_dev 화면을 만든다.

사용: python dev_spec/_tools/apply_dev_map.py ADMN-USER-001 [ADMN-...]
  - 원본: prototype_clean/<코드>_baseline.html (읽기만)
  - 변경 목록: dev_spec/_maps/<코드>.py 의 OPS (찾을 문구 · 바꿀 문구 · 기대 건수)
  - 출력: prototype_dev/<코드>_baseline.html, 원본 상태는 prototype_dev/_SOURCES.md 에 기록
  - 기대 건수와 다른 항목이 하나라도 있으면 파일을 쓰지 않고 목록만 보여 준다(원본이 바뀌었을 때 손으로 맞출 곳).
  - 공통 파일(common-*.js · common-v84.css · fonts · img)은 prototype_clean 것을 그대로 복사한다(원본은 건드리지 않는다).
"""
import datetime
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "prototype_clean")
DST = os.path.join(ROOT, "prototype_dev")
MAPS = os.path.join(ROOT, "dev_spec", "_maps")
COMMON = ["common-master.js", "common-snb.js", "common-v84.css", "fonts", "img"]


def load_map(code):
    spec = importlib.util.spec_from_file_location(code.replace("-", "_"), os.path.join(MAPS, code + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, encoding="utf-8").stdout.strip()


def apply_ops(text, ops):
    errors = []
    for i, op in enumerate(ops):
        kind = op["kind"]
        if kind == "replace":
            n = text.count(op["find"])
            if n != op["count"]:
                errors.append(f"#{i} 기대 {op['count']}건 · 실제 {n}건: {op['find'][:90]!r}")
                continue
            text = text.replace(op["find"], op["replace"])
        elif kind == "regex":
            pat = re.compile(op["find"])
            n = len(pat.findall(text))
            if n != op["count"]:
                errors.append(f"#{i} 기대 {op['count']}건 · 실제 {n}건: /{op['find'][:90]}/")
                continue
            text = pat.sub(op["replace"], text)
        elif kind == "insert_before":
            n = text.count(op["anchor"])
            if n != 1:
                errors.append(f"#{i} 기준 문구 {n}건(1건이어야 함): {op['anchor'][:90]!r}")
                continue
            text = text.replace(op["anchor"], op["html"] + op["anchor"])
        elif kind == "insert_after":
            n = text.count(op["anchor"])
            if n != 1:
                errors.append(f"#{i} 기준 문구 {n}건(1건이어야 함): {op['anchor'][:90]!r}")
                continue
            text = text.replace(op["anchor"], op["anchor"] + op["html"])
        else:
            errors.append(f"#{i} 모르는 종류 {kind}")
    return text, errors


def summarize_sources():
    d = os.path.join(DST, "_sources")
    rows = []
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            rows.append(f.read().strip())
    head = ["# prototype_dev 원본 기록", "",
            "apply_dev_map.py가 만들 때마다 갱신한다(화면별 원본은 _sources/). 원본이 바뀌면 다시 돌리고, 건수 불일치는 dev_spec/_maps/<코드>.py를 고친다.", "",
            "| 화면 | 원본 prototype_clean 상태 | 원본 sha256(앞 12) | 맞춘 dev 커밋 | 변경 항목 수 | 생성 시각 |", "|---|---|---|---|---|---|"]
    tmp = os.path.join(DST, f"_SOURCES.md.{os.getpid()}")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(head + rows) + "\n")
    os.replace(tmp, os.path.join(DST, "_SOURCES.md"))


def build(code):
    src_name = f"{code}_baseline.html"
    src_path = os.path.join(SRC, src_name)
    with open(src_path, "rb") as f:
        raw = f.read()
    eol = "\r\n" if raw.count(b"\r\n") == raw.count(b"\n") else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    m = load_map(code)
    text, errors = apply_ops(text, m.OPS)
    if errors:
        print(f"[{code}] 중단 — 기대 건수 불일치 {len(errors)}건, 파일을 쓰지 않음")
        for e in errors:
            print("  ", e)
        return False
    os.makedirs(DST, exist_ok=True)
    with open(os.path.join(DST, src_name), "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", eol))
    for c in COMMON:
        s, d = os.path.join(SRC, c), os.path.join(DST, c)
        try:
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            elif os.path.exists(s):
                shutil.copy2(s, d)
        except OSError:
            pass  # 다른 작업자가 같은 공통 파일을 복사 중 — 내용이 같으므로 건너뛴다
    head = git("log", "-1", "--format=%h", "--", f"prototype_clean/{src_name}")
    dirty = git("status", "--porcelain", "--", f"prototype_clean/{src_name}")
    state = f"{head}" + (" + 미커밋 작업 트리" if dirty else "")
    sha = hashlib.sha256(raw).hexdigest()[:12]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # 화면마다 한 파일(여러 작업자가 동시에 돌려도 겹치지 않게). 목록은 summarize_sources()가 _SOURCES.md로 모은다
    os.makedirs(os.path.join(DST, "_sources"), exist_ok=True)
    with open(os.path.join(DST, "_sources", f"{code}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"| {code} | {state} | {sha} | {getattr(m, 'DEV_COMMIT', '?')} | {len(m.OPS)} | {now} |\n")
    summarize_sources()
    print(f"[{code}] 완료 — 변경 {len(m.OPS)}항목, 원본 {state} ({sha})")
    return True


if __name__ == "__main__":
    ok = all([build(c) for c in sys.argv[1:]])
    sys.exit(0 if ok else 1)
