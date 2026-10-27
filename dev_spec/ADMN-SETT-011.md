# ADMN-SETT-011 물류비 대사(3PL) — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-011_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-011 · ADMN-SETT-011-S1(물류비 대사 상세 — 프로토타입은 한 화면 + `modal-resolve`)
- 개발 진행: **개발 미구현(d562524a 기준), 규칙 기반 명명.** dev-progress 초기값 "2차"(DECISIONS 107 — 물류비 대사 1차 제외). 라우트 · 컨트롤러 · 뷰 없음, 테이블만 있음

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.logistics-reconciliations.index` (규칙) | 물류비 대사(3PL) | 개발 미구현. 같은 성격의 `admin.settlement.pg-reconciliations.index` 이름 규칙을 따름 |

## 2. 화면별 라우트
개발 미구현, 규칙 기반 명명. URL 접두사 `/{admin}/settlement/logistics-reconciliations`.
### ADMN-SETT-011 물류비 대사
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(월 · 탭 · 상태) | GET | `/{admin}/settlement/logistics-reconciliations` (규칙) | `admin.settlement.logistics-reconciliations.index` (규칙) | can_view | (규칙) LogisticsReconciliationController@index |
| 3PL 명세서 업로드 | POST | `…/logistics-reconciliations/statements` (규칙) | `admin.settlement.logistics-reconciliations.statements.store` (규칙) | can_create | (규칙) |
| 대사 실행 | POST | `…/logistics-reconciliations` (규칙) | `admin.settlement.logistics-reconciliations.store` (규칙) | can_create | (규칙) PG 재대사와 같은 모양 |
| 3PL 명세 · 매입 계산서 엑셀 | GET | `…/logistics-reconciliations/download` (규칙) | `admin.settlement.logistics-reconciliations.download` (규칙) | can_download (사유 ReasonRequest) | (규칙) |
| 대사 완료 처리(Lock) | PUT | `…/logistics-reconciliations/{settlement}/lock` (규칙) | `admin.settlement.logistics-reconciliations.lock.update` (규칙) | can_update | (규칙) |
### ADMN-SETT-011-S1 물류비 대사 상세 · 불일치 처리
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 불일치 처리 저장(`modal-resolve`) | PUT | `…/logistics-reconciliations/items/{item}` (규칙) | `admin.settlement.logistics-reconciliations.items.update` (규칙) | can_update | (규칙) |

## 3. 폼 필드 · 검증
개발 미구현, 규칙 기반 명명(컬럼 이름 기준).
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` (규칙) | YYYY-MM | 정산월 = logistics_settlements.settlement_month | `month-select` |
| `statement_file` (규칙) | 엑셀 파일 | 3PL 명세서 | 명세서 업로드(uploadStatement) |
| `resolve_result` (규칙) | 선택 필수 | 승인 지급 · 차감 요청 · 차월 이월 — 코드값 개발에 없음 | `resolve-result` |
| `memo` | 필수("사유 없이 종결할 수 없다" — 컬럼 주석) | logistics_settlement_items.memo | `resolve-memo` |

