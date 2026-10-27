# CLASS_MAP — 개발 class ↔ 프로토타입 기준

- **JS 의존** = 개발 JS · Blade 가 이 이름을 잡거나 붙인다. **이름을 바꾸지 말 것**(모양은 `sjm-dev-skin.css` 가 바꾼다).
- **프로토타입 기준** = 같은 역할의 프로토타입 class 와 디자인 값(`prototype_clean/`). 프로토타입은 계열마다 class 이름이 달라 대표 이름을 적었다.
- **키트** = `sjm-dev-skin.css` 가 이미 입히는지(✓) 여부.
- 근거 파일: 개발 `public/admin/assets/scss/*`, `public/admin/assets/js/custom.js`, `resources/views/admin/inc/*`. 프로토타입 `prototype_clean/common-v84.css` 와 화면 `<style>`.

## 1. 골격
| 요소 | 개발 class | JS 의존 | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 머리 | `.header` `.header__wrap` `.utility` | — | 상단 바 `.top-bar` | 흰 바탕, 하단선 #E2E8F0, 높이 60px | ✓ |
| 로고 칸 | `.admin__logo a` | — | SNB 위 `.snb-brand` | 남색 #0F172A, 흰 로고(`img/sjm_logo-horizontal-white.png`, 높이 17px) | ✓ |
| 프로필 메뉴 | `.user_profile` `.user_profile__wrap` `.user_profile__info` + `active` | **JS** (`custom.js:176-197`) | (없음) | 흰 카드, 테두리 #E2E8F0, 둥글기 10px | ✓ |
| 본문 | `.container` `.content` | — | `#v4-root-shell` `#v4-page-body` | 바탕 #F8FAFC, 여백 22px 28px 96px | ✓ |
| 페이지 제목 | `.content__header` `.content h2` `.content__title` | — | `.top-bar-left .crumb-title` | 흰 띠 · 하단선 #E2E8F0, 16px/800 #0F172A | ✓ |
| 구획 카드 | `.content__wrap` `.search .search__wrap` | — | `.card` | 흰 바탕, 테두리 #E2E8F0, 둥글기 10px, 그림자 0 1px 3px rgba(15,23,42,.06) | ✓ |
| 골격 변수 | `--snb-w` `--header-h` | — | `--snb-width` `--topbar-height` | 260px / 60px | ✓ |

## 2. SNB
| 요소 | 개발 class | JS 의존 | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SNB 틀 | `.snb` `.snb__wrap` | **JS** `.snb` (`custom.js:723`) | `#v4-master-snb` | 폭 260px, 바탕 #0F172A, 오른쪽선 #1E293B | ✓ |
| 홈 바로가기 | `.link__home a` | — | (없음) | 12px #94A3B8, hover #1E293B 바탕 | ✓ |
| 1depth 목록 | `.snb__depth--1 > li.snb__item` | **JS** (`custom.js:726`) | `.snb-group` | 항목 간격 2px | ✓ |
| 1depth 링크(그룹) | `.snb__link` (하위 있음) | **JS** (`custom.js:741`) | `.snb-group-title` | 12.5px/700 #94A3B8, 열리면 흰 글자 + 화살표 회전 | ✓ |
| 1depth 링크(단독) | `.snb__link` (하위 없음, 예: 대시보드) | **JS** | `.snb-item` | 높이 34px, 둥글기 7px, 12.5px/500 #CBD5E1 | ✓ |
| 펼침 상태 | `li.snb__item.active` | **JS + 서버** (`custom.js:727`, `snb.blade.php`) | (프로토타입은 접기 없음) | 상태 class 그대로 사용 | ✓(모양만) |
| 2depth 목록 | `.snb__depth--2` + 인라인 `display` · `height` | **JS** (`custom.js:730-806` 슬라이드) | `.snb-item-list` | 열림 · 닫힘 속성은 건드리지 않음 | ✓(색만) |
| 2depth 링크 | `.snb__depth--2 li a` | — | `.snb-item` | 높이 32px, 들여쓰기 22px, #CBD5E1, hover #1E293B | ✓ |
| 현재 메뉴 | `.snb__depth--2 li.active` / 단독 1depth `li.active` | **서버** | `.snb-item.active` | 바탕 #2563EB, 흰 글자 700, 그림자 0 2px 8px rgba(37,99,235,.35) (개발의 밑줄 대신) | ✓ |

