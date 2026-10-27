# ADMN-BOOK-001 도서 공급 원장 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-BOOK-001_baseline.html` (원본 상태: d6723b0 v7.01)
- 맞춘 개발 커밋: `a8016168` (2026-10-27) — d562524a 이후 이 화면 변경은 `suppliers.code` 주석 정정(e555839b)뿐
- v7.01 정본 변경: 재고 2단 차감(white 결정 Q-3PL-1, 설계서 v3.2.25): 결제 완료 → 예약(가용 감소), 3PL 송장 업로드 → 실재고 확정 차감. 화면은 실재고 · 예약 · 가용 3칸. 개발은 재고 1칸(books.stock · goods.stock, 결제 시 즉시 차감)이라 예약 · 가용은 개발 미구현 — reserved_stock (규칙), 가용 = stock − reserved_stock 파생. 개발팀 전달 대상
- 포함 화면: BOOK-001 공급 원장 목록 · BOOK-001-S1 SKU · 공급원가 등록/수정 · 정가 변경 이력 모달 · [경로 1] 가채번 도서 불러오기 모달 · [경로 3] 선등록 SKU 불러오기 모달
- 개발 진행: 일부 구현. 목록 · 공급 정보 등록/수정 · 신규 SKU 발급 · 정가 변경 등록 · 매입처 등록 · 위탁 도서 탭 · 엑셀은 있음. **SKU(교재) 신규 채번은 개발에서 교재 관리(PROD-004) 몫**이고 이 화면은 기존 교재에 공급 정보를 붙인다. 가채번 · 선등록 불러오기 모달은 미구현. `_index/progress.md` BOOK-001 커밋 언급 10건(라우트 주석 없음)

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| BOOK-001 공급 원장 목록(L665) | 탭 `list` 도서 공급 원장 | `resources/views/admin/book-supply/index.blade.php` |
| BOOK-001-S1 등록 · 수정(L669) | 공급 정보 등록 · 수정 | `book-supply/edit.blade.php` + `form.blade.php` |
| `modalBookPriceHistory`(L864) | 탭 `prices` 정가 이력 + 정가 변경 등록 폼 | `book-supply/_prices.blade.php` |
| (프로토 없음) | 탭 `suppliers` 매입처 | `book-supply/_suppliers.blade.php` |
| (프로토 없음) | 탭 `consignment` 위탁 도서 | `book-supply/_consignment.blade.php` |
| `modal-inst-temp`(L1292) [경로 1] | 없음 | — |
| `modal-prod-pending`(L1338) [경로 3] | 없음(개발은 등록 폼 `book_id` select가 '공급 형태 없는 교재' 목록 — 기능상 가장 가까움) | `form.blade.php:20-31` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.book-supply.index` | 도서 공급 원장(라우트 주석 `routes/admin.php:433` "재무 메뉴 권한 전용") | 목록 · S1 · 모달 전부 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 버튼 노출: `@adminCan('admin.book-supply.index', …)` (`index.blade.php:92,104,141`, `_prices.blade.php:83`, `_suppliers.blade.php:44`, `form.blade.php:119`).
- 사입 원가 열람 · 입력은 재무 권한(`BookSupplyService::canViewCost`, `BookSupplyService.php:83-87`). 프로토는 `#role-mask-select`로 시연(L658).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{book}` = `books.id`.

### BOOK-001 목록 · 탭
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(`?tab=list\|prices\|suppliers\|consignment`) | GET | `/book-supply` | `admin.book-supply.index` | 조회 | BookSupplyController@index |
| 엑셀(사유) | GET | `/book-supply/download` | `admin.book-supply.download` | 다운로드 | BookSupplyController@download |
| 매입처 등록(탭 suppliers) | POST | `/book-supply/suppliers` | `admin.book-supply.suppliers.store` | 등록 | SupplierController@store |

### BOOK-001-S1 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/book-supply/create` | `admin.book-supply.create` | 등록 | BookSupplyController@create |
| 등록(기존 교재에 공급 정보) | POST | `/book-supply` | `admin.book-supply.store` | 등록 | BookSupplyController@store |
| 수정 폼 | GET | `/book-supply/{book}/edit` | `admin.book-supply.edit` | 수정 | BookSupplyController@edit |
| 수정 | PUT | `/book-supply/{book}` | `admin.book-supply.update` | 수정 | BookSupplyController@update |
| 신규 SKU 발급(기존 SKU 판매중지 → 교재 등록 화면으로) | PUT | `/book-supply/{book}/reissue` | `admin.book-supply.reissue.update` | 수정 | BookSupplyController@reissue |
| [경로 1] 가채번 도서 조회 | GET | `/book-supply/temp-books` (규칙) | `admin.book-supply.temp-books.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명(데이터는 `book_royalty_contracts.temp_code`에 있음) |
| [경로 3] 원가 미입력 선등록 SKU 조회 | GET | `/book-supply/pending-books` (규칙) | `admin.book-supply.pending-books.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명 |

