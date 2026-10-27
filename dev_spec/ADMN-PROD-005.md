# ADMN-PROD-005 패키지 · 환급반 상품 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-005_baseline.html` (원본 상태: `18d66c1` v6.92)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PROD-005 목록 · 005-S2 패키지 상세(프로토에만) · 005-S1 등록 · 수정 · 강좌 선택 모달 · 교재 선택 모달
- 개발 진행: 구현(목록 · 등록 · 수정 · 삭제 · 복사 · 판매중지 · 미리보기 · 엑셀). `_index/progress.md` PROD-005 커밋 언급 7건(라우트 주석 없음). 005-S2 읽기 전용 상세는 개발 미구현

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 005 패키지 목록(L595) | PROD-005 목록 | `resources/views/admin/packages/index.blade.php` |
| 005-S2 패키지 상세(L599) | (없음 — 목록 행 클릭이 수정 화면) | — |
| 005-S1 등록 · 수정(L603) | PROD-005-S1 | `packages/create.blade.php` · `edit.blade.php` + `form.blade.php` |
| `modal-course-picker`(L1243) | 강좌 검색(공용 API) | `form.blade.php:410` `admin.api.courses` |
| `modal-book-picker`(L1272) | 교재 검색(공용 API) + 교재 정보 조회 | `form.blade.php:427,487` `admin.api.books` · `admin.packages.books.index` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.packages.index` | 패키지(올패스)관리(라우트 주석 `routes/admin.php:453`) | 005 · S1 · S2 · 모달 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 버튼 노출: `@adminCan('admin.packages.index', can_download|can_create|can_update|can_delete)` (`index.blade.php:83,96,149,153,159`, `edit.blade.php:33`).
- 구성품 검색 API `admin.api.courses` · `admin.api.books`는 메뉴 권한 밖(로그인만, `_index/routes.md` 200 · 201줄).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{package}` = `packages.id`.

### PROD-005 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 · 정렬 | GET | `/packages` | `admin.packages.index` | 조회 | PackageController@index |
| 엑셀(패키지 + 구성품 배분가, 사유) | GET | `/packages/download` | `admin.packages.download` | 다운로드 | PackageController@download |
| 복사 | POST | `/packages/{package}/copy` | `admin.packages.copy.store` | 등록 | PackageController@copy |
| 삭제 | DELETE | `/packages/{package}` | `admin.packages.destroy` | 삭제 | PackageController@destroy |

### PROD-005-S2 상세
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 읽기 전용 상세 · 변경 이력 | GET | `/packages/{package}` (규칙) | `admin.packages.show` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명 |

### PROD-005-S1 등록 · 수정 · 모달
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/packages/create` | `admin.packages.create` | 등록 | PackageController@create |
| 등록 | POST | `/packages` | `admin.packages.store` | 등록 | PackageController@store |
| 수정 폼 | GET | `/packages/{package}/edit` | `admin.packages.edit` | 수정 | PackageController@edit |
| 수정 | PUT | `/packages/{package}` | `admin.packages.update` | 수정 | PackageController@update |
| 판매중지 | POST | `/packages/{package}/stop-selling` | `admin.packages.stop.update` | 수정 | PackageController@stopSelling |
| 미리보기(신규) | POST | `/packages/preview` | `admin.packages.preview.store` | 등록 | PackageController@previewNew |
| 미리보기(저장분) | POST·PUT | `/packages/{package}/preview` | `admin.packages.preview.update` | 수정 | PackageController@previewSaved |
| 교재 정보(저자 · ISBN · 정산 경로 · 배송) | GET | `/packages/books` | `admin.packages.books.index` | 조회 | PackageController@books |
| 강좌 선택 모달 검색 | GET | `/api/courses` | `admin.api.courses` | 로그인만 | CourseController@apiList |
| 교재 선택 모달 검색 | GET | `/api/books` | `admin.api.books` | 로그인만 | BookController@apiList |

## 3. 폼 필드 · 검증

### 목록 검색 (GET, PackageService::normalizeFilters `PackageService.php:168-185`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `root_category_id` · `category_id` | 1Depth · 2Depth 카테고리 | `#filter-cat` (고정 3종) |
| `display_status` | `selling` 노출 · `hidden` 숨김 · `stopped` 판매중지 (LIST_DISPLAY_LABELS) | `#filter-status` 판매중 · 판매대기 · 판매중지 · 판매종료 + `#filter-display` Y · N |
| `title` | 패키지명 · 코드, 100자 | `#filter-keyword` (패키지명 / 코드 / 포함 강사명) |
| `duration_min` · `duration_max` | 수강일수 범위 | 프로토 없음(개발에만) |
| `sort` · `direction` | `title` · `sale_price` · `duration_days` · `created_at` / asc · desc | 프로토 없음 |
| (패키지 유형) | 개발 없음 | `#filter-pkg-type` 합격 환급반 · 일반 종합 패키지 · 연간 프리패스 |
| (등록일 기간) | 개발 없음 | `#filter-date-from` · `#filter-date-to` |

