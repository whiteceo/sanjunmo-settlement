"""ADMN-SETT-005 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-005.md
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



def ACTX(prefix, count=1, **kw):
    """onclick="prefix(인자 포함 앞부분) 앞에 개발 라우트 속성을 단다"""
    R(f'onclick="{prefix}', attrs(**kw).lstrip() + f' onclick="{prefix}', count)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-005",
    "devCommit": DEV_COMMIT,
    "progress": "구현(SETT-005 목록 · S1 등록/수정 별도 페이지 /form · 확정/반려 모달). 4채널 정정 작업 표 · 감사 로그 탭 · 근거 파일 · 과세최저한 키 · 2단계 승인 표시는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.adjustments.index", "label": "정산 수동 조정 (show · store · update · destroy · download 같은 메뉴 권한)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

ADJ = A + "/settlement/adjustments"

# ── 상단 바 ─────────────────────────────────────────
R('''<button class="btn" onclick="location.href='ADMN-SETT-002_baseline.html'">''',
  '''<button class="btn"''' + attrs(route="admin.settlement.board.index", method="GET", url=A + "/settlement/board", perm="조회(월간 정산 메뉴)") + ''' onclick="location.href='ADMN-SETT-002_baseline.html'">''')
R('<button class="btn btn-primary" id="btnOpenNewAdjPage">',
  '<button class="btn btn-primary" id="btnOpenNewAdjPage"' + attrs(route="admin.settlement.adjustments.show", method="GET", url=ADJ + "/form", perm="조회(폼 열기) · 저장은 등록") + '>')

# ── KPI(개발: 당월 반영 · 미확정 · 확정 · 반려 · 전월 정정) ──────────
R('<section class="kpi-grid">', '<section class="kpi-grid"' + attrs(note="개발 KPI: 당월 반영 조정 건수 · 미확정(등록) · 확정(정산서 반영) · 반려 · 전월 정정 라인") + '>')
R('<div class="kpi-card" data-filter="NEED_2ND_APPROVAL">', '<div class="kpi-card" data-filter="NEED_2ND_APPROVAL" data-dev-flag="proto-only" data-dev-note="2차 승인 — 개발은 재무 담당 단독 확정(정책 확인)">')
R('<div class="kpi-card" data-filter="NEED_1ST_APPROVAL">', '<div class="kpi-card" data-filter="NEED_1ST_APPROVAL" data-dev-name="status" data-dev-value="pending (등록 · 미확정)">')
R('<div class="kpi-card" data-filter="APPROVED">', '<div class="kpi-card" data-filter="APPROVED" data-dev-name="status" data-dev-value="approved (확정)">')

# ── 탭 ─────────────────────────────────────────────
R('data-tab="tabWorkspace">', 'data-tab="tabWorkspace"' + attrs(route="admin.settlement.adjustments.index", method="GET", url=ADJ, perm="조회") + '>')
R('data-tab="tabChannels">', 'data-tab="tabChannels"' + attrs(flag="proto-only", note="4채널 정정 작업 표 — 개발은 S1에 세무 케이스 · 정정 채널 미리보기만(correction_channel)") + '>')
R('data-tab="tabAudit">', 'data-tab="tabAudit"' + attrs(flag="proto-only", note="수동 조정 감사 로그 표 — 개발 미구현(admin_logs)") + '>')

# ── 목록(#searchForm GET) ─────────────────────────────
ACT("openNewAdjPage", route="admin.settlement.adjustments.show", method="GET", url=ADJ + "/form", perm="조회(폼 열기)")
R('<div class="filter-bar">', '<div class="filter-bar" id="searchForm"' + attrs(route="admin.settlement.adjustments.index", method="GET", url=ADJ, perm="조회",
                                                                              note="KEEP: applied_month · origin_month · adjust_type · reason_type · status · keyword · page") + '>')
