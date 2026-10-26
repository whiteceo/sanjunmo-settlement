# ADMN-SETT-007 수취인 분할 지분 설정 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-007_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-007 · ADMN-SETT-007-S1(수취인 분할 편집)
- 개발 진행: 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 3건). S1 은 dev-progress 초기값 "2차"(DECISIONS 113 ① — 분할 "계산"이 2차)이나 편집 · 저장 · 시뮬레이터 화면은 d562524a 에 있다. 정산 엔진은 분할 계약 권리자를 PAYEE_SPLIT 으로 보류

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.payee-splits.index` | 수취인 분할 지분 설정 | 라우트 정규화 규칙. 운영 DB 행 미확인 |

- 공동 서명 풀 추가 · 제외는 `.store`(can_create) · `.destroy`(can_delete) 로 같은 메뉴 권한 행을 쓴다. 시뮬레이터는 `.show`(can_view) — 저장하지 않는다.

## 2. 화면별 라우트
### ADMN-SETT-007 계약별 수취인 분할 현황
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 현황 목록 | GET | `/{admin}/settlement/payee-splits` | `admin.settlement.payee-splits.index` | can_view | PayeeSplitController@index |
| 신규 분할 — 대상 계약 선택(별도 페이지) | GET | `/{admin}/settlement/payee-splits/create` | `admin.settlement.payee-splits.create` | can_create | PayeeSplitController@create |

### ADMN-SETT-007-S1 수취인 분할 편집(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 편집 화면 | GET | `/{admin}/settlement/payee-splits/{contract}` | `admin.settlement.payee-splits.edit` | can_update | PayeeSplitController@edit |
| 분할 비율 저장(구성 전체 교체) | PUT | `/{admin}/settlement/payee-splits/{contract}` | `admin.settlement.payee-splits.update` | can_update | PayeeSplitController@update |
| 배분 시뮬레이터(JSON, 저장 안 함) | GET | `/{admin}/settlement/payee-splits/{contract}/simulate` | `admin.settlement.payee-splits.show` | can_view | PayeeSplitController@show |
| 공동 서명 수취인 풀 추가 | POST | `/{admin}/settlement/payee-splits/{contract}/co-signers` | `admin.settlement.payee-splits.store` | can_create | PayeeSplitController@store |
| 공동 서명 수취인 풀 제외 | DELETE | `/{admin}/settlement/payee-splits/{contract}/co-signers/{coSigner}` | `admin.settlement.payee-splits.destroy` | can_delete | PayeeSplitController@destroy |

- `{contract}` = rights_holder_contracts.id, `{coSigner}` = contract_co_signers.id. 편집이 `edit` 접미사라 수정 권한이 있어야 열린다(SETT-001 S1 과 다름).

## 3. 폼 필드 · 검증
### 분할 비율 저장 (PayeeSplitRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `reason` | required · string 10~255 (trim) | 변경 사유(감사 통제) | 저장 시 사유 |
| `splits[i][payee_id]` | required · integer | 수취인(공동 서명 풀에서 select) | 수취인 행 |
| `splits[i][split_ratio]` | required · numeric 0.01~100 · decimal:0,2 | 분할 비율(%) — 합계 100.00 | updateSplitRatio 입력 |
| `splits[i][start_date]` | required · Y-m-d | 적용 시작일 | |
| `splits[i][end_date]` | nullable · Y-m-d · ≥ start_date | 적용 종료일 | updateEndBasis |
| `splits[i][note]` | nullable · ≤255 | 비율 근거 메모 | — |
| `splits` | required · array 1~20 | | |

- 서비스 차단 문구(app/Services/Admin/PayeeSplitService.php:209-284): 사유 10자 미만 · 수취인 0명 · 선급금 미종결 계약(5.3절) · 같은 수취인 중복 · 공동 서명/승계인이 아닌 수취인(4.1절) · 합계 ≠ 100.00 · 상속 승계 수취인인데 SUCCESSION 증빙 없음(16.1절).

### 공동 서명 수취인 추가 (ContractCoSignerRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `payee_id` | required · integer · exists rights_holders | 수취인 | `coSignerModal` 선택 |
| `role` | required · ≤50 | 계약상 지위(원 저작자 · 공동서명 소속사 · 법정 상속인 등 자유 입력) | |
| `entity_type` | nullable · ≤50 | 사업자 구분 표기 | |
| `tax_case` | nullable · ≤50 | 세무 케이스 표기(TX-02 등) | |
| `is_author` | nullable · boolean | 저작자 본인 | |
| `succession_yn` | nullable · boolean | 상속 승계 | |
| `succession_date` | succession_yn=1 이면 required · Y-m-d | 승계 확정일 | |

### 시뮬레이터 (쿼리)
| name | 뜻 |
|---|---|
| `base_amount` | 배분 기준액(원) `#simBase` |
| `splits[i][payee_id]` · `splits[i][split_ratio]` | 현재 편집 행에서 읽음 |

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `status` | `ALL` 전체 계약 보기 · `SPLIT` 2계층 분할 수취 활성(2인 이상) · `SINGLE` 단독 수취(원 권리자 100.00%) · `SUCCESSION` 사망·상속 수취인 승계 계약 · `BLOCKED` 선급금 미종결로 분할 차단된 계약(5.3절) — 버튼형 | `listFilterSelect` |
| `keyword` | `#keyword` | `listSearchInput` |