### 정가 변경 이력 (프로토 모달 · 개발 탭)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 이력 조회 | GET | `/book-supply?tab=prices&book_id=` | `admin.book-supply.index` | 조회 | BookSupplyController@index |
| 정가 변경 등록 | PUT | `/book-supply/{book}/prices` | `admin.book-supply.prices.update` | 수정 | BookSupplyController@storePrice |

## 3. 폼 필드 · 검증

### 목록 검색 (GET, `BookSupplyService.php:104-115`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `keyword` | 도서명 / ISBN / SKU / 관리코드, 100자 | `#filter-keyword` |
| `book_supply_type` | `OWN_PUBLISHED` 자사 발행 · `PURCHASED_RESALE` 매입 재판매 · `CONSIGNMENT` 위탁 · `BUNDLED` 부속 | `#filter-supply-type` 자체출판(인세) · 위탁판매 · 사입판매 · 비매품(번들) |
| `settlement` | `Y` · `N` 정산 대상 | 프로토 없음 |
| `sales` | `yes` · `no` 판매 이력 | 프로토 없음 |
| `tab` | `list` · `prices` · `suppliers` · `consignment` | 프로토 탭 없음 |
| (출발 경로) | 개발 없음 | `#filter-origin` `INST_TEMP` · `BOOK_LEDGER` · `PROD_DIRECT` |
| (원가 확정 상태) | 개발 없음 | `#filter-cost-status` `CONFIRMED` · `PENDING` |
| (공급처) | 개발 없음 | `#filter-supplier` |
| (적용 기준일) | 개발 없음 | 날짜 input(L982) |

### S1 공급 정보 (BookSupplyRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `book_id` | 등록 required(공급 형태 없는 기존 교재) · 수정 prohibited | books.id | `#f-sku` 정식 SKU(`PROD-BK-1011`, 이 화면에서 채번) — 8절 Q1 |
| (가채번 코드) | 개발 없음(계약 쪽 `book_royalty_contracts.temp_code`) | | `#f-temp-code` `BK-REQ-2026-0011` |
| (도서명 · ISBN · 저자 · 공급처) | 교재 관리(PROD-004) 값 읽기 전용 표시 | | `#f-title` · `#f-isbn` · `#f-author` · `#f-ins-code` · `#f-supplier` |
| `book_supply_type` | required · 선택지 `OWN_PUBLISHED` · `PURCHASED_RESALE` · `BUNDLED` (**`CONSIGNMENT` 저장 거부 — 2차**). 판매 이력 있으면 변경 불가 | `OWN_PUBLISHED` 자사 발행 · `PURCHASED_RESALE` 매입 재판매 · `BUNDLED` 부속 | `f-supply-type` 자체출판(인세) · 위탁판매 · 사입판매 · 비매품(번들) — 8절 Q2 |
| `own_copyright_yn` | nullable boolean, OWN_PUBLISHED면 필수(서비스) | `0` 외부 저작권자 · `1` 자사 보유 | `f-own-copyright` `false` · `true` |
| `supplier_id` | PURCHASED_RESALE면 필수(서비스) | suppliers.id | `#f-supplier` |
| `cost_price` | nullable · 0~100,000,000 · 재무 권한만 | | `#f-supply-cost`(공급률 × 정가 자동) |
| (정산 대상 · 정산 경로) | 표시 `#settlementRequired` · `#settlementRoute` (공급 형태 파생) | `SETTLEMENT_ROUTE_LABELS` | 목록 '정산 파이프라인 라우팅'(L773) |
| (도서 정가) | 이 폼에 없음 — 정가 변경 등록(`prices.update`)으로만 | | `#f-price` |
| (공급률 / 제조원가율) | 개발 없음(원가 금액 직접 입력) | | `#f-supply-rate` |
| (저자 인세율) | 이 화면 없음 — 계약 원장 `book-royalties.royalty_rate` | | `#f-royalty-rate` · `#f-royalty-amt` |
| (기본 할인율 · 실판매가) | 이 화면 없음 — 교재 관리(PROD-004) | | `#f-discount-rate`(0~10) · `#f-sale-price` |

