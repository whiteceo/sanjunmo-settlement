# ADMN-PTNR-002 물류 파트너 센터 — 개발 명세

> **추론 기반 신규, 정본 근거 없음.** 정본에는 거래처 소속 외부 계정의 소속 규칙과 3PL 계정의 업무 범위(출고지시 엑셀 · 송장 업로드, 금액 · 강좌내역 마스킹)만 있고, 이 화면(별도 파트너 센터) 자체의 근거는 없다. 아래 근거에서 화면 구성을 추론했다. 확인할 가정은 `dev_spec/_drafts/POLICY_D_PTNR-002.md`(9항목).

## 0. 추론 근거
### 정본 문서
| 근거 | 위치 | 이 화면에 쓴 내용 |
|---|---|---|
| 소속 3종 · 거래처 유형 · 본인 바인딩 2단 통제 | `README.md:43`(1절이 아니라 2절 5항 "국세청·전기오류수정·파트너 RBAC") | 진입 판정: 소속 = 거래처, 거래처 유형으로 구분, 메뉴 접근 + 데이터 범위 2단 |
| 화면 목록 — 거래처 관리 · 물류비 대사 · SNB 밖 파트너 전용 | `README.md:84` · `README.md:85` · `README.md:91` | PTNR-001과 같은 SNB 밖 화면 형태, VEND-001 거래처, SETT-011 물류비 |
| [S3-03] 외부 물류 계정은 타 메뉴 접근 없이 본인 배정 출고 · 송장 업무만 | `docs/산준모닷컴 구축 통합 상세 설계서.md:363-364` | 탭 범위(출고 · 송장 · 배송), 다른 메뉴 없음 |
| 3PL 계정도 출고지시 엑셀 다운로드 가능, 결제금액 · 강좌내역 마스킹 격리 | 같은 문서 `:379` | 발주 엑셀(출고지시) 버튼 · 금액 비표시 |
| 운송장 엑셀 일괄 업로드 · 배송완료(D+3) · 월말 3PL 수수료 집계 | 같은 문서 `:381-384` | 송장 등록 탭, 배송 현황, 물류비 탭 |
| 월간 정산 · 대사(SETT-011 포함)는 "내부 재무/정산 전용 — 외부 비노출" | 같은 문서 `:410` | **물류비 탭과 충돌** — 청구 쪽 결과만 보이게 줄이고 POLICY D-PTNR2-02로 확인 |
| READ_AND_APPROVE_ONLY — 외부 계정은 3PL 송장 업로드만 허용 | 같은 문서 `:454` | 쓰기 동작을 송장 · 예외 · 소명 · 명세서 제출로 한정, 마스터 수정 없음 |
| 거래처 데이터 범위: 3PL은 출고 · 반품 데이터, 결제금액 · 강좌내역 마스킹 | 같은 문서 `:461` · `:478` (OWN_SCOPE_ONLY) | 반품진행중 탭(조회만), 금액 비표시 |
| 거래처 마스터 분리(suppliers · supplier_type), 3PL 물류 용역은 과세 → 전자세금계산서 | `docs/[산준모 정산시스템]_02_…명세서.md:64-69` | 내 정보(거래처 유형 · 증빙), 세금계산서 안내 |
| 화면 대조표 VEND-001 · SETT-011, suppliers 사전, SETT-011 매칭 키 | `docs/[산준모 정산시스템]_03_…데이터사전.md:23` · `:33` · `:82` · `:355-356` | 물류비 탭 매칭 순서(송장번호 → 주문번호 → 수령인 · 출고일) |

