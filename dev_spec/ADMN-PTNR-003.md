# ADMN-PTNR-003 공급사 파트너 센터 — 개발 명세

> **추론 기반 신규, 정본 근거 없음.** 거래처(매입처 · 도서 공급사)용 외부 화면은 정본(통합 설계서 · 정산 00~04권)과 개발 코드 어디에도 없다. 소속 규칙 · 매입 재판매 · 거래처 테이블 · 도서 수불 같은 관련 기능에서 추론해 만들었다. 정본에 직접 근거가 있는 부분은 아래 표에 절을 적었고, 나머지 핵심 가정(C 9건: D-PTNR3-01~08 · 10)은 **확정(2026-10-27 white, D-PTNR3-NN 권고대로)** 이다. D-PTNR3-09는 원래 정본 판단(A). 근거 · 권고 원문은 `scripts/qa/reports/review/findings/devspec/POLICY_D_PTNR3.md`.

## 추론 근거 목록

| 구분 | 근거 (문서 절 · 파일:줄) | 이 화면에 쓴 내용 | 근거 강도 |
|---|---|---|---|
| 정본 | `README.md` L43 (1절 5항) | 외부 계정 소속 3종(내부 직원 / 권리자 / 거래처), 데이터 범위는 소속으로 · 메뉴 접근과 데이터 범위(본인 바인딩)/기능 범위 2단 통제. "새 외부 파트너는 소속을 늘리지 않고 거래처 유형을 추가" | 직접 |
| 정본 | `README.md` L84 · L91 | VEND-001 = 매입처 · 물류 대행사 거래처 원장, SNB 밖 파트너 전용 화면은 PTNR-001 하나(권리자용) — 거래처용은 없음 | 직접(빈자리 확인) |
| 정본 | 02권 2.4절 L64~70 | 매입처는 권리자가 아니라 거래처 테이블 `suppliers`. 도서 매입처 → 전자계산서 수취, 정정은 수취 증빙 재요청(채널 4), 대금은 AP 결제 · 대량이체 제외 | 직접 |
| 정본 | 01권 6.1절 L406 · L412 · L413 | 매입 재판매(`PURCHASED_RESALE`) — 정산 엔진 비인입, 원가는 매입 원가, 대금은 AP 경로, 당사가 공급받는 자로 전자계산서 수취, TX-11 | 직접 |
| 정본 | 01권 6.5절 L490 | 매입처 수취 계산서는 권리자 발행 증빙 제출 영역에 넣지 않고 수취 상태(미수취 / 수취 완료 / 금액 불일치)로 따로 추적 | 직접(제출 흐름과 긴장 — 확정(2026-10-27 white, D-PTNR3-04 권고대로): 공급사 제출은 별도 테이블 · 별도 상태의 수취 확인 보조, 확정은 재무팀 홈택스 대조) |
| 정본 | 03권 L295 | 매입처는 사업자등록번호 · 계좌만 수집(주민등록번호 없음) | 직접 |
| 정본 | 03권 L356 · L357 · L377 · L427 | VEND-001 · BOOK-001 역할, 매입처도 국세청 상태조회 대상, 폐업 감지 시 신규 증빙 요청 중단 · 미지급 잔액 유지 | 직접 |
| 프로토타입 | `prototype_clean/ADMN-PTNR-001_baseline.html` (전체) | 레이아웃 · 헤더 · 탭 · 표 · 모달 · 클래스, `?holder=&role=` 착지, 역할 그룹 `side`/`aff` 검사, 세금계산서 · 증빙 제출 흐름(L273~311 · L1004~1061), 내 정보 열람 전용 | 디자인 기준 |
| 프로토타입 | `prototype_clean/ADMN-SETT-011_baseline.html` L281~312 · L414~421 · L541~560 | 도서 매입 계산서 대조(S1): 기준 금액 = 당월 입고 수량 × 사입 원가, 9월분 SUP-0004/0005/0006/0008 수량 · 원가 · 수취 상태 — 이 화면 9월 숫자 원천 | 직접(숫자) |
| 프로토타입 | `prototype_clean/ADMN-PROD-004_baseline.html` L1489~1533 · L1793~1812 | 재고 수불 유형(입고 · 고객 반품 입고 · 파손 차감 · 실사 조정), PROD-BK-2001 매입가 12,000원 · 매입처 SUP-0003 · 재고 140권 | 직접(숫자) |
| 프로토타입 | `prototype_clean/ADMN-BOOK-001_baseline.html` L843 · L972 | 사입 도서 매입처 표기(SUP-0003), 공급 원장 = 공급 형태 · 원가 마스터 | 참고 |
| 프로토타입 | `prototype_clean/ADMN-VEND-001_baseline.html` · `common-master.js` VENDOR_TYPE_SEED · VENDOR_SEED | 거래처 유형 양식(PURCHASE / LOGISTICS), 거래처 코드 SUP-NNNN, 거래 조건(공급률 · 지급 조건), 거래 중지 = 발주 대상 제외 | 직접 |
| 프로토타입 | `prototype_clean/ADMN-SETT-002_baseline.html` S2 (PTNR-001 `renderStatement` L781~889로 재현) | 정산서 형식: 문서 머리 · 당사자 2칸 · 요약 표 · 산출 요약 · 항목별 표 · 증빙 · 하단 안내 | 형식 |
| 프로토타입 | `prototype_clean/ADMN-SETT-008_baseline.html` L878~895 | 매입처 SUP-0003 국세청 재조회 · TX-11 고정 · "면세 계산서 수취 대상" | 참고 |
| 개발 | `routes/admin.php:434-450` | `admin.book-supply.*` 라우트(공급 원장 = 운영자 화면), `book-supply.suppliers.store` 매입처 등록 | 이름 규칙 |
| 개발 | `app/Models/BookStockLog.php:44-69` | 수불 코드 `in` · `return_in` · `disposal` · `audit` · `order_out` · `order_restore` — 매입처 반출 코드 없음 | 이름 · 빈자리 |
| 개발 | `app/Http/Requests/Admin/BookStockAdjustRequest.php:26-37` | `type` · `quantity` · `memo` | 필드명 |
| 개발 | `app/Http/Requests/Admin/SupplierRequest.php:29-44` | `business_no` · `bank_name` · `account_no` · `account_holder` · `settlement_terms` · `contact_email` | 필드명 |
| 개발 | `app/Models/Supplier.php:20-37` · `database/migrations/2026_09_18_000126_create_suppliers_table.php:24` | `suppliers` 컬럼, 계좌 암호화(`account_no_enc` hidden), `business_status` | 컬럼 |
| 개발 | `app/Services/Admin/BookSupplyService.php:24-50` | 공급 형태 상수, 위탁(CONSIGNMENT) 1차 조회만 | 범위 |
| 개발 | `database/migrations/2026_09_08_000079_add_settlement_columns.php:122-139` | `book_purchase_costs` — **순 판매 수량 × 권당 원가**(판매 기준). 프로토타입 SETT-011은 입고 기준. 확정(2026-10-27 white, D-PTNR3-02 권고대로): 대금은 입고 기준, `book_purchase_costs`는 매출원가 집계로 정리 | 충돌 → 개발팀 전달 |
| 개발 | `config/admin.php:35-44` | 역할별 착지(`landing`) — 외부 3PL · 공급사 착지 없음(`logistics`는 내부 물류팀) | 빈자리 |