## 3. 버튼 — 개발 조합 → 프로토타입 역할
| 개발 class | 쓰는 곳(예) | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- |
| `.btn` (단독) | 검색 초기화 · 폼 취소 | `.btn.btn-outline` | 32px, 흰 바탕, 테두리 #CBD5E1, 12.5px/700, 둥글기 6px | ✓ |
| `.btn.button--search` | 검색 조회 | `.btn.btn-primary` | #2563EB, hover #1D4ED8, 흰 글자 | ✓ |
| `.btn.btn--save` · `.btn.btn--add` | 폼 저장 · 등록 | `.btn.btn-primary` | 위와 같음(개발에서는 정의가 없어 검정으로 보이던 것) | ✓ |
| `.btn__small` (단독) | 행 버튼 | `.btn.btn-dark.btn-sm` | 28px, #0F172A, 11.5px | ✓ |
| `.btn__small.btn--basic` · `.btn--mail` | 기간 버튼 · 행 버튼 | `.btn.btn-outline.btn-sm` | 28px, 흰 바탕, 테두리 #CBD5E1 | ✓ |
| `.btn__small.btn--save` | 엑셀 다운로드 · 작은 저장 | `.btn.btn-primary.btn-sm` | 28px, #2563EB | ✓ |
| `.btn__small.btn--secondary` | — | `.btn.btn-dark.btn-sm` | #0F172A | ✓ |
| `.btn__small.btn--excel` | 엑셀 | `.btn.btn-success`(외곽선형) | 흰 바탕, 테두리 #BBF7D0, 글자 #15803D | ✓ |
| `.btn__small.btn--line` | 삭제 | `.btn.btn-danger.btn-sm` | 바탕 #FEF2F2, 테두리 #FECACA, 글자 #DC2626 | ✓ |
| `.btn__system` | 모달 확인 · 폼 하단 | `.btn.btn-primary` | 32px, 최소 폭 88px, #2563EB | ✓ |
| `.btn__system.btn--basic` | 모달 취소 | `.btn.btn-outline` | 흰 바탕, 테두리 #CBD5E1 | ✓ |
| `.btn__system.btn--secondary` · `.btn--modify` | — | `.btn.btn-dark` | #0F172A | ✓ |
| `.btn__system.btn--success` | — | `.btn.btn-success` | 초록 외곽선형 | ✓ |
| `.btn__system.btn--warning` | 반려 · 위험 | `.btn.btn-danger` | 연한 빨강 | ✓ |
| `:disabled` (모든 버튼) | — | `.btn:disabled` | 바탕 #E2E8F0, 글자 #94A3B8 | ✓ |
| `.btn__icon` · `.btn__tiny` · `.btn_data` | 아이콘 버튼 | (프로토타입은 이모지 글자) | 아이콘 그림을 쓰므로 키트가 손대지 않음 | — |
| `.btn__group` | 버튼 묶음 | `.modal-footer` · `.subpage-foot` | 간격 8px. 모달 안에서는 오른쪽 정렬(`align--c` 는 가운데 유지) | ✓ |
| `.layer__open` + `data-target` | 모달 여는 버튼 | — | **JS** (`custom.js:62,77`) — 이름 유지 | — |
| `.layer-pop--close` | 모달 닫는 버튼 | — | **JS** (`custom.js:63,112-126`) — 이름 유지 | — |

