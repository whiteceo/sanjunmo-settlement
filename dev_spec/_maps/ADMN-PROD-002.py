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
NAME("fKeyword", "keyword", note="제목 또는 cdn_key 부분 일치 — 프로토는 DRM ID도 검색(v6.92), 개발 LectureRepository에 drm_content_id 검색 추가 필요")
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
# v6.92: 'VOD Key' 열 → '영상 (CDN 경로 · DRM ID)'(결정 반영 D-PROD-01)
R('<th style="width:230px;">영상 (CDN 경로 · DRM ID)</th>', '<th style="width:230px;"' + attrs(name="cdn_key", note="+ drm_content_id. 수정 권한이 없으면 뒤 4자리 **** 마스킹 · 비면 '미등록' 배지") + '>영상 (CDN 경로 · DRM ID)</th>')
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
# v6.92: VOD Key 1칸(s1VodKey · verifyVodKey · s1VodVerifiedBadge) 삭제 → 영상 출처 + CDN 경로 + DRM ID + YouTube 링크(결정 반영 D-PROD-01, 개발안과 같음)
NAME("s1Source", "source_type", note="cdn · youtube(맛보기 Y 강의만)")
DEVNAME('<option value="CDN"', "source_type", value="cdn")  # v3.2.32 작업 중 고침: '>' 뒤에 붙어 옵션 글자로 보이던 속성
DEVNAME('<option value="YOUTUBE"', "source_type", value="youtube")
NAME("s1CdnPath", "cdn_key", note="5~255 · CDN_KEY_PATTERN · 전체 유일, 도메인 · 서명 URL 금지")
NAME("s1DrmId", "drm_content_id", note="max 100 · 전체 유일. 유료(맛보기 N) 필수 — 개발은 nullable(D-PROD-01 필수 규칙 반영 필요). 값이 있으면 duration_sec을 OVP 값으로")
ACT("verifyDrmId", route="admin.lectures.vod-info.index", method="GET", url=A + "/lectures/vod-info?drm_content_id=", perm="조회", note="개발 #vodVerify → #vodVerifyResult (lectures.vod_verified_at)")
R('id="s1DrmVerifiedBadge"', 'id="s1DrmVerifiedBadge"' + attrs(name="vod_verified_at", note="개발 #vodVerifyResult"))
NAME("s1YtUrl", "source_url", note="max 500 · http/https — youtube일 때")
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

# ── v3.2.32 (2026-11-02 white 결정, S2-10): 강의 상태 업데이트 예정 → 공개 · 구매자 업데이트 알림 ──────────
# 개발에 없음 → 전부 proto-only. 이름은 (규칙): lectures.publish_status(upcoming · published) · planned_at · published_at,
# 저장 필드 notify_buyers, 대상 인원 조회 admin.lectures.notify-targets.index
V3232_NOTE = "v3.2.32 정본 변경(S2-10) — 개발 미구현"
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <style>\n'
    '  /* v3.2.32 구매자 알림 확인 모달 — PROD-003 · 005와 같은 모달 구조(.modal-window · header · body · footer) */\n'
    '  .modal-backdrop { background: rgba(15, 23, 42, 0.55); }\n'
    '  .modal-window { background: #fff; border-radius: 12px; width: 100%; max-width: 660px; max-height: 86vh; display: flex; flex-direction: column; box-shadow: 0 20px 40px rgba(15, 23, 42, 0.25); overflow: hidden; }\n'
    '  .modal-header { padding: 15px 20px; border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; }\n'
    '  .modal-title { font-size: 15px; font-weight: 800; color: var(--ink); }\n'
    '  .modal-body { padding: 18px 20px; overflow-y: auto; }\n'
    '  .modal-footer { padding: 12px 20px; border-top: 1px solid var(--line); background: #f8fafc; display: flex; justify-content: flex-end; gap: 8px; }\n'
    '  .pub-box { margin: 0 0 12px; padding: 9px 12px; border-radius: 8px; font-size: 12.5px; line-height: 1.6; font-weight: 600; }\n'
    '  .pub-box.warn { border: 1px solid var(--warn-line); background: var(--warn-soft); color: var(--warn); }\n'
    '  .pub-box.info { border: 1px solid #BFDBFE; background: #EFF6FF; color: #1E3A8A; }\n'
    '  </style>\n')))

