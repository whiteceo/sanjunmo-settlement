# ADMN-INST-001 권리자 계약 원장 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-INST-001_baseline.html` (원본 상태: `84c22e2` + **미커밋 작업 트리**(3,909줄, 다른 세션 수정 중). 아래 프로토 줄 번호는 2026-10-27 작업 트리 기준 — 통합 커밋 후 다시 맞춘다)
- 맞춘 개발 커밋: `a8016168` (2026-10-27) — 이 화면 변경은 `e555839b`(선택지 라벨 5건을 프로토 문구로 · 목록 배열 쿼리 차단)
- 포함 화면: INST-001 탭 1 권리자 계약 목록 · 탭 2 계약 상세 조건 편집(권리자 · 세무 정보 = INST-001-S1, 계약 조건 = INST-001-S2) · 탭 3 국세청 확인 이력 · 탭 4 변경 · 열람 이력 · INST-001-P1 요율 잠금 · 상태 동기화 안내 · INST-001-P2 검증 상세 · 조항별 입력 모달(요율 · 도서 · 매핑 · 회차 · 수당 · 선급 · 수취인 · 증빙 · 진위 확인 등)
- 개발 진행: 구현(권리자 목록 · 등록 · 수정 · 국세청 진위 확인 · 계약 등록/수정/열람 · 메모 · 교재 인세 저서 원장 · 선급 원장 라인 · 상태 동기화 · 엑셀). 탭 4 변경 · 열람 이력 전용 화면은 미구현. 위탁 조항 · 환급 부담 B · C는 1차 저장 거부. `_index/progress.md` INST-001 커밋 29건 · 라우트 주석 있음

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 탭 1 `page-list` 계약 목록(행 = 계약) | INST-001 권리자 목록(행 = 권리자, 계약 이력 레이어) | `resources/views/admin/rights-holders/index.blade.php` (`#layerContractHistory` · `#layerNewContract`) |
| 탭 2 권리자 · 세무 영역(`bizType` ~ `taxDecisionReason`) | INST-001-S1 권리자 등록 · 수정 | `rights-holders/create.blade.php` · `edit.blade.php` + `form.blade.php` |
| 탭 2 계약 조건 영역(`contractStart` ~ 조항 카드 · 증빙 · 메모) | INST-001-S2 계약 상세 | `rights-holders/contracts/create · edit.blade.php` + `form.blade.php` + `_term-*.blade.php` |
| 탭 3 `page-nts` 국세청 확인 이력 | S1 수정 화면 `?tab=nts` | `rights-holders/_nts-history.blade.php` |
| 탭 4 `page-audit` 변경 · 열람 이력 | 없음(공통 관리 로그) | — |
| P1 요율 잠금 안내(`openInst001RateLockModalP1`) · 상태 변경 모달 | `#layerContractLock` · `#layerContractStatus` | `contracts/_lock-modal.blade.php` · `_status-modal.blade.php` |
| P2 검증 상세(`validationModal`) | `#layerInstValidation` | `contracts/_savebar.blade.php` |
| 증빙 모달(`evidenceModal`) | `#evidenceModal` | `contracts/_evidence-modal.blade.php` |
| 수취인 연결 · 신규 수취인(`payeeLinkModal` · `payeeNewModal` · `splitModal`) | 수취인 분할(SETT-007) | `PayeeSplitController`(SETT-007 명세 참고) |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.rights-holders.index` | 권리자 계약 원장(라우트 주석 `routes/admin.php:488`) | 탭 1~4 · P1 · P2 · 조항 모달 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 계약 상세 라우트는 상위 메뉴(권리자 계약 원장) 권한을 따른다(`routes/admin.php:501`).
- 계약 열람(`contracts.show`)은 조회 권한, 편집(`contracts.edit`)은 수정 권한(`routes/admin.php:505-507`). 프로토의 `#role` 계약 운영자 · 재무 책임자 시연(L289)은 개발에서 메뉴 권한 + 재무 판정으로 갈린다.
- `nts-verify` · `status-sync`는 접미사 예외로 수정 권한.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{rightsHolder}` = `rights_holders.id`, `{contract}` = `rights_holder_contracts.id`.

### INST-001 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 | GET | `/rights-holders` | `admin.rights-holders.index` | 조회 | RightsHolderController@index |
| 엑셀(사유) | GET | `/rights-holders/download` | `admin.rights-holders.download` | 다운로드 | RightsHolderController@download |
| 계약 상태 일괄 동기화(만료 반영) | POST | `/rights-holders/status-sync` | `admin.rights-holders.status-sync` | 수정 | RightsHolderController@statusSync |
| 권리자별 계약 이력(JSON, 레이어) | GET | `/rights-holders/{rightsHolder}/contracts` | `admin.rights-holders.contracts` | 조회 | RightsHolderController@contracts |

### INST-001-S1 권리자 · 세무 (프로토 탭 2 상단)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/rights-holders/create` | `admin.rights-holders.create` | 등록 | RightsHolderController@create |
| 등록 | POST | `/rights-holders` | `admin.rights-holders.store` | 등록 | RightsHolderController@store |
| 수정 폼(`?tab=holder\|nts`) | GET | `/rights-holders/{rightsHolder}/edit` | `admin.rights-holders.edit` | 수정 | RightsHolderController@edit |
| 수정 | PUT | `/rights-holders/{rightsHolder}` | `admin.rights-holders.update` | 수정 | RightsHolderController@update |
| 국세청 진위 확인 | POST | `/rights-holders/{rightsHolder}/nts-verify` | `admin.rights-holders.nts-verify` | 수정 | RightsHolderController@ntsVerify |
| 삭제 | — | — | 없음(계약 원장 보존, `routes/admin.php:523`) | | |

