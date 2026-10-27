"""ADMN-BRD-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BRD-001.md
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
    "code": "ADMN-BRD-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(BRD-001 · 006 · 003 · 004 · 009와 각 S1). 공지 분류 · 행 고정 토글 · FAQ TOP 고정 · 카테고리 이름 변경/순서/노출 · 상품 Q&A 엑셀 · 당첨자 경품 지급은 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.notices.index", "label": "공지사항 관리"},
        {"route": "admin.faqs.index", "label": "FAQ 관리"},
        {"route": "admin.product-qnas.index", "label": "상품 Q&A 관리"},
        {"route": "admin.study-qnas.index", "label": "학습 Q&A 관리"},
        {"route": "admin.winners.index", "label": "당첨자 발표 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# 모달 id(modal-faq-cat · modal-pqna · modal-lqna)는 그대로 둔다 — 개발은 FAQ 카테고리 = 목록 안 인라인 폼, 상품/학습 Q&A S1 = 별도 페이지(show)라 레이어 id가 없다

# ── 탭 → 개발 메뉴 ──────────────────────────────────
for tab, route, url in (("notice", "admin.notices.index", "/notices"), ("faq", "admin.faqs.index", "/faqs"),
                        ("pqna", "admin.product-qnas.index", "/product-qnas"), ("qna", "admin.study-qnas.index", "/study-qnas"),
                        ("winner", "admin.winners.index", "/winners")):
    R(f'onclick="switchTab(\'{tab}\')"', attrs(route=route, method="GET", url=A + url, perm="조회").lstrip() + f' onclick="switchTab(\'{tab}\')"')

# ── BRD-001 공지 목록 ────────────────────────────────
R('id="notice-cat-filter"', 'id="notice-cat-filter" data-dev-flag="proto-only" data-dev-note="공지 분류 — 개발 없음(게시판 code=notice 하나). 개발 필터: status · pinned · device_scope · date_from · date_to · author"')
NAME("notice-keyword", "keyword", note="개발 keyword = 제목 + 본문")
R('<button class="btn btn-primary" onclick="openNoticePage(null)">',
  '<button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.notices.status.update", method="PUT", url=A + "/notices/status", perm="수정", note="bulkForm: ids[]") + '>선택 숨김</button>\n'
  '            <button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.notices.selected.destroy", method="DELETE", url=A + "/notices/selected", perm="삭제", note="bulkForm: ids[] (소프트 삭제)") + '>선택 삭제</button>\n'
  '            <button class="btn btn-primary"' + attrs(route="admin.notices.create", method="GET", url=A + "/notices/create", perm="등록") + ' onclick="openNoticePage(null)">')
R('onclick="openNoticePage(${n.id})"', attrs(route="admin.notices.edit", method="GET", url=A + "/notices/{notice}/edit", perm="수정").lstrip() + ' onclick="openNoticePage(${n.id})"')
ACT("toggleNoticePin", flag="proto-only", note="행 단위 상단 고정 즉시 토글 — 개발은 수정 폼 is_pinned · pin_order로만")

# ── BRD-001-S1 공지 등록 · 수정 (noticeForm) ──────────────
R('id="notice-form-cat"', 'id="notice-form-cat" data-dev-flag="proto-only" data-dev-note="공지 분류 선택 — 개발 없음(정책 질문)"')
NAME("notice-form-pin", "is_pinned", value="1", note="고정 최대 5건(Post::PIN_MAX). 순위는 pin_order 1~5")
R('<label><input type="checkbox" id="notice-form-visible" checked /> 즉시 노출</label>',
  '<label><input type="checkbox" id="notice-form-visible" checked' + attrs(name="publish_mode", value="immediate(켬) · draft(끔)", note="개발 publish_mode 3택: immediate · scheduled · draft. 숨김은 목록 일괄 숨김으로만") + ' /> 즉시 노출</label>')
R('<div class="form-group full">\n            <label class="form-label">공지 제목 *</label>',
  '<div class="form-group" data-dev-flag="dev-only" data-dev-note="NoticeRequest: device_pc · device_mobile(하나 이상) → device_scope all · pc · mobile">\n'
  '            <label class="form-label">노출 기기 *</label>\n'
  '            <div style="display:flex; gap:14px; align-items:center; height:36px;">\n'
  '              <label><input type="checkbox" name="device_pc" value="1" checked /> PC</label>\n'
  '              <label><input type="checkbox" name="device_mobile" value="1" checked /> 모바일</label>\n'
  '            </div>\n'
  '          </div>\n'
  '          <div class="form-group" data-dev-flag="dev-only" data-dev-note="publish_mode=scheduled일 때 published_at 필수(과거 시각 거부). 게시 기간 started_at · ended_at">\n'
  '            <label class="form-label">발행 방식 · 예약 시각</label>\n'
  '            <div style="display:flex; gap:8px;">\n'
  '              <select name="publish_mode" style="width:140px;"><option value="immediate">즉시 발행</option><option value="scheduled">예약 발행</option><option value="draft">임시 저장</option></select>\n'
  '              <input type="datetime-local" id="publishedAt" name="published_at" step="300" style="flex:1;" />\n'
  '            </div>\n'
  '          </div>\n'
  '          <div class="form-group full">\n            <label class="form-label">공지 제목 *</label>')
NAME("notice-form-title", "title", note="max:100")
R('id="notice-form-body"', 'id="notice-form-body"' + attrs(name="content", note="Purifier 저장. 첨부 attachments[] 최대 5개 · 개당 10MB(jpg · png · pdf · hwp · zip)"))
ACT("saveNoticeItem", route="admin.notices.store | admin.notices.update", method="POST | PUT", url=A + "/notices | /notices/{notice}", perm="등록 | 수정")

# ── BRD-006 FAQ ─────────────────────────────────────
NAME("faq-keyword", "keyword", note="개발은 질문만 검색")
R('<button class="btn btn-primary" onclick="openFaqPage(null)">',
  '<button class="btn btn-primary"' + attrs(route="admin.faqs.create", method="GET", url=A + "/faqs/create", perm="등록",
  note="개발 목록 일괄: admin.faqs.status.update(is_visible) · admin.faqs.category.update(category_id), ids[] 1~200") + ' onclick="openFaqPage(null)">')
R('onclick="openFaqPage(${f.id})"', attrs(route="admin.faqs.edit", method="GET", url=A + "/faqs/{faq}/edit", perm="수정").lstrip() + ' onclick="openFaqPage(${f.id})"')
R('onclick="deleteFaq(${f.id})"', attrs(route="admin.faqs.destroy", method="DELETE", url=A + "/faqs/{faq}", perm="삭제").lstrip() + ' onclick="deleteFaq(${f.id})"')
ACT("selectFaqCat", count=2, route="admin.faqs.index", method="GET", url=A + "/faqs", perm="조회", name="category_id")
NAME("faq-form-cat", "category_id", note="faq_categories.id")
R('id="faq-form-top"', 'id="faq-form-top" data-dev-flag="proto-only" data-dev-note="자주 찾는 TOP 고정 — 개발은 weight(0~999, 클수록 위) 정렬(정책 질문)"')
R('<label><input type="checkbox" id="faq-form-visible" checked /> 프론트 노출</label>',
  '<label><input type="checkbox" id="faq-form-visible" name="is_visible" value="1" checked /> 프론트 노출</label>\n'
  '              <label data-dev-flag="dev-only" data-dev-note="faqWeight — required integer 0~999">가중치 <input type="number" name="weight" min="0" max="999" value="0" style="width:70px;" /></label>')
NAME("faq-form-q", "question", note="max:100")
R('id="faq-form-a"', 'id="faq-form-a"' + attrs(name="answer"))
ACT("saveFaqItem", route="admin.faqs.store | admin.faqs.update", method="POST | PUT", url=A + "/faqs | /faqs/{faq}", perm="등록 | 수정")
ACT("openFaqCategoryModal", note="개발 FAQ 카테고리는 목록 화면 안 인라인 폼(name + 삭제)")
NAME("new-faq-cat-name", "name", note="max:50")
ACT("addFaqCategory", route="admin.faqs.categories.store", method="POST", url=A + "/faqs/categories", perm="등록", note="sort_order · is_active는 추가 때만")
R('onchange="renameFaqCategory(', 'data-dev-flag="proto-only" data-dev-note="카테고리 이름 변경 — 개발 없음" onchange="renameFaqCategory(')
R('onchange="toggleFaqCatVisible(', 'data-dev-flag="proto-only" data-dev-note="카테고리 노출 토글 — 개발 없음(추가 때 is_active만)" onchange="toggleFaqCatVisible(')
ACT("moveFaqCat", count=2, flag="proto-only", note="카테고리 순서 변경 — 개발 없음(추가 때 sort_order만)")
ACT("removeFaqCat", route="admin.faqs.categories.destroy", method="DELETE", url=A + "/faqs/categories/{faqCategory}", perm="삭제", note="하위 FAQ가 있으면 삭제 불가")

# ── BRD-003 상품 Q&A ─────────────────────────────────
NAME("pqna-keyword", "keyword")
NAME("pqna-type", "inquiry_type", note="개발 현재 값 composition · price · delivery · period · etc — 프로토타입 5종은 개발 옛 값(LEGACY_INQUIRY_TYPES)(정책 질문)")
NAME("pqna-owner", "assign_dept", value="logistics 물류팀 · ta 조교 · cs CS")
NAME("pqna-status", "status", value="pending · answered · hidden")
DEVNAME('<option value="WAITING" selected>미답변</option>', "status", value="pending")
DEVNAME('<option value="DONE">답변완료</option>', "status", value="answered")
DEVNAME('<option value="HIDDEN">숨김</option>', "status", value="hidden")
NAME("pqna-open", "is_secret")
DEVNAME('<option value="PUBLIC">공개</option>', "is_secret", value="0")
DEVNAME('<option value="SECRET">비밀글</option>', "is_secret", value="1")
R('onclick="selectPqnaKind(\'${k}\')"', attrs(route="admin.product-qnas.index", method="GET", url=A + "/product-qnas?tab=", perm="조회",
  name="tab", note="개발 탭: all · book · course · package · pending").lstrip() + ' onclick="selectPqnaKind(\'${k}\')"')
NAME("pqna-bulk-owner", "assign_user_id", note="개발 일괄 지정은 부서가 아니라 담당자(사람)")
ACT("bulkAssignPqna", route="admin.product-qnas.assignees.update", method="PUT", url=A + "/product-qnas/assignees", perm="수정", note="bulkAssignForm: ids[] · assign_user_id")
ACT("bulkHidePqna", flag="proto-only", note="상품 Q&A 선택 숨김 일괄 — 개발 없음(건별 action=hide)")
R('onclick="showToast(\'현재 조회 조건의 상품 Q&A', 'data-dev-flag="proto-only" data-dev-note="상품 Q&A 엑셀 — 개발 없음" onclick="showToast(\'현재 조회 조건의 상품 Q&A')
R('id="pqna-check-all"', 'id="pqna-check-all"' + attrs(name="ids[]"))
ACT("openPqnaModal", route="admin.product-qnas.show", method="GET", url=A + "/product-qnas/{productQna}", perm="조회", note="개발 003-S1은 별도 페이지(processForm)")
NAME("pqna-modal-owner", "assign_dept", value="logistics · ta · cs (프로토타입은 SJM_MASTER 역할 그룹)")
NAME("pqna-modal-open", "is_secret")
DEVNAME('<option value="PUBLIC">공개 (상품 상세에 노출)</option>', "is_secret", value="0")
DEVNAME('<option value="SECRET">비밀글 (작성 회원만 열람)</option>', "is_secret", value="1 (action=secret 비밀글 전환)")
NAME("pqna-modal-answer", "answer_content", note="action=answer일 때 필수 · min:10")
R('<button class="btn btn-outline" onclick="hidePqna()">숨김 처리</button>',
  '<button class="btn btn-outline"' + attrs(route="admin.product-qnas.update", method="PUT", url=A + "/product-qnas/{productQna}", perm="수정", name="action", value="hide") + ' onclick="hidePqna()">숨김 처리</button>')
ACT("savePqnaAnswer", route="admin.product-qnas.update", method="PUT", url=A + "/product-qnas/{productQna}", perm="수정", name="action", value="answer",
    note="알림 재발송은 admin.product-qnas.notifications.update")

# ── BRD-004 학습 Q&A ─────────────────────────────────
ACT("openLqnaModal", route="admin.study-qnas.show", method="GET", url=A + "/study-qnas/{studyQna}", perm="조회",
    note="개발 004-S1은 별도 페이지. 목록 필터 course_id · status(pending · answered · escalated) · date_from · date_to · mine · keyword")
R('id="lqna-role"', 'id="lqna-role" data-dev-flag="proto-only" data-dev-note="처리 역할 그룹(시연용) — 개발은 로그인 관리자 권한 · 담당 범위(instructor_id · assign_ta_id)"')
NAME("lqna-answer", "answer_content", note="action=answer일 때 필수 · min:10")
R('<button class="btn btn-primary" id="lqna-save" onclick="saveLqnaAnswer()">답변 등록</button>',
  '<button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.study-qnas.update", method="PUT", url=A + "/study-qnas/{studyQna}", perm="수정", name="action", value="escalate",
  note="강사 확인 요청. 개발 추가: is_public_qna(공개 Q&A 전환) · notify(답변 알림, 기본 켬)") + '>강사 확인 요청</button>\n'
  '      <button class="btn btn-primary" id="lqna-save"' + attrs(route="admin.study-qnas.update", method="PUT", url=A + "/study-qnas/{studyQna}", perm="수정", name="action", value="answer") + ' onclick="saveLqnaAnswer()">답변 등록</button>')

# ── BRD-009 당첨자 발표 ──────────────────────────────
R('<button class="btn btn-primary" onclick="openWinnerPage(null)">',
  '<button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.winners.status.update", method="PUT", url=A + "/winners/status", perm="수정", note="hideForm: ids[]") + '>선택 숨김</button>\n'
  '            <button class="btn btn-primary"' + attrs(route="admin.winners.create", method="GET", url=A + "/winners/create", perm="등록") + ' onclick="openWinnerPage(null)">')
R('onclick="openWinnerPage(\'${p.postId}\')"', attrs(route="admin.winners.edit", method="GET", url=A + "/winners/{winner}/edit", perm="수정").lstrip() + ' onclick="openWinnerPage(\'${p.postId}\')"')
NAME("winpost-event-code", "promotion_id", note="promotionSelect — 이벤트 1:1")
NAME("winpost-status", "publish_mode", value="immediate · scheduled")
DEVNAME('<option value="PUBLISHED">즉시 게시 (노출)</option>', "publish_mode", value="immediate")
DEVNAME('<option value="SCHEDULED">예약 게시</option>', "publish_mode", value="scheduled")
R('<option value="DRAFT">임시저장 (비노출)</option>', '<option value="DRAFT" data-dev-flag="proto-only" data-dev-note="임시저장 발표 — 개발 없음(2택)">임시저장 (비노출)</option>')
NAME("winpost-date", "published_at", note="publishedAt — scheduled일 때 필수")
NAME("winpost-title", "title", note="titleInput — max:100")
R('id="winpost-exp-event"', 'id="winpost-exp-event" data-dev-flag="proto-only" data-dev-note="노출 위치 선택 — 개발 없음"')
R('id="winpost-exp-notice"', 'id="winpost-exp-notice" data-dev-flag="proto-only" data-dev-note="공지사항 상단 동시 노출 — 개발 없음"')
R('id="winpost-send-alim"', 'id="winpost-send-alim" data-dev-flag="proto-only" data-dev-note="당첨자 개별 알림톡 — 개발 없음"')
R('id="winpost-body"', 'id="winpost-body"' + attrs(name="content"))
ACT("saveWinnerPost", route="admin.winners.store | admin.winners.update", method="POST | PUT", url=A + "/winners | /winners/{winner}", perm="등록 | 수정",
    note="명단은 winners_text(줄마다 아이디 · 경품) 또는 winners_file(xlsx 2MB) — 저장 시 회원 아이디 대조 · 마스킹 값만 저장")
R('<button type="button" class="btn btn-outline btn-sm" onclick="toggleWinnerRowForm(true)">',
  '<button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.winners.template.download", method="GET", url=A + "/winners/template/download", perm="다운로드") + '>명단 엑셀 양식</button>\n'
  '            <label class="btn btn-outline btn-sm" data-dev-flag="dev-only" data-dev-note="winners_file — xlsx · 2MB">명단 엑셀 업로드 <input type="file" name="winners_file" accept=".xlsx" style="display:none;" /></label>\n'
  '            <button type="button" class="btn btn-outline btn-sm" onclick="toggleWinnerRowForm(true)">')
R('id="winrow-type"', 'id="winrow-type" data-dev-flag="proto-only" data-dev-note="경품 지급 유형 — 개발 없음(정책 질문)"')
# v6.92: winrow-phone(원본 휴대폰 입력) 삭제(결정 반영, S-17) — 명단은 회원번호 + 마스킹 값만
DEVNAME('id="winrow-member"', "winners_text", note="줄마다 '아이디 경품' 중 아이디 — 개발은 저장 시 회원 아이디 대조 · 마스킹 값만 저장(회원번호 입력은 (규칙))")
ACT("previewWinnerMember", flag="proto-only", note="회원 원장 조회 미리 보기 — 개발은 저장 시 아이디 대조(별도 조회 라우트 없음)")
ACT("addWinnerRow", name="winners_text", note="개발은 줄마다 '아이디 경품' 텍스트로 받음")
ACT("batchGrantSelectedWinners", flag="proto-only", note="경품 일괄 지급 — 개발 없음")
ACT("grantSingleWinner", flag="proto-only", note="경품 개별 지급 — 개발 없음")
ACT("registerTrackingForWinner", flag="proto-only", note="경품 송장번호 — 개발 없음")

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("FAQ 탭", "switchTab('faq')", "#view-faq"),
    ("상품 Q&A 탭", "switchTab('pqna')", "#view-pqna"),
    ("학습 Q&A 탭", "switchTab('qna')", "#view-qna"),
    ("당첨자 탭", "switchTab('winner')", "#view-winner"),
    ("공지 등록 S1", "openNoticePage(null)", "[data-subpage='notice-form']"),
    ("FAQ 등록 S1", "switchTab('faq'); openFaqPage(null)", "[data-subpage='faq-form']"),
    # FAQ 카테고리 모달은 clean 원본에서도 열리지 않음(openFaqCategoryModal이 open 클래스만 붙이고 핫픽스 인라인 display:none을 안 지움) — 원본 문제라 VERIFY에서 뺌
    ("FAQ 수정 S1", "switchTab('faq'); openFaqPage(FAQS[0].id)", "[data-subpage='faq-form']"),
    ("상품 Q&A 답변 모달", "switchTab('pqna'); openPqnaModal(PQNA_LIST[0].id)", "#modal-pqna"),
    ("학습 Q&A 답변 모달", "switchTab('qna'); openLqnaModal(QNA_LIST[0].id)", "#modal-lqna"),
    ("당첨자 발표 S1", "switchTab('winner'); openWinnerPage(WINNER_POSTS[0].postId)", "[data-subpage='winner-post']"),
]
