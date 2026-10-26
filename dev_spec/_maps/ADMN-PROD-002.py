"""ADMN-PROD-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-002.md
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
    "code": "ADMN-PROD-002",
    "devCommit": DEV_COMMIT,
    "progress": "구현(002 목록 · 002-S1 등록/수정). 정산 매핑 표시 · 연결 강좌/패키지 표는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.lectures.index", "label": "강의 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 하위 화면 전환 ───────────────────────────────────
R('id="btn-view-list" onclick=', 'id="btn-view-list"' + attrs(route="admin.lectures.index", method="GET", url=A + "/lectures", perm="조회") + ' onclick=')
R('id="btn-view-form" onclick=', 'id="btn-view-form"' + attrs(route="admin.lectures.create", method="GET", url=A + "/lectures/create", perm="등록") + ' onclick=')

# ── 002 목록 검색 ────────────────────────────────────
NAME("fCat1", "root_category_id", note="개발 #searchRoot (categories.id 1Depth). 질의 없이 들어오면 최근 작업 카테고리(세션 admin.lectures.recent_category)로 채움")
NAME("fCat2", "category_id", note="개발 #searchChild (2Depth, root로 좁힘)")
NAME("fInst", "instructor_id")
NAME("fSample", "is_preview", value="'' 전체 · 1 Y · 0 N (프로토 ALL · Y · N)")
NAME("fKeyword", "keyword", note="제목 또는 cdn_key 부분 일치")
R('          <tr>\n            <th>맛보기</th>',
  '          <tr data-dev-flag="dev-only" data-dev-note="개발 검색 year · type (Lecture::TYPE_LABELS)">\n'
  '            <th>연도</th>\n'
  '            <td><select name="year" style="width:140px;"><option value="">전체</option><option value="2026">2026</option><option value="2025">2025</option></select></td>\n'
  '            <th>강의 구분</th>\n'
  '            <td><select name="type" style="width:200px;"><option value="">전체</option><option value="normal">일반 강의</option><option value="ot">OT</option><option value="sample">샘플 강의</option>'
  '<option value="product_intro">상품 소개 영상</option><option value="instructor_intro">강사 소개 영상</option><option value="free">무료 공개</option></select></td>\n'
  '          </tr>\n'
  '          <tr>\n            <th>맛보기</th>')
ACT("applyFilter", route="admin.lectures.index", method="GET", url=A + "/lectures", perm="조회")
ACT("resetFilter", route="admin.lectures.index", method="GET", url=A + "/lectures?reset=1", perm="조회")

# ── 002 툴바 · 목록 ──────────────────────────────────
R('<div class="count-info" id="listCountText">', '<div class="count-info" id="listCountText"' + attrs(note="전체 N건 · 맛보기 N건(previewCount)") + '>')
R("<button class=\"btn\" onclick=\"showToast('강의(영상 Unit) 목록 엑셀 파일이 다운로드되었습니다.')\">엑셀 다운로드</button>",
  '<button class="btn"' + attrs(route="admin.lectures.download", method="GET", url=A + "/lectures/download", perm="다운로드",
                               note="사유 레이어 layerReason(공통) — reason · reason_etc · reason_ref")
  + " onclick=\"showToast('강의(영상 Unit) 목록 엑셀 파일이 다운로드되었습니다.')\">엑셀 다운로드</button>\n"
  '          <button class="btn" data-dev-flag="dev-only"' + attrs(route="admin.lectures.selected.download", method="POST", url=A + "/lectures/download-selected", perm="다운로드",
                                                                note="체크한 행 ids[] + 사유") + '>선택 다운로드</button>')
ACT("openFormView", count=2, route="admin.lectures.create | admin.lectures.edit", method="GET", url=A + "/lectures/create | /lectures/{lecture}/edit",
    perm="등록 | 수정")
R('<th style="width:70px;">번호</th>',
  '<th style="width:36px;" data-dev-flag="dev-only"><input type="checkbox" id="checkAll" /></th>\n              <th style="width:70px;">번호</th>')
R('        <td>${item.no}</td>',
  '        <td data-dev-flag="dev-only"><input type="checkbox" class="check-item" name="ids[]" value="${item.no}" /></td>\n        <td>${item.no}</td>')
R('<th style="width:190px;">VOD Key</th>', '<th style="width:190px;"' + attrs(name="cdn_key", note="수정 권한이 없으면 뒤 4자리 **** 마스킹 · 비면 '미등록' 배지") + '>VOD Key</th>')
R('<th style="width:145px;">재생시간</th>', '<th style="width:145px;"' + attrs(name="duration_sec", note="개발 표시 '2,940초 (49:00)', 0이면 '미입력'") + '>재생시간</th>')
R('<th style="width:75px;">맛보기</th>', '<th style="width:75px;"' + attrs(name="is_preview") + '>맛보기</th>')
R('<th style="width:180px;">정산 매핑 (SETT-001)</th>', '<th style="width:180px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 정산 매핑 컬럼 없음">정산 매핑 (SETT-001)</th>')
R('        <td>${mapCell}</td>', '        <td data-dev-flag="proto-only">${mapCell}</td>')
R('<tbody id="lessonTableBody">', '<tbody id="lessonTableBody"' + attrs(note="개발 행 .lec-row--link data-href → 행 클릭도 수정 폼 · 정렬 id desc 고정") + '>')

# ── 002-S1 등록 · 수정 ─────────────────────────────────
R('<span class="badge b-pri" id="s1MappingBadge">', '<span class="badge b-pri" id="s1MappingBadge" data-dev-flag="proto-only" data-dev-note="정산 매핑 배지 — 개발 없음(Q-PROD002-3)">')
R('<select id="s1Cat1">', '<select id="s1Cat1"' + attrs(name="(전송 안 함)", note="개발 #formRoot") + '>')
NAME("s1Cat2", "category_id", note="개발 #formChild — 2Depth만")
NAME("s1Inst", "instructor_id", note="개발 #instructorSelect — 프로필 등록 + 계약 유효 강사만")
NAME("s1Title", "title", note="required · max 255 (화면 maxlength 80)")
NAME("s1VodKey", "cdn_key",
     note="개발은 CDN 경로(예 2026/LEC_00001.mp4, 5~255 · 전체 유일) + 별도 drm_content_id(#drmContentId) 2칸 — 정본은 VOD Key 1칸(Q-PROD002-2, 정책 확인 전이라 칸 추가 안 함)")
ACT("verifyVodKey", route="admin.lectures.vod-info.index", method="GET", url=A + "/lectures/vod-info?drm_content_id=", perm="조회", note="개발 #vodVerify → #vodVerifyResult (lectures.vod_verified_at)")
R('id="s1VodVerifiedBadge"', 'id="s1VodVerifiedBadge"' + attrs(name="vod_verified_at", note="개발 #vodVerifyResult"))
NAME("s1Duration", "duration_sec", note="drm_content_id 없을 때 required · min 1 — 있으면 OVP 값으로 채우고 입력 잠금(#durationAutoHelp)")
R('id="s1DurationFormatted"', 'id="s1DurationFormatted"' + attrs(note="개발 #durationClock"))
ACT("fetchFromVodMeta", route="admin.lectures.vod-info.index", method="GET", url=A + "/lectures/vod-info?drm_content_id=", perm="조회", note="개발 #vodMeta")
R('<div class="help-warn">진도율 산정의 분모',
  '<div class="help-txt" data-dev-flag="dev-only"' + attrs(route="admin.lectures.duration-impact.index", method="GET", url=A + "/lectures/duration-impact?lecture_id=&duration_sec=", perm="조회",
                                                           note="저장 전 재생시간 변경 영향 조회(JSON) — 정본 05 PROD-002-S1 진도율 재계산 경고와 일치")
  + '>저장 전에 재생시간 변경 영향(영향 수강생 수 · 인정 진도율 미달 전환 예상)을 조회해 확인 창으로 보여 준다.</div>\n'
  '          <div class="help-warn">진도율 산정의 분모')
DEVNAME("onclick=\"setSampleYn('Y')\"", "is_preview", value="1")
DEVNAME("onclick=\"setSampleYn('N')\"", "is_preview", value="0")
R('id="s1PdfBox"', 'id="s1PdfBox"' + attrs(name="attachments[]", note="개발 #existingAttachments · #newFileList · #fileSelector — pdf 1개 · RealFileType 검사"))
ACT("attachSamplePdf", note="개발 #fileSelector → attachments[]")
ACT("removePdf", note="기존 첨부 삭제 → delete_attachments[]")
R('<div class="help-txt">PDF 50MB 이하 1개', '<div class="help-txt"' + attrs(note="개발 max 20480KB(20MB) — 정본 50MB와 다름(Q-PROD002-1)") + '>PDF 50MB 이하 1개')
DEVNAME('onclick="setUseYn(true)"', "is_active", value="1")
DEVNAME('onclick="setUseYn(false)"', "is_active", value="0", note="미사용 강의는 신규 편성 후보에서 제외(CourseRequest)")
R('id="s1RefCourseCount"', 'id="s1RefCourseCount"' + attrs(note="개발은 편성 강좌 수(courseCount, course_lectures)만 — 패키지 수 없음"))
R('        <!-- 사용 여부 -->',
  '        <!-- 개발에만: 강의 구분 · 연도 -->\n'
  '        <div class="form-row" data-dev-flag="dev-only" data-dev-note="개발 LectureRequest type(required) · year(2020~2040) · 강의 코드 LEC_00001 서버 채번. source_type · source_url(YouTube)은 Q-PROD002-2 확인 전이라 추가 안 함">\n'
  '          <label>강의 구분 · 연도 <span class="req">*</span></label>\n'
  '          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">\n'
  '            <select name="type"><option value="normal">일반 강의</option><option value="ot">OT</option><option value="sample">샘플 강의</option><option value="product_intro">상품 소개 영상</option>'
  '<option value="instructor_intro">강사 소개 영상</option><option value="free">무료 공개</option></select>\n'
  '            <select name="year"><option value="">연도 선택</option><option value="2026">2026</option><option value="2025">2025</option></select>\n'
  '          </div>\n'
  '        </div>\n\n'
  '        <!-- 사용 여부 -->')
R('<table class="grid-table" id="s1LinkTable">', '<table class="grid-table" id="s1LinkTable" data-dev-flag="proto-only"'
  + attrs(route="admin.lectures.products.index (규칙)", method="GET", url=A + "/lectures/{lecture}/products", perm="조회", note="연결 강좌 · 패키지 표 — 개발 미구현") + '>')
R("<button type=\"button\" class=\"btn btn-sm btn-pri\" onclick=\"window.location.href='ADMN-SETT-001_baseline.html'\">",
  "<button type=\"button\" class=\"btn btn-sm btn-pri\" data-dev-flag=\"proto-only\" data-dev-note=\"SETT-001 이동 — 개발 폼에 링크 없음 · 미매핑 판매 차단도 개발 없음(Q-PROD002-3)\" onclick=\"window.location.href='ADMN-SETT-001_baseline.html'\">")
ACT("backToList", route="admin.lectures.index", method="GET", url=A + "/lectures?list[*]", perm="조회")
ACT("deleteLesson", route="admin.lectures.destroy", method="DELETE", url=A + "/lectures/{lecture}", perm="삭제",
    note="개발 #lectureDelete · #lectureDeleteForm — 편성 강좌 수만 검사(패키지 수는 프로토만)")
ACT("saveLesson", route="admin.lectures.store | admin.lectures.update", method="POST | PUT", url=A + "/lectures | /lectures/{lecture}", perm="등록 | 수정",
    note="개발 #lectureForm (LectureRequest)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "backToList()", "#viewList"),
    ("목록 행", "renderListTable()", "#lessonTableBody tr"),
    ("등록 view", "openFormView(null)", "#viewForm"),
    ("수정 view", "openFormView(128)", "#s1Title"),
    ("연결 표", "openFormView(128)", "#s1LinkTable"),
    ("맛보기 Y", "openFormView(128); setSampleYn('Y')", "#pillSampleY"),
    ("필터", "backToList(); document.getElementById('fSample').value='Y'; applyFilter()", "#lessonTableBody"),
]
