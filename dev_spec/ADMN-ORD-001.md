# ADMN-ORD-001 주문 · 배송 통합 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-ORD-001_baseline.html` (원본 상태: d6723b0 v7.01)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- v7.01 정본 변경: 재고 2단 차감(white 결정 Q-3PL-1, 설계서 v3.2.25): 결제 완료 → 예약(가용 감소), 3PL 송장 업로드 → 실재고 확정 차감. 화면은 실재고 · 예약 · 가용 3칸. 개발은 재고 1칸(books.stock · goods.stock, 결제 시 즉시 차감)이라 예약 · 가용은 개발 미구현 — reserved_stock (규칙), 가용 = stock − reserved_stock 파생. 개발팀 전달 대상
- 포함 화면: ORD-001 주문 목록 · 001-S1 주문 상세(배송지 Lock) · 001-P4 수강권 직권 부여 · ORD-002 배송 관리(탭 4개: 출고 대기 · S1 배송중 · S2 배송완료 · S3 반품 수거 · 검수) · 002-P1 송장 벌크 업로드 · 002-P2 송장 단건 등록/정정 · 002-P3 발주 배치 · 업로드 이력 · 3PL 발주 확인 모달
- 개발 진행: 구현(ORD-001 · 001-S1 · 002 · 002-P1 라우트 · 화면 있음, `_index/progress.md` 48~51행). 001-P4 직권 부여 · 가상계좌 입금 기한 연장 · 3PL 외부 계정(ROLE_PARTNER_3PL)은 미구현 → 규칙 기반 명명
- 근거: 개발 `routes/admin.php:851-889`, `app/Http/Controllers/Admin/OrderController.php` · `DeliveryController.php` · `RefundController.php`(반품 검수), `app/Services/Admin/OrderService.php` · `DeliveryService.php`, `config/delivery.php`

프로토타입 view ↔ 개발 화면
| 프로토타입 view(id) | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| `view-ord001` (`sw-ord001`) | ORD-001 주문 목록 | `resources/views/admin/orders/index.blade.php` |
| `view-ord001s1` (`sw-ord001s1`) | ORD-001-S1 주문 상세 (+ 인쇄) | `orders/show.blade.php` · `orders/print.blade.php` |
| `modalDirectGrant` | ORD-001-P4 수강권 직권 부여 | 없음(개발 미구현) |
| `view-ord002` (`sw-ord002`) · `shipTab-READY/SHIPPING/DELIVERED/RETURN` | ORD-002 배송 관리 탭 4개 | `deliveries/index.blade.php` (`?tab=ready\|shipping\|delivered\|return`) |
| `modal3plConfirm` | 발주 확인(출고지시) | `deliveries/index` `layerDispatch` |
| `modalBulkUpload` | ORD-002-P1 | `deliveries/index` `layerImport` · `layerImportResult` |
| `modalSingleWaybill` | ORD-002-P2 | `deliveries/index` `layerTracking` |
| `modalBatchHistory` | ORD-002-P3 | `deliveries/index` `layerBatches` ← Ajax `deliveries/batches.blade.php` |
| `returnInspectPanel` | ORD-002-S3 검수 입력 | `deliveries/index` `inspectionPanel` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 방법 |
|---|---|---|---|
| `admin.orders.index` | 주문 내역 관리(추정) | view-ord001 · view-ord001s1 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |
| `admin.deliveries.index` | 배송 관리 · 3PL 연동(추정) | view-ord002 + 모달 4종 + 반품 검수 | 〃 |
| (직권 부여) `admin.orders.grants.index`(규칙) 또는 `admin.orders.index` 등록 축 | — | modalDirectGrant | 개발 미구현 |

