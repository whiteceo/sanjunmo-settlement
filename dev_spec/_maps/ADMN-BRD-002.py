"""ADMN-BRD-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BRD-002.md
apply_dev_map.py가 읽는다. 각 항목의 기대 건수가 원본과 다르면 전체를 멈춘다.
"""
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
    "code": "ADMN-BRD-002",
    "devCommit": DEV_COMMIT,
    "progress": "구현(BRD-002 · 002-S1 · 002-P1). 유형별 분기 워크스페이스 · 매크로 · 주문 바인딩 · 세션 강제 로그아웃 · 타부서 이관중 상태는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.inquiries.index", "label": "1:1 문의 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# 이관 모달 id(transfer-modal)는 그대로 둔다 — 공통 모달 닫기 핫픽스가 id에 'modal'이 든 요소를 찾는다. 개발은 레이어 없이 분류 변경(category.update)

# ── 002 목록 · 스코어카드 ─────────────────────────────
ACT("filterByStatus", count=3, route="admin.inquiries.index", method="GET", url=A + "/inquiries", perm="조회",
    note="WAITING → status=received · SLA_WARN → sla_over=1 · ANSWERED → answered_today=1 (개발 스코어카드 5종: + processing · notify_fail)")
ACT("filterByCategory", count=7, route="admin.inquiries.index", method="GET", url=A + "/inquiries", perm="조회",
    note="유형 칩 → 개발 category_id(1:1 문의 분류 관리 소분류). 유형 5대 분기는 프로토타입 구성")
NAME("filter-status", "status", value="received 접수 · processing 처리중 · answered 답변완료 · hold 보류")
DEVNAME('<option value="WAITING">', "status", value="received")
R('<option value="TRANSFERRED">', '<option value="TRANSFERRED" data-dev-flag="proto-only" data-dev-note="개발 상태 없음 — 이관되면 assign_board로 RFD-002-S1 목록으로 옮겨 이 목록에서 빠짐">')
DEVNAME('<option value="IN_PROGRESS">', "status", value="processing")
DEVNAME('<option value="ANSWERED">', "status", value="answered")
DEVNAME('<option value="HOLD">', "status", value="hold")
NAME("filter-assignee", "mine", value="1 = 내 담당만")
DEVNAME('<option value="MINE">', "mine", value="1")
R('<option value="NONE">', '<option value="NONE" data-dev-flag="proto-only" data-dev-note="미지정 담당자 필터 — 개발 없음">')
R('id="filter-order-link"', 'id="filter-order-link" data-dev-flag="proto-only" data-dev-note="주문연동 필터 — 개발 없음(order_id는 회원 접수 때만)"')
R('<input type="date" class="input" value="2026-10-16" />',
  '<input type="date" class="input" name="date_from" value="2026-10-16" />\n'
  '            <input type="date" class="input" name="date_to" value="2026-10-16" data-dev-flag="dev-only" data-dev-note="개발 문의일 기간 date_from ~ date_to" />')
NAME("filter-keyword", "member", note="개발 회원 검색: 이름 · 이메일 · 비회원 이름, 숫자면 회원번호. 문의번호 · 카페 ID · 주문번호 검색은 개발 없음")
ACT("applyTableFilter", route="admin.inquiries.index", method="GET", url=A + "/inquiries", perm="조회",
    note="개발 추가 필터: has_file · sla_over · answered_today · notify_fail · unanswered · per_page")
R('<button type="button" class="btn btn-sm" onclick="requestTransfer(\'INQ',
  '<button type="button" class="btn btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.inquiries.download", method="GET", url=A + "/inquiries/download", perm="다운로드",
  note="엑셀(현재 조건) — 반출 사유 공용 모달 layerReason(reason · reason_etc · reason_ref). 선택 다운로드는 admin.inquiries.selected.download(POST, ids[])") + '>엑셀 다운로드</button>\n'
  '              <button type="button" class="btn btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.inquiries.assignees.update", method="PUT", url=A + "/inquiries/assignees", perm="수정 + 최고 관리자",
  name="assign_user_id", note="bulkAssignForm: ids[] · assign_user_id — 최고 관리자만 보임") + '>담당자 일괄 지정</button>\n'
  '              <button type="button" class="btn btn-sm" onclick="requestTransfer(\'INQ')
ACT("openCaseDetail", count=21, route="admin.inquiries.show", method="GET", url=A + "/inquiries/{inquiry}", perm="조회",
    note="개발 S1은 별도 페이지. 진입 시 수정 권한이 있으면 미지정 건을 본인에게 배정하고 접수 → 처리중(선점)")

# ── 002-S1 상세 · 답변 (processForm) ──────────────────
R('id="dt-user"', 'id="dt-user"' + attrs(route="admin.inquiries.member.show", method="GET", url=A + "/inquiries/{inquiry}/member", perm="조회",
  note="개발 002-P1 회원 컨텍스트 모달 memberContextModal(회원 · 최근 주문 · 수강 진도, fetch). 프로토타입은 상세 안 카드"))
