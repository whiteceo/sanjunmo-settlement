# ADMN-USER-001 회원관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-USER-001_baseline.html` (원본 상태: `18d66c1` v6.92)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: USER-001 · 001-P1 · 002 · 002-P1 · 002-P2 · 002-P3 · 003 · 004 · 004-P1 · 005 · 006 · 006-S1 · 006-S2 · 006-S3(프로토타입 한 파일 안의 view 5개 + 모달)
- 개발 진행: 구현(001~006 라우트 · 화면 있음). 002-P3(1:1 메시지) · 006-S3(처리 결과)는 미구현 → 규칙 기반 명명
- 근거 상세: 회원관리 개발 검토(로컬 `scripts/qa/reports/review/findings/member/`, git 제외) — 아래 7절에 요지만 옮겼다

프로토타입 view ↔ 개발 화면
| 프로토타입 view(id) | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| `view-list` | USER-001 회원 목록 | `resources/views/admin/members/index.blade.php` |
| `view-detail` | USER-002 회원 상세 | `members/view.blade.php` (+ `_point-grant-modal`, `_download-modal`) |
| `view-course` | USER-003 수강 · 기기 제어 + USER-004 진도율 | `members/course/index.blade.php` + `_control-modals`, `member-progress/index · adjust · adjust-history` |
| `view-tags` | USER-006 그룹 · 태그 (+S1 · S2) | `members/group/index · save`, `members/tag/form` |
| `view-blacklist` | USER-005 블랙리스트 | `members/blacklist/index · create` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명(개발 서버) | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.members.index` | 회원 관리 | view-list · view-detail | 개발 서버 메뉴 관리 열람(10-26) |
| `admin.members.course.index` | 수강 · 기기 제어 | view-course(수강 표) | 〃 |
| `admin.member-progress.index` | 진도율 / 이어보기 | view-course(진도 표 · 보정) | 〃 |
| `admin.members.blacklist.index` | 블랙리스트 | view-blacklist | 〃 |
| `admin.members.group.index` | 그룹 · 태그 | view-tags | 〃 |

- 권한 축 5개(조회 · 등록 · 수정 · 삭제 · 다운로드). 프로토타입 권한 매트릭스(CONF-005)는 '회원' 1행 → 개발은 위 5행.
- 주의(개발 결함, 검토 #9): 상세 화면의 블랙리스트 · 그룹 버튼은 `@adminCan('admin.members.index', …)`로 노출을 판정하지만 서버는 `members.blacklist.index` · `members.group.index` 메뉴로 막는다(`view.blade.php:172`, `blacklist/index.blade.php:104,134`, `group/index.blade.php:57`). prototype_dev는 버튼마다 서버가 보는 메뉴를 `data-dev-perm`에 적는다.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{member}` = `users.id`.

### USER-001 회원 목록 · 001-P1 엑셀
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 | GET | `/members` | `admin.members.index` | 조회 | MemberController@index |
| 엑셀 다운로드(P1 제출) | GET | `/members/download` | `admin.members.download` | 다운로드 | MemberController@download |
| 선택 회원 메시지 발송 | → | `/message-templates/campaigns/create`(대상 회원 id 전달) | `admin.message-templates.campaigns.create` | 등록(메시지 템플릿 메뉴) | MessageCampaignController@create |
| 선택 회원 태그 부여 | → | `/members/group` (scope=selected) | `admin.members.group.index` | 조회 → 실행은 `members.group.member.update` | |

