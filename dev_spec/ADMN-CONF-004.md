# ADMN-CONF-004 메시지 템플릿 · 타겟 발송 · 발송 이력 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-004_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-004 메시지 템플릿 관리 · ADMN-CONF-004-S1 타겟 단체 알림톡/LMS 예약 발송 · 프로토타입 3번째 탭 "통합 발송 이력 및 실패 재발송 (ADMN-CONF-007)" · 개발 ADMN-CONF-007 알림톡 SENS 템플릿 관리
- 개발 진행: 구현(담당 이응민, `_index/progress.md` 109 · 110 · 113행). 통합 발송 이력 · 실패 재발송 화면은 개발 미구현(7절)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.message-templates.index` | 메시지 템플릿 관리 | routes/admin.php:1105. S1 `admin.message-templates.campaigns.*` 는 하위 자원이라 이 메뉴 권한으로 판정(주석 routes/admin.php:1108-1109, DECISIONS 163 ③) |
| `admin.sens-templates.index` | 알림톡 SENS 템플릿 관리 | routes/admin.php:1133. [SENS 동기화]는 서비스가 최고 관리자만 다시 허용 — routes/admin.php:1134 주석 |

- 상세 = 수정 화면: `show` 를 조회 권한으로 열고 저장(PUT)만 수정 권한 — CS 는 문구만 본다(routes/admin.php:1123 주석).
- 템플릿 코드는 시스템 상수라 삭제 · 코드 변경 경로 없음(routes/admin.php:1101 주석).

## 2. 화면별 라우트

### ADMN-CONF-004 메시지 템플릿
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/message-templates` | `admin.message-templates.index` | can_view | MessageTemplateController@index |
| 등록 폼(`?code=`) | GET | `/{admin}/message-templates/create` | `admin.message-templates.create` | can_create | MessageTemplateController@create |
| 등록 | POST | `/{admin}/message-templates` | `admin.message-templates.store` | can_create | MessageTemplateController@store |
| 상세 = 수정 화면 | GET | `/{admin}/message-templates/{messageTemplate}` | `admin.message-templates.show` | can_view | MessageTemplateController@show |
| 수정 | PUT | `/{admin}/message-templates/{messageTemplate}` | `admin.message-templates.update` | can_update | MessageTemplateController@update |
| 테스트 발송(횟수 제한) | POST | `/{admin}/message-templates/{messageTemplate}/test-sends` | `admin.message-templates.test-sends.store` | can_create | MessageTemplateController@testSend |

### ADMN-CONF-004-S1 타겟 단체 예약 발송
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 예약 화면 + 예약 이력 | GET | `/{admin}/message-templates/campaigns` | `admin.message-templates.campaigns.index` | can_view | MessageCampaignController@index |
| 예약 등록 | POST | `/{admin}/message-templates/campaigns` | `admin.message-templates.campaigns.store` | can_create | MessageCampaignController@store |
| 대상 명단 엑셀(사유 입력) | GET | `/{admin}/message-templates/campaigns/download` | `admin.message-templates.campaigns.download` | can_download | MessageCampaignController@download |
| 나에게 테스트 발송 | POST | `/{admin}/message-templates/campaigns/test-sends` | `admin.message-templates.campaigns.test-sends.store` | can_create | MessageCampaignController@testSend |
| 예약 상세 | GET | `/{admin}/message-templates/campaigns/{campaign}` | `admin.message-templates.campaigns.show` | can_view | MessageCampaignController@show |
| 예약 취소 | PUT | `/{admin}/message-templates/campaigns/{campaign}/status` | `admin.message-templates.campaigns.status.update` | can_update | MessageCampaignController@cancel |

- 예약 취소는 발송 30분 전까지(`MessageCampaignService::CANCEL_LEAD_MINUTES`, "미확정" 주석) — MessageCampaignService.php:48-49
- 실제 발송은 스케줄 명령 `SendScheduledCampaigns`(routes/console.php)

