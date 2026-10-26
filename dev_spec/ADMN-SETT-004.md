# ADMN-SETT-004 PG 정산 원장 대사 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-004_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-004 · ADMN-SETT-004-S1(PG 대사 차이 상세)
- 개발 진행: 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 5건). S1 은 dev-progress 초기값 "2차"(DECISIONS 105)이나 d562524a 에 상세 페이지 · 소명 승인이 들어와 있다

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.pg-reconciliations.index` | PG 정산 원장 대사 | 라우트 정규화 규칙(…index). 운영 DB 행은 저장소 시드가 없어 미확인 |

- show · store · update 모두 같은 메뉴 권한 행을 쓴다. 감사 로그 탭은 `admin.admin-logs.index` 로 이동 버튼만 둔다(index.blade.php:182).

## 2. 화면별 라우트
### ADMN-SETT-004 PG 대사 워크스페이스
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(월 · 탭 · 필터) | GET | `/{admin}/settlement/pg-reconciliations` | `admin.settlement.pg-reconciliations.index` | can_view | PgReconciliationController@index |
| PG 원장 배치 재대사 실행 | POST | `/{admin}/settlement/pg-reconciliations` | `admin.settlement.pg-reconciliations.store` | can_create | PgReconciliationController@store |

### ADMN-SETT-004-S1 PG 대사 차이 상세(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 차이 건 상세 | GET | `/{admin}/settlement/pg-reconciliations/{item}` | `admin.settlement.pg-reconciliations.show` | can_view | PgReconciliationController@show |
| 차이 소명 승인(마감 차단 해제) | PUT | `/{admin}/settlement/pg-reconciliations/{item}` | `admin.settlement.pg-reconciliations.update` | can_update | PgReconciliationController@update |

- `{item}` = pg_reconciliation_items.id (숫자 18자리까지, routes/admin.php:609 주석). 상세 · 승인 후 목록 조건 `month · tab · reason · method` 를 유지한다(KEEP).

## 3. 폼 필드 · 검증
### 재대사 실행 (PgReconciliationRunRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` | required · date_format:Y-m | 대사 귀속월 | `monthSelect` + "🔄 PG 원장 배치 재대사 실행" |

### 차이 소명 승인 (PgReconciliationApproveRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `mismatch_reason_code` | required · in REASON_LABELS | `UNKNOWN_MISMATCH`(미분류 · 마감차단) · `TIMING_GAP`(기간 귀속차) · `PARTIAL_CANCEL_PENDING`(부분취소 처리 대기) · `PG_FEE_DIFF`(PG 수수료 원단위 차감차) · `REFUND_TIMING_DIFF`(환불 처리 시차) | 상세 원인 코드 선택 |
| `explanation` | required · string 10~500 (trim) | 차이 소명 근거(감사 로그 필수) | 소명 입력 · approveReconciliation |

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` | YYYY-MM (월 버튼 · `#monthPick`) | `monthSelect` |
| `tab` | `workspace`(1. PG 원장 1:1 대사 및 소명 워크스페이스) · `tax`(2. 복합 결제 3계층 과·면세 분할…) · `timing`(3. 가상계좌 · 실시간 계좌이체 복구 시차 점검) · `audit`(4. 대사 · 소명 감사 로그) | tabRecon · tabTaxSplit · tabVbank · tabAudit |
| `reason` | '' 전체 + REASON_LABELS 5종 | `reasonFilter` |
| `method` | '' 전체 결제수단 · `CARD` 신용카드 · `VIRTUAL_ACCOUNT` 가상계좌 · `BANK_TR` 실시간 계좌이체 | `methodFilter` |

