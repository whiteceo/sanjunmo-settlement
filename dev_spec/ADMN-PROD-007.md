# ADMN-PROD-007 상품 마스터(일반상품) — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-007_baseline.html` (원본 상태: d6723b0 v7.01)
- 맞춘 개발 커밋: `a8016168` (2026-10-27) — d562524a 이후 이 화면 변경은 `suppliers.code` 주석 정정(e555839b)뿐
- v7.01 정본 변경: 재고 2단 차감(white 결정 Q-3PL-1, 설계서 v3.2.25): 결제 완료 → 예약(가용 감소), 3PL 송장 업로드 → 실재고 확정 차감. 화면은 실재고 · 예약 · 가용 3칸. 개발은 재고 1칸(books.stock · goods.stock, 결제 시 즉시 차감)이라 예약 · 가용은 개발 미구현 — reserved_stock (규칙), 가용 = stock − reserved_stock 파생. 개발팀 전달 대상
- 포함 화면: PROD-007 목록 · 007-S1 등록 · 수정 · 007-P1 재고 조정 · 007-P2 입출고 이력
- 개발 진행: 구현(목록 · 등록 · 수정 · 판매중지 · 일괄 판매중지 · 재고 조정 · 입출고 이력 · 엑셀). `_index/progress.md` PROD-007 · 007-S1 라우트 주석 있음

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 목록(`switchView('list')`) | PROD-007 목록 | `resources/views/admin/goods/index.blade.php` |
| 등록 · 수정 폼(`openForm`) | PROD-007-S1 | `goods/create.blade.php` · `goods/edit.blade.php` + `goods/form.blade.php` |
| `modal-stock-p1` 재고 조정 | 007-P1 | `goods/edit.blade.php` `#layerGoodsStockAdjust` |
| `modal-stock-p2` 입출고 이력 | 007-P2 | `goods/edit.blade.php` `#layerGoodsStockLogs` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.goods.index` | 상품 마스터(추정) | 목록 · S1 · P1 · P2 전부 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 권한 축 5개. 화면 안 버튼 노출은 모두 `@adminCan('admin.goods.index', …)`(`goods/index.blade.php:126,140,144,207`, `goods/edit.blade.php:25,29`).
- 사입 원가 열람 · 엑셀은 메뉴 권한 + `AdminPermissionService::canManageCostPrice()`(재무 권한) 이중 판정(`GoodsController.php:51`, `GoodsService.php:40-43`). 프로토타입은 `#chk-fin-role` 체크박스로 시연(L341).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{goods}` = `goods.id`(숫자만, `whereId`).

### PROD-007 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 | GET | `/goods` | `admin.goods.index` | 조회 | GoodsController@index |
| 엑셀 다운로드(사유 레이어 `layerReason`) | GET | `/goods/download` | `admin.goods.download` | 다운로드 + 재무 권한 | GoodsController@download |
| 선택 판매중지 | POST | `/goods/bulk-stop` | `admin.goods.bulk-stop.update` | 수정 | GoodsController@bulkStop |

### PROD-007-S1 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/goods/create` | `admin.goods.create` | 등록 | GoodsController@create |
| 등록 | POST | `/goods` | `admin.goods.store` | 등록 | GoodsController@store |
| 수정 폼 | GET | `/goods/{goods}/edit` | `admin.goods.edit` | 수정 | GoodsController@edit |
| 수정 | PUT | `/goods/{goods}` | `admin.goods.update` | 수정 | GoodsController@update |
| 판매중지 전환 | POST | `/goods/{goods}/stop-selling` | `admin.goods.stop.update` | 수정 | GoodsController@stopSelling |
| 삭제 | — | — | 없음(주문이 상품 ID 참조, `routes/admin.php:414`) | | |