- 프로토타입 파일: `prototype_dev/ADMN-PTNR-003_baseline.html` (prototype_clean 원본 없음 — 이 파일이 원본. `apply_dev_map.py` 대상 아님. prototype_clean에 같은 화면이 생기면 그쪽을 원본으로 바꾼다)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PTNR-003(홈) · 공급 원장 · 발주 · 입고 확인(+ 발주 확인 모달 · 이의 제기 모달) · 월 매입 정산서 · 세금계산서 · 증빙 제출 · 내 정보(+ 변경 요청 모달). 화면 코드는 PTNR 규칙으로 지었다(001 권리자, 002는 3PL 후보용으로 비워 둠 — `_STATUS.md` 신규 후보 1행)
- 개발 진행: **미구현(규칙 기반 명명)** — `_index/progress.md`에 화면 코드 없음, 외부(거래처) 로그인 · 역할 없음

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.partner.book-supply.index` (규칙) | 공급 원장 | 개발 미구현 |
| `admin.partner.purchase-orders.index` (규칙) | 입고 · 반출 확인 (1단계) / 발주 · 입고 확인 (2단계) | 〃 — 확정(2026-10-27 white, D-PTNR3-05 권고대로) 1단계는 시스템 발주 없이 입고 전표 확인 · 이의만 |
| `admin.partner.purchase-statements.index` (규칙) | 월 매입 정산서 | 〃 |
| `admin.partner.purchase-invoices.index` (규칙) | 세금계산서 · 증빙 제출 | 〃 |
| `admin.partner.profile.index` (규칙) | 내 정보 | 〃 |

- 역할 그룹: **`RG-09` 도서 공급사** — 2차에 매입처 외부 계정 발급 · 역할 그룹 1개 추가 확정(2026-10-27 white, D-PTNR3-01 권고대로). `side: EXTERNAL`, `aff: ["VENDOR"]`, `perms: { supply: "RWX" }`. v6.92(18d66c1)부터 공통 기준정보(`common-master.js`)에 RG-09 '도서 공급사'가 있다(`on: false` 1차 미사용, `perms: {}`, 시작 화면 PTNR-003). 화면은 이름 · side · aff를 기준정보에서 읽고, 기준정보에 `supply` 권한 값이 없을 때만 최초값 `ROLE_PROPOSED.perms.supply = "RWX"`를 쓴다(RG-09 자체가 없으면 `ROLE_PROPOSED` 전체). 메뉴 키 `supply`는 기준정보 메뉴 목록에 아직 없다(2차에 추가). 상단 역할 칩의 "(가정)" 표시는 뺐다. 개발 `admin_roles.code` 가칭 `supplier`.
- 본인 바인딩(데이터 범위): 계정의 소속 거래처 `supplier_id`로 모든 조회를 거른다. 화면은 `?vendor=SUP-NNNN`으로 흉내 낸다(지시서의 `VD-NNNN` 대신 기존 코드 SUP-NNNN 사용 — 개발 `suppliers.code` = `SUP-%05d`).
- 기능 범위: `supply` R = 조회, W = 발주 확인 · 입고/반출 확인 · 이의 · 증빙 제출 · 변경 요청, X = 엑셀 · PDF.
- 진입 차단: 거래처 없음 / 거래처 유형 양식이 PURCHASE가 아님(3PL `SUP-0020` 차단) / 역할 그룹이 EXTERNAL · VENDOR가 아님(`RG-05` 차단) / supply R 없음.
- 열람 전용: 거래처 `on=false` 또는 사업자 상태 폐업 · 휴업(예 `SUP-0008`) — 쓰기 버튼 숨김, 미지급 잔액 표시(03권 L427 추론). 확정(2026-10-27 white, D-PTNR3-07 권고대로): 열람 전용은 미지급 잔액(정산서가 있는 달의 순 매입액 − 지급액 합계)이 남아 있는 동안만, **잔액이 0이면 진입 차단(잠금)**.
- 메뉴 권한 5축과의 대응: 접미사 규칙대로 `index`·`show` 조회, `store` 등록, `confirm.update` 수정, `download` 다운로드. 삭제 동작 없음.

## 2. 화면별 라우트 (전부 개발 미구현, 규칙 기반 명명)

### PTNR-003 공급 원장
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(월 · 도서 필터) | GET | `/{admin}/partner/book-supply` | `admin.partner.book-supply.index` (규칙) | can_view | `Partner\BookSupplyController@index` (규칙) |
| 엑셀 | GET | `/{admin}/partner/book-supply/download` | `admin.partner.book-supply.download` (규칙) | can_download | `@download` (규칙) |

### PTNR-003 발주 · 입고 확인
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/partner/purchase-orders` | `admin.partner.purchase-orders.index` (규칙) | can_view | `Partner\PurchaseOrderController@index` (규칙) |
| 발주 확인(납품 예정일 회신) — **2단계** | PUT | `/{admin}/partner/purchase-orders/{purchaseOrder}/confirm` | `admin.partner.purchase-orders.confirm.update` (규칙) | can_update | `@confirm` (규칙) — 1단계에서는 만들지 않음(D-PTNR3-05) |
| 입고 확인 | PUT | `/{admin}/partner/stock-receipts/{stockReceipt}/confirm` | `admin.partner.stock-receipts.confirm.update` (규칙) | can_update | `Partner\StockReceiptController@confirm` (규칙) |
| 입고 이의 제기 | POST | `/{admin}/partner/stock-receipts/{stockReceipt}/dispute` | `admin.partner.stock-receipts.dispute.store` (규칙) | can_create | `@dispute` (규칙) |
| 반출 확인 | PUT | `/{admin}/partner/stock-returns/{stockReturn}/confirm` | `admin.partner.stock-returns.confirm.update` (규칙) | can_update | `Partner\StockReturnController@confirm` (규칙) |
| 반출 이의 제기 | POST | `/{admin}/partner/stock-returns/{stockReturn}/dispute` | `admin.partner.stock-returns.dispute.store` (규칙) | can_create | `@dispute` (규칙) |

