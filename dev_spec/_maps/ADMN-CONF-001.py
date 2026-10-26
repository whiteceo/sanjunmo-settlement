"""ADMN-CONF-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-CONF-001.md
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
    "code": "ADMN-CONF-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(CONF-001 · S1 띠배너 · S2 모달 팝업). 사용자 메인 미리보기(preview_token)는 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.display.index", "label": "전시/메뉴 관리 (배너 · 띠배너 · 팝업 공용 권한)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 상단 · 탭 ────────────────────────────────────────
R('<button type="button" class="btn btn-sm btn-outline" onclick="showToast(\'프론트 미리보기 토큰',
  '<button type="button" class="btn btn-sm btn-outline"' + attrs(flag="proto-only", route="admin.display.preview.show (규칙)", method="GET", url=A + "/display/preview?preview_token=", perm="조회",
                                                                note="사용자 메인 미리보기 — 개발은 띠배너 폼 안 미리보기(#stripPreview)만") + ' onclick="showToast(\'프론트 미리보기 토큰')
R('id="tab-domain-banner" onclick=', 'id="tab-domain-banner"' + attrs(route="admin.display.index", method="GET", url=A + "/display?tab=main_slide", perm="조회") + ' onclick=')
R('id="tab-domain-strip" onclick=', 'id="tab-domain-strip"' + attrs(route="admin.display.index", method="GET", url=A + "/display?tab=strip", perm="조회") + ' onclick=')
R('id="tab-domain-popup" onclick=', 'id="tab-domain-popup"' + attrs(route="admin.display.index", method="GET", url=A + "/display?tab=modal", perm="조회") + ' onclick=')
R('<button type="button" class="inner-tab" id="tab-domain-strip"',
  '<button type="button" class="inner-tab" id="tab-domain-event-list" data-dev-flag="dev-only"' + attrs(route="admin.display.index", method="GET", url=A + "/display?tab=event_list", perm="조회",
                                                                                                     note="개발 탭 event_list = 배너 position event_list_top (DisplayController::TABS)")
  + ' onclick="showToast(\'이벤트 목록 상단 배너(event_list_top) — 메인 슬라이드 배너와 같은 폼을 씁니다.\')">🗂️ 이벤트 목록 상단 배너</button>\n'
  '        <button type="button" class="inner-tab" id="tab-domain-strip"')

# ── 001 메인 슬라이드 배너 ────────────────────────────
R('onclick="showToast(\'변경된 배너 노출 순서가 저장되었습니다.\')"',
  attrs(route="admin.display.banners.order.update", method="PUT", url=A + "/banners/order", perm="수정", note="#reorderForm: orders[n][id] · orders[n][sort_order] · position(hero · event_list_top)").lstrip()
  + ' onclick="showToast(\'변경된 배너 노출 순서가 저장되었습니다.\')"')
R('onclick="openBannerDetail(null)"', attrs(route="admin.display.banners.create", method="GET", url=A + "/banners/create", perm="등록").lstrip() + ' onclick="openBannerDetail(null)"')
R('class="btn btn-sm btn-outline" onclick="openBannerDetail(${i})"',
  'class="btn btn-sm btn-outline"' + attrs(route="admin.display.banners.edit", method="GET", url=A + "/banners/{banner}/edit", perm="수정") + ' onclick="openBannerDetail(${i})"')
R('<div class="card-body" style="padding:0;">\n            <table class="data-table">\n              <thead>\n                <tr>\n                  <th style="width:90px;">노출 순서</th>',
  '<div class="card-body" style="padding:0;">\n'
  '            <div style="display:flex; gap:8px; align-items:center; padding:10px 14px;" data-dev-flag="dev-only" data-dev-note="개발 목록 필터: title · is_active(1/0) · exposure_status(live · reserved · ended · stopped)">\n'
  '              <input type="text" class="f-input" name="title" placeholder="배너명 검색" style="width:200px;" />\n'
  '              <select class="f-select" name="is_active" style="width:110px;"><option value="">사용 전체</option><option value="1">사용</option><option value="0">미사용</option></select>\n'
  '              <select class="f-select" name="exposure_status" style="width:130px;"><option value="">노출 상태 전체</option><option value="live">노출중</option><option value="reserved">예약</option><option value="ended">종료</option><option value="stopped">중지</option></select>\n'
  '            </div>\n'
  '            <table class="data-table">\n              <thead>\n                <tr>\n                  <th style="width:90px;">노출 순서</th>')
NAME("bd-name", "title")
NAME("bd-device", "device", value="all · pc · mobile (프로토 값 '공통(PC+MO)' · 'PC 전용' · '모바일 전용')")
NAME("bd-order", "sort_order")
NAME("bd-pc-img", "image", note="jpg · jpeg · png · webp 5MB, svg 차단")
NAME("bd-alt", "alt_text")
NAME("bd-mo-img", "mobile_image")
R('value="main_allpass_2026_mo.webp (750×620px · 198KB)" />',
  'value="main_allpass_2026_mo.webp (750×620px · 198KB)" />\n'
  '                    <input type="text" class="f-input" name="mobile_alt_text" style="width:100%; margin-bottom:6px;" placeholder="모바일 대체 텍스트(선택)" data-dev-flag="dev-only" data-dev-note="BannerRequest mobile_alt_text · 이미지 삭제 체크 delete_image · delete_mobile_image" />')
NAME("bd-url", "link_url", note="DisplayLinkUrl 규칙(/ 또는 https://)")
NAME("bd-target", "link_target", value="_self · _blank")
DEVNAME('id="bd-period"', "start_at · end_at", note="프로토 문자열 1칸 → 개발 날짜 2칸")
NAME("bd-status", "is_active", value="1 사용 / 0 미사용 (노출중 · 예약 · 종료는 기간으로 계산한 exposure_status)")
R('id="btn-save-banner" onclick=', 'id="btn-save-banner"' + attrs(route="admin.display.banners.store | admin.display.banners.update", method="POST | PUT", url=A + "/banners | /banners/{banner}", perm="등록 | 수정") + ' onclick=')

# ── S1 띠배너 ──────────────────────────────────────
R('onclick="openStripDetail(null)"', attrs(route="admin.display.strip-banners.create", method="GET", url=A + "/display/strip-banners/create", perm="등록").lstrip() + ' onclick="openStripDetail(null)"')
R('class="btn btn-sm btn-outline" onclick="openStripDetail(${i})"',
  'class="btn btn-sm btn-outline"' + attrs(route="admin.display.strip-banners.edit", method="GET", url=A + "/display/strip-banners/{stripBanner}/edit", perm="수정") + ' onclick="openStripDetail(${i})"')
NAME("sd-loc", "position", value="event_top · course_list_top (+ 개발 main_slide_bottom)")
R('<option value="강좌 목록 상단 (USER-LECT-002)">강좌 목록 상단 (USER-LECT-002)</option>',
  '<option value="강좌 목록 상단 (USER-LECT-002)">강좌 목록 상단 (USER-LECT-002)</option>\n'
  '                      <option value="메인 슬라이드 배너 하단" data-dev-flag="dev-only" data-dev-value="main_slide_bottom">메인 슬라이드 배너 하단</option>')
NAME("sd-target", "target", value="guest 비로그인 · member 로그인 · all 전체")
NAME("sd-text", "title", note="max 40 (Banner::STRIP_TEXT_MAX)")
NAME("sd-bg", "bg_color")
NAME("sd-fg", "text_color")
R('id="sd-contrast-badge"', 'id="sd-contrast-badge"' + attrs(note="개발 #stripRatio 명도 대비 표시"))
NAME("sd-url", "link_url")
DEVNAME('id="sd-period"', "always · start_at · end_at", note="'상시 노출' = always=1")
R('<th>이동 URL / 노출 기간</th>',
  '<th data-dev-flag="dev-only" data-dev-note="StripBannerRequest devices[] (1개 이상) · link_blank">노출 기기 / 새 창</th>\n'
  '                  <td colspan="3" data-dev-flag="dev-only">\n'
  '                    <label style="margin-right:12px;"><input type="checkbox" name="devices[]" value="pc" checked /> PC</label>\n'
  '                    <label style="margin-right:12px;"><input type="checkbox" name="devices[]" value="mobile" checked /> 모바일</label>\n'
  '                    <label><input type="checkbox" name="link_blank" value="1" /> 새 창으로 열기</label>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n'
  '                  <th>이동 URL / 노출 기간</th>')
R('onclick="saveStripItem()"', attrs(route="admin.display.strip-banners.store | admin.display.strip-banners.update", method="POST | PUT",
                                     url=A + "/display/strip-banners | /display/strip-banners/{stripBanner}", perm="등록 | 수정").lstrip() + ' onclick="saveStripItem()"')

# ── S2 모달 팝업 ────────────────────────────────────
R('onclick="openPopupDetail(null)"', attrs(route="admin.display.popups.create", method="GET", url=A + "/popups/create", perm="등록").lstrip() + ' onclick="openPopupDetail(null)"')
R('class="btn btn-sm btn-outline" onclick="openPopupDetail(${i})"',
  'class="btn btn-sm btn-outline"' + attrs(route="admin.display.popups.edit", method="GET", url=A + "/popups/{popup}/edit", perm="수정") + ' onclick="openPopupDetail(${i})"')
NAME("pd-name", "title")
NAME("pd-device", "device", value="all · pc · mobile")
NAME("pd-order", "sort_order")
DEVNAME('name="pd_link_mode" value="BOARD"', "link_type", value="post")
DEVNAME('name="pd_link_mode" value="URL"', "link_type", value="url")
NAME("pd-board-sel", "post_id", note="값 = posts.id")
NAME("pd-url", "link_url")
DEVNAME('id="pd-img"', "image · mobile_image · alt_text")
DEVNAME('id="pd-period"', "start_at · end_at")
NAME("pd-status", "is_active", value="1 / 0")
R('                  <th>PC / 모바일 팝업 이미지 *</th>',
  '                  <th data-dev-flag="dev-only" data-dev-note="PopupRequest position_type(center · custom) · pos_x · pos_y · width · height">위치 / 크기</th>\n'
  '                  <td data-dev-flag="dev-only">\n'
  '                    <select class="f-select" name="position_type" style="width:120px;"><option value="center">화면 중앙</option><option value="custom">좌표 지정</option></select>\n'
  '                    <input type="number" class="f-input" name="pos_x" placeholder="X" style="width:60px;" /> <input type="number" class="f-input" name="pos_y" placeholder="Y" style="width:60px;" />\n'
  '                    <input type="number" class="f-input" name="width" placeholder="너비" style="width:70px;" /> <input type="number" class="f-input" name="height" placeholder="높이" style="width:70px;" />\n'
  '                  </td>\n'
  '                  <th data-dev-flag="dev-only" data-dev-note="use_today_close · use_week_close · use_close_button (boolean 필수)">닫기 옵션</th>\n'
  '                  <td data-dev-flag="dev-only">\n'
  '                    <label style="margin-right:10px;"><input type="checkbox" name="use_today_close" value="1" checked /> 오늘 하루 보지 않기</label>\n'
  '                    <label style="margin-right:10px;"><input type="checkbox" name="use_week_close" value="1" /> 일주일 보지 않기</label>\n'
  '                    <label><input type="checkbox" name="use_close_button" value="1" checked /> 닫기 버튼</label>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n'
  '                  <th>PC / 모바일 팝업 이미지 *</th>')
R('onclick="savePopupItem()"', attrs(route="admin.display.popups.store | admin.display.popups.update", method="POST | PUT", url=A + "/popups | /popups/{popup}", perm="등록 | 수정",
                                     note="redirect_from=display").lstrip() + ' onclick="savePopupItem()"')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("배너 목록", "switchDomainTab('banner')", "#panel-banner-list"),
    ("배너 신규", "openBannerDetail(null)", "#panel-banner-detail"),
    ("배너 수정", "openBannerDetail(0)", "#panel-banner-detail"),
    ("띠배너 목록", "switchDomainTab('strip')", "#panel-strip-list"),
    ("띠배너 상세", "openStripDetail(0)", "#panel-strip-detail"),
    ("팝업 목록", "switchDomainTab('popup')", "#panel-popup-list"),
    ("팝업 상세 · URL 모드", "openPopupDetail(0); document.querySelector('input[name=pd_link_mode][value=URL]').checked = true; togglePopupLinkMode()", "#pd-url-box"),
    ("팝업 저장", "openPopupDetail(null); savePopupItem()", "#panel-popup-list"),
]
