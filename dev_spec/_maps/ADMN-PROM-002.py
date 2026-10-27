"""ADMN-PROM-002 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROM-002.md
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
    "code": "ADMN-PROM-002",
    "devCommit": DEV_COMMIT,
    "progress": "PROM-002 · P1 구현. PROM-003 일부(사이트 설정 ③ 포인트 구획) — 포인트 원장 목록 · 후기 보상 P · 무상 잔액 상한은 개발 없음(주황 표시)",
    "menus": [
        {"route": "admin.coupons.index", "label": "쿠폰 관리"},
        {"route": "admin.site-settings.index", "label": "사이트 설정 (③ 포인트 정책)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 레이어 id → 개발 id ─────────────────────────────
RENAME_ID("modal-p1", "couponCapAlert", 4)
RENAME_ID("modal-point", "layerPointGrant", 3)

# ── 서브뷰 → 개발 화면 ───────────────────────────────
R('onclick="switchSubView(\'list\')">\n', attrs(route="admin.coupons.index", method="GET", url=A + "/coupons", perm="조회").lstrip() + ' onclick="switchSubView(\'list\')">\n')
R('onclick="switchSubView(\'point\')"', attrs(route="admin.site-settings.index", method="GET", url=A + "/site-settings", perm="조회(사이트 설정 메뉴)",
  note="개발은 포인트 정책을 사이트 설정 ③ 포인트 구획에 둠(정책 질문)").lstrip() + ' onclick="switchSubView(\'point\')"')
ACT("openFormNew", count=3, route="admin.coupons.create", method="GET", url=A + "/coupons/create", perm="등록")

# ── 002 목록 ─────────────────────────────────────────
ACT("quickFilterStatus", count=4, route="admin.coupons.index", method="GET", url=A + "/coupons", perm="조회",
    note="개발 현황: operating 운영중 · issued 총 발급 · used 사용 · rate 사용률 · expired 미사용 소멸")
NAME("q-keyword", "keyword", note="쿠폰명 · 코드, max:100")
NAME("q-type", "type", value="percent · fixed")
DEVNAME('<option value="RATE">정률 (%)</option>', "type", value="percent")
DEVNAME('<option value="FIXED">정액 (원)</option>', "type", value="fixed")
NAME("q-method", "issue_method", value="auto · bulk · code")
DEVNAME('<option value="AUTO">자동 발급 (회원가입 웰컴 등)</option>', "issue_method", value="auto")
DEVNAME('<option value="BULK">수동 대량 발급 (그룹·태그 타겟)</option>', "issue_method", value="bulk")
DEVNAME('<option value="CODE">코드 입력형 (오프라인·카페 코드)</option>', "issue_method", value="code")
NAME("q-status", "status", value="issuing · suspended · ended")
DEVNAME('<option value="ACTIVE">발급중 (기간 내 발급 가능)</option>', "status", value="issuing")
DEVNAME('<option value="PAUSED">발급중지 (신규 차단·기발급분 사용가능)</option>', "status", value="suspended (저장값 disabled)")
DEVNAME('<option value="EXPIRED">기간종료 (유효기간 만료)</option>', "status", value="ended")
ACT("renderMasterGrid", route="admin.coupons.index", method="GET", url=A + "/coupons", perm="조회", note="개발 추가 필터: date_from · date_to(등록일)")
ACT("downloadExcelReport", route="admin.coupons.download", method="GET", url=A + "/coupons/download", perm="다운로드", note="반출 사유 공용 모달 layerReason")
R('<tr onclick="openFormEdit(${c.no})">', '<tr' + attrs(route="admin.coupons.show", method="GET", url=A + "/coupons/{coupon}", perm="조회", note="개발 상세 = 지급 회원 목록(uc_status 필터)") + ' onclick="openFormEdit(${c.no})">')
R('<button type="button" class="btn btn-sm" onclick="openFormEdit(${c.no})">상세/수정</button>',
  '<button type="button" class="btn btn-sm"' + attrs(route="admin.coupons.edit", method="GET", url=A + "/coupons/{coupon}/edit", perm="수정",
  note="개발 행 동작 메뉴 rowActionMenu: 지급 · 발급 중지 · 긴급 사용 중지(최고 관리자) · 공개 전환 · 비고 이력") + ' onclick="openFormEdit(${c.no})">상세/수정</button>\n'
  '              <button type="button" class="btn btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.coupons.issue.store", method="POST", url=A + "/coupons/{coupon}/issue", perm="등록",
  name="user_ids_text | user_ids_file", note="couponIssueModal — 회원 식별자 줄 입력(max:20000) 또는 xlsx 2MB. 양식 admin.coupons.issue-template.create") + '>지급</button>\n'
  '              <button type="button" class="btn btn-sm" data-dev-flag="dev-only"' + attrs(route="admin.coupons.emergency-status.update", method="PUT", url=A + "/coupons/{coupon}/emergency-status", perm="수정 + 최고 관리자",
  name="reason", note="couponEmergencyModal — 사유 10~500자. 보유분까지 사용 불가") + '>긴급 중지</button>')

# ── 002 등록 · 수정 (CouponRequest) ─────────────────────
ACT("triggerP1Demo", count=2, flag="proto-only", note="P1 시연 버튼 — 개발은 저장 시 서버 검증 후 cap_alert로 couponCapAlert를 띄움")
NAME("f-name", "name", note="max:30")
R('id="f-code"', 'id="f-code"' + attrs(note="개발 code는 코드 입력형 쿠폰 코드(등록만 · ^[A-Z0-9_]+$ · max:50, 수정 불가) — 아래 '사용자 입력 코드' 칸"))
R('onclick="setCouponType(\'RATE\')"', 'data-dev-name="type" data-dev-value="percent" onclick="setCouponType(\'RATE\')"')
R('onclick="setCouponType(\'FIXED\')"', 'data-dev-name="type" data-dev-value="fixed" onclick="setCouponType(\'FIXED\')"')
NAME("f-val", "discount_value", note="coupon-discount — 정률 1~40 정수 / 정액 1,000~200,000 · 1,000원 단위. 초과 시 cap_alert(P1)")
NAME("f-min-order", "min_order_amount", note="0 · 비움 = 제한 없음")
R('onclick="setExpMode(\'DN\')"', 'data-dev-name="expire_mode" data-dev-value="days" onclick="setExpMode(\'DN\')"')
R('onclick="setExpMode(\'ABS\')"', 'data-dev-name="expire_mode" data-dev-value="fixed" onclick="setExpMode(\'ABS\')"')
NAME("f-exp-days", "expire_days", note="1~3650 (기본 21)")
R('id="f-exp-start"', 'id="f-exp-start" data-dev-flag="proto-only" data-dev-note="절대 기간 시작일 — 개발은 종료일 expire_at 하나"')
NAME("f-exp-end", "expire_at", note="오늘 이후(그날 자정까지)")
NAME("f-limit-total", "max_issue_count", note="coupon-max-issue — 비우면 무제한")
NAME("f-limit-unlim", "unlimited", value="1", note="coupon-unlimited")
NAME("f-limit-per", "max_per_user", note="비우면 1")
# v6.92: f-dup-coupon(다른 쿠폰 중복 허용 체크) 삭제(결정 반영, D-BRD-04) — '1주문 1쿠폰' 고정 표시로
R('id="f-one-coupon-fixed"', 'id="f-one-coupon-fixed"' + attrs(name="allow_stack_coupon", value="0", note="개발 coupons.allow_stack_coupon 기본 0 — 폼 입력 없음(1주문 1쿠폰 고정, v6.92 D-BRD-04)"))
NAME("f-dup-point", "allow_with_point", value="1")
R('onclick="setTargetScope(\'ALL\')"', 'data-dev-name="target_scope" data-dev-value="all" onclick="setTargetScope(\'ALL\')"')
R('onclick="setTargetScope(\'CAT\')"', 'data-dev-name="target_scope" data-dev-value="selected + target_category_ids[]" onclick="setTargetScope(\'CAT\')"')
R('onclick="setTargetScope(\'ITEM\')"', 'data-dev-name="target_scope" data-dev-value="selected + target_course_ids[] · target_package_ids[]" onclick="setTargetScope(\'ITEM\')"')
R('onclick="showToast(\'적용 대상 카테고리가 추가되었습니다.\')"', 'data-dev-name="target_category_ids[]" data-dev-note="카테고리 최대 200 · 강좌/패키지 각 500, 교재 없음" onclick="showToast(\'적용 대상 카테고리가 추가되었습니다.\')"')
R('onclick="setIssueMethod(\'AUTO\')"', 'data-dev-name="issue_method" data-dev-value="auto" onclick="setIssueMethod(\'AUTO\')"')
R('onclick="setIssueMethod(\'BULK\')"', 'data-dev-name="issue_method" data-dev-value="bulk" onclick="setIssueMethod(\'BULK\')"')
R('onclick="setIssueMethod(\'CODE\')"', 'data-dev-name="issue_method" data-dev-value="code" onclick="setIssueMethod(\'CODE\')"')
NAME("tg-select", "target_group_id", note="coupon-target-group — 사용 중 회원 그룹 · 태그(user_groups.id)")
R("onclick=\"showToast('ADMN-USER-006", attrs(route="admin.coupons.target-count.index", method="GET", url=A + "/coupons/target-count", perm="조회", note="previewCount() — 대상 수 JSON").lstrip() + " onclick=\"showToast('ADMN-USER-006")
R('id="row-promo-code"', 'id="row-promo-code"' + attrs(name="code", note="코드 입력형 쿠폰 코드 — 등록만 · ^[A-Z0-9_]+$ · 중복 불가"))
R('<input type="datetime-local" class="form-input" value="2026-08-25T10:00" />', '<input type="datetime-local" class="form-input" name="scheduled_at" value="2026-08-25T10:00" />')
R('<input type="checkbox" checked /> 발급 알림톡 동시 발송', '<input type="checkbox" name="send_notification" value="1" checked /> 발급 알림톡 동시 발송')
R('                    <!-- 발급 예약 -->',
  '                    <tr data-dev-flag="dev-only" data-dev-note="개발 CouponRequest: is_public(공개 전환 admin.coupons.visibility.update) · memo(비고 max:500, 이력 admin.coupons.memo-history.index)">\n'
  '                      <th>공개 · 비고</th>\n'
  '                      <td>\n'
  '                        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">\n'
  '                          <label style="display:inline-flex; align-items:center; gap:5px; font-weight:700;"><input type="checkbox" name="is_public" value="1" /> 사용자 페이지 공개</label>\n'
  '                          <input type="text" name="memo" class="form-input" style="width:360px;" maxlength="500" placeholder="비고 (중지 사유 등, 500자)" />\n'
  '                        </div>\n'
  '                      </td>\n'
  '                    </tr>\n\n'
  '                    <!-- 발급 예약 -->')
ACT("pauseCurrentCoupon", route="admin.coupons.status.update", method="PUT", url=A + "/coupons/{coupon}/status", perm="수정", name="memo", note="couponSuspendModal — 중지 사유 → 비고(max:500)")
ACT("saveCouponMaster", route="admin.coupons.store | admin.coupons.update", method="POST | PUT", url=A + "/coupons | /coupons/{coupon}", perm="등록 | 수정",
    note="등록은 form_token(1회용 40자) 필수. 발급 이력이 있으면 종류 · 할인값 · 유효기간 잠금")
R('id="sim-lec"', 'id="sim-lec" data-dev-flag="proto-only" data-dev-note="Cap 시뮬레이터 입력 — 개발은 고정 예시 문구(cap-sim)"')
R('id="sim-book"', 'id="sim-book" data-dev-flag="proto-only" data-dev-note="Cap 시뮬레이터 입력 — 개발 없음"')
ACT("focusBackToDiscountInput", count=3, note="개발 couponCapAlertOk — 할인값 칸으로 포커스")

# ── PROM-003 포인트 정책 (사이트 설정 ③ 포인트) ──────────
R('<input type="checkbox" checked /> 자동 지급 사용', '<input type="checkbox" checked data-dev-note="개발은 welcome_point=0이면 미지급" /> 자동 지급 사용')
R('<input type="number" class="form-input" style="width:110px; font-weight:800;" value="5000" />',
  '<input type="number" class="form-input" style="width:110px; font-weight:800;" name="welcome_point" value="5000" data-dev-note="0~100000 (DI 생애 1회)" />')
R('<input type="number" class="form-input" style="width:80px; font-weight:800;" value="1" step="0.5" />',
  '<input type="number" class="form-input" style="width:80px; font-weight:800;" name="point_earn_rate" value="1" step="0.5" data-dev-note="0~10(%)" />')
R('id="pol-review"', 'id="pol-review" data-dev-flag="proto-only" data-dev-note="일반 후기 보상 P — 개발 site_settings에 없음(우수 후기는 BRD-005-S1에서 금액 직접 입력)"')
R('id="pol-best"', 'id="pol-best" data-dev-flag="proto-only" data-dev-note="베스트 · 합격수기 보상 P — 개발 없음"')
R('id="pol-cap"', 'id="pol-cap" data-dev-flag="proto-only" data-dev-note="무상 포인트 잔액 상한 — 개발 없음(정책 질문)"')
R('                <tr>\n                  <th>포인트 사용 기준 · 유효기간</th>',
  '                <tr data-dev-flag="dev-only" data-dev-note="SiteSettingRequest ③ 포인트: earn_rounding · deduct_priority · expire_notice_days · expire_notice_alimtalk/lms/email · paid_restore_grace_days · free/paid_point_expire_years · point_change_reason">\n'
  '                  <th>적립 단수 · 소멸 안내 · 변경 사유</th>\n'
  '                  <td>\n'
  '                    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">\n'
  '                      <select name="earn_rounding" class="form-select"><option value="ceil">올림</option><option value="floor">버림</option><option value="round">반올림</option></select>\n'
  '                      <span>무상 유효</span><input type="number" name="free_point_expire_years" class="form-input" style="width:60px;" min="1" max="10" value="2" /><span>년</span>\n'
  '                      <span>유상 유효</span><input type="number" name="paid_point_expire_years" class="form-input" style="width:60px;" min="1" max="10" value="5" /><span>년</span>\n'
  '                      <span>소멸 안내</span><input type="number" name="expire_notice_days" class="form-input" style="width:60px;" min="0" max="90" value="30" /><span>일 전</span>\n'
  '                      <input type="text" name="point_change_reason" class="form-input" style="width:240px;" maxlength="200" placeholder="변경 사유 (포인트 항목이 바뀌면 필수)" />\n'
  '                    </div>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n                  <th>포인트 사용 기준 · 유효기간</th>')
ACT("savePointPolicy", route="admin.site-settings.update", method="PUT", url=A + "/site-settings", perm="수정(사이트 설정 메뉴)", note="정책 변경 이력 pointHistory(admin_logs)")
R('<th>거래 ID / 일시</th>', '<th data-dev-flag="proto-only" data-dev-route="admin.points.index (규칙)" data-dev-method="GET" data-dev-url="' + A + '/points" data-dev-perm="조회" data-dev-note="포인트 원장 전체 목록 — 개발 미구현(point_logs). 회원별은 회원 상세">거래 ID / 일시</th>')
ACT("openPointModal", note="개발은 회원 상세(ADMN-USER-002-P1) layerPointGrant")
NAME("pt-member", "member", note="개발은 회원 상세 경로 {member}")
NAME("pt-amt", "amount", note="개발 MemberPointRequest: direction · amount · reason_code · reason(10~200자) · expire_preset")
ACT("confirmPointGrant", route="admin.members.points.store", method="POST", url=A + "/members/{member}/points", perm="등록(회원관리 메뉴)")

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("등록 폼", "openFormNew()", "#view-form"),
    ("수정 폼", "openFormEdit(MASTER_COUPONS[0].no)", "#view-form"),
    ("포인트 정책", "switchSubView('point')", "#view-point"),
    ("목록 복귀", "openFormNew(); switchSubView('list')", "#view-list"),
    # couponCapAlert(modal-p1) · layerPointGrant(modal-point)는 clean 원본에서도 열리지 않음(show 클래스만 붙이고 핫픽스 인라인 display:none을 안 지움) — 원본 문제라 VERIFY에서 뺌
    ("코드 입력형", "openFormNew(); setIssueMethod('CODE')", "#row-promo-code"),
    ("절대 기간", "openFormNew(); setExpMode('ABS')", "#exp-abs-box"),
]