### INST-001-S2 계약 상세 (프로토 탭 2 하단)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 계약 등록 폼 | GET | `/rights-holders/{rightsHolder}/contracts/create` | `admin.rights-holders.contracts.create` | 등록 | RightsHolderContractController@create |
| 계약 등록 | POST | `/rights-holders/{rightsHolder}/contracts` | `admin.rights-holders.contracts.store` | 등록 | RightsHolderContractController@store |
| 계약 편집 폼 | GET | `/rights-holders/{rightsHolder}/contracts/{contract}/edit` | `admin.rights-holders.contracts.edit` | 수정 | RightsHolderContractController@edit |
| 계약 열람(읽기 전용) | GET | `/rights-holders/{rightsHolder}/contracts/{contract}` | `admin.rights-holders.contracts.show` | 조회 | RightsHolderContractController@show |
| 계약 저장 | PUT | `/rights-holders/{rightsHolder}/contracts/{contract}` | `admin.rights-holders.contracts.update` | 수정 | RightsHolderContractController@update |
| 메모 등록 | POST | `…/contracts/{contract}/memos` | `admin.rights-holders.contracts.memos.store` | 등록 | RightsHolderContractController@storeMemo |
| 교재 인세 저서 등록(가채번 포함) | POST | `…/contracts/{contract}/book-royalties` | `admin.rights-holders.contracts.book-royalties.store` | 등록 | RightsHolderContractController@storeBookRoyalty |
| 저서 수정 · 삭제 | PUT · DELETE | `…/book-royalties/{bookRoyalty}` | `admin.rights-holders.contracts.book-royalties.update` · `.destroy` | 수정 · 삭제 | RightsHolderContractController@updateBookRoyalty · destroyBookRoyalty |
| 선급 원장 라인 추가 · 수정 | POST · PUT | `…/contracts/{contract}/prepayment-lines[/{prepaymentLine}]` | `admin.rights-holders.contracts.prepayment-lines.store` · `.update` | 등록 · 수정 | RightsHolderContractController@storePrepaymentLine · updatePrepaymentLine |
| 1계층 매핑 연결 | → | SETT-001 | `admin.settlement.rights-mapping.index` | | (SETT-001 명세) |
| 계약 삭제 | — | — | 없음(`routes/admin.php:523`, 프로토 `confirmDelete`는 작성 중 계약만 — 확인 필요) | | |

### 탭 4 변경 · 열람 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 계약 변경 · 열람 이력 | GET | `/rights-holders/{rightsHolder}/logs` (규칙) | `admin.rights-holders.logs.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명(현재 `admin.admin-logs.index`) |

## 3. 폼 필드 · 검증

