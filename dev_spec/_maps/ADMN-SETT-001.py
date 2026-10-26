"""ADMN-SETT-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-001.md
apply_dev_map.py가 읽는다. 각 항목의 기대 건수가 원본과 다르면 전체를 멈춘다.
이 화면은 onclick 대신 data-action 위임 클릭이라 ACT 대신 DA(data-action 앞에 속성)를 쓴다.
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


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(SETT-001 목록 · S1 편집 별도 페이지 · P1 위반 모달). 감사 이력 탭 · 모계약 종료일 동기화 · 잔여 지분 자동 채우기 · 스냅샷 · 일반 상품은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.rights-mapping.index", "label": "상품별 권리자 매핑 (show · store · contracts 같은 메뉴 권한)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 탭: 개발은 목록 · 편집 별도 페이지 ──────────────────────
R('<button class="on" data-tab="list" id="tabBtnList" type="button">',
  '<button class="on" data-tab="list" id="tabBtnList" type="button"' + attrs(route="admin.settlement.rights-mapping.index", method="GET", url=A + "/settlement/rights-mapping", perm="조회") + '>')
R('<button data-tab="detail" id="tabBtnDetail" type="button">',
  '<button data-tab="detail" id="tabBtnDetail" type="button"' + attrs(route="admin.settlement.rights-mapping.show", method="GET", url=A + "/settlement/rights-mapping/edit?type=course|book&id=", perm="조회",
                                                                       note="개발은 별도 페이지(#mappingForm). URL은 /edit이지만 이름은 show — 조회 권한으로 열림") + '>')
R('<button data-tab="audit" id="tabBtnAudit" type="button">',
  '<button data-tab="audit" id="tabBtnAudit" type="button"' + attrs(flag="proto-only", route="admin.settlement.rights-mapping.history.index (규칙)", method="GET",
                                                                     url=A + "/settlement/rights-mapping/history", perm="조회", note="개발은 '변경 이력' 버튼 disabled 준비 중") + '>')
DA("goList", count=2, route="admin.settlement.rights-mapping.index", method="GET", url=A + "/settlement/rights-mapping?list[...]", perm="조회",
   note="저장 응답 redirect = 직전 검색 조건(LIST_KEYS)")

# ── 001 목록 검색(#searchForm GET) ─────────────────────────
R('<div class="row c4" style="margin-bottom:12px">',
  '<div class="row c4" style="margin-bottom:12px" id="searchForm"' + attrs(route="admin.settlement.rights-mapping.index", method="GET", url=A + "/settlement/rights-mapping", perm="조회",
                                                                          note="개발 #searchForm — 30건/페이지, created_at desc") + '>')
NAME("fType", "product_type", value="'' 전체 · course 강좌 · book 도서 SKU")
R('<option value="ALL">전체 (온라인 강좌 + 실물 도서)</option>', '<option value="ALL" data-dev-value="">전체 (온라인 강좌 + 실물 도서)</option>')
R('<option value="COURSE">온라인 강좌', '<option value="COURSE" data-dev-value="course">온라인 강좌')
R('<option value="BOOK">실물 도서 SKU', '<option value="BOOK" data-dev-value="book">실물 도서 SKU')
R('<option value="GOODS">일반 상품', '<option value="GOODS" data-dev-flag="proto-only" data-dev-note="개발 목록은 강좌 · 도서만(정책 확인 필요)">일반 상품')
NAME("fStatus", "verify_state", value="'' · unmapped · share_error · expiring · auto · ok")
R('<option value="ALL">전체 상태 보기</option>', '<option value="ALL" data-dev-value="">전체 상태 보기</option>')
R('<option value="UNMAPPED">', '<option value="UNMAPPED" data-dev-value="unmapped">')
R('<option value="MISMATCH">', '<option value="MISMATCH" data-dev-flag="proto-only" data-dev-note="개발 목록 값 없음 — 저장 시 PERIOD_RANGE 위반으로만 차단">')
R('<option value="OK">', '<option value="OK" data-dev-value="ok">')
R('<option value="AUTO">', '<option value="AUTO" data-dev-value="auto">')
NAME("fKeyword", "keyword", note="개발: 강좌 title · code / 도서 title · code · isbn LIKE — 권리자명은 rights_holder_id select로 분리")
R('          <div class="tablewrap" id="productListTable"></div>',
  '          <div class="row c4" style="margin-bottom:12px" data-dev-flag="dev-only" data-dev-note="개발 LIST_KEYS: supply_type · rights_holder_id · valid_on">\n'
  '            <div>\n'
  '              <label class="lbl" for="devSupplyType">공급 형태</label>\n'
  '              <select class="fc" id="devSupplyType" name="supply_type"><option value="">전체</option><option value="OWN_PUBLISHED">자사 발행</option><option value="PURCHASED_RESALE">매입 재판매</option><option value="CONSIGNMENT">위탁</option><option value="BUNDLED">부속</option></select>\n'
  '            </div>\n'
  '            <div>\n'
  '              <label class="lbl" for="devRightsHolder">권리자</label>\n'
  '              <select class="fc" id="devRightsHolder" name="rights_holder_id"><option value="">전체 권리자</option></select>\n'
  '            </div>\n'
  '            <div>\n'
  '              <label class="lbl" for="devValidOn">매핑 유효일</label>\n'
  '              <input class="fc" id="devValidOn" name="valid_on" type="date" value="2026-10-27">\n'
  '            </div>\n'
  '          </div>\n'
  '          <div class="tablewrap" id="productListTable"></div>')

# 스코어카드(JS 템플릿 안)
R('data-kpi="ALL">', 'data-kpi="ALL" data-dev-name="verify_state" data-dev-value="">')
R('data-kpi="UNMAPPED">', 'data-kpi="UNMAPPED" data-dev-name="verify_state" data-dev-value="unmapped">')
R('data-kpi="MISMATCH">', 'data-kpi="MISMATCH" data-dev-flag="proto-only" data-dev-note="개발 스코어카드 없음(계약 기간 불일치)">')
R('data-kpi="OK">', 'data-kpi="OK" data-dev-name="verify_state" data-dev-value="ok (개발 auto 카드는 별도)">')
R('      <div class="k-sub">100.00% 검증 및 자동고정 완료</div>\n    </button>\n',
  '      <div class="k-sub">100.00% 검증 및 자동고정 완료</div>\n    </button>\n'
  '    <button type="button" class="kpi-card" data-dev-flag="dev-only" data-dev-name="verify_state" data-dev-value="share_error" data-dev-note="개발 스코어카드 — 검색 조건과 무관한 전체 건수">\n'
  '      <div class="k-title"><span class="neg">지분 합계 오류</span><span class="chip ng">점검</span></div>\n'
  '      <div class="k-num neg">—</div>\n'
  '      <div class="k-sub">날짜 구간별 지분 합계 100.00% 아님</div>\n'
  '    </button>\n'
  '    <button type="button" class="kpi-card" data-dev-flag="dev-only" data-dev-name="verify_state" data-dev-value="expiring" data-dev-note="개발 스코어카드 — 계약 만료 30일 이내">\n'
  '      <div class="k-title"><span>계약 만료 임박 (D-30)</span><span class="chip warn">갱신 확인</span></div>\n'
  '      <div class="k-num" style="color:var(--warn)">—</div>\n'
  '      <div class="k-sub">적용 계약 종료일 30일 이내</div>\n'
  '    </button>\n')

# 목록 행 → S1 편집
R('<button type="button" class="btn sm ${ev.status==="UNMAPPED"?"pr":""}" data-open-product="${esc(p.id)}">',
  '<button type="button" class="btn sm ${ev.status==="UNMAPPED"?"pr":""}"' + attrs(route="admin.settlement.rights-mapping.show", method="GET",
                                                                                  url=A + "/settlement/rights-mapping/edit?type=&id=", perm="조회") + ' data-open-product="${esc(p.id)}">')

# ── S1 편집 ───────────────────────────────────────
NAME("quickJumpSelect", "id", note="개발 편집 페이지 쿼리 type · id")
R('<span id="detailSaleBadge"></span>',
  '<span id="detailSaleBadge"></span>\n'
  '            <span class="sub" data-dev-flag="dev-only" data-dev-note="개발 S1 머리 정보: 마감 경계(site_settings.settlement_closed_month) · 저장 허용 시작 · 계약 원장 링크">'
  '마감 경계 2026-09 · 저장 허용 시작 2026-10-01 · <a href="ADMN-INST-001_baseline.html">계약 원장</a></span>')
DA("syncContractDates", flag="proto-only", route="admin.settlement.rights-mapping.contract-sync.update (규칙)", method="PUT",
   url=A + "/settlement/rights-mapping/contract-sync", perm="수정", note="모계약 종료일 일괄 동기화 — 개발 미구현")
DA("copyToAllLessons", note="개발: #checkAllLectures · .js-lecture-group → lecture_ids[] 로 같은 행을 여러 강의에 저장")
DA("quickFillRemainder", flag="proto-only", note="잔여 지분 자사 자동 채우기 — 개발 미구현")
DA("addShareRow", route="admin.settlement.rights-mapping.contracts", method="GET", url=A + "/settlement/rights-mapping/contracts?rights_holder_id=&type=&id=", perm="조회",
   note="개발 .layer__open[data-target=layerHolderPick] → 권리자 선택 후 적용 계약 후보(JSON)")
DA("snapshot", flag="proto-only", note="최근 저장 스냅샷 JSON — 개발 미구현")
DA("validationModal", note="개발 P1 #layerMappingViolation — store 422 violations(SHARE_SUM · SIGNER_SCOPE · CONTRACT_INVALID · PERIOD_RANGE · LOCKED_MONTH · PERIOD_DUP · NOT_TARGET · CONSIGNMENT_SINGLE · SUPPLY_TYPE_MISSING), #mvFitWindow 허용 구간으로 맞추기 · #mvGoLedger 계약 원장 이동")
DA("save", route="admin.settlement.rights-mapping.store", method="POST", url=A + "/settlement/rights-mapping", perm="등록",
   note="개발 #btnSave fetch JSON {type · id · lecture_ids[] · rows[]} → {ok · message · redirect}")
R('<button class="btn pr" id="saveButton"', '<button class="btn pr" id="saveButton" data-dev-note="개발 id #btnSave"')
R('<div id="modalBack" class="modalback" hidden="">',
  '<div id="modalBack" class="modalback" hidden=""' + attrs(note="공용 모달 — 행 추가는 개발 #layerHolderPick, 검증 상세는 #layerMappingViolation") + '>')

# 행 관리 버튼(JS 템플릿 안)
R('data-action="editRow"', attrs(note="개발 행 입력 tr[data-key] .js-contract · .js-share · .js-start · .js-end — 값이 바뀌면 서비스가 기존 행을 닫고 새 행 삽입(rows.*.id)").lstrip() + ' data-action="editRow"')
R('data-action="deleteRow"', attrs(note="개발 .js-remove (미저장 행 제거)").lstrip() + ' data-action="deleteRow"')
R('data-action="endRow"', attrs(note="개발은 rows.*.end_date 지정 후 저장 — 종료 사유 필드 없음").lstrip() + ' data-action="endRow"')

# 행 모달 필드(FormData가 name을 읽으므로 data-dev-name만)
DEVNAME('id="m_endDate" name="endDate"', "rows[n][end_date]")
DEVNAME('id="m_endReason" name="endReason"', "(없음)", note="개발 행에 사유 필드 없음(감사 로그만)")
DEVNAME('id="m_holderId" name="holderId"', "rows[n][rights_holder_id]")
DEVNAME('id="m_contractId" name="contractId"', "rows[n][contract_id]", note="필수 — rights_holder_contracts.id")
DEVNAME('id="m_share" name="share"', "rows[n][share_ratio]", note="0~100 · 소수 2자리")
DEVNAME('id="m_start" name="start"', "rows[n][start_date]")
DEVNAME('id="m_endBasis" name="endBasis"', "(없음)", note="종료 기준(모계약 연동) — 개발 없음, end_date NULL = 기한 없음")
DEVNAME('id="m_end" name="end"', "rows[n][end_date]")
DEVNAME('id="m_reason" name="reason"', "(없음)", note="개발 행에 변경 사유 필드 없음")

# ── 검증 ───────────────────────────────────────────
VERIFY = [
    ("목록 탭", "switchTab('list')", "#view-list"),
    ("편집 탭", "switchTab('detail')", "#view-detail"),
    ("이력 탭", "switchTab('audit')", "#view-audit"),
    ("상품 선택 → 편집", "selectProductAndOpenDetail(products[0].id)", "#view-detail"),
    ("행 추가 모달", "closeModal(); selectProductAndOpenDetail(products[0].id); openRowModal(null)", "#modalBack"),
    ("행 추가 모달 필드", "closeModal(); selectProductAndOpenDetail(products[0].id); openRowModal(null)", "#m_holderId"),
    ("검증 상세 모달", "closeModal(); switchTab('detail'); document.querySelector('[data-action=validationModal]').click()", "#modalBack"),
]
