"""ADMN-SETT-004 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-004.md
apply_dev_map.py가 읽는다. 각 항목의 기대 건수가 원본과 다르면 전체를 멈춘다.
"""
import json

DEV_COMMIT = "d562524a"
A = "/sj-admin"
OPS = []


def R(find, replace, count=1):
    OPS.append(dict(kind="replace", find=find, replace=replace, count=count))


def RE(find, replace, count):
    OPS.append(dict(kind="regex", find=find, replace=replace, count=count))


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def attrs(route=None, method=None, url=None, perm=None, flag=None, note=None, name=None, value=None):
    out = ""
    for k, v in (("route", route), ("method", method), ("url", url), ("perm", perm), ("flag", flag), ("note", note), ("name", name), ("value", value)):
        if v:
            out += f' data-dev-{k}="{esc(v)}"'
    return out


def ACT(fn, count=1, **kw):
    """onclick="fn( 앞에 개발 라우트 속성을 단다"""
    R(f'onclick="{fn}(', attrs(**kw).lstrip() + f' onclick="{fn}(', count)


def NAME(id_, name, value=None, note=None):
    """JS가 id로 찾는 입력 — 실제 name 속성을 개발 이름으로 넣는다"""
    R(f'id="{id_}"', f'id="{id_}" name="{name}"' + attrs(value=value, note=note), 1)


def DEVNAME(find, name, value=None, note=None, count=1):
    """JS가 name · value에 기대는 라디오 등 — data-dev-name · data-dev-value만 단다"""
    R(find, find + attrs(name=name, value=value, note=note), count)


def RENAME_ID(old, new, count):
    """id 와 그 참조(getElementById · 문자열)를 모두 바꾼다"""
    RE(r"(?<![\w-])" + old.replace("-", r"\-") + r"(?![\w-])", new, count)



# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-004",
    "devCommit": DEV_COMMIT,
    "progress": "구현(SETT-004 워크스페이스 · S1 차이 상세 별도 페이지 · 소명 승인). 단수차액 자동 대체 · 분류만 저장 · 주문번호 검색 · 화면 안 감사 로그 표는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.pg-reconciliations.index", "label": "PG 정산 원장 대사 (show · store · update 같은 메뉴 권한)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

PG = A + "/settlement/pg-reconciliations"

# ── 상단 바 ─────────────────────────────────────────
NAME("monthSelect", "month", note="개발 월 버튼 .st-btn.st-btn--sm(.st-btn--pr=현재) · #monthPick")
R('<button class="btn" id="btnRunRecon">',
  '<button class="btn" id="btnRunRecon"' + attrs(route="admin.settlement.pg-reconciliations.store", method="POST", url=PG, perm="등록",
                                                 note="PgReconciliationRunRequest: month(Y-m) hidden. is_locked 월은 비활성") + '>')
R('<button class="btn btn-primary" id="btnAutoPenny">',
  '<button class="btn btn-primary" id="btnAutoPenny"' + attrs(flag="proto-only", route="admin.settlement.pg-reconciliations.penny.store (규칙)", method="POST", url=PG + "/penny",
                                                              perm="등록", note="1,000원 이내 단수차액 자동 대체 — 개발 미구현(정책 확인)") + '>')

# ── 탭(개발 ?tab=workspace|tax|timing|audit) ──────────────────
R('data-tab="tabRecon">', 'data-tab="tabRecon"' + attrs(route="admin.settlement.pg-reconciliations.index", method="GET", url=PG + "?tab=workspace", perm="조회") + '>')
R('data-tab="tabTaxSplit">', 'data-tab="tabTaxSplit"' + attrs(route="admin.settlement.pg-reconciliations.index", method="GET", url=PG + "?tab=tax", perm="조회") + '>')
R('data-tab="tabVbank">', 'data-tab="tabVbank"' + attrs(route="admin.settlement.pg-reconciliations.index", method="GET", url=PG + "?tab=timing", perm="조회") + '>')
R('data-tab="tabAudit">', 'data-tab="tabAudit"' + attrs(route="admin.settlement.pg-reconciliations.index", method="GET", url=PG + "?tab=audit", perm="조회",
                                                         note="개발 audit 탭은 관리자 로그(admin.admin-logs.index) 이동 버튼만 — 화면 안 로그 표는 프로토타입만") + '>')

