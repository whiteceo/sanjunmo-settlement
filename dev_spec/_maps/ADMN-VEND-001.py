"""ADMN-VEND-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-VEND-001.md
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
    "code": "ADMN-VEND-001",
    "devCommit": DEV_COMMIT,
    "progress": "독립 화면 개발 미구현 — 이름은 (규칙). 가장 가까운 구현: 도서 공급 원장 매입처 탭(admin.book-supply.index ?tab=suppliers) + 매입처 등록(admin.book-supply.suppliers.store). 유형 관리 · 수정 · 거래 중지 · 국세청 조회는 주황 표시",
    "menus": [
        {"route": "admin.vendors.index (규칙)", "label": "거래처 관리"},
        {"route": "admin.book-supply.index", "label": "도서 공급 원장(매입처 탭 ③ — 개발 구현분)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

B = A + "/vendors"

# ── 모달 id → 개발 레이어 id(규칙) ───────────────────────
RENAME_ID("modal-vendor", "layerVendor", 5)
RENAME_ID("modal-type", "layerVendorType", 4)

# ── 목록 ────────────────────────────────────────────
NAME("flt-type", "type", note="(규칙) vendor_type_id")
NAME("flt-status", "status", value="active 거래 중 · suspended 거래 중지 (규칙, 프로토타입 값 ON · OFF 유지)")
NAME("flt-keyword", "keyword")
ACT("openTypeModal", flag="proto-only", route="admin.vendors.types.index (규칙)", method="GET", url=B + "/types", perm="조회", note="거래처 유형 테이블 없음 — 규칙상 vendor_types")
ACT("openVendorModal", count=2, note="null = 등록, id = 수정. 수정은 개발 라우트 없음(admin.vendors.update (규칙) PUT /vendors/{vendor})")

# ── 거래처 등록 · 수정 모달 ─────────────────────────────
NAME("vf-type", "vendor_type_id", note="(규칙)")
NAME("vf-id", "code", note="SUP-%04d 자동 채번(개발 SupplierService와 같은 방식)")
NAME("vf-name", "name", note="SupplierRequest ≤100")
NAME("vf-biz", "business_no", note="digits:10 · 중복 불가")
ACT("checkNts", flag="proto-only", route="admin.vendors.nts-verify (규칙)", method="POST", url=B + "/{vendor}/nts-verify", perm="수정(nts-verify 접미사)",
    note="개발 매입처 탭 '사업자 확인' 버튼은 disabled(준비 중) — 등록 시 business_status PENDING_VERIFICATION")
NAME("vf-ceo", "ceo_name")
R('id="vf-tax"', 'id="vf-tax"' + attrs(name="payee_tax_type", flag="proto-only", note="과세유형 직접 선택 — 개발은 입력받지 않고 국세청 응답으로만 채움(정책 질문 D-SETT)"))
NAME("vf-contact", "contact_email", note="개발은 담당 메일(email) — 프로토타입은 연락처")
NAME("vf-since", "started_at", note="(규칙) 거래 시작일 — 개발 매입처는 개업일자 open_date")
R('<div class="form-row"><label>거래 조건</label><div id="vf-terms"></div></div>',
  '<div class="form-row" data-dev-flag="dev-only" data-dev-note="개발 SupplierRequest open_date · bank_name · account_no(암호화 저장 · 마스킹) · account_holder · cost_account_type">'
  '<label>개업일자 · 계좌</label><div style="display:flex; flex-direction:column; gap:8px;">'
  '<div style="display:flex; gap:8px;"><input class="f-input" type="date" name="open_date" style="width:160px;" title="개업일자" />'
  '<select class="f-select" name="cost_account_type"><option value="INVENTORY_PURCHASE">재고자산 취득</option><option value="BUYOUT_RIGHT">무형 판권 취득</option></select></div>'
  '<div style="display:flex; gap:8px;"><input class="f-input" name="bank_name" style="width:140px;" placeholder="은행" />'
  '<input class="f-input" name="account_no" style="width:200px;" placeholder="계좌번호 (숫자 · -)" />'
  '<input class="f-input" name="account_holder" style="width:140px;" placeholder="예금주" /></div></div></div>\n'
  '        <div class="form-row"><label>거래 조건</label><div id="vf-terms"' + attrs(name="settlement_terms", note="개발은 지급 조건 문자열 한 칸(≤100) — 프로토타입 구조화 입력(vt-rate 등)") + '></div></div>')
# v6.92: 매입 거래 조건 '반품 조건' 칸 추가(D-PTNR3-03 결정 반영) — 개발은 settlement_terms 문자열 한 칸뿐
NAME("vt-ret-cond", "return_terms", note="(규칙) 반품(반출) 조건 — 파본 · 인쇄 불량은 반출, 그 밖의 반품은 이 조건이 있을 때만(D-PTNR3-03). 개발 suppliers 칸 없음")
NAME("vf-susp-ok", "suspend_approved", value="1", note="(규칙) 재무 책임자 승인")
NAME("vf-susp-reason", "suspend_reason", note="(규칙)")
DEVNAME('name="vf-on" value="ON"', "status", value="active (규칙)")
DEVNAME('name="vf-on" value="OFF"', "status", value="suspended (규칙)", note="거래 상태 칸 개발 없음 — business_status 기반 발주 가능 / 신규 발주 차단")
ACT("saveVendor", route="admin.book-supply.suppliers.store", method="POST", url=A + "/book-supply/suppliers", perm="등록(도서 공급 원장 메뉴)",
    note="개발 구현분은 매입처 등록만(#supplierForm). 거래처 관리 경로는 admin.vendors.store | admin.vendors.update (규칙) — 수정 라우트 없음")
R('onclick="saveVendor()"', 'id="vendorSubmit" onclick="saveVendor()"')

# ── 거래처 유형 관리 ─────────────────────────────────
NAME("nt-name", "name", note="(규칙) vendor_types.name")
NAME("nt-form", "terms_form", value="purchase · logistics · general (규칙, 프로토타입 값 PURCHASE · LOGISTICS · GENERAL 유지)")
NAME("nt-evidence", "evidence_type", value="tax_invoice 전자세금계산서 · invoice 전자계산서 (규칙)")
ACT("addType", flag="proto-only", route="admin.vendors.types.store (규칙)", method="POST", url=B + "/types", perm="등록")
R("onchange=\"setTypeStatus(", attrs(flag="proto-only", route="admin.vendors.types.update (규칙)", method="PUT", url=B + "/types/{type}", perm="수정").lstrip() + " onchange=\"setTypeStatus(")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("거래처 등록 모달", "openVendorModal(null)", "#layerVendor|#modal-vendor"),
    ("거래처 수정 모달", "openVendorModal('SUP-0020')", "#layerVendor|#modal-vendor"),
    ("거래처 유형 모달", "openTypeModal()", "#layerVendorType|#modal-type"),
    ("상태 필터", "document.getElementById('flt-status').value='OFF'; renderVendors()", "#flt-status"),
]
