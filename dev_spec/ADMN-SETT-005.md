# ADMN-SETT-005 정산 수동 조정 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-005_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-005 · ADMN-SETT-005-S1(조정 라인 등록 · 수정)
- 개발 진행: 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 4건). S1 은 별도 페이지(`/form`), 확정 · 반려는 목록의 모달

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.adjustments.index` | 정산 수동 조정 | 엑셀 메뉴 키 `EXCEL_MENU`(app/Http/Controllers/Admin/SettlementAdjustmentController.php) + 정규화 규칙. 운영 DB 행 미확인 |

- 등록 · 수정 폼은 `show` 접미사라 조회 권한으로 열리고, 저장은 `store`(can_create), 확정 · 반려는 `update`(can_update), 삭제는 `destroy`(can_delete).

## 2. 화면별 라우트
### ADMN-SETT-005 수동 조정 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 · KPI | GET | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.index` | can_view | SettlementAdjustmentController@index |
| 조정 명세 엑셀(사유 필수) | GET | `/{admin}/settlement/adjustments/download` | `admin.settlement.adjustments.download` | can_download | SettlementAdjustmentController@download |
| 확정 · 반려(모달 `#layerAdjDecision`) | PUT | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.update` | can_update | SettlementAdjustmentController@update |
| 삭제 | DELETE | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.destroy` | can_delete | SettlementAdjustmentController@destroy (뷰에 버튼 없음) |

### ADMN-SETT-005-S1 조정 라인 등록 · 수정(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 폼 열기 `?id=`(있으면 수정) | GET | `/{admin}/settlement/adjustments/form` | `admin.settlement.adjustments.show` | can_view | SettlementAdjustmentController@show |
| 저장(신규 · 수정 공통, hidden `id`) | POST | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.store` | can_create | SettlementAdjustmentController@store |

- id 를 URL 파라미터가 아니라 쿼리 · 본문 `id` 로 받는다(update · destroy 도 본문 `id`). 저장 후 목록 조건 KEEP(applied_month · origin_month · adjust_type · reason_type · status · keyword · page) 유지.
- SETT-002-S1 에서 `admin.settlement.adjustments.show` 로 바로 들어온다(board/show.blade.php:142).

## 3. 폼 필드 · 검증
### 조정 라인 저장 (SettlementAdjustmentRequest) — `#adjForm`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `id` | hidden, 있으면 수정 | | — |
| `adjust_type` | required · in | `CURRENT` 당월 수동 조정 · `PRIOR_FIX` 전월 정정(마감 후 전기오류수정) · `ACCOUNT_TRANSFER` 계정 간 대체 전표 · `PRO_RATA` 지원금 이행률 정산 · `SUPPORT_CAP_MANUAL` 지원금 한도 수기 조정 · `ALLOWANCE` 정액 · 건당 수당 | `newAdjType` |
| `origin_settlement_id` | nullable · integer, PRIOR_FIX · ACCOUNT_TRANSFER 면 필수 | 원 정산서 | `newOriginStmt` |
| `origin_month` | required · YYYY-MM, PRIOR_FIX 면 applied_month 보다 앞서야 | 원 발생 귀속월 | `newOriginMonth` |
| `applied_month` | required · YYYY-MM | 반영월 | `newAppliedMonth` |
| `rights_holder_id` | required · integer | 권리자 | (원 정산서에서 자동) |
| `payee_id` | nullable · integer | 수취인(NULL=권리자 본인) | `newPayee` |
| `contract_id` | nullable · integer | 계약 | — |
| `transfer_pair_key` | nullable · ≤40 | 대체 전표 쌍 키 | — |
| `reason_type` | required · in | rate_error 요율 오류 · share_error 지분율 오류 · payee_split_error 수취인 분할 오류 · refund_missing 환불 반영 누락 · lumpsum_month_error 약정금 귀속월 오류 · buyout_income_error 매절 소득 구분 오류 · tax_type_misjudge 과세유형 오인 · reconcile_diff 대사 차이 정정 · account_transfer 계정 간 대체 · book_supply_type_error 도서 공급 형태 오등록 · support_cap_error 지원금 한도 판정 오류 · consignment_fee_error 위탁 수수료율 오류 · etc 기타 | `newReasonCode` |
| `explanation` | required · 20~2000 (trim) | 소명 내용 | `newExplanation` |
| `adjust_amount` | required · integer · not 0 (부호 포함, 음수=차감) | | `newAdjAmount` |
| `account_type` | required · in | `PRE_TAX` 세전 · `POST_TAX` 세후 | `newAccountType` |
| `vat_type` | required · in | `taxable` 과세 · `exempt` 면세 | `newTaxType` |
| `income_category` | nullable · in BUSINESS/OTHER | BUSINESS 면 호 금지, OTHER 면 호 필수 | `newIncomeCategory`(상위 축) |
| `income_clause` | nullable · in C05 · C15 · C17 · C19 | 기타소득 호 | `newIncomeCategory`(호 포함 단일 select) |

