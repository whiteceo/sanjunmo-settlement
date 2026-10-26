"""ADMN-CONF-003 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-003.md
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
    "code": "ADMN-CONF-003",
    "devCommit": DEV_COMMIT,
    "progress": "구현(CONF-003 플레이어 설정 · CONF-008 인증 발송 설정). 재마스킹 시간 · 수동 포인트 유효기간 · 학습 Q&A 운영 방식 · IP 급증 감지는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.player-settings.index", "label": "플레이어/DRM 설정 (최고 관리자 전용)"},
        {"route": "admin.verify-settings.index", "label": "인증 발송 설정"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 탭 → 메뉴 2개 페이지 ─────────────────────────────
R('id="tab-btn-player" onclick=', 'id="tab-btn-player"' + attrs(route="admin.player-settings.index", method="GET", url=A + "/player-settings", perm="조회 + 최고 관리자") + ' onclick=')
R('id="tab-btn-auth" onclick=', 'id="tab-btn-auth"' + attrs(route="admin.verify-settings.index", method="GET", url=A + "/verify-settings", perm="조회") + ' onclick=')

# ── CONF-003 플레이어 (#playerSettingForm, PlayerSettingRequest) ──
ACT("savePlayerConfig", route="admin.player-settings.update", method="PUT", url=A + "/player-settings", perm="수정 + 최고 관리자",
    note="개발은 저장 전 확인 레이어 #layerPlayerSettingSave(변경 전/후 · 영향 · 재생 중 인원 GET admin.player-settings.playing-count.index)")
R('<button type="button" class="btn btn-sm btn-primary" data-dev-route="admin.player-settings.update"',
  '<button type="button" class="btn btn-sm btn-outline" data-dev-flag="dev-only" data-dev-note="#playerSettingRestore 기본값 복원" onclick="showToast(\'기본값을 폼에 채웠습니다. 저장해야 반영됩니다.\')">↺ 기본값 복원</button>\n'
  '            <button type="button" class="btn btn-sm btn-primary" data-dev-route="admin.player-settings.update"')
NAME("pl-wm-text", "watermark_content", value="email (개발 1종 — 프로토 3종 선택지와 다름)")
NAME("pl-wm-interval", "watermark_move_interval", note="1~300초")
NAME("pl-wm-duration", "watermark_display_duration", note="1~300 · ≤ 이동 주기")
NAME("pl-wm-opacity", "watermark_opacity", note="1~100 %")
NAME("pl-wm-size", "watermark_font_size", note="8~48 px")
DEVNAME('name="pl_fwd" value="ON"', "limit_forward", value="1")
DEVNAME('name="pl_fwd" value="OFF"', "limit_forward", value="0", note="무료 · 맛보기 예외는 개발 별도 필드 limit_forward_free_off")
NAME("pl-max-speed", "speed_max", value="0.5 ~ 2.0 단계 (프로토 2.5x는 개발 단계에 없음 — 정본 결정: 개발에 2.5 추가 권장)")
R('                        최소 <code>0.5x</code> ~ 최대',
  '                        최소 <select class="f-select" name="speed_min" style="width:90px;" data-dev-flag="dev-only" data-dev-note="PlayerSettingRequest speed_min (배속 단계)"><option value="0.5" selected>0.5x</option><option value="0.75">0.75x</option><option value="1.0">1.0x</option></select> ~ 최대')
NAME("pl-credit-speed", "progress_speed_policy",
     note="개발은 all · limited 2택 — 정본은 진도 인정 최대 배속 숫자(통합설계서 L273). 개발팀 전달 항목이라 프로토 숫자 입력 유지")
R('<input type="number" class="f-input" style="width:65px;" value="5" />',
  '<input type="number" class="f-input" style="width:65px;" value="5" data-dev-flag="proto-only" data-dev-note="24시간 접속 IP 급증 감지 — 개발 미구현" />')
R('                    <tr>\n                      <th>동시접속 세션 제어 (1차 오픈) *</th>',
  '                    <tr data-dev-flag="dev-only" data-dev-note="PlayerSettingRequest resume_use · resume_offset_sec(0~600) · rewind_allow · watermark_mobile_same · limit_forward_free_off">\n'
  '                      <th>이어보기 · 되감기 · 모바일</th>\n'
  '                      <td>\n'
  '                        <label style="margin-right:12px;"><input type="checkbox" name="resume_use" value="1" checked /> 이어보기</label>\n'
  '                        <input type="number" class="f-input" name="resume_offset_sec" style="width:65px;" value="5" /> 초 전부터 &nbsp;·&nbsp;\n'
  '                        <label style="margin-right:12px;"><input type="checkbox" name="rewind_allow" value="1" checked /> 10초 뒤로 허용</label>\n'
  '                        <label style="margin-right:12px;"><input type="checkbox" name="watermark_mobile_same" value="1" checked /> 모바일 앱 동일 적용</label>\n'
  '                        <label><input type="checkbox" name="limit_forward_free_off" value="1" checked /> 무료 · 맛보기 건너뛰기 허용</label>\n'
  '                      </td>\n'
  '                    </tr>\n'
  '                    <tr>\n                      <th>동시접속 세션 제어 (1차 오픈) *</th>')
R('<div style="font-size:13px; font-weight:800; margin-bottom:8px;">📋 최근 플레이어 · 보안 설정 변경 이력</div>',
  '<div style="font-size:13px; font-weight:800; margin-bottom:8px;">📋 최근 플레이어 · 보안 설정 변경 이력'
  ' <button type="button" class="btn btn-sm btn-outline" data-dev-flag="dev-only" data-dev-route="admin.player-settings.history.index" data-dev-method="GET" data-dev-url="' + A + '/player-settings/history" data-dev-perm="조회 + 최고 관리자" data-dev-note="admin_logs 원장 · 20건 페이지(history_page)" onclick="showToast(\'변경 이력 전체 페이지로 이동합니다.\')">전체 이력 ↗</button></div>')

# ── 프로토타입에만 있는 설정 카드 ────────────────────────
ACT("savePrivacyConfig", flag="proto-only", route="admin.privacy-settings.update (규칙)", method="PUT", url=A + "/privacy-settings", perm="수정",
    note="개발은 MaskingService::UNMASK_TTL_SECONDS=30 상수(정본: 회원 600초 · 권리자 30초 설정값 — 개발팀 전달)")
NAME("pv-member-sec", "pii_unmask_ttl_member_sec", note="(규칙) site_settings")
NAME("pv-holder-sec", "pii_unmask_ttl_holder_sec", note="(규칙) site_settings")
ACT("saveManualPointExpiry", flag="proto-only", route="admin.point-settings.update (규칙)", method="PUT", url=A + "/point-settings", perm="수정")
NAME("mpe-days", "manual_point_expire_options", note="(규칙) site_settings")
NAME("mpe-default", "manual_point_expire_default", note="(규칙) site_settings")
DEVNAME('name="lqna_mode" value="CAFE"', "study_qna_mode", value="cafe", note="(규칙) site_settings — 개발 미구현")
DEVNAME('name="lqna_mode" value="INTERNAL"', "study_qna_mode", value="internal")
R('<div class="card" id="card-lqna-mode">', '<div class="card" id="card-lqna-mode" data-dev-flag="proto-only" data-dev-note="학습 Q&amp;A 운영 방식 설정 — 개발 미구현">')

# ── CONF-008 인증 발송 (#verifySettingForm, VerifySettingRequest) ──
R('onclick="showToast(\'SMS 본인인증 발송 제한 정책이 저장되었습니다.\')"',
  attrs(route="admin.verify-settings.update", method="PUT", url=A + "/verify-settings", perm="수정", note="개발 #verifySaveOpen → #verifySaveLayer 확인 후 저장").lstrip()
  + ' onclick="showToast(\'SMS 본인인증 발송 제한 정책이 저장되었습니다.\')"')
R('<input type="number" class="f-input" style="width:75px;" value="5" />', '<input type="number" class="f-input" style="width:75px;" name="verify_daily_limit" value="5" />')
R('<input type="number" class="f-input" style="width:75px;" value="20" />', '<input type="number" class="f-input" style="width:75px;" name="verify_ip_daily_limit" value="20" />')
R('<input type="number" class="f-input" style="width:75px;" value="30" />',
  '<input type="number" class="f-input" style="width:75px;" value="30" data-dev-name="verify_resend_cooldown_sec" data-dev-note="site_settings 값만 있고 개발 화면 입력 없음" />')
R('<input type="number" class="f-input" style="width:75px;" value="3" />',
  '<input type="number" class="f-input" style="width:75px;" value="3" data-dev-name="verify_code_ttl_sec" data-dev-note="개발은 초 단위(300) · 화면 입력 없음" />')
R('              </tbody>\n            </table>\n\n            <div style="display:flex; justify-content:space-between; align-items:center; margin:18px 0 10px;">',
  '                <tr data-dev-flag="dev-only" data-dev-note="VerifySettingRequest verify_session_ttl_user_min(5~60분, 저장은 초 verify_session_ttl_user_sec)">\n'
  '                  <th>사용자 인증 유효 시간 *</th>\n'
  '                  <td colspan="3">인증 완료 후 <input type="number" class="f-input" style="width:75px;" name="verify_session_ttl_user_min" value="30" /> 분 동안 재인증 없이 진행</td>\n'
  '                </tr>\n'
  '              </tbody>\n            </table>\n\n'
  '            <div style="display:flex; gap:6px; align-items:center; margin:14px 0 0;" data-dev-flag="dev-only" data-dev-note="VerifyCapResetRequest user_id · reason — 조회 쿼리 account">\n'
  '              <span style="font-size:12.5px; font-weight:800;">계정 발송 횟수 수동 초기화</span>\n'
  '              <input type="text" class="f-input" name="account" style="width:200px;" maxlength="100" placeholder="이메일 또는 회원번호" />\n'
  '              <input type="text" class="f-input" name="reason" style="width:240px;" maxlength="200" placeholder="초기화 사유" />\n'
  '              <button type="button" class="btn btn-sm btn-outline" data-dev-route="admin.verify-settings.resets.store" data-dev-method="POST" data-dev-url="' + A + '/verify-settings/resets" data-dev-perm="등록" onclick="showToast(\'발송 횟수를 초기화했습니다.\')">초기화</button>\n'
  '            </div>\n\n'
  '            <div style="display:flex; justify-content:space-between; align-items:center; margin:18px 0 10px;">')
R('<input type="text" id="new-ip-val"',
  '<select class="f-select" name="mode" style="width:110px;" data-dev-flag="dev-only" data-dev-note="VerificationIpExceptionRequest mode"><option value="single">단일 IP</option><option value="cidr">IP 대역(CIDR, /16 이상)</option></select>\n'
  '                <input type="text" id="new-ip-val"')
NAME("new-ip-val", "ip", note="max 45 · mode별 형식")
NAME("new-ip-memo", "memo", note="max 100")
ACT("addWhitelistIp", route="admin.verify-settings.ip-exceptions.store", method="POST", url=A + "/verify-settings/ip-exceptions", perm="등록", note="개발은 #verifyIpLayer 레이어에서 등록")
ACT("removeWhitelistIp", route="admin.verify-settings.ip-exceptions.destroy", method="DELETE", url=A + "/verify-settings/ip-exceptions/{ipException}", perm="삭제")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("플레이어 탭", "switchConfTab('player')", "#panel-player"),
    ("인증 탭", "switchConfTab('auth')", "#panel-auth"),
    ("워터마크 미리보기", "switchConfTab('player'); updateWmPreview()", "#wm-preview-chip"),
    ("플레이어 저장", "switchConfTab('player'); savePlayerConfig()", "#player-hist-tbody"),
    ("재마스킹 저장", "switchConfTab('player'); savePrivacyConfig()", "#card-privacy-display"),
    ("포인트 유효기간 저장", "switchConfTab('player'); saveManualPointExpiry()", "#card-manual-point-expiry"),
    ("허용 IP 추가", "switchConfTab('auth'); document.getElementById('new-ip-val').value='1.2.3.4'; document.getElementById('new-ip-memo').value='테스트'; addWhitelistIp()", "#ip-whitelist-tbody"),
]
