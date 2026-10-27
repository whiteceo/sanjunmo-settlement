# ADMN-VEND-001 거래처 관리 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-VEND-001_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: a8016168 (2026-10-27) — 이 화면 변경은 e555839b(`suppliers.code` 주석 자릿수만, 마이그레이션 000274). 거래처 관리 화면은 여전히 개발 미구현
- 포함 화면: ADMN-VEND-001 (모달 `modal-vendor` 거래처 등록 · `modal-type` 거래처 유형 관리)
- 개발 진행: **독립 화면은 개발 미구현(d562524a 기준), 규칙 기반 명명.** config/dev-progress.php 에 ADMN-VEND 코드가 없다(tests/Feature/Admin/QaResultAdminTest.php 의 "ADMN-VEND-001 … 화면 없음"은 테스트용 더미 행). 가장 가까운 개발 구현은 도서 공급 원장(`admin.book-supply.index`) 의 **매입처 탭(`?tab=suppliers`) + 매입처 등록** 이다

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.vendors.index` (규칙) | 거래처 관리 | 개발 미구현 |
| `admin.book-supply.index` | 도서 공급 원장(매입처 탭 포함) | routes/admin.php:438 · `@adminCan('admin.book-supply.index', 'can_create')`(resources/views/admin/book-supply/_suppliers.blade.php:44) |

- 현재 매입처 등록 `admin.book-supply.suppliers.store` 는 정규화 후 `admin.book-supply.index` 메뉴의 can_create 로 판정.
- 거래처 소속 외부 계정 역할 그룹(공통 기준정보 `common-master.js`, v6.92): RG-08 외부 3PL — 메뉴 키 `shipout` RWX(출고 대상 조회 · 출고 지시(발주 엑셀) · 송장 업로드) · `logibill` RW(월 물류비 명세서 제출, 메뉴 '물류비 청구 · 대사' = SETT-011 · PTNR-002), RG-09 도서 공급사 — 1차 미사용(`on: false`, 권한 없음, 2차에 PTNR-003과 함께). 거래처 관리 메뉴 키는 `vendor`. 개발 역할 코드 · 메뉴 없음(규칙: `3pl` · `supplier`).

## 2. 화면별 라우트
### 개발 구현분 — 매입처(도서 공급 원장 탭 ③)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 매입처 목록(탭) | GET | `/{admin}/book-supply?tab=suppliers` | `admin.book-supply.index` | can_view | BookSupplyController@index |
| 매입처 임시 등록(국세청 확인 전) | POST | `/{admin}/book-supply/suppliers` | `admin.book-supply.suppliers.store` | can_create | SupplierController@store |

### ADMN-VEND-001 거래처 관리 — 개발 미구현, 규칙 기반 명명
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/vendors` (규칙) | `admin.vendors.index` (규칙) | can_view | (규칙) VendorController@index |
| 등록 | POST | `/{admin}/vendors` (규칙) | `admin.vendors.store` (규칙) | can_create | (규칙) |
| 수정 · 거래 중지 | PUT | `/{admin}/vendors/{vendor}` (규칙) | `admin.vendors.update` (규칙) | can_update | (규칙) |
| 국세청 상태조회 | POST | `/{admin}/vendors/{vendor}/nts-verify` (규칙) | `admin.vendors.nts-verify` (규칙, 접미사 nts-verify → can_update — 권리자 원장 `admin.rights-holders.nts-verify` 와 같은 모양) | can_update | (규칙) |
| 거래처 유형 추가 | POST | `/{admin}/vendors/types` (규칙) | `admin.vendors.types.store` (규칙) | can_create | (규칙) |
| 거래처 유형 사용 · 중지 | PUT | `/{admin}/vendors/types/{type}` (규칙) | `admin.vendors.types.update` (규칙) | can_update | (규칙) |

## 3. 폼 필드 · 검증
### 매입처 등록 (SupplierRequest — 개발 구현) — `#supplierForm`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `name` | required · ≤100 | 상호 | `vf-name` 거래처명 |
| `business_no` | required · digits:10 (중복 불가) | 사업자등록번호 | `vf-biz` |
| `ceo_name` | nullable · ≤50 | 대표자명 | `vf-ceo` |
| `open_date` | nullable · Y-m-d | 개업일자 | — (프로토타입은 거래 시작일 `vf-since`) |
| `bank_name` · `account_no`(숫자 · -) · `account_holder` | nullable | 계좌 — account_no 는 암호화 저장 | — |
| `settlement_terms` | nullable · ≤100 | 정산(지급) 조건 자유 문자열 | 거래 조건 양식(renderTermsForm) |
| `contact_email` | nullable · email · ≤100 | 담당 메일 | `vf-contact`(연락처) |

