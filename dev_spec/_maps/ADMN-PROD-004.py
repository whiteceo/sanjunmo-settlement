"""ADMN-PROD-004 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-004.md
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



def PROTO(id_, note, name=None):
    """프로토타입에만 있는 입력 — proto-only 표시"""
    R(f'id="{id_}"', f'id="{id_}"' + (f' name="{name}"' if name else "") + attrs(flag="proto-only", note=note), 1)


NL = "\n"  # apply_dev_map.py는 줄 끝을 LF로 맞춰 읽는다(원본은 CRLF에 LF 2줄 섞임 → 출력은 LF)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-PROD-004",
    "devCommit": DEV_COMMIT,
    "progress": "구현(목록 · 등록/수정 · 재고 조정 · 판매중지 · 재고 이력 레이어). 프로토 '교재 상세 조회' · 3-Way 가채번/공급원장 불러오기 · 3원장 신호등은 개발 미구현",
    "menus": [
        {"route": "admin.books.index", "label": "교재 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modal-stock-adjust", "layerStockAdjust", 3)
RENAME_ID("modal-autostop-confirm", "layerBookStop", 3)

# ── 상단 · 하위 화면 전환 ─────────────────────────────────
R('<div class="role-sim-box" title="ADMN-BOOK-001 공급원가 열람 권한 시뮬레이터">',
  '<div class="role-sim-box" title="ADMN-BOOK-001 공급원가 열람 권한 시뮬레이터"' + attrs(note="개발 역할 코드 finance(재무) 또는 최고 관리자만 사입 원가 열람 · 저장(AdminPermissionService::canManageCostPrice)") + '>')
R('data-view="list" onclick=', 'data-view="list"' + attrs(route="admin.books.index", method="GET", url=A + "/books", perm="조회") + ' onclick=')
R('data-view="detail" onclick=', 'data-view="detail" data-dev-flag="proto-only"' + attrs(route="admin.books.show (규칙)", method="GET", url=A + "/books/{book}", perm="조회",
                                                                                      note="교재 상세 조회 — 개발 미구현(행 클릭이 수정 폼, 재고 이력은 수정 화면 레이어 layerStockLogs)") + ' onclick=')
R('data-view="form" onclick=', 'data-view="form"' + attrs(route="admin.books.create | admin.books.edit", method="GET", url=A + "/books/create | /books/{book}/edit", perm="등록 | 수정") + ' onclick=')
R('<div class="book-pipeline-stepper">', '<div class="book-pipeline-stepper" data-dev-flag="proto-only" data-dev-note="도서 3원장 4단계 신호등 — 개발 없음">')
ACT("openNewBookForm", count=2, route="admin.books.create", method="GET", url=A + "/books/create", perm="등록")

# ── 004 목록 검색 ────────────────────────────────────
NAME("filter-cat", "category_id", note="자격증 종류(카테고리)")
PROTO("filter-origin", "등록 출발 경로(INST_TEMP · BOOK_LEDGER · PROD_DIRECT) — 개발 없음(Q-PROD004-4). 개발은 공급 형태 book_supply_type 필터")
NAME("filter-status", "display_status", value="selling · hidden · stopped — 예약판매 · 판매대기 · 일시품절 · 판매종료 없음(Q-PROD004-2)")
NAME("filter-stock", "stock_status", value="normal 정상 · low 임계치 이하 · soldout 품절 (프로토 LOW · ZERO)")
PROTO("filter-display", "노출 Y/N 분리 — 개발 없음(Q-PROD004-2)")
NAME("filter-keyword", "title", note="개발은 title · author · publisher · isbn 4칸 따로(SKU · 가채번 검색 없음)")
R('              <div class="filter-field filter-span-2">',
  '              <div class="filter-field" data-dev-flag="dev-only" data-dev-note="개발 book_supply_type 필터(BookSupplyService::SUPPLY_LABELS)">' + NL +
  '                <label>공급 형태</label>' + NL +
  '                <select name="book_supply_type" class="form-select"><option value="">전체</option><option value="OWN_PUBLISHED">자사 발행</option><option value="PURCHASED_RESALE">매입 재판매</option><option value="CONSIGNMENT">위탁</option><option value="BUNDLED">부속</option></select>' + NL +
  '              </div>' + NL +
  '              <div class="filter-field" data-dev-flag="dev-only" data-dev-note="개발 is_free · published_from · published_to · instructor_id 필터">' + NL +
  '                <label>판매 구분 · 발행일</label>' + NL +
  '                <div style="display:flex; gap:6px; align-items:center;">' + NL +
  '                  <select name="is_free" class="form-select" style="width:90px;"><option value="">전체</option><option value="0">유료</option><option value="1">무료</option></select>' + NL +
  '                  <input type="date" name="published_from" class="form-input">' + NL +
  '                  <input type="date" name="published_to" class="form-input">' + NL +
  '                </div>' + NL +
  '              </div>' + NL +
  '              <div class="filter-field filter-span-2">')
ACT("resetBookFilters", route="admin.books.index", method="GET", url=A + "/books", perm="조회")
ACT("renderBookList", route="admin.books.index", method="GET", url=A + "/books", perm="조회")

# ── 004 목록 ───────────────────────────────────────
R("<button type=\"button\" class=\"btn btn-outline\" onclick=\"showToast('교재 마스터 목록 CSV 다운로드가 완료되었습니다.')\">엑셀 다운로드 (CSV)</button>",
  '<button type="button" class="btn btn-outline"' + attrs(route="admin.books.download", method="GET", url=A + "/books/download", perm="다운로드", note="사유 레이어 layerReason(공통)")
  + " onclick=\"showToast('교재 마스터 목록 CSV 다운로드가 완료되었습니다.')\">엑셀 다운로드 (CSV)</button>" + NL +
  '              <button type="button" class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.books.selected.download", method="POST", url=A + "/books/download-selected", perm="다운로드",
                                                                                         note="체크한 행 ids[] + 사유") + '>선택 다운로드</button>')
R('<th class="text-center" style="width:46px;">No</th>',
  '<th class="text-center" style="width:36px;" data-dev-flag="dev-only"><input type="checkbox" id="checkAll" /></th>' + NL +
  '                    <th class="text-center" style="width:46px;">No</th>')
R('            <td class="text-center">${filtered.length - idx}</td>',
  '            <td class="text-center" data-dev-flag="dev-only" onclick="event.stopPropagation();"><input type="checkbox" class="check-item" name="ids[]" value="${b.sku}" /></td>' + NL +
  '            <td class="text-center">${filtered.length - idx}</td>')
R('<th style="width:110px;">교재 SKU / 가채번</th>', '<th style="width:110px;"' + attrs(name="code", note="개발 BK_00001 — 가채번 표시는 개발 없음") + '>교재 SKU / 가채번</th>')
R('<th style="width:135px;">등록 출발 경로</th>', '<th style="width:135px;" data-dev-flag="proto-only" data-dev-note="등록 출발 경로 — 개발 없음(Q-PROD004-4). 개발에는 공급 형태 컬럼">등록 출발 경로</th>')
R('<th style="width:95px;">저자 / 출판사</th>', '<th style="width:95px;"' + attrs(name="author · publisher", note="개발 2컬럼 + ISBN · 발행일 컬럼") + '>저자 / 출판사</th>')
R('<th class="text-right" style="width:95px;">정가(면세)</th>', '<th class="text-right" style="width:95px;"' + attrs(name="sale_price", note="개발 '판매가' (= 정가)") + '>정가(면세)</th>')
R('<th class="text-right" style="width:120px;">공급원가(BOOK-001)</th>', '<th class="text-right" style="width:120px;"' + attrs(name="cost_price", note="재무(finance) 역할만 컬럼 표시") + '>공급원가(BOOK-001)</th>')
R('<th class="text-center" style="width:215px;">3원장 연동 신호등 (계약·원가·매핑)</th>', '<th class="text-center" style="width:215px;" data-dev-flag="proto-only" data-dev-note="3원장 신호등 — 개발 없음. 개발에는 \'연결 상품 수\' 컬럼">3원장 연동 신호등 (계약·원가·매핑)</th>')
R('<th class="text-center" style="width:150px;">재고 (가용 / 실재고 · 예약)</th>', '<th class="text-center" style="width:150px;"' + attrs(name="stock · stock_status", note="v7.01 재고 2단 차감: 실재고 = books.stock, 예약 · 가용은 개발 없음 — reserved_stock (규칙) · available = stock − reserved_stock") + '>재고 (가용 / 실재고 · 예약)</th>')
R('id="d-stock-trio"', 'id="d-stock-trio" data-dev-flag="proto-only"' + attrs(note="실재고 · 예약 · 가용 3칸 — 개발은 books.stock 1칸. 예약(결제 완료 ~ 3PL 송장 업로드)은 개발 미구현, reserved_stock (규칙)"))
R('id="stock-hardlock-msg"', 'id="stock-hardlock-msg"' + attrs(note="가용 재고 기준 판매 잠금 — 개발은 stock 기준"))
R('<th class="text-center" style="width:105px;">판매상태</th>', '<th class="text-center" style="width:105px;"' + attrs(name="display_status") + '>판매상태</th>')
R('<th class="text-center" style="width:90px;">등록일</th>', '<th class="text-center" style="width:90px;" data-dev-flag="proto-only" data-dev-note="개발 목록에 등록일 없음">등록일</th>')
R('<tr onclick="selectBookForStepper(', '<tr data-dev-note="개발 행 클릭 → 수정 폼 · 신호등 갱신은 프로토만" onclick="selectBookForStepper(')
R('<a class="book-link" onclick="event.stopPropagation(); openBookDetail(',
  '<a class="book-link" data-dev-flag="proto-only" data-dev-route="admin.books.show (규칙)" onclick="event.stopPropagation(); openBookDetail(')
ACT("openBookDetail", flag="proto-only", route="admin.books.show (규칙)", method="GET", url=A + "/books/{book}", perm="조회")
R('<button type="button" class="btn btn-soft btn-sm" onclick="openBookEdit(\'${b.sku}\')">수정</button>',
  '<button type="button" class="btn btn-soft btn-sm" onclick="openBookEdit(\'${b.sku}\')">수정</button>' + NL +
  '                <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.books.copy.store", method="POST", url=A + "/books/{book}/copy", perm="등록", note="#actionForm") + '>복사</button>' + NL +
  '                <button type="button" class="btn btn-outline btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.books.destroy", method="DELETE", url=A + "/books/{book}", perm="삭제", note="#actionForm + #actionMethod") + '>삭제</button>')
ACT("openBookEdit", route="admin.books.edit", method="GET", url=A + "/books/{book}/edit", perm="수정")

# ── 프로토 004 상세(개발 미구현) ──────────────────────────
R('<section id="subview-detail" class="subview-panel">', '<section id="subview-detail" class="subview-panel" data-dev-flag="proto-only" data-dev-note="교재 상세 조회 — 개발 미구현(admin.books.show 규칙)">')
ACT("openStockAdjustModal", count=2, route="admin.books.edit", method="GET", url=A + "/books/{book}/edit", perm="수정", note="개발은 수정 화면의 재고 조정 레이어 layerStockAdjust")
ACT("editCurrentDetailBook", route="admin.books.edit", method="GET", url=A + "/books/{book}/edit", perm="수정")
R('<tbody id="detail-stock-log-tbody">', '<tbody id="detail-stock-log-tbody"' + attrs(note="개발 재고 이력 레이어 layerStockLogs (book_stock_logs: type · quantity · before_stock · after_stock · order_id · admin_id · memo)") + '>')

# ── 004-S1 등록 · 수정 ─────────────────────────────────
ACT("saveBookForm", route="admin.books.store | admin.books.update", method="POST | PUT", url=A + "/books | /books/{book}", perm="등록 | 수정", note="BookRequest")
ACT("selectEntryMode", count=3, flag="proto-only", note="3-Way 등록 출발 경로 — 개발 없음(Q-PROD004-4)")
R('onclick="event.stopPropagation(); openTempBookModal();"', 'data-dev-flag="proto-only" data-dev-route="admin.books.royalty-contracts.index (규칙)" onclick="event.stopPropagation(); openTempBookModal();"')
R('onclick="event.stopPropagation(); openSupplyLedgerModal();"', 'data-dev-flag="proto-only" data-dev-route="admin.books.supply-skus.index (규칙)" onclick="event.stopPropagation(); openSupplyLedgerModal();"')
R('id="f-sku"', 'id="f-sku"' + attrs(name="code", note="개발 서버 채번 BK_00001"))
PROTO("f-temp-code", "가채번 코드 — 개발 없음(Q-PROD004-4)")
ACT("openTempBookModal", flag="proto-only", route="admin.books.royalty-contracts.index (규칙)", method="GET", url=A + "/books/royalty-contracts", perm="조회")
NAME("f-cat", "category_id", note="2Depth만 · category_products 대표")
NAME("f-pub-date", "published_at")
R('                <tr>' + NL + '                  <th>교재명 <span class="req-star">*</span></th>',
  '                <tr data-dev-flag="dev-only" data-dev-note="개발 cert_category_ids[](1Depth 복수) · edition · book_size · page_count">' + NL +
  '                  <th>자격증 종류</th>' + NL +
  '                  <td>' + NL +
  '                    <select name="cert_category_ids[]" class="form-select" style="width:220px;" multiple size="2"><option value="산업안전기사">산업안전기사</option><option value="건설안전기사">건설안전기사</option></select>' + NL +
  '                  </td>' + NL +
  '                  <th>판쇄 · 판형 · 페이지</th>' + NL +
  '                  <td>' + NL +
  '                    <div style="display:flex; gap:6px;">' + NL +
  '                      <input type="text" name="edition" class="form-input" style="width:90px;" placeholder="판쇄">' + NL +
  '                      <input type="text" name="book_size" class="form-input" style="width:90px;" placeholder="판형">' + NL +
  '                      <input type="number" name="page_count" class="form-input" style="width:90px;" placeholder="페이지">' + NL +
  '                    </div>' + NL +
  '                  </td>' + NL +
  '                </tr>' + NL +
  '                <tr>' + NL + '                  <th>교재명 <span class="req-star">*</span></th>')
NAME("f-title", "title", note="required · max 255")
PROTO("f-subtitle", "부제 — 개발 없음")
NAME("f-author", "author", note="required · max 100 (book_authors)")
NAME("f-author-inst", "instructors[0][instructor_id]", note="개발 #instructorRows — instructors[n][instructor_id] · [role] m · s · a")
NAME("f-publisher", "publisher")
NAME("f-isbn", "isbn", note="개발 #isbn · #isbnFormat — 부속(BUNDLED) 외 required · 전체 유일 · 형식 검사(서버 isbnRule)")
ACT("validateIsbnField", flag="proto-only", note="ISBN 검증 버튼 — 개발은 서버 검증만")
R('                <tr>' + NL + '                  <th>도서 정가 <span class="req-star">*</span></th>',
  '                <tr data-dev-flag="dev-only" data-dev-note="개발 #isFree toggleFreeBook() — 등록 때만, 1이면 가격 0 · 도서정가제 제외">' + NL +
  '                  <th>판매 구분</th>' + NL +
  '                  <td colspan="3">' + NL +
  '                    <label class="option-label"><input type="checkbox" name="is_free" value="1"><span>무료 도서</span></label>' + NL +
  '                  </td>' + NL +
  '                </tr>' + NL +
  '                <tr>' + NL + '                  <th>도서 정가 <span class="req-star">*</span></th>')
NAME("f-list-price", "original_price", note="등록 때만 — 수정은 BOOK-001 정가 이력(admin.book-supply.prices.update)")
R('id="f-book-discount-rate"', 'id="f-book-discount-rate"' + attrs(note="개발 교재별 할인율 칸 없음 — 판매가 직접 입력 + site_settings.book_discount_rate_limit(기본 0%) 검증(Q-PROD004-3)"))
NAME("f-sale-price", "sale_price", note="등록 때만 · ≤ 정가 · 정가 × (1 − 한도%) 이상")
R('<span class="badge badge-info">기본 3,000원 · 도서/상품 실결제 30,000원 이상 무료배송</span>',
  '<span class="badge badge-info">기본 3,000원 · 도서/상품 실결제 30,000원 이상 무료배송</span>' + NL +
  '                    <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:6px;" data-dev-flag="dev-only" data-dev-note="개발 교재별 배송 정책 delivery_fee · is_free_delivery · free_delivery_threshold · island_delivery_fee · return_delivery_fee · package_bundled_yn">' + NL +
  '                      <input type="number" name="delivery_fee" class="form-input text-right" style="width:100px;" placeholder="배송비">' + NL +
  '                      <input type="number" name="free_delivery_threshold" class="form-input text-right" style="width:120px;" placeholder="무료 기준금액">' + NL +
  '                      <input type="number" name="island_delivery_fee" class="form-input text-right" style="width:110px;" placeholder="도서산간">' + NL +
  '                      <input type="number" name="return_delivery_fee" class="form-input text-right" style="width:110px;" placeholder="반품 배송비">' + NL +
  '                      <label class="option-label"><input type="checkbox" name="is_free_delivery" value="1"><span>무조건 무료</span></label>' + NL +
  '                      <label class="option-label"><input type="checkbox" name="package_bundled_yn" value="1"><span>패키지 동봉</span></label>' + NL +
  '                    </div>')
R('id="f-supply-ledger"', 'id="f-supply-ledger"' + attrs(name="book_supply_type", value="OWN_PUBLISHED · PURCHASED_RESALE · CONSIGNMENT · BUNDLED",
                                                         note="개발 교재 폼에서 받지 않음(LEDGER_OWNED_KEYS) — 🔒 표시 + BOOK-001(admin.book-supply.edit)에서 지정(Q-PROD004-4)"))
R('id="f-supply-vendor"', 'id="f-supply-vendor"' + attrs(name="supplier_id", note="BOOK-001 소관"))
NAME("f-is-preorder", "is_preorder")
NAME("f-release-date", "release_date", note="DB 컬럼만 — 개발 폼 입력칸 없음(restock_date만 있음)")
NAME("f-stock-qty", "stock", note="등록 때만 required — 이후 재고 조정(admin.books.stock.update)으로만")
ACT("setZeroStockDemo", flag="proto-only", note="재고 0권 하드락 시뮬레이션 — 개발은 재고 0이면 전시와 별개로 품절 처리")
NAME("f-safe-stock", "stock_alert_qty")
DEVNAME('id="radio-book-sale" value="판매중"', "display_status", value="selling")
R('id="radio-book-preorder" value="예약판매"', 'id="radio-book-preorder" value="예약판매" data-dev-name="is_preorder" data-dev-value="1 (+ display_status selling)" data-dev-note="개발은 판매 상태가 아니라 is_preorder 플래그"')
R('id="radio-book-ready" value="판매대기"', 'id="radio-book-ready" value="판매대기" data-dev-flag="proto-only" data-dev-note="판매대기(원장 매핑 대기) — 개발 없음(Q-PROD004-2)"')
R('id="radio-book-out" value="일시품절"', 'id="radio-book-out" value="일시품절" data-dev-flag="proto-only" data-dev-note="일시품절 — 개발은 상태값이 아니라 재고 0 파생 품절(soldout)"')
DEVNAME('id="radio-book-pause" value="판매중지"', "display_status", value="stopped", note="개발은 [판매중지] 레이어 layerBookStop(admin.books.stop.update)으로도 전환")
R('id="radio-book-end" value="판매종료"', 'id="radio-book-end" value="판매종료" data-dev-flag="proto-only" data-dev-note="판매종료(구판 · 절판) — 개발 없음(Q-PROD004-2)"')
R('name="f-book-display" value="Y"', 'name="f-book-display" value="Y" data-dev-name="display_status" data-dev-note="노출 분리 — 개발은 display_status 1칸(Q-PROD004-2)"')
R('name="f-book-display" value="N"', 'name="f-book-display" value="N" data-dev-name="display_status" data-dev-value="hidden"')
R("onclick=\"showToast('표지 이미지 업로드 창 호출')\"",
  attrs(name="thumbnail", note="개발 #thumbnailSelector — jpg/png/webp · 5MB · 700×980 이상 · 5:7, 삭제 delete_thumbnail").lstrip() + " onclick=\"showToast('표지 이미지 업로드 창 호출')\"")
R("onclick=\"showToast('미리보기 PDF 업로드 (최대 20MB)')\"",
  attrs(name="preview_images[]", note="개발은 미리보기 이미지 여러 장(#previewSelector, 5MB) — PDF 아님").lstrip() + " onclick=\"showToast('미리보기 PDF 업로드 (최대 20MB)')\"")
R('                <tr>' + NL + '                  <th>교재 목차 및 상세 소개 <span class="req-star">*</span></th>',
  '                <tr data-dev-flag="dev-only" data-dev-note="개발 detail_images[] (#detailSelector) · table_of_contents(목차 별도 칸)">' + NL +
  '                  <th>상세 이미지</th>' + NL +
  '                  <td>' + NL +
  '                    <input type="file" name="detail_images[]" class="form-input" style="width:320px;" accept="image/*" multiple>' + NL +
  '                  </td>' + NL +
  '                  <th>목차</th>' + NL +
  '                  <td>' + NL +
  '                    <textarea name="table_of_contents" class="form-textarea" rows="2" placeholder="목차"></textarea>' + NL +
  '                  </td>' + NL +
  '                </tr>' + NL +
  '                <tr>' + NL + '                  <th>교재 목차 및 상세 소개 <span class="req-star">*</span></th>')
NAME("f-book-desc", "description", note="개발은 description · table_of_contents 2칸")

# ── 모달 ──────────────────────────────────────────
R('<div class="modal-backdrop" id="modal-temp-book">', '<div class="modal-backdrop" id="modal-temp-book" data-dev-flag="proto-only" data-dev-note="가채번 도서 불러오기 — 개발 미구현(book_royalty_contracts 원장 필드만)">')
R('<div class="modal-backdrop" id="modal-supply-sku">', '<div class="modal-backdrop" id="modal-supply-sku" data-dev-flag="proto-only" data-dev-note="공급원장 SKU 불러오기 — 개발 미구현(등록 후 BOOK-001에서 공급 형태 지정)">')
ACT("applyTempBookSelection", count=2, flag="proto-only")
ACT("applySupplySkuSelection", count=2, flag="proto-only")
NAME("modal-stock-type", "type", value="in 입고 · return_in 반품 입고 · disposal 파본 폐기 · audit 실사 조정 (이력 전용 order_out · order_restore)")
R('<option value="입고(+)">', '<option value="입고(+)" data-dev-value="in">')
R('<option value="반품입고(+)">', '<option value="반품입고(+)" data-dev-value="return_in">')
R('<option value="파손차감(-)">', '<option value="파손차감(-)" data-dev-value="disposal">')
R('<option value="실사조정(-)">', '<option value="실사조정(-)" data-dev-value="audit">')
NAME("modal-stock-qty", "quantity", note="정수 ≠ 0 (음수 = 차감)")
NAME("modal-stock-reason", "memo", note="개발 nullable · max 255 (프로토는 필수)")
ACT("confirmStockAdjust", route="admin.books.stock.update", method="PUT", url=A + "/books/{book}/stock", perm="수정")
R('<div class="modal-title" id="autostop-title">', '<div class="modal-title" id="autostop-title"' + attrs(note="개발 layerBookStop은 '패키지 N건의 판매 가능 상태가 깨집니다' 표시만 — 강좌 · 패키지 자동 판매중지는 개발 없음(Q-PROD004-1)") + '>')
ACT("confirmAutoStop", route="admin.books.stop.update", method="POST", url=A + "/books/{book}/stop-selling", perm="수정",
    note="개발은 교재만 stopped로 바꿈(연결 상품 자동 판매중지 없음, Q-PROD004-1)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchSubview('list')", "#subview-list"),
    ("목록 행", "switchSubview('list'); renderBookList()", "#book-list-tbody tr"),
    ("상세 view", "openBookDetail('PROD-BK-1011')", "#subview-detail"),
    ("상세 재고 이력", "openBookDetail('PROD-BK-1011')", "#detail-stock-log-tbody"),
    ("수정 view", "openBookEdit('PROD-BK-1011')", "#subview-form"),
    ("신규 view", "openNewBookForm()", "#f-title"),
    ("경로 2 선택", "openNewBookForm(); selectEntryMode('BOOK_LEDGER')", "#entry-card-BOOK_LEDGER"),
    # 재고 · 가채번 · 공급원장 모달은 clean 원본에서도 열리지 않아(open 클래스만 붙이고 인라인 display:none 유지) 검증에서 뺐다 — 원본 문제로 보고
    ("판매종료 잠금", "openBookEdit('PROD-BK-1011'); syncEndOfSaleLock()", "#subview-form"),
]
