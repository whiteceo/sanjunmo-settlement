# ADMN-BRD-002 1:1 문의 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-BRD-002_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-BRD-002(목록), ADMN-BRD-002-S1(1:1 답변 등록 · 알림톡), ADMN-BRD-002-P1(회원 컨텍스트 모달)
- 개발 진행: 구현. 담당 이응민(`config/dev-progress.php`), 커밋 언급 BRD-002 10 · S1 10 · P1 2(dev_spec/_index/progress.md)
- 관련: 답변 영역 조각 `inquiries/partials/inquiry-panel.blade.php` 를 환불 관리 상세(ADMN-RFD-002-S1)가 그대로 쓴다. 결제 · 환불 분류로 바꾸면 RFD-002-S1 로 이관돼 이 목록에서 빠진다(Inquiry::ROUTED_BOARDS).

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.inquiries.index` | 1:1 문의 관리 | InquiryController 의 `menuKey: 'admin.inquiries.index'`(:78, :99) · `permissions->can(…, 'admin.inquiries.index', 'can_update')`(:178). 메뉴 행 데이터는 DB(저장소에 없음) |

- 권한은 라우트 이름 접미사로 판정. ROUTE_PERMISSIONS 예외 없음.
- 별도 조건(컨트롤러 판정)
  - 담당자 일괄 지정 · 잠금 해제: 최고 관리자만(`isSuperAdmin`, abort 403) — InquiryController.php:63, :235.
  - 상세 진입 시 답변 권한(수정)이 있으면 미지정 건을 본인에게 배정하고 접수 → 처리중으로 바꾼다(선점). 다른 관리자가 담당이면 읽기 전용 + 잠금 배너.
  - 답변 알림 재발송은 수정 권한.
  - 엑셀은 다운로드 권한 + 반출 사유(ReasonRequest).

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`).

### ADMN-BRD-002 1:1 문의 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 스코어카드 | GET | `/{admin}/inquiries` | `admin.inquiries.index` | 조회 | InquiryController@index |
| 엑셀(현재 조건) | GET | `/{admin}/inquiries/download` | `admin.inquiries.download` | 다운로드 | InquiryController@download |
| 엑셀(선택) | POST | `/{admin}/inquiries/download-selected` | `admin.inquiries.selected.download` | 다운로드 | InquiryController@downloadSelected |
| 담당자 일괄 지정 | PUT | `/{admin}/inquiries/assignees` | `admin.inquiries.assignees.update` | 수정(+최고 관리자) | InquiryController@bulkAssign |

### ADMN-BRD-002-S1 1:1 답변 등록 · 알림톡 (별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세(선점) | GET | `/{admin}/inquiries/{inquiry}` | `admin.inquiries.show` | 조회 | InquiryController@show |
| 처리(임시저장 · 보류 · 답변) | PUT | `/{admin}/inquiries/{inquiry}` | `admin.inquiries.update` | 수정 | InquiryController@update |
| 분류 변경(이관) | PUT | `/{admin}/inquiries/{inquiry}/category` | `admin.inquiries.category.update` | 수정 | InquiryController@changeCategory |
| 잠금(담당자) 해제 | PUT | `/{admin}/inquiries/{inquiry}/assignee` | `admin.inquiries.assignee.update` | 수정(+최고 관리자) | InquiryController@releaseLock |
| 답변 알림 재발송 | PUT | `/{admin}/inquiries/{inquiry}/notifications/{notificationLog}` | `admin.inquiries.notifications.update` | 수정 | InquiryController@resendNotification |

### ADMN-BRD-002-P1 회원 컨텍스트 모달 (모달, 내용은 열 때 fetch)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 모달 내용(HTML 조각) | GET | `/{admin}/inquiries/{inquiry}/member` | `admin.inquiries.member.show` | 조회 | InquiryController@memberContext |
| [회원 상세로 이동] | PUT → 302 | `admin.inquiries.update` 에 `action=draft` + `go_member=1` | — | 수정 | 임시 저장 후 `admin.members.show` 로 이동 |