- 목록 표(index.blade.php:100-105): 계약 식별자 / 계약명 · 1계층 원 권리자(저작자) · 현재 2계층 수취인 구성 및 비율 · 선급금 원장 상태(5.3절) · 합계 검증 · 관리 액션([편집] → S1).
- 계약 선택 페이지(create.blade.php:74-79): 계약번호 / 계약명 · 1계층 원 권리자 · 공동 서명 후보 풀 · 선급금 잔액(5.3절) · 현재 분할 상태 · 선택. 같은 `status` · `keyword` 필터.
- S1 표: 공동 서명 풀(수취인 · 계약상 지위 · 사업자 구분 · 세무 케이스 · 저작자 본인 · 상속 승계 · 관리[풀에서 제외]), 분할 행(수취인 · 분할 비율 · 적용 시작일 · 적용 종료일 · 비율 근거 메모 · 삭제), 시뮬레이터 결과(수취인 · 분할 비율 · 배분액), 8단계 비분할 격리 규칙 표(정산 구성 항목 · payee_split_base 분할 여부 · 규칙 · 근거).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| payee_splits.contract_id | foreignId | 계약 | 계약 식별자 |
| payee_splits.rights_holder_id | foreignId | 1계층 원 권리자 | 원 권리자 |
| payee_splits.payee_id | unsignedBigInteger | 수취인(권리자 본인도 한 행) | 수취인 |
| payee_splits.split_ratio | decimal(5,2) | 분할 비율 — 합계 100.00 | 비율 |
| payee_splits.start_date / end_date | date / date null | 적용 기간 | |
| payee_splits.note | string(255) null | 비율 근거 메모 | 메모 |
| contract_co_signers.contract_id · payee_id · role · entity_type · tax_case · is_author · succession_yn · succession_date | | 공동 서명 수취인 풀 | S1 풀 표 |
| rights_holder_contracts.* | | 계약 마스터 | 목록 |
| (선급금 원장 — RightsHolderContractPrepaymentRepository 등) | | 미상계 잔액 > 0 이면 분할 차단 | 선급금 원장 상태 |
| settlement_lines.payee_id · payee_split_base · payout_hold_reason=`PAYEE_SPLIT` | | 정산 반영 · 1차 보류 | SETT-002 |

출처: dev_spec/_index/schema.md payee_splits(2316) · contract_co_signers(2758).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 상태 버튼 `.st-btn(.st-btn--pr)` `?status=` · `#keyword` | 목록 필터 | `listFilterSelect` · `listSearchInput` |
| [신규 분할] → `…payee-splits.create` 페이지 | 대상 계약 선택 | `contractPickerModal` · `modalContractSearch` · `modalContractFilter` |
| 풀 추가 폼(POST) `#payee_id` · `#role` · `#entity_type` · `#tax_case` · `#is_author` · `#succession_yn` · `#succession_date` | 공동 서명 수취인 추가 | `coSignerModal` |
| 풀 제외 폼(DELETE) `.st-btn--danger` | 풀에서 제외 | — |
| 저장 폼(PUT) `#reason` + `#splitRows tr` (name `splits[i][…]`) · `[data-split-remove]` | 분할 행 편집 · 저장 | saveCurrentSplit · removePayeeRow |
| `#simBase` · `#simRun` · `#simResult` | 배분 시뮬레이터(fetch `…payee-splits.show`) | updateSimBase |

출처: resources/views/admin/settlement/payee-splits/index.blade.php:11-139 · create.blade.php:11-121 · edit.blade.php:78-323 · form.blade.php:18-56.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 공동 서명 수취인 풀 관리(추가 · 제외, 지위 · 사업자 구분 · 세무 케이스 · 저작자 · 상속 승계 · 승계 확정일) — contract_co_signers.
- 분할 행 비율 근거 메모(`note`), 변경 사유(`reason`) 10자.
- 배분 시뮬레이터(기준액 입력 → 수취인별 배분액).
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 비율 프리셋(applyPresetRatio) · 잔여 비율 마지막 행 채우기(fillRemainingToLast).
- 탭 3 감사 로그 표(기록 시각 · 작업 유형 · Before/After) — 개발은 별도 표 없음(추정: admin_logs).
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `listFilterSelect` 5종 | `status` ALL · SPLIT · SINGLE · SUCCESSION · BLOCKED |
| `listSearchInput` | `keyword` |
| `contractPickerModal` | `admin.settlement.payee-splits.create` 페이지 |
| 편집 워크스페이스 탭(switchView) | `admin.settlement.payee-splits.edit` 페이지 `/payee-splits/{contract}` |
| `coSignerModal`(마스터 후보에서 선택) | 풀 추가 폼 → contract_co_signers 저장 |
| saveCurrentSplit | PUT `…payee-splits.update` (`reason` + `splits[]`) |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
- 확인 필요: 프로토타입은 공동 서명 수취인을 계약 마스터에서 고르기만 하는데, 개발은 이 화면에서 풀(지위 · 승계 정보)을 직접 등록한다. 공동 서명인 등록 주체(계약 원장 vs 이 화면)를 어디로 둘지.
- 확인 필요: 분할을 저장해도 1차 정산은 PAYEE_SPLIT 으로 보류된다(DECISIONS 113 ①) — 프로토타입 저장 후 안내 문구에 반영할지.

## 출처
- routes/admin.php:586-597
- app/Http/Controllers/Admin/PayeeSplitController.php
- app/Http/Requests/Admin/PayeeSplitRequest.php · ContractCoSignerRequest.php
- app/Services/Admin/PayeeSplitService.php:28-50, 209-284, 342-373
- resources/views/admin/settlement/payee-splits/index.blade.php · create.blade.php · edit.blade.php · form.blade.php
- config/dev-progress.php:85-86, 219