- 워크스페이스 표(_tab-workspace.blade.php:63-70): PG TID / 주문번호 · 수단 / 일시 · 자체 DB 금액 · PG 원장 금액 · 대사 차액 · 차이 원인 코드 · 귀속 권리자 / 소명·통제 상태 · 관리([상세] → S1).
- 시차 탭 표(index.blade.php:149-153): PG TID · 결제 일시 · 대사 차액 · 차이 원인 코드 · 대사 판정.
- S1 표: 귀속 권리자(권리자 · 지분(스냅샷) · 몫(스냅샷) · 목록 대표), 품목 안분(품목 ID · 품목명/유형 · 1층 공급유형 · 2층 카테고리 · 3층 부가세 · 정가 · 쿠폰·포인트 안분할인 · 실결제 배분액 · 정산 파이프라인 귀속).
- 프로토타입 `searchInput`(주문번호 검색)은 개발에 없다.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| pg_reconciliations.settlement_month · our_count · our_amount · pg_count · pg_amount · mismatch_count · diff_amount | | 월 대사 헤더 | KPI |
| pg_reconciliations.status | string(30) | draft / matched / mismatched / confirmed | 월 상태 |
| pg_reconciliations.is_locked · admin_id · confirmed_at | | 최종 매출 마감 락 | 재대사 버튼 비활성 |
| pg_reconciliation_items.pg_tid · order_no · paid_at | | PG 거래번호 · 주문번호 · 결제 일시 | 첫 칸 |
| pg_reconciliation_items.our_amount · pg_amount · diff_amount | integer | 자사 · PG · 차액 | 금액 열 |
| pg_reconciliation_items.match_status | string(30) | matched / amount_diff / missing_ours / missing_pg | 대사 판정 |
| pg_reconciliation_items.mismatch_reason_code | string(30) | 3절 5종 | 차이 원인 코드 |
| pg_reconciliation_items.explanation | string(500) | 소명 근거 | S1 |
| pg_reconciliation_items.approval_status | string(20) | UNRESOLVED 미소명 · PENDING_APPROVAL 분류 완료·승인 대기 · APPROVED 소명 승인 완료 · MATCHED 차액 0원 | 소명·통제 상태 |
| pg_reconciliation_items.approved_by · approved_at · rights_holder_id | | 승인자 · 대표 귀속 권리자 | |
| pg_reconciliation_item_holders.item_id · rights_holder_id · share_rate_snapshot · share_amount_snapshot · is_primary | | 권리자별 귀속 스냅샷(차단 판정은 전 권리자) | S1 귀속 권리자 표 |
| pg_settlement_records.* (settlement_month · pg_provider · payment_key · order_no · approval_no · type(payment/cancel) · amount · fee_amount · approved_at · raw_data) | | PG 원장 적재 | 원장 금액 |
| settlement_lines.payout_hold_reason = `PG_RECON_UNCLASSIFIED` | | UNKNOWN_MISMATCH 남은 권리자 지급 보류 | SETT-002 연동 |

출처: dev_spec/_index/schema.md pg_settlement_records(1360) · pg_reconciliations(1376) · pg_reconciliation_items(1394) · pg_reconciliation_item_holders(2773); app/Models/PgReconciliationItem.php:22-60.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 월 버튼 `.st-btn.st-btn--sm(.st-btn--pr=현재)` | 기준월 전환 | `monthSelect` |
| 재대사 폼(POST, hidden `month`) | 재대사 실행 | "🔄 PG 원장 배치 재대사 실행" |
| 탭 버튼 `.st-btn(.st-btn--pr)` `?tab=` | 탭 4종 | tabRecon 등 |
| 필터 폼 hidden `month` · `tab`, `#reason`(name reason) · `#method`(name method) · `#monthPick`(name month) | 워크스페이스 필터 | `reasonFilter` · `methodFilter` · `searchInput` |
| 승인 폼(PUT) `#mismatch_reason_code` · `#explanation` | S1 소명 승인 | renderDetail 영역 · approveReconciliation |
| `.st-btn` 계열 | 이 화면은 공통 `btn` 대신 `st-btn` 클래스를 쓴다 | — |

출처: resources/views/admin/settlement/pg-reconciliations/index.blade.php:11-182 · _tab-workspace.blade.php:8-114 · show.blade.php:77-191.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 귀속 권리자 스냅샷 표(지분 · 몫 · 목록 대표) — pg_reconciliation_item_holders.
- 감사 로그 탭에서 관리자 로그(`admin.admin-logs.index`) 이동.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- "⚡ 1,000원 이내 단수차액 자동 대체".
- 분류만 저장(saveClassificationOnly) — 개발은 원인 코드 + 소명을 한 번에 승인(update)만 한다.
- 주문번호 검색(`searchInput`).
- 감사 로그 표를 화면 안에 직접 그림 — 개발은 관리자 로그 화면으로 보낸다.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `monthSelect` | `month` |
| `reasonFilter` | `reason` (`#reason`) |
| `methodFilter` 신용카드 · 가상계좌 · 실시간 계좌이체 | `method` CARD · VIRTUAL_ACCOUNT · BANK_TR |
| tabRecon · tabTaxSplit · tabVbank · tabAudit | `tab` workspace · tax · timing · audit |
| 소명/통제 상태 라벨 | approval_status UNRESOLVED · PENDING_APPROVAL · APPROVED · MATCHED |
| 우측 상세 패널(selectRecord) | S1 별도 페이지 `…pg-reconciliations.show` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: "1,000원 이내 단수차액 자동 대체"가 개발에 없다 — 정본에서 1차 범위인지.
- 확인 필요: 프로토타입의 "분류만 저장(승인 대기)" 단계를 둘지 — 개발 approval_status 에 PENDING_APPROVAL 값은 있으나 그 상태로 바꾸는 라우트는 없다.

## 출처
- routes/admin.php:605-610
- app/Http/Controllers/Admin/PgReconciliationController.php (index · show · update · store · filters · keep)
- app/Http/Requests/Admin/PgReconciliationApproveRequest.php · PgReconciliationRunRequest.php
- app/Services/Admin/PgReconciliationScreenService.php:23-40, 49-107
- app/Models/PgReconciliationItem.php:22-60
- resources/views/admin/settlement/pg-reconciliations/index.blade.php · _tab-workspace.blade.php · show.blade.php
- config/dev-progress.php:80-81, 216
