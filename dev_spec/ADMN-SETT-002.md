# ADMN-SETT-002 월간 정산 및 집행 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-002_baseline.html (원본 상태: 319e3d4 v6.98)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- v6.98 정본 변경(정본 v3.2.24 · v4.0.15): 마감된 달 정정 · 보정 전표는 차월 세금 계산 직전 반영(세전 · 위탁 9단계, 세후 10단계, 02권 10.2) — 안내 문구 변경, 새 입력 없음
- 포함 화면: ADMN-SETT-002 · ADMN-SETT-002-S1 · ADMN-SETT-002-S2 · ADMN-SETT-002-P1(이월 발생 내역) · ADMN-SETT-002-P2(마감 게이트)
- 개발 진행: 일부 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 9건). 탭 중 "증빙 승인 현황"(evidence)은 enabled=false, 개발지원금 소진 원장 · 은행 결과 파일 대사는 없음

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.board.index` | 월간 정산 및 집행 | 라우트 정규화 규칙 + 엑셀 메뉴 키 `EXCEL_MENU`(app/Http/Controllers/Admin/SettlementBoardController.php). 운영 DB 행은 미확인 |
| `admin.settlement.statements.index` | 권리자 제공 정산서(S2) | 엑셀 메뉴 키 `EXCEL_MENU`(app/Http/Controllers/Admin/SettlementStatementController.php). 별도 메뉴 행이 없으면 `admin.settlement.index` 로 올라감 — 메뉴 행 존재 미확인(추정: 별도 메뉴) |

- `…board.memos.store` · `…board.close.store` · `…board.carryovers.show` 는 정규화 후 하위 자원 세그먼트를 걷어 `admin.settlement.board.index` 권한을 쓴다(app/Services/Admin/AdminPermissionService.php:433-476).
- 예외: `admin.settlement.board.download`(이체 리스트)는 ROUTE_PERMISSIONS 로 **can_download + can_update** 둘 다 요구(AdminPermissionService.php:358-367).
- 마감 확정은 라우트 권한(can_create) 외에 서비스가 재무팀 · 최고 관리자로 다시 판정(routes/admin.php:549 주석, SettlementClosePermissionException).

## 2. 화면별 라우트
### ADMN-SETT-002 월간 정산 보드
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 보드(월 · 탭 · 필터) | GET | `/{admin}/settlement/board` | `admin.settlement.board.index` | can_view | SettlementBoardController@index |
| 이체 리스트 엑셀(사유 필수) | GET | `/{admin}/settlement/board/download` | `admin.settlement.board.download` | can_download + can_update | SettlementBoardController@download |
| 1~11단계 배치 재실행 | POST | `/{admin}/settlement/board/recalculate` | `admin.settlement.board.recalculate` | can_update | SettlementBoardController@update |

### ADMN-SETT-002-P2 당월 정산 마감 확정(모달)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 마감 확정 | POST | `/{admin}/settlement/board/close` | `admin.settlement.board.close.store` | can_create (+서비스 재판정) | SettlementBoardController@store |

### ADMN-SETT-002-S1 통합 정산서 상세(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 권리자 상세 `?month=` | GET | `/{admin}/settlement/board/{rightsHolder}` | `admin.settlement.board.show` | can_view | SettlementBoardController@show |
| 재무팀 검토 메모 등록 | POST | `/{admin}/settlement/board/memos` | `admin.settlement.board.memos.store` | can_create | SettlementBoardController@storeMemo |

### ADMN-SETT-002-P1 이월 발생 내역(모달 조각)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 권리자 이월 내역 `?month=` | GET | `/{admin}/settlement/board/{rightsHolder}/carryovers` | `admin.settlement.board.carryovers.show` | can_view | SettlementBoardController@carryover (뷰 `_carryover-modal`) |

### ADMN-SETT-002-S2 권리자 제공 정산서(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 미리보기 `?month=&rights_holder_id=` | GET | `/{admin}/settlement/statements` | `admin.settlement.statements.index` | can_view | SettlementStatementController@index |
| 정산서 엑셀(사유 필수) | GET | `/{admin}/settlement/statements/download` | `admin.settlement.statements.download` | can_download | SettlementStatementController@download |

- S2 는 `guard($month, $rightsHolderId)` 가 막으면(추정: 미마감 등) 문구만 보이고 미리보기를 그리지 않는다(SettlementStatementController.php index · download).
- v6.92 S2 표시 추가(입력 없음): 지급일 박스 `#s2PayoutDateBox`(S-04 — 매월 10일, 휴일이면 다음 영업일 · 최소 지급액 미달은 차월 합산 · 반환 청구는 지급 없음) · 이번 지급 반영 기한 `#s2DisputeDeadlineBox`(S-05 — 발행일 + 설정값 기본 7일, 설정 키 (규칙) `site_settings.stmt_dispute_reflect_days`, 기한 뒤 이견도 접수는 막지 않고 SETT-005 정정 대상 안내).

