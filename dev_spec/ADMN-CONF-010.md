# ADMN-CONF-010 시스템 감사 로그 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-010_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: a8016168 (2026-10-27) — 정산 감사 기능은 4c1a2622 "정산 감사 로그 — 귀속월 축 · 9대 이벤트 · 해시 체인 · 월별 패키지"(2026-10-27 12:29, psm), dev 병합 ee0d5abd. 마이그레이션 2026_10_27_000269
- 포함 화면: ADMN-CONF-010 탭 1 감사 이벤트 건별 원장 · 탭 2 정산월별 감사 통계 · 월마감 스냅샷 · 탭 3 운영자 접근 · 권한 · 다운로드 로그(정본에서 CONF-006 을 통합)
- 개발 진행: **구현(개발 화면 코드는 ADMN-CONF-006)**. 개발은 새 화면 · 새 라우트를 만들지 않고 기존 관리자 로그(`admin.admin-logs.index`, CONF-006 이력/보안 로그, 담당 이응민, `_index/progress.md` 112행)에 탭 2개를 더했다(AdminLogController.php:49-76 "CONF-010 은 새 화면이 아니라 이 화면의 탭이다"). 화면 제목은 프로토 "시스템 정산 감사 로그 — 월별/기간별 불변 원장"(admin-logs/index.blade.php, 4c1a2622). 로그인 로그(`admin.login-logs.index`)는 별도 메뉴 그대로. 진행표 코드는 여전히 CONF-006(config/dev-progress.php:125)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.admin-logs.index` | 관리자 로그(개발 CONF-006) = 프로토 CONF-010 탭 1 · 2 · 3 | routes/admin.php:319-325, `_index/routes.md` 75-77 |
| `admin.login-logs.index` | 관리자 로그인 로그(개발 CONF-006) = 프로토 탭 3 의 로그인 부분 | routes/admin.php:327-334, `_index/routes.md` 78-80 |

- 권한 축: 탭 1 · 2 조회와 해시 체인 검증은 `can_view`(같은 index 라우트의 GET 쿼리), 월별 패키지 · 월 원장 추출은 `can_download`(`admin.admin-logs.download` 하나가 받음, AdminLogController.php:165-171 "반출 권한도 한 칸이어야 한다"). 버튼도 `@adminCan('admin.admin-logs.index', 'can_download')`로 숨김(_tab-audit.blade.php:129, _tab-audit-monthly.blade.php:83).
- 정산 화면의 "감사 로그 (ADMN-CONF-010)" 안내 카드(pass-refunds · pg-reconciliations)는 계속 관리자 로그로 보낸다 — resources/views/admin/settlement/pass-refunds/index.blade.php:188-198, pg-reconciliations/index.blade.php:175.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. 탭은 라우트가 아니라 쿼리 `tab` 이다(LogSearchRequest.php:76-87).

### CONF-010 탭 1 · 탭 2 · 탭 3 — 관리자 로그(개발 CONF-006)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 탭 3 운영자 접근 로그 목록(기본 탭) | GET | `/admin-logs` (`tab` 없음 또는 `tab=access`) | `admin.admin-logs.index` | can_view | AdminLogController@index :55-76 |
| 탭 1 감사 이벤트 건별 원장 | GET | `/admin-logs?tab=audit&audit_month=&category=&screen=&audit_keyword=&start_date=&end_date=&audit_page=` | `admin.admin-logs.index` | can_view | AdminLogController@index → auditViewData :86-131 |
| 탭 2 정산월별 감사 통계 | GET | `/admin-logs?tab=audit-monthly` | `admin.admin-logs.index` | can_view | AdminLogController@index :133-140 |
| 해시 체인 무결성 검증(탭 1 · 2) | GET | `…?tab=audit&verify=1` · `…?tab=audit-monthly&verify=1` | `admin.admin-logs.index` | can_view | SettlementAuditService@verifyChain :110-196 (AdminLogController.php:128-130, 137-139) |
| 건별 전 · 후 상세 | GET | `/admin-logs/{adminLog}` | `admin.admin-logs.show` | can_view | AdminLogController@show :148-160 (감사 이벤트 · 귀속월 · 블록 해시 칸 추가) |
| 관리자 로그 엑셀(사유) | GET | `/admin-logs/download` | `admin.admin-logs.download` | can_download | AdminLogController@download :165-210 |
| 월별 감사 패키지 · 현재 월 원장 추출(CSV, 사유) | GET | `/admin-logs/download?package_month=YYYY-MM&reason=…` | `admin.admin-logs.download` | can_download | AdminLogController@download → downloadMonthPackage :225-249 |

### CONF-010 탭 3 — 로그인 로그(개발 CONF-006, 이번 변경 없음)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/login-logs` | `admin.login-logs.index` | can_view | LoginLogController@index :43 |
| 엑셀(사유 입력) | GET | `/login-logs/download` | `admin.login-logs.download` | can_download | LoginLogController@download :81 |
| 상세 | GET | `/login-logs/{loginLog}` | `admin.login-logs.show` | can_view | LoginLogController@show :62 |