- 접미사 `confirm` · `dispute`는 SUFFIX_PERMISSIONS 밖이라 하위 자원 + 표준 접미사(`confirm.update` · `dispute.store`)로 지었다(README 규칙 "추가 쓰기 동작은 하위 자원").

### PTNR-003 월 매입 정산서
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 월 선택 · 보기 | GET | `/{admin}/partner/purchase-statements?month=` | `admin.partner.purchase-statements.index` (규칙) | can_view | `Partner\PurchaseStatementController@index` (규칙) |
| PDF | GET | `/{admin}/partner/purchase-statements/{month}/download` | `admin.partner.purchase-statements.download` (규칙) | can_download | `@download` (규칙) |

### PTNR-003 세금계산서 · 증빙 제출
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/partner/purchase-invoices` | `admin.partner.purchase-invoices.index` (규칙) | can_view | `Partner\PurchaseInvoiceController@index` (규칙) |
| 제출 · 수정 제출 | POST | `/{admin}/partner/purchase-invoices` | `admin.partner.purchase-invoices.store` (규칙) | can_create | `@store` (규칙) |

### PTNR-003 내 정보
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 보기 | GET | `/{admin}/partner/profile` | `admin.partner.profile.index` (규칙) | can_view | `Partner\ProfileController@index` (규칙) |
| 변경 요청 | POST | `/{admin}/partner/profile/change-requests` | `admin.partner.profile.change-requests.store` (규칙) | can_create | `@storeChangeRequest` (규칙) |

- URL 접두사 `/{admin}/partner/...`는 관리자 앱 안에 외부 계정을 두는 현 구조(PTNR-001과 같음)를 따른다. 계정 부여는 확정(D-PTNR3-01)이고, 별도 도메인 · 가드로 뺄지는 개발 구조 판단.

## 3. 폼 필드 · 검증 (개발 미구현, 규칙 기반 명명)

### 발주 확인 `purchaseOrderConfirmForm` (PurchaseOrderConfirmRequest (규칙)) — 2단계(D-PTNR3-05)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `expected_date` | required, date_format:Y-m-d, after_or_equal:today | | `#poExpectedDate` 납품 예정일 |
| `quantity` | required, integer, min:1, lte:발주 수량 | | `#poQty` 납품 가능 수량 |
| `memo` | nullable, string, max:255 — quantity < 발주 수량이면 required(공백 제외 10자) | | `#poMemo` |

