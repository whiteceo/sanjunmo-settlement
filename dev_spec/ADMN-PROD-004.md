# ADMN-PROD-004 교재 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-004_baseline.html` (원본 상태: d6723b0 v7.01)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- v7.01 정본 변경: 재고 2단 차감(white 결정 Q-3PL-1, 설계서 v3.2.25): 결제 완료 → 예약(가용 감소), 3PL 송장 업로드 → 실재고 확정 차감. 화면은 실재고 · 예약 · 가용 3칸. 개발은 재고 1칸(books.stock · goods.stock, 결제 시 즉시 차감)이라 예약 · 가용은 개발 미구현 — reserved_stock (규칙), 가용 = stock − reserved_stock 파생. 개발팀 전달 대상
- 포함 화면: PROD-004 교재 목록 · 004-S2 교재 상세 · 재고이력 · 004-S1 교재 등록/수정 + 모달 4개(`modal-temp-book` 가채번 불러오기 · `modal-supply-sku` 공급원장 SKU 불러오기 · `modal-stock-adjust` 재고 수불 · `modal-autostop-confirm` 연결 상품 자동 판매중지 확인)
- 개발 진행: 구현(목록 · 등록 · 수정 · 재고 조정 · 판매중지 · 재고 이력 레이어). 교재 상세 화면 · 가채번/공급원장 불러오기 · 3원장 신호등은 미구현

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 004 교재 목록 | PROD-004 목록 | `resources/views/admin/books/index.blade.php` |
| 004-S2 교재 상세 · 재고이력 | 없음(재고 이력은 수정 화면 레이어 `layerStockLogs`) | `books/edit.blade.php:119` |
| 004-S1 교재 등록/수정 | PROD-004-S1 등록 · 수정 | `books/create.blade.php` · `edit.blade.php` + 공통 `form.blade.php` |
| `modal-stock-adjust` | 재고 조정 레이어 `layerStockAdjust` | `edit.blade.php:59-110` |
| `modal-autostop-confirm` | 판매중지 확인 레이어 `layerBookStop`(영향 패키지 표시만) | `edit.blade.php:177-215` |
| `modal-temp-book` · `modal-supply-sku` | 없음 — 개발 미구현 | — |
| 공급 형태 · 정가 변경 | 도서 공급 원장(BOOK-001, `admin.book-supply.*`) 소관 | `form.blade.php:209` 이동 버튼 |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.books.index` | 교재 관리(추정) | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 권한 축 5개. 재고 조정 · 판매중지는 수정(`stock.update` · `stop.update`), 복사는 등록, 엑셀 · 선택 다운로드는 다운로드.
- 사입 원가(`books.cost_price`)는 메뉴 권한과 별도로 역할 `finance`(재무) 또는 최고 관리자만 본다 · 저장한다(`AdminPermissionService.php:23, 126-145` `canManageCostPrice`). 프로토 `#role-mask-select`(재무팀 원가 열람) · `applyRoleCostMasking()`과 같은 규칙.
- 교재 첨부(표지 외 미리보기 · 상세 이미지) 다운로드는 `book` → `admin.books.index` 메뉴로 판정(`AttachmentController.php:33`).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{book}` = `books.id`. 근거 `routes/admin.php:370-388`.

### PROD-004 교재 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 | GET | `/books` | `admin.books.index` | 조회 | BookController@index |
| 엑셀 다운로드(사유) | GET | `/books/download` | `admin.books.download` | 다운로드 | BookController@download |
| 선택 다운로드(`ids[]`) | POST | `/books/download-selected` | `admin.books.selected.download` | 다운로드 | BookController@downloadSelected |
| 행 [복사] | POST | `/books/{book}/copy` | `admin.books.copy.store` | 등록 | BookController@copy (`actionForm`) |
| 행 [삭제] | DELETE | `/books/{book}` | `admin.books.destroy` | 삭제 | BookController@destroy (`actionForm` + `actionMethod`) |
| 선택 레이어용 목록(강좌 · 패키지 폼) | GET | `/api/books` | `admin.api.books` | 로그인 + 상품 메뉴 조회 | BookController@apiList |

### 프로토 004-S2 교재 상세 · 재고이력 (개발 미구현, 규칙 기반 명명)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세 조회 | GET | `/books/{book}` (규칙) | `admin.books.show` (규칙) | 조회 | 개발 미구현 — 개발은 행 클릭이 수정 폼, 재고 이력은 수정 화면 레이어 |

### PROD-004-S1 교재 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/books/create` | `admin.books.create` | 등록 | BookController@create |
| 저장(신규) | POST | `/books` | `admin.books.store` | 등록 | BookController@store |
| 수정 폼(+ 재고 조정 · 재고 이력 · 판매중지 레이어) | GET | `/books/{book}/edit` | `admin.books.edit` | 수정 | BookController@edit |
| 저장(수정) | PUT | `/books/{book}` | `admin.books.update` | 수정 | BookController@update |
| 재고 조정(`modal-stock-adjust`) | PUT | `/books/{book}/stock` | `admin.books.stock.update` | 수정 | BookController@stockAdjust |
| 판매중지(`modal-autostop-confirm`) | POST | `/books/{book}/stop-selling` | `admin.books.stop.update` | 수정 | BookController@stopSelling |
| 공급 형태 · 정가 변경 | → | `/book-supply/{book}/edit` · `PUT /book-supply/{book}/prices` | `admin.book-supply.edit` · `admin.book-supply.prices.update` | 수정(BOOK-001 메뉴) | BookSupplyController |
| 가채번 도서 불러오기(`modal-temp-book`) | GET | `/books/royalty-contracts` (규칙) | `admin.books.royalty-contracts.index` (규칙) | 조회 | 개발 미구현(`book_royalty_contracts`에 원장 필드만, mig 2026_10_16_000215) |
| 공급원장 SKU 불러오기(`modal-supply-sku`) | GET | `/books/supply-skus` (규칙) | `admin.books.supply-skus.index` (규칙) | 조회 | 개발 미구현(개발은 등록 후 BOOK-001에서 공급 형태 지정) |
| ISBN 검증 | — | (서버 검증 `isbnRule()`만) | | | 프로토 `validateIsbnField()` 버튼 |