- 앞 판의 규칙 기반 라우트(`admin.audit-logs.*`, `…monthly.download`, `…verifications.store`)는 쓰지 않는다 — 개발은 전부 위 두 라우트(index · download)에 쿼리로 얹었다.

## 3. 폼 필드 · 검증

### 검색 (LogSearchRequest — 관리자 로그 · 로그인 로그 · 정산 감사 탭 공용, `_index/requests.md` 1705)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `start_date` · `end_date` | nullable · `Y-m-d` · end ≥ start, 최대 90일(:29, :331-360) · 진입 기본 7일(:34, :103-138). **정산 감사 탭은 직접 지정했을 때만 기간 조건을 건다**(hasExplicitPeriod :218-229, auditFilters :252-270) | — | `#dateFrom` · `#dateTo` |
| `period` | nullable · in 1 · 7 · 30 · 90(:43-48) | 오늘 · 7일 · 30일 · 90일 | `applyQuickDate()` 버튼 |
| `keyword` | nullable · max:100 | — | (탭 3) |
| `ip` · `per_page` | max:45 · integer | — | — |
| `type` (관리자 로그) | nullable · in ACTION_TYPES(:60-67) | `personal_view` 개인정보 열람 · `unmask` 마스킹 해제 · `member_update` 회원 정보 수정 · `excel_download` 엑셀 다운로드 · `setting_change` 설정 변경 · `role_change` 권한 변경 | `#accessTypeSelect`(일부) |
| `result_status` · `target_type` · `target_member` · `admin_role_code` · `disallowed_ip_only` (관리자 로그) | success/fail · max:50 · max:191 · max:30 · 0/1 | — | (없음) |
| `status` · `event` (로그인 로그) | success/fail · max:30 | 로그인 이벤트 코드 | `#accessTypeSelect`(로그인 성공 · 실패) |
| `tab` | 정의 밖 값은 걷어내 기본 탭으로(:148-164, :237-242) | `audit` 탭 1 · `audit-monthly` 탭 2 · `access` 탭 3(기본) | `switchTab()` |
| `audit_month` | `YYYY-MM`(01~12) 아니면 걷어냄(:166-170). 탭 1 진입 때 비어 있고 기간도 없으면 로그가 있는 가장 최근 달(AdminLogController.php:111-116) | 귀속 정산월 | `#monthFilterSelect` |
| `category` | `SettlementAuditEvent::CATEGORIES` 키 밖이면 걷어냄 | `share` 1. 1계층·2계층 지분율 및 매핑 변경 · `finance` 2. 정산 수동 조정 · 계정 간 대체 · 수기 검수 · `state` 3. 지원금 상태전이 · 국세청 · 도서 공급형태 · `pii` 4. 민감정보 마스킹 해제 및 계층 1 개인정보 파기(SettlementAuditEvent.php:35-43) | `#catSelect` · `setAuditCategory()` KPI 카드 |
| `screen` | `SettlementAuditEvent::SCREENS` 키 밖이면 걷어냄 | 프로토 8종 + 개발 4종: SETT-001 · SETT-007 · INST-002 · SETT-005 · SETT-002 · SETT-008 · BOOK-001 · USER-007 + SETT-004 · SETT-006 · SETT-009 · INST-001(:81-142) | `#screenSelect` |
| `audit_keyword` | nullable · max:100(:204). 사유 · 작업자 · 로그 ID 만 검색, 전 · 후 스냅샷은 검색하지 않음(_tab-audit.blade.php:100-102) | — | `#auditKeyword` |
| `audit_page` | nullable · integer ≥ 1 | — | — |
| `verify` | `'1'` 일 때만 체인 검증(:162, wantsVerify :279-282) | — | `verifyHashChain()` |
| `package_month` | `YYYY-MM` 아니면 걷어냄 → 일반 로그 엑셀로 처리(:161, packageMonth :273-276) | 추출 귀속월 | `exportMonthPackage()` · `exportAuditCsv()` |