- 권한 축 5개(조회 · 등록 · 수정 · 삭제 · 다운로드). 화면 버튼은 `@adminCan('<메뉴>', '<축>')`로 노출(예 `orders/show.blade.php:133,192,227`, `deliveries/index.blade.php:91,95,98,104`).
- 반품 검수(`admin.deliveries.returns.update`)는 환불 관리가 아니라 **배송 관리 메뉴** 수정 권한을 따른다(`routes/admin.php:884` 주석, `RefundController.php:188-191`).
- 출고지시 회수는 메뉴 삭제 권한 + 컨트롤러에서 최고관리자 재판정(`OrderController.php:134-138`). 프로토타입도 "상위 권한 예외 기능"(`toggleShipOrderLock` L3537).
- 3PL 발주 엑셀은 상태를 바꾸는 POST지만 개인정보 반출이라 **다운로드** 권한(`routes/admin.php:872` 주석).
- 프로토타입 역할 전환 `btnRoleAdmin` · `btnRole3pl`(`ROLE_PARTNER_3PL`, L539-540)은 개발에 대응 역할 없음 → 8절 Q-ORD-4.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{order}` = `orders.id`, `{delivery}` = `deliveries.id`, `{batch}` = `delivery_batches.id`, `{refund}` = `refunds.id`.

### ORD-001 주문 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색(쿼리 없으면 최근 1개월로 리다이렉트) | GET | `/orders` | `admin.orders.index` | 조회 | OrderController@index |
| 조회용 엑셀(라인 단위) — 사유 레이어 `layerReason` | GET | `/orders/download` | `admin.orders.download` | 다운로드 | OrderController@download |
| KPI 카드: 배송준비중 · 입금대기 · 환불/반품 요청 | GET | `/orders?statuses[]=ready` · `statuses[]=waiting` · `refund_requested=1` | `admin.orders.index` | 조회 | (index의 readyUrl · waitingUrl · refundUrl) |
| 배송 관리로 이동 | → | `/deliveries?tab=ready` | `admin.deliveries.index` | 조회 | |
| 행 [상세] (새 탭) · [환불건] | → | `/orders/{order}` · `/refunds/{refund}` | `admin.orders.show` · `admin.refunds.show` | 조회 | |

### ORD-001-S1 주문 상세
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세(열람 로그 `order_detail`) | GET | `/orders/{order}` | `admin.orders.show` | 조회 | OrderController@show |
| 거래명세서 · 주문서 인쇄 | GET | `/orders/{order}/print` | `admin.orders.print.show` | 조회 | OrderController@showPrint |
| 배송지 수기 보정(사유 필수 · 알림톡 `TPL_DELIVERY_ADDRESS_CHANGED`) | PUT | `/orders/{order}/address` | `admin.orders.address.update` | 수정 | OrderController@updateAddress |
| 출고지시 회수(잠금 해제) | DELETE | `/orders/{order}/dispatch` | `admin.orders.dispatch.destroy` | 삭제 + 최고관리자 | OrderController@destroyDispatch — v6.92 프로토에서 버튼 삭제(S-13), 아래 출고보류 · 맞교환으로 대체 |
| 3PL 출고보류 요청(사유 · 메모, 상태 requested) | POST | `/orders/{order}/ship-holds` (규칙) | `admin.orders.ship-holds.store` (규칙) | 수정 | 개발 미구현(S-13) — `sendShipHoldRequest()` |
| 3PL 회신 입력(보류 완료 → 잠금 해제 / 이미 출고 → 잠금 유지) | PUT | `/orders/{order}/ship-holds/{hold}` (규칙) | `admin.orders.ship-holds.update` (규칙) | 수정(3PL 계정 또는 물류팀 대리) | 개발 미구현(S-13) — `recordShipHoldReply('HELD'\|'SHIPPED')` |
| 맞교환 재출고 등록(다음 발주 배치에 재출고 라인) | POST | `/orders/{order}/reships` (규칙) | `admin.orders.reships.store` (규칙) | 등록 | 개발 미구현(S-13) — `saveSwapReship()` |
| 관리자 메모 추가 | POST | `/orders/{order}/memos` | `admin.orders.memos.store` | 등록 | OrderController@storeMemo |
| ~~가상계좌 입금 기한 연장~~ | | | | | v6.92 삭제(D-ORD-01, 개발과 같음) |
| 가상계좌 입금 계좌 · 기한 재안내(알림톡 `TPL_VBANK_ISSUED`, 기한 그대로) | POST | `/orders/{order}/deposit-notice` (규칙) | `admin.orders.deposit-notice.store` (규칙) | 수정 | 개발 미구현(D-ORD-01) — `resendVbankNotice()` |
| 도서산간 추가 배송비 결제 · 입금 확인(확인 전 3PL 발주 제외) | PUT | `/orders/{order}/island-fee` (규칙) | `admin.orders.island-fee.update` (규칙) | 수정 | 개발 미구현(D-ORD-10) — `confirmIslandFeePaid()` |
| 회원 상세 | → | `/members/{member}` | `admin.members.show` | 조회(회원 메뉴) | |
| 배송 관리에서 보기 | → | `/deliveries?tab=…&search_type=order_no&keyword=<주문번호>` | `admin.deliveries.index` | 조회 | |
| 반품 배너 [환불 건 보기] | → | `/refunds/{refund}` | `admin.refunds.show` | 조회(환불 메뉴) | |

### ORD-001-P4 수강권 직권 부여 (0원 주문)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 부여 폼 | GET | `/orders/grants/create` (규칙) | `admin.orders.grants.create` (규칙) | 등록 | 개발 미구현 |
| 부여 실행(0원 주문 생성) | POST | `/orders/grants` (규칙) | `admin.orders.grants.store` (규칙) | 등록 | 개발 미구현 |

### ORD-002 배송 관리 (탭 · 툴바)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 탭 목록(`tab=ready\|shipping\|delivered\|return`) | GET | `/deliveries` | `admin.deliveries.index` | 조회 | DeliveryController@index |
| 3PL 발주 엑셀 = 출고지시(배송지 Lock · 배치 채번) | POST | `/deliveries/dispatch` | `admin.deliveries.dispatch.download` | **다운로드** | DeliveryController@storeDispatch |
| 배송완료일 보정(배송완료 탭) | PUT | `/deliveries/delivered` | `admin.deliveries.delivered.update` | 수정 | DeliveryController@updateDelivered |
| S3 반품 검수 저장(검수 · 귀책 · 사진) | PUT | `/deliveries/returns/{refund}` | `admin.deliveries.returns.update` | 수정 | RefundController@updateReturnInspection |
| S3 검수 사진 열람 | GET | `/deliveries/returns/{refund}/photos/{photo}` | `admin.deliveries.returns.show` | 조회 | RefundController@showReturnPhoto |
| 주문 상세 열기 | → | `/orders/{order}` | `admin.orders.show` | 조회(주문 메뉴) | |

### ORD-002-P1 송장 벌크 업로드
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| STEP 1 파일 사전 읽기(JSON, 저장 안 함) | POST | `/deliveries/tracking/preview` | `admin.deliveries.tracking.preview.store` | 등록 | DeliveryController@previewTracking |
| STEP 2 업로드 · 검증 실행(1,000행 초과는 큐) | POST | `/deliveries/tracking` | `admin.deliveries.tracking.store` | 등록 | DeliveryController@storeTracking |
| 표준 양식 받기 | GET | `/deliveries/tracking/template/download` | `admin.deliveries.template.download` | 다운로드 | DeliveryController@downloadTemplate |
| 실패 목록 엑셀(3PL 회신용) | GET | `/deliveries/tracking/{batch}/failures/download` | `admin.deliveries.failures.download` | 다운로드 | DeliveryController@downloadFailures |
| 알림톡 발송 실패 재시도 | PUT | `/deliveries/batches/{batch}/notifications` | `admin.deliveries.batches.notifications.update` | 수정 | DeliveryController@updateNotifications |

### ORD-002-P2 송장 단건 등록 · 정정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록(신규) / 정정(운송장 있는 라인) — 처리 구분은 라인 상태로 자동 | PUT | `/deliveries/{delivery}/tracking` | `admin.deliveries.tracking.update` | 수정 | DeliveryController@updateTracking |

### ORD-002-P3 발주 배치 · 업로드 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 이력 조각(Ajax 전용, 직접 열면 배송 관리로) | GET | `/deliveries/batches?date_from=&date_to=&type=` | `admin.deliveries.batches.index` | 조회 | DeliveryController@batches |
| 보관 파일 재다운로드(출고지시 새로 안 걺) | GET | `/deliveries/batches/{batch}/download` | `admin.deliveries.batches.download` | 다운로드 | DeliveryController@downloadBatch |

## 3. 폼 필드 · 검증

### 001 목록 검색 (GET 쿼리, OrderService::normalizeFilters `OrderService.php:126`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `date_basis` | 허용값 외 → `paid_at` | `paid_at` 결제일시 · `created_at` 주문일시 · `shipped_at` 출고일시 · `refund_completed_at` 환불완료일시 | `#fDateType` |
| `date_from` · `date_to` (id `dateFrom` · `dateTo`) | Y-m-d. 한쪽 비고 검색어 없으면 1개월로 채움(PERIOD_ALL_NOTICE) | 기간 칩 `today` · `7d` · `1m` · `3m` · `all` | 날짜 2칸(L661 · L663, id 없음) · `selectQuickDate()` 오늘/7일/1개월/3개월/전체 |
| `method` | METHOD_FILTERS | `card` 카드 · `easy_pay` 간편결제 · `virtual_account` 가상계좌 · `transfer` 계좌이체 · `mobile_phone` 휴대폰 · `gift` 상품권(문화 · 도서 · 게임 3종 묶음) | `#fPayMethod` |
| `statuses[]` | FILTER_STATUSES 교집합. `[전체]`와 배타 | `waiting` 결제대기 · `paid` 결제완료 · `ready` 배송준비중 · `shipping` 배송중 · `delivered` 배송완료 · `returning` 반품진행중 · `refunded` 환불완료 · `rejected` 기각 | `#statusChipGroup` `data-status` 결제대기 · … · **반품수거중** · 환불완료 · 기각 |
| `refund_requested` | 1 | KPI '환불/반품 요청' | `#kpi-ord-return` |
| `kind` | KINDS | `lecture` 인강 단독 · `book` 교재 단독 · `mixed` 복합(패키지) | `#typeChipGroup` 인강 · 교재 · 복합 · **일반상품**(개발 없음) |
| `amount_min` · `amount_max` | 숫자, 0 이상 | | 최소 · 최대 금액 input(L718 · L720, id 없음) |
| `physical_only` | 1 | | `#chkHasDelivery` |
| `search_type` | SEARCH_TYPES, 기본 `order_no` | `order_no` 주문번호 · `buyer` 구매자명 · `receiver` 수령인명 · `phone` 휴대전화 번호(검색 시 열람 로그) | `#fSearchKey` ORDER_NO · BUYER · RECEIVER · PHONE |
| `keyword` | 주문번호 외 2자 이상(KEYWORD_MIN) | | `#fSearchVal` |
| `sort` · `direction` | `paid_at` · `final_amount` / `asc` · `desc` | | 표 머리(결제일시 · 실결제금액) |
| `per_page` | `50` · `100` · `200` | | 50/100/200개씩 select(L756, id 없음) |