NAME("searchInput", "keyword", note="권리자명 · 수취인명 · 소명 내용 LIKE (조정 ID · 원 정산서 ID 검색은 개발 없음)")
NAME("reasonFilter", "reason_type", note="개발 13종 소문자 snake: rate_error · share_error · payee_split_error · refund_missing · lumpsum_month_error · buyout_income_error · tax_type_misjudge · reconcile_diff · account_transfer · book_supply_type_error · support_cap_error · consignment_fee_error · etc")
R('                <option value="ETC">기타 (ETC)</option>\n              </select>\n',
  '                <option value="ETC">기타 (ETC)</option>\n              </select>\n'
  '              <input type="month" class="input" name="applied_month" value="2026-10" title="반영월" data-dev-flag="dev-only" data-dev-note="개발 필터 applied_month">\n'
  '              <input type="month" class="input" name="origin_month" title="원 발생월" data-dev-flag="dev-only" data-dev-note="개발 필터 origin_month">\n'
  '              <select class="select" name="adjust_type" data-dev-flag="dev-only" data-dev-note="개발 TYPE_LABELS 6종"><option value="">전체 조정 유형</option><option value="CURRENT">당월 수동 조정</option><option value="PRIOR_FIX">전월 정정</option><option value="ACCOUNT_TRANSFER">계정 간 대체 전표</option><option value="PRO_RATA">지원금 이행률 정산</option><option value="SUPPORT_CAP_MANUAL">지원금 한도 수기 조정</option><option value="ALLOWANCE">정액 · 건당 수당</option></select>\n'
  '              <select class="select" name="status" data-dev-flag="dev-only" data-dev-note="개발 상태 3종"><option value="">전체 상태</option><option value="pending">등록</option><option value="approved">확정</option><option value="rejected">반려</option></select>\n')
R('              <div class="card-title">정산 수동 조정 및 계정 대체 전표 목록</div>\n',
  '              <div class="card-title">정산 수동 조정 및 계정 대체 전표 목록</div>\n'
  '              <button class="btn btn-sm" type="button" data-dev-flag="dev-only" data-dev-route="admin.settlement.adjustments.download" data-dev-method="GET" data-dev-url="' + ADJ + '/download" data-dev-perm="다운로드"'
  ' data-dev-note="공통 #layerReason 사유(reason · reason_ref · reason_etc) + data-reason-params 목록 조건. 파일명 정산수동조정_&lt;applied_month|all&gt;"'
  ''' onclick="showToast('조정 명세 엑셀 — 개발: 다운로드 사유 입력 후 내려받기')">조정 명세 엑셀</button>\n''')
R('<th>승인 단계 </th>', '<th data-dev-flag="proto-only" data-dev-note="2단계 승인 표시 — 개발은 단독 확정(approved_at · approver1_id)">승인 단계 </th>')
ACT("openAdjPage", note="개발 [수정] → admin.settlement.adjustments.show /form?id= , [확정] · [반려] → #layerAdjDecision 모달",
    route="admin.settlement.adjustments.show", method="GET", url=ADJ + "/form?id=", perm="조회")

# ── S1 등록 · 수정(개발 #adjForm, POST store) ─────────────────────
R('<div class="card subpage-card" id="adjNewCard">',
  '<div class="card subpage-card" id="adjNewCard"' + attrs(route="admin.settlement.adjustments.store", method="POST", url=ADJ, perm="등록",
                                                                                  note="개발 #adjForm — hidden id 있으면 수정") + '>')