### 개발 ADMN-CONF-007 알림톡 SENS 템플릿
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(`?status=&keyword=&code=`) | GET | `/{admin}/sens-templates` | `admin.sens-templates.index` | can_view | SensTemplateController@index |
| SENS 동기화 | POST | `/{admin}/sens-templates/sync` | `admin.sens-templates.sync.store` | can_create(+최고 관리자) | SensTemplateController@sync |

## 3. 폼 필드 · 검증

### 템플릿 `#templateForm` (MessageTemplateRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `code` | POST 일 때만 required · in TemplateCatalog 코드 (수정 시 무시) | 발송 조건(시스템 이벤트 코드) | `#tpl-form-code` · `#tpl-form-domain` |
| `channel` | required · in | `alimtalk` 알림톡 · `sms` LMS(문자) · `email` 메일 | `#tpl-form-channel` |
| `use_fallback` | nullable · boolean | 알림톡 실패 시 LMS 대체 | `#tpl-form-fallback` |
| `subject` | email 이면 required · max:255 · 바이트 규칙(LMS 제목 40바이트) | — | `#tpl-form-title` |
| `content` | required · 채널별 길이(알림톡 1000자 · LMS 2000바이트 · 메일 10000자) | 치환 변수 포함 | `#tpl-form-body` |
| `fallback_content` | nullable · LMS 바이트 규칙 | LMS 대체 본문(버튼 링크를 URL 로 풀어 씀) | (없음) |
| `is_active` | required · boolean | 사용 여부 | (없음) |

### 예약 발송 `#campaignStoreForm` (MessageCampaignRequest — store 라우트에서만 rules 적용)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `template_id` | required · integer | notification_templates.id | `#send-tpl-select` |
| `target_type` | required · string | `group` 저장 그룹 · `tags` 태그 조합 · `members` 회원 목록 검색 조건 | `#send-target-seg` |
| `saved_group_id` | (target_type=group) | user_groups.id | 세그먼트 항목 |
| `tags[]` · `exclude_tags[]` · `tag_join` | (target_type=tags) | 태그 포함/제외 · 결합 방식 | — |
| `member_ids` + 회원 목록 필터 키(`date_from` · `date_to` · `status` · `search_type` · `keyword` · `join_method` · `inactive_days` · `address` · `point_min` · `point_max` · `minus_only` · `group_id` · `sort` · `direction`) | (target_type=members) | ADMN-USER-001 검색 조건 그대로 | — |
| `expected_target` | required · integer ≥1 | 화면에 보인 최종 대상 수(서버 재계산과 대조) | — |
| `scheduled_at` | required · `Y-m-d\TH:i` · 지금 이후 | 예약 일시(광고성 21:00~08:00 불가 — 컬럼 주석) | `#send-schedule-dt` |
| `send_reason` | required · max:200 | 발송 사유(내부) | (없음) |
| `return` (테스트 발송) | 내부 경로만 | 돌아갈 주소 | — |

- 대상 명단 엑셀은 사유 입력(ReasonRequest — `reason` 등, 공통 사유 모달 `admin.inc.reason-modal`).

### SENS 템플릿 목록 필터
| 쿼리 name | 값 |
|---|---|
| `status` | `approved` 승인 · `pending` 심사중 · `rejected` 반려 · `none` 동기화 전 |
| `keyword` · `code` | 문자열 · 선택 템플릿 코드(치환 변수 대조 표 열기) |

## 4. 목록 필터 · 정렬 · 표 컬럼

### 템플릿 목록 (MessageTemplateController.php:27)
| 쿼리 name | 값 | 프로토타입 대응 |
|---|---|---|
| `group` | `join` 회원가입 · `member` 회원 · `payment` 결제 · `delivery` 배송 · `point` 포인트 · `inquiry` 문의 · `refund` 환불 · `notice` 단체 공지 | (없음) |
| `channel` | `alimtalk` · `sms` · `email` | `#tpl-channel-filter` |
| `active` | 사용 여부 | (없음) |
| `keyword` | 문자열 | `#tpl-keyword` |

