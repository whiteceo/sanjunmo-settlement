# ADMN-USER-007 민감 정보 열람 통제 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-USER-007_baseline.html` (원본 상태: `18d66c1` v6.92)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: USER-007(탭 3개: 1 민감정보 금고 · 2 보존기한 · 파기 · 3 필드 매핑 · 열람 이력) · 열람 사유 모달(`unmaskReasonModal`) · 증빙 뷰어(`docViewerModal`) · 007-P2 파기 결과 보고서(`modal-pii-destruction-result`)
- 개발 진행: **미구현(규칙 기반 명명)**. `_index/progress.md`에 USER-007 줄 없음, 라우트 · 뷰 없음(routes/admin.php에서 privacy · pii · retention · destruct 검색 0건). 화면 밖 공용 부품만 있다 — 마스킹 해제 API(`admin.masking.unmask`) · `<x-masked>` 컴포넌트 · 공용 사유 모달(`layerReason`) · 암호화 보관(권리자 · 매입처 · 환급 · 환불 계좌) · `destruction_hold` 플래그 · 비공개 첨부 다운로드 · 관리자 로그(`admin_logs`)
- 근거 상세: 회원관리 개발 검토 `scripts/qa/reports/review/findings/member/E_privacy_permission.md`(E-01 · 02 · 04 · 05 · 06 · 07 · 08 · 10) · `회원관리_개발검토_종합.md`(2절 #15, 3절 007, 4절 #1 · #3). 파일:줄은 이 명세 작성 때 다시 확인했다(검토 문서의 MaskingController 줄 번호 497-529는 현재 99-137)

프로토타입 탭 ↔ 개발
| 프로토타입 | 개발에 있는 것 | 개발 뷰 · 코드 |
|---|---|---|
| 탭1 `tabPanel-vault` 민감정보 금고(주민번호 · 계좌 · 증빙 사본) | 화면 없음. 권리자 등록 · 수정 화면 안의 `<x-masked>` 해제 버튼, 정산서 · 환급 심사 · 매입처 목록의 계좌 해제 | `rights-holders/form.blade.php:216-217, 588-589`, `settlement/statements/index.blade.php:130-133`, `pass-refunds/show.blade.php:228`, `book-supply/_suppliers.blade.php:22, 32` |
| 탭2 `tabPanel-retention` 보존기한 3계층 · 파기 스케줄러 | `destruction_hold` 컬럼만(파기 배치 · 분리 저장 "별건") | `database/migrations/2026_09_21_000151_add_destruction_hold_columns.php:17` |
| 탭3 `tabPanel-fieldmap` 파기 필드 매핑 · 열람 이력 | 매핑 없음. 열람 이력은 관리자 로그 화면(`type=unmask`) | `admin-logs/index.blade.php`, `LogSearchRequest.php:59-66` |
| `unmaskReasonModal` | 공용 사유 모달 `layerReason` | `resources/views/admin/inc/reason-modal.blade.php:28-102` |
| `docViewerModal`(Presigned 5분) | 비공개 첨부 다운로드 → S3면 임시 URL 리다이렉트(300초) | `AttachmentController.php:140-148`, `config/filesystems.php:190` |
| `modal-pii-destruction-result`(007-P2) | 없음 | — |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.pii-records.index` (규칙) | 민감 정보 열람 통제 | 개발 미구현, 규칙 기반 명명. 탭 2 · 3은 하위 자원으로 두어 같은 메뉴로 판정(접미사 → `.index` 정규화 후 끝에서 두 번째 세그먼트를 걷어 `admin.pii-records.index`로 귀속 — AdminPermissionService 정규화 규칙, E 1절) |
| `admin.admin-logs.index` | 관리자 로그(프로토 CONF-010) | 개발 있음(`_index/routes.md` 305). 열람 이력 원본 |

- 프로토타입 권한 행: `privacy` "민감 정보 · 시스템 감사 로그" = USER-007 · CONF-010 1행(`prototype_clean/common-master.js:63`), 재무팀 기본 `privacy: "RW"`(:88). 개발은 위 2행(+ CONF-010 쪽 `admin.login-logs.index`)으로 나뉜다.
- **마스킹 해제는 메뉴 권한 밖**: `admin.masking.unmask`는 `admin.auth`만 걸리고(routes/admin.php:181-184) 판정은 `MaskingService::canUnmask()` = 최고관리자만(MaskingService.php:359-382). 해제 버튼도 같은 판정으로 숨김(View/Components/Masked.php:70-74). 재무 담당자가 열람하려면 종합 4절 #3 결정이 먼저다.
- 증빙 사본 다운로드 `admin.attachments.download`도 메뉴 권한 밖이고, 첨부가 매달린 대상의 메뉴 조회 권한을 컨트롤러가 직접 본다 — 권리자 서류는 `admin.rights-holders.index`(AttachmentController.php:32-49, 60-78).
- 파기 승인(탭2)은 등록 권한(`destruction.store`)으로 판정된다. 프로토타입 "재무 담당자 승인 · 무인 자동삭제 금지"(L390)를 역할로 더 좁힐지는 메뉴 권한 설정으로 처리(권한 축 5개: 조회 · 등록 · 수정 · 삭제 · 다운로드).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`.

### USER-007 탭1 민감정보 금고 · 열람 사유 모달 · 증빙 뷰어
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(수취 주체 필터) | GET | `/pii-records?target_type=&holder_type=&keyword=` (규칙) | `admin.pii-records.index` (규칙) | 조회 | 개발 미구현 |
| 마스킹 해제(주민번호 · 계좌 — **필드마다 1회 호출**) | POST | `/masking/unmask` | `admin.masking.unmask` | 메뉴 권한 밖(canUnmask = 최고관리자) | MaskingController@unmask (개발 있음) |
| 해제 상태 재조회(TTL 안에서만) | POST | `/masking/unmask` + `grant_only=1` | `admin.masking.unmask` | 〃 | MaskingController@unmask :57-65 (만료 시 410) |
| 즉시 재마스킹(단건 · 전체) | DELETE | `/masking/grants` (규칙) | `admin.masking.grants.destroy` (규칙) | 메뉴 권한 밖(본인 세션의 해제 기록만 지움) | 개발 미구현 — 해제 기록은 세션 `masking_grants`(MaskingService.php:109, 130-138). 화면은 타이머로만 다시 가림(masked.blade.php:56-71) |
| 증빙 사본 열람(Presigned 5분) | GET | `/attachments/{attachment}/download` | `admin.attachments.download` | 대상 메뉴 조회(`admin.rights-holders.index`) | AttachmentController@download (개발 있음, **사유 없음** — 8절 Q1) |
| 증빙 사본 열람 사유 전달 | GET 쿼리 | `…/download?reason=&reason_etc=&reason_ref=` (규칙) | (같은 라우트) | | 개발 미구현 |

### USER-007 탭2 보존기한 · 파기 스케줄러 · 007-P2 파기 결과
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 파기 후보 · 보류 목록 | GET | `/pii-records/retention?status=` (규칙) | `admin.pii-records.retention.index` (규칙) | 조회 | 개발 미구현 |
| 계층 1 필드 파기 승인 실행 | POST | `/pii-records/retention/{rightsHolder}/destruction` (규칙) | `admin.pii-records.retention.destruction.store` (규칙) | 등록 | 개발 미구현 |
| 파기 보류 설정 · 해제(세무조사 · 소송 · 이의신청) | PUT | `/pii-records/retention/{rightsHolder}/hold` (규칙) | `admin.pii-records.retention.hold.update` (규칙) | 수정 | 개발 미구현(컬럼만 — 000151:15, 27) |
| P2 파기 결과 보고서 | GET | `/pii-records/destructions/{batch}` (규칙) | `admin.pii-records.destructions.show` (규칙) | 조회 | 개발 미구현 |
| P2 파기 확인서 PDF | GET | `/pii-records/destructions/{batch}/download` (규칙) | `admin.pii-records.destructions.download` (규칙) | 다운로드 | 개발 미구현 |

### USER-007 탭3 필드 매핑 · 열람 이력
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 파기 필드 매핑 표 | GET | `/pii-records/field-maps` (규칙) | `admin.pii-records.field-maps.index` (규칙) | 조회 | 개발 미구현 |
| 매핑 수정("코드 수정 없는 테이블 기반 통제") | PUT | `/pii-records/field-maps/{fieldMap}` (규칙) | `admin.pii-records.field-maps.update` (규칙) | 수정 | 개발 미구현 |
| 열람 · 파기 이력(화면 안 표) | GET | `/pii-records/access-logs` (규칙) | `admin.pii-records.access-logs.index` (규칙) | 조회 | 개발 미구현 — 데이터는 `admin_logs`(sub_action `unmask` · `download`) |
| 열람 이력 전체 · 정산 감사 로그로 이동(`goNav` CONF-010) | → | `/admin-logs?type=unmask` | `admin.admin-logs.index` | 조회(관리자 로그 메뉴) | AdminLogController@index (개발 있음) |

## 3. 폼 필드 · 검증

### 열람 사유 모달 → 마스킹 해제 (MaskingUnmaskRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `target_type` | required · max 30, 허용 목록 밖이면 422 | `rights_holder` · `supplier` · `refund_claim` · `user`(MaskingService.php:43-63) | 행의 `holderCategory`(INDIVIDUAL · BIZ → `rights_holder`, REFUND → `refund_claim`) |
| `target_id` | required · integer ≥ 1 | | 행 식별자(`RH-0019` 등 — 개발은 숫자 id) |
| `field` | required · max 30 | `resident_no_enc` 주민번호 · `account_no_enc` 계좌번호 | 프로토는 한 번에 둘 다 해제(`requestUnmask(id,'UNMASK')` L925) |
| `level` | nullable · `high` · `basic` — 권리자 · 환급 필드는 basic을 보내도 high로 확정(MaskingService.php:85-95, MaskingUnmaskRequest.php:75-82) | | (없음 — 전부 사유 필수) |
| `reason` | high면 required · `in:` ReasonRequest::REASONS | `refund_account` 환불 계좌 확인 · `delivery_error` 배송 오류 확인 · `identity_check` 본인 확인 요청 · `payment_inquiry` 결제 오류 조사 · `legal_request` 법적 요청 대응 · `settlement_check` 정산 · 지급 확인 · `etc` 기타(직접 입력) (ReasonRequest.php:48-56) | 빠른 선택 칩 4개 `.reason-chip`(L512-515) — 프로토 칩은 문장을 채울 뿐 |
| `reason_etc` | reason=etc일 때 required · 10~150자(ReasonRequest.php:64-86) | | `#unmaskReasonInput`(공백 제외 10자 · 서로 다른 글자 3개 이상 · v6.92부터 공백 포함 200자 이하 `maxlength=200`(M-04), `reasonCheck`) — 개발 150자 상한과 50자 차이 |
| `reason_ref` | nullable · max 50 · 영숫자 하이픈 | | (없음) |
| `screen` | nullable · max 100 (호출 라우트 이름) | | (없음) |
| 응답 | `{success, value, level, ttl}` — ttl = 30초 상수(MaskingService.php:106) | | 열람 유지시간 `remaskHolderSec` 기본 30(`ttlSec()` L659, common-master.js:421) |

- 차이: 프로토는 모든 해제에 **자유 입력 10자**, 개발은 정형 사유를 고르면 0자 통과(종합 2절 #15 결함 · E-04, 정책 아님). prototype_dev는 개발 이름(`reason` select + `reason_etc`)으로 바꾸되 상세 10자 칸은 정본대로 남긴다.

### 증빙 사본 열람 (규칙 — 현재 개발은 입력 없음)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` · `reason_etc` · `reason_ref` (규칙) | ReasonRequest와 같음 | `unmaskReasonModal`(mode `DOC`) → `confirmUnmaskAction` L987 |

### 탭1 목록 필터 (규칙)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `target_type` (규칙) | `rights_holder` · `refund_claim` · `supplier` · `refund`(규칙 — 환불 수취 계좌) | `#holderTypeFilter` ALL · INDIVIDUAL · BIZ · REFUND |
| `holder_type` | `personal` 개인 · `business` 사업자 · `consignor` 위탁자 · `internal` 자사 권리자(RightsHolder.php:55-65, 파생 :386-401) | INDIVIDUAL → `personal`, BIZ → `business` |
| `keyword` (규칙) | 권리자명 · 권리자번호 | (없음) |

### 탭2 파기 승인 · 보류 (규칙)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `reason` | MemberReasonRequest 규칙(공백 제외 10자 · 서로 다른 글자 3개 · 200자 이하) (규칙) | | 승인 사유(프로토는 고정 문구 L1130) |
| `fields[]` (규칙) | 파기할 매핑 행, 기본 = 계층 1 전부 | `resident_no_enc` · `account_no_enc` · `name`(비식별 전환) · 증빙 첨부 | 파기 대상 필드 |
| `destruction_hold` | boolean | true · false | 보류 사유 배지(`holdYn` L756-) |
| `hold_reason` (규칙) | holder 단위 보류는 required · max 200 | `tax_audit` 세무조사 · `litigation` 소송 · `objection` 이의신청 (규칙, 000151:15 문구 기준) | `holdReason` |

## 4. 목록 필터 · 정렬 · 표 컬럼

### 탭1 금고 표 (`vaultTbody`, 프로토 L352-363)
| 프로토타입 컬럼 | 개발 값 · 표시 |
|---|---|
| 식별자 / 성명(상호) | `rights_holders.id` · `name` (프로토 `RH-0019`는 표시 코드, 개발에 별도 권리자번호 없음) |
| 주체 유형 및 수집 근거 | `holder_type_label`(개인 · 사업자 · 위탁자 · 자사 권리자) + `tax_type_label`(TX-01~13) |
| 주민등록번호(AES-256) | `<x-masked type="resident_no" placeholder="******-*******" target-type="rights_holder" field="resident_no_enc">` — 마스킹 형식 `960101-1******`(MaskingService.php:327-338). 사업자는 미수집 |
| 지급/환급 은행 및 계좌번호 | `bank_name` + `<x-masked type="account_no" …field="account_no_enc">` — 형식 `****3369`(뒤 4자리, 별 4개 고정 :348-357). 프로토 `110-421-******`와 다름 |
| 프라이빗 S3 증빙 사본 | `attachments`(attachable `rights_holder`, `disk=secure`) → `admin.attachments.download` |
| 보존 계층 상태 | (규칙) 파생: `destruction_hold` · 파기 여부 · 계약 상태 |
| 복호화 실패 | 개발에만 — `decryptFailed()` 시 "복호화 불가" 안내(rights-holders/form.blade.php:212-214) |

### 탭2 보존 표 (`retentionTbody`, L381-393)
| 프로토타입 컬럼 | 개발 값(규칙) |
|---|---|
| 레코드 식별자 / 대상자 · 계약 | `rights_holders.id` · `name` · `rights_holder_contracts.id` |
| 계약 종료일 / 국세 법정신고기한 | `rights_holder_contracts.ended_at` · `terminated_at` / (규칙) 산출값 |
| 계층 1 파기 예정일(신고기한 + 5년) | (규칙) `pii_destroy_due_on` 산출 |
| 계층 2 원장 보존 만료일(장부 폐쇄 + 10년) | (규칙) 산출 |
| 계층 3 보류 사유 | `destruction_hold`(권리자 · 선급금 원장 · 지원금 약정 · 반환 채권) + (규칙) `hold_reason` |
| 파기 배치 상태 | (규칙) `candidate` 승인 대기 · `hold` 보류 · `destroyed` 계층 1 파기 완료 |
| 승인 액션 | `destruction.store` 버튼(등록 권한) |

### 탭3 열람 이력 (`accessLogTbody`, L456-467) ↔ `admin_logs`
| 프로토타입 컬럼 | 개발 컬럼 |
|---|---|
| 기록 시각 | `created_at` |
| 대상 식별자 / 성명 | `target_type` · `target_id` (+ `after_value.target_user_id`, MaskingController.php:110) |
| 수행 액션 구분 | `action=view` + `sub_action=unmask`(해제) · `download`(증빙 사본, AttachmentController.php:114-127) |
| 입력된 사유 | `reason`(라벨 원문 · 기타는 "기타 — 입력문", ReasonRequest.php:108-115) · `reason_ref` |
| 작업자(RBAC 그룹) | `admin_login_id` · `admin_role_code` 스냅샷 |
| 재마스킹 / 후속 상태 | 개발 없음(재마스킹은 세션 · 화면 타이머라 기록되지 않음) |

## 5. DB 테이블 · 컬럼

| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `rights_holders.resident_no_enc` | text | 주민번호 13자리 암호문(Laravel Crypt, `config/app.php:100` AES-256-CBC · APP_KEY). 접근자가 복호화, 실패 시 null + 경고 로그(RightsHolder.php:295-364) | 탭1 주민번호 |
| `rights_holders.account_no_enc` · `bank_name` · `account_holder` | text · string | 정산 계좌 암호문 · 은행 · 예금주. `$hidden`으로 응답 직렬화 제외(:264-267), `SECRET_FIELDS`(:231) | 탭1 계좌 |
| `rights_holders.birth_date` | date | 주민번호 앞 7자리에서 계산(2026_10_22_000246) | 파기 매핑 대상(규칙) |
| `rights_holders.destruction_hold` | boolean | 세무조사 · 소송 · 이의신청 진행 중이면 true(000151:27). 4개 테이블 모두 `_index/schema.md`에 있음(2026_09_21_000151) | 탭2 보류 |
| `prepayment_ledgers.destruction_hold` · `support_fund_agreements.destruction_hold` · `exclusive_contract_clawbacks.destruction_hold` | boolean | 미상계 선급금 · 대손 채권 / 미소진 지원금 한도 / 미회수 반환 채권(000151:23-28) | 탭2 보류 사유 |
| `rights_holder_account_histories` (`bank_name`, `account_no_enc`, `account_holder`, `changed_by`, `changed_at`) | | 변경 전 계좌. "평문 열람 경로 없음 · 개인정보 파기 대상", FK cascadeOnDelete(2026_10_21_000230:35-50) — 권리자는 SoftDeletes라 연쇄 삭제가 일어나지 않음 | 파기 매핑 대상(규칙) |
| `refund_claims.account_no_enc` · `bank_name` · `account_holder` | text | 합격 환급 입금 계좌 암호문(RefundClaim.php:179-207) | 탭1 REFUND 행 |
| `refunds.refund_bank_code` · `refund_account_no` · `refund_account_holder` | string · text | 현금 환불 수취 계좌 암호문. "보관: 환불 완료 후 5년 뒤 파기 — 파기 배치는 따로", 보관 기간 **미확정**(2026_10_19_000219:12-14) | 탭1(규칙) — 해제 대상 목록에 없음 |
| `suppliers.account_no_enc` | text | 매입처 계좌 암호문(Supplier.php:65-70) | 탭1(규칙, 거래처) |
| `attachments` (`attachable_type`, `attachable_id`, `disk`=secure, `file_path`, `original_name`) | `disk` varchar(20) NOT NULL(media 공개 · editor · secure 비공개) · `original_name` string(255) NOT NULL · `file_path` string(500) | 신분증 · 통장 · 사업자등록증 사본(RightsHolder 관계 `attachments()`) | 탭1 증빙 사본 |
| `admin_logs` (`action`, `sub_action`, `target_type`, `target_id`, `after_value`, `reason`, `reason_ref`, `admin_login_id`, `admin_role_code`, `ip`, `user_agent`) | | 열람 · 다운로드 감사 로그. 원문 미기록(MaskingController.php:104-111) | 탭3 열람 이력 |
| `pii_destruction_field_maps` (규칙) (`table_name`, `column_name`, `label`, `tier` 1 · 2, `action` `nullify` · `anonymize` · `delete_file` · `keep`, `ledger_impact`) | | 프로토 `pii_destruction_field_map`(L403) | 탭3 매핑 표 |
| `pii_destruction_batches` (규칙) (`batch_no`, `approved_by`, `executed_at`, `target_count`, `held_count`, `reason`) | | 프로토 `BATCH-PII-202610-001` | 007-P2 요약 |
| `pii_destruction_items` (규칙) (`pii_destruction_batch_id`, `target_type`, `target_id`, `column_name`, `action`, `destroyed_at`) | | | 007-P2 대조표 |
| `rights_holders.pii_destroyed_at` · `anonymized_name` (규칙) | timestamp · string | 계층 1 파기 시각 · 비식별 표시명(프로토 `이*기_CT-2020-0011`) | 탭1 · 탭2 |

## 6. 개발 JS · 마크업 이름

| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `<x-masked type= target-type= target-id= field= level= placeholder=>` → `span.masked#masked-{type}-{id}-{field}` | 마스킹 칸(Masked.php:77) | `.pii-chip` |
| `.masked__unmask` + `data-target="layerReason"` · `data-reason-mode="ajax"` · `data-reason-action` · `data-reason-params` | high 등급 해제 버튼(masked.blade.php:26-43) | `requestUnmask(id,'UNMASK')` 버튼 "마스킹 해제(사유입력)" |
| `window.maskedScheduleRemask(cellId, masked, ttl)` | TTL 뒤 화면 재마스킹(masked.blade.php:56-71) | 1초 `setInterval` 카운트다운 L1061 · `.ttl-timer` |
| `layerReason` · `reasonForm` · `reasonModalTitle` · `reasonLead` · `reasonSelect`(name `reason`) · `reasonEtcRow` · `reasonEtc` · `reasonEtcCount` · `reasonRef` · `reasonSubmit` | 공용 사유 모달(reason-modal.blade.php:28-102) | `unmaskReasonModal` · `#modalTargetSummary` · `.reason-chip` · `#unmaskReasonInput` · `#reasonCharCount` · `#btnConfirmUnmask` |
| `piiRecordSearchForm` · `piiHolderType` (규칙) | 탭1 필터 | `#holderTypeFilter` |
| `remaskAllButton` · `remaskButton` (규칙) | 전체 · 단건 즉시 재마스킹 | `maskAllNow()` 버튼(L290) · "즉시 재마스킹" |
| `piiUnmaskedCount` · `piiDestructCandidateCount` (규칙) | KPI | `#kpiUnmaskedCount` · `#kpiDestructCandidate` |
| `layerDocViewer` (규칙) — 개발은 다운로드 링크가 바로 임시 URL로 리다이렉트 | 증빙 뷰어 | `docViewerModal` · `#docViewerBody` |
| `layerPiiDestruction` · `piiDestructionForm` · `piiDestructionSubmit` (규칙) | 파기 승인 확인 | `approveTier1Destruction(idx)` L1119(확인 모달 없음) |
| `layerPiiDestructionResult` · `piiDestructionDownload` (규칙) | 007-P2 | `modal-pii-destruction-result` · "국세청 감사 증빙 다운로드(PDF)" L647 |
| `piiFieldMapTable` · `piiAccessLogTable` (규칙) | 탭3 표 | 매핑 표(L404-450) · `#accessLogTbody` |
| `[data-unmask-by-admin]` | 관리자별 해제 건수 표(관리자 로그 화면, 1일 임계 50 — config/admin.php:85) | (없음) |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 해제 허용 목록(target_type × field) — 목록 밖 요청은 422(MaskingService.php:43-63, MaskingController.php:72-76). 매입처 계좌(`supplier`)도 해제 대상
- 등급 2단(high 사유 필수 / basic 사유 없음)과 서버 측 등급 확정 — 권리자 · 환급 필드는 항상 high
- 로그 적재 실패 시 원문 미반환(500), 복호화 실패 시 로그 전 차단(422)(MaskingController.php:87-127) — 정본(화면설계서 03 "실패 시 해제 안 함")과 일치
- TTL 만료 후 재조회 차단 410(:57-65), 해제 기록은 서버 저장 없이 세션 단위(MaskingService.php:124-138)
- 복호화 불가 표시(값 없음과 구분) · 관리자별 일일 해제 건수 집계(`dailyUnmaskCount`, 관리자 로그 화면 임계 50)
- 사유 참조번호 `reason_ref`, 해제 화면 기록 `screen`
- 비공개 첨부 다운로드 기록(`sub_action=download`, 파일명 미기록 — AttachmentController.php:108-127)

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- USER-007 화면 자체(메뉴 · 탭 3개 · KPI 4개) — 종합 3절 007, E-10
- 주민번호 + 계좌를 **한 번의 사유로 동시 해제** — 개발은 필드마다 해제 · 로그 1건씩(prototype_dev는 개발 방식으로 버튼을 필드별로 둔다)
- 증빙 사본 열람 전 10자 사유 · 워터마크 뷰어 · "창 닫으면 URL 폐기" — 개발은 사유 없이 기록만, 임시 URL 300초는 같음(config/filesystems.php:190 `SECURE_URL_TTL`)
- 즉시 재마스킹(단건 · 전체) · '현재 해제 중' 건수 KPI · 남은 초 표시 — 개발은 자동 타이머만(E 부록)
- 재마스킹 시간 운영 설정(`remaskHolderSec`, CONF-003) — 개발 30초 상수(E-02, 종합 4절 #1 결정 반영 대상)
- 보존기한 3계층 계산 · 파기 후보 · 재무 승인 파기 · 비식별 표시명 전환 · 파기 결과 보고서 · 파기 확인서 PDF
- 파기 필드 매핑 테이블과 그 관리 화면
- 화면 안 열람 이력 표(개발은 관리자 로그 화면에서 `type=unmask`로 조회)
- 환불 수취 계좌(`refunds.refund_account_no`) 열람 통제 — 정본 03권 USER-007 정의(`docs/[산준모 정산시스템]_03_…데이터사전.md:358`)는 포함, 개발은 해제 목록에 없고 "화면은 뒤 4자리만"
- 파기 매핑에 넣어야 할 개발 테이블: `rights_holder_account_histories`(변경 전 계좌), `rights_holders.birth_date` · `address` · `phone`, `refunds.refund_account_*`, `refund_claims.account_*`, `suppliers.account_no_enc`(프로토 매핑 표는 5행뿐)
- 참고(프로토 내부 불일치): 탭2는 계층 3 = 파기 보류 예외(L378)인데 P2 보고서는 계층 3 = 세무증빙 · 감사로그 5년 보존(L623-634). 프로토 수정 대상으로 남긴다

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `rights_holders.rrn_encrypted` | `rights_holders.resident_no_enc` |
| `rights_holders.bank_account_enc` | `rights_holders.account_no_enc` |
| `rights_holders.holder_name` | `rights_holders.name` |
| `s3://private-bucket/id_cards/*` | `attachments`(disk `secure`) — 저장소는 `filesystems` 설정 |
| 암호화 "AES-256 (AWS KMS)" · SSE-KMS | 앱 암호화 Laravel Crypt AES-256-CBC(APP_KEY) — KMS 미사용 |
| `ADMN_AUDIT_LOG` | `admin_logs` |
| 수취 주체 INDIVIDUAL · BIZ · REFUND | `target_type` rights_holder · refund_claim (+ `holder_type` personal · business · consignor · internal) |
| 행위 "마스킹 해제" · "Presigned URL 발급" | `action=view` + `sub_action` `unmask` · `download` |
| 계좌 마스킹 `110-421-******` | `****8920`(뒤 4자리, 별 4개 고정) |
| 열람 유지시간 `remaskHolderSec`(설정값, 기본 30) | `MaskingService::UNMASK_TTL_SECONDS = 30`(상수) — 정본 결정(4절 #1)대로 설정값으로 바뀌어야 함 |
| 역할 `ROLE_FINANCE_ADMIN` | `admin_roles.code = finance`(로그에는 `admin_role_code`) |
| `destruction_hold`(권리자 1곳) | 4개 테이블 각각의 `destruction_hold` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)

회원관리 검토 4절에 이미 있는 것: **#1**(재마스킹 시간 — 결정됨, 개발 30초 상수는 전달 대상) · **#3**(마스킹 해제 권한 — 재무 담당자가 권리자 · 환급 계좌를 열 수 있게 할지. USER-007 실무가 여기에 달려 있다). 아래는 이 화면에서 새로 나온 것이다.

1. **증빙 사본(신분증 · 통장) 열람 사유** — 정본: 증빙 사본 다운로드도 10자 사유 팝업 강제(03권 데이터사전:358, 프로토 `requestUnmask(id,'DOC')` L925 → `confirmUnmaskAction` L987). 개발: "사유 입력까지 요구할지는 정하지 않았다. 이번 차수는 기록만 남긴다"(AttachmentController.php:106). 비공개 구획에는 문의 · 후기 · 진도 보정 첨부와 유료 자료도 함께 있어(:32-49), 사유를 권리자 · 환급 증빙에만 받을지 비공개 첨부 전체에 받을지 정해야 한다.
2. **합격환급 수취인 주민번호 수집 · 22% 원천징수** — 정본: 설계서 407행 "기타소득세 22% 원천징수 후 지급", 프로토 REFUND 행 "제세공과금 22% 신고용 주민번호 수집"(L344 · L719-735). 개발: `refund_claims`에 주민번호 컬럼 없음(계좌만, `_index/schema.md` refund_claims), 화면설계서 07:1448 "제세공과금(기타소득) 처리는 1차 범위에 넣지 않는다". 1차에 주민번호를 받고 원천징수하는지. **→ 결정(v6.92 white, S-02)**: 합격환급 신청 때 주민번호를 항상 받음(신분증 이미지 없이 번호만 입력 · USER-007 암호화 보관), 원천징수 대상 맞음 — 개발 `refund_claims`에 주민번호 암호문 칸 추가 필요.
3. **계층 3 파기 보류 판정 방식** — 프로토: 미상계 선급금 · 미소진 지원금 · 대손 · 소송이 있으면 "파기 대상에서 자동 격리"(L378). 개발: 4개 테이블에 저장형 boolean 플래그만 두고 값을 세팅하는 코드가 없다(000151:17, 저장소 전체 검색 결과 마이그레이션 · 테스트 외 사용처 0). 잔액 · 상태로 파기 시점에 자동 산출할지, 운영자가 플래그를 거는지(세무조사 · 소송은 수동일 수밖에 없음).
4. **환불 수취 계좌 보관 기간 기산점** — 프로토 · 정본 계층 1은 "국세 법정신고기한 + 5년"(L377 · L386, L1130). 개발 `refunds.refund_account_*`는 "환불 완료 후 5년(전자상거래법 대금결제 기록)"을 파트장 안으로 적고 미확정 표시(2026_10_19_000219:12-14). 환불 수취 계좌 · 환급 계좌는 어느 기준으로 파기하는지. **→ 결정(v6.87 white, D-USER7-01): 환불 수취 계좌 원번호는 환불 완료일 + 5년 후 파기(정산 03권 v4.0.13).**

## 출처
- routes/admin.php:174-184
- app/Services/MaskingService.php:43-138, 327-382
- app/Http/Controllers/Admin/MaskingController.php:34-137
- app/Http/Requests/Admin/MaskingUnmaskRequest.php:27-90 · ReasonRequest.php:48-124
- app/View/Components/Masked.php:35-78 · resources/views/components/masked.blade.php:8-71 · resources/views/admin/inc/reason-modal.blade.php:28-102
- app/Repositories/MaskingRepository.php:14-20 · app/Services/Admin/AdminLogService.php:122-124, 265-318 · app/Http/Requests/Admin/LogSearchRequest.php:59-66 · config/admin.php:85
- app/Http/Controllers/Admin/AttachmentController.php:32-49, 60-148 · config/filesystems.php:190
- app/Models/RightsHolder.php:55-65, 231-364 · RefundClaim.php:104, 179-207 · Supplier.php:46, 65-94 · config/app.php:100
- database/migrations/2026_09_21_000151_add_destruction_hold_columns.php · 2026_10_19_000219_add_refund_account_columns_to_refunds_table.php:12-23 · 2026_10_21_000230_create_rights_holder_account_histories_table.php:32-51
- resources/views/admin/rights-holders/form.blade.php:212-217, 585-589 · settlement/statements/index.blade.php:126-133 · pass-refunds/show.blade.php:225-228 · book-supply/_suppliers.blade.php:22, 32
- 프로토타입: prototype_clean/ADMN-USER-007_baseline.html L290 · 309-322 · 331-467 · 492-648 · 659-1179, prototype_clean/common-master.js:63 · 88 · 415-421