### 이의 제기 `stockReceiptDisputeForm` (StockDisputeRequest (규칙))
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `reason_code` | required, in | `qty_short`(수량이 적게 잡힘) · `qty_over`(수량이 많게 잡힘) · `not_defective`(파본 · 불량 사유 이견) · `other`(기타) | `#disputeReason` |
| `quantity` | required, integer, min:0 | | `#disputeQty` 공급사 기준 수량 |
| `reason` | MemberReasonRequest 규칙 재사용(공백 제외 10자 이상 · 서로 다른 글자 3개 이상 · 200자 이하) | | `#disputeMemo` |

### 증빙 제출 `purchaseInvoiceForm` (PurchaseInvoiceRequest (규칙))
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `purchase_invoice_id` | required, 본인 거래처 · 상태 none/reissue_requested | | 목록 행(`openTaxForm(id)`) — 화면은 JS 키 |
| `nts_approval_no` | required, regex `^\d{8}-\d{8}-\d{8}$` | | `#tiApproval` |
| `issue_date` | required, date, 공급(입고) 월 안 | | `#tiDate` |
| `supply_amount` | required, integer, = 입고 기준 매입액 | | `#tiSupply` |
| `tax_amount` | required, integer, in:0 (도서 면세) | | `#tiVat` |
| `evidence_file` | required, file, mimes:pdf | | `#tiFile` |

### 내 정보 변경 요청 `profileChangeRequestForm` (SupplierChangeRequest (규칙))
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `request_type` | required, in | `bank_account`(정산 계좌) · `contact`(담당자 메일) · `business_info`(사업자 정보) | `#pcType` |
| `bank_name` · `account_no` · `account_holder` | `request_type=bank_account`면 required. 형식은 SupplierRequest와 같음(`account_no` regex `^[0-9-]+$`), 예금주 = 사업자 명의 | | `#pcBank` · `#pcAccount` · `#pcHolder` |
| `contact_email` | `request_type=contact`면 required, email, max:100 | | `#pcEmail` |
| `reason` | 공백 제외 10자 이상, 200자 이하 | | `#pcReason` |
| `evidence_file` | bank_account · business_info면 required(통장 사본 / 사업자등록증) | | `#pcFile` |

