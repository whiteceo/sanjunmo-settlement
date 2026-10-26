"""개발 저장소(D:\\Work\\sanjunmo, 읽기 전용)에서 화면별 명세의 바탕 색인을 뽑는다.

출력(dev_spec/_index/):
  routes.md      관리자 라우트 전체 — 이름 · 메서드 · URL · 컨트롤러@메서드 · 권한 단위 · 바로 위 주석
  requests.md    Admin 요청 검증 클래스별 rules() 원문
  schema.md      마이그레이션을 누적한 테이블별 컬럼(타입 · 주석)
  progress.md    config/dev-progress.php 화면 목록 + 커밋 Progress 줄 + 라우트 주석 · 커밋에 화면 코드가 나온 횟수
  meta.md        기준 dev 커밋

사용: python dev_spec/_tools/extract_dev.py [개발 저장소 경로]
"""
import os
import re
import subprocess
import sys
from collections import OrderedDict, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

DEV = sys.argv[1] if len(sys.argv) > 1 else r"D:\Work\sanjunmo"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_index")
os.makedirs(OUT, exist_ok=True)

SUFFIX = {
    "index": "can_view", "show": "can_view", "create": "can_create", "store": "can_create",
    "edit": "can_update", "update": "can_update", "destroy": "can_delete", "download": "can_download",
    "recalculate": "can_update", "status-sync": "can_update", "contracts": "can_view",
    "reset-verify-cap": "can_update", "nts-verify": "can_update",
}


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def git(*args):
    return subprocess.run(["git", "-C", DEV, *args], capture_output=True, text=True, encoding="utf-8").stdout


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ── 라우트 ──────────────────────────────────────────────
def parse_routes():
    src = read(os.path.join(DEV, "routes", "admin.php"))
    lines = src.split("\n")
    stack = []  # (prefix, name, permission_checked)
    rows = []
    buf, comments, start = "", [], 0
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if not buf:
            if s.startswith("//"):
                comments.append(s[2:].strip())
                continue
            if not s:
                comments = []
                continue
            if s.startswith("});") or s == "}":
                if s.startswith("});") and stack:
                    stack.pop()
                comments = []
                continue
            start = i
        buf += " " + s
        if buf.rstrip().endswith("{") and "group(function" in buf:
            pm = re.search(r"Route::prefix\((['\"])(.*?)\1\)", buf)
            if "config('admin.prefix')" in buf:
                prefix = "{admin}"
            else:
                prefix = pm.group(2) if pm else ""
            nm = re.search(r"->name\('([^']*)'\)", buf)
            perm = "AdminPermissionMiddleware" in buf
            stack.append((prefix, nm.group(1) if nm else "", perm, " ".join(comments)))
            buf, comments = "", []
            continue
        if not buf.rstrip().endswith(";"):
            continue
        m = re.search(r"Route::(get|post|put|patch|delete|match)\(\s*(?:\[[^\]]*\],\s*)?'([^']*)'\s*,\s*(.*)", buf)
        if m:
            method, uri, rest = m.group(1).upper(), m.group(2), m.group(3)
            cm = re.search(r"\[(\w+)::class,\s*'(\w+)'\]", rest)
            action = f"{cm.group(1)}@{cm.group(2)}" if cm else ("closure" if "fn ()" in rest or "function" in rest else rest[:40])
            nm = re.findall(r"->name\('([^']*)'\)", rest)
            name = "".join(f[1] for f in stack) + (nm[-1] if nm else "")
            parts = [f[0] for f in stack if f[0] not in ("", "/")] + ([uri] if uri not in ("", "/") else [])
            url = "/" + "/".join(parts)
            perm_checked = any(f[2] for f in stack)
            suffix = name.rsplit(".", 1)[-1] if nm else ""
            perm = (SUFFIX.get(suffix, "차단(매핑 밖 접미사)") if perm_checked else "메뉴 권한 밖(로그인만)")
            ctx = " / ".join(f[3] for f in stack if f[3])
            rows.append(dict(line=start, method=method, url=url, name=name, action=action, perm=perm,
                             comment=" ".join(comments), ctx=ctx))
        buf, comments = "", []
    return rows