### 목록 검색 (GET, `RightsHolderController.php:35-40`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `keyword` | 이름 · 코드 · 계약 | `#clSearch` |
| `birth_date` · `phone_tail` | 개인 식별 보조 | 프로토 없음 |
| `holder_types[]` | `개인` · `사업자` · `위탁자` · `자사 권리자`(HOLDER_TYPE_LABELS) | `#clFilterParty` 법인 사업자 · 개인 사업자 · 개인 |
| `tax_type` | `personal` · `simplified` · `general` · `exempt` | 프로토 없음 |
| `business_status` · `api_expired` · `tax_pending` | 사업 상태 · 조회 만료 · 세무 보류 | `#clFilterStatus` `ALERT`(만료 임박 / 세무 보류 / 미확정) |
| `contract_status[]` | `pending` 작성 중 · `active` 계약 중 · `expired` 만료 · `terminated` 중도 해지. 첫 진입 기본 pending + active | `#clFilterStatus` `DRAFT` · `ACTIVE` · `EXPIRED`(만료/해지) |
| `contract_type` · `expiry_soon` · `alert` · `started_from` · `started_to` · `valid_on` | 계약 유형 · 만료 임박 · 조치 필요 · 시작일 범위 · 기준일 | 프로토 없음(`ALERT` 일부) |
| `ids[]` | 선택 행(엑셀) | — |

- 배열 쿼리(e555839b): 배열이 정상인 키는 `holder_types[]` · `contract_status[]` · `ids[]`뿐이고, 그 밖의 키에 배열이 오면 빈 값으로 본다(전에는 500) — `RightsHolderController.php:45-49` · `:340-350`.

### S1 권리자 · 세무 (RightsHolderRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `name` | required · max 100 | | `#holderName` 상호명 / 성명 |
| `tax_type` | required | `personal` 개인(인적용역 3.3%) · `simplified` 간이과세자 · `general` 일반과세자 · `exempt` 면세사업자 | 사업자 · 개인 radio `BUSINESS` · `PERSON`(L660-661) + 국세청 자동 |
| `is_internal` | boolean | 자사 귀속 | `#bizType` '자사 귀속' |
| `rights_holder_type` | `RIGHTS_HOLDER` · `CONSIGNOR`(사업자만, 자사와 동시 불가) | | 프로토 없음(위탁 계약은 조항 카드) |
| `business_subtype` | 사업자 · 비자사면 required | `SOLE` 개인사업자 · `CORP` 법인·단체 | `#bizType` 개인사업자 · 법인·단체 |
| `business_number` | 사업자면 required · 숫자 10 | | `#bizNumber` |
| `ceo_name` | 사업자면 required | | `#representative` |
| `open_date` | 사업자 · 비자사면 required | | `#openingDate` |
| `biz_category` · `biz_item` · `biz_address` | 사업자면 required | | 프로토 없음(개발에만) |
| `tax_email` | general · exempt면 required | | 프로토 없음 |
| `tax_invoice_eligible_yn` · `vat_treatment` | | | (계약 쪽 `#vatTreatment`) |
| `resident_no_enc` | 개인 · 비자사 · 등록이면 required · 13자리 | | `#residentId` |
| `is_resident` | boolean | | `#resident` 거주자 · 비거주자 |
| `payee_is_author` | 개인이면 required | | `#payeeAuthor` 본인 · 본인 아님 |
| `income_category` · `income_clause` | OTHER면 clause required | `BUSINESS` 사업소득 · `OTHER` 기타소득 / `C05` · `C15` · `C17` · `C19` | `#incomeCategory`('해당 없음 / 라인별' 포함) · `#incomeClause` |
| (업무 외 노무 활용) | 개발 없음 | | `#externalLabor` |
| `address` · `address_detail` | 개인이면 required | | 프로토 없음 |
| `suspended_approval_reason` | max 255 | | `#suspendedReason`(휴업자 저장 예외 승인) |
| `tax_decision_status` | | `PENDING_REVIEW` 검토 보류 · `DECIDED` 판정 완료 | `#taxDecision` |
| `matrix_case_id` · `tax_decision_reason` | DECIDED면 required | MATRIX_CASE_IDS | `#matrixCase` · `#taxDecisionReason` |
| `bank_name` · `account_no_enc` · `account_holder` | 비자사면 required(계좌는 등록 시) | | `#payeeAccount` |
| `partnership_started_at` · `email` · `phone` | | | 프로토 없음 |
| `proofs[PERSON_ID\|BANKBOOK\|BIZ_LICENSE][]` | 각 1개 · jpg/png/pdf · 10MB | | 증빙 선택(L1383대) |
| `return_contract_id` | 계약 화면에서 왔을 때 복귀 | | — |

