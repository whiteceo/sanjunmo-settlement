# ADMN-SETT-006 합격 환급반 관리(정산 반영) — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-006_baseline.html (원본 상태: 319e3d4 v6.98)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- v6.98 정본 변경(정본 v3.2.24 · v4.0.15): 합격환급 = 기타소득 사례금 C17(20% + 지방 10%, 지급명세서 연 1회) — 원천징수 표시 변경, 새 입력 없음
- 포함 화면: ADMN-SETT-006 (프로토타입 상세 모달 `sett006DetailModal` → 개발은 상세 페이지)
- 개발 진행: 일부 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 2건). dev-progress 초기값 "2차"(DECISIONS 108 · 113 ② — 1차는 부담 방식 A 만, B · C 차감은 2차). d562524a 에는 A 확정만 있고 B · C 는 마감 보류

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.pass-refunds.index` | 합격 환급반 관리(정산) | 라우트 정규화 규칙. 운영 DB 행 미확인 |

- 회원 쪽 합격 환급 심사(`admin.pass-refunds.*`, PassRefundController)는 다른 화면이다 — 이 화면은 `admin.settlement.pass-refunds.*` 로 정산 차감 검수만 한다.

## 2. 화면별 라우트
### ADMN-SETT-006 합격 환급 정산 반영
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(월 · 탭 · 부담 옵션) | GET | `/{admin}/settlement/pass-refunds` | `admin.settlement.pass-refunds.index` | can_view | PassRefundSettleController@index |
| 환급 건 상세(별도 페이지) | GET | `/{admin}/settlement/pass-refunds/{claim}` | `admin.settlement.pass-refunds.show` | can_view | PassRefundSettleController@show |
| 정산 차감 확정(검수 승인) | PUT | `/{admin}/settlement/pass-refunds/{claim}` | `admin.settlement.pass-refunds.update` | can_update | PassRefundSettleController@update |

- `{claim}` = refund_claims.id (숫자 18자리까지). 목록 조건 KEEP = month · tab · burden.
- v6.92 반려(환급 불가 확정, S-03): 심사 상세 [⛔ 반려] `#hrfRejectBtn` → `openRejectModal()` → `#rejectModal` → `confirmReject()` = 개발 `admin.pass-refunds.update`(PUT `/{admin}/pass-refunds/{passRefund}`, PassRefundReviewRequest `action=reject`, 합격 환급 심사 메뉴 can_update).
- 일괄 확정 라우트 없음 — 건별 update 만.

## 3. 폼 필드 · 검증
### 정산 차감 확정 (PassRefundSettleRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `opinion` | required · string 10~500 (trim) | 검수 의견(감사 로그 reason) | 상세 모달 승인(approveSettlementDeduct) — 프로토타입은 의견 입력 없음 |

### 반려 (PassRefundReviewRequest action=reject) — v6.92 S-03
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `action` | required | `reject` | `confirmReject()` |
| `reject_reason` | reject일 때 required · `PassRefundService::REJECT_REASONS` | 개발 `name_mismatch` · `review_length` · `bankbook_unreadable` · `link_unavailable` · `other_round` · `other`(미확정 표시) | `#rejectCode`(JS `REJECT_REASONS`) NOT_PASSED · PROGRESS_SHORT · APPLY_EXPIRED · NAME_MISMATCH · REVIEW_REJECTED · ETC — **코드 목록 다름**, S-03 결정 목록으로 개발 상수를 맞출 것 |
| `reject_detail` | reject일 때 required · 10~1000자 | 고객 안내 문구(환급 불가 알림톡) | `#rejectNotice` |

- 금액은 입력받지 않는다. 옵션 A 면 rs_deduct_amount · support_deduct_amount 를 0 으로 확정, B · C 면 검증 오류("1차에서 차감을 확정할 수 없습니다 … 마감 보류")(app/Services/Admin/PassRefundSettleService.php:148-190).

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` | YYYY-MM (월 버튼 · `#monthPick`) — 정산 귀속월 | `topMonthSelect` |
| `tab` | `workspace`(1. 합격 환급 신청 검수 및 원거래 스냅샷 역참조 워크스페이스) · `mmg`(2. MMG 이중 부담 회피 & 지원금 C-01 캡 흡수 방지 검증) · `audit`(3. 환급 승인 감사 로그) | tabWorkspace · tabRules · tabAudit |
| `burden` | '' 전체 · `A` 플랫폼 전액 부담(기본값) · `B` 비율 공동 부담(4단계 공제) · `C` 매출 취소 처리(4단계 차감) | `burdenFilter` |

