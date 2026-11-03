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
# 3PL 화면 반영(초안, 기능 정의 초안 2 F5): 거래처 유형은 suppliers.type (규칙) — 프로토타입 값은 유형 코드 VT-xx 유지
TYPE_VALUES = "book_supplier 도서 공급사(VT-01) · warehouse 보관 창고(VT-03) · courier 배송사(VT-04) (규칙, suppliers.type) — 상품 매입처(VT-02)는 굿즈 범위 결정(정책질문 28번) 뒤"
NAME("flt-type", "type", value=TYPE_VALUES, note="(규칙) suppliers.type — 이전 이름 vendor_type_id")
NAME("flt-status", "status", value="active 거래 중 · suspended 거래 중지 (규칙, 프로토타입 값 ON · OFF 유지)")
NAME("flt-keyword", "keyword")
ACT("openTypeModal", flag="proto-only", route="admin.vendors.types.index (규칙)", method="GET", url=B + "/types", perm="조회", note="거래처 유형 테이블 없음 — 규칙상 vendor_types")
ACT("openVendorModal", count=2, note="null = 등록, id = 수정. 수정은 개발 라우트 없음(admin.vendors.update (규칙) PUT /vendors/{vendor})")

# ── 거래처 등록 · 수정 모달 ─────────────────────────────
NAME("vf-type", "type", value=TYPE_VALUES, note="(규칙) suppliers.type — 이전 이름 vendor_type_id. 보관 창고일 때만 단가 · 운영 연락처 · 메일 참조 칸")
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

# ── 3PL 화면 반영(초안, 기능 정의 초안 2 F5 · SCREEN_3PL.md) ────────────────
# 거래처 유형 3종(도서 공급사 · 보관 창고 · 배송사), 보관 창고만 배송 · 회수 단가 · 운영 연락처 · 메일 참조, 1차 보관 창고 1곳만 활성.
# 유형 · 거래처 최초값은 공통 common-master.js(SJM_MASTER)에 있다 — 공통 파일은 고치지 않고 이 화면 안에서만 덧씌운다.
# 저장은 dev 전용 저장소 키(sjm.dev.vend3pl.v1) — prototype_clean 화면의 sjm.master.* 값과 섞이지 않게.
R('''    const M = window.SJM_MASTER;
    const NOW''', '''    // (dev 3PL 초안) 공통 SJM_MASTER 위에 거래처 유형 3종 · 보관 창고 정보 · 샘플을 이 화면 안에서만 덧씌운다
    const M0 = window.SJM_MASTER;
    const DEV_KEY = 'sjm.dev.vend3pl.v1';
    const DEV_TYPE_PATCH = { 'VT-01': { name: '도서 공급사', kind: 'book_supplier' }, 'VT-03': { kind: 'warehouse' } }; // VT-03 이름 '보관 창고'는 공통 최초값(2026-11-04)
    const DEV_TYPE_ADD = [{ id: 'VT-04', name: '배송사', kind: 'courier', form: 'GENERAL', evidence: '전자세금계산서(과세)', on: true, order: 4 }];
    // 1차 보관 창고는 대영물류 1곳 — 이전 샘플 CJ대한통운 파주 물류센터는 거래 중지로 둔다
    const DEV_VENDOR_PATCH = { 'SUP-0020': { on: false } };
    const DEV_VENDOR_ADD = [
      { id: 'SUP-0021', type: 'VT-01', name: '오스틴북스', bizNo: '999-99-00021', ceo: '[대표자]', taxType: '일반과세', status: '계속', checkedAt: '2026-11-04', on: true,
        terms: { rate: '', pay: '[결제 조건 — 계약 후 입력]' }, contact: '[연락처]', since: '2026-11-01' },
      { id: 'SUP-0022', type: 'VT-03', name: '대영물류', bizNo: '999-99-00022', ceo: '[대표자]', taxType: '일반과세', status: '계속', checkedAt: '2026-11-04', on: true,
        terms: { outFee: '2000', returnFee: '4000', storage: '', cycle: '월 1회 (익월 초 명세서)', opsContact: '낭주특송 [담당자 이름 · 연락처]', mailCc: '오스틴북스 [메일 주소]' }, contact: '[연락처]', since: '2026-11-01' },
      { id: 'SUP-0023', type: 'VT-04', name: '낭주특송', bizNo: '999-99-00023', ceo: '[대표자]', taxType: '일반과세', status: '계속', checkedAt: '2026-11-04', on: true,
        terms: { memo: '출고 · 회수 운송 — 롯데택배 위탁' }, contact: '[연락처]', since: '2026-11-01' }
    ];
    const devLoad = () => { try { return JSON.parse(localStorage.getItem(DEV_KEY) || 'null') || {}; } catch (e) { return {}; } };
    const devSave = (k, v) => { try { const s = devLoad(); s[k] = JSON.parse(JSON.stringify(v)); localStorage.setItem(DEV_KEY, JSON.stringify(s)); } catch (e) {} };
    const devTypes = () => devLoad().types || M0.vendors.types().map(t => Object.assign({}, t, DEV_TYPE_PATCH[t.id] || {})).concat(DEV_TYPE_ADD.filter(a => !M0.vendors.type(a.id)));
    const devVendors = () => devLoad().vendors || M0.vendors.list().map(v => Object.assign({}, v, DEV_VENDOR_PATCH[v.id] || {})).concat(DEV_VENDOR_ADD.filter(a => !M0.vendors.get(a.id)));
    const devMaxNo = arr => Math.max(0, ...arr.map(x => parseInt(String(x.id).split('-')[1], 10) || 0));
    const M = { vendors: {
      types: () => devTypes().sort((a, b) => (a.order || 0) - (b.order || 0)),
      activeTypes: () => M.vendors.types().filter(t => t.on),
      type: id => devTypes().find(t => t.id === id) || null,
      list: () => devVendors(),
      get: id => devVendors().find(v => v.id === id) || null,
      name: id => (M.vendors.get(id) || {}).name || id,
      byType: id => devVendors().filter(v => v.type === id),
      save: list => devSave('vendors', list),
      saveTypes: list => devSave('types', list),
      nextId: () => 'SUP-' + String(devMaxNo(devVendors()) + 1).padStart(4, '0'),
      nextTypeId: () => 'VT-' + String(devMaxNo(devTypes()) + 1).padStart(2, '0')
    } };
    const NOW''')