# 목록 검색: 강의 상태
OPS.append(dict(kind="insert_before", anchor="          <tr>\n            <th>맛보기</th>", html=(
    '          <tr' + attrs(flag="proto-only", name="publish_status (규칙)", value="'' 전체 · published 공개 · upcoming 업데이트 예정 · overdue=1 예정일 지남(미공개)", note=V3232_NOTE) + '>\n'
    '            <th>강의 상태</th>\n'
    '            <td colspan="3">\n'
    '              <select id="fPubStatus" name="publish_status" style="width:220px;" onchange="applyFilter()">\n'
    '                <option value="ALL">전체</option>\n'
    '                <option value="PUBLIC">공개</option>\n'
    '                <option value="UPCOMING">업데이트 예정</option>\n'
    '                <option value="OVERDUE">예정일 지남 · 미공개</option>\n'
    '              </select>\n'
    '            </td>\n'
    '          </tr>\n')))
R('  const sample = document.getElementById("fSample").value;',
  '  const sample = document.getElementById("fSample").value;\n  const pubSt = (document.getElementById("fPubStatus") || {}).value || "ALL";')
R('    if (sample !== "ALL" && item.sampleYn !== sample) return false;',
  '    if (sample !== "ALL" && item.sampleYn !== sample) return false;\n    if (!pubMatch(item, pubSt)) return false;')
R('  document.getElementById("fKeyword").value = "";',
  '  document.getElementById("fKeyword").value = "";\n  if (document.getElementById("fPubStatus")) document.getElementById("fPubStatus").value = "ALL";')

# 목록: 예정일 경과 경고 · 알림 그룹 결과
OPS.append(dict(kind="insert_before", anchor="      <!-- 목록 그리드 -->", html=(
    '      <div id="pubOverdueAlert" class="pub-box warn" style="display:none;"' + attrs(flag="proto-only", note="예정일(planned_at) < 오늘 AND publish_status=upcoming 건수 — " + V3232_NOTE) + '></div>\n'
    '      <div id="pubNotifyResult" class="pub-box info" style="display:none;"' + attrs(flag="proto-only", route="admin.message-templates.campaigns.index", method="GET",
                                                                               url=A + "/message-templates/campaigns?target_type=group&saved_group_id={id}", perm="조회",
                                                                               note="공개 저장 때 만든 정적 저장 그룹(user_groups kind=saved_group · group_type=static)으로 단체 발송 화면 진입 — " + V3232_NOTE) + '></div>\n')))

# 목록 표: 강의 상태 열 · 업데이트 예정 강의의 빈 영상 · 재생시간 표시
R('<th class="left">강의 제목</th>',
  '<th class="left">강의 제목</th>\n              <th style="width:150px;"' + attrs(flag="proto-only", name="publish_status · planned_at (규칙)", note=V3232_NOTE) + '>강의 상태</th>')
R('        <td class="left"><strong>${item.title}</strong></td>',
  '        <td class="left"><strong>${item.title}</strong></td>\n        <td data-dev-flag="proto-only">${pubCell(item)}</td>')
R('        ? `<span class="badge b-bad">미등록</span>`',
  '        ? (item.pubStatus === "UPCOMING" ? `<span class="badge b-gray">공개 전환 때 등록</span>` : `<span class="badge b-bad">미등록</span>`)')
R('      : `<span class="badge b-bad">미입력</span>`;',
  '      : (item.pubStatus === "UPCOMING" ? `<span class="badge b-gray">공개 전환 때 입력</span>` : `<span class="badge b-bad">미입력</span>`);')

