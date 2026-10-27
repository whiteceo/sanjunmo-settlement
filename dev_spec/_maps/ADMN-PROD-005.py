"""ADMN-PROD-005 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-005.md
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
    "code": "ADMN-PROD-005",
    "devCommit": DEV_COMMIT,
    "progress": "구현(목록 · 등록 · 수정 · 삭제 · 복사 · 판매중지 · 미리보기 · 엑셀). 005-S2 읽기 전용 상세 · 패키지 유형 3종 · 안분 가중치 직접 수정 · 정산 1계층 게이트는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.packages.index", "label": "패키지(올패스)관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 하위 화면 탭 ────────────────────────────────────
R('data-view="detail" onclick="switchSubview(\'detail\')"',
  'data-view="detail"' + attrs(flag="proto-only", route="admin.packages.show (규칙)", method="GET", url=A + "/packages/{package}", perm="조회",
                               note="005-S2 읽기 전용 상세 · 변경 이력 — 개발 미구현(목록 행 클릭이 수정 화면)") + ' onclick="switchSubview(\'detail\')"')

# ── 005 목록 검색 ────────────────────────────────────
NAME("filter-cat", "category_id", note="개발은 root_category_id(1Depth) · category_id(2Depth) 2칸 — searchRoot · searchChild")
R('id="filter-pkg-type"', 'id="filter-pkg-type" data-dev-flag="proto-only" data-dev-note="패키지 유형 3종 — 개발 없음(is_pass_refund 1개만)"')
NAME("filter-status", "display_status", value="selling 노출 · hidden 숨김 · stopped 판매중지 (판매대기 · 판매종료는 개발 없음 — 정책 질문 Q-PROD005-3)")
R('id="filter-display"', 'id="filter-display" data-dev-flag="proto-only" data-dev-note="프론트 노출 Y/N — 개발은 display_status 1칸에 합침"')
NAME("filter-keyword", "title", note="패키지명 · 코드, 100자 — 포함 강사명 검색은 개발 없음")
R('id="filter-date-from"', 'id="filter-date-from" data-dev-flag="proto-only" data-dev-note="등록일 기간 — 개발 없음"')
R('<input type="date" id="filter-date-to" class="form-input" value="2026-12-31">\n              </div>',
  '<input type="date" id="filter-date-to" class="form-input" value="2026-12-31" data-dev-flag="proto-only" data-dev-note="등록일 기간 — 개발 없음">\n              </div>\n'
  '              <div class="filter-field" data-dev-flag="dev-only" data-dev-note="PackageService::normalizeFilters duration_min · duration_max">\n'
  '                <label>수강일수 범위</label>\n'
  '                <div style="display:flex; align-items:center; gap:6px;">\n'
  '                  <input type="number" class="form-input" name="duration_min" min="1" placeholder="최소"> ~\n'
  '                  <input type="number" class="form-input" name="duration_max" min="1" placeholder="최대"> 일\n'
  '                </div>\n'
  '              </div>')
ACT("resetPkgFilters", note="개발은 /packages 로 이동(조건 제거)")
ACT("renderPkgList", route="admin.packages.index", method="GET", url=A + "/packages", perm="조회",
    note="정렬 sort=title · sale_price · duration_days · created_at, direction=asc · desc")
ACT("showToast", route="admin.packages.download", method="GET", url=A + "/packages/download", perm="다운로드",
    note="패키지 + 구성품 배분가, 사유 입력")
ACT("openNewPkgForm", route="admin.packages.create", method="GET", url=A + "/packages/create", perm="등록")

# ── 005 목록 행(스크립트 템플릿) ─────────────────────────
ACT("openPkgDetail", count=2, flag="proto-only", route="admin.packages.show (규칙)", method="GET", url=A + "/packages/{package}", perm="조회",
    note="개발은 패키지명 클릭 → 수정 화면(admin.packages.edit)")
ACT("openPkgEdit", route="admin.packages.edit", method="GET", url=A + "/packages/{package}/edit", perm="수정")
R('onclick="openPkgEdit(\'${p.code}\')">수정</button>',
  'onclick="openPkgEdit(\'${p.code}\')">수정</button>\n'
  '                <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.packages.copy.store" data-dev-method="POST" data-dev-url="' + A + '/packages/{package}/copy" data-dev-perm="등록" onclick="showToast(\'[개발] 패키지 복사 — POST /packages/{package}/copy\')">복사</button>\n'
  '                <button type="button" class="btn btn-danger-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.packages.destroy" data-dev-method="DELETE" data-dev-url="' + A + '/packages/{package}" data-dev-perm="삭제" data-dev-note="soft delete" onclick="showToast(\'[개발] 패키지 삭제 — DELETE /packages/{package}\')">삭제</button>')

# ── 005-S2 상세 ────────────────────────────────────
ACT("editCurrentDetailPkg", route="admin.packages.edit", method="GET", url=A + "/packages/{package}/edit", perm="수정")

# ── 005-S1 등록 · 수정 ───────────────────────────────
ACT("savePkgForm", route="admin.packages.store | admin.packages.update", method="POST | PUT", url=A + "/packages | /packages/{package}", perm="등록 | 수정",
    note="PackageRequest — 개발은 저장 전 확인 레이어 layerPackageSaveConfirm")
R('onclick="savePkgForm()">패키지 상품 저장</button>',
  'onclick="savePkgForm()">패키지 상품 저장</button>\n'
  '            <button type="button" class="btn btn-soft" data-dev-flag="dev-only" data-dev-route="admin.packages.preview.store | admin.packages.preview.update" data-dev-method="POST | PUT" data-dev-url="' + A + '/packages/preview | /packages/{package}/preview" data-dev-perm="등록 | 수정" onclick="showToast(\'[개발] 프론트 미리보기 — formaction data-preview\')">미리보기</button>')
R('id="f-pkg-code"', 'id="f-pkg-code"' + attrs(name="code", note="개발 자동 채번 PKG_00001 형식(입력 칸 아님)"))
NAME("f-pkg-cat", "category_id", note="개발은 formRoot(root_category_id) · formChild(category_id, 2Depth만)")
DEVNAME('name="f-pkg-type" value="환급반"', "is_pass_refund", value="1")
DEVNAME('name="f-pkg-type" value="일반패키지"', "is_pass_refund", value="0")
DEVNAME('name="f-pkg-type" value="연간프리패스"', "(없음)", note="연간 프리패스 — 개발 미구현")
R('name="f-pkg-type" value="연간프리패스"', 'name="f-pkg-type" value="연간프리패스" data-dev-flag="proto-only"')
NAME("f-pkg-title", "title", note="개발 max 255")
R('id="f-pkg-summary"', 'id="f-pkg-summary" data-dev-flag="proto-only" data-dev-note="한줄 서브 카피 — 개발 없음"')
R('maxlength="200" value="필기+실기 전 과정 무제한 수강 + 공식 주교재 2권 포함 · 동차 합격 시 수강료 100% 환급">\n                  </td>\n                </tr>',
  'maxlength="200" value="필기+실기 전 과정 무제한 수강 + 공식 주교재 2권 포함 · 동차 합격 시 수강료 100% 환급">\n                  </td>\n                </tr>\n'
  '                <tr data-dev-flag="dev-only" data-dev-note="PackageRequest thumbnail · delete_thumbnail · description (pkgThumbBox)">\n'
  '                  <th>대표 이미지</th>\n'
  '                  <td>\n'
  '                    <input type="file" class="form-input" name="thumbnail" accept="image/jpeg,image/png,image/webp">\n'
  '                    <span class="field-hint">jpg · png · webp, 5MB 이하, 720×405(16:9) 이상</span>\n'
  '                  </td>\n'
  '                  <th>패키지 소개</th>\n'
  '                  <td>\n'
  '                    <textarea class="form-input" name="description" rows="3" placeholder="패키지 소개 (에디터)"></textarea>\n'
  '                  </td>\n'
  '                </tr>')
# 10-27 v6.84: 원본에서 [자동 안분] 버튼 삭제(D-PROD-04 정본 처리 — 정가 비율 자동, 개발과 같아짐)
ACT("openCoursePickerModal", route="admin.api.courses", method="GET", url=A + "/api/courses", perm="로그인만(메뉴 권한 밖)")
ACT("openBookPickerModal", route="admin.api.books", method="GET", url=A + "/api/books", perm="로그인만(메뉴 권한 밖)",
    note="교재 정보는 admin.packages.books.index GET /packages/books")
ACT("confirmAddCoursesToPkg", note="items[n][product_type]=course · items[n][product_id]=courses.id · items[n][sort_order]")
ACT("confirmAddBooksToPkg", note="items[n][product_type]=book · items[n][product_id]=books.id")
ACT("removeCourseFromPkg", note="강좌 1개 이상 필수(개발 PackageRequest도 같음)")
ACT("removeBookFromPkg", note="items[n] 제거")
R('id="f-course-discount"', 'id="f-course-discount"' + attrs(note="강좌 할인액 입력 — 개발은 입력 없음(sale_price − 구성품 정가 합계 = 총할인, 정책 질문 Q-PROD005-2)"))
NAME("f-pkg-total-price", "sale_price", note="개발 판매 기획가 1칸 직접 입력(정수 ≥ 0, 구성품 정가 합계 이하) — 프로토는 계산 결과 표시")
NAME("f-pkg-days", "duration_days", note="정수 ≥ 1, 기본 180 — 구성 강좌 기간을 덮어씀")
R('id="f-pkg-extend-allow"', 'id="f-pkg-extend-allow" data-dev-flag="proto-only" data-dev-note="불합격 시 1회 무상 연장 — 개발 없음"')
R('id="f-pkg-settlement-sim"', 'id="f-pkg-settlement-sim" data-dev-flag="proto-only" data-dev-note="정산 1계층 지분 100% 판매중 게이트 — 개발 저장 검증에 없음(정책 질문 Q-PROD005-4)"')
DEVNAME('name="f-pkg-status" id="radio-pkg-sale" value="판매중"', "display_status", value="selling")
DEVNAME('name="f-pkg-status" id="radio-pkg-ready" value="판매대기"', "display_status", value="hidden", note="판매대기 — 개발은 hidden(비전시)으로만 대응(정책 질문 Q-PROD005-3)")
DEVNAME('name="f-pkg-status" value="판매중지"', "display_status", value="stopped",
        note="판매중지 — POST /packages/{package}/stop-selling (admin.packages.stop.update, 수정)")
DEVNAME('name="f-pkg-status" value="판매종료"', "(없음)", note="판매종료 — 개발 없음")
R('name="f-pkg-status" value="판매종료"', 'name="f-pkg-status" value="판매종료" data-dev-flag="proto-only"')
DEVNAME('name="f-pkg-display" value="Y"', "display_status", value="selling", note="노출 Y/N — 개발은 display_status 1칸")
DEVNAME('name="f-pkg-display" value="N"', "display_status", value="hidden")
NAME("f-refund-progress", "refund_min_progress", note="환급 대상이면 필수 1~100, 기본 site_settings refund_claim_min_progress. 판매 후 변경은 기존 수강생에 소급 안 함(v6.92 S-14)")
# v6.92: 판매 후 환급 조건 변경 소급 안 함 안내 · 변경 전후 표시(S-14 결정 반영)
R('<div id="f-refund-retro-note"', '<div id="f-refund-retro-note"' + attrs(flag="proto-only", note="(규칙) order_items.refund_terms_snapshot JSON — 결제 시점 판정 대상 lecture_ids · 재생시간 · refund_min_progress · 필수 출석일수. 개발은 packages.refund_min_progress 현재 값 1개 · 스냅샷 없음"))
R('id="f-refund-attendance"', 'id="f-refund-attendance" data-dev-flag="proto-only" data-dev-note="필수 출석일수 — 개발 없음(정책 질문 Q-PROD005-7)"')
R('id="f-refund-deadline"', 'id="f-refund-deadline" data-dev-flag="proto-only" data-dev-note="환급 신청 기한 — 개발 없음"')
R('id="f-refund-burden-opt"', 'id="f-refund-burden-opt" data-dev-flag="proto-only" data-dev-note="환급 분담 옵션 — 개발은 권리자 계약 단위 refund_promo_burden_type(정책 질문 Q-PROD005-5)"')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchSubview('list')", "#subview-list"),
    ("상세 view", "openPkgDetail('PKG-2601')", "#subview-detail"),
    ("수정 view", "openPkgEdit('PKG-2601')", "#subview-form"),
    ("등록 view", "openNewPkgForm()", "#subview-form"),
    ("환급 설정 영역", "openPkgEdit('PKG-2601')", "#f-refund-progress"),
    ("정산 게이트 배너", "openNewPkgForm()", "#f-pkg-settlement-banner"),
    # 모달은 버튼 클릭으로 연다(공통 핫픽스가 클릭 때만 인라인 display:none을 푼다)
    ("강좌 선택 모달", "openNewPkgForm(); document.querySelector('[onclick^=\"openCoursePickerModal\"]').click()", "#modal-course-picker"),
    ("교재 선택 모달", "openNewPkgForm(); document.querySelector('[onclick^=\"openBookPickerModal\"]').click()", "#modal-book-picker"),
]
