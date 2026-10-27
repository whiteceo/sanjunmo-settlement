# ADMN-SETT-009 내부 정산 조회 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-009_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26) — 이 커밋 자체가 SETT-009 구현 커밋("내부 정산 조회 — 자사 귀속 · 손익 대사 · 세무 산출물", DECISIONS 195 · 204)
- 포함 화면: ADMN-SETT-009
- 개발 진행: 구현 (담당 박성민, 라우트 주석 있음 · 커밋 언급 4건). 조회 전용 화면(자금 집행 · 마감 없음)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.internal.index` | 내부 정산 조회 | 엑셀 메뉴 키 `EXCEL_MENU`(app/Http/Controllers/Admin/InternalSettlementController.php) + 정규화 규칙. 운영 DB 행 미확인 |

- 산출물 다운로드는 `download` 접미사 → can_download, 사유 입력 필수(ReasonRequest).
- 주의: 마이그레이션 2026_09_21_000156 이 옛 물류비 대사 코드를 "SETT-003 → SETT-009"로 바꾼 주석을 남겼지만, d562524a 기준 SETT-009 는 내부 정산 조회다(config/dev-progress.php:88). DB 코멘트의 "ADMN-SETT-009 물류비 대사"는 옛 번호.

## 2. 화면별 라우트
### ADMN-SETT-009 내부 정산 조회
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 조회(월 · 탭 · 파이프라인) | GET | `/{admin}/settlement/internal` | `admin.settlement.internal.index` | can_view | InternalSettlementController@index |
| 세무 산출물 엑셀(사유 필수) `?month=&output=` | GET | `/{admin}/settlement/internal/download` | `admin.settlement.internal.download` | can_download | InternalSettlementController@download |

## 3. 폼 필드 · 검증
### 산출물 다운로드 (ReasonRequest — 공통 `#layerReason`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `month` | YYYY-MM 아니면 404 | 조회 기준월 | `monthSelect` |
| `output` | 아래 key 중 available=true 만, 아니면 404 | `withholding` 1. 원천징수이행상황신고서 기초 자료(CSV) · `business_income` 2. 거주자 사업소득 간이지급명세서(홈택스 TXT) · `other_income` 3. 거주자 기타소득 간이지급명세서(C19 한정, 홈택스 TXT) · `base_diff` 4. 과세표준 · 실지급액 차액 검증 명세(CSV) · `exempt_sales` 5. 면세 매출 3계통 및 과세 매출 분리 명세(CSV) · `consignment` 6. 위탁 거래 및 매입 계산서 수취 대사 명세 | downloadTaxFile |
| `reason` · `reason_ref` · `reason_etc` | ReasonRequest (ADMN-SETT-002 명세 3절 값) | 반출 사유 | 프로토타입 사유 모달 없음 |

- 홈택스 TXT 추출 버튼은 disabled(_tab-tax.blade.php:43) — 다운로드는 엑셀(산출물 시트)로 나간다. 파일명 `<산출물 이름>_<month>`.

## 4. 목록 필터 · 정렬 · 표 컬럼
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `month` | YYYY-MM (월 버튼 · `#monthPick`) | `monthSelect` |
| `tab` | `pipeline`(1. 파이프라인별 전사 손익 · 권리자/자사 대조표) · `support`(2. 자사 지분 내 개발지원금 차감 검증) · `goods`(3. 일반 소비재 및 비인입 도서 명세) · `tax`(4. 월별·연간 세무 신고 기초 산출물 센터) | switchTab 4종 |
| `pipeline` | '' 전체 · `P1_1` 온라인 강좌 수익배분 · `P2_1` 자사 발행 도서 인세 · `P2_2` 위탁 도서 판매대금 · `P2_3` 일반 상품 판매매출 · `P5_1` 매출연동 개발지원금 · `P7_1` 비정기 가산금 | `pipeFilterSelect` |