### 001 조회용 엑셀 (OrderDownloadRequest extends ReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `reason` · `reason_etc` · `reason_ref` | ReasonRequest(정형 사유 + 기타 + 근거 번호). 공용 레이어 `layerReason` | | 프로토는 사유 없음 — `downloadOrderLookupExcel()`(L3050) 로그만 → Q-ORD-2 |
| (검색 조건) | 현재 목록 쿼리 그대로 | | |

### 001-S1 배송지 수기 보정 (OrderAddressRequest extends MemberReasonRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `receiver_name` | required · 2~30자 | | `#inpRecvName` |
| `receiver_phone` | 숫자만 남겨 `^\d{10,11}$` | | `#inpRecvPhone` |
| `receiver_zipcode` | `^\d{5}$` (우편번호 찾기 결과만) | | `#inpZipcode` · `#btnFindZip` |
| `receiver_address` | required · max 200 · 사서함 · 군사우편 차단(`Delivery::UNSHIPPABLE_ADDRESS_PATTERN`) | | `#inpAddr1` |
| `receiver_address_detail` | nullable · max 200 · 같은 차단 | | `#inpAddr2` |
| `delivery_memo` | nullable · max 100 | | `#inpShipMsg` |
| `reason` | MemberReasonRequest(공백 제외 10자 · 서로 다른 글자 3개 · 200자) | | `#inpAddrChangeReason`(프로토는 2자 이상) |
| (도서산간 판정 배지) | 개발 폼 없음(`deliveries.fee_type` ISLAND은 주문 시 판정) | `FREE` 무료 · `PREPAID` 선불 · `ISLAND` 도서산간 | `#islandCheckBadge` |
| `island_fee_liability` (규칙, D-ORD-10) | 도서산간으로 바뀌어 추가 배송비가 생길 때 required | `customer` 고객 귀책 · `admin` 관리자 귀책 | radio `islandFault` CUSTOMER · ADMIN |
| `island_fee_method` (규칙) | liability=customer일 때 required | `pg_link` PG 추가 결제(결제 링크 · 개인 결제창) · `bank_transfer` 무통장 입금 안내 · `reorder` 취소 후 재주문 안내(주소 미적용) | radio `islandMethod` PG_LINK · BANK · REORDER |
| `island_fee_cost_account` (규칙) | liability=admin일 때 required(미청구 · 운영 비용) | `sga` 판관비 · `misc_loss` 잡손실 | `#inpIslandCostAcct` SGA · MISC_LOSS |

