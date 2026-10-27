# ADMN-CONF-001 전시 배너 · 띠배너 · 모달 팝업 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-001_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-001 메인 슬라이드 배너 · ADMN-CONF-001-S1 띠배너 · ADMN-CONF-001-S2 모달 팝업
- 개발 진행: 구현(담당 이응민, `_index/progress.md` 104~106행 — S1 dev 배포 80a579d · 50fd206, S2 dev 반영)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.display.index` | 전시/메뉴 관리 | routes/admin.php:1088. 배너 · 팝업 · 띠배너 라우트 이름을 모두 `admin.display.*` 아래에 둬 이 메뉴 하나의 권한으로 판정(주석 routes/admin.php:1181-1183 — `admin.popups.*` 는 admin_menus 에 없어 최고 관리자 외 막혔음) |

- URL 은 `/{admin}/banners` · `/{admin}/popups` · `/{admin}/display/strip-banners` 로 서로 다르지만 이름은 `admin.display.banners.*` · `admin.display.popups.*` · `admin.display.strip-banners.*`.

## 2. 화면별 라우트

### ADMN-CONF-001 통합 목록(탭) · 메인 슬라이드 배너
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 통합 목록(`?tab=`) | GET | `/{admin}/display` | `admin.display.index` | can_view | DisplayController@index |
| 배너 목록(단독) | GET | `/{admin}/banners` | `admin.display.banners.index` | can_view | BannerController@index |
| 배너 등록 폼 | GET | `/{admin}/banners/create` | `admin.display.banners.create` | can_create | BannerController@create |
| 배너 등록 | POST | `/{admin}/banners` | `admin.display.banners.store` | can_create | BannerController@store |
| 노출 순서 일괄 저장 | PUT | `/{admin}/banners/order` | `admin.display.banners.order.update` | can_update | BannerController@reorder |
| 배너 수정 폼 | GET | `/{admin}/banners/{banner}/edit` | `admin.display.banners.edit` | can_update | BannerController@edit |
| 배너 수정 | PUT | `/{admin}/banners/{banner}` | `admin.display.banners.update` | can_update | BannerController@update |
| 배너 삭제 | DELETE | `/{admin}/banners/{banner}` | `admin.display.banners.destroy` | can_delete | BannerController@destroy |

- 탭 값(`DisplayController::TABS`): `main_slide` 메인 슬라이드 배너(기본) · `event_list` 이벤트 목록 상단 배너 · `strip` 띠배너 · `modal` 모달 팝업 — DisplayController.php:21-26, :36-45
- 탭 → 배너 position: `main_slide`→`hero`, `event_list`→`event_list_top` (Banner::DISPLAY_AREAS)

### ADMN-CONF-001-S1 띠배너
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/display?tab=strip` (`&position=`) | `admin.display.index` | can_view | DisplayController@index → stripIndex |
| 등록 폼 | GET | `/{admin}/display/strip-banners/create` | `admin.display.strip-banners.create` | can_create | StripBannerController@create |
| 등록 | POST | `/{admin}/display/strip-banners` | `admin.display.strip-banners.store` | can_create | StripBannerController@store |
| 순서 일괄 저장 | PUT | `/{admin}/display/strip-banners/order` | `admin.display.strip-banners.order.update` | can_update | StripBannerController@reorder |
| 수정 폼 | GET | `/{admin}/display/strip-banners/{stripBanner}/edit` | `admin.display.strip-banners.edit` | can_update | StripBannerController@edit |
| 수정 | PUT | `/{admin}/display/strip-banners/{stripBanner}` | `admin.display.strip-banners.update` | can_update | StripBannerController@update |
| 삭제 | DELETE | `/{admin}/display/strip-banners/{stripBanner}` | `admin.display.strip-banners.destroy` | can_delete | StripBannerController@destroy |