- 과세유형(`payee_tax_type`)은 입력받지 않는다 — 국세청 응답값으로만 채운다(값 일반과세 · 간이과세 · 면세, Supplier::PAYEE_TAX_TYPES). 프로토타입 `vf-tax` 는 직접 선택.
- 등록 시 코드 `SUP-%04d`(id) 채번, business_status = `PENDING_VERIFICATION`(국세청 확인 대기)(app/Services/Admin/SupplierService.php:28-59).

### 거래처 관리 추가 필드 — 개발 미구현, 규칙 기반 명명
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `vendor_type_id` (규칙) | 필수 | 거래처 유형 | `vf-type` |
| `code` | 자동 채번(SUP-%04d 와 같은 방식) | 거래처 코드 | `vf-id` |
| `status` (규칙) | `active` 거래 중 · `suspended` 거래 중지 (규칙, 소문자 snake) | | 라디오 ON / OFF |
| `suspend_reason` (규칙) · `suspend_approved` (규칙) | 거래 중지 시 | 재무 책임자 승인 · 사유 | `vf-susp-reason` · `vf-susp-ok` |
| `started_at` (규칙) | date | 거래 시작일 | `vf-since` |
| `return_terms` (규칙) | nullable · 문자열 | 반품(반출) 조건 — 매입 유형만. 비우면 '파본 · 인쇄 불량만 반출' | `vt-ret-cond`(v6.92 추가, D-PTNR3-03) |
| 유형: `name` · `terms_form`(`purchase` 매입 · `logistics` 물류 대행 · `general` 일반) (규칙) · `evidence_type`(`tax_invoice` 전자세금계산서 · `invoice` 전자계산서) (규칙) | | 거래처 유형 | `nt-name` · `nt-form` · `nt-evidence` |

## 4. 목록 필터 · 정렬 · 표 컬럼
- 개발 매입처 탭: 필터 없음. 표(_suppliers.blade.php:8-15): 매입처(이름 + 코드) · 사업자등록번호(마스킹, `<x-masked type="business_no">`) · 과세유형 · 사업자 상태(계속사업자 / 국세청 확인 대기 / 상태 미확인) · 국세청 확인(일자 또는 "미확인 · 임시 등록") · 증빙(—) · 발주(가능 / 신규 발주 차단) · 계좌(마스킹, 사유 해제).
- 거래처 관리(규칙): `type`(규칙) · `status`(규칙) · `keyword` ↔ 프로토타입 `flt-type` · `flt-status` · `flt-keyword`. 표: 거래처 코드 · 거래처명 · 유형 · 사업자등록번호 · 사업자 상태(국세청) · 거래 조건 · 쓰는 화면 · 상태 · 관리.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| suppliers.code | string(50) unique | 매입처 코드 SUP-%04d — 스키마 주석도 %04d로 정정(`database/migrations/2026_10_27_000274_fix_suppliers_code_comment.php:22`, 컬럼 정의 불변). 채번 `SupplierService::store()` | 거래처 코드 |
| suppliers.name | string(100) | 상호 | 거래처명 |
| suppliers.business_no | string(20) null | 사업자등록번호 | 사업자등록번호 |
| suppliers.ceo_name · open_date | | 대표자 · 개업일자 | |
| suppliers.payee_tax_type | string(20) null | 국세청 과세유형 응답값 | 과세유형 |
| suppliers.business_status | string(20) null | 계속 / 휴업 / 폐업 / PENDING_VERIFICATION | 사업자 상태 |
| suppliers.api_checked_at · api_response_snapshot | | 국세청 조회 일시 · 원문 | 국세청 확인 |
| suppliers.bank_name · account_no_enc · account_holder | | 계좌(암호화) | 계좌 |
| suppliers.settlement_terms | string(100) null | 지급 조건 | 거래 조건 |
| suppliers.contact_email | string(100) null | 담당 메일 | 연락처 |
| suppliers.cost_account_type | string(30) | INVENTORY_PURCHASE 재고자산 취득 / BUYOUT_RIGHT 무형 판권 취득 | — |
| suppliers.deleted_at | timestamp nullable | SoftDeletes(모델) | — |
| books.supplier_id · goods.supplier_id | unsignedBigInteger null | 매입처 연결(AP 경로) | 쓰는 화면 |
| nts_verification_logs (subject_type=`SUPPLIER`) | | 국세청 확인 이력 | SETT-008 연동 |
| 거래처 유형 테이블 | — | 없음 — 규칙상 `vendor_types` (규칙) | `modal-type` |
| 3PL 물류 대행 거래처 | — | 없음(suppliers 는 도서 · 상품 매입처만) | 유형 "물류 대행" |

