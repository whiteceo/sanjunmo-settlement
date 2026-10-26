"""ADMN-INST-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-INST-002.md
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


M = A + "/rights-holders/milestones"

# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-INST-002",
    "devCommit": DEV_COMMIT,
    "progress": "일부 구현(검수 큐 검색 · 3대 게이트 판정 · 승인/반려). 탭 2 일할 반환 · 일시정산, 탭 3 감사 로그, 상세 편집(소득 구분 · 귀속월 · 증빙 파일) · 임시 저장 · 승인 후 자동 재연산은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.rights-holders.milestones.index", "label": "약정금 마일스톤 검수"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 스코어카드 · 탭 ─────────────────────────────────
R('<div class="kpi-card" data-filter="GATE_BLOCKED">',
  '<div class="kpi-card" data-filter="GATE_BLOCKED"' + attrs(name="approval_status", value="hold 게이트 차단 보류(개발은 상태값으로 저장)") + '>')
R('<div class="kpi-card" data-filter="APPROVED">',
  '<div class="kpi-card" data-filter="APPROVED"' + attrs(name="approval_status", value="approved (+ transferred_at 이관 완료 카드는 개발에 따로 있음)") + '>')
R('data-tab="tabWorkspace">', 'data-tab="tabWorkspace"' + attrs(route="admin.rights-holders.milestones.index", method="GET", url=M, perm="조회") + '>')
R('data-tab="tabClawback">', 'data-tab="tabClawback"' + attrs(flag="proto-only", route="admin.rights-holders.milestones.clawbacks.index (규칙)", method="GET", url=M + "/clawbacks", perm="조회",
                                                              note="중도해지 일할 반환 · 일시정산 — 개발 미구현(exclusive_contract_clawbacks 테이블은 있음)") + '>')
R('data-tab="tabAudit">', 'data-tab="tabAudit"' + attrs(flag="proto-only", route="admin.rights-holders.milestones.logs.index (규칙)", method="GET", url=M + "/logs", perm="조회",
                                                        note="검수 감사 로그 — 개발은 공통 admin.admin-logs.index(milestone_* 하위 동작)") + '>')

# ── 탭 1 검수 큐 검색 ─────────────────────────────────
NAME("searchInput", "keyword", note="식별자 · 권리자 · 계약")
NAME("typeFilter", "term_type", value="EXC · DEV · BUYOUT · ETC (프로토 EXCLUSIVE_FEE → EXC, SUPPORT_LUMP_INST · SUPPORT_RS_ONCE → DEV, FLAT_ALLOWANCE → ETC)")
R('<option value="LUMP_SETTLE">', '<option value="LUMP_SETTLE" data-dev-flag="proto-only" data-dev-note="LUMP_SETTLE — 개발 term_type에 없음">')
R('<option value="SUPPORT_RS_ONCE">', '<option value="SUPPORT_RS_ONCE" data-dev-note="개발은 DEV 하나(일시금 · 분할형과 구분 없음)">')
R('              </select>\n            </div>\n            <div class="table-wrap">',
  '              </select>\n'
  '              <input type="month" class="input" name="target_month" value="2026-10" style="width:140px;" data-dev-flag="dev-only" data-dev-note="귀속월 — 미지정이면 당월 고정">\n'
  '              <select class="select" name="approval_status" data-dev-flag="dev-only" data-dev-note="ContractMilestone 검수 상태">\n'
  '                <option value="">전체 검수 상태</option>\n'
  '                <option value="pending">검수 대기</option>\n'
  '                <option value="approved">검수 승인</option>\n'
  '                <option value="rejected">검수 반려</option>\n'
  '                <option value="hold">게이트 차단 보류</option>\n'
  '              </select>\n'
  '            </div>\n            <div class="table-wrap">')
ACT("selectItem", route="admin.rights-holders.milestones.index", method="GET", url=M, perm="조회",
    note="개발은 행의 [검수] 버튼 [data-milestone-id] → 검수 레이어 layerMilestoneReview(milestone_id)")

# ── 상세 검수(스크립트 템플릿) ───────────────────────────
ACT("fixMissingRsTargets", route="admin.rights-holders.contracts.edit", method="GET", url=A + "/rights-holders/{rightsHolder}/contracts/{contract}/edit", perm="수정",
    note="R/S 약정 대상 누락 보완 — 개발은 계약 상세(INST-001-S2)로 이동")
ACT("recheckNts", route="admin.rights-holders.nts-verify", method="POST", url=A + "/rights-holders/{rightsHolder}/nts-verify", perm="수정(접미사 예외)",
    note="게이트 C: 계속사업자 + 조회 90일 이내")
R('<select id="editIncomeCategory"', '<select id="editIncomeCategory" data-dev-flag="proto-only" data-dev-note="소득 구분 — 개발은 이 화면에서 수정 불가(게이트 A 표시만)"')
R('<select id="editIncomeClause"', '<select id="editIncomeClause" data-dev-flag="proto-only" data-dev-note="기타소득 호 — 개발은 이 화면에서 수정 불가"')
R('<select id="editInspectMode"', '<select id="editInspectMode" name="verify_method" data-dev-value="EVIDENCE_FILE 증빙 파일 · MANUAL_NOTE 수기 소명"')
R('<select id="editTargetMonth"', '<select id="editTargetMonth" data-dev-flag="proto-only" data-dev-note="귀속월 — 개발은 스케줄 target_month 그대로(정책 질문 Q-INST002-3)"')
R('<input type="text" id="editEvidenceFile"', '<input type="text" id="editEvidenceFile" data-dev-flag="proto-only" data-dev-note="증빙 파일 — 개발 1차 미지원(정책 질문 Q-INST002-5)"')
R('<textarea id="editMemo"', '<textarea id="editMemo" name="review_note" data-dev-note="개발 20자 이상 · 2000자 이하(프로토 10자 — 정책 질문 Q-INST002-1), 개발 id msReviewNote"')
ACT("saveDraft", flag="proto-only", route="admin.rights-holders.milestones.draft.update (규칙)", method="PUT", url=M + "/{milestone}/draft", perm="수정")
ACT("approveMilestone", route="admin.rights-holders.milestones.update", method="PUT", url=M, perm="수정",
    note="milestone_id · decision=approve · verify_method · review_note — 개발 msApproveBtn. 승인 후 자동 재연산 없음(정책 질문 Q-INST002-2)")
R('          ✔ 검수 승인 및 당월 정산서(SETT-002) 이관 확정\n        </button>',
  '          ✔ 검수 승인 및 당월 정산서(SETT-002) 이관 확정\n        </button>\n'
  '        <button class="btn btn-danger" data-dev-flag="dev-only" data-dev-route="admin.rights-holders.milestones.update" data-dev-method="PUT" data-dev-url="' + M + '" data-dev-perm="수정" data-dev-note="decision=reject — 개발 msRejectBtn" '
  'onclick="rejectMilestoneItem(\'${item.id}\')" ${isApproved ? "disabled" : ""}>반려</button>')

# ── 자동 재연산 알림 ─────────────────────────────────
R('id="recalcNoticeModal"', 'id="recalcNoticeModal" data-dev-flag="proto-only" data-dev-note="승인 후 자동 재연산 알림 — 개발 없음(정책 질문 Q-INST002-2)"')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("탭 1 워크스페이스", "document.querySelector('.tab-btn[data-tab=\"tabWorkspace\"]').click()", "#tabWorkspace"),
    ("탭 2 일할 반환", "document.querySelector('.tab-btn[data-tab=\"tabClawback\"]').click()", "#tabClawback"),
    ("탭 3 감사 로그", "document.querySelector('.tab-btn[data-tab=\"tabAudit\"]').click()", "#tabAudit"),
    ("검수 상세", "document.querySelector('.tab-btn[data-tab=\"tabWorkspace\"]').click(); selectItem('MS-2026-001')", "#detailBody"),
    ("검수 방식 선택", "document.querySelector('.tab-btn[data-tab=\"tabWorkspace\"]').click(); selectItem('MS-2026-004')", "#editInspectMode"),
    ("재연산 알림 모달", "openRecalcNotice('<p>확인</p>')", "#recalcNoticeModal"),
]