### 001-S1 출고지시 회수 (MemberReasonRequest) — v6.92 프로토 버튼 삭제(S-13)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` | MemberReasonRequest | 없음(예전 `#btnToggleShipLock` · `#btnRecallShipOrder`) |

### 001-S1 3PL 출고보류 요청 · 회신 · 맞교환 재출고 — 개발 미구현, 규칙 기반 명명(S-13)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `reason_code` (출고보류) | required | `address` 배송지 오기재 · 변경 · `cancel` 주문 취소 · `item` 품목 오류 · `etc` 기타 | `#inpShipHoldReason` ADDR · CANCEL · ITEM · ETC |
| `memo` | etc일 때 required | | `#inpShipHoldMemo` |
| `result` (3PL 회신) | required | `held` 보류 완료(잠금 해제) · `already_shipped` 이미 출고(잠금 유지) | `#btnHoldReplyHeld` · `#btnHoldReplyShipped` |
| `reason_code` (맞교환) | required | `address` · `wrong_item` · `defective` · `etc` | `#inpSwapReason` ADDR · WRONG_ITEM · DEFECTIVE · ETC |
| `order_item_id` | required · 주문 실물 라인(교재 · 일반상품) | | `#inpSwapItem` |
| `return_tracking_no` | required · 숫자 10~14자리 | | `#inpSwapReturnWb` |
| (조건) | 보류 요청 = 출고지시 잠금 + 미출고, 맞교환 = '이미 출고' 회신 또는 배송중 · 배송완료 | | `applyShipLockUiState()` |

### 001-S1 관리자 메모 (OrderMemoRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `content` | required · max 500(`OrderService::MEMO_MAX`). 추가만, 내부 전용 | `#inpAdminMemo` · `addAdminTimelineMemo()` |

### 001-S1 가상계좌 입금 기한 연장 — v6.92 삭제(D-ORD-01)
- 프로토의 `#inpNewVbankDue` · `#inpVbankReason` · `extendVbankDueDate()` 삭제. 기한은 `payments.raw_response.virtualAccount.dueDate`(토스 발급 응답) 그대로, 기본 유효 시간 `site_settings.virtual_account_valid_hours` = 72. 재안내 `#btnVbankResend` · `resendVbankNotice()`는 입력 필드 없음.

### 001-P4 수강권 직권 부여 — 개발 미구현, 규칙 기반 명명
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `member_id` (규칙) | required · users.id | `#grantUserId` (+ `#grantUserName` · `#grantUserEmail` 표시) |
| `product_type` · `product_id` (규칙, order_items 기준) | required | `#grantProdCode` |
| `course_days` (규칙) | required | `#grantPeriodDays` 30 · 90 · 180 · 365 |
| `reason` (규칙) | MemberReasonRequest(프로토 10자 이상) | `#grantReason` |

### 002 탭 목록 검색 (GET, DeliveryService::normalizeFilters `DeliveryService.php:130`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `tab` | TABS, 기본 `ready` | `ready` 출고 대기(배송준비중) · `shipping` 배송중 · `delivered` 배송완료 · `return` 반품 수거 · 검수 | `switchShipTab('READY'\|'SHIPPING'\|'DELIVERED'\|'RETURN')` · `#shipTab-*` |
| `date_from` · `date_to` | Y-m-d | | 결제 기간 날짜 2칸(L837 · L839) |
| `book_id` | 숫자(books.id) | | `#fShipSku` |
| (배송 권역) | 개발 없음 | | 권역 select(L857) 수도권 · 지방권 · 제주 · 도서산간 |
| (도서산간만) | 개발 없음 | | `#chkIslandOnly` |
| `search_type` | 기본 `order_no` | `order_no` 주문번호 · `receiver` 수령인명 · `phone` 휴대전화 · `tracking` 운송장번호 | 검색 구분 select(L871, id 없음) |
| `keyword` | | | `#fShipKeyword` |
| `sort` · `direction` | 탭별 TAB_SORTS · 기본 DEFAULT_SORTS | `paid_at` 결제일 · `shipped_at` 출고일 · `status` 상태 · `delivered_at` 배송완료일 · `received_at` 입고일 | 프로토 없음 |
| `per_page` | 50 · 100 · 200 | | |

### 002 발주(출고지시) (Request 클래스 없음 — 컨트롤러가 숫자만 거름)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | numeric(deliveries.id). 서비스가 출고지시 · 예약판매 · 환불 심사 중 · 취소 건을 빼고 건수 안내 | 행 체크 · `#btnSelectAllShipQuery` → `#btn3plDownload` → `modal3plConfirm` → `execute3plExcelDownload()` |

### 002 배송완료일 보정 (DeliveryDeliveredRequest extends MemberReasonRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | required · integer | 프로토 없음(개발에만) |
| `delivered_at` | Y-m-d · 오늘 이전 | 〃 |
| `reason` | MemberReasonRequest | 〃 |

### 002-S3 반품 검수 (ReturnInspectionRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `inspection_result` | required | `normal` 정상(재판매 가능) · `defective` 파본 · 불량(규칙, D-ORD-09 — 회사 귀책 고정 · 재고 미입고 · 교재비 차감 없음) · `damaged` 고객 훼손(재판매 불가) | `#inpInspectResult` NORMAL · DEFECTIVE · DAMAGED |
| `liability` | normal일 때 required | `customer` 고객 귀책 · `company` 회사 귀책 | `#inpInspectFault` CUSTOMER_ONEWAY(편도) · CUSTOMER(왕복) · COMPANY → Q-RFD-7(ADMN-RFD-002.md) |
| `inspection_memo` | nullable · max 2000 | | `#inpInspectMemo` |
| `photos[]` | jpg · png · 10MB · 최대 `RefundService::INSPECTION_PHOTO_MAX`. 필수 = 훼손 또는 고객 귀책(이미 올린 사진 있으면 면제) → D-ORD-02로 고객 훼손(`damaged`)만 필수 | | `#btnInspectPhoto` · `attachInspectPhoto()` · `#inspectPhotoLabel` · `#inspectPhotoReq` → Q-ORD-3 |
| `row_id` · `inspection_row` | 화면 내부(선택 행) | | `selectReturnRow()` |
| (입고 확인) | 이 화면에서 받지 않음 — 입고 전 건은 선택 불가, 환불 관리 `refunds.receipt.update`에서 | | 프로토도 입고 입력 없음 |