출처: dev_spec/_index/schema.md suppliers(2044-2061) · books(248) · goods(2451); app/Models/Supplier.php:21-75.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#supplierForm` (POST `admin.book-supply.suppliers.store`) | 매입처 등록 폼(탭 안 인라인) | `modal-vendor` · saveVendor |
| `[data-submit-once]` | 중복 제출 방지 | — |
| "사업자 확인" 버튼 disabled "준비 중" | 국세청 확인 | checkNts |
| `<x-masked …>` 컴포넌트 | 사업자번호 · 계좌 마스킹 | — |
| `#layerVendor` · `#vendorForm` · `#vendorSubmit` (규칙) | 거래처 등록 · 수정 모달 | `modal-vendor` |
| `#layerVendorType` · `#vendorTypeForm` (규칙) | 거래처 유형 관리 | `modal-type` |

출처: resources/views/admin/book-supply/_suppliers.blade.php:8-90.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 계좌(은행 · 계좌번호 · 예금주) 입력과 마스킹 해제 열람, 개업일자.
- 발주 가능 표시(계속사업자만 가능, 임시 등록 · 휴업 · 폐업은 신규 발주 차단).
- 원가 계정 구분(cost_account_type).
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 독립 "거래처 관리" 화면 · 거래처 유형 관리(유형 · 거래 조건 양식 · 수취 증빙) · 거래 중지(재무 책임자 승인 · 사유) · 변경 이력 표 · KPI.
- 국세청 상태조회 실행 — 개발 버튼 disabled.
- 물류 대행(3PL) 거래처 — 개발 suppliers 는 매입처만.
- 수정 — 개발 매입처는 등록만 있고 수정 라우트가 없다.
- 매입 거래 조건 '반품 조건'(`vt-ret-cond`, v6.92) — 사입 도서 반출 허용 범위. 개발 suppliers 칸 없음. **→ 결정(v6.92 white, D-PTNR3-03)**: 파본 · 인쇄 불량은 반출, 그 밖의 반품은 거래 조건에 있을 때만 허용.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `vf-name` · `vf-biz` · `vf-ceo` | `name` · `business_no` · `ceo_name` |
| `vf-tax` 직접 선택 | `payee_tax_type` 국세청 응답으로만 |
| `vf-contact` 연락처 | `contact_email` 담당 메일 |
| 거래 조건 구조화 입력(공급률 · 결제 · 반품 조건 · 건당 단가) | `settlement_terms` 문자열 한 칸 — 반품 조건 `return_terms` (규칙)는 개발 칸 없음 |
| 거래처 코드 SUP-0020 | SUP-%04d (일치) |
| 거래 중 / 거래 중지 | business_status 기반 발주 가능 / 신규 발주 차단(거래 상태 칸 없음) |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 거래처를 독립 메뉴로 둘지, 개발처럼 도서 공급 원장의 매입처 탭으로 둘지. **→ 정본대로(POLICY_D_SETT A, 03권 §16.1 L356 · 02권 §2.4 L66)**: 거래처 관리는 독립 화면 VEND-001 — 개발팀 전달
- 확인 필요: 3PL 물류 대행사를 거래처(suppliers)에 함께 둘지 — 개발 suppliers 는 매입처 전용(cost_account_type 이 재고 · 판권만). **→ 정본대로(POLICY_D_SETT A, 02권 §2.4 L66 · L67 · L69)**: 3PL도 suppliers에서 관리 — 개발 `cost_account_type`에 물류 용역 계정 추가 전달
- 확인 필요: 과세유형을 운영자가 직접 고르는 것(프로토타입) vs 국세청 응답으로만 채우는 것(개발). **→ 정본대로(POLICY_D_SETT A, 03권 §17.4 L412 · L409)**: 국세청 응답으로 자동 채움 · 편집 불가 — 개발이 맞음, 프로토 `vf-tax`를 읽기 전용으로

## 출처
- routes/admin.php:438-443
- app/Http/Controllers/Admin/SupplierController.php · BookSupplyController.php:35-51, 150
- app/Http/Requests/Admin/SupplierRequest.php (dev_spec/_index/requests.md:3416)
- app/Services/Admin/SupplierService.php:23-59 · BookSupplyService.php:97
- app/Models/Supplier.php:21-75
- resources/views/admin/book-supply/_suppliers.blade.php
- tests/Feature/Admin/QaResultAdminTest.php:108, 190 (더미 행)
