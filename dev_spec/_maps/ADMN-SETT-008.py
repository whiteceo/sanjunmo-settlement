"""ADMN-SETT-008 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-008.md
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
    "code": "ADMN-SETT-008",
    "devCommit": DEV_COMMIT,
    "progress": "구현(전환 승인 · 보류는 권리자 건만, 위탁자 · 매입처는 2차). 정기 일괄 조회 · 재시도 즉시 호출 · 세무 판정 보류 해제는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.nts.index", "label": "사업자등록 확인 이력"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

LIST = dict(route="admin.settlement.nts.index", method="GET", url=A + "/settlement/nts", perm="조회")

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modal-tax-transition", "layerNtsReview", 3)

# ── 상단 버튼(addEventListener) ─────────────────────────
R('<button class="btn" id="btnBatchCheck">', '<button class="btn" id="btnBatchCheck"'
  + attrs(flag="proto-only", note="정기 일괄 상태조회 — 개발은 배치 · 스케줄러(nts_periodic_check_schedule), 화면 라우트 없음") + '>')
R('<button class="btn btn-primary" id="btnReprocessQueue">', '<button class="btn btn-primary" id="btnReprocessQueue"'
  + attrs(flag="proto-only", note="재시도 큐 즉시 재호출 — 개발 라우트 없음(queue_status queued · retrying · resolved · abandoned)") + '>')

# ── KPI · 탭 · 필터 ──────────────────────────────────
R('<div class="kpi-card" data-filter="CHANGE_DETECTED">', '<div class="kpi-card" data-filter="CHANGE_DETECTED"' + attrs(name="review", value="unreviewed", **LIST) + '>')
DEVNAME('data-tab="tabHistory"', "tab", value="history")
DEVNAME('data-tab="tabMapping"', "tab", value="mapping")
DEVNAME('data-tab="tabRetry"', "tab", value="params")
NAME("searchInput", "keyword", note="b_no · rights_holders.name LIKE")
NAME("partnerTypeFilter", "subject_type", value="RIGHTS_HOLDER 권리자 · CONSIGNOR 위탁자 · SUPPLIER 매입처 (프로토타입 값 한글 라벨 유지)")
NAME("triggerFilter", "trigger_type",
     value="CONTRACT_REG · PERIODIC · AD_HOC · MILESTONE_APPROVAL · PURCHASE_ORDER · CONSIGNMENT_REG",
     note="프로토타입 '정산 마감 전 90일'은 개발 값 없음 · PURCHASE_ORDER · CONSIGNMENT_REG는 프로토타입 없음(정책 질문 D-SETT)")
R('<option value="마감 전 90일 경과">', '<option value="마감 전 90일 경과" data-dev-flag="proto-only" data-dev-note="개발 trigger_type에 없음">')
# 개발 review 필터(change_review_status) — 정본 디자인(.select)으로 추가
R('                <option value="마감 전 90일 경과" data-dev-flag="proto-only" data-dev-note="개발 trigger_type에 없음">정산 마감 전 90일 유효기간 경과</option>\n              </select>',
  '                <option value="마감 전 90일 경과" data-dev-flag="proto-only" data-dev-note="개발 trigger_type에 없음">정산 마감 전 90일 유효기간 경과</option>\n              </select>\n'
  '              <select class="select" name="review" data-dev-flag="dev-only" data-dev-note="개발 change_review_status 필터">\n'
  '                <option value="">전체 확인 상태</option>\n'
  '                <option value="unreviewed">미확인</option>\n'
  '                <option value="approved">승인</option>\n'
  '                <option value="held">보류</option>\n'
  '              </select>')

# ── 상세 패널 · 전환 승인 ───────────────────────────────
ACT("selectRecord", note="개발은 우측 상세 패널 없음 — 행의 [승인 검토] 버튼(.layer__open data-log-id)으로 모달")
R('id="inputEffDate"', 'id="inputEffDate"' + attrs(note="전환 효력일 — 개발은 API 응답 tax_type_change_dt 사용, 입력 없음"))
ACT("approveTaxTypeChange", route="admin.settlement.nts.update", method="PUT", url=A + "/settlement/nts/tax-type", perm="수정",
    note="개발 .layer__open[data-target=layerNtsReview][data-log-id] — 권리자 건만(위탁자 · 매입처 2차)")
ACT("confirmTaxTypeTransition", route="admin.settlement.nts.update", method="PUT", url=A + "/settlement/nts/tax-type", perm="수정",
    note="개발 #ntsReviewApproveBtn · hold=0. 승인 후 tab=history로 복귀(조건 유지)")
R('onclick="confirmTaxTypeTransition()"', 'id="ntsReviewApproveBtn" onclick="confirmTaxTypeTransition()"')
ACT("resolvePendingReview", flag="proto-only", route="admin.settlement.nts.tax-decision.update (규칙)", method="PUT", url=A + "/settlement/nts/tax-decision", perm="수정",
    note="세무 판정 보류(PENDING_REVIEW) 해제 — 개발 경로 없음")
R('id="inputReviewMemo"', 'id="inputReviewMemo" name="memo"' + attrs(note="(규칙) 세무 판정 확정 근거"))

# 개발 전환 승인 · 보류 폼(NtsTaxTypeReviewRequest) — 모달 안 정본 디자인(.form-group · .input)으로 추가
R('<div style="padding:12px 20px; background:var(--bg); border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px;">',
  '<div data-dev-flag="dev-only" data-dev-note="개발 #ntsReviewForm: log_id · explanation(20~2000자) · hold(1 보류 / 0 승인)" style="padding:0 20px 14px;">\n'
  '        <input type="hidden" id="ntsReviewLogId" name="log_id" value="" />\n'
  '        <input type="hidden" id="ntsReviewHold" name="hold" value="0" />\n'
  '        <div class="form-group">\n'
  '          <label class="form-label" for="ntsReviewExplanation">소명 내용 (20자 이상) <span id="ntsReviewCount" style="color:var(--text-muted); font-weight:500;">0자</span></label>\n'
  '          <textarea id="ntsReviewExplanation" name="explanation" class="input" rows="3" placeholder="전환 근거(정정 사업자등록증 확인 등)를 20자 이상 입력하세요."></textarea>\n'
  '        </div>\n'
  '      </div>\n'
  '      <div style="padding:12px 20px; background:var(--bg); border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:8px;">')
R('        <button type="button" class="btn" onclick="closeTaxTransitionModal()">취소</button>',
  '        <button type="button" class="btn" onclick="closeTaxTransitionModal()">취소</button>\n'
  '        <button type="button" class="btn" id="ntsReviewHoldBtn"' + attrs(flag="dev-only", route="admin.settlement.nts.update", method="PUT", url=A + "/settlement/nts/tax-type", perm="수정",
                                                                       note="hold=1 보류 — 원장 미변경 · 마감 보류 유지") + '>보류</button>')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("이력 탭", "document.querySelector('[data-tab=tabHistory]').click()", "#tabHistory"),
    ("매핑 탭", "document.querySelector('[data-tab=tabMapping]').click()", "#tabMapping"),
    ("파라미터 탭", "document.querySelector('[data-tab=tabRetry]').click()", "#tabRetry"),
    ("상세 패널", "document.querySelector('[data-tab=tabHistory]').click(); selectRecord('NTS-202610-07')", "#inputReviewMemo"),
    # 원본 결함: 여는 버튼 이름에 open · Modal이 없어 공통 핫픽스 인라인 display:none이 안 풀린다(clean도 안 열림) — 잠금만 풀어 id · 동작을 비교
    ("전환 승인 모달", "document.querySelector('[data-tab=tabHistory]').click(); selectRecord('NTS-202610-01'); document.querySelector('[onclick^=approveTaxTypeChange]').click(); document.querySelector('.modal-backdrop.open').style.removeProperty('display')", "#layerNtsReview|#modal-tax-transition"),
]
