"""ADMN-LOGIN-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-LOGIN-001.md
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



# ── 머리: 개발 매핑 표시 (로그인 화면 — SNB 없음, </head> 앞 삽입은 같음) ─────
DEV_MAP = {
    "code": "ADMN-LOGIN-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(LOGIN-001 · P1 레이어 · LOGIN-002 아이디 찾기 · LOGIN-003 비밀번호 찾기 · 비밀번호 변경). 시연 버튼 · 역할 프리셋 · 권한 없음 안내는 프로토 전용 — 주황 표시",
    "menus": [
        {"route": "admin.login", "label": "관리자 로그인 (메뉴 권한 밖 — admin.ip 허용 IP만)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── P1 잠금 안내 → 개발 레이어 #layerAccountLock ───────────────
RENAME_ID("box-lockout-p1", "layerAccountLock", 4)
RENAME_ID("lockout-account", "lockTargetId", 2)
R('<div id="layerAccountLock" class="alert-box alert-danger" style="display:none;">',
  '<div id="layerAccountLock" class="alert-box alert-danger" style="display:none;" data-dev-note="개발은 레이어(.layer-pop__overlay) — lock_reason auto_5fail만 P1, admin_block은 공통 Alert. 개발 레이어에 잠금 일시 · 접속 IP(뒤 2옥텟 마스킹) · 계정 상태 · 문의처">')
R('또는 최고 관리자에게 <strong>운영자 권한 관리(ADMN-CONF-005)</strong>에서 잠금 해제를 요청하세요.',
  '또는 최고 관리자에게 <strong>운영자 권한 관리(ADMN-CONF-005)</strong>에서 잠금 해제를 요청하세요.\n'
  '              <div style="margin-top:8px;" data-dev-flag="dev-only"><button type="button" class="link-btn"'
  + attrs(route="admin.password-reset.from-lock", method="POST", url=A + "/password-reset/from-lock", perm="로그인 밖", note="hidden login_id(old) → 비밀번호 찾기로")
  + ' onclick="switchAuthMode(\'reset-pw\')">비밀번호 재설정하기 →</button></div>')

# ── 시연 전용 ──────────────────────────────────────
ACT("triggerSessionExpiredBanner", flag="proto-only", note="시연 버튼 — 개발 대응 불필요")
ACT("triggerLockoutState", flag="proto-only", note="시연 버튼 — 개발 대응 불필요")
R('<select id="sel-demo-account"', '<select id="sel-demo-account" data-dev-flag="proto-only" data-dev-note="시연용 계정 프리셋"')
R('<div id="box-noperm"', '<div id="box-noperm" data-dev-flag="proto-only" data-dev-note="권한 없음 안내 — 개발은 admin_intended 세션 복귀(화면 표시 없음)"')
R('<div id="banner-session-expired"', '<div id="banner-session-expired" data-dev-note="개발 .login__expired — logout_reason idle · session_expired · session_kicked · account_disabled. 만료 1분 전 #layerSessionExpire [연장] POST admin.session.extend"')

# ── 모드 전환 → 페이지 3개 ────────────────────────────────
R('id="mode-btn-login" onclick=', 'id="mode-btn-login"' + attrs(route="admin.login", method="GET", url=A + "/login", perm="로그인 밖") + ' onclick=')
R('id="mode-btn-find-id" onclick=', 'id="mode-btn-find-id"' + attrs(route="admin.find-id.form", method="GET", url=A + "/find-id?restart=1", perm="로그인 밖") + ' onclick=')
R('id="mode-btn-reset-pw" onclick=', 'id="mode-btn-reset-pw"' + attrs(route="admin.password-reset.form", method="GET", url=A + "/password-reset?restart=1", perm="로그인 밖") + ' onclick=')
R('onclick="switchAuthMode(\'find-id\')">아이디 찾기 (ADMN-LOGIN-002)', attrs(route="admin.find-id.form", method="GET", url=A + "/find-id?restart=1", perm="로그인 밖").lstrip() + ' onclick="switchAuthMode(\'find-id\')">아이디 찾기 (ADMN-LOGIN-002)')
R('onclick="switchAuthMode(\'reset-pw\')">비밀번호 찾기 · 잠금 해제', attrs(route="admin.password-reset.form", method="GET", url=A + "/password-reset?restart=1", perm="로그인 밖").lstrip() + ' onclick="switchAuthMode(\'reset-pw\')">비밀번호 찾기 · 잠금 해제')

# ── 001 로그인 (#loginForm, LoginRequest) ─────────────────
NAME("inp-login-email", "login_id", note="개발 id #login_id · maxlength 60")
NAME("inp-login-pw", "password", note="개발 id #password · required(개발 min:6 — 정본 결정: 하한 검사 제거 권장)")
R('<div id="caps-lock-warn"', '<div id="caps-lock-warn" data-dev-note="개발 #capsLockWarn (.fm__help--warn)"')
R('<span id="lbl-fail-cnt"', '<span id="lbl-fail-cnt" data-dev-note="개발 .fm__help--count — 비밀번호 오류만 (n/5회)"')
R('onkeyup="checkCapsLock(event)" placeholder="비밀번호 입력 (오류 시연: wrong 입력)" />',
  'onkeyup="checkCapsLock(event)" placeholder="비밀번호 입력 (오류 시연: wrong 입력)" />\n'
  '              <button type="button" class="link-btn" data-dev-flag="dev-only" data-dev-note="개발 #passwordToggle (aria-pressed)" aria-pressed="false"'
  ' onclick="var i=document.getElementById(\'inp-login-pw\'); i.type = i.type === \'password\' ? \'text\' : \'password\'; this.setAttribute(\'aria-pressed\', i.type === \'text\');">비밀번호 표시</button>')
ACT("handleAdminLogin", route="admin.login.post", method="POST", url=A + "/login", perm="로그인 밖(분당 10회)",
    note="개발 #loginSubmit · 성공 후 must_change_password → password-change, admin_intended, 역할별 랜딩 순")

# ── 002 아이디 찾기 (FindIdSendCodeRequest · FindIdVerifyCodeRequest) ──
NAME("inp-find-name", "name", note="2~20자")
NAME("inp-find-phone", "phone", note="숫자 10~11자리(하이픈 없음)")
R("onclick=\"sendSmsOtp('find')\"", attrs(route="admin.find-id.send-code", method="POST", url=A + "/find-id/send-code", perm="로그인 밖").lstrip() + " onclick=\"sendSmsOtp('find')\"")
NAME("inp-find-otp", "code", note="digits:6 · 개발 id #code")
ACT("verifyFindIdOtp", route="admin.find-id.verify-code", method="POST", url=A + "/find-id/verify-code", perm="로그인 밖")
ACT("applyFoundEmailAndGoLogin", route="admin.find-id.to-login", method="POST", url=A + "/find-id/to-login", perm="로그인 밖",
    note="개발은 POST로 넘김(URL에 아이디 없음) · 비밀번호 찾기로 POST admin.find-id.to-password-reset")
R('<div id="box-found-id-result"', '<div id="box-found-id-result" data-dev-note="개발 #findIdResult"')

# ── 003 비밀번호 찾기 (1 이메일 → 2 휴대전화 → 3 저장) ──────────
NAME("inp-reset-email", "login_id", note="1단계 · max 60")
R('            <div class="form-group">\n              <label class="form-label">등록 휴대폰 번호 *</label>',
  '            <div class="form-group" data-dev-flag="dev-only" data-dev-note="1단계 이메일 인증번호 — PasswordResetSendCodeRequest · PasswordResetVerifyCodeRequest (정본 L109: 이메일+SMS 인증, 개발이 맞음)">\n'
  '              <label class="form-label">이메일 인증번호 (6자리) *</label>\n'
  '              <div style="display:flex; gap:8px;">\n'
  '                <input type="text" class="form-input" name="code" maxlength="6" placeholder="메일로 받은 6자리" />\n'
  '                <button type="button" class="btn-submit" style="width:140px; margin-top:0; font-size:12px;"'
  + attrs(route="admin.password-reset.send-code | admin.password-reset.verify-code", method="POST", url=A + "/password-reset/send-code | /password-reset/verify-code", perm="로그인 밖")
  + ' onclick="sendSmsOtp(\'reset-email\')">메일 발송 · 확인</button>\n'
  '              </div>\n'
  '            </div>\n'
  '            <div class="form-group" data-dev-flag="dev-only" data-dev-note="2단계 PasswordResetSmsSendRequest name (개발 #owner_name)">\n'
  '              <label class="form-label">이름 *</label>\n'
  '              <input type="text" class="form-input" name="name" placeholder="등록된 실명" />\n'
  '            </div>\n'
  '            <div class="form-group">\n              <label class="form-label">등록 휴대폰 번호 *</label>')
NAME("inp-reset-phone", "phone", note="2단계 · digits_between:10,11 (개발 #owner_phone)")
R("onclick=\"sendSmsOtp('reset')\"", attrs(route="admin.password-reset.sms.send-code", method="POST", url=A + "/password-reset/sms/send-code", perm="로그인 밖").lstrip() + " onclick=\"sendSmsOtp('reset')\"")
NAME("inp-reset-otp", "code", note="2단계 · digits:6 (개발 #sms_code) → POST admin.password-reset.sms.verify-code")
NAME("inp-reset-pw1", "password", note="3단계 · 8~64자 영문+숫자+특수문자(v6.92 D-CONF-05 결정 — 개발 max:12 → 64로) · maxlength 64")
NAME("inp-reset-pw2", "password_confirmation")
ACT("submitPasswordReset", route="admin.password-reset.store", method="POST", url=A + "/password-reset", perm="로그인 밖", note="개발 #pwResetForm · #pwResetSubmit")

# ── 비밀번호 변경 (개발 ADMN-LOGIN-B, AdminPasswordChangeRequest) ───
R('<div id="panel-change-pw" class="view-panel">', '<div id="panel-change-pw" class="view-panel" data-dev-note="개발 password-change 페이지 — 첫 로그인 · 90일 경과 공용(must_change_password)">')
NAME("inp-chg-cur", "current_password")
NAME("inp-chg-pw1", "password", note="8~64자(v6.92 D-CONF-05 결정, 개발 max:12 → 64) · 아이디 · 이름 3자 포함 금지 · 연속 4자 금지 · 최근 3개 재사용 금지")
NAME("inp-chg-pw2", "password_confirmation")
ACT("submitChangePw", route="admin.password-change.update", method="PUT", url=A + "/password-change", perm="로그인만")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("로그인", "switchAuthMode('login')", "#panel-login"),
    ("아이디 찾기", "switchAuthMode('find-id')", "#panel-find-id"),
    ("아이디 찾기 결과", "switchAuthMode('find-id'); verifyFindIdOtp()", "#box-found-id-result"),
    ("찾은 아이디로 로그인", "switchAuthMode('find-id'); verifyFindIdOtp(); applyFoundEmailAndGoLogin('cs.kim@sanjunmo.com')", "#panel-login"),
    ("비밀번호 재설정", "switchAuthMode('reset-pw')", "#panel-reset-pw"),
    ("비밀번호 변경", "switchAuthMode('change-pw')", "#panel-change-pw"),
    # P1 시연(triggerLockoutState)은 clean 원본에서도 #login-screen-badge가 없어 TypeError — 원본 문제라 VERIFY에서 뺌(보고)
    ("로그인 실패 1회", "switchAuthMode('login'); document.getElementById('inp-login-pw').value = 'wrong'; handleAdminLogin()", "#lbl-fail-cnt"),
    ("재설정 후 잠금 해제", "submitPasswordReset()", "#panel-login"),
]
