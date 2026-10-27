# ADMN-PTNR-001 파트너 센터(권리자 · 강사 전용) — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-PTNR-001_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-PTNR-001 (탭 5: 홈 · 본인 정산서 · 학습 Q&A 관리 · 세금계산서 · 증빙 제출 · 내 정보, 모달 `modalQnaDetail`)
- 개발 진행: **개발 미구현(d562524a 기준), 규칙 기반 명명.** config/dev-progress.php 에 ADMN-PTNR 코드 자체가 없다. 관련 기능만 따로 있음: 강사 · 조교 역할 범위 제한(instructorScope), 학습 Q&A 관리(`admin.study-qnas.*`), 권리자 제공 정산서(`admin.settlement.statements.*`)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.partner-center.index` (규칙) | 파트너 센터 | 개발 미구현 |
| `admin.study-qnas.index` | 학습 Q&A 관리(기존) | routes/admin.php:807 — 강사 · 조교 역할은 `instructorScope()` 로 자기 강사 건만 본다 |
| `admin.settlement.statements.index` | 권리자 제공 정산서(기존, 관리자용) | routes/admin.php:563 |

- 개발의 역할 범위: 관리자 역할 코드 `instructor`(강사, instructors.user_id 연결) · `assistant`(조교, instructor_assistants) 만 가진 계정은 연결된 강사 id 목록으로 좁힌다. 다른 역할이 하나라도 있으면 제한 없음(null), 연결이 없으면 빈 목록(fail-closed)(app/Services/Admin/AdminPermissionService.php:75-105). 파트너 센터도 이 범위를 쓰면 된다(추정).
- 권리자(rights_holders) 본인 로그인 계정 연결 칸은 확인되지 않았다 — 권리자 ↔ 관리자 계정 연결은 instructors.user_id 경유뿐(추정).

## 2. 화면별 라우트
개발 미구현, 규칙 기반 명명(탭 = 하위 자원).
### ADMN-PTNR-001 파트너 센터
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 홈 | GET | `/{admin}/partner-center` (규칙) | `admin.partner-center.index` (규칙) | can_view | (규칙) PartnerCenterController@index |
| 본인 정산서 `?month=` | GET | `/{admin}/partner-center/statements` (규칙) | `admin.partner-center.statements.index` (규칙) | can_view | (규칙) |
| 정산서 PDF | GET | `/{admin}/partner-center/statements/download` (규칙) | `admin.partner-center.statements.download` (규칙) | can_download | (규칙) |
| 학습 Q&A 목록 | GET | `/{admin}/partner-center/study-qnas` (규칙) — 또는 기존 `admin.study-qnas.index` 재사용 | `admin.partner-center.study-qnas.index` (규칙) | can_view | (규칙) |
| 학습 Q&A 답변 · 보류 | PUT | `/{admin}/partner-center/study-qnas/{studyQna}` (규칙) — 기존 `admin.study-qnas.update` | `admin.partner-center.study-qnas.update` (규칙) | can_update | (규칙) |
| 증빙 목록 | GET | `/{admin}/partner-center/tax-documents` (규칙) | `admin.partner-center.tax-documents.index` (규칙) | can_view | (규칙) |
| 증빙 제출 | POST | `/{admin}/partner-center/tax-documents` (규칙) | `admin.partner-center.tax-documents.store` (규칙) | can_create | (규칙) |
| 내 정보 | GET | `/{admin}/partner-center/profile` (규칙) | `admin.partner-center.profile.show` (규칙) | can_view | (규칙) |

- 기존 관리자 학습 Q&A: `admin.study-qnas.index|show|update`, `admin.study-qnas.notifications.update`, `admin.study-qnas.files.show`(routes/admin.php:807-812).

## 3. 폼 필드 · 검증
### 학습 Q&A 답변 (기존 StudyQnaProcessRequest — 재사용 시)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `action` | required · in | `answer` 답변 · `escalate` 강사확인 요청 | 답변 등록(submitQnaAnswer) · 보류(holdQna) |
| `answer_content` | action=answer 면 required · 10자 이상 | 답변 본문 | 모달 답변 입력 |
| `is_public_qna` | nullable · boolean | 공개 Q&A 여부 | — |
| `notify` | nullable · boolean(기본 ON) | 답변 알림 | — |

### 세금계산서 · 증빙 제출 — 개발 미구현, 규칙 기반 명명
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `settlement_month` (규칙) | YYYY-MM | 대상 정산서 | (탭 표의 행) |
| `approval_no` (규칙) | 필수 | 승인번호 | `tiApproval` |
| `issued_date` (규칙) | 필수 · date | 작성일자 | `tiDate` |
| `supply_amount` (규칙) | 필수 · integer | 공급가액 (settlement_lines.supply_amount 와 같은 이름) | `tiSupply` |
| `vat_amount` (규칙) | 필수 · integer | 세액 (settlement_lines.vat_amount 와 같은 이름) | `tiVat` |
| `file` (규칙) | 필수 · PDF | 증빙 파일 | `tiFile` |

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` (규칙) | YYYY-MM | `stmtMonth` · shiftStmtMonth |
| `course_id` (규칙) | 강좌 | `qnaCourseFilter` |
| `status` | 기존 StudyQna::STATUS `pending` 미답변 · `answered` 답변완료 · `escalated` 강사확인 | `qnaStatusFilter` 답변대기 · 답변완료 · 보류 |