### 프로토타입 (prototype_clean, 84c22e2 + 미커밋 작업 트리)
| 근거 | 위치 | 쓴 내용 |
|---|---|---|
| 파트너 전용 화면 레이아웃 · 클래스 · 모달 · 진입 판정 | `ADMN-PTNR-001_baseline.html:19-158`(CSS) · `:161-340`(구조) · `:620-648`(resolveContext) · `:1108-1182`(모달 닫기 핫픽스) | 그대로 복사 · 같은 패턴(`?holder=` → `?vendor=`) |
| 3PL 격리 보기(ROLE_PARTNER_3PL) · 마스킹 규칙 | `ADMN-ORD-001_baseline.html:539-540` · `:794-803` · `:1788-1822` · `:3124-3126` | 이름 두 번째 글자 · 연락처 가운데 4자리 가림, 금액 "권한제한" |
| 출고 대기 · 배송중 · 배송완료 · 반품 샘플 | `ADMN-ORD-001_baseline.html:3065-3087`(SHIP_LINES) | 샘플 13라인 그대로(주문번호 · 수령인 · 교재) |
| P1 송장 벌크 업로드 · E01~E06 · 부분 커밋 | `ADMN-ORD-001_baseline.html:1355-1530` | 사전 읽기 → 확정 2단계, 오류 코드 |
| P2 송장 단건 등록/정정 · P3 배치 이력 | `ADMN-ORD-001_baseline.html:1539-1610` · `:1622-1690` | 개별 등록 모달, 발주 · 업로드 이력 표(BATCH-20260818-01 · UPL-20260818-03) |
| 물류비 대사 2026-09 데이터 · 계약 단가 표시 | `ADMN-SETT-011_baseline.html:140-160` · `:384-420` · `:454-460` | KPI(1,842 · 1,849 · 불일치 7 · 3,698,000원) · 표본 12행 · 배송비/반품 청구 · 반품 판정 대기 3건 |
| 불일치 처리 결과(승인 지급 · 차감 · 차월 이월) | `ADMN-SETT-011_baseline.html:352-360` | 처리 결과 열(대사 확정 전 "검수 중") |
| 거래처 유형 양식 LOGISTICS · 계약 단가 · 외부 계정 연결 | `ADMN-VEND-001_baseline.html:137` · `:241` · `:263` · `:283` · `:448` | 진입 조건(form = LOGISTICS), 내 정보 거래 조건 |
| 역할 그룹 RG-08 외부 3PL(aff VENDOR, shipout RW) · 메뉴 shipout · 거래처 SUP-0020 | `common-master.js:49` · `:98` · `:148` · `:167` | 권한 판정(R · W · X), 기본 진입값 |
| 교재 출고 연동(비매품 번들은 3PL 출고만) | `ADMN-BOOK-001_baseline.html:853` | 교재 · 상품 열(상품코드 PROD-BK-1006) |

### 개발 코드 (D:\Work\sanjunmo, d562524a, 읽기 전용)
| 근거 | 위치 |
|---|---|
| 물류 역할 착지 = 내부 배송 관리 | `config/admin.php:38` (`'logistics' => 'admin.deliveries.index'`) |
| 배송 관리 라우트 묶음 | `routes/admin.php:866-889` |
| 발주 = 출고지시(POST, can_download) · 사전 읽기 · 업로드 · 단건 | `app/Http/Controllers/Admin/DeliveryController.php:74` · `:134` · `:144` · `:212` |
| 송장 업로드 검증 `file` · `batch_id` · `overwrite` · `notify` | `app/Http/Requests/Admin/DeliveryTrackingImportRequest.php:33-36` |
| 송장 단건 검증 `courier` · `tracking_no` · `shipped_at` · `reason_code` · `reason_memo` · `notify` | `app/Http/Requests/Admin/DeliveryTrackingRequest.php:34-39` |
| 택배사 코드 CJ · HANJIN · LOTTE · EPOST | `config/delivery.php:10-15` |
| 발주 엑셀 컬럼(수령인 연락처 원문 포함) · 송장 회신 필수 컬럼 · 오류 문구 · 등록 사유 | `app/Services/Admin/DeliveryService.php:53` · `:56` · `:66-71` · `:102` |
| 배송 상태 코드 · 라벨, 배송비 구분 | `app/Models/Delivery.php:28-48` · `:56-60` |
| 사유 입력 규칙 | `app/Http/Requests/Admin/MemberReasonRequest.php` |
| 접미사 → 권한(fail-closed) | `app/Services/Admin/AdminPermissionService.php:261` · `:301` |
| 테이블 deliveries · delivery_batches · logistics_settlements · suppliers | `database/migrations/2026_06_25_000003_create_remaining_tables.php:170` · `2026_08_14_000012_…` · `2026_08_14_000015_…` · `2026_09_18_000126_…` |