- 정산 계좌 변경 처리 순서 — 확정(2026-10-27 white, D-PTNR3-08 권고대로): 화면 요청(사업자 명의 통장 사본) → 재무팀이 **이미 등록된 대표 번호**로 전화 확인 → 재무 책임자 승인 → 반영(CONF-010 감사 로그). 반영 전까지 기존 계좌로 지급. 공급사가 직접 고치는 경로는 두지 않는다.

## 4. 목록 필터 · 정렬 · 표 컬럼

| 목록 | 필터(name) | 정렬 | 컬럼 |
|---|---|---|---|
| 공급 원장 | `month`(YYYY-MM) · `book_id` | 도서 코드 | 도서 · 상품코드 / 매입 단가 / 기초 재고 / 입고(+) / 판매 출고(−) / 고객 반품 입고(+) / 매입처 반품(−) / 폐기 · 실사 조정 / 기말 재고 / 입고 기준 매입액 + 합계 행. 아래 입고 · 반출 전표 이력 |
| 입고 전표(1단계) · 발주 · 입고(2단계) | `status` 1단계 received · confirmed · disputed / 2단계 + ordered · accepted | 발주일 내림차순 | 관련 발주(2단계는 발주번호) / 발주일 / 도서 / 발주 수량 / 납품 예정일 / 입고 수량 / 입고 전표 / 상태 / 처리 |
| 반출 | — | 요청일 내림차순 | 반출번호 / 요청일 / 도서 / 수량 / 사유 / 매입 대금 차감 / 상태 / 처리 |
| 증빙 | — | 귀속월 내림차순 | 매입 귀속월 / 도서 / 증빙 종류 / 공급가액 / 세액 / 수취 계산서 금액 / 발행 기한(지남 표시) / 상태 / 제출 |

- 변경 요청 상태(규칙): `requested` 요청 접수 · `call_verified` 전화 확인 완료 · `approved` 재무 책임자 승인 · `done` 반영 완료(정산 계좌는 이 순서, 그 밖의 항목은 requested → done). 화면은 정산 계좌 요청 행에 단계 표시.
- 상태 코드(규칙, snake): 발주 `ordered` 발주 확인 대기 · `accepted` 납품 예정 · `received` 입고 확인 대기 · `confirmed` 입고 확인 완료 · `disputed` 이의 제기. 반출 `pending` · `confirmed` · `disputed`. 증빙 `none` 미수취 · `submitted` 제출 · `received` 수취 완료 · `reissue_requested` 수정 발행 요청 · `waiting` 마감 전. 지급 `paid` · `partial` · `hold` · `open`. 화면 JS는 대문자 키(`ORDERED` 등)를 쓴다.
- SETT-011 S1 상태와의 대응: `NONE`→`none`, `DONE`→`received`, `MISMATCH` · `REQUESTED`(재요청 중)→`reissue_requested`. 공급사 제출(`submitted`)은 SETT-011에 없는 새 상태 — 운영자 화면에 "공급사 제출 · 대조 대기"로 보여야 함(SETT-011 쪽 변경 필요, 이 작업 범위 밖).

## 5. DB 테이블 · 컬럼

| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `suppliers.code` · `name` · `business_no` · `ceo_name` · `payee_tax_type` · `business_status` · `api_checked_at` | 기존 | 거래처 기본 · 국세청 상태 | 상단 · 내 정보 · 정산서 공급자 칸 |
| `suppliers.bank_name` · `account_no_enc` · `account_holder` · `settlement_terms` · `contact_email` | 기존 | 계좌(마스킹만) · 지급 조건 · 메일 | 내 정보 · 정산서 |
| `books.code` · `title` · `cost_price` · `supplier_id` · `stock` · `book_supply_type` | 기존 | 공급 도서 · 매입 단가 · 재고 | 공급 원장 |
| `book_stock_logs.type` · `quantity` · `before_stock` · `after_stock` · `memo` · `created_at` | 기존 | 수불(입고 `in`, 고객 반품 `return_in`, 출고 `order_out`, 폐기 `disposal`, 실사 `audit`) | 공급 원장 월 집계 · 이력 |
| `book_stock_logs.type = 'return_out'` (규칙) | 코드 추가 | 매입처 반품(반출) | 공급 원장 · 반출 표 |
| `users.supplier_id` (규칙) | FK 추가 | 외부 계정 소속 거래처(본인 바인딩) | 진입 판정 |
| `suppliers.return_terms` (규칙) | 코드 추가 | 반품(반출) 조건 `defect_only` 파본 · 인쇄 불량만(기본) · `returnable` 재고 반품 가능 — VEND-001 거래 조건(PURCHASE 양식)에 칸 추가(D-PTNR3-03) | 내 정보 거래 조건 |
| `purchase_orders` (규칙, 2단계): `id` · `code`(PO-YYYY-MM-NNN) · `supplier_id` · `book_id` · `quantity` · `ordered_at` · `expected_date` · `confirmed_quantity` · `status` · `memo` · `admin_id` · `confirmed_by` · `confirmed_at` | 신규 | 발주 | 발주 표 |
| `stock_receipts` (규칙): `id` · `code`(WH-YYYYMMDD-NN) · `purchase_order_id` · `book_id` · `quantity` · `received_at` · `status` · `confirmed_by` · `confirmed_at` | 신규 | 물류센터 입고 전표 | 발주 표 입고 열 |
| `stock_returns` (규칙): `id` · `code`(RT-YYYY-MM-NNN) · `supplier_id` · `book_id` · `quantity` · `reason` · `unit_cost` · `status` · `requested_at` · `confirmed_at` | 신규 | 매입처 반출 | 반출 표 |
| `stock_disputes` (규칙): `id` · `disputable_type` · `disputable_id` · `reason_code` · `quantity` · `reason` · `status` · `created_by` · `resolved_by` · `resolved_at` | 신규 | 이의 제기 | 상태 아래 메모 |
| `purchase_invoices` (규칙): `id` · `supplier_id` · `book_id` · `month` · `supply_amount` · `tax_amount` · `received_amount` · `nts_approval_no` · `issue_date` · `evidence_path` · `status` · `submitted_by` · `matched_by` · `matched_at` | 신규 | 수취 계산서(SETT-011 S1 행과 같은 단위) | 증빙 표 · 정산서 3절 |
| `supplier_change_requests` (규칙): `id` · `supplier_id` · `request_type` · `payload_enc` · `reason` · `evidence_path` · `status` · `requested_by` · `call_verified_by` · `call_verified_at` · `approved_by` · `approved_at` · `processed_by` · `processed_at` | 신규 | 내 정보 변경 요청(원문 암호화), 정산 계좌는 전화 확인 · 재무 책임자 승인 기록(D-PTNR3-08) | 변경 요청 내역 |
| `book_purchase_costs.net_qty` · `unit_cost` · `total_cost` · `match_status` | 기존 | 개발의 월 매입 원가 = **순 판매 × 원가** | 이 화면은 쓰지 않음(입고 기준). 확정(D-PTNR3-02): 매출원가(판매 × 원가) 집계로 이름 · 주석 정리, "출판사 세금계산서와 대조" 용도는 입고 기준 테이블로 옮김 — 개발팀 전달 |

- 지급(AP) 실적은 회계 시스템에 있다(02권 2.4절). 확정(2026-10-27 white, D-PTNR3-06 권고대로): 계산서 수취분만 지급(미수취 · 불일치분 보류)하고 지급 상태를 공급사에 보여 준다. 지급액 · 지급일을 회계 연동으로 가져올지 재무 수기 입력으로 할지는 별도 결정이라 테이블은 정하지 않았다.

## 6. 개발 JS · 마크업 이름

| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `layerPurchaseOrderConfirm` · `purchaseOrderConfirmForm` · `purchaseOrderConfirmSubmit` | 발주 확인 모달 | 같음(이 파일은 처음부터 개발 이름) |
| `layerStockReceiptDispute` · `stockReceiptDisputeForm` · `stockReceiptDisputeSubmit` | 입고 · 반출 이의 모달(반출일 때 제출 버튼의 `data-dev-route`를 `stock-returns`로 바꿈) | 같음 |
| `layerProfileChangeRequest` · `profileChangeRequestForm` · `profileChangeRequestSubmit` | 내 정보 변경 요청 모달 | 같음 |
| `purchaseInvoiceForm` · `purchaseInvoiceSubmit` | 증빙 제출 카드(PTNR-001 `taxFormCard` · `btnTaxSubmit`에 해당) | 같음 |
| `.ptnr-*` | PTNR-001 디자인 클래스 그대로 | — |
| 모달 열기 · 닫기 | `open` 클래스 + 인라인 `display` 제거 / `open` 제거(공통 모달 핫픽스 대응, CLAUDE.md 알려진 함정) | `openLayer` · `closeLayer` |