## 3. 폼 필드 · 검증
### 답변 처리 `processForm` (InquiryProcessRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `action` | required in:draft,hold,answer (`actionField` 값 교체 후 제출) | draft=임시 저장(상세에 머묾) · hold=보류 처리 · answer=답변 등록(목록으로) | `saveDraftAnswer()` · `holdCase()` · `submitFinalAnswer()` |
| `answer_content` | answer 일 때 required · 공백 제외 10자 이상 | 회원 마이페이지에 그대로 노출 | `dt-answer-input` |
| `internal_memo` | nullable string | 회원 미노출 | 없음(이관 모달 `modal-memo` 가 비슷) |
| `draft_content` | nullable string | 임시 저장 초안 | 없음 |
| `hold_reason` | hold 일 때 required · max:255. 답변완료 건은 보류 불가(서비스) | | `dt-hold-reason` |
| `hold_until` | hold 일 때 required · date · 오늘 이후 | 재개 예정일 | 없음 |
| `edit_reason` | max:255. 답변완료 건을 다시 answer 하면 필수(서비스) | [답변 수정] 펼친 뒤 입력 | 없음 |
| `notify` | nullable boolean, 기본 ON(hidden 0 + checkbox 1) | `notifyAnswer` | 체크박스 "답변 등록 시 카카오 알림톡(SENS) + 이메일 동시 발송"(id 없음) |
| `notify_skip_reason` | max:200. 새 답변에서 notify 끄면 필수(서비스) | `notifySkipRow` | 없음 |
| `go_member` | nullable boolean | P1 [회원 상세로 이동] | 없음 |

### 분류 변경 (컨트롤러 인라인 검증, InquiryController@changeCategory)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `category_id` | required integer · 소분류 존재. 상품 Q&A · 학습 질문 게시판으로는 이관 불가 | inquiry_categories.id(소분류) | 이관 모달 `modal-target-cat` (+ `modal-memo` 내부 이관 메모, `modal-target-depts` 부서 표시) |

### 잠금 해제 (InquiryReleaseRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `release_reason` | required string max:255 | 없음(`dt-reassign` 담당자 재배정이 비슷) |

### 담당자 일괄 지정 `bulkAssignForm` (InquiryBulkAssignRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | required array min:1 · integer | 없음 |
| `assign_user_id` | required integer · 1:1 문의 답변 가능 관리자만(서비스) | `dt-reassign`(상세 단건 재배정) |

### 엑셀 반출 사유 (ReasonRequest — 공용 `layerReason` 모달)
| 필드 name | 규칙 | 코드값(라벨) |
|---|---|---|
| `reason` | required in REASONS | refund_account 환불 계좌 확인 · delivery_error 배송 오류 확인 · identity_check 본인 확인 요청 · payment_inquiry 결제 오류 조사 · legal_request 법적 요청 대응 · settlement_check 정산 · 지급 확인 · etc 기타(직접 입력) |
| `reason_etc` | etc 일 때 필수 10~150자 | |
| `reason_ref` | nullable max:50 영숫자 · `-` | |
| `ids[]` | 선택 다운로드일 때 required(SelectedIdsRequest) | |

