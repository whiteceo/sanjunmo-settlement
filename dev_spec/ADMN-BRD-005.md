# ADMN-BRD-005 수강후기 · 합격수기 관리 및 무료콘텐츠 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-BRD-005_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-BRD-005(수기 / 합격 후기 관리), ADMN-BRD-005-S1(합격 후기 검증), ADMN-BRD-010(무료콘텐츠 관리), ADMN-BRD-010-S1(무료콘텐츠 등록 · 수정)
- 개발 진행: 구현. 담당 이응민(`config/dev-progress.php`). progress 표 BRD-005 커밋 언급 9 · S1 4 · BRD-010 2 · 010-S1 1
- 구조 차이 요지: 프로토타입은 탭 3개(`courseReview` 수강후기 · `passEssay` 합격수기 · `freeLecture` 무료특강/빈출문제) + 서브페이지(`pass-audit` · `free-lecture`). 개발은 후기 하나의 목록(`reviews`, 수기 · 합격 후기를 한 테이블에서 검증)과 무료콘텐츠(`free-contents`) 두 메뉴다.

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.reviews.index` | 수기 / 합격 후기 관리 | ReviewController `permissions->can(…, 'admin.reviews.index', 'can_update')`(:64), AttachmentController 매핑 `'review' => 'admin.reviews.index'`(:47) |
| `admin.free-contents.index` | 무료콘텐츠 관리 | 라우트 정규화. 무료콘텐츠 PDF 받기도 이 메뉴 조회 권한(AttachmentController:36 주석) |
| `admin.members.index`(회원관리) | — | 우수 후기 포인트 수동 지급 라우트 `admin.members.review-points.store` 는 회원관리 메뉴의 등록 권한으로 판정(routes/admin.php:993 주석, 박성민 10-21) |

- ROUTE_PERMISSIONS 예외 없음. 무료콘텐츠 엑셀은 개인정보가 없어 사유 입력 없이 다운로드 권한만(FreeContentController:115 주석).

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`).

### ADMN-BRD-005 수기 / 합격 후기 관리
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 스코어카드 | GET | `/{admin}/reviews` | `admin.reviews.index` | 조회 | ReviewController@index |
| 선택 노출/숨김 | PUT | `/{admin}/reviews/display` | `admin.reviews.display.update` | 수정 | ReviewController@bulkDisplay |
| 선택 베스트 선정/해제 | PUT | `/{admin}/reviews/best` | `admin.reviews.best.update` | 수정 | ReviewController@bulkBest |

### ADMN-BRD-005-S1 합격 후기 검증 (별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세 · 검증 화면 | GET | `/{admin}/reviews/{review}` | `admin.reviews.show` | 조회 | ReviewController@show |
| 검증 처리(검증완료 · 반려 · 숨김 + 노출 설정) | PUT | `/{admin}/reviews/{review}` | `admin.reviews.update` | 수정 | ReviewController@update |
| 우수 후기 포인트 수동 지급 | POST | `/{admin}/members/review-points/{review}` | `admin.members.review-points.store` | 등록(회원관리 메뉴) | ReviewController@grantPoint |
| 지급 알림 재발송 | PUT | `/{admin}/reviews/{review}/notifications/{notificationLog}` | `admin.reviews.notifications.update` | 수정 | ReviewController@resendNotification |

### ADMN-BRD-010 무료콘텐츠 관리 / 010-S1 등록 · 수정 (목록과 폼은 별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/free-contents` | `admin.free-contents.index` | 조회 | FreeContentController@index |
| 등록 폼(S1) | GET | `/{admin}/free-contents/create` | `admin.free-contents.create` | 등록 | FreeContentController@create |
| 등록 저장 | POST | `/{admin}/free-contents` | `admin.free-contents.store` | 등록 | FreeContentController@store |
| 엑셀(현재 조건) | GET | `/{admin}/free-contents/download` | `admin.free-contents.download` | 다운로드 | FreeContentController@download |
| 저장 전 중복 경고(JSON) | GET | `/{admin}/free-contents/duplicates` | `admin.free-contents.duplicates.index` | 조회 | FreeContentController@duplicates |
| 선택 전시/비전시 | PUT | `/{admin}/free-contents/status` | `admin.free-contents.status.update` | 수정 | FreeContentController@bulkStatus |
| 선택 삭제 | DELETE | `/{admin}/free-contents/selected` | `admin.free-contents.selected.destroy` | 삭제 | FreeContentController@bulkDelete |
| 수정 폼(S1) | GET | `/{admin}/free-contents/{freeContent}/edit` | `admin.free-contents.edit` | 수정 | FreeContentController@edit |
| 수정 저장 | PUT | `/{admin}/free-contents/{freeContent}` | `admin.free-contents.update` | 수정 | FreeContentController@update |

