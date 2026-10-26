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
        {"route": "admin.settlement.logistics-reconciliations.index (규칙)", "label": "물류비 대사(3PL)"},
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

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("출고 탭", "switchTab('out')", "#tab-out"),
    ("배송비 · 반품 탭", "switchTab('ship')", "#tab-ship"),
    ("도서 매입 탭", "switchTab('book')", "#tab-book"),
    ("불일치만 보기", "switchTab('out'); showMismatchOnly()", "#flt-status"),
    ("불일치 처리 모달", "switchTab('out'); openResolve(2)", "#layerLogisticsResolve|#modal-resolve"),
]
