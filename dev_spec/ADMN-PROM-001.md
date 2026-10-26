# ADMN-PROM-001 이벤트 · 기획전 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-PROM-001_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-PROM-001(이벤트 관리 목록), ADMN-PROM-001-S1(중복 할인 일괄 차단), ADMN-PROM-001-S2(이벤트 상세 조회), ADMN-PROM-001-S3(기획전 등록 · 수정)
- 개발 진행: 구현. 담당 이응민(`config/dev-progress.php`). progress 표 커밋 언급 PROM-001 8 · S1 4 · S2 0 · S3 7(S2 는 뷰 주석 `promotions/show.blade.php:1` 로 구현 확인)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.promotions.index` | 이벤트 관리 | PromotionController 엑셀 `menuKey: 'admin.promotions.index'`(:66). 메뉴 행 데이터는 DB |

- ROUTE_PERMISSIONS 예외 없음. 하위 자원(`blocks` · `assets` · `targets` · `slug` · `preview` · `status`)은 모두 이 메뉴로 올라간다.
- 접미사 판정 주의: 작성 중 미리보기 `admin.promotions.preview.index`(POST)는 저장하지 않으므로 조회, 저장본 미리보기 `preview.show` 조회, 에셋 올리기 `assets.store` 등록 · 지우기 `assets.destroy` 삭제, 즉시 중단 `status.update` 수정.
- 즉시 중단(stopped)된 기획전은 수정 · 차단 설정 진입 시 상세로 돌려보낸다(PromotionController edit · blocksEdit), 차단 저장은 404.

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`). 사용자 랜딩 주소는 `sanjunmo.com/event/{slug}`(promotions.slug 주석).

### ADMN-PROM-001 이벤트 관리(목록)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/promotions` | `admin.promotions.index` | 조회 | PromotionController@index |
| 엑셀(현재 조건, 사유) | GET | `/{admin}/promotions/download` | `admin.promotions.download` | 다운로드 | PromotionController@download |

### ADMN-PROM-001-S2 이벤트 상세 조회 (별도 페이지 · 읽기 전용)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세 | GET | `/{admin}/promotions/{promotion}` | `admin.promotions.show` | 조회 | PromotionController@show |
| 저장본 미리보기(새 창) | GET | `/{admin}/promotions/{promotion}/preview` | `admin.promotions.preview.show` | 조회 | PromotionController@preview |
| 즉시 중단(사유) | PUT | `/{admin}/promotions/{promotion}/status` | `admin.promotions.status.update` | 수정 | PromotionController@stop |

### ADMN-PROM-001-S3 기획전 등록 · 수정 (별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/{admin}/promotions/create` | `admin.promotions.create` | 등록 | PromotionController@create |
| 등록 저장 | POST | `/{admin}/promotions` | `admin.promotions.store` | 등록 | PromotionController@store |
| 수정 폼 | GET | `/{admin}/promotions/{promotion}/edit` | `admin.promotions.edit` | 수정 | PromotionController@edit |
| 수정 저장 | PUT | `/{admin}/promotions/{promotion}` | `admin.promotions.update` | 수정 | PromotionController@update |
| 대상 상품 검색(JSON) | GET | `/{admin}/promotions/targets` | `admin.promotions.targets.index` | 조회 | PromotionController@targets |
| Slug 중복 확인(JSON) | GET | `/{admin}/promotions/slug` | `admin.promotions.slug.index` | 조회 | PromotionController@slug |
| 작성 중 소스 미리보기 | POST | `/{admin}/promotions/preview` | `admin.promotions.preview.index` | 조회 | PromotionController@previewDraft |
| 랜딩 에셋 올리기(JSON) | POST | `/{admin}/promotions/{promotion}/assets` | `admin.promotions.assets.store` | 등록 | PromotionController@storeAssets |
| 랜딩 에셋 지우기(JSON) | DELETE | `/{admin}/promotions/{promotion}/assets` | `admin.promotions.assets.destroy` | 삭제 | PromotionController@destroyAsset |

### ADMN-PROM-001-S1 중복 할인 일괄 차단 (별도 페이지, 하위 자원 blocks)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 차단 설정 화면 | GET | `/{admin}/promotions/{promotion}/blocks/edit` | `admin.promotions.blocks.edit` | 수정 | PromotionController@blocksEdit |
| 차단 저장 | PUT | `/{admin}/promotions/{promotion}/blocks` | `admin.promotions.blocks.update` | 수정 | PromotionController@blocksUpdate |

- 에셋은 기획전 id 가 있어야 올릴 수 있다(등록 후 수정 화면에서). 등록 폼에서는 저장 뒤 사용 — 추정(라우트가 `{promotion}` 하위).

