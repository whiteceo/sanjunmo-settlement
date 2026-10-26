"""ADMN-CONF-005 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-005.md
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
    "code": "ADMN-CONF-005",
    "devCommit": DEV_COMMIT,
    "progress": "구현(관리자 계정 · 권한 그룹 · 메뉴 관리). 역할 그룹 추가 · 미사용 · 변경 영향 확인 · 변경 이력 · 계정 소속(권리자 · 거래처)은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.admin-users.index", "label": "관리자 계정"},
        {"route": "admin.admin-roles.index", "label": "권한 그룹"},
        {"route": "admin.admin-menus.index", "label": "메뉴 관리 (개발에만)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 탭 → 메뉴 3개 ───────────────────────────────────
R('id="tabBtn-accounts" onclick=', 'id="tabBtn-accounts"' + attrs(route="admin.admin-users.index", method="GET", url=A + "/admin-users", perm="조회") + ' onclick=')
R('id="tabBtn-roles" onclick=', 'id="tabBtn-roles"' + attrs(route="admin.admin-roles.index", method="GET", url=A + "/admin-roles", perm="조회") + ' onclick=')
R('        <a class="btn btn-outline btn-sm tab-link" href="ADMN-CONF-010_baseline.html?view=access">',
  '        <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.admin-menus.index" data-dev-method="GET" data-dev-url="' + A + '/admin-menus" data-dev-perm="조회"'
  ' data-dev-note="메뉴 관리(AdminMenuRequest parent_id · name · route_name · url · icon · sort_order · is_active) — 권한 단위 admin_menus.screen_code" onclick="showToast(\'메뉴 관리 화면(admin-menus)으로 이동합니다.\')">3. 메뉴 관리</button>\n'
  '        <a class="btn btn-outline btn-sm tab-link" href="ADMN-CONF-010_baseline.html?view=access">')

# ── 탭 1 관리자 계정 ─────────────────────────────────
NAME("acc-role-filter", "admin_role_id")
NAME("acc-keyword", "keyword", note="개발 search_field: login_id · name · email · phone (데이터 범위 검색은 개발 없음)")
R('<span id="acc-summary"',
  '<select class="f-select" name="is_locked" style="width:110px;" data-dev-flag="dev-only" data-dev-note="개발 목록 필터 is_locked · per_page(10 · 20 · 30)"><option value="">상태 전체</option><option value="0">정상</option><option value="1">잠금</option></select>\n'
  '              <span id="acc-summary"')
R('onclick="openAccountModal(null)"', attrs(route="admin.admin-users.create", method="GET", url=A + "/admin-users/create", perm="등록").lstrip() + ' onclick="openAccountModal(null)"')
R('onclick="openAccountModal(\'${a.id}\')"', attrs(route="admin.admin-users.edit", method="GET", url=A + "/admin-users/{adminUser}/edit", perm="수정").lstrip() + ' onclick="openAccountModal(\'${a.id}\')"')
R('<th>접속 제한</th>', '<th data-dev-flag="proto-only" data-dev-note="개발 목록에 없음(admin_allowed_ips는 있음)">접속 제한</th>')
R('<th style="width:300px;">소속 (데이터 범위)</th>', '<th style="width:300px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 없음 — 계정 소속(내부 · 권리자 · 거래처) 축 미구현">소속 (데이터 범위)</th>')

# 계정 발급 · 수정 모달 → 개발 admin-users create · edit 페이지 (AdminUserRequest)
NAME("af-id", "login_id", note="max 50 · 중복 불가")
NAME("af-name", "name", note="max 50")
R('class="af-role" value="${g.id}"', 'class="af-role" data-dev-name="admin_role_id" data-dev-note="개발 폼은 역할 1개 선택(admin_user_roles 테이블은 다중 가능)" value="${g.id}"')
R('        <div class="form-row"><label>역할 그룹 *</label>',
  '        <div class="form-row" data-dev-flag="dev-only" data-dev-note="AdminUserRequest email · phone"><label>이메일 / 전화번호</label><div style="display:flex; gap:6px;"><input class="f-input" name="email" type="email" maxlength="100" style="flex:1;" placeholder="admin@sanjunmo.com" /><input class="f-input" name="phone" maxlength="20" style="width:160px;" placeholder="010-0000-0000" /></div></div>\n'
  '        <div class="form-row" data-dev-flag="dev-only" data-dev-note="발급 시 필수 · 수정 시 비우면 유지 · 8~12자 영문+숫자+특수문자(정책 D-CONF-05: 8~64자 권고)"><label>비밀번호</label><div style="display:flex; gap:6px;"><input class="f-input" name="password" type="password" style="flex:1;" placeholder="비밀번호" autocomplete="new-password" /><input class="f-input" name="password_confirmation" type="password" style="flex:1;" placeholder="비밀번호 확인" autocomplete="new-password" /></div></div>\n'
  '        <div class="form-row"><label>역할 그룹 *</label>')
DEVNAME('name="af-kind" value="STAFF"', "(없음)", note="계정 소속 축 — 개발 미구현. 강사 · 조교 역할은 linked_instructor_id · assistant_instructor_ids[]")
DEVNAME('name="af-kind" value="RH"', "(없음)", note="권리자 계정 — 개발 역할 코드 없음")
DEVNAME('name="af-kind" value="VENDOR"', "(없음)", note="거래처 계정 — 개발 역할 코드 없음")
R('id="af-sec"', 'id="af-sec" data-dev-flag="proto-only" data-dev-note="접속 제한 — 개발은 admin_allowed_ips 테이블(화면 입력 없음)"')
DEVNAME('name="af-status" value="ACTIVE"', "is_locked", value="(체크 해제)")
DEVNAME('name="af-status" value="LOCKED"', "is_locked", value="1")
R('<label><input type="radio" name="af-status" value="LOCKED" data-dev-name="is_locked" data-dev-value="1" /> 잠금 · 중지</label></div></div>',
  '<label><input type="radio" name="af-status" value="LOCKED" data-dev-name="is_locked" data-dev-value="1" /> 잠금 · 중지</label></div></div>\n'
  '        <div class="form-row" data-dev-flag="dev-only" data-dev-note="잠긴 계정을 해제할 때 필수 · max 200 (#unlock_reason)"><label>잠금 해제 사유</label><div><input class="f-input" name="unlock_reason" maxlength="200" style="width:100%;" placeholder="잠금 해제 시 입력" /></div></div>\n'
  '        <div class="form-row" data-dev-flag="dev-only" data-dev-note="최고관리자에게만 노출(canResetVerifyCap) · reason"><label>인증번호 발송 횟수</label><div><button type="button" class="btn btn-outline btn-sm" data-dev-route="admin.admin-users.reset-verify-cap" data-dev-method="POST" data-dev-url="' + A + '/admin-users/{adminUser}/reset-verify-cap" data-dev-perm="수정 + 최고관리자" onclick="showToast(\'인증번호 발송 횟수를 초기화했습니다.\')">발송 횟수 초기화</button></div></div>')
ACT("saveAccount", route="admin.admin-users.store | admin.admin-users.update", method="POST | PUT", url=A + "/admin-users | /admin-users/{adminUser}", perm="등록 | 수정",
    note="삭제 경로 없음 — 정지(잠금)로만")

# ── 탭 2 역할 그룹 · 권한 ─────────────────────────────
R('onclick="openRoleModal(null)"', attrs(flag="proto-only", route="admin.admin-roles.store (규칙)", method="POST", url=A + "/admin-roles", perm="등록",
                                         note="역할 그룹 추가 — 개발 store 라우트 없음(정본: 운영 중 추가 · 미사용 — 개발팀 전달)").lstrip() + ' onclick="openRoleModal(null)"')
R('onclick="openRoleModal(selectedRoleId)"', attrs(route="admin.admin-roles.edit", method="GET", url=A + "/admin-roles/{adminRole}/edit", perm="수정",
                                                   note="최고관리자(super) 그룹은 최고관리자만 편집").lstrip() + ' onclick="openRoleModal(selectedRoleId)"')
ACT("toggleRoleStatus", flag="proto-only", route="admin.admin-roles.status.update (규칙)", method="PUT", url=A + "/admin-roles/{adminRole}/status", perm="수정", note="+ admin_roles.is_active (규칙)")
ACT("selectRole", route="admin.admin-roles.edit", method="GET", url=A + "/admin-roles/{adminRole}/edit", perm="수정")
R('class="perm-check" data-menu="${m.key}"',
  'class="perm-check" data-dev-name="permissions[{admin_menu_id}][can_view|can_create|can_update|can_delete|can_download]" data-dev-note="개발 5축 — 프로토 R · W · X 3축 유지(정책 M-02)" data-menu="${m.key}"')
ACT("reviewPermChanges", route="admin.admin-roles.update", method="PUT", url=A + "/admin-roles/{adminRole}", perm="수정", note="개발은 변경 영향 확인 모달 없이 바로 저장")
NAME("rf-name", "name", note="max 100 · 중복 불가")
NAME("rf-id", "code", note="^[a-z0-9_]+$ · 개발 6종 super · cs · logistics · finance · instructor · assistant")
NAME("rf-desc", "description", note="max 500")
DEVNAME('name="rf-side" value="INTERNAL"', "is_external", value="0", note="(규칙) admin_roles.is_external — 개발 미구현")
DEVNAME('name="rf-side" value="EXTERNAL"', "is_external", value="1")
R('id="rf-queue"', 'id="rf-queue" data-dev-flag="proto-only" data-dev-note="문의 큐 — 개발은 inquiry_category_roles.role_code"')
NAME("rf-order", "sort_order")
R('id="rf-start"', 'id="rf-start" data-dev-name="landing_route" data-dev-flag="proto-only" data-dev-note="(규칙) admin_roles.landing_route — 개발은 config/admin.php landing 상수"')
R('id="rf-dash-area"', 'id="rf-dash-area" data-dev-flag="proto-only" data-dev-note="대시보드 기본 영역 — 개발은 DashboardService::VISIBLE 상수"')
R('id="rf-copy"', 'id="rf-copy" data-dev-flag="proto-only" data-dev-note="권한 시작값 복사 — 개발 없음"')
ACT("saveRole", route="admin.admin-roles.update | admin.admin-roles.store (규칙)", method="PUT | POST", url=A + "/admin-roles/{adminRole} | /admin-roles", perm="수정 | 등록")
ACT("confirmImpact", route="admin.admin-roles.update", method="PUT", url=A + "/admin-roles/{adminRole}", perm="수정")
R('<div class="modal-backdrop" id="modal-impact">', '<div class="modal-backdrop" id="modal-impact" data-dev-flag="proto-only" data-dev-note="변경 영향 확인(영향 계정 · 문의 분류) — 개발 없음">')
R('<tbody id="log-tbody"></tbody>', '<tbody id="log-tbody" data-dev-flag="proto-only" data-dev-note="역할 그룹 변경 이력 — 개발은 admin_logs 기록만, 화면 없음"></tbody>')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("계정 탭", "switchTab('accounts')", "#tab-accounts"),
    ("역할 탭", "switchTab('roles')", "#tab-roles"),
    ("계정 발급 모달", "switchTab('accounts'); openAccountModal(null)", "#modal-account"),
    ("계정 수정 모달", "switchTab('accounts'); openAccountModal(ACCOUNTS[0].id)", "#modal-account"),
    ("역할 그룹 추가 모달", "switchTab('roles'); openRoleModal(null)", "#modal-role"),
    ("역할 그룹 수정 모달", "switchTab('roles'); openRoleModal(selectedRoleId)", "#modal-role"),
    ("권한 체크 → 영향 확인", "switchTab('roles'); const c = document.querySelector('.perm-check'); c.checked = !c.checked; c.dispatchEvent(new Event('change')); reviewPermChanges()", "#modal-impact|#tab-roles"),
]