### ADMN-CONF-001-S2 모달 팝업
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(통합 화면은 `display?tab=modal`) | GET | `/{admin}/popups` | `admin.display.popups.index` | can_view | PopupController@index |
| 등록 폼 | GET | `/{admin}/popups/create` | `admin.display.popups.create` | can_create | PopupController@create |
| 등록 | POST | `/{admin}/popups` | `admin.display.popups.store` | can_create | PopupController@store |
| 순서 일괄 저장 | PUT | `/{admin}/popups/order` | `admin.display.popups.order.update` | can_update | PopupController@reorder |
| 수정 폼 | GET | `/{admin}/popups/{popup}/edit` | `admin.display.popups.edit` | can_update | PopupController@edit |
| 수정 | PUT | `/{admin}/popups/{popup}` | `admin.display.popups.update` | can_update | PopupController@update |
| 삭제 | DELETE | `/{admin}/popups/{popup}` | `admin.display.popups.destroy` | can_delete | PopupController@destroy |

## 3. 폼 필드 · 검증

### 배너 등록 · 수정 (BannerRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `position` | required · in POSITIONS | `hero` 메인 히어로 · `mid_left` · `mid_right` · `event_bottom` · `sub_top` · `event_list_top` | (탭으로 고정) |
| `device` | required · in DEVICES | `all` 공통 · `pc` · `mobile` | `#bd-device` |
| `title` | required · max:255 | — | `#bd-name` 배너 관리명 |
| `image` · `mobile_image` | nullable · image · jpg/jpeg/png/webp · 5MB · 실제 파일형 검사(svg 차단) | 권장 hero PC 1920×520 · MO 750×620 | `#bd-pc-img` · `#bd-mo-img` |
| `delete_image` · `delete_mobile_image` | nullable · boolean | — | (없음) |
| `alt_text` | required · max:255 | — | `#bd-alt` |
| `mobile_alt_text` | nullable · max:255 | — | (없음) |
| `link_url` | nullable · max:500 · DisplayLinkUrl | — | `#bd-url` |
| `link_target` | required · in | `_self` 현재 창 · `_blank` 새 창 | `#bd-target` |
| `start_at` · `end_at` | nullable · date · end ≥ start | — | `#bd-period`(문자열 1칸) |
| `sort_order` | nullable · integer ≥0 | — | `#bd-order` |
| `is_active` | required · boolean | 1 사용 / 0 미사용 | `#bd-status`(노출중 · 예약 · 노출중지) |
| `redirect_area` (hidden) | 컨트롤러가 읽음 | 저장 후 돌아갈 탭 | — |

### 순서 저장 (BannerReorderRequest · StripBannerReorderRequest · PopupReorderRequest)
| 필드 name | 규칙 |
|---|---|
| `orders[n][id]` · `orders[n][sort_order]` | required · integer · id distinct · sort_order ≥0 |
| `position` | 배너: required · in DISPLAY_AREAS 값(`hero` · `event_list_top`) / 띠배너: nullable · in STRIP_POSITIONS(돌아갈 필터) |

### 띠배너 (StripBannerRequest) — `#stripForm`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `position` | required · in STRIP_POSITIONS | `event_top` 메인 상단(헤더 위) · `main_slide_bottom` 메인 슬라이드 배너 하단 · `course_list_top` 강좌 목록 상단 | `#sd-loc` |
| `target` | required · in TARGETS | `all` 전체 · `guest` 비로그인 · `member` 로그인 | `#sd-target` |
| `title` | required · max:40 (`Banner::STRIP_TEXT_MAX`) | — | `#sd-text` |
| `bg_color` · `text_color` | required · `#RRGGBB` | — | `#sd-bg` · `#sd-fg` |
| `link_url` | nullable · max:500 · DisplayLinkUrl | — | `#sd-url` |
| `link_blank` | nullable · boolean | 새 창 | (없음) |
| `devices[]` | required · 1개 이상 · `pc` / `mobile` | — | (없음) |
| `always` | nullable · boolean | 상시 노출 | `#sd-period`("상시 노출") |
| `start_at` · `end_at` | always=1 이면 제외, 아니면 required · date · end ≥ start | — | `#sd-period` |
| `is_active` | required · boolean | — | (목록 상태) |