- 표 컬럼: 템플릿 코드 · 템플릿명 · 발송 시점 · 채널 · 수신 동의 · 심사 · 상태 · 관리 — message-templates/index.blade.php:129
- 예약 이력 표: 예약 일시 · 템플릿 · 발송 사유 · 대상 · 성공 · 실패 · 상태 · 관리 — campaigns/index.blade.php:257
- SENS 목록: 템플릿 코드 · 템플릿 이름 · 발송 조건 · 승인 상태 · 최종 동기화, 상세 표 치환 변수 · 넘기는 값 · 검증 · 비고 — sens-templates/index.blade.php:99, :153

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| notification_templates.code · name · channel | string | 이벤트 코드 · 템플릿명 · `alimtalk`/`sms`/`email` | 코드 · 명 · 채널 |
| notification_templates.trigger_group · send_timing | string | 발송 조건 분류(위 group 값) · 발송 시점 설명 | 발송 조건 |
| notification_templates.is_advertising | tinyint | 1 광고성(마케팅 동의자만) / 0 거래성 | 수신 동의 |
| notification_templates.subject · content · variables · buttons | — | 제목 · 본문 · 치환 변수 · 카카오 버튼(SENS 동기화본) | 편집 |
| notification_templates.use_fallback · fallback_channel(`lms`/`sms`) · fallback_content | — | 대체 발송 | 대체문자 |
| notification_templates.provider_template_code | string(100) | 카카오 승인 템플릿 코드 | SENS 코드 |
| notification_templates.approval_status | string(20) | `none` 심사 불필요 · `pending` 심사중 · `approved` 승인 · `rejected` 반려 | 심사 |
| notification_templates.approval_reason · approval_requested_at · approval_checked_at · approved_content | — | 반려 사유 · 요청 · 조회 시각 · 직전 승인 본문 | 심사 |
| notification_templates.is_required · is_active | boolean | 필수(삭제 불가) · 사용 | 상태 |
| notification_templates.is_send_blocked · block_reason · sens_synced_at | — | 치환 변수 불일치 차단 · 사유 · 최종 동기화 | 경고 · 동기화 |
| notification_campaigns.template_id · admin_id · send_reason · filter_params | — | 템플릿 · 등록자 · 사유 · 대상 조건 스냅샷 | 예약 |
| notification_campaigns.total_count · excluded_agree_count · excluded_unsub_count · target_count · estimated_count | int | 조회 · 미동의 제외 · 수신거부 제외 · 최종 · 예상 건수 | 대상 계산 |
| notification_campaigns.scheduled_at · status | — | 예약 일시 · `scheduled` 예약 · `processing` 발송중 · `completed` 완료 · `canceled` 취소 · `failed` 실패 | 상태 |
| notification_campaigns.success_count · fail_count · fallback_count · started_at · finished_at · canceled_at | — | 결과 | 이력 |
| notification_logs.channel · receiver · status(`pending`/`sent`/`failed`) · fail_reason_code(`unsubscribed` · `invalid_number` · `not_kakao_user` · `timeout` · `provider_error`) · is_fallback · is_test · retry_count · last_retry_at · campaign_id | — | 건별 발송 이력 | (이력 화면 미구현) |
| batch_job_logs (`sens_template_sync`) | — | SENS 동기화 실행 기록 | 동기화 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#templateForm` | 템플릿 등록 · 수정 폼(별도 페이지) | `modal-template` |
| `#mtContent` · `#mtContentCount` · `#mtPreview` · `[data-mt-chip]` | 본문 · 글자 수 · 미리보기 · 치환 변수 칩 | `#tpl-form-body` · `insertTplVar()` |
| `#mtUseFallback` · `#mtFallback` · `#mtFallbackCount` · `#mtFallbackRow` · `#mtFallbackWrap` | 대체 발송 | `#tpl-form-fallback` |
| `#testSendForm` · `#testSendButton` | 테스트 발송 | (없음) |
| `#campaignStoreForm` · `[data-campaign-block]` · `[data-campaign-target]` · `[data-target-count]` · `[data-estimate]` · `[data-scheduled-at]` | 예약 발송 폼 · 대상 수 · 비용 추정 | `executeTargetSend()` · `updateSendTargetCount()` |
| `#campaignTestForm` | 나에게 테스트 발송 | (없음) |
| `[data-reason-action]` · `[data-reason-params]` · `[data-reason-count]` · `[data-reason-lead]` · `[data-reason-submit]` | 명단 엑셀 사유 모달 연결 | (없음) |

