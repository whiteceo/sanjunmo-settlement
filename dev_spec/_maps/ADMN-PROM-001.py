"""ADMN-PROM-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PROM-001.md
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
    "code": "ADMN-PROM-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(PROM-001 · S1 · S2 · S3). 랜딩 배너 PC · 모바일 · alt, 상태 직접 선택, 행별 차단 표시, Beautify, 주소 · 소스 복사는 개발 없음 — 주황 표시",
    "menus": [
        {"route": "admin.promotions.index", "label": "이벤트 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# 개발 S1 · S2 · S3는 별도 페이지. 프로토타입 SJM_PAGE 구획(view-list · view-detail · view-form)에 개발 id를 단다
R('<section id="view-form" class="view-panel subview-panel" data-subpage="form">',
  '<section id="view-form" class="view-panel subview-panel" data-subpage="form"' + attrs(note="개발 폼 id promo-form (S3). S1 차단은 별도 페이지 blockForm") + '>')
R('id="promo-role-sim"', 'id="promo-role-sim" data-dev-flag="proto-only" data-dev-note="역할 그룹 시연 — 개발은 로그인 관리자 권한"')

# ── 001 목록 ─────────────────────────────────────────
ACT("setCategoryFilter", count=3, route="admin.promotions.index", method="GET", url=A + "/promotions", perm="조회", name="type", value="'' · promotion · event")
ACT("filterBlockOnly", flag="proto-only", note="KPI 중복 할인 차단 작동중 — 개발 없음")
R('<button type="button" class="btn btn-primary" data-perm-w="promo" onclick="openPromoFormNew()">',
  '<button type="button" class="btn" data-dev-flag="dev-only"' + attrs(route="admin.promotions.download", method="GET", url=A + "/promotions/download", perm="다운로드",
  note="반출 사유 공용 모달 layerReason(reason · reason_etc · reason_ref)") + '>엑셀 다운로드</button>\n'
  '              <button type="button" class="btn btn-primary" data-perm-w="promo"' + attrs(route="admin.promotions.create", method="GET", url=A + "/promotions/create", perm="등록") + ' onclick="openPromoFormNew()">')
NAME("flt-cat", "type", value="promotion · event")
DEVNAME('<option value="PROMO">기획전 (기획상품)</option>', "type", value="promotion")
DEVNAME('<option value="EVENT">이벤트 (일반이벤트)</option>', "type", value="event")
NAME("flt-status", "status", value="scheduled · active · ended · stopped(개발에만)")
DEVNAME('<option value="ACTIVE">진행중</option>', "status", value="active")
DEVNAME('<option value="READY">예약 (노출 대기)</option>', "status", value="scheduled")
DEVNAME('<option value="ENDED">종료</option>', "status", value="ended")
R('id="flt-block"', 'id="flt-block" data-dev-flag="proto-only" data-dev-note="차단 ON/OFF 필터 — 개발 없음. 개발 추가 필터: period_from · period_to · sort(started_asc · started_desc)"')
NAME("flt-kw", "keyword", note="max:100")
R("onclick=\"openPromoDetail('${item.code}')\"", attrs(route="admin.promotions.show", method="GET", url=A + "/promotions/{promotion}", perm="조회").lstrip() + " onclick=\"openPromoDetail('${item.code}')\"")
R("onclick=\"openPromoEdit('${item.code}')\"", attrs(route="admin.promotions.edit", method="GET", url=A + "/promotions/{promotion}/edit", perm="수정",
  note="차단 설정은 별도 페이지 admin.promotions.blocks.edit(GET /promotions/{promotion}/blocks/edit)").lstrip() + " onclick=\"openPromoEdit('${item.code}')\"")

# ── 001-S2 상세 ─────────────────────────────────────
R('<button type="button" class="btn" onclick="copyPromoDetailUrl()">',
  '<button type="button" class="btn btn-danger" data-dev-flag="dev-only"' + attrs(route="admin.promotions.status.update", method="PUT", url=A + "/promotions/{promotion}/status", perm="수정",
  name="reason", note="즉시 중단 promotionStopModal — reason 2~200자 필수. 중단 후 수정 · 차단 잠금(정책 질문: 비노출 강제 숨김과 같은지)") + '>⏹ 즉시 중단</button>\n'
  '              <button type="button" class="btn" data-dev-flag="proto-only" data-dev-note="주소 복사 — 개발 없음" onclick="copyPromoDetailUrl()">')
ACT("togglePromoDetailPreview", route="admin.promotions.preview.show", method="GET", url=A + "/promotions/{promotion}/preview", perm="조회", note="개발은 저장본 미리보기 새 창")
ACT("editCurrentPromoDetail", count=2, route="admin.promotions.edit", method="GET", url=A + "/promotions/{promotion}/edit", perm="수정")
ACT("copyPromoDetailSource", count=3, flag="proto-only", note="소스 복사 — 개발 없음")

# ── 001-S3 등록 · 수정 (promo-form, PromotionRequest) ──────
ACT("savePromoItem", route="admin.promotions.store | admin.promotions.update", method="POST | PUT", url=A + "/promotions | /promotions/{promotion}", perm="등록 | 수정")
ACT("openFullPreviewModal", route="admin.promotions.preview.index", method="POST", url=A + "/promotions/preview", perm="조회(저장 안 함)", note="개발 promo-preview — 작성 중 소스 미리보기")
DEVNAME('name="promo_cat" id="cat-radio-promo" value="PROMO"', "type", value="promotion")
DEVNAME('name="promo_cat" id="cat-radio-event" value="EVENT"', "type", value="event")
NAME("f-promo-title", "title", note="max:40 (Promotion::MAX_TITLE_LENGTH)")
R('id="f-promo-code"', 'id="f-promo-code"' + attrs(note="개발은 서버 자동 채번 PRM-YYMM-NNN, 입력 없음 · 수정 불가"))
R('<span class="badge badge-ok" id="slug-valid-badge">',
  '<button type="button" class="btn btn-xs" id="promo-slug-check" data-dev-flag="dev-only"' + attrs(route="admin.promotions.slug.index", method="GET", url=A + "/promotions/slug", perm="조회",
  note="Slug 중복 확인(JSON) — 결과 promo-slug-result") + '>중복 확인</button>\n'
  '                      <span class="badge badge-ok" id="slug-valid-badge">')
NAME("f-promo-slug", "slug", note="promo-slug — 2~40 · ^[a-z0-9]+(-[a-z0-9]+)*$ · 중복 불가(종료 · 중단 포함)")
NAME("f-promo-start", "started_at", note="Y-m-d\\TH:i")
NAME("f-promo-end", "ended_at", note="started_at 이후")
R('id="f-promo-status"', 'id="f-promo-status" data-dev-flag="proto-only" data-dev-note="상태 직접 선택 — 개발은 기간 · 배치로 자동(scheduled · active · ended), 중단은 별도 동작(stopped)"')
R('                <tr>\n                  <th>PC · 모바일 목록 배너',
  '                <tr data-dev-flag="dev-only" data-dev-note="PromotionRequest: thumbnail(등록 때 필수 · jpg · png · webp · 1MB) · headline · sort_type">\n'
  '                  <th>목록 썸네일 · 상단 카피 · 진열 순서</th>\n'
  '                  <td>\n'
  '                    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">\n'
  '                      <input type="file" name="thumbnail" accept=".jpg,.jpeg,.png,.webp" class="form-input" />\n'
  '                      <input type="text" name="headline" class="form-input" style="width:280px;" maxlength="255" placeholder="상단 카피 (비우면 기획전명)" />\n'
  '                      <select name="sort_type" class="form-select"><option value="manual">수동 정렬</option><option value="sales">판매량순</option><option value="price_asc">낮은 가격순</option><option value="created_desc">등록 역순</option></select>\n'
  '                    </div>\n'
  '                  </td>\n'
  '                </tr>\n'
  '                <tr>\n                  <th>PC · 모바일 목록 배너')
R('id="f-banner-pc"', 'id="f-banner-pc" data-dev-flag="proto-only" data-dev-note="랜딩 배너 — 개발 폼 미연결(banner_pc_path 스키마만, 정책 질문)"')
R('id="f-banner-mo"', 'id="f-banner-mo" data-dev-flag="proto-only" data-dev-note="banner_mobile_path — 개발 폼 미연결"')
R('id="f-banner-alt"', 'id="f-banner-alt" data-dev-flag="proto-only" data-dev-note="배너 alt — 개발 없음"')
NAME("inp-new-asset-name", "files[]", note="promo-asset-input — 1~20개 · jpg · png · webp · gif · mp4 · webm · woff · woff2 · 개당 20MB")
ACT("uploadNewS3Asset", route="admin.promotions.assets.store", method="POST", url=A + "/promotions/{promotion}/assets", perm="등록", note="기획전 id가 있어야 올림(수정 화면). 지우기는 admin.promotions.assets.destroy")
ACT("beautifyCurrentCode", flag="proto-only", note="코드 자동 정렬 — 개발 없음")
ACT("validatePromoCodeSecurity", note="개발 promo-lint · lintHtml() · lintBraces() (클라이언트 점검)")
R('id="cm-code-input"', 'id="cm-code-input"' + attrs(name="html_content | css_content | js_content", note="개발은 소스 3분할 textarea(promo-source-html · -css · -js), 각 최대 1,000,000자"))

# ── 001-S1 중복 할인 차단 (blockForm) ──────────────────
NAME("chk-bulk-disable", "enabled", value="1 · 0(모든 기획전에서 해제)", note="개발 S1은 별도 페이지 admin.promotions.blocks.edit")
NAME("chk-block-cpn", "benefits[]", value="coupon")
NAME("chk-block-pt", "benefits[]", value="point")
NAME("chk-block-earn", "benefits[]", value="earn")
R('<div id="bulk-disable-config-box"',
  '<div data-dev-flag="dev-only" data-dev-note="PromotionBlockRequest: block_from · block_to(차단 기간, 노출 기간과 별개) · target(all · selected) + product_ids[] · reason(max:100, 주문서 혜택 입력란 아래 노출)" '
  'style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:10px; font-size:12px;">\n'
  '                  <strong>차단 기간</strong> <input type="date" id="blockFrom" name="block_from" class="form-input" /> ~ <input type="date" name="block_to" class="form-input" />\n'
  '                  <select name="target" class="form-select"><option value="all">전체 대상 상품</option><option value="selected">선택 상품</option></select>\n'
  '                  <input type="text" name="reason" class="form-input" style="width:280px;" maxlength="100" placeholder="주문서에 보일 차단 사유" />\n'
  '                  <button type="button" class="btn btn-xs btn-primary"' + attrs(route="admin.promotions.blocks.update", method="PUT", url=A + "/promotions/{promotion}/blocks", perm="수정") + '>차단 저장</button>\n'
  '                </div>\n'
  '                <div id="bulk-disable-config-box"')
NAME("sel-add-prod", "products[n][type|id]", note="개발 promo-target-type · promo-target-keyword · promo-target-search(GET admin.promotions.targets.index JSON). 행: products[n][type|id|promo_price|discount_rate], 1~500행")
ACT("addMappedProduct", note="개발 addRow() — products[n][…] 행 추가")
ACT("removeMappedProd", count=2)

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("상세 S2", "openPromoDetail(PROMO_ITEMS[0].code)", "#view-detail"),
    ("신규 등록 S3", "openPromoFormNew()", "#view-form"),
    ("수정 S3", "openPromoEdit(PROMO_ITEMS[0].code)", "#view-form"),
    ("목록 복귀", "openPromoFormNew(); switchPromoView('list')", "#view-list"),
    ("코드 탭 CSS", "openPromoFormNew(); switchCodeTab('CSS')", "#cm-code-input"),
    ("모바일 미리보기", "openPromoFormNew(); setPreviewViewport('375px')", "#view-form"),
]