# 머리 · 안내 문구 — 용어: 도서 공급사 · 보관 창고 · 배송사 (원본의 '3PL' 제거는 2026-11-04 prototype_clean에 반영)
R('거래처 관리 (매입처 · 물류 대행사 · 공급 파트너)', '거래처 관리 (도서 공급사 · 보관 창고 · 배송사 · 매입처)')
R('도서 · 상품 매입처, 물류 업체(보관 창고 · 배송사), 이후 생기는 공급 파트너.',
  '도서 공급사 · 상품 매입처, 물류를 맡는 보관 창고 · 배송사, 이후 생기는 공급 파트너. 1차 보관 창고는 1곳만 거래 중으로 둡니다.')

# 거래 조건 — 보관 창고(물류 대행 양식)일 때만 배송 · 회수 단가 · 운영 연락처 · 메일 참조
WH_LABEL = 'style="font-size:11.5px; color:var(--text-sub); font-weight:700; margin-bottom:2px;"'
R('''html = `<div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:8px;"><input class="f-input" id="vt-out" type="number" placeholder="출고 건당 단가(원)" value="${x.outFee || ''}" /><input class="f-input" id="vt-ret" type="number" placeholder="반품 회수 단가(원)" value="${x.returnFee || ''}" /><input class="f-input" id="vt-sto" type="number" placeholder="월 보관료(원)" value="${x.storage || ''}" /><input class="f-input" id="vt-cycle" placeholder="정산 주기" value="${x.cycle || '월 1회 (익월 초 명세서)'}" /></div><div class="form-help">물류비 대사(ADMN-SETT-011)가 이 단가로 물류 업체 청구를 검수합니다.</div>`;''',
  '''html = `<div id="vt-wh" style="display:grid; grid-template-columns:repeat(2, 1fr); gap:8px;">'''
  f'''<div><div {WH_LABEL}>배송 건당 단가(원) *</div><input class="f-input" id="vt-out" type="number" style="width:100%;" placeholder="배송 건당 단가(원)" value="${{x.outFee || ''}}"''' + attrs(name="delivery_fee", note="(규칙) suppliers.delivery_fee — 보관 창고만. 개발 suppliers 칸 없음") + ''' /></div>'''
  f'''<div><div {WH_LABEL}>회수 단가(원) *</div><input class="f-input" id="vt-ret" type="number" style="width:100%;" placeholder="회수 단가(원)" value="${{x.returnFee || '4000'}}"''' + attrs(name="return_fee", note="(규칙) suppliers.return_fee — 기본 4,000원, 물류비 대사 반품 행 기준값") + ''' /></div>'''
  f'''<div><div {WH_LABEL}>월 보관료(원)</div><input class="f-input" id="vt-sto" type="number" style="width:100%;" placeholder="월 보관료(원)" value="${{x.storage || ''}}" /></div>'''
  f'''<div><div {WH_LABEL}>정산 주기</div><input class="f-input" id="vt-cycle" style="width:100%;" placeholder="정산 주기" value="${{x.cycle || '월 1회 (익월 초 명세서)'}}" /></div>'''
  f'''<div><div {WH_LABEL}>운영 연락처</div><input class="f-input" id="vt-ops" style="width:100%;" placeholder="출고 · 회수 운영 연락 (배송사 담당자)" value="${{x.opsContact || ''}}"''' + attrs(flag="proto-only", name="ops_contact", note="(규칙) suppliers.ops_contact — 운영 연락은 배송사 담당자와 직접(F7)") + ''' /></div>'''
  f'''<div><div {WH_LABEL}>메일 참조</div><input class="f-input" id="vt-cc" style="width:100%;" placeholder="메일 참조 (도서 공급사 메일)" value="${{x.mailCc || ''}}"''' + attrs(flag="proto-only", name="mail_cc", note="(규칙) suppliers.mail_cc — 메일은 도서 공급사 참조(F7)") + ''' /></div>'''
  '''</div><div class="form-help">배송 · 회수 단가는 물류비 대사의 기준값입니다 — 보관 창고 월 청구를 이 단가로 검수합니다(회수 기본 4,000원).</div>`;''')