### 모달 팝업 (PopupRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `title` | required · max:255 | — | `#pd-name` |
| `image` · `mobile_image` · `delete_*` · `alt_text`(required) · `mobile_alt_text` | 배너와 같음 | — | `#pd-img` |
| `link_type` | required · in LINK_TYPES | `url` 링크 직접 입력 · `post` 등록된 게시물 선택 | 라디오 `BOARD` / `URL` |
| `post_id` | link_type=post 면 required · posts 존재 | — | `#pd-board-sel` |
| `link_url` · `link_target` | 배너와 같음 | `_self` · `_blank` | `#pd-url` |
| `position_type` | required · in | `center` 화면 중앙 · `custom` 좌표 지정 | (없음) |
| `pos_x` · `pos_y` · `width` · `height` | nullable · integer (크기 ≥0) | px | (없음) |
| `start_at` · `end_at` | nullable · date · end ≥ start | — | `#pd-period` |
| `device` | required · in | `all` · `pc` · `mobile` | `#pd-device` |
| `use_today_close` · `use_week_close` · `use_close_button` | required · boolean | 오늘 하루 · 일주일 안 보기 · 닫기 버튼 | (없음) |
| `sort_order` | nullable · integer ≥0 | — | `#pd-order` |
| `is_active` | required · boolean | — | `#pd-status` |
| `redirect_from` (hidden) | `display` 면 통합 화면으로 복귀 | — | — |

## 4. 목록 필터 · 정렬 · 표 컬럼
| 쿼리 name | 값 | 화면 |
|---|---|---|
| `tab` | `main_slide` · `event_list` · `strip` · `modal` | 통합 목록 |
| `title` | 문자열 | 배너 · 팝업 탭 |
| `is_active` | 1 / 0 | 〃 |
| `exposure_status` | `live` 노출중 · `reserved` 예약 · `ended` 종료 · `stopped` 중지 (HasExposureStatus) | 〃 |
| `position` | STRIP_POSITIONS | 띠배너 탭 |

