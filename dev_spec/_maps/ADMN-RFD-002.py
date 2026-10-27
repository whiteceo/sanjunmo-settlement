"""ADMN-RFD-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-RFD-002.md
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
    "code": "ADMN-RFD-002",
    "devCommit": DEV_COMMIT,
    "progress": "구현(RFD-004 · 002 · 002-S1 · P1 · P2 · 003 · 003-S2). 상세 라인 체크 · 목록 진입 보정 · 무상 P 보정은 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.refunds.index", "label": "환불 요청 관리 (목록 · 상세 · 1:1 문의)"},
        {"route": "admin.refund-histories.index", "label": "환불 내역 조회 (완료 · 보정 거래)"},
        {"route": "admin.pass-refunds.index", "label": "합격 환급 심사 (케이스 4 계좌 환불만)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 · 버튼 id → 개발 id ─────────────────────────────
RENAME_ID("modal-p1", "layerMinus", 4)
RENAME_ID("modal-p2", "layerPointUsages", 3)
RENAME_ID("p1-reason", "minusReason", 2)
RENAME_ID("p1-chk", "minusAgree", 2)
RENAME_ID("btn-final-submit", "approveButton", 3)
RENAME_ID("rfd-adjust-form", "adjustForm", 2)
RENAME_ID("m3f-ra-submit", "adjustSubmit", 1)
RENAME_ID("m3f-ra-preview", "adjustPreview", 2)

# ── 화면 전환 ───────────────────────────────────────
ACTX("showMainView('list')\">📋", route="admin.refunds.index", method="GET", url=A + "/refunds", perm="조회")
ACTX("showMainView('detail')", route="admin.refunds.show", method="GET", url=A + "/refunds/{refund}", perm="조회")
ACTX("showMainView('done')", route="admin.refund-histories.index", method="GET", url=A + "/refund-histories", perm="조회")

# ── 004 요청 목록 ────────────────────────────────────
for _st, _dev in (("ALL", "all"), ("접수", "requested"), ("상담필요", "consult"), ("환불진행", "progress"), ("환불보류", "held"), ("환불완료", "completed"), ("거절기각", "rejected")):
    ACTX(f"filterListByStatus('{_st}'", route="admin.refunds.index", method="GET", url=A + f"/refunds?tab={_dev}", perm="조회")
R('<input type="text" class="form-control" value="2026-10-01 ~ 2026-10-16" />',
  '<input type="text" class="form-control" value="2026-10-01 ~ 2026-10-16" data-dev-name="from · to" data-dev-note="개발은 날짜 2칸(Y-m-d), 기본 최근 30일" />')
R('<select class="form-control">\n                  <option>전체 (주문목록 직접신청 + 1:1 문의)</option>\n                  <option>마이페이지 주문목록 직접 신청</option>\n                  <option>1:1 결제/환불 문의 접수</option>',
  '<select class="form-control" name="inflow">\n                  <option value="">전체 (주문목록 직접신청 + 1:1 문의)</option>\n                  <option value="mypage">마이페이지 주문목록 직접 신청</option>\n                  <option value="inquiry">1:1 결제/환불 문의 접수</option>')
R('<select class="form-control">\n                  <option>전체 (인강 / 교재 / 패키지)</option>',
  '<select class="form-control" name="product"' + attrs(note="개발 값: within 1개월 이내 · over 1개월 초과 · book 교재 포함 — 프로토 구분(패키지 · 단과 · 교재)과 기준이 다름") + '>\n                  <option>전체 (인강 / 교재 / 패키지)</option>')
R('              <div class="form-group">\n                <label>검색어 (주문번호 / 회원명 / 접수번호)</label>',
  '              <div class="form-group" data-dev-flag="dev-only" data-dev-note="개발 RefundAdminService 요청 유형 · 처리 기한 필터">\n'
  '                <label>요청 유형 / 처리 기한</label>\n'
  '                <div style="display:flex; gap:6px;">\n'
  '                  <select class="form-control" name="type"><option value="">전체 유형</option><option value="cancel">취소(전액)</option><option value="partial">환불(부분)</option><option value="return">반품</option></select>\n'
  '                  <select class="form-control" name="deadline"><option value="">전체 기한</option><option value="overdue">기한 초과 건만</option><option value="due">기한 D-1 이하</option></select>\n'
  '                </div>\n'
  '              </div>\n'
  '              <div class="form-group">\n                <label>검색어 (주문번호 / 회원명 / 접수번호)</label>')
R('<input type="text" class="form-control" placeholder="주문번호 또는 이름 입력" />', '<input type="text" class="form-control" name="keyword" maxlength="50" placeholder="주문번호 또는 이름 입력" />')
R('<button class="btn btn-primary" style="flex:1;">🔍 조회</button>', '<button class="btn btn-primary" style="flex:1;"' + attrs(route="admin.refunds.index", method="GET", url=A + "/refunds", perm="조회") + '>🔍 조회</button>')
R('<button class="btn btn-outline">📥 엑셀 다운로드</button>', '<button class="btn btn-outline" id="requestExcel"' + attrs(route="admin.refunds.download", method="GET", url=A + "/refunds/download", perm="다운로드", note="사유 레이어 layerReason · 회원명 마스킹") + '>📥 엑셀 다운로드</button>')
ACTX("openDetailView('HONG')", count=2, route="admin.refunds.show", method="GET", url=A + "/refunds/{refund}", perm="조회")
ACTX("openDetailView('KIM')", count=2, route="admin.refunds.inquiries.show", method="GET", url=A + "/refunds/inquiries/{inquiry}", perm="조회", note="판정 전 1:1 문의 — 개발은 별도 화면 inquiry-show")
ACTX("openDetailView('CHOI')", count=2, route="admin.refunds.show", method="GET", url=A + "/refunds/{refund}", perm="조회")
ACTX("openDetailView('PARK')", route="admin.refunds.show", method="GET", url=A + "/refunds/{refund}", perm="조회")

# ── 002 상세 · 왼쪽 탭 ────────────────────────────────
ACTX("switchLeftTab('reason')", route="admin.refunds.show", method="GET", url=A + "/refunds/{refund}", perm="조회")
ACTX("switchLeftTab('inquiry')", route="admin.refunds.inquiries.show", method="GET", url=A + "/refunds/inquiries/{inquiry}", perm="조회",
     note="개발은 환불 상세 / 문의 상세 두 화면(프로토는 한 화면 탭)")
ALERT("S3 비공개 버킷", route="admin.refunds.photos.show", method="GET", url=A + "/refunds/{refund}/photos/{photo}", perm="조회")
ACT("unmaskBank", route="admin.masking.unmask", method="POST", url=A + "/masking/unmask", perm="메뉴 권한 밖(MaskingService)")

# ── 002-S1 문의 ─────────────────────────────────────
R('<select class="form-control" style="width:145px; padding:4px 8px;">\n                    <option selected>[결제·환불]</option>',
  '<select class="form-control" style="width:145px; padding:4px 8px;" name="category_id"' + attrs(note="값 = 문의 분류 id(RefundInquiryCategoryRequest) · PUT admin.refunds.inquiries.category.update") + '>\n                    <option selected>[결제·환불]</option>')
ALERT("선택한 담당 부서 게시판", route="admin.refunds.inquiries.category.update", method="PUT", url=A + "/refunds/inquiries/{inquiry}/category", perm="수정")
DEVNAME('name="inq_mode" id="radio-mode-consult" value="CONSULT"', "sub_type", value="consult")
DEVNAME('name="inq_mode" id="radio-mode-refund" value="REFUND"', "sub_type", value="partial · full (부분 · 전액)")
ACT("setInquiryMode", route="admin.refunds.inquiries.sub-type.update", method="PUT", url=A + "/refunds/inquiries/{inquiry}/sub-type", perm="수정",
    note="sub_type · order_id · item_ids[] · judge_reason")
ACTX("this.parentElement.innerHTML", route="admin.refunds.inquiries.sub-type.update", method="PUT", url=A + "/refunds/inquiries/{inquiry}/sub-type", perm="수정", note="order_id 연결")
NAME("inq-reply-textarea", "answer_content", note="answer일 때 10자 이상")
# v6.92: 보류 alert 버튼 → openRfdHold() 모달(#modal-rfd-hold)로 바뀜(결정 반영 S-11). 예전 dev-only 사유 select는 모달 안 hold-reason으로 대체돼 삭제
R('id="btn-rfd-hold" onclick="openRfdHold()"', 'id="btn-rfd-hold"' + attrs(perm="수정", note="1:1 문의 패널 — 저장 admin.refunds.inquiries.hold.update(PUT /refunds/inquiries/{inquiry}/hold)") + ' onclick="openRfdHold()"')
R('id="btn-rfd-hold2" onclick="openRfdHold()"', 'id="btn-rfd-hold2"' + attrs(perm="수정", note="환불 상세 계산기 — 저장 admin.refunds.hold.update(PUT /refunds/{refund}/hold)") + ' onclick="openRfdHold()"')
NAME("hold-reason", "hold_reason", note="RefundHoldRequest — 값 같음(customer_reply · return_wait · payment_check · other)")
NAME("hold-memo", "hold_memo", note="개발 required · 500자 — 프로토는 기타만 필수(10자)")
ACT("confirmRfdHold", route="admin.refunds.hold.update", method="PUT", url=A + "/refunds/{refund}/hold", perm="수정",
    note="1:1 문의 건은 admin.refunds.inquiries.hold.update. 법정 환급 기한 · 처리 기한은 멈추지 않음(S-11)")
ALERT("1:1 문의 답변이 등록", route="admin.refunds.inquiries.update", method="PUT", url=A + "/refunds/inquiries/{inquiry}", perm="수정", note="action=draft · answer · hold")

# ── 002 검수 · 포인트 · 계산 ──────────────────────────
ACT("openPointHistory", route="admin.refunds.point-usages.index", method="GET", url=A + "/refunds/{refund}/point-usages", perm="조회")
NAME("sel-book-inspect", "inspection_result", note="WAIT = 입고 전(개발은 입고 확인 receipt.update 별도). 3값 normal · defective · damaged(D-ORD-09, defective는 개발 추가 필요)")
DEVNAME('<option value="PASS"', "inspection_result", value="normal")
DEVNAME('<option value="DAMAGED"', "inspection_result", value="defective", note="(규칙) D-ORD-09 — 파본/불량 · 회사 귀책 고정 · 재고 미입고. 프로토 코드 DAMAGED ≠ 개발 damaged")
DEVNAME('<option value="REJECT"', "inspection_result", value="damaged", note="고객 훼손")
ACT("attachRfdInspectPhoto", name="photos[]", note="jpg · png · 10MB — 고객 훼손(damaged)만 필수(D-ORD-02)")
R('<option value="WAIT" selected>', '<option value="WAIT"' + attrs(note="입고 전 — 개발 warehouse_received_at 비어 있음") + ' selected>')
NAME("sel-fault", "liability", note="개발 customer · company 2종 — 고객 귀책은 항상 왕복(Q-RFD-7)")
DEVNAME('<option value="CUSTOMER_ONEWAY"', "liability", value="customer", note="편도 구분 없음")
R('<option value="CUSTOMER" selected>', '<option value="CUSTOMER"' + attrs(name="liability", value="customer") + ' selected>')
DEVNAME('<option value="COMPANY"', "liability", value="company")
R('                <!-- 적립금 A vs B 한 줄 요약 테이블 -->',
  '                <div style="display:grid; grid-template-columns:1fr 1fr auto; gap:12px; align-items:end; margin-bottom:12px;"'
  + attrs(flag="dev-only", route="admin.refunds.receipt.update", method="PUT", url=A + "/refunds/{refund}/receipt", perm="수정",
          note="3PL 창고 입고 확인 단계(RefundReceiptRequest) — 검수(admin.refunds.inspection.update)와 분리") + '>\n'
  '                  <div class="form-group" style="margin-bottom:0;"><label>반품 수거 송장번호</label><input type="text" class="form-control" name="return_tracking_no" maxlength="100" placeholder="수거 송장 (선택)" /></div>\n'
  '                  <div class="form-group" style="margin-bottom:0;"><label>창고 입고 일시</label><input type="datetime-local" class="form-control" name="received_at" /></div>\n'
  '                  <button type="button" class="btn btn-sm btn-outline">📦 입고 확인</button>\n'
  '                </div>\n'
  '                <!-- 적립금 A vs B 한 줄 요약 테이블 -->')
R('<button class="btn btn-sm btn-outline" onclick="window.print()">🖨️ 명세서 인쇄</button>',
  '<div style="display:flex; gap:6px;">'
  '<button type="button" class="btn btn-sm btn-outline"' + attrs(flag="dev-only", route="admin.refunds.recalculate", method="POST", url=A + "/refunds/{refund}/recalculate", perm="수정(접미사 예외)", note="스냅샷 · 예정액 재계산(recalculateForm)") + '>🔄 재계산</button>'
  '<button class="btn btn-sm btn-outline"' + attrs(route="admin.refunds.print.show", method="GET", url=A + "/refunds/{refund}/print", perm="조회") + ' onclick="window.print()">🖨️ 명세서 인쇄</button></div>')
NAME("c-admin-adj", "manual_amount", note="개발은 최종 환불 현금을 덮어씀(절대값 0~1억) — 프로토는 ± 가감액")
R('<input type="text" class="form-control" placeholder="보정 사유 입력 (최소 10자)"', '<input type="text" class="form-control" name="manual_reason" data-dev-note="manual_amount 있으면 10~500자" placeholder="보정 사유 입력 (최소 10자)"')
# v6.92: 거절 alert 버튼 → openRfdReject() 모달(#modal-rfd-reject)로 바뀜(결정 반영 S-11)
ACT("openRfdReject", perm="수정", note="개발 레이어 layerReject")
DEVNAME('name="reject-reason" value="LEGAL_NO_REFUND"', "reject_reason", value="legal_no_refund", note="(규칙) 개발은 사유 코드 없음(MemberReasonRequest reason만)")
DEVNAME('name="reject-reason" value="INSPECTION_FAIL"', "reject_reason", value="inspection_fail")
DEVNAME('name="reject-reason" value="DUPLICATE"', "reject_reason", value="duplicate")
NAME("reject-notice", "reason", note="MemberReasonRequest 공백 제외 10자 · 200자 — 고객 안내 알림톡 문구")
ACT("confirmRfdReject", route="admin.refunds.rejection.update", method="PUT", url=A + "/refunds/{refund}/rejection", perm="수정")
ACT("submitFinalRefund", route="admin.refunds.approval.update", method="PUT", url=A + "/refunds/{refund}/approval", perm="수정 + 재무(canSettleMoney)",
    note="1:1 문의 건은 admin.refunds.inquiries.cancel.update, PG 기간 초과 계좌 환불은 admin.pass-refunds.account-refunds.update")
ACT("confirmP1", route="admin.refunds.approval.update", method="PUT", url=A + "/refunds/{refund}/approval", perm="수정 + 재무", note="minus_agree · minus_reason(10~150자)")
R('id="minusReason"', 'id="minusReason" name="minus_reason"')
R('id="minusAgree"', 'id="minusAgree" name="minus_agree" value="1"')

# ── 003 완료 내역 · 상세 · S2 ─────────────────────────
R('<button class="btn btn-sm btn-outline">📥 PG 대사용 엑셀 다운로드</button>\n            </div>\n          </div>',
  '<button class="btn btn-sm btn-outline" id="historyPgExcel"' + attrs(route="admin.refund-histories.download", method="GET", url=A + "/refund-histories/download (PG 대사용)", perm="다운로드", note="사유 레이어") + '>📥 PG 대사용 엑셀 다운로드</button>\n            </div>\n          </div>\n'
  '          <div class="card-body" style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;"' + attrs(flag="dev-only", note="개발 normalizeHistoryFilters — 탭 7개 · 기간 · 범위 · PG 결과") + '>\n'
  '            <select class="form-control" name="tab" style="width:150px;"><option value="all">전체</option><option value="course">인강</option><option value="book">실물 교재</option><option value="rejected">반품 기각</option><option value="minus">마이너스 전환</option><option value="grace">D+7 유예 적용</option><option value="adjusted">보정 거래</option></select>\n'
  '            <input type="date" class="form-control" name="date_from" value="2026-10-01" style="width:140px;" /> ~ <input type="date" class="form-control" name="date_to" value="2026-10-16" style="width:140px;" />\n'
  '            <select class="form-control" name="scope" style="width:110px;"><option value="">전체 범위</option><option value="full">전액</option><option value="partial">부분</option><option value="return">반품</option></select>\n'
  '            <select class="form-control" name="pg" style="width:110px;"><option value="">PG 전체</option><option value="normal">정상</option><option value="failed">실패</option></select>\n'
  '          </div>')
ACTX("openRefundAdjustPage(null, 'list')", flag="proto-only", note="목록에서 원 환불 고르고 보정 — 개발은 완료 상세에서만 진입(원 환불 고정)")
ACTX("openRefundAdjustPage('RFD-", count=2, route="admin.refund-histories.adjustments.create", method="GET", url=A + "/refund-histories/{refund}/adjustments/create", perm="등록 + 재무")
ACTX("openRefundAdjustPage(null, 'detail')", route="admin.refund-histories.adjustments.create", method="GET", url=A + "/refund-histories/{refund}/adjustments/create", perm="등록 + 재무")
ACTX("openRfdDonePage('RFD-2026-001120')\">", count=2, route="admin.refund-histories.show", method="GET", url=A + "/refund-histories/{refund}", perm="조회")
ACTX("openRfdDonePage('RFD-2026-001098')\">", count=2, route="admin.refund-histories.show", method="GET", url=A + "/refund-histories/{refund}", perm="조회")
R('id="m3f-ra-rfd"', 'id="m3f-ra-rfd" data-dev-note="개발은 URL {refund} 고정(완료 건만) — 선택 칸 없음"')
DEVNAME('name="m3f-ra-type" value="ADD"', "adjustment_type", value="extra_refund")
DEVNAME('name="m3f-ra-type" value="RECOVER"', "adjustment_type", value="clawback")
DEVNAME('name="m3f-ra-type" value="POINT"', "adjustment_type", value="point", note="개발은 유상 P만(무상 P 보정 없음)")
NAME("m3f-ra-amount", "amount", note="1~1억, 원 또는 P(수단으로 구분) — 개발은 한 칸")
NAME("m3f-ra-pkind", "point_kind", note="(규칙) S-09 포인트 단독 보정 — paid 적립 P · free 무상 P. 개발은 유상 P만")
R('<option value="PAID">적립 P', '<option value="PAID"' + attrs(name="point_kind", value="paid") + '>적립 P')
R('<option value="FREE">무상 P', '<option value="FREE"' + attrs(name="point_kind", value="free") + '>무상 P')
NAME("m3f-ra-pexp", "point_expires_at", note="(규칙) S-09 포인트 만료일 필수")
R('id="m3f-ra-point"', 'id="m3f-ra-point" data-dev-flag="proto-only" data-dev-note="금액 · 포인트 동시 입력 — 개발은 한 거래 = 한 수단(amount 한 칸)"')
NAME("m3f-ra-exec", "method", note="유형별 허용 METHODS_BY_TYPE")
R('<option>토스페이먼츠 PG 추가 부분취소</option>', '<option data-dev-value="pg_cancel">토스페이먼츠 PG 추가 부분취소</option>')
R('<option>고객 환불계좌 무통장 입금</option>', '<option data-dev-value="bank_transfer">고객 환불계좌 무통장 입금</option>')
R('<option>고객 과오납 환수 입금 확인</option>', '<option data-dev-value="customer_claim">고객 과오납 환수 입금 확인</option>')
R('<option>포인트 원장만 조정</option>', '<option data-dev-value="point_grant · point_deduct">포인트 원장만 조정</option>')
NAME("m3f-ra-reason", "reason", note="공백 제외 10자 · 2000자 이하")
R('id="m3f-ra-reason-count">현재 0자 / 최소 10자</div>\n          </div>',
  'id="m3f-ra-reason-count">현재 0자 / 최소 10자</div>\n          </div>\n'
  '          <div class="m3f-sec" style="margin-bottom:0;"' + attrs(flag="dev-only", note="개발 RefundAdjustmentRequest evidences[](jpg · png · pdf · 10MB · 최대 3개) · bank_transfer일 때 bank_code · account_no · account_holder") + '>\n'
  '            <div class="m3f-sec-title">6. 보정 근거 파일 <span style="font-weight:500; color:#64748B;">(최대 3개 · jpg · png · pdf · 10MB)</span></div>\n'
  '            <input type="file" class="form-control" name="evidences[]" multiple accept=".jpg,.jpeg,.png,.pdf" style="width:100%;" />\n'
  '          </div>')
ACT("submitRefundAdjust", route="admin.refund-histories.adjustments.store", method="POST", url=A + "/refund-histories/{refund}/adjustments", perm="등록 + 재무(canRegisterAdjustment)",
    note="layerAdjustConfirm 확인 후 제출 · 회원 안내 TPL_RFD_ADJUST")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("상세 view", "showMainView('detail')", "#view-detail"),
    ("케이스 2 문의 탭", "openDetailView('KIM'); switchLeftTab('inquiry')", "#left-pane-inquiry"),
    ("완료 view", "showMainView('done')", "#view-done"),
    ("P2 포인트 내역", "openDetailView('HONG'); document.getElementById('btn-point-history').click()", "#layerPointUsages|#modal-p2"),
    ("완료 상세", "showMainView('done'); openRfdDonePage('RFD-2026-001120')", "#rfd-done-body"),
    ("S2 보정 등록", "showMainView('done'); openRefundAdjustPage('RFD-2026-001120', 'list')", "#adjustForm|#rfd-adjust-form"),
]