### 반출 사유 (ReasonRequest — 공통 사유 모달 `layerReason`)
| 필드 name | 규칙 | 코드값(라벨) |
|---|---|---|
| `reason` | required · in | `refund_account` 환불 계좌 확인 · `delivery_error` 배송 오류 확인 · `identity_check` 본인 확인 요청 · `payment_inquiry` 결제 오류 조사 · `legal_request` 법적 요청 대응 · `settlement_check` 정산 · 지급 확인 · `etc` 기타(직접 입력) |
| `reason_ref` | nullable · max:50 · 영문 · 숫자 · 하이픈 | 관련 문의 · 주문번호 |
| `reason_etc` | `etc` 일 때 required · 10~150자 | 기타 사유 |

- 월별 패키지도 같은 사유 모달 · ExcelDownloadService 를 탄다 — 사유 · 건수 · IP 가 `excel_download_logs` · `admin_logs` 에 남고 파일 첫 행에 워터마크 · 안내문(AdminLogController.php:212-249, SettlementAuditService.php:247).

## 4. 목록 필터 · 정렬 · 표 컬럼

### 탭 1 감사 이벤트 건별 원장 (`_tab-audit.blade.php`)
- 필터: 귀속월 `#auditMonth`(:39) · 감사 영역 `#auditCategory`(:49) · 발생 화면 `#auditScreen`(:59)(셋 다 바꾸면 바로 이동) · 기간 `#auditStart` · `#auditEnd`(:76, :80) · 검색어 `#auditKeyword`(:86-87) · 초기화(:95).
- KPI 5장: 전체 9대 영역 + 영역 4장(라벨 · 배지 · 설명은 `CATEGORY_KPI`, SettlementAuditEvent.php:48-69), 카드 버튼이 `category` 로 좁힘(_tab-audit.blade.php:106-122).
- 버튼: 해시 체인 위변조 무결성 검증(:127), 현재 조회 월 감사 원장 추출(CSV)(:129-146, 귀속월을 고르지 않으면 비활성 — "추출은 귀속 정산월 단위").
- 체인 검증 결과: 정상 / 끊긴 구간 N건, 체인 시작 로그 ID · 체인 밖 건수 · 최종 블록 해시, 5만 건 초과 시 "앞부분만 검증" 경고(:149-175), 끊긴 구간 표(로그 ID · 발생 일시 · 구분 · 내용, :178-190). 구분 = `tampered` 내용 변경 · `restarted` 시작점 재등장 · `orphan` 시작점 없는 첫 행 · `broken` 직전 해시 불일치(SettlementAuditService.php:141-183).
- 표 컬럼(:238-247): 로그 ID / 발생 일시 · 귀속 정산월 · 발생 화면 · 감사 이벤트 구분(16.1절 9대 항목) · 대상 엔티티 / 권리자 · 입력된 변경·열람·승인 사유 · 작업자 / IP · 전·후 비교 및 화면 이동(`admin.admin-logs.show` 페이지 :300, 발생 화면 이동 :303).
- 귀속월 = `target_month` 있으면 그 값, 없으면 발생월(AdminLog::getAuditMonthAttribute, SettlementAuditRepository.php:31 `COALESCE(target_month, DATE_FORMAT(created_at,'%Y-%m'))`).