### 확정 · 반려 (SettlementAdjustmentDecisionRequest) — `#layerAdjDecision`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `id` | hidden `#adjDecisionId` | | 선택 행 |
| `decision` | hidden `#adjDecisionMode` | `confirm` · `reject` | approveAdjustment |
| `reject_reason` | decision=reject 일 때 required · trim 후 2자 이상 | 반려 사유 | (프로토타입 반려 사유 입력 없음) |

### 다운로드 사유 (ReasonRequest — 공통 `#layerReason`)
- `reason` · `reason_ref` · `reason_etc` (값은 ADMN-SETT-002 명세 3절과 같음). 목록 조건은 `data-reason-params` 로 함께 넘긴다.

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `applied_month` | YYYY-MM | 없음 |
| `origin_month` | YYYY-MM | 없음 |
| `adjust_type` | TYPE_LABELS 6종 | 없음 |
| `reason_type` | REASON_LABELS 13종 | `reasonFilter` |
| `status` | `pending` 등록 · `approved` 확정 · `rejected` 반려 | 없음 |
| `keyword` | 권리자명 · 수취인명 · 소명 내용 LIKE (app/Repositories/Admin/SettlementAdjustmentRepository.php:93-99) | `searchInput` |

- KPI(index.blade.php:73-77): 당월 반영 조정 건수 · 미확정(등록) · 확정(정산서 반영) · 반려 · 전월 정정 라인.
- 표(index.blade.php:187-194): 조정 ID / 원 정산서 · 유형 · 원 발생월 → 반영월 · 권리자 / 수취인(세무 유형) · 사유 구분 · 조정 금액 · 계정 / 과면세 / 증빙 정정 채널 · 상태 · 관리([수정] → S1, [확정] · [반려] → 모달).
- 엑셀 헤더: 조정 ID · 유형 · 원 발생월 · 반영월 · 권리자 · 수취인 · 세무 유형 · 사유 구분 · 조정 금액 · 계정 · 과면세 · 증빙 정정 채널 · 상태 · 소명. 파일명 `정산수동조정_<applied_month|all>`.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| settlement_adjustments.rights_holder_id · payee_id · contract_id | | 권리자 · 수취인 · 계약 | 권리자 / 수취인 |
| settlement_adjustments.adjust_type | string(20) | 6종(3절) | 유형 |
| settlement_adjustments.origin_month · applied_month | char(7) | 원 발생 귀속월 · 반영월 | 원 발생월 → 반영월 |
| settlement_adjustments.reason_type | string(30) | 13종(3절) | 사유 구분 |
| settlement_adjustments.explanation | text | 소명(최소 20자) | 소명 |
| settlement_adjustments.adjust_amount | integer | 부호 포함 | 조정 금액 |
| settlement_adjustments.vat_type · income_category · income_clause · account_type | | 과면세 · 소득 구분 · 호 · 계정 | 계정 / 과면세 |
| settlement_adjustments.status | string(20) | 모델 상수 pending(등록) · approved(확정) · rejected(반려). 컬럼 주석에는 applied(정산서 반영 완료)도 있음 | 상태 |
| settlement_adjustments.approved_at · approver1_id · approver2_id · reject_reason · created_by | | 확정 일시 · 확정자 · (2차 승인자 컬럼은 남아 있음) · 반려 사유 · 등록자 | 감사 |
| settlement_adjustments.origin_settlement_id | unsignedBigInteger | 원 정산서(주석상 instructor_settlements.id) | 원 정산서 |
| settlement_adjustments.matrix_case_id · correction_channel · correction_channel_sub | | 세무 케이스 · 증빙 정정 채널(channel_1 수정 전자세금계산서 · channel_2 수정 전자계산서 · channel_3a 원천세 수정신고 · channel_3b 기록 정정 · channel_4 수취 증빙 재요청 · internal 자사 내부 대체 전표) | 증빙 정정 채널 · S1 미리보기 |
| settlement_adjustments.transfer_pair_key | string(40) | 대체 전표 쌍 | S1 |