### USER-002 회원 상세 · P1 포인트 · P2 소셜 · P3 메시지
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세 (탭 `?tab=order\|refund\|inquiry\|course\|point\|history`) | GET | `/members/{member}` | `admin.members.show` | 조회 | MemberController@show |
| 일반 정보 저장 | PUT | `/members/{member}` | `admin.members.update` | 수정 | MemberController@update |
| 상태 변경(정상 ↔ 휴면) | PUT | `/members/{member}/status` | `admin.members.status.update` | 수정 | MemberController@updateStatus |
| P1 무상 포인트 지급 · 차감 | POST | `/members/{member}/points` | `admin.members.points.store` | **등록** | MemberController@storePoint |
| P2 소셜 연동 해제 | DELETE | `/members/{member}/social/{socialAccount}` | `admin.members.social.destroy` | **삭제** | MemberController@destroySocial |
| 쿠폰 회수 | PUT | `/members/{member}/coupons/{userCoupon}` | `admin.members.coupons.update` | 수정 | MemberController@revokeCoupon |
| 마스킹 해제 | POST | `/masking/unmask` | `admin.masking.unmask` | 메뉴 권한 밖(MaskingService::canUnmask) | MaskingController@unmask |
| P3 1:1 메시지 즉시 발송 | POST | `/members/{member}/messages` (규칙) | `admin.members.messages.store` (규칙) | 등록 | 개발 미구현 |
| 임시 비밀번호 메일 | POST | `/members/{member}/temp-password` (규칙) | `admin.members.temp-password.store` (규칙) | 등록 | 개발 미구현(버튼 비활성) |
| 비밀번호 수동 초기화 | PUT | `/members/{member}/password` (규칙) | `admin.members.password.update` (규칙) | 수정 + 최고 관리자 | 개발 미구현 |
| 5회 오류 잠금 해제 | PUT | `/members/{member}/lock` (규칙) | `admin.members.lock.update` (규칙) | 수정 | 개발 미구현 |
| CS 상담 기록 추가 | POST | `/members/{member}/cs-memos` (규칙) | `admin.members.cs-memos.store` (규칙) | 등록 | 개발 미구현(메모 1칸 `admin_memo`) |
| 관리 이력 전체 | → | `/admin-logs?target_member={id}` | `admin.admin-logs.index` | 조회(로그 메뉴) | |

### USER-003 수강 · 기기 제어
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 회원 검색 · 수강 목록 | GET | `/members/course?member_id=&type=&keyword=&include_ended=` | `admin.members.course.index` | 조회 | MemberCourseController@index |
| 종료일 연장(+N일) | POST | `/members/course/{userCourse}/extend` | `admin.members.course.extend.update` | 수정 | MemberCourseController@extend |
| 일시정지 | POST | `/members/course/{userCourse}/pause` | `admin.members.course.pause.update` | 수정 | MemberCourseController@pause |
| 일시정지 해제 | POST | `/members/course/{userCourse}/resume` | `admin.members.course.resume.update` | 수정 | MemberCourseController@resume |
| 종료일 단축(−N일) | POST | `/members/course/{userCourse}/shorten` (규칙) | `admin.members.course.shorten.update` (규칙) | 수정 | 개발 미구현(정책 질문) |
| 세션 강제 로그아웃 | POST | `/members/course/{userCourse}/session` (규칙) | `admin.members.course.session.destroy` (규칙) | 삭제 | 개발 미구현("SPK 콘솔에서", 정책 질문) |
| 기기 리셋 | POST | `/members/course/{userCourse}/device-reset` (규칙) | `admin.members.course.device-reset.update` (규칙) | 수정 | 개발 미구현 |

### USER-004 진도율 · 004-P1 보정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 조회 | GET | `/member-progress?user=&course=course:{id}\|package:{id}` | `admin.member-progress.index` | 조회 | MemberProgressController@index |
| 진도율 재집계 | POST | `/member-progress/recalculate` | `admin.member-progress.recalculate` | **수정**(접미사 예외) | MemberProgressController@recalculate |
| 진도 엑셀 | GET | `/member-progress/download` | `admin.member-progress.download` | 다운로드 | MemberProgressController@download |
| 보정 폼(P1) | GET | `/member-progress/{userCourse}/lectures/{lecture}/adjust` | `admin.member-progress.adjust.edit` | 수정 | ProgressAdjustmentController@edit |
| 보정 이력 | GET | `/member-progress/{userCourse}/lectures/{lecture}/adjust/history` | `admin.member-progress.adjust.history.index` | 조회 | ProgressAdjustmentController@history |
| 보정 반영 | PUT | `/member-progress/{userCourse}/lectures/{lecture}/adjust` | `admin.member-progress.adjust.update` | 수정 | ProgressAdjustmentController@update |