### PROD-007-P1 재고 조정 · P2 입출고 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| P1 재고 조정 저장 | PUT | `/goods/{goods}/stock` | `admin.goods.stock.update` | 수정 | GoodsController@stockAdjust |
| P2 입출고 이력 | (수정 폼에 함께 실림, `stockLogs`) | `/goods/{goods}/edit` | `admin.goods.edit` | 수정 | GoodsController@edit(`formData`) |
| P2 기간 · 구분 필터 조회 | GET | `/goods/{goods}/stock-logs` (규칙) | `admin.goods.stock-logs.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명(개발은 전체 이력을 레이어에 한 번에 그림) |

## 3. 폼 필드 · 검증

### 목록 검색 (GET, GoodsService::normalizeFilters `GoodsService.php:50-61`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `goods_supply_type` | `PURCHASED_RESALE`(매입 재판매) · `DIRECT_SALE`(자사 직접 판매) | `#fl-supply` (프로토 값 동일, '전체' = `ALL` → 개발은 빈 값) |
| `sale_status` | `selling`(판매중) · `stopped`(판매중지) · `soldout`(품절 — 재고 파생) | `#fl-status` 판매중 · 판매대기 · 판매중지 · 품절 · 판매종료 (개발에 판매대기 · 판매종료 없음 — 8절 Q1) |
| `stock_status` | `normal`(정상) · `low`(재고 임박) · `soldout`(품절) | `#fl-stock` `NORMAL` · `LOW` · `OUT` |
| `keyword` | 상품명 · GDS 코드, 100자 | `#fl-kw` |
| `page` | 페이지(30건 고정 `PER_PAGE`) | |
| (스코어카드 링크) | 전체 · 판매중 · 임박 · 품절 건수 | 프로토 없음(개발에만) |

### 일괄 판매중지 (GoodsRequest, bulk-stop 분기 `GoodsRequest.php:36-41`)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | required · array · 1~500 · integer | `.g-chk` 행 체크박스, `bulkStopSale()` |

### S1 등록 · 수정 (GoodsRequest `GoodsRequest.php:43-65`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (상품 ID) | 저장 후 `GDS-%04d`(id) 자동 채번(`GoodsService.php:105-107`) | | `#f-id` (readonly, `GDS-0001`) |
| `name` | required · max 255 | | `#f-name` (프로토 placeholder '최대 80자') |
| `goods_supply_type` | required · in SUPPLY_LABELS. 판매 이력 있으면 변경 불가(서비스 검증 `GoodsService.php:332-334`, 폼은 disabled + hidden) | `PURCHASED_RESALE` 매입 재판매 · `DIRECT_SALE` 자사 직접 판매 | `#f-supply` · 잠금 문구 `#f-supply-lock-msg` |
| `display_status` | required · in STATUS_LABELS | `selling` 판매중 · `stopped` 판매중지 | `#f-status` 판매중 · 판매대기 · 판매중지 · 판매종료 (8절 Q1) |
| `category_id` | nullable · integer (category_products 다형 매핑) | `categories` 선택 목록 | `#f-cat` 굿즈 · 학습용품 / 공학용 계산기 / 문구 · 노트 (프로토는 고정 3종) |
| `sale_price` | required · integer 0~100,000,000 (콤마 제거) | | `#f-price` (프로토 min 100 · step 100, 저장 시 >0) |
| (공급가액 · 부가세) | 화면 표시만 `#vatSplit`, `Goods::splitVat` 반올림 | | `#f-vat-split` (FLOOR — 8절 Q2) |
| `cost_price` | nullable · integer. 재무 권한 아니면 무시, DIRECT_SALE이면 null | | `#f-cost` · `#f-cost-hint` |
| (원가 계정 · 세무 판정) | 고정 표시 `INVENTORY_PURCHASE` · TX-13 | | 고정 표시(같음) |
| `stock` | required · integer 0~1,000,000 — **수정 화면에서도 직접 입력** | | `#f-stock` (프로토 readonly, 조정 레이어로만 — 8절 Q3) |
| `stock_alert_qty` | nullable · integer | | `#f-threshold` (프로토 필수 *) |
| `supplier_id` | PURCHASED_RESALE이면 required · suppliers 존재(서비스) | suppliers.id | `#f-supplier` |
| (사업 상태) | 매입처 option `data-status` → `#supplierStatus` | | 프로토 없음(개발에만) |
| (매입 대금 경로 · 배송 정책) | 고정 문구 | | 고정 문구(같음) |
| `thumbnail` | 등록 required · 수정 nullable · jpg/jpeg/png/webp · 5MB | | '파일 변경' 버튼(L622, 동작 없음) |
| `description` | nullable · 65,535바이트 · Purifier | | `#f-desc` |