### 002-P1 송장 벌크 업로드 (DeliveryTrackingImportRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `file` | required · xlsx · 10MB(`delivery.import_max_kb`) · 최대 5,000행 | 시트 `송장`, 필수 헤더 주문번호 · 주문라인번호 · 택배사코드 · 운송장번호 · 출고일자(+ 출고수량 · 비고) | 업로드 파일(L1376) · `#btnP1Step1` |
| `batch_id` | nullable · 발주(export) 배치 | | 발주 배치 지정 select(L1385) `BATCH-…` · 전체 배치 허용 |
| `notify` | boolean | 배송출고 알림톡 | '배송출고 알림톡 자동 발송' 체크(L1396) |
| `overwrite` | boolean | 기존 운송장 덮어쓰기 | '기존 운송장 덮어쓰기' 체크(L1398) |
| (부분 커밋) | 개발은 항상 정상 행만 반영 · 실패는 실패 목록 | 오류 코드 `E01` 주문번호 불일치 · `E02` 이미 처리됨 · `E03` 필수값 누락 · `E04` 형식 오류 · `E05` 상태 불일치 · `E06` 운송장 중복 · `E99` 일시 오류 | '오류 행은 건너뛰고 정상 행만 부분 커밋' 체크(L1397) · 실패 표(L1458) |

### 002-P2 송장 단건 등록 · 정정 (DeliveryTrackingRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `courier` | `config('delivery.couriers')` 키 | `CJ` CJ대한통운 · `HANJIN` 한진택배 · `LOTTE` 롯데택배 · `EPOST` 우체국택배 | `#p2Courier` |
| `tracking_no` | `^\d{10,14}$` | | `#p2WaybillNo` |
| `shipped_at` | Y-m-d · 오늘 이전 | | `#p2ShipDate` |
| `reason_code` | required | `missing` 3PL 회신 누락 · `typo` 운송장 오타 정정 · `courier` 택배사 변경 · `etc` 기타 | `#p2ReasonType` |
| `reason_memo` | etc일 때 required · max 200 | | `#p2ReasonMemo` |
| `notify` | boolean(신규 등록만 발송, 정정은 미발송) | | `#p2SendAlimtalk` |

### 002-P3 이력 조회 (DeliveryBatchRequest — 틀린 값은 기본값)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `date_from` · `date_to` | 기본 오늘 포함 최근 30일 | | 프로토 없음(기간 고정 표) |
| `type` | | `all` 전체 · `export` 발주 다운로드 · `import` 송장 업로드 | 표 '구분' 열 |

## 4. 목록 필터 · 정렬 · 표 컬럼

### ORD-001 주문 목록 (`orders/index.blade.php:152-162`)
| 개발 컬럼 | 정렬 키 | 프로토타입 컬럼(L768) |
|---|---|---|
| 주문번호 (+ 면세 근거) | | 주문번호 / 과세근거 |
| 결제일시 | `paid_at` | 결제(주문)일시 |
| 구매자 (/ 수령인) | | 구매자 / 수령인 |
| 구분 `KIND_SHORT` 인강 · 교재 · 복합 | | 구분 |
| 주문 라인(강좌 · 교재 · 배송비) | | 주문 라인 아이템 |
| 실결제금액 | `final_amount` | 실결제금액 |
| 결제수단 | | 결제수단 (토스) |
| 주문상태(대표값 우선순위: 반품 > 배송준비중 > 배송중 > 기각 > 배송완료) + 🔒 출고지시 완료 | | 대표 주문상태 |
| 관리: [상세] · [환불건] | | 관리 |

요약 카드(`orders/index.blade.php:20`): 조회 주문 · 실결제 합계 · 배송준비중 · 입금대기(가상계좌) · 환불/반품 요청 ↔ 프로토 `#kpi-ord-all` · `#kpi-ord-ready` · `#kpi-ord-vbank` · `#kpi-ord-ship`(배송중 — 개발 카드 없음) · `#kpi-ord-return`.

### ORD-002 배송 관리
- 툴바: 선택 건수 `selectedCount`, 조회 결과 전체 선택 `selectAllResults`(서버가 `readyIds` 전달) ↔ `#shipSelectedCnt` · `#btnSelectAllShipQuery`.
- 발주 엑셀 컬럼(`DeliveryService::DISPATCH_HEADERS`): 주문번호 · 주문라인번호 · 수령인명 · 수령인연락처 · 우편번호 · 기본주소 · 상세주소 · 상품코드 · 상품명 · 수량 · 배송메시지 · 배송비구분 · 주문일시 · 발주배치번호 · 비고.
- 빈 목록 문구는 탭별 `EMPTY_MESSAGES`. 반품 탭 상단 '검수 대기 n건'(`awaitingInspectionCount`).
- 배송완료 자동 처리: 출고 D+3(`delivery.auto_complete_days`, 배치 `deliveries:auto-complete`). 배송중 → 배송완료 관리자 수동 전환 경로는 없음.

