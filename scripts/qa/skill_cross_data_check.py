#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Skill 3] 화면 간 데이터 대조기 (읽기 전용 QA 도구 — HTML을 수정하지 않음)

목적
  같은 권리자 · 계약 · 도서가 화면마다 다른 이름 · 번호로 적혀 있지 않은지 대조한다.
  샘플 데이터라도 화면 사이에서 어긋나면 검수자가 흐름을 따라갈 수 없다.

검사 (마크업 + 스크립트 문자열 전체, 태그 제거 후)
  [1] 권리자 RH-NNNN       → 붙어 있는 이름("정종대 (RH-0025)", "RH-0025 (정종대)")이 둘 이상이면 오류
  [2] 계약 CON-YYYY-NNN     → 같은 줄 가까이(60자)에 함께 적힌 권리자 RH 코드가 둘 이상이면 오류
  [2b] 스크립트 데이터       → 한 객체 안의 권리자 코드 키(holderId · rightsHolderId · payeeId 등)와
                              이름 키(holderName · rightsHolderName 등)를 짝지어, 같은 RH 코드에 다른 이름이 붙으면 오류.
                              계약 코드 키(id · contractId)와 권리자 코드 키를 짝지어, 같은 계약이 다른 권리자를 가리키면 오류
  [3] 도서 SKU PROD-BK-NNNN → 옛 형식(BOOK-NNNN · BK-YYYY-NNN · TMP-BK-*)이 남아 있으면 오류
                              임시코드는 BK-REQ-YYYY-NNNN만 허용(자릿수가 다르면 오류)
                              같은 도서명이 서로 다른 SKU로 적혀 있으면 오류
                              같은 SKU에 붙은 도서명이 여럿이면 참고(약칭일 수 있음)
                              스크립트 객체 안의 SKU 키(sku · productId · id)와 이름 키(title · productName · name)도 짝짓는다
  [4] 이름 → 코드 역방향    → 같은 권리자 이름이 서로 다른 RH 코드로 적혀 있으면 오류
  [5] 수취인 코드           → 2계층 수취인도 권리자 원장의 RH 코드를 쓴다. 옛 수취인 코드(PY-NNNN)가 남아 있으면 오류
  [6] 관계 대조             → 기준: ADMN-SETT-001 상품 · 지분 매핑. 대상: lines + attributedHolders 필드가 있는 화면(RELATION_SCREENS).
                              결제일에 유효한 매핑의 (권리자, 지분) 집합 ≠ 귀속 권리자 집합이면 오류, SETT-001에 없는 상품(SHIPPING 제외)도 오류,
                              rightsHolderId가 귀속 외부 권리자에 없으면 오류. lines가 빈 행 · 필드 없음은 참고(관계 오류/참고 칸에 따로 집계)

사용법:
  python scripts/qa/skill_cross_data_check.py                  # prototype_clean 기준(두 폴더는 데이터가 같음)
  python scripts/qa/skill_cross_data_check.py prototype
  python scripts/qa/skill_cross_data_check.py --strict         # 오류 1건 이상이면 exit 1
