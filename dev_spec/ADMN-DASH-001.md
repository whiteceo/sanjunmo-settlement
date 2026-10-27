# ADMN-DASH-001 통합 대시보드 · 매출/상품 통계 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-DASH-001_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-DASH-001 대시보드 홈 · ADMN-STAT-001 매출 통계 · ADMN-STAT-002 상품 통계
- 개발 진행: 구현(담당 이응민, `_index/progress.md` 11~13행). 프로토타입은 한 파일 3뷰(`switchView`), 개발은 페이지 3개

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| (없음) `admin.dashboard` | 대시보드 홈 | 메뉴 권한 밖(로그인만) — routes/admin.php:187. 대신 컨트롤러가 역할을 본다: `config('admin.dashboard_denied_roles')` = `instructor` · `assistant` 는 자기 랜딩으로 리다이렉트, 갈 곳이 없으면 `admin.errors.no-menu` 403 — DashboardController.php:30-45, config/admin.php:49 |
| `admin.sales-stats.index` | 매출 통계 | 라우트 정규화(라우트 이름 = 목록형). admin_menus 행은 저장소 마이그레이션 · 시더에 없어(서버 DB 데이터) 저장소로 확인 불가 — 라우트 이름 기준 |
| `admin.product-stats.index` | 상품 통계 | 〃 |

- 대시보드 블록 노출은 메뉴 권한이 아니라 역할 코드별 상수 `DashboardService::VISIBLE` 로 정한다(여러 역할이면 합집합, 맵에 없는 역할은 아무 블록도 안 봄) — app/Services/Admin/DashboardService.php:38-44, :88-96

| 역할 code | 보이는 블록 |
|---|---|
| `super` | 전부(`*`) |
| `cs` | `card.paid` · `card.signup` · `card.inquiry` · `queue.pass_refund` |
| `logistics` | `card.delivery` · `queue.return` · `external.3pl` |
| `finance` | `card.paid` · `card.paid_amount` · `queue.pass_refund` · `queue.refund_overdue` · `queue.settlement` · `trend` |

- 블록 안 바로가기 링크는 대상 라우트의 `can_view` 가 있을 때만 만든다(없으면 링크 없음) — DashboardService.php:282-283

## 2. 화면별 라우트

### ADMN-DASH-001 대시보드 홈
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 화면 / 블록 부분 갱신(AJAX 면 `_body` 만) | GET | `/{admin}/dashboard` (`?fresh=1` 강제 재계산) | `admin.dashboard` | 로그인만 | DashboardController@index |
| 관리자 루트 | GET | `/{admin}` | `admin.` | 로그인만 | closure → dashboard |

- 집계는 캐시 `admin-dashboard` 60초, `fresh=1` 은 관리자별 3초 쿨다운 — DashboardService.php:28-33, :74-80
- 블록 링크 대상(DashboardService.php:378-512): 당일 결제 → `admin.orders.index?date_basis=paid_at&date_from=&date_to=&statuses[]=…`, 신규 가입 → `admin.members.index?date_from=&date_to=`, 미처리 문의 → `admin.inquiries.index?unanswered=1`, 배송대기 → `admin.deliveries.index?tab=ready`, 환급 심사 대기 → `admin.pass-refunds.index?status=reviewing`, 환불 기한 초과 → `admin.refunds.index?deadline=overdue&from=&to=`, 정산 미확정(전월) → `admin.settlement.board.index?month=YYYY-MM`, 반품 접수 → `admin.deliveries.index?tab=return`, 매출 추이 상세 → `admin.sales-stats.index?preset=7`, 보안 → `admin.admin-logs.index?period=1&type=excel_download` · `admin.members.blacklist.index`

### ADMN-STAT-001 매출 통계
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 조회 | GET | `/{admin}/sales-stats` | `admin.sales-stats.index` | can_view | SalesStatController@index |
| 엑셀 | GET | `/{admin}/sales-stats/download` | `admin.sales-stats.download` | can_download | SalesStatController@download |

### ADMN-STAT-002 상품 통계
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 조회 | GET | `/{admin}/product-stats` | `admin.product-stats.index` | can_view | ProductStatController@index |
| 엑셀 | GET | `/{admin}/product-stats/download` | `admin.product-stats.download` | can_download | ProductStatController@download |

## 3. 폼 필드 · 검증
- 대시보드: 입력 폼 없음. 쿼리 `fresh=1` 만 읽는다 — DashboardController.php:47
- 통계 엑셀은 사유 입력 없음(개인정보 없는 집계). 반출 기록만 `excel_download_logs` 에 남김(menu_key `admin.sales-stats.index`) — SalesStatController.php:51-73

## 4. 목록 필터 · 정렬 · 표 컬럼