### S1 등록 · 수정 (PackageRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (패키지 코드) | 자동 `PKG_00001`(`PackageRepository.php:174-180`) | | `#f-pkg-code` `PKG-2601` |
| `title` | required · max 255 | | `#f-pkg-title` (100자) |
| (한줄 서브 카피) | 개발 없음 | | `#f-pkg-summary` |
| `root_category_id` · `category_id` | category_id required · 2Depth만 | | `#f-pkg-cat` |
| (패키지 유형) | 개발은 `is_pass_refund` 하나 | `1` 환급 대상 · `0` 일반 | `f-pkg-type` 환급반 · 일반패키지 · 연간프리패스 |
| `duration_days` | required · integer ≥ 1 (기본 180, 구성 강좌 기간을 덮어씀) | | `#f-pkg-days` |
| (불합격 시 1회 무상 연장 90일) | 개발 없음 | | `#f-pkg-extend-allow` |
| `sale_price` | required · integer ≥ 0, 콤마 제거. **패키지 총 판매 기획가** 1칸. 구성품 정가 합계 이하 · 할인은 강좌 정가 합계 이하 | | 프로토는 `#f-course-discount`(강좌 할인액) 입력 → `#f-course-net-price` + `#f-book-net-price` = `#f-pkg-total-price`(8절 Q1 · Q2) |
| `display_status` | required | `selling` 전시 · 판매중 · `hidden` 비전시 · `stopped` 판매중지 | `f-pkg-status` `#radio-pkg-sale` 판매중 · `#radio-pkg-ready` 판매대기 · 판매중지 · 판매종료 + `f-pkg-display` Y · N (8절 Q3) |
| `is_pass_refund` | required · boolean | | `f-pkg-type`=환급반 · `toggleRefundSection()` |
| `refund_min_progress` | 환급 대상이면 required · 1~100 (기본 site_settings `refund_claim_min_progress`) | | `#f-refund-progress` |
| (필수 출석일수 · 환급 신청 기한) | 개발 없음 | | `#f-refund-attendance` · `#f-refund-deadline` |
| (결제 시점 환급 조건 박제) | `order_items.refund_terms_snapshot` (규칙) JSON — 인정 진도율 · 필수 출석일수 · 판정 대상 차시. 판매 후 변경은 변경 이후 결제분부터(S-14) | | `#f-refund-retro-note` · `#f-refund-retro-diff`(변경 전 → 후) |
| (환급 분담 옵션) | 개발은 패키지에 없음(계약 단위 `refund_promo_burden_type`) | | `#f-refund-burden-opt` `OPT_A` · `OPT_B` · `OPT_C` (8절 Q5) |
| (정산 1계층 매핑 검증) | 개발 없음 | | `#f-pkg-settlement-sim` · `#f-pkg-settlement-banner` (8절 Q4) |
| `description` | nullable · Purifier | | 프로토 없음(개발에만) |
| `thumbnail` · `delete_thumbnail` | jpg/png/webp · 5MB · 720×405(16:9) 이상 | | 프로토 없음(개발에만) |
| `items[n][product_type]` | required | `course` 강좌 · `book` 교재 | 강좌 표 `#form-pkg-courses-tbody`(L994) · 교재 표(L1034) |
| `items[n][product_id]` | required · integer | courses.id · books.id | 강좌코드(`CRS-…`) · 교재 SKU(`PROD-BK-…`) |
| `items[n][sort_order]` | nullable · integer | | 순번 |
| `items` 전체 | 1개 이상 · 강좌 1개 이상 · 중복 불가 · **구성품 전부 전시 · 판매중이어야 저장**(`PackageRequest.php:98-187`) | | 강좌 최소 1개(`removeCourseFromPkg`, L1931) · 주교재 상태 경고 `bkSyncPkgs`(L1426) (8절 Q6) |
| (안분 가중치) | 입력 없음 — 서버가 강좌 정가 비율로 `price_ratio` · `discount_amount` 계산(`PackagePricingService.php`) | | `updateCourseWeight()` 직접 입력 · `autoDistributeCourseWeights()` (8절 Q2) |