## 3. 폼 필드 · 검증
### 후기 검증 `modForm` (ReviewModerationRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `verify_status` | required in:verified,rejected,hidden (`verifyStatus`) | verified=검증 완료 · rejected=반려 · hidden=숨김 | `decidePassEssay('APPROVED'/'REJECTED')` |
| `reject_reason` | rejected 일 때 required · 10~255자 (`rejectReason`). 공통 사유 칩: 합격증 미제출 · 타 회차 합격증 · 글자 수 미달 · 광고·비방 포함 · 수강 이력 없음(Review::REJECT_REASONS) | 회원 마이페이지 · 알림에 그대로 노출 | v6.92: `pe-reject-chip`(사유 유형 6종 — '증빙 식별 불가'는 개발 칩에 없음) + `pe-reject-text`(10~255자) |
| `display_site` | nullable boolean | 사이트 후기 목록 노출 | 수강후기 `toggleCourseReviewVisible` |
| `is_best` | nullable boolean. 베스트 동시 최대 12(Review::BEST_MAX) | 베스트 | `toggleBestCourseReview` |
| `display_instructor_home` | nullable boolean | 강사 홈 노출 | 없음 |
| `cafe_verified` | nullable boolean | 카페 공유 확인 → cafe_verified_at | 없음 |

### 우수 후기 포인트 지급 (ReviewPointRequest extends MemberReasonRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `amount` | required · 1~999,999,999 정수(정규식) | 지급 포인트 | v6.92: 목록 [후기 보상 지급] `openReviewRewardModal()` → 모달 `modal-review-reward` `rw-amount`(기본값 = 포인트 정책 후기 보상값) · [지급] `confirmReviewReward()` |
| `reason` | required · 10~200자 · 공백 제외 10자 · 서로 다른 글자 3개 이상 | 지급 사유 | v6.92: `rw-reason` — 프로토는 금액을 정책값에서 바꿀 때만 필수(개발은 항상 필수) |
| (규칙) 후기 보상 회수 | 사유 `revoke_reason` in:false_fact,plagiarism,self_delete(게시 후 기본 30일 `reviewRevokeDays`) · 무상 P 잔액 한도 | 허위 사실 · 표절 · 단기 자진 삭제 | v6.92 S-21: `modal-review-revoke` `rv-reason` 라디오 · `confirmReviewRevoke()` — 개발 라우트 없음 |
- 지급 가능 상태(ReviewService::pointPanel): granted 지급함 · unverified 검증 전 · forbidden 권한 없음 · ready 지급 가능. 후기당 1회(reviews.point_granted_at).

### 후기 일괄 `bulkForm` (컨트롤러 인라인 검증)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | required array min:1 · integer | 없음(행 단위 토글만) |
| `show` (`bulkShow`) | display.update 일 때 required boolean | |
| `best` (`bulkBest`) | best.update 일 때 required boolean | |

### 무료콘텐츠 등록 · 수정 `freeContentForm` (FreeContentRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `content_type` | required in FreeContent::TYPES | EXAM=빈출자료 · DAILY=매일 1문제(정조교의 매일 1문제) | `fl-form-type`(v6.92: EXAM 빈출자료 · DAILY 매일 1문제 — 개발과 같음) |
| `cert_category_id` | required integer (categories 1Depth) | 자격증 | `fl-form-cert` |
| `year` | required 2000~2100 | 연도 | `fl-form-year` |
| `round_no` (`roundNo`) | EXAM 이면 required · 1~999. DAILY 는 서비스가 비움 | 회차 | 없음 |
| `title` | required max:100 | | `fl-form-title` |
| `content` | nullable(에디터) | 본문 · 해설 | `fl-form-body` |
| `status` | required in published,hidden | published=전시 · hidden=비전시 | 노출상태 |
| `started_at` | nullable Y-m-d | 전시 시작일 | v6.92: `fl-form-date` 게시일(프로토 필수, 매일 1문제는 게시일 하루 1문제) |
| `related_course_id` | nullable integer | 관련 강좌(상세 하단 카드) | 없음 |
| `attachments[]` | max 5 · PDF만 · 개당 10MB(실제 바이트 검사) | | `fl-form-pdf`(파일명 텍스트) |
| `delete_attachments[]` | integer | | 없음 |
| `list_query` | max:1000 | 저장 후 목록 조건 | 없음 |
| (없음) | | | ~~`fl-form-vod` 연동 VOD 에셋 코드 / 러닝타임~~ v6.92 삭제(S-22 · D-BRD-01). 공개 범위 고정 표시 `fl-form-access`(본문 누구나 · PDF 로그인 회원만, 입력 없음) |