### P1 재고 조정 (GoodsStockAdjustRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `type` | required · in ADJUST_TYPE_LABELS | `inbound` 입고 · `restore` 복구 · `adjust` 수기 조정 · `damaged` 파손 · `lost` 분실 · `etc` 기타 (규칙, v6.92 D-PROD-06) | `#p1-reason` 입고 · 반품 입고 · 파손·불량 폐기 · 분실 · 실사 조정 · 기타 (v6.92 6종) |
| `reason_etc` (규칙) | `type=etc` 이면 required · max 50 | 기타 사유 직접 입력 | `#p1-reason-etc` (v6.92) |
| `quantity` | required · integer · not 0 · **부호 있는 증감**(음수 = 차감). 결과 재고 < 0이면 거부(`GoodsService.php:212`) | | `#p1-dir` PLUS · MINUS + `#p1-qty`(1 이상) |
| `memo` | nullable · max 255 | | `#p1-memo` (프로토 최대 200자, v6.92부터 '실사 조정'이면 필수) |
| (조정 후 재고 미리보기) | 개발 없음 | | `#p1-after-stock` |

### P2 입출고 이력 필터
| 필드 | 개발 | 프로토타입 대응 |
|---|---|---|
| 기간 `date_from` · `date_to` (규칙) | 개발 미구현 | 날짜 input 2칸(id 없음, L713) |
| 구분 `type` (규칙) | 개발 미구현 | `#p2-filter-type` 수기 조정 · 주문 차감 · 취소·반품 복원 |

## 4. 목록 필터 · 정렬 · 표 컬럼

| 개발 컬럼(`index.blade.php:160-169`) | 프로토타입 컬럼(L463) |
|---|---|
| 선택 `ids[]`(판매중지 행은 disabled) | 체크박스 `.g-chk` |
| 상품 ID `code` | 상품 ID |
| 공급 형태 `supply_label` | 공급 형태 |
| 상품명(→ edit 링크 `.link--view`) | 상품명 |
| 판매가 VAT 포함 | 판매가 (VAT 포함) |
| (없음) | 공급가액 / 부가세 (10/11) — 프로토에만 |
| 사입 원가(재무 외 `***`) | 사입 원가 (대외비) |
| 재고(임박 · 품절 배지, 행 배경) | 재고 (임계치 20) |
| (없음) | 세무 / 정산 — 프로토에만 |
| 판매 상태 | 판매 상태 |
| 관리(수정) | 재고 제어 / 관리(재고 조정 · 이력 버튼) |