# ── 1. 워크스페이스 필터(개발 필터 폼 hidden month · tab) ───────────
R('id="searchInput"', 'id="searchInput" data-dev-flag="proto-only" data-dev-note="주문번호 · TID 검색 — 개발 필터에 없음"')
NAME("reasonFilter", "reason", note="개발 #reason — '' 전체 + REASON_LABELS 5종(값 그대로)")
R('<option value="ALL">전체 차이 원인 코드</option>', '<option value="ALL" data-dev-value="">전체 차이 원인 코드</option>')
NAME("methodFilter", "method", note="개발 #method")
R('<option value="ALL">전체 결제수단</option>', '<option value="ALL" data-dev-value="">전체 결제수단</option>')
R('<option value="VBANK">가상계좌</option>', '<option value="VBANK" data-dev-value="VIRTUAL_ACCOUNT">가상계좌</option>')

# 목록 행 → S1 상세(개발 별도 페이지)
ACT("selectRecord", route="admin.settlement.pg-reconciliations.show", method="GET", url=PG + "/{item}?month=&tab=&reason=&method=", perm="조회",
    note="개발 [상세] → S1 별도 페이지. 목록 조건 month · tab · reason · method 유지(KEEP)")
R('<div class="detail-body" id="detailBody">',
  '<div class="detail-body" id="detailBody"' + attrs(route="admin.settlement.pg-reconciliations.show", method="GET", url=PG + "/{item}", perm="조회",
                                                     note="개발 S1은 별도 페이지 — 귀속 권리자 스냅샷 표(pg_reconciliation_item_holders: 지분 · 몫 · 목록 대표 is_primary) 포함") + '>')

# S1 소명 승인 폼(PUT) — JS가 id로 읽음
NAME("editReasonCode", "mismatch_reason_code", note="REASON_LABELS 5종(값 그대로)")
NAME("editMemo", "explanation", note="10~500자(trim) · 감사 로그 필수")
ACT("saveClassificationOnly", flag="proto-only", note="분류만 임시 저장 — 개발 경로 없음(approval_status PENDING_APPROVAL 값만 있음, 정책 확인)")
ACT("approveReconciliation", route="admin.settlement.pg-reconciliations.update", method="PUT", url=PG + "/{item}", perm="수정")

# ── 4. 감사 로그 탭: 개발은 관리자 로그로 이동 ─────────────────
R('            <div class="card-title">PG 대사 · 원인 분류 · 소명 승인 감사 로그 (ADMN-CONF-010 연동)</div>\n',
  '            <div class="card-title">PG 대사 · 원인 분류 · 소명 승인 감사 로그 (ADMN-CONF-010 연동)</div>\n'
  '            <a class="btn btn-sm" href="ADMN-CONF-010_baseline.html" data-dev-flag="dev-only" data-dev-route="admin.admin-logs.index" data-dev-method="GET" data-dev-url="' + A + '/admin-logs" data-dev-perm="조회(관리자 로그 메뉴)">관리자 로그에서 보기 →</a>\n')
R('<tbody id="auditTableBody"></tbody>', '<tbody id="auditTableBody" data-dev-flag="proto-only" data-dev-note="화면 안 감사 로그 표 — 개발은 admin_logs 화면"></tbody>')

# ── 하단 게이트 바 ────────────────────────────────────
R('''<button class="btn btn-sm" onclick="location.href='ADMN-SETT-002_baseline.html'">''',
  '''<button class="btn btn-sm"''' + attrs(route="admin.settlement.board.index", method="GET", url=A + "/settlement/board", perm="조회(월간 정산 메뉴)") + ''' onclick="location.href='ADMN-SETT-002_baseline.html'">''')

# ── 검증 ───────────────────────────────────────────
VERIFY = [
    ("1. 워크스페이스 탭", "document.querySelector('[data-tab=tabRecon]').click()", "#tabRecon"),
    ("2. 과·면세 분할 탭", "document.querySelector('[data-tab=tabTaxSplit]').click()", "#tabTaxSplit"),
    ("3. 시차 점검 탭", "document.querySelector('[data-tab=tabVbank]').click()", "#tabVbank"),
    ("4. 감사 로그 탭", "document.querySelector('[data-tab=tabAudit]').click()", "#tabAudit"),
    ("S1 상세 선택", "document.querySelector('[data-tab=tabRecon]').click(); selectRecord(state.records[0].id)", "#detailBody"),
    ("S1 원인 코드 입력", "document.querySelector('[data-tab=tabRecon]').click(); selectRecord(state.records.find(r => r.diff !== 0).id)", "#editReasonCode"),
    ("S1 소명 입력", "document.querySelector('[data-tab=tabRecon]').click(); selectRecord(state.records.find(r => r.diff !== 0).id)", "#editMemo"),
]