## 3. 폼 필드 · 검증
### 기획전 등록 · 수정 `promo-form` (PromotionRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `type` | required in promotion,event | promotion=기획전 · event=이벤트 | `promo_cat`(`cat-radio-promo` · `cat-radio-event`) |
| `title` | required max:40(Promotion::MAX_TITLE_LENGTH) | 기획전명(랜딩 h1 · 카드 제목) | `f-promo-title` |
| (코드) | 서버 자동 채번 `PRM-YYMM-{일련}`, 수정 불가 | promotions.code | `f-promo-code`(입력란) |
| `slug` (`promo-slug`) | required 2~40 · `^[a-z0-9]+(-[a-z0-9]+)*$` · 중복 불가(종료 · 중단 포함). 확인 버튼 `promo-slug-check` | URL 식별자 | `f-promo-slug` |
| `started_at` / `ended_at` | required `Y-m-d\TH:i` · ended_at after started_at | 노출 기간(분 단위) | `f-promo-start` · `f-promo-end` |
| (상태) | 입력 없음 — 기간 · 배치로 자동(scheduled · active · ended), 중단은 별도 동작 | | `f-promo-status`(진행중 · 예약 · 비노출) |
| `thumbnail` | 등록 때 required · jpg,jpeg,png,webp · 1MB(실제 바이트) | 목록 썸네일(720×405 권장) | `f-banner-pc` · `f-banner-mo` · `f-banner-alt`(배너 · alt) |
| `headline` | nullable max:255 (비우면 기획전명) | 상단 카피 | 없음 |
| `sort_type` | required in manual,sales,price_asc,created_desc | 수동 정렬 · 판매량순 · 낮은 가격순 · 등록 역순 | 없음(대상 상품 "노출순서" 열만) |
| `html_content` | required · 최대 1,000,000자 | 랜딩 HTML | `cm-code-input` + `switchCodeTab('HTML')` |
| `css_content` / `js_content` | nullable · 최대 1,000,000자. CSS 는 `#sanjunmo-promotion-wrapper` 스코프 자동 접두(css_scoped), z-index 900 · document.write 경고 | 랜딩 CSS · JS | `switchCodeTab('CSS'/'JS')` |
| `products[n][type]` | required in course,package,book | 대상 상품 구분 | `sel-add-prod` 옵션 접두(패키지 · 단과 · 교재) |
| `products[n][id]` | required integer min:1 · 1~500행 | 상품 id | 상품코드 |
| `products[n][promo_price]` | nullable integer min:0 (교재는 도서정가제로 정가 고정) | 기획전가 | 판매가 열 |
| `products[n][discount_rate]` | nullable 0~100 (한쪽 입력 시 다른 쪽 원 단위 절사 자동 계산) | 할인율 | 없음 |

### 즉시 중단 `promotionStopModal` (PromotionStopRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` | required 2~200자 | 없음(상태 "비노출(강제 숨김)" 선택이 비슷) |

### 중복 할인 일괄 차단 `blockForm` (PromotionBlockRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `enabled` | required in 0,1. 0 이면 모든 기획전에서 해제(완료 문구) | 차단 사용 | `chk-bulk-disable` |
| `benefits[]` | in coupon,point,earn | 쿠폰 · 포인트 · 적립 차단 | `chk-block-cpn` · `chk-block-pt` · `chk-block-earn` |
| `block_from` / `block_to` (`blockFrom`) | enabled=1 이면 required date | 차단 기간(노출 기간과 별개) | 없음 |
| `target` | enabled=1 이면 required in all,selected · `toggleTarget()` | 전체 대상 상품 / 선택 상품 | 없음(행별 쿠폰 · 포인트 · 적립 열) |
| `product_ids[]` | integer | 선택 대상 | 대상 상품 행 |
| `reason` | enabled=1 이면 required · max:100(40자 권장) | 주문서 혜택 입력란 아래 노출 사유. 기본 문구 PromotionProduct::DEFAULT_BLOCK_REASON | 없음 |

### 에셋 (PromotionAssetRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `files[]` | 1~20개 · jpg,jpeg,png,webp,gif,mp4,webm,woff,woff2 · 개당 20MB(실제 바이트) | `inp-new-asset-name` · `uploadNewS3Asset()` |

### 엑셀 반출 사유 (ReasonRequest, 공용 `layerReason`)
`reason`(refund_account · delivery_error · identity_check · payment_inquiry · legal_request · settlement_check · etc) · `reason_etc`(etc 일 때 10~150자) · `reason_ref`.