### S2 계약 공통 (RightsHolderContractRequest::coreRules)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `title` | required · max 255 | | 계약명(목록) |
| `status` | required | `pending` 작성 중 · `active` 계약 중 · `expired` 만료 · `terminated` 중도 해지 | `#contractStatus` `DRAFT` · `ACTIVE` · `EXPIRED` · `TERMINATED` |
| `started_at` · `ended_at` | required · 종료 ≥ 시작 | | `#contractStart` · 현재 종료일 `#currentEndView` |
| `initial_end_date` | nullable | | `#initialEnd` |
| `terminated_at` · `terminate_reason` | terminated면 일자 required | | `#terminationDate` |
| `confirm_identifier` | 상태 변경 확인 입력 | | (P1 상태 동기화 확인) |
| `auto_extend` · `renewal_unit_years` · `renewal_stop_yn` | 자동 연장이면 단위 1 · 2 · 3년 | | `#renewalMode` · `#renewalMonths` · `#renewalStop` |
| `contract_expiry_alert_days` | 1~365 | | `#expiryAlert` |
| `min_payout_limit` · `min_claim_limit` | 0 이상 · 0 이하 | | `#minPayout` · `#minClaim` |
| `origin_type` · `predecessor_contract_id` | required · 승계면 선행 required | `NEW` 신규 계약 · `SUCCESSION` 승계 계약 | `#originType` · `#predecessor` |
| `refund_promo_burden_type` | required · **`A`만** | `A` 플랫폼 전액(기본) · (`B` 비율 공동 부담 · `C` 매출 취소 — 표시만) | `#refundBurden` A · B · C (8절 Q1) |
| `term_course_yn` · `rate_lines[n][started_at\|ended_at\|rate\|rate_type\|rate_basis\|mmg_amount\|reason]` | 강좌 R/S 조항, 1행 이상 | `rate_type` `BASIC` 기본 R/S · `SUPPORT` 지원금 R/S / `rate_basis` 순매출(PG 차감) · 결제 총액 · 순매출(PG+쿠폰 차감) | `#onOnline` · `#basicRateTable` · `rateModal()` |
| `mmg_enabled` · `vat_treatment` · `vat_exception_yn` · `vat_exception_reason` | | `vat_treatment` `ADD` 공급가액 기준 · VAT 별도 가산 · `GROSS` 공급대가 총액 기준 · 해당 시 역산(라벨 = 프로토, `app/Models/RightsHolder.php:166-170`) | `#mmgEnabled` · `#mmgAnnualCap` · `#vatTreatment` · `#vatException` · `#vatExceptionReason` |
| `term_book_yn` · `royalty_rate` · `royalty_basis` | 도서 인세 조항이면 required | `LIST_PRICE` 도서 정가 · `ACTUAL_PAID` 이용자 실구매가(배송비 제외) | `#onRoyalty` · `#royaltyDefaultRate` · `#royaltyDefaultBasis`, 목록 상단 radio `PAID_AMOUNT` · `LIST_PRICE`(L371) |
| `term_cons_yn` | **0만 허용(1차 위탁 미개방)** | | `#onConsignment` (8절 Q2) |
| `consignment_fee_type` · `consignment_fee_rate` · `consignment_promo_override_yn` · `consignment_return_*` | 위탁 켜졌을 때만(현재 제외) | `consignment_fee_type` `NET_DEDUCT` 수수료 차감 후 지급 · `GROSS_SETTLE` 총액 지급 후 수수료 청구(라벨 = 프로토, `RightsHolder.php:173-177`) | `#consignmentFeeType` · `#consignmentRate` · `#consignmentOverride` · `#returnTracking` · `#returnOwner` · `#returnDeadline` |
| `evidences[n][evidence_type\|file_name]` · `docs[]` · `deleted_*` | 증빙 50건 · 파일 10MB | ContractEvidence::TYPE_LABELS | `#evidenceTable` · `evidenceModal()` |

