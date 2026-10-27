# ADMN-CONF-010 시스템 감사 로그 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-010_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-010 탭 1 감사 이벤트 건별 원장 · 탭 2 정산월별 감사 통계 · 월마감 스냅샷 · 탭 3 운영자 접근 · 권한 · 다운로드 로그(정본에서 CONF-006 을 통합)
- 개발 진행: 화면 코드 ADMN-CONF-010 은 개발 미구현(d562524a 기준 — 메뉴 · 라우트 없음, 정산 화면 두 곳의 안내 카드 제목에만 등장). 대응 화면은 개발 ADMN-CONF-006 이력/보안 로그(구현, 담당 이응민, `_index/progress.md` 112행) = 관리자 로그 · 로그인 로그. 탭 1(정산 원장 감사 원장) · 탭 2(월별 통계 · 해시 체인)는 개발 미구현

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.admin-logs.index` | 관리자 로그 (개발 CONF-006) | routes/admin.php:305 (주석 :301 "관리자 로그") |
| `admin.login-logs.index` | 관리자 로그인 로그 (개발 CONF-006) | routes/admin.php:313 (주석 :309) |
| `admin.audit-logs.index` (규칙) | 시스템 감사 로그 | 개발 미구현, 규칙 기반 명명 |

- 정산 화면의 "감사 로그 (ADMN-CONF-010)" 카드는 관리자 로그로 보내는 안내만 한다(행위 필터 `pass_refund_settle_confirm`) — resources/views/admin/settlement/pass-refunds/index.blade.php:188-198, pg-reconciliations/index.blade.php:175, app/Services/Admin/PassRefundSettleService.php:32, PgReconciliationScreenService.php:27

## 2. 화면별 라우트

### 탭 3 대응 — 관리자 로그 (개발 CONF-006)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/admin-logs` | `admin.admin-logs.index` | can_view | AdminLogController@index |
| 엑셀(사유 입력) | GET | `/{admin}/admin-logs/download` | `admin.admin-logs.download` | can_download | AdminLogController@download |
| 상세(전 · 후 값) | GET | `/{admin}/admin-logs/{adminLog}` | `admin.admin-logs.show` | can_view | AdminLogController@show |

### 탭 3 대응 — 로그인 로그 (개발 CONF-006)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/login-logs` | `admin.login-logs.index` | can_view | LoginLogController@index |
| 엑셀(사유 입력) | GET | `/{admin}/login-logs/download` | `admin.login-logs.download` | can_download | LoginLogController@download |
| 상세 | GET | `/{admin}/login-logs/{loginLog}` | `admin.login-logs.show` | can_view | LoginLogController@show |

### 탭 1 · 탭 2 — 개발 미구현, 규칙 기반 명명
| 동작 | 메서드 | URL | 라우트 이름 | 권한 |
|---|---|---|---|---|
| 감사 원장 목록 | GET | `/{admin}/audit-logs` | `admin.audit-logs.index` (규칙) | can_view |
| 건별 전 · 후 상세 | GET | `/{admin}/audit-logs/{auditLog}` | `admin.audit-logs.show` (규칙) | can_view |
| 기간 원장 추출 | GET | `/{admin}/audit-logs/download` | `admin.audit-logs.download` (규칙) | can_download |
| 월별 통계 | GET | `/{admin}/audit-logs/monthly` | `admin.audit-logs.monthly.index` (규칙) | can_view |
| 월별 패키지 추출 | GET | `/{admin}/audit-logs/monthly/download` | `admin.audit-logs.monthly.download` (규칙) | can_download |
| 해시 체인 검증 — 2차(v6.92 D-CONF-03) | POST | `/{admin}/audit-logs/verifications` | `admin.audit-logs.verifications.store` (규칙) | can_create |

## 3. 폼 필드 · 검증

### 검색 (LogSearchRequest — 두 로그 공용)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `start_date` · `end_date` | nullable · `Y-m-d` · end ≥ start, 최대 90일 · 기본 7일 | — | `#dateFrom` · `#dateTo` |
| `period` | nullable · in 1 · 7 · 30 · 90 | 오늘 · 7일 · 30일 · 90일 | `applyQuickDate()` 버튼(오늘 · 최근 7일 · 당월 · 전월 · 전체) |
| `keyword` | nullable · max:100 | — | `#auditKeyword` |
| `ip` | nullable · max:45 | — | (없음) |
| `per_page` | nullable · integer | — | — |
| `type` (관리자 로그) | nullable · in ACTION_TYPES | `personal_view` 개인정보 열람 · `unmask` 마스킹 해제 · `member_update` 회원 정보 수정 · `excel_download` 엑셀 다운로드 · `setting_change` 설정 변경 · `role_change` 권한 변경 | `#accessTypeSelect`(일부) |
| `result_status` (관리자 로그) | nullable · `success` / `fail` | — | (없음) |
| `target_type` (관리자 로그) | nullable · max:50 | 대상 유형 | `#catSelect`(유사) |
| `target_member` (관리자 로그) | nullable · max:191 | 대상 회원 | (없음) |
| `admin_role_code` (관리자 로그) | nullable · max:30 | 역할 code | (없음) |
| `disallowed_ip_only` (관리자 로그) | nullable · 0/1 | 허용 외 IP 만 | (없음) |
| `status` (로그인 로그) | nullable · `success` / `fail` | — | `#accessTypeSelect`(로그인 성공 · 실패) |
| `event` (로그인 로그) | nullable · max:30 | 아래 이벤트 코드 | 〃 |