## 3. 폼 필드 · 검증

### 004 목록 검색 (GET, `BookService` 필터 · `index.blade.php:30-150`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `title` · `author` · `publisher` · `isbn` | text 각각 | `#filter-keyword` 1칸(교재명 / SKU / 가채번 / ISBN / 저자명) |
| `category_id` | 자격증 종류(카테고리) | `#filter-cat` |
| `stock_status` | `normal` 정상 · `low` 임계치 이하 · `soldout` 품절 (`Book::STOCK_STATUS_LABELS`) | `#filter-stock` 전체 · 안전재고 미달 · 품절 |
| `is_free` | 판매 구분(유료/무료) | 프로토 없음 |
| `instructor_id` | 강사 | 프로토 없음 |
| `display_status` | `selling` · `hidden` · `stopped` | `#filter-status` 판매중 · 예약판매 · 판매대기 · 일시품절 · 판매중지 · 판매종료 + `#filter-display` Y · N |
| `published_from` · `published_to` | 발행일 기간 | 프로토 없음 |
| `book_supply_type` | `OWN_PUBLISHED` 자사 발행 · `PURCHASED_RESALE` 매입 재판매 · `CONSIGNMENT` 위탁 · `BUNDLED` 부속 (`BookSupplyService::SUPPLY_LABELS`) | 프로토 없음(`#filter-origin` 등록 출발 경로 `INST_TEMP` 등은 개발 없음) |