### S2 지급 조항 (paymentTermRules)
| 필드 name | 규칙 · 코드값 | 프로토타입 대응 |
|---|---|---|
| `term_exc_yn` · `exc_fee_amount` · `exc_service_started_at` · `exc_service_ended_at` | 전속계약금 | `#onExclusive` · `#exclusiveTotal` · `#exclusiveStart` · `#exclusiveEnd` |
| `exc_payment_method` | `LUMP_SUM` 일시 · `INSTALLMENT` 분할 | `#exclusiveStructure` 회차 분할 · 일시 지급 |
| `exc_target_month` · `exc_rows[n][title\|target_month\|amount]` | 일시 귀속월 · 분할 회차 | 회차 추가(`milestoneModal`) |
| `exc_clawback_policy` | `NONE` 반환 조항 없음 · `PRO_RATA` 잔여기간 일할 반환 · `FULL` 전액 반환 | `#exclusiveClawback` |
| `exc_penalty_clause_yn` · `exc_penalty_calc_type` · `exc_penalty_multiple_rate` · `exc_penalty_fixed_amount` · `exc_penalty_base` · `exc_penalty_clawback_relation` · `exc_penalty_trigger_text` · `exc_penalty_offset_consent_yn` | 배율 · 정액 / `exc_penalty_base` `TOTAL_AGREED` 약정 총액 · `PAID_GROSS` 기지급액 / `exc_penalty_clawback_relation` `INCLUSIVE` 위약금에 포함 · `CUMULATIVE` 병과 — 라벨은 a8016168에서 프로토 문구로(`app/Models/ExclusiveContractFee.php:53-67`) | `#penaltyEnabled` · `#penaltyMethod` · `#penaltyRate` · `#penaltyFixed` · `#penaltyBasis` · `#penaltyRelation` · `#penaltyTrigger` · `#penaltyConsent` |
| `term_dev_yn` · `dev_payment_method` | `REVENUE_SHARE` 매출 쉐어 · `INSTALLMENT` 확정금액 분할 · `LUMP_SUM` 일시금 | `#onDevelopment` · `#supportMethod` |
| `dev_offset_type` | `CONDITIONAL` 상계 허용(기본) · `NON_OFFSET` 비상계 | `#supportOffset` |
| `dev_cap_type` · `dev_total_cap_amount` | `CAPPED` · `UNLIMITED` | `#supportCapType` · `#supportCap` |
| `dev_rate_basis` | `SAME_AS_BASIC` · `NET_PG` · `CUSTOM` | `#supportRateTable`(SUPPORT 라인) |
| `dev_start_month` · `dev_end_basis` · `dev_end_month` | `FIXED_DATE` 지정일 · `CONTRACT_LINKED` 모계약 연동 | `#supportEndBasis` · `#supportEndDate` |
| `dev_lecture_*` · `dev_book_*` · `dev_*_targets[]` | 약정 대상(전체 · 선택) | `#supportScope` · `#supportTargets` · `#supportTargetCount` |
| `dev_cap_restore` · `dev_termination_policy` | 환급 차감분 한도 복원 · 종료 정책 | `#supportRestore` · `#supportTerminationPolicy` |
| `dev_total_amount` · `dev_auto_split` · `dev_rows[]` · `dev_lump_*` | 분할 · 일시 회차 | `#supportFixed` · `#supportSchedule` |
| (지원금 약정 식별자) | 자동 | `#supportAgreement` `SFA-2026-001` |
| `term_buyout_yn` · `buyout_amount` · `buyout_target_month` · `buyout_exclusive_*` · `buyout_*_targets[]` · `buyout_rights_scope` · `buyout_income` | 매절 | `#onBuyout` · `#buyoutAmount` · `#buyoutUntil` · `#buyoutScope` · `#buyoutTargets` · `#buyoutIncome` |
| `term_etc_yn` · `etc_amount_type` · `etc_unit_price` · `etc_rows[]` | `FIXED` 정액 · `PER_UNIT` 건당 | `#onAllowance` · `#allowanceType` · `#allowanceUnit` · `#allowanceTable` |
| `term_adv_yn` · `adv_nature` · `adv_offset_target` · `adv_payee_type` · `adv_offset_payee_id` | 선급금 성격 · 상계 대상(`adv_offset_target` `RS_BOOK` 강의 R/S + 도서 인세 · `RS` 강의 R/S만 · `BOOK` 도서 인세만, 각 '(+ 상계 허용 지원금)' — 라벨 = 프로토, `app/Services/Admin/RightsHolderContractPrepaymentService.php:31-39`) · 수취 주체 | `#onAdvance` · `#advanceNature` · `#advanceTarget` · `#advanceTable` |

### 메모 · 저서 · 선급 라인
| 폼 | Request | 프로토타입 대응 |
|---|---|---|
| 메모 `memoForm` | RightsHolderContractMemoRequest | `#memoText` · 메모 등록 · `#memoList` |
| 교재 인세 저서 `bookRoyaltyForm`(`book_id` 또는 임시코드 `BK-REQ-YYYY-NNNN` + 가제 · 출간 예정일, `royalty_rate`, `royalty_basis`) | BookRoyaltyContractRequest | `#bookTable` · `bookNew()` · `bookExisting()` · `bookEdit()` |
| 선급 원장 라인 `advLineForm` | RightsHolderContractPrepaymentLineRequest | `advanceModal()` · `#advanceSummary` |

## 4. 목록 필터 · 정렬 · 표 컬럼