R("if (form === 'LOGISTICS') return { outFee: g('vt-out'), returnFee: g('vt-ret'), storage: g('vt-sto'), cycle: g('vt-cycle') };",
  "if (form === 'LOGISTICS') return { outFee: g('vt-out'), returnFee: g('vt-ret'), storage: g('vt-sto'), cycle: g('vt-cycle'), opsContact: g('vt-ops'), mailCc: g('vt-cc') };")
R("if (t.form === 'LOGISTICS') return `출고 건당 ${won(x.outFee)}원 · 반품 회수 ${won(x.returnFee)}원 · 보관 월 ${won(x.storage)}원 · ${x.cycle || ''}`;",
  "if (t.form === 'LOGISTICS') return `배송 건당 ${won(x.outFee)}원 · 회수 ${won(x.returnFee)}원${x.storage ? ' · 보관 월 ' + won(x.storage) + '원' : ''} · ${x.cycle || ''}${x.opsContact ? ' · 운영 연락 ' + x.opsContact : ''}${x.mailCc ? ' · 메일 참조 ' + x.mailCc : ''}`;")
R("if (t.form === 'LOGISTICS' && !(Number(terms.outFee) > 0)) return fail('물류 대행사는 출고 건당 단가를 입력해야 물류비 대사를 할 수 있습니다.');",
  "if (t.form === 'LOGISTICS' && !(Number(terms.outFee) > 0 && Number(terms.returnFee) > 0)) return fail('보관 창고는 배송 · 회수 단가를 입력해야 물류비 대사를 할 수 있습니다.');")
# 1차 보관 창고 1곳만 활성 — 두 번째 활성 저장을 막는다(이름 확인 직후, 국세청 조회보다 먼저)
R("if (!name) return fail('거래처명을 입력해 주십시오.');",
  "if (!name) return fail('거래처명을 입력해 주십시오.');\n"
  "      const otherWh = t.kind === 'warehouse' && on ? M.vendors.list().find(v => v.on && v.id !== editingId && (M.vendors.type(v.type) || {}).kind === 'warehouse') : null;\n"
  "      if (otherWh) return fail(`1차는 보관 창고 1곳만 거래 중으로 둘 수 있습니다. 지금 거래 중인 보관 창고 ${otherWh.name}(${otherWh.id})을(를) 먼저 거래 중지하거나, 이 거래처를 거래 중지로 저장해 주십시오.`);")
# 목록 유형 배지 — 배송사도 물류 쪽 색으로
R("<span class=\"badge ${t && t.form === 'LOGISTICS' ? 'badge-purple' : 'badge-blue'}\">",
  "<span class=\"badge ${t && (t.form === 'LOGISTICS' || t.kind === 'courier') ? 'badge-purple' : 'badge-blue'}\">")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("거래처 등록 모달", "openVendorModal(null)", "#layerVendor|#modal-vendor"),
    ("거래처 수정 모달", "openVendorModal('SUP-0020')", "#layerVendor|#modal-vendor"),
    ("거래처 유형 모달", "openTypeModal()", "#layerVendorType|#modal-type"),
    ("상태 필터", "document.getElementById('flt-status').value='OFF'; renderVendors()", "#flt-status"),
    # 3PL 화면 반영(초안): dev는 보관 창고 칸(#vt-wh · #vt-ops), clean은 기존 물류 대행 칸(#vt-out)
    ("보관 창고 유형 칸", "openVendorModal(null); document.getElementById('vf-type').value='VT-03'; renderTermsForm()", "#vt-wh|#vt-out"),
    ("배송사 유형(dev) · 매입 양식(clean)", "openVendorModal(null); if (M.vendors.type('VT-04')) { document.getElementById('vf-type').value='VT-04'; renderTermsForm(); }", "#vt-memo|#vt-rate"),
    ("보관 창고 두 번째 활성 저장 막음(dev) · 형식 오류(clean)", "openVendorModal(null); document.getElementById('vf-type').value='VT-03'; renderTermsForm(); document.getElementById('vf-name').value='시험 창고'; saveVendor()", "#vendor-error"),
    ("유형 필터 보관 창고", "document.getElementById('flt-type').value='VT-03'; renderVendors()", "#vendor-tbody tr"),
]