routes = parse_routes()
out = ["# 관리자 라우트 색인", "", "권한 단위 = 라우트 이름 접미사 → AdminPermissionService::SUFFIX_PERMISSIONS. "
       "메뉴는 라우트 이름의 목록형(…index)으로 정규화해 admin_menus 와 맞춘다.", "",
       "| 줄 | 메서드 | URL | 라우트 이름 | 컨트롤러@메서드 | 권한 | 주석 |", "|---|---|---|---|---|---|---|"]
for r in routes:
    c = (r["comment"] or "").replace("|", "\\|")
    out.append(f"| {r['line']} | {r['method']} | `{r['url']}` | `{r['name']}` | {r['action']} | {r['perm']} | {c} |")
write("routes.md", "\n".join(out) + "\n")

# ── 요청 검증 ────────────────────────────────────────────
req_dir = os.path.join(DEV, "app", "Http", "Requests", "Admin")
out = ["# Admin 요청 검증(rules) 색인", ""]
for fn in sorted(os.listdir(req_dir)):
    if not fn.endswith(".php"):
        continue
    src = read(os.path.join(req_dir, fn))
    parent = re.search(r"class \w+ extends (\w+)", src)
    out.append(f"## {fn[:-4]}" + (f" (extends {parent.group(1)})" if parent else ""))
    consts = re.findall(r"(?:public|private|protected)? ?const (\w+) = (.*?);", src, re.S)
    for k, v in consts:
        v = re.sub(r"\s+", " ", v)
        out.append(f"- const `{k}` = {v[:400]}")
    m = re.search(r"function rules\(\)[^{]*\{(.*?)\n    \}", src, re.S)
    if m:
        out += ["```php", m.group(1).strip("\n"), "```"]
    a = re.search(r"function attributes\(\)[^{]*\{(.*?)\n    \}", src, re.S)
    if a:
        out += ["attributes:", "```php", a.group(1).strip("\n"), "```"]
    out.append("")
write("requests.md", "\n".join(out) + "\n")

# ── 스키마 ──────────────────────────────────────────────
mig_dir = os.path.join(DEV, "database", "migrations")
tables = OrderedDict()
col_re = re.compile(r"\$table->(\w+)\(\s*'(\w+)'([^;]*);")
for fn in sorted(os.listdir(mig_dir)):
    src = read(os.path.join(mig_dir, fn))
    if "function down" in src:
        src = src[:src.find("function down")]  # 되돌리기 쪽 dropColumn 은 보지 않는다
    for blk in re.finditer(r"Schema::(create|table)\(\s*'(\w+)'\s*,\s*function.*?\n\s*\}\);", src, re.S):
        kind, t = blk.group(1), blk.group(2)
        cols = tables.setdefault(t, OrderedDict())
        body = blk.group(0)
        if kind == "create":
            cols.setdefault("__created", fn)
            if "$table->id()" in body:
                cols.setdefault("id", dict(type="id", flags="", comment="PK", mig=fn[:17]))
        for cm in col_re.finditer(body):
            typ, col, rest = cm.groups()
            if typ in ("dropColumn",):
                cols.pop(col, None)
                continue
            if typ in ("index", "unique", "foreign", "dropIndex", "dropUnique", "dropForeign", "primary"):
                continue
            if typ == "renameColumn":
                nm = re.search(r"'(\w+)'", rest)
                if nm and col in cols:
                    cols[nm.group(1)] = cols.pop(col)
                continue
            prev = cols.get(col, {})
            com = re.search(r"->comment\(\s*'((?:[^'\\]|\\.)*)'", rest)
            flags = [f for f in ("nullable", "unique", "change") if f"->{f}(" in rest]
            args = re.match(r"\s*,\s*([^)]*)\)", rest)
            cols[col] = dict(type=typ + (f"({args.group(1).strip()})" if args and args.group(1).strip() else ""),
                             flags=",".join(flags), comment=com.group(1) if com else prev.get("comment", ""), mig=fn[:17])
        for dm in re.finditer(r"dropColumn\(\s*\[?([^\])]*)", body):
            for c in re.findall(r"'(\w+)'", dm.group(1)):
                cols.pop(c, None)
    for dm in re.finditer(r"Schema::(?:dropIfExists|drop)\(\s*'(\w+)'", src):
        tables.pop(dm.group(1), None)