| 개발 컬럼(`index.blade.php:336-354`, 행 = 권리자) | 프로토타입(행 = 계약, 목록 `renderContractList` L3653) |
|---|---|
| 선택 `checkAll` | — |
| 권리자 ID · 식별 · 권리자 유형 | 계약번호 / 권리자명 · 권리자 구분 |
| 세무 유형(국세청 자동) · 사업자 상태 / API 확인일 | 세무 판정 · 국세청 상태 |
| 식별번호(마스킹) | — |
| 유효 계약 · 계약 유형 · 계약 기간 · 기본 요율 · 계약 상태 | 포함 파이프라인 · 계약 기간 · 계약 상태 |
| 매핑 상품 · 프론트 전시 | 1계층 매핑 현황 카드(L367, 읽기 전용) |
| 관리 · 계약 이력(`layerContractHistory`: 차수 · 계약명 · 유형 · 기간 · 요율 · 상태 · 종료 방식 · 자동연장) | `quickContractSwitch`(L622) |

상단 요약 카드(유효 계약 등, `index.blade.php:19`)는 개발에만.

## 5. DB 테이블 · 컬럼 (주요, 전체는 `_index/schema.md`)
| 테이블 | 주요 컬럼 | 화면 |
|---|---|---|
| `rights_holders` | `code`(RH-), `name`, `tax_type`(varchar(20) NOT NULL), `is_internal`, `rights_holder_type`, `business_subtype`, `business_number`, `ceo_name`, `open_date`, `business_status`, `api_checked_at`, `resident_no_enc`, `is_resident`, `payee_is_author`, `income_category`, `income_clause`, `tax_decision_status`, `matrix_case_id`, `tax_decision_reason`, `suspended_approval_reason`, `bank_name`, `account_no_enc`, `account_holder`, `tax_email`, `consignment_*` | S1 · 목록 |
| `rights_holder_contracts` | `title`, `status`, `sequence_no`, `started_at`, `ended_at`, `initial_end_date`, `terminated_at`, `auto_extend`, `renewal_unit_years`, `renewal_stop_yn`, `contract_expiry_alert_days`, `min_payout_limit`, `min_claim_limit`, `origin_type`, `predecessor_contract_id`, `refund_promo_burden_type` | S2 |
| `contract_rate_lines` | `rate_type`(BASIC · SUPPORT), `rate`, `rate_basis`, `mmg_amount`, `started_at`, `ended_at`, `agreement_id` | S2 요율 |
| `contract_terms` · `contract_term_targets` | 조항 on/off · 약정 대상 | S2 |
| `exclusive_contract_fees` · `exclusive_contract_clawbacks` | 전속계약금 · 반환 | S2 · INST-002 |
| `support_fund_agreements` · `support_fund_ledgers` | 지원금 약정 · 소진 | S2 · INST-002 |
| `contract_milestones` | 회차 스케줄(INST-002 검수 대상) | S2 · INST-002 |
| `book_royalty_contracts` | `book_id`(bigint unsigned nullable — 출간 전 SKU 미연결이면 NULL), `temp_code`, `book_title`, `expected_publish_date`, `royalty_rate`, `royalty_basis`, `started_at`, `ended_at`(date nullable), `status` | S2 도서 |
| `prepayment_ledgers` · `prepayment_ledger_lines` | 선급 원장 | S2 선급 |
| `contract_evidences` · `rights_holder_contract_memos` · `rights_holder_account_histories` · `contract_co_signers` | 증빙 · 메모 · 계좌 이력 · 공동 수취인 | S1 · S2 |