ACT("alert", route="admin.attachments.download", method="GET", url=A + "/attachments/{attachment}/download", perm="다운로드")
ACT("insertMacro", count=8, flag="proto-only", note="유형별 매크로 삽입 — 개발 없음")
ACT("bindDetectedOrder", flag="proto-only", route="admin.inquiries.order.update (규칙)", method="PUT", url=A + "/inquiries/{inquiry}/order", perm="수정",
    note="주문번호 자동 탐지 · 바인딩 — 개발 없음(정책 질문)")
ACT("transferToRefundQueue", flag="proto-only", note="환불 심사 큐 즉시 이관 — 개발은 분류 변경(admin.inquiries.category.update) 하나로 이관")
ACT("resetConcurrentSession", flag="proto-only", note="세션 강제 로그아웃 — 개발은 회원 수강 · 기기 제어(ADMN-USER-003) 쪽")
NAME("dt-answer-input", "answer_content", note="action=answer일 때 필수 · 공백 제외 10자 이상")
R('placeholder="수험생에게 발송할 답변 내용을 입력하거나 상단 매크로 칩을 클릭하세요."></textarea>',
  'placeholder="수험생에게 발송할 답변 내용을 입력하거나 상단 매크로 칩을 클릭하세요."></textarea>\n'
  '                  <textarea class="textarea" name="internal_memo" style="min-height:60px; margin-top:8px;" placeholder="내부 메모 (회원 · 알림 미노출)" data-dev-flag="dev-only" data-dev-note="inquiries.internal_memo"></textarea>')
R('<input type="checkbox" checked /> 답변 등록 시',
  '<input type="checkbox" id="notifyAnswer" name="notify" value="1" checked' + attrs(note="끄면 notify_skip_reason(notifySkipRow) 필수 — 새 답변일 때") + ' /> 답변 등록 시')
ACT("saveDraftAnswer", route="admin.inquiries.update", method="PUT", url=A + "/inquiries/{inquiry}", perm="수정", name="action", value="draft")
R('class="btn btn-primary" onclick="submitFinalAnswer()"',
  'class="btn btn-primary"' + attrs(route="admin.inquiries.update", method="PUT", url=A + "/inquiries/{inquiry}", perm="수정", name="action", value="answer",
  note="개발 버튼 문구 '답변 등록'(id answerSubmit) + notify 체크. 답변완료 건 재답변은 edit_reason 필수") + ' onclick="submitFinalAnswer()"')
NAME("dt-hold-reason", "hold_reason", note="action=hold일 때 필수 · max:255")
R('placeholder="보류 사유 (타 부서 확인 대기 등)" style="height:28px; width:220px;" />',
  'placeholder="보류 사유 (타 부서 확인 대기 등)" style="height:28px; width:220px;" />\n'
  '            <input type="date" class="input" name="hold_until" style="height:28px;" data-dev-flag="dev-only" data-dev-note="보류 재개 예정일 — action=hold일 때 필수 · 오늘 이후" />')
ACT("holdCase", route="admin.inquiries.update", method="PUT", url=A + "/inquiries/{inquiry}", perm="수정", name="action", value="hold")
NAME("dt-reassign", "assign_user_id", note="1:1 문의 답변 가능 관리자만")
ACT("reassignCase", route="admin.inquiries.assignees.update", method="PUT", url=A + "/inquiries/assignees", perm="수정 + 최고 관리자",
    note="개발 단건 잠금 해제는 admin.inquiries.assignee.update(PUT /inquiries/{inquiry}/assignee, release_reason 필수)")
R('id="dt-assign-banner"', 'id="dt-assign-banner"' + attrs(note="개발 .iq-lock 잠금 배너 · .iq-lock__form(release_reason)"))

# ── 이관 모달(분류 변경) ───────────────────────────────
ACT("requestTransfer", count=2, perm="수정", note="개발은 분류 변경 폼(category_id) — 레이어 없음")
NAME("modal-target-cat", "category_id", note="소분류 inquiry_categories.id. 상품 Q&A · 학습 질문 게시판으로는 이관 불가. 결제 · 환불 분류면 RFD-002-S1로 이관")
R('id="modal-target-depts"', 'id="modal-target-depts" data-dev-flag="proto-only" data-dev-note="담당 부서 표시 — 개발 분류 변경은 category_id만"')
R('id="modal-memo"', 'id="modal-memo" data-dev-flag="proto-only" data-dev-note="내부 이관 메모 — 개발 분류 변경에 없음(답변 폼 internal_memo가 비슷)"')
ACT("confirmTransfer", route="admin.inquiries.category.update", method="PUT", url=A + "/inquiries/{inquiry}/category", perm="수정")

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("상세 view", "switchView('detail')", "#view-detail"),
    ("케이스 상세 열기", "openCaseDetail('INQ-20261016-088')", "#view-detail"),
    ("이관 모달", "openCaseDetail('INQ-20261016-091'); requestTransfer('INQ-20261016-091')", "#transfer-modal"),
    ("목록 복귀", "switchView('list')", "#view-list"),
    ("유형 필터", "filterByCategory('REFUND')", "#inquiry-table"),
    ("상태 카드", "filterByStatus('WAITING')", "#inquiry-table"),
]