- 표(index.blade.php:119-126): 환급ID / 원주문(결제월) · 수강생 / 상품명 · 귀속 권리자 / 부담 옵션 · 수강생 환급액 · 4단계 R/S 공제(BASIC) · 4·5단계 지원금 공제(P5.1) · 검수 상태 · 관리([상세]).
- 대상: refund_claims.status = paid(RefundClaim::STATUS_PAID) 이고 settlement_target_month 가 그 달(app/Repositories/Admin/PassRefundSettleRepository.php:32-53, 120-142).
- 상세(show.blade.php:66-69): 귀속 권리자 표(권리자 · 계약 · 부담 옵션 · 1차 처리) + `#opinion` + [정산 차감 확정](A 만 활성).
- MMG 탭 표(_tab-mmg.blade.php:24-30, 73-75): 구분 · 2단계 순수 신규 R/S · 3단계 MMG 판정 모수 · 3단계 플랫폼 MMG 보전금 · 4단계 옵션 C 차감 · 권리자 최종 세전 수령액 · 재무 영향 판정 / 연산 단계 설명.
- 감사 탭: 관리자 로그(`admin.admin-logs.index`)로 이동, sub_action `pass_refund_settle_confirm`.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| refund_claims.id · user_id · order_item_id · paid_at | | 환급 신청 · 대상 라인 · 지급 일시 | 환급ID / 원주문 |
| refund_claims.status | string(30) | received / reviewing / approved / rejected (컬럼 주석) — 모델 STATUS_PAID 로 거름 | — |
| refund_claims.rs_deduct_amount | integer null | 4단계 R/S 공제액. A=0 / B·C=NULL | 4단계 R/S 공제 |
| refund_claims.support_deduct_amount | integer null | 4·5단계 지원금 공제액. A=0 / B·C=NULL | 지원금 공제 |
| refund_claims.settlement_target_month | char(7) null | 정산 귀속월(승인 확정일 기준, 원 결제월로 소급하지 않음) | 월 |
| refund_claims.settle_review_status | string(20) null | PENDING 검수 대기 · CONFIRMED 차감 확정 · HOLD 마감 보류(B·C) | 검수 상태 |
| refund_claims.settle_reviewed_by · settle_reviewed_at | | 검수자 · 일시 | 상세 |
| rights_holder_contracts.refund_promo_burden_type | string(1) | A 플랫폼 전액 · B R/S 지분율 비율 분담 · C 매출 취소 | 부담 옵션 |
| lecture_instructors (course_lectures 경유) | | 귀속 권리자 판정 | 귀속 권리자 |
| settlement_lines.payout_hold_reason = `REFUND_BURDEN` | | B · C 권리자 마감 보류 | SETT-002 |

출처: dev_spec/_index/schema.md refund_claims(1290~) · rights_holder_contracts(2015).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 월 버튼 `.st-btn(.st-btn--pr)` `?month=` | 귀속월 | `topMonthSelect` |
| 탭 버튼 `.st-btn` `?tab=` | 탭 3종 | tabWorkspace · tabRules · tabAudit |
| 필터 폼 hidden `month` · `tab`, `#burden`(name burden), `#monthPick`(name month) | 필터 | `burdenFilter` |
| 상세 페이지 폼(PUT) `#opinion` | 검수 의견 + 확정 | `sett006DetailModal` |

출처: resources/views/admin/settlement/pass-refunds/index.blade.php:11-197 · show.blade.php:66-143.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 검수 의견(`opinion`, 10자 이상) 입력.
- B · C 건 확정 차단 + 마감 보류(HOLD) 상태.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 필터 원 결제월(`fOriginMonth`) · 강사(`fInstructor`) · 상태(`fStatus`) · 통합 검색(`searchInput`).
- 체크박스 일괄 확정(`chkAll` · approveSelectedItems), 정산 대사용 엑셀 다운로드, KPI "해당 건만 보기".
- 4대 제출증빙 확인 · 인정 진도율 열, 재계산 안내 모달(`recalcNoticeModal`, localStorage `sjm.settle.recalcEvents.v1`).
- 감사 이력 표를 화면 안에 그림 — 개발은 관리자 로그로 보낸다.
- 반려 상태 `REJECTED`(⛔ 환급 불가 확정) · 반려 모달 **→ 결정(v6.92 white, S-03)**: 사유 코드 + 고객 안내 필수, 종결 · 정산 차감 없음 · 지급 없음, 계좌 문제는 새 상태 없이 보완 요청, 지급은 월 1회 심사 승인월 익월 10일(설정값) — 개발은 반려(action=reject)가 있으나 사유 코드 목록이 다름(3절)
- 원천징수용 주민등록번호 행 · 본인인증 실명 대조(`#hrfRrnRow`, 미입력 · 불일치면 승인 불가) · 환급금 지급 예정일(`#hrfPayoutRow`) **→ 결정(v6.92 white, S-02 · S-03)**: 주민번호 항상 받음(번호만 · 암호화, 신분증 사본 없음) — 개발 심사 체크 항목 대응 확인 필요
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `topMonthSelect` | `month` |
| `burdenFilter` 옵션 A/B/C 라벨 | `burden` A · B · C |
| `fStatus` 차감 승인 대기 / 정산 반영 완료 / 반려(REJECTED, v6.92) | settle_review_status PENDING / CONFIRMED (+HOLD) · 반려는 refund_claims.status `rejected` |
| `sett006DetailModal` | `admin.settlement.pass-refunds.show` 페이지 |
| 강사료(R/S) 차감액 · 개발지원금 차감 | rs_deduct_amount · support_deduct_amount |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 프로토타입은 B · C 건도 차감액을 계산해 확정하는 흐름인데, 개발 1차는 B · C 를 HOLD(마감 보류)로 둔다(DECISIONS 113 ②). 프로토타입에 "2차" 표시를 둘지. **→ 결정(white 10-27, D-SETT-02)**: B · C 부담 계약이 실제로 있음 → 1차에 B · C 차감 연산 구현(개발 HOLD 해제 전달), 프로토에 '2차' 표시 안 함
- 확인 필요: 일괄 확정(체크박스) 유지 여부 — 개발은 건별 검수 의견 필수. **→ 정본대로(POLICY_D_SETT A, 02권 §10.1 L356)**: 일괄 확정은 정본 기능(권리자별 1회 재연산) — 유지, 검수 의견은 일괄 모달 공통 1칸 가능(개발팀 전달)

## 출처
- routes/admin.php:617-620
- app/Http/Controllers/Admin/PassRefundSettleController.php
- app/Http/Requests/Admin/PassRefundSettleRequest.php
- app/Services/Admin/PassRefundSettleService.php:29-44, 148-196
- app/Repositories/Admin/PassRefundSettleRepository.php:32-142
- resources/views/admin/settlement/pass-refunds/index.blade.php · show.blade.php · _tab-mmg.blade.php
- config/dev-progress.php:84, 220