## 4. 목록 필터 · 정렬 · 표 컬럼
- 필터(쿼리 파라미터, InquiryController::filters :113-131): `date_from` · `date_to`(문의일) · `status`(received 접수 · processing 처리중 · answered 답변완료 · hold 보류) · `category_id`(소분류) · `mine`(1=내 담당) · `member`(이름 · 이메일 · 비회원 이름, 숫자면 회원번호) · `has_file`(1) · `sla_over`(1) · `unanswered`(1, 대시보드 연결) · `answered_today`(1) · `notify_fail`(1) · `per_page`(20/50/100).
- 스코어카드 5종(누르면 해당 조건): 미답변(접수) `status=received` · 처리중 `status=processing` · SLA 24h 초과 `sla_over=1` · 오늘 답변완료 `answered_today=1` · 알림톡 발송 실패 `notify_fail=1`(0 이 아니면 주황).
- 범위: 결제 · 환불로 이관된 건(assign_board = ADMN-RFD-002-S1)은 제외.
- 정렬: SLA 초과 미처리 건 맨 위 → created_at desc → id desc (InquiryRepository:31-39).
- 표 컬럼(개발): 선택 · 문의일 · 분류 · 제목 · 회원 · 첨부 · 담당자 · 경과 · 상태 · 처리.
- 엑셀 열: 접수번호 · 문의일시 · 분류 · 제목 · 회원번호 · 첨부 · 담당자 · 상태 · 답변일시(이름 · 이메일 제외).
- 프로토타입 표: 문의번호/접수일시 · 문의 유형 · 질문자(카페 ID) · 제목 및 요약 · 연결 주문번호/상품 · 연결 도메인(분기 타겟) · 담당 부서 큐 · 담당자 · 처리 상태 · 액션. 필터 `filter-status` · `filter-assignee` · `filter-order-link` · `filter-keyword` + 유형 칩 5종.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| inquiries.inquiry_no | string(30) unique | QNA-YYYY-{일련} 문의번호 | 엑셀 접수번호 · 상세 |
| inquiries.category_id | bigint | 소분류 inquiry_categories.id | 분류 |
| inquiries.user_id / guest_company · guest_name · guest_phone · guest_email | | 회원 / 비회원(제휴) 접수 | 회원 |
| inquiries.title / content | | 문의 제목 · 본문 | 상세 |
| inquiries.assign_user_id | bigint | 담당자 = 답변 잠금 | 담당자 · 잠금 배너 |
| inquiries.status | string(20) | received 접수 · processing 처리중 · answered 답변완료 · hold 보류 | 상태 |
| inquiries.hold_reason / hold_until | string / date | 보류 사유 · 재개 예정일 | 보류 입력 |
| inquiries.answer_content / draft_content | longText | 답변 · 임시 저장 초안 | 답변 작성 |
| inquiries.answered_by / answered_at | | 답변자 · 답변 시각(SLA 기준) | 목록 · 엑셀 |
| inquiries.internal_memo | text | 내부 메모(회원 · 알림 미노출) | 내부 메모 |
| inquiries.inquiry_type / sub_type / assign_board | string(30) | 라우팅 키 · 하위 분류(consult · partial · full) · 배정 화면코드(ADMN-BRD-002/003/004, ADMN-RFD-002-S1) | 목록 범위 |
| inquiries.order_id / order_item_id / course_id | bigint | 관련 주문 · 라인 · 강좌(회원이 접수 때 선택) | 상세 주문 링크 |
| inquiries.privacy_agreed_at | timestamp | 개인정보 동의 | — |
| inquiries.refund_hold_reason / refund_hold_memo / refund_held_at | | 환불 판정 전 보류(RFD-002-S1 용) | — |
| inquiry_categories.* | | 대분류/소분류(parent_id) · target_screen | 분류 선택 |
| attachments(attachable=inquiry) | | 회원 첨부 — `admin.attachments.download` 로 받음 | 첨부 |
| notification_logs(target_type=inquiry) | | 답변 알림 발송 이력 · 실패 집계(`notify_fail`) | 발송 이력 · 스코어카드 |
| admin_logs | | 선점 · 처리 · 잠금 해제 · 분류 변경 이력(edit_reason · 알림 미발송 사유 포함) | — |

- 상수: Inquiry::SLA_HOURS = 24, 알림 템플릿 `SJM_QNA_ANSWER_01`(알림톡/LMS) · `SJM_QNA_ANSWER_EMAIL_01`(메일), 변수 name · title(20자) · answered_at · answer_url.

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `bulkAssignForm` · `submitBulkAssign()` · `.iq-bulk` | 담당자 일괄 지정(최고 관리자만 보임) | 없음 |
| `.check-item` · `ids[]` | 목록 선택 | 없음 |
| `.layer__open[data-target="layerReason"]` + `data-reason-title/action/method/submit/lead/params` · `reasonModalPrepareSelected()` | 엑셀 반출 사유 공용 모달 | 없음 |
| `processForm` · `actionField` · `submitProcess('draft'/'hold'/'answer')` | 답변 처리 폼 | `dt-answer-input` 영역 |
| `answerEditOpen` · `openAnswerEdit()` | 답변완료 건 [답변 수정] 펼치기 | 없음 |
| `notifyAnswer` · `notifySkipRow` · `.iq-notify` · `answerSubmit` | 답변 알림 on/off · 미발송 사유 | 알림톡 체크박스(id 없음) |
| `.iq-lock` · `.iq-lock__form` · `release_reason` | 동시 답변 잠금 배너 · 해제 | `dt-assign-banner` |
| `memberContextModal`(`.layer-pop__overlay.layer-pop--hidden`) · `memberContextBody` · `loadMemberContext(url)` · `goMemberDetail()` | P1 모달 | 상세 안 카드 "질문자 및 바인딩 주문 컨텍스트"(모달 아님) |
| `admin.inc._notify-history` | 발송 이력 · 재발송 | 없음 |
| `<x-masked type="name/email" :unmaskable="true">` | 마스킹 · 해제 | 없음 |

