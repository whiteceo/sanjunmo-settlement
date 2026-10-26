"""ADMN-SETT-006 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-006.md
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
    "code": "ADMN-SETT-006",
    "devCommit": DEV_COMMIT,
    "progress": "일부 구현(2차). 옵션 A 확정만 있고 B · C는 마감 보류(HOLD). 일괄 확정 · 엑셀 · 보완 요청 · 재연산 안내는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.pass-refunds.index", "label": "합격 환급반 관리(정산)"},
        {"route": "admin.pass-refunds.index", "label": "합격 환급 심사(회원 쪽, 심사 승인 · 증빙 열람)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

LIST = dict(route="admin.settlement.pass-refunds.index", method="GET", url=A + "/settlement/pass-refunds", perm="조회")

# ── 상단 · 필터 ──────────────────────────────────────
NAME("topMonthSelect", "month", value="YYYY-MM (정산 귀속월)", note="개발은 월 버튼 + #monthPick")
NAME("burdenFilter", "burden", value="'' 전체 · A 플랫폼 전액 · B 비율 공동 부담 · C 매출 취소 (프로토타입 값 OPTION_A/B/C 유지)")
FLAG("fOriginMonth", "proto-only", "원 결제월 필터 — 개발 없음")
FLAG("fInstructor", "proto-only", "귀속 강사 필터 — 개발 없음")
FLAG("fStatus", "proto-only", "상태 필터 — 개발 없음. 개발 settle_review_status: PENDING 검수 대기 · CONFIRMED 차감 확정 · HOLD 마감 보류(B · C)")
FLAG("searchInput", "proto-only", "통합 검색 — 개발 없음")
ACT("renderTable", note="목록 조회 — 개발 KEEP: month · tab · burden", **LIST)
ACT("resetFilters", **LIST)
ACT("filterByKpi", count=6, flag="proto-only", note="KPI '해당 건만 보기' — 개발 없음")

# ── 탭(개발 ?tab=) ───────────────────────────────────
DEVNAME('data-tab="tabWorkspace"', "tab", value="workspace")
DEVNAME('data-tab="tabRules"', "tab", value="mmg")
DEVNAME('data-tab="tabAudit"', "tab", value="audit")
R('<section id="tabAudit" class="tab-panel hidden">',
  '<section id="tabAudit" class="tab-panel hidden"' + attrs(route="admin.admin-logs.index", method="GET", url=A + "/admin-logs", perm="조회(관리자 로그 메뉴)",
                                                          note="개발 감사 탭은 관리자 로그로 이동(sub_action pass_refund_settle_confirm) — 화면 안 이력 표는 프로토타입만") + '>')

# ── 목록 동작 ────────────────────────────────────────
ACT("approveSelectedItems", flag="proto-only", route="admin.settlement.pass-refunds.bulk.update (규칙)", method="PUT", url=A + "/settlement/pass-refunds/bulk", perm="수정",
    note="일괄 확정 — 개발은 건별 update만(검수 의견 필수)")
FLAG("chkAll", "proto-only", "일괄 선택 — 개발 없음")
R("onclick=\"showToast('당월 합격환급",
  attrs(flag="proto-only", route="admin.settlement.pass-refunds.download (규칙)", method="GET", url=A + "/settlement/pass-refunds/download", perm="다운로드").lstrip()
  + " onclick=\"showToast('당월 합격환급")
ACT("openHrfDetailPage", count=2, route="admin.settlement.pass-refunds.show", method="GET", url=A + "/settlement/pass-refunds/{claim}", perm="조회")

# ── 상세(심사 · 정산 차감) ─────────────────────────────
R("onclick=\"showToast('합격증 사본",
  attrs(route="admin.pass-refunds.files.show", method="GET", url=A + "/pass-refunds/{passRefund}/files/{file}", perm="조회(합격 환급 심사 메뉴)").lstrip()
  + " onclick=\"showToast('합격증 사본")
R("onclick=\"showToast('통장 사본",
  attrs(route="admin.pass-refunds.files.show", method="GET", url=A + "/pass-refunds/{passRefund}/files/{file}", perm="조회(합격 환급 심사 메뉴)").lstrip()
  + " onclick=\"showToast('통장 사본")
NAME("detailMemoInput", "opinion", note="개발 검수 의견 — 필수 10~500자(PassRefundSettleRequest), 감사 로그 reason")
ACT("approveReview", route="admin.pass-refunds.update", method="PUT", url=A + "/pass-refunds/{passRefund}", perm="수정(합격 환급 심사 메뉴)",
    note="PassRefundReviewRequest action=approve + checks[](8종) · exam_year · exam_round · admin_memo")
ACT("approveSettlementDeduct", route="admin.settlement.pass-refunds.update", method="PUT", url=A + "/settlement/pass-refunds/{claim}", perm="수정",
    note="opinion 필수. 옵션 A만 rs · support 차감 0으로 확정, B · C는 검증 오류(마감 보류 HOLD) — 정책 질문 D-SETT")
ACT("openSupplementModal", flag="proto-only", note="보완 요청 — 개발 심사는 action verify · approve · reject · memo만(반려 reject_reason · reject_detail)")
ACT("sendSupplementRequest", flag="proto-only", route="admin.pass-refunds.supplements.store (규칙)", method="POST", url=A + "/pass-refunds/{passRefund}/supplements", perm="등록")
NAME("supplementReason", "reason")
R('class="sup-item"', 'class="sup-item" name="items[]"')
FLAG("recalcNoticeModal", "proto-only", "정산서 자동 재연산 안내 — 개발 없음(localStorage sjm.settle.recalcEvents.v1)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("목록 탭", "document.querySelector('[data-tab=tabWorkspace]').click()", "#tabWorkspace"),
    ("MMG 탭", "document.querySelector('[data-tab=tabRules]').click()", "#tabRules"),
    ("이력 탭", "document.querySelector('[data-tab=tabAudit]').click()", "#tabAudit"),
    ("상세 페이지(차감 대기)", "openHrfDetailPage('HRF-202610-02')", "#hrfDeductApproveBtn"),
    ("상세 페이지(심사 대기)", "openHrfDetailPage('HRF-202610-06')", "#hrfReviewApproveBtn"),
    ("보완 요청 모달", "openHrfDetailPage('HRF-202610-06'); openSupplementModal('HRF-202610-06')", "#supplementModal"),
    ("재연산 안내 모달", "openRecalcNotice('<p>x</p>')", "#recalcNoticeModal"),
]
