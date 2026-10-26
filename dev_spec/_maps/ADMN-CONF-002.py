"""ADMN-CONF-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-002.md
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
    "code": "ADMN-CONF-002",
    "devCommit": DEV_COMMIT,
    "progress": "구현(CONF-002 목록 · 이력 · 개정 편집 · 상세). [유형 2] 직접 수정 · 개정 고지 발송 바로가기 · 에디터 도구는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.terms.index", "label": "약관·정책 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 목록 ──────────────────────────────────────────
R('onclick="showToast(\'신규 약관 코드(T06 등)',
  attrs(flag="proto-only", note="개발은 6종 고정(Term CODES T01~T06) — 종류 추가 경로 없음").lstrip() + ' onclick="showToast(\'신규 약관 코드(T06 등)')
R('<button type="button" class="btn btn-sm btn-primary" onclick="openTermDetail(\'${t.code}\', \'edit\')">',
  '<button type="button" class="btn btn-sm btn-primary"' + attrs(route="admin.terms.create", method="GET", url=A + "/terms/create?type=", perm="등록",
                                                                 note="작성중 개정본이 있으면 그 편집(admin.terms.edit)으로") + ' onclick="openTermDetail(\'${t.code}\', \'edit\')">')
R('<button type="button" class="btn btn-sm btn-outline" onclick="openTermDetail(\'${t.code}\', \'history\')">',
  '<button type="button" class="btn btn-sm btn-outline"' + attrs(route="admin.terms.history.index", method="GET", url=A + "/terms/history?type=", perm="조회") + ' onclick="openTermDetail(\'${t.code}\', \'history\')">')

# ── 상세 머리 ──────────────────────────────────────
NAME("dt-term-switcher", "type", value="T01 service · T02 privacy_consent · T03 privacy · T04 refund · T05 marketing · T06 age14")
R('<option value="T05">[T05] 마케팅 정보 수신 동의 (현행 v1.1)</option>',
  '<option value="T05">[T05] 마케팅 정보 수신 동의 (현행 v1.1)</option>\n'
  '                <option value="T06" disabled data-dev-flag="dev-only" data-dev-value="age14" data-dev-note="개발 6종 중 프로토 switcher에 없는 종류(만 14세 이상 확인)">[T06] 만 14세 이상 확인 (개발 전용)</option>')
R('<button type="button" class="btn btn-sm btn-outline" onclick="goTermsNoticeSend()">',
  '<button type="button" class="btn btn-sm btn-outline"' + attrs(flag="proto-only", note="개정 고지 발송 바로가기(CONF-004-S1) — 개발 약관 화면에 없음") + ' onclick="goTermsNoticeSend()">')
R('onclick="goTermsNoticeSend(\'${h.ver}\')"', attrs(flag="proto-only", note="이력 행 개정 고지 발송 — 개발 없음").lstrip() + ' onclick="goTermsNoticeSend(\'${h.ver}\')"')
R('id="tab-btn-edit" onclick=', 'id="tab-btn-edit"' + attrs(route="admin.terms.create | admin.terms.edit", method="GET", url=A + "/terms/create?type= | /terms/{term}/edit", perm="등록 | 수정") + ' onclick=')
R('id="tab-btn-history" onclick=', 'id="tab-btn-history"' + attrs(route="admin.terms.history.index", method="GET", url=A + "/terms/history?type=", perm="조회") + ' onclick=')
R('onclick="switchDetailTab(\'edit\')">+ 새 개정 버전 등록하기', attrs(route="admin.terms.create", method="GET", url=A + "/terms/create?type=", perm="등록").lstrip() + ' onclick="switchDetailTab(\'edit\')">+ 새 개정 버전 등록하기')

# ── 개정 편집 (#termForm, TermRequest) ─────────────────
DEVNAME('name="edit_mode" value="NEW_REV"', "(새 개정 = POST admin.terms.store)")
DEVNAME('name="edit_mode" value="DIRECT_FIX"', "(없음)", note="[유형 2] 현행/공시예정 본문 직접 수정 — 개발은 확정 버전 수정 불가(정책 D-CONF-01)")
R('name="edit_mode" value="DIRECT_FIX"', 'name="edit_mode" value="DIRECT_FIX" data-dev-flag="proto-only"')
NAME("ed-rev-type", "revision", value="minor 일반 개정 · major 전면 개정 (프로토 값 MINOR · MAJOR)")
NAME("ed-adverse", "is_unfavorable", value="0 일반(7일) · 1 불리(30일) (프로토 값 NO · YES)")
R('id="ed-ver-num"', 'id="ed-ver-num"' + attrs(note="개발 #termVersion · [data-term-version] 표시용 — 번호는 서버가 revision으로 채번"))
NAME("ed-announce-date", "notice_date")
NAME("ed-effective-date", "effective_date", note="≥ notice_date")
NAME("ed-reason", "change_reason", note="confirm이면 필수 · max 500")
NAME("ed-body", "content")
R('              <!-- 법정 사전 공고 기간 검증 배너 -->',
  '              <div style="margin-bottom:14px;" data-dev-flag="dev-only" data-dev-note="TermRequest title (required · max 255)">\n'
  '                <label style="display:block; font-size:12px; font-weight:800; margin-bottom:4px;">약관 제목 *</label>\n'
  '                <input type="text" class="f-input" name="title" style="width:100%;" value="환불 · 청약철회 규정" />\n'
  '              </div>\n'
  '              <!-- 법정 사전 공고 기간 검증 배너 -->')
ACT("insertEditorTag", count=4, flag="proto-only", note="에디터 서식 도구 — 개발 textarea(content)만")
ACT("openDiffModal", note="개발 #termCurrent · #termCompare · #termCompareToggle(같은 페이지 대조)")
R('<button type="button" class="btn btn-outline" onclick="resetEditorToCurrent()">↺ 현행 조문으로 초기화</button>',
  '<button type="button" class="btn btn-outline" data-dev-flag="proto-only" data-dev-note="현행 조문으로 초기화 — 개발 없음" onclick="resetEditorToCurrent()">↺ 현행 조문으로 초기화</button>\n'
  '                  <button type="button" class="btn btn-outline" data-dev-flag="dev-only" data-dev-note="개발 #layerTermPreview · #termPreviewFrame · #termPreviewOpen" onclick="showToast(\'사용자 화면 미리보기 레이어(#layerTermPreview)를 엽니다.\')">👁 사용자 화면 미리보기</button>')
ACT("saveTermDraft", route="admin.terms.store | admin.terms.update", method="POST | PUT", url=A + "/terms | /terms/{term}", perm="등록 | 수정", value="action=draft")
R('<button type="button" class="btn btn-outline" data-dev-route="admin.terms.store | admin.terms.update"',
  '<button type="button" class="btn btn-outline" data-dev-flag="dev-only" data-dev-route="admin.terms.destroy" data-dev-method="DELETE" data-dev-url="' + A + '/terms/{term}" data-dev-perm="삭제" data-dev-note="작성중(draft) 개정본 버리기" onclick="showToast(\'작성중 개정본을 버립니다.\')">작성중 개정본 버리기</button>\n'
  '                  <button type="button" class="btn btn-outline" data-dev-route="admin.terms.store | admin.terms.update"')
ACT("openSaveConfirmModal", note="개발은 확인 모달 없이 같은 폼 action=confirm 제출")
ACT("commitTermSave", route="admin.terms.store | admin.terms.update", method="POST | PUT", url=A + "/terms | /terms/{term}", perm="등록 | 수정", value="action=confirm")

# ── 이력 · 버전 상세 ────────────────────────────────
ACT("openVerModal", route="admin.terms.show", method="GET", url=A + "/terms/{term}", perm="조회")
ACT("loadVerToEditor", flag="proto-only", note="이 버전 본문을 편집창으로 불러오기 — 개발 없음")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
# 모달은 실제 클릭처럼 공통 핫픽스의 인라인 display:none을 먼저 푼다
U = "document.querySelectorAll('.modal-backdrop').forEach(m => m.style.removeProperty('display')); "
VERIFY = [
    ("목록", "switchView('list')", "#view-list"),
    ("상세 편집", "openTermDetail('T04', 'edit')", "#view-detail"),
    ("상세 이력", "openTermDetail('T03', 'history')", "#view-detail"),
    ("대조 모달", U + "openTermDetail('T04', 'edit'); openDiffModal()", "#modal-diff"),
    ("버전 열람 모달", U + "openTermDetail('T04', 'history'); openVerModal(0)", "#modal-view-ver"),
    ("저장 확인 모달", U + "openTermDetail('T04', 'edit'); openSaveConfirmModal()", "#modal-save-confirm"),
    ("직접 수정 모드", "openTermDetail('T04', 'edit'); document.querySelector('input[name=edit_mode][value=DIRECT_FIX]').checked = true; onChangeEditMode()", "#ed-body"),
]