### 정가 변경 등록 (BookPriceRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `price` | required · 0~10,000,000 | | 이력 표 '적용 정가'(L874) |
| `effective_from` | required · Y-m-d · 오늘 이후 · 현재 정가 시작일 이후 · 발행일 + `book_reprice_min_months`(기본 12)개월 이후 | | '적용 시작일 (effective_from)' |
| `price_owner` | required | `SELF` 당사 결정 · `CONSIGNOR` 위탁자 결정 | '변경 사유 및 스냅샷 상태' |
| `reason` | CONSIGNOR면 required · max 255 | | 〃 |
| 탭 선택 `book_id` | GET select | | `openBookPriceHistoryModal()` |

### 매입처 등록 (SupplierRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `name` | required · max 100 | 프로토 없음(거래처 관리 VEND-001이 정본 위치 — 7절) |
| `business_no` | required · 숫자 10자리 | 〃 |
| `ceo_name` · `open_date` · `settlement_terms` · `bank_name` · `account_no` · `account_holder` · `contact_email` | nullable | 〃 |

## 4. 목록 필터 · 정렬 · 표 컬럼

| 개발 컬럼(`index.blade.php:112-121`) | 프로토타입 컬럼(L1005) |
|---|---|
| SKU / 관리코드 | 도서 SKU / 가채번 |
| (없음) | 출발 경로 |
| 도서명 | 도서명 / ISBN-13 |
| (없음) | 공급처 / 저자 |
| 공급 형태(위탁은 '위탁 · 2차') | 공급계약 유형 |
| 저작권 귀속 | (상세 표 '자사저작권' L773) |
| 정산 대상 · 정산 경로 | (상세 표 '정산 파이프라인 라우팅') |
| 판매 이력 | (상세 표 '공급형태 변경 잠금') |
| 현재 정가 | 도서 정가 |
| (없음) | 공급률/원가율 · 단위 공급원가 · 저자 인세율 · 3원장 연동 상태 |
| 관리(수정) | 관리 |