## 4. 입력
| 요소 | 개발 class | JS 의존 | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 글자 · 날짜 · 숫자 | `input.input__text`, `input[type=date|datetime-local|number|password]` | 화면별 id (`#dateFrom` 등) | `.f-input` / `.form-input` / `.input` | 32px, 테두리 #CBD5E1, 둥글기 6px, 12.5px, focus 테두리 #2563EB + 3px 링 | ✓ |
| 선택 | `select`, `.select` | — | `.f-select` | 32px, 같은 테두리, 개발 화살표 그림 유지 | ✓ |
| 여러 줄 | `textarea`, `.input__textarea` | 에디터는 `#editor_{name}` **JS** | `.f-textarea` | padding 8px 10px, 같은 테두리 | ✓ |
| 체크박스 | `input[type=checkbox]` (개발이 그린 체크 표시) | 화면별 `#checkAll` · `.member-check` 등 | 브라우저 기본 + 파랑 | 16px, 둥글기 4px, 체크 시 #2563EB | ✓ |
| 라디오 | `input[type=radio]` | — | 브라우저 기본 + 파랑 | 16px, 체크 시 5px #2563EB 테두리 | ✓ |
| 필수 표시 | `.text--required` | — | `.req` | 빨강 글자 `*`(개발의 빨간 칩 대신) | ✓ |
| 오류 칸 · 문구 | `.fld--err`, `.text--warning`, `.txt--red` | — | `.form-error` | 테두리 #DC2626, 바탕 #FEF2F2 / 글자 #DC2626 11.5px | ✓ |
| 도움말 | `.fm-help`, `.fm__help(--warn|--ok)`, `.text--desc`, `.text--small` | — | `.form-help` | 11.5px #64748B | ✓ |
| 숫자 콤마 | `bindNumberInput` 이 묶는 입력 | **JS** (`public/assets/js/common.js`) | `.num` (등폭 숫자) | 모양만 | — |

## 5. 검색 · 표 · 페이지 번호
| 요소 | 개발 class | JS 의존 | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 검색 구역 | `.search` `.search__wrap` `.search__table` | — | `.card` + `.search-tbl` | 카드 안 조건표, th #F8FAFC 12px/700 #475569, 칸선 #E2E8F0. 버튼은 개발 배치(오른쪽) 유지 | ✓ |
| 목록 요약 줄 | `.list__detail` `.list__detail__total` | 화면별 `#selectedCount` | 목록 카드 머리 | 12.5px #475569, 숫자 #2563EB 800 | ✓ |
| 목록 표 | `.table__list` | `td[data-url]` **JS** (`custom.js:200`), `.drag-sort` **JS**, `td[data-label]` | `.data-table` | 흰 바탕, 테두리 #E2E8F0 둥글기 10px, th #F8FAFC 11.5px/700 #475569, td 12.5px 10px 12px, 행 hover #F8FAFC, 기본 왼쪽 정렬(`align--*` 는 개발 지정 유지) | ✓ |
| 상세 표 | `.table__view` | — | `.kv-table` | th #F8FAFC 12px/700, td 12.5px, 칸선 #E2E8F0 | ✓ |
| 페이지 번호 | `.pagination` `.pagination__item(.current)` `.pagination__btn--*` | — (링크) | `.pagination .page-btn(.active)` | 30px, 테두리 #E2E8F0, 둥글기 6px, 현재 #2563EB | ✓ |

## 6. 탭 · 모달 · 알림 · 배지
| 요소 | 개발 class | JS 의존 | 프로토타입 기준 | 디자인 값 | 키트 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 내용 전환 탭 | `.tab__wrap` `.tab__menu` `.tab__item` `.tab__content` + `data-tab` | **JS** (`custom.js:219-264`), 켜짐 `tab__item--active` · `tab__content--active` | `.tabs .tab-btn(.active)` 밑줄 탭 | 13px/600 #475569, 켜짐 #2563EB 800 + 밑줄 2px | ✓ |
| 탭 모양만 | `.tab__list .tab__item(.active)` `.tab__badge` | 서버 `active` | 밑줄 탭 | 위와 같음, 개수 배지 알약 | ✓ |
| 모달 | `.layer-pop__overlay` `.layer-pop__wrap(.w--xs|s|m|l|full)` `.layer-pop__content` `.layer__title` `.btn--close` | **JS** 상태 `layer-pop--hidden` · `layer_pop--show` · `body.layer--open` (`custom.js:61-127`, ESC `footer.blade.php:110-142`) | `.modal-backdrop .modal-box` | 덮개 rgba(15,23,42,.5) · SNB 오른쪽부터, 상자 둥글기 12px · 그림자 0 20px 50px rgba(15,23,42,.25) · padding 22px 24px, 제목 16px/800 + 하단선, 하단 버튼 오른쪽 | ✓ |
| 알림 | `#layerAlert` `#alertMessage` | **JS** (`footer.blade.php:146-166`) | 토스트 `#toast-box` | 모달 모양 그대로(개발 방식 유지) | ✓ |
| 사유 모달 | `#layerReason` 외 `#reason*` · `data-reason-*` | **JS** (`reason-modal.blade.php`) | P1 사유 모달 | 모달 모양 | ✓ |
| 선택 레이어 · 강좌 불러오기 | `#selectLayer*` `.sl-*`, `#cll*` `.cll-*` | **JS** (`select-layer.js`, `course-lecture-loader`) | 선택 모달 | 둥글기 · 그림자 · 덮개만 | ✓ |
| 배지 | `.badge` + `badge--soft|outline|solid` + 상태 `badge--{waiting|request|progress|feedback|setup|complete|stop|active|pending|suspend|cancel}` | 서버가 상태 class 를 정함 | `.badge .badge-{green|blue|amber|red|gray}` | 알약 999px, 11.5px/700. 색 대응 ↓ | ✓ |