### 9대 감사 이벤트 판정 (SettlementAuditEvent::EVENTS, :167-345 — 컬럼이 아니라 조회 때 sub_action · target_type 으로 판정)
| 항목 | 이벤트 키 | 발생 화면 | sub_action |
|---|---|---|---|
| 1 민감 정보 열람 | `pii_unmask` | USER-007 | `unmask` + target_type 정산 쪽 5종만(rights_holder · rights_holder_contract · refund_claim · payee_split · contract_co_signer) — 회원 · 주문 해제는 탭 3 에만 |
| 2 지분율 변경 | `rights_share_change` · `payee_split_change` | SETT-001 · SETT-007 | `rights_mapping_save` · `payee_split_save` · `payee_split_cosigner_add/remove` |
| 3 수기 검수 | `manual_review` | INST-002 | `milestone_approve/reject/hold` |
| 4 수동 조정 | `manual_adjustment` | SETT-005 | `adjustment_create/update/reject/delete` |
| 5 계정 간 대체 | `account_transfer` | SETT-005 | `adjustment_confirm` |
| 6 개인정보 파기 | `pii_destruction` | USER-007 | `pii_destruction_approve` |
| 7 국세청 전환 | `nts_tax_type` | SETT-008 | `nts_tax_type_approve/hold` |
| 8 도서 공급형태 | `book_supply` | BOOK-001 | `supply_update` · `reissue_sku` · `price_change` |
| 9 지원금 한도 복원 | `support_fund_state` | SETT-002 | `settlement_run` · `settlement_recompute` |
| (9대 밖, 개발 추가) | `settlement_close` · `settlement_memo` · `pg_reconciliation` · `pass_refund_settle` · `rights_contract` · `rights_holder_master` · `settlement_export`(반출, after_value.menu_key 로 화면 판정) | SETT-002 · 004 · 006 · INST-001 · 반출 화면 | |

### 탭 2 정산월별 감사 통계 (`_tab-audit-monthly.blade.php`)
- 표 컬럼(:49-56): 정산 기준월 · 총 감사 로그 수 · 1·2계층 지분변경 · 수동조정·계정대체·수기검수 · 지원금·국세청·도서 · 민감정보 열람·파기 · 월별 마지막 블록 해시 · 월별 원장 보기 / 추출.
- 월별 마지막 블록 해시 = 그 달 체인 행 중 최대 id 의 `block_hash`, 체인 행이 없으면 "체인 밖 · 체인 시작 전 기록"(:69-77, SettlementAuditRepository.php:128-151).
- "이 달의 로그 보기" → 탭 1 `audit_month`(:81), "⬇ 월별 패키지" → 사유 모달 → download `package_month`(:83-97). 해시 체인 검증 버튼(:17).
- 통계는 조회 때 집계한다(별도 스냅샷 테이블 없음, SettlementAuditRepository.php:105-152).

### 월별 패키지 CSV 열 (SettlementAuditService::monthPackage :214-275)
No · 로그 ID · 발생 일시 · 귀속 정산월 · 발생 화면 · 감사 이벤트 구분 · 감사 영역 · 대상 구분 · 대상 ID · 사유 · 사유 참조 · 변경된 칸(변경 전) · 변경된 칸(변경 후) · 작업자 · 아이디 · 역할 · 접속 IP · 결과 · 블록 해시(없으면 "체인 밖") · 직전 블록 해시. 전 · 후는 **값이 아니라 바뀐 칸 이름만**(changedKeys :280-318, 30칸 넘으면 "… 외 N칸"). 건수와 파일 행수를 맞추려 추출 시작 때 최대 id 로 고정(SettlementAuditRepository.php:166-189, 216-219).

