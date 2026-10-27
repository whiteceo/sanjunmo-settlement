# ADMN-INST-002 약정금 마일스톤 검수 · 승인 원장 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-INST-002_baseline.html` (원본 상태: `18d66c1` v6.92)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: INST-002 탭 1 검수 워크스페이스(목록 + 상세 검수) · 탭 2 전속계약금 중도해지 일할 반환 · 종료 일시정산(LUMP_SETTLE) · 탭 3 검수 · 수기 소명 감사 로그 · `recalcNoticeModal` 자동 재연산 알림
- 개발 진행: 일부 구현. 검수 큐(귀속월 · 유형 · 상태 · 검색) · 3대 게이트 판정 · 승인/반려(검수 방식 + 의견)만 있음. 탭 2 · 탭 3 · 상세 편집(소득 구분 · 귀속월 · 증빙 파일) · 임시 저장 · 승인 후 자동 재연산은 미구현. `_index/progress.md` INST-002 라우트 주석 있음

프로토타입 view ↔ 개발 화면
| 프로토타입 view / 모달 | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| `tabWorkspace` 검수 큐 + 우측 상세(`renderDetail`, L1227) | 검수 큐 표 + 검수 레이어 | `resources/views/admin/rights-holders/milestones/index.blade.php` (`#layerMilestoneReview`) |
| `tabClawback` 일할 반환 · 일시정산(L517) | 없음 | — |
| `tabAudit` 감사 로그(L518) | 없음(공통 관리 로그 `admin.admin-logs.index`에 `milestone_*` 하위 동작으로 남음) | — |
| `recalcNoticeModal`(L681) | 없음 | — |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.rights-holders.milestones.index` | 약정금 마일스톤 검수(라우트 주석 `routes/admin.php:476`) | 탭 1~3 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 승인 · 반려는 수정 권한(`can_update`) — 7단계 정산 인입을 열기 때문(`routes/admin.php:484-485`). 버튼 노출 `@adminCan('admin.rights-holders.milestones.index', 'can_update')` (`milestones/index.blade.php:204`).
- 라우트는 권리자 원장 그룹보다 위에 둔다(`{rightsHolder}` 충돌 방지, `routes/admin.php:478-479`).
- 자금 출금 경로 없음(정본 01권 7.2절과 일치, `MilestoneReviewController.php:17-18`).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`.

### 탭 1 검수 워크스페이스
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 검수 큐(`?target_month=&term_type=&approval_status=&keyword=`) | GET | `/rights-holders/milestones` | `admin.rights-holders.milestones.index` | 조회 | MilestoneReviewController@index |
| 검수 승인 · 반려(`decision`) | PUT | `/rights-holders/milestones` | `admin.rights-holders.milestones.update` | 수정 | MilestoneReviewController@update |
| 임시 저장(소득 구분 · 귀속월 · 검수 방식 · 의견) | PUT | `/rights-holders/milestones/{milestone}/draft` (규칙) | `admin.rights-holders.milestones.draft.update` (규칙) | 수정 | 개발 미구현, 규칙 기반 명명 |
| 국세청 재조회 | POST | `/rights-holders/{rightsHolder}/nts-verify` | `admin.rights-holders.nts-verify` | 수정(접미사 예외) | RightsHolderController@ntsVerify (INST-001과 공용) |
| R/S 약정 대상 누락 보완 | → | 계약 상세(INST-001-S2) | `admin.rights-holders.contracts.edit` | 수정 | RightsHolderContractController@edit |
| 월간 정산으로 이동 | → | SETT-002 | (SETT-002 명세 참고) | | |

### 탭 2 중도해지 일할 반환 · 종료 일시정산
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/rights-holders/milestones/clawbacks` (규칙) | `admin.rights-holders.milestones.clawbacks.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명(테이블 `exclusive_contract_clawbacks`는 있음) |