## 4. 목록 필터 · 정렬 · 표 컬럼
- 필터(PromotionService::normalizeFilters:189-211): `period_from` · `period_to`(첫 진입은 이번 달 1일 ~ 4개월 뒤) · `status`(scheduled 예약 · active 진행중 · ended 종료 · stopped 중단) · `type`(promotion 기획전 · event 이벤트) · `keyword`(100자) · `sort`(started_asc / started_desc, 노출 기간 머리 클릭 토글 ▲▼).
- 진행중 건수(`activeCount`) 표시.
- 표 컬럼(개발): No · 기획전 코드 · 구분 · 기획전명 · 노출 기간 · 대상 상품 · 상태 · 관리.
- 프로토타입: 코드 · 카테고리 구분 · 제목/동적 URL 슬러그 · 노출 기간 · 대상 상품 · 중복할인 차단(001-S1) · 진행 상태 · 당첨발표(BRD-009) · 관리. 필터 `flt-cat` · `flt-status`(진행중 · 예약 · 종료) · `flt-block`(차단 ON/OFF) · `flt-kw`.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| promotions.code | string(30) unique | PRM-YYMM-{일련} 자동, 수정 불가(정산 · 통계 키) | 기획전 코드 |
| promotions.type | string(20) | promotion 기획전 · event 이벤트 | 구분 |
| promotions.title | string(255), 입력 40자 | 기획전명 | 제목 |
| promotions.slug | string(40) unique | `/event/{slug}` | Slug · 사용자 주소 |
| promotions.started_at / ended_at | dateTime | 노출 기간(분 단위, KST) | 노출 기간 |
| promotions.status | string(20) | scheduled 예약 · active 진행중 · ended 종료 · stopped 중단(관리자 강제). 직접 입력 없음 | 상태 배지 |
| promotions.thumbnail_path | string(255) | 목록 썸네일 | 썸네일 |
| promotions.banner_pc_path / banner_mobile_path | string(255) | 랜딩 배너(스키마에 있으나 폼 미연결 — form.blade.php:139 "스키마 확인 뒤 붙인다") | — |
| promotions.headline / sort_type | | 상단 카피 · 진열 순서 | 상세 |
| promotions.html_content / css_content / js_content / css_scoped | longText | 랜딩 소스 · 스코프 변환 CSS | 소스 3분할 |
| promotions.admin_id | bigint | 최종 수정자 | — |
| promotion_products.product_type / product_id | | course · package · book | 대상 상품 |
| promotion_products.original_price_snapshot / promo_price / discount_rate / sort_no | | 저장 시점 정가 · 기획전가 · 할인율 · 진열 순서 | 대상 상품 표 |
| promotion_products.block_coupon / block_point / block_earn | tinyint | 쿠폰 · 포인트 사용 · 구매 적립 차단 | S1 |
| promotion_products.block_from / block_to / block_reason | dateTime / string(100) | 차단 기간 · 사용자 노출 사유 | S1 |
| posts.promotion_id | bigint | 당첨자 발표(BRD-009) ↔ 이벤트 1:1 | (목록 열 없음) |
| admin_logs | | 등록 · 수정 · 중단 사유 · 차단 변경 이력 — 추정(중단 사유 전용 컬럼 없음) | — |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `promo-form` | 등록 · 수정 폼 | `view-form`(`data-subpage="form"`) |
| `promo-slug` · `promo-slug-check` · `promo-slug-result` | Slug 입력 · 중복 확인 | `f-promo-slug` |
| `promo-target-type` · `promo-target-keyword` · `promo-target-search` · `promo-target-results` · `promo-products` · `promo-products-empty` · `addRow()` · `bindRow()` · `search()` | 대상 상품 검색 · 추가 | `sel-add-prod` · `addMappedProduct()` · `removeMappedProd()` |
| `promo-source-html` / `-css` / `-js`(name `html_content` 등, `_source-panes`) | 소스 3분할 | `cm-code-input` · `switchCodeTab()` |
| `promo-lint` · `promo-lint-result` · `lintHtml()` · `lintBraces()` | 문법 점검 | `validatePromoCodeSecurity()` |
| `promo-preview` | 작성 중 미리보기(POST preview.index) | `openFullPreviewModal()` · `setPreviewViewport()` |
| `promo-asset-drop` · `promo-asset-input` · `promo-asset-message` · `promo-assets` · `upload()` · `removeAsset()` · `renderAssets()` | 랜딩 에셋 | `uploadNewS3Asset()` · `insertAssetToEditor()` · `copyAssetUrl()` |
| `promotionStopModal`(`data-target`) | 즉시 중단 모달(사유) | 없음 |
| `blockForm` · `blockFrom` · `toggleTarget()` | 중복 할인 차단 페이지 | `chk-bulk-disable` 구획(폼 안) |
| `.layer__open[data-target="layerReason"]` | 엑셀 사유 모달 | 없음 |
| `.promo-pending` | 미연결 항목 표시(배너) | — |

