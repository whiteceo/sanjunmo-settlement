"""ADMN-PROD-006 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-006.md
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
    "code": "ADMN-PROD-006",
    "devCommit": DEV_COMMIT,
    "progress": "구현(목록 · 등록 · 수정 · 삭제 · 권리자 검색 · 엑셀). 006-S2 읽기 전용 상세 · 메인 추천 · 홍보 영상 · 배너 · 인사말 · 노출 순서 일괄 저장은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.instructor-profiles.index", "label": "강사 프로필 / 전시 관리(추정)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 하위 화면 탭 ────────────────────────────────────
R('data-view="detail" onclick="switchSubview(\'detail\')"',
  'data-view="detail"' + attrs(flag="proto-only", route="admin.instructor-profiles.show (규칙)", method="GET", url=A + "/instructor-profiles/{instructorProfile}", perm="조회",
                               note="006-S2 읽기 전용 상세 — 개발 미구현(강사명 링크가 수정 화면)") + ' onclick="switchSubview(\'detail\')"')

# ── 006 목록 검색 ────────────────────────────────────
NAME("filter-cat", "category_id", note="categories 1Depth id")
NAME("filter-contract", "contract_status", value="active 계약중 · expired 종료 · terminated 정지 (기본 목록 pending+active) — 만료임박 / 갱신대기 구분은 개발 없음")
NAME("filter-display", "is_display", value="1 노출 · 0 숨김")
R('id="filter-featured"', 'id="filter-featured" data-dev-flag="proto-only" data-dev-note="메인 추천 필터 — 개발 없음"')
NAME("filter-keyword", "keyword", note="개발은 강사명만 — 권리자코드 · 슬로건 검색은 개발 없음")
NAME("filter-sort", "sort", value="name · contract_status · updated_at (+ direction asc · desc) — 노출 순서 정렬은 개발 없음")
ACT("resetInstFilters", note="개발은 /instructor-profiles 로 이동(조건 제거)")
ACT("renderInstList", route="admin.instructor-profiles.index", method="GET", url=A + "/instructor-profiles", perm="조회",
    note="기본 정렬 id desc, 20건 페이지")
R('onclick="showToast(\'변경된 강사 노출 순서가 프론트 강사관에 반영되었습니다.\')">노출 순서 일괄 저장</button>',
  'data-dev-flag="proto-only" data-dev-route="admin.instructor-profiles.sort.update (규칙)" data-dev-method="PUT" data-dev-url="' + A + '/instructor-profiles/sort" data-dev-perm="수정" '
  'onclick="showToast(\'변경된 강사 노출 순서가 프론트 강사관에 반영되었습니다.\')">노출 순서 일괄 저장</button>\n'
  '              <button type="button" class="btn btn-outline" data-dev-flag="dev-only" data-dev-route="admin.instructor-profiles.download" data-dev-method="GET" data-dev-url="' + A + '/instructor-profiles/download" data-dev-perm="다운로드" data-dev-note="사유 레이어 layerReason" '
  'onclick="showToast(\'[개발] 엑셀 다운로드 — 사유 입력 후 GET /instructor-profiles/download\')">엑셀 다운로드</button>')
ACT("openNewInstForm", route="admin.instructor-profiles.create", method="GET", url=A + "/instructor-profiles/create", perm="등록")

# ── 006 목록 행(스크립트 템플릿) ─────────────────────────
ACT("openInstDetail", count=2, flag="proto-only", route="admin.instructor-profiles.show (규칙)", method="GET", url=A + "/instructor-profiles/{instructorProfile}", perm="조회",
    note="개발은 강사명 링크 → 수정 화면(admin.instructor-profiles.edit)")
ACT("openInstEdit", route="admin.instructor-profiles.edit", method="GET", url=A + "/instructor-profiles/{instructorProfile}/edit", perm="수정")
R('onclick="openInstEdit(\'${item.profCode}\')">수정</button>',
  'onclick="openInstEdit(\'${item.profCode}\')">수정</button>\n'
  '              <button type="button" class="btn btn-danger-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.instructor-profiles.destroy" data-dev-method="DELETE" data-dev-url="' + A + '/instructor-profiles/{instructorProfile}" data-dev-perm="삭제" '
  'onclick="showToast(\'[개발] 강사 프로필 삭제 — DELETE /instructor-profiles/{instructorProfile}\')">삭제</button>')

# ── 006-S2 상세 ────────────────────────────────────
ACT("editCurrentDetailInst", route="admin.instructor-profiles.edit", method="GET", url=A + "/instructor-profiles/{instructorProfile}/edit", perm="수정")

# ── 006-S1 등록 · 수정 ───────────────────────────────
ACT("saveInstForm", route="admin.instructor-profiles.store | admin.instructor-profiles.update", method="POST | PUT",
    url=A + "/instructor-profiles | /instructor-profiles/{instructorProfile}", perm="등록 | 수정", note="InstructorProfileRequest — 1권리자 1프로필")
R('id="f-prof-code"', 'id="f-prof-code" data-dev-flag="proto-only" data-dev-note="프로필 코드 PRF-YYNN — 개발 없음(instructor_profiles.id)"')
NAME("f-ins-master", "rights_holder_id", note="개발은 검색(searchRightsHolders) 후 hidden rightsHolderId — 위탁자 · 자사 권리자 제외")
R('                <tr>\n                  <th>계약 원장 연동 상태</th>',
  '                <tr data-dev-flag="dev-only" data-dev-route="admin.instructor-profiles.instructors.index" data-dev-method="GET" data-dev-url="' + A + '/instructor-profiles/search-instructors" data-dev-perm="조회" data-dev-note="개인: 이름 + 생년월일 일치 시만 선택, 사업자: 사업자등록번호. exclude_profile_id">\n'
  '                  <th>권리자 검색</th>\n'
  '                  <td colspan="3">\n'
  '                    <div style="display:flex; align-items:center; gap:8px;">\n'
  '                      <input type="text" id="searchName" class="form-input" style="width:150px;" name="name" placeholder="이름">\n'
  '                      <input type="date" id="searchBirth" class="form-input" style="width:160px;" name="birth_date">\n'
  '                      <input type="text" id="searchBizNo" class="form-input" style="width:180px;" name="business_number" placeholder="사업자등록번호">\n'
  '                      <button type="button" class="btn btn-soft btn-sm" onclick="showToast(\'[개발] 권리자 검색 — GET /instructor-profiles/search-instructors\')">검색</button>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n                  <th>계약 원장 연동 상태</th>')
R('id="f-contract-gate-box"', 'id="f-contract-gate-box"' + attrs(note="개발 linkedInfo · linkedContract(PROFILE_DETAIL_STATUS_LABELS) + 노출 판정표 verdictTable · 계약 무효 경고 layerInstructorBlind"))
NAME("f-inst-name", "display_name", note="max 50")
NAME("f-inst-cat", "categories[]", note="개발은 1Depth 복수 선택(min 1) — 프로토는 대표 1개(정책 질문 Q-PROD006-2)")
NAME("f-inst-slogan", "intro_text", note="개발 intro_text 120자(카드 요약) 또는 title 100자 — 대응 확인 필요")
R('placeholder="강사 카드 및 상세 배너 상단에 노출할 한줄 캐치프레이즈 (최대 100자)">\n                  </td>\n                </tr>',
  'placeholder="강사 카드 및 상세 배너 상단에 노출할 한줄 캐치프레이즈 (최대 100자)">\n                  </td>\n                </tr>\n'
  '                <tr data-dev-flag="dev-only" data-dev-note="InstructorProfileRequest instructor_type · home_link_type · home_url">\n'
  '                  <th>강사 구분 <span class="req-star">*</span></th>\n'
  '                  <td>\n'
  '                    <div class="inline-options">\n'
  '                      <label class="option-label"><input type="radio" name="instructor_type" value="main" checked=""><span>정강사</span></label>\n'
  '                      <label class="option-label"><input type="radio" name="instructor_type" value="sub"><span>부강사</span></label>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                  <th>강사 홈 링크 <span class="req-star">*</span></th>\n'
  '                  <td>\n'
  '                    <div class="inline-options">\n'
  '                      <label class="option-label"><input type="radio" name="home_link_type" value="internal" checked=""><span>내부링크</span></label>\n'
  '                      <label class="option-label"><input type="radio" name="home_link_type" value="external"><span>아웃링크</span></label>\n'
  '                    </div>\n'
  '                    <input type="url" id="homeUrl" class="form-input" name="home_url" maxlength="500" placeholder="아웃링크 URL (아웃링크일 때 필수)" style="margin-top:6px;">\n'
  '                  </td>\n'
  '                </tr>')
DEVNAME('name="f-inst-display" id="radio-inst-disp-y" value="Y"', "is_display", value="1")
DEVNAME('name="f-inst-display" id="radio-inst-disp-n" value="N"', "is_display", value="0", note="등록 기본 OFF. 계약 종료 · 해지면 프론트 강제 숨김")
NAME("f-inst-order", "sort_order", note="0 이상, 카테고리와 무관한 전체 순서(정책 질문 Q-PROD006-1)")
R('id="f-inst-featured"', 'id="f-inst-featured" data-dev-flag="proto-only" data-dev-note="메인 홈 추천 강사 캐러셀 — 개발 없음"')
R('<span>메인 홈 추천 강사 캐러셀 노출</span>\n                      </label>',
  '<span>메인 홈 추천 강사 캐러셀 노출</span>\n                      </label>\n'
  '                      <label class="option-label" data-dev-flag="dev-only" data-dev-note="맛보기 자동 진열(기본 ON, 현재 건수 표시)">\n'
  '                        <input type="checkbox" name="auto_preview" value="1" checked="">\n'
  '                        <span>맛보기 자동 진열</span>\n'
  '                      </label>')
R('onclick="showToast(\'강사 목록용 프로필 이미지 업로드 창 호출 (480x600px PNG 권장)\')"',
  'data-dev-name="photo" data-dev-note="jpg · jpeg · png · webp, 2MB, 480×640 이상 3:4 (+ delete_photo)" onclick="showToast(\'강사 목록용 프로필 이미지 업로드 창 호출 (480x600px PNG 권장)\')"')
R('onclick="showToast(\'강사 상세 상단 배너 이미지 업로드 창 호출\')"',
  'data-dev-flag="proto-only" data-dev-note="상단 배너 이미지 — 개발 없음" onclick="showToast(\'강사 상세 상단 배너 이미지 업로드 창 호출\')"')
R('id="f-intro-vod"', 'id="f-intro-vod" data-dev-flag="proto-only" data-dev-note="대표 홍보 영상 — 개발 폼에 없음(instructors.intro_lecture_id 칸만 있음)"')
R('onclick="showToast(\'ADMN-PROD-002 맛보기/홍보 영상 미디어키 검증 완료 (3분 20초)\')"',
  'data-dev-flag="proto-only" data-dev-note="미디어키 확인 — 개발 미구현" onclick="showToast(\'ADMN-PROD-002 맛보기/홍보 영상 미디어키 검증 완료 (3분 20초)\')"')
R('<div id="career-builder-wrap"></div>', '<div id="career-builder-wrap"' + attrs(name="career", note="개발은 에디터 HTML 1칸(빈 문단 불가) — 프로토는 행 빌더") + '></div>')
ACT("addCareerLine", note="개발 career 에디터 1칸")
ACT("removeCareerLine", note="개발 career 에디터 1칸")
R('id="f-inst-greeting"', 'id="f-inst-greeting" data-dev-flag="proto-only" data-dev-note="인사말 · 학습 가이드 — 개발 없음"')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchSubview('list')", "#subview-list"),
    ("상세 view", "openInstDetail('PRF-2601')", "#subview-detail"),
    ("수정 view", "openInstEdit('PRF-2601')", "#subview-form"),
    ("등록 view", "openNewInstForm()", "#subview-form"),
    ("계약 게이트", "openNewInstForm()", "#f-contract-gate-box"),
    ("약력 빌더", "openInstEdit('PRF-2601')", "#career-builder-wrap"),
]
