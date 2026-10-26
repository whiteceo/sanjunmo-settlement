"""ADMN-PROD-007 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROD-007.md
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
    "code": "ADMN-PROD-007",
    "devCommit": DEV_COMMIT,
    "progress": "구현(목록 · 등록 · 수정 · 판매중지 · 일괄 판매중지 · 재고 조정 · 입출고 이력 · 엑셀). 판매대기 · 판매종료 · P2 기간 · 구분 필터 · 조정 후 재고 미리보기는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.goods.index", "label": "상품 마스터(추정)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modal-stock-p1", "layerGoodsStockAdjust", 5)
RENAME_ID("modal-stock-p2", "layerGoodsStockLogs", 4)

# ── 007 목록 ───────────────────────────────────────
R('id="chk-fin-role"', 'id="chk-fin-role" data-dev-flag="proto-only" data-dev-note="재무 권한 시연 토글 — 개발은 AdminPermissionService::canManageCostPrice() 실제 권한"')
ACT("filterStock", count=4, route="admin.goods.index", method="GET", url=A + "/goods", perm="조회",
    note="스코어카드(전체 · 판매중 · 재고 임박 · 품절) 클릭 → sale_status · stock_status 필터")
NAME("fl-supply", "goods_supply_type", value="PURCHASED_RESALE · DIRECT_SALE ('전체' ALL → 빈 값)")
NAME("fl-status", "sale_status", value="selling · stopped · soldout(재고 파생) — 판매대기 · 판매종료는 개발 없음(정책 질문 Q-PROD007-1)")
NAME("fl-stock", "stock_status", value="normal · low · soldout (프로토 NORMAL · LOW · OUT)")
NAME("fl-kw", "keyword", note="상품명 · GDS 코드, 100자")
ACT("resetSearch", note="개발은 /goods 로 이동(조건 제거)")
ACT("renderTable", route="admin.goods.index", method="GET", url=A + "/goods", perm="조회", note="30건 고정 페이지, 정렬 파라미터 없음")
ACT("bulkStopSale", route="admin.goods.bulk-stop.update", method="POST", url=A + "/goods/bulk-stop", perm="수정",
    note="ids[] 1~500 — 개발 bulkStop · bulkStopForm")
R('id="btn-excel" onclick="showToast(', 'id="btn-excel"' + attrs(route="admin.goods.download", method="GET", url=A + "/goods/download", perm="다운로드 + 재무 권한",
                                                                note="사유 레이어 layerReason") + ' onclick="showToast(')
ACT("openForm", count=3, route="admin.goods.create | admin.goods.edit", method="GET", url=A + "/goods/create | /goods/{goods}/edit", perm="등록 | 수정",
    note="개발 행 클릭 tr[data-href] → 수정")
R('<th style="width:36px;"><input type="checkbox" onchange="document.querySelectorAll(\'.g-chk\')',
  '<th style="width:36px;"><input type="checkbox" id="checkAll" onchange="document.querySelectorAll(\'.g-chk\')')
R('<input type="checkbox" class="g-chk" value="${g.id}" />', '<input type="checkbox" class="g-chk" name="ids[]" data-bulk-check value="${g.id}" />')
ACT("openStockAdjustModal", count=3, route="admin.goods.edit", method="GET", url=A + "/goods/{goods}/edit", perm="수정",
    note="개발 P1은 수정 화면 안 레이어(.layer__open[data-target=layerGoodsStockAdjust]) — 목록에서 바로 여는 버튼은 개발 없음")
ACT("openStockHistoryModal", count=3, route="admin.goods.edit", method="GET", url=A + "/goods/{goods}/edit", perm="수정",
    note="개발 P2는 수정 폼에 함께 실린 stockLogs를 레이어에 그림")

# ── 007-S1 등록 · 수정 ───────────────────────────────
R('id="f-id"', 'id="f-id"' + attrs(name="code", note="저장 후 GDS-%04d(id) 자동 채번 — 입력 칸 아님"))
NAME("f-supply", "goods_supply_type", note="판매 이력 있으면 변경 불가(서버 차단, 폼 disabled + hidden)")
NAME("f-name", "name", note="max 255")
NAME("f-cat", "category_id", note="nullable — category_products 다형 매핑")
NAME("f-status", "display_status", value="selling 판매중 · stopped 판매중지 — 판매대기 · 판매종료는 개발 없음(정책 질문 Q-PROD007-1)")
NAME("f-price", "sale_price", note="정수 0~100,000,000 — 개발 id salePrice")
R('id="f-vat-split"', 'id="f-vat-split"' + attrs(note="개발 #vatSplit 표시만, Goods::splitVat 반올림(프로토 FLOOR — 정책 질문 Q-PROD007-2)"))
NAME("f-cost", "cost_price", note="재무 권한 아니면 무시, DIRECT_SALE이면 null — 개발 id costPrice")
R('id="f-stock"', 'id="f-stock"' + attrs(name="stock", note="개발 수정 폼은 stock 직접 입력(이력 없이 덮어씀) — 프로토는 조정 레이어로만(정책 질문 Q-PROD007-3)"))
NAME("f-threshold", "stock_alert_qty", note="개발 nullable(정책 질문 Q-PROD007-5)")
NAME("f-supplier", "supplier_id", note="PURCHASED_RESALE이면 필수 — 개발 id supplierId")
R('<option value="SELF">해당 없음 (자사 직접 제작)</option>\n                    </select>',
  '<option value="SELF">해당 없음 (자사 직접 제작)</option>\n                    </select>\n'
  '                    <span id="supplierStatus" class="badge badge-gray" style="margin-left:6px;" data-dev-flag="dev-only" data-dev-note="매입처 option data-status → 사업 상태 표시">사업 상태: 정상</span>')
R('<button type="button" class="btn btn-sm btn-outline">파일 변경</button>',
  '<button type="button" class="btn btn-sm btn-outline"' + attrs(name="thumbnail", note="등록 필수 · 수정 선택, jpg · jpeg · png · webp, 5MB") + '>파일 변경</button>')
NAME("f-desc", "description", note="65,535바이트 · Purifier")
ACT("stopCurrentProduct", route="admin.goods.stop.update", method="POST", url=A + "/goods/{goods}/stop-selling", perm="수정",
    note="개발 goodsStop · goodsStopForm. 삭제 라우트 없음(주문 참조)")
ACT("saveProductForm", route="admin.goods.store | admin.goods.update", method="POST | PUT", url=A + "/goods | /goods/{goods}", perm="등록 | 수정",
    note="GoodsRequest — 개발 폼 id goodsForm")

# ── 007-P1 재고 조정 ─────────────────────────────────
NAME("p1-dir", "(quantity 부호)", note="개발은 quantity 부호 있는 정수 1칸(음수 = 차감)")
NAME("p1-qty", "quantity", note="not 0, 결과 재고 < 0이면 거부")
NAME("p1-reason", "type", value="inbound 입고 · restore 복구 · adjust 수기 조정 · damaged 파손 · lost 분실 — 프로토 목록과 다름(정책 질문 Q-PROD007-4)")
NAME("p1-memo", "memo", note="개발 선택 · 255자")
R('id="p1-after-stock"', 'id="p1-after-stock" data-dev-flag="proto-only" data-dev-note="조정 후 재고 미리보기 — 개발 없음"')
ACT("confirmStockAdjust", route="admin.goods.stock.update", method="PUT", url=A + "/goods/{goods}/stock", perm="수정")

# ── 007-P2 입출고 이력 ───────────────────────────────
R('<input type="date" class="f-input" value="2026-09-17" /> ~ <input type="date" class="f-input" value="2026-10-17" />',
  '<input type="date" class="f-input" name="date_from" value="2026-09-17" data-dev-flag="proto-only" data-dev-note="(규칙) admin.goods.stock-logs.index — 개발 미구현" /> ~ '
  '<input type="date" class="f-input" name="date_to" value="2026-10-17" data-dev-flag="proto-only" />')
R('id="p2-filter-type"', 'id="p2-filter-type"' + attrs(flag="proto-only", name="type", value="outbound 판매 출고 · restore 복구 · adjust 수기 조정 …",
                                                       route="admin.goods.stock-logs.index (규칙)", method="GET", url=A + "/goods/{goods}/stock-logs", perm="조회"))
R('onclick="showToast(\'입출고 원장(goods_stock_log) 엑셀 다운로드가 완료되었습니다.\')"',
  'data-dev-flag="proto-only" data-dev-note="입출고 이력 엑셀 — 개발 없음" onclick="showToast(\'입출고 원장(goods_stock_log) 엑셀 다운로드가 완료되었습니다.\')"')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 view", "switchView('list')", "#view-list"),
    ("등록 view", "openForm('NEW')", "#view-form"),
    ("수정 view", "openForm('GDS-0001')", "#view-form"),
    # 모달은 버튼 클릭으로 연다(공통 핫픽스가 클릭 때만 인라인 display:none을 푼다)
    ("P1 재고 조정(목록)", "document.querySelector('#view-list [onclick^=\"openStockAdjustModal\"]').click()", "#layerGoodsStockAdjust|#modal-stock-p1"),
    ("P2 입출고 이력(목록)", "document.querySelector('#view-list [onclick^=\"openStockHistoryModal\"]').click()", "#layerGoodsStockLogs|#modal-stock-p2"),
    ("P1 재고 조정(수정 화면)", "openForm('GDS-0002'); document.getElementById('btn-form-p1').click()", "#layerGoodsStockAdjust|#modal-stock-p1"),
]
