"""ADMN-CONF-010 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-010.md
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
    "code": "ADMN-CONF-010",
    "devCommit": DEV_COMMIT,
    "progress": "개발 미구현(CONF-010 메뉴 · 라우트 없음). 탭 3은 개발 CONF-006 관리자 로그 · 로그인 로그(구현)에 대응. 탭 1 · 2 · 해시 체인은 규칙 기반 명명 — 주황 표시",
    "menus": [
        {"route": "admin.audit-logs.index (규칙)", "label": "시스템 감사 로그 (개발 미구현)"},
        {"route": "admin.admin-logs.index", "label": "관리자 로그 (개발 CONF-006)"},
        {"route": "admin.login-logs.index", "label": "관리자 로그인 로그 (개발 CONF-006)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 상단 버튼 ────────────────────────────────────────
ACT("verifyHashChain", flag="proto-only", route="admin.audit-logs.verifications.store (규칙)", method="POST", url=A + "/audit-logs/verifications", perm="등록",
    note="해시 체인 — 개발 흔적 없음(정책 D-CONF-03: 2차 권고)")
ACT("exportAuditCsv", flag="proto-only", route="admin.audit-logs.download (규칙)", method="GET", url=A + "/audit-logs/download", perm="다운로드",
    note="ReasonRequest reason · reason_ref · reason_etc (공통 사유 모달)")

# ── 기간 바 (LogSearchRequest) ──────────────────────────
R('<select id="monthFilterSelect"', '<select id="monthFilterSelect" data-dev-flag="proto-only" data-dev-name="settlement_month" data-dev-note="(규칙) admin_logs.settlement_month — 개발 컬럼 없음"')
NAME("dateFrom", "start_date", note="Y-m-d · 최대 90일 · 기본 7일 (개발 id #startDate)")
NAME("dateTo", "end_date", note="개발 id #endDate")
R('id="preset-TODAY" onclick=', 'id="preset-TODAY"' + attrs(name="period", value="1") + ' onclick=')
R('id="preset-7D" onclick=', 'id="preset-7D"' + attrs(name="period", value="7") + ' onclick=')
R('id="preset-CUR_M" onclick=', 'id="preset-CUR_M"' + attrs(name="period", value="30 (개발은 일수 프리셋 — 당월 개념 없음)") + ' onclick=')
R('id="preset-PREV_M" onclick=', 'id="preset-PREV_M" data-dev-flag="proto-only" data-dev-note="전월 마감분 — 개발 없음(정산월 컬럼 없음)" onclick=')
R('id="preset-ALL" onclick=', 'id="preset-ALL" data-dev-flag="proto-only" data-dev-note="전체 기간 — 개발 1회 조회 최대 90일(period 90). 정본 결정: 최근 90일로" onclick=')

# ── 탭 ───────────────────────────────────────────
R('id="tabBtn-logs" onclick=', 'id="tabBtn-logs"' + attrs(flag="proto-only", route="admin.audit-logs.index (규칙)", method="GET", url=A + "/audit-logs", perm="조회") + ' onclick=')
R('id="tabBtn-monthly" onclick=', 'id="tabBtn-monthly"' + attrs(flag="proto-only", route="admin.audit-logs.monthly.index (규칙)", method="GET", url=A + "/audit-logs/monthly", perm="조회") + ' onclick=')
R('id="tabBtn-access" onclick=', 'id="tabBtn-access"' + attrs(route="admin.admin-logs.index | admin.login-logs.index", method="GET", url=A + "/admin-logs | /login-logs", perm="조회",
                                                              note="개발 CONF-006 — 관리자 로그(type 필터) + 로그인 로그(event · status 필터) 두 메뉴") + ' onclick=')

# ── 탭 1 감사 원장 (개발 미구현) ──────────────────────────
NAME("catSelect", "target_type", note="(유사) 개발 관리자 로그 target_type · type — 정산 감사 4구분은 개발 없음")
R('<select id="screenSelect"', '<select id="screenSelect" data-dev-flag="proto-only" data-dev-name="screen_code" data-dev-note="(규칙) admin_logs.screen_code — 개발은 menu_id"')
NAME("auditKeyword", "keyword", note="max 100")
ACT("setAuditCategory", count=5, note="KPI 카드 → 감사 영역 필터(프로토 전용 집계)")
R('<tr class="clickable-row" onclick="openDiffModal(', '<tr class="clickable-row"' + attrs(route="admin.audit-logs.show (규칙)", method="GET", url=A + "/audit-logs/{auditLog}", perm="조회") + ' onclick="openDiffModal(')
R('<button class="btn btn-sm btn-pri" onclick="openDiffModal(', '<button class="btn btn-sm btn-pri"' + attrs(route="admin.admin-logs.show", method="GET", url=A + "/admin-logs/{adminLog}", perm="조회",
                                                                                                          note="개발 상세 = view 페이지(before_value · after_value)") + ' onclick="openDiffModal(')
R('<div class="modal-backdrop" id="diffModal">', '<div class="modal-backdrop" id="diffModal" data-dev-note="개발은 레이어가 아니라 admin-logs/{adminLog} 상세 페이지 — 해시 줄은 프로토 전용">')

# ── 탭 2 월별 통계 (개발 미구현) ──────────────────────────
ACT("jumpToMonthLogs", count=3, flag="proto-only", route="admin.audit-logs.index (규칙)", method="GET", url=A + "/audit-logs?settlement_month=", perm="조회")
ACT("exportMonthPackage", count=3, flag="proto-only", route="admin.audit-logs.monthly.download (규칙)", method="GET", url=A + "/audit-logs/monthly/download", perm="다운로드",
    note="(규칙) audit_log_snapshots month · last_hash · counts · closed_at")

# ── 탭 3 접근 · 권한 · 다운로드 → 개발 관리자 로그 · 로그인 로그 ─────
NAME("accessTypeSelect", "event", value="LOGIN_SUCCESS · LOGIN_FAIL · ACCOUNT_LOCKED · ACCOUNT_UNLOCKED … 18종 (관리자 로그는 type: personal_view · unmask · member_update · excel_download · setting_change · role_change)",
     note="로그인 로그 status(success · fail) · event")
R('            <span style="margin-left:auto; font-size:12px; color:var(--muted);" id="accessCountInfo"></span>',
  '            <span data-dev-flag="dev-only" data-dev-note="관리자 로그 LogSearchRequest: result_status · admin_role_code · target_member · ip · disallowed_ip_only" style="display:flex; gap:6px; align-items:center;">\n'
  '              <select class="select" name="result_status"><option value="">결과 전체</option><option value="success">성공</option><option value="fail">실패</option></select>\n'
  '              <input type="text" class="input" name="target_member" maxlength="191" style="width:140px;" placeholder="대상 회원">\n'
  '              <input type="text" class="input" name="ip" maxlength="45" style="width:120px;" placeholder="IP">\n'
  '              <label style="font-size:12px;"><input type="checkbox" name="disallowed_ip_only" value="1"> 허용 외 IP만</label>\n'
  '            </span>\n'
  '            <span style="margin-left:auto; font-size:12px; color:var(--muted);" id="accessCountInfo"></span>\n'
  '            <button class="btn btn-sm" data-dev-flag="dev-only" data-dev-route="admin.admin-logs.download | admin.login-logs.download" data-dev-method="GET" data-dev-url="' + A + '/admin-logs/download | /login-logs/download" data-dev-perm="다운로드"'
  ' data-dev-note="엑셀 사유 모달(ReasonRequest reason: refund_account · delivery_error · identity_check · payment_inquiry · legal_request · settlement_check · etc)" onclick="showToast(\'다운로드 사유를 입력한 뒤 엑셀을 받습니다.\')">⬇ 엑셀</button>')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
U = "document.querySelectorAll('.modal-backdrop').forEach(m => m.style.removeProperty('display')); "
VERIFY = [
    ("원장 탭", "switchTab('logs')", "#tabPanel-logs"),
    ("월별 탭", "switchTab('monthly')", "#tabPanel-monthly"),
    ("접근 로그 탭", "switchTab('access')", "#tabPanel-access"),
    ("전·후 비교 모달", U + "switchTab('logs'); openDiffModal(AUDIT_EVENTS[0].logId)", "#diffModal"),
    ("이 달의 로그 보기", "switchTab('monthly'); jumpToMonthLogs('2026-09')", "#tabPanel-logs"),
    ("빠른 기간 7일", "applyQuickDate('7D')", "#auditListTbody"),
    ("감사 영역 PII", "switchTab('logs'); setAuditCategory('PII')", "#tabPanel-logs"),
    ("접근 유형 필터", "switchTab('access'); document.getElementById('accessTypeSelect').value='LOGIN'; renderAccessLogs()", "#tabPanel-access"),
]