- 하위 화면 표현: 템플릿 목록 · 상세(수정) · 예약 발송(campaigns) · 예약 상세 · SENS 템플릿 모두 별도 페이지. 프로토타입은 한 페이지 3탭 + 템플릿 모달.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 템플릿 · 예약 발송의 테스트 발송, 예약 취소(30분 전), 예약 상세 페이지, 대상 명단 엑셀(사유).
- 예약 대상 3방식(`group` · `tags` · `members`)과 미동의 · 수신거부 제외 계산, 비용 추정 표(구분 · 건수 · 단가 · 예상 소진).
- 발송 사유 `send_reason`(필수).
- SENS 템플릿 관리 화면(치환 변수 대조), 치환 변수 불일치 발송 차단 표시.
- 발송 조건 분류 `group` 필터(8종).

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- "통합 발송 이력 및 실패 재발송" 탭(발송배치 ID · 성공/실패 · 재발송) — 개발에 건별 이력 · 재발송 화면 없음(notification_logs 테이블만). 규칙 기반 명명: `admin.message-logs.index`(규칙) · 재발송 `admin.message-logs.resends.store`(규칙)
- 즉시 발송(`send-schedule-mode` = 즉시) — 개발은 예약만(`scheduled_at` required · after:now).
- 템플릿 모달의 SENS 상태 직접 선택(`#tpl-form-status`) · 반려 사유 입력 — 개발은 SENS 동기화 결과로만 바뀜.
- 메시지 성격 필터(`#tpl-type-filter` 정보성/광고성), 알림톡 버튼명 입력(`#tpl-form-btn-name`) — 개발은 SENS 동기화본 `buttons`.
- 저장 후 SENS 상태 동기화 버튼.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 화면 코드: 프로토타입 탭 3 "ADMN-CONF-007 = 통합 발송 이력", 개발 ADMN-CONF-007 = 알림톡 SENS 템플릿 관리 — 코드 의미가 다름.
- 채널 값: 프로토타입 `ALIMTALK` · `SMS/LMS` · `EMAIL` → `alimtalk` · `sms` · `email`.
- SENS 상태: 프로토타입 APPROVED · INSPECTING · REJECTED · 초안 → `approved` · `pending` · `rejected` · `none`.
- 세그먼트 select(`#send-target-seg` 고정 목록) → `target_type` + `saved_group_id` / `tags[]` / 회원 검색 조건.
- 템플릿 등록 모달 → 별도 페이지 `create` · `show`.

## 8. 정책 질문 (white 확인 필요)
- 즉시 발송 허용 여부(개발은 예약만) — 확인 필요.
- ADMN-CONF-007 화면 코드: 정본은 "발송 이력 · 실패 재발송" 인지 "SENS 템플릿 관리" 인지 — 확인 필요.
- 예약 취소 마감 30분(개발 "미확정") — 확인 필요.

## 출처
- routes/admin.php:1101-1135
- app/Http/Controllers/Admin/MessageTemplateController.php:22-79 · MessageCampaignController.php:27-148 · SensTemplateController.php:16-29
- `_index/requests.md` MessageTemplateRequest · MessageCampaignRequest
- app/Http/Requests/Admin/MessageCampaignRequest.php:72-102
- app/Services/Admin/MessageCampaignService.php:36-49 · MemberService.php:24-28 · SensTemplateService.php:26-31
- app/Services/Notification/TemplateCatalog.php:29-54
- app/Models/NotificationCampaign.php:27-33
- resources/views/admin/message-templates/index.blade.php:70-129 · form.blade.php · edit.blade.php · campaigns/index.blade.php:28-257 · sens-templates/index.blade.php:56-153
- `_index/schema.md` notification_templates · notification_campaigns · notification_logs
- 프로토타입: prototype_clean/ADMN-CONF-004_baseline.html:389-1154 (digest 기준)