## 5. DB 테이블 · 컬럼 (화면에 쓰는 것만, 전체는 `_index/schema.md`)
| 테이블.컬럼 | 뜻 | 화면 |
|---|---|---|
| `orders.order_no` · `user_id` · `status`(pending · paid · cancelled · refunded) · `payment_method` · `final_amount` · `paid_at` | 주문. 화면 상태는 `OrderService::displayStatus`로 파생(가상계좌 미입금 = 결제대기, 기한 만료 취소 = 기각) | 001 · S1 |
| `orders.receiver_name` · `receiver_phone` · `receiver_zipcode` · `receiver_address` · `receiver_address_detail` · `delivery_memo` | 수령인 · 배송지(보정 대상) | S1 |
| `orders.exemption_basis` | `EDU_SERVICE` 교육용역 · `BOOK_GOODS` 도서 재화 · `MIXED` 복합 | 001 과세근거 · S1 `#detailExemptionBadge` |
| `orders.course_amount` · `book_amount` · `delivery_fee` · `earned_point` · `has_physical_item` | 강좌 · 교재 합계 · 배송비 · 적립 예정 · 실물 포함 | S1 결제 정보 |
| `order_items.line_no`(int unsigned NOT NULL, 주문 안 1부터 · 송장 업로드 매칭 키) · `product_id`(bigint unsigned nullable — 배송비 라인 SHIPPING_FEE는 NULL) · `item_type`(LECTURE · BOOK · SHIPPING_FEE) · `product_name` · `original_price` · `quantity` · `coupon_discount` · `point_discount` · `final_price` · `tax_treatment` · `refund_status` | 주문 라인 | S1 `#detailLinesTbody` |
| `payments.payment_key` · `approval_no` · `card_name` · `card_number` · `raw_response`(json, 가상계좌 계좌 · 입금기한은 `virtualAccount.dueDate`에서 읽음, `OrderService::depositInfo`) | PG 거래 · 가상계좌 입금 안내. `virtual_account_*` · `vbank_*` 컬럼은 삭제됨(2026_09_08_000076_drop_payment_legacy_columns) | S1 `#dtPgTid` · `#vbankDueText` |
| `site_settings.virtual_account_valid_hours` | 가상계좌 입금 기한(발급 후 시간, 1~2160, 지나면 자동 취소, 이미 발급된 계좌에는 미적용) | S1 '발급 후 N시간' 표기 |
| `order_cs_logs` (`order_id`, `admin_id`, `cs_type`='memo', `content`) | 관리자 메모(추가만) | S1 처리 이력 `#detailTimelineTbody` |
| `order_status_logs` | 상태 변경 이력 | S1 처리 이력 |
| `deliveries` (`order_item_id`, `status` READY · SHIPPING · DELIVERED · RETURNING · REFUNDED · REJECTED, `courier`, `tracking_no`, `ship_ordered_at`(= 배송지 Lock), `batch_id`, `shipped_at`, `delivered_at`, `zipcode`, `fee_type`, `notification_sent_at`) | 배송 라인(1행 = 교재 라인 1건) | 002 표 · S1 배송 블록 |
| `delivery_logs` (`delivery_id`, `status`, `description`, `logged_at`) | 배송 이력(정정 · 알림 실패 표식) | 002 '정정 n' 배지 · S1 |
| `delivery_batches` (`batch_no`, `type` export · import, `file_name`, `file_path`, `total_count`, `success_count`, `fail_count`, `status`, `admin_id`) | 발주 · 송장 배치 | P3 |
| `delivery_batch_items` (`row_no`, `order_no`, `line_no`, `carrier`, `tracking_no`, `shipped_at`, `result`, `error_code`, `error_message`) | 송장 업로드 행 결과 | P1 실패 표 |
| `refunds.warehouse_received_at` · `inspection_result` · `liability` · `inspection_memo` · `return_tracking_no` | 반품 입고 · 검수 | S3 |
| `attachments` (type `inspection_photo`, disk `secure`) | 검수 사진 | S3 |
| `excel_download_logs` (`admin_id` bigint unsigned nullable) | 발주 엑셀 · 조회 엑셀 반출 원장 | 001 엑셀 · 002 발주 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `dateFrom` · `dateTo` · `[data-period-from]` | 001 기간 · 기간 칩 | 날짜 input · `selectQuickDate()` |
| `[data-status-all]` · `[data-status-item]` | 001 상태 체크(전체와 배타) | `#statusChipGroup` `.filter-chip` |
| `layerReason` (`data-reason-action` · `data-reason-params`) | 001 엑셀 사유 공용 레이어 | 없음 |
| `layerAddress` · `addressForm` | S1 배송지 수정 레이어 | `#btnEnableAddrEdit` · `.addr-field` · `#addrCompareConfirmBox`(인라인 편집) |
| `layerRevoke` | S1 출고지시 회수 | `#btnToggleShipLock` · `#btnRecallShipOrder` · `#detailLockBanner` |
| `[data-copy]` | 주문번호 복사 | 복사 버튼(L1038) |
| `deliveryContent` | 002 본문 | `view-ord002` |
| `selectedCount` · `selectAllResults` · `checkPage` | 002 선택 · 전체 선택 | `#shipSelectedCnt` · `#btnSelectAllShipQuery` · `toggleShipCheckAll()` |
| `dispatchButton` · `dispatchForm` · `layerDispatch` · `dispatchCount` · `dispatchConfirm` · `dispatchDone` | 발주 = 출고지시 | `#btn3plDownload` · `modal3plConfirm` |
| `layerImport` · `importForm` · `importFile` · `importPreview` · `importTemplateHint` · `layerImportResult` · `importNotified` · `importNotifyFailed` | P1 | `#btnBulkWaybill` · `modalBulkUpload` · `#btnP1Step1` · `#btnP1Step2` · `#p1Step1Box` · `#p1Step2Box` · `#p1AlimtalkCnt` · `#p1RetryBanner` · `#btnP1Action` |
| `trackingButton` · `layerTracking` · `trackingForm` | P2 | `#btnSingleWaybill` · `modalSingleWaybill` · `#p2*` |
| `batchesButton` · `layerBatches` · `batchHistoryBody` | P3 | `#btnBatchHistory` · `modalBatchHistory` |
| `deliveredButton` · `layerDelivered` · `deliveredForm` · `deliveredIds` | 배송완료일 보정 | 없음(개발에만) |
| `inspectionPanel` · `inspectionTarget` · `inspectionEmpty` · `inspectionReadonly` · `inspectionForm` · `inspectionFields` · `inspectionPhotoButton` · `inspectionPhotos` · `inspectionPicked` · `inspectionPhotoCount` · `inspectionClear` | S3 검수 입력 | `#returnInspectPanel` · `#inspectPanelTitle` · `#inpInspectResult` · `#inpInspectFault` · `#inpInspectMemo` · `#inspectPhotoLabel` · `clearReturnSelection()` |