- 첫 화면(SUP-0004) 기준 `data-dev-route` 19곳(탭 5 · 정적 버튼 · 폼, 행 버튼은 상태에 따라 늘고 줆), 실제 `name=` 입력 22개, `data-dev-flag="proto-only"` 11곳(섹션 6 · 모달 3 · 폼 1 · 배지 1).

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 없음. 개발에는 이 화면이 없다.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 화면 전체. 외부 거래처 계정(소속 `supplier_id`) · 역할 그룹 `supplier` · 착지(`config/admin.php` landing) 추가가 먼저 필요.
- 발주(`purchase_orders`)와 입고 전표 확인: 개발에는 발주 개념이 없고 재고는 `books.stock` 조정(`admin.books.stock.update`)만 있다.
- 매입처 반출(`return_out`): `BookStockLog` 코드에 없다.
- 공급사 증빙 제출: 개발 · 정본 모두 매입처 계산서는 "당사가 수취"로만 다룬다.
- 내 정보 변경 요청: 개발은 운영자가 `SupplierRequest`로 직접 고친다.

### 10-27 확정 반영 (2026-10-27 white, D-PTNR3-NN 권고대로)
- D-PTNR3-01 (10-27 확정 반영): 2차 외부 계정 · 역할 그룹 '도서 공급사' 1개 추가 확정 — 상단 역할 칩의 "(가정)" 표시 제거. 공통 기준정보 RG-09 추가 완료(v6.92, 1차 미사용) — 권한(`supply`)은 2차에 기준정보에 넣는다.
- D-PTNR3-02 · 04 · 06 · 10: 화면이 이미 권고대로(입고 기준 대금, 공급사 제출은 보조 · 확정은 홈택스 대조, 수취분만 지급 · 지급 상태 공개, 판매 출고 · 재고 수량 공개 · 판매가 · 고객 정보 숨김) — 화면 변경 없음. 02는 개발팀 전달(`book_purchase_costs` 이름 정리), 04는 정본 6.5절에 "공급사 화면 제출은 수취 확인 보조" 한 줄 보완 제안(정본 담당 작업).
- D-PTNR3-03 (10-27 확정 반영): 내 정보 거래 조건에 '반품(반출) 조건' 행 추가(기본 파본 · 인쇄 불량만, 거래 조건에 반품 가능이면 재고 반품 포함), 반출 표 안내 문구를 같은 기준으로 고침. 반출은 확인한 달 매입액에서 차감. 매입처별 조건은 공통 기준정보에 칸이 없어 화면 안 값(`VD_RETURN_TERMS`, 샘플)으로 둠 — VEND-001 칸 추가는 후속. 이미 받은 계산서 분의 정정 방법(수정 계산서 등)은 세무 확인 필요.
- D-PTNR3-05 (10-27 확정 반영): 1단계는 시스템 발주 없이 입고 전표 확인 · 이의만 — 메뉴 · 제목을 '입고 · 반출 확인'으로, 발주 확인 대기 · 납품 예정 행과 상태 필터 · 발주 확인 버튼을 뺌. 발주 확인 모달 · 코드는 2단계용으로 남기고 `?po_stage=2`로 미리 보기.
- D-PTNR3-07 (10-27 확정 반영): 폐업 · 휴업 · 거래 중지 계정은 미지급 잔액이 남은 동안 열람 전용(안내에 잔액 표시), 잔액 0이면 진입 차단(잠금).
- D-PTNR3-08 (10-27 확정 반영): 정산 계좌 변경 안내 · 요청 내역에 처리 순서(요청 → 대표 연락처 전화 확인 → 재무 책임자 승인 → 반영 · 감사 로그) 표시, 상태 `CALL_VERIFIED` · `APPROVED` 추가.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 거래처 코드: 지시서 `VD-NNNN` → 기존 `SUP-NNNN`(프로토 `common-master.js` · 개발 `suppliers.code`).
- 월 매입액 기준: 프로토(SETT-011 · 이 화면) **입고 기준** ↔ 개발 `book_purchase_costs` **순 판매 기준**. 정본 01권 6.1(재고자산 취득 `INVENTORY_PURCHASE`)은 입고 기준 쪽이라 화면은 입고 기준으로 두고 D-PTNR3-02로 올렸다.