### 탭 3 (기존)
- 관리자 로그 표: No · 관리자 · 역할 · 메뉴 · 행위 · 대상 · 사유 / 상세 · 결과 · Method · IP · 일시 · 관리 — admin-logs/index.blade.php:359-372. 마스킹 해제 관리자별 표(`[data-unmask-by-admin]` :108, 관리자 · 오늘 해제 · 이번 달 해제 · 비고 :112, 1일 임계 config/admin.php:85 = 50).
- 로그인 로그 표 · 이벤트 18종: app/Models/LoginLog.php:23-42(변경 없음).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| admin_logs.target_month | char(7) nullable, index | 귀속 정산월 YYYY-MM. 발생월과 귀속월이 갈리는 정산 행위만 채움(조정 반영월 · 마일스톤 대상월 · 대사월 · 마감월), 나머지 NULL = 발생월로 읽음(000269:23-29, `_index/schema.md` 759) | 탭 1 귀속 정산월 · 탭 2 정산 기준월 |
| admin_logs.block_hash | char(64) nullable | SHA-256 행 해시. 정산 감사 이벤트만 채움, 기존 행 · 다른 도메인 NULL = 체인 밖(000269:31-37, schema.md 760) | 상세 "블록 해시" · 탭 2 월별 마지막 블록 해시 · CSV |
| admin_logs.prev_block_hash | char(64) nullable | 직전 체인 행의 block_hash, 체인 첫 행은 `GENESIS`(000269:39-45, schema.md 761) | 상세 "직전 블록" · CSV |
| admin_logs.admin_id · admin_login_id · admin_role_code · menu_id · action · sub_action · target_type · target_id · before_value · after_value · reason · reason_ref · request_method · request_url · result_status · ip · user_agent · created_at | (기존) | 행위 기록. 위 18칸 + target_month 가 해시 입력(AuditBlockHash.php:44-64, id 는 제외) | 탭 1 · 3 |
| login_logs.* · excel_download_logs.* | (기존) | 로그인 이력 · 반출 기록 | 탭 3 · 반출 |

- 해시 방식(AuditBlockHash.php): `sha256("prev=<prev>\n필드=값\n…")`, NULL 은 `\0`, 배열은 키 정렬 JSON, 시각은 초 단위(:72-132). 적재는 `AdminLogRepository::storeChained` — 꼬리 행 `lockForUpdate` 후 prev 를 물고 INSERT 한 번(4c1a2622 AdminLogRepository.php), 실패하면 체인 밖으로라도 적재(AdminLogService, 4c1a2622). 정산 감사 이벤트 판정은 `SettlementAuditEvent::isAuditEvent`(:448).
- 귀속월을 넘기는 호출부 12곳: MilestoneReviewService.php:378 · PassRefundSettleService.php:192 · SettlementAdjustmentService.php:164, 213, 256, 295 · SettlementBoardService.php:215 · PgReconciliationService.php:296, 339 · SettlementCloseService.php:136 · SettlementPersistService.php:129 · SettlementRunService.php:86. 마스킹 해제(MaskingController)는 공용이라 넘기지 않음(커밋 본문).
- 월마감 스냅샷 전용 테이블은 없다(앞 판의 규칙 이름 `audit_log_snapshots` 폐기).
- Append-Only 는 코드 주석상 "DB 계정에서 UPDATE·DELETE 를 회수한다"(AuditBlockHash.php:16-17, AdminLogRepository storeChained 주석) — 마이그레이션 · 코드로 권한을 회수하는 부분은 저장소에 없음(운영 DB 계정 설정 몫).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `.st-tabs` 버튼(쿼리 `tab`) | 탭 전환(서버 왕복) | `switchTab()` |
| `#auditMonth` · `#auditCategory` · `#auditScreen` (onchange 이동) | 탭 1 귀속월 · 감사 영역 · 발생 화면 | `#monthFilterSelect` · `#catSelect` · `#screenSelect` |
| `#auditStart` · `#auditEnd` (name `start_date` · `end_date`) | 탭 1 기간 | `#dateFrom` · `#dateTo` |
| `#auditKeyword` (name `audit_keyword`) | 탭 1 검색어 | `#auditKeyword` |
| `.st-kpi-card` 버튼 | 영역 KPI · 좁히기 | `#kpiValAll` · `#kpiValShare` · `#kpiValFinance` · `#kpiValState` · `#kpiValPii` · `setAuditCategory()` |
| `verify=1` 링크 버튼 | 해시 체인 검증 | `verifyHashChain()` |
| `.layer__open[data-target="layerReason"]` + `data-reason-title` · `data-reason-action` · `data-reason-submit` · `data-reason-lead` · `data-reason-params`(`package_month`) · `data-reason-count` | 월 원장 · 월별 패키지 추출 사유 모달 | `exportAuditCsv()` · `exportMonthPackage()` |
| `admin.admin-logs.show` 페이지(귀속 정산월 · 감사 이벤트 구분 · 블록 해시 · 직전 블록 행) | 전 · 후 비교 | `openDiffModal()` · `#diffModal` · `#diffBeforeBox` · `#diffAfterBox` · `#diffHashText` |
| "↗ 화면 이동" 버튼(`SCREENS[...]['route']`) | 발생 화면 이동 | `#btnJumpSourceScreen` · `goNav()` |
| "이 달의 로그 보기" 버튼 | 탭 2 → 탭 1 | `jumpToMonthLogs()` |
| `#searchForm` · `#startDate` · `#endDate` · `#type` · `#result_status` · `#admin_role_code` · `#target_type` · `#target_member` · `#ip` · `#perPageForm` · `#per_page` | 탭 3 관리자 로그 검색(index.blade.php:130-327) | `#accessTypeSelect` |
| `#status` · `#event` | 로그인 로그 검색 | `#accessTypeSelect` |
| `[data-unmask-by-admin]` | 마스킹 해제 관리자별 표 | (없음) |