### 중복 경고 (FreeContentDuplicateRequest, GET JSON)
`content_type` · `cert_category_id` · `year` · `round_no` · `except_id` — 같은 구분 · 자격증 · 연도 · 회차가 있으면 막지 않고 경고.

### 무료콘텐츠 일괄 (FreeContentStatusRequest · SelectedIdsRequest)
`ids[]`(required) + `status`(published/hidden, `bulkStatus`). 삭제는 `bulkMethod` 를 DELETE 로 바꿔 `admin.free-contents.selected.destroy`.

## 4. 목록 필터 · 정렬 · 표 컬럼
### 후기 목록 (ReviewController@index:26-50, ReviewRepository:110-147)
- 필터: `date_from` · `date_to` · `verify_status`(pending/verified/rejected/hidden) · `exam_target_id` · `exam_round` · `instructor_id` · `cafe`(shared/not) · `display`(shown/hidden) · `is_best`(1) · `point`(granted/not) · `refund`(1=환급 신청 연계) · `keyword`(제목) · `per_page`.
- 기본: 쿼리가 없으면 최근 90일 · 검증 대기.
- 정렬: created_at asc → id asc(오래된 대기 건부터, ReviewRepository:22-23).
- 스코어카드: pending 검증 대기 · verified 검증 완료 · cafe 카페 공유 · best 베스트 · refund 환급 연계.
- 표 컬럼(개발): 선택 · 작성일 · 제목 · 작성자 · 합격 증빙 · 글자수 · 카페 공유 · 포인트 · 상태 · 처리.
- 프로토타입: 수강후기 표(후기번호 · 강좌/강사 · 진도율 · 별점 · 제목/한줄평 · 수강생 · 베스트/포인트 · 노출상태 · 관리)와 합격수기 표(수기번호 · 종목/회차 · 합격 구분 · 제목/공부법 · 증빙 파일 · 작성자 · 검수 상태 · 검수 액션)가 따로. 필터 `cr-best-filter` · `cr-keyword` · `pe-status-filter`(심사대기 · 인증승인 완료 · 반려) · `pe-keyword`.