## 4. 목록 필터 · 정렬 · 표 컬럼
개발 미구현. 프로토타입 기준 + 컬럼 대응:
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` (규칙) | YYYY-MM | `month-select` |
| `tab` (규칙) | `outbound`(출고 · 수수료) · `shipping`(배송비 · 반품) · `books`(도서 매입 계산서) (규칙) | switchTab 3종 |
| `match_status` | matched 일치 · billed_only 3PL만 존재 · ours_only DB만 존재 · qty_diff 수량 차이 · price_diff 단가 차이 (컬럼 주석 값) | `flt-status` |

- 출고 표 ↔ logistics_settlement_items: 출고일 shipped_at · 송장번호 tracking_no · 주문번호 order_no · 수령인 receiver_name · 수량 quantity · DB 출고 our_shipped · 3PL 청구 billed · 단가 unit_price · 차이 diff_amount · 처리 결과 · 메모 memo.
- 도서 매입 표 ↔ book_purchase_costs: 도서명 book_name · 매입처 publisher · 수량 sold_qty/returned_qty/net_qty · 사입 원가 unit_cost · 매입액 total_cost · 수취 상태 match_status(matched/calc_diff).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| logistics_settlements.settlement_month | char(7) | 정산월 | 월 |
| logistics_settlements.our_delivery_count · our_delivery_amount · our_return_count · our_return_amount | integer | 자사 집계 배송 · 반품 | 배송비 · 반품 대사 |
| logistics_settlements.billed_delivery_count · billed_delivery_amount · billed_return_count · billed_return_amount | integer | 3PL 청구 | 3PL 청구(지급) |
| logistics_settlements.book_cost_amount · diff_amount | integer | 사입 원가 합계 · 차액 | 요약 |
| logistics_settlements.status | string(30) | draft / matched / mismatched / confirmed | 대사 상태 |
| logistics_settlements.is_locked · admin_id · confirmed_at · memo | | 물류 정산 Lock(재무 마감 [2]단계, SETT-004 매출 마감 이후) | 대사 완료 처리 |
| logistics_settlement_items.* | | 위 4절 | 출고 표 |
| book_purchase_costs.* | | 위 4절 | 도서 매입 계산서 대조 |
| delivery_batches.batch_no · type(export/import) · status | | 3PL 발주 배치 | 매칭 키 |
| deliveries.batch_id · ship_ordered_at · fee_type(FREE/PREPAID/ISLAND) | batch_id bigint unsigned nullable(delivery_batches.id) | 출고 지시 · 배송비 구분 | 매칭 |

출처: dev_spec/_index/schema.md logistics_settlements(1337) · delivery_batches(1273) · logistics_settlement_items(1665) · book_purchase_costs(1685~); database/migrations/2026_08_14_000015 · 2026_09_08_000079.

## 6. 개발 JS · 마크업 이름
개발 미구현, 규칙 기반 명명(README 명명 규칙: camelCase, 모달 `layer<기능>`, 폼 `<기능>Form`).
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#searchForm` (규칙) | 월 · 상태 필터 | `month-select` · `flt-status` |
| `#layerLogisticsResolve` · `#logisticsResolveForm` · `#logisticsResolveSubmit` (규칙) | 불일치 처리 모달 | `modal-resolve` · `resolve-result` · `resolve-memo` |
| `#layerStatementUpload` · `#statementUploadForm` (규칙) | 명세서 업로드 | uploadStatement |
| `.layer__open[data-target="layerReason"]` (공통) | 엑셀 사유 | downloadExcel |

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 없음(테이블만). 테이블에 있는 `is_locked`(매출 마감 이후에만 잠금) 선후 조건은 프로토타입 "대사 완료 처리"에 안내로 반영할 수 있다.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 화면 전체: 명세서 업로드 · 대사 실행 · 불일치 처리 · 반품 귀책 판정(saveJudge) · 계산서 재발행 요청(requestReissue) · 계산서 수취(receiveInvoice) · 엑셀 · 대사 완료 · 처리 이력.
- 반품 귀책 판정 · 고객 공제액 · 계산서 수취 상태 저장 칸은 현재 테이블에 없다.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `flt-status` 일치 · 불일치 · 3PL만 · DB만 · 수량 · 단가 차이 | match_status matched · billed_only · ours_only · qty_diff · price_diff |
| 처리 결과 승인 지급 · 차감 요청 · 차월 이월 | 개발 코드값 없음(memo 만) |
| 매입처 SUP-xxxx | book_purchase_costs.publisher(문자열) — suppliers.id 연결 없음 |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 화면 번호 — 개발 DB 코멘트(마이그레이션 2026_09_21_000156)는 물류비 대사를 "ADMN-SETT-009"로 적고 있으나 dev-progress 와 프로토타입은 SETT-011. 코멘트 정리 필요 여부(개발팀 전달). **→ 정본대로(POLICY_D_SETT A, 03권 §16.1 L355 · L354)**: 물류비 대사는 SETT-011(SETT-009는 내부 정산 조회) — 개발 마이그레이션 코멘트 정리 전달
- 확인 필요: 불일치 처리 결과(승인 지급 · 차감 요청 · 차월 이월)와 반품 귀책 판정 값을 어디에 저장할지 — 현재 테이블에 칸이 없다. **→ 정본대로(POLICY_D_SETT A, 03권 §16.1 L355)**: 처리 결과(승인 지급 · 차감 요청 · 차월 이월) · 메모 없이 종결 불가, 반품 귀책은 CS 판정 — 저장 칸은 개발 구현 몫(`logistics_settlements` 행에 추가 전달)

## 출처
- config/dev-progress.php:89-90, 217-218
- database/migrations/2026_08_14_000015_create_logistics_settlements_table.php:12
- database/migrations/2026_09_08_000079_add_settlement_columns.php:10
- database/migrations/2026_09_21_000156_rename_sett003_to_sett009_in_comments.php:8-41
- dev_spec/_index/schema.md:1273-1359, 1665-1703
- (라우트 · 컨트롤러 · 뷰 없음 — routes/admin.php grep "logistics" 0건)
