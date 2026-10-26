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
# 마이그레이션을 파일 순서대로 다시 돌려 테이블별 최종 컬럼을 만든다. up() 만 본다(down() 은 괄호 짝으로 잘라낸다).
# 잡는 패턴: Schema::create · table 블록(function · fn 둘 다), timestamps() · softDeletes(),
# '컬럼' => fn (Blueprint $t) => $t->타입('컬럼') 배열과 $this->헬퍼('테이블', …) 호출(widen 포함),
# 한 줄 · 여러 줄 dropColumn([...]), foreach ([...] as $c) { … dropColumn($c) }, renameColumn,
# Schema::rename · drop · dropIfExists, DB::statement("ALTER TABLE t MODIFY [COLUMN] c 타입 …").
mig_dir = os.path.join(DEV, "database", "migrations")
COL_TYPES = ("string|char|text|longText|mediumText|tinyText|integer|bigInteger|unsignedBigInteger|unsignedInteger|"
             "tinyInteger|unsignedTinyInteger|smallInteger|unsignedSmallInteger|mediumInteger|unsignedMediumInteger|"
             "boolean|decimal|unsignedDecimal|date|dateTime|dateTimeTz|timestamp|timestampTz|time|year|json|jsonb|"
             "foreignId|enum|set|uuid|ulid|ipAddress|macAddress|binary|float|double|bigIncrements|increments")
col_def_re = re.compile(r"\$(\w+)->(%s)\(\s*(?:'(\w+)'|\$(\w+))" % COL_TYPES)
TABLE_LIT = re.compile(r"(?:Schema::(?:table|create|hasColumn|hasTable)|\$this->\w+)\(\s*'(\w+)'")


def split_top(inner):
    """괄호 안쪽 문자열을 최상위 ',' 로 나눈다."""
    parts, depth, q, cur = [], 0, None, ""
    i = 0
    while i < len(inner):
        ch = inner[i]
        if q:
            cur += ch
            if ch == "\\" and i + 1 < len(inner):
                cur += inner[i + 1]
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
            cur += ch
        elif ch in "([{":
            depth += 1
            cur += ch
        elif ch in ")]}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip():
        parts.append(cur.strip())
    return parts