### 무료콘텐츠 목록 (FreeContentIndexRequest:29-49)
- 필터: `type`(EXAM/DAILY) · `cert` · `year` · `round` · `display`(published/hidden) · `keyword`(100자) · `sort`(latest 등록일순 · year 연도순 · round 회차순) · `page`.
- 표 컬럼(개발): 선택 · No · 구분 · 자격증 · 제목 · 연도 · 회차 · PDF · 등록일 · 등록자 · 전시.
- 프로토타입: 콘텐츠 ID · 구분 · 종목/대비연도 · 제목 · 게시일 · PDF(로그인 회원만) · 조회수 · 노출상태 · 관리(v6.92: '연동 VOD/러닝타임' 열 → '게시일'). 필터 `fl-type-filter`(EXAM · DAILY) · `fl-cert-filter`.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| reviews.user_id / course_id / instructor_id | | 작성 회원(마스킹) · 수강 강좌 · 강사 | 작성자 · 강좌/강사 |
| reviews.title / content / rating(1~5, 회원값) / char_count | | 본문 · 별점 · 글자수(우수 기준 1,000자 Review::CHAR_THRESHOLD) | 글자수 |
| reviews.exam_target_id / exam_round | | 응시 종목 · 회차 | 종목/회차 |
| reviews.pass_cert_path | string(255) | 합격 증빙 이미지 | 합격 증빙 |
| reviews.cafe_share_url / cafe_verified_at | | 네이버 카페 공유 · 확인 시각 | 카페 공유 |
| reviews.verify_status | string(20) | pending 검증 대기 · verified 검증 완료 · rejected 반려 · hidden 숨김 | 상태 |
| reviews.reject_reason / verified_by / verified_at | | 반려 사유 · 처리자 · 시각 | 검증 |
| reviews.is_best / display_site / display_instructor_home | boolean | 베스트 · 사이트 노출 · 강사 홈 노출 | 노출 · 베스트 |
| reviews.refund_claim_id | bigint | 합격환급 신청 연계(반려 시 환급 심사도 막힘) | 환급 연계 링크(`admin.pass-refunds.show`) |
| reviews.point_granted_at | timestamp | 우수 후기 포인트 지급(1회) | 포인트 |
| points / point_logs | | 지급 원장(회원 수동 지급과 같은 경로) | 지급 이력 |
| notification_logs(target=review) | | 지급 알림 이력 · 재발송 | 발송 이력 |
| boards.code = `free-content` | | 무료콘텐츠 게시판(FreeContent::BOARD_CODE) | — |
| posts.content_type | string(10) | EXAM 빈출자료 · DAILY 매일 1문제 | 구분 |
| posts.cert_category_id / year / round_no / related_course_id | | 자격증(categories 1Depth) · 연도 · 회차(빈출만) · 관련 강좌 | 자격증 · 연도 · 회차 |
| posts.status / started_at / view_count | | 전시(published) · 비전시(hidden) · 전시 시작일 · 조회수 | 전시 |
| attachments(PDF) | | 무료콘텐츠 PDF(로그인 회원만 받는 비공개 파일) | PDF |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `bulkForm` · `bulkShow` · `bulkBest` · `toggleAll()` · `submitBulk()` | 후기 목록 일괄 노출 · 베스트 | 행 버튼 `toggleCourseReviewVisible` · `toggleBestCourseReview` |
| `modForm` · `verifyStatus` · `rejectReason` · `btnVerify` · `refresh()` · `submitMod()` | 검증 처리 폼 | 서브페이지 `pass-audit` · `decidePassEssay()` |
| 포인트 지급 폼(action `admin.members.review-points.store`, `amount` · `reason`) | 우수 후기 포인트 | v6.92: 모달 `modal-review-reward`(`rw-amount` · `rw-reason` · `confirmReviewReward()`) |
| `admin.inc._notify-history` | 지급 알림 이력 · 재발송 | 없음 |
| `freeContentForm` · `roundField` · `roundNo` · `roundNone` | 무료콘텐츠 폼(DAILY 이면 회차 숨김) | 서브페이지 `free-lecture` · `fl-form-*` |
| `filterType` · `filterRound` | 목록 필터(구분에 따라 회차 필터) | `fl-type-filter` |
| `bulkForm` · `bulkMethod` · `bulkStatus` | 무료콘텐츠 일괄 전시 · 삭제 | 없음 |