out = ["# 테이블 · 컬럼 색인 (마이그레이션 누적)", "", "타입 뒤 인자 · nullable 등 플래그 · 주석 · 마지막으로 바꾼 마이그레이션.", ""]
for t, cols in tables.items():
    out.append(f"## {t}")
    out.append("| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |")
    out.append("|---|---|---|---|---|")
    for c, d in cols.items():
        if c == "__created":
            continue
        out.append(f"| `{c}` | {d['type']} | {d['flags']} | {d['comment'].replace('|', '/')} | {d['mig']} |")
    out.append("")
write("schema.md", "\n".join(out) + "\n")

# ── 진행 상태 ────────────────────────────────────────────
cfg = read(os.path.join(DEV, "config", "dev-progress.php"))
screens = re.findall(r"'(ADMN-[A-Z]+-\d+(?:-[A-Z0-9]+)?)' => \['([^']*)', '([^']*)'\]", cfg)
initial = dict((k, v) for k, v in re.findall(r"'(ADMN-[\w-]+)' => \['([^']*)'", cfg.split("'initial'")[1])) if "'initial'" in cfg else {}
log = git("log", "--format=%h%x09%s%n%b%x00", "dev")
commits = [c.strip() for c in log.split("\x00") if c.strip()]
prog = defaultdict(list)
mention = defaultdict(int)
for c in commits:
    for ln in c.split("\n"):
        if ln.startswith("Progress:"):
            for code in re.findall(r"ADMN-[A-Z]+-\d+(?:-[A-Z]\d+)?", ln):
                prog[code].append(ln[9:].strip()[:160])
    for code in set(re.findall(r"ADMN-[A-Z]+-\d+(?:-[A-Z]\d+)?", c)):
        mention[code] += 1
route_src = read(os.path.join(DEV, "routes", "admin.php"))
out = ["# 개발 진행 상태 (config/dev-progress.php + 커밋)", "",
       "판정: 라우트 주석 또는 커밋에 화면 코드가 나오면 '구현 흔적 있음'. Progress 줄이 있으면 그 상태가 우선.", "",
       "| 화면 코드 | 화면명 | 담당 | 초기값 | 커밋 언급 수 | 라우트 주석 | 최신 Progress |", "|---|---|---|---|---|---|---|"]
seen = set()
for code, nm, who in screens:
    if code in seen:
        continue
    seen.add(code)
    in_route = "있음" if code in route_src else ""
    p = prog.get(code, [""])[0].replace("|", "/")
    out.append(f"| {code} | {nm} | {who} | {initial.get(code, '')} | {mention.get(code, 0)} | {in_route} | {p} |")
write("progress.md", "\n".join(out) + "\n")

head = git("log", "-1", "--format=%H %ci %s", "dev").strip()
write("meta.md", f"# 기준 개발 커밋\n\n- 저장소: whiteceo 로컬 클론 `{DEV}` (dev 브랜치, 읽기 전용)\n- 커밋: `{head}`\n"
      f"- 라우트 {len(routes)}개 · 테이블 {len(tables)}개 · 화면 {len(seen)}개\n")
print(f"routes={len(routes)} tables={len(tables)} screens={len(seen)} head={head[:9]}")