### 004-S1 교재 저장 (BookRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (교재 코드) | 서버 채번 `BK_00001` | | `#f-sku`(예 `PROD-BK-1011`) |
| (가채번 코드) | 개발 없음 | | `#f-temp-code`(예 `BK-REQ-2026-0011`) |
| `title` | required · max 255 | | `#f-title` |
| (부제) | 개발 없음 | | `#f-subtitle` |
| `category_id` | required · 2Depth만 · `category_products` 대표 | | `#f-cat` |
| `cert_category_ids[]` | nullable · 1Depth만 · distinct (자격증 종류 복수) | | 프로토 없음 |
| `isbn` | 부속(BUNDLED) 외 required · max 30 · 전체 유일 · 형식 검사 | | `#f-isbn` + `validateIsbnField()` |
| `author` · `publisher` | required · max 100 | | `#f-author` · `#f-publisher` |
| `instructors[n][instructor_id]` · `[role]` | nullable · `m` · `s` · `a` · distinct | 저자 강사 매핑 | `#f-author-inst`(권리자 1명 선택) |
| `published_at` · `edition` | date · max 50 | 발행일 · 판쇄 | `#f-pub-date` |
| `is_free` | 등록 때만 · boolean (1이면 가격 0, 도서정가제 제외) | | 프로토 없음 |
| `original_price` | 등록 때만 required · ≥ 0 (수정은 exclude — BOOK-001 정가 이력) | | `#f-list-price` |
| `sale_price` | 등록 때만 required · ≤ 정가 · 정가 × (1 − `site_settings.book_discount_rate_limit`%) 이상(기본 한도 0%) | | `#f-sale-price`(자동) ← `#f-book-discount-rate`(0~10%) |
| `cost_price` | exclude — BOOK-001에서만 | 사입 원가(재무 역할만) | 목록 '공급원가(BOOK-001)' |
| (공급 형태) | 교재 폼에서 받지 않음(`LEDGER_OWNED_KEYS`, `BookService.php:40-47`) — 수정 화면에 🔒 표시 + BOOK-001 이동 | `book_supply_type` 4종 | `#f-supply-ledger` · `#f-supply-vendor` (`onSupplyLedgerChange()`) |
| `stock` | 등록 때만 required · ≥ 0 (이후 재고 조정으로만) | | `#f-stock-qty` |
| `stock_alert_qty` | nullable · ≥ 0 | 품절 임박 기준 | `#f-safe-stock`(20) |
| `is_preorder` · `restock_date` | boolean · date (요청 규칙만 있고 폼에는 `restock_date`만 있음, `is_preorder` · `release_date` 입력칸 없음) | 예약 판매 · 재입고 예정일 | `#f-is-preorder` · `#f-release-date`(출간 예정일) |
| `delivery_fee` · `is_free_delivery` · `free_delivery_threshold` · `island_delivery_fee` · `return_delivery_fee` · `package_bundled_yn` | nullable · int/boolean | 배송 정책 | '배송비 정책' 칸 |
| `page_count` · `book_size` | int · max 50 | 페이지 · 판형 | 프로토 없음 |
| `display_status` | required · `selling` 전시 · 판매중 · `hidden` 비전시 · `stopped` 판매중지 | | `radio-book-*` 6종 + 노출 Y/N (Q-PROD004-2) |
| `description` · `table_of_contents` | nullable | 소개 · 목차 | `#f-book-desc`(1칸) |
| `thumbnail` · `delete_thumbnail` | jpg/png/webp · 5MB · 700×980 이상 · 5:7 | 표지 | '교재 표지 이미지' |
| `preview_images[]` · `detail_images[]` · `deleted_attachments[]` | 이미지 5MB | 미리보기 · 상세 이미지 | '미리보기 샘플 PDF'(프로토는 PDF 1개) |

### 재고 조정 (BookStockAdjustRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `type` | required · `BookStockLog::ADJUST_TYPE_LABELS` | `in` 입고 · `return_in` 반품 입고 · `disposal` 파본 폐기 · `audit` 실사 조정 | `#modal-stock-type` 신규 인쇄/사입 입고 · 고객 반품 양품 입고 · 파손/오염 재고 차감 · 물류센터 재고실사 차감 |
| `quantity` | required · integer · ≠ 0 (음수 = 차감) | | `#modal-stock-qty` |
| `memo` | nullable · max 255 | | `#modal-stock-reason`(프로토는 필수 *) |

이력 표기용 추가 코드: `order_out` 주문 출고 · `order_restore` 주문 취소 복원(`BookStockLog::TYPE_LABELS`).