# S1: 강의 상태 · 공개 예정일
OPS.append(dict(kind="insert_before", anchor="        <!-- 영상 식별자: CDN 콘텐츠 경로 + DRM 콘텐츠 ID", html=(
    '        <!-- 강의 상태 (v3.2.32 S2-10): 업데이트 예정 → 공개 -->\n'
    '        <div class="form-row"' + attrs(flag="proto-only", note="(규칙) lectures.publish_status upcoming · published (Lecture::PUBLISH_STATUS_LABELS) — 강의 구분 type(normal · ot · sample …)과 별개 값. " + V3232_NOTE) + '>\n'
    '          <label>강의 상태 <span class="req">*</span></label>\n'
    '          <div class="chk-group">\n'
    '            <div class="chk-box-item" id="pillPubPublic"' + attrs(name="publish_status", value="published") + ' onclick="setPubStatus(\'PUBLIC\')">\n'
    '              <input type="checkbox" id="chkPubPublic" style="pointer-events:none;"> 공개 — 영상 재생 가능\n'
    '            </div>\n'
    '            <div class="chk-box-item" id="pillPubUpcoming"' + attrs(name="publish_status", value="upcoming") + ' onclick="setPubStatus(\'UPCOMING\')">\n'
    '              <input type="checkbox" id="chkPubUpcoming" style="pointer-events:none;"> 업데이트 예정 — 영상 없이 먼저 등록\n'
    '            </div>\n'
    '          </div>\n'
    '          <div id="s1PlannedRow" style="display:none; margin-top:10px;">\n'
    '            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">\n'
    '              <span style="font-size:12.5px; font-weight:700;">공개 예정일 <span class="req">*</span></span>\n'
    '              <input type="date" id="s1PlannedAt" name="planned_at"' + attrs(note="(규칙) lectures.planned_at date — upcoming이면 required") + ' style="width:180px;" oninput="updatePlannedPreview()" onchange="updatePlannedPreview()">\n'
    '              <span id="s1PlannedPreview" style="font-size:12px; font-weight:700; color:var(--warn);"></span>\n'
    '            </div>\n'
    '            <div class="help-txt">업데이트 예정이면 영상 출처 · CDN 경로 · DRM 콘텐츠 ID · 재생 시간을 비워 저장할 수 있습니다. 영상을 채워 \'공개\'로 바꿔 저장할 때 구매자에게 알림을 보낼지 묻습니다.</div>\n'
    '            <div class="help-warn">업데이트 예정 강의는 공개 전까지 재생할 수 없고, 진도율 분모와 7일 · 2강 전액환불 판정에서 빠집니다. 인강 부분환불의 전체 회차에는 들어가며, 공개 전 강의는 학습하지 않은 회차로 봅니다.</div>\n'
    '          </div>\n'
    '        </div>\n\n')))

# 구매자 알림 확인 모달 (공개 전환 저장 시)
OPS.append(dict(kind="insert_before", anchor='<div class="toast" id="toast"></div>', html=(
    '<!-- v3.2.32 구매자 업데이트 알림 확인 (업데이트 예정 → 공개 저장 시) -->\n'
    '<div class="modal-backdrop" id="layerLectureNotify"' + attrs(flag="proto-only", route="admin.lectures.notify-targets.index (규칙)", method="GET",
                                                                  url=A + "/lectures/{lecture}/notify-targets", perm="조회",
                                                                  note="대상 인원 미리 보기(JSON): 이 강의가 든 강좌의 유효 수강권 보유자(user_courses.status active · paused + 사전판매 시작 전), 단과 · 패키지 경유 회원 중복 제거 — " + V3232_NOTE) + '>\n'
    '  <div class="modal-window">\n'
    '    <div class="modal-header">\n'
    '      <div class="modal-title">구매자에게 업데이트 알림을 보낼까요?</div>\n'
    '      <button type="button" class="btn btn-sm modal-close">닫기 ✕</button>\n'
    '    </div>\n'
    '    <div class="modal-body">\n'
    '      <div class="pub-box info" id="lnSummary"></div>\n'
    '      <table class="grid-table">\n'
    '        <thead><tr><th style="width:90px;">구분</th><th style="width:110px;">상품 코드</th><th>상품명</th><th style="width:130px;">유효 수강권 보유자</th></tr></thead>\n'
    '        <tbody id="lnRows"></tbody>\n'
    '      </table>\n'
    '      <div id="lnTotal" style="margin-top:10px; font-size:13px; font-weight:800;"></div>\n'
    '      <div class="help-txt">대상: 이 강의가 든 강좌의 유효 수강권 보유자(수강중 · 일시정지 · 사전판매 시작 전, 단과 · 패키지 경유 모두). 제외: 수강 만료 · 환불/취소 완료 · 탈퇴. 단과와 패키지로 같은 강좌를 가진 회원은 1건만 받습니다.</div>\n'
    '      <div class="chk-group" style="margin-top:12px;"' + attrs(name="notify_buyers (규칙)", value="1 보냄(기본) · 0 안 보냄") + '>\n'
    '        <label style="display:flex; gap:6px; align-items:center; font-size:13px; font-weight:700;"><input type="radio" name="lnSend" value="1" checked> 알림 보냄 (알림톡 · 메일, 정보성)</label>\n'
    '        <label style="display:flex; gap:6px; align-items:center; font-size:13px; font-weight:700;"><input type="radio" name="lnSend" value="0"> 보내지 않음</label>\n'
    '      </div>\n'
    '      <div class="help-txt">보냄을 고르면 대상 회원으로 발송 대상 그룹(정적)을 만들어 단체 발송(정보성) 화면으로 넘깁니다. 예약 시각 · 템플릿은 단체 발송 화면에서 정합니다. 본문에 다른 상품 홍보 · 구매 링크를 넣지 않습니다.</div>\n'
    '    </div>\n'
    '    <div class="modal-footer">\n'
    '      <button type="button" class="btn">취소</button>\n'
    '      <button type="button" class="btn btn-dark" id="lnSubmit"' + attrs(route="admin.lectures.update", method="PUT", url=A + "/lectures/{lecture}",
                                                                          perm="수정", note="publish_status=published + notify_buyers=1 → (규칙) 정적 저장 그룹 생성(user_groups · user_group_members) 후 admin.message-templates.campaigns.index?target_type=group&saved_group_id= 로 이동") + ' onclick="pubConfirmNotify()">공개로 저장</button>\n'
    '    </div>\n'
    '  </div>\n'
    '</div>\n\n')))