### 탭 3 감사 로그
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 검수 감사 로그 | GET | `/rights-holders/milestones/logs` (규칙) | `admin.rights-holders.milestones.logs.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명. 현재는 `admin.admin-logs.index`(CONF-006) |

## 3. 폼 필드 · 검증

### 검수 큐 검색 (GET, `MilestoneReviewController.php:29-34`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `target_month` | `YYYY-MM`, 미지정이면 당월 | 귀속월 컬럼 · `#editTargetMonth` |
| `term_type` | `EXC` 전속계약금 (일회성 비상계) · `DEV` 개발지원금 (일시금 · 분할형) · `BUYOUT` 매절 대금 (권리 양도) · `ETC` 정액 · 건당 수당 | `#typeFilter` `EXCLUSIVE_FEE` · `SUPPORT_LUMP_INST` · `SUPPORT_RS_ONCE` · `BUYOUT` · `FLAT_ALLOWANCE` · `LUMP_SETTLE` |
| `approval_status` | `pending` 검수 대기 · `approved` 검수 승인 · `rejected` 검수 반려 · `hold` 게이트 차단 보류 | 상태 배지(L543 '게이트 / 검수 상태') |
| `keyword` | 식별자 · 권리자 · 계약 | `#searchInput` |
| `page` | | |

### 검수 승인 · 반려 (MilestoneReviewRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `milestone_id` | required · integer | contract_milestones.id | 큐 행 선택 `selectItem(id)` (프로토 식별자 `MS-2026-001`) |
| `decision` | required | `approve` · `reject` | `approveMilestone()` · `rejectMilestoneItem()` |
| `verify_method` | required | `EVIDENCE_FILE` 증빙 파일 · `MANUAL_NOTE` 수기 소명 (1차는 파일을 받지 않음) | `#editInspectMode` `EVIDENCE_FILE` · `MANUAL_NOTE` |
| `review_note` | required · **20자 이상** · 2000자 이하 | | `#editMemo` · 글자 수 `#editMemoCount` (v6.92 프로토도 공백 제외 20자 · 최대 2,000자 — D-PROD-07) |
| (증빙 파일) | 개발 없음 | | `#editEvidenceFile` |
| (소득 구분 · 기타소득 호) | 이 화면에서 수정 불가(게이트 A 표시만) | `BUSINESS` · `OTHER` / `C05` · `C15` · `C17` · `C19` | `#editIncomeCategory` · `#editIncomeClause` |
| (귀속월) | 이 화면에서 수정 불가(스케줄 값) | | `#editTargetMonth` (8절 Q3) |
| 숨김 `target_month` · `term_type` · `approval_status` · `keyword` · `page` | 목록 복귀용 | | |

### 3대 게이트 (MilestoneReviewService::evaluateGates `:92-107`)
| 게이트 | 개발 판정 | 프로토타입 대응 |
|---|---|---|
| A 소득 구분 | `income_category` 필수, OTHER면 `income_clause` 필수 | `evaluateGates`(L1075) A — 정본은 `payee_is_author`도 요구(8절 Q4) |
| B 지원금 약정 필수값 | 한도 유형 · 총 한도/종료 정책 짝 · SUPPORT 요율 라인 · 약정 대상 · 종료 기준 | B |
| C 국세청 | 계속사업자 + 조회 90일 이내 | C · `recheckNts()` |
| 마감월 차단 | 귀속월 마감 확정이면 승인 불가(ADMN-SETT-005로 안내) | `LOCKED_MONTHS`(L1506-1509) |

## 4. 목록 필터 · 정렬 · 표 컬럼

스코어카드(`index.blade.php:68-72`): 전체 검수 대상 · 검수 대기 · 게이트 차단 보류 · 검수 승인 · 정산서 이관 완료.

| 개발 컬럼(`index.blade.php:150-156`) | 프로토타입 컬럼(L543) |
|---|---|
| 식별자 / 계약 | 식별자 / 계약 ID |
| 권리자 / 약정 구분 | 권리자 / 약정 구분 |
| 약정 금액 (세전) | 약정 금액 (또는 요율) |
| 소득 구분 | 상계 / 소득구분 |
| 귀속월 | 귀속월 (target_month) |
| 3대 게이트 · 검수 상태 + 검수 버튼 | 게이트 / 검수 상태 |