## 4. 목록 필터 · 정렬 · 표 컬럼 (004)
| 개발 컬럼 | 프로토타입 컬럼 |
|---|---|
| 선택 체크(`#checkAll` · `ids[]`) | 없음 |
| No | No |
| 교재코드(`code`) | 교재 SKU / 가채번 |
| (없음) | 등록 출발 경로(경로 1 · 2 · 3) |
| 교재명 | 교재명 |
| 저자 · 출판사(2컬럼) | 저자 / 출판사 |
| ISBN · 발행일 | (상세에만) |
| 공급 형태 | (없음 — 신호등에 포함) |
| 판매가 (= 정가) | 정가(면세) |
| 사입 원가(재무 역할만 컬럼 표시) | 공급원가(BOOK-001)(역할 마스킹) |
| (없음) | 3원장 연동 신호등(계약 · 원가 · 매핑) |
| 현재 재고 · 재고 상태 | 현재 재고 |
| 연결 상품 수 | (없음) |
| 전시 상태 | 판매상태 |
| (없음) | 등록일 |
| 관리 [수정] [복사] [삭제] | 관리 |

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `books.id` · `code` | id · string(50) | PK · `BK_00001` | 교재코드 |
| `books.isbn` | string(30) unique | ISBN | ISBN |
| `books.title` · `author` · `publisher` · `published_at` · `edition` | | 서지 | 기본 정보 |
| `books.original_price` · `sale_price` | int | 정가 · 판매가(정가 이력은 `book_price_histories`) | 가격 |
| `books.cost_price` | int | 사입 원가(재무만) | 사입 원가 |
| `books.is_free` | boolean | 무료 도서 | 판매 구분 |
| `books.stock` · `stock_alert_qty` | int | 재고 · 품절 임박 기준 | 재고 |
| `books.is_preorder` · `release_date` · `restock_date` | | 예약 판매 · 출간 예정일 · 재입고 예정일 | 예약판매 |
| `books.delivery_fee` · `is_free_delivery` · `free_delivery_threshold` · `island_delivery_fee` · `return_delivery_fee` · `package_bundled_yn` | `is_free_delivery` tinyint(1) NOT NULL(금액 조건과 무관하게 항상 무료배송, 2026_09_30_000177) | 배송 정책 | 배송비 정책 |
| `books.book_supply_type` · `settlement_required_yn` · `cost_account_type` · `supplier_id` · `own_copyright_yn` | | 공급 형태 · 정산 대상 · 원가 계정 · 매입처 · 자사 권리(BOOK-001 소관) | 공급 형태 🔒 |
| `books.display_status` | string(20) | `selling` · `hidden` · `stopped` | 전시 상태 |
| `books.page_count` · `book_size` · `thumbnail_path` · `description` · `table_of_contents` | | 상세 | 상세 콘텐츠 |
| `books.deleted_at` | timestamp nullable | 소프트 삭제 (2026_09_08_000092) | — |
| `book_stock_logs` (`type`, `quantity`, `before_stock`, `after_stock`, `order_id`, `admin_id`, `memo`) | | 재고 수불 | 재고 이력(프로토 :982 표) |
| `book_authors` · `product_instructors`(`product_type`='book', `product_id`, `instructor_id` foreignId, `role`, `sort_order`) | | 저자 · 강사 매핑(`Book::instructors()`, 색인 주석은 course / package지만 모델이 book으로도 쓴다) | 저자 |
| `category_products` (`product_type=book`, `is_primary` 1 = 노출 2Depth, 0 = 자격증 종류 1Depth) | | 카테고리 | 카테고리 |
| `course_books` · `package_items` | | 연결 강좌 · 패키지 | 연결 상품 · 판매중지 영향 |
| `book_royalty_contracts` | | 인세 계약(가채번 연동 후보, 확인 필요) | 프로토 `modal-temp-book` |
| `site_settings.book_discount_rate_limit` | decimal(5,2) 기본 0 | 도서 할인 한도 % | 판매가 검증 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `listForm` · `checkAll` · `actionForm` · `actionMethod` | 목록 선택 · 행 복사/삭제 제출 | 없음 |
| `isbn` · `isbnFormat` | ISBN · 형식 안내 | `#f-isbn` · `validateIsbnField()` |
| `isFree` (`toggleFreeBook()`) | 무료 도서 | 없음 |
| `original_price` · `sale_price` · `discountRate` | 가격 · 할인율 표시 | `#f-list-price` · `#f-sale-price` · `#f-book-discount-rate` (`syncBookSalePrice()`) |
| `thumbnailBox` · `thumbnailCurrent` · `thumbnailSelector` · `delete_thumbnail` · `thumbnailNew` | 표지 | 표지 파일 선택 |
| `existingPreviewImages` · `newPreviewList` · `previewSelector` · `existingDetailImages` · `newDetailList` · `detailSelector` | 미리보기 · 상세 이미지 | 미리보기 PDF |
| `instructorRows` · `instructorEmptyRow` | 저자 강사 | `#f-author-inst` |
| `layerStockAdjust` (`type` · `quantity` · `memo`) | 재고 조정 | `modal-stock-adjust` (`#modal-stock-type` · `#modal-stock-qty` · `#modal-stock-reason`, `confirmStockAdjust()`) |
| `layerStockLogs` | 재고 이력 | 004-S2 재고 이력 표 |
| `layerBookStop` | 판매중지 확인(깨지는 패키지 목록) | `modal-autostop-confirm` (`confirmAutoStop()`) |
| (없음) | 가채번 · 공급원장 불러오기 | `modal-temp-book` · `modal-supply-sku` · `selectEntryMode()` |
| (없음) | 3원장 신호등 | `updateTopStepperByBook()` · `#step1-light` 등 |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 무료 도서(`is_free`), 자격증 종류 복수(`cert_category_ids[]`), 판형 · 페이지 · 판쇄, 미리보기 · 상세 이미지 여러 장
- 배송 정책 세부(개별 배송비 · 무조건 무료 · 조건부 무료 기준 · 도서산간 · 반품 배송비 · 패키지 동봉 적용)
- 정가 · 판매가 · 무료 여부 · 초기 재고는 등록 때만, 이후 정가는 BOOK-001 정가 이력, 재고는 재고 조정으로만(`BookRequest.php:96-112`)
- 공급 형태 · 사입 원가 · 매입처는 BOOK-001 소관(교재 폼은 🔒 표시)
- 도서 할인 한도를 사이트 설정 `book_discount_rate_limit`(기본 0%)로 서버 검증(`BookRequest.php:255-281`)
- 판매중지 시 깨지는 패키지 목록 확인 레이어, 목록 복사 · 삭제 · 선택 다운로드, 재고 상태 · 공급 형태 · 발행일 · 강사 필터, 연결 상품 수 컬럼

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 3-Way 등록(경로 1 계약원장 가채번 불러오기 · 경로 2 공급원장 SKU 불러오기 · 경로 3 직접 등록)과 가채번 코드 · 등록 출발 경로 필터/컬럼
- 도서 3원장 4단계 신호등(:726-780) · 목록 3원장 연동 신호등 컬럼(:885)
- 교재 상세 조회 화면(004-S2) — 개발은 수정 화면 레이어로 재고 이력만
- 판매 상태 6종(예약판매 · 판매대기 · 일시품절 · 판매종료 포함) + 노출 Y/N (Q-PROD004-2)
- 주교재 판매중지 · 판매종료 시 연결 강좌 · 패키지 자동 판매중지(`bkAutoStopTargets()` · `confirmAutoStop()`, PROD-003 :1686-1689) (Q-PROD004-1)
- 재고 0권 판매 하드락 시뮬레이션(`checkZeroStockHardLock()`) — 개발은 재고 0이면 전시와 별개로 품절 처리(`form.blade.php:550-556`)
- 부제(`#f-subtitle`), 재고 조정 사유 필수

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| SKU `PROD-BK-1011` | `books.code` `BK_00001` |
| `#f-title` · `#f-isbn` · `#f-author` · `#f-publisher` · `#f-pub-date` · `#f-list-price` · `#f-sale-price` | `title` · `isbn` · `author` · `publisher` · `published_at` · `original_price` · `sale_price` |
| `#f-stock-qty` · `#f-safe-stock` · `#f-is-preorder` · `#f-release-date` | `stock` · `stock_alert_qty` · `is_preorder` · `release_date`(DB 컬럼만, 개발 폼 입력칸 없음) |
| `#f-book-discount-rate`(0~10%) 입력 | 판매가 직접 입력 + 한도 `book_discount_rate_limit` 검증 |
| 재고 유형 4종(한글) | `in` · `return_in` · `disposal` · `audit` |
| 안전재고 미달 · 품절 | `stock_status` `low` · `soldout` |
| 판매상태 6종 + 노출 Y/N | `display_status` `selling` · `hidden` · `stopped` (+ `is_preorder`, 재고 파생 품절) |
| 공급 형태 셀렉트(`#f-supply-ledger`) | `book_supply_type` `OWN_PUBLISHED` · `PURCHASED_RESALE` · `CONSIGNMENT` · `BUNDLED` (BOOK-001에서 지정) |
| 재무팀 원가 열람 역할 | 역할 코드 `finance` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
- **Q-PROD004-1 주교재 판매중지 · 판매종료 시 연결 강좌 · 패키지 자동 판매중지** — 정본 프로토(v6.42): 주교재가 판매중지 · 판매종료되면 연결 강좌 · 패키지를 자동 판매중지하고 [판매중] 선택을 잠근다(복귀는 수동), 일시품절은 구매만 일시 중지, 부교재는 경고만(`prototype_clean/ADMN-PROD-003_baseline.html:1686-1689`, `ADMN-PROD-004_baseline.html` `modal-autostop-confirm` :1535 · `bkAutoStopTargets()`). 개발: 교재 판매중지는 교재만 `stopped`로 바꾸고 "패키지 N건의 판매 가능 상태가 깨집니다" 문구만 보여 준다. 강좌는 보지 않는다(`app/Services/Admin/BookService.php:287-320`). 자동 판매중지를 넣을지, 경고만 둘지. **→ 정본대로(POLICY_D_PROD A, 통합설계서 L249(2026-10-26 확정))**: 주교재 판매중지 · 판매종료 시 연결 강좌 · 패키지 자동 판매중지(복귀 수동), 일시품절은 구매만 차단, 부교재는 경고만 — 개발팀 전달
- **Q-PROD004-2 교재 판매 상태 체계** — 정본 프로토: 판매중 · 예약판매 · 판매대기(원장 매핑 대기) · 일시품절(재고 0) · 판매중지(구매 차단) · 판매종료(구판 · 절판) 6종 + 노출 Y/N(`ADMN-PROD-004_baseline.html:1290-1326`, 필터 :823). 개발: `display_status` 3값(`selling` · `hidden` · `stopped`) + `is_preorder` + 재고 파생 품절(`BookRequest.php` `display_status`, `form.blade.php:540-556`). 특히 '판매대기(원장 매핑 대기)'는 3원장 매핑 전 판매를 막는 규칙인데 개발에 없다. PROD-003 Q-PROD003-1과 함께 결정. **→ 정본대로(POLICY_D_PROD A, 통합설계서 L248(2026-10-26 확정))**: 교재 6종 + 노출 Y/N 별도 칸, 판매대기(매핑 대기) 판매 차단 포함 — 개발팀 전달
- **Q-PROD004-3 도서 할인 한도 기본값** — 정본 프로토: 도서정가제 상한 10% 이내 기본 할인 `book_discount_rate` 0~10% 입력(`ADMN-PROD-004_baseline.html:780-782`, 헤더 :687). 개발: 교재별 할인율 칸 없이 판매가를 직접 넣고, 한도는 사이트 설정 `book_discount_rate_limit` 기본 0%(`database/migrations/2026_09_21_000149_add_v7_settings_to_site_settings_table.php:26`, `BookRequest.php:268-280`). 기본 0%면 교재 할인이 막힌다. 한도 기본값을 10%로 둘지, 교재별 할인율 칸을 둘지. **→ 정본대로(POLICY_D_PROD A, 통합설계서 기본 할인율 0~10% · S2-04 · 출판문화산업 진흥법 제22조)**: 교재별 `book_discount_rate`(0~10%), `book_discount_rate_limit`은 쿠폰 · 포인트 추가 할인 한도로 정리 — 개발팀 전달
- **Q-PROD004-4 교재 등록 출발 경로(3-Way)** — 정본 프로토: 계약원장 가채번(BK-REQ) 불러오기 시 저자 인세 자동 상속, 공급원장 SKU 불러오기, 직접 등록 3경로(:814-816, `modal-temp-book` :1381, `modal-supply-sku` :1433). 개발: 교재 관리에서 먼저 등록하고 공급 형태는 BOOK-001에서 나중에 지정, 가채번 연결 화면 없음(`BookService.php:40-47` `LEDGER_OWNED_KEYS`, `form.blade.php:198-213` "등록 후 도서 공급 원장에서 지정합니다"; `BookRequest.php` 주석 "미확정: 부속 도서는 원장에서 먼저 등록"). 어느 원장이 출발점인지(등록 순서) 정할 것. **→ 정본대로(D-PROD-03 A, 통합설계서 L244-246 · PROJECT_STATE 1절 2026-10-23)**: 3경로 출발 허용, 공급 형태 등록 시 필수 · `PROD-BK` 채번, 가채번(BK-REQ) 연결 — 개발팀 전달 + 프로토 채번 앞자리 수정