## 3. 폼 필드 · 검증
### 배치 재실행 (SettlementBoardRecalculateRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` | rules() 비어 있음 · `stringInput('month')` | YYYY-MM 데이터 기준월 | "⚙️ 1~11단계 통합 연산 배치 재실행" |

### 마감 확정 (SettlementBoardCloseRequest) — `#settlementCloseForm`
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` | hidden · stringInput | 보고 있는 기준월 | modal-sett-gate |
| `confirm_month` | 담당자 직접 입력, `month` 와 다르면 실행 안 함 | YYYY-MM | (프로토타입에 입력칸 없음 — 최종 확정 버튼만) |

### 검토 메모 (SettlementMemoRequest) — S1
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` | stringInput | 기준월 | |
| `rights_holder_id` | required · integer ≥1 | | selS1Holder |
| `payee_id` | nullable · integer ≥1 | NULL=권리자 단위 메모 | |
| `memo` | required · string 2~2000 | | `inpS1NewMemo` |

### 다운로드 사유 (ReasonRequest — 공통 `#layerReason`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `reason` | required · in | refund_account(환불 계좌 확인) · delivery_error(배송 오류 확인) · identity_check(본인 확인 요청) · payment_inquiry(결제 오류 조사) · legal_request(법적 요청 대응) · settlement_check(정산 · 지급 확인) · etc(기타(직접 입력)) | 프로토타입 다운로드 버튼에 사유 모달 없음 |
| `reason_ref` | nullable · ≤50 · 영숫자 - | 관련 문의 · 주문번호 | |
| `reason_etc` | etc 일 때 필수(10~150자) | | |
| `month` · `rights_holder_id` | 쿼리 | | |

