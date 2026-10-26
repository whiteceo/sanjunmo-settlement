"""ADMN-ORD-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-ORD-001.md
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


def ACTX(head, count=1, **kw):
    """onclick="<head> 앞에 개발 속성을 단다 — 같은 함수를 인자 · 문구로 구분할 때"""
    R(f'onclick="{head}', attrs(**kw).lstrip() + f' onclick="{head}', count)


def ALERT(prefix, count=1, **kw):
    """alert 버튼은 문구 앞부분으로 구분한다"""
    ACTX(f"alert('{prefix}", count, **kw)


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
    "code": "ADMN-ORD-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(ORD-001 · 001-S1 · 002 · 002-P1~P3). 001-P4 직권 부여 · 가상계좌 기한 연장 · 3PL 외부 계정은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.orders.index", "label": "주문 내역 관리 (목록 · 상세)"},
        {"route": "admin.deliveries.index", "label": "배송 관리 · 3PL 연동"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 · 패널 · 버튼 id → 개발 id ──────────────────────
RENAME_ID("modal3plConfirm", "layerDispatch", 5)
RENAME_ID("modalBulkUpload", "layerImport", 6)
RENAME_ID("modalSingleWaybill", "layerTracking", 5)
RENAME_ID("modalBatchHistory", "layerBatches", 4)
RENAME_ID("returnInspectPanel", "inspectionPanel", 2)
RENAME_ID("inspectPanelTitle", "inspectionTarget", 2)
RENAME_ID("btn3plDownload", "dispatchButton", 2)
RENAME_ID("btnSingleWaybill", "trackingButton", 2)
RENAME_ID("btnBatchHistory", "batchesButton", 1)
RENAME_ID("btnSelectAllShipQuery", "selectAllResults", 1)
RENAME_ID("shipSelectedCnt", "selectedCount", 1)
R('<div class="modal-backdrop" id="modalDirectGrant">',
  '<div class="modal-backdrop" id="modalDirectGrant" data-dev-flag="proto-only" data-dev-note="001-P4 수강권 직권 부여 — 개발 미구현. 레이어 id (규칙) layerDirectGrant">')

# ── 상단 역할 전환 · 화면 전환 ───────────────────────────
ACT("setSessionRole", count=2, flag="proto-only", note="3PL 외부 계정(ROLE_PARTNER_3PL) — 개발에 역할 없음, 메뉴 권한만(Q-ORD-4)")
ACTX("switchOrdView('ord001')\">📋", route="admin.orders.index", method="GET", url=A + "/orders", perm="조회")
ACTX("switchOrdView('ord002')\">🚚", route="admin.deliveries.index", method="GET", url=A + "/deliveries?tab=ready", perm="조회")
ACTX("switchOrdView('ord001s1')\">🔍", route="admin.orders.show", method="GET", url=A + "/orders/{order}", perm="조회")

# ── KPI 카드 ─────────────────────────────────────────
ACTX("filterOrdListByKpi('ALL')", route="admin.orders.index", method="GET", url=A + "/orders", perm="조회")
ACTX("filterOrdListByKpi('배송준비중')", route="admin.orders.index", method="GET", url=A + "/orders?statuses[]=ready", perm="조회")
ACTX("filterOrdListByKpi('결제대기')", route="admin.orders.index", method="GET", url=A + "/orders?statuses[]=waiting", perm="조회")
ACTX("filterOrdListByKpi('배송중')", flag="proto-only", note="KPI '배송중' 카드 — 개발 요약 카드에 없음(목록 statuses[]=shipping으로 조회는 가능)")
ACTX("filterOrdListByKpi('반품수거중')", route="admin.orders.index", method="GET", url=A + "/orders?refund_requested=1", perm="조회")

# ── 001 목록 검색 ────────────────────────────────────
NAME("fDateType", "date_basis", note="개발 값: paid_at · created_at · shipped_at · refund_completed_at")
DEVNAME('<option value="PAID_AT"', "date_basis", value="paid_at")
DEVNAME('<option value="ORDER_AT"', "date_basis", value="created_at")
DEVNAME('<option value="SHIP_AT"', "date_basis", value="shipped_at")
DEVNAME('<option value="REFUND_AT"', "date_basis", value="refund_completed_at")
R('<input type="date" class="form-input" value="2026-02-01" style="width:135px;" />', '<input type="date" class="form-input" id="dateFrom" name="date_from" value="2026-02-01" style="width:135px;" />')
R('<input type="date" class="form-input" value="2026-10-26" style="width:135px;" />', '<input type="date" class="form-input" id="dateTo" name="date_to" value="2026-10-26" style="width:135px;" />')
ACT("selectQuickDate", count=5, note="개발 기간 칩 [data-period-from] today · 7d · 1m · 3m · all")
NAME("fPayMethod", "method", note="개발 값: card · easy_pay · virtual_account · transfer · mobile_phone · gift(상품권 3종 묶음 — 프로토 없음)")
DEVNAME('<option value="신용/체크카드"', "method", value="card")
DEVNAME('<option value="간편결제"', "method", value="easy_pay")
DEVNAME('<option value="가상계좌"', "method", value="virtual_account")
DEVNAME('<option value="계좌이체"', "method", value="transfer")
DEVNAME('<option value="휴대폰결제"', "method", value="mobile_phone")
R('<div class="chip-group" id="statusChipGroup">', '<div class="chip-group" id="statusChipGroup"' + attrs(name="statuses[]", note="[data-status-all] · [data-status-item] — 전체와 배타") + '>')
DEVNAME('data-status="ALL"', "statuses[]", value="(전체 — data-status-all)")
DEVNAME('data-status="결제대기"', "statuses[]", value="waiting")
DEVNAME('data-status="결제완료"', "statuses[]", value="paid")
DEVNAME('data-status="배송준비중"', "statuses[]", value="ready")
DEVNAME('data-status="배송중"', "statuses[]", value="shipping")
DEVNAME('data-status="배송완료"', "statuses[]", value="delivered")
DEVNAME('data-status="반품수거중"', "statuses[]", value="returning", note="개발 라벨 '반품진행중'(Delivery::STATUS_LABELS) — 화면 라벨은 정본 유지")
DEVNAME('data-status="환불완료"', "statuses[]", value="refunded")
DEVNAME('data-status="기각"', "statuses[]", value="rejected")
R('<div class="chip-group" id="typeChipGroup">', '<div class="chip-group" id="typeChipGroup"' + attrs(name="kind") + '>')
DEVNAME('data-type="인강"', "kind", value="lecture")
DEVNAME('data-type="교재"', "kind", value="book")
DEVNAME('data-type="복합"', "kind", value="mixed")
R('data-type="일반상품"', 'data-type="일반상품" data-dev-flag="proto-only" data-dev-note="개발 OrderService::KINDS는 인강 · 교재 · 복합 3종(order_items.item_type에 일반상품 없음)"')
R('<input type="text" class="form-input" placeholder="최소 금액" style="width:100px;" />', '<input type="text" class="form-input" name="amount_min" placeholder="최소 금액" style="width:100px;" />')
R('<input type="text" class="form-input" placeholder="최대 금액" style="width:100px;" />', '<input type="text" class="form-input" name="amount_max" placeholder="최대 금액" style="width:100px;" />')
NAME("chkHasDelivery", "physical_only", value="1")
NAME("fSearchKey", "search_type", note="개발 값: order_no · buyer · receiver · phone(검색 시 열람 로그)")
DEVNAME('<option value="ORDER_NO"', "search_type", value="order_no")
DEVNAME('<option value="BUYER"', "search_type", value="buyer")
DEVNAME('<option value="RECEIVER"', "search_type", value="receiver")
DEVNAME('<option value="PHONE"', "search_type", value="phone")
NAME("fSearchVal", "keyword", note="주문번호 외 2자 이상")
ACTX("renderOrderList()\">조회", route="admin.orders.index", method="GET", url=A + "/orders", perm="조회")
ACT("resetOrdFilter", count=2, route="admin.orders.index", method="GET", url=A + "/orders", perm="조회")
R('<select class="form-select" style="width:105px;">\n                    <option>50개씩 보기</option>\n                    <option>100개씩 보기</option>\n                    <option>200개씩 보기</option>',
  '<select class="form-select" style="width:105px;" name="per_page">\n                    <option value="50">50개씩 보기</option>\n                    <option value="100">100개씩 보기</option>\n                    <option value="200">200개씩 보기</option>')
ACT("downloadOrderLookupExcel", route="admin.orders.download", method="GET", url=A + "/orders/download", perm="다운로드",
    note="개발은 공용 사유 레이어 layerReason(reason · reason_etc · reason_ref)을 먼저 띄움 — 정본은 사유 없이 열람 로그만(Q-ORD-2), 화면은 정본 유지")
ACT("openDirectGrantModal", flag="proto-only", route="admin.orders.grants.create (규칙)", method="GET", url=A + "/orders/grants/create", perm="등록")
ACT("goToDeliveryManageWithReady", route="admin.deliveries.index", method="GET", url=A + "/deliveries?tab=ready", perm="조회(배송 관리 메뉴)")
ACT("toggleAllOrdRows", note="개발 목록은 행 선택 없음(조회 · 엑셀만)")

# ── 001-S1 주문 상세 ─────────────────────────────────
ACT("toggleShipOrderLock", count=2, route="admin.orders.dispatch.destroy", method="DELETE", url=A + "/orders/{order}/dispatch", perm="삭제 + 최고관리자",
    note="개발 레이어 layerRevoke — reason(MemberReasonRequest)")
ALERT("회원 상세(ADMN-MBR-001)", route="admin.members.show", method="GET", url=A + "/members/{member}", perm="조회(회원 메뉴)")
R('id="vbankExtendBox"', 'id="vbankExtendBox" data-dev-flag="proto-only" data-dev-note="가상계좌 입금 기한 연장 — 개발 의도적 미구현(OrderService.php:490, Q-ORD-1)"')
NAME("inpNewVbankDue", "virtual_account_due_at", note="(규칙) payments.virtual_account_due_at")
NAME("inpVbankReason", "reason")
ACT("extendVbankDueDate", flag="proto-only", route="admin.orders.deposit-due.update (규칙)", method="PUT", url=A + "/orders/{order}/deposit-due", perm="수정")
ACT("enableAddressEditMode", perm="수정", note="개발은 레이어 layerAddress · addressForm(인라인 편집 아님)")
NAME("inpRecvName", "receiver_name")
NAME("inpRecvPhone", "receiver_phone", note="숫자만 10~11자리")
NAME("inpZipcode", "receiver_zipcode")
ACT("simulateZipSearch", note="우편번호 찾기 결과만 receiver_zipcode로")
R('id="islandCheckBadge"', 'id="islandCheckBadge" data-dev-flag="proto-only" data-dev-note="배송지 보정 시 도서산간 추가배송비 판정 — 개발 보정은 금액 재판정 없음(확인 필요)"')
NAME("inpAddr1", "receiver_address", note="사서함 · 군사우편 차단(Delivery::UNSHIPPABLE_ADDRESS_PATTERN)")
NAME("inpAddr2", "receiver_address_detail")
NAME("inpShipMsg", "delivery_memo", note="100자 이하")
NAME("inpAddrChangeReason", "reason", note="MemberReasonRequest 10자 이상(프로토 2자)")
ACT("commitAddressChange", route="admin.orders.address.update", method="PUT", url=A + "/orders/{order}/address", perm="수정",
    note="알림톡 TPL_DELIVERY_ADDRESS_CHANGED")
ACTX("switchOrdView('ord002')\">배송 관리에서 보기", route="admin.deliveries.index", method="GET",
     url=A + "/deliveries?tab=…&search_type=order_no&keyword={order_no}", perm="조회")
ACTX("window.print()", route="admin.orders.print.show", method="GET", url=A + "/orders/{order}/print", perm="조회")
NAME("inpAdminMemo", "content", note="500자 이하, 추가만(order_cs_logs)")
ACT("addAdminTimelineMemo", route="admin.orders.memos.store", method="POST", url=A + "/orders/{order}/memos", perm="등록")

# ── 002 배송 관리 탭 · 검색 ───────────────────────────
for _tab, _dev in (("READY", "ready"), ("SHIPPING", "shipping"), ("DELIVERED", "delivered"), ("RETURN", "return")):
    ACTX(f"switchShipTab('{_tab}')", route="admin.deliveries.index", method="GET", url=A + f"/deliveries?tab={_dev}", perm="조회")
R('<input type="date" class="form-input" value="2026-08-01" style="width:135px;" />', '<input type="date" class="form-input" name="date_from" value="2026-08-01" style="width:135px;" />')
R('<input type="date" class="form-input" value="2026-08-18" style="width:135px;" />', '<input type="date" class="form-input" name="date_to" value="2026-08-18" style="width:135px;" />')
NAME("fShipSku", "book_id", note="값 = books.id(프로토는 상품명)")
R('<select class="form-select" style="width:140px;">\n                          <option value="ALL">전체 권역</option>',
  '<select class="form-select" style="width:140px;" data-dev-flag="proto-only" data-dev-note="배송 권역 필터 — 개발 DeliveryService::normalizeFilters에 없음">\n                          <option value="ALL">전체 권역</option>')
R('id="chkIslandOnly" onchange', 'id="chkIslandOnly" data-dev-flag="proto-only" data-dev-note="도서산간만 보기 — 개발 필터 없음" onchange')
R('<select class="form-select" style="width:130px;">\n                          <option>주문번호</option>\n                          <option>수령인명</option>\n                          <option>휴대전화</option>\n                          <option>운송장번호</option>',
  '<select class="form-select" style="width:130px;" name="search_type">\n                          <option value="order_no">주문번호</option>\n                          <option value="receiver">수령인명</option>\n                          <option value="phone">휴대전화</option>\n                          <option value="tracking">운송장번호</option>')
NAME("fShipKeyword", "keyword")
ACTX("renderShipTable()\">조회", route="admin.deliveries.index", method="GET", url=A + "/deliveries", perm="조회")
R('<span style="font-size:11.5px;color:var(--text-muted);margin-left:6px;">※ 배송 상태는 상단 선택 탭으로',
  '<select class="form-select" name="sort" style="width:150px;" data-dev-flag="dev-only" data-dev-note="개발 탭별 정렬 TAB_SORTS · DEFAULT_SORTS(sort · direction)">'
  '<option value="paid_at">결제일 오래된 순</option><option value="shipped_at">출고일순</option><option value="status">상태순</option>'
  '<option value="delivered_at">배송완료일순</option><option value="received_at">입고일순</option></select>\n'
  '                        <span style="font-size:11.5px;color:var(--text-muted);margin-left:6px;">※ 배송 상태는 상단 선택 탭으로')

# ── 002 툴바 · 발주 ──────────────────────────────────
ACT("selectAllShipRows", note="개발 selectAllResults — 서버가 readyIds 전달")
ACT("open3plConfirmModal", perm="다운로드", note="개발 dispatchButton → 레이어 layerDispatch")
ACT("execute3plExcelDownload", route="admin.deliveries.dispatch.download", method="POST", url=A + "/deliveries/dispatch", perm="다운로드",
    note="ids[] — 출고지시 · 예약판매 · 환불 심사 중 · 취소 건은 서비스가 빼고 건수 안내")
ACTX("openModal('layerImport')", count=2, perm="등록", note="개발 레이어 layerImport · importForm")
ACT("openSingleWaybillModal", perm="수정", note="개발 trackingButton → 레이어 layerTracking")
ACTX("openModal('layerBatches')", route="admin.deliveries.batches.index", method="GET", url=A + "/deliveries/batches?date_from=&date_to=&type=", perm="조회")
R('                  <button type="button" class="btn btn-outline" id="batchesButton"',
  '                  <button type="button" class="btn btn-outline" id="deliveredButton" disabled title="배송완료 탭에서 행을 선택하면 사용"'
  + attrs(flag="dev-only", route="admin.deliveries.delivered.update", method="PUT", url=A + "/deliveries/delivered", perm="수정",
          note="배송완료일 보정 layerDelivered — ids[] · delivered_at(오늘 이전) · reason(MemberReasonRequest)") + '>\n'
  '                    📅 배송완료일 보정\n'
  '                  </button>\n'
  '                  <button type="button" class="btn btn-outline" id="batchesButton"')

# ── 002-S3 반품 검수 ─────────────────────────────────
NAME("inpInspectResult", "inspection_result")
DEVNAME('<option value="NORMAL"', "inspection_result", value="normal")
DEVNAME('<option value="DAMAGED"', "inspection_result", value="damaged")
NAME("inpInspectFault", "liability", note="normal일 때 required — 개발은 customer · company 2종(편도 · 왕복 구분 없음, Q-RFD-7)")
DEVNAME('<option value="CUSTOMER_ONEWAY"', "liability", value="customer", note="편도 구분 없음")
R('<option value="CUSTOMER">', '<option value="CUSTOMER"' + attrs(name="liability", value="customer") + '>')
DEVNAME('<option value="COMPANY"', "liability", value="company")
NAME("inpInspectMemo", "inspection_memo", note="2000자 이하")
ALERT("창고 검수 사진", name="photos[]", note="jpg · png · 10MB — 필수: 훼손 또는 고객 귀책(Q-ORD-3). 열람 admin.deliveries.returns.show")
ACT("clearReturnSelection", note="개발 inspectionClear")
ACT("saveReturnInspection", route="admin.deliveries.returns.update", method="PUT", url=A + "/deliveries/returns/{refund}", perm="수정(배송 관리 메뉴)")

# ── 002-P1 송장 벌크 업로드 ───────────────────────────
ACTX("switchP1Step(1)", route="admin.deliveries.tracking.preview.store", method="POST", url=A + "/deliveries/tracking/preview", perm="등록",
     note="STEP 1 사전 읽기(JSON, 저장 안 함)")
R('<input type="text" class="form-input" value="3PL_송장회신_20260818.xlsx"', '<input type="text" class="form-input" data-dev-name="file" data-dev-note="xlsx · 10MB · 5,000행 — 개발 id importFile" value="3PL_송장회신_20260818.xlsx"')
R('<select class="form-select" style="width:320px;">\n                    <option value="BATCH-20260818-01">',
  '<select class="form-select" style="width:320px;" name="batch_id"' + attrs(note="값 = delivery_batches.id(export), 비우면 전체 배치") + '>\n                    <option value="BATCH-20260818-01">')
R('<label><input type="checkbox" checked /> 배송출고 알림톡 자동 발송', '<label><input type="checkbox" name="notify" value="1" checked /> 배송출고 알림톡 자동 발송')
R('<label><input type="checkbox" checked /> 오류 행은 건너뛰고', '<label><input type="checkbox" checked' + attrs(note="개발은 항상 정상 행만 반영(옵션 없음)") + ' /> 오류 행은 건너뛰고')
R('<input type="checkbox" /> 기존 운송장 덮어쓰기', '<input type="checkbox" name="overwrite" value="1" /> 기존 운송장 덮어쓰기')
ALERT("3PL 송장 업로드 표준 엑셀 양식", route="admin.deliveries.template.download", method="GET", url=A + "/deliveries/tracking/template/download", perm="다운로드")
ALERT("3PL 회신용 실패 목록 엑셀", route="admin.deliveries.failures.download", method="GET", url=A + "/deliveries/tracking/{batch}/failures/download", perm="다운로드")
ACT("retryFailedAlimtalk", route="admin.deliveries.batches.notifications.update", method="PUT", url=A + "/deliveries/batches/{batch}/notifications", perm="수정")
R('id="btnP1Action" onclick="switchP1Step(2)"', 'id="btnP1Action"' + attrs(route="admin.deliveries.tracking.store", method="POST", url=A + "/deliveries/tracking", perm="등록", note="1,000행 초과는 큐 처리") + ' onclick="switchP1Step(2)"')

# ── 002-P2 송장 단건 ─────────────────────────────────
NAME("p2Courier", "courier")
DEVNAME('<option value="CJ대한통운"', "courier", value="CJ")
DEVNAME('<option value="한진택배"', "courier", value="HANJIN")
DEVNAME('<option value="롯데택배"', "courier", value="LOTTE")
DEVNAME('<option value="우체국택배"', "courier", value="EPOST")
NAME("p2WaybillNo", "tracking_no", note="숫자 10~14자리")
NAME("p2ShipDate", "shipped_at")
NAME("p2ReasonType", "reason_code")
DEVNAME('<option value="3PL 회신 누락"', "reason_code", value="missing")
DEVNAME('<option value="운송장 오타 정정"', "reason_code", value="typo")
DEVNAME('<option value="택배사 변경"', "reason_code", value="courier")
R('<option value="기타">기타 (하단', '<option value="기타"' + attrs(name="reason_code", value="etc") + '>기타 (하단')
NAME("p2ReasonMemo", "reason_memo", note="etc일 때 필수 · 200자 이하")
NAME("p2SendAlimtalk", "notify", value="1")
ACT("submitSingleWaybill", route="admin.deliveries.tracking.update", method="PUT", url=A + "/deliveries/{delivery}/tracking", perm="수정")

# ── 002-P3 이력 ─────────────────────────────────────
R('      <div class="modal-body">\n        <div class="table-wrap">\n          <table class="data-table" style="min-width:100%;">\n            <thead>\n              <tr>\n                <th>배치 · 업로드 번호</th>',
  '      <div class="modal-body">\n'
  '        <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;" data-dev-flag="dev-only" data-dev-note="개발 DeliveryBatchRequest 기간 · 구분 필터(기본 최근 30일)">\n'
  '          <input type="date" class="form-input" name="date_from" value="2026-07-20" style="width:135px;" />\n'
  '          <span>~</span>\n'
  '          <input type="date" class="form-input" name="date_to" value="2026-08-18" style="width:135px;" />\n'
  '          <select class="form-select" name="type" style="width:150px;"><option value="all">전체</option><option value="export">발주 다운로드</option><option value="import">송장 업로드</option></select>\n'
  '        </div>\n'
  '        <div class="table-wrap" id="batchHistoryBody">\n          <table class="data-table" style="min-width:100%;">\n            <thead>\n              <tr>\n                <th>배치 · 업로드 번호</th>')
ALERT("발송 실패 2건에 대해", route="admin.deliveries.batches.notifications.update", method="PUT", url=A + "/deliveries/batches/{batch}/notifications", perm="수정")
ALERT("업로드 원본 파일", route="admin.deliveries.batches.download", method="GET", url=A + "/deliveries/batches/{batch}/download", perm="다운로드")
ALERT("실패 7건 엑셀", route="admin.deliveries.failures.download", method="GET", url=A + "/deliveries/tracking/{batch}/failures/download", perm="다운로드")
ALERT("동일 발주 엑셀 파일을 재다운로드", count=2, route="admin.deliveries.batches.download", method="GET", url=A + "/deliveries/batches/{batch}/download", perm="다운로드")

# ── 001-P4 수강권 직권 부여 (개발 미구현, 규칙 기반 명명) ──────
NAME("grantUserId", "member_id", note="(규칙) users.id")
ALERT("회원 검색 팝업", flag="proto-only", note="회원 검색 — 개발 직권 부여 화면 없음")
NAME("grantProdCode", "product_id", note="(규칙) product_type · product_id")
NAME("grantPeriodDays", "course_days", note="(규칙)")
NAME("grantReason", "reason", note="(규칙) MemberReasonRequest")
ACT("submitDirectGrant", flag="proto-only", route="admin.orders.grants.store (규칙)", method="POST", url=A + "/orders/grants", perm="등록")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("배송 관리 view", "switchOrdView('ord002')", "#view-ord002"),
    ("주문 상세 view", "switchOrdView('ord001s1')", "#view-ord001s1"),
    ("반품 탭", "switchOrdView('ord002'); switchShipTab('RETURN')", "#shipTab-RETURN"),
    ("발주 확인 모달", "switchOrdView('ord002'); switchShipTab('READY'); document.querySelectorAll('.ship-cb').forEach((c, i) => c.checked = (i === 0)); updateShipToolbarButtons(); document.querySelector('#dispatchButton,#btn3plDownload').click()", "#layerDispatch|#modal3plConfirm"),
    ("P1 벌크 업로드", "switchOrdView('ord002'); document.getElementById('btnBulkWaybill').click()", "#layerImport|#modalBulkUpload"),
    ("P1 STEP 2", "switchOrdView('ord002'); document.getElementById('btnBulkWaybill').click(); switchP1Step(2)", "#p1Step2Box"),
    ("P2 단건", "switchOrdView('ord002'); switchShipTab('READY'); document.querySelectorAll('.ship-cb').forEach((c, i) => c.checked = (i === 0)); updateShipToolbarButtons(); document.querySelector('#trackingButton,#btnSingleWaybill').click()", "#layerTracking|#modalSingleWaybill"),
    ("P3 이력", "switchOrdView('ord002'); document.querySelector('#batchesButton,#btnBatchHistory').click()", "#layerBatches|#modalBatchHistory"),
    ("P4 직권 부여", "document.querySelector('[onclick^=openDirectGrantModal]').click()", "#modalDirectGrant"),
]