### USER-005 블랙리스트
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 원장(탭 `tab=listed\|…`, `state=active\|closed`, `keyword`) | GET | `/members/blacklist` | `admin.members.blacklist.index` | 조회 | MemberBlacklistController@index |
| 수동 등재 폼 | GET | `/members/blacklist/create?member_id=` | `admin.members.blacklist.create` | 등록 | MemberBlacklistController@create |
| 등재 | POST | `/members/blacklist` | `admin.members.blacklist.store` | 등록 | MemberBlacklistController@store |
| 정지 해제 | PUT | `/members/blacklist/{sanction}` | `admin.members.blacklist.update` | 수정 | MemberBlacklistController@update |
| 관리자 강제 탈퇴 | POST | `/members/{member}/withdrawal` (규칙) | `admin.members.withdrawal.store` (규칙) | 등록 | 개발 미구현(서비스 함수만) |

### USER-006 그룹 · 태그 · S1 태그 폼 · S2 조건 그룹 · S3 처리 결과
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(태그 · 그룹 · 일괄 처리) | GET | `/members/group` | `admin.members.group.index` | 조회 | MemberGroupController@index |
| 수동 태그 간이 등록 | POST | `/members/group` | `admin.members.group.store` | 등록 | MemberGroupController@store |
| 태그 이름 · 설명 수정 | PUT | `/members/group/{group}` | `admin.members.group.update` | 수정 | MemberGroupController@update |
| 태그 삭제 | DELETE | `/members/group/{group}` | `admin.members.group.destroy` | 삭제 | MemberGroupController@destroy |
| 일괄 부여 · 해제 실행 | PUT | `/members/group/member` | `admin.members.group.member.update` | 수정 | MemberGroupController@updateMember |
| 엑셀 명단 매칭 | POST | `/members/group/upload` | `admin.members.group.upload.store` | 등록 | MemberGroupController@storeUpload |
| 미매칭 명단 받기 | GET | `/members/group/unmatched/download` | `admin.members.group.unmatched.download` | 다운로드 | MemberGroupController@downloadUnmatched |
| S1 태그 생성 폼(`?mode=manual\|auto`) | GET | `/members/group/tag/create` | `admin.members.group.tag.create` | 등록 | MemberTagController@create |
| S1 태그 저장 | POST | `/members/group/tag` | `admin.members.group.tag.store` | 등록 | MemberTagController@store |
| S1 대상 미리보기 | GET | `/members/group/tag/preview` | `admin.members.group.tag.preview.index` | 조회 | MemberTagController@preview |
| S1 태그 수정 폼 · 저장 | GET · PUT | `/members/group/tag/{tag}/edit` · `/members/group/tag/{tag}` | `admin.members.group.tag.edit` · `.update` | 수정 | MemberTagController@edit · update |
| S2 조건 그룹 저장 폼 · 저장 | GET · POST | `/members/group/saved/create` · `/members/group/saved` | `admin.members.group.saved.create` · `.store` | 등록 | SavedGroupController@create · store |
| S2 조건 그룹 수정 · 삭제 | PUT · DELETE | `/members/group/saved/{group}` (규칙) | `admin.members.group.saved.update` · `.destroy` (규칙) | 수정 · 삭제 | 개발 미구현(검토 #4) |
| 자동 태그에서 회원 제외 | POST | `/members/group/tag/{tag}/exclusions` (규칙) | `admin.members.group.tag.exclusions.store` (규칙) | 등록 | 개발 미구현(서비스 `excludeMember`만, 검토 #3) |
| S3 처리 결과 · 재처리 · 처리 단위 해제 | GET · POST · DELETE | `/members/group/batches/{batch}` 등 (규칙) | `admin.members.group.batches.show` · `.retry.store` · `.destroy` (규칙) | 조회 · 등록 · 삭제 | 개발 미구현 |

## 3. 폼 필드 · 검증

### 001 목록 검색 (GET 쿼리, MemberService::FILTER_KEYS)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `date_from` · `date_to` | date | 가입일 날짜 2칸 |
| `status` | `active`(정상) · `dormant`(휴면) · `withdrawn`(탈퇴) · `suspended`(정지 — 표시용 파생, DB status 아님) | 회원 상태 select |
| `search_type` | `name` · `email` · `phone_tail` · `member_no` | 검색어 구분 select (프로토 '산준모 카페 ID'는 개발 없음) |
| `keyword` | text | `#kw-input` |
| `join_method` | `email` · `naver` · `kakao` · `google` | 가입 방식 |
| `point_min` · `point_max` · `minus_only`(1) | number · checkbox | 보유 포인트 · `#chk-minus-only` |
| `group_id` | user_groups.id | 태그 · 그룹 select |
| `inactive_days` | `30` · `90` · `365` | 최종 접속 select |
| `address` | `''` · `registered` · `none` | 배송 주소 |
| `sort` · `direction` | `created_at` · `paid_point` · `free_point` · `last_login_at` / `asc` · `desc` | 표 머리 정렬 |
| `per_page` | `30` · `50` · `100` | `#grid-page-size` |
| `ids[]` | users.id | 행 체크박스 |

### 001-P1 엑셀 다운로드 (MemberDownloadRequest extends ReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `fields[]` | required · array · min:1 | `joined_at` 가입일 · `name` · `email` · `phone` · `address` · `points` · `status` (기본 해제: phone · address) | `#ex-cols-block` 체크박스 |
| `reason` · `reason_etc` · `reason_ref` | ReasonRequest(정형 사유 + 기타 직접 입력 + 근거 번호) | | `#excel-reason` |
| `pledge_purpose` · `pledge_destroy` | accepted | | `#ex-pledge-1` · `#ex-pledge-2` |

### 002 일반 정보 (MemberRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `is_marketing_agreed` | required · boolean (이메일 · SMS · 알림톡 통합 1값) | `#dt-mkt-agree` |
| `address` · `address_detail` | nullable · max 255 · 100 | 기본 배송지 |
| `admin_memo` | nullable · max 2000 (덮어쓰기, 이전 값은 user_change_logs) | 프로토는 CS 상담 이력 타임라인(`#cm-*`) — 7절 |
| `exam_target_ids[]` | integer · exam_targets 존재 | 응시 예정(관심 자격) |

### 002 상태 변경 (MemberStatusRequest extends MemberReasonRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `status` | `active` · `dormant`만(EDITABLE_STATUSES). 정지는 블랙리스트 등재로만, 탈퇴는 본인 절차로만 | `#modal-st-val` |
| `reason` | 공백 제외 10자 · 서로 다른 글자 3개 이상 · 200자 이하 | `#modal-st-reason` |

- (v6.92, M-04 결정) 짧은 사유 칸은 공백 포함 200자 이하(프로토 `maxlength=200` — `#modal-st-reason` · `#pt-reason-txt` · `#ext-reason-input` · `#excel-reason` · `#social-reason` · `#unmask-reason` · `#pwt-reason` · `#pwr-reason` · `#blr-reason` · `#rsn-reason` · `#m3f-pa-reason` · `#cm-result-note`), 서술형 칸(CS 상담 내용 `#cm-content` · 블랙리스트 상세 경위 `#bl-detail-memo`)은 1,000자 이하. 개발 MemberReasonRequest 200자와 일치, 서술형 두 칸만 1,000자로 늘린다.

### 002-P1 포인트 (MemberPointRequest extends MemberReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `direction` | required | `grant` 지급 · `deduct` 차감 | `pt_mode` PLUS · MINUS |
| `amount` | `^[1-9]\d{0,8}$` (상한 검사 없음 — 검토 #7) | | `#pt-amount` |
| `reason_code` | required | `cs_outage` CS 보상(서비스 장애) · `cs_delivery` CS 보상(배송 지연) · `event` 이벤트 당첨 · `promotion` 프로모션 보상 · `correction` 오지급 정정 · `partner` 제휴 정산 · `other` 기타 | `#pt-reason-cat` |
| `reason` | MemberReasonRequest | | `#pt-reason-txt` |
| `expire_preset` | grant일 때 required | `30` · `90`(기본) · `180` · `custom` | `#pt-exp` |
| `expire_date` | preset=custom일 때 required · 오늘 이후 | | 프로토 없음(개발에만) |
| (알림톡 발송) | 개발 없음 | | `#pt-alimtalk`(프로토에만) |

### 002-P2 소셜 연동 해제
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` | MemberReasonRequest | `#social-reason` |
| 대상 | URL의 `{socialAccount}` = social_accounts.id | `#social-modal-rows` 행 |

### 003 수강 제어 (CourseExtendRequest · CoursePauseRequest extends MemberReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `member_id` | required | | 선택 회원 |
| `days` | `^[1-9]\d{0,3}$` | 프리셋 `days_preset` 7 · 15 · 30 · 60 · 90 | `#ext-days-input`, `setExtendDays()` 버튼 |
| `reason_code` | required | `cs_compensation` CS 보상(서비스 장애) · `device_issue` 기기 문제 · `long_absence` 군입대·장기부재 · `event` 이벤트 제공 · `correction` 오적용 정정 · `etc` 기타 | 프로토 없음(자유 사유만) |
| `reason` | MemberReasonRequest | | `#ext-reason-input` |
| `indefinite` | pause만 required `0\|1` (1 = 무기한) | | 프로토 없음(정책 질문) |
| (조정 구분) | 개발은 라우트로 나눔(extend · pause · resume) | | `adj_type` EXTEND · SHORTEN · PAUSE |
| 검색 `type` · `keyword` · `include_ended` | GET | | `#crs-search-type` |

### 004-P1 진도 보정 (ProgressAdjustmentRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `adjusted_rate` | integer 0~100 | | `#m3f-pa-rate` |
| `reason_code` | required | `log_lost` 플레이어 장애로 재생 로그 유실 · `ingest_missed` 서버 점검 중 적재 누락 · `lecture_reorg` 콘텐츠 교체로 차시 재편 · `etc` 기타(직접 입력) | `#m3f-pa-type` |
| `reason_text` | etc일 때 required · max 100 | | |
| `detail` | 20~1000자 | | `#m3f-pa-reason` |
| `evidence[]` | 파일 1~5개 필수 | | `#m3f-pa-file` |

### 005 블랙리스트 등재 (MemberBlacklistRequest) · 해제 (MemberReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `member_id` | required | | 수동 등재 모달 회원 선택 |
| `reason_type` | required | `concurrent_ip` 동시 접속 IP · `concurrent_session` 동시 재생 세션 · `speed_tamper` 배속 · 탐색 변조 · `minus_point` 마이너스 포인트 · `other` 기타 | 적발 유형 |
| `duration` | required | `7` · `30` · `permanent` (권장: 1회 7 · 2회 30 · 3회 이상 영구) | 정지 기간 |
| `reason` | MemberReasonRequest — 서술형 1,000자로 늘림(v6.92 M-04, 개발 200자) | | 상세 사유 `#bl-detail-memo` |
| `refund_confirm` | nullable boolean | | |
| 해제 `reason` | MemberReasonRequest | | `#blr-reason` |
| 목록 `tab` · `state` · `keyword` | GET | `state`: `active` · `closed` | 필터 |

### 006 일괄 부여 · 해제 (MemberGroupBulkRequest extends MemberReasonRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `group_id` | required | | `#m3f-bk-tag` |
| `action` | required | `assign` 부여 · `remove` 해제 | `m3f-bk-action` ADD · REMOVE |
| `scope` | required | `selected` · `filter` · `upload` | `m3f-bk-scope` CHECKED · COND · EXCEL |
| `member_ids[]` | scope=selected일 때 · 최대 MAX_BULK | | 체크 회원 |
| `filter` | scope=filter일 때 array | | 현재 조건 |
| `file` (upload.store) | 엑셀 | | `#m3f-bk-file` |
| `reason` | MemberReasonRequest | | `#m3f-bk-reason` |
| 목록 필터 `tags[]` · `tag_join` · `exclude_tags[]` | GET | `tag_join`: and · or | 태그 조합 필터 |

### 006-S1 태그 생성 · 수정 (MemberTagRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `name` | required · max 100 | | `#m3f-tc-name` |
| (태그 코드) | 개발은 `user_groups.code` 자동 | | `#m3f-tc-code` |
| `axis` | required | `certificate` 자격증 · `learning` 학습 상태 · `campaign` 캠페인 | 프로토 없음(개발에만) |
| `assign_method` | required | `manual` · `auto` | `m3f-tc-type` MANUAL · AUTO |
| `badge_color` | required | `gray` · `blue` · `green` · `orange` · `red` · `purple` | 프로토 없음(개발에만) |
| `description` | max 255 | | 설명 |
| `eval_cycle` | auto만 | `daily` 매일 06:00 · `weekly` 매주 월 06:00 · `monthly` 매월 1일 06:00 | 평가 주기 |
| `on_exit` | auto만 | `keep` 유지(권장) · `release` 자동 해제 | 이탈 처리 |
| `conditions[n][field\|op\|value\|join]` | value max 50 | (조건 항목 5종) | `modalTagCond` `#m3f-cd-*` |

### 006-S2 조건 그룹 저장 (SavedGroupRequest)
| 필드 | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `name` | required · max 100 | | `#m3f-grp-name` |
| `group_type` | required | `static` 정적 · `dynamic` 동적 | `m3f-grp-mode` STATIC · DYNAMIC |
| `share_scope` | required | `all` 전체 운영자 · `owner` 본인만 | `m3f-grp-share` ALL · MINE |
| `description` | max 255 | | `#m3f-gs-memo` |
| `tags[]` · `tag_join` · `exclude_tags[]` | 목록에서 들고 옴 | `tag_join` and · or | `m3f-grp-op` AND · OR |

## 4. 목록 표 컬럼 (001)
| 개발 컬럼 | 정렬 키 | 프로토타입 컬럼 |
|---|---|---|
| 가입일 | `created_at` | 가입일 ▾ |
| 이름 | | 회원번호 / 이름 (개발은 회원번호 없음) |
| 이메일(ID) | | 이메일(ID) · 가입방식 |
| (없음) | | 산준모 카페 ID — 프로토에만 |
| 휴대폰 | | 휴대폰 |
| 누적 결제 · 누적 환불 | (정렬 없음) | 누적 결제 ▾ · 누적 환불 ▾ |
| 유상 P | `paid_point` | **적립 P** ▾ (용어 다름 — 정본은 '적립 P', 개발 '유상 P') |
| 무상 P | `free_point` | 무상 P ▾ |
| 상태 | | 상태 / 잠금 |
| 최종 접속 · 관리 | `last_login_at` | 최종 접속 · 관리 |

## 5. DB 테이블 · 컬럼 (화면에 쓰는 것만, 전체는 `_index/schema.md`)
| 테이블.컬럼 | 뜻 | 화면 |
|---|---|---|
| `users.id` | 회원번호(화면 표기 없음) | 001 · 002 |
| `users.name` · `email` · `login_id` · `phone` | 이름 · 이메일 · 관리자 로그인 ID(회원은 NULL) · 휴대폰(하이픈 제거) | 001 · 002 |
| `users.status` | `active` · `dormant` · `withdrawn`. 정지는 `is_locked` + `lock_reason=admin_block`로 파생 | 001 · 002 |
| `users.is_locked` · `lock_reason` · `locked_until` · `login_fail_count` | 잠금(`auto_5fail` 5회 실패 · `admin_block` 관리자 정지) | 002 |
| `users.join_method` | `email` · `naver` · `kakao` · `google` | 001 · 002 |
| `users.is_marketing_agreed` · `marketing_agreed_at` | 마케팅 수신 통합 1값 · 동의/철회 시각 | 002 |
| `users.address` · `address_detail` | 기본 배송지 | 001 필터 · 002 |
| `users.cafe_id` | 산준모 네이버 카페 ID(가입 데이터에 있음, 관리자 화면 미표시) | 002 |
| `users.di_hash` | 본인인증 DI 해시 | 002 |
| `users.total_points` | 포인트 잔액 캐시(무상+유상, 마이너스 가능) | 001 |
| `users.last_login_at` · `admin_memo` · `birth_date` · `gender` | | 002 |
| `points` (`type`, `amount`, `balance`, `source`, `expires_at`, `admin_id`, `memo`) | 포인트 적립 단위(유상/무상 구분 `type`) | 002 포인트 원장 |
| `point_logs` (`action`, `amount`, `balance_after`, `order_id`, `refund_id`, `reason`) | 포인트 원장 | 002 포인트 원장 탭 |
| `social_accounts` (`provider`, `provider_id`) | 소셜 연동 | 002-P2 |
| `user_change_logs` (`field`, `before_value`, `after_value`, `admin_id`, `ip`) | 회원 정보 변경 이력 | 002 관리 이력 |
| `user_sanctions` (`type`, `reason_type`, `reason`, `ends_at`, `released_at`, `released_by`, `admin_id`) | 블랙리스트 원장 | 005 |
| `user_courses` (`progress_rate` 등) · `lecture_progress_adjustments` (`original_rate`, `adjusted_rate`, `reason_code`, `reason_text`, `detail`, `adjusted_by`) | 수강 · 보정 | 003 · 004 |
| `user_groups` (`code`, `name`, `kind` tag/saved_group, `group_type`, `assign_method`, `axis`, `badge_color`, `eval_cycle`, `on_exit`, `share_scope`, `condition_json`, `member_count`, `last_synced_at`, `is_system`, `created_by`) | 태그 · 저장 그룹 | 006 |
| `user_group_members` (`user_id`, `user_group_id`, `assigned_by`) · `user_group_exclusions` | 소속 · 자동 태그 제외 | 006 |

## 6. 개발 JS · 마크업 이름
| 개발 id | 역할 | 프로토타입 대응 id |
|---|---|---|
| `memberSearchForm` | 001 검색 폼 | (form 없음, `#view-list` 필터 표) |
| `dateFrom` · `dateTo` | 가입일 | 날짜 input(id 없음) |
| `checkAll` · `.member-check` · `selectedCount` | 전체 선택 · 행 체크 · 선택 수 | `toggleAllRows()` |
| `assignTagButton` · `campaignButton` | 선택 회원 태그 · 메시지 | `openBulkTagModal()` · `sendBulkMsg()` 버튼 |
| `layerMemberDownload` · `memberDownloadForm` · `memberDownloadFields` · `memberDownloadReason` · `memberDownloadEtc` · `memberDownloadRef` · `memberDownloadSubmit` · `memberDownloadDone` | 001-P1 | `modal-excel-p1` · `#ex-cols-block` · `#excel-reason` · `#btn-excel-submit` |
| `layerMemberStatus` | 002 상태 변경 | `modal-status` |
| `layerPointGrant` · `pointGrantForm` | 002-P1 | `modal-point-p1` |
| `layerSocialUnlink` · `socialUnlinkForm` · `socialUnlinkReason` | 002-P2 | `modal-social` · `#social-reason` |
| `layerCourseExtend` · `courseExtendForm` · `layerCoursePause` · `coursePauseForm` · `layerCourseResume` · `courseResumeForm` | 003 | `view-course` 조정 패널(모달 아님) |
| `progressAdjustForm` · `adjustReasonCode` · `adjustReasonText` · `refundAfterRate` · `refundImpact` · `progressAdjustSubmit` | 004-P1 | `modalProgressAdjust` · `#m3f-pa-*` |
| `layerSanctionRelease` · `sanctionReleaseForm` | 005 해제 | `modal-bl-release` |
| `groupBulkForm` · `groupBulkSummary` · `groupUploadForm` | 006 일괄 처리 | `view-tags` 일괄 패널 `#m3f-bk-*` · `modalBulkTagConfirm` |
| `tagForm` · `tagAssignMethod` · `tagAutoBlock` · `tagConditionRows` · `tagConditionAdd` · `tagPreviewButton` · `tagPreviewCount` · `tagPreviewList` | 006-S1 | `#m3f-tc-*` · `modalTagCond` |
| `savedGroupPreview` · `savedGroupPreviewToggle` | 006-S2 | `modalGroupSave` |

마크업 공통: 모달 `.layer` + `id="layer…"`, 폼 `method="post"` + `@method('PUT'\|'DELETE')`, 입력 `.input__text` · `.select`, 버튼 `.btn__small` · `.btn__system` + `.btn--basic` · `.btn--del`, 링크 `.link--view`, 마스킹 컴포넌트 `<x-masked type= target-type= target-id= field= level=>`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 002-P1 포인트 만료일 직접 지정(`expire_preset=custom` + `expire_date`) — 정책 질문 Q-USER-23(정본은 30 · 90 · 180일만)
- 002 쿠폰 회수(`admin.members.coupons.update`) — 상세 쿠폰 목록 행 버튼
- 002 응시 예정(관심 자격) 수정 `exam_target_ids[]`
- 003 사유 코드 `reason_code` 6종, 일시정지 무기한 `indefinite`, 일시정지 해제(resume) 별도 동작
- 004-P1 사유 코드 4종 · `reason_text` · 근거 파일 1~5개 · 보정 이력 화면, 환급 영향 미리보기(`refundImpact`)
- 005 정지 기간 권장값 자동 선택(누적 1회 7 · 2회 30 · 3회 이상 영구), 위반 유형 5종(`concurrent_session` 포함)
- 006-S1 태그 축(`axis`) · 배지 색(`badge_color`) · 대상 미리보기(인원 + 마스킹 명단)
- 006 엑셀 명단 매칭 후 미매칭 명단 다운로드

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 001 · 002 회원번호 · 산준모 카페 ID 검색 · 표시 · 수정(DB `cafe_id`는 있음)
- 002 CS 상담 이력 타임라인(일시 · 담당자 · 채널 · 처리 결과 4종 · 이관 부서) — 개발은 `admin_memo` 1칸. 규칙 기반 이름: 상담 내용 `content` (규칙, 10~1,000자) · 처리 결과 메모 `result_note` (규칙, 200자)
- 002 임시 비밀번호 메일 · 비밀번호 수동 초기화 · 5회 잠금 해제
- 002-P3 1:1 메시지(알림톡 · SMS · 이메일) 즉시 발송
- 002 마스킹 해제 사유 10자 · 재마스킹 남은 시간 배지 · 즉시 재마스킹(설정값 `remaskMemberSec` 600초)
- 002-P1 지급 알림톡 옵션 · 조작 후 예상 잔액 · 1회 30,000P · 무상 보유 상한(검토 #7)
- 003 종료일 단축 · 일시정지 3회 · 통산 30일 상한 · 세션 강제 로그아웃 · 기기 리셋 · DRM 만료일 동기화
- 004 보정 포함 배지 · 회원 단위 보정 원장
- 005 마이너스 부채 자동 등재 · 관리자 강제 탈퇴 · 제재 범위 · 모니터링 경고 단계
- 006 태그 · 그룹 코드 컬럼 · 연동 액션(쿠폰 · 메시지) · 조건 항목 약 20종(개발 5종) · 조건 결과 전체 일괄 부여 · 1만 건 초과 백그라운드 · 시스템 태그 자동 전환
- 006-S2 저장 그룹 수정 · 삭제 · 발송/쿠폰 연결
- 006-S3 처리 결과 · 재처리 · 처리 단위 해제 · 결과 엑셀

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 적립 P | 유상 P (`paid_point`) — 화면 라벨은 정본 '적립 P' 유지, 값 키만 개발 |
| 회원 상태 정상 · 휴면 · 정지(BL) | `active` · `dormant` · 파생 `suspended`(`is_locked`) |
| `pt_mode` PLUS · MINUS | `direction` grant · deduct |
| `adj_type` EXTEND · SHORTEN · PAUSE | 라우트 extend · (없음) · pause |
| `m3f-bk-action` ADD · REMOVE | `action` assign · remove |
| `m3f-bk-scope` CHECKED · COND · EXCEL | `scope` selected · filter · upload |
| `m3f-tc-type` AUTO · MANUAL | `assign_method` auto · manual |
| `m3f-grp-mode` DYNAMIC · STATIC | `group_type` dynamic · static |
| `m3f-grp-share` ALL · MINE | `share_scope` all · owner |
| `m3f-grp-op` AND · OR | `tag_join` and · or |
| 계약번호(수강) | 주문번호 기준 `user_courses.id` |

## 8. 정책 질문
회원관리 정책 판단 23건은 `scripts/qa/reports/review/findings/member/회원관리_개발검토_종합.md` 4절에 있다(#1 결정됨). 이 화면 작업에서 새로 생긴 질문은 없다. 정책 큐(`findings/POLICY_QUEUE.md`)로 옮길 때는 그 문서 번호를 그대로 쓴다.

- 관리자 사유 입력 200자 상한(개발에만 있음)을 정본에 넣을지(정책 큐 M-04). **→ 결정(v6.92 white, M-04)**: 짧은 사유 10~200자 공통 규칙, 서술형 칸(CS 상담 내용 · 블랙리스트 상세 경위)은 1,000자.
