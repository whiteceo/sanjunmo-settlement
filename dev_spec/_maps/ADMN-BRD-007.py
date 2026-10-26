"""ADMN-BRD-007 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BRD-007.md
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
    "code": "ADMN-BRD-007",
    "devCommit": DEV_COMMIT,
    "progress": "구현(BRD-007 · 007-S1, 724a7a0). 분류 변경 이력 표 · 담당 부서 복수 선택 · KPI 자동 배정 화면 수는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.inquiry-categories.index", "label": "1:1 문의 분류 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 레이어 · 구획 id → 개발 id ──────────────────────────
RENAME_ID("modal-major", "majorPanelSection", 4)
RENAME_ID("cat-form-title", "subFormTitle", 2)
R('<section class="subview-panel" data-subpage="form">', '<section class="subview-panel" data-subpage="form" id="subFormSection">')

# ── 007 목록 ─────────────────────────────────────────
NAME("flt-major", "parent_id", note="값 = inquiry_categories.id (프로토타입은 대분류 접두 코드)")
NAME("flt-status", "is_active", value="'' 전체 · 1 사용 · 0 미사용 (프로토타입 ALL · ON · OFF)")
R('<span id="cat-summary" style="font-weight:700; color:var(--text-sub);"></span>',
  '<select class="f-select" name="per_page" data-dev-flag="dev-only" data-dev-note="개발 changePerPage() — 20 · 50 · 100"><option value="20">20개씩</option><option value="50">50개씩</option><option value="100">100개씩</option></select>\n'
  '            <span id="cat-summary" style="font-weight:700; color:var(--text-sub);"></span>')
ACT("openMajorModal", note="개발은 같은 페이지 구획 majorPanelSection")
ACT("openCatPage", route="admin.inquiry-categories.store", method="POST", url=A + "/inquiry-categories", perm="등록",
    note="개발은 등록 · 수정 폼을 여는 GET 라우트 없음(같은 페이지 subForm)")
R('onclick="event.stopPropagation(); openCatPage(',
  attrs(route="admin.inquiry-categories.update", method="PUT", url=A + "/inquiry-categories/{inquiryCategory}", perm="수정").lstrip()
  + ' onclick="event.stopPropagation(); openCatPage(')
ACT("bulkSetStatus", count=2, route="admin.inquiry-categories.status.update", method="PUT", url=A + "/inquiry-categories/status", perm="수정",
    note="bulkForm: ids[] · is_active(bulkActive) 1 · 0 — 프로토타입 ON · OFF")
R('id="cat-check-all"', 'id="cat-check-all"' + attrs(note="개발 toggleAll()"))
R('class="cat-check" value="${c.code}"', 'class="cat-check" name="ids[]" value="${c.code}"' + attrs(value="inquiry_categories.id (프로토타입은 분류 코드)"))
R('<div class="card-title">🕘 분류 변경 이력</div>',
  '<div class="card-title" data-dev-flag="proto-only" data-dev-note="개발은 admin_logs에만 남기고 화면 표시 없음">🕘 분류 변경 이력</div>')
R('<div class="k-num" id="kpi-screens">', '<div class="k-num" id="kpi-screens" data-dev-flag="proto-only" data-dev-note="개발 counts는 majors · subs · inactive만">')

# ── 007-S1 소분류 등록 · 수정 (subForm) ─────────────────
NAME("cf-major", "parent_id", note="subParent — 값 = 대분류 id. 수정 때는 서버가 무시(잠금)")
NAME("cf-name", "name", note="subName — max:40, 같은 대분류 안 중복 불가")
R('id="cf-code"', 'id="cf-code"' + attrs(note="subCode — 전송 안 함. 서버가 VOC-{대분류code}-NN 자동 채번"))
NAME("cf-screen", "target_screen", note="subTarget — 개발 허용 4종: ADMN-BRD-002 · ADMN-BRD-002-S1 · ADMN-RFD-002-S1 · ADMN-USER-003 (프로토타입 목록 10종)")
R('id="cf-depts"', 'id="cf-depts"' + attrs(name="assign_role", note="subRole — 개발은 단일 선택(admin_roles.code, super 제외). 복수 선택은 프로토타입만(정책 질문)"))
DEVNAME('name="cf-status" value="ON"', "is_active", value="1")
DEVNAME('name="cf-status" value="OFF"', "is_active", value="0")
NAME("cf-order", "sort_order", note="subSort — nullable integer min:0")
ACT("saveCat", route="admin.inquiry-categories.store | admin.inquiry-categories.update", method="POST | PUT",
    url=A + "/inquiry-categories | /inquiry-categories/{inquiryCategory}", perm="등록 | 수정")
R('<div class="modal-backdrop" id="modal-route-confirm">',
  '<div class="modal-backdrop" id="modal-route-confirm"' + attrs(note="개발은 beforeSubmit의 confirm() 대화상자") + '>')

# ── 대분류 관리 (majorForm) ────────────────────────────
NAME("new-major-name", "name", note="majorName — max:50")
NAME("new-major-prefix", "code", note="majorCode — ^[A-Z0-9]+$ · max:20 · 중복 불가, 등록 후 잠금(프로토타입 영문 대문자 2~5자)")
R('<button type="button" class="btn btn-outline" onclick="addMajor()">대분류 추가</button>',
  '<input class="f-input" type="number" min="0" name="sort_order" style="width:80px;" placeholder="순서" data-dev-flag="dev-only" data-dev-note="majorSort — nullable integer min:0" />\n'
  '          <button type="button" class="btn btn-outline"' + attrs(route="admin.inquiry-categories.majors.store", method="POST", url=A + "/inquiry-categories/majors", perm="등록") + ' onclick="addMajor()">대분류 추가</button>')
R('onchange="setMajorStatus(',
  attrs(route="admin.inquiry-categories.majors.update", method="PUT", url=A + "/inquiry-categories/majors/{inquiryCategory}", perm="수정",
        name="is_active", note="개발 대분류 수정은 이름 · 순서 · 상태를 함께 저장(majorActive1/0). 하위 소분류가 있으면 미사용 불가").lstrip()
  + ' onchange="setMajorStatus(')
R('<thead><tr><th style="width:90px;">코드 접두</th>',
  '<thead><tr><th style="width:90px;"' + attrs(name="code", note="개발 대분류 표: 약어 · 대분류명 · 순서 · 상태 · 관리(수정)") + '>코드 접두</th>')

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("분류 등록 S1", "openCatPage(null)", "#subFormSection|[data-subpage='form']"),
    ("분류 수정 S1", "openCatPage(document.querySelector('.cat-check').value)", "#subFormSection|[data-subpage='form']"),
    ("대분류 관리", "openMajorModal()", "#majorPanelSection|#modal-major"),
    ("목록 복귀", "openCatPage(null); SJM_PAGE.back()", "[data-subpage='list']"),
    ("상태 필터 미사용", "document.getElementById('flt-status').value='OFF'; renderCats()", "#cat-tbody"),
]
