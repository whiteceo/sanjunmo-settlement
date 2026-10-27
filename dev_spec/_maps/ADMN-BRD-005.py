"""ADMN-BRD-005 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BRD-005.md
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
    "code": "ADMN-BRD-005",
    "devCommit": DEV_COMMIT,
    "progress": "구현(BRD-005 · 005-S1 · BRD-010 · 010-S1). 수강후기/합격수기 분리 탭 · 진도율 · 별점 · 후기 보상 회수 · 버전 이력은 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.reviews.index", "label": "수기 / 합격 후기 관리"},
        {"route": "admin.free-contents.index", "label": "무료콘텐츠 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# 합격수기 검수 모달(modal-pass-audit)은 id 유지 — 개발 005-S1은 별도 페이지(admin.reviews.show)의 modForm, 레이어 id 없음

# ── 탭 → 개발 메뉴 ──────────────────────────────────
R('onclick="switchTab(\'courseReview\')"', attrs(route="admin.reviews.index", method="GET", url=A + "/reviews", perm="조회",
  note="개발은 수기 · 합격 후기를 한 목록(reviews)에서 처리 — 수강후기 탭 분리는 프로토타입 구성").lstrip() + ' onclick="switchTab(\'courseReview\')"')
R('onclick="switchTab(\'passEssay\')"', attrs(route="admin.reviews.index", method="GET", url=A + "/reviews", perm="조회",
  note="개발 필터 verify_status · exam_target_id · exam_round · instructor_id · cafe · display · is_best · point · refund · keyword").lstrip() + ' onclick="switchTab(\'passEssay\')"')
R('onclick="switchTab(\'freeLecture\')"', attrs(route="admin.free-contents.index", method="GET", url=A + "/free-contents", perm="조회",
  note="개발 BRD-010 무료콘텐츠 관리(별도 메뉴)").lstrip() + ' onclick="switchTab(\'freeLecture\')"')

# ── 005 수강후기 ────────────────────────────────────
NAME("cr-best-filter", "is_best", value="1 = 베스트만 (일반 필터는 개발 없음)")
DEVNAME('<option value="BEST">', "is_best", value="1")
NAME("cr-keyword", "keyword", note="개발 keyword = 제목 검색")
ACT("toggleBestCourseReview", route="admin.reviews.best.update", method="PUT", url=A + "/reviews/best", perm="수정",
    note="bulkForm: ids[] · best(bulkBest) 1 · 0 — 베스트 동시 최대 12")
ACT("toggleCourseReviewVisible", route="admin.reviews.display.update", method="PUT", url=A + "/reviews/display", perm="수정",
    note="bulkForm: ids[] · show(bulkShow) 1 · 0 → reviews.display_site")

# ── 005 합격수기 · 005-S1 검증 ─────────────────────────
NAME("pe-status-filter", "verify_status", value="pending · verified · rejected · hidden(개발에만)")
DEVNAME('<option value="PENDING">', "verify_status", value="pending")
DEVNAME('<option value="APPROVED">', "verify_status", value="verified")
DEVNAME('<option value="REJECTED">', "verify_status", value="rejected")
NAME("pe-keyword", "keyword", note="개발 keyword = 제목 검색. 종목 · 회차는 exam_target_id · exam_round 필터")
ACT("openPassAuditModal", count=2, route="admin.reviews.show", method="GET", url=A + "/reviews/{review}", perm="조회",
    note="개발 005-S1은 별도 페이지(modForm)")
R('onclick="decidePassEssay(\'REJECTED\')"', attrs(route="admin.reviews.update", method="PUT", url=A + "/reviews/{review}", perm="수정",
  name="verify_status", value="rejected", note="reject_reason 10~255자 필수(회원 마이페이지 · 알림에 노출)").lstrip() + ' onclick="decidePassEssay(\'REJECTED\')"')
R('onclick="decidePassEssay(\'APPROVED\')"', attrs(route="admin.reviews.update", method="PUT", url=A + "/reviews/{review}", perm="수정",
  name="verify_status", value="verified", note="검증만(지급 없음) — 지급은 따로 admin.members.review-points.store(v6.92 D-BRD-02로 개발과 같아짐)").lstrip() + ' onclick="decidePassEssay(\'APPROVED\')"')
# v6.92: pe-reward-note 아래 dev-only 반려 사유 · 우수 후기 포인트 폼 삭제(결정 반영, D-BRD-02 · S-21) — 원본에 반려 사유 · 후기 보상 지급 모달이 생겨 그 요소에 개발 이름을 단다
DEVNAME('id="pe-reject-chip"', "reject_reason", note="개발 공통 사유 칩(Review::REJECT_REASONS) — 고르면 reject_reason 앞에 채움, 별도 필드 없음. '증빙 식별 불가'는 개발 칩에 없음")
NAME("pe-reject-text", "reject_reason", note="rejected일 때 required · 10~255자(rejectReason)")
ACT("openReviewRewardModal", route="admin.members.review-points.store", method="POST", url=A + "/members/review-points/{review}", perm="등록(회원관리 메뉴)",
    note="ReviewService::pointPanel ready일 때만(검증 완료 · 미지급). 후기당 1회(reviews.point_granted_at)")
NAME("rw-amount", "amount", note="required · 1~999,999,999 정수. 기본값 = 포인트 정책 후기 보상값")
NAME("rw-reason", "reason", note="개발은 항상 required 10~200자 · 공백 제외 10자 · 서로 다른 글자 3개(프로토는 금액을 바꿀 때만)")
ACT("confirmReviewReward", route="admin.members.review-points.store", method="POST", url=A + "/members/review-points/{review}", perm="등록(회원관리 메뉴)",
    note="ReviewPointRequest amount · reason")
ACT("openReviewRevokeModal", flag="proto-only", note="후기 보상 회수(S-21) — 개발 없음")
ACT("confirmReviewRevoke", flag="proto-only", note="후기 보상 회수 — 개발 없음(무상 P 잔액 한도 회수 라우트 없음)")

# ── BRD-010 무료콘텐츠 목록 ───────────────────────────
NAME("fl-type-filter", "type", value="EXAM 빈출자료 · DAILY 매일 1문제")
# 10-27 v6.84: 원본에서 FREE_LECTURE 구분 삭제(개발 구분과 같아짐)
NAME("fl-cert-filter", "cert", note="값 = categories.id (1Depth 자격증)")
R('<button class="btn btn-primary" onclick="openFreeLecturePage(null)">',
  '<button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.free-contents.download", method="GET", url=A + "/free-contents/download", perm="다운로드",
  note="개인정보 없음 — 사유 입력 없이 다운로드") + '>엑셀 다운로드</button>\n'
  '            <button class="btn btn-primary"' + attrs(route="admin.free-contents.create", method="GET", url=A + "/free-contents/create", perm="등록") + ' onclick="openFreeLecturePage(null)">')
R("onclick=\"openFreeLecturePage('${item.id}')\"",
  attrs(route="admin.free-contents.edit", method="GET", url=A + "/free-contents/{freeContent}/edit", perm="수정").lstrip() + " onclick=\"openFreeLecturePage('${item.id}')\"")

# ── BRD-010-S1 등록 · 수정 (freeContentForm) ─────────────
NAME("fl-form-type", "content_type", value="EXAM 빈출자료 · DAILY 매일 1문제", note="개발 FreeContent::TYPES와 같음(v6.92 S-22 · D-BRD-01)")
# v6.92: FREQ_EXAM 옵션 삭제(결정 반영, S-22 · D-BRD-01) — 원본 구분이 EXAM · DAILY로 개발과 같아짐
DEVNAME('<option value="EXAM">', "content_type", value="EXAM", count=2)
DEVNAME('<option value="DAILY">', "content_type", value="DAILY", count=2)
NAME("fl-form-cert", "cert_category_id", note="값 = categories.id (1Depth)")
R('id="fl-form-year" value="2026 대비" style="width:120px;" />',
  'id="fl-form-year" value="2026 대비" style="width:120px;" />\n'
  '              <input type="number" name="round_no" min="1" max="999" placeholder="회차" style="width:80px;" data-dev-flag="dev-only" data-dev-note="roundNo — EXAM이면 필수 · 1~999, DAILY는 비움" />')
NAME("fl-form-year", "year", note="정수 2000~2100 (프로토타입 '2026 대비' 문구)")
NAME("fl-form-title", "title", note="max:100")
# v6.92: fl-form-vod(VOD 에셋 · 러닝타임) 삭제(결정 반영, S-22 · D-BRD-01) — 무료특강 영상은 PROD-002 · 003에서 등록
NAME("fl-form-date", "started_at", note="개발 전시 시작일 nullable Y-m-d — 프로토 게시일(필수)")
NAME("fl-form-pdf", "attachments[]", note="PDF만 · 최대 5개 · 개당 10MB (프로토타입은 파일명 텍스트). 삭제는 delete_attachments[]")
R('id="fl-form-body"', 'id="fl-form-body"' + attrs(name="content", note="nullable(에디터)"))
R('<div style="font-weight:800; font-size:13.5px; margin-bottom:6px;">파일 · 본문 버전 이력</div>',
  '<div style="font-weight:800; font-size:13.5px; margin-bottom:6px;" data-dev-flag="proto-only" data-dev-note="버전 이력 — 개발 없음">파일 · 본문 버전 이력</div>')
ACT("saveFreeLecture", route="admin.free-contents.store | admin.free-contents.update", method="POST | PUT",
    url=A + "/free-contents | /free-contents/{freeContent}", perm="등록 | 수정",
    note="저장 전 중복 경고 GET admin.free-contents.duplicates.index(JSON). 개발 추가 필드: status(published · hidden) · started_at · related_course_id")

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("합격수기 탭", "switchTab('passEssay')", "#view-passEssay"),
    ("무료콘텐츠 탭", "switchTab('freeLecture')", "#view-freeLecture"),
    ("수강후기 탭", "switchTab('passEssay'); switchTab('courseReview')", "#view-courseReview"),
    ("합격수기 검수 모달", "switchTab('passEssay'); openPassAuditModal(PASS_ESSAYS[0].id)", "#modal-pass-audit"),
    ("무료콘텐츠 등록 S1", "switchTab('freeLecture'); openFreeLecturePage(null)", "[data-subpage='free-lecture']"),
    ("무료콘텐츠 수정 S1", "switchTab('freeLecture'); openFreeLecturePage(FREE_LECTURES[0].id)", "[data-subpage='free-lecture']"),
]
