"""ADMN-SETT-007 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-007.md
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


def FLAG(id_, flag, note=None):
    """id 요소에 개발 표시(dev-only · proto-only)만 단다"""
    R(f'id="{id_}"', f'id="{id_}"' + attrs(flag=flag, note=note), 1)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-007",
    "devCommit": DEV_COMMIT,
    "progress": "구현(SETT-007 · S1 편집 · 저장 · 시뮬레이터). 분할 '계산'은 2차 — 1차 정산은 PAYEE_SPLIT 보류. 비율 프리셋 · 잔여 채움 · 감사 로그 표는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.payee-splits.index", "label": "수취인 분할 지분 설정"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

LIST = dict(route="admin.settlement.payee-splits.index", method="GET", url=A + "/settlement/payee-splits", perm="조회")
EDIT = dict(route="admin.settlement.payee-splits.edit", method="GET", url=A + "/settlement/payee-splits/{contract}", perm="수정(edit 접미사)")
CREATE = dict(route="admin.settlement.payee-splits.create", method="GET", url=A + "/settlement/payee-splits/create", perm="등록")

# ── 007 현황 목록 ────────────────────────────────────
ACT("applyListFilter", count=4, note="KPI → status 필터(개발 ?status= 버튼)", **LIST)
NAME("listFilterSelect", "status", value="ALL · SPLIT · SINGLE · SUCCESSION · BLOCKED")
NAME("listSearchInput", "keyword")
ACT("openContractPickerModal", count=6, note="개발은 계약 선택 별도 페이지(create.blade.php) — 모달 아님", **CREATE)
NAME("modalContractSearch", "keyword")
NAME("modalContractFilter", "status", note="개발 계약 선택 페이지도 목록과 같은 status(ALL · SPLIT · SINGLE · SUCCESSION · BLOCKED) — 프로토타입 AVAILABLE 값은 개발 없음")
ACT("openContractEditor", count=2, **EDIT)
ACT("pickContractFromModal", **EDIT)
R('id="tabBtn-list" onclick="switchView(', 'id="tabBtn-list"' + attrs(**LIST) + ' onclick="switchView(')
R('id="tabBtn-editor" onclick="switchView(', 'id="tabBtn-editor"' + attrs(note="개발은 편집 별도 페이지(S1)", **EDIT) + ' onclick="switchView(')
R('id="tabBtn-rules" onclick="switchView(', 'id="tabBtn-rules"'
  + attrs(note="8단계 비분할 격리 규칙 표는 개발 편집 페이지에 있음. 감사 로그 표는 프로토타입만(개발 별도 표 없음, admin_logs 추정)") + ' onclick="switchView(')

# ── S1 편집 ─────────────────────────────────────────
ACT("applyPresetRatio", count=4, flag="proto-only", note="비율 프리셋 — 개발 없음")
ACT("fillRemainingToLast", flag="proto-only", note="잔여 지분 마지막 행 채움 — 개발 없음")
ACT("openCoSignerModal",
    note="개발은 이 화면에서 공동 서명 풀을 직접 등록(POST admin.settlement.payee-splits.store: payee_id · role · entity_type · tax_case · is_author · succession_yn · succession_date) · 제외(DELETE …destroy). 정본은 계약 원장에서 고르기만 — 등록 주체 정책 질문 D-SETT, 추가하지 않음")
ACT("addSignerFromModal", note="개발은 분할 행 splits[i][payee_id] select에서 풀 수취인 선택(저장 전 화면 안)")
ACT("removePayeeRow", note="개발 [data-split-remove] — 저장 전 화면 안")
R('oninput="updateSplitRatio(', 'name="splits[${idx}][split_ratio]"' + attrs(value="0.01~100 · 소수 2자리 · 합계 100.00") + ' oninput="updateSplitRatio(')
R('onchange="getSelectedContract().splits[${idx}].startDate', 'name="splits[${idx}][start_date]" onchange="getSelectedContract().splits[${idx}].startDate')
R('onchange="updateEndBasis(', attrs(flag="proto-only", note="종료 기준(계약 종료 연동 · 지정일) — 개발은 end_date nullable만(빈 값 = 기한 없음)").lstrip() + ' onchange="updateEndBasis(')
R('onchange="getSelectedContract().splits[${idx}].endDate', 'name="splits[${idx}][end_date]" onchange="getSelectedContract().splits[${idx}].endDate')
R('oninput="getSelectedContract().splits[${idx}].note', 'name="splits[${idx}][note]" oninput="getSelectedContract().splits[${idx}].note')
R('oninput="getSelectedContract().changeReason', 'id="reason" name="reason"' + attrs(note="PayeeSplitRequest 10~255자") + ' oninput="getSelectedContract().changeReason')
R('oninput="updateSimBase(', 'id="simBase" name="base_amount"'
  + attrs(route="admin.settlement.payee-splits.show", method="GET", url=A + "/settlement/payee-splits/{contract}/simulate", perm="조회", note="개발 #simRun 버튼으로 fetch(JSON, 저장 안 함) → #simResult")
  + ' oninput="updateSimBase(')
ACT("saveCurrentSplit", route="admin.settlement.payee-splits.update", method="PUT", url=A + "/settlement/payee-splits/{contract}", perm="수정",
    note="reason + splits[i][payee_id · split_ratio · start_date · end_date · note] 구성 전체 교체. 저장해도 1차 정산은 PAYEE_SPLIT 보류")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("현황 목록", "switchView('list')", "#viewPanel-list"),
    ("편집 워크스페이스", "openContractEditor('CT-2026-0715')", "#viewPanel-editor"),
    ("규칙 · 감사 탭", "switchView('rules')", "#viewPanel-rules"),
    ("계약 선택 모달", "document.querySelector('[onclick^=openContractPickerModal]').click()", "#contractPickerModal"),
    ("공동 서명 모달", "openContractEditor('CT-2026-0715'); document.querySelector('[onclick^=openCoSignerModal]').click()", "#coSignerModal"),
]