- 정산서 표 ↔ settlement_lines: 정산 귀속월 target_month · 세전 정산금 taxable_base · 세액 withholding_income_tax + withholding_local_tax / vat_amount · 선급금 차감 offset_amount · 세후 지급액 payable_amount · 상태 payout_hold_reason.

## 5. DB 테이블 · 컬럼
개발에 파트너 센터 전용 테이블 없음. 읽을 기존 테이블:
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| settlement_lines.(rights_holder_id · payee_id · target_month · taxable_base · vat_amount · withholding_income_tax · withholding_local_tax · offset_amount · payable_amount · payout_hold_reason) | | 본인 정산 | 본인 정산서 · 홈 |
| carryover_ledgers.(rights_holder_id · origin_month · amount · account_type) | | 이월 | 선급금 차감 · 이월 |
| study_qnas (status pending/answered/escalated) | | 학습 Q&A | 학습 Q&A 관리 |
| instructors.user_id · instructor_assistants | | 로그인 계정 ↔ 강사 연결 | 범위 판정 |
| rights_holders.(code · name · tax_type · bank_name …) | | 내 정보 | 내 정보 |
| 세금계산서 · 증빙 제출 저장 테이블 | — | 없음(개발 미구현) — 이름 규칙상 `tax_document_submissions` (규칙) | 증빙 제출 |
| site_settings `settlement_payout_day` (규칙, 기본 10) · `statement_dispute_reflect_days` (규칙, 기본 7) | int | 정산금 지급일(매월 10일, 휴일이면 다음 영업일) · 이번 지급 반영 기한(발행일 + 7일) — v6.92 S-04 · S-05 | 본인 정산서 `#stmtPayoutDate` · `#stmtDisputeDeadline` |

## 6. 개발 JS · 마크업 이름
개발 미구현, 규칙 기반 명명.
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `.tab__list .tab__item.active` (공통 탭) | 탭 5종 | switchPtnrTab |
| `#layerStudyQnaAnswer` · `#studyQnaAnswerForm` · `#studyQnaAnswerSubmit` (규칙) | Q&A 상세 · 답변 | `modalQnaDetail` |
| `#taxDocumentForm` · `#taxDocumentSubmit` (규칙) | 증빙 제출 | tiApproval 등 · submitTaxDoc |
| `.layer__open[data-target="layerReason"]` (공통) | 정산서 다운로드 사유(관리자 화면 규칙과 같게 할 경우) | downloadStatementPdf |

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 학습 Q&A 처리의 `escalate`(강사확인) · 공개 여부 · 답변 알림 토글, 첨부 파일 받기 — 기존 관리자 화면 기능.
- 강사 · 조교 역할 범위 제한(fail-closed).
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 파트너 센터 화면 전체(홈 요약 · 본인 정산서 월 이동 · PDF · 증빙 제출 · 내 정보).
- 세금계산서 · 증빙 제출 저장 — SETT-002 의 증빙 탭(evidence)도 개발에서 비활성이다.
- 이름 · 아이디 마스킹 표시(ptnrMaskName · ptnrMaskId).
- (v6.92) 본인 정산서의 지급일 줄(`#stmtPayoutDate` — 지급 완료 · 이월 차월 합산 · 지급 없음 · 반환 청구 구분)과 이번 지급 반영 기한 줄(`#stmtDisputeDeadline`). **→ 결정(v6.92 white, S-04 · S-05)**: 정산금 지급일 매월 10일(휴일이면 다음 영업일), 이견은 '이번 지급 반영 기한'(기본 발행일 + 7일, 설정값)으로만 적고 기한 후 이견 불가 · 승인 간주는 넣지 않음 — ADMN-SETT-002-S2와 같은 문구.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `qnaStatusFilter` 답변대기 · 답변완료 · 보류 | `status` pending · answered · escalated(강사확인) — "보류" 대응 값 없음 |
| 정산서 열 이름 | settlement_lines 컬럼(4절) |
| `tiSupply` · `tiVat` | `supply_amount` · `vat_amount` (규칙, 기존 컬럼명) |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 파트너 센터 로그인 주체 — 개발은 관리자 계정 + 강사/조교 역할로만 범위를 좁힌다. 강사가 아닌 권리자(저자 · 소속사 · 상속인)가 쓰는 경로가 없다. **→ 정본대로(POLICY_D_SETT A, 통합설계서 L49 · L455 · README L91 · PROJECT_STATE 1절)**: 권리자 소속 강사 · 저작권자(2계층 수취인 포함) 전용, 조교는 내부 직원이라 제외, 데이터 범위는 계정 소속 — 개발팀 전달
- 확인 필요: 학습 Q&A "보류" 상태 — 개발 상태값은 미답변 · 답변완료 · 강사확인 3종. **→ 정책 아님(POLICY_D_SETT B)**: 화면 · 이름 문제로 처리 — 프로토를 개발 3종에 맞추고 '보류'는 빼거나 내부 메모로

## 출처
- config/dev-progress.php (ADMN-PTNR 항목 없음)
- app/Services/Admin/AdminPermissionService.php:75-105
- routes/admin.php:563-564, 807-812
- app/Http/Requests/Admin/StudyQnaProcessRequest.php (dev_spec/_index/requests.md:3401)
- app/Models/StudyQna.php:15-19
- dev_spec/_index/schema.md settlement_lines(2617) · carryover_ledgers(2141)