하위 화면: 개발 S1 · S2 · S3 모두 별도 페이지(`blocks.edit` · `show` · `create`/`edit`). 프로토타입은 SJM_PAGE 서브페이지 `list` · `detail` · `form` 이고 S1 은 S3 폼 안 4번 구획에 합쳐져 있다.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 즉시 중단(사유 필수) · 중단 상태(stopped), 중단 후 수정 · 차단 잠금.
- 상품 진열 순서 `sort_type`, 상단 카피 `headline`, 할인율 자동 계산 · 정가 스냅샷.
- 차단 기간(block_from/to) · 대상 범위(전체/선택) · 사용자 노출 사유, 차단 해제(enabled=0).
- Slug 중복 확인 버튼, 노출 기간 정렬 토글, 기간 필터, 엑셀 다운로드(사유).
- 에셋 형식 · 용량 제한(20개 · 20MB, 영상 · 웹폰트 포함).

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 랜딩 배너 PC · 모바일 · 대체 텍스트(개발 폼에 "스키마 확인 뒤 연결" 표시).
- 상태 직접 선택(진행중 · 예약 · 비노출 강제 숨김) — 개발은 자동 + 중단.
- 목록 열 "중복할인 차단" · "당첨발표(BRD-009)", 차단 ON/OFF 필터, KPI "중복 할인 일괄 차단 작동중".
- 상품 행마다 쿠폰 · 포인트 · 적립 개별 표시/설정(개발은 차단 페이지에서 혜택 · 대상 일괄 지정, 저장은 행 단위 컬럼).
- 코드 자동 정렬(Beautify), 상세 화면 주소 복사 · 소스 복사.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 구분: `promo_cat` → `type`(promotion · event).
- 코드: 프로토타입 입력 `f-promo-code` → 개발 자동 채번(입력 없음, `PRM-YYMM-NNN`).
- 상태 값: 진행중 → `active`, 예약 → `scheduled`, 종료 → `ended`, 비노출(강제 숨김) → 개발 `stopped`(중단, 사유 필수 · 되돌리기 없음 — 추정: 재개 라우트 없음).
- 대상 상품: `sel-add-prod` → `products[n][type|id|promo_price|discount_rate]`.
- 차단 체크: `chk-block-cpn/pt/earn` → `benefits[]` = coupon · point · earn, `chk-bulk-disable` → `enabled`.
- 제목 길이: 개발 40자 제한.

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
- "비노출(강제 숨김)"과 개발 "즉시 중단(stopped, 사유 필수 · 이후 수정 불가)"을 같은 것으로 볼지 확인 필요.
- 랜딩 배너(PC · 모바일 · alt) 저장 위치 확인 필요 — 개발 주석은 banner_pc/mobile_path 를 목록 썸네일 용도로 보고 미연결.
- 중복 할인 차단을 상품 행별로 다르게 둘지(프로토타입) 혜택 · 대상을 일괄로 둘지(개발 S1) 확인 필요.

## 출처
- routes/admin.php:1061-1083 (dev_spec/_index/routes.md)
- app/Http/Controllers/Admin/PromotionController.php:38-58(index), 59-90(download), 92-108(create · store), 109-120(show), 121-139(edit · update), 140-160(blocks), 161-169(stop), 170-186(preview), 187-219(targets · slug), 220-235(assets)
- app/Http/Requests/Admin/PromotionRequest.php · PromotionBlockRequest.php · PromotionStopRequest.php · PromotionAssetRequest.php · ReasonRequest.php
- app/Services/Admin/PromotionService.php:189-219, 273-316, 322-373, 380
- app/Services/Admin/PromotionAssetService.php:23, 28
- app/Models/Promotion.php:17-57 · app/Models/PromotionProduct.php:13-29
- resources/views/admin/promotions/index.blade.php · form.blade.php:138-141 · show.blade.php:1 · blocks.blade.php · _source-panes.blade.php · _stop-modal.blade.php · create.blade.php · edit.blade.php
- database: dev_spec/_index/schema.md promotions · promotion_products · posts.promotion_id
- 프로토타입: prototype_clean/ADMN-PROM-001_baseline.html:375-456(목록), 457-558(S2 상세), 559-790(S3 · S1 폼), 926-1002(스크립트 · SJM_PAGE)