## 4. 목록 필터 · 정렬 · 표 컬럼
### 보드 쿼리 (index)
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` | YYYY-MM, 월 탭(`.tab__list > .tab__item.active`) | `monthSelect` |
| `tab` | `summary`(통합 정산서) · `evidence`(증빙 승인 현황, 비활성) · `transfer`(이체 리스트) · `carryover`(이월 잔액) | tabStatements · tabTaxInvoice · tabFirmbanking (tabSupportLedger 대응 없음) |
| `pipeline` | `P1_1` 온라인 강좌 수익배분(1.1) · `P2_1` 자사 발행 도서 인세(2.1) · `P2_2` 위탁 도서 판매대금(2.2, 1차 미수집 "—") · `P5_1` 매출연동 개발지원금(5.1) | `pipelineFilter` |
| `state` | `payable` 지급 확정 · `carried` 지급 이월 · `hold` 마감 보류 · `tax_pending` 세무 판정 보류 · `internal` 자사 귀속 | 집행 판정 열 |
| `hold_reason` | settlement_lines.payout_hold_reason 값(5절) | 없음 |
| `keyword` | rights_holders.name · code LIKE | `searchInput` |

- 스코어카드(index.blade.php:143-147): 당월 정산 대상 수취인 · 당월 실지급 대상(≥10만원/강제) · 지급 보류 · 차월 이월 적재 · 마이너스 청구서 발행(10단계) · 2채널 역발행 · 수취 증빙 대기.
- 배치 모니터 4묶음(SettlementBoardService.php:126-143): collect 집계(1~2단계) · adjust 보정(3~5) · split 분배(6~8) · tax 과세 · 집행(9~11), 상태 pending · failed · done.
- 통합 정산서 표(_tab-summary.blade.php:65-74): 권리자(코드) · 수취인 · 구분별 금액(P1_1 · P2_1 · P2_2 · P5_1) · 과세표준 · 원천세 · VAT · 실지급 · 상태 · 관리, 합계 행(실지급은 자사 권리자 제외). 정렬 rights_holder_id, COALESCE(payee_id, rights_holder_id).
- 이체 리스트 표: 권리자(코드) · 수취인 · 은행 · 계좌 · 예금주 · 이체 금액. 엑셀 헤더: 권리자코드 · 권리자 · 수취인 · 은행 · 예금주 · 이체 금액.
- 이월 잔액 표: 권리자(코드) · 발생월 · 계정 · 트랙 · 사유 · 소득 구분 · 금액 · 지급 예약.
- S1 표: 정산 입력 구분 · 분할 기준액 · 선급금 상계 · 과세표준 · 원천세 · VAT · 지급 예정 · 상태 / 단계별 중간값 / 메모 이력(작성 일시 · 작성자 · 내용, 최신순).
- S2: 머리(공급자 · 발행일 · 지급 예정일 · 이견 제기 기간 · 입금 계좌) + 표(구분 · 과세표준 · 공급가액 · 부가세 · 선급금 상계 · 원천징수 · 실지급액) + 합계(과세표준 · 실지급액 · 원천징수 · 선급금 상계 · 이월 잔액). 엑셀 파일명 `권리자정산서_<documentNo>`.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| settlement_closings.target_month | char(7) unique | 데이터 기준월(월 1행) | 월 탭 |
| settlement_closings.locked_yn | boolean | 마감 잠금. 해제 경로 없음 | 마감 상태 · 재실행 버튼 비활성 |
| settlement_closings.aggregated_at / confirmed_at / admin_id | | 마지막 집계 · 마감 확정 일시 · 확정자 | 배치 모니터 · 마감 |
| settlement_lines.rights_holder_id / payee_id | | 원 권리자 / 수취인(NULL=분할 없음) | 권리자 · 수취인 |
| settlement_lines.target_month | char(7) | 기준월 | |
| settlement_lines.pipeline_id | string(10) | P1_1 · P2_1 · P5_1 · LUMPSUM (보드 상수는 P1_1 · P2_1 · P2_2 · P5_1) | 구분별 금액 열 |
| settlement_lines.payee_split_base · offset_amount · taxable_base · supply_amount · vat_amount · withholding_income_tax · withholding_local_tax · payable_amount | integer | 8단계 분할 기준액 · 선급금 상계 · 과세표준 · 공급가액 · VAT · 소득세 · 지방소득세 · 11단계 지급 예정액 | 표 금액 열 |
| settlement_lines.tax_decision_status | string(20) | DECIDED / PENDING_REVIEW | 상태 tax_pending |
| settlement_lines.matrix_case_id · income_category(BUSINESS/OTHER) · income_clause | | 세무 매트릭스 케이스 · 소득 구분 | 세무 매트릭스 |
| settlement_lines.payout_hold_reason | string(30) null | TAX_PENDING 세무 판정 보류 · NTS_EXPIRED 사업자 확인 90일 경과 · PENDING_VERIFY 임시 등록 확인 대기 · PAYEE_SPLIT 수취인 분할 2차 지원 · REFUND_BURDEN 환급 부담 B · C 2차 지원 · PG_RECON_UNCLASSIFIED PG 대사 미분류 불일치 | 상태 배지 · 보류 사유 필터 |
| carryover_ledgers.origin_month · account_type(PRE_TAX/POST_TAX) · track(A/B1/B2/S/MIXED) · reason(payout_under/claim_under/post_close_fix) · amount · is_expired · payout_reservation_status(NONE/RESERVED/SETTLED) | reason varchar(30) NOT NULL | 이월 원장 | P1 · 이월 잔액 탭 |
| settlement_review_memos.settlement_month · rights_holder_id · payee_id · memo · created_by · created_at | | 재무팀 검토 메모(수정 · 삭제 없음) | S1 메모 |
| rights_holders.code · name · is_internal · tax_type | | 권리자 원장 | 권리자 열 |

출처: dev_spec/_index/schema.md settlement_lines(2617) · settlement_closings(2648) · carryover_ledgers(2141) · settlement_review_memos(2704); app/Models/SettlementLine.php:21-76; app/Repositories/Settlement/SettlementBoardRepository.php:26, 296-372.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `.tab__list .tab__item.active` (`?month=`) | 기준월 탭 | `monthSelect` |
| 탭 링크 `?tab=summary|transfer|carryover` | 보드 탭 | tabStatements · tabFirmbanking 등 |
| 검색 폼(GET, hidden `month` · `tab`) | 통합 정산서 필터 | searchInput · pipelineFilter |
| `#settlementCloseModal`(`.layer_pop`) · `#settlementCloseForm` · `#settlementConfirmMonth`(name `confirm_month`) · `#settlementCloseSubmit` | P2 마감 모달 | `modal-sett-gate` |
| `.layer__open[data-target="layerReason"][data-action][data-method="get"]` | 이체 리스트 엑셀 사유 모달 | "📥 대량이체 엑셀 다운로드" |
| `.layer__open[data-target="layerReason"][data-reason-action][data-reason-title][data-reason-submit][data-reason-lead]` | S2 다운로드 사유 모달 | modalStatementS2 |
| 메모 폼 (name `month` · `rights_holder_id` · `memo`) | S1 메모 | `inpS1NewMemo` · saveS1AuditMemo |
| `_carryover-modal` 조각(이월 내역 엑셀 버튼 disabled "2차 구현") | P1 | `modalCarryoverP1` |