배지 색 대응(상태 class 는 개발 것 그대로):
| 개발 상태 | 프로토타입 색 | 연한(soft) | 외곽선(outline) | 진한(solid) |
| :--- | :--- | :--- | :--- | :--- |
| `active` `complete` | 초록 | #DCFCE7 / #15803D | 흰 바탕 · #BBF7D0 테두리 | #16A34A |
| `request` `progress` `setup` `feedback` | 파랑 | #DBEAFE / #1D4ED8 | #BFDBFE 테두리 | #2563EB |
| `waiting` `pending` | 노랑 | #FEF3C7 / #B45309 | #FDE68A 테두리 | #D97706 |
| `stop` `suspend` | 빨강 | #FEE2E2 / #B91C1C | #FECACA 테두리 | #DC2626 |
| `cancel` | 회색 | #F1F5F9 / #475569 | #E2E8F0 테두리 | #64748B |

## 7. 정리 권장(개발에서 쓰지만 CSS 정의가 없던 것)
| class | 상황(조사 결과) | 키트 처리 |
| :--- | :--- | :--- |
| `txt--red` | 50개 파일 393회 사용, 어떤 CSS 에도 정의 없음 | 위험 글자색으로 정의 |
| `fm__help` `fm__help--warn` `--ok` | 48개 파일 사용, `.account`(로그인) 안에서만 정의 | 도움말 글자로 전역 정의 |
| `text--desc` | 6개 파일 사용, 달력 폼 안에서만 정의 | 도움말 글자로 정의 |
| `.btn.btn--save` | 69개 파일 사용, `btn__small` 안에서만 정의돼 검정 버튼으로 보임 | 주 버튼(파랑)으로 정의 |
| `admin__member`(main) | 정의 없음 | 그대로(모양 없음) |

## 8. 바꾸면 안 되는 이름 — 전체(개발 JS · Blade)
`.snb` `.snb__depth--1` `.snb__link` `.snb__depth--2` `li.active`(SNB) · `.layer__open` `data-target` `.layer-pop--close` `.layer-pop__overlay` `layer-pop--hidden` `layer_pop--show` `body.layer--open` · `data-tab` `.tab__wrap` `.tab__item` `.tab__content` `tab__item--active` `tab__content--active` · `td[data-url]` · `.drag-sort` `tr.depth--1/2` `drag--active/over/placeholder` `td[data-label="순서"] .order--number` · `.user_profile` `.user_profile__wrap` `.user_profile__info` · `.target__top` `.target__bottom` `.scroll__target` · `.table__utility` · `.uix-accordion*` · `.toggle__active` · `[data-toggle]` `active--nav` `active--target` · `.lcp-hover` `.lcp__content` · `.nav__tab__wrap` `.nav__target__wrap` `.nav__menu__wrap` 하위 · `.setting--uix` `.switch-list__item` · `#layerAlert` `#alertMessage` · `#layerAdminProfile` `#adminProfileForm` · `#layerReason` `#reason*` `data-reason-*` · `.masked` `.masked__unmask` `data-masked-*` · `#selectLayer*` `.sl-*` · `#cll*` `.cll-*` · `#loadingOverlay` `#loadingText` · `#layerSessionExpire` `data-remain` · `#editor_{name}`.
화면 하단 `<script>` 가 잡는 화면별 id · class(`#checkAll`, `.member-check`, `.member-row`, `data-period-from` 등)도 같은 원칙으로 유지한다.