- 파이프라인 표(index.blade.php:123-131): 파이프라인 · 귀속 · 라인 수 · 분할 기준액 · 과세표준 · 공급가액 · 부가세 · 소득세 · 실지급액.
- 지원금 표(164-170): 권리자 · 약정 범위 · 발생액 · 확정액 · 확정 순액 · 한도 소진 · 잔여 한도.
- 소비재 · 비인입 도서 표(_tab-goods.blade.php:22-29, 66-72): 주문번호 · 품목명 · 수량 · 공급형태 · 과·면세 · 정가 · 실결제액 · 결제일 / 사입원가.
- 산출물 표(_tab-tax.blade.php:22-25): 산출물 명칭 · 집계 대상 및 기준 · 법정 제출 기한 · 산출물 추출.
- 상단 고정 문구 READ_ONLY_NOTICE(app/Services/Admin/InternalSettlementService.php:41).
- 프로토타입 `searchKeyword`(검색어)는 개발에 없다.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| settlement_lines.target_month · pipeline_id · rights_holder_id · payee_split_base · taxable_base · supply_amount · vat_amount · withholding_income_tax · payable_amount · income_category · income_clause | | 월 정산 라인(읽기) — 귀속(외부/자사)은 rights_holders.is_internal | 파이프라인 표 · 산출물 |
| rights_holders.is_internal | boolean | 자사 권리자 | 귀속 |
| support_fund_agreements · buyout_payments 등 지원금 약정 | | 약정 범위 · 한도(읽기, 추정) | 지원금 표 |
| order_items · goods · books (book_supply_type_snapshot, cost_price snapshot) | | 일반 상품 · 비인입 도서 매출 | 소비재 표 |
| settlement_closings | | 다운로드 감사 대상 타입 `settlement_closing` | — |

- 이 화면은 쓰기 테이블이 없다(다운로드 감사 로그만).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 월 버튼 `.st-btn(.st-btn--pr)` · `#monthPick`(name month) | 기준월 | `monthSelect` · changeMonth |
| 탭 버튼 `.st-btn` `?tab=` | 탭 4종 | switchTab |
| 필터 폼 hidden `month` · `tab`, `#pipeline`(name pipeline) | 파이프라인 | `pipeFilterSelect` · setPipelineFilter |
| `.layer__open[data-target="layerReason"][data-action][data-method="get"]` | 산출물 다운로드 사유 | downloadTaxFile |

출처: resources/views/admin/settlement/internal/index.blade.php:11-170 · _tab-tax.blade.php:22-43 · _tab-goods.blade.php.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 파이프라인 `P7_1`(비정기 가산금) 필터 값.
- 산출물 6번 "위탁 거래 및 매입 계산서 수취 대사 명세".
- 다운로드 사유 입력.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- "⬇ 전사 내부 손익·정산 대사표 (CSV)"(exportInternalReport) — 개발은 산출물별 다운로드만.
- 검색어(`searchKeyword`), 상품/SKU 단위 행(개발 파이프라인 표는 파이프라인 · 귀속 단위 집계).
- 홈택스 TXT 추출 — 개발 버튼 disabled.
- 산출물 표의 "당월 집계 요약" 열.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `monthSelect` | `month` |
| `pipeFilterSelect` 라벨 | `pipeline` P1_1 · P2_1 · P2_2 · P2_3 · P5_1 · P7_1 |
| switchTab(1~4) | `tab` pipeline · support · goods · tax |
| downloadTaxFile(종류) | `output` withholding · business_income · other_income · base_diff · exempt_sales · consignment |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 개발 settlement_lines.pipeline_id 주석은 `LUMPSUM` 을 쓰는데 이 화면 필터는 `P7_1`(비정기 가산금)을 쓴다 — 같은 값의 두 이름인지. **→ 정본대로(POLICY_D_SETT A, 01권 §18.4 L653 · 02권 L174)**: 정본에 'Pipeline 7.1'은 없고 비정기 가산금은 7단계 `LUMPSUM_ADD` — 개발 안 이름을 `LUMPSUM_ADD` 하나로 정리(개발팀 전달), 프로토는 `P7_1` 추가 안 함
- 확인 필요: 프로토타입 상품/SKU 단위 손익 표를 유지할지(개발은 파이프라인 집계). **→ 정책 아님(POLICY_D_SETT B)**: 화면 · 이름 문제로 처리 — 파이프라인 합계를 위에, SKU 행은 펼침(내역)으로 유지

## 출처
- routes/admin.php:628-630
- app/Http/Controllers/Admin/InternalSettlementController.php
- app/Services/Admin/InternalSettlementService.php:22-41, 160-210
- resources/views/admin/settlement/internal/index.blade.php · _tab-tax.blade.php · _tab-goods.blade.php
- database/migrations/2026_09_21_000156_rename_sett003_to_sett009_in_comments.php:8-41
- config/dev-progress.php:88