마크업 공통: 레이어 `.layer-pop__overlay.layer-pop--hidden` + `id="layer…"`, 열기 `.layer__open` + `data-target`, 닫기 `.layer-pop--close`, 버튼 `.btn__small` + `.btn--basic` · `.btn--save` · `.btn--del`, 표 `.table__list`, 도움말 `.fm__help` · `.fm__help--warn`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 002 배송완료일 보정(`deliveries.delivered.update`, 사유 필수) — `DeliveryController.php:253-275`
- 002 탭별 정렬 선택(`TAB_SORTS` · `DEFAULT_SORTS`) — `DeliveryService.php:83-91`
- P1 표준 양식 다운로드 · STEP 1 사전 읽기 JSON · 1,000행 초과 큐 처리 · 실패 목록 엑셀 — `DeliveryController.php:131-205`, `config/delivery.php`
- P3 기간 · 구분 필터, 보관 파일 재다운로드 — `DeliveryBatchRequest.php`, `DeliveryController.php:114-129`
- 001 엑셀 반출 사유 입력(공용 `layerReason`) — `OrderDownloadRequest.php`(Q-ORD-2)
- 001 휴대전화 검색 열람 로그(번호 마스킹) — `OrderController.php:55-58`
- S1 주소 차단 규칙(사서함 · 군사우편) — `Delivery.php:24-26`
- 발주 시 예약판매 · 환불 심사 중 · 취소 건 자동 제외 안내 — `DeliveryController.php:90-95`

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 001-P4 수강권 직권 부여(0원 주문, 구 ORD-003) — 프로토 `modalDirectGrant` L1696, `submitDirectGrant()` L1831. 개발 검색 결과 없음
- S1 가상계좌 입금 기한 연장 — 프로토 `#vbankExtendBox` L1067-1077, `extendVbankDueDate()` L3596. 개발 `OrderService.php:490` 의도적 미구현. 기한을 담을 `payments` 컬럼도 없다(`virtual_account_due_at` 삭제, 기한은 PG 발급 응답 원문에만) → Q-ORD-1 (10-27 스키마 재색인 반영) **→ 결정(v6.92 white, D-ORD-01)**: 연장 없음(개발과 같음) · 기본 기한 72시간, 프로토는 연장 박스 삭제 · 재안내 알림톡(`resendVbankNotice()`, 개발 미구현)으로 바꿈
- 3PL 외부 계정 격리 모드(ROLE_PARTNER_3PL, 금액 · 결제수단 차단, 연락처 마스킹) — 프로토 L539-540 · L794-803 · `setSessionRole()` L1788. 개발 역할 없음 → Q-ORD-4 (v6.92: 3PL 보기 마스킹 위치를 PTNR-002와 같게 — 이름 가운데 글자 · 연락처 끝 4자리, 출고 대기 외 탭 · 검수 패널까지. `pName()` · `pPhone()`)
- 001 주문 구분 '일반상품(과세 10%)' — 프로토 L712. 개발 `OrderService::KINDS`(`OrderService.php:96`)는 인강 · 교재 · 복합 3종, `order_items.item_type`도 LECTURE · BOOK · SHIPPING_FEE만
- 002 배송 권역 필터 · 도서산간만 체크 — 프로토 L857 · `#chkIslandOnly` L864. 개발 `normalizeFilters`에 없음(`DeliveryService.php:130-150`)
- KPI '배송중' 카드 — 프로토 `#kpi-ord-ship` L626. 개발 요약은 4개 + 건수
- S1 주소 변경 시 도서산간 추가배송비 고객 청구 판정 배지 — 프로토 `simulateZipSearch()` L3565. 개발 배송지 보정은 금액 재판정 없음(확인 필요) **→ 결정(v6.92 white, D-ORD-10)**: 고객 귀책은 PG 추가 결제 · 무통장 입금 · 재주문 안내 중 택1(결제 · 입금 확인 전 3PL 발주 제외), 관리자 귀책은 미청구 · 판관비/잡손실 — 프로토 `#islandFeeBox` · `confirmIslandFeePaid()`, 개발 미구현
- S1 3PL 출고보류 요청 · 3PL 회신 · 맞교환 재출고 등록(v6.92 신설, S-13) — 프로토 `#shipHoldPanel` · `sendShipHoldRequest()` · `recordShipHoldReply()` · `saveSwapReship()`. 개발은 출고지시 회수(`orders.dispatch.destroy`)만 있음 **→ 결정(v6.92 white, S-13)**: 회수(잠금만 해제) 버튼 없음, 보류 완료 회신 때만 잠금 해제 · 이미 출고면 맞교환
- 002-S3 검수 결과 '파본 · 불량'(v6.92 신설) **→ 결정(v6.92 white, D-ORD-09)**: 정상 · 파본/불량(회사 귀책 · 재고 미입고) · 고객 훼손 3값, 개발 `inspection_result`에 `defective` 추가 필요

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 상태 칩 `data-status` 한글(결제대기 … 기각) | `statuses[]` `waiting` · `paid` · `ready` · `shipping` · `delivered` · `returning` · `refunded` · `rejected` |
| 반품수거중 | 반품진행중(`returning`, `Delivery::STATUS_LABELS`) |
| `data-type` 인강 · 교재 · 복합 · 일반상품 | `kind` `lecture` · `book` · `mixed` |
| `#fDateType` 한글 옵션 | `date_basis` `paid_at` · `created_at` · `shipped_at` · `refund_completed_at` |
| `#fSearchKey` ORDER_NO · BUYER · RECEIVER · PHONE | `search_type` `order_no` · `buyer` · `receiver` · `phone` |
| 배송 검색 주문번호 · 수령인명 · 휴대전화 · 운송장번호 | `search_type` `order_no` · `receiver` · `phone` · `tracking` |
| `shipTab-READY` · `SHIPPING` · `DELIVERED` · `RETURN` | `tab` `ready` · `shipping` · `delivered` · `return` |
| `#inpInspectResult` NORMAL · DEFECTIVE · DAMAGED | `inspection_result` `normal` · `defective`(규칙, D-ORD-09) · `damaged` |
| `#inpInspectFault` CUSTOMER_ONEWAY · CUSTOMER · COMPANY | `liability` `customer` · `company`(편도 구분 없음 — Q-RFD-7) |
| `#p2Courier` 한글 택배사명 | `courier` `CJ` · `HANJIN` · `LOTTE` · `EPOST` |
| `#p2ReasonType` 한글 | `reason_code` `missing` · `typo` · `courier` · `etc` |
| 배치 번호 `BATCH-YYYYMMDD-NN` | `delivery_batches.batch_no`(형식은 서비스 채번, 확인 필요) |
| 주문 상세 배송지 인라인 편집 | 레이어 `layerAddress` + PUT `orders.address.update` |
| 처리 이력 구분(배송지보정 · 출고지시회수 · 기한연장 · 관리자메모) | `OrderService::ACTION_LABELS` `address_update` 배송지 수정 · `dispatch_revoke` 출고지시 회수 · `tracking_register` 송장 단건 등록 · `tracking_correct` 운송장 정정 · `delivered` 배송완료 처리 + 메모 |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)