정렬 파라미터 없음.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `contract_milestones.code` | string(30) | 표시 식별자 `EXC-YYYY-NN` · `SUP-YYYY-NNN` · `MS-YYYY-NNN` | 식별자 |
| `contract_milestones.contract_id` | | rights_holder_contracts.id | 계약 |
| `contract_milestones.term_type` | string(10) | `EXC` · `DEV` · `BUYOUT` · `ETC` | 약정 구분 |
| `contract_milestones.sequence_no` · `title` | | 회차 · 항목명 | 상세 |
| `contract_milestones.target_month` | char(7) | 귀속월 | 귀속월 |
| `contract_milestones.unit_count` · `unit_price` · `amount` | | 건수 · 단가 · 금액(세전) | 약정 금액 |
| `contract_milestones.income_category` · `income_clause` | | 소득 구분 · 기타소득 호 | 소득 구분 · 게이트 A |
| `contract_milestones.approval_status` | varchar(20) NOT NULL, 기본 `pending` | `pending` · `approved` · `rejected` · `hold`(컬럼 주석은 3값, `hold`는 모델 상수 `APPROVAL_HOLD` — 2026_10_21_000241) | 검수 상태 |
| `contract_milestones.verify_method` · `review_note` · `approver_id` · `approved_at` | | 검수 방식 · 의견 · 승인자 · 처리 시각 | 검수 레이어 |
| `contract_milestones.transferred_at` · `settlement_line_id` | | 7단계 이관 시각 · 정산 라인 | 스코어카드 '이관 완료' |
| `contract_milestones.paid_at` | date | 지급 실행일(값 있으면 수정 불가) | — |
| `support_fund_agreements` · `contract_rate_lines`(SUPPORT) · `contract_term_targets` | | 게이트 B 원천 | 게이트 B |
| `rights_holders` 국세청 조회 칸 | | 게이트 C 원천 | 게이트 C |
| `exclusive_contract_fees` · `exclusive_contract_clawbacks` | | 전속계약금 · 중도해지 반환(탭 2 원천 후보) | 탭 2(미구현) |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `searchForm` · `input[name=target_month]` · `select[name=term_type\|approval_status]` · `input[name=keyword]` | 큐 검색 | `#searchInput` · `#typeFilter` |
| `[data-milestone-id]` 검수 버튼 | 검수 레이어 열기 | 큐 행 클릭 `selectItem()` |
| `layerMilestoneReview` · `milestoneReviewForm` | 검수 레이어 | 우측 상세 패널(`renderDetail`) |
| `msReviewId` · `msReviewDecision` | 대상 · 결정 | — |
| `msReviewSubject` · `msReviewAmount` · `msReviewGateWarn` | 대상 · 금액 · 게이트 경고 | 상세 게이트 박스 |
| `select[name=verify_method]` | 검수 방식 | `#editInspectMode` |
| `msReviewNote` · `msReviewCount` | 의견 · 글자 수 | `#editMemo` |
| `msApproveBtn` · `msRejectBtn` | 승인 · 반려 | `approveMilestone()` · `rejectMilestoneItem()` |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 검수 상태 `hold`(게이트 차단 보류) — 게이트 실패 상태로 승인 시도하면 보류로 남기고 사유를 의견에 붙임 — `MilestoneReviewService.php:284-301`
- 스코어카드 5종 — `milestones/index.blade.php:66-72`
- 귀속월 미지정 시 당월 고정 — `MilestoneReviewService.php:57-62`

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 탭 2 전속계약금 중도해지 일할 반환 · 지원금 종료 일시정산(LUMP_SETTLE) 산출표(L584)
- 탭 3 검수 · 수기 소명 감사 로그(L642)
- 상세에서 소득 구분 · 기타소득 호 · 귀속월 수정, 임시 저장 `saveDraft()`(L1483), R/S 대상 누락 보완 `fixMissingRsTargets()`(L1473), 국세청 재조회 버튼
- 증빙 파일 첨부(`#editEvidenceFile`) — 개발은 1차 미지원(`MilestoneReviewRequest.php:16-17`)
- 약정 유형 '개발지원금 (매출연동 R/S 체결 1회)' · 'LUMP_SETTLE' 구분(개발 term_type은 4종)
- 승인 후 자동 재연산 알림 모달 `recalcNoticeModal` · localStorage `sjm.settle.recalcEvents.v1`(L681-715)

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#typeFilter` `EXCLUSIVE_FEE` | `term_type` `EXC` |
| `SUPPORT_LUMP_INST` · `SUPPORT_RS_ONCE` | `DEV` (구분 없음) |
| `BUYOUT` | `BUYOUT` |
| `FLAT_ALLOWANCE` | `ETC` |
| `LUMP_SETTLE` | (없음) |
| `#editInspectMode` | `verify_method` |
| `#editMemo` | `review_note` |
| 식별자 `MS-2026-001` | `contract_milestones.code` (`MS-YYYY-NNN` 등) · 키는 `milestone_id` |