NAME("newAdjType", "adjust_type", note="개발 값: CURRENT · PRIOR_FIX · ACCOUNT_TRANSFER · PRO_RATA · SUPPORT_CAP_MANUAL · ALLOWANCE(정액 · 건당 수당, 개발에만 — 정책 확인)")
R('<option value="CURRENT_MANUAL">', '<option value="CURRENT_MANUAL" data-dev-value="CURRENT">')
R('<option value="PRIOR_CORRECTION">', '<option value="PRIOR_CORRECTION" data-dev-value="PRIOR_FIX">')
NAME("newPayee", "payee_id", note="NULL = 권리자 본인. rights_holder_id는 원 정산서에서 자동")
NAME("newOriginStmt", "origin_settlement_id", note="정수 id — PRIOR_FIX · ACCOUNT_TRANSFER면 필수 (프로토타입 STMT-YYYYMM-…)")
NAME("newReasonCode", "reason_type", note="개발 13종 소문자 snake(3절)")
# 10-27 v6.84: 원본에서 PREPAY_OFFSET_ERR · MMG_CALC_ERR 삭제(개발 13종과 같아짐)
R('id="newTaxTypeEvidence"', 'id="newTaxTypeEvidence" data-dev-flag="proto-only" data-dev-note="과세유형 오인 근거 파일 — 개발 없음"')
NAME("newOriginMonth", "origin_month", note="YYYY-MM · PRIOR_FIX면 applied_month보다 앞서야")
NAME("newAppliedMonth", "applied_month")
NAME("newAdjAmount", "adjust_amount", note="정수 · 0 아님 · 음수=차감")
NAME("newAccountType", "account_type", value="PRE_TAX · POST_TAX (대체는 adjust_type ACCOUNT_TRANSFER + transfer_pair_key)")
NAME("newTaxType", "vat_type", value="exempt · taxable")
NAME("newIncomeCategory", "income_category", value="BUSINESS · OTHER (+ income_clause C05 · C15 · C17 · C19 별도 칸, 재화는 둘 다 비움)")
R('id="newTaxThresholdKey"', 'id="newTaxThresholdKey" data-dev-flag="proto-only" data-dev-note="과세최저한 판정 단위 키 — 개발 없음"')
R('      <!-- 실시간 승인 단계 및 4채널 증빙 정정 자동 판정 미리보기 -->\n',
  '      <div class="form-group" data-dev-flag="dev-only" data-dev-note="개발 SettlementAdjustmentRequest transfer_pair_key(≤40)">\n'
  '        <label class="form-label">대체 전표 쌍 키 (transfer_pair_key · 계정 간 대체일 때)</label>\n'
  '        <input type="text" class="input mono" name="transfer_pair_key" maxlength="40" placeholder="예: TR-202610-0001">\n'
  '      </div>\n'
  '      <!-- 실시간 승인 단계 및 4채널 증빙 정정 자동 판정 미리보기 -->\n')
NAME("newExplanation", "explanation", note="20~2000자(trim) · 개발 #adjExplanation")
ACT("submitNewAdjustment", route="admin.settlement.adjustments.store", method="POST", url=ADJ, perm="등록", note="개발 #adjSubmit '저장 (상태: 등록)'")

# ── S1 상세 · 확정(개발 #layerAdjDecision, PUT update) ─────────────
R('id="editExplanation"', 'id="editExplanation" name="explanation"')
ACTX("approveAdjustment('${item.id}', 1", route="admin.settlement.adjustments.update", method="PUT", url=ADJ, perm="수정",
    note="개발 #layerAdjDecision: id · decision=confirm")
ACTX("approveAdjustment('${item.id}', 2", flag="proto-only", note="재무 책임자 2차 승인 — 개발은 단독 확정(정책 확인)")
R('''      <div style="display:flex; justify-content:flex-end; gap:8px;">
        ${item.status === "WAIT_1ST" ? `''',
  '''      <div style="display:flex; justify-content:flex-end; gap:8px;">
        ${item.status === "APPROVED" ? "" : '<button class="btn" type="button" data-dev-flag="dev-only" data-dev-route="admin.settlement.adjustments.update" data-dev-method="PUT" data-dev-url="''' + ADJ + '''" data-dev-perm="수정" data-dev-name="reject_reason" data-dev-note="개발 #layerAdjDecision decision=reject — 반려 사유 2자 이상 필수" onclick="showToast(&quot;반려 — 개발: 반려 사유 입력 후 decision=reject&quot;)">반려</button>'}
        ${item.status === "WAIT_1ST" ? `''')

# ── 검증 ───────────────────────────────────────────
VERIFY = [
    ("1. 워크스페이스 탭", "document.querySelector('[data-tab=tabWorkspace]').click()", "#tabWorkspace"),
    ("2. 4채널 정정 탭", "document.querySelector('[data-tab=tabChannels]').click()", "#tabChannels"),
    ("3. 감사 로그 탭", "document.querySelector('[data-tab=tabAudit]').click()", "#tabAudit"),
    ("S1 등록 페이지", "openNewAdjPage()", "#adjNewCard"),
    ("S1 등록 폼 필드", "openNewAdjPage()", "#newExplanation"),
    ("S1 상세 · 승인", "SJM_PAGE.back(); openAdjPage(state.items[0].id)", "#adjDetailCard"),
    ("S1 상세 소명", "SJM_PAGE.back(); openAdjPage(state.items[0].id)", "#editExplanation"),
]
