# ADMN-USER-007 민감 정보 열람 통제 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-USER-007_baseline.html` (원본 상태: `18d66c1` v6.92)
- 맞춘 개발 커밋: `a8016168` (2026-10-27) — 화면은 `ef3b5183` "민감 정보 열람 통제 — 마스킹 해제 사유 · 3계층 보존 파기 스케줄"(2026-10-27 09:45, psm). 마이그레이션 2026_10_26_000268, 시더 `PiiDestructionFieldMapSeeder`
- 포함 화면: USER-007(탭 3개: 1 민감정보 금고 · 2 보존기한 · 파기 · 3 필드 매핑 · 열람 이력) · 열람 사유 모달(`unmaskReasonModal`) · 증빙 뷰어(`docViewerModal`) · 007-P2 파기 결과 보고서(`modal-pii-destruction-result`)
- 개발 진행: **일부 구현**. 화면 `admin.users.pii-control.index`(탭 3 · KPI 4 · 필터) + 파기 승인 기록(`PUT …/{rightsHolder}`)이 생겼다. 마스킹 해제는 새 경로 없이 기존 `admin.masking.unmask`를 그대로 부르고(routes/admin.php:651), **실제 파기 · 파기 결과 보고서 · 보류 설정 · 필드 맵 수정은 없다**(커밋 본문 "실제 파기는 범위 밖. 예정 · 승인 기록까지만"). `config/dev-progress.php`에 USER-007 줄은 아직 없다(`_index/progress.md`에 없음)
- 근거 상세: 회원관리 개발 검토 `scripts/qa/reports/review/findings/member/E_privacy_permission.md`(E-01 · 02 · 04 · 05 · 06 · 07 · 08 · 10) · `회원관리_개발검토_종합.md`(2절 #15, 3절 007, 4절 #1 · #3). 공용 마스킹 부품(MaskingService · MaskingController · ReasonRequest · `<x-masked>` · reason-modal · AttachmentController)은 d562524a 이후 바뀌지 않았다(`git log d562524a..a8016168` 해당 파일 0건)

프로토타입 탭 ↔ 개발
| 프로토타입 | 개발에 있는 것 | 개발 뷰 · 코드 |
|---|---|---|
| 탭1 `tabPanel-vault` 민감정보 금고(주민번호 · 계좌 · 증빙 사본) | `tab=subjects` 수취 주체 표 — 주민번호 · 계좌는 `<x-masked>` 해제 버튼, 증빙은 "계약 원장 첨부에서 열람" 문구만 | `users/pii-control/index.blade.php:73-158` |
| 탭2 `tabPanel-retention` 보존기한 3계층 · 파기 스케줄러 | `tab=schedule` 파기 예정 표 + 승인 폼 + 보류 격리 표(삭제 버튼 없음) | `users/pii-control/_tab-schedule.blade.php:1-110` |
| 탭3 `tabPanel-fieldmap` 파기 필드 매핑 · 열람 이력 | `tab=fieldmap` 필드 맵 표(읽기 전용) + 열람 · 승인 로그 50건 | `users/pii-control/_tab-fieldmap.blade.php:1-84` |
| `unmaskReasonModal` | 공용 사유 모달 `layerReason`(`<x-masked>` 버튼이 연다) | `resources/views/admin/inc/reason-modal.blade.php:28-102`, `components/masked.blade.php:26-43` |
| `docViewerModal`(Presigned 5분) | 이 화면에는 없음. 비공개 첨부 다운로드 → S3면 임시 URL 300초 | `AttachmentController.php:140-148`, `config/filesystems.php:190` |
| `modal-pii-destruction-result`(007-P2) | 없음 | — |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.users.pii-control.index` | 민감 정보 열람 통제 | routes/admin.php:650-658, `_index/routes.md` 215-216. admin_menus 행은 저장소 시드 · 마이그레이션에 없음(DB 관리 화면에서 등록) |
| `admin.admin-logs.index` | 관리자 로그(프로토 CONF-010) | `_index/routes.md` 75. 열람 이력 원본. 정산 감사 탭 1의 감사 영역 `pii`(이벤트 `pii_unmask` · `pii_destruction`)가 이 화면을 발생 화면 `ADMN-USER-007`로 가리킴(app/Support/Audit/SettlementAuditEvent.php:117-121) |

- 프로토타입 권한 행: `privacy` "민감 정보 · 시스템 감사 로그" = USER-007 · CONF-010 1행(`prototype_clean/common-master.js:63`), 재무팀 기본 `privacy: "RW"`(:88). 개발은 위 2행(+ `admin.login-logs.index`)으로 나뉜다.
- 파기 승인은 **수정 권한**(`can_update`, 접미사 `update`)으로 판정되고 버튼도 `@adminCan('admin.users.pii-control.index', 'can_update')`로 숨긴다(_tab-schedule.blade.php:57-66). 앞 판의 규칙 이름(`destruction.store` 등록 권한)은 쓰지 않는다.
- **마스킹 해제는 메뉴 권한 밖 그대로**: `admin.masking.unmask`는 `admin.auth`만(routes/admin.php:185-186) · 판정 `MaskingService::canUnmask()` = 최고관리자만(MaskingService.php:379-382). 이 화면도 같은 함수로 해제 버튼을 보인다(PiiControlService.php:90-91). → 8절 · 7절(M-02 · POLICY_D_USER7 A 결정과 다름).
- 증빙 사본 다운로드 `admin.attachments.download`(routes/admin.php:180-181)도 메뉴 권한 밖, 첨부 대상 메뉴 조회 권한을 컨트롤러가 직접 본다(AttachmentController.php:32-49, 60-78).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. 탭은 쿼리 `tab`(`subjects` 기본 · `schedule` · `fieldmap`, PiiControlService.php:28-32).

### USER-007 탭1 민감정보 금고 · 열람 사유 모달 · 증빙 뷰어
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 화면(탭 1 · 필터) | GET | `/users/pii-control?tab=subjects&subject=&keyword=` | `admin.users.pii-control.index` | can_view | PiiControlController@index :29-42 |
| 마스킹 해제(주민번호 · 계좌 — **필드마다 1회 호출**) | POST | `/masking/unmask` | `admin.masking.unmask` | 메뉴 권한 밖(canUnmask = 최고관리자) | MaskingController@unmask :49 (변경 없음) |
| 해제 상태 재조회(TTL 안에서만) | POST | `/masking/unmask` + `grant_only=1` | `admin.masking.unmask` | 〃 | MaskingController@unmask :59-64 (만료 시 410) |
| 즉시 재마스킹(단건 · 전체) | DELETE | `/masking/grants` (규칙) | `admin.masking.grants.destroy` (규칙) | 메뉴 권한 밖 | 개발 미구현 — 해제 기록은 세션 `masking_grants`(MaskingService.php:109, 130-138), 화면은 타이머로만 다시 가림 |
| 증빙 사본 열람 | GET | `/attachments/{attachment}/download` | `admin.attachments.download` | 대상 메뉴 조회 | AttachmentController@download (**사유 없음** :106). 이 화면에는 링크가 없다 — "계약 원장 첨부에서 열람" 문구만(index.blade.php:139-142). `PiiControlService::evidenceRoute()`(:170-173)는 만들어 뒀지만 뷰에서 안 씀 |
| 증빙 사본 열람 사유 전달 | GET 쿼리 | `…/download?reason=&reason_etc=&reason_ref=` (규칙) | (같은 라우트) | | 개발 미구현 |

### USER-007 탭2 보존기한 · 파기 스케줄러 · 007-P2 파기 결과
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 파기 예정 · 보류 격리 목록 | GET | `/users/pii-control?tab=schedule` | `admin.users.pii-control.index` | can_view | PiiControlController@index |
| 계층 1 파기 승인(기록만, 삭제 없음) | PUT | `/users/pii-control/{rightsHolder}` | `admin.users.pii-control.update` | can_update | PiiControlController@update :45-56 → PiiControlService::approveDestruction :118-167 |
| 파기 보류 설정 · 해제(세무조사 · 소송 · 이의신청) | PUT | `/users/pii-control/{rightsHolder}/hold` (규칙) | `admin.users.pii-control.hold.update` (규칙) | can_update | 개발 미구현(플래그 읽기만 — PiiControlRepository.php:81, 106) |
| 실제 파기 배치 | — | — | — | — | 개발 미구현(배치가 승인 기록을 읽어 실행 예정 — PiiControlController.php:18, 000268:16-17) |
| P2 파기 결과 보고서 | GET | `/users/pii-control/destructions/{batch}` (규칙) | `admin.users.pii-control.destructions.show` (규칙) | can_view | 개발 미구현 |
| P2 파기 확인서 PDF | GET | `/users/pii-control/destructions/{batch}/download` (규칙) | `admin.users.pii-control.destructions.download` (규칙) | can_download | 개발 미구현 |

### USER-007 탭3 필드 매핑 · 열람 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 파기 필드 매핑 표 + 열람 · 승인 로그 | GET | `/users/pii-control?tab=fieldmap` | `admin.users.pii-control.index` | can_view | PiiControlRepository::fieldMap :129-136 · unmaskLogs :146-160 |
| 매핑 수정("코드 수정 없는 테이블 기반 통제") | PUT | `/users/pii-control/field-maps/{fieldMap}` (규칙) | `admin.users.pii-control.field-maps.update` (규칙) | can_update | 개발 미구현 — 행 추가 · 수정은 DB 직접(PiiDestructionFieldMap.php:10-11) |
| 열람 이력 전체 · 정산 감사 로그로 이동(`goNav` CONF-010) | → | `/admin-logs?type=unmask` 또는 `/admin-logs?tab=audit&category=pii` | `admin.admin-logs.index` | 조회(관리자 로그 메뉴) | AdminLogController@index — 이 화면에는 이동 버튼이 없음(_tab-fieldmap.blade.php:46-50 배지만) |

## 3. 폼 필드 · 검증

### 탭1 목록 필터 (PiiControlController::index — Request 클래스 없음, `stringQuery`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `tab` | `subjects` · `schedule` · `fieldmap`, 밖이면 `subjects`(PiiControlService.php:80) | 탭 버튼 |
| `subject` · `#subject` | `''` 전체 · `personal` 개인 비사업자/프리랜서 · `business` 법인/개인사업자 · `refund` 합격환급반 수강생(PiiControlService.php:35-40, 라벨은 프로토 문구) | `#holderTypeFilter` ALL · INDIVIDUAL · BIZ · REFUND |
| `keyword` · `#keyword` | `rights_holders.code` · `name` LIKE(PiiControlRepository.php:57-62) | (없음) |

- 결함(정책 아님): 저장소가 `rights_holder_type = 'personal'`로 거른다(PiiControlRepository.php:51-55, 뷰 index.blade.php:117 · 122도 같음). 그런데 `rights_holders.rights_holder_type` 값은 `RIGHTS_HOLDER` · `CONSIGNOR`이고 `personal`은 `tax_type` 값이다(`_index/schema.md` rights_holders `tax_type` · `rights_holder_type`, RightsHolder.php TYPE_*). 테스트가 `rights_holder_type => 'personal'`로 심어 통과한다(PiiControlTest.php:49). 실데이터에서는 개인 필터 0건 · 모든 행 "법인·사업자는 수집 안 함"이 된다. `refund` 필터는 저장소에 분기가 없어 전체가 나온다.

### 열람 사유 모달 → 마스킹 해제 (MaskingUnmaskRequest — 변경 없음)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `target_type` | required · max 30, 허용 목록 밖이면 422 | `rights_holder` · `supplier` · `refund_claim` · `user`(MaskingService.php:43-63). 이 화면은 `rights_holder`만 보냄(index.blade.php:125, 133) | 행의 `holderCategory` |
| `target_id` | required · integer ≥ 1 | | 행 식별자 |
| `field` | required · max 30 | `resident_no_enc` 주민번호 · `account_no_enc` 계좌번호 | 프로토는 한 번에 둘 다 해제(`requestUnmask(id,'UNMASK')` L925) |
| `level` | nullable · `high` · `basic` — 권리자 · 환급 필드는 high 확정(MaskingService.php:90-95). 이 화면은 level 생략 = 기본 high(Masked.php:59) | | (없음 — 전부 사유 필수) |
| `reason` | high면 required · `in:` ReasonRequest::REASONS | `refund_account` · `delivery_error` · `identity_check` · `payment_inquiry` · `legal_request` · `settlement_check` · `etc`(ReasonRequest.php:48-56) | `.reason-chip`(L512-515) |
| `reason_etc` | reason=etc일 때 required · 10~150자(ReasonRequest.php:64-86) | | `#unmaskReasonInput`(공백 제외 10자 · 서로 다른 글자 3개 · 200자 이하, M-04) |
| `reason_ref` · `screen` | nullable · max 50 영숫자 하이픈 · max 100 | | (없음) |
| 응답 | `{success, value, level, ttl}` — ttl = 30초 상수(MaskingService.php:106) | | `remaskHolderSec` 기본 30 |

- 차이: 화면 안내문은 "사유(10자 이상)를 입력하면"(index.blade.php:42-45, `reasonMin`=10)이라 적지만, 실제 해제 검증은 정형 사유를 고르면 0자 통과 그대로다(종합 2절 #15 결함 · E-04, 정책 아님).

### 탭2 파기 승인 (PiiDestructionApproveRequest, `_index/requests.md` 2319)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `reason` | required · string · min 10(`PiiControlService::REASON_MIN`) · max 500(PiiDestructionApproveRequest.php:16-21). 서비스가 trim 후 10자 미만이면 다시 거절(PiiControlService.php:124-128) | | 승인 사유(프로토는 고정 문구 L1130) — 개발 입력칸 `name="reason"` `maxlength=500`(_tab-schedule.blade.php:61-62) |
| (서버 판정) `destruction_hold` | true면 422 "파기 보류로 격리된 건"(PiiControlService.php:130-134) | | 보류 배지(`holdYn` L756-) |
| (서버 판정) `tier1_destroy_due_at` | NULL이면 422 "예정일이 산정되지 않아"(:136-140), 버튼도 disabled(_tab-schedule.blade.php:63-64) | | 파기 예정일 |

- 승인 결과: `destruction_batch_status=APPROVED` · `destruction_approved_by` · `destruction_approved_at`만 바뀌고 개인정보 칸은 그대로(:147-154). 로그 `action=update` · `sub_action=pii_destruction_approve` · `target_type=rights_holder` · before/after 상태값 · reason(:158-166) → 정산 감사 체인에 들어감(CONF-010 이벤트 `pii_destruction`).
- 사유 규칙이 MemberReasonRequest(공백 제외 10자 · 서로 다른 글자 3개 · 200자 이하)와 다르다 — 공백 포함 10자 · 500자 · 반복 글자 검사 없음.

### 탭2 파기 보류 (규칙 — 개발 미구현)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `destruction_hold` | boolean | true · false | 보류 사유 배지 |
| `hold_reason` (규칙) | required · max 200 | `tax_audit` 세무조사 · `litigation` 소송 · `objection` 이의신청 (규칙) | `holdReason` |

## 4. 목록 필터 · 정렬 · 표 컬럼

### KPI 4 (PiiControlService::summary :98-110, index.blade.php:19-24)
| 프로토 KPI(L307-322) | 개발 KPI |
|---|---|
| 암호화 관리 대상 주체 | 전체 수취 주체(`subjects` 건수) |
| 현재 마스킹 일시 해제 중 `#kpiUnmaskedCount` | **주민등록번호 보유**(`has_resident_no` 건수) — 해제 중 건수 없음 |
| 계층 1 개인정보 파기 후보 `#kpiDestructCandidate` | 계층 1 파기 기한 도래(예정일 ≤ 오늘 · DONE 아님) |
| 계층 3 파기 보류 예외 | 파기 보류 격리(`destruction_hold` true 건수) |

### 탭1 수취 주체 표 (index.blade.php:96-158, 정렬 `rh.id` 내림차순)
| 프로토타입 컬럼(`vaultTbody`, L352-363) | 개발 값 · 표시 |
|---|---|
| 식별자 / 성명(상호) | `rights_holders.code` · `name` (:112-115) |
| 주체 유형 및 수집 근거 | `rights_holder_type === 'personal'` ? "개인 비사업자/프리랜서" : "법인/개인사업자" + `tax_type` 원값(:116-119) — 3절 결함 참고 |
| 주민등록번호(AES-256) | 사업자: "법인·사업자는 수집 안 함" / 있음: `<x-masked type="resident_no" value="" target-type="rights_holder" field="resident_no_enc">` / 없음: "미수집"(:120-130). 저장소는 암호문을 고르지 않고 `has_resident_no` 플래그만(PiiControlRepository.php:44-46) |
| 지급/환급 은행 및 계좌번호 | `<x-masked type="account_no" … field="account_no_enc">` / "미등록"(:131-138). 은행명은 표시 안 함 |
| 프라이빗 S3 증빙 사본 | "계약 원장 첨부에서 열람" 문구만(:139-142) |
| 보존 계층 상태 | 보류 격리 / 예정일 미산정 / "계층 1 {예정일}"(:143-151) |

- 행 원천은 `rights_holders`(+ active 계약 `MIN(ended_at)`)뿐 — `refund_claims` · `suppliers` · `refunds` 행은 없다(PiiControlRepository.php:29-65).

### 탭2 파기 예정 표 (_tab-schedule.blade.php:25-74, 정렬 `tier1_destroy_due_at`, `id`)
| 프로토타입 컬럼(`retentionTbody`, L381-393) | 개발 값 |
|---|---|
| 레코드 식별자 / 대상자 · 계약 | `code` · `name`(계약 없음) |
| 계약 종료일 / 국세 법정신고기한 | 없음 |
| 계층 1 파기 예정일(신고기한 + 5년) | `tier1_destroy_due_at` 또는 "— 미산정" |
| 계층 2 원장 보존 만료일(장부 폐쇄 + 10년) | `tier2_retain_until` 또는 "— 미산정" |
| 계층 3 보류 사유 | 표에서 빼고 아래 "계층 3 — 파기 보류 격리" 표로 따로(:76-110, 사유 칸 없음) |
| 파기 배치 상태 | `destruction_batch_status` 라벨(PENDING 파기 예정 · APPROVED 승인 완료(배치 대기) · HELD 보류 격리 · DONE 파기 완료, PiiControlService.php:42-56) |
| (개발 추가) 승인자 / 승인 시각 | `destruction_approved_at` 또는 "미승인" |
| 승인 액션 | 사유 입력칸 + "파기 승인" 버튼(can_update) |

- 예정일을 채우는 코드가 없다 — 커밋 본문 "파기 기준일(법정신고기한 · 장부 폐쇄일)은 법령 해석이라 미산정 — NULL 이면 승인이 막힌다". 그래서 현재 모든 행이 "미산정"이고 승인 불가.

### 탭3 필드 맵 표 (_tab-fieldmap.blade.php:7-44, `is_active` · `sort_order` 순)
| 프로토 컬럼(L404-450) | 개발 컬럼 |
|---|---|
| 테이블 / 대상 컬럼명 | `target_table` + `.target_column` |
| 한글 필드 명칭 | `label` |
| 보존 계층 구분 | `tier_label` 없으면 `TIER_LABELS[retention_tier]` |
| 계층 1 만료 시 처리 방식 | `expiry_action` |
| 정산 원장 금액·조인 영향도 | `ledger_impact` |

시드 5행(PiiDestructionFieldMapSeeder.php:43-101, 멱등): `rights_holders.resident_no_enc`(계층 1) · `rights_holders.account_no_enc`(계층 1) · `rights_holders.name`(계층 2, 비식별 표시명 전환) · `attachments.file_path`(계층 1, 신분증 · 통장 사본) · `settlement_lines`(계층 2, 절대 삭제 금지). 프로토 이름 → 개발 이름: `rrn_encrypted` → `resident_no_enc`, `bank_account_enc` → `account_no_enc`, `holder_name` → `name`, `settlement_statements` → `settlement_lines`, `s3://private-bucket/id_cards/*` → `attachments.file_path`.

### 탭3 열람 · 승인 로그 (_tab-fieldmap.blade.php:46-84 ↔ `admin_logs`, 최근 50건, PiiControlRepository.php:146-160)
| 프로토타입 컬럼(`accessLogTbody`, L456-467) | 개발 컬럼 |
|---|---|
| 기록 시각 | `created_at` |
| 대상 식별자 / 성명 | `target_type #target_id`(성명 없음) |
| 수행 액션 구분 | `sub_action` 원값(`unmask` · `pii_destruction_approve`) — 증빙 다운로드(`download`)는 포함 안 함 |
| 입력된 사유 | `reason` |
| 작업자(RBAC 그룹) | `users.name`(역할 없음) |
| 재마스킹 / 후속 상태 | 고정 문구: unmask → "30초 후 자동 재마스킹", 승인 → "배치 대기" |

- 주의: `unmask`를 대상 구분 없이 읽는다 — 회원 · 주문 해제까지 이 표에 섞인다(CONF-010 정산 감사는 정산 대상 5종으로 좁힘, SettlementAuditEvent.php `pii_unmask`). "당일"이라는 주석과 달리 날짜 조건 없음(:139-146).

## 5. DB 테이블 · 컬럼

| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `pii_destruction_field_map` (`target_table` string(100) · `target_column` string(100) nullable · `label` string(100) · `retention_tier` tinyint 1 · 2 · 3 · `tier_label` string(60) · `expiry_action` string(255) · `ledger_impact` string(255) · `sort_order` · `is_active`, unique(`target_table`,`target_column`)) | | 파기 필드 매핑. 테이블 이름은 단수형(000268:31-64, `_index/schema.md` 2874) | 탭3 매핑 표 |
| `rights_holders.tier1_destroy_due_at` · `refund_claims.tier1_destroy_due_at` | date nullable | 계층 1 파기 예정일(신고기한 + 5년), NULL = 미산정(000268:73-76) | 탭1 상태 · 탭2 |
| `rights_holders.tier2_retain_until` · `refund_claims.…` | date nullable | 계층 2 원장 보존 만료일(장부 폐쇄 + 10년)(:78-81) | 탭2 |
| `rights_holders.destruction_batch_status` · `refund_claims.…` | string(20) nullable | `PENDING` · `APPROVED` · `HELD` · `DONE`(:83-86) | 탭2 |
| `rights_holders.destruction_approved_by` · `destruction_approved_at` · `refund_claims.…` | bigint unsigned · timestamp nullable | 승인자 users.id · 승인 시각(:88-96). 인덱스 `(tier1_destroy_due_at, destruction_batch_status)`(:99-104) | 탭2 승인자 |
| `rights_holders.resident_no_enc` | text | 주민번호 암호문(Laravel Crypt AES-256-CBC · APP_KEY). 이 화면은 존재 여부만 읽음 | 탭1 |
| `rights_holders.account_no_enc` · `bank_name` · `account_holder` | text · string | 정산 계좌 암호문 · 은행 · 예금주 | 탭1 |
| `rights_holders.destruction_hold` | boolean(캐스트 추가, RightsHolder.php ef3b5183) | 세무조사 · 소송 · 이의신청 진행 중이면 true(000151:27). **이 화면이 처음으로 읽는다**(PiiControlRepository.php:72) — 세팅 코드는 여전히 없음 | 탭2 보류 격리 |
| `prepayment_ledgers` · `support_fund_agreements` · `exclusive_contract_clawbacks` `.destruction_hold` | boolean | 미상계 선급금 · 미소진 지원금 · 미회수 반환 채권(000151:23-28) — 이 화면은 읽지 않음 | (없음) |
| `refund_claims.account_no_enc` · `bank_name` · `account_holder` | text | 합격 환급 계좌 암호문. 주민번호 칸은 여전히 없음(`_index/schema.md` refund_claims) | (화면에 행 없음) |
| `refunds.refund_bank_code` · `refund_account_no` · `refund_account_holder` | string · text | 현금 환불 수취 계좌 암호문. 파기 스케줄 칸 없음 | (없음) |
| `rights_holder_account_histories` · `suppliers.account_no_enc` · `attachments` | | 변경 전 계좌 · 매입처 계좌 · 증빙 파일 | 필드 맵에는 `attachments.file_path`만 |
| `admin_logs` (`sub_action` `unmask` · `pii_destruction_approve`, `reason`, `admin_id`, …) | | 열람 · 승인 감사 로그. 정산 감사 대상이면 `block_hash` 체인(CONF-010 000269) | 탭3 로그 |
| `pii_destruction_batches` · `pii_destruction_items` (규칙) | | 파기 배치 · 대조표 | 007-P2 — 개발 미구현 |
| `rights_holders.pii_destroyed_at` · `anonymized_name` (규칙) | | 파기 시각 · 비식별 표시명 | 개발 미구현 |

## 6. 개발 JS · 마크업 이름

| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `.st-tabs` 버튼(쿼리 `tab`) | 탭 전환(서버 왕복, index.blade.php:66-71) | 탭 버튼 · `tabPanel-vault` · `tabPanel-retention` · `tabPanel-fieldmap` |
| `#subject` (name `subject`) · `#keyword` (name `keyword`) | 탭1 필터(:74-94) | `#holderTypeFilter` |
| `.st-kpi-card` (4장) | KPI(:47-55) | `#kpiUnmaskedCount` · `#kpiDestructCandidate` 등 |
| `<x-masked …>` → `span.masked#masked-{type}-{id}-{field}` · `.masked__unmask[data-target="layerReason"][data-reason-mode="ajax"]` | 마스킹 칸 · 해제 버튼(Masked.php:77, masked.blade.php:26-43) | `.pii-chip` · `requestUnmask(id,'UNMASK')` |
| `window.maskedScheduleRemask(cellId, masked, ttl)` | TTL 뒤 재마스킹(masked.blade.php:56-71) | `.ttl-timer` 카운트다운 L1061 |
| `layerReason` · `reasonForm` · `reasonSelect` · `reasonEtc` · `reasonRef` · `reasonSubmit` 등 | 공용 사유 모달(reason-modal.blade.php:28-102) | `unmaskReasonModal` · `#unmaskReasonInput` · `#btnConfirmUnmask` |
| 행별 `<form method="post">` + `@method('PUT')` + `input[name=reason].st-fc` + "파기 승인" 버튼 | 파기 승인(모달 없이 표 안 폼, _tab-schedule.blade.php:58-65) | `approveTier1Destruction(idx)` L1119 |
| `remaskAllButton` · `remaskButton` (규칙) | 즉시 재마스킹 | `maskAllNow()` L290 — 개발 미구현 |
| `layerDocViewer` (규칙) | 증빙 뷰어 | `docViewerModal` — 개발 미구현 |
| `layerPiiDestructionResult` · `piiDestructionDownload` (규칙) | 007-P2 | `modal-pii-destruction-result` — 개발 미구현 |

- 개발 화면은 id가 거의 없다(필터 2개뿐). 표는 `.st-table`, 칩은 `.st-chip--ok/warn/ng/info`(정산 공용 settlement.css).

## 7. 기능 차이

### 결정 · 정본과 다른 점 (개발팀 전달 대상)
- **마스킹 해제 권한(회원 #3 · M-02 · POLICY_D_USER7 A)**: 결정 = 회원 쪽은 메뉴 권한 연동, 권리자 · 환급 쪽은 정산 권한 재무 운영자 그룹까지. 개발 = 여전히 최고관리자만(MaskingService.php:379-382), 이 화면도 같은 함수를 부른다(PiiControlService.php:90-91). 재무 담당자는 이 화면을 열어도 해제 버튼이 없다(PiiControlTest `해제_권한이_없으면_해제_버튼이_안_보인다`).
- **재마스킹 시간(회원 #1 결정)**: 설정값이어야 하나 개발은 30초 상수 그대로(MaskingService.php:106), 화면 문구도 상수를 그림(index.blade.php:39, 44).
- **환불 수취 계좌 보관 기간(D-USER7-01 — 환불 완료일 + 5년 후 파기)**: 개발 파기 스케줄 칸은 `rights_holders` · `refund_claims` 두 곳뿐(000268:27). `refunds.refund_account_*`에는 예정일 · 상태 칸이 없고 필드 맵 시드에도 없으며 화면 목록에도 없다. 기산점(환불 완료일)도 어디에도 계산되지 않는다.
- **합격환급 계좌(POLICY_D_USER7 A — 법정신고기한 + 5년)**: `refund_claims`에 스케줄 칸은 생겼지만 화면은 `rights_holders`만 읽는다(PiiControlRepository.php:31, 79, 104). `subject=refund` 필터는 라벨만 있고 분기 없음.
- **계층 1 · 2 예정일 산정**: 정본 기준(신고기한 + 5년, 장부 폐쇄 + 10년)이 있지만 개발은 "법령 해석이라 미산정"으로 두고 NULL이면 승인을 막는다 — 현재 승인 가능한 행이 없다(커밋 본문, PiiControlService.php:136-140).
- **증빙 사본 열람 사유(POLICY_D_USER7 A — 권리자 · 계약 · 선급금 · 합격환급 증빙은 10자 사유 필수)**: 개발은 여전히 기록만(AttachmentController.php:106), 이 화면에는 증빙 열람 링크 자체가 없다.
- **계층 3 보류 판정(POLICY_D_USER7 A — 선급금 잔액 · 대손 · 미소진 지원금은 원장 값으로 자동, 세무조사 · 소송 · 이의신청은 수동 보류 + 사유)**: 개발은 `rights_holders.destruction_hold` 플래그만 읽고(나머지 3개 테이블 플래그 미사용), 자동 산출 · 수동 보류 설정 화면 · 보류 사유 칸이 없다. 안내문은 "자동 격리합니다"라고 적는다(_tab-schedule.blade.php:15-16).
- **합격환급 수취인 주민번호(S-02 — 항상 받음 · 암호화 보관)**: `refund_claims`에 주민번호 칸 여전히 없음.
- **열람 사유 10자(정본 · 결함 E-04)**: 화면 안내는 10자 이상이라 적지만 해제 검증은 정형 사유만 고르면 0자 통과(3절).

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 파기 승인 이력 칸(승인자 · 승인 시각), 배치 상태 4종(PENDING · APPROVED · HELD · DONE), 보류 격리 건을 별도 표로 보여 주기, 예정일 미산정 시 승인 차단.
- 승인 사유 서버 재검증 · 보류 건 승인 차단(422), 승인 로그가 정산 감사 해시 체인에 들어감.
- 저장소가 암호문을 고르지 않고 존재 플래그만 내림 — HTML · 뷰 값 · 로그에 원문 없음을 테스트가 고정(PiiControlTest :87, :108, :216).
- 기존: 해제 허용 목록(422), 등급 2단 · 서버 확정, 로그 실패 시 원문 미반환, TTL 만료 410, 복호화 불가 표시, 관리자별 일일 해제 건수, `reason_ref` · `screen`, 비공개 첨부 다운로드 기록.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 실제 파기 실행 · 비식별 표시명 전환 · 007-P2 파기 결과 보고서 · 파기 확인서 PDF.
- 파기 보류 수동 설정 · 해제와 보류 사유, 보존 3계층 예정일 계산(계약 종료일 · 법정신고기한 칸).
- 주민번호 + 계좌 한 번의 사유로 동시 해제(개발은 필드마다).
- 증빙 사본 뷰어(워터마크 · 창 닫으면 URL 폐기) · 열람 전 사유.
- 즉시 재마스킹(단건 · 전체) · '현재 해제 중' KPI · 남은 초 표시.
- 재마스킹 시간 운영 설정(`remaskHolderSec`, CONF-003).
- 필드 맵 수정 화면(개발은 표 읽기만, 행 추가는 DB).
- 수취 주체 중 합격환급 수강생(REFUND) · 매입처 · 환불 수취 계좌 행.
- 파기 매핑에 넣어야 할 개발 테이블(시드 5행 밖): `rights_holder_account_histories`, `rights_holders.birth_date` · `address` · `phone`, `refunds.refund_account_*`, `refund_claims.account_*`, `suppliers.account_no_enc`.
- 참고(프로토 내부 불일치): 탭2는 계층 3 = 파기 보류 예외(L378)인데 P2 보고서는 계층 3 = 세무증빙 · 감사로그 5년 보존(L623-634). 개발은 탭2 정의(계층 3 = 보류 예외, PiiDestructionFieldMap.php:25-31)를 따랐다. 프로토 수정 대상으로 남긴다.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 화면 경로(규칙 `admin.pii-records.*`, 앞 판) | `admin.users.pii-control.index` · `.update` |
| 탭 `tabPanel-vault` · `-retention` · `-fieldmap` | `?tab=subjects` · `schedule` · `fieldmap` |
| `#holderTypeFilter` ALL · INDIVIDUAL · BIZ · REFUND | `subject` `''` · `personal` · `business` · `refund` |
| `pii_destruction_field_map`(프로토 L403) 컬럼 `table_name` · `column_name` · `tier` · `action` | `pii_destruction_field_map`(단수 그대로) `target_table` · `target_column` · `retention_tier` · `expiry_action` (+ `tier_label` · `ledger_impact` · `sort_order` · `is_active`) |
| 파기 상태 candidate · hold · destroyed (앞 판 규칙) | `PENDING` · `APPROVED` · `HELD` · `DONE` |
| 계층 1 파기 예정일 · 계층 2 보존 만료일 | `tier1_destroy_due_at` · `tier2_retain_until` |
| 파기 승인 행위 | `admin_logs.sub_action = pii_destruction_approve`(action `update`) |
| `rights_holders.rrn_encrypted` · `bank_account_enc` · `holder_name` | `resident_no_enc` · `account_no_enc` · `name` |
| `s3://private-bucket/id_cards/*` | `attachments.file_path`(disk `secure`) |
| 암호화 "AES-256 (AWS KMS)" | Laravel Crypt AES-256-CBC(APP_KEY), 시드 문구에는 "KMS 참조 해제"가 프로토 그대로 남음 |
| `ADMN_AUDIT_LOG` | `admin_logs` |
| 행위 "마스킹 해제" · "Presigned URL 발급" | `action=view` + `sub_action` `unmask` · `download` |
| 계좌 마스킹 `110-421-******` | `****8920`(뒤 4자리) |
| 열람 유지시간 `remaskHolderSec` | `MaskingService::UNMASK_TTL_SECONDS = 30` |
| 역할 `ROLE_FINANCE_ADMIN` | `admin_roles.code = finance` |
| 파기 승인 권한(재무 담당자) | 메뉴 `can_update` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

회원관리 검토 4절에 이미 있는 것: **#1**(재마스킹 시간 — 결정됨, 개발 30초 상수는 전달 대상 · a8016168에도 상수) · **#3**(마스킹 해제 권한). 회원 쪽은 **→ 결정(white 10-27, M-02)**: 권고대로(메뉴 권한 연동) · 권리자 · 환급 쪽은 **→ 정본대로(POLICY_D_USER7 A, 03권 §3.4 L313)**: 정산 권한 재무 운영자 그룹 — 개발 `canUnmask`를 권리자 · 환급 필드는 재무 그룹까지. **a8016168 기준 개발은 아직 최고관리자만(7절)**

1. **증빙 사본(신분증 · 통장) 열람 사유** — **→ 정본대로(POLICY_D_USER7 A, 03권 §3.4 L314 · §16.1 L358 · §3.3 L305)**: 증빙 사본 다운로드는 10자 사유 필수 — 대상은 권리자 · 계약 · 선급금 · 합격환급 증빙 첨부, 문의 · 후기 등 그 밖의 첨부는 기록만(개발팀 전달). a8016168 기준 개발은 기록만(AttachmentController.php:106), USER-007 화면에는 증빙 링크 없음.
2. **합격환급 수취인 주민번호 수집 · 22% 원천징수** — **→ 결정(v6.92 white, S-02)**: 합격환급 신청 때 주민번호를 항상 받음(번호만 입력 · USER-007 암호화 보관), 원천징수 대상 — 개발 `refund_claims`에 주민번호 암호문 칸 추가 필요. a8016168 기준 칸 없음. 개발 필터 라벨은 "제세공과금 22% 신고용 수집"을 프로토 그대로 적었다(PiiControlService.php:39).
3. **계층 3 파기 보류 판정 방식** — **→ 정본대로(POLICY_D_USER7 A, 03권 §3.5 L334 · L335)**: 선급금 잔액 · 대손 · 미소진 지원금은 후보 산출 때 원장 값으로 자동 판정, 세무조사 · 소송 · 이의신청은 운영자 수동 보류(사유 필수). a8016168 기준 개발은 `rights_holders.destruction_hold` 플래그 읽기만(자동 판정 · 수동 설정 · 사유 없음).
4. **환불 수취 계좌 보관 기간 기산점** — **→ 결정(v6.87 white, D-USER7-01): 환불 수취 계좌 원번호는 환불 완료일 + 5년 후 파기(정산 03권 v4.0.13).** · 합격환급 계좌는 **→ 정본대로(POLICY_D_USER7 A, 03권 §3.5 L328)**: 계층 1 기준선 법정신고기한 + 5년. a8016168 기준 개발은 `refunds`에 파기 스케줄 칸이 없고, `refund_claims`는 칸만 있고 화면 · 산정 없음.

## 출처
- routes/admin.php:180-186, 650-658 · `_index/routes.md` 29-30, 215-216
- app/Http/Controllers/Admin/PiiControlController.php:1-63 · app/Http/Requests/Admin/PiiDestructionApproveRequest.php:16-38 · `_index/requests.md` 2319
- app/Services/Admin/PiiControlService.php:28-173 · app/Repositories/Admin/PiiControlRepository.php:29-160
- app/Models/PiiDestructionFieldMap.php:15-44 · app/Models/RightsHolder.php(ef3b5183 fillable · casts) · database/seeders/PiiDestructionFieldMapSeeder.php:22-103
- database/migrations/2026_10_26_000268_create_pii_destruction_field_map_and_schedule_columns.php:27-133 · `_index/schema.md` 2874(pii_destruction_field_map), refund_claims · rights_holders 000268 행
- resources/views/admin/users/pii-control/index.blade.php:1-168 · _tab-schedule.blade.php:1-110 · _tab-fieldmap.blade.php:1-84
- tests/Feature/Admin/PiiControlTest.php:49, 87-304(11건)
- app/Services/MaskingService.php:43-138, 327-357, 379-382 · app/Http/Controllers/Admin/MaskingController.php:49-126 · ReasonRequest.php:48-124 · MaskingUnmaskRequest.php · app/View/Components/Masked.php:59-77 · resources/views/components/masked.blade.php:11-71 · resources/views/admin/inc/reason-modal.blade.php:28-102
- app/Http/Controllers/Admin/AttachmentController.php:32-49, 60-148 · config/filesystems.php:190 · app/Support/Audit/SettlementAuditEvent.php:117-121
- database/migrations/2026_09_21_000151_add_destruction_hold_columns.php · 2026_10_19_000219_add_refund_account_columns_to_refunds_table.php:12-23 · 2026_10_21_000230_create_rights_holder_account_histories_table.php:32-51
- 프로토타입: prototype_clean/ADMN-USER-007_baseline.html L290 · 307-345 · 352-467 · 492-648 · 659-1179, prototype_clean/common-master.js:63 · 88 · 415-421