---

- 프로토타입 파일: prototype_dev/ADMN-PTNR-002_baseline.html (원본 없음 — prototype_clean에 대응 파일이 없는 신규. 디자인 원본은 prototype_clean/ADMN-PTNR-001_baseline.html, 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-PTNR-002(홈 · 출고 대상 · 송장 등록 · 배송 현황/예외 · 물류비 청구/대사 결과 · 내 정보) + 레이어 5개(`layerDispatch` · `layerImportResult` · `layerTracking` · `layerDeliveryException` · `layerBillObjection`)
- 개발 진행: **미구현(규칙 기반 명명).** 개발 진행표(`_index/progress.md`)에 화면 코드 없음. 개발에는 내부 배송 관리(`admin.deliveries.*`, ADMN-ORD-002)와 물류 역할 착지만 있고, 거래처 소속 계정 · 데이터 범위 바인딩이 없다.

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.partner.deliveries.index` (규칙) | 출고 대상 · 송장 등록 · 배송 현황 | 개발 미구현. 프로토타입 메뉴 키 `shipout`(R 조회 · W 등록 · X 다운로드)에 대응 |
| `admin.partner.logistics-bills.index` (규칙) | 물류비 청구 · 대사 결과 | 개발 미구현. 프로토타입은 별도 메뉴 키 없이 `shipout` R로 노출(가정 — POLICY D-PTNR2-02) |
| (메뉴 아님) `admin.partner.profile.show` (규칙) | 내 정보 | 로그인 계정 공통 |

- 진입: 로그인 후 역할 그룹 시작 화면(`startScreen`)으로 착지. 프로토타입 URL `ADMN-PTNR-002_baseline.html?vendor=SUP-NNNN&role=RG-08`. 개발은 `config/admin.php` landing에 거래처 소속 역할 코드(예 `vendor_logistics` (규칙))를 추가해 `admin.partner.deliveries.index`로 보낸다.
- 진입 차단(프로토타입 `resolveContext()`): 거래처 없음 · 거래처 유형 양식이 LOGISTICS가 아님 · 거래 중지(`on=false`) · 역할 그룹이 EXTERNAL + aff VENDOR가 아님 · `shipout` R 없음.
- 데이터 범위(본인 바인딩): 모든 조회 · 쓰기는 로그인 계정의 `supplier_id`(규칙)로 거른다. 이 거래처에 배정된 출고(`deliveries.supplier_id` (규칙) 또는 발주 배치의 거래처)만.
- 현재 RG-08 최초값은 `shipout: "RW"` — X(다운로드)가 없어 발주 엑셀(출고지시) 버튼은 비활성 + 안내. 정본 `:379`는 3PL 계정의 출고지시를 허용 → POLICY D-PTNR2-04.

## 2. 화면별 라우트
개발 미구현, 규칙 기반 명명. URL 접두사 `/{admin}/partner/…`. 동작은 기존 `admin.deliveries.*`와 같은 컨트롤러 메서드 모양을 따르되 데이터 범위만 거래처로 묶는다(재사용 대안은 7절).

### ADMN-PTNR-002 출고 대상 · 송장 · 배송 현황
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(탭 ready · shipping · delivered · return, 검색) | GET | `/{admin}/partner/deliveries` | `admin.partner.deliveries.index` (규칙) | can_view | (규칙) Partner\DeliveryController@index ← `DeliveryController@index` 모양 |
| 발주 엑셀 = 출고지시(`layerDispatch`) | POST | `/{admin}/partner/deliveries/dispatch` | `admin.partner.deliveries.dispatch.download` (규칙) | can_download | (규칙) @storeDispatch |
| 발주 파일 재다운로드 | GET | `/{admin}/partner/deliveries/batches/{batch}/download` | `admin.partner.deliveries.batches.download` (규칙) | can_download | (규칙) @downloadBatch |
| 발주 · 업로드 이력 | GET | `/{admin}/partner/deliveries/batches` | `admin.partner.deliveries.batches.index` (규칙) | can_view | (규칙) @batches |
| 송장 표준 양식 | GET | `/{admin}/partner/deliveries/tracking/template/download` | `admin.partner.deliveries.template.download` (규칙) | can_download | (규칙) @downloadTemplate |
| 송장 파일 사전 읽기(저장 안 함) | POST | `/{admin}/partner/deliveries/tracking/preview` | `admin.partner.deliveries.tracking.preview.store` (규칙) | can_create | (규칙) @previewTracking |
| 송장 업로드 확정(`layerImportResult`) | POST | `/{admin}/partner/deliveries/tracking` | `admin.partner.deliveries.tracking.store` (규칙) | can_create | (규칙) @storeTracking |
| 실패 목록 엑셀 | GET | `/{admin}/partner/deliveries/tracking/{batch}/failures/download` | `admin.partner.deliveries.failures.download` (규칙) | can_download | (규칙) @downloadFailures |
| 송장 개별 등록 · 정정(`layerTracking`) | PUT | `/{admin}/partner/deliveries/{delivery}/tracking` | `admin.partner.deliveries.tracking.update` (규칙) | can_update | (규칙) @updateTracking |
| 배송 예외 등록(`layerDeliveryException`) | POST | `/{admin}/partner/deliveries/{delivery}/exceptions` | `admin.partner.deliveries.exceptions.store` (규칙) | can_create | (규칙) @storeException — **개발에 대응 없음** |

### ADMN-PTNR-002 물류비 청구 · 대사 결과
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 월별 대사 결과(청구 쪽) | GET | `/{admin}/partner/logistics-bills?settlement_month=YYYY-MM` | `admin.partner.logistics-bills.index` (규칙) | can_view | (규칙) Partner\LogisticsBillController@index |
| 월 수수료 명세서 제출 | POST | `/{admin}/partner/logistics-bills/statements` | `admin.partner.logistics-bills.statements.store` (규칙) | can_create | (규칙) — 내부 SETT-011 `…logistics-reconciliations.statements.store` (규칙)와 같은 저장소 |
| 불일치 소명 제출(`layerBillObjection`) | POST | `/{admin}/partner/logistics-bills/items/{item}/objections` | `admin.partner.logistics-bills.items.objections.store` (규칙) | can_create | (규칙) |

### 내 정보 · 공통
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 내 정보(읽기 전용) | GET | `/{admin}/partner/profile` | `admin.partner.profile.show` (규칙) | 로그인만 | (규칙) |
| 로그아웃 | POST | `/{admin}/logout` | `admin.logout` | 로그인만 | AuthController@logout |

## 3. 폼 필드 · 검증
### 출고 대상 검색 (index 쿼리)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `tab` | 기본 `ready` | `ready` 출고 대기 · `shipping` 배송중 · `delivered` 배송완료 · `return` 반품진행중 (`DeliveryService::TAB_SHORT`) | 메뉴 · 상태 칩 |
| `lock` (규칙) | 선택 | `before` 출고지시 전 · `locked` 출고지시 완료 | `#readyLockFilter` |
| `search_type` | `order_no` · `receiver` (외부 계정은 `phone` · `tracking` 검색 제외 — 가린 값으로 역추적 방지) | `DeliveryService::SEARCH_TYPES` 일부 | `#readyKeyType` |
| `keyword` (규칙 — 개발 실제 이름은 index 필터 확인 필요) | 수령인명은 완전 일치만 | | `#readyKeyword` |

### 발주 = 출고지시 (개발 storeDispatch — Request 클래스 없음)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `ids[]` | 필수 · 이 거래처 배정 · `ship_ordered_at` NULL 라인만 | | `.ready-cb` · `#dispatchIds` |

### 송장 업로드 (DeliveryTrackingImportRequest 재사용)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `file` | required · file · mimes:xlsx · max 10240KB | 필수 컬럼 주문번호 · 주문라인번호 · 택배사코드 · 운송장번호 · 출고일자 | `#importFile` |
| `batch_id` | nullable · integer — 외부 계정은 자기 거래처 배치만 | | `#importBatch` |
| `overwrite` | nullable · boolean | | `#importOverwrite` |
| `notify` | nullable · boolean | | `#importNotify` |
| 행 결과 | E01~E06 (`DeliveryService::ERROR_MESSAGES`) | E01 주문번호 불일치 · E02 이미 처리됨 · E03 필수값 누락 · E04 형식 오류 · E05 상태 불일치 · E06 운송장 중복 | `#importResultTable` |

### 송장 개별 등록 · 정정 (DeliveryTrackingRequest 재사용)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `courier` | required · in config('delivery.couriers') | `CJ` CJ대한통운 · `HANJIN` 한진택배 · `LOTTE` 롯데택배 · `EPOST` 우체국택배 | `#trackingCourier` |
| `tracking_no` | required · `^\d{10,14}$` · 중복 시 E06 | | `#trackingNo` |
| `shipped_at` | required · Y-m-d · before_or_equal:today | | `#trackingShippedAt` |
| `reason_code` | required · in TRACKING_REASONS | `missing` 3PL 회신 누락 · `typo` 운송장 오타 정정 · `courier` 택배사 변경 · `etc` 기타 | `#trackingReason` |
| `reason_memo` | nullable · max 200 · `etc`면 필수 | | `#trackingMemo` |
| `notify` | nullable · boolean | | `#trackingNotify` |

### 배송 예외 등록 (규칙 — DeliveryExceptionRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `exception_type` | required · in | `return_to_sender` 반송 · `lost` 분실 · `damaged` 파손 (규칙) | `#exceptionType` |
| `occurred_at` | required · Y-m-d · before_or_equal:today | | `#exceptionOccurredAt` |
| `reason` | MemberReasonRequest 규칙(공백 제외 10자 이상 · 서로 다른 글자 3개 이상 · 200자 이하) | | `#exceptionReason` |
| `attachment` | nullable · image/pdf | | `#exceptionFile` |
- 같은 라인에 처리 중 예외가 있으면 등록 거부.

### 월 명세서 제출 · 소명 (규칙)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `settlement_month` | char(7) YYYY-MM | | `#billMonth` |
| `file` (명세서) | required · mimes:xlsx | | `#billStatementFile` |
| `reason` (소명) | MemberReasonRequest 규칙 | | `#objectionReason` |
| `attachment` (소명) | nullable | | `#objectionFile` |
- 소명은 대사 결과가 `ONLY_3PL` · `DIFF`이고 대사 완료(Lock) 전인 행만.

## 4. 목록 필터 · 정렬 · 표 컬럼
| 탭 | 컬럼 | 비고 |
|---|---|---|
| 출고 대상 | 선택 · 주문번호 #라인 · 수령인(가림) · 연락처(가림) · 배송지 · 교재 · 상품(상품코드) · 수량 · 배송비 구분(`fee_type` 라벨만) · 출고지시(시각 · 배치) · 송장 | 결제금액 · 배송비 금액 · 강좌 라인 비표시. 출고지시 완료 라인은 선택 불가 |
| 배송중 | 주문번호 · 수령인 · 연락처 · 배송지 · 교재 · 수량 · 출고일 · 택배사/운송장(정정 n · 예외 배지) · 관리(정정 · 예외 등록) | |
| 배송완료 | 주문번호 · 수령인(가림) · 교재 · 수량 · 출고일 · 배송완료일 · 완료 근거 · 운송장 · 예외 등록 | **연락처 · 주소 비표시**(가정 — D-PTNR2-03) |
| 반품진행중 | 주문번호 · 수령인(가림) · 반품 교재 · 수량 · 수거 운송장 · 창고 입고일 · 검수 상태 | 조회만(검수 입력은 운영자 — D-PTNR2-06) |
| 예외 | 주문번호 · 구분 · 발생일 · 내용 · 등록 · 처리 상태 | |
| 물류비 대사 | No · 출고일 · 송장번호 · 주문번호 · 수령인(가림) · 수량 · 산준모 기록 · 청구 · 단가 · 대사 결과 · 처리 결과 · 소명 | 불일치만 보기 토글. 고객 배송비 수납액 · 도서 매입 대조 탭은 비표시 |
| 배송비 · 반품 청구 | 구분 · 청구 금액 · 산정 | 지급(청구) 쪽만 |
- 정렬: 개발 `DeliveryService::TAB_SORTS` 그대로(탭별 기본값).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `deliveries.status` | string(30) | READY · SHIPPING · DELIVERED · RETURNING · REFUNDED · REJECTED | 탭 · 상태 칩 |
| `deliveries.receiver_name` · `receiver_phone` · `address` · `address_detail` · `zipcode` · `delivery_request` | | 수령인 · 배송지 | 출고 대상 · 배송중(이름 · 연락처 가림) |
| `deliveries.ship_ordered_at` · `batch_id` | timestamp · bigint | 출고지시 시각 · 발주 배치 | 출고지시 열 |
| `deliveries.courier` · `tracking_no` · `shipped_at` · `delivered_at` | | 운송장 · 출고 · 배송완료 | 송장 · 배송 현황 |
| `deliveries.fee_type` | string(20) | FREE · PREPAID · ISLAND | 배송비 구분(라벨만) |
| `delivery_batches.*` (`batch_no` · `type` export/import · `total_count` · `success_count` · `fail_count` · `admin_id`) | | 발주 · 업로드 이력 | 발주 · 업로드 이력 표 |
| `logistics_settlements.*` (`settlement_month` · `billed_delivery_count/amount` · `billed_return_count/amount` · `our_delivery_count` · `status` · `is_locked`) | | 월 물류 정산 요약 | 물류비 KPI(`our_*`는 "산준모 출고 기록" 건수만) |
| `suppliers.code` · `name` · `business_no` · `ceo_name` · `payee_tax_type` · `business_status` · `api_checked_at` · `bank_name` · `account_no_enc` · `account_holder` · `settlement_terms` · `contact_email` | | 거래처 원장 | 내 정보(계좌는 가린 값) |
| `suppliers.supplier_type` (규칙) | string | 거래처 유형 — 정본 02권 2.4절에 있으나 개발 테이블에 없음 | 진입 판정(LOGISTICS) |
| `users.supplier_id` (규칙) | unsignedBigInteger nullable | 계정 소속 거래처(본인 바인딩 키) | 진입 · 모든 조회 범위 |
| `deliveries.supplier_id` (규칙) 또는 `delivery_batches.supplier_id` (규칙) | | 출고 배정 거래처(3PL이 여럿일 때) | 데이터 범위 |
| `delivery_exceptions` (규칙: `delivery_id` · `supplier_id` · `exception_type` · `occurred_at` · `reason` · `attachment_path` · `status` · `created_by` · `resolved_by` · `resolved_at`) | | 배송 예외 | 예외 탭 |
| `logistics_statement_files` · `logistics_reconciliation_items` · `logistics_item_objections` (규칙) | | 명세서 원본 · 대사 행 · 소명 | 물류비 탭 — SETT-011 명세와 같은 저장소 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `dispatchButton` · `layerDispatch` · `dispatchForm` · `dispatchCount` · `dispatchConfirm` | 발주 = 출고지시 (ORD-001 명세와 같은 이름) | 같은 id 사용 |
| `importForm` · `importFile` · `importPreview` · `layerImportResult` · `importSubmit` (규칙) | 송장 업로드 | 같은 id 사용 |
| `layerTracking` · `trackingForm` · `trackingSubmit` | 송장 단건 | 같은 id 사용 |
| `layerDeliveryException` · `deliveryExceptionForm` · `deliveryExceptionSubmit` (규칙) | 배송 예외 | 같은 id 사용 |
| `layerBillObjection` · `billObjectionForm` · `billObjectionSubmit` (규칙) | 소명 제출 | 같은 id 사용 |
| `billStatementForm` · `billStatementSubmit` (규칙) | 명세서 제출 | 같은 id 사용 |
- 화면 디자인 클래스는 PTNR-001(`ptnr-*`) 그대로. 개발 공통 레이어 마크업(`.layer-pop__overlay` 등)으로 옮길 때 id만 유지.
- 모든 동작 버튼에 `data-dev-route` · `data-dev-method` · `data-dev-url` · `data-dev-perm`, 주요 영역에 `data-dev-flag="proto-only"`(화면 전체 개발 미구현).

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 없음(개발에 거래처 계정 화면이 없음). 내부 배송 관리의 배송완료일 보정(`admin.deliveries.delivered.update`)은 운영자 기능이라 넣지 않음.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 화면 전체: 거래처 소속 계정 · 본인 바인딩(`users.supplier_id`), 거래처 유형(`suppliers.supplier_type`), 파트너 라우트 묶음.
- 배송 예외 등록(반송 · 분실 · 파손) — 개발 테이블 없음.
- 물류비 대사 결과 조회 · 명세서 제출 · 소명 — 내부 SETT-011도 개발 미구현(테이블만).
- 화면 표시 마스킹(이름 · 연락처) — 개발 내부 배송 관리는 원문 표시.

### 이름 · 값이 다름 / 설계 대안
- 대안 A(권장 검토): 별도 `admin.partner.deliveries.*` 대신 기존 `admin.deliveries.*`를 그대로 쓰고, 거래처 소속 계정이면 서비스 계층에서 범위 · 마스킹 · 버튼을 줄인다. 라우트 수가 줄지만 메뉴 권한이 내부 물류팀과 한 행을 공유한다 → POLICY D-PTNR2-01.
- 진입 파라미터: 요청서의 `?vendor=VD-NNNN` 대신 기존 거래처 코드 `SUP-NNNN`(공통 기준정보 · 개발 `suppliers.code`)을 썼다.
- 마스킹 위치: 프로토타입 공통(ORD-001)은 이름 두 번째 글자 · 연락처 가운데 4자리. 개인정보위 운송장 권고(2025-09)는 이름 가운데 글자 · 연락처 끝 4자리 → D-PTNR2-03.

## 8. 정책 질문 (white 확인 필요 — 상세는 `_drafts/POLICY_D_PTNR-002.md`)
| 번호 | 질문 | 긴급도 |
|---|---|---|
| D-PTNR2-01 | 3PL 업무를 별도 파트너 센터로 둘지, 정본대로 ORD-002 격리 보기로 둘지 | 상 |
| D-PTNR2-02 | 물류비 대사 결과를 3PL에게 보여 줄지(정본 "외부 비노출"과 충돌) · 범위 | 상 |
| D-PTNR2-03 | 3PL에게 주는 개인정보 범위 · 마스킹 방식 · 처리위탁 계약 | 상 |
| D-PTNR2-04 | 3PL 계정의 출고지시(발주 엑셀) 실행 권한 | 중 |
| D-PTNR2-05 | 배송 예외(반송 · 분실 · 파손) 등록 · 후속 처리 책임 | 중 |
| D-PTNR2-06 | 반품 입고 검수 입력을 3PL에 열지 | 중 |
| D-PTNR2-07 | 월 명세서를 3PL이 직접 제출 · 소명하는 경로 | 중 |
| D-PTNR2-08 | 3PL이 여럿일 때 출고 배정 기준 | 하 |
| D-PTNR2-09 | 거래처 계정 발급 · 담당자 단위 · 해지 시 회수 | 하 |
