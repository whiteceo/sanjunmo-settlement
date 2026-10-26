"""ADMN-DASH-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-DASH-001.md
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
    "code": "ADMN-DASH-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(DASH-001 대시보드 · STAT-001 매출 통계 · STAT-002 상품 통계). 발송 실패 재발송 · API 수동 점검 · 통계 엑셀 사유 · 역할 미리보기는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.dashboard", "label": "대시보드 홈 (메뉴 권한 밖 — 로그인만, 블록은 DashboardService::VISIBLE)"},
        {"route": "admin.sales-stats.index", "label": "매출 통계 (STAT-001)"},
        {"route": "admin.product-stats.index", "label": "상품 통계 (STAT-002)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 머리 · 뷰 전환 → 페이지 3개 ───────────────────────────
R('<select id="rbac-role-sim"', '<select id="rbac-role-sim" data-dev-flag="proto-only" data-dev-note="역할 그룹 화면 미리보기(시연 전용) — 개발은 로그인 역할로 블록 결정"')
R('id="tab-btn-dash" onclick=', 'id="tab-btn-dash"' + attrs(route="admin.dashboard", method="GET", url=A + "/dashboard", perm="로그인만(instructor · assistant는 자기 랜딩으로)") + ' onclick=')
R('id="tab-btn-stat-sales" onclick=', 'id="tab-btn-stat-sales"' + attrs(route="admin.sales-stats.index", method="GET", url=A + "/sales-stats", perm="조회") + ' onclick=')
R('id="tab-btn-stat-prod" onclick=', 'id="tab-btn-stat-prod"' + attrs(route="admin.product-stats.index", method="GET", url=A + "/product-stats", perm="조회") + ' onclick=')

# ── 대시보드 홈 ─────────────────────────────────────
ACT("manualRefreshDash", route="admin.dashboard", method="GET", url=A + "/dashboard?fresh=1", perm="로그인만",
    note="개발 [data-dash-refresh] · 캐시 60초 · fresh 3초 쿨다운 · 60초 자동 갱신(X-Admin-Background: 1)")
ACT("toggleDashSec", count=5, note="개발 .dash-panel 블록은 접기 없음")
R('onclick="switchView(\'stat-sales\')">매출 통계 상세', attrs(route="admin.sales-stats.index", method="GET", url=A + "/sales-stats?preset=7", perm="조회").lstrip() + ' onclick="switchView(\'stat-sales\')">매출 통계 상세')
ACT("openFailQueueModal", flag="proto-only", note="발송 실패 큐 · 재발송 — 개발은 실패 건수 · 안내만(정본 결정: 프로토 유지)")
R('<div class="modal-backdrop" id="modal-fail-queue">', '<div class="modal-backdrop" id="modal-fail-queue" data-dev-flag="proto-only">')
ACT("retrySingleFail", count=2, flag="proto-only", route="admin.message-logs.resends.store (규칙)", method="POST", url=A + "/message-logs/{log}/resends", perm="등록")
ACT("retryAllTransientFails", flag="proto-only", route="admin.message-logs.resends.store (규칙)", method="POST", url=A + "/message-logs/resends", perm="등록")
ACT("runApiHealthCheck", flag="proto-only", note="API 상태 수동 점검 — 개발은 상태값(ok · warn · off · none) 표시만")
R('<a href="ADMN-RFD-002_baseline.html" class="btn btn-xs btn-primary">', '<a href="ADMN-RFD-002_baseline.html" class="btn btn-xs btn-primary"' + attrs(route="admin.pass-refunds.index", method="GET", url=A + "/pass-refunds?status=reviewing", perm="조회(대상 메뉴)") + '>')
R('<a href="ADMN-ORD-001_baseline.html" class="btn btn-xs">배송 ↗</a>', '<a href="ADMN-ORD-001_baseline.html" class="btn btn-xs"' + attrs(route="admin.deliveries.index", method="GET", url=A + "/deliveries?tab=ready", perm="조회(대상 메뉴)") + '>배송 ↗</a>')
R('<a href="ADMN-SETT-002_baseline.html" class="btn btn-xs">정산 ↗</a>', '<a href="ADMN-SETT-002_baseline.html" class="btn btn-xs"' + attrs(route="admin.settlement.board.index", method="GET", url=A + "/settlement/board?month=YYYY-MM", perm="조회(대상 메뉴)") + '>정산 ↗</a>')
R('<a href="ADMN-CONF-010_baseline.html" class="btn btn-xs">', '<a href="ADMN-CONF-010_baseline.html" class="btn btn-xs"' + attrs(route="admin.admin-logs.index", method="GET", url=A + "/admin-logs?period=1&type=excel_download", perm="조회(대상 메뉴)") + '>')
R('<a href="ADMN-CONF-004_baseline.html?view=send" class="btn">', '<a href="ADMN-CONF-004_baseline.html?view=send" class="btn"' + attrs(route="admin.message-templates.campaigns.index", method="GET", url=A + "/message-templates/campaigns", perm="조회(대상 메뉴)") + '>')

# ── STAT-001 매출 통계 (SalesStatRequest::filters) ──────────
ACT("setSalesPeriodPreset", count=4, name="preset", value="7 · 14 · 30 · 365")
NAME("stat-sales-from", "from", note="Y-m-d · 최대 13개월")
NAME("stat-sales-to", "to")
NAME("stat-sales-unit", "unit", value="day · week · month (프로토 DAY · WEEK · MONTH)")
R('<select id="stat-sales-type"', '<select id="stat-sales-type" data-dev-name="kinds[]" data-dev-value="single · package · book (개발은 체크박스 여럿 — 프로토 select 1개)"')
NAME("stat-sales-method", "method", value="'' · card · virtual_account · easy_pay (+ 개발 transfer · mobile_phone · gift)")
R('            <option value="EASY">간편결제(토스·카카오)</option>',
  '            <option value="EASY">간편결제(토스·카카오)</option>\n'
  '            <option value="TRANSFER" disabled data-dev-flag="dev-only" data-dev-value="transfer">계좌이체</option>\n'
  '            <option value="MOBILE" disabled data-dev-flag="dev-only" data-dev-value="mobile_phone">휴대폰 결제</option>\n'
  '            <option value="GIFT" disabled data-dev-flag="dev-only" data-dev-value="gift">상품권</option>')
R('<button type="button" class="btn btn-primary btn-xs" onclick="renderSalesStat()">',
  '<strong data-dev-flag="dev-only">기준:</strong>\n'
  '          <select class="form-select" name="basis" data-dev-flag="dev-only" data-dev-note="paid 결제일 기준(원거래일 소급) · refund_confirmed 환불일 기준(발생일)"><option value="paid">결제일 기준</option><option value="refund_confirmed">환불일 기준</option></select>\n'
  '          <button type="button" class="btn btn-primary btn-xs"' + attrs(route="admin.sales-stats.index", method="GET", url=A + "/sales-stats", perm="조회") + ' onclick="renderSalesStat()">')
R('onclick="openStatExcelModal(\'ADMN-STAT-001', attrs(route="admin.sales-stats.download", method="GET", url=A + "/sales-stats/download", perm="다운로드",
                                                     note="개발은 사유 없이 바로 다운로드(excel_download_logs 기록) — 정책 D-CONF-04").lstrip() + ' onclick="openStatExcelModal(\'ADMN-STAT-001')

# ── STAT-002 상품 통계 (ProductStatRequest::filters) ─────────
R('onclick="showToast(\'최근 7일 상품 판매 순위를 조회했습니다.\')"', attrs(name="preset", value="7").lstrip() + ' onclick="showToast(\'최근 7일 상품 판매 순위를 조회했습니다.\')"')
R('onclick="showToast(\'최근 14일 상품 판매 순위를 조회했습니다.\')"', attrs(name="preset", value="14").lstrip() + ' onclick="showToast(\'최근 14일 상품 판매 순위를 조회했습니다.\')"')
R('<select id="stat-prod-type"', '<select id="stat-prod-type" data-dev-name="kinds[]" data-dev-value="package · single · book"')
NAME("stat-prod-sort", "sort", value="revenue (NET_AMT) · completed (NET_CNT) · refund_rate")
R('            <option value="NET_CNT">순결제건수 많은순</option>',
  '            <option value="NET_CNT">순결제건수 많은순</option>\n'
  '            <option value="REFUND_RATE" disabled data-dev-flag="dev-only" data-dev-value="refund_rate">환불율 높은순</option>')
R('onclick="openStatExcelModal(\'ADMN-STAT-002', attrs(route="admin.product-stats.download", method="GET", url=A + "/product-stats/download", perm="다운로드").lstrip() + ' onclick="openStatExcelModal(\'ADMN-STAT-002')
R('<textarea id="inp-excel-reason"', '<textarea id="inp-excel-reason" data-dev-flag="proto-only" data-dev-note="통계 엑셀 사유 — 개발 없음(개인정보 없는 집계). 정책 D-CONF-04 권고: 사유 받지 않음"')
ACT("confirmStatExcelDownload", route="admin.sales-stats.download | admin.product-stats.download", method="GET", url=A + "/sales-stats/download | /product-stats/download", perm="다운로드")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
U = "document.querySelectorAll('.modal-backdrop').forEach(m => m.style.removeProperty('display')); "
VERIFY = [
    ("대시보드", "switchView('dash')", "#view-dash"),
    ("매출 통계", "switchView('stat-sales')", "#view-stat-sales"),
    ("상품 통계", "switchView('stat-prod')", "#view-stat-prod"),
    ("매출 프리셋 14일", "switchView('stat-sales'); setSalesPeriodPreset(14, null)", "#view-stat-sales"),
    ("상품 정렬", "switchView('stat-prod'); document.getElementById('stat-prod-sort').value='NET_CNT'; renderProdStat()", "#view-stat-prod"),
    ("발송 실패 큐 모달", U + "switchView('dash'); openFailQueueModal()", "#modal-fail-queue"),
    ("통계 엑셀 모달", U + "switchView('stat-sales'); openStatExcelModal('ADMN-STAT-001 매출 통계')", "#modal-stat-excel"),
    ("섹션 접기", "switchView('dash'); toggleDashSec('SALES')", "#view-dash"),
]