## 4. 목록 필터 · 정렬 · 표 컬럼

| 개발 컬럼(`index.blade.php:109-119`) | 정렬 키 | 프로토타입 컬럼(L723) |
|---|---|---|
| No | | No |
| (코드는 패키지명 칸 검색만) | | 패키지코드 |
| (없음) | | 유형 |
| 카테고리 | | 카테고리 |
| 패키지명(→ edit) | `title` | 패키지 상품명 |
| 구성품 | | 구성 (강좌/교재) |
| 수강일수 | `duration_days` | (없음) |
| 판매 기획가 | `sale_price` | 강좌 결제액 · 교재 결제액 · 총 판매가 (3칸) |
| (없음) | | 환급조건 · 정산매핑(1계층) |
| 전시(+ 블라인드 사유) | | 판매상태 |
| 등록일 | `created_at` | 등록일 |
| 관리(수정 · 복사 · 삭제) | | 관리 |

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `packages.code` | string(50) unique | 패키지 코드 `PKG_NNNNN` | 목록 · S1 |
| `packages.title` | string(255) | 패키지명 | 목록 · S1 |
| `packages.duration_days` | integer | 수강일수 | 목록 · S1 |
| `packages.original_price` | integer | 구성품 정가 합계(서버 계산) | S1 합계 |
| `packages.sale_price` | integer | 판매 기획가(총액) | 목록 · S1 |
| `packages.display_status` | string(20) | `selling` · `hidden` · `stopped` (HasDisplayStatus) | 목록 · S1 |
| `packages.is_pass_refund` · `refund_min_progress` | boolean · tinyint | 합격 환급 대상 · 인정 진도율 | S1 환급 설정 |
| `packages.thumbnail_path` · `description` | | 대표 이미지 · 소개 | S1 |
| `packages.is_public` | tinyint | 초기 공개 여부 칸(현재 화면 미사용, 확인 필요) | — |
| `package_items` (`product_type`, `product_id`, `sort_order`, `original_price_snapshot`, `price_ratio`, `discount_amount`, `is_excluded_from_discount`) | | 구성품 · 할인 배분 원장(교재는 비율 0 · 할인 0 · 제외 1) | S1 구성 표 · 엑셀 |
| `category_products` (`product_type`='package') | | 노출 카테고리 | 목록 · S1 |
| `product_instructors` (`product_type`='package', `product_id`, `instructor_id`, `role` m/s/a, `sort_order`) | | 옛 `package_instructors`는 이름이 바뀜(2026_07_10_200000_rename_package_instructors_to_product_instructors — `package_id` → `product_type` · `product_id`, `is_main` → `role`), `settlement_rate`는 삭제됨(2026_09_15_000110_drop_settlement_rate_from_instructors_and_product_instructors). 패키지 화면은 현재 미사용(확인 필요) | — |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `searchRoot` · `searchChild` · `select[name=display_status]` · `input[name=title\|duration_min\|duration_max]` | 목록 검색 | `#filter-cat` · `#filter-status` · `#filter-display` · `#filter-keyword` |
| `actionForm` · `actionMethod` · `copyPackage()` · `deletePackage()` | 복사 · 삭제 | (없음) |
| `packageForm` | S1 폼 | 폼 영역 · `savePkgForm()` |
| `pkgTitle` · `formRoot` · `formChild` · `pkgDuration` · `salePrice` | 기본 정보 | `#f-pkg-title` · `#f-pkg-cat` · `#f-pkg-days` · `#f-pkg-total-price` |
| `isPassRefund` · `refundMinProgress` | 환급 설정 | `f-pkg-type` · `#f-refund-progress` |
| `pkgThumbBox` · `pkgThumbCurrent` · `pkgThumbSelector` · `pkg_delete_thumbnail` | 대표 이미지 | (없음) |
| `itemRows` · `courseCount` · `bookCount` · `originalTotal` · `footOriginal` · `footDiscount` · `allocationError` | 구성품 · 배분 표 | `#form-pkg-courses-tbody` · `foot-course-list-sum` · `foot-weight-sum` · `foot-allocated-sum` |
| `pvTitle` · `pvSale` · `pvItems` · `pvLines` · `pvLineCount` · `pvTotal` · `pvError` · `pvBookNote` · `alLines` · `alCheck` | 장바구니 분할 미리보기 · 배분 검산 | (없음) |
| `layerPackageSaveConfirm` · `pkgConfirmBody` · `pkgConfirmOk` | 저장 확인 | (없음) |
| `packageStop` · `packageStopForm` | 판매중지 | `#radio-pkg-*` 판매중지 선택 |
| `[data-preview]`(formaction 미리보기) | 프론트 미리보기 | (없음) |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 패키지 복사 · 삭제(soft) · 프론트 미리보기 — `routes/admin.php:465-471`
- 대표 이미지(720×405) · 패키지 소개(에디터) — `PackageRequest.php:61-64`
- 장바구니 인서트 라인 미리보기 · 배분 검산 — `form.blade.php:300-366`
- 목록 수강일수 범위 필터 · 열 정렬 — `PackageService.php:147-152,168-185`
- 목록 블라인드 사유(강사 계약 종료 강좌 포함) — `PackageService.php:205-230`
- 저장 시 구성품 정가를 서버가 다시 읽음(화면 값 불신) — `PackageService.php:520-538`

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 005-S2 읽기 전용 상세 · 변경 이력(L802-887)
- 패키지 유형 3종(합격 환급반 · 일반 종합 · 연간 프리패스 — 카테고리 전 강좌 무제한, L950-958)
- 한줄 서브 카피 `#f-pkg-summary`, 불합격 시 1회 무상 연장 `#f-pkg-extend-allow`
- 합격 환급 조건 중 필수 출석일수 · 환급 신청 기한 · 공제 항목 고정 표시 · 분담 옵션(L1189-1227). 설계서 `:239` · `:407`은 출석일수를 정본 조건으로 둠
- 정산 1계층 지분 100% 미완성 시 판매중 전환 차단(`applyPkgSettlementLock`, L2038)
- 안분 가중치 직접 수정 · 자동 안분 버튼(L989)
- 교재 연동 상태 경고 · 자동 판매중지 로그(`bk*` 함수, localStorage `sjm.prod.bookStatus.v1` 등 L1337-1523)
- 목록 유형 · 등록일 필터, 강좌 결제액 · 교재 결제액 분리 컬럼
- (v6.92) '기존 수강생 적용' 행 — 판매 이력 환급반의 인정 진도율 · 출석일수를 바꾸면 변경 전 → 후를 보여 주고 저장 때 확인. 개발은 `refund_min_progress` 현재 값 1개 · 결제 시점 스냅샷 없음. **→ 결정(v6.92 white, S-14)**: 진도율 기준 변경 소급 안 함, 결제 시점 환급 조건을 주문 라인에 박제(`order_items.refund_terms_snapshot` (규칙)).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 패키지코드 `PKG-2601` | `code` `PKG_00001` |
| `f-pkg-status` 판매중 · 판매대기 · 판매중지 · 판매종료 + `f-pkg-display` Y · N | `display_status` `selling` · `hidden` · `stopped` (1칸) |
| `f-pkg-type` 환급반 | `is_pass_refund=1` |
| `#f-refund-progress` 필수 진도율 | `refund_min_progress` 인정 진도율 |
| `#f-pkg-days` | `duration_days` |
| `#f-course-discount` 강좌 할인액 | (입력 없음) `sale_price` − 구성품 정가 합계 = 총할인 |
| `#f-pkg-total-price` 총 판매가 | `sale_price` 판매 기획가 |
| 매출 안분 가중치(%) | `package_items.price_ratio` |
| 패키지 내 안분 매출액 | `original_price_snapshot` + `discount_amount`(음수) |
| 강좌코드 · 교재 SKU | `items[n][product_type]` + `product_id` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-PROD005-1 | 패키지 안 교재 라인 금액: 정본은 '포함 교재 실결제액 = 정가 대비 최대 10% 기본할인가'(실판매가). 개발은 교재 **정가**(`books.original_price`)를 그대로 쓰고 할인 0 | 설계서 `:238`, 프로토 `recalcPackagePricing` L2020(`b.sale`) · 교재 표 '도서 정가 / 실판매가' L1034 | `app/Repositories/Admin/PackageRepository.php:282-285`, `app/Services/Product/PackagePricingService.php:84-88` **→ 정본대로(POLICY_D_PROD A, 통합설계서 S2-05 · 02권)**: 패키지 교재 라인 = 실판매가(정가 대비 최대 10% 할인) — 개발팀 전달 |
| Q-PROD005-2 | 강좌 할인 안분 기준: 정본은 '단과 기준가(판매가) 비율 안분' + 운영자 가중치 조정 허용. 개발은 강좌 **정가** 비율 자동 안분, 수정 불가. 입력도 정본은 강좌 할인액, 개발은 패키지 총액 | 설계서 `:224`, 프로토 L1889-1901(`baseSalePrice`) · L1917 · L2019 | `PackagePricingService.php:1-45`(배분 규칙 주석), `PackageRepository.php:272-275`, `PackageRequest.php:56` **→ 정본대로(D-PROD-04 A, 02권 8.3 · 00 INDEX §2)**: 정가 비율 자동 안분 · 수동 조정 없음 — 개발이 맞음, 설계서 문구 정정(v3.2.21) |
| Q-PROD005-3 | 판매 상태: 정본 공통 4상태(판매대기 · 판매중 · 판매중지 · 판매종료, 판매종료는 미노출 고정) + 프론트 노출 Y/N. 개발은 `selling` · `hidden` · `stopped` 3값 1칸. 판매대기 · 판매종료를 추가하고 노출을 별도 칸으로 둘지 | 설계서 `:246`(2026-10-26 확정), 프로토 L1142-1168 | `app/Models/Concerns/HasDisplayStatus.php:19-30`, `PackageRequest.php:57` **→ 정본대로(POLICY_D_PROD A, 통합설계서 L248(2026-10-26 확정))**: 공통 4상태 + 노출 Y/N 별도 칸 — 개발에 `ready` · `ended` 추가 전달 |
| Q-PROD005-4 | 판매중 전환 게이트: 프로토는 포함 강좌 1계층 지분 합계 100% 미만이면 판매중 선택 잠금. 개발 저장 검증에 지분 확인 없음(구성품 판매 상태만 봄) | 프로토 L1121 · L2038-2058 | `PackageRequest.php:98-187`(지분 검증 없음) **→ 정본대로(POLICY_D_PROD A, 통합설계서 S2-02 · 01권 4.2)**: 포함 강좌 1계층 지분 100% 전까지 판매중 불가 — 개발팀 전달 |
| Q-PROD005-5 | 환급 분담 옵션(A · B · C) 단위: 프로토 PROD-005는 패키지마다 고름. 프로토 INST-001 · 개발은 권리자 계약 단위(`refund_promo_burden_type`). 정본끼리도 갈림 | 프로토 PROD-005 L1227, 프로토 INST-001 `#refundBurden` L875, 설계서 `:239` | `app/Http/Requests/Admin/RightsHolderContractRequest.php:89`, `packages` 테이블에 칸 없음(`_index/schema.md` packages) **→ 정본대로(POLICY_D_PROD A, 01권 15.3 · 설계서 Flow 2-1)**: 환급 부담 옵션은 계약 단위 — 개발이 맞음, 프로토 PROD-005는 계약 값 읽기 전용 표시 |
| Q-PROD005-6 | 구성 교재가 판매중이 아닐 때: 정본은 주교재 판매중지 · 종료 → 패키지 자동 판매중지, 주교재 일시품절 → 구매만 일시 차단, **부교재는 경고만**. 개발은 구성품(강좌 · 교재 구분 없이) 하나라도 판매중이 아니면 패키지 저장 자체를 막고, 자동 판매중지 연동은 없음 | 설계서 `:248`(2026-10-26 확정), 프로토 `bkSyncPkgs` L1426 | `PackageRequest.php:150-187` **→ 정본대로(POLICY_D_PROD A, 통합설계서 L249(2026-10-26 확정))**: 주교재만 자동 판매중지, 부교재 · 일시품절은 패키지 저장 허용으로 완화 — 개발팀 전달 |
| Q-PROD005-7 | 합격 환급 조건 항목: 정본은 진도율 + 필수 출석일수(+ 신청 기한). 개발은 인정 진도율 1개만 | 설계서 `:407`, 프로토 L1189-1214 | `PackageRequest.php:58-60`, `packages.refund_min_progress` **→ 정본대로(POLICY_D_PROD A, 통합설계서 L408)**: 필수 출석일수 칸 추가 — 개발팀 전달(신청 기한은 정본에 없어 문서 정정 제안으로) |