- 하위 화면 표현: 탭은 서버 렌더(쿼리 `tab`), 전 · 후 비교는 모달이 아니라 상세 페이지. 프로토는 한 페이지 3탭 JS 전환 + `diffModal`.

## 7. 기능 차이

### 개발이 결정보다 앞서 있음 (white 확인 대상)
- **D-CONF-03 결정은 "1차 = Append-Only 저장 + 월별 감사 원장 추출, 해시 체인 · 블록 해시는 2차"인데, 개발(4c1a2622)은 해시 체인까지 1차에 구현했다** — `block_hash` · `prev_block_hash` 컬럼(000269:31-45), 적재 시 체인 연결(AdminLogRepository::storeChained), 무결성 검증 버튼 · 끊긴 구간 표(SettlementAuditService.php:110-196, _tab-audit.blade.php:127, 149-190), 월별 마지막 블록 해시(_tab-audit-monthly.blade.php:55, 69-77), CSV 블록 해시 열. 결정은 바꾸지 않았다. 프로토는 결정대로 검증 버튼 '(2차)' · 블록 해시 칸 '2차' 표시 상태다(ADMN-CONF-010_baseline.html:283, 464-505, 527, 1134). 프로토를 개발에 맞춰 1차로 올릴지, 개발에 2차로 미루라고 전달할지 **white 확인 대상**.

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 체인 밖 행 구분(기존 행 소급 없음, `GENESIS` 시작점), 끊긴 구간 4종 분류 · 5만 건 초과 경고, 체인 연결 실패 시 체인 밖 적재.
- 9대 밖 정산 행위 6종 + 반출(`settlement_export`) 이벤트, 발생 화면 4종 추가(SETT-004 · 006 · 009 · INST-001).
- 월별 패키지 · 월 원장 추출에 반출 사유(ReasonRequest) · 워터마크 · 바뀐 칸 이름만 내보내기 · 추출 시점 id 고정. 추출 라벨은 "(CSV)" — JSON 을 내보내지 않으므로 프로토 문구를 고쳤다(커밋 본문).
- 탭 1 검색어는 사유 · 작업자 · 로그 ID 만(스냅샷 미검색).
- 기존: 로그 엑셀 다운로드 사유, 마스킹 해제 관리자별 집계 · 임계 강조, 관리자 로그 필터 결과 · 역할 · 대상 회원 · 허용 외 IP, 로그인 이벤트 18종.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 월마감 스냅샷 "아카이브"(마감 시점 동결본) — 개발 탭 2는 조회 때마다 집계하는 통계이고 별도 스냅샷 저장이 없다.
- 감사 이벤트 9대 항목 중 항목 9(지원금 COMPLETED → ACTIVE 복원)는 개발이 `settlement_run` · `settlement_recompute` 전체를 이 항목으로 묶는다 — 상태 전이 자체를 따로 기록하지 않음(SettlementAuditEvent.php:260-269 "별도 경로가 없어 집계 · 재집계 로그가 원천").
- 전 · 후 JSON 비교 모달(`diffModal`) — 개발은 상세 페이지.
- 탭 1 기본 탭: 프로토는 탭 1(감사 이벤트)로 진입, 개발은 기존 운영자 접근 로그(탭 3)로 진입하고 탭바 순서만 프로토대로(LogSearchRequest.php:70-87).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 화면 코드: 프로토 CONF-010(CONF-006 통합) → 개발 화면 제목은 CONF-010 문구로 바꿨지만 메뉴 · 라우트 · dev-progress 코드는 CONF-006 이름(`admin-logs` · `login-logs` 두 메뉴).
- 탭: `switchTab(1~3)` → `?tab=audit` · `audit-monthly` · (없음/`access`).
- 감사 영역: 프로토 SHARE · FINANCE · STATE · PII → `share` · `finance` · `state` · `pii`(라벨 · 번호는 프로토 그대로).
- 월 선택 `monthFilterSelect` → `audit_month`, 영역 `catSelect` → `category`, 화면 `screenSelect` → `screen`, 검색어 → `audit_keyword`, 기간 `dateFrom` · `dateTo` → `start_date` · `end_date`(정산 감사 탭은 지정했을 때만, 최대 90일).
- 귀속월 · 해시 칸: 프로토 `settlement_month` · `prev_hash` · `hash` → `target_month` · `prev_block_hash` · `block_hash`.
- 추출: "월별 패키지(JSON/CSV)" → `admin.admin-logs.download?package_month=` CSV 한 가지.

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 감사 로그 해시 체인 · 월마감 스냅샷을 1차 범위로 둘지 — 확인 필요. **→ 결정(v6.92 white, D-CONF-03)**: 1차 = Append-Only 저장 + 월별 감사 원장 추출, 해시 체인 · 블록 해시는 2차. **[개발이 결정보다 앞서 있음 — white 확인 대상]** a8016168 기준 개발(4c1a2622 · 000269)은 해시 체인 · 블록 해시 · 무결성 검증을 이미 1차로 구현했다(7절 첫 소절). 결정은 그대로 두고 사실만 적는다. 월마감 스냅샷 아카이브는 개발도 미구현(조회 때 집계).
- 조회 기간 상한: 개발 90일, 프로토 "전체 기간" — 확인 필요. **→ 정책 아님(POLICY_D_CONF B)**: 화면 · 이름 문제로 처리 — 1회 조회 최대 90일 · 기본 7일(개발값), 프로토 '전체 기간'은 '최근 90일'로, 긴 기간은 월별 원장 추출. (개발 정산 감사 탭은 귀속월 축이라 기간 미지정 시 7일 제한이 걸리지 않는다 — LogSearchRequest.php:218-270)
- 화면 코드 CONF-006 → CONF-010 통합을 개발(dev-progress · 메뉴)에도 맞출지 — 확인 필요. **→ 정본대로(POLICY_D_CONF A, 정산 03권 L359 · 통합설계서 L411)**: CONF-006은 결번, CONF-010으로 통합 — 개발팀 전달(메뉴 · dev-progress 코드). a8016168 기준 개발은 화면 제목만 CONF-010 문구, 메뉴 · 진행표 코드는 CONF-006 그대로.