## 6. 개발 JS · 마크업 이름
| 개발 id | 역할 | 프로토타입 대응 id |
|---|---|---|
| `searchForm` · `fKeyword` · `fBirth` · `fPhone` · `fTax` · `fBiz` · `fType` · `fValidOn` | 목록 검색 | `#clSearch` · `#clFilterStatus` · `#clFilterParty` |
| `layerContractHistory` · `chTitle` · `chBody` · `chGoDetail` | 계약 이력 | `#quickContractSwitch` |
| `layerNewContract` | 신규 계약 대상 권리자 선택 | '+ 신규 권리자 계약 등록'(L334) |
| `rightsHolderForm` · `holderName` · `taxType` · `taxTypeFixed` · `isInternal` · `partyPerson` · `partyBusiness` · `businessSubtype` · `businessNumber` · `ceoName` · `openDate` · `residentNo` · `isResident` · `payeeIsAuthorYes/No` · `incomeCategory` · `incomeClause` · `taxDecisionStatus` · `matrixCaseId` · `taxDecisionReason` · `suspendedApprovalReason` · `bankName` · `accountNo` · `accountHolder` | S1 | `#holderName` · `#bizType` · 사업자/개인 radio · `#bizNumber` · `#representative` · `#openingDate` · `#residentId` · `#resident` · `#payeeAuthor` · `#incomeCategory` · `#incomeClause` · `#taxDecision` · `#matrixCase` · `#taxDecisionReason` · `#suspendedReason` · `#payeeAccount` |
| `contractForm` · `contractStatus` · `terminateFields` · `predecessorRow` · `renewalUnitRow` · `renewalStopRow` · `manualEndRow` | S2 공통 | `#contractStatus` · `#terminationDate` · `#predecessor` · `#renewalMonths` · `#renewalStop` |
| `online` · `termCourse` · `mmgEnabled` · `vatTreatment` · `vatExceptionRow` | 강좌 R/S | `#online` · `#onOnline` · `#mmgEnabled` · `#vatTreatment` · `#vatExceptionWrap` |
| `royalty` · `termBook` · `layerBookRoyalty` · `bookRoyaltyForm` · `bookRoyalty*` | 도서 인세 · 저서 원장 | `#royalty` · `#onRoyalty` · `#bookTable` |
| `consignment` · `termCons` | 위탁 | `#consignment` · `#onConsignment` |
| `exclusive` · `termExc` · `excRows` · `excPenalty*` | 전속계약금 · 위약 | `#onExclusive` · `#penalty*` |
| `development` · `termDev` · `devRsBody` · `devSplitBody` · `devLumpBody` · `devRows` · `devEndBasis` | 지원금 | `#onDevelopment` · `#support*` |
| `buyout` · `termBuyout` · `buyoutLecture` · `buyoutBook` | 매절 | `#buyout` · `#onBuyout` · `#buyout*` |
| `allowance` · `termEtc` · `etcRows` · `etcUnitPrice` | 수당 | `#allowance` · `#onAllowance` · `#allowance*` |
| `advance` · `termAdv` · `advLineForm` · `adv*` | 선급 | `#advance` · `#onAdvance` · `#advance*` |
| `mapping` | 1계층 매핑(SETT-001 링크) | `#inst001ReadonlyMappingCard` |
| `evidence` · `evidenceTableBody` · `evidenceModal*` | 증빙 | `#evidence` · `#evidenceTable` |
| `memoForm` · `memoText` | 메모 | `#memoText` · `#memoList` |
| `layerContractLock` | 요율 잠금 안내(P1) | `openInst001RateLockModalP1` |
| `layerContractStatus` · `csIdentifier` · `csConfirm` | 상태 변경 확인 | 상태 동기화 영향 안내(P1) |
| `layerInstValidation` | 검증 상세(P2) | `validationModal()` · '검증 상세'(L1433대) |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 목록 단위가 권리자이고 계약은 이력 레이어(차수 · 종료 방식 · 자동연장) — `index.blade.php:646-650`
- 계약 상태 일괄 동기화(`status-sync`), 요약 카드
- 권리자 구분 `rights_holder_type`(권리자 · 위탁자), 사업자 업태 · 종목 · 사업장 주소 · 세금계산서 메일 필수
- 계약 읽기 전용 열람(`contracts.show`, 조회 권한)
- 선급 원장 라인 개별 등록 · 수정, 저서 원장 개별 등록 · 수정 · 삭제(임시코드)
- 증빙 파일 실제 업로드(권리자 신분증 · 통장 · 사업자등록증, 계약 증빙 50건)

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 탭 4 변경 · 열람 이력(`page-audit`, `renderAudit`)
- 업무 외 노무 활용 `#externalLabor`
- 위탁 조항 저장(1차 거부 — 8절 Q2), 환급 부담 B · C 저장(1차 거부 — 8절 Q1)
- 중도해지 일할 반환 산출 버튼(`clawbackModal`, '일수·반환액 산출'), 분할 상태 시연
- 재무 책임자 승인 · 휴업자 저장 예외 승인 '모의' 흐름(역할 전환 시연 `#role`)
- 목록 상단 도서 인세 기준 radio(`PAID_AMOUNT` · `LIST_PRICE`, L371) — 개발은 계약별 `royalty_basis`

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#contractStatus` `DRAFT` · `ACTIVE` · `EXPIRED` · `TERMINATED` | `status` `pending` · `active` · `expired` · `terminated`  라벨은 개발이 바꾸지 않음(e555839b 메시지) — 프로토 안에서 '작성 중'(select L297)과 '작성 중(DRAFT)'(목록 칩 L3697)이 갈려 있어 프로토 쪽 한 가지로 맞출 것 |
| 사업자 · 개인 radio `BUSINESS` · `PERSON` | `tax_type` `personal` / `simplified` · `general` · `exempt` |
| `#bizType` 개인사업자 · 법인·단체 · 자사 귀속 | `business_subtype` `SOLE` · `CORP` + `is_internal` |
| `#payeeAuthor` 본인 · 본인 아님 | `payee_is_author` 1 · 0 |
| `#resident` 거주자 · 비거주자 | `is_resident` 1 · 0 |
| `#taxDecision` 검토 보류 · 판정 완료 | `tax_decision_status` `PENDING_REVIEW` · `DECIDED` |
| `#renewalMode` 자동 갱신 · 수동 종료 / `#renewalMonths` 1 · 2 · 3년 | `auto_extend` / `renewal_unit_years` 1 · 2 · 3 |
| `#originType` 신규 · 승계 | `origin_type` `NEW` · `SUCCESSION` |
| `#refundBurden` A · B · C | `refund_promo_burden_type` `A`(B · C 표시만) |
| `#exclusiveStructure` 회차 분할 · 일시 지급 | `exc_payment_method` `INSTALLMENT` · `LUMP_SUM` |
| `#exclusiveClawback` 잔여기간 일할 반환 · 전액 반환 · 반환 없음 | `exc_clawback_policy` `PRO_RATA` · `FULL` · `NONE` |
| `#penaltyBasis` `TOTAL` · `PAID` | `exc_penalty_base` `TOTAL_AGREED` · `PAID_GROSS` — 라벨(약정 총액 · 기지급액)은 같음(a8016168에서 개발 구현, 라벨만) |
| `#penaltyRelation` `INCLUDED` · `ADDITIONAL` | `exc_penalty_clawback_relation` `INCLUSIVE` · `CUMULATIVE` — 라벨(위약금에 포함 · 병과)은 같음(a8016168에서 개발 구현, 라벨만) |
| `#vatTreatment` `VAT_ADDED` · `VAT_INCLUDED` | `vat_treatment` `ADD` · `GROSS` — 라벨 같음(a8016168에서 개발 구현, 라벨만) |
| `#advanceTarget` `BOTH` · `ONLINE` · `ROYALTY` | `adv_offset_target` `RS_BOOK` · `RS` · `BOOK` — 라벨 같음(a8016168에서 개발 구현, 라벨만) |
| `#consignmentFeeType` `NET_DEDUCT` · `GROSS_SETTLE` | 값 · 라벨 모두 같음(a8016168에서 개발 구현) |
| `#supportMethod` · `#supportOffset` · `#supportCapType` · `#supportEndBasis` | `dev_payment_method` · `dev_offset_type` · `dev_cap_type` · `dev_end_basis` |
| 도서 인세 기준 `PAID_AMOUNT` | `royalty_basis` `ACTUAL_PAID` |
| 계약번호 `CT-2026-0412` | `rights_holder_contracts.id` + `sequence_no`(표시 형식 확인 필요) |
| 권리자 코드 `RH-0019` | `rights_holders.code` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-INST001-1 | 환급 부담 방식 B · C: 정본 · 프로토는 계약마다 A · B · C 선택. 개발은 1차에 A만 저장(DECISIONS 113 ②, B · C 차감 연산 2차). 1차 범위를 A로 확정하는지 | 설계서 `:239`(옵션 A/B/C), 프로토 `#refundBurden` L948-953 | `app/Http/Requests/Admin/RightsHolderContractRequest.php:86-89`, `app/Models/RightsHolderContract.php:148-164` **→ 결정(white 10-27, D-SETT-02)**: B · C 부담 계약이 실제로 있음 → 1차에 B · C 저장 · 차감 연산 구현(개발 전달) |
| Q-INST001-2 | 위탁 조항(도서 위탁판매) 적용: 프로토는 위탁 카드 [적용] 선택 가능. 개발은 1차 저장 거부(화면설계서 v12 S2 ⑨ · DECISIONS 94). 도서 공급 원장의 위탁 저장 거부(BOOK-001 Q2)와 같은 결정인지 | 설계서 `:251`(CONSIGNMENT), 프로토 `#onConsignment` L1368 | `RightsHolderContractRequest.php:99-102` **→ 결정(white 10-27, D-PROD-05)**: BOOK-001과 같은 결정 — 위탁 계약이 없어도 1차 개발, 위탁 조항도 1차 저장(개발 전달) |