정렬: 개발 정렬 파라미터 없음(저장소 기본 순서). 페이지 30건.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `goods.code` | string(50) | 상품 ID `GDS-%04d` | 목록 · S1 `#f-id` |
| `goods.name` | string(255) | 상품명 | 목록 · S1 |
| `goods.goods_supply_type` | string(20) | `PURCHASED_RESALE` · `DIRECT_SALE` | 목록 · S1 |
| `goods.original_price` | integer | 정가 — 화면 입력 없음, 판매가와 같은 값 저장(`GoodsService.php:349-350` 미확정) | — |
| `goods.sale_price` | integer | 판매가(VAT 포함) | 목록 · S1 |
| `goods.cost_price` | integer null | 사입 원가(대외비) | 목록 · S1 |
| `goods.stock` · `stock_alert_qty` | integer | 현재 재고 · 임박 기준 | 목록 · S1 · P1 |
| `goods.display_status` | string(20) | `selling` · `stopped` (마이그레이션 주석은 `hidden`도 언급, 모델은 2값) | 목록 · S1 |
| `goods.supplier_id` | FK suppliers | 매입처 | S1 |
| `goods.thumbnail_path` · `description` | | 대표 이미지 · 상세 | S1 |
| `goods.delivery_fee` · `is_free_delivery` · `free_delivery_threshold` · `island_delivery_fee` · `return_delivery_fee` | | 배송 정책(화면 입력 없음, NULL = 사이트 기본) | — |
| `goods.maker` | string(100) null | 제조사(화면 없음) | — |
| `category_products` (다형) | | 노출 카테고리 | S1 `#f-cat` |
| `goods_stock_logs` (`goods_id`, `type`, `quantity`, `before_stock`, `after_stock`, `order_id`, `order_item_id`, `admin_id`, `memo`, `created_at`) | | 입출고 원장. `type`에 `outbound`(판매 출고) 추가 | P1 · P2 |
| `suppliers` (`code` SUP-%04d — 주석 정정 a8016168 · 마이그레이션 000274, `name`, `business_status`, `cost_account_type` …) | | 매입처 | S1 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 검색 `form[method=get]`(id 없음) · `select[name=goods_supply_type\|sale_status\|stock_status]` · `input[name=keyword]` | 목록 검색 | `#fl-supply` · `#fl-status` · `#fl-stock` · `#fl-kw` |
| `layerReason` + `data-reason-*` | 엑셀 사유 레이어(공통) | `#btn-excel` |
| `bulkStop` · `bulkStopForm` · `checkAll` · `[data-bulk-check]` | 일괄 판매중지 | `bulkStopSale()` 버튼 · `.g-chk` |
| `tr[data-href]` | 행 클릭 → 수정 | 행 클릭 `openForm(id)` |
| `goodsForm` | S1 수정 폼 | 폼 영역(form 태그 없음) |
| `salePrice` · `vatSplit` · `costPrice` | 판매가 · 분해 표시 · 원가 | `#f-price` · `#f-vat-split` · `#f-cost` |
| `supplierId` · `supplierStatus` | 매입처 · 사업 상태 | `#f-supplier` |
| `goodsStop` · `goodsStopForm` | 판매중지 전환 | `stopCurrentProduct()` 버튼 |
| `layerGoodsStockAdjust` (`.layer__open[data-target]`) | P1 | `modal-stock-p1` · `#btn-p1-save` |
| `layerGoodsStockLogs` | P2 | `modal-stock-p2` · `#p2-tbody` |

