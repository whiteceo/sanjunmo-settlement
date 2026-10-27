"""ADMN-CONF-004 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-004.md
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
    "code": "ADMN-CONF-004",
    "devCommit": DEV_COMMIT,
    "progress": "구현(CONF-004 템플릿 · S1 예약 발송 · 개발 CONF-007 SENS 템플릿). 통합 발송 이력 · 실패 재발송(프로토 CONF-004-S2, 예전 표기 CONF-007 — v6.92) · 즉시 발송(재확인 모달)은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.message-templates.index", "label": "메시지 템플릿 관리 (S1 campaigns · S2 발송 이력(규칙) 포함)"},
        {"route": "admin.sens-templates.index", "label": "알림톡 SENS 템플릿 관리 (개발 CONF-007)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 탭 → 별도 페이지 ───────────────────────────────────
R('onclick="switchTab(\'tpl\')" id="tab-btn-tpl"', attrs(route="admin.message-templates.index", method="GET", url=A + "/message-templates", perm="조회").lstrip() + ' onclick="switchTab(\'tpl\')" id="tab-btn-tpl"')
R('onclick="switchTab(\'send\')" id="tab-btn-send"', attrs(route="admin.message-templates.campaigns.index", method="GET", url=A + "/message-templates/campaigns", perm="조회").lstrip() + ' onclick="switchTab(\'send\')" id="tab-btn-send"')
R('onclick="switchTab(\'hist\')" id="tab-btn-hist"', attrs(flag="proto-only", route="admin.message-logs.index (규칙)", method="GET", url=A + "/message-logs", perm="조회",
                                                         note="ADMN-CONF-004-S2 통합 발송 이력 · 실패 재발송(v6.92 코드 정정, 예전 표기 CONF-007) — 개발 미구현(notification_logs만). 1차는 이력 조회 + 발송사 장애 건 재발송만(D-ORD-12). CONF-007 코드는 개발 · 정본 모두 SENS 템플릿 관리").lstrip() + ' onclick="switchTab(\'hist\')" id="tab-btn-hist"')
R('<section id="view-hist" class="view-section">', '<section id="view-hist" class="view-section" data-dev-flag="proto-only" data-dev-note="재발송(규칙) admin.message-logs.resends.store POST /message-logs/{log}/resends">')

# ── CONF-004 템플릿 목록 ────────────────────────────────
R('<button class="btn btn-primary btn-sm" onclick="openTemplateModal()">',
  '<button class="btn btn-primary btn-sm"' + attrs(route="admin.message-templates.create", method="GET", url=A + "/message-templates/create?code=", perm="등록") + ' onclick="openTemplateModal()">')
R('<button class="btn btn-primary" onclick="openTemplateModal()">',
  '<button class="btn btn-primary"' + attrs(route="admin.message-templates.create", method="GET", url=A + "/message-templates/create?code=", perm="등록") + ' onclick="openTemplateModal()">')
R('onclick="openTemplateModal(\'${t.code}\')"', attrs(route="admin.message-templates.show", method="GET", url=A + "/message-templates/{messageTemplate}", perm="조회(저장은 수정)").lstrip() + ' onclick="openTemplateModal(\'${t.code}\')"')
ACT("syncAllSens", route="admin.sens-templates.sync.store", method="POST", url=A + "/sens-templates/sync", perm="등록 + 최고 관리자")
ACT("syncSensStatus", route="admin.sens-templates.sync.store", method="POST", url=A + "/sens-templates/sync", perm="등록 + 최고 관리자", note="개발은 건별 동기화 없이 전체 동기화")
ACT("jumpToSendWithTpl", route="admin.message-templates.campaigns.index", method="GET", url=A + "/message-templates/campaigns", perm="조회")
NAME("tpl-channel-filter", "channel", value="'' · alimtalk · sms · email (프로토 값 ALL · ALIMTALK · SMS_LMS · EMAIL)")
NAME("tpl-status-filter", "status", value="approved · pending · rejected · none (SENS 템플릿 목록 필터)")
R('<select id="tpl-type-filter"', '<select id="tpl-type-filter" data-dev-flag="proto-only" data-dev-note="메시지 성격 필터 — 개발 없음(컬럼 is_advertising은 있음)"')
NAME("tpl-keyword", "keyword")
R('<select id="tpl-channel-filter"',
  '<select name="group" data-dev-flag="dev-only" data-dev-note="개발 발송 조건 분류 필터(TemplateCatalog)"><option value="">발송 조건 전체</option><option value="join">회원가입</option><option value="member">회원</option><option value="payment">결제</option><option value="delivery">배송</option><option value="point">포인트</option><option value="inquiry">문의</option><option value="refund">환불</option><option value="notice">단체 공지</option></select>\n'
  '            <select id="tpl-channel-filter"')

# ── 템플릿 모달 → 개발 #templateForm (별도 페이지) ───────────
R('<div class="modal-backdrop" id="modal-template">', '<div class="modal-backdrop" id="modal-template" data-dev-note="개발은 레이어가 아니라 별도 페이지 create · show(#templateForm)">')
NAME("tpl-form-code", "code", note="등록 때만 · TemplateCatalog 코드(수정 시 무시)")
NAME("tpl-form-channel", "channel", value="alimtalk · sms · email (프로토 ALIMTALK · SMS_LMS · EMAIL)")
R('<select id="tpl-form-type"', '<select id="tpl-form-type" data-dev-name="is_advertising" data-dev-value="0 정보성 · 1 광고성" data-dev-note="개발은 템플릿 카탈로그 고정값 — 입력 칸 없음"')
R('<select id="tpl-form-domain"', '<select id="tpl-form-domain" data-dev-name="trigger_group" data-dev-note="개발은 code(발송 조건)로 정해짐"')
NAME("tpl-form-title", "subject", note="email이면 필수 · LMS 제목 40바이트")
R('<input type="text" id="tpl-form-sens-code"', '<input type="text" id="tpl-form-sens-code" data-dev-name="provider_template_code" data-dev-note="SENS 동기화본"')
R('<select id="tpl-form-status"', '<select id="tpl-form-status" data-dev-name="approval_status" data-dev-value="none · pending · approved · rejected"')
R('<input type="text" id="tpl-form-reject-reason"', '<input type="text" id="tpl-form-reject-reason" data-dev-name="approval_reason"')
ACT("insertTplVar", count=7, note="개발 [data-mt-chip] 치환 변수 칩")
NAME("tpl-form-body", "content", note="알림톡 1000자 · LMS 2000바이트 · 메일 10000자")
R('<input type="text" id="tpl-form-btn-name"', '<input type="text" id="tpl-form-btn-name" data-dev-flag="proto-only" data-dev-note="버튼은 SENS 동기화본 buttons — 입력 칸 없음"')
NAME("tpl-form-fallback", "use_fallback", value="1")
R('<label><input type="checkbox" id="tpl-form-fallback" name="use_fallback" data-dev-value="1" checked /> 알림톡 수신 불가 시 동일 본문으로 SMS/LMS 자동 전환 발송</label>',
  '<label><input type="checkbox" id="tpl-form-fallback" name="use_fallback" data-dev-value="1" checked /> 알림톡 수신 불가 시 동일 본문으로 SMS/LMS 자동 전환 발송</label>\n'
  '            <label data-dev-flag="dev-only" data-dev-note="MessageTemplateRequest is_active (required)"><input type="checkbox" name="is_active" value="1" checked /> 사용</label>')
R('        <div class="form-group">\n          <label class="form-label">알림톡 하단 링크 버튼명</label>',
  '        <div class="form-group full" data-dev-flag="dev-only" data-dev-note="MessageTemplateRequest fallback_content (#mtFallback)">\n'
  '          <label class="form-label">대체문자(LMS) 본문</label>\n'
  '          <textarea name="fallback_content" rows="3" placeholder="알림톡 버튼 링크는 URL로 풀어 씁니다."></textarea>\n'
  '        </div>\n'
  '        <div class="form-group">\n          <label class="form-label">알림톡 하단 링크 버튼명</label>')
R('onclick="saveTemplateWithStatus(\'SYNC\')"', attrs(flag="proto-only", note="저장 후 SENS 상태 동기화 — 개발은 목록의 전체 동기화만").lstrip() + ' onclick="saveTemplateWithStatus(\'SYNC\')"')
R('onclick="saveTemplateWithStatus(null)"', attrs(route="admin.message-templates.store | admin.message-templates.update", method="POST | PUT", url=A + "/message-templates | /message-templates/{messageTemplate}", perm="등록 | 수정").lstrip() + ' onclick="saveTemplateWithStatus(null)"')
R('        <button class="btn btn-warning" type="button" data-dev-flag="proto-only"',
  '        <button class="btn btn-outline" type="button" data-dev-flag="dev-only" data-dev-route="admin.message-templates.test-sends.store" data-dev-method="POST" data-dev-url="' + A + '/message-templates/{messageTemplate}/test-sends" data-dev-perm="등록" data-dev-note="#testSendForm 테스트 발송(횟수 제한)" onclick="showToast(\'테스트 발송을 요청했습니다.\')">📨 테스트 발송</button>\n'
  '        <button class="btn btn-warning" type="button" data-dev-flag="proto-only"')

# ── S1 타겟 예약 발송 (#campaignStoreForm, MessageCampaignRequest) ──
NAME("send-tpl-select", "template_id", note="notification_templates.id")
NAME("send-target-seg", "saved_group_id", note="개발 target_type = group(saved_group_id) · tags(tags[] · exclude_tags[] · tag_join) · members(회원 목록 검색 조건) — 프로토 고정 세그먼트 목록과 다름")
R('              <select id="send-target-seg"',
  '              <select name="target_type" style="margin-bottom:6px;" data-dev-flag="dev-only" data-dev-note="MessageCampaignRequest target_type"><option value="group">저장 그룹</option><option value="tags">태그 조합</option><option value="members">회원 목록 검색 조건</option></select>\n'
  '              <select id="send-target-seg"')
R('<select id="send-schedule-mode"', '<select id="send-schedule-mode" data-dev-note="개발은 예약만(scheduled_at 필수 · 지금 이후) — 즉시 발송은 정책 D-CONF-02"')
R('<option value="NOW">즉시 발송</option>', '<option value="NOW" data-dev-flag="proto-only">즉시 발송</option>')
NAME("send-schedule-dt", "scheduled_at", note="Y-m-d\\TH:i · 광고성 21:00~08:00 불가")
R('<input type="checkbox" id="send-fallback-chk"', '<input type="checkbox" id="send-fallback-chk" data-dev-note="개발은 템플릿 use_fallback을 따름 — 발송 단위 옵션 없음"')
R('<textarea id="send-body-preview"', '<textarea id="send-body-preview" data-dev-note="미리보기 — 개발은 본문을 템플릿에서 읽음"')
R('            <div class="form-group">\n              <label class="form-label">4. 발송 본문 확인',
  '            <div class="form-group" data-dev-flag="dev-only" data-dev-note="MessageCampaignRequest send_reason (필수 · max 200) · expected_target(화면 대상 수)">\n'
  '              <label class="form-label">발송 사유 (내부) *</label>\n'
  '              <input type="text" name="send_reason" maxlength="200" style="width:100%;" placeholder="예: 11월 실기 대비 특강 안내" />\n'
  '              <input type="hidden" name="expected_target" value="1420" />\n'
  '            </div>\n'
  '            <div class="form-group">\n              <label class="form-label">4. 발송 본문 확인')
R('<button class="btn btn-primary" onclick="executeTargetSend()">',
  '<span style="display:flex; gap:6px;" data-dev-flag="dev-only">'
  '<button class="btn btn-outline" type="button" data-dev-route="admin.message-templates.campaigns.download" data-dev-method="GET" data-dev-url="' + A + '/message-templates/campaigns/download" data-dev-perm="다운로드" data-dev-note="대상 명단 엑셀 — 사유 모달(reason)" onclick="showToast(\'대상 명단 엑셀은 다운로드 사유를 입력한 뒤 받습니다.\')">명단 엑셀</button>'
  '<button class="btn btn-outline" type="button" data-dev-route="admin.message-templates.campaigns.test-sends.store" data-dev-method="POST" data-dev-url="' + A + '/message-templates/campaigns/test-sends" data-dev-perm="등록" data-dev-note="#campaignTestForm" onclick="showToast(\'나에게 테스트 발송을 요청했습니다.\')">나에게 테스트</button></span>\n'
  '              <button class="btn btn-primary"' + attrs(route="admin.message-templates.campaigns.store", method="POST", url=A + "/message-templates/campaigns", perm="등록",
                                                      note="예약 상세 admin.message-templates.campaigns.show · 취소 PUT …/campaigns/{campaign}/status(발송 30분 전까지)") + ' onclick="executeTargetSend()">')

# ── v6.92: 즉시 발송 재확인 · 발송 이력 S2(조회 · 예약 취소 · 발송사 장애 건 재발송) — S-23 + D-CONF-02 · D-ORD-12 결정 반영 ──
R('<div class="ctx-note" id="send-rule-note"', '<div class="ctx-note" id="send-rule-note" data-dev-note="광고성 법정 금지 21:00~08:00 · 즉시 · 예약 시작 상한 20:50(설정값 adSendStartLimit) · 예약 취소 30분 전(설정값 sendCancelLeadMin = 개발 CANCEL_LEAD_MINUTES)"')
R('<div class="modal-backdrop" id="modal-send-confirm">', '<div class="modal-backdrop" id="modal-send-confirm" data-dev-flag="proto-only" data-dev-note="즉시 발송 재확인(대상 수 · 비용 · 본문) — 개발은 예약만. 즉시 발송 허용(S-23 · D-CONF-02 결정)">')
ACT("confirmImmediateSend", flag="proto-only", route="admin.message-templates.campaigns.store", method="POST", url=A + "/message-templates/campaigns", perm="등록",
    note="(규칙) 즉시 발송 = send_mode immediate · scheduled_at 없음 — 개발 MessageCampaignRequest는 scheduled_at 필수(after:now)")
NAME("hist-status-filter", "status", value="'' 전체 · done 발송완료 · reserved 예약 · canceled 예약 취소 · failed 실패 있음 (규칙, 프로토 값 ALL · DONE · RESERVED · CANCELED · FAILED 유지)")
NAME("hist-keyword", "keyword", note="(규칙) 배치 ID · 템플릿 코드 · 제목")
ACT("cancelReserved", route="admin.message-templates.campaigns.status.update", method="PUT", url=A + "/message-templates/campaigns/{campaign}/status", perm="수정",
    note="예약 취소 — 발송 30분 전까지(CANCEL_LEAD_MINUTES · 설정값)")
ACT("openFailModal", flag="proto-only", route="admin.message-logs.show (규칙)", method="GET", url=A + "/message-logs/{batch}", perm="조회", note="(규칙) 실패 건 · 실패 사유")
R('<div class="modal-backdrop" id="modal-hist-fail">', '<div class="modal-backdrop" id="modal-hist-fail" data-dev-flag="proto-only" data-dev-note="실패 사유 provider_error · timeout(재발송 대상) · optout · invalid_number · not_kakao_user(재발송 안 함) (규칙)">')
ACT("resendProviderFails", flag="proto-only", route="admin.message-logs.resends.store (규칙)", method="POST", url=A + "/message-logs/{batch}/resends", perm="등록",
    note="발송사 장애 건만 재발송(D-ORD-12) — 광고성은 야간 구간 · 수신 동의 재확인")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
U = "document.querySelectorAll('.modal-backdrop').forEach(m => m.style.removeProperty('display')); "
VERIFY = [
    ("템플릿 탭", "switchTab('tpl')", "#view-tpl"),
    ("발송 탭", "switchTab('send')", "#view-send"),
    ("이력 탭", "switchTab('hist')", "#view-hist"),
    ("신규 템플릿 모달", U + "switchTab('tpl'); openTemplateModal()", "#modal-template"),
    ("템플릿 상세 모달", U + "switchTab('tpl'); openTemplateModal(TEMPLATES[0].code)", "#modal-template"),
    ("채널 필터", "switchTab('tpl'); document.getElementById('tpl-channel-filter').value='EMAIL'; renderTemplates()", "#view-tpl"),
    ("발송 실행", "switchTab('send'); executeTargetSend()", "#view-send|#view-hist"),
    ("실패 건 · 재발송 모달(v6.92 S2)", U + "switchTab('hist'); openFailModal('SND-261016-01')", "#modal-hist-fail"),
]