## 출처
- routes/admin.php:319-334 · `_index/routes.md` 75-80
- app/Http/Controllers/Admin/AdminLogController.php:29-249 · LoginLogController.php:43-81
- app/Http/Requests/Admin/LogSearchRequest.php:29-282 · `_index/requests.md` 1705 LogSearchRequest · ReasonRequest
- app/Support/Audit/SettlementAuditEvent.php:22-142, 167-345, 448 · app/Support/Audit/AuditBlockHash.php:16-155
- app/Services/Admin/SettlementAuditService.php:29, 110-196, 214-318, 328 · app/Repositories/Admin/SettlementAuditRepository.php:31-44, 105-219
- app/Services/Admin/AdminLogService.php · app/Repositories/Admin/AdminLogRepository.php · app/Models/AdminLog.php (`git show 4c1a2622`)
- database/migrations/2026_10_27_000269_add_settlement_audit_columns_to_admin_logs_table.php:23-53 · `_index/schema.md` 759-761
- resources/views/admin/admin-logs/index.blade.php:59-72, 108-112, 130-372 · _tab-audit.blade.php:11-303 · _tab-audit-monthly.blade.php:17-97 · view.blade.php
- 귀속월 호출부: 5절 목록 · config/admin.php:85 · config/dev-progress.php:125 · app/Models/LoginLog.php:23-42
- tests/Feature/Admin/SettlementAuditLogTest.php(4c1a2622, 20건)
- 프로토타입: prototype_clean/ADMN-CONF-010_baseline.html:283-570(id), 280-1192 (digest 기준)