## 8. 정책 확정 (2026-10-27 white — 각 항목 권고대로, 원문 `scripts/qa/reports/review/findings/devspec/POLICY_D_PTNR3.md`)
| 번호 | 내용 | 확정 | 화면 반영 |
|---|---|---|---|
| D-PTNR3-01 | 매입처 외부 계정 · 역할 그룹 | 확정(2026-10-27 white, D-PTNR3-01 권고대로): 2차에 계정 발급 + 역할 그룹 '도서 공급사' 1개 추가 | (10-27 확정 반영) "(가정)" 표시 제거. 기준정보 RG-09 추가 완료(v6.92) — supply 권한은 화면 최초값 |
| D-PTNR3-02 | 월 매입 대금 기준 | 확정(2026-10-27 white, D-PTNR3-02 권고대로): 입고 기준 + 개발 `book_purchase_costs`는 매출원가 집계로 정리 | 이미 권고대로. 개발팀 전달 |
| D-PTNR3-03 | 매입처 반품(반출) | 확정(2026-10-27 white, D-PTNR3-03 권고대로): 파본 · 인쇄 불량 반출, 거래 조건에 있으면 재고 반품도, 확인 월 매입액 차감 | (10-27 확정 반영) 반품 조건 표시 |
| D-PTNR3-04 | 매입 계산서 제출 흐름 | 확정(2026-10-27 white, D-PTNR3-04 권고대로): 제출은 보조, 확정은 재무팀 홈택스 대조 | 이미 권고대로 |
| D-PTNR3-05 | 발주 시스템화 | 확정(2026-10-27 white, D-PTNR3-05 권고대로): 1단계 입고 전표 확인 · 이의만 → 2단계 발주 | (10-27 확정 반영) 발주 확인 버튼 · 행 숨김, `?po_stage=2` |
| D-PTNR3-06 | 미수취분 지급 보류 · 지급 상태 | 확정(2026-10-27 white, D-PTNR3-06 권고대로): 수취분만 지급 + 상태 공개, 연동 방식은 별도 결정 | 이미 권고대로 |
| D-PTNR3-07 | 폐업 · 휴업 · 거래 중지 계정 | 확정(2026-10-27 white, D-PTNR3-07 권고대로): 열람만, 잔액 0이면 잠금 | (10-27 확정 반영) 잔액 표시 · 잠금 |
| D-PTNR3-08 | 정산 계좌 변경 요청 | 확정(2026-10-27 white, D-PTNR3-08 권고대로): 화면 요청 → 전화 확인 → 재무 책임자 승인 → 반영 | (10-27 확정 반영) 처리 순서 · 상태 |
| D-PTNR3-09 | 위탁사 화면 구분 | A(정본 02권 2.4절): 위탁사는 PTNR-001 | 변경 없음 |
| D-PTNR3-10 | 판매 출고 · 재고 수량 공개 | 확정(2026-10-27 white, D-PTNR3-10 권고대로): 본인 공급 도서 수량까지 공개, 판매가 · 고객 정보 숨김 | 이미 권고대로 |

## 검증 (2026-10-27)
- Python Playwright, `file://` 직접 열기, 새 브라우저 컨텍스트. 스크립트는 저장소 밖 임시 폴더.
- 36/36 PASS, pageerror 0 · console error 0: 탭 6개 전환, 공급 원장 9월 합계 26,120,000원 · 10월 기말 326권, 정산서 9월 순 매입 26,120,000원 · 8월 24,780,000원, 발주 확인 모달(✕ 닫기 · 다시 열기 · 검증 · 확인), 입고 확인, 반출 이의(취소 닫기 · 등록), 변경 요청(Esc 닫기 · 등록), 증빙 제출(승인번호 · 금액 · 파일 검증 → 제출 완료 · 배지 0), SUP-0005 수정 제출 · 본인 데이터만, SUP-0008 열람 전용, 3PL(SUP-0020) · 강사 역할(RG-05) 차단, SUP-0003 9월 정산서 없음.
- 확정 반영 후 재검증(2026-10-27): 47/47 PASS, pageerror 0 · console error 0. 위 항목에 더해 1단계 메뉴 '입고 · 반출 확인' · 발주 확인 버튼 · 발주 대기 행 · 상태 필터 없음 · 모달 열기 차단, `?po_stage=2`에서 발주 확인 모달 흐름, 역할 칩 "(가정)" 없음, 계좌 변경 처리 순서 표시, 반품 조건 행, SUP-0008 미지급 잔액 1,740,000원 표시, 거래 중지 + 잔액 0(SUP-0003, 같은 컨텍스트 localStorage) 잠금.
- v6.92 재검증(공통 기준정보 RG-09 `on: false` · `perms: {}` 반영 — supply 권한 최초값 대체): 47/47 PASS, pageerror 0 · console error 0. 대체 전에는 기준정보 RG-09의 빈 권한 때문에 진입이 막혔다.