### ADMN-STAT-001 (SalesStatRequest::filters — rules 는 비어 있고 쿼리를 걸러 읽음)
| 쿼리 name | 값 | 기본 | 프로토타입 대응 |
|---|---|---|---|
| `preset` | `7` · `14` · `30` · `365` (7일 · 14일 · 30일 · 1년) | 30 | `setSalesPeriodPreset()` 버튼 |
| `from` · `to` | `Y-m-d`(존재하지 않는 날짜는 버림), 최대 13개월 | — | `#stat-sales-from` · `#stat-sales-to` |
| `unit` | `day` 일별 · `week` 주별 · `month` 월별 | — | `#stat-sales-unit` |
| `kinds[]` | `single` 단과 강좌 · `package` 올패스 패키지 · `book` 교재(체크박스) | 전체 | `#stat-sales-type`(select 1개) |
| `method` | `card` · `easy_pay` · `virtual_account` · `transfer` · `mobile_phone` · `gift` | '' 전체 | `#stat-sales-method` |
| `basis` | `paid` 결제일 기준(원거래일 소급) · `refund_confirmed` 환불일 기준(발생일) | `paid` | (없음) |
| `page` | 1~1000, 쪽당 31행 | 1 | — |

- 표 컬럼(data-label): 단위열(일자/주/월) · 결제건수 · 결제금액 · 환불건수 · 환불금액 · 순매출 · 환불율(10% 초과 강조) · 배송비(참고) + 합계행 — resources/views/admin/sales-stats/index.blade.php:153-184
- 요약 카드: 결제금액 · 환불금액 · 순매출(수수료 · 정산금 차감 전) · 일 평균 순매출 — SalesStatService.php:335-340
- 조회량 초과 문구: "조회량이 많습니다. 집계 단위를 월별로 바꾸거나 기간을 줄여주세요." — SalesStatService.php:57

### ADMN-STAT-002 (ProductStatRequest::filters, 매출 통계 필터 상속)
| 쿼리 name | 값 | 기본 | 프로토타입 대응 |
|---|---|---|---|
| `preset` · `from` · `to` · `kinds[]` · `page` | 위와 같음 | — | `#stat-prod-type` |
| `sort` | `completed` 결제 완료 건수 · `revenue` 실 매출액 · `refund_rate` 환불율 | `completed` | `#stat-prod-sort` |

- 표 컬럼: 순위 · 유형 · 상품명 · 결제건수 · 취소/환불(환불율) · 완료건수 · 실 매출액 · 점유율 — product-stats/index.blade.php:127-143

## 5. DB 테이블 · 컬럼
대시보드는 자체 테이블이 없고 여러 테이블을 집계한다(DashboardRepository + 타 서비스).

| 테이블.컬럼 | 뜻 | 화면 표시 위치 |
|---|---|---|
| orders(결제 상태 · paid_at) | 당일 결제 건수 | 카드 "당일 결제 완료" |
| (ActualPaidRepository 실결제 집계) | 결제 · 환불 · 순매출 | 카드 결제 금액 · 최근 7일 순매출 · 매출 통계 |
| users(created_at · join_method) | 당일 가입(소셜 / 이메일) | 카드 "당일 신규 가입" |
| inquiries(접수 · 처리중 · SLA 초과) | 미처리 문의 | 카드 "미처리 CS 문의 (누적)" |
| orders/deliveries(미발송) | 배송대기 · D+2 | 카드 "배송대기 (누적)" |
| refund_claims(심사중) | 환급 심사 대기 · 최장 경과 | 큐 |
| refunds(처리 기한 = 사유 발생일 + 5영업일, config admin.holidays) | 기한 초과 | 큐 |
| settlement_closings · 권리 매핑 미매핑 수 | 전월 정산 미확정 · 지급일(D-n) | 큐 |
| notification_logs(채널별 · 24시간 실패) | 알림 발송 현황 | "알림 발송 현황" |
| lecture_play_logs/DRM · payments · pg_notifications · identity_verifications | 외부 연동 상태 | "외부 연동 상태" |
| admin_logs(엑셀 다운로드: admin_login_id · target_type · sub_action · reason · after_value.row_count) | 금일 다운로드 최근 5건 | "금일 보안 이상 징후" |