출처: resources/views/admin/settlement/board/index.blade.php · _tab-summary.blade.php · _tab-transfer.blade.php:9-12 · _close.blade.php:52-113 · show.blade.php:109-153 · statements/index.blade.php:36-95.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 기준월 탭 · 배치 모니터 4묶음 상태 · 이월 잔액 탭.
- 필터 `state` · `hold_reason`, 보류 사유 코드 6종(PG_RECON_UNCLASSIFIED 포함).
- 마감 모달의 기준월 직접 입력(`confirm_month`) 확인.
- 다운로드 사유 입력(ReasonRequest) — 이체 리스트 · S2.
- S1 → 수동 조정 등록(`admin.settlement.adjustments.show`) · 보드 · 이월 · S2 링크(show.blade.php:141-153).
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 탭 2 개발지원금 소진 원장(tabSupportLedger).
- 탭 3 2채널 증빙 제출 · 홈택스 대사 · 위탁 계산서 수취(modalTaxSubmit · 재발송 · 홈택스 업로드) — 개발 `evidence` 탭 비활성.
- 탭 4 은행 이체 결과 파일 등록 · 1:1 대사 · 송금 실패 시연 — 개발은 이체 리스트 엑셀만.
- S2 정산금 지급일 표기(`#s2PayoutDateBox`) **→ 결정(v6.92 white, S-04)**: 매월 10일(휴일이면 다음 영업일), 최소 지급액 미달 이월은 차월 합산 지급 — 개발 S2 머리 '지급 예정일' 산출 규칙 확인 필요
- S2 '이번 지급 반영 기한'(`#s2DisputeDeadlineBox`) **→ 결정(v6.92 white, S-05)**: '이견 제기 기간' 대신 발행일 + 설정값(기본 7일) 반영 기한, 기한 경과로 이견 접수를 막지 않음 — 개발 설정 키 (규칙) `stmt_dispute_reflect_days`
- S1 "0원/미해당 테이블 전체 보기", 마스킹 해제, 단건 확정, 월 이동. S2 발송 대상 선택 · 발송.
- 이월 원장 P1 의 계정 필터(selP1AccountType) · 이월 엑셀(개발 disabled).
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| S1 · S2 · P1 모달(modalStatementS1/S2, modalCarryoverP1) | S1 `…board.show` 페이지, S2 `…statements.index` 페이지, P1 `…board.carryovers.show` 조각 |
| `monthSelect` | `month` (YYYY-MM) |
| `pipelineFilter` 라벨 | `pipeline` = P1_1 · P2_1 · P2_2 · P5_1 |
| `searchInput` | `keyword` |
| 집행 판정 라벨 | `state` = payable · carried · hold · tax_pending · internal |
| `inpS1NewMemo` | `memo` (+`rights_holder_id` · `payee_id`) |
| modal-sett-gate 최종 확정 | `#settlementCloseModal` + `confirm_month` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 개발 보드 상수에 `P2_2`(위탁 도서 판매대금)가 있으나 settlement_lines.pipeline_id 주석에는 P2_2 가 없고 `LUMPSUM` 이 있다(1차 미수집 처리). 프로토타입 표기와 일치 여부. **→ 정본대로(POLICY_D_SETT A, 02권 §8.3 L169 · L174 · 03권 L218)**: 2단계 입력은 P1_1 · P2_1 · P2_2 · P5_1, `LUMPSUM_ADD`는 7단계(파이프라인 아님) — 프로토가 정본과 같음, 개발 `pipeline_id` 주석 정리 전달
- 확인 필요: 이체 리스트 다운로드에 수정 권한까지 요구하는 규칙(ROUTE_PERMISSIONS)을 프로토타입 권한 안내에 반영할지. **→ 결정(v6.92 white, D-SETT-05)**: 쓰기(W) + 엑셀(X) 함께 필요(개발 규칙 그대로 확정), 프로토 탭 4에 안내 `#firmbankingPermNote` 추가

## 출처
- routes/admin.php:543-564
- app/Http/Controllers/Admin/SettlementBoardController.php (index · show · update · store · storeMemo · download · carryover)
- app/Http/Controllers/Admin/SettlementStatementController.php (index · download)
- app/Http/Requests/Admin/SettlementBoardRecalculateRequest.php:28-30 · SettlementBoardCloseRequest.php:28-36 · SettlementMemoRequest(dev_spec/_index/requests.md:3288) · ReasonRequest.php:48-56
- app/Services/Admin/SettlementBoardService.php:27-143
- app/Repositories/Settlement/SettlementBoardRepository.php:26, 296-372
- app/Models/SettlementLine.php:21-76
- app/Services/Admin/AdminPermissionService.php:358-367, 433-476
- resources/views/admin/settlement/board/*.blade.php · statements/index.blade.php