## 8. 정책 질문

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-INST002-1 | 검수 의견 최소 글자 수: 프로토 10자, 개발 20자. 정본 문서는 '필수'만 규정 | 01권 7.2절 '담당자 수기 소명형 검수'(`docs/[산준모 정산시스템]_01_…기획서.md:543`), 프로토 L1517-1520 | `app/Services/Admin/MilestoneReviewService.php:39`, `app/Http/Requests/Admin/MilestoneReviewRequest.php:31` **→ 결정(v6.92 white, D-PROD-07)**: 공백 제외 20자(반려 사유도 같음) — 개발 20자 검사가 공백을 빼고 세는지만 맞춘다 |
| Q-INST002-2 | 승인 시 정산서 자동 반영: 정본은 배치 실행 후 · 마감 전 승인이면 같은 트랜잭션에서 해당 권리자 1~11단계 재연산 + 알림 모달. 개발 승인은 상태만 바꾸고 "7단계로 인입됩니다" 안내, 재연산 호출 없음 | 01권 7.2절 '승인 시 정산서 자동 반영'(`:548`), 설계서 `:44` · `:508`, 프로토 L681-715 | `MilestoneReviewService.php:264-312`(재연산 호출 없음) |
| Q-INST002-3 | 귀속월 확정 위치: 정본은 검수 승인 때 귀속월을 확정(마감월 지정 차단). 프로토는 상세에서 귀속월을 고를 수 있음. 개발은 스케줄에 저장된 `target_month`를 그대로 쓰고 이 화면에서 바꿀 수 없음 | 01권 7.2절 '정산 반영 귀속월 확정 및 이관'(`:547`), 프로토 `#editTargetMonth` L1506 | `MilestoneReviewController.php:47-60`(귀속월 입력 없음) |
| Q-INST002-4 | 게이트 A 범위: 정본은 소득 구분 상위 축 · 기타소득 호 · **저작자 본인 여부(payee_is_author)** 미지정 시 승인 비활성. 개발 게이트 A는 앞의 두 값만 본다 | 01권 7.2절 '소득 구분 미지정 차단'(`:544`) | `MilestoneReviewService.php:109-125` |
| Q-INST002-5 | 증빙 첨부형 검수: 정본은 파일 첨부(선택) 방식 제공. 개발은 1차에서 파일을 받지 않고 선택지만 둠(첨부 다운로드 메뉴 미등록). 1차 범위로 확정해도 되는지 | 01권 7.2절 '증빙 첨부형 검수'(`:542`), 프로토 `#editEvidenceFile` | `MilestoneReviewRequest.php:16-17`, `app/Models/ContractMilestone.php:41-53` |