### 엑셀 다운로드 사유 (ReasonRequest — 공통 사유 모달 `admin.inc.reason-modal`)
| 필드 name | 규칙 | 코드값(라벨) |
|---|---|---|
| `reason` | required · in | `refund_account` 환불 계좌 확인 · `delivery_error` 배송 오류 확인 · `identity_check` 본인 확인 요청 · `payment_inquiry` 결제 오류 조사 · `legal_request` 법적 요청 대응 · `settlement_check` 정산 · 지급 확인 · `etc` 기타(직접 입력) |
| `reason_ref` | nullable · max:50 · 영문 · 숫자 · 하이픈 | 관련 문의 · 주문번호 |
| `reason_etc` | `etc` 일 때 required · 10~150자 | 기타 사유 |

## 4. 목록 필터 · 정렬 · 표 컬럼
- 관리자 로그 표: No · 관리자 · 역할 · 메뉴 · 행위 · 대상 · 사유 / 상세 · 결과 · Method · IP · 일시 · 관리 — admin-logs/index.blade.php:326-337. 상단 요약 카드, 마스킹 해제 관리자별 표(관리자 · 오늘 해제 · 이번 달 해제 · 비고, 1일 임계 `config('admin.unmask_daily_alert_threshold')`=50 넘으면 강조) — :49-77
- 로그인 로그 표: No · 회원 · 아이디 · 이벤트 · 상태 · 실패 사유 · IP · 일시 · 관리 — login-logs/index.blade.php:233-241
- 로그인 이벤트 코드(app/Models/LoginLog.php:23-42): `LOGIN_SUCCESS` · `LOGIN_FAIL` · `ACCOUNT_LOCKED` · `LOGIN_BLOCKED` 잠긴 계정 재시도 · `ACCOUNT_UNLOCKED` · `PASSWORD_RESET` · `IP_DENIED` · `TOKEN_REUSE` · `FIND_ID_ATTEMPT` · `FIND_ID_SUCCESS` · `FIND_PW_ATTEMPT` · `FIND_PW_SUCCESS` · `PW_RESET_CAP_EXCEEDED` · `FIND_ID_CAP_EXCEEDED` · `PW_RESET_OWNER_MISMATCH` · `SESSION_EXPIRED` 무조작 자동 로그아웃 · `PASSWORD_CONFIRM_LOCKED` · `PASSWORD_CONFIRM_UNLOCKED`

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| admin_logs.admin_id · admin_login_id · admin_role_code | admin_id bigint unsigned nullable | 행위자 · 시점 아이디 · 역할 code 스냅샷 | 관리자 · 역할 |
| admin_logs.menu_id | — | admin_menus.id | 메뉴 |
| admin_logs.action · sub_action | string | 대분류 · 도메인 소분류(`approve` · `reject` · `routing_change` · `ship_order` · `confirm` · `unmask` · `dispatch` 등) | 행위 |
| admin_logs.target_type · target_id | — | 대상 | 대상 |
| admin_logs.before_value · after_value | json | 변경 전 · 후 | 상세(프로토타입 diffModal) |
| admin_logs.reason · reason_ref | string | 열람 · 처리 사유(삭제 불가) · 참조번호 | 사유 / 상세 |
| admin_logs.request_method · request_url · result_status · ip · user_agent · created_at | — | 요청 정보 | Method · IP · 일시 |
| login_logs.user_id · login_id · event · status · fail_reason · fail_count · ip · user_agent · country · detail · created_at | event varchar(30) NOT NULL | 로그인 · 계정 찾기 이력 | 로그인 로그 |
| excel_download_logs.admin_id · admin_login_id · admin_role_code · menu_key · download_type · filter_params · row_count · reason · status · ip · expired_at | admin_id bigint unsigned nullable | 엑셀 반출 기록 | (전용 화면 없음, 관리자 로그 `excel_download`) |