def unquote(v):
    v = v.strip()
    m = re.fullmatch(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", v, re.S)
    return (m.group(1) if m.group(1) is not None else m.group(2)) if m else None


def array_rows(lit):
    """'[ ... ]' 리터럴 → [(키 또는 None, 값 원문)]."""
    rows = []
    for part in split_top(lit.strip()[1:-1]):
        km = re.match(r"('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")\s*=>\s*(.*)$", part, re.S)
        rows.append((unquote(km.group(1)), km.group(2).strip()) if km else (None, part))
    return rows


def array_literal(src, expr, pos):
    """foreach 대상 식 → 배열 리터럴 원문(리터럴 · self::상수 · 앞에서 대입한 $변수)."""
    expr = expr.strip()
    if expr.startswith("["):
        return expr
    cm = re.fullmatch(r"(?:self|static)::(\w+)", expr)
    if cm:
        d = re.search(r"const\s+%s\s*=\s*\[" % cm.group(1), src)
        return src[d.end() - 1:match_brace(src, d.end() - 1, "[", "]") + 1] if d else None
    vm = re.fullmatch(r"\$(\w+)", expr)
    if vm:
        last = None
        for a in re.finditer(r"\$%s\s*=(?![=>])\s*" % vm.group(1), src[:pos]):
            last = a
        if last:
            b = src.find("[", last.end())
            if b >= 0 and b < stmt_end(src, last.end()):
                return src[b:match_brace(src, b, "[", "]") + 1]
    return None


def foreach_bindings(src, pos):
    """pos 를 감싸는 foreach 들의 반복 행 — [{변수: 문자열}] (안쪽 foreach 우선)."""
    found = []
    for m in re.finditer(r"foreach\s*\(", src[:pos]):
        cp = match_brace(src, m.end() - 1, "(", ")")
        head = src[m.end():cp]
        ob = src.find("{", cp)
        if ob < 0 or ob > pos or match_brace(src, ob) < pos:
            continue
        hm = re.match(r"(.*)\s+as\s+(.*)$", head, re.S)
        if not hm:
            continue
        lit = array_literal(src, hm.group(1), m.start())
        if not lit:
            continue
        asc = hm.group(2).strip()
        km = re.match(r"\$(\w+)\s*=>\s*(.*)$", asc, re.S)
        kvar, vexp = (km.group(1), km.group(2).strip()) if km else (None, asc)
        rows = []
        for k, v in array_rows(lit):
            b = {}
            if kvar and k is not None:
                b[kvar] = k
            if vexp.startswith("["):
                names = [re.sub(r"^\$", "", x.strip()) for x in vexp[1:-1].split(",")]
                vals = [unquote(x) for x in split_top(v.strip()[1:-1])] if v.strip().startswith("[") else []
                for n, val in zip(names, vals):
                    if n and val is not None:
                        b[n] = val
            elif vexp.startswith("$"):
                if unquote(v) is not None:
                    b[vexp[1:]] = unquote(v)
                elif k is None:
                    continue
            rows.append(b)
        found.append((m.start(), rows))
    return [r for _, r in sorted(found, key=lambda x: -x[0])]


def resolve_names(src, pos, var):
    """$var 가 가리키는 이름 목록 — 감싸는 foreach 의 반복 값, 없으면 앞에서 대입한 배열 리터럴의 문자열들."""
    for rows in foreach_bindings(src, pos):
        names = [r[var] for r in rows if var in r]
        if names:
            return names
    lit = array_literal(src, "$" + var, pos)
    if lit:
        inner = lit
        # array_values(array_filter([...])) 처럼 감싼 경우도 첫 배열 리터럴을 쓴다
        return [unquote(v) for k, v in array_rows(inner) if k is None and unquote(v) is not None]
    return []


def match_brace(s, i, open_ch="{", close_ch="}"):
    """s[i] 가 여는 괄호일 때 짝이 되는 닫는 괄호 위치. 문자열 안 괄호는 건너뛴다."""
    depth, q, j = 0, None, i
    while j < len(s):
        ch = s[j]
        if q:
            if ch == "\\":
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return len(s) - 1


def strip_down(src):
    m = re.search(r"public function down\(\)[^{]*\{", src)
    if not m:
        return src
    end = match_brace(src, m.end() - 1)
    return src[:m.start()] + src[end + 1:]


def stmt_end(s, i):
    """i 에서 시작한 체인의 끝(최상위 ';' · ',' 또는 바깥 괄호가 닫히는 곳)."""
    depth, q, j = 0, None, i
    while j < len(s):
        ch = s[j]
        if q:
            if ch == "\\":
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                return j
            depth -= 1
        elif ch in ";," and depth == 0:
            return j
        j += 1
    return j


def col_entry(typ, rest):
    com = re.search(r"->comment\(\s*'((?:[^'\\]|\\.)*)'", rest) or re.search(r'->comment\(\s*"((?:[^"\\]|\\.)*)"', rest)
    flags = [f for f in ("nullable", "unique", "change") if f"->{f}(" in rest]
    if "->nullable(false)" in rest and "nullable" in flags:
        flags.remove("nullable")
    args = re.match(r"\s*,\s*([^)]*)\)", rest)
    a = args.group(1).strip() if args and typ != "enum" else ""
    return dict(type=typ + (f"({a})" if a else ""), flags=",".join(flags), comment=com.group(1) if com else "")


def table_for(src, pos, chunk_start, chunk_end):
    """블록 밖 컬럼 정의의 테이블: 같은 문장 앞쪽 → 같은 함수 안 가장 가까운 뒤쪽 → 앞쪽 테이블 리터럴."""
    head = src[max(chunk_start, src.rfind(";", 0, pos) + 1):pos]
    m = list(TABLE_LIT.finditer(head))
    if m:
        return m[-1].group(1)
    after = TABLE_LIT.search(src, pos, chunk_end)
    if after:
        return after.group(1)
    before = list(TABLE_LIT.finditer(src, chunk_start, pos))
    return before[-1].group(1) if before else None


tables = OrderedDict()


def apply(ev, fn):
    kind, t = ev[1], ev[2]
    if kind == "drop_table":
        tables.pop(t, None)
        return
    if kind == "rename_table":
        if t in tables:
            tables[ev[3]] = tables.pop(t)
        return
    cols = tables.setdefault(t, OrderedDict())
    if kind == "create":
        cols.setdefault("__created", fn)
    elif kind == "col":
        d = dict(ev[4])
        if d.pop("_guard", False) and ev[3] in cols and "change" not in d["flags"]:
            return  # if (! Schema::hasColumn(…)) 로 감싼 추가 — 이미 있으면 실행되지 않는다
        if not d["comment"]:
            d["comment"] = cols.get(ev[3], {}).get("comment", "")
        d["mig"] = fn[:17]
        cols[ev[3]] = d
    elif kind == "drop_col":
        cols.pop(ev[3], None)
    elif kind == "rename_col":
        if ev[3] in cols:
            tables[t] = OrderedDict((ev[4] if k == ev[3] else k, v) for k, v in cols.items())
    elif kind == "modify":
        prev = cols.get(ev[3], {})
        cols[ev[3]] = dict(type=ev[4], flags=ev[5], comment=prev.get("comment", ""), mig=fn[:17])


def guarded(src, pos):
    """pos 가 'if (! Schema::hasColumn(…)) { … }' 안에 있는지."""
    last = None
    for m in re.finditer(r"if\s*\(\s*!\s*Schema::hasColumn\(", src[:pos]):
        last = m
    if not last:
        return False
    ob = src.find("{", match_brace(src, src.find("(", last.start()), "(", ")"))
    return ob >= 0 and ob < pos <= match_brace(src, ob)


def block_events(body, base, t, evs, src):
    """Schema::create · table 블록 안의 컬럼 동작."""
    for m in re.finditer(r"\$\w+->id\(\)", body):
        evs.append((base + m.start(), "col", t, "id", dict(type="id", flags="", comment="PK")))
    for m in re.finditer(r"\$\w+->(timestamps|timestampsTz|nullableTimestamps)\(\)", body):
        for c in ("created_at", "updated_at"):
            evs.append((base + m.start(), "col", t, c, dict(type="timestamp", flags="nullable", comment="")))
    for m in re.finditer(r"\$\w+->softDeletes(?:Tz)?\(\s*(?:'(\w+)')?", body):
        evs.append((base + m.start(), "col", t, m.group(1) or "deleted_at", dict(type="timestamp", flags="nullable", comment="")))
    for m in re.finditer(r"\$\w+->rememberToken\(\)", body):
        evs.append((base + m.start(), "col", t, "remember_token", dict(type="string(100)", flags="nullable", comment="")))
    for m in re.finditer(r"\$\w+->(nullableMorphs|morphs)\(\s*'(\w+)'", body):
        fl = "nullable" if m.group(1).startswith("nullable") else ""
        evs.append((base + m.start(), "col", t, m.group(2) + "_type", dict(type="string(255)", flags=fl, comment="")))
        evs.append((base + m.start(), "col", t, m.group(2) + "_id", dict(type="unsignedBigInteger", flags=fl, comment="")))
    for m in col_def_re.finditer(body):
        rest = body[m.end():stmt_end(body, m.end(2))]
        names = [m.group(3)] if m.group(3) else resolve_names(src, base + m.start(), m.group(4))
        for c in names:
            evs.append((base + m.start(), "col", t, c, dict(col_entry(m.group(2), rest), _guard=guarded(src, base + m.start()))))
    for m in re.finditer(r"->renameColumn\(\s*'(\w+)'\s*,\s*'(\w+)'", body):
        evs.append((base + m.start(), "rename_col", t, m.group(1), m.group(2)))
    for m in re.finditer(r"->dropColumn\(", body):
        arg = body[m.end():match_brace(body, m.end() - 1, "(", ")")]
        names = re.findall(r"'(\w+)'", arg)
        vm = re.fullmatch(r"\s*\$(\w+)\s*", arg)
        if vm:
            names = resolve_names(src, base + m.start(), vm.group(1))
        for c in names:
            evs.append((base + m.start(), "drop_col", t, c))
    for m in re.finditer(r"->(dropTimestamps|dropSoftDeletes)\(", body):
        for c in (("created_at", "updated_at") if m.group(1) == "dropTimestamps" else ("deleted_at",)):
            evs.append((base + m.start(), "drop_col", t, c))


for fn in sorted(os.listdir(mig_dir)):
    src = strip_down(read(os.path.join(mig_dir, fn)))
    evs, covered = [], []
    # 1) Schema::create · table('리터럴', function {…} | fn (…) => …)
    for m in re.finditer(r"Schema::(create|table)\(\s*(?:'(\w+)'|\$(\w+))\s*,\s*(?:static\s+)?(function|fn)\b", src):
        kind = m.group(1)
        tnames = [m.group(2)] if m.group(2) else resolve_names(src, m.start(), m.group(3))
        if m.group(4) == "function":
            ob = src.find("{", m.end())
            cb = match_brace(src, ob)
        else:
            ob = m.end()
            cb = match_brace(src, src.find("(", m.start()), "(", ")")
        body = src[ob:cb + 1]
        covered.append((ob, cb))
        for t in tnames:
            if kind == "create":
                evs.append((m.start(), "create", t))
            block_events(body, ob, t, evs, src)
    # 2) 블록 밖 컬럼 정의('컬럼' => fn 배열, $this->widen 등 헬퍼 호출 인자)
    funcs = []
    for fm in re.finditer(r"function\s+\w+\s*\([^)]*\)[^{;]*\{", src):
        funcs.append((fm.start(), match_brace(src, fm.end() - 1)))
    for m in col_def_re.finditer(src):
        if any(a <= m.start() <= b for a, b in covered):
            continue
        cs, ce = min(((a, b) for a, b in funcs if a <= m.start() <= b), key=lambda x: x[1] - x[0], default=(0, len(src)))
        t = table_for(src, m.start(), cs, ce)
        if not t:
            continue
        rest = src[m.end():stmt_end(src, m.end(2))]
        for c in ([m.group(3)] if m.group(3) else resolve_names(src, m.start(), m.group(4))):
            evs.append((m.start(), "col", t, c, dict(col_entry(m.group(2), rest), _guard=guarded(src, m.start()))))
    # 3) 테이블 이름 바꾸기 · 지우기
    for m in re.finditer(r"Schema::rename\(\s*'(\w+)'\s*,\s*'(\w+)'", src):
        evs.append((m.start(), "rename_table", m.group(1), m.group(2)))
    for m in re.finditer(r"Schema::(?:dropIfExists|drop)\(\s*'(\w+)'", src):
        evs.append((m.start(), "drop_table", m.group(1)))
    # 4) 원시 SQL ALTER … MODIFY
    tok = r"`?(\{?\$\w+\}?|\w+)`?"
    for m in re.finditer(r"ALTER TABLE\s+%s\s+MODIFY\s+(?:COLUMN\s+)?%s\s+(\{\$\w+\}|[A-Za-z]+(?:\([^)]*\))?(?:\s+UNSIGNED)?)([^\"';]*)" % (tok, tok), src):
        parts = [m.group(1), m.group(2), m.group(3)]
        vars_ = [re.sub(r"[{}$]", "", x) for x in parts if "$" in x]
        rows = [{}]
        if vars_:
            rows = next((r for r in foreach_bindings(src, m.start()) if any(all(v in x for v in vars_) for x in r)), [])
        for row in rows:
            t, c, d = [row.get(re.sub(r"[{}$]", "", x)) if "$" in x else x for x in parts]
            if not (t and c and d):
                continue
            tail = m.group(4) if "$" not in m.group(3) else d
            tm = re.match(r"\s*([A-Za-z]+(?:\([^)]*\))?(?:\s+UNSIGNED)?)", d)
            fl = "" if re.search(r"NOT NULL", tail, re.I) else "nullable"
            evs.append((m.start(), "modify", t, c, tm.group(1).lower() if tm else d.lower(), ",".join(f for f in (fl, "sql") if f)))
    for ev in sorted(evs, key=lambda e: e[0]):
        apply(ev, fn)

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
