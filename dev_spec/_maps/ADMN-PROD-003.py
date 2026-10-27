"""ADMN-PROD-003 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-003.md
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



def PROTO(id_, note, name=None):
    """프로토타입에만 있는 입력 — proto-only 표시"""
    R(f'id="{id_}"', f'id="{id_}"' + (f' name="{name}"' if name else "") + attrs(flag="proto-only", note=note), 1)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-PROD-003",
    "devCommit": DEV_COMMIT,
    "progress": "구현(목록 · 등록/수정 · 커리큘럼 구성). 프로토 003-S2 '상세 조회'는 개발 미구현. 개발 코드는 등록/수정 = 003-S2, 커리큘럼 = 003-S1(별도 페이지)",
    "menus": [
        {"route": "admin.courses.index", "label": "단과 강좌 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 하위 화면 전환 ───────────────────────────────────
R('data-view="list" onclick=', 'data-view="list"' + attrs(route="admin.courses.index", method="GET", url=A + "/courses", perm="조회") + ' onclick=')
R('data-view="detail" onclick=', 'data-view="detail" data-dev-flag="proto-only"' + attrs(route="admin.courses.show (규칙)", method="GET", url=A + "/courses/{course}", perm="조회",
                                                                                      note="강좌 상세 조회 — 개발 미구현(개발은 목록 행 클릭이 바로 수정 폼)") + ' onclick=')
R('data-view="form" onclick=', 'data-view="form"' + attrs(route="admin.courses.create | admin.courses.edit", method="GET", url=A + "/courses/create | /courses/{course}/edit", perm="등록 | 수정",
                                                          note="개발 화면 코드 PROD-003-S2 (커리큘럼 구성은 PROD-003-S1 별도 페이지)") + ' onclick=')

# ── 003 목록 검색 ────────────────────────────────────
NAME("filter-cat1", "root_category_id", note="개발 #searchRoot")
NAME("filter-cat2", "category_id", note="개발 #searchChild")
NAME("filter-instructor", "instructor_id", note="대표 강사")
NAME("filter-sale-status", "display_status", value="selling 전시 · 판매중 · hidden 비전시 · stopped 판매중지 — 판매대기 · 판매종료 없음(Q-PROD003-1)")
PROTO("filter-display", "프론트 노출 Y/N — 개발은 display_status 1칸(Q-PROD003-1)")
PROTO("filter-date-from", "등록일 기간 검색 — 개발 없음")
PROTO("filter-date-to", "등록일 기간 검색 — 개발 없음")
NAME("filter-keyword", "keyword", note="강좌명 또는 강좌 코드 — 강사명 검색은 개발 없음")
R('              <div class="filter-field filter-span-2">',
  '              <div class="filter-field" data-dev-flag="dev-only" data-dev-note="개발 book_mapped 필터">\n'
  '                <label>교재 매핑</label>\n'
  '                <select name="book_mapped" class="form-select"><option value="">전체</option><option value="1">매핑됨</option><option value="0">미매핑</option></select>\n'
  '              </div>\n'
  '              <div class="filter-field filter-span-2">')
ACT("resetCourseFilters", route="admin.courses.index", method="GET", url=A + "/courses", perm="조회")
ACT("renderCourseList", route="admin.courses.index", method="GET", url=A + "/courses", perm="조회",
    note="정렬 sort = title · duration_days · sale_price · created_at, direction asc · desc (표 머리)")

# ── 003 목록 ───────────────────────────────────────
R('<span class="card-subtitle">총 <strong id="course-total-count"', '<span class="card-subtitle"' + attrs(note="개발 툴바: 전체 N건 · 전시중 N건(sellingCount)") + '>총 <strong id="course-total-count"')
ACT("exportCourseCsv", route="admin.courses.download", method="GET", url=A + "/courses/download", perm="다운로드", note="사유 레이어 layerReason(공통)")
ACT("openNewCourseForm", route="admin.courses.create", method="GET", url=A + "/courses/create", perm="등록")
R('<th style="width:110px;">강좌코드</th>', '<th style="width:110px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 강좌코드 컬럼 없음(코드 CRS_00001)">강좌코드</th>')
R('<th style="width:105px;">담당 강사</th>', '<th style="width:105px;"' + attrs(name="instructor_id", note="대표 강사 + '강사 계약 종료' 배지(자동 판매중지 없음)") + '>담당 강사</th>')
R('<th class="text-center" style="width:110px;">수강기간</th>', '<th class="text-center" style="width:110px;"' + attrs(name="sort=duration_days") + '>수강기간</th>')
R('<th class="text-right" style="width:95px;">정가</th>\n                    <th class="text-right" style="width:115px;">',
  '<th class="text-right" style="width:95px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 정가 컬럼 없음">정가</th>\n                    <th class="text-right" style="width:115px;">')
R('<th class="text-right" style="width:115px;">판매가 (할인율)</th>', '<th class="text-right" style="width:115px;"' + attrs(name="sort=sale_price") + '>판매가 (할인율)</th>')
R('<th class="text-center" style="width:85px;">총 강의수</th>', '<th class="text-center" style="width:85px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 총 강의수 없음">총 강의수</th>')
R('<th class="text-center" style="width:125px;">정산 매핑 (1계층)</th>', '<th class="text-center" style="width:125px;" data-dev-flag="proto-only" data-dev-note="정산 매핑 컬럼 — 개발 없음(Q-PROD003-3). 개발에는 대신 \'교재 매핑\' 매핑/미매핑 컬럼">정산 매핑 (1계층)</th>')
R('<th class="text-center" style="width:90px;">판매상태</th>', '<th class="text-center" style="width:90px;"' + attrs(name="display_status", note="판매상태 + 노출여부 2컬럼 → 개발 '전시' 1컬럼") + '>판매상태</th>')
R('<th class="text-center" style="width:75px;">노출여부</th>', '<th class="text-center" style="width:75px;" data-dev-flag="proto-only" data-dev-note="노출여부 분리 — 개발 없음(Q-PROD003-1)">노출여부</th>')
R('<th class="text-center" style="width:100px;">등록일</th>', '<th class="text-center" style="width:100px;"' + attrs(name="sort=created_at") + '>등록일</th>')
ACT("openCourseDetail", count=2, flag="proto-only", route="admin.courses.show (규칙)", method="GET", url=A + "/courses/{course}", perm="조회",
    note="개발은 행 클릭(.crs-row--link data-href) → 수정 폼")
ACT("openCourseEdit", route="admin.courses.edit", method="GET", url=A + "/courses/{course}/edit", perm="수정")

# ── 프로토 003-S2 상세 조회(개발 미구현) ─────────────────────
R('<section id="subview-detail" class="subview-panel">', '<section id="subview-detail" class="subview-panel" data-dev-flag="proto-only" data-dev-note="강좌 상세 조회 화면 — 개발 미구현(admin.courses.show 규칙)">')
R('<a class="btn btn-soft" href="ADMN-SETT-001_baseline.html">정산 지분 매핑 (ADMN-SETT-001)</a>',
  '<a class="btn btn-soft" href="ADMN-SETT-001_baseline.html" data-dev-flag="proto-only" data-dev-note="SETT-001 이동 — 개발 강좌 화면에 없음">정산 지분 매핑 (ADMN-SETT-001)</a>')
ACT("editCurrentDetailCourse", route="admin.courses.edit", method="GET", url=A + "/courses/{course}/edit", perm="수정")
R('<div class="card" id="bk-log-card">', '<div class="card" id="bk-log-card" data-dev-flag="proto-only"'
  + attrs(route="admin.courses.status-logs.index (규칙)", method="GET", url=A + "/courses/{course}/status-logs", perm="조회",
          note="판매 상태 변경 이력 — 개발 미구현(admin_logs subAction stop_selling에만 남음). 주교재 연동 자동 판매중지도 개발 없음(Q-PROD004-1)") + '>')

# ── 등록 · 수정 (개발 PROD-003-S2) ────────────────────────
R('<button type="button" class="btn btn-outline" onclick="switchSubview(\'list\')">취소</button>',
  '<a class="btn btn-outline" href="#" data-dev-flag="dev-only"' + attrs(route="front.course.show", note="프론트 미리보기(form.blade.php:595)") + '>프론트 미리보기</a>\n'
  '            <button type="button" class="btn btn-outline" data-dev-flag="dev-only" id="courseStop"' + attrs(route="admin.courses.stop.update", method="POST", url=A + "/courses/{course}/stop-selling", perm="수정",
                                                                                                         note="개발 #courseStopForm — 판매중지 전용 버튼(프로토는 판매 상태 라디오)") + '>판매중지</button>\n'
  '            <button type="button" class="btn btn-outline" data-dev-flag="dev-only" id="courseDelete"' + attrs(route="admin.courses.destroy", method="DELETE", url=A + "/courses/{course}", perm="삭제",
                                                                                                           note="개발 #courseDeleteForm — user_courses · order_items · package_items · cart_items 등 참조 7종 있으면 거부(비전시 · 판매중지 안내)") + '>삭제</button>\n'
  '            <button type="button" class="btn btn-outline" onclick="switchSubview(\'list\')">취소</button>')
ACT("saveCourseForm", route="admin.courses.store | admin.courses.update", method="POST | PUT", url=A + "/courses | /courses/{course}", perm="등록 | 수정",
    note="개발 #courseForm (CourseRequest)")
R('id="f-code"', 'id="f-code"' + attrs(note="개발 서버 채번 CRS_00001 (프로토 CRS-YYNN)"))
R('id="f-created-at"', 'id="f-created-at"' + attrs(name="created_at"))
R('<select id="f-cat1"', '<select id="f-cat1"' + attrs(name="(전송 안 함)", note="개발 #formRoot"))
NAME("f-cat2", "category_id", note="개발 #formChild — 2Depth만 · category_products 대표 1건")
NAME("f-instructor", "instructors[0][instructor_id]", value="instructors[0][role]=m (대표)", note="개발 #mainInstructor — 계약 유효 강사만(기존 값은 통과)")
NAME("f-title", "title", note="required · max 255")
PROTO("f-summary", "한줄 요약 — 개발 없음")
PROTO("f-tags", "검색 태그 — 개발 없음")
R('                <tr>\n                  <th>강좌 한줄 요약</th>\n                  <td colspan="3">',
  '                <tr data-dev-flag="dev-only" data-dev-note="개발 #instructorTable · #instructorRows — instructors[n][instructor_id] · instructors[n][role] (s 부강사 · a 참여), distinct">\n'
  '                  <th>참여 강사</th>\n'
  '                  <td colspan="3">\n'
  '                    <div style="display:flex; gap:8px; align-items:center;">\n'
  '                      <select name="instructors[1][instructor_id]" class="form-select" style="width:260px;"><option value="">강사 선택</option><option value="정종대">정종대 (RH-0025)</option><option value="이건설">이건설 (RH-0046)</option></select>\n'
  '                      <select name="instructors[1][role]" class="form-select" style="width:130px;"><option value="s">부강사</option><option value="a">참여</option></select>\n'
  '                      <button type="button" class="btn btn-outline btn-sm">+ 강사 추가</button>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n                  <th>강좌 한줄 요약</th>\n                  <td colspan="3">')

NAME("f-list-price", "original_price", note="required · 정수 ≥ 0")
PROTO("f-discount-type", "할인 설정 — 개발 없음(판매가 직접 입력, 할인율은 #discountRateDisplay 표시만)")
PROTO("f-discount-val", "할인 값 — 개발 없음")
NAME("f-sale-price-display", "sale_price", note="개발은 직접 입력(required · ≤ 정가) #salePrice")
R('<span class="badge badge-info">면세 상품 (VAT 0%', '<span class="badge badge-info"' + attrs(name="tax_type", value="exempt (서버 고정)") + '>면세 상품 (VAT 0%')
R('                <tr>\n                  <th>수강기간 설정 <span class="req-star">*</span></th>',
  '                <tr data-dev-flag="dev-only" data-dev-note="개발 CourseRequest cost_price(원가) · allow_coupon · allow_point(기본 1)">\n'
  '                  <th>원가</th>\n'
  '                  <td>\n'
  '                    <div class="input-with-unit" style="width:200px;">\n'
  '                      <input type="number" name="cost_price" class="form-input text-right" value="" min="0" step="1000">\n'
  '                      <span class="input-unit">원</span>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                  <th>프로모션 허용</th>\n'
  '                  <td>\n'
  '                    <div class="inline-options">\n'
  '                      <label class="option-label"><input type="checkbox" name="allow_coupon" value="1" checked=""><span>쿠폰 사용</span></label>\n'
  '                      <label class="option-label"><input type="checkbox" name="allow_point" value="1" checked=""><span>포인트 사용</span></label>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n                  <th>수강기간 설정 <span class="req-star">*</span></th>')
DEVNAME('name="f-period-type" value="DAYS"', "duration_days", note="개발은 N일 + start_type(immediate · scheduled + start_date) — 지정일 시작은 Q-PROD003-2 확인 전이라 추가 안 함")
R('name="f-period-type" value="FIXED_DATE"', 'name="f-period-type" value="FIXED_DATE" data-dev-flag="proto-only" data-dev-note="수강 만료일 고정 — 개발 없음(Q-PROD003-2)"')
NAME("f-period-days", "duration_days", note="개발 #durationDays — required · min 1")
PROTO("f-period-enddate", "만료일 고정 — 개발 없음(Q-PROD003-2)")
PROTO("f-pause-allow", "일시정지 허용 정책 — 개발 없음(Q-PROD003-4, 일시정지는 USER-003 건별)")
PROTO("f-pause-count", "Q-PROD003-4")
PROTO("f-pause-days", "Q-PROD003-4")
PROTO("f-settlement-sim", "정산 1계층 매핑 검증(하드락) — 개발 없음(Q-PROD003-3)")
DEVNAME('name="f-sale-status" id="radio-sale-on" value="판매중"', "display_status", value="selling")
R('name="f-sale-status" id="radio-sale-ready" value="판매대기"', 'name="f-sale-status" id="radio-sale-ready" value="판매대기" data-dev-flag="proto-only" data-dev-name="display_status" data-dev-note="판매대기 — 개발 없음(가장 가까운 값 hidden, Q-PROD003-1)"')
DEVNAME('name="f-sale-status" value="판매중지"', "display_status", value="stopped", note="개발은 [판매중지] 버튼(admin.courses.stop.update)으로도 전환")
R('name="f-sale-status" value="판매종료"', 'name="f-sale-status" value="판매종료" data-dev-flag="proto-only" data-dev-name="display_status" data-dev-note="판매종료 — 개발 없음(Q-PROD003-1)"')
R('name="f-display-yn" value="Y"', 'name="f-display-yn" value="Y" data-dev-name="display_status" data-dev-note="노출 분리 — 개발은 display_status 1칸(Y ≈ selling · stopped, N ≈ hidden), Q-PROD003-1"')
R('name="f-display-yn" value="N"', 'name="f-display-yn" value="N" data-dev-name="display_status" data-dev-value="hidden"')

# ── 커리큘럼(개발 PROD-003-S1 별도 페이지) ───────────────────
# v6.92: 판매 후 편성 변경 소급 안 함 안내(S-14 결정 반영) — 추가 차시는 기존 수강생 판정 분모에서 뺌, 결제 시점 조건을 주문 라인에 박제
R('<div id="form-retro-note"', '<div id="form-retro-note"' + attrs(note="기존 수강생 소급 안 함(S-14) — 개발 '진도율 분모 증가' 영향 미리 보기(#crsImpact · #curImpact)와 반대 방향. (규칙) order_items.refund_terms_snapshot JSON — 결제 시점 판정 대상 lecture_ids · 재생시간 · refund_min_progress · 필수 출석일수"))
R('id="form-curriculum-summary"', 'id="form-curriculum-summary"' + attrs(note="개발 #clCount · #clSeconds · #clLabel (폼 안 요약) / 커리큘럼 페이지 #curCount · #curSeconds · #curLabel"))
ACT("addCurriculumSection", flag="proto-only", note="섹션(대단원) 구분 — 개발 없음(course_lectures 1단 순서만)")
R('            <div id="form-sections-wrapper"></div>',
  '            <div class="field-hint" data-dev-flag="dev-only"' + attrs(route="admin.courses.curriculum.index", method="GET", url=A + "/courses/{course}/curriculum", perm="조회",
                                                                    note="개발 커리큘럼 구성 페이지(#curriculumForm) · 변경 영향 미리 보기 #crsImpact · #curImpact")
  + '>판매 이력이 있는 강좌는 기존 강의를 제외할 수 없고 추가만 가능하다. 저장 전에 기존 수강생 진도율 분모 변화(영향 인원)를 미리 보여 준다.</div>\n'
  '            <div id="form-sections-wrapper" data-dev-name="lectures[]" data-dev-note="순서 = 배열 순서 · 편성 가능(VOD Key + 재생시간) 강의만"></div>')
ACT("openLectureModal", route="admin.api.lectures", method="GET", url=A + "/api/lectures", perm="상품 메뉴 4종 중 조회 1개",
    note="개발은 커리큘럼 페이지 후보 표(category_id · instructor_id · keyword · all=1)")
ACT("removeSection", flag="proto-only", note="섹션 — 개발 없음")
ACT("moveLecture", count=2, note="개발은 드래그 순서(#curRenumber)")
R('onchange="togglePreview(', 'data-dev-flag="proto-only" data-dev-note="섹션별 맛보기 토글 — 개발 없음(맛보기는 강의 is_preview)" onchange="togglePreview(')
ACT("removeLectureFromSection", note="판매 이력 강좌는 기존 강의 제외 불가(CourseService.php:714-724)")

# ── 교재 매핑 ─────────────────────────────────────
ACT("openTextbookModal", route="admin.api.books", method="GET", url=A + "/api/books", perm="상품 메뉴 4종 중 조회 1개", note="개발 #bookTable · #bookRows")
R('onchange="mappedTextbooks[${idx}].role = this.value"', 'data-dev-name="books[n][book_type]" data-dev-value="main 주교재 · sub 부교재" onchange="mappedTextbooks[${idx}].role = this.value"')
ACT("removeMappedTextbook", note="books[n] 행 제거")

# ── 썸네일 · 소개 ───────────────────────────────────
NAME("f-thumb", "thumbnail", note="jpg/png/webp · 5MB · 720×405(16:9) 이상 · 삭제는 delete_thumbnail (#courseThumbSelector)")
R("onclick=\"showToast('썸네일 파일 선택 창이", attrs(note="개발 #courseThumbSelector").lstrip() + " onclick=\"showToast('썸네일 파일 선택 창이")
NAME("f-desc", "description", note="개발은 description · target_audience · content 3칸(에디터)")
R('''90% 이상 재생 시 출석/진도 인정</textarea>
                  </td>
                </tr>''',
  '''90% 이상 재생 시 출석/진도 인정</textarea>
                  </td>
                </tr>
                <tr data-dev-flag="dev-only" data-dev-note="개발 target_audience · content (에디터)">
                  <th>수강 대상 · 내용 및 특징</th>
                  <td>
                    <textarea name="target_audience" class="form-textarea" rows="2" placeholder="수강 대상"></textarea>
                    <textarea name="content" class="form-textarea" rows="3" placeholder="내용 및 특징" style="margin-top:6px;"></textarea>
                  </td>
                </tr>
                <tr data-dev-flag="dev-only" data-dev-note="개발 intro_lecture_id · sample_lecture_id(살아 있는 강의) · badge_slot_1_code · badge_slot_2_code(강조 배지)">
                  <th>소개 · 샘플 영상 · 강조 배지</th>
                  <td>
                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                      <input type="text" name="intro_lecture_id" class="form-input" style="width:220px;" placeholder="소개 영상 (강의 선택)" readonly="">
                      <input type="text" name="sample_lecture_id" class="form-input" style="width:220px;" placeholder="샘플 강의 (강의 선택)" readonly="">
                      <input type="text" name="badge_slot_1_code" class="form-input" style="width:160px;" placeholder="강조 배지 1">
                      <input type="text" name="badge_slot_2_code" class="form-input" style="width:160px;" placeholder="강조 배지 2">
                    </div>
                  </td>
                </tr>''')

# ── 모달 ──────────────────────────────────────────
R('<div class="modal-backdrop" id="modal-lecture-picker">', '<div class="modal-backdrop" id="modal-lecture-picker"'
  + attrs(note="개발은 모달 없이 커리큘럼 페이지(PROD-003-S1) 후보 표 #candCheckAll · #candAdd") + '>')
NAME("modal-lec-keyword", "keyword")
ACT("renderLectureModalRows", route="admin.courses.curriculum.index", method="GET", url=A + "/courses/{course}/curriculum?keyword=", perm="조회")
R('<input type="checkbox" class="lec-pick-chk"', '<input type="checkbox" class="lec-pick-chk" data-dev-name="lectures[]"')
ACT("confirmAddLecturesToSection", route="admin.courses.curriculum.update", method="PUT", url=A + "/courses/{course}/curriculum", perm="수정",
    note="개발 #candAdd → #curSave (CourseCurriculumRequest lectures[])")
R('<div class="modal-backdrop" id="modal-textbook-picker">', '<div class="modal-backdrop" id="modal-textbook-picker"'
  + attrs(note="개발 form.blade.php:975 교재 선택(admin.api.books)") + '>')
R('<select class="form-select book-role-sel" data-sku="${b.sku}" style=', '<select class="form-select book-role-sel" data-sku="${b.sku}" data-dev-name="books[n][book_type]" data-dev-value="main · sub" style=')
ACT("confirmAddTextbooks", note="books[n][book_id] · books[n][book_type] 행 추가(저장은 강좌 저장과 함께)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchSubview('list')", "#subview-list"),
    ("목록 행", "switchSubview('list'); renderCourseList()", "#course-list-tbody tr"),
    ("상세 view", "openCourseDetail('CRS-2601')", "#subview-detail"),
    ("수정 view", "openCourseEdit('CRS-2601')", "#subview-form"),
    ("신규 view", "openNewCourseForm()", "#f-title"),
    # 강의 · 교재 모달(openLectureModal · openTextbookModal)은 clean 원본에서도 열리지 않아(open 클래스만 붙이고 인라인 display:none 유지) 검증에서 뺐다 — 원본 문제로 보고
    ("교재 표", "openCourseEdit('CRS-2601'); renderFormTextbooks()", "#form-textbooks-tbody tr"),
    ("상세 교재 · 이력", "openCourseDetail('CRS-2601')", "#detail-textbook-tbody"),
    ("섹션 추가", "openCourseEdit('CRS-2601'); addCurriculumSection()", "#form-sections-wrapper"),
]