정렬 없음, 30건 페이지. 목록 상단 '가채번 대기 건수'(`pendingTempCodeCount`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `books.code` · `title` · `isbn` · `author` · `publisher` | | SKU · 도서 기본(교재 관리가 씀) | 목록 · S1 |
| `books.book_supply_type` | string(20) null | `OWN_PUBLISHED` · `PURCHASED_RESALE` · `CONSIGNMENT` · `BUNDLED` | 목록 · S1 |
| `books.own_copyright_yn` | boolean | 자사 권리 보유(자사 100% 자동 매핑) | 목록 · S1 |
| `books.settlement_required_yn` | boolean | 정산 대상(공급 형태 파생) | 목록 · S1 |
| `books.cost_account_type` | string(30) | `BUYOUT_RIGHT` · `INVENTORY_PURCHASE` | S1 |
| `books.supplier_id` | FK suppliers | 매입처 | S1 |
| `books.cost_price` | integer null | 사입 원가(대외비) | S1 |
| `books.original_price` · `sale_price` | integer | 정가 · 판매가(정가 이력과 동기) | 목록 |
| `books.published_at` | date | 재정가 가능일 계산 기준 | 정가 이력 |
| `book_price_histories` (`price`, `effective_from`, `effective_to`, `price_owner`, `reason`, `admin_id`) | | 정가 이력 | 정가 이력 탭 · 프로토 모달 |
| `suppliers` (`code` SUP-%04d — 주석 정정 a8016168 · 마이그레이션 000274, `name`, `business_no`, `business_status`, `account_no_enc` …) | | 매입처 | 매입처 탭 |
| `book_royalty_contracts` (`temp_code`, `book_title`, `royalty_rate`, `royalty_basis`, `book_id`) | `book_id` bigint unsigned nullable — SKU 연결 전(가채번 단계)은 NULL, 연결 후 books.id(2026_10_16_000215) | 가채번 · 인세(계약 원장 소관) | 프로토 [경로 1] 모달 대응 데이터 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 탭 링크 `?tab=` | 원장 · 정가 이력 · 매입처 · 위탁 | (없음) |
| 검색 form · `select[name=book_supply_type\|settlement\|sales]` · `input[name=keyword]` | 목록 검색 | `#filter-supply-type` · `#filter-keyword` |
| `layerReason` + `data-reason-*` | 엑셀 사유 | '원장 엑셀 다운로드'(L999) |
| `tr[data-href]` | 행 → 수정 | `openEditLedger()` |
| `bookSupplyForm` | S1 폼 | 폼 영역 · `saveLedgerForm()` |
| `settlementRequired` · `settlementRoute` · `bookSupplyToggle()` | 정산 파생 표시 | `applySupplyTypeUi()` · `onSupplyTypeChange()` |
| `reissueButton` · `reissueForm` | 신규 SKU 발급 | `issueNewSkuFromLocked()`(L1221) |
| `priceForm` | 정가 변경 등록 | `modalBookPriceHistory` · `recordPriceHistory()` |
| `supplierForm` | 매입처 등록 | (없음) |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 정가 변경 등록 폼(유효 시작일 · 결정 주체 SELF/CONSIGNOR · 통보 근거) 및 재정가 가능일(발행 + 12개월) 검증 — `BookPriceRequest.php`, `BookSupplyService.php:346-375`
- 매입처 탭 · 매입처 등록 — `_suppliers.blade.php`, `SupplierRequest.php`
- 위탁 도서 탭(위탁자 · 위탁 계약 · 재고 회수 조건) — `_consignment.blade.php`
- 목록 정산 대상 · 판매 이력 필터 — `BookSupplyService.php:111-114`
- 엑셀 반출 사유

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 이 화면에서 정식 SKU `PROD-BK-NNNN` 채번 · 도서명 · ISBN · 저자 · 공급처 입력(L1128-1168) — 8절 Q1
- 3경로 출발(경로 1 가채번 불러오기 `modal-inst-temp`, 경로 3 선등록 SKU 불러오기 `modal-prod-pending`) · 출발 경로 필터 · 원가 확정 상태 필터
- 공급률(%) → 단위 공급원가 자동 계산, 저자 인세율 · 권당 인세, 기본 할인율 → 실판매가, 권당 예상 매출총이익(L1196-1268)
- 적용 기준일 조회(L982), 3원장 연동 상태 컬럼

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `f-supply-type` 자체출판(인세) · 위탁판매 · 사입판매 · 비매품(번들) | `book_supply_type` `OWN_PUBLISHED` · `CONSIGNMENT` · `PURCHASED_RESALE` · `BUNDLED` |
| 비매품(번들) | 라벨 '부속' |
| `f-own-copyright` `true` · `false` | `own_copyright_yn` `1` · `0` |
| `#f-sku` | `book_id`(등록) / `books.code` |
| `#f-supply-cost` 단위 공급원가 | `cost_price` 사입 원가 |
| `book_price_history` (문구) | `book_price_histories` |
| 정가 이력 '적용 종료일 (effective_to)' | `effective_to` (서버가 이전 행을 닫음) |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-BOOK001-1 | 도서 SKU를 어디서 처음 만드는가. 정본은 도서 공급원장(BOOK-001)에서 정식 SKU · ISBN · 공급 유형 · 초기 재고를 등록하고 교재 관리(PROD-004)가 불러온다(경로 2), 3경로 출발 허용. 개발은 SKU를 교재 관리에서만 만들고 BOOK-001은 기존 교재에 공급 정보만 붙인다(신규 SKU 발급도 교재 등록 화면으로 보냄) | 설계서 `:244` · `:298`, 프로토 L1128-1142 · L1866-1900 | `app/Http/Requests/Admin/BookSupplyRequest.php:32`, `app/Http/Controllers/Admin/BookSupplyController.php:123-133`, `resources/views/admin/book-supply/form.blade.php:20-31` **→ 정본대로(D-PROD-03 A, 설계서 L244-246 · PROJECT_STATE 1절 2026-10-23)**: 3경로 출발 허용, 공급 형태를 등록 시 필수로 받고 그 자리에서 `PROD-BK` 채번 — 개발팀 전달 + 프로토 채번 앞자리 수정 |
| Q-BOOK001-2 | 위탁판매(CONSIGNMENT) 등록: 정본은 4대 공급 형태 모두 선택 가능. 개발은 '위탁은 2차(결정 2026-10-19)'로 저장 거부 · 조회만. 이 2차 결정이 정본에 반영된 결정인지 | 설계서 `:251`, 프로토 L1207 | `BookSupplyRequest.php:34-36,48`, `app/Services/Admin/BookSupplyService.php:42-50` **→ 결정(white 10-27, D-PROD-05)**: 위탁 계약이 없어도 1차 개발 — 위탁 판매 1차 구현(개발 '위탁 2차' 결정 철회 전달) |
| Q-BOOK001-3 | 공급원가 입력 방식: 프로토는 공급률/제조원가율(%)을 넣고 단위 원가를 자동 산출. 개발은 원가 금액을 직접 입력(`cost_price`)하고 비율 칸이 없다. 위탁 수수료 · 공급률을 원장 값으로 남길지 | 프로토 L1252-1261 · `recalcSupplyNumbers` L1903, 설계서 `:223`('원가/인세율/위탁수수료') | `BookSupplyRequest.php:40`, `_index/schema.md` books(공급률 칸 없음) **→ 정책 아님(POLICY_D_PROD B)**: 화면 · 이름 문제로 처리 — 금액(`cost_price`)을 저장값으로, 프로토는 공급률 입력 시 금액 자동 계산 · 둘 다 표시 |