마크업 공통: 레이어 `.layer-pop__overlay.layer-pop--hidden` + `.layer__open[data-target]`, 입력 `.input__text` · `.select`, 버튼 `.btn__system` · `.btn__small` + `.btn--basic` · `.btn--save`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 목록 스코어카드(전체 · 판매중 · 재고 임박 · 품절 건수, 클릭 필터) — `goods/index.blade.php:83-101`
- 엑셀 반출 사유 입력 레이어 + 재무 권한 제한 — `GoodsController.php:49-76`
- S1 매입처 사업 상태 표시 `#supplierStatus` — `goods/form.blade.php:158-159`
- S1 대표 이미지 업로드 실제 검증(jpg · png · webp · 5MB) — `GoodsRequest.php:58`
- 판매 이력 있는 상품의 공급 형태 변경 서버 차단 — `GoodsService.php:332-334` (프로토는 문구만, L519)

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 판매 상태 판매대기 · 판매종료 및 상태별 안내(`syncGoodsStatusHint`, L1058) — 8절 Q1
- 목록 공급가액 / 부가세 · 세무 / 정산 컬럼(L463)
- P1 조정 후 재고 미리보기 · 음수 차단 즉시 표시(`updateP1Preview`, L1099)
- P2 기간 · 구분 필터(L713-715)
- 권리자 매핑 표시(자사 100% 자동 매핑, L543-546) — 개발 폼에 없음
- 재무 권한 시뮬레이션 토글 `#chk-fin-role`(시연용, 개발은 실제 권한)

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#fl-status` 판매중 · 판매중지 · 품절 | `sale_status` `selling` · `stopped` · `soldout` |
| `#fl-stock` `NORMAL` · `LOW` · `OUT` | `stock_status` `normal` · `low` · `soldout` |
| `#f-status` 판매중 · 판매중지 | `display_status` `selling` · `stopped` |
| `p1-dir` PLUS · MINUS + `p1-qty` | `quantity` 부호 있는 정수 1칸 |
| `p1-reason` 한글 값 | `type` `inbound` · `restore` · `adjust` · `damaged` · `lost` |
| `p1-memo` | `memo` |
| 이력 '처리 후 재고' | `before_stock` → `after_stock` 둘 다 표시 |
| `goods_stock_log` (문구) | 테이블 `goods_stock_logs` |
| P2 구분 '주문 차감' · '취소·반품 복원' · '수기 조정' | `type` `outbound` 판매 출고 · `restore` 복구 · `adjust` 수기 조정 등 |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-PROD007-1 | 일반상품 판매 상태: 정본은 공통 4상태(판매대기 · 판매중 · 판매중지 · 판매종료) + 자동 `품절`. 개발은 `selling` · `stopped` 2값(품절은 재고 파생). 정본 확정 사항이라 개발에 `ready`(판매대기) · `ended`(판매종료) 추가 요청으로 보면 되는지 | 통합 설계서 3.2.2 3항 '상품 판매 상태 공통 기준(2026-10-26 확정)' (`docs/산준모닷컴 구축 통합 상세 설계서.md:246`), 프로토 `#fl-status` L413-419 · `#f-status` L533-537 | `app/Models/Goods.php:32-39,100-104`, `app/Services/Admin/GoodsService.php:58` **→ 정본대로(POLICY_D_PROD A, 통합설계서 3.2.2 3항(2026-10-26 확정))**: 공통 4상태 + 자동 품절 — 개발에 `ready` · `ended` 추가 요청으로 보면 됨 |
| Q-PROD007-2 | 부가세 분해 끝수: 프로토는 `FLOOR(판매가×100/110)`, 설계서는 `Round(결제액×10/11, 0)`, 개발은 반올림. 정본끼리 다르므로 어느 쪽으로 맞출지 | 프로토 L562 · L824-828(`Math.floor`), 설계서 `:263`(Round) | `app/Models/Goods.php:121-133`('미확정' 주석) **→ 정본대로(D-PROD-09 A, 02권 8.3 · 00 INDEX §2)**: 공급가액 내림(총액 역산)으로 통일, 설계서 문구 정정(v3.2.21) — 개발 반올림 정정 전달 |
| Q-PROD007-3 | 현재 재고 직접 수정: 프로토는 수정 모드에서 현재고 덮어쓰기 불가(조정 레이어로만, 사유 이력 필수). 개발 수정 폼은 `stock`을 그대로 받아 이력 없이 덮어쓴다 | 프로토 L590-593 | `app/Http/Requests/Admin/GoodsRequest.php:51`, `app/Services/Admin/GoodsService.php:329`, `resources/views/admin/goods/form.blade.php:131` **→ 결정(v6.92 white, D-PROD-06)**: 수정 폼 덮어쓰기를 막고 사유 이력이 남는 조정(P1)으로만 바꾼다 — 개발 `GoodsRequest` `stock` 입력 제거 |
| Q-PROD007-4 | 재고 조정 사유 목록과 메모 필수: 프로토 5종(신규 발주 입고 · 고객 반품 양품 입고 · 파손·불량 폐기 · 물류센터 재고 실사 조정 · 기타 — 기타는 메모 필수, 200자) vs 개발 5종(입고 · 복구 · 수기 조정 · 파손 · 분실, 메모 선택 255자). 어느 목록으로 확정할지 | 프로토 L679-690 · L1125-1128 | `app/Models/GoodsStockLog.php:62-68`, `app/Http/Requests/Admin/GoodsStockAdjustRequest.php:118-121` **→ 결정(v6.92 white, D-PROD-06)**: 사유 6종(입고 · 반품 입고 · 파손·불량 폐기 · 분실 · 실사 조정 · 기타) + '기타'는 사유 직접 입력 필수, 실사 조정은 메모 필수 |
| Q-PROD007-5 | 재고 알림 임계치 필수 여부: 프로토 필수(*), 개발 nullable(비면 임박 판정 안 함) | 프로토 L595-597 | `GoodsRequest.php:52`, `app/Models/Goods.php:118` **→ 정본대로(POLICY_D_PROD A, 통합설계서 S2-09 L280)**: 안전재고 경고 기준 20개 — 기본값 20, 비면 20 적용(개발팀 전달) |