하위 화면: 개발 S1 = 별도 페이지(`admin.inquiries.show`), P1 = 레이어 모달(fetch). 프로토타입은 한 HTML 안 `view-list` / `view-detail` 섹션 전환(`switchView`) + 이관 모달 `transfer-modal`.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 엑셀 다운로드(현재 조건 · 선택) + 반출 사유.
- 담당자 일괄 지정(최고 관리자), 잠금 해제(사유 필수, 최고 관리자).
- 보류 재개 예정일 `hold_until`, 내부 메모, 답변완료 건 수정 사유 `edit_reason`, 알림 끌 때 사유 `notify_skip_reason`.
- 스코어카드 "알림톡 발송 실패" · 발송 이력 · 재발송.
- 검색 필터: 첨부 있음 · SLA 초과 · 오늘 답변완료 · 회원 검색(이름 · 이메일 · 회원번호).
- P1 회원 컨텍스트 모달(회원 · 최근 주문 · 수강 진도) + 임시 저장 후 회원 상세 이동.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 문의 유형 5대 분기 워크스페이스(결제 · 환불 / 배송 · 3PL Lock / 수강 · 동시접속 세션 초기화 / 합격환급 · 포인트 / 학습질문 오인입)와 유형별 매크로 삽입(`insertMacro`).
- 주문번호 자동 탐지 · 바인딩(`bindDetectedOrder`) — 개발 inquiries.order_id 는 회원 접수 때만 채워지고 관리자 바인딩 라우트 없음.
- 이관 모달의 내부 이관 메모 · 담당 부서 표시, "환불 심사 큐로 즉시 이관" 버튼(개발은 분류 변경 하나로 이관).
- 세션 강제 로그아웃(개발은 회원 수강 · 기기 제어 ADMN-USER-003 쪽 라우트).
- 상태 "타부서 이관중"(TRANSFERRED), 주문연동 필터.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 상태 코드: WAITING → `received`(접수), IN_PROGRESS → `processing`, ANSWERED → `answered`, HOLD → `hold`. TRANSFERRED 는 개발에 없음(이관되면 RFD-002-S1 목록으로 이동).
- 담당자 필터: `filter-assignee` MINE → `mine=1`. NONE(미지정) 필터는 개발에 없음.
- 유형 칩(REFUND · SHIPPING · PLAYER · BENEFIT · STUDY_MISROUTE) → 개발 `category_id`(1:1 문의 분류 관리 소분류).
- 답변 등록 버튼 문구 "CS 답변 등록 및 알림톡 발송" → 개발 "답변 등록" + `notify` 체크.
- 상세 화면 표현: `view-detail` 섹션 → 개발 별도 페이지 `admin.inquiries.show`.

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
- 관리자가 문의에 주문번호를 바인딩하는 기능(프로토타입)이 필요한지 확인 필요 — 개발은 회원 접수 시 선택만.
- "타부서 이관중" 상태를 별도 상태로 둘지 확인 필요 — 개발은 분류 변경 시 assign_board 로 다른 화면 큐로 옮기고 상태는 그대로.
- 미지정 담당자 필터 · 담당 부서 큐 표시가 필요한지 확인 필요.

## 출처
- routes/admin.php:775-788 (dev_spec/_index/routes.md)
- app/Http/Controllers/Admin/InquiryController.php:26, 38-54, 61-66, 73-108, 113-131, 138-148, 170-195, 202-210, 216-228, 233-238, 245-262, 268-290
- app/Http/Requests/Admin/InquiryProcessRequest.php · InquiryReleaseRequest.php · InquiryBulkAssignRequest.php · ReasonRequest.php:21-67 · SelectedIdsRequest.php
- app/Services/Admin/InquiryService.php:24-27, 143-160, 170-190, 193-275, 279-307, 314-334, 347-380
- app/Repositories/Admin/InquiryRepository.php:25, 31-39, 82, 93-105, 186-222
- app/Models/Inquiry.php:16-70
- resources/views/admin/inquiries/index.blade.php:22-35, 95-128, 140-170, 184-190 · show.blade.php:18-93 · partials/inquiry-panel.blade.php:1-12, 20-30, 85-100, 136-240 · partials/member-context.blade.php
- database: dev_spec/_index/schema.md inquiries · inquiry_categories · notification_logs · attachments
- 프로토타입: prototype_clean/ADMN-BRD-002_baseline.html:488-530(카드), 592-680(목록), 810-1030(상세), 1039-1072(transfer-modal), 1240-1275(잠금 · 보류)