리포트: scripts/qa/reports/CROSS_DATA_CHECK_REPORT.md
"""
import argparse
import datetime
import html
import os
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORT = os.path.join(ROOT, "scripts", "qa", "reports", "CROSS_DATA_CHECK_REPORT.md")

NAME = r"([가-힣]{2,4})(?:\s*(?:강사|대표|저자|작가))?"
RH = r"RH-\d{4}"
CON = r"CON-\d{4}-\d{3}"
CT = r"(?:CT|CON)-\d{4}-[0-9A-Z]{3,4}"
RH_KEY = r"(?:rightsHolderId|primaryHolderId|holderId|payeeId|partnerId|rights_holder_id)"
NAME_KEY = r"(?:rightsHolderName|primaryHolderName|holderName|payeeName|partnerName|holder_name)"
CT_KEY = r"(?:id|contractId|contract_id)"


def lead_name(s):
    """이름 값의 첫 한글 낱말(2자 이상) — '고(故) 박위생 → …' → 박위생, '(주)산준교육 에이전시' → 산준교육"""
    if "*" in s:                               # 비식별(가명) 표시는 대조하지 않는다
        return None
    for w in re.findall(r"[가-힣]{2,}", s):
        if w not in NOT_NAME:
            return w[:4]
    return None


def objects(raw):
    """스크립트 객체 리터럴 조각 — 중괄호 안쪽(중첩 없는 가장 안쪽 객체)"""
    return re.findall(r"\{[^{}]{0,2000}\}", raw)
BK = r"PROD-BK-\d{4}"
BK_OLD = r"\bBOOK-(?:\d{4}|X{4}|AUTO)\b|(?<![A-Z-])BK-\d{4}-\d+|TMP-BK-[0-9A-Z*]+"
BK_REQ = r"BK-REQ-\d{4}-\d+"
TITLE_CH = r"[^()<>'\"\n|·:\[\]{}]"
NOT_NAME = {"강사", "대표", "저자", "본인", "정산", "계약", "권리", "수취", "위탁", "전속", "인세", "도서", "산업", "소방", "선택", "현재", "공동", "단독", "해지", "대상", "주권", "외부", "권리자", "정상", "사단법인", "재단법인", "주식회사"}


def plain(text):
    text = re.sub(r"/\*.*?\*/|<!--.*?-->", " ", text, flags=re.S)   # 주석은 화면 데이터가 아니다
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def norm_title(t):
    t = re.sub(r"\s+", " ", t).strip(" -–—.,…")
    t = re.sub(r"^\d{4}\s*", "", t)          # 연도 접두 제거
    return t


# 관계 대조 설정 — lines + attributedHolders 형식을 쓰는 화면을 여기에 추가하면 자동 검사된다
RELATION_BASE = "ADMN-SETT-001_baseline.html"
RELATION_SCREENS = ["ADMN-SETT-004_baseline.html"]
RELATION_SKIP_PRODUCTS = {"SHIPPING"}
INTERNAL_ID = "RH-INTERNAL"


def match_close(text, i, op, cl):
    """text[i]==op 인 위치에서 짝이 맞는 닫는 괄호 위치(문자열 리터럴 · 주석 안은 무시), 없으면 -1"""
    depth, q, j, n = 0, None, i, len(text)
    while j < n:
        c = text[j]
        if q:
            if c == "\\":
                j += 1
            elif c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif text.startswith("//", j):
            j = text.find("\n", j)
            if j < 0:
                return -1
        elif text.startswith("/*", j):
            j = text.find("*/", j)
            if j < 0:
                return -1
            j += 1
        elif c == op:
            depth += 1
        elif c == cl:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def array_after(raw, key_pat):
    """key_pat 뒤의 [ ... ] 본문(없으면 None)"""
    m = re.search(key_pat + r"\s*[:=]?\s*\[", raw)
    if not m:
        return None
    i = m.end() - 1
    e = match_close(raw, i, "[", "]")
    return raw[i + 1:e] if e > 0 else None


def top_objects(body):
    out, i = [], 0
    while True:
        i = body.find("{", i)
        if i < 0:
            return out
        e = match_close(body, i, "{", "}")
        if e < 0:
            return out
        out.append(body[i:e + 1])
        i = e + 1


def strs(o, key):
    m = re.search(r"\b" + key + r"""\s*:\s*["']([^"']*)["']""", o)
    return m.group(1) if m else None


def num(o, key):
    m = re.search(r"\b" + key + r"\s*:\s*(-?\d+(?:\.\d+)?)", o)
    return float(m.group(1)) if m else None


def load_relation_base(base):
    """SETT-001 → (상품 {id: (kind, name, [lesson id])}, 매핑 {단위 id: [(holderId, share, start, end)]})"""
    path = os.path.join(base, RELATION_BASE)
    if not os.path.exists(path):
        return None, None
    raw = open(path, encoding="utf-8").read()
    pa = array_after(raw, r"\bconst\s+products")
    if pa is None:
        return None, None
    prods = {}
    for blk in top_objects(pa):
        head = blk.split("lessons", 1)[0]
        pid = strs(head, "id")
        if pid:
            prods[pid] = (strs(head, "kind"), strs(head, "name"), re.findall(r"""id\s*:\s*["'](LSN-[^"']+)["']""", blk))
    maps = {}
    mm = re.search(r"\bmappings\s*:\s*\{", raw)
    if mm:
        i = mm.end() - 1
        e = match_close(raw, i, "{", "}")
        body = raw[i + 1:e]
        for k in re.finditer(r"""["']([A-Za-z0-9-]+)["']\s*:\s*\[""", body):
            a = k.end() - 1
            b = match_close(body, a, "[", "]")
            rows = []
            for o in top_objects(body[a + 1:b]):
                hid = strs(o, "holderId")
                if hid:
                    rows.append((hid, num(o, "share"), strs(o, "start"), strs(o, "end")))
            maps[k.group(1)] = rows
    return prods, maps


def valid_set(rows, day):
    return {(h, round(sh or 0, 2)) for h, sh, st, en in rows if (not st or st <= day) and (not en or day <= en)}


def fmt_set(s):
    return "{" + ", ".join(f"{h} {sh:g}%" for h, sh in sorted(s)) + "}" if s else "{}"


def relation_check(base, folder_files):
    """관계 대조 → (오류 목록, 참고 목록, 대조한 상품 줄 수). 행 형식: (유형, 대상, 내용)"""
    errs, notes, checked = [], [], 0
    prods, maps = load_relation_base(base)
    if prods is None:
        return [], [("관계 대조 건너뜀", RELATION_BASE, "기준 데이터(상품 · 매핑)를 읽지 못함")], 0
    for scr in RELATION_SCREENS:
        if scr not in folder_files:
            notes.append(("관계 대조 건너뜀", scr, "화면 파일 없음"))
            continue
        raw = open(os.path.join(base, scr), encoding="utf-8").read()
        body = array_after(raw, r"\brecords")
        if body is None:
            notes.append(("관계 대조 건너뜀", scr, "records 없음"))
            continue
        recs = top_objects(body)
        if not any(re.search(r"\blines\s*:", r) and re.search(r"\battributedHolders\s*:", r) for r in recs):
            notes.append(("관계 대조 건너뜀", scr, f"필드 없음 — records {len(recs)}건에 lines · attributedHolders가 아직 없다"))
            continue
        for r in recs:
            la = array_after(r, r"\blines")
            aa = array_after(r, r"\battributedHolders")
            top = r
            for key in ("lines", "attributedHolders"):
                m = re.search(r"\b" + key + r"\s*:\s*\[", top)
                if m:
                    e = match_close(top, m.end() - 1, "[", "]")
                    top = top[:m.start()] + top[e + 1:]
            rid = strs(top, "id") or "?"
            if la is None or aa is None:
                notes.append(("관계 대조: 필드 없음", f"{scr} {rid}", "lines 또는 attributedHolders 누락"))
                continue
            paid = (strs(top, "paidAt") or "")[:10]
            lines = [(strs(o, "productId"), strs(o, "name")) for o in top_objects(la)]
            attr = defaultdict(set)
            ext = set()
            for o in top_objects(aa):
                pid, hid = strs(o, "productId"), strs(o, "holderId")
                attr[pid].add((hid, round(num(o, "share") or 0, 2)))
                if hid != INTERNAL_ID and not re.search(r"\binternal\s*:\s*true", o):
                    ext.add(hid)
            if not lines:
                notes.append(("관계 대조: lines 비어 있음(주문 매칭 불가)", f"{scr} {rid}", "상품 대조 생략"))
            for pid, nm in lines:
                if pid in RELATION_SKIP_PRODUCTS:
                    continue
                checked += 1
                if pid not in prods and pid not in maps:
                    errs.append(("관계: 상품이 SETT-001에 없음", f"{scr} {rid}", f"productId `{pid}` ({nm})"))
                    continue
                units = prods[pid][2] if pid in prods and prods[pid][2] else [pid]
                exps = [valid_set(maps.get(u, []), paid) for u in units]
                got = attr.get(pid, set())
                if got in exps:
                    continue
                exp_txt = " 또는 ".join(sorted({fmt_set(e) for e in exps}))
                errs.append(("관계: 귀속 권리자 불일치", f"{scr} {rid}", f"상품 `{pid}` ({nm}) 결제일 {paid} — 기대 {exp_txt} · 실제 {fmt_set(got)}"))
            for pid in sorted(x for x in set(attr) - {p for p, _ in lines} if x):
                errs.append(("관계: lines에 없는 상품의 귀속 행", f"{scr} {rid}", f"productId `{pid}`"))
            rh = strs(top, "rightsHolderId")
            if rh and rh != INTERNAL_ID and ext and rh not in ext:
                errs.append(("관계: rightsHolderId가 귀속 외부 권리자에 없음", f"{scr} {rid}", f"`{rh}` ∉ {{{', '.join(sorted(ext))}}}"))
    return errs, notes, checked


def scan(folder):
    base = os.path.join(ROOT, folder)
    files = sorted(f for f in os.listdir(base) if f.endswith(".html"))
    rh_names = defaultdict(lambda: defaultdict(set))     # RH → 이름 → 파일
    name_rh = defaultdict(lambda: defaultdict(set))      # 이름 → RH → 파일
    con_rh = defaultdict(lambda: defaultdict(set))       # CON → RH → 파일
    bk_titles = defaultdict(lambda: defaultdict(set))    # BK → 도서명 → 파일
    title_bk = defaultdict(lambda: defaultdict(set))     # 도서명 → BK → 파일
    bk_files = defaultdict(set)
    bk_old = defaultdict(set)                            # 옛 도서 코드 형식 → 파일
    py_old = defaultdict(set)                            # 옛 수취인 코드 → 파일
    obj_rh_names = defaultdict(lambda: defaultdict(set))  # 스크립트 객체: RH → 이름 → 파일
    obj_ct_rh = defaultdict(lambda: defaultdict(set))     # 스크립트 객체: 계약 → RH → 파일
    for f in files:
        raw = open(os.path.join(base, f), encoding="utf-8").read()
        for o in objects(raw):
            sku = re.search(r"""\b(?:sku|productId|id)\s*:\s*["'](""" + BK + r""")["']""", o)
            ttl = re.search(r"""\b(?:title|productName|name)\s*:\s*["']([^"']{4,80})["']""", o)
            if sku and ttl and re.search(r"[가-힣]", ttl.group(1)):
                title = norm_title(ttl.group(1))
                bk_titles[sku.group(1)][title].add(f)
                title_bk[title][sku.group(1)].add(f)
            rid = re.search(RH_KEY + r"""\s*:\s*["'](""" + RH + r""")["']""", o)
            if not rid:
                continue
            nm = re.search(NAME_KEY + r"""\s*:\s*["']([^"']{1,80})["']""", o)
            if nm and lead_name(nm.group(1)):
                obj_rh_names[rid.group(1)][lead_name(nm.group(1))].add(f)
            ct = re.search(CT_KEY + r"""\s*:\s*["'](""" + CT + r""")["']""", o)
            if ct:
                obj_ct_rh[ct.group(1)][rid.group(1)].add(f)
        t = plain(raw)
        for m in re.finditer(NAME + r"\s*\(\s*(" + RH + r")", t):
            if m.group(1) not in NOT_NAME:
                rh_names[m.group(2)][m.group(1)].add(f)
        for m in re.finditer(r"(" + RH + r")\s*\(\s*" + NAME + r"\s*[)·/,]", t):
            if m.group(2) not in NOT_NAME:
                rh_names[m.group(1)][m.group(2)].add(f)
        for code, names in rh_names.items():
            for n, fs in names.items():
                if f in fs:
                    name_rh[n][code].add(f)
        for m in re.finditer(CON, t):
            win = t[max(0, m.start() - 60): m.end() + 60]
            for r in set(re.findall(RH, win)):
                con_rh[m.group(0)][r].add(f)
        for m in re.finditer(BK, t):
            bk_files[m.group(0)].add(f)
        for m in re.finditer(BK_OLD, raw):
            bk_old[m.group(0)].add(f)
        for m in re.finditer(r"\bPY-\d{4}(?:-S\d)?", raw):
            py_old[m.group(0)].add(f)
        for m in re.finditer(BK_REQ, raw):
            if len(m.group(0).rsplit("-", 1)[1]) != 4:
                bk_old[m.group(0)].add(f)
        pats = [
            (r"(" + TITLE_CH + r"{4,40}?)\s*\(\s*(?:ISBN [\d-]+\s*·\s*SKU:\s*)?(" + BK + r")\s*\)", 1, 2),
            (r"(" + BK + r")\s*\(\s*(" + TITLE_CH + r"{4,40}?)\s*[)…]", 2, 1),
            (r"""(?:sku|productId)\s*:\s*["'](""" + BK + r""")["']\s*,\s*(?:title|productName)\s*:\s*["']([^"']{4,60})["']""", 2, 1),
        ]
        for pat, ti, ci in pats:
            for m in re.finditer(pat, t):
                title = norm_title(m.group(ti))
                if len(title) >= 4 and re.search(r"[가-힣]", title):
                    bk_titles[m.group(ci)][title].add(f)
                    title_bk[title][m.group(ci)].add(f)
    return files, rh_names, name_rh, con_rh, bk_titles, title_bk, bk_files, bk_old, py_old, obj_rh_names, obj_ct_rh


def fmt(d):
    return "; ".join(f"`{k}` ({', '.join(sorted(v))})" for k, v in sorted(d.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default="prototype_clean")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    files, rh_names, name_rh, con_rh, bk_titles, title_bk, bk_files, bk_old, py_old, obj_rh_names, obj_ct_rh = scan(args.folder)

    errors, notes = [], []
    for code, names in sorted(rh_names.items()):
        if len(names) > 1:
            errors.append(("권리자 이름 충돌", code, fmt(names)))
    for n, codes in sorted(name_rh.items()):
        if len(codes) > 1:
            errors.append(("같은 이름 · 다른 권리자 코드", n, fmt(codes)))
    for code, rhs in sorted(con_rh.items()):
        if len(rhs) > 1:
            errors.append(("계약 ↔ 권리자 불일치", code, fmt(rhs)))
    for code, names in sorted(obj_rh_names.items()):
        if len(names) > 1:
            errors.append(("권리자 이름 충돌(스크립트 데이터)", code, fmt(names)))
    obj_name_rh = defaultdict(lambda: defaultdict(set))
    for code, names in obj_rh_names.items():
        for n, fs in names.items():
            obj_name_rh[n][code] |= fs
    for n, codes in sorted(obj_name_rh.items()):
        if len(codes) > 1:
            errors.append(("같은 이름 · 다른 권리자 코드(스크립트 데이터)", n, fmt(codes)))
    for code, rhs in sorted(obj_ct_rh.items()):
        if len(rhs) > 1:
            errors.append(("계약 ↔ 권리자 불일치(스크립트 데이터)", code, fmt(rhs)))
    for c in sorted(bk_old):
        errors.append(("도서 코드 형식 불일치", c, "SKU는 PROD-BK-NNNN, 임시코드는 BK-REQ-YYYY-NNNN — " + ", ".join(sorted(bk_old[c]))))
    for c in sorted(py_old):
        errors.append(("옛 수취인 코드", c, "2계층 수취인도 권리자 원장의 RH 코드를 쓴다 — " + ", ".join(sorted(py_old[c]))))
    for title, codes in sorted(title_bk.items()):
        if len(codes) > 1:
            errors.append(("같은 도서명 · 다른 도서 코드", title, fmt(codes)))
    for code, titles in sorted(bk_titles.items()):
        if len(titles) > 1:
            notes.append(("한 도서 코드 · 여러 도서명(약칭 여부 확인)", code, fmt(titles)))

    rel_err, rel_note, rel_n = relation_check(os.path.join(ROOT, args.folder), files)

    L = ["# CROSS DATA CHECK REPORT — 화면 간 권리자 · 계약 · 도서 데이터 대조", "",
         f"- 생성: {datetime.datetime.now():%Y-%m-%d %H:%M}",
         f"- 대상: `{args.folder}` ({len(files)}개 파일)",
         f"- 수집: 권리자 코드 {len(rh_names)} · 계약 코드 {len(con_rh)} · 도서 코드 {len(bk_files)} · 스크립트 객체 권리자 {len(obj_rh_names)} · 계약 {len(obj_ct_rh)}",
         f"- 결과: 오류 {len(errors)}건 · 참고 {len(notes)}건", ""]
    for title, rows in (("오류", errors), ("참고", notes)):
        L += [f"## {title} ({len(rows)}건)", ""]
        if rows:
            L += ["| 유형 | 대상 | 내용 (값 · 파일) |", "| :--- | :--- | :--- |"]
            L += [f"| {k} | `{c}` | {v} |" for k, c, v in rows]
        else:
            L.append("없음")
        L.append("")
    L += [f"## 관계 대조 (오류 {len(rel_err)}건 · 참고 {len(rel_note)}건)", "",
          f"- 기준: `{RELATION_BASE}` 상품 · 매핑 / 대상 화면: {', '.join(RELATION_SCREENS)} / 대조한 상품 줄 {rel_n}건", ""]
    for title, rows in (("관계 오류", rel_err), ("관계 참고", rel_note)):
        L += [f"### {title} ({len(rows)}건)", ""]
        if rows:
            L += ["| 유형 | 대상 | 내용 |", "| :--- | :--- | :--- |"]
            L += [f"| {k} | {c} | {v} |" for k, c, v in rows]
        else:
            L.append("없음")
        L.append("")
    L += ["## 권리자 코드별 이름", "", "| 코드 | 이름 (파일) |", "| :--- | :--- |"]
    L += [f"| `{c}` | {fmt(n)} |" for c, n in sorted(rh_names.items())]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"[Skill 3] {args.folder}: 권리자 {len(rh_names)} · 계약 {len(con_rh)} · 도서 {len(bk_files)} | 오류 {len(errors)} · 참고 {len(notes)} | 관계 오류 {len(rel_err)} · 참고 {len(rel_note)} → {os.path.relpath(REPORT, ROOT)}")
    if args.strict and (errors or rel_err):
        sys.exit(1)


if __name__ == "__main__":
    main()
