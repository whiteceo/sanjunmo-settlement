"""ADMN-BOOK-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BOOK-001.md
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
    "code": "ADMN-BOOK-001",
    "devCommit": DEV_COMMIT,
    "progress": "일부 구현(목록 · 공급 정보 등록/수정 · 신규 SKU 발급 · 정가 변경 등록 · 매입처 등록 · 위탁 도서 탭 · 엑셀). SKU 신규 채번은 교재 관리(PROD-004) 몫, 가채번 · 선등록 불러오기 · 공급률 계산은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.book-supply.index", "label": "도서 공급 원장(재무 메뉴 권한 전용)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 상단 · 안내 ────────────────────────────────────
R('id="role-mask-select"', 'id="role-mask-select" data-dev-flag="proto-only" data-dev-note="재무 권한 시연 — 개발은 BookSupplyService::canViewCost 실제 권한"')
ACT("openPendingProdBookForm", flag="proto-only", route="admin.book-supply.pending-books.index (규칙)", method="GET", url=A + "/book-supply/pending-books", perm="조회",
    note="[경로 3] 원가 미입력 선등록 SKU — 개발은 등록 폼 book_id select(공급 형태 없는 교재)")

# ── 목록 ──────────────────────────────────────────
ACT("openBookPriceHistoryModal", route="admin.book-supply.index", method="GET", url=A + "/book-supply?tab=prices&book_id=", perm="조회",
    note="개발은 모달이 아니라 탭 prices(정가 이력 + 정가 변경 등록 폼 priceForm)")
R('<a href="ADMN-SETT-001_baseline.html" class="btn btn-outline btn-sm">1계층 지분 매핑 (ADMN-SETT-001) ↗</a>',
  '<a href="ADMN-SETT-001_baseline.html" class="btn btn-outline btn-sm">1계층 지분 매핑 (ADMN-SETT-001) ↗</a>\n'
  '            <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.book-supply.index" data-dev-method="GET" data-dev-url="' + A + '/book-supply?tab=suppliers" data-dev-perm="조회" data-dev-note="매입처 탭 + 매입처 등록 supplierForm(SupplierRequest) POST admin.book-supply.suppliers.store" onclick="showToast(\'[개발] 매입처 탭 — GET /book-supply?tab=suppliers\')">매입처</button>\n'
  '            <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only" data-dev-route="admin.book-supply.index" data-dev-method="GET" data-dev-url="' + A + '/book-supply?tab=consignment" data-dev-perm="조회" data-dev-note="위탁 도서 탭(위탁자 · 위탁 계약 · 재고 회수 조건, 조회만)" onclick="showToast(\'[개발] 위탁 도서 탭 — GET /book-supply?tab=consignment\')">위탁 도서</button>')
NAME("filter-supply-type", "book_supply_type", value="OWN_PUBLISHED 자사 발행 · PURCHASED_RESALE 매입 재판매 · CONSIGNMENT 위탁 · BUNDLED 부속")
R('id="filter-origin"', 'id="filter-origin" data-dev-flag="proto-only" data-dev-note="출발 경로 — 개발 없음"')
R('id="filter-cost-status"', 'id="filter-cost-status" data-dev-flag="proto-only" data-dev-note="원가 확정 상태 — 개발 없음"')
R('id="filter-supplier"', 'id="filter-supplier" data-dev-flag="proto-only" data-dev-note="공급처 필터 — 개발 없음"')
NAME("filter-keyword", "keyword", note="도서명 · ISBN · SKU · 관리코드, 100자")
R('<input type="date" class="form-input" value="2026-10-15">\n              </div>',
  '<input type="date" class="form-input" value="2026-10-15" data-dev-flag="proto-only" data-dev-note="적용 기준일 — 개발 없음">\n              </div>\n'
  '              <div class="filter-field" data-dev-flag="dev-only" data-dev-note="BookSupplyService.php:111-114">\n'
  '                <label>정산 대상 / 판매 이력</label>\n'
  '                <div style="display:flex; gap:6px;">\n'
  '                  <select class="form-select" name="settlement"><option value="">정산 전체</option><option value="Y">정산 대상</option><option value="N">정산 비대상</option></select>\n'
  '                  <select class="form-select" name="sales"><option value="">판매 이력 전체</option><option value="yes">판매 이력 있음</option><option value="no">판매 이력 없음</option></select>\n'
  '                </div>\n'
  '              </div>')
ACT("resetLedgerFilters", note="개발은 /book-supply 로 이동(조건 제거)")
ACT("renderLedgerList", route="admin.book-supply.index", method="GET", url=A + "/book-supply?tab=list", perm="조회", note="정렬 없음, 30건 페이지")
R('onclick="showToast(\'도서 공급 원장 CSV', attrs(route="admin.book-supply.download", method="GET", url=A + "/book-supply/download", perm="다운로드", note="사유 레이어 layerReason").lstrip() + ' onclick="showToast(\'도서 공급 원장 CSV')
ACT("openNewLedgerForm", route="admin.book-supply.create", method="GET", url=A + "/book-supply/create", perm="등록",
    note="개발은 기존 교재(공급 형태 없음)에 공급 정보를 붙임 — SKU 신규 채번은 교재 관리(정책 질문 Q-BOOK001-1)")
ACT("openEditLedger", route="admin.book-supply.edit", method="GET", url=A + "/book-supply/{book}/edit", perm="수정", note="개발 행 클릭 tr[data-href]")
R('onclick="event.stopPropagation(); openEditLedger(', 'data-dev-route="admin.book-supply.edit" data-dev-method="GET" data-dev-url="' + A + '/book-supply/{book}/edit" data-dev-perm="수정" onclick="event.stopPropagation(); openEditLedger(')

# ── 정가 변경 이력 모달 ───────────────────────────────
R('<tbody id="price-history-tbody">', '<tbody id="price-history-tbody"' + attrs(note="book_price_histories(price · effective_from · effective_to · price_owner · reason · admin_id)") + '>')
R('          <div class="modal-footer">\n            <button type="button" class="btn btn-primary" onclick="closeBookPriceHistoryModal()">확인</button>',
  '            <div data-dev-flag="dev-only" data-dev-route="admin.book-supply.prices.update" data-dev-method="PUT" data-dev-url="' + A + '/book-supply/{book}/prices" data-dev-perm="수정" data-dev-note="BookPriceRequest — 오늘 이후 · 현재 정가 시작일 이후 · 발행일 + book_reprice_min_months(기본 12)개월 이후" style="margin-top:14px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;">\n'
  '              <strong style="font-size:12px;">정가 변경 등록</strong>\n'
  '              <input type="number" class="form-input" name="price" min="0" max="10000000" placeholder="적용 정가" style="width:130px;">\n'
  '              <input type="date" class="form-input" name="effective_from" style="width:150px;">\n'
  '              <select class="form-select" name="price_owner" style="width:150px;"><option value="SELF">당사 결정</option><option value="CONSIGNOR">위탁자 결정</option></select>\n'
  '              <input type="text" class="form-input" name="reason" maxlength="255" placeholder="통보 근거 (위탁자 결정이면 필수)" style="width:240px;">\n'
  '              <button type="button" class="btn btn-soft btn-sm" onclick="showToast(\'[개발] 정가 변경 등록 — PUT /book-supply/{book}/prices\')">등록</button>\n'
  '            </div>\n'
  '          </div>\n'
  '          <div class="modal-footer">\n            <button type="button" class="btn btn-primary" onclick="closeBookPriceHistoryModal()">확인</button>', 1)

# ── S1 등록 · 수정 ─────────────────────────────────
ACT("saveLedgerForm", route="admin.book-supply.store | admin.book-supply.update", method="POST | PUT", url=A + "/book-supply | /book-supply/{book}", perm="등록 | 수정",
    note="BookSupplyRequest — 개발 폼 id bookSupplyForm")
ACT("selectLedgerEntryMode", count=3, flag="proto-only", note="3경로 출발 선택 — 개발 없음(등록은 book_id 선택 1가지)")
R('onclick="event.stopPropagation(); openInstTempModal();"',
  'data-dev-flag="proto-only" data-dev-route="admin.book-supply.temp-books.index (규칙)" data-dev-method="GET" data-dev-url="' + A + '/book-supply/temp-books" data-dev-perm="조회" onclick="event.stopPropagation(); openInstTempModal();"')
R('onclick="event.stopPropagation(); selectLedgerEntryMode(\'BOOK_LEDGER\');"',
  'data-dev-flag="proto-only" data-dev-note="이 화면 SKU 채번 — 개발은 교재 관리(PROD-004)" onclick="event.stopPropagation(); selectLedgerEntryMode(\'BOOK_LEDGER\');"')
R('onclick="event.stopPropagation(); openProdPendingModal();"',
  'data-dev-flag="proto-only" data-dev-route="admin.book-supply.pending-books.index (규칙)" data-dev-method="GET" data-dev-url="' + A + '/book-supply/pending-books" data-dev-perm="조회" onclick="event.stopPropagation(); openProdPendingModal();"')
R('id="f-sku"', 'id="f-sku"' + attrs(name="book_id", note="등록 필수(공급 형태 없는 기존 교재 books.id) · 수정 prohibited — 프로토는 이 화면에서 PROD-BK 채번(정책 질문 Q-BOOK001-1)"))
R('id="f-temp-code"', 'id="f-temp-code" data-dev-flag="proto-only" data-dev-note="가채번 코드 — 개발은 계약 쪽 book_royalty_contracts.temp_code"')
ACT("openInstTempModal", flag="proto-only", route="admin.book-supply.temp-books.index (규칙)", method="GET", url=A + "/book-supply/temp-books", perm="조회")
R('id="f-title"', 'id="f-title"' + attrs(note="교재 관리(PROD-004) 값 읽기 전용 표시"))
NAME("f-supplier", "supplier_id", note="PURCHASED_RESALE면 필수")
R('id="f-isbn"', 'id="f-isbn"' + attrs(note="교재 관리(PROD-004) 값 읽기 전용 표시"))
R('id="f-author"', 'id="f-author"' + attrs(note="교재 관리(PROD-004) 값 읽기 전용 표시"))
R('id="f-ins-code"', 'id="f-ins-code" data-dev-flag="proto-only" data-dev-note="저자 권리자 · 인세 — 개발은 계약 원장 book-royalties"')
DEVNAME('name="f-supply-type" value="자체출판(인세)"', "book_supply_type", value="OWN_PUBLISHED")
DEVNAME('name="f-supply-type" value="위탁판매"', "book_supply_type", value="CONSIGNMENT", note="개발은 위탁 저장 거부(2차, 정책 질문 Q-BOOK001-2)")
DEVNAME('name="f-supply-type" value="사입판매"', "book_supply_type", value="PURCHASED_RESALE")
DEVNAME('name="f-supply-type" value="비매품(번들)"', "book_supply_type", value="BUNDLED", note="개발 라벨 '부속'")
ACT("issueNewSkuFromLocked", route="admin.book-supply.reissue.update", method="PUT", url=A + "/book-supply/{book}/reissue", perm="수정",
    note="기존 SKU 판매중지 → 교재 등록 화면으로 — 개발 reissueButton · reissueForm")
DEVNAME('name="f-own-copyright" value="false"', "own_copyright_yn", value="0")
DEVNAME('name="f-own-copyright" value="true"', "own_copyright_yn", value="1")
R('id="f-price"', 'id="f-price"' + attrs(note="개발 공급 정보 폼에 정가 없음 — 정가 변경 등록(admin.book-supply.prices.update)으로만"))
R('id="f-supply-rate"', 'id="f-supply-rate" data-dev-flag="proto-only" data-dev-note="공급률 / 제조원가율 — 개발 없음(원가 금액 직접 입력, 정책 질문 Q-BOOK001-3)"')
NAME("f-supply-cost", "cost_price", note="개발은 직접 입력 0~100,000,000 · 재무 권한만")
R('id="f-royalty-rate"', 'id="f-royalty-rate" data-dev-flag="proto-only" data-dev-note="저자 인세율 — 이 화면 없음(계약 원장 royalty_rate)"')
R('id="f-discount-rate"', 'id="f-discount-rate" data-dev-flag="proto-only" data-dev-note="기본 할인율 — 이 화면 없음(교재 관리 PROD-004)"')
R('id="f-sale-price"', 'id="f-sale-price" data-dev-flag="proto-only" data-dev-note="실판매가 — 이 화면 없음(교재 관리 PROD-004)"')
R('id="f-price-owner"', 'id="f-price-owner"' + attrs(name="price_owner", value="SELF · CONSIGNOR (정가 변경 등록 폼)"))
R('id="f-settlement-required"', 'id="f-settlement-required"' + attrs(note="개발 #settlementRequired · #settlementRoute(SETTLEMENT_ROUTE_LABELS) — 공급 형태 파생"))
R('id="f-consign-base-view"', 'id="f-consign-base-view" data-dev-note="위탁 정산 기준가(계약 연결 표시) — 개발은 위탁 도서 탭 조회만(위탁 등록 2차)"')
R('id="f-return-owner"', 'id="f-return-owner" data-dev-flag="proto-only" data-dev-note="위탁 재고 회수 — 개발은 위탁 도서 탭 조회만"')
R('id="f-init-stock"', 'id="f-init-stock" data-dev-flag="proto-only" data-dev-note="초기 재고 — 개발은 교재 관리(PROD-004)"')

# ── [경로 1] · [경로 3] 모달 ───────────────────────────
ACT("applyInstTempToLedger", count=2, flag="proto-only", note="가채번 도서 적용 — 개발 없음")
ACT("applyProdPendingToLedger", flag="proto-only", note="선등록 SKU 적용 — 개발 없음")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchSubview('list')", "#subview-list"),
    ("등록 view", "openNewLedgerForm()", "#subview-form"),
    ("수정 view", "openEditLedger('PROD-BK-1011')", "#subview-form"),
    ("선등록 불러오기", "openPendingProdBookForm()", "#subview-form"),
    # 모달은 버튼 클릭으로 연다(공통 핫픽스가 클릭 때만 인라인 display:none을 푼다)
    ("정가 이력 모달", "switchSubview('list'); document.querySelector('[onclick^=\"openBookPriceHistoryModal\"]').click()", "#modalBookPriceHistory"),
    ("가채번 모달", "openNewLedgerForm(); document.querySelector('[onclick^=\"openInstTempModal\"]').click()", "#modal-inst-temp"),
    ("선등록 SKU 모달", "openNewLedgerForm(); document.querySelector('[onclick*=\"openProdPendingModal\"]').click()", "#modal-prod-pending"),
]
