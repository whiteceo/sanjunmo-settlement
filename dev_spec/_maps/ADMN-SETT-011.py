"""ADMN-SETT-011 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-011.md
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
    "code": "ADMN-SETT-011",
    "devCommit": DEV_COMMIT,
    "progress": "개발 미구현(2차, DECISIONS 107 물류비 대사 1차 제외) — 테이블만 있음(logistics_settlements · logistics_settlement_items · book_purchase_costs). 이름은 모두 (규칙), 동작은 전부 주황 표시",
    "menus": [
        {"route": "admin.settlement.logistics-reconciliations.index (규칙)", "label": "물류비 대사"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

B = A + "/settlement/logistics-reconciliations"
RT = "admin.settlement.logistics-reconciliations"
LIST = dict(flag="proto-only", route=RT + ".index (규칙)", method="GET", url=B, perm="조회")

# ── 모달 id → 개발 레이어 id(규칙) ───────────────────────
RENAME_ID("modal-resolve", "layerLogisticsResolve", 5)

# ── 상단 · 탭 ────────────────────────────────────────
NAME("month-select", "month", value="YYYY-MM = logistics_settlements.settlement_month")
ACT("uploadStatement", count=2, flag="proto-only", route=RT + ".statements.store (규칙)", method="POST", url=B + "/statements", perm="등록",
    note="statement_file (규칙) — 개발 #layerStatementUpload · #statementUploadForm (규칙)")
ACT("runRecon", flag="proto-only", route=RT + ".store (규칙)", method="POST", url=B, perm="등록", note="대사 실행 — PG 재대사와 같은 모양")
R('id="tabBtn-out" onclick="switchTab(', 'id="tabBtn-out"' + attrs(name="tab", value="outbound (규칙)", **LIST) + ' onclick="switchTab(')
R('id="tabBtn-ship" onclick="switchTab(', 'id="tabBtn-ship"' + attrs(name="tab", value="shipping (규칙)", **LIST) + ' onclick="switchTab(')
R('id="tabBtn-book" onclick="switchTab(', 'id="tabBtn-book"' + attrs(name="tab", value="books (규칙)", **LIST) + ' onclick="switchTab(')

# ── 1. 출고 · 수수료 ──────────────────────────────────
ACT("showMismatchOnly", note="match_status ≠ matched", **LIST)
NAME("flt-status", "match_status", value="matched 일치 · billed_only 3PL만 · ours_only DB만 · qty_diff 수량 차이 · price_diff 단가 차이 (프로토타입 값 MATCH · ONLY_3PL · ONLY_DB · DIFF 유지)",
     note="'불일치 전체'(MISMATCH)는 개발 컬럼 값 없음 — matched 제외로 조회")
ACT("resetOutFilter", count=2, **LIST)
ACT("openResolve", note="logistics_settlement_items 행 처리", flag="proto-only")
NAME("resolve-result", "resolve_result", note="(규칙) 처리 결과 PAY 승인 지급 · DEDUCT 차감 요청 · CARRY 차월 이월 — 저장 칸 · 코드값 개발 없음(정책 질문 D-SETT)")
NAME("resolve-memo", "memo", note="logistics_settlement_items.memo — 사유 없이 종결 불가(컬럼 주석)")
ACT("saveResolve", flag="proto-only", route=RT + ".items.update (규칙)", method="PUT", url=B + "/items/{item}", perm="수정")
R('onclick="saveResolve()"', 'id="logisticsResolveSubmit" onclick="saveResolve()"')

# ── 2. 배송비 · 반품 ──────────────────────────────────
ACT("saveJudge", flag="proto-only", route=RT + ".returns.update (규칙)", method="PUT", url=B + "/returns/{item}", perm="수정",
    note="반품 귀책 판정 · 고객 공제액 — 저장 칸 개발 테이블에 없음")

# ── 3. 도서 매입 계산서 ────────────────────────────────
ACT("requestReissue", flag="proto-only", route=RT + ".book-invoices.reissue.store (규칙)", method="POST", url=B + "/book-invoices/{bookPurchaseCost}/reissue", perm="등록",
    note="book_purchase_costs.match_status calc_diff 건")
ACT("receiveInvoice", flag="proto-only", route=RT + ".book-invoices.update (규칙)", method="PUT", url=B + "/book-invoices/{bookPurchaseCost}", perm="수정",
    note="계산서 수취 상태 저장 칸 개발 테이블에 없음 — 매입처는 publisher 문자열(suppliers.id 연결 없음)")
ACT("downloadExcel", count=2, flag="proto-only", route=RT + ".download (규칙)", method="GET", url=B + "/download", perm="다운로드",
    note="사유 필수(ReasonRequest, 공통 #layerReason)")
ACT("completeRecon", flag="proto-only", route=RT + ".lock.update (규칙)", method="PUT", url=B + "/{settlement}/lock", perm="수정",
    note="logistics_settlements.is_locked · confirmed_at — 매출 마감(SETT-004) 이후에만 잠금(재무 마감 2단계)")

# ── 3PL 화면 반영(초안, 기능 정의 초안 2 F8 · SCREEN_3PL.md) ────────────────
# 화면 노출 '3PL' → '물류비 대사' · '보관 창고' · '창고'(용어 표)는 2026-11-04 원본(prototype_clean)에 반영돼 여기서는 회수 단가 문구만 덧씌운다.
# 코드값(ONLY_3PL · value="3PL") · 파일명(3pl_*.xlsx)은 그대로
R("/ 창고 회수비 4,000원", "/ 창고 회수 단가 4,000원(회수 송장번호로 매칭)")

# 보관 창고 · 계약 단가 — 거래처 관리 dev 화면 값(sjm.dev.vend3pl.v1)을 먼저 읽고, 없으면 그 화면 샘플(대영물류)과 같은 값.
# 공통 SJM_MASTER의 물류 대행 거래처(CJ대한통운 파주 물류센터)는 dev 거래처 관리에서 거래 중지로 덧씌웠으므로 여기서도 쓰지 않는다
R("""      // 보관 창고 · 계약 단가는 거래처 관리(물류 대행 양식)에서 읽는다
      const tpls = M.vendors.byForm('LOGISTICS').filter(v => v.on);""",
  """      // (dev 3PL 초안) 보관 창고 · 계약 단가는 거래처 관리 dev 화면 값을 먼저 읽고, 없으면 그 화면 샘플(대영물류)과 같은 값
      const devWh = (() => { try { const s = JSON.parse(localStorage.getItem('sjm.dev.vend3pl.v1') || 'null'); return s && s.vendors ? s.vendors.filter(v => v.type === 'VT-03') : null; } catch (e) { return null; } })();
      const tpls = (devWh || [{ id: 'SUP-0022', name: '대영물류', on: true, terms: { outFee: '2000', returnFee: '4000', storage: '' } }]).filter(v => v.on);""")
R("'등록된 물류 대행사 없음'", "'거래 중인 보관 창고 없음'")
R("`계약 단가(거래처 관리): 출고 건당 ${won(Number(v.terms.outFee))}원 · 반품 회수 ${won(Number(v.terms.returnFee))}원 · 보관료 월 ${won(Number(v.terms.storage))}원(보관료 별도 정산 · 이 대사 범위 밖) — 창고 청구 단가가 이와 다르면 불일치로 봅니다.`",
  "`계약 단가(거래처 관리): 배송 건당 ${won(Number(v.terms.outFee))}원 · 회수 단가 ${won(Number(v.terms.returnFee || 4000))}원 · 보관료는 별도 정산(이 대사 범위 밖) — 창고 청구 단가가 이와 다르면 불일치로 봅니다. 매칭 키: 출고 행은 송장번호, 반품(회수) 행은 회수 송장번호.`")
R('<div class="k-sub">송장번호 → 주문번호 → 수령인 · 출고일 순서로 매칭</div>',
  '<div class="k-sub">송장번호 → 주문번호 → 수령인 · 출고일 순서로 매칭 · 반품은 회수 송장번호</div>')

# 예시 행: 취소완료(출고 안 됨) 건이 창고 청구에 있으면 차이(청구 대상 아님)
R("order: 'SJM-20260929-004590 · 문*희', qty: 1, db: '출고', claim: '청구', price: 2000, status: 'MATCH', diff: '일치' }",
  "order: 'SJM-20260929-004590 · 문*희', qty: 1, db: '출고', claim: '청구', price: 2000, status: 'MATCH', diff: '일치' },\n"
  "          { no: 13, date: '09.30', waybill: '6841-2201-0815', order: 'SJM-20260929-004593 · 장*민', qty: 1, db: '취소완료 (출고 안 됨)', claim: '청구', price: 2000, status: 'ONLY_3PL', diff: '취소완료 건 청구 — 청구 대상 아님' }")

# 반품(회수) 행 매칭 키 = 회수 송장번호(F4 회신)
R('<th style="width:170px;">주문번호 · 수령인</th><th style="width:150px;">DB 반품 사유</th>',
  '<th style="width:170px;">주문번호 · 수령인</th><th style="width:140px;"' + attrs(flag="proto-only", name="return_waybill_no", note="(규칙) logistics_settlement_items 반품 행 매칭 키 — 회수 송장번호(F4 회신으로 저장). 개발 칸 없음") + '>회수 송장번호 (매칭 키)</th><th style="width:150px;">DB 반품 사유</th>')
R("<td>${r.dbReason}</td>", "<td>${r.rtnWaybill || '—'}</td>\n          <td>${r.dbReason}</td>")
R("{ order: 'SJM-20260905-004102 · 김*수', dbReason", "{ order: 'SJM-20260905-004102 · 김*수', rtnWaybill: '2510-0908-3311', dbReason")
R("{ order: 'SJM-20260912-004260 · 이*정', dbReason", "{ order: 'SJM-20260912-004260 · 이*정', rtnWaybill: '2510-0915-3478', dbReason")
R("{ order: 'SJM-20260921-004418 · 박*현', dbReason", "{ order: 'SJM-20260921-004418 · 박*현', rtnWaybill: '2510-0924-3602', dbReason")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("출고 탭", "switchTab('out')", "#tab-out"),
    ("배송비 · 반품 탭", "switchTab('ship')", "#tab-ship"),
    ("도서 매입 탭", "switchTab('book')", "#tab-book"),
    ("불일치만 보기", "switchTab('out'); showMismatchOnly()", "#flt-status"),
    ("불일치 처리 모달", "switchTab('out'); openResolve(2)", "#layerLogisticsResolve|#modal-resolve"),
    # 3PL 화면 반영(초안): 취소완료 건 청구 예시 행(no 13) 처리 모달, 반품 대사 표
    ("취소완료 건 청구 처리 모달(dev) · 불일치 처리(clean)", "switchTab('out'); openResolve(cur().rows.some(r => r.no === 13) ? 13 : 2)", "#layerLogisticsResolve|#modal-resolve"),
    ("반품 대사 표(회수 송장번호)", "switchTab('ship')", "#ret-tbody tr"),
]