- 정렬은 `sort_order`(드래그 · 이동 버튼 `data-move` 후 `#reorderForm` PUT). 메인 슬라이드 동시 노출 권장 상한 5개 초과 시 경고(`Banner::MAIN_SLIDE_MAX`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| banners.position | string(30) | 이미지 배너 위치 · 띠배너 위치 공용(위 코드값) | 탭 · 노출 위치 |
| banners.device | string(10) | `all` · `pc` · `mobile` | 노출 기기 |
| banners.target | string(10) | 띠배너 노출 대상 `all` · `guest` · `member`(이미지 배너는 all) | 띠배너 노출 대상 |
| banners.title | string(255) | 배너명 / 띠배너 문구 | 관리명 · 문구 |
| banners.bg_color · text_color | char(7) | 띠배너 색(이미지 배너 NULL) | 배경색 / 글자색 |
| banners.image_path · mobile_image_path · alt_text · mobile_alt_text | — | 이미지 · 대체 텍스트 | 규격 · 관리명 |
| banners.link_url · link_target | — | 클릭 이동 · `_self`/`_blank` | 이동 URL |
| banners.start_at · end_at · sort_order · is_active | — | 노출 기간 · 순서 · 사용 여부 | 기간 · 순서 · 상태 |
| popups.title · image_path · mobile_image_path · alt_text · mobile_alt_text | — | 팝업명 · 이미지 | 관리명 · 규격 |
| popups.link_type · post_id · link_url · link_target | — | 연결 방식 `url`/`post`, 게시글 posts.id | 연결 방식 |
| popups.position_type · pos_x · pos_y · width · height | — | `center`/`custom` 좌표 · 크기 | — |
| popups.device · use_today_close · use_week_close · use_close_button | — | 노출 대상 · 닫기 옵션 | 노출 기기 |
| popups.start_at · end_at · sort_order · is_active | — | 기간 · 순서 · 사용 | 기간 · 상태 |

- 노출 상태는 저장값이 아니라 `is_active` + 기간으로 계산(`live`/`reserved`/`ended`/`stopped`) — app/Models/Concerns/HasExposureStatus.php:12-22

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `display/_head.blade.php` 탭 링크(`?tab=`) | 3+1 탭(페이지 이동) | `switchDomainTab()` |
| `#reorderForm` · `[data-move]` · `[data-sort-order]` · `[data-sort-label]` | 순서 저장 | "노출 순서 저장" 버튼 |
| `#actionForm` · `#actionMethod` · `#deleteForm` | 행 삭제 등 공용 제출 | 관리 열 |
| `#stripForm` · `#stripPosition` · `#stripText` · `#stripBg`/`#stripBgHex` · `#stripFg`/`#stripFgHex` · `#stripAlways` · `#stripStart` · `#stripEnd` · `#stripRatio`(명도 대비) · `#stripPreview` · `#stripPreviewPage` · `#stripPreviewButton` | 띠배너 폼 · 미리보기 | `#sd-*` · `updateStripPreview()` |
| `[data-link-type]` · `#popupLinkUrl` · `#popupLinkPost` · `[data-post-filter]` · `[data-post-select]` · `#popupPosCustom` · `[data-popup-notice]` | 팝업 연결 방식 · 좌표 토글 | `togglePopupLinkMode()` · `#pd-board-sel` |
| `[data-flash-warning]` | 저장 후 경고 플래시 | — |

- 하위 화면 표현: 목록은 한 페이지 탭(`display?tab=`), 등록 · 수정은 각각 별도 페이지(`banners/create` · `edit` 등). 프로토타입은 같은 페이지 안 상세 패널 전환.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 탭 `event_list` 이벤트 목록 상단 배너.
- 띠배너 위치 `main_slide_bottom`, `devices[]`(PC · 모바일 최소 1개), `link_blank`, 명도 대비 표시.
- 팝업 `position_type`(중앙/좌표) · `pos_x` · `pos_y` · `width` · `height`, `use_today_close` · `use_week_close` · `use_close_button`.
- 모바일 대체 텍스트 `mobile_alt_text`, 이미지 삭제 체크 `delete_image` · `delete_mobile_image`.
- 목록 필터 `title` · `is_active` · `exposure_status`.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 사용자 메인 미리보기(`?preview_token`) 버튼 — 개발은 띠배너 미리보기만.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 상태: 프로토타입 select(노출중 · 예약 · 노출중지) → 개발 `is_active`(1/0) 저장 + 기간으로 계산한 `exposure_status`.
- 기간: 프로토타입 문자열 1칸(`#bd-period` 등) → `start_at` · `end_at`(띠배너는 `always` 체크).
- 팝업 연결: 라디오 값 `BOARD`/`URL` → `link_type` = `post`/`url`, 게시글 `post_id`.
- 띠배너 노출 대상 라벨 순서 · 값: "비로그인 회원 · 로그인 회원 · 전체 회원" → `guest` · `member` · `all`.
- 띠배너 위치 "메인 최상단 (GNB …)" → `event_top`(메인 상단 헤더 위).
- 필드 id `bd-*` · `sd-*` · `pd-*` → 3절 name.

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 띠배너 위치 `main_slide_bottom`(메인 슬라이드 배너 하단)이 프로토타입에 없음 — 정본 반영 여부 확인 필요. **→ 정책 아님(POLICY_D_CONF B)**: 화면 · 이름 문제로 처리 — 프로토 `#sd-loc`에 '메인 슬라이드 배너 하단' 선택지 추가
- 팝업 노출 옵션(일주일 안 보기 · 닫기 버튼 · 좌표 지정)이 정본에 있는지 확인 필요. **→ 정책 아님(POLICY_D_CONF B)**: 화면 · 이름 문제로 처리 — 프로토 팝업 폼에 일주일 안 보기 · 닫기 버튼 · 위치(중앙/좌표) 추가, 동시 노출 최대 2건 유지

## 출처
- routes/admin.php:1086-1206
- app/Http/Controllers/Admin/DisplayController.php:21-98 · BannerController.php:20-115 · PopupController.php:20-110 · StripBannerController.php
- `_index/requests.md` BannerRequest · BannerReorderRequest · StripBannerRequest · StripBannerReorderRequest · PopupRequest · PopupReorderRequest
- app/Models/Banner.php:24-107 · Popup.php:20-50 · Concerns/HasExposureStatus.php:12-22
- resources/views/admin/display/index.blade.php · _head.blade.php · banners/form.blade.php · popups/form.blade.php · strip-banners/form.blade.php · strip-banners/index.blade.php
- `_index/schema.md` banners · popups (마이그레이션 2026_10_15_000212 · 2026_10_02_000181)
- 프로토타입: prototype_clean/ADMN-CONF-001_baseline.html:106-670 (digest 기준)