| 번호 | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-ORD-1 | 가상계좌 입금 기한 연장을 제공하는가? 정본은 S1에서 새 기한 + 사유로 연장하고 알림톡(TPL_VBANK_DUE_EXTENDED)을 보낸다. 개발은 "토스에 발급 후 기한 변경 방법이 없어 두지 않는다"며 연장을 뺐고, 주석이 "관리자 연장 대상"이던 `payments.virtual_account_due_at`도 삭제됐다. 기한은 발급 응답 원문(`raw_response`)에만 남고, 운영자가 정하는 것은 새 발급분의 유효 시간(`site_settings.virtual_account_valid_hours`)뿐이다. 제공하지 않으면 프로토에서 연장 박스를 빼고 '재발급 안내'(또는 기본 유효 시간 안내)로 바꿀지 | 프로토 L1067-1077 `#vbankExtendBox`, `extendVbankDueDate()` L3596 | `app/Services/Admin/OrderService.php:490`, `app/Services/Order/OrderService.php:701`(depositInfo), `database/migrations/2026_09_08_000076_drop_payment_legacy_columns.php`, `2026_10_20_000226_add_virtual_account_valid_hours_to_site_settings_table.php` (10-27 스키마 재색인 반영)  **→ 결정(v6.92 white, D-ORD-01)**: 연장 없음 · 기본 입금 기한 72시간(`virtual_account_valid_hours` 기본값 24 → 72) · 같은 계좌 · 기한 재안내(`TPL_VBANK_ISSUED`)만 |
| Q-ORD-2 | 주문 조회용 엑셀에 반출 사유를 받는가? 정본(ORD-001 ⑥)은 사유 없이 열람 로그만, 개발은 CONF-005 반출 정책을 따라 공용 사유(ReasonRequest)를 받는다(개발이 충돌 대장에 기록) | 프로토 `downloadOrderLookupExcel()` L3050 | `app/Http/Requests/Admin/OrderDownloadRequest.php:7` |
| Q-ORD-3 | 반품 검수 사진 필수 범위 — 정본 배송 관리 화면은 '훼손 판정 시 필수', 개발은 훼손 **또는 정상 + 고객 귀책**에도 필수(두 화면 제안을 합친 임시안, 개발도 미확정 표시) | 프로토 L953 "창고 검수 증빙 사진 (훼손 판정 시 필수)" | `app/Http/Requests/Admin/ReturnInspectionRequest.php:32`, `app/Models/Refund.php:281`  **→ 결정(v6.92 white, D-ORD-02)**: 고객 훼손 판정 때만 필수(정상 + 고객 귀책 필수 제거). 함께 D-ORD-09 검수 3값 |
| Q-ORD-4 | 외부 3PL 대행사 계정(ROLE_PARTNER_3PL)을 두는가? 정본은 배송 관리 전용 격리 세션(금액 · 결제수단 차단, 연락처 마스킹, 발주 · P1 · P2 · S3만)을 정의. 개발은 역할 없이 메뉴 권한(`admin.deliveries.index`)만 있고 발주 파일에 연락처 원문이 실림 | 프로토 L539-540, L794-803, `setSessionRole()` L1788 | `routes/admin.php:866-889`(메뉴 권한만), `app/Services/Admin/DeliveryService.php:53` DISPATCH_HEADERS(수령인연락처) |

- 반품 배송비 귀책(편도 3,000 / 왕복 6,000) 질문은 계산 규칙이라 `ADMN-RFD-002.md` Q-RFD-7에 둔다(S3 `#inpInspectFault` 값도 그 결정을 따른다).