- 탭 1 · 2 용 컬럼(개발 미구현, 규칙 기반 명명): `admin_logs.settlement_month`(귀속 정산월) (규칙) · `admin_logs.screen_code`(발생 화면) (규칙) · `admin_logs.prev_hash` · `admin_logs.hash`(해시 체인 — 2차, D-CONF-03) (규칙) · 월 스냅샷 테이블 `audit_log_snapshots`(month · last_hash · counts · closed_at) (규칙). 해시 체인 관련 컬럼은 개발 마이그레이션에 없음(grep `hash_chain` · `prev_hash` · `block_hash` 결과 0).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#searchForm` · `#startDate` · `#endDate` · `#type` · `#result_status` · `#admin_role_code` · `#target_type` · `#target_member` · `#ip` | 관리자 로그 검색 | `#dateFrom` · `#dateTo` · `#catSelect` · `#screenSelect` · `#auditKeyword` |
| `#status` · `#event` | 로그인 로그 검색 | `#accessTypeSelect` |
| `#perPageForm` · `#per_page` | 쪽 크기 | — |
| `[data-reason-action]` · `[data-reason-params]` · `[data-reason-title]` · `[data-reason-lead]` · `[data-reason-submit]` | 엑셀 사유 모달 연결 | `exportAuditCsv()` |
| `[data-unmask-by-admin]` | 마스킹 해제 관리자별 표 | (없음) |

- 하위 화면 표현: 관리자 로그 · 로그인 로그가 별도 메뉴 · 별도 페이지, 상세는 `view.blade.php` 페이지. 프로토타입은 한 페이지 3탭 + `diffModal`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 로그 엑셀 다운로드 사유 입력(ReasonRequest), 마스킹 해제 관리자별 집계 · 임계 강조.
- 관리자 로그 필터 결과 · 역할 · 대상 회원 · 허용 외 IP 만.
- 로그인 이벤트 18종(계정 찾기 · 한도 초과 · 무조작 로그아웃 등).

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 탭 1 정산 원장 감사(귀속 정산월 · 발생 화면 · 감사 이벤트 구분 · 권리자) — 개발은 정산 행위도 admin_logs 에 쌓지만 정산월 · 화면 코드 컬럼과 전용 화면이 없음.
- 탭 2 정산월별 감사 통계 · 월마감 스냅샷 · 월별 패키지 추출 · 월별 마지막 블록 해시. **→ 결정(v6.92 white, D-CONF-03)**: 1차 = 월별 통계 · 월별 감사 원장 추출, 블록 해시 칸은 '2차'로 표시.
- [해시 체인 위변조 무결성 검증]. **→ 결정(v6.92 white, D-CONF-03)**: 2차 기능 — 버튼은 '(2차)' 표시 · 안내 토스트만, 1차는 Append-Only 저장(수정 · 삭제 권한 없음).
- 월 선택(`#monthFilterSelect`) · 전월 마감분 · 전체 기간 프리셋(개발 최대 90일).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 화면 코드: 프로토타입 CONF-010(CONF-006 통합) → 개발은 CONF-006 이름으로 `admin-logs` · `login-logs` 두 메뉴.
- 탭 3 "운영자 접근 · 권한 · 다운로드 로그" → 개발 관리자 로그(`type` 필터) + 로그인 로그(`event` · `status` 필터)로 나뉨.
- 기간: `dateFrom` · `dateTo` → `start_date` · `end_date`, 프리셋 → `period`.

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 감사 로그 해시 체인 · 월마감 스냅샷을 1차 범위로 둘지(개발 흔적 없음) — 확인 필요. **→ 결정(v6.92 white, D-CONF-03)**: 1차 = Append-Only 저장 + 월별 감사 원장 추출, 해시 체인 · 블록 해시는 2차.
- 조회 기간 상한: 개발 90일, 프로토타입 "전체 기간" — 확인 필요. **→ 정책 아님(POLICY_D_CONF B)**: 화면 · 이름 문제로 처리 — 1회 조회 최대 90일 · 기본 7일(개발값), 프로토 '전체 기간'은 '최근 90일'로, 긴 기간은 월별 원장 추출
- 화면 코드 CONF-006 → CONF-010 통합을 개발(dev-progress · 메뉴)에도 맞출지 — 확인 필요. **→ 정본대로(POLICY_D_CONF A, 정산 03권 L359 · 통합설계서 L411)**: CONF-006은 결번, CONF-010으로 통합 — 개발팀 전달(메뉴 · dev-progress 코드)

## 출처
- routes/admin.php:300-316
- app/Http/Controllers/Admin/AdminLogController.php:41-120 · LoginLogController.php:35-105
- `_index/requests.md` LogSearchRequest · ReasonRequest · MaskingUnmaskRequest
- app/Models/LoginLog.php:23-42
- config/admin.php:83-85
- resources/views/admin/admin-logs/index.blade.php:49-337 · view.blade.php · login-logs/index.blade.php:46-241 · view.blade.php · inc/reason-modal.blade.php
- resources/views/admin/settlement/pass-refunds/index.blade.php:188-198 · pg-reconciliations/index.blade.php:175
- app/Services/Admin/PassRefundSettleService.php:32 · PgReconciliationScreenService.php:27
- `_index/schema.md` admin_logs · login_logs · excel_download_logs
- 프로토타입: prototype_clean/ADMN-CONF-010_baseline.html:280-1192 (digest 기준)
