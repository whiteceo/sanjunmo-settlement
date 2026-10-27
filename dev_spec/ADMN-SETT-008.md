# ADMN-SETT-008 사업자등록 확인 이력 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-008_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-008 (프로토타입 모달 `modal-tax-transition` → 개발 모달 `#layerNtsReview`)
- 개발 진행: 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 5건). 전환 승인은 권리자 건만(위탁자 · 매입처는 2차) — v6.92 D-SETT-04로 위탁자는 1차에 넣어야 함(8절)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.nts.index` | 사업자등록 확인 이력 | 라우트 정규화 규칙. 운영 DB 행 미확인 |

- 개별 진위 확인 실행은 이 화면이 아니라 권리자 원장의 `admin.rights-holders.nts-verify`(POST `/{admin}/rights-holders/{rightsHolder}/nts-verify`, 접미사 nts-verify → can_update, 메뉴는 권리자 원장)이다(routes/admin.php:519).

## 2. 화면별 라우트
### ADMN-SETT-008 사업자등록 확인 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(탭 · 필터 · KPI) | GET | `/{admin}/settlement/nts` | `admin.settlement.nts.index` | can_view | NtsVerificationController@index |
| 과세유형 전환 승인 · 보류 | PUT | `/{admin}/settlement/nts/tax-type` | `admin.settlement.nts.update` | can_update | NtsVerificationController@update |

- 승인 후에는 `tab=history` 로 돌아가며 나머지 조건(subject_type · trigger_type · review · keyword · page)을 유지한다.
- 정기 일괄 조회 · 재시도 큐 즉시 재호출 라우트는 없다(배치 · 스케줄러, 추정).

| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 매입처 전환 감지 — 매입 증빙 수기 확인 기록(v6.92, D-SETT-04) | POST | `/{admin}/settlement/nts/supplier-checks` (규칙) | `admin.settlement.nts.supplier-checks.store` (규칙) | can_update | 개발 미구현 — `recordSupplierManualCheck()` · `#btnSupplierManualCheck`(확인자 · 시각만 기록, 원장 행 안 바꿈, 입력 필드 없음 — `log_id`만) |

## 3. 폼 필드 · 검증
### 전환 승인 · 보류 (NtsTaxTypeReviewRequest) — `#ntsReviewForm`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `log_id` | required · integer | nts_verification_logs.id (`#ntsReviewLogId`) | 선택 행(selectRecord) |
| `explanation` | required · 20~2000 (trim) | 소명 내용 (`#ntsReviewExplanation`, 글자 수 `#ntsReviewCount`) | 프로토타입 모달에 소명 입력 없음 |
| `hold` | nullable · boolean (`#ntsReviewHold`) | 1=보류(원장 미변경 · 마감 보류 유지) / 0=승인 | "✔ 정산 기준 행 분할 승인" 만 있음 |
| (목록 조건 hidden) | tab · subject_type · trigger_type · review · keyword · page | | |

### 개별 진위 확인 (NtsVerifyRequest — 권리자 원장에서 사용, 참고)
| 필드 name | 규칙 | 뜻 |
|---|---|---|
| `business_number` | required · digits:10 (공백 · 하이픈 제거) | 사업자등록번호 |
| `ceo_name` | required · ≤50 | 대표자명 |
| `open_date` | required · date | 개업일 |
| `return_contract_id` | nullable · integer | 계약 상세에서 실행했을 때 복귀 |

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `tab` | `history`(1. 확인 이력 · 전환 승인) · `mapping`(2. 과세유형 코드 매핑) · `params`(3. 호출 파라미터 · 재시도) | tabHistory · tabMapping · tabRetry |
| `subject_type` | `RIGHTS_HOLDER` 권리자(강사 · 저자) · `CONSIGNOR` 위탁자(위탁 도서 출판사) · `SUPPLIER` 매입처(사입 도서 총판) | `partnerTypeFilter` |
| `trigger_type` | `CONTRACT_REG` 계약 등록 · `PERIODIC` 정기 · `AD_HOC` 수시 · `MILESTONE_APPROVAL` 약정금 승인 · `PURCHASE_ORDER` 발주 · `CONSIGNMENT_REG` 위탁 등록 | `triggerFilter` |
| `review` | `unreviewed` 미확인 · `approved` 승인 · `held` 보류 (change_review_status) | 없음(KPI 클릭) |
| `keyword` | b_no · rights_holders.name LIKE | `searchInput` |

