"""ADMN-PROD-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-001.md
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
    "code": "ADMN-PROD-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(트리 · 정보 폼 · 정렬 저장 · 삭제). 검색으로 트리 거르기 · ▲▼ 이동 · 노드 메모는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.categories.index", "label": "카테고리 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 검색 ───────────────────────────────────────────
NAME("filterActive", "is_active", value="'' 전체 · 1 전시중 · 0 비전시 (프로토 ALL · ON · OFF)",
     note="개발은 검색 값을 받아 폼에만 채우고 트리에는 적용하지 않음(CategoryController.php:39)")
NAME("filterKeyword", "keyword")
ACT("applyFilter", route="admin.categories.index", method="GET", url=A + "/categories?is_active=&keyword=", perm="조회",
    note="검색으로 트리 거르기는 프로토타입만(개발 결함)")

# ── 트리 ───────────────────────────────────────────
R('id="treeContainer"', 'id="treeContainer"' + attrs(note="개발 #catTree (table.cat__tree__table, 행 data-cat-id · data-cat-parent) — 빈 1Depth는 '하위 분류를 추가하세요' 안내 행, 1Depth도 하위 합계 강좌 수 표시"))
ACT("selectCategory", route="admin.categories.index", method="GET", url=A + "/categories?id={category}", perm="조회")
R('<span class="drag-handle" title="드래그하여 순서 변경">', '<span class="drag-handle" title="드래그하여 순서 변경"' + attrs(note="개발 .cat__handle (HTML5 드래그)") + '>')
R('${c.note ? `<span style="font-size:11px;', '${c.note ? `<span data-dev-flag="proto-only" data-dev-note="노드 메모 — 개발 컬럼 없음" style="font-size:11px;')
ACT("moveOrder", count=2, flag="proto-only", note="▲▼ 순서 이동 — 개발은 드래그만(정본 05 :124 드래그 통일, 보조 UI)")
R('<button class="btn" onclick="startAddCategory(1)">',
  '<button class="btn"' + attrs(route="admin.categories.index", method="GET", url=A + "/categories?parent=0", perm="등록") + ' onclick="startAddCategory(1)">')
R('<button class="btn" onclick="startAddCategory(2)">',
  '<button class="btn" id="catAddChild"' + attrs(route="admin.categories.index", method="GET", url=A + "/categories?parent={category}", perm="등록",
                                                 note="개발은 1Depth 선택 시만 활성") + ' onclick="startAddCategory(2)">')
ACT("saveTreeOrder", route="admin.categories.sort.update", method="POST", url=A + "/categories/sort", perm="수정",
    note="items[n][id] · items[n][parent_id] · items[n][sort_order] (#catSortForm · #catSortPayload) — 다른 상위로 옮기면 전체 거절")
R('<button class="btn btn-dark" data-dev-route="admin.categories.sort.update"', '<button class="btn btn-dark" id="catSortSave" data-dev-route="admin.categories.sort.update"')
R('            <div class="tree-actions">',
  '            <div class="help-warn" id="catSortNotice" data-dev-flag="dev-only" data-dev-note="개발 catSortNotice — 순서를 바꾸면 표시, 다른 노드 클릭 시 confirm · beforeunload 경고">'
  '순서가 바뀌었습니다. [정렬 저장]을 눌러야 반영됩니다.</div>\n'
  '            <div class="tree-actions">')

# ── 카테고리 정보 폼 ─────────────────────────────────
R('id="detailContainer"', 'id="detailContainer"' + attrs(note="개발 #catForm (신규 POST /categories · 수정 PUT /categories/{category}) · .cat__panel"))
R('<div class="help-txt">1Depth 신규 등록 시에는 \'최상위\' 로 고정 · 변경 불가</div>',
  '<div class="help-txt">1Depth 신규 등록 시에는 \'최상위\' 로 고정 · 변경 불가</div>\n'
  '      ${node.depth === 2 ? `<select class="f-select" name="parent_id" style="width:100%; margin-top:6px;" data-dev-flag="dev-only" '
  'data-dev-note="개발 index.blade.php:201-209 — 2Depth는 상위(1Depth만 후보)를 바꿀 수 있음, 옮기면 새 형제 맨 뒤(정본 05 :123)">'
  '${CATEGORIES.filter(p => p.depth === 1).map(p => `<option value="${p.id}" ${p.id === node.parentId ? \'selected\' : \'\'}>${p.name}${p.active ? \'\' : \' (비전시)\'}</option>`).join("")}</select>` : \'\'}')
NAME("inpCatName", "name", note="required · max 30 · 같은 부모 아래 이름 중복 불가")
R('<span>${node.order}</span>', '<span data-dev-name="sort_order" data-dev-note="요청으로 받지 않음 — 정렬 저장으로만">${node.order}</span>')
DEVNAME('onclick="setNodeActive(true)"', "is_active", value="1")
DEVNAME('onclick="setNodeActive(false)"', "is_active", value="0")
R('<div class="help-warn">비활성 전환 시 하위 2Depth · 소속 강좌가 프론트에서 함께 숨겨진다(기결제 회원의 학습은 유지)</div>',
  '<div class="help-warn">비활성 전환 시 하위 2Depth · 소속 강좌가 프론트에서 함께 숨겨진다(기결제 회원의 학습은 유지)</div>\n'
  '      <div class="help-txt" data-dev-flag="dev-only" data-dev-note="개발 layerCatDeactivate · catDeactivateConfirm (index.blade.php:361-398) — 정본 05 :131 영향 범위 모달과 일치">'
  '활성 → 비활성으로 저장하면 영향 범위(하위 분류 N · 소속 강좌 N · 기결제 회원 수강 유지) 확인 창이 먼저 뜬다.</div>')
R('<span>${node.code}</span>', '<span data-dev-name="code" data-dev-note="개발 CAT_%04d 자동 채번(CategoryService.php:229-239) · 수정 불가">${node.code}</span>')
R("onclick=\"window.location.href='ADMN-PROD-003_baseline.html'\"",
  attrs(route="admin.courses.edit", method="GET", url=A + "/courses/{course}/edit", perm="수정(강좌 메뉴)").lstrip() + " onclick=\"window.location.href='ADMN-PROD-003_baseline.html'\"")
R('<span class="badge ${crs.display ? \'b-on\' : \'b-off\'}">', '<span class="badge ${crs.display ? \'b-on\' : \'b-off\'}" data-dev-name="courses.display_status" data-dev-value="selling → ON">')
ACT("deleteCategory", route="admin.categories.destroy", method="DELETE", url=A + "/categories/{category}", perm="삭제",
    note="개발 거부 조건 추가: Default · 강의(lectures.category_id) · 강사 담당 과목(instructor_categories) 참조 (#catDelete · #catDeleteForm)")
ACT("saveCategory", route="admin.categories.store | admin.categories.update", method="POST | PUT", url=A + "/categories | /categories/{category}",
    perm="등록 | 수정", note="CategoryRequest: parent_id · name · is_active (slug · sort_order · code는 서버)")
R('<strong>삭제 제약 —</strong>', '<strong' + attrs(note="개발은 Default 카테고리 · 강의 노출 분류 · 강사 담당 과목 참조도 삭제 거부") + '>삭제 제약 —</strong>')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("트리 렌더", "renderTree()", "#treeContainer .tree-node"),
    ("2Depth 선택", "selectCategory('CAT-102')", "#inpCatName"),
    ("1Depth 선택", "selectCategory('CAT-100')", "#detailContainer .section-title-bar"),
    ("1Depth 신규", "startAddCategory(1)", "#inpCatName"),
    ("2Depth 신규", "selectCategory('CAT-200'); startAddCategory(2)", "#inpCatName"),
    ("비활성 칩", "selectCategory('CAT-101'); setNodeActive(false)", "#detailContainer .chk-pill.active-pill"),
    ("검색 필터", "document.getElementById('filterActive').value='OFF'; applyFilter()", "#treeContainer"),
]
