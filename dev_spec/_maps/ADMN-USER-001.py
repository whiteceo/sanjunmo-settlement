"""ADMN-USER-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-USER-001.md
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
    "code": "ADMN-USER-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(USER-001~006). 002-P3 · 006-S3 · 비밀번호 초기화 등은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.members.index", "label": "회원 관리 (목록 · 상세)"},
        {"route": "admin.members.course.index", "label": "수강 · 기기 제어"},
        {"route": "admin.member-progress.index", "label": "진도율 / 이어보기"},
        {"route": "admin.members.blacklist.index", "label": "블랙리스트"},
        {"route": "admin.members.group.index", "label": "그룹 · 태그"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modal-excel-p1", "layerMemberDownload", 5)
RENAME_ID("modal-point-p1", "layerPointGrant", 5)
RENAME_ID("modal-status", "layerMemberStatus", 5)
RENAME_ID("modal-social", "layerSocialUnlink", 4)
RENAME_ID("modal-bl-release", "layerSanctionRelease", 5)
RENAME_ID("excel-reason", "memberDownloadReason", 4)
RENAME_ID("ex-cols-block", "memberDownloadFields", 2)
RENAME_ID("btn-excel-submit", "memberDownloadSubmit", 3)
RENAME_ID("social-reason", "socialUnlinkReason", 7)

# ── 001 목록 검색 ────────────────────────────────────
R('<input type="date" class="f-input" value="2026-07-17" />', '<input type="date" class="f-input" id="dateFrom" name="date_from" value="2026-07-17" />')
R('<input type="date" class="f-input" value="2026-10-17" />', '<input type="date" class="f-input" id="dateTo" name="date_to" value="2026-10-17" />')
R('<div class="chip-group" id="status-chips">', '<div class="chip-group" id="status-chips"' + attrs(name="status", value="'' 전체 · active 정상 · dormant 휴면 · suspended 정지(표시용 파생: is_locked) — 비밀번호 5회 잠금 필터는 개발 없음") + '>')
R('<select class="f-select" style="width:130px;">\n                      <option>이름</option>',
  '<select class="f-select" style="width:130px;" name="search_type"' + attrs(note="개발 값: name · email · phone_tail · member_no — 산준모 카페 ID 검색은 개발 없음") + '>\n                      <option value="name">이름</option>')
R('<option>이메일(ID)</option>\n                      <option>휴대폰 뒤 4자리</option>\n                      <option>회원번호</option>\n                      <option>산준모 카페 ID</option>',
  '<option value="email">이메일(ID)</option>\n                      <option value="phone_tail">휴대폰 뒤 4자리</option>\n                      <option value="member_no">회원번호</option>\n                      <option value="cafe_id" data-dev-flag="proto-only" data-dev-note="개발 SEARCH_TYPES에 없음(users.cafe_id 컬럼은 있음)">산준모 카페 ID</option>')
NAME("kw-input", "keyword")
R('<input type="number" class="f-input" style="width:90px;" value="0" /> ~\n                    <input type="text" class="f-input" style="width:100px;" placeholder="제한없음" /> P',
  '<input type="number" class="f-input" style="width:90px;" name="point_min" value="0" /> ~\n                    <input type="text" class="f-input" style="width:100px;" name="point_max" placeholder="제한없음" /> P')
NAME("chk-minus-only", "minus_only", value="1")
R('<select class="f-select" style="width:220px;">\n                      <option value="">전체 (ADMN-USER-006 태그 연동)</option>',
  '<select class="f-select" style="width:220px;" name="group_id"' + attrs(note="값 = user_groups.id (프로토타입은 태그 코드)") + '>\n                      <option value="">전체 (ADMN-USER-006 태그 연동)</option>')
R('<select class="f-select" style="width:170px;">\n                      <option>전체</option>\n                      <option>30일 이상 미접속</option>\n                      <option>90일 이상 미접속</option>\n                      <option>1년 경과 (휴면 전환 대상)</option>',
  '<select class="f-select" style="width:170px;" name="inactive_days">\n                      <option value="">전체</option>\n                      <option value="30">30일 이상 미접속</option>\n                      <option value="90">90일 이상 미접속</option>\n                      <option value="365">1년 경과 (휴면 전환 대상)</option>')
R('<input type="checkbox" /> 주소 미등록 (교재 주문 건 발송 불가 CS 추출용)',
  '<input type="checkbox" name="address" value="none"' + attrs(note="개발은 라디오 3택: '' 전체 · registered 등록자 · none 미등록") + ' /> 주소 미등록 (교재 주문 건 발송 불가 CS 추출용)')
R('<button type="button" class="btn btn-dark" onclick="showToast(\'검색 조건 원문이',
  '<button type="button" class="btn btn-dark"' + attrs(route="admin.members.index", method="GET", url=A + "/members", perm="조회") + ' onclick="showToast(\'검색 조건 원문이')
NAME("grid-page-size", "per_page")
R('<th style="width:36px;"><input type="checkbox" onchange="toggleAllRows(this.checked)" /></th>',
  '<th style="width:36px;"><input type="checkbox" id="checkAll" onchange="toggleAllRows(this.checked)" /></th>')
R('<input type="checkbox" class="row-chk" onchange="updateSelCount()" />', '<input type="checkbox" class="row-chk member-check" name="ids[]" onchange="updateSelCount()" />', 6)
R('<th class="tr-right">적립 P ▾</th>', '<th class="tr-right"' + attrs(name="sort=paid_point", note="개발 라벨 '유상 P' — 화면 라벨은 정본 '적립 P' 유지") + '>적립 P ▾</th>')
R('<th class="tr-right">무상 P ▾</th>', '<th class="tr-right"' + attrs(name="sort=free_point") + '>무상 P ▾</th>')
R('<th>산준모 카페 ID</th>', '<th data-dev-flag="proto-only" data-dev-note="개발 목록에 없음(users.cafe_id)">산준모 카페 ID</th>')
ACT("sortMemberGrid", count=2, note="개발 정렬 키: created_at · paid_point · free_point · last_login_at (sort · direction)")

ACT("openBulkTagModal", route="admin.members.group.index", method="GET", url=A + "/members/group", perm="조회(그룹 · 태그 메뉴)")
R('onclick="openBulkTagModal()"', 'id="assignTagButton" onclick="openBulkTagModal()"')
ACT("sendBulkMsg", route="admin.message-templates.campaigns.create", method="GET", url=A + "/message-templates/campaigns/create", perm="등록(메시지 템플릿 메뉴)")
R('onclick="sendBulkMsg()"', 'id="campaignButton" onclick="sendBulkMsg()"')
ACT("submitExcelDownload", route="admin.members.download", method="GET", url=A + "/members/download", perm="다운로드")
NAME("memberDownloadReason", "reason", note="ReasonRequest: reason · reason_etc · reason_ref")
NAME("ex-pledge-1", "pledge_purpose")
NAME("ex-pledge-2", "pledge_destroy")
R('id="memberDownloadFields"', 'id="memberDownloadFields"' + attrs(name="fields[]", value="joined_at · name · email · phone · address · points · status (기본 해제 phone · address)"))

# ── 002 상세 ───────────────────────────────────────
ACT("saveMemberProfile", count=2, route="admin.members.update", method="PUT", url=A + "/members/{member}", perm="수정")
NAME("dt-mkt-agree", "is_marketing_agreed")
R('id="dt-cafe"', 'id="dt-cafe" data-dev-flag="proto-only" data-dev-note="개발 회원 정보 수정(MemberRequest)에 없음 — users.cafe_id 컬럼은 있음"')
NAME("dt-status-sel", "status", note="상태 변경은 별도 PUT /members/{member}/status — active · dormant만. 정지는 블랙리스트 등재로만")
ACT("openStatusModal", perm="수정")
ACT("confirmStatusChange", route="admin.members.status.update", method="PUT", url=A + "/members/{member}/status", perm="수정")
NAME("modal-st-val", "status", value="active · dormant")
NAME("modal-st-reason", "reason")
ACT("unmaskMemberDetail", note="마스킹 해제 — 프로토타입 사유 10자 · 재마스킹 설정값은 개발 없음(30초 고정)")
ACT("confirmUnmaskMember", route="admin.masking.unmask", method="POST", url=A + "/masking/unmask", perm="메뉴 권한 밖(MaskingService::canUnmask, 현재 최고 관리자만)")
NAME("unmask-reason", "reason", note="개발 마스킹 해제는 사유를 받지 않음(정책 질문 회원관리 #2)")
ACT("openPointModal", perm="등록")
ACT("submitManualPoint", route="admin.members.points.store", method="POST", url=A + "/members/{member}/points", perm="등록")
DEVNAME('name="pt_mode" value="PLUS"', "direction", value="grant")
DEVNAME('name="pt_mode" value="MINUS"', "direction", value="deduct")
NAME("pt-amount", "amount")
NAME("pt-reason-cat", "reason_code", note="개발 7종: cs_outage · cs_delivery · event · promotion · correction · partner · other — 프로토타입 4종과 목록이 다름")
NAME("pt-reason-txt", "reason")
NAME("pt-exp", "expire_preset", value="30 · 90 · 180 (개발은 custom + expire_date 직접 지정도 있음 — 정본은 3택)")
R('id="pt-alimtalk"', 'id="pt-alimtalk" data-dev-flag="proto-only" data-dev-note="지급 알림톡 — 개발 미구현"')
ACT("openSocialModal", perm="삭제")
ACT("unlinkSocial", route="admin.members.social.destroy", method="DELETE", url=A + "/members/{member}/social/{socialAccount}", perm="삭제")
NAME("socialUnlinkReason", "reason")
ACT("revokeCoupon", route="admin.members.coupons.update", method="PUT", url=A + "/members/{member}/coupons/{userCoupon}", perm="수정")
ACT("openDirectMsgModal", count=3, flag="proto-only", note="1:1 메시지 즉시 발송(002-P3) — 개발 미구현")
ACT("submitDirectMsg", flag="proto-only", route="admin.members.messages.store (규칙)", method="POST", url=A + "/members/{member}/messages", perm="등록")
ACT("openPwTempModal", flag="proto-only", note="임시 비밀번호 메일 — 개발 미구현(버튼 비활성)")
ACT("confirmPwTemp", flag="proto-only", route="admin.members.temp-password.store (규칙)", method="POST", url=A + "/members/{member}/temp-password", perm="등록")
NAME("pwt-reason", "reason")
ACT("openPwResetModal", flag="proto-only", note="비밀번호 수동 초기화 — 개발 미구현")
ACT("confirmPwReset", flag="proto-only", route="admin.members.password.update (규칙)", method="PUT", url=A + "/members/{member}/password", perm="수정 + 최고 관리자")
ACT("unlockPw5", flag="proto-only", route="admin.members.lock.update (규칙)", method="PUT", url=A + "/members/{member}/lock", perm="수정")
ACT("addCsMemo", flag="proto-only", route="admin.members.cs-memos.store (규칙)", method="POST", url=A + "/members/{member}/cs-memos", perm="등록",
    note="개발은 관리자 메모 1칸(users.admin_memo, PUT /members/{member})")
NAME("cm-content", "content", note="(규칙) CS 상담 기록 — 개발 미구현")

# ── 003 수강 · 기기 ─────────────────────────────────
NAME("crs-search-type", "type")
DEVNAME('name="adj_type" value="EXTEND"', "(라우트로 구분)", value="extend → admin.members.course.extend.update")
DEVNAME('name="adj_type" value="SHORTEN"', "(없음)", note="종료일 단축 — 개발 미구현(정책 질문 회원관리 #5)")
R('name="adj_type" value="SHORTEN"', 'name="adj_type" value="SHORTEN" data-dev-flag="proto-only"')
DEVNAME('name="adj_type" value="PAUSE"', "(라우트로 구분)", value="pause → admin.members.course.pause.update (indefinite 0 · 1)")
NAME("ext-days-input", "days", note="프리셋 days_preset 7 · 15 · 30 · 60 · 90")
NAME("ext-reason-input", "reason")
R('<input type="text" id="ext-reason-input"',
  '<select class="f-select" name="reason_code" style="width:100%; margin-bottom:6px;" data-dev-flag="dev-only" data-dev-note="개발 UserCourseControlService::REASONS">'
  '<option value="">조정 사유 구분 선택</option><option value="cs_compensation">CS 보상(서비스 장애)</option><option value="device_issue">기기 문제</option>'
  '<option value="long_absence">군입대·장기부재</option><option value="event">이벤트 제공</option><option value="correction">오적용 정정</option><option value="etc">기타</option></select>\n'
  '                    <input type="text" id="ext-reason-input"')
ACT("applyCourseExtend", route="admin.members.course.extend.update | admin.members.course.pause.update", method="POST",
    url=A + "/members/course/{userCourse}/extend | /pause", perm="수정")
ACT("releaseCoursePause", route="admin.members.course.resume.update", method="POST", url=A + "/members/course/{userCourse}/resume", perm="수정")
ACT("killSession", flag="proto-only", route="admin.members.course.session.destroy (규칙)", method="POST", url=A + "/members/course/{userCourse}/session", perm="삭제",
    note="개발은 SPK 콘솔에서 처리(정책 질문 회원관리 #7)")
ACT("recordConsoleDeviceReset", flag="proto-only", note="SPK 콘솔 기기 리셋 기록 — 개발에 기록 경로 없음")

# ── 004 진도율 · P1 보정 ──────────────────────────────
ACT("m3fRecalcProgress", route="admin.member-progress.recalculate", method="POST", url=A + "/member-progress/recalculate", perm="수정(접미사 예외)")
ACT("openProgressAdjustModal", count=6, route="admin.member-progress.adjust.edit", method="GET",
    url=A + "/member-progress/{userCourse}/lectures/{lecture}/adjust", perm="수정")
ACT("submitProgressAdjustLedger", route="admin.member-progress.adjust.update", method="PUT",
    url=A + "/member-progress/{userCourse}/lectures/{lecture}/adjust", perm="수정")
ACT("m3fShowAdjHistory", route="admin.member-progress.adjust.history.index", method="GET",
    url=A + "/member-progress/{userCourse}/lectures/{lecture}/adjust/history", perm="조회")
NAME("m3f-pa-rate", "adjusted_rate", note="정수 0~100")
NAME("m3f-pa-type", "reason_code", note="개발 4종: log_lost · ingest_missed · lecture_reorg · etc(+reason_text) — 프로토타입 목록과 다름(정책 질문 회원관리 #9)")
NAME("m3f-pa-reason", "detail", note="개발 20~1000자")
NAME("m3f-pa-file", "evidence[]", note="1~5개 필수")

# ── 005 블랙리스트 ──────────────────────────────────
ACT("openManualBlacklistModal", count=4, route="admin.members.blacklist.create", method="GET", url=A + "/members/blacklist/create?member_id=", perm="등록(블랙리스트 메뉴)")
ACT("submitManualBlacklistMember", route="admin.members.blacklist.store", method="POST", url=A + "/members/blacklist", perm="등록",
    note="member_id · reason_type(concurrent_ip · concurrent_session · speed_tamper · minus_point · other) · duration(7 · 30 · permanent) · reason")
ACT("releaseBlacklistRow", count=2, perm="수정(블랙리스트 메뉴)")
ACT("confirmBlacklistRelease", route="admin.members.blacklist.update", method="PUT", url=A + "/members/blacklist/{sanction}", perm="수정")
NAME("blr-reason", "reason")
ACT("releaseMemberSuspension", route="admin.members.blacklist.update", method="PUT", url=A + "/members/blacklist/{sanction}", perm="수정(블랙리스트 메뉴)")
ACT("forceWithdrawRow", flag="proto-only", route="admin.members.withdrawal.store (규칙)", method="POST", url=A + "/members/{member}/withdrawal", perm="등록",
    note="관리자 강제 탈퇴 — 개발은 서비스 함수만, 경로 없음")

# ── 006 그룹 · 태그 ────────────────────────────────
ACT("openTagFormPage", count=2, route="admin.members.group.tag.create", method="GET", url=A + "/members/group/tag/create?mode=manual|auto", perm="등록")
ACT("submitTagCreate", route="admin.members.group.tag.store | admin.members.group.tag.update", method="POST | PUT", url=A + "/members/group/tag | /members/group/tag/{tag}", perm="등록 | 수정")
NAME("m3f-tc-name", "name")
R('id="m3f-tc-code"', 'id="m3f-tc-code"' + attrs(note="개발은 user_groups.code 자동 — 입력 칸 없음"))
DEVNAME('name="m3f-tc-type" value="AUTO"', "assign_method", value="auto")
DEVNAME('name="m3f-tc-type" value="MANUAL"', "assign_method", value="manual")
R('          <div class="m3f-field">\n            <span class="m3f-label">부여 유형</span>',
  '          <div class="m3f-grid2" data-dev-flag="dev-only" data-dev-note="개발 MemberTagRequest: axis · badge_color (필수)">\n'
  '            <div class="m3f-field">\n'
  '              <label for="m3f-tc-axis">태그 분류 <span class="m3f-req">*</span></label>\n'
  '              <select id="m3f-tc-axis" name="axis" class="f-select" style="width:100%;"><option value="certificate">자격증</option><option value="learning">학습 상태</option><option value="campaign">캠페인</option></select>\n'
  '            </div>\n'
  '            <div class="m3f-field">\n'
  '              <label for="m3f-tc-color">배지 색 <span class="m3f-req">*</span></label>\n'
  '              <select id="m3f-tc-color" name="badge_color" class="f-select" style="width:100%;"><option value="gray">회색</option><option value="blue" selected>파랑</option><option value="green">초록</option><option value="orange">주황</option><option value="red">빨강</option><option value="purple">보라</option></select>\n'
  '            </div>\n'
  '          </div>\n'
  '          <div class="m3f-field">\n            <span class="m3f-label">부여 유형</span>')
ACT("openTagCondModal", note="조건 → conditions[n][field|op|value|join] (개발 조건 항목 5종)")
ACT("openTagDeleteModal", perm="삭제")
ACT("m3fConfirmDeleteTag", route="admin.members.group.destroy", method="DELETE", url=A + "/members/group/{group}", perm="삭제")
ACT("m3fAddExclude", flag="proto-only", route="admin.members.group.tag.exclusions.store (규칙)", method="POST", url=A + "/members/group/tag/{tag}/exclusions", perm="등록",
    note="개발은 서비스 excludeMember만, 경로 없음")
ACT("m3fRestoreExclude", flag="proto-only", route="admin.members.group.tag.exclusions.destroy (규칙)", method="DELETE", url=A + "/members/group/tag/{tag}/exclusions/{user}", perm="삭제")
NAME("m3f-bk-tag", "group_id")
DEVNAME('name="m3f-bk-action" value="ADD"', "action", value="assign")
DEVNAME('name="m3f-bk-action" value="REMOVE"', "action", value="remove")
DEVNAME('name="m3f-bk-scope" value="CHECKED"', "scope", value="selected (+ member_ids[])")
DEVNAME('name="m3f-bk-scope" value="COND"', "scope", value="filter (+ filter[])")
DEVNAME('name="m3f-bk-scope" value="EXCEL"', "scope", value="upload (먼저 POST members/group/upload)")
NAME("m3f-bk-file", "file", note="POST admin.members.group.upload.store → 미매칭은 GET admin.members.group.unmatched.download")
NAME("m3f-bk-reason", "reason")
ACT("m3fBulkExecute", route="admin.members.group.member.update", method="PUT", url=A + "/members/group/member", perm="수정")
ACT("openGroupSaveModal", route="admin.members.group.saved.create", method="GET", url=A + "/members/group/saved/create", perm="등록")
ACT("m3fSaveGroup", count=2, route="admin.members.group.saved.store", method="POST", url=A + "/members/group/saved", perm="등록")
NAME("m3f-grp-name", "name")
NAME("m3f-gs-memo", "description")
DEVNAME('name="m3f-grp-op" value="AND"', "tag_join", value="and")
DEVNAME('name="m3f-grp-op" value="OR"', "tag_join", value="or")
DEVNAME('name="m3f-grp-mode" value="DYNAMIC"', "group_type", value="dynamic")
DEVNAME('name="m3f-grp-mode" value="STATIC"', "group_type", value="static")
DEVNAME('name="m3f-grp-share" value="ALL"', "share_scope", value="all")
DEVNAME('name="m3f-grp-share" value="MINE"', "share_scope", value="owner")
ACT("m3fEditGroup", flag="proto-only", route="admin.members.group.saved.update (규칙)", method="PUT", url=A + "/members/group/saved/{group}", perm="수정")
ACT("m3fConfirmDeleteGroup", flag="proto-only", route="admin.members.group.saved.destroy (규칙)", method="DELETE", url=A + "/members/group/saved/{group}", perm="삭제")
ACT("m3fGroupMessage", flag="proto-only", note="저장 그룹 → 발송 연결 — 개발 경로 없음")
ACT("m3fGroupCoupon", flag="proto-only", note="저장 그룹 → 쿠폰 연결 — 개발 경로 없음(쿠폰은 그룹 발급 지원)")
ACT("openTagResultPage", flag="proto-only", route="admin.members.group.batches.show (규칙)", method="GET", url=A + "/members/group/batches/{batch}", perm="조회")
ACT("m3fTrRetry", flag="proto-only", route="admin.members.group.batches.retry.store (규칙)", method="POST", url=A + "/members/group/batches/{batch}/retry", perm="등록")
ACT("m3fTrRevert", flag="proto-only", route="admin.members.group.batches.destroy (규칙)", method="DELETE", url=A + "/members/group/batches/{batch}", perm="삭제")
ACT("m3fTrExcelDownload", flag="proto-only", route="admin.members.group.batches.download (규칙)", method="GET", url=A + "/members/group/batches/{batch}/download", perm="다운로드")