- 대상별 최신 조회 1건만 보인다(`latestPerSubject`).
- KPI(index.blade.php:54-58): 전체 조회 대상 거래처 · 과세유형 전환 감지(승인 대기, 클릭 시 `review=unreviewed`) · 폐업 · 휴업 감지 · 세무 판정 보류 격리 · 계속사업자 · 유효기간 정상.
- 이력 표(154-160): 거래처 구분 / 명칭 · 사업자등록번호 · 납세자 상태 · 원장 과세유형 → API 응답 · 매트릭스 케이스 · 전환 효력일 / 폐업일 · 통제 상태(+[승인 검토] 모달 버튼).
- 매핑 표(240-244): 국세청 코드 · 국세청 과세유형 명칭 · 수취인 과세유형 · 세금계산서 발급 · 연결 매트릭스 케이스.
- 파라미터 표(288): 파라미터 명칭 · 시스템 코드 · 설정 기준값 · 운영 통제 규칙 — 코드 `nts_check_validity_days` · `nts.chunk_size` · `nts.batch_interval_ms` · `nts.retry_times` · `nts_periodic_check_schedule`(app/Services/Admin/NtsVerificationScreenService.php:230-257).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| nts_verification_logs.subject_type · subject_id | | RIGHTS_HOLDER / CONSIGNOR / SUPPLIER + rights_holders.id 또는 suppliers.id | 거래처 구분 / 명칭 |
| nts_verification_logs.contract_id | | 계약 등록 시점 조회 | |
| nts_verification_logs.api_type | string(10) | VALIDATE 진위확인 · STATUS 상태조회 | |
| nts_verification_logs.b_no | string(20) | 사업자등록번호 10자리 | 사업자등록번호 |
| nts_verification_logs.b_stt | string(20) | 계속사업자 / 휴업자 / 폐업자 | 납세자 상태 |
| nts_verification_logs.tax_type · tax_type_cd · tax_type_change_dt · invoice_apply_dt · end_dt | | 과세유형 응답 · 코드 · 전환일 · 세금계산서 적용일 · 폐업일 | 원장 → API · 전환 효력일 / 폐업일 |
| nts_verification_logs.match_result | string(20) | match 일치 · mismatch 불일치 · not_found 확인 불가 | |
| nts_verification_logs.trigger_type | string(24) | 4절 6종 | 트리거 |
| nts_verification_logs.change_review_status | string(20) | unreviewed · approved · held | 통제 상태 |
| nts_verification_logs.error_code · retry_count · queue_status(queued · retrying · resolved · abandoned) | | 재시도 큐 | 파라미터 · 재시도 탭 |
| nts_verification_logs.request_payload · response_payload · checked_at · checked_by | | 원문 · 조회 일시 · 조회자(배치 NULL) | |
| rights_holders.tax_type 등 | tax_type varchar(20) NOT NULL(personal · simplified · general · exempt) · open_date date nullable(국세청 start_dt, 2026_10_15_000207) | 승인 시 원장 갱신 · 마감 보류 해제 | |
| settlement_lines.payout_hold_reason = `NTS_EXPIRED` | | 사업자 확인 90일 경과 보류 | SETT-002 |

출처: dev_spec/_index/schema.md nts_verification_logs(2361-2384); app/Models/NtsVerificationLog.php:25-88.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `.tab__list .tab__item.active` `?tab=` | 탭 3종 | tabHistory 등 |
| `#searchForm`(hidden `tab`) | 필터 | searchInput · partnerTypeFilter · triggerFilter |
| `.layer__open[data-target="layerNtsReview"][data-log-id][data-subject][data-tax-type]` | 승인 검토 열기 | approveTaxTypeChange |
| `#layerNtsReview` · `#ntsReviewForm` · `#ntsReviewLogId` · `#ntsReviewHold` · `#ntsReviewSubject` · `#ntsReviewTaxType` · `#ntsReviewExplanation` · `#ntsReviewCount` · `#ntsReviewHoldBtn` · `#ntsReviewApproveBtn` | 전환 승인 · 보류 모달 | `modal-tax-transition` · confirmTaxTypeTransition |

출처: resources/views/admin/settlement/nts/index.blade.php:43-378.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 보류(`hold`) 선택과 소명(20자 이상) 입력.
- `review` 필터(미확인 · 승인 · 보류), KPI 5종.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- "🔄 정기 일괄 상태조회 실행", "⚡ 실패 재시도 큐 즉시 재호출" 버튼.
- 우측 상세 패널(renderDetail · 폐업 관계 표 closureTableHtml) · 버전 분할 표(버전 구분 · 유효 기간 · 원장 상태).
- 사업자번호 · 법인번호 마스킹 표시 함수(maskBizNo · maskCorpNo) — 개발 마스킹 적용 여부 미확인.
- 매입처 전환 감지 패널(`#supplierChangePanel`) · 수기 확인 기록(v6.92) — 개발 미구현(위 2절 규칙 이름)
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `searchInput` | `keyword` |
| `partnerTypeFilter` 권리자 · 위탁자 · 매입처 | `subject_type` RIGHTS_HOLDER · CONSIGNOR · SUPPLIER |
| `triggerFilter` 정기 재조회 · 계약 등록 · 갱신 시 · 정산 마감 전 90일 | `trigger_type` PERIODIC · CONTRACT_REG · AD_HOC · MILESTONE_APPROVAL · PURCHASE_ORDER · CONSIGNMENT_REG |
| 탭 3 "네트워크 장애 재시도 큐 및 배치 스케줄 파라미터" | `tab=params` "호출 파라미터 · 재시도" |
| `modal-tax-transition` | `#layerNtsReview` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 프로토타입 트리거 "정산 마감 전 90일"은 개발 trigger_type 에 대응 값이 없다(가까운 값 PERIODIC · MILESTONE_APPROVAL). 반대로 PURCHASE_ORDER · CONSIGNMENT_REG 는 프로토타입에 없다.
- 확인 필요: 위탁자 · 매입처 전환 승인은 개발 1차 범위 밖(서비스 문구 "2차") — 프로토타입 표시 여부. **→ 결정(v6.92 white, D-SETT-04)**: 전환 승인은 권리자 + 위탁자까지 1차(개발 범위 넓힘 필요), 매입처는 1차 감지 · 수기 확인 기록만(원장 미변경, 승인 2차) · 매입처 감지 건은 SETT-002 마감 차단에서 뺌

## 출처
- routes/admin.php:519, 637-639
- app/Http/Controllers/Admin/NtsVerificationController.php
- app/Http/Requests/Admin/NtsTaxTypeReviewRequest.php · NtsVerifyRequest.php
- app/Services/Admin/NtsVerificationScreenService.php:46-95, 230-257
- app/Repositories/Nts/NtsVerificationLogRepository.php:110-128
- app/Models/NtsVerificationLog.php:25-88
- resources/views/admin/settlement/nts/index.blade.php
