"""ADMN-SETT-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-002.md
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


def DA(action, count=1, **kw):
    """data-action="action" 앞에 개발 라우트 속성을 단다(위임 클릭 화면용 ACT)"""
    R(f'data-action="{action}"', attrs(**kw).lstrip() + f' data-action="{action}"', count)



def ACTX(prefix, count=1, **kw):
    """onclick="prefix(인자 포함 앞부분) 앞에 개발 라우트 속성을 단다"""
    R(f'onclick="{prefix}', attrs(**kw).lstrip() + f' onclick="{prefix}', count)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-002",
    "devCommit": DEV_COMMIT,
    "progress": "일부 구현(보드 · S1 · S2 · P1 · P2 마감). 개발지원금 소진 원장 · 증빙(evidence 탭 비활성) · 은행 결과 파일 대사 · S2 발송은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.board.index", "label": "월간 정산 및 집행 (memos · close · carryovers 같은 메뉴 권한)"},
        {"route": "admin.settlement.statements.index", "label": "권리자 제공 정산서 S2 (메뉴 행 존재 미확인)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

BOARD = A + "/settlement/board"

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modal-sett-gate", "settlementCloseModal", 3)

# ── 상단 바(보드) ─────────────────────────────────────
NAME("monthSelect", "month", note="개발 기준월 탭 .tab__list .tab__item.active (?month=YYYY-MM)")
R('<button class="btn" id="btnRunEngine">',
  '<button class="btn" id="btnRunEngine"' + attrs(route="admin.settlement.board.recalculate", method="POST", url=BOARD + "/recalculate", perm="수정",
                                                  note="month만 보냄. 마감 잠금(locked_yn) 월은 비활성") + '>')
ACT("openStatementPageS1(getSelectedPayeeKey", route="admin.settlement.board.show", method="GET", url=BOARD + "/{rightsHolder}?month=", perm="조회")
ACT("openStatementPageS2(getSelectedPayeeKey", route="admin.settlement.statements.index", method="GET", url=A + "/settlement/statements?month=&rights_holder_id=", perm="조회(정산서 메뉴)")
R('<button class="btn" id="btnOpenCarryModal">',
  '<button class="btn" id="btnOpenCarryModal"' + attrs(route="admin.settlement.board.carryovers.show", method="GET", url=BOARD + "/{rightsHolder}/carryovers?month=", perm="조회",
                                                       note="개발은 권리자 단위 조각(_carryover-modal) — 보드 탭 carryover(이월 잔액)도 있음") + '>')
R('<button class="btn btn-primary" id="btnLockSettlement">',
  '<button class="btn btn-primary" id="btnLockSettlement"' + attrs(note="P2 마감 모달 열기 — 개발 #settlementCloseModal") + '>')

# ── 탭(개발 ?tab=summary|evidence|transfer|carryover) ─────────
R('data-tab="tabStatements">', 'data-tab="tabStatements"' + attrs(route="admin.settlement.board.index", method="GET", url=BOARD + "?tab=summary", perm="조회") + '>')
R('data-tab="tabSupportLedger">', 'data-tab="tabSupportLedger"' + attrs(flag="proto-only", note="개발지원금 소진 원장 — 개발 탭 없음") + '>')
R('data-tab="tabTaxInvoice">', 'data-tab="tabTaxInvoice"' + attrs(flag="proto-only", route="admin.settlement.board.index", method="GET", url=BOARD + "?tab=evidence", perm="조회",
                                                                 note="개발 evidence 탭 enabled=false(비활성)") + '>')
R('data-tab="tabFirmbanking">', 'data-tab="tabFirmbanking"' + attrs(route="admin.settlement.board.index", method="GET", url=BOARD + "?tab=transfer", perm="조회",
                                                                   note="개발은 이체 리스트 표 + 엑셀만. 개발 carryover(이월 잔액) 탭은 프로토타입 P1 원장에 대응") + '>')

# ── 1. 통합 정산서 필터 ─────────────────────────────────
NAME("searchInput", "keyword", note="rights_holders.name · code LIKE")
NAME("pipelineFilter", "pipeline", value="'' · P1_1 · P2_1 · P2_2 · P5_1 (값 그대로)")
R('<option value="P5_1">매출연동 개발지원금</option>\n              </select>\n',
  '<option value="P5_1">매출연동 개발지원금</option>\n              </select>\n'
  '              <select class="select" name="state" data-dev-flag="dev-only" data-dev-note="개발 보드 필터 state">'
  '<option value="">전체 집행 판정</option><option value="payable">지급 확정</option><option value="carried">지급 이월</option><option value="hold">마감 보류</option><option value="tax_pending">세무 판정 보류</option><option value="internal">자사 귀속</option></select>\n'
  '              <select class="select" name="hold_reason" data-dev-flag="dev-only" data-dev-note="개발 settlement_lines.payout_hold_reason">'
  '<option value="">전체 보류 사유</option><option value="TAX_PENDING">세무 판정 보류</option><option value="NTS_EXPIRED">사업자 확인 90일 경과</option><option value="PENDING_VERIFY">임시 등록 확인 대기</option>'
  '<option value="PAYEE_SPLIT">수취인 분할(2차)</option><option value="REFUND_BURDEN">환급 부담 B · C(2차)</option><option value="PG_RECON_UNCLASSIFIED">PG 대사 미분류 불일치</option></select>\n')
ACT("event.stopPropagation(); openStatementPageS1", route="admin.settlement.board.show", method="GET", url=BOARD + "/{rightsHolder}?month=", perm="조회")
ACT("goToManualAdjustment", route="admin.settlement.adjustments.show", method="GET", url=A + "/settlement/adjustments", perm="조회(수동 조정 메뉴)")

# ── 3. 증빙 · 홈택스(개발 evidence 비활성) ───────────────────
ACT("remindTaxSubmit", flag="proto-only", note="미제출 권리자 재발송 — 개발 미구현")
ACT("openTaxSubmitModal", count=2, flag="proto-only", note="세금계산서 제출(승인번호 · PDF) — 개발 미구현")
ACT("runHometaxRecon", flag="proto-only", note="홈택스 매입 내역 업로드 · 대사 — 개발 미구현")
ACT("submitTaxDoc", flag="proto-only", route="admin.settlement.board.evidence.store (규칙)", method="POST", url=BOARD + "/evidence", perm="등록")
R('id="modalTaxSubmit"', 'id="modalTaxSubmit" data-dev-flag="proto-only"')

# ── 4. 대량이체 ────────────────────────────────────────
ACT("simulateBankFailure", flag="proto-only", note="QA 시연 — 개발 없음")
ACTX("showFirmbankingToast('result'", flag="proto-only", route="admin.settlement.board.transfer-results.store (규칙)", method="POST", url=BOARD + "/transfer-results", perm="등록",
    note="은행 결과 파일 1:1 대사 — 개발 미구현")
ACTX("showFirmbankingToast('download'", route="admin.settlement.board.download", method="GET", url=BOARD + "/download?month=", perm="다운로드 + 수정(ROUTE_PERMISSIONS) — v6.92 D-SETT-05 확정(쓰기 W + 엑셀 X), 프로토 #firmbankingPermNote",
    note="개발은 .layer__open[data-target=layerReason] 사유 모달(reason · reason_ref · reason_etc) 후 다운로드")

# ── S1 통합 정산서 상세(개발 별도 페이지 board.show) ─────────────
R('<section class="subview-panel stmt-subpage" data-subpage="s1">',
  '<section class="subview-panel stmt-subpage" data-subpage="s1"' + attrs(route="admin.settlement.board.show", method="GET", url=BOARD + "/{rightsHolder}?month=", perm="조회") + '>')
ACT("SJM_PAGE.back", count=2, route="admin.settlement.board.index", method="GET", url=BOARD + "?month=", perm="조회")
ACT("shiftS1Month", count=2, flag="proto-only", note="S1 월 이동 — 개발 없음(?month= 직접)")
NAME("selS1Holder", "rights_holder_id", note="개발은 URL {rightsHolder}")
R('id="chkS1ShowAllTables"', 'id="chkS1ShowAllTables" data-dev-flag="proto-only" data-dev-note="0원/미해당 표 전체 보기 — 개발 없음"')
ACT("unmaskS1Identity", flag="proto-only", note="실명번호 · 계좌 마스킹 해제 — 개발 S1에 없음")
R('id="s1ManualAdjLink"', 'id="s1ManualAdjLink"' + attrs(route="admin.settlement.adjustments.show", method="GET", url=A + "/settlement/adjustments", perm="조회(수동 조정 메뉴)"))
NAME("inpS1NewMemo", "memo", note="SettlementMemoRequest: month · rights_holder_id · payee_id(NULL=권리자 단위) · memo 2~2000자. 수정 · 삭제 없음")
ACT("saveS1AuditMemo", route="admin.settlement.board.memos.store", method="POST", url=BOARD + "/memos", perm="등록")
ACTX("openCarryoverModalP1(document.getElementById('selS1Holder')", route="admin.settlement.board.carryovers.show", method="GET", url=BOARD + "/{rightsHolder}/carryovers?month=", perm="조회")
ACTX("openCarryoverModalP1('${c.holderId}', 'OPERATOR'", route="admin.settlement.board.carryovers.show", method="GET", url=BOARD + "/{rightsHolder}/carryovers?month=", perm="조회")
ACTX("openStatementPageS2(document.getElementById('selS1Holder')", route="admin.settlement.statements.index", method="GET", url=A + "/settlement/statements?month=&rights_holder_id=", perm="조회(정산서 메뉴)")
ACTX("showToast('📄 내부 보관용", flag="proto-only", note="내부 정산서 PDF — 개발 없음")
ACT("confirmSingleStatementS1", flag="proto-only", note="개별 정산서 단건 확정 — 개발은 월 단위 마감(close.store)만")

# ── S2 권리자 제공 정산서(개발 statements.index) ─────────────────
R('<section class="subview-panel stmt-subpage" data-subpage="s2">',
  '<section class="subview-panel stmt-subpage" data-subpage="s2"' + attrs(route="admin.settlement.statements.index", method="GET", url=A + "/settlement/statements?month=&rights_holder_id=", perm="조회",
                                                                         note="guard(month, rights_holder_id)가 막으면 문구만 표시") + '>')
ACT("shiftS2Month", count=2, flag="proto-only", note="S2 월 이동 — 개발 없음(?month= 직접)")
NAME("selS2Holder", "rights_holder_id")
ACTX("openCarryoverModalP1(document.getElementById('selS2Holder')", route="admin.settlement.board.carryovers.show", method="GET", url=BOARD + "/{rightsHolder}/carryovers?month=", perm="조회")
ACTX("openCarryoverModalP1('${c.holderId}', 'PARTNER'", route="admin.settlement.board.carryovers.show", method="GET", url=BOARD + "/{rightsHolder}/carryovers?month=", perm="조회")
ACTX("openStatementPageS1(document.getElementById('selS2Holder')", route="admin.settlement.board.show", method="GET", url=BOARD + "/{rightsHolder}?month=", perm="조회")
ACT("goLockFromS2", note="마감 확정 화면으로 — 개발 #settlementCloseModal")
ACT("sendStatementS2", flag="proto-only", route="admin.settlement.statements.send.store (규칙)", method="POST", url=A + "/settlement/statements/send", perm="등록",
    note="권리자 이메일 · 알림톡 발송 — 개발 미구현")
ACTX("showToast('📄 권리자 제공용", route="admin.settlement.statements.download", method="GET", url=A + "/settlement/statements/download?month=&rights_holder_id=", perm="다운로드",
    note="개발은 엑셀(권리자정산서_<documentNo>) + 사유 모달 layerReason — PDF 아님", name="reason",
     value="refund_account · delivery_error · identity_check · payment_inquiry · legal_request · settlement_check · etc")


# ── P2 마감 게이트(개발 #settlementCloseModal · #settlementCloseForm) ──────
ACT("switchGateCase", count=2, flag="proto-only", note="시연 케이스 토글 — 개발 없음")
ACT("confirmFinalLockFromGate", route="admin.settlement.board.close.store", method="POST", url=BOARD + "/close", perm="등록 + 서비스 재판정(재무팀 · 최고 관리자)")
R('id="btnGateConfirmLock"', 'id="btnGateConfirmLock" data-dev-note="개발 id #settlementCloseSubmit"')
R('        <button type="button" class="btn" onclick="closeSettGateModal()">취소</button>',
  '        <input type="hidden" name="month" value="2026-10" data-dev-flag="dev-only" />\n'
  '        <input type="text" class="input" id="settlementConfirmMonth" name="confirm_month" placeholder="기준월 직접 입력 (예: 2026-10)" style="width:190px;" data-dev-flag="dev-only" data-dev-note="개발 SettlementBoardCloseRequest — month와 다르면 실행 안 함" />\n'
  '        <button type="button" class="btn" onclick="closeSettGateModal()">취소</button>')

# ── P1 이월 발생 내역 ─────────────────────────────────
ACT("switchCarryoverP1Mode", count=2, note="개발은 운영자 뷰 조각 하나(S2 안에서 같은 조각)")
NAME("selP1Holder", "rights_holder_id", note="개발은 URL {rightsHolder}")
R('id="selP1AccountType"', 'id="selP1AccountType" data-dev-flag="proto-only" data-dev-note="계정 필터 — 개발 없음(account_type PRE_TAX · POST_TAX 컬럼은 있음)"')
ACTX("showToast('📥 이월 발생 내역", flag="proto-only", note="이월 내역 엑셀 — 개발 버튼 disabled '2차 구현'")

# ── 검증 ───────────────────────────────────────────
VERIFY = [
    ("1. 통합 정산서 탭", "document.querySelector('[data-tab=tabStatements]').click()", "#tabStatements"),
    ("2. 지원금 원장 탭", "document.querySelector('[data-tab=tabSupportLedger]').click()", "#tabSupportLedger"),
    ("3. 증빙 탭", "document.querySelector('[data-tab=tabTaxInvoice]').click()", "#tabTaxInvoice"),
    ("4. 대량이체 탭", "document.querySelector('[data-tab=tabFirmbanking]').click()", "#tabFirmbanking"),
    ("P2 마감 게이트", "closeSettGateModal(); openSettGateModal()", "#settlementCloseModal|#modal-sett-gate"),
    # P1 이월 모달(#modalCarryoverP1)은 clean 원본에서도 열리지 않아 뺐다 — 공통 모달 핫픽스가 건 인라인 display:none을 openCarryoverModalP1이 지우지 않음(원본 문제, 보고만)
    ("세금계산서 제출 모달", "closeCarryoverModalP1(); openTaxSubmitModal('OPERATOR')", "#modalTaxSubmit"),
    ("S1 페이지", "closeTaxSubmitModal(); openStatementPageS1(getSelectedPayeeKey())", "[data-subpage=s1]"),
    ("S2 페이지", "openStatementPageS2(getSelectedPayeeKey())", "[data-subpage=s2]"),
]