출처: dev_spec/_index/schema.md settlement_adjustments(2330-2360); app/Models/SettlementAdjustment.php:28-134.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#searchForm` | 목록 검색 | searchInput · reasonFilter |
| `.layer__open[data-target="layerReason"][data-reason-action|title|submit|lead|params]` | 엑셀 사유 모달 | — |
| `.layer__open[data-target="layerAdjDecision"][data-adj-decision="confirm|reject"][data-adj-id]` | 확정 · 반려 열기 | approveAdjustment |
| `#layerAdjDecision` · `#adjDecisionTitle` · `#adjDecisionId` · `#adjDecisionMode` · `#adjConfirmLead` · `#adjRejectBox` | 결정 모달 | — |
| `#adjForm` | S1 폼 | 신규 조정 폼(openNewAdjPage) |
| `#adjType`(name adjust_type) | 유형 | `newAdjType` |
| `#adjExplanation` · `#adjExplanationCount` | 소명 · 글자 수 | `newExplanation` |
| `#adjSubmit` "저장 (상태: 등록)" | 저장 | "✔ 수동 조정 레코드 등록"(submitNewAdjustment) |

출처: resources/views/admin/settlement/adjustments/index.blade.php:73-318 · form.blade.php:43-277.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 목록 필터 `applied_month` · `origin_month` · `adjust_type` · `status`.
- 유형 `ALLOWANCE`(정액 · 건당 수당).
- 반려 + 반려 사유(`reject_reason`), 상태 3종(등록 · 확정 · 반려).
- 조정 명세 엑셀 다운로드(사유 입력).
- 대체 전표 쌍 키(`transfer_pair_key`) 입력.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 탭 2 4채널 증빙 정정 분기 · 원천세 수정신고 작업 표(정정 작업 상태 · 재요청 발송) — 개발은 S1 에 세무 케이스 · 정정 채널 · 병기 채널 미리보기 표만 있다(form.blade.php:233).
- 탭 3 수동 조정 감사 로그 표.
- 과세유형 오인 정정 근거 파일 첨부(`newTaxTypeEvidence`).
- 과세최저한 판정 단위 키 입력(`newTaxThresholdKey`).
- 승인 단계 열(2단계 승인 표시) — 개발은 재무 담당 단독 확정.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| newAdjType 당월 · 전월 정정 · 세전/세후 계정 간 · 이행률 PRO_RATA · 한도 수기 | `adjust_type` CURRENT · PRIOR_FIX · ACCOUNT_TRANSFER · PRO_RATA · SUPPORT_CAP_MANUAL (+ALLOWANCE) |
| newReasonCode / reasonFilter `RATE_…` 대문자 코드, "선급금 상계액 오류" · "최저보장 보전금 산출" 등 | `reason_type` 소문자 snake 13종 — 선급금 상계 · 최저보장 항목 없음 |
| newOriginStmt (STMT-YYYYMM-…) | `origin_settlement_id` (정수 id) |
| newOriginMonth · newAppliedMonth | `origin_month` · `applied_month` |
| newAdjAmount | `adjust_amount` |
| newAccountType adj_account_type | `account_type` PRE_TAX · POST_TAX |
| newTaxType EXEMPT · TAXABLE | `vat_type` exempt · taxable |
| newIncomeCategory(상위 축 + 호 한 칸, "원천징수 비대상(재화)" 포함) | `income_category` + `income_clause` 두 칸(재화 공급은 둘 다 비움) |
| newExplanation adj_explanation | `explanation` |
| newPayee | `payee_id` |
| 신규 등록 페이지(SJM_PAGE) | `admin.settlement.adjustments.show` `/form?id=` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 프로토타입 사유 "선급금 상계액 오류" · "최저보장 보전금 산출 오류"가 개발 reason_type 에 없다. 반대로 개발의 `ALLOWANCE`(정액 · 건당 수당) 유형은 프로토타입에 없다.
- 확인 필요: 승인 단계 — 개발은 재무 담당 단독 확정(approved_at · approver1_id, PO 2026-09-22 주석). 프로토타입의 2단계 승인 표시를 유지할지.
- 확인 필요: settlement_adjustments.status 주석의 `applied`(정산서 반영 완료)는 모델 상수에 없다.

## 출처
- routes/admin.php:571-579
- app/Http/Controllers/Admin/SettlementAdjustmentController.php (index · show · store · update · destroy · download · filters · keep)
- app/Http/Requests/Admin/SettlementAdjustmentRequest.php · SettlementAdjustmentDecisionRequest.php
- app/Models/SettlementAdjustment.php:28-134
- resources/views/admin/settlement/adjustments/index.blade.php · form.blade.php
- resources/views/admin/settlement/board/show.blade.php:142