# JS (원본 함수는 감싸기만 한다 — onclick 이름 · 원래 검증은 그대로)
OPS.append(dict(kind="insert_before", anchor="</script><script>\n/* === [UNIVERSAL-MODAL-CLOSER-HOTFIX] === */", html=r'''
// ============================================================================
// v3.2.32 (2026-11-02 white 결정, S2-10) 강의 상태 업데이트 예정 → 공개 · 구매자 업데이트 알림 — 개발 미구현(proto-only)
// (규칙) lectures.publish_status upcoming · published, planned_at, published_at
// ============================================================================
const PUB_TODAY = "2026-11-02"; // 샘플 기준일
const PUB_SAMPLE_LINKS = [
  { type: "COURSE", code: "CRS-2602", name: "2026 산업안전기사 실기 필답형 만점 답안 작성 전략반", pos: "", status: "판매중" },
  { type: "PACKAGE", code: "PKG-2601", name: "2026 산업안전기사 필기+실기 0원 합격 환급반 (교재포함)", pos: "구성 강좌 CRS-2602 경유", status: "판매중" },
  { type: "PACKAGE", code: "PKG-2602", name: "2026 산업안전기사 필기+실기(필답+작업) 올인원 종합반", pos: "구성 강좌 CRS-2602 경유", status: "판매중" }
];
const PUB_SAMPLE_AUDIENCE = { rows: { "CRS-2602": 412, "PKG-2601": 236, "PKG-2602": 188 }, dup: 37 };
LESSONS.forEach(l => { if (!l.pubStatus) l.pubStatus = "PUBLIC"; });
LESSONS.unshift(
  {
    no: 130, cat1: "산업안전기사", cat2: "실기",
    title: "[실기 필답] 13. 2026년 개정 산업안전보건법 반영 특강",
    instructor: "안창훈", source: "CDN", cdnPath: "", drmId: "", ytUrl: "", verifiedAt: "미검증",
    durationSec: null, pdfFile: "", sampleYn: "N", useYn: true, refCourseCount: 1, mappedYn: true,
    pubStatus: "UPCOMING", plannedAt: "2026-12-15", audience: PUB_SAMPLE_AUDIENCE,
    links: PUB_SAMPLE_LINKS.map(l => Object.assign({}, l, { pos: l.type === "COURSE" ? "커리큘럼 13강 (업데이트 예정)" : l.pos }))
  },
  {
    no: 129, cat1: "산업안전기사", cat2: "실기",
    title: "[실기 필답] 12. 2026년 3회 필답형 기출 해설",
    instructor: "안창훈", source: "CDN", cdnPath: "", drmId: "", ytUrl: "", verifiedAt: "미검증",
    durationSec: null, pdfFile: "", sampleYn: "N", useYn: true, refCourseCount: 1, mappedYn: true,
    pubStatus: "UPCOMING", plannedAt: "2026-10-30", audience: PUB_SAMPLE_AUDIENCE,
    links: PUB_SAMPLE_LINKS.map(l => Object.assign({}, l, { pos: l.type === "COURSE" ? "커리큘럼 12강 (업데이트 예정)" : l.pos }))
  }
);

let currentPubStatus = "PUBLIC";
let pubPending = null;

function pubOverdue(item) {
  return item.pubStatus === "UPCOMING" && !!item.plannedAt && item.plannedAt < PUB_TODAY;
}
function pubMatch(item, st) {
  if (!st || st === "ALL") return true;
  if (st === "PUBLIC") return item.pubStatus !== "UPCOMING";
  if (st === "UPCOMING") return item.pubStatus === "UPCOMING";
  if (st === "OVERDUE") return pubOverdue(item);
  return true;
}
function pubDateText(d) {
  const p = (d || "").split("-");
  return p.length === 3 ? `${p[0]}년 ${Number(p[1])}월 ${Number(p[2])}일` : "";
}
function pubCell(item) {
  if (item.pubStatus !== "UPCOMING") return `<span class="badge b-ok">공개</span>`;
  if (pubOverdue(item)) return `<span class="badge b-bad">예정일 지남 · 미공개</span><div style="font-size:11px; color:var(--bad); margin-top:3px;">예정 ${item.plannedAt}</div>`;
  return `<span class="badge b-warn">업데이트 예정</span><div style="font-size:11px; color:var(--sub); margin-top:3px;">${item.plannedAt}</div>`;
}
function pubRenderAlerts() {
  const over = LESSONS.filter(pubOverdue);
  const el = document.getElementById("pubOverdueAlert");
  if (!el) return;
  el.style.display = over.length ? "block" : "none";
  el.innerHTML = over.length
    ? `공개 예정일이 지났는데 아직 공개하지 않은 강의 ${over.length}건 — ${over.map(l => `${l.title} (예정 ${l.plannedAt})`).join(" · ")}. 영상 · DRM 콘텐츠 ID를 채워 공개하거나 예정일을 고쳐 주세요.`
    : "";
}

function setPubStatus(st) {
  const item = editingNo ? LESSONS.find(x => x.no === editingNo) : null;
  if (st === "UPCOMING" && item && item.pubStatus !== "UPCOMING") {
    alert("이미 공개된 강의는 업데이트 예정으로 되돌릴 수 없습니다.\n수강생의 재생 · 진도 기록이 끊기기 때문입니다.");
    return;
  }
  currentPubStatus = st;
  document.getElementById("pillPubPublic").classList.toggle("selected", st === "PUBLIC");
  document.getElementById("chkPubPublic").checked = (st === "PUBLIC");
  document.getElementById("pillPubUpcoming").classList.toggle("selected", st === "UPCOMING");
  document.getElementById("chkPubUpcoming").checked = (st === "UPCOMING");
  document.getElementById("s1PlannedRow").style.display = st === "UPCOMING" ? "" : "none";
  pubToggleReq(st);
  updatePlannedPreview();
}
// 업데이트 예정이면 영상 항목의 필수(*) 표시를 '공개 때 필수'로 바꾼다 — 공개 예정일은 필수(s1PlannedRow)
function pubToggleReq(st) {
  const up = st === "UPCOMING";
  ["영상 출처", "CDN 콘텐츠 경로", "DRM 콘텐츠 ID", "재생 시간(초)"].forEach(name => {
    document.querySelectorAll("label").forEach(lb => {
      const req = lb.querySelector(".req");
      if (!req || !lb.textContent.trim().startsWith(name)) return;
      req.style.display = up ? "none" : "";
      let later = lb.querySelector(".pub-later");
      if (up && !later) {
        later = document.createElement("span");
        later.className = "pub-later";
        later.style.cssText = "font-size:11px; font-weight:700; color:var(--text-muted); margin-left:4px;";
        later.textContent = "(선택 · 공개 때 필수)";
        lb.appendChild(later);
      }
      if (later) later.style.display = up ? "" : "none";
    });
  });
}
function updatePlannedPreview() {
  const v = document.getElementById("s1PlannedAt").value;
  const el = document.getElementById("s1PlannedPreview");
  el.textContent = v
    ? `프론트 커리큘럼 표시: '${pubDateText(v)} 업데이트 예정' (재생 불가)${v < PUB_TODAY ? " · 예정일이 이미 지났습니다" : ""}`
    : "예정일을 넣으면 프론트 표시 문구를 보여 줍니다";
}

// 목록 렌더 뒤 경고 갱신
const _pubRenderListTable = renderListTable;
renderListTable = function () {
  _pubRenderListTable();
  pubRenderAlerts();
};

// 등록 · 수정 진입 시 상태 채우기
const _pubOpenFormView = openFormView;
openFormView = function (no) {
  _pubOpenFormView(no);
  const item = LESSONS.find(x => x.no === no);
  document.getElementById("s1PlannedAt").value = (item && item.plannedAt) || "";
  setPubStatus(item ? (item.pubStatus || "PUBLIC") : "PUBLIC");
};

// 저장
const _pubSaveLesson = saveLesson;
function pubFormValues() {
  const source = document.getElementById("s1Source").value;
  return {
    title: document.getElementById("s1Title").value.trim(),
    source,
    cdnPath: source === "CDN" ? document.getElementById("s1CdnPath").value.trim() : "",
    drmId: source === "CDN" ? document.getElementById("s1DrmId").value.trim() : "",
    ytUrl: source === "YOUTUBE" ? document.getElementById("s1YtUrl").value.trim() : "",
    dur: parseInt(document.getElementById("s1Duration").value, 10) || null,
    plannedAt: document.getElementById("s1PlannedAt").value
  };
}
function pubSaveUpcoming(item) {
  const v = pubFormValues();
  if (!v.title) { alert("강의 제목을 입력해 주세요."); return; }
  if (!v.plannedAt) { alert("업데이트 예정 강의는 공개 예정일이 필수입니다."); return; }
  if (v.source === "CDN" && v.cdnPath) {
    const err = cdnPathError(v.cdnPath);
    if (err) { alert(err); return; }
  }
  const fields = {
    cat1: document.getElementById("s1Cat1").value,
    cat2: document.getElementById("s1Cat2").value,
    instructor: document.getElementById("s1Inst").value,
    title: v.title, source: v.source, cdnPath: v.cdnPath, drmId: v.drmId, ytUrl: v.ytUrl,
    durationSec: v.dur, sampleYn: currentSampleYn, useYn: currentUseYn, pdfFile: currentPdfFile,
    pubStatus: "UPCOMING", plannedAt: v.plannedAt
  };
  if (item) {
    Object.assign(item, fields);
  } else {
    const nextNo = Math.max(...LESSONS.map(l => l.no)) + 1;
    LESSONS.unshift(Object.assign({ no: nextNo, verifiedAt: "미검증", refCourseCount: 0, mappedYn: false, links: [] }, fields));
  }
  backToList();
  showToast(`'${v.title}' — 업데이트 예정(공개 예정일 ${v.plannedAt})으로 저장했습니다. 영상 경로 · DRM 콘텐츠 ID는 공개로 바꿀 때 채웁니다.`);
}
function pubCheckPublishable() {
  const v = pubFormValues();
  if (!v.title) { alert("강의 제목을 입력해 주세요."); return false; }
  if (v.source === "CDN") {
    const err = cdnPathError(v.cdnPath);
    if (err) { alert(`공개하려면 영상 경로를 채워야 합니다.\n${err}`); return false; }
    if (currentSampleYn === "N" && !v.drmId) { alert("공개하려면 DRM 콘텐츠 ID를 채워 주세요(유료 강의 필수)."); return false; }
    if (!v.drmId && !v.dur) { alert("재생 시간(초)을 입력하거나 DRM 메타에서 가져와 주세요."); return false; }
  } else {
    if (currentSampleYn !== "Y") { alert("YouTube 링크는 맛보기 Y(전체 공개) 강의에만 쓸 수 있습니다."); return false; }
    if (!/^https:\/\/(www\.)?(youtube\.com|youtu\.be)\//i.test(v.ytUrl)) { alert("YouTube 링크(https://www.youtube.com/... 또는 https://youtu.be/...)를 입력해 주세요."); return false; }
  }
  return true;
}
function pubAudience(item) {
  const sold = (item.links || []).filter(l => l.status === "판매중");
  if (!sold.length) return null;
  const a = item.audience || { rows: {}, dup: 0 };
  const rows = sold.map((l, i) => Object.assign({}, l, { n: a.rows[l.code] != null ? a.rows[l.code] : 40 + i * 15 }));
  const sum = rows.reduce((s, r) => s + r.n, 0);
  return { rows, dup: a.dup || 0, total: sum - (a.dup || 0) };
}
function pubOpenModal(id) {
  const el = document.getElementById(id);
  el.style.removeProperty("display");
  el.classList.add("open");
}
function pubCloseModal(id) {
  const el = document.getElementById(id);
  el.classList.remove("open");
  el.style.setProperty("display", "none", "important");
}
function pubOpenNotifyModal(item, aud) {
  pubPending = { no: item.no, aud };
  document.getElementById("lnSummary").innerHTML =
    `<strong>${item.title}</strong> 강의를 '공개'로 바꿉니다. 이 강의가 든 판매 중 상품의 구매자에게 새 강의 추가 알림(알림톡 · 메일)을 보낼 수 있습니다.`;
  document.getElementById("lnRows").innerHTML = aud.rows.map(r => `<tr>
      <td><span class="badge ${r.type === "COURSE" ? "b-pri" : "b-gray"}">${r.type === "COURSE" ? "단과 강좌" : "패키지"}</span></td>
      <td><code>${r.code}</code></td>
      <td style="text-align:left;">${r.name}</td>
      <td>${r.n.toLocaleString("ko-KR")}명</td>
    </tr>`).join("");
  document.getElementById("lnTotal").textContent =
    `발송 대상 ${aud.total.toLocaleString("ko-KR")}명 (합계 ${(aud.total + aud.dup).toLocaleString("ko-KR")}명 − 단과 · 패키지 중복 ${aud.dup.toLocaleString("ko-KR")}명)`;
  document.querySelector('input[name="lnSend"][value="1"]').checked = true;
  pubOpenModal("layerLectureNotify");
}
function pubCommitPublish(item, notify, aud) {
  const v = pubFormValues();
  const prevDur = item.durationSec;
  // 업데이트 예정 → 공개는 재생시간 '변경'이 아니라 첫 입력이다 — 재생시간 변경 소급 확인 창(S-14) 대상이 아니다
  item.durationSec = v.dur;
  _pubSaveLesson();
  if (document.getElementById("viewForm").style.display !== "none") { item.durationSec = prevDur; return; } // 원래 검증에서 막힘
  item.pubStatus = "PUBLIC";
  item.publishedAt = PUB_TODAY;
  (item.links || []).forEach(l => { l.pos = l.pos.replace(" (업데이트 예정)", ""); });
  renderListTable(); // 공개로 바뀐 상태 · 지난 예정 경고 다시 그림
  const box = document.getElementById("pubNotifyResult");
  if (notify && aud) {
    const group = `[강의 업데이트] ${item.title} · ${PUB_TODAY}`;
    box.style.display = "block";
    box.innerHTML = `발송 대상 그룹 <strong>${group}</strong>(정적, ${aud.total.toLocaleString("ko-KR")}명)을 만들었습니다. 단체 발송(정보성)에서 템플릿 · 예약 시각을 정해 보내 주세요. <a href="ADMN-CONF-004_baseline.html">단체 발송으로 이동 →</a>`;
    showToast(`'${item.title}' 공개 저장 · 발송 대상 그룹(${aud.total.toLocaleString("ko-KR")}명)을 만들었습니다.`);
  } else {
    box.style.display = "none";
    showToast(`'${item.title}'을(를) 공개로 저장했습니다${aud ? " (구매자 알림 보내지 않음)" : " (판매 중 편성 상품이 없어 알림 대상 없음)"}.`);
  }
}
function pubConfirmNotify() {
  if (!pubPending) return;
  const item = LESSONS.find(x => x.no === pubPending.no);
  const aud = pubPending.aud;
  const send = (document.querySelector('input[name="lnSend"]:checked') || {}).value === "1";
  pubPending = null;
  pubCloseModal("layerLectureNotify");
  if (item) pubCommitPublish(item, send, aud);
}
saveLesson = function () {
  const item = editingNo ? LESSONS.find(x => x.no === editingNo) : null;
  if (currentPubStatus === "UPCOMING") { pubSaveUpcoming(item); return; }
  if (!(item && item.pubStatus === "UPCOMING")) { _pubSaveLesson(); return; }
  // 업데이트 예정 → 공개: 영상 · DRM 콘텐츠 ID를 채운 뒤에만 공개, 판매 중 편성 상품이 있으면 알림 확인
  if (!pubCheckPublishable()) return;
  const aud = pubAudience(item);
  if (!aud) { pubCommitPublish(item, false, null); return; }
  pubOpenNotifyModal(item, aud);
};
''' + "\n"))

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