- 큐 경과 강조: 3일 초과 주황, 5일 초과 빨강 — DashboardService.php:47-49
- 외부 연동 상태값: `ok` · `warn` · `off`(연동 전) · `none` — DashboardService.php:531-541 (CDN · 3PL 은 `off` 고정)

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#dashboardBody` | AJAX 로 바꾸는 블록 영역(`_body.blade.php`) | 대시보드 뷰 |
| `[data-dash-refresh]` | [새로고침] — `?fresh=1` | `manualRefreshDash()` |
| 60초 `setInterval` + 헤더 `X-Admin-Background: 1` | 자동 갱신(무조작 시간을 늘리지 않음) | (프로토타입 갱신 시각 표시) |
| `.dash-kpis--{cols}` · `.dash-kpi__label/value/sub/flag` | KPI 카드 | 섹션 카드 |
| `.dash-panel` · `.dash-panel__title`(알림 발송 현황 · 처리 대기 큐 · 최근 7일 순매출 · 외부 연동 상태 · 금일 보안 이상 징후) | 블록 | `toggleDashSec()` 섹션 5개 |
| `.dash-elapsed--{tone}` · `.dash-pill--{tone}` · `.dash-badge--{status}` · `.dash-dot--{status}` | 경과 · 상태 표시 | 배지 |
| `.dash-chart__*` | 7일 막대 | 7일 표 |
| 통계: `<form method="get">` · `select[name=unit/method/basis/sort]` · `input[name=kinds[]][data-kind-item]` · `input[name=preset][data-preset-input]` · `#salesChart` · `#productChart` · `tr[data-slice]` | 통계 검색 · 차트 | `#stat-sales-*` · `#stat-prod-*` |

- 하위 화면 표현: 매출 · 상품 통계는 별도 페이지(`admin.sales-stats.index`, `admin.product-stats.index`). 대시보드 블록은 아코디언 아님(프로토타입은 접기 토글).

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 매출 통계 `basis`(결제일 기준 / 환불일 기준), `method` 에 `transfer` · `mobile_phone` · `gift`.
- 상품 통계 정렬 `refund_rate`.
- 블록별 오류 상태("일시적으로 조회할 수 없습니다") — DashboardService.php:136-148.
- 정산 큐의 지급일 D-n 표시.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 발송 실패 큐 모달 `modal-fail-queue` 와 건별 · 일괄 재발송(개발은 실패 건수 · 안내 문구만, 재발송 동작 없음).
- [API 상태 수동 점검] `runApiHealthCheck()`.
- 통계 엑셀 사유 입력 모달 `modal-stat-excel`(개발은 사유 없이 바로 다운로드).
- 역할 그룹 화면 미리보기 `#rbac-role-sim`(시연 전용).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 상품 유형: 프로토타입 select 1개(`#stat-sales-type`) → 개발 체크박스 `kinds[]` 값 `single` · `package` · `book`.
- 집계 단위 `#stat-sales-unit` → `unit` = `day`/`week`/`month`.
- 기간 프리셋 → `preset` = 7/14/30/365.
- 상품 정렬 `#stat-prod-sort`(일 순매출액 · 순결제건수) → `sort` = `revenue` · `completed` · `refund_rate`.
- 매출 통계 표 컬럼 "결제금액 (배송비 제외)" · "일 순매출" → 개발 "결제금액" · "순매출".

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 통계 엑셀 다운로드 사유: 프로토타입 필수 10자, 개발은 개인정보 없음 이유로 사유 없음 — 확인 필요. **→ 정본대로(D-CONF-04 A, 통합설계서 L127 · L180 [S1-04] · 안전성 확보조치 기준 제8조 ②)**: 개인정보 없는 통계 엑셀은 사유 없이 다운로드 기록만(CONF-010) — 개발이 맞음, 프로토 사유 필수 제거
- 대시보드 발송 실패 재발송을 대시보드에서 할지(개발은 미구현) — 확인 필요. **→ 정책 아님(POLICY_D_CONF B)**: 화면 · 이름 문제로 처리 — 프로토 유지(실패 큐 모달), 개발은 모달 또는 발송 이력 재발송 링크 중 택일
- 재무(finance) 역할에 알림 · 보안 블록 비노출(개발 DECISIONS 158 ①) — 프로토타입 역할별 노출과 대조 확인 필요. **→ 정본대로(POLICY_D_CONF A, 통합설계서 v3.2.19 L50 · L411)**: 블록 노출은 역할 이름이 아니라 메뉴 권한 기준 — 개발팀 전달(finance 하드코딩 → 권한 기준)

## 출처
- routes/admin.php:111, :187, :1249-1258
- app/Http/Controllers/Admin/DashboardController.php:16-51
- app/Services/Admin/DashboardService.php:28-148, :150-270, :280-300, :378-541
- app/Repositories/Admin/DashboardRepository.php:29-209
- config/admin.php:35-51
- resources/views/admin/dashboard/index.blade.php:20-61 · _body.blade.php:35-205
- app/Http/Controllers/Admin/SalesStatController.php:25-73 · ProductStatController.php
- app/Http/Requests/Admin/SalesStatRequest.php:30-53 · ProductStatRequest.php:15-28
- app/Services/Admin/SalesStatService.php:24-60, :335-340 · ProductStatService.php:18-25 · OrderService.php:72
- app/Repositories/Settlement/ActualPaidRepository.php:34-51
- resources/views/admin/sales-stats/index.blade.php:17-184 · _period.blade.php · _kinds.blade.php · product-stats/index.blade.php:17-189
- 프로토타입: prototype_clean/ADMN-DASH-001_baseline.html:448-1372 (digest 기준)