하위 화면: 개발 BRD-005-S1 = 별도 페이지 `admin.reviews.show`, BRD-010-S1 = 별도 페이지 create/edit. 프로토타입은 SJM_PAGE 서브페이지 `pass-audit` · `free-lecture`.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 후기: 상태 숨김(hidden) · 강사 홈 노출 · 카페 공유 확인 · 환급 신청 연계 표시/필터 · 스코어카드 5종 · 일괄 노출/베스트 · 응시 종목 · 회차 · 강사 · 포인트 지급 여부 필터 · 반려 공통 사유 칩.
- 우수 후기 포인트 지급을 검증과 분리(금액 · 사유 입력, 회원관리 등록 권한) + 지급 알림 재발송. **→ 결정(v6.92 white, D-BRD-02)**: 프로토도 승인(검증 완료)과 후기 보상 지급을 나눔 — 목록 [후기 보상 지급] 모달, 1건 1회, 금액 기본 = 정책값(바꾸면 사유). 지급 알림 재발송은 여전히 개발에만
- 무료콘텐츠: ~~매일 1문제(DAILY) 구분~~(v6.92 프로토에 추가), 회차, ~~전시 시작일~~(v6.92 프로토 게시일), 관련 강좌, PDF 다중 첨부(5), 저장 전 중복 경고, 정렬(등록일 · 연도 · 회차), 엑셀, 일괄 전시/비전시 · 삭제.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 수강후기와 합격수기의 분리 운영(별도 탭 · 별도 상태 체계). 개발 reviews 는 한 테이블 · 한 목록이다.
- 수강후기 표의 수강 진도율 · 별점 열, 합격수기 "합격 구분" 열.
- 무료특강 영상(FREE_LECTURE) 구분과 VOD 에셋 코드 · 러닝타임. **→ 결정(v6.92 white, S-22 · D-BRD-01)**: 무료콘텐츠는 빈출자료 · 매일 1문제 2종(개발 TYPES와 같음), VOD 필드 · 열 삭제 — 무료특강 영상은 PROD-002 맛보기 · PROD-003 무료 강좌에서 등록
- (v6.92 S-21) 후기 보상 회수(허위 · 표절 · 게시 후 30일 안 자진 삭제, 무상 P 잔액 한도) · 보상 후기 '포인트 지급 후기' 배지 · 합격수기 반려 시 합격환급 '보완 요청' 연동 표시.
- 무료콘텐츠 버전 이력 표(버전 · 저장일 · PDF · 본문 요약 · 변경 내용).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 검수 상태: 심사대기 → `pending`, 인증승인 완료(APPROVED) → `verified`, 반려(REJECTED) → `rejected`.
- 무료콘텐츠 구분: FREQ_EXAM → `EXAM`(빈출자료). FREE_LECTURE 는 개발에 없고 개발 DAILY(매일 1문제)는 프로토타입에 없음. **→ 결정(v6.92 white, S-22 · D-BRD-01)**: 프로토 값이 `EXAM` · `DAILY`로 바뀌어 차이 없음
- 노출상태 → 무료콘텐츠 `status` published(전시) · hidden(비전시), 후기 `display_site`.
- 화면 단위: 탭 3개 → 개발 메뉴 2개(`reviews` · `free-contents`).

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_BRD.md` 의 D-BRD 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 수강후기와 합격수기를 분리 운영할지 확인 필요 — 개발은 "수기·합격 후기" 한 테이블(reviews)로 검증 · 노출 · 포인트를 처리한다(Review 모델 주석). **→ 정책 아님(POLICY_D_BRD B)**: 화면 · 이름 문제로 처리 — 데이터는 개발 reviews 한 테이블, 탭은 합격 증빙 유무 필터(있음 = 합격수기 / 없음 = 수강후기), 상태는 개발 4값
- 합격 인증 승인과 보상 포인트 지급을 한 동작으로 묶을지 확인 필요 — 개발은 검증 후 별도 지급(금액 · 사유, 회원관리 등록 권한). **→ 결정(v6.92 white, D-BRD-02 · S-21)**: 나눈다 — 승인은 검증만, 지급은 목록 [후기 보상 지급](1건 1회, 정책값 기본 · 바꾸면 사유), 회수는 허위 · 표절 · 30일 안 자진 삭제만
- 무료콘텐츠 구분(무료특강 영상 · 빈출문제 vs 개발 빈출자료 · 매일 1문제)과 VOD 연동 여부 확인 필요. **→ 결정(v6.92 white, S-22 · D-BRD-01)**: 빈출자료(EXAM) · 매일 1문제(DAILY) 2종 1차 운영, VOD 연동 없음(무료특강 영상은 PROD-002 · 003)

## 출처
- routes/admin.php:721-730, 837-848, 993 (dev_spec/_index/routes.md)
- app/Http/Controllers/Admin/ReviewController.php:26-50, 56-73, 78-83, 101-140
- app/Http/Requests/Admin/ReviewModerationRequest.php · ReviewPointRequest.php · MemberReasonRequest.php
- app/Services/Admin/ReviewService.php:76, 134, 160, 199, 247-272
- app/Repositories/Admin/ReviewRepository.php:22-23, 31-40, 110-147
- app/Models/Review.php:16-35
- app/Http/Controllers/Admin/FreeContentController.php:21, 30-130 · app/Http/Requests/Admin/FreeContentRequest.php · FreeContentIndexRequest.php:14, 29-49 · FreeContentDuplicateRequest.php · FreeContentStatusRequest.php
- app/Models/FreeContent.php:9-29
- app/Http/Controllers/Admin/AttachmentController.php:36, 47
- resources/views/admin/reviews/index.blade.php:38-130, 159-205 · reviews/show.blade.php:9, 126-210, 238-258 · free-contents/index.blade.php · free-contents/form.blade.php · create.blade.php · edit.blade.php
- database: dev_spec/_index/schema.md reviews · posts(content_type 등 2026_10_21_000239) · attachments
- 프로토타입: prototype_clean/ADMN-BRD-005_baseline.html:743-1030(목록 · 탭), 1027-1120(서브페이지), 1277-1546(스크립트)
