# 테이블 · 컬럼 색인 (마이그레이션 누적)

타입 뒤 인자 · nullable 등 플래그 · 주석 · 마지막으로 바꾼 마이그레이션.

## users
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `login_id` | string(50) | nullable,change | 관리자 로그인 아이디. 일반 회원은 email을 아이디로 사용하므로 NULL | 2026_08_14_000046 |
| `name` | string(50) | nullable,change | 회원 이름 | 2026_07_23_000003 |
| `phone` | string(20) | nullable,change | 휴대폰 번호. 하이픈 제거 저장 | 2026_07_23_000003 |
| `email` | string(100) | nullable,unique | 이메일 주소 | 2026_06_25_000001 |
| `password` | string(255) | nullable | 해시 비밀번호. 소셜 전용 회원은 NULL 가능 | 2026_06_25_000001 |
| `address` | string(255) | nullable | 기본 배송지 주소 | 2026_06_25_000001 |
| `address_detail` | string(100) | nullable | 기본 배송지 상세주소 | 2026_06_25_000001 |
| `role` | string(20) |  | user / instructor / admin 등 계정 유형 | 2026_06_25_000001 |
| `is_verified` | tinyInteger |  | 본인인증 완료 여부 | 2026_06_25_000001 |
| `login_fail_count` | unsignedTinyInteger |  | 로그인 연속 실패 횟수 | 2026_06_25_000001 |
| `is_locked` | boolean | change | 로그인 차단 여부. 로그인 5회 실패 자동 잠금 및 관리자 정지 공용 | 2026_08_14_000035 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000001 |
| `status` | string(20) | change | active=정상 / dormant=휴면 / withdrawn=탈퇴. 정지는 is_locked로 관리 | 2026_08_14_000035 |
| `birth_date` | date | nullable | 생년월일. 본인인증 수취값 | 2026_08_14_000029 |
| `gender` | string(10) | nullable | male / female. 본인인증 수취값 | 2026_08_14_000029 |
| `cafe_id` | string(100) | nullable | 산준모 네이버 카페 ID. 선택 입력, 형식 검사 없음 | 2026_08_14_000029 |
| `locked_until` | timestamp | nullable,change | 자동 해제 예정 시각. 영구 잠금이면 NULL. 해제 가능 여부는 lock_reason으로 판정 | 2026_08_14_000040 |
| `lock_reason` | string(20) | nullable | 잠금 사유. auto_5fail=로그인 5회 실패(재설정 시 해제) / admin_block=관리자 정지(해제 불가). NULL이면 미잠금 | 2026_08_14_000040 |
| `marketing_agreed_at` | timestamp | nullable | 마케팅 수신 동의 또는 철회 일시. 발송 시 동의 시점 증빙용 | 2026_08_14_000044 |
| `last_login_at` | timestamp | nullable | 최종 로그인 일시. 휴면 전환 판정 및 회원 목록 검색·정렬용 | 2026_08_14_000044 |
| `di_hash` | string(64) | nullable,unique | 본인인증 DI의 SHA-256 해시. 탈퇴 시 NULL 파기. 중복가입 차단 및 명의 대조용. | 2026_09_07_000051 |
| `join_method` | string(20) |  | 가입 유입 채널. email / naver / kakao / google. | 2026_09_07_000059 |
| `is_marketing_agreed` | boolean |  | 마케팅 정보 수신 동의 여부. 이메일·SMS·알림톡 통합 단일 값. | 2026_09_07_000059 |
| `must_change_password` | boolean |  | 첫 로그인 시 비밀번호 변경 강제 여부. 기본값 0. | 2026_09_08_000095 |
| `unsub_token` | string(32) | nullable | 광고 수신거부 링크 토큰. 정보통신망법 제50조 무료 거부 수단. | 2026_09_08_000095 |
| `total_points` | integer |  | 포인트 잔액 캐시. 무상 + 유상 합계. 환불 시 선사용 혜택 보전 공제로 마이너스가 될 수 있으며 0P 미만이면 포인트 사용과 회원탈퇴가 차단된다. | 2026_09_08_000105 |
| `password_changed_at` | dateTime | nullable | 비밀번호 마지막 변경 일시. 관리자 90일 주기 변경 강제 판정 기준(admin.password_max_age_days). 회원은 NULL | 2026_09_28_000164 |
| `verify_cap_reset_at` | dateTime | nullable | 인증번호 발송 횟수 수동 초기화 시각. 이 시각 이전 발송은 한도 계산에서 제외한다(ADMN-CONF-005). NULL 이면 초기화 이력 없음 | 2026_09_28_000165 |
| `admin_memo` | text | nullable | 관리자 내부 메모. 회원 비노출. 수정 전 내용은 user_change_logs(field=admin_memo) | 2026_09_28_000166 |

## exam_targets
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `name` | string(100) |  | 응시예정 명칭 | 2026_06_25_000001 |
| `code` | string(50) | unique | 응시예정 고유 코드 | 2026_06_25_000001 |
| `sort_order` | integer |  | 노출 순서 | 2026_06_25_000001 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_06_25_000001 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000001 |
| `type` | string(20) |  | 구분. license=종목, subject=과목, course=과정, exam=응시예정 | 2026_07_08_200001 |

## user_exam_targets
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000001 |
| `exam_target_id` | foreignId |  | exam_targets.id 참조 | 2026_06_25_000001 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |

## social_accounts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000001 |
| `provider` | string(30) |  | naver / kakao / google 등 제공자 | 2026_06_25_000001 |
| `provider_id` | string(100) |  | 소셜 플랫폼 사용자 ID | 2026_06_25_000001 |
| `provider_token` | text | nullable | 소셜 액세스 토큰 | 2026_06_25_000001 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |

## identity_verifications
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `user_id` | foreignId | nullable | users.id 참조. 가입 전 인증 시 NULL 가능 | 2026_06_25_000001 |
| `imp_uid` | string(100) |  | 인증 거래 고유번호 | 2026_06_25_000001 |
| `name` | string(50) |  | 인증된 실명 | 2026_06_25_000001 |
| `phone` | string(20) |  | 인증된 휴대폰 번호 | 2026_06_25_000001 |
| `ci` | string(255) | nullable | 연계정보. 암호화 저장 권장 | 2026_06_25_000001 |
| `di` | string(255) | nullable | 중복가입확인정보. 암호화 저장 권장 | 2026_06_25_000001 |
| `verified_at` | timestamp |  | 인증 완료 일시 | 2026_06_25_000001 |
| `birth_date` | date | nullable | 인증된 생년월일 | 2026_08_14_000030 |
| `gender` | string(10) | nullable | 인증된 성별. male / female | 2026_08_14_000030 |
| `verification_type` | string(30) |  | join=회원가입 / course=수강시작 / find=계정찾기 / etc | 2026_08_14_000030 |

## sms_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `phone` | string(20) |  | 수신 휴대폰 번호 | 2026_06_25_000001 |
| `type` | string(30) |  | 가입/비번찾기/전화번호변경 등 발송 용도 | 2026_06_25_000001 |
| `expires_at` | timestamp |  | 만료 일시 | 2026_06_25_000001 |
| `verified_at` | timestamp | nullable | 인증 완료 일시 | 2026_06_25_000001 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |
| `ip` | string(45) | nullable | 발송 요청 IP. 동일 IP 기준 발송 횟수 제한 판정에 사용 | 2026_08_14_000047 |
| `code_hash` | string(255) |  | 인증번호 해시. 평문 저장 금지. | 2026_09_07_000048 |
| `attempt_count` | unsignedTinyInteger |  | 인증번호 검증 시도 횟수. 임계치 초과 시 세션 무효화. | 2026_09_07_000048 |
| `invalidated_at` | timestamp | nullable | 인증 세션 폐기 일시. 재발송 시 이전 행, 검증 성공 시 당해 행. | 2026_09_07_000048 |

## login_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000001 |
| `user_id` | foreignId | nullable | users.id 참조 | 2026_06_25_000001 |
| `ip` | string(45) |  | 접속 IP | 2026_06_25_000001 |
| `user_agent` | string(500) | nullable | 브라우저/기기 정보 | 2026_06_25_000001 |
| `status` | string(20) |  | success / fail | 2026_06_25_000001 |
| `fail_reason` | string(100) | nullable | 실패 사유 | 2026_06_25_000001 |
| `created_at` | timestamp |  |  | 2026_06_25_000001 |
| `event` | string(30) |  | LOGIN_SUCCESS / LOGIN_FAIL / ACCOUNT_LOCKED / ACCOUNT_UNLOCKED / PASSWORD_RESET / IP_DENIED / TOKEN_REUSE | 2026_08_14_000045 |
| `country` | char(2) | nullable | ISO 3166-1 alpha-2 국가코드 | 2026_08_14_000045 |
| `fail_count` | tinyInteger |  | 해당 시점의 누적 로그인 실패 횟수 | 2026_08_14_000045 |
| `login_id` | string(50) | nullable | 시도한 아이디 원문. 존재하지 않는 계정 시도는 user_id 가 NULL 이라 이 값이 유일한 단서다. 계정명 사전 공격 탐지에 쓴다 | 2026_09_10_000106 |
| `detail` | json | nullable | 이벤트 부가 정보. ACCOUNT_LOCKED 는 직전 실패 시도 스냅샷(created_at · ip · user_agent) 배열을 담는다. 다른 이벤트는 NULL | 2026_09_28_000166 |

## instructors
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `user_id` | unsignedBigInteger | nullable,change | users.id 참조 | 2026_07_07_200000 |
| `name` | string(50) |  | 강사명 | 2026_06_25_000002 |
| `bio` | text | nullable | 강사 소개 | 2026_06_25_000002 |
| `profile_image` | string(255) | nullable | 프로필 이미지 경로 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `intro_lecture_id` | foreignId | nullable |  | 2026_07_24_100000 |
| `tax_type` | string(20) | nullable | personal=인적용역 3.3% / business=사업자 10% | 2026_08_14_000031 |
| `business_number` | string(30) | nullable | 사업자등록번호. tax_type=business 인 경우 | 2026_08_14_000031 |
| `bank_name` | string(50) | nullable | 정산 입금 은행 | 2026_08_14_000031 |
| `account_no` | string(255) | nullable | 정산 계좌번호. 암호화 저장 | 2026_08_14_000031 |
| `account_holder` | string(50) | nullable | 예금주 | 2026_08_14_000031 |
| `code` | string(20) | nullable,unique | 강사 코드. INST-000012 형식 자동 채번. 등록 후 변경 불가. | 2026_09_07_000062 |
| `birth_date` | date | nullable | 생년월일. 실명과 조합해 고유 식별. 목록 검색 키. | 2026_09_07_000062 |
| `phone` | string(20) | nullable | 휴대전화 번호. 식별 보조 및 뒤 4자리 검색. | 2026_09_07_000062 |
| `email` | string(100) | nullable | 일반 연락용 이메일. | 2026_09_07_000062 |
| `tax_email` | string(100) | nullable | 세금계산서·계산서 수취 전용 이메일. 사업자 유형 시 필수. | 2026_09_07_000062 |
| `slug` | string(100) | nullable,unique | 강사홈 URL 슬러그. /instructor/{slug} 라우팅 및 강좌 목록 필터. | 2026_09_07_000062 |
| `instructor_type` | string(10) |  | 강사 구분. main=정강사 / sub=부강사. 표시·통계용이며 요율은 계약이 결정한다. | 2026_09_07_000062 |
| `rights_holder_id` | foreignId | nullable | 정산 주체. rights_holders.id. NULL 이면 전시 전용 강사다 | 2026_09_15_000114 |

## lectures
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `code` | string(50) | unique | 강의 고유 코드 | 2026_06_25_000002 |
| `title` | string(255) |  | 강의 제목 | 2026_06_25_000002 |
| `instructor_id` | foreignId |  | instructors.id 참조 | 2026_06_25_000002 |
| `year` | smallInteger | nullable | 제작/대상 연도 | 2026_06_25_000002 |
| `cdn_key` | string(255) | nullable | CDN 영상 키 | 2026_06_25_000002 |
| `duration_sec` | unsignedInteger |  | 영상 길이(초) | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `source_type` | string(20) |  |  | 2026_07_08_100001 |
| `source_url` | string(500) | nullable |  | 2026_07_08_100001 |
| `exam_target_id` | unsignedBigInteger | nullable | exam_targets.id 참조. type=subject인 과목. | 2026_07_08_200002 |
| `type` | string(20) |  |  | 2026_07_24_100000 |
| `is_preview` | boolean |  | 맛보기 공개 여부. 비회원 재생 허용. DRM·워터마크 미적용. | 2026_09_07_000064 |
| `category_id` | unsignedBigInteger | nullable | 노출 분류. categories.id 참조. ADMN-PROD-002 등록 폼의 카테고리 셀렉트 값이며 2Depth(과정 분류)를 선택한다. 무료강의 목록(USER-FREE-001)의 자격증 탭 필터에도 쓰인다. | 2026_09_08_000092 |
| `vod_verified_at` | timestamp | nullable | VOD Key 유효성 검사 시각. StarPlayer+ API 로 Key 존재·재생 가능 여부·러닝타임을 조회한 시점이다. 값이 없으면 등록만 하고 확인하지 않은 강의다. | 2026_09_08_000092 |
| `view_count` | unsignedInteger |  | 조회수. 무료강의 목록(USER-FREE-001) 카드 표기 및 조회 많은 순 정렬에 사용한다. 비회원 재생이 허용되므로 세션 기준 중복 집계를 코드에서 차단한다. | 2026_09_08_000092 |
| `is_active` | tinyInteger |  | 사용 여부. 0이면 신규 커리큘럼 편성 후보에서 제외한다. 이미 편성된 강좌에서 자동으로 빠지지는 않으며 커리큘럼 화면에 경고만 띄운다. 자동 제거는 수강생 커리큘럼을 흔든다. 실무에서 필요한 동작은 삭제가 아니라 이 전환이다. 기본값 1. | 2026_09_08_000092 |
| `drm_content_id` | string(100) | nullable | StarPlayer+ 멀티DRM 콘텐츠 ID(OVP drm_content_id). cdn_key 와 별개 | 2026_10_07_000199 |

## courses
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `code` | string(50) | unique | 강좌 코드 | 2026_06_25_000002 |
| `title` | string(255) |  | 강좌명 | 2026_06_25_000002 |
| `instructor_id` | foreignId |  | 대표 강사 ID | 2026_06_25_000002 |
| `duration_days` | integer |  | 수강 가능 일수 | 2026_06_25_000002 |
| `original_price` | integer |  | 정가 | 2026_06_25_000002 |
| `sale_price` | integer |  | 판매가 | 2026_06_25_000002 |
| `is_public` | tinyInteger |  | 사용자 페이지 공개 여부 | 2026_06_25_000002 |
| `is_featured` | tinyInteger |  | 추천/주요 강좌 여부 | 2026_06_25_000002 |
| `thumbnail_path` | string(255) | nullable | 썸네일 경로 | 2026_06_25_000002 |
| `description` | text | nullable | 상세 설명 | 2026_06_25_000002 |
| `target_audience` | text | nullable | 수강 대상 설명 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `exam_target_id` | unsignedBigInteger | nullable | exam_targets.id 참조. 과정(필기/실기) 매핑. | 2026_07_10_210000 |
| `content` | text | nullable | 내용 및 특징. 강좌 상세 페이지 본문. | 2026_07_23_000005 |
| `cost_price` | unsignedInteger | nullable | 원가 (매입/제작 원가) | 2026_07_23_000004 |
| `intro_lecture_id` | foreignId | nullable |  | 2026_07_24_100000 |
| `sample_lecture_id` | foreignId | nullable |  | 2026_07_24_100000 |
| `tax_type` | string(10) |  | 과세 구분. exempt=면세 고정. 학원법상 교육용역. | 2026_09_07_000067 |
| `allow_coupon` | boolean |  | 쿠폰 적용 허용 여부. | 2026_09_07_000067 |
| `allow_point` | boolean |  | 포인트 사용 허용 여부. | 2026_09_07_000067 |
| `start_type` | string(20) |  | 수강 시작 기준. immediate=결제 승인 즉시 / scheduled=지정일 시작(사전판매). | 2026_09_07_000067 |
| `start_date` | date | nullable | 수강 시작 지정일. start_type=scheduled일 때만 사용. | 2026_09_07_000067 |

## course_lectures
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000002 |
| `lecture_id` | foreignId |  | lectures.id 참조 | 2026_06_25_000002 |
| `sort_order` | integer |  | 강좌 내 차시 순서 | 2026_06_25_000002 |

## packages
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `code` | string(50) | unique | 패키지 코드 | 2026_06_25_000002 |
| `title` | string(255) |  | 패키지명 | 2026_06_25_000002 |
| `duration_days` | integer |  | 수강 가능 일수 | 2026_06_25_000002 |
| `original_price` | integer |  | 정가 | 2026_06_25_000002 |
| `sale_price` | integer |  | 판매가 | 2026_06_25_000002 |
| `is_public` | tinyInteger |  | 공개 여부 | 2026_06_25_000002 |
| `thumbnail_path` | string(255) | nullable | 썸네일 경로 | 2026_06_25_000002 |
| `description` | text | nullable | 상세 설명 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `is_pass_refund` | boolean |  | 합격 환급 대상 패키지. 체크하지 않으면 환급 신청 버튼이 뜨지 않는다 | 2026_09_30_000180 |
| `refund_min_progress` | unsignedTinyInteger | nullable | 합격 환급 인정 진도율(%). 패키지 단위(PO 2026-09-22). 입력 기본값만 site_settings.refund_claim_min_progress | 2026_09_30_000180 |

## books
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `code` | string(50) | unique | 교재 코드 | 2026_06_25_000002 |
| `isbn` | string(30) | nullable,unique | ISBN | 2026_06_25_000002 |
| `title` | string(255) |  | 교재명 | 2026_06_25_000002 |
| `author` | string(100) | nullable | 저자 | 2026_06_25_000002 |
| `publisher` | string(100) | nullable | 출판사 | 2026_06_25_000002 |
| `original_price` | integer |  | 정가 | 2026_06_25_000002 |
| `sale_price` | integer |  | 판매가 | 2026_06_25_000002 |
| `stock` | integer |  | 현재 재고 | 2026_06_25_000002 |
| `page_count` | integer | nullable | 페이지 수 | 2026_06_25_000002 |
| `description` | text | nullable | 교재 설명 | 2026_06_25_000002 |
| `table_of_contents` | text | nullable | 목차 | 2026_06_25_000002 |
| `thumbnail_path` | string(255) | nullable | 썸네일 경로 | 2026_06_25_000002 |
| `is_public` | tinyInteger |  | 공개 여부 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `cost_price` | integer | nullable | 매입 원가 | 2026_07_10_000012 |
| `delivery_fee` | integer | nullable | 개별 배송비. NULL이면 site_settings 기본값 적용 | 2026_08_14_000033 |
| `is_free_delivery` | boolean |  | 금액 조건과 무관하게 항상 무료배송 | 2026_08_14_000033 |
| `return_delivery_fee` | integer | nullable | 교재별 반품 왕복 배송비. NULL이면 site_settings 기본값 적용 | 2026_08_14_000038 |
| `published_at` | date | nullable | 발행일. 목록 검색 조건 및 개정판 구분에 사용. | 2026_09_07_000068 |
| `edition` | string(30) | nullable | 판·쇄 정보. 예: 3판 2쇄. | 2026_09_07_000068 |
| `is_free` | boolean |  | 무료 도서 여부. 1이면 가격 관련 값이 모두 0이며 도서정가제 대상 제외. | 2026_09_07_000068 |
| `free_delivery_threshold` | integer | nullable | 조건부 무료배송 기준 금액. 교재 합계가 이 값 이상이면 배송비 0원. NULL이면 미적용. | 2026_09_07_000068 |
| `island_delivery_fee` | integer | nullable | 도서산간 추가 배송비. 주소 판정으로 자동 가산. NULL이면 site_settings 값 적용. | 2026_09_07_000068 |
| `stock_alert_qty` | integer | nullable | 품절 임박 기준 수량. 재고가 이 값 이하면 대시보드에 알림. | 2026_09_07_000068 |
| `is_preorder` | boolean |  | 예약 판매 여부. 1이면 3PL 발주 대상에서 제외한다. | 2026_09_07_000068 |
| `release_date` | date | nullable | 출간 예정일. 예약 판매 시 발송 시작 기준. | 2026_09_07_000068 |
| `book_size` | string(30) | nullable | 판형. 4x6배판 등. 화면 "페이지/판형" 표기값. | 2026_09_08_000100 |
| `restock_date` | date | nullable | 재입고 예정일. 품절 시 화면에 "(예정)" 을 붙여 노출한다. 미입력 시 문장 생략. | 2026_09_08_000100 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000100 |
| `book_supply_type` | string(20) | nullable | 공급 형태. OWN_PUBLISHED=자사 발행 / PURCHASED_RESALE=매입 재판매 / CONSIGNMENT=위탁 / BUNDLED=부속·사은품 (합의서 6.1) | 2026_09_18_000127 |
| `settlement_required_yn` | boolean |  | 정산 대상 여부. book_supply_type 파생값 — OWN_PUBLISHED·CONSIGNMENT 는 1. 지분 100% 하드락도 이 값이 1인 도서에만 건다 | 2026_09_18_000127 |
| `cost_account_type` | string(30) | nullable | 원가 계정. BUYOUT_RIGHT=무형 판권 취득 / INVENTORY_PURCHASE=재고자산 취득 (합의서 6.1) | 2026_09_18_000127 |
| `supplier_id` | unsignedBigInteger | nullable | 매입처 suppliers.id. 매입 재판매·위탁 도서의 AP 경로 연결 | 2026_09_18_000127 |
| `own_copyright_yn` | boolean |  | 자사 권리 보유 여부. true 면 자사 권리자 100% 자동 매핑 · 외부 지급 없음 (합의서 6.1) | 2026_09_19_000144 |
| `package_bundled_yn` | boolean |  | 패키지 동봉 여부. 1이면 패키지 구성품으로 팔릴 때도 이 교재의 배송 정책을 동일 적용한다 (설계서 ADMN-PROD-004-S1 ④) | 2026_10_13_000205 |

## course_books
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000002 |
| `book_id` | foreignId |  | books.id 참조 | 2026_06_25_000002 |
| `book_type` | string(20) | nullable | 주교재/부교재 구분. main / sub | 2026_06_25_000002 |
| `sort_order` | integer |  | 부교재 복수 시 노출 순서 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |

## package_instructors
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `package_id` | foreignId |  | packages.id 참조 | 2026_06_25_000002 |
| `instructor_id` | foreignId |  | instructors.id 참조 | 2026_06_25_000002 |
| `is_main` | tinyInteger |  | 주강사 여부. 1=주강사, 0=참여강사 | 2026_06_25_000002 |
| `settlement_rate` | decimal(5, 2) | nullable | 패키지별 강사 요율. NULL이면 instructors.settlement_rate 적용 | 2026_06_25_000002 |
| `sort_order` | integer |  | 노출 순서 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |

## product_badges
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `product_type` | string(20) |  | course / package | 2026_06_25_000002 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_06_25_000002 |
| `badge_slot` | unsignedTinyInteger |  | 배지 슬롯. 1=강조1, 2=강조2 | 2026_06_25_000002 |
| `badge_type` | string(20) |  | hot/new/best/event/completed/update | 2026_06_25_000002 |
| `is_active` | tinyInteger |  | 노출 여부 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000002 |

## book_stock_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `book_id` | foreignId |  | books.id 참조 | 2026_06_25_000002 |
| `type` | string(30) |  | 입고/출고/복구/조정 등 | 2026_06_25_000002 |
| `quantity` | integer |  | 변동 수량 | 2026_06_25_000002 |
| `before_stock` | integer |  | 변동 전 재고 | 2026_06_25_000002 |
| `after_stock` | integer |  | 변동 후 재고 | 2026_06_25_000002 |
| `order_id` | unsignedBigInteger | nullable | 관련 주문 ID | 2026_06_25_000002 |
| `order_item_id` | unsignedBigInteger | nullable | 관련 주문상품 ID | 2026_06_25_000002 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 ID | 2026_06_25_000002 |
| `memo` | text | nullable | 메모 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |

## product_search_keywords
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000002 |
| `product_type` | string(20) |  | course / package / book | 2026_06_25_000002 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_06_25_000002 |
| `keyword` | string(100) |  | 검색 키워드 | 2026_06_25_000002 |
| `created_at` | timestamp |  |  | 2026_06_25_000002 |
| `source_type` | string(30) |  | title / instructor / exam_target / category / book / course / publisher | 2026_08_14_000027 |
| `weight` | integer |  | 검색 우선순위 가중치 | 2026_08_14_000027 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000027 |

## categories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `parent_id` | unsignedBigInteger | nullable | 상위 카테고리 ID. 최상위는 NULL | 2026_06_25_000003 |
| `name` | string(100) |  | 카테고리명 | 2026_06_25_000003 |
| `slug` | string(100) | nullable | URL/검색용 식별값 | 2026_06_25_000003 |
| `depth` | unsignedTinyInteger |  | 카테고리 깊이. 1=대분류, 2=중분류, 3=소분류 | 2026_06_25_000003 |
| `sort_order` | integer |  | 동일 parent_id 내 노출 순서 | 2026_06_25_000003 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `code` | string(50) | nullable,unique | 카테고리 코드. 영문 대문자+언더스코어. 최초 저장 시 자동 채번 후 수정 불가. | 2026_09_07_000066 |
| `is_default` | boolean |  | 1Depth 기본 종목 여부. 프론트 첫 진입 시 기본 선택되며 삭제 불가. | 2026_09_07_000066 |

## category_products
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `category_id` | foreignId |  | categories.id 참조 | 2026_06_25_000003 |
| `product_type` | string(20) |  | 상품 유형. course / package / book | 2026_06_25_000003 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_06_25_000003 |
| `sort_order` | integer |  | 해당 카테고리 내 상품 노출 순서 | 2026_06_25_000003 |
| `is_primary` | tinyInteger |  | 대표 카테고리 여부 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |

## user_courses
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000003 |
| `order_item_id` | unsignedBigInteger | nullable | order_items.id 참조 | 2026_06_25_000003 |
| `status` | string(20) |  | active / expired / paused | 2026_06_25_000003 |
| `started_at` | timestamp | nullable | 수강 시작 일시 | 2026_06_25_000003 |
| `expires_at` | timestamp | nullable | 수강 만료 일시 | 2026_06_25_000003 |
| `pause_remaining_days` | integer | nullable | 남은 일시정지 가능 일수 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `order_id` | unsignedBigInteger | nullable | orders.id 참조. 주문 단위 조회용 비정규화 | 2026_08_14_000025 |
| `package_id` | unsignedBigInteger | nullable | 패키지 구매 시 원 패키지 ID. FK 아님 | 2026_08_14_000025 |
| `pause_count_left` | integer | nullable | 남은 일시정지 가능 횟수 | 2026_08_14_000025 |
| `progress_rate` | decimal(5, 2) |  | 강좌 진도율(%). 수강완료 인정 차시 수 / 전체 차시 수. 차시 인정 여부가 바뀐 시점에만 갱신한다. 10초 주기 재생 로그마다 갱신하지 않는다. | 2026_09_08_000103 |
| `completed_lecture_count` | unsignedSmallInteger |  | 수강완료 인정 차시 수. 화면 표기 "15/24차시" 의 분자. | 2026_09_08_000103 |
| `total_lecture_count` | unsignedSmallInteger |  | 전체 차시 수. 수강 시작 시점 스냅샷. 차시 증감으로 기존 수강생 진도율이 소급 변동하는 것을 막는다. | 2026_09_08_000103 |
| `last_watched_at` | timestamp | nullable | 마지막 학습 일시. 이어보기 퀵위젯 정렬 키. | 2026_09_08_000103 |
| `extended_days` | integer |  | 관리자 연장 누적 일수. 연장 상한(원 수강일수 1배) 판정 기준. 정지 순연분은 포함하지 않는다 | 2026_10_19_000220 |
| `paused_at` | timestamp | nullable | 일시정지 시작 일시. NULL = 정지 중 아님. 해제 시 이 시각부터 센 일수만큼 expires_at 을 순연한다 | 2026_10_19_000220 |

## lecture_progresses
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000003 |
| `lecture_id` | foreignId |  | lectures.id 참조 | 2026_06_25_000003 |
| `last_position_sec` | unsignedInteger |  | 마지막 재생 위치(초) | 2026_06_25_000003 |
| `max_position_sec` | unsignedInteger |  | 최대 시청 위치(초) | 2026_06_25_000003 |
| `is_completed` | tinyInteger |  | 수강 완료 여부 | 2026_06_25_000003 |
| `completed_at` | timestamp | nullable | 완료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `user_course_id` | unsignedBigInteger | nullable | user_courses.id 참조. 수강권한 단위 집계용 | 2026_08_14_000024 |
| `watched_seconds` | integer |  | 인정 시청 시간(초). 이수 판정 기준 | 2026_08_14_000024 |
| `total_play_sec` | integer |  | 총 재생 시간(초). 반복 재생 포함 | 2026_08_14_000024 |
| `play_count` | integer |  | 재생 횟수 | 2026_08_14_000024 |
| `duration_sec` | integer |  | 강의 길이 스냅샷(초) | 2026_08_14_000024 |
| `last_watched_at` | timestamp | nullable | 마지막 시청 일시 | 2026_08_14_000024 |

## course_pause_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000003 |
| `user_course_id` | unsignedBigInteger |  | user_courses.id 참조 | 2026_06_25_000003 |
| `paused_at` | timestamp |  | 일시정지 시작 일시 | 2026_06_25_000003 |
| `resumed_at` | timestamp | nullable | 재개 일시 | 2026_06_25_000003 |
| `pause_days` | integer |  | 정지 일수 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger | nullable | 정지를 건 관리자 users.id. NULL = 배치 처리 또는 계정 삭제 | 2026_10_19_000220 |
| `reason_code` | string(30) | nullable | 정형 사유 — cs_compensation / device_issue / long_absence / event / correction / etc | 2026_10_19_000220 |
| `reason` | string(500) | nullable | 상세 사유 원문(10자 이상). 수정 불가 — 정정은 새 행으로 남긴다 | 2026_10_19_000220 |
| `is_indefinite` | tinyInteger |  | 무기한 정지 여부(군입대 등). 1 = 수동 해제만, scheduled_resume_at 없음 | 2026_10_19_000220 |
| `scheduled_resume_at` | timestamp | nullable | 자동 해제 예정 일시. 이 시각이 지나면 courses:resume-paused 가 해제한다 | 2026_10_19_000220 |

## orders
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_no` | string(50) | unique | 주문번호 | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `total_amount` | integer |  | 총 주문 금액 | 2026_06_25_000003 |
| `discount_amount` | integer |  | 할인 금액 | 2026_06_25_000003 |
| `mileage_used` | integer |  | 사용 마일리지 | 2026_06_25_000003 |
| `final_amount` | integer |  | 최종 결제 금액 | 2026_06_25_000003 |
| `status` | string(30) |  | pending / paid / cancelled / refunded 등 | 2026_06_25_000003 |
| `coupon_id` | unsignedBigInteger | nullable | coupons.id 참조 | 2026_06_25_000003 |
| `receiver_name` | string(50) | nullable | 수령인 이름 | 2026_06_25_000003 |
| `receiver_phone` | string(20) | nullable | 수령인 전화번호 | 2026_06_25_000003 |
| `receiver_address` | string(255) | nullable | 배송지 주소 | 2026_06_25_000003 |
| `receiver_address_detail` | string(100) | nullable | 배송지 상세주소 | 2026_06_25_000003 |
| `delivery_memo` | string(255) | nullable | 배송 메모 | 2026_06_25_000003 |
| `paid_at` | timestamp | nullable | 결제 완료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `delivery_fee` | integer |  | 배송비. 강사 정산 기준액에서 제외되므로 별도 보관 | 2026_08_14_000020 |
| `payment_method` | string(30) | nullable | 결제수단: card / vbank / trans 등 | 2026_08_14_000020 |
| `cancel_reason` | text | nullable | 주문 취소 사유 | 2026_08_14_000020 |
| `cancelled_at` | timestamp | nullable | 주문 취소 일시 | 2026_08_14_000020 |
| `order_token` | string(64) | nullable,unique | 주문 요청 토큰. 결제 이중 제출 방지용 멱등키 | 2026_08_14_000044 |
| `has_physical_item` | boolean |  | 실물 교재 포함 여부. 배송지 폼 노출 / 배송비 가산 / 결제 후 배송대기 트리거 3개가 이 값 하나로 결정된다. 강좌만 주문이면 0이며 배송 관련 요소를 DOM 에서 완전히 제거한다. | 2026_09_08_000104 |
| `course_amount` | integer |  | 강좌 라인 합계. 쿠폰·포인트 할인 적용 가능 금액의 기준이다. 교재 라인과 배송비는 이 금액에서 제외된다. | 2026_09_08_000104 |
| `book_amount` | integer |  | 교재 라인 합계. 도서정가제에 따라 쿠폰·포인트가 원천 차단되며 적립도 지급하지 않는다. 서버가 할인 가능액을 0원으로 락한다. | 2026_09_08_000104 |
| `earned_point` | integer |  | 적립 예정 포인트. 실결제액 x site_settings.point_earn_rate 올림. 유상 포인트로 적립되며 환불 시 LIFO 회수·부활 대상. | 2026_09_08_000104 |
| `exemption_basis` | string(20) | nullable | 면세 근거. EDU_SERVICE=교육용역(부가법 26①15) / BOOK_GOODS=도서 재화(26①8) / MIXED (합의서 8.1) | 2026_09_18_000135 |
| `receiver_zipcode` | string(5) | nullable | 수령지 우편번호. 주소 검색 결과. 도서산간 판정 · 3PL 발주 필수값 | 2026_09_30_000177 |

## order_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `product_type` | string(20) |  | course / package / book | 2026_06_25_000003 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_06_25_000003 |
| `product_name` | string(255) |  | 상품명 스냅샷 | 2026_06_25_000003 |
| `quantity` | integer |  | 수량 | 2026_06_25_000003 |
| `unit_price` | integer |  | 단가 | 2026_06_25_000003 |
| `discount_amount` | integer |  | 항목 할인 금액 | 2026_06_25_000003 |
| `final_price` | integer |  | 최종 금액 | 2026_06_25_000003 |
| `status` | string(30) |  | ordered / cancelled / refunded 등 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `instructor_name_snapshot` | string(100) | nullable | 구매 당시 강사명 스냅샷 | 2026_08_14_000021 |
| `course_days_snapshot` | integer | nullable | 구매 당시 수강기간(일) 스냅샷 | 2026_08_14_000021 |
| `original_price` | integer |  | 구매 당시 정가 | 2026_08_14_000021 |
| `sale_price` | integer |  | 구매 당시 판매가 | 2026_08_14_000021 |
| `refund_status` | string(20) |  | none / partial / full | 2026_08_14_000021 |
| `refunded_amount` | integer |  | 환불 누계금액 | 2026_08_14_000021 |
| `line_no` | unsignedInteger | nullable | 주문 내 라인 순번. 1부터 시작. 송장 벌크 업로드 매칭 키(주문번호 + 라인번호). | 2026_09_08_000077 |
| `cost_snapshot` | integer | nullable | 구매 당시 사입 원가 스냅샷. 교재 라인에만 값이 있다. 원가가 변경되어도 과거 주문의 손익이 소급 변동하지 않도록 고정 보관한다. ADMN-SETT-003 도서 매입 원가 정산의 기준값이다. | 2026_09_08_000092 |
| `item_type` | string(20) | nullable | 정산 인입 구분. LECTURE / BOOK / SHIPPING_FEE. product_type(상품 종류)과 축이 다르다 (합의서 8.1) | 2026_09_18_000135 |
| `book_supply_type_snapshot` | string(20) | nullable | 구매 시점 도서 공급 형태. 마스터를 조인하면 재연산 멱등성이 깨진다 (합의서 6.1) | 2026_09_18_000135 |
| `goods_supply_type_snapshot` | string(20) | nullable | 주문 시점 소비재 공급 형태. PURCHASED_RESALE / DIRECT_SALE. 재연산 멱등성 보존(§18.1) | 2026_09_22_000160 |
| `supply_type` | string(10) | nullable | 과·면세 1층 공급 유형. SERVICE=용역 / GOODS=재화 (§8.1) | 2026_09_22_000160 |
| `supply_category` | string(10) | nullable | 과·면세 2층 공급 카테고리. EDU=교육용역 / BOOK=도서 / GENERAL=일반 소비재 (§8.1) | 2026_09_22_000160 |
| `tax_treatment` | string(10) | nullable | 과·면세 3층 처리. EXEMPT=면세(EDU·BOOK) / TAXABLE=과세 10%(GENERAL). 2층에서 파생하되 판정 시점 값을 고정 보관한다(§8.1) | 2026_09_22_000160 |
| `package_id` | unsignedBigInteger | nullable | 패키지 구성품 라인이면 packages.id. 장바구니 분할 그룹 키를 그대로 옮긴다. FK 아님 | 2026_09_28_000168 |
| `coupon_discount` | integer |  | 이 라인에 배분된 쿠폰 할인. 강좌 정가 비율 안분(합의서 §8.1 · §13) | 2026_09_30_000180 |
| `point_discount` | integer |  | 이 라인에 배분된 포인트 사용액. discount_amount = coupon_discount + point_discount | 2026_09_30_000180 |
| `user_coupon_id` | unsignedBigInteger | nullable | 이 라인에 걸린 보유 쿠폰(user_coupons.id). 쿠폰은 상품마다 1장씩 여러 장 | 2026_09_30_000180 |
| `pass_refund_min_progress` | unsignedTinyInteger | nullable | 구매 시점 합격 환급 인정 진도율(%). 환급 대상 패키지의 강좌 라인에만. NULL = 환급 대상 아님 | 2026_09_30_000180 |
| `coupon_cap_applied` | boolean |  | 이 라인에 걸린 쿠폰의 감면액이 실감면 상한(Coupon::DISCOUNT_CAP)에 깎였는가. CS · 정산 대사용 | 2026_10_02_000183 |
| `course_lecture_count_snapshot` | unsignedInteger | nullable | 결제 시점 강좌 차시 수(환불 진도율 산식 분모). 강좌 라인만. NULL = 고정값 없음(수강권 차시 수 사용) | 2026_10_12_000202 |
| `promotion_id` | unsignedBigInteger | nullable | 기획전가로 팔린 라인의 기획전(promotions.id). 기획전 없이 산 라인은 NULL | 2026_10_15_000209 |

## payments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `imp_uid` | string(100) | nullable,change | [레거시] 포트원 거래 고유번호 | 2026_08_14_000023 |
| `merchant_uid` | string(100) | nullable,change | [레거시] 가맹점 주문번호 | 2026_08_14_000023 |
| `pay_method` | string(30) | nullable,change | [레거시] card / vbank / trans / phone | 2026_08_14_000023 |
| `pg_provider` | string(50) | nullable | PG사 | 2026_06_25_000003 |
| `amount` | integer |  | 결제 금액 | 2026_06_25_000003 |
| `status` | string(30) |  | ready / paid / cancelled / failed 등 | 2026_06_25_000003 |
| `card_name` | string(50) | nullable | 카드사명 | 2026_06_25_000003 |
| `card_number` | string(30) | nullable | 카드번호 마스킹 | 2026_06_25_000003 |
| `vbank_name` | string(50) | nullable | 가상계좌 은행명 | 2026_06_25_000003 |
| `vbank_num` | string(50) | nullable | 가상계좌 번호 | 2026_06_25_000003 |
| `vbank_due` | timestamp | nullable | 가상계좌 입금 마감 일시 | 2026_06_25_000003 |
| `paid_at` | timestamp | nullable | 결제 완료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `payment_key` | string(255) | nullable,change | PG 거래 키. SeedPay tid. 결제창 인증 전에는 NULL | 2026_09_28_000168 |
| `approval_no` | string(100) | nullable | 승인번호 | 2026_08_14_000023 |
| `virtual_account_bank` | string(50) | nullable | 가상계좌 은행 | 2026_08_14_000023 |
| `virtual_account_no` | string(100) | nullable | 가상계좌 번호 | 2026_08_14_000023 |
| `virtual_account_holder` | string(50) | nullable | 가상계좌 예금주 | 2026_08_14_000023 |
| `virtual_account_due_at` | timestamp | nullable | 입금기한. 관리자 연장 대상 | 2026_08_14_000023 |
| `depositor_name` | string(50) | nullable | 실제 입금자명 | 2026_08_14_000023 |
| `raw_response` | json | nullable | PG 결제/환불 응답 원문. 매출 대사 근거자료 | 2026_08_14_000023 |
| `requested_at` | timestamp | nullable | 결제 요청 일시 | 2026_08_14_000023 |
| `approved_at` | timestamp | nullable | 승인 일시 | 2026_08_14_000023 |
| `deposited_at` | timestamp | nullable | 가상계좌 입금 일시 | 2026_08_14_000023 |
| `failed_at` | timestamp | nullable | 결제 실패 일시 | 2026_08_14_000023 |
| `tax_free_amount` | integer |  | 면세 금액. PG 전송 시 전액 면세로 승인하며 taxFreeAmount = 실결제액, vat = 0 이다. 과세·면세를 라인별로 쪼개 두 번 승인하지 않는다. | 2026_09_08_000104 |
| `vat_amount` | integer |  | 부가세. 전액 면세이므로 항상 0이다. 사용자 화면에는 이 항목 자체를 노출하지 않는다. | 2026_09_08_000104 |
| `cancelled_amount` | integer |  | PG 취소 누계액. 부분취소는 status 를 paid 로 두고 이 값만 늘린다 | 2026_09_28_000168 |

## refunds
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `order_item_id` | unsignedBigInteger | nullable | order_items.id 참조 | 2026_06_25_000003 |
| `payment_id` | foreignId |  | payments.id 참조 | 2026_06_25_000003 |
| `refund_amount` | integer |  | 환불 금액 | 2026_06_25_000003 |
| `mileage_restored` | integer |  | 복원된 마일리지 | 2026_06_25_000003 |
| `reason` | text | nullable,change | 환불 사유 | 2026_08_14_000022 |
| `status` | string(30) |  | requested / completed / rejected 등 | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 users.id | 2026_06_25_000003 |
| `completed_at` | timestamp | nullable | 환불 완료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `refund_type` | string(20) |  | full / partial / manual | 2026_08_14_000022 |
| `refund_base_amount` | integer |  | 환불 계산 기준금액. 해당 order_item 실결제금액 | 2026_08_14_000022 |
| `refund_rate` | decimal(5, 2) | nullable | 환불 비율(%). 관리자 임의 금액 환불이면 NULL | 2026_08_14_000022 |
| `refund_method` | string(30) |  | card_cancel / bank_transfer / manual | 2026_08_14_000022 |
| `pg_refund_key` | string(255) | nullable | PG 환불 키. 수동환불이면 NULL | 2026_08_14_000022 |
| `admin_memo` | text | nullable | 내부 처리 메모 | 2026_08_14_000022 |
| `settlement_status` | string(30) |  | pending / reflected / excluded. 정산 반영 상태 | 2026_08_14_000022 |
| `settlement_reflected_at` | timestamp | nullable | 정산 반영 일시 | 2026_08_14_000022 |
| `requested_at` | timestamp | nullable | 환불 요청 일시 | 2026_08_14_000022 |
| `approved_at` | timestamp | nullable | 환불 승인 일시 | 2026_08_14_000022 |
| `refund_scope` | string(20) |  | 환불 범위. full=전액 / partial=부분(라인 선택). 패키지 주문은 라인 단위로 나눠 계산한다. | 2026_09_08_000078 |
| `progress_deduction` | integer |  | 수강 차시 비례 차감액. 실결제액 × (수강완료 차시 ÷ 총 차시). 원 단위 절사. | 2026_09_08_000078 |
| `delivery_fee_deduction` | integer |  | 반품 왕복 배송비 공제액. 고객 귀책일 때만 공제하며 회사 귀책이면 0이다. | 2026_09_08_000078 |
| `point_clawback_amount` | integer |  | 적립 포인트 회수액. 유상 적립 + 무상 프로모션 포인트 모두 회수 대상. | 2026_09_08_000078 |
| `point_shortage_amount` | integer |  | 회수 부족분. 이미 사용해 회수하지 못한 금액이며 1P=1원으로 현금에서 선차감한다. | 2026_09_08_000078 |
| `minus_point_amount` | integer |  | 마이너스 적재액. 부족분이 환불 예정액을 초과해 현금 공제가 불가능할 때 유상 마이너스로 적재. | 2026_09_08_000078 |
| `restored_point_amount` | integer |  | LIFO 복원액. 결제에 사용한 포인트를 사용 역순으로 되돌리며 유상을 최우선 복원한다. | 2026_09_08_000078 |
| `calc_snapshot` | json | nullable | 연산 근거 스냅샷. 단계별 산식·대입값·금액. 정책이 바뀌어도 당시 계산이 재현되어야 한다. | 2026_09_08_000078 |
| `return_tracking_no` | string(100) | nullable | 반품 수거 운송장번호. | 2026_09_08_000078 |
| `warehouse_received_at` | timestamp | nullable | 3PL 창고 실물 입고 일시. 입고 전에는 검수 입력이 잠긴다. | 2026_09_08_000078 |
| `inspection_result` | string(20) | nullable | 훼손 검수 결과. normal=정상(재판매 가능) / damaged=불합격(훼손·필기·재판매 불가). 운영자 수동 판정이며 자동 판정하지 않는다. | 2026_09_08_000078 |
| `liability` | string(20) | nullable | 반품 귀책. customer=고객 귀책(단순 변심, 왕복 배송비 공제) / company=회사 귀책(파손·오배송, 공제 없이 100% 환불). | 2026_09_08_000078 |
| `inspection_memo` | text | nullable | 검수 메모. 검수 사진은 attachments 다형 참조로 저장한다. 분쟁 증빙이다. | 2026_09_08_000078 |
| `locked_by` | unsignedBigInteger | nullable | 심사 중인 관리자 users.id. 뒤에 들어온 관리자는 읽기 전용으로 진입한다. | 2026_09_08_000078 |
| `locked_at` | timestamp | nullable | 잠금 시각. 30분 무조작 시 자동 해제한다. | 2026_09_08_000078 |
| `pg_cancel_no` | string(100) | nullable | PG 취소번호. 예: CNL-20260817-0442. | 2026_09_08_000078 |
| `pg_cancel_status` | string(20) | nullable | PG 취소 전송 상태. normal=정상 / failed=실패·재전송 대상. 실패 시 롤백 후 재전송한다. | 2026_09_08_000078 |
| `inquiry_id` | unsignedBigInteger | nullable | 연결 1:1 문의. inquiries.id 참조. 결제·환불 분류로 접수된 문의가 환불 관리 목록으로 자동 배정될 때 연결한다. 문의 원문과 환불 연산·승인을 문의번호로 1:1 연결한다. | 2026_09_08_000087 |
| `refund_bank_code` | string(10) | nullable | 환불 계좌 은행 코드(토스 은행 두 자리 코드). 가상계좌 · 계좌이체 결제 환불에만. 보관: 환불 완료 후 5년 뒤 파기 | 2026_10_19_000219 |
| `refund_account_no` | text | nullable | 환불 계좌번호 암호문(앱 암호화). 평문 저장 금지 · 화면은 뒤 4자리만. 보관: 환불 완료 후 5년 뒤 파기 | 2026_10_19_000219 |
| `refund_account_holder` | string(50) | nullable | 환불 계좌 예금주. 보관: 환불 완료 후 5년 뒤 파기 | 2026_10_19_000219 |
| `hold_reason` | string(30) | nullable | 환불보류 사유 코드. customer_reply=고객 회신 대기 / return_wait=증정품 · 교재 반환 대기 / payment_check=결제 정보 확인 중 / other=기타. status=held 일 때만 뜻이 있다 | 2026_10_20_000232 |
| `hold_memo` | string(500) | nullable | 환불보류 메모(필수 입력, 내부용 · 회원 비노출) | 2026_10_20_000232 |
| `held_at` | timestamp | nullable | 환불보류 시작 시각. 보류 경과일 정렬 기준. 보류 중 사유만 고치면 그대로 둔다 | 2026_10_20_000232 |

## order_cs_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger |  | 처리 관리자 users.id | 2026_06_25_000003 |
| `cs_type` | string(50) |  | 문의유형. 취소/환불/변경/기타 | 2026_06_25_000003 |
| `content` | text |  | CS 내용 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |

## order_status_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `order_item_id` | unsignedBigInteger | nullable | order_items.id 참조 | 2026_06_25_000003 |
| `from_status` | string(30) | nullable | 이전 상태 | 2026_06_25_000003 |
| `to_status` | string(30) |  | 변경 상태 | 2026_06_25_000003 |
| `changed_by` | unsignedBigInteger | nullable | 변경자 users.id | 2026_06_25_000003 |
| `reason` | string(255) | nullable | 변경 사유 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |

## deliveries
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `order_item_id` | unsignedBigInteger |  | order_items.id 참조 | 2026_06_25_000003 |
| `courier` | string(50) | nullable | 택배사명 | 2026_06_25_000003 |
| `tracking_no` | string(100) | nullable | 운송장 번호 | 2026_06_25_000003 |
| `status` | string(30) |  | ready / shipped / in_transit / delivered 등 | 2026_06_25_000003 |
| `receiver_name` | string(50) | nullable | 수령인 | 2026_06_25_000003 |
| `receiver_phone` | string(20) | nullable | 수령인 연락처 | 2026_06_25_000003 |
| `address` | string(255) | nullable | 배송지 주소 | 2026_06_25_000003 |
| `address_detail` | string(100) | nullable | 배송지 상세주소 | 2026_06_25_000003 |
| `shipped_at` | timestamp | nullable | 출고 일시 | 2026_06_25_000003 |
| `delivered_at` | timestamp | nullable | 배송 완료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `delivery_request` | text | nullable | 배송 요청사항 | 2026_08_14_000026 |
| `sender_location` | string(100) | nullable | 출고지. 3PL 출고 지시 엑셀 항목 | 2026_08_14_000026 |
| `admin_memo` | text | nullable | 관리자 메모 | 2026_08_14_000026 |
| `notification_sent_at` | timestamp | nullable | 배송 알림 발송 일시. 중복 발송 방지 | 2026_08_14_000026 |
| `ship_ordered_at` | timestamp | nullable | 출고 지시 일시. 3PL 발주 엑셀 다운로드 시점. 값이 있으면 수령인·배송지 수정을 잠근다. | 2026_09_08_000077 |
| `batch_id` | unsignedBigInteger | nullable | 3PL 발주 배치. delivery_batches.id 참조. ADMN-SETT-003 물류비 대사 매칭 키. | 2026_09_08_000077 |
| `zipcode` | string(5) | nullable | 우편번호 스냅샷. 도서산간 판정 기준값(3PL 발주 엑셀) | 2026_09_30_000177 |
| `fee_type` | string(20) | nullable | 배송비 구분. FREE 무료 / PREPAID 선불 / ISLAND 도서산간 (3PL 발주 엑셀) | 2026_09_30_000177 |

## delivery_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `delivery_id` | foreignId |  | deliveries.id 참조 | 2026_06_25_000003 |
| `status` | string(30) |  | 배송 상태 | 2026_06_25_000003 |
| `location` | string(100) | nullable | 현재 위치 | 2026_06_25_000003 |
| `description` | text | nullable | 상세 내용 | 2026_06_25_000003 |
| `logged_at` | timestamp |  | 기록 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |

## coupons
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `name` | string(100) |  | 쿠폰명 | 2026_06_25_000003 |
| `code` | string(50) | nullable,unique | 쿠폰 코드. 코드 쿠폰만 해당 | 2026_06_25_000003 |
| `type` | string(20) |  | percent / fixed | 2026_06_25_000003 |
| `target_type` | string(30) |  | all / course / package / category | 2026_06_25_000003 |
| `target_id` | unsignedBigInteger | nullable | 대상 ID | 2026_06_25_000003 |
| `min_order_amount` | integer |  | 최소 주문 금액 | 2026_06_25_000003 |
| `discount_value` | integer |  | 할인값 | 2026_06_25_000003 |
| `expire_days` | integer | nullable | 발급 후 만료 일수 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `status` | string(20) |  | active(사용중) / disabled(사용불가) | 2026_07_22_000001 |
| `max_issue_count` | unsignedInteger | nullable | 최대 발급 수량. NULL=무제한(기간 지속 지급형) | 2026_07_22_000001 |
| `memo` | string(500) | nullable | 관리자 비고(중단 사유 등 자유 기록) | 2026_07_22_000001 |
| `is_public` | tinyInteger |  | 사용자 페이지 공개 여부(1=공개, 0=비공개) | 2026_07_27_000001 |
| `expire_at` | date | nullable | 쿠폰 종료일(이 날짜까지 사용, 전원 공통). 비우면 상시 | 2026_07_29_000002 |
| `max_discount_amount` | integer | nullable | 정률 할인 시 최대 할인금액. NULL이면 상한 없음. type=fixed면 미사용 | 2026_08_14_000032 |
| `issued_count` | unsignedInteger |  | 발급 수(시스템 관리 카운터) | 2026_09_28_000171 |
| `emergency_suspended_at` | timestamp | nullable | 긴급 사용 중지 일시(최고 관리자). 값이 있으면 보유 · 취소 복원 쿠폰도 사용불가. | 2026_09_30_000175 |

## coupon_issue_batches
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `coupon_id` | foreignId |  | coupons.id 참조 | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger |  | users.id 참조 | 2026_06_25_000003 |
| `issue_type` | string(30) |  | 수동 / 엑셀 / 텍스트 | 2026_06_25_000003 |
| `total_count` | integer |  | 전체 대상 수 | 2026_06_25_000003 |
| `success_count` | integer |  | 성공 건수 | 2026_06_25_000003 |
| `failed_count` | integer |  | 실패 건수 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |

## user_coupons
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `coupon_id` | foreignId |  | coupons.id 참조 | 2026_06_25_000003 |
| `issue_batch_id` | foreignId | nullable | coupon_issue_batches.id 참조 | 2026_06_25_000003 |
| `status` | string(30) |  | issued / used / expired 등 | 2026_06_25_000003 |
| `issued_at` | timestamp |  | 발급 일시 | 2026_06_25_000003 |
| `expires_at` | timestamp | nullable | 만료 일시 | 2026_06_25_000003 |
| `used_at` | timestamp | nullable | 사용 일시 | 2026_06_25_000003 |
| `used_order_id` | unsignedBigInteger | nullable | 사용 주문 ID | 2026_06_25_000003 |
| `discount_amount` | integer | nullable | 실제 할인금액 | 2026_06_25_000003 |

## posts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `category` | string(30) | nullable,change | 레거시 분류(공지/이벤트/FAQ/당첨발표) — 게시판 전환 후 미사용 | 2026_07_23_000001 |
| `title` | string(255) |  | 제목 | 2026_06_25_000003 |
| `content` | longText |  | 본문 | 2026_06_25_000003 |
| `author_id` | unsignedBigInteger |  | 작성자 users.id | 2026_06_25_000003 |
| `view_count` | integer |  | 조회수 | 2026_06_25_000003 |
| `is_pinned` | tinyInteger |  | 상단 고정 여부 | 2026_06_25_000003 |
| `is_public` | tinyInteger |  | 공개 여부 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `board_id` | unsignedBigInteger | nullable | 소속 게시판 boards.id | 2026_07_16_120001 |
| `device_scope` | string(10) |  | 노출 기기. all=공통 / pc=PC만 / mobile=모바일만. 둘 다 해제한 상태는 저장을 거부한다(어디에도 안 보이는 글이 생긴다). 모바일 전용 이벤트가 PC에 노출되어 참여 불가 문의가 발생하는 것을 막는 통제값이다. popups.device 와 같은 소문자 체계를 쓴다. | 2026_09_08_000086 |
| `status` | string(20) |  | 발행 상태. draft=임시저장 / scheduled=예약발행 / published=게시중 / hidden=숨김. 임시저장은 사용자 화면에 미노출하며 작성자 본인만 목록에서 확인한다. | 2026_09_08_000086 |
| `pin_order` | integer | nullable | 상단 고정 순위. is_pinned=1 인 글의 노출 순서다. 목록 최상단에 이 순서대로 붙는다. 미고정 글은 NULL. | 2026_09_08_000086 |
| `published_at` | dateTime | nullable | 예약 발행 시각. 배치가 이 시각에 status 를 published 로 전환한다. 과거 시각은 저장을 거부한다. | 2026_09_08_000086 |
| `started_at` | dateTime | nullable | 게시 시작 일시. | 2026_09_08_000086 |
| `ended_at` | dateTime | nullable | 게시 종료 일시. NULL이면 무기한. 종료일이 지난 글은 자동으로 상태가 종료되며 사용자 화면에서 내려간다. | 2026_09_08_000086 |
| `allow_comment` | tinyInteger |  | 댓글 허용 여부. 이벤트 글에는 참여 댓글용으로 켠다. 기본값 0. | 2026_09_08_000086 |
| `related_post_id` | unsignedBigInteger | nullable | 연결 원본 게시글. 당첨자 발표 글이 원본 이벤트 글을 가리키며 두 글이 상호 링크된다. posts.id 자기참조. | 2026_09_08_000086 |
| `promotion_id` | unsignedBigInteger | nullable | 당첨자 발표가 연결된 이벤트(promotions.id). 이벤트 1건 : 발표 1건 | 2026_10_15_000208 |
| `content_type` | string(10) | nullable | 무료콘텐츠 구분. EXAM=빈출자료 / DAILY=정조교의 매일 1문제. 다른 게시판 글은 NULL | 2026_10_21_000239 |
| `cert_category_id` | unsignedBigInteger | nullable | 무료콘텐츠 자격증 — categories.id(1Depth) 참조. 두 구분 모두 필수(화면 검증) | 2026_10_21_000239 |
| `year` | unsignedSmallInteger | nullable | 무료콘텐츠 연도 | 2026_10_21_000239 |
| `round_no` | unsignedSmallInteger | nullable | 무료콘텐츠 회차 — 빈출자료만. 범위를 고정하지 않는다(자격증마다 시행 횟수가 다르다) | 2026_10_21_000239 |
| `related_course_id` | unsignedBigInteger | nullable | 무료콘텐츠 관련 강좌 — courses.id 참조. 상세 하단 관련 강좌 카드. 비우면 블록을 숨긴다 | 2026_10_21_000239 |

## attachments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `attachable_type` | string(100) |  | 연결 대상 모델/도메인 | 2026_06_25_000003 |
| `attachable_id` | unsignedBigInteger |  | 연결 대상 ID | 2026_06_25_000003 |
| `original_name` | string(255) | nullable | 업로드 당시 파일명. 저장명은 UUID 라 사람이 읽을 수 없다 | 2026_09_16_000120 |
| `file_path` | string(500) |  | 저장 경로 | 2026_06_25_000003 |
| `mime_type` | string(100) | nullable | MIME 타입 | 2026_06_25_000003 |
| `size` | unsignedBigInteger |  | 파일 크기(byte) | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `type` | string(30) | nullable |  | 2026_07_10_000010 |
| `sort_order` | integer | nullable |  | 2026_07_10_000010 |
| `download_count` | unsignedInteger |  | 다운로드 건수. 원본 경로를 감추는 다운로드 라우트에서 집계한다. | 2026_09_08_000102 |
| `disk` | string(20) | nullable | 저장 구획 — media(공개) / editor(에디터) / secure(비공개) | 2026_09_16_000120 |

## admin_menus
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `parent_id` | unsignedBigInteger | nullable | 상위 메뉴 ID. self 참조 | 2026_06_25_000003 |
| `name` | string(100) |  | 메뉴명 | 2026_06_25_000003 |
| `route_name` | string(100) | nullable | Laravel route name | 2026_06_25_000003 |
| `url` | string(255) | nullable | 메뉴 URL | 2026_06_25_000003 |
| `icon` | string(50) | nullable | 아이콘 | 2026_06_25_000003 |
| `sort_order` | integer |  | 노출 순서 | 2026_06_25_000003 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `screen_code` | string(30) | nullable | 화면 설계 코드. ADMN-USER-001 형식. 권한 매트릭스 행 식별자. | 2026_09_08_000095 |

## admin_roles
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `name` | string(100) |  | 권한 그룹명 | 2026_06_25_000003 |
| `description` | text | nullable | 설명 | 2026_06_25_000003 |
| `is_system` | tinyInteger |  | 시스템 기본 권한 여부 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `updated_at` | timestamp | nullable |  | 2026_06_25_000003 |
| `code` | string(30) | nullable | 역할 코드. super / cs / logistics / finance / instructor / assistant. inquiry_categories.assign_role 참조 대상. | 2026_09_08_000095 |
| `sort_order` | integer |  | 노출 순서. 권한 매트릭스 역할 선택 정렬용. | 2026_09_08_000095 |

## admin_user_roles
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `user_id` | foreignId |  | users.id 참조 | 2026_06_25_000003 |
| `admin_role_id` | foreignId |  | admin_roles.id 참조 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |

## admin_role_menus
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `admin_role_id` | foreignId |  | admin_roles.id 참조 | 2026_06_25_000003 |
| `admin_menu_id` | foreignId |  | admin_menus.id 참조 | 2026_06_25_000003 |
| `can_view` | tinyInteger |  | 조회 권한 | 2026_06_25_000003 |
| `can_create` | tinyInteger |  | 등록 권한 | 2026_06_25_000003 |
| `can_update` | tinyInteger |  | 수정 권한 | 2026_06_25_000003 |
| `can_delete` | tinyInteger |  | 삭제 권한 | 2026_06_25_000003 |
| `can_download` | tinyInteger |  | 다운로드 권한 | 2026_06_25_000003 |
| `note` | string(200) | nullable | 권한 부여 사유 메모. 권한 매트릭스 비고 컬럼. | 2026_09_08_000095 |

## admin_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger |  | 행위자 users.id | 2026_06_25_000003 |
| `menu_id` | unsignedBigInteger | nullable | admin_menus.id | 2026_06_25_000003 |
| `action` | string(100) |  | 수행 액션 | 2026_06_25_000003 |
| `target_type` | string(50) | nullable | 대상 타입 | 2026_06_25_000003 |
| `target_id` | unsignedBigInteger | nullable | 대상 ID | 2026_06_25_000003 |
| `before_value` | json | nullable | 변경 전 값 | 2026_06_25_000003 |
| `after_value` | json | nullable | 변경 후 값 | 2026_06_25_000003 |
| `request_method` | string(10) | nullable | HTTP 메서드 | 2026_06_25_000003 |
| `request_url` | string(500) | nullable | 요청 URL | 2026_06_25_000003 |
| `result_status` | string(10) | nullable | 처리 결과 상태 | 2026_06_25_000003 |
| `ip` | string(45) |  | 접속 IP | 2026_06_25_000003 |
| `user_agent` | string(500) | nullable | 브라우저/기기 정보 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `sub_action` | string(50) | nullable | 도메인 행위 소분류. approve / reject / routing_change / ship_order / confirm / unmask 등. 일반 조회·수정은 NULL. action(대분류)과 직교한다. | 2026_09_08_000080 |
| `reason` | string(200) | nullable | 열람·처리 사유. 개인정보 열람 및 마스킹 해제 시 필수. 기록은 삭제할 수 없다. | 2026_09_08_000098 |
| `reason_ref` | string(50) | nullable | 사유 관련 참조번호. 문의번호(Q-2026-08812) 또는 주문번호. | 2026_09_08_000098 |
| `admin_login_id` | string(50) | nullable | 행위 시점 관리자 아이디 스냅샷. 계정 삭제 후에도 행위자를 추적한다 | 2026_09_10_000106 |
| `admin_role_code` | string(50) | nullable | 행위 시점 역할 code 스냅샷. admin_roles.code 기준이며 다중 부여 시 콤마로 잇는다. 역할명이 바뀌어도 과거 로그가 흔들리지 않도록 이름이 아닌 code 를 남긴다 | 2026_09_10_000106 |

## excel_download_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger |  | 요청 관리자 users.id | 2026_06_25_000003 |
| `menu_key` | string(100) |  | 요청 메뉴 키 | 2026_06_25_000003 |
| `download_type` | string(50) |  | 다운로드 유형 | 2026_06_25_000003 |
| `file_name` | string(255) | nullable | 생성 파일명 | 2026_06_25_000003 |
| `file_path` | string(500) | nullable | private storage 내부 파일 경로 | 2026_06_25_000003 |
| `filter_params` | json | nullable | 검색/필터 조건 | 2026_06_25_000003 |
| `row_count` | integer | nullable | 생성 행 수 | 2026_06_25_000003 |
| `reason` | text | nullable | 다운로드 사유 | 2026_06_25_000003 |
| `status` | string(30) |  | pending / processing / completed / failed | 2026_06_25_000003 |
| `error_message` | text | nullable | 실패 메시지 | 2026_06_25_000003 |
| `ip` | string(45) |  | 요청 IP | 2026_06_25_000003 |
| `user_agent` | string(500) | nullable | 요청 User-Agent | 2026_06_25_000003 |
| `started_at` | timestamp | nullable | 작업 시작 일시 | 2026_06_25_000003 |
| `completed_at` | timestamp | nullable | 작업 완료 일시 | 2026_06_25_000003 |
| `expired_at` | timestamp | nullable | 파일 삭제 기준 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `admin_login_id` | string(50) | nullable | 요청 시점 관리자 아이디 스냅샷. 계정 삭제 후에도 반출자를 추적한다 | 2026_09_10_000108 |
| `admin_role_code` | string(50) | nullable | 요청 시점 역할 code 스냅샷. admin_roles.code 기준. 역할명이 바뀌어도 과거 로그가 흔들리지 않도록 이름이 아닌 code 를 남긴다 | 2026_09_10_000108 |

## batch_job_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `job_name` | string(100) |  | 작업명 | 2026_06_25_000003 |
| `status` | string(30) |  | success / failed / running 등 | 2026_06_25_000003 |
| `total_count` | integer | nullable | 전체 건수 | 2026_06_25_000003 |
| `success_count` | integer | nullable | 성공 건수 | 2026_06_25_000003 |
| `failed_count` | integer | nullable | 실패 건수 | 2026_06_25_000003 |
| `error_message` | text | nullable | 오류 메시지 | 2026_06_25_000003 |
| `started_at` | timestamp | nullable | 시작 일시 | 2026_06_25_000003 |
| `finished_at` | timestamp | nullable | 종료 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `step_code` | string(20) | nullable | 정산 스텝 불변 코드. CARRY_IN / ACCRUAL / MMG_ADJ / DEDUCT / SUPPORT_CAP / PREPAY_OFFSET / LUMPSUM_ADD / PAYEE_SPLIT / TAX / CLAIM / PAYOUT | 2026_09_18_000136 |
| `step_group` | string(20) | nullable | 배치 모니터링·재시도 묶음. AGGREGATE(1~2) / ADJUST(3~5) / DISTRIBUTE(6~8) / TAX_PAYOUT(9~11) | 2026_09_18_000136 |
| `target_month` | char(7) | nullable | 정산 귀속월 YYYY-MM. 재실행 단위 | 2026_09_18_000136 |

## order_item_allocations
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `order_item_id` | foreignId |  | order_items.id 참조 | 2026_06_25_000003 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000003 |
| `instructor_id` | foreignId |  | instructors.id 참조 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `base_amount` | integer |  | 기준 실결제액. 배송비·실물 교재 라인 제외, 할인 비례 배분 후 강좌별 금액. | 2026_09_08_000079 |
| `share_rate_snapshot` | decimal(5, 2) | nullable | 지분율(%). 거래일 시점 product_instructor_shares 스냅샷. 이후 지분이 바뀌어도 변하지 않는다. | 2026_09_08_000079 |
| `share_amount` | integer |  | ① 지분 반영액. 실결제액 × 지분율 후 원 단위 절사(버림). | 2026_09_08_000079 |
| `commission_rate_snapshot` | decimal(5, 2) | nullable | 계약 정산요율(%). 거래일 시점 instructor_contracts 스냅샷. 지분율과는 다른 축이다. | 2026_09_08_000079 |
| `settlement_amount` | integer |  | ② 정산액. ① × 정산요율 후 원 단위 절사(버림). 강사 귀속 최종 금액. | 2026_09_08_000079 |

## instructor_settlements
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `instructor_id` | foreignId |  | instructors.id 참조 | 2026_06_25_000003 |
| `settlement_month` | char(7) |  | 정산월 YYYY-MM | 2026_06_25_000003 |
| `total_sales_amount` | integer |  | 총 매출액 | 2026_06_25_000003 |
| `commission_amount` | integer |  | 수수료/공제액 | 2026_06_25_000003 |
| `settlement_amount` | integer |  | 최종 정산금액 | 2026_06_25_000003 |
| `status` | string(30) |  | draft / confirmed / paid 등 | 2026_06_25_000003 |
| `admin_id` | unsignedBigInteger | nullable | 확정/지급 처리 관리자 users.id | 2026_06_25_000003 |
| `memo` | text | nullable | 메모 | 2026_06_25_000003 |
| `confirmed_at` | timestamp | nullable | 확정 일시 | 2026_06_25_000003 |
| `paid_at` | timestamp | nullable | 지급 일시 | 2026_06_25_000003 |
| `created_at` | timestamp |  |  | 2026_06_25_000003 |
| `tax_type_snapshot` | string(20) | nullable | 세무 처리 구분 스냅샷. personal=원천세 3.3% / business=사업자 10%. 정산 화면에서 임의 변경 불가. | 2026_09_08_000079 |
| `refund_deduction` | integer |  | 환불 차감액(음수). 환불 발생일이 속한 월의 정산에서 차감하며 원거래 시점 스냅샷으로 환수액을 역산한다. | 2026_09_08_000079 |
| `carryover_in` | integer |  | 전월 이월액. 전월 마이너스 잔액을 그대로 승계한다. | 2026_09_08_000079 |
| `carryover_out` | integer |  | 차월 이월액(음수). 당월 환불이 매출을 초과해 지급 대상액이 음수면 실지급 0원 처리 후 다음 달로 넘긴다. | 2026_09_08_000079 |
| `payable_amount` | integer |  | 지급 대상액(세전). 판매 정산액 + 환불 차감 + 전월 이월. | 2026_09_08_000079 |
| `tax_amount` | integer |  | 세액. 원천세는 음수(공제), 사업자 부가세는 양수(가산). 원 단위 절사. | 2026_09_08_000079 |
| `net_payment` | integer |  | 실지급액. 지급 대상액 + 세액. | 2026_09_08_000079 |
| `is_locked` | tinyInteger |  | 정산 확정 Lock. 1이면 재집계·금액 수정·지분 소급 반영이 모두 차단된다. 최고 관리자도 해제 불가. | 2026_09_08_000079 |
| `aggregated_at` | timestamp | nullable | 집계 실행 일시. 재집계 시 갱신한다. | 2026_09_08_000079 |

## instructor_settlement_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_25_000003 |
| `settlement_id` | foreignId |  | instructor_settlements.id 참조 | 2026_06_25_000003 |
| `order_item_allocation_id` | foreignId |  | order_item_allocations.id 참조 | 2026_06_25_000003 |
| `order_id` | foreignId |  | orders.id 참조 | 2026_06_25_000003 |
| `order_item_id` | foreignId |  | order_items.id 참조 | 2026_06_25_000003 |
| `course_id` | foreignId |  | courses.id 참조 | 2026_06_25_000003 |
| `product_name` | string(255) |  | 정산 대상 상품명 스냅샷 | 2026_06_25_000003 |
| `commission_rate` | decimal(5, 2) |  | 정산율/수수료율 | 2026_06_25_000003 |
| `settlement_amount` | integer |  | 최종 상세 정산액 | 2026_06_25_000003 |
| `paid_at` | timestamp | nullable | 지급 일시 | 2026_06_25_000003 |
| `item_type` | string(20) |  | 행 유형. sale=판매 정산 / refund=환불 차감. 환불 차감 행은 원거래일과 환불일을 함께 표기한다. | 2026_09_08_000079 |
| `order_count` | unsignedInteger |  | 해당 상품의 거래 건수. | 2026_09_08_000079 |
| `base_amount` | integer |  | 기준 실결제액 합계. 배송비·교재 제외. | 2026_09_08_000079 |
| `share_rate` | decimal(5, 2) | nullable | 지분율(%). 거래일 스냅샷. | 2026_09_08_000079 |
| `share_amount` | integer |  | ① 지분 반영액. 원 단위 절사 후. | 2026_09_08_000079 |

## admin_allowed_ips
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_06_26_000001 |
| `ip` | string(45) | unique | 허용 IP | 2026_06_26_000001 |
| `description` | string(100) | nullable | 메모 (예: 박성민 재택) | 2026_06_26_000001 |
| `is_active` | tinyInteger |  | 활성 여부 | 2026_06_26_000001 |
| `created_at` | timestamp |  |  | 2026_06_26_000001 |
| `updated_at` | timestamp | nullable |  | 2026_06_26_000001 |
| `admin_role_id` | unsignedBigInteger | nullable | 허용 대상 권한그룹 admin_roles.id. NULL이면 전체 역할 공통 허용. | 2026_09_07_000056 |
| `user_id` | unsignedBigInteger | nullable | 허용 대상 관리자 users.id. 계정 전용 예외. NULL 이면 역할 규칙 또는 전역 규칙. | 2026_09_08_000095 |

## product_instructors
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `product_type` | string(20) |  | course / package | 2026_07_10_200000 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_07_10_200000 |
| `role` | char(1) |  | m=대표 / s=부강사 / a=참여 | 2026_07_10_200000 |

## badges
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_13_100000 |
| `code` | string(20) | unique | 배지 코드 (product_badges.badge_type과 매칭) | 2026_07_13_100000 |
| `label` | string(50) |  | 관리자 UI 표시명 | 2026_07_13_100000 |
| `slot` | unsignedTinyInteger |  | 1=강조1 / 2=강조2 | 2026_07_13_100000 |
| `image_path` | string(255) | nullable | 배지 이미지 파일 경로 | 2026_07_13_100000 |
| `color` | string(20) | nullable | 배경색 hex | 2026_07_13_100000 |
| `text_color` | string(20) | nullable | 텍스트색 hex | 2026_07_13_100000 |
| `icon` | string(50) | nullable | 아이콘 CSS class 또는 이모지 | 2026_07_13_100000 |
| `sort_order` | integer |  |  | 2026_07_13_100000 |
| `is_active` | tinyInteger |  | 1=노출 / 0=미노출 | 2026_07_13_100000 |
| `created_at` | timestamp |  |  | 2026_07_13_100000 |
| `updated_at` | timestamp | nullable |  | 2026_07_13_100000 |

## boards
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_120000 |
| `name` | string(100) |  | 게시판명 | 2026_07_16_120000 |
| `code` | string(50) | nullable,unique | 게시판 식별 코드(라우팅/구분). 미입력 시 자동 생성 | 2026_07_16_120000 |
| `type` | string(20) |  | 게시판 유형: list/faq/gallery/page/community | 2026_07_16_120000 |
| `sort_order` | integer |  | 노출 순서 | 2026_07_16_120000 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_07_16_120000 |
| `created_at` | timestamp |  |  | 2026_07_16_120000 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_120000 |
| `description` | text | nullable | 게시판 설명. 목록 상단 안내문구 | 2026_08_14_000028 |

## post_comments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_120002 |
| `post_id` | unsignedBigInteger |  | 게시글 posts.id | 2026_07_16_120002 |
| `parent_id` | unsignedBigInteger | nullable | 상위 댓글 post_comments.id (답글) | 2026_07_16_120002 |
| `user_id` | unsignedBigInteger |  | 작성자 users.id | 2026_07_16_120002 |
| `content` | text |  | 댓글 내용 | 2026_07_16_120002 |
| `is_public` | tinyInteger |  | 공개 여부(관리자 블라인드 처리용) | 2026_07_16_120002 |
| `created_at` | timestamp |  |  | 2026_07_16_120002 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_120002 |

## site_settings
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_130000 |
| `site_name` | string(100) | nullable | 사이트명 | 2026_07_16_130000 |
| `logo_path` | string(255) | nullable | 로고 | 2026_07_16_130000 |
| `favicon_path` | string(255) | nullable | 파비콘 | 2026_07_16_130000 |
| `company_name` | string(100) | nullable | 상호 | 2026_07_16_130000 |
| `ceo_name` | string(50) | nullable | 대표자 | 2026_07_16_130000 |
| `business_number` | string(30) | nullable | 사업자등록번호 | 2026_07_16_130000 |
| `mail_order_number` | string(50) | nullable | 통신판매업신고번호 | 2026_07_16_130000 |
| `address` | string(255) | nullable | 주소 | 2026_07_16_130000 |
| `tel` | string(30) | nullable | 대표전화 | 2026_07_16_130000 |
| `cs_tel` | string(30) | nullable | 고객센터 전화 | 2026_07_16_130000 |
| `cs_hours` | string(100) | nullable | 고객센터 운영시간 | 2026_07_16_130000 |
| `email` | string(100) | nullable | 대표 이메일 | 2026_07_16_130000 |
| `copyright` | string(255) | nullable | 저작권 문구 | 2026_07_16_130000 |
| `sns_naver` | string(255) | nullable | 네이버 링크 | 2026_07_16_130000 |
| `sns_youtube` | string(255) | nullable | 유튜브 링크 | 2026_07_16_130000 |
| `sns_instagram` | string(255) | nullable | 인스타그램 링크 | 2026_07_16_130000 |
| `created_at` | timestamp |  |  | 2026_07_16_130000 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_130000 |
| `privacy_officer` | string(50) | nullable | 개인정보관리책임자 | 2026_07_28_000002 |
| `edu_facility_number` | string(50) | nullable | 원격평생교육시설신고번호 | 2026_07_28_000002 |
| `hosting_provider` | string(100) | nullable | 호스팅 제공자 | 2026_07_28_000002 |
| `delivery_fee` | integer |  | 기본 배송비 | 2026_08_14_000034 |
| `free_delivery_threshold` | integer | nullable | 무료배송 기준 금액. NULL이면 조건부 무료배송 미적용 | 2026_08_14_000034 |
| `island_delivery_fee` | integer |  | 도서산간 추가 배송비 | 2026_08_14_000034 |
| `return_delivery_fee` | integer |  | 반품 왕복 배송비 기본값 | 2026_08_14_000036 |
| `point_earn_rate` | decimal(5, 2) |  | 포인트 적립률(%) | 2026_08_14_000036 |
| `max_device_count` | unsignedTinyInteger |  | 기기 등록 가능 대수 | 2026_08_14_000036 |
| `device_abuse_threshold` | unsignedTinyInteger | nullable | 기기 다중 접속 적발 임계치. NULL이면 자동 필터 미적용 | 2026_08_14_000036 |
| `refund_claim_min_progress` | unsignedTinyInteger |  | 합격 환급 신청 최소 진도율(%). 절사 기준 | 2026_08_14_000036 |
| `verify_daily_limit` | unsignedTinyInteger | change | 계정(DI) 기준 인증 요청 한도(롤링 24시간). 기본값 10. | 2026_10_15_000213 |
| `verify_ip_hourly_limit` | unsignedSmallInteger |  | IP 기준 시간당 소프트캡. 초과 시 쿨다운 적용. 기본값 10. | 2026_09_07_000055 |
| `verify_ip_daily_limit` | unsignedSmallInteger | change | IP 기준 인증 요청 한도(롤링 24시간). 기본값 10. | 2026_10_15_000213 |
| `verify_max_attempts` | unsignedTinyInteger |  | 인증번호 오입력 허용 횟수. 초과 시 세션 무효화. 기본값 5. | 2026_09_07_000055 |
| `verify_code_ttl_sec` | unsignedSmallInteger |  | 인증번호 유효시간(초). 기본값 300(5분). | 2026_09_07_000055 |
| `verify_resend_cooldown_sec` | unsignedSmallInteger |  | 인증번호 재발송 쿨다운(초). 기본값 30. | 2026_09_07_000055 |
| `verify_session_ttl_user_sec` | unsignedSmallInteger |  | 사용자 인증 세션 유효시간(초). 기본값 1800(30분). | 2026_09_07_000055 |
| `verify_session_ttl_admin_sec` | unsignedSmallInteger |  | 관리자 인증 세션 유효시간(초). 기본값 600(10분). | 2026_09_07_000055 |
| `password_history_count` | unsignedTinyInteger |  | 비밀번호 재사용 금지 이력 개수. 현재 비밀번호는 별도 대조. 기본값 3. | 2026_09_07_000055 |
| `join_verify_max_attempts` | unsignedTinyInteger |  | 가입 본인인증 연속 실패 허용 횟수. 초과 시 잠금. 기본값 5. | 2026_09_07_000058 |
| `join_verify_lock_sec` | unsignedSmallInteger |  | 가입 본인인증 실패 잠금 시간(초). 경과 후 자동 해제. 기본값 600(10분). | 2026_09_07_000058 |
| `remember_ttl_user_days` | unsignedSmallInteger |  | 사용자 자동 로그인 유지 기간(일). 기본값 30. | 2026_09_07_000058 |
| `remember_ttl_admin_days` | unsignedSmallInteger |  | 관리자 자동 로그인 유지 기간(일). 기본값 7. | 2026_09_07_000058 |
| `welcome_point` | unsignedInteger |  | 신규 가입 축하금(P). 무상 포인트로 회원가입 트랜잭션 안에서 즉시 지급한다. DI 기준 생애 1회. 0이면 미지급. | 2026_09_08_000085 |
| `earn_book_line` | tinyInteger |  | 실물 교재 라인 유상 적립 지급 여부. 도서정가제로 교재는 쿠폰·포인트 사용이 원천 차단되므로 적립도 주지 않는다. 기본값 0(미지급). | 2026_09_08_000085 |
| `earn_rounding` | string(10) |  | 유상 적립 단수 처리. ceil=올림 / floor=버림 / round=반올림. 1P 단위. 기본값 ceil. | 2026_09_08_000085 |
| `earn_confirm_timing` | string(30) |  | 적립 확정 시점. paid=결제 승인 즉시 / delivered=배송완료 후 / course_started=수강 시작 후. 기본값 paid. | 2026_09_08_000085 |
| `free_point_expire_years` | unsignedTinyInteger |  | 무상 포인트 유효기간(년). 가입 축하금·관리자 수동 지급·보상성 지급이 해당한다. 환불 시 회수 대상. | 2026_09_08_000085 |
| `paid_point_expire_years` | unsignedTinyInteger | nullable | 유상 포인트 유효기간(년). 실결제로 적립된 포인트다. NULL이면 무기한. 환불 시 LIFO 부활 대상. | 2026_09_08_000085 |
| `deduct_priority` | string(30) |  | 차감 우선순위. expire_asc_free_first=만료 임박순, 같은 만료일이면 무상 우선. 회원 손해를 최소화하는 순서다. | 2026_09_08_000085 |
| `expire_notice_days` | unsignedSmallInteger |  | 소멸 사전 안내 일수. 매일 09:00 배치가 D+N 소멸 예정 포인트를 스캔해 대상 회원에게 발송한다. 0이면 미발송. 1~90일. | 2026_09_08_000085 |
| `expire_notice_alimtalk` | tinyInteger |  | 소멸 안내 알림톡 발송 여부. 기본값 1. | 2026_09_08_000085 |
| `expire_notice_lms` | tinyInteger |  | 소멸 안내 알림톡 실패 시 LMS(문자) 대체 발송 여부. 기본값 1. | 2026_09_08_000085 |
| `expire_notice_email` | tinyInteger |  | 소멸 안내 이메일 발송 여부. 기본값 0. | 2026_09_08_000085 |
| `paid_restore_grace_days` | unsignedTinyInteger |  | 만료 유상 포인트 부활 유예 일수. 환불 시점에 이미 원 유효기간이 도과한 유상 포인트를 되돌릴 때 환불 완료일 + N일 자정으로 유효기간을 재설정한다. ADMN-RFD-003 D+7 유예 탭과 연동한다. | 2026_09_08_000085 |
| `ad_block_start_hour` | unsignedTinyInteger |  | 광고성 메시지 발송 금지 시작 시(24h). 정보통신망법 제50조. 기본값 21. | 2026_09_08_000096 |
| `ad_block_end_hour` | unsignedTinyInteger |  | 광고성 메시지 발송 금지 종료 시(24h). 기본값 8. 설계서 06 표기는 오타. | 2026_09_08_000096 |
| `campaign_cancel_before_min` | unsignedSmallInteger |  | 예약 발송 취소 가능 시한(분). 큐 적재 시작 후에는 취소되지 않는다. 기본값 30. | 2026_09_08_000096 |
| `lecture_complete_min_rate` | unsignedTinyInteger |  | 차시 수강완료 인정 최소 진도율(%). 화면 목차 하단에 상시 노출한다. 기본값 90. | 2026_09_08_000103 |
| `book_supply_type_default` | string(20) | nullable | 도서 등록 시 공급 형태 기본값. NULL=미지정(담당자 선택 강제) | 2026_09_18_000137 |
| `book_supply_type_change_allowed_yn` | boolean |  | 판매 이력 있는 도서의 공급 형태 변경 허용 여부. false 면 신규 SKU 를 발급한다 | 2026_09_18_000137 |
| `consignment_fee_type_default` | string(20) |  | 위탁 수수료 수취 방식 기본값. NET_DEDUCT / GROSS_SETTLE | 2026_09_18_000137 |
| `consignment_return_tracking_yn` | boolean |  | 위탁 반품 실물 반환 추적 사용 여부 | 2026_09_18_000137 |
| `book_reprice_min_months` | unsignedSmallInteger |  | 도서 재정가 가능 최소 경과 개월. 출판문화산업 진흥법 제22조 제2항 | 2026_09_18_000137 |
| `support_fund_payment_method_default` | string(20) |  | 개발지원금 지급 방식 기본값. LUMP_SUM / INSTALLMENT / REVENUE_SHARE | 2026_09_18_000137 |
| `support_fund_scope_default` | string(20) |  | R/S형 지원금 기본 모수 범위. TRACK_A_ONLY / TRACK_B1_ONLY / TRACK_A_B1 | 2026_09_18_000137 |
| `support_fund_offset_allowed_yn` | boolean |  | R/S형 지원금의 선급금 상계 허용 여부. 겹치면 이중 회수가 된다 | 2026_09_18_000137 |
| `support_fund_cap_restore_on_refund` | boolean |  | 환불 발생 시 지원금 한도 복원 여부 | 2026_09_18_000137 |
| `support_fund_termination_policy_default` | string(20) |  | 지원금 종료 시 미소진 잔액 처리 기본값. FORFEIT / LUMP_SETTLE / PRO_RATA | 2026_09_18_000137 |
| `support_fund_mmg_include_yn` | boolean |  | 지원금 S 라인의 MMG 판정 모수 포함 여부. 변경 불가 — 포함하면 지원금이 보장액에 흡수된다 | 2026_09_18_000137 |
| `carryover_force_settle_month` | unsignedTinyInteger |  | 세전 이월 강제 종결 월. 연도를 넘겨 상쇄하면 연간 지급명세서와 과세표준이 어긋난다 | 2026_09_18_000137 |
| `carryover_max_months` | unsignedTinyInteger |  | 지급 이월 연속 허용 개월 | 2026_09_18_000137 |
| `nts_check_validity_days` | integer |  | 사업자등록 확인 결과 유효기간 (기본값: 90일). 합의서 부록 B | 2026_09_21_000149 |
| `book_discount_rate_limit` | decimal(5, 2) |  | 도서 최대 할인율 (기본값: 0%. 법정 상한은 정가의 10%이며 본 값은 내부 정책). 합의서 부록 B | 2026_09_21_000149 |
| `book_point_rate_limit` | decimal(5, 2) |  | 도서 최대 마일리지 적립률 (기본값: 0%. 할인과 합산하여 정가의 15% 이내라는 법정 상한 내에서만 상향 가능). 합의서 부록 B | 2026_09_21_000149 |
| `settlement_closed_month` | char(7) | nullable | 정산 마감 완료월 YYYY-MM(잠정). 이 달까지의 요율 라인은 잠긴다 | 2026_10_02_000189 |
| `manual_adj_approval_threshold` | unsignedInteger |  | 수동 조정 단독 승인 임계 금액(원). 넘으면 재무 책임자 2차 승인 | 2026_10_03_000198 |
| `promotion_block_enabled` | boolean |  | 기획전 중복 할인 차단 사용(킬 스위치). 0 이면 상품별 차단 · 스케줄이 남아 있어도 즉시 해제. 전 기획전 공통(DECISIONS #74) | 2026_10_15_000210 |
| `corporate_number` | string(30) | nullable | 법인등록번호(푸터 표기) | 2026_10_15_000211 |
| `publisher_number` | string(50) | nullable | 출판사등록번호(푸터 표기) | 2026_10_15_000211 |
| `partnership_email` | string(100) | nullable | 제휴 문의 수신 메일(USER-INFO-002) | 2026_10_15_000211 |
| `package_delivery_notice` | text | nullable | 패키지 상세 배송 안내(USER-LECT-003-S1 ④). 한 줄에 "항목: 내용". 비우면 화면 고정 문구 | 2026_10_16_000218 |
| `virtual_account_valid_hours` | unsignedSmallInteger |  | 가상계좌 입금 기한(발급 후 시간, 1~2160). 지나면 주문 자동 취소. 이미 발급된 계좌에는 적용되지 않음 | 2026_10_20_000226 |
| `pass_review_min_chars` | unsignedSmallInteger |  | 합격 수기 최소 글자 수(심사 참고 기준). 카페 비공개글은 서버가 읽을 수 없어 판정은 육안 | 2026_10_20_000234 |
| `pass_review_keep_months` | unsignedTinyInteger |  | 합격 수기 게시 유지 의무 기간(개월, 환급 지급 뒤) | 2026_10_20_000234 |
| `pass_review_clawback_rule` | string(500) | nullable | 유지 기간 안에 수기를 지우면 환급금을 회수하는 조건(안내 문구). 비우면 안내하지 않음 | 2026_10_20_000234 |
| `pg_recon_unclassified_max` | unsignedInteger |  | PG 대사 미분류(UNKNOWN_MISMATCH) 허용 건수. 초과하면 월 마감 화면에 경고(차단 아님 · DECISIONS 105). 기본 0건 | 2026_10_21_000236 |
| `pg_recon_tolerance_company` | unsignedInteger |  | PG 대사 전사 총액 차액 허용액(원). 절대값이 넘으면 월 마감 화면에 경고(차단 아님 · DECISIONS 105). 기본 1,000원 | 2026_10_21_000236 |

## terms
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_130001 |
| `type` | string(30) |  | 약관 종류: service/privacy/refund/marketing | 2026_07_16_130001 |
| `version` | integer |  | 개정판 버전 | 2026_07_16_130001 |
| `title` | string(255) |  | 제목 | 2026_07_16_130001 |
| `content` | longText |  | 본문 | 2026_07_16_130001 |
| `effective_date` | date | nullable | 시행일 | 2026_07_16_130001 |
| `is_active` | tinyInteger |  | 현재 시행 버전 여부 | 2026_07_16_130001 |
| `created_at` | timestamp |  |  | 2026_07_16_130001 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_130001 |
| `code` | string(10) | nullable | 약관 종류 코드. T01~T06 고정. 임의 추가·삭제하지 않는다. | 2026_09_08_000098 |
| `is_required` | boolean |  | 필수 약관 여부. 회원가입 STEP1 체크박스 필수/선택과 1:1. 기본값 1. | 2026_09_08_000098 |
| `notice_date` | date | nullable | 공시 일자. 사용자 공지 게시 시작일. 시행일자와 분리 입력한다. | 2026_09_08_000098 |
| `change_reason` | string(500) | nullable | 개정 사유. 필수. 사용자 공지사항 본문과 재동의 안내 메시지 요약문으로 재사용한다. | 2026_09_08_000098 |
| `status` | string(20) |  | active=시행중 / pending=공시중(시행 전) / expired=폐지 / draft=작성중(임시저장). 기본값 active. | 2026_09_08_000098 |
| `admin_id` | unsignedBigInteger | nullable | 최종 수정자 users.id. 목록의 최종 수정자 컬럼. | 2026_09_08_000098 |
| `is_unfavorable` | boolean |  | 회원에게 불리한 개정 여부. 1 이면 공시 기준 30일, 0 이면 7일 | 2026_10_02_000182 |

## popups
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_130002 |
| `title` | string(255) |  | 팝업명 | 2026_07_16_130002 |
| `image_path` | string(255) | nullable | 팝업 이미지 | 2026_07_16_130002 |
| `link_url` | string(500) | nullable | 클릭 이동 URL | 2026_07_16_130002 |
| `pos_x` | integer | nullable | 위치 X(px) | 2026_07_16_130002 |
| `pos_y` | integer | nullable | 위치 Y(px) | 2026_07_16_130002 |
| `width` | integer | nullable | 너비(px) | 2026_07_16_130002 |
| `height` | integer | nullable | 높이(px) | 2026_07_16_130002 |
| `start_at` | dateTime | nullable | 노출 시작 | 2026_07_16_130002 |
| `end_at` | dateTime | nullable | 노출 종료 | 2026_07_16_130002 |
| `device` | string(10) |  | 노출 대상: all/pc/mobile | 2026_07_16_130002 |
| `use_today_close` | tinyInteger |  | 오늘 하루 안보기 사용 | 2026_07_16_130002 |
| `sort_order` | integer |  | 노출 순서 | 2026_07_16_130002 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_07_16_130002 |
| `created_at` | timestamp |  |  | 2026_07_16_130002 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_130002 |
| `mobile_image_path` | string(255) | nullable | 모바일 이미지. 등록하지 않으면 PC 이미지가 축소 노출된다. | 2026_09_08_000098 |
| `alt_text` | string(255) | nullable | 이미지 대체 텍스트(alt). 웹접근성 필수. | 2026_09_08_000098 |
| `mobile_alt_text` | string(255) | nullable | 모바일 이미지 대체 텍스트(alt). | 2026_09_08_000098 |
| `link_target` | string(10) |  | 링크 타겟. _blank=새 창 / _self. 기본값 _self. | 2026_09_08_000098 |
| `use_week_close` | boolean |  |  | 2026_09_08_000098 |
| `use_close_button` | boolean |  |  | 2026_09_08_000098 |
| `position_type` | string(20) |  | 노출 위치. center=화면 중앙 / custom=pos_x·pos_y 지정. 기본값 center. | 2026_09_08_000098 |
| `link_type` | string(10) |  | 클릭 연결 방식: url(링크 직접 입력) / post(등록된 게시물 선택) | 2026_10_02_000181 |
| `post_id` | unsignedBigInteger | nullable | 연결 게시글(posts.id). link_type=post 일 때만. 팝업 → 게시글 단방향 | 2026_10_02_000181 |

## banners
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_16_130003 |
| `position` | string(30) | change | 노출 위치 | 2026_07_28_000003 |
| `title` | string(255) |  | 배너명 | 2026_07_16_130003 |
| `image_path` | string(255) | nullable | PC 이미지 | 2026_07_16_130003 |
| `mobile_image_path` | string(255) | nullable | 모바일 이미지 | 2026_07_16_130003 |
| `link_url` | string(500) | nullable | 클릭 이동 URL | 2026_07_16_130003 |
| `start_at` | dateTime | nullable | 노출 시작 | 2026_07_16_130003 |
| `end_at` | dateTime | nullable | 노출 종료 | 2026_07_16_130003 |
| `sort_order` | integer |  | 노출 순서 | 2026_07_16_130003 |
| `is_active` | tinyInteger |  | 사용 여부 | 2026_07_16_130003 |
| `created_at` | timestamp |  |  | 2026_07_16_130003 |
| `updated_at` | timestamp | nullable |  | 2026_07_16_130003 |
| `link_target` | string(10) |  | 링크 오픈 방식(_self/_blank) | 2026_07_28_000001 |
| `device` | string(10) |  | 노출 기기. all=공통 / pc / mobile. 기본값 all. | 2026_09_08_000098 |
| `alt_text` | string(255) | nullable | PC 이미지 대체 텍스트(alt). 웹접근성 필수. | 2026_09_08_000098 |
| `mobile_alt_text` | string(255) | nullable | 모바일 이미지 대체 텍스트(alt). | 2026_09_08_000098 |
| `target` | string(10) |  | 노출 대상(띠배너): all 전체 · guest 비로그인 · member 로그인. 이미지 배너는 all | 2026_10_15_000212 |
| `bg_color` | char(7) | nullable | 띠배너 배경색 #RRGGBB. 이미지 배너는 NULL | 2026_10_15_000212 |
| `text_color` | char(7) | nullable | 띠배너 글자색 #RRGGBB. 이미지 배너는 NULL | 2026_10_15_000212 |

## coupon_memo_histories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_07_23_000002 |
| `coupon_id` | foreignId |  | coupons.id 참조 | 2026_07_23_000002 |
| `memo` | string(500) | nullable | 해당 시점의 비고 값(빈 값이면 NULL) | 2026_07_23_000002 |
| `admin_id` | foreignId | nullable | 작성/수정한 관리자 users.id | 2026_07_23_000002 |
| `created_at` | timestamp |  |  | 2026_07_23_000002 |

## points
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 포인트 적립 건 ID | 2026_08_14_000001 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000001 |
| `type` | string(20) |  | paid=유상 / free=무상 | 2026_08_14_000001 |
| `amount` | integer |  | 최초 적립액. 불변 | 2026_08_14_000001 |
| `balance` | integer |  | 현재 잔여액. 음수 허용(마이너스 채권) | 2026_08_14_000001 |
| `source` | string(30) |  | signup / purchase / event / cs / restore / clawback | 2026_08_14_000001 |
| `source_order_id` | unsignedBigInteger | nullable | 구매 적립 시 원 주문 ID. FK는 Set 3 이후 추가 | 2026_08_14_000001 |
| `restored_from_id` | unsignedBigInteger | nullable | 부활분이면 원본 적립 건 ID (self) | 2026_08_14_000001 |
| `expires_at` | dateTime |  | 개별 소멸 예정 시각 | 2026_08_14_000001 |
| `expired_at` | dateTime | nullable | 실제 소멸 처리 시각 | 2026_08_14_000001 |
| `admin_id` | unsignedBigInteger | nullable | CS 수동 지급 처리자 users.id | 2026_08_14_000001 |
| `memo` | text | nullable | CS 수동 지급 사유 | 2026_08_14_000001 |
| `created_at` | timestamp |  | 적립 일시 | 2026_08_14_000001 |
| `updated_at` | timestamp | nullable | 잔여액 갱신 일시 | 2026_08_14_000001 |

## point_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 포인트 원장 ID | 2026_08_14_000002 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000002 |
| `point_id` | unsignedBigInteger | nullable | 움직인 적립 건. points.id 참조 | 2026_08_14_000002 |
| `action` | string(20) |  | earn / use / expire / clawback / restore / offset | 2026_08_14_000002 |
| `amount` | integer |  | 부호 포함. +적립·부활 / -사용·소멸·회수 | 2026_08_14_000002 |
| `balance_after` | integer |  | 기록 시점 총 잔액. 감사용 | 2026_08_14_000002 |
| `order_id` | unsignedBigInteger | nullable | 관련 주문 ID. FK는 Set 3 이후 추가 | 2026_08_14_000002 |
| `refund_id` | unsignedBigInteger | nullable | 환불 회차 식별. FK는 Set 3 이후 추가 | 2026_08_14_000002 |
| `idempotency_key` | string(100) | nullable | 재시도 중복 차단 키 | 2026_08_14_000002 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 users.id | 2026_08_14_000002 |
| `reason` | text | nullable | 사유 | 2026_08_14_000002 |
| `created_at` | timestamp |  | 기록 일시 | 2026_08_14_000002 |

## point_consumptions
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 소진 매칭 ID | 2026_08_14_000003 |
| `usage_log_id` | unsignedBigInteger |  | 사용 원장 행. point_logs.id 참조 | 2026_08_14_000003 |
| `point_id` | unsignedBigInteger |  | 어느 적립 건에서 빠졌는지. points.id 참조 | 2026_08_14_000003 |
| `amount` | integer |  | 빠진 금액 | 2026_08_14_000003 |
| `restored_amount` | integer |  | 그중 이미 부활된 누계 | 2026_08_14_000003 |
| `created_at` | timestamp |  | 기록 일시 | 2026_08_14_000003 |
| `updated_at` | timestamp | nullable | 부활 갱신 일시 | 2026_08_14_000003 |

## user_groups
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 회원 그룹 ID | 2026_08_14_000005 |
| `code` | string(50) |  | 그룹 코드 | 2026_08_14_000005 |
| `name` | string(100) |  | 태그명 | 2026_08_14_000005 |
| `description` | string(255) | nullable | 태그 설명 | 2026_08_14_000005 |
| `sort_order` | integer |  | 노출 순서 | 2026_08_14_000005 |
| `is_active` | boolean |  | 사용 여부 | 2026_08_14_000005 |
| `created_at` | timestamp |  | 등록 일시 | 2026_08_14_000005 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000005 |
| `group_type` | string(10) |  | 그룹 유형. static=명단 고정 / dynamic=조건 기반 재계산. | 2026_09_07_000061 |
| `assign_method` | string(10) |  | 부여 방식. auto=배치 자동 / manual=운영자 수동. | 2026_09_07_000061 |
| `condition_json` | json | nullable | 자동 태그·동적 그룹 조건식. 수동 태그는 NULL. | 2026_09_07_000061 |
| `last_synced_at` | timestamp | nullable | 자동 태그 배치 최종 갱신 일시. 매일 06:00 재계산. | 2026_09_07_000061 |
| `member_count` | unsignedInteger |  | 대상 회원 수 캐시. 조회 시점 실계산 부하 회피용. | 2026_09_07_000061 |
| `is_system` | boolean |  | 시스템 기본 태그 여부. 1이면 수정·삭제 불가. | 2026_09_07_000061 |
| `created_by` | unsignedBigInteger | nullable | 생성 관리자 users.id. 시스템 생성은 NULL. | 2026_09_07_000061 |
| `kind` | string(20) |  | 묶음 종류. tag=태그(S1) / saved_group=저장 그룹(S2). 기존 행은 전부 tag 다 | 2026_10_23_000251 |
| `axis` | string(20) |  | 태그 축. certificate=자격증 / learning=학습 상태 / campaign=캠페인. 계층이 아니라 분류 표기다 | 2026_10_23_000251 |
| `badge_color` | string(20) |  | 뱃지 색. gray / blue / green / orange / red / purple | 2026_10_23_000251 |
| `eval_cycle` | string(10) | nullable | 자동 태그 평가 주기. daily=매일 06:00 / weekly=매주 월 06:00 / monthly=매월 1일 06:00. 수동 태그는 NULL | 2026_10_23_000251 |
| `on_exit` | string(10) |  | 조건 이탈 시 처리. keep=유지 / release=자동 해제. 자동 태그만 쓴다 | 2026_10_23_000251 |
| `share_scope` | string(10) |  | 공유 범위. all=전체 운영자 / owner=본인만. 저장 그룹(S2)에서 쓴다 | 2026_10_23_000251 |

## user_group_members
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 매핑 ID | 2026_08_14_000006 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000006 |
| `user_group_id` | unsignedBigInteger |  | user_groups.id 참조 | 2026_08_14_000006 |
| `assigned_by` | unsignedBigInteger | nullable | 부여 관리자 users.id | 2026_08_14_000006 |
| `created_at` | timestamp |  | 부여 일시 | 2026_08_14_000006 |

## user_sanctions
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 제재 이력 ID | 2026_08_14_000007 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000007 |
| `type` | string(30) |  | lock=정지 / unlock=해제 | 2026_08_14_000007 |
| `reason` | text |  | 징계 사유 | 2026_08_14_000007 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 users.id | 2026_08_14_000007 |
| `released_at` | timestamp | nullable | 해제 일시 | 2026_08_14_000007 |
| `released_by` | unsignedBigInteger | nullable | 해제 처리자 users.id | 2026_08_14_000007 |
| `created_at` | timestamp |  | 처리 일시 | 2026_08_14_000007 |
| `reason_type` | string(30) | nullable | 정형 사유. concurrent_ip / concurrent_session / speed_tamper / minus_point / other | 2026_09_28_000167 |
| `ends_at` | timestamp | nullable | 정지 종료 예정 일시. NULL 이면 영구 정지(lock 행 한정) | 2026_09_28_000167 |

## user_withdrawals
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 탈퇴 이력 ID | 2026_08_14_000008 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000008 |
| `reason_type` | string(50) | nullable | 탈퇴 사유 구분 | 2026_08_14_000008 |
| `reason` | text | nullable | 상세 사유 | 2026_08_14_000008 |
| `void_points` | integer |  | 소멸 마일리지 | 2026_08_14_000008 |
| `void_coupons` | integer |  | 소멸 쿠폰 수 | 2026_08_14_000008 |
| `withdrawn_at` | timestamp |  | 탈퇴 처리 일시 | 2026_08_14_000008 |
| `created_at` | timestamp |  | 기록 일시 | 2026_08_14_000008 |
| `void_free_points` | integer |  | 소멸 무상 포인트. 가입 축하금·관리자 수동 지급분. | 2026_09_08_000105 |
| `void_paid_points` | integer |  | 소멸 유상 포인트. 실결제로 적립된 분. | 2026_09_08_000105 |
| `void_course_count` | integer |  | 소멸 수강중 강좌 수. 잔여 수강 기간이 모두 소멸되며 환불되지 않는다. | 2026_09_08_000105 |
| `void_course_days` | integer |  | 소멸 잔여 수강일 합계. 화면에 "잔여 138일" 형태로 숫자를 노출한다. | 2026_09_08_000105 |
| `pending_delivery_count` | integer |  | 탈퇴 시점 미배송 주문 건수. 익명화로 배송지가 파기되어 배송 불가가 된다. | 2026_09_08_000105 |
| `pending_refund_count` | integer |  | 탈퇴 시점 진행 중 환불 건수. 반품 검수·PG 취소가 중단될 수 있어 완료 후 탈퇴를 권장한다. | 2026_09_08_000105 |
| `ip` | string(45) | nullable | 탈퇴 요청 IP. | 2026_09_08_000105 |
| `di_hash` | string(64) | nullable | 탈퇴 시점 본인인증 DI의 SHA-256 해시(users.di_hash 와 같은 값). 재가입 횟수 · 탈퇴 시점 계정 집계 기준 | 2026_10_07_000200 |

## notification_templates
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 템플릿 ID | 2026_08_14_000009 |
| `code` | string(50) |  | 이벤트 코드. join_complete / order_paid / withdraw 등 | 2026_08_14_000009 |
| `name` | string(100) |  | 템플릿명 | 2026_08_14_000009 |
| `channel` | string(20) |  | alimtalk / sms / email | 2026_08_14_000009 |
| `provider_template_code` | string(100) | nullable | 카카오 승인 템플릿 코드 | 2026_08_14_000009 |
| `subject` | string(255) | nullable | 메일 제목 | 2026_08_14_000009 |
| `content` | text |  | 본문. 치환변수 포함 | 2026_08_14_000009 |
| `variables` | json | nullable | 치환변수 목록 | 2026_08_14_000009 |
| `is_active` | boolean |  | 사용 여부 | 2026_08_14_000009 |
| `created_at` | timestamp |  | 등록 일시 | 2026_08_14_000009 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000009 |
| `is_advertising` | tinyInteger |  | 광고성 여부. 1이면 마케팅 수신 동의자에게만 발송. 0=거래성(동의 무관) | 2026_08_14_000044 |
| `trigger_group` | string(30) | nullable | 발송 조건 분류. join / payment / delivery / point / inquiry / refund / marketing. 목록 검색 필터. | 2026_09_08_000096 |
| `send_timing` | string(100) | nullable | 발송 시점 설명. "가입 완료 즉시" / "PG 승인 직후" 등. 목록 표시 문구. | 2026_09_08_000096 |
| `use_fallback` | boolean |  | 대체 발송 사용 여부. 1이면 주 채널 실패 시 fallback_channel 로 재발송. 기본값 0. | 2026_09_08_000096 |
| `fallback_channel` | string(20) | nullable | 대체 채널. lms / sms. use_fallback=0 이면 NULL. | 2026_09_08_000096 |
| `fallback_content` | text | nullable | 대체 발송 본문. 알림톡 버튼 링크를 URL 로 풀어 쓴 LMS 전용 본문. | 2026_09_08_000096 |
| `approval_status` | string(20) |  | 카카오 심사 상태. none=심사 불필요(LMS·메일 전용) / pending=심사중 / approved=승인 / rejected=반려. 기본값 none. | 2026_09_08_000096 |
| `approval_reason` | string(500) | nullable | 심사 반려 사유. 목록 상태 옆에 노출하며 수정 후 재요청한다. | 2026_09_08_000096 |
| `approval_requested_at` | timestamp | nullable | 심사 요청 일시. | 2026_09_08_000096 |
| `approval_checked_at` | timestamp | nullable | 심사 상태 최종 조회 일시. 값이 낡으면 화면에 조회 실패로 표시한다. | 2026_09_08_000096 |
| `approved_content` | text | nullable | 직전 승인 본문. 심사중 상태에서는 이 본문으로 발송한다. 승인 시 content 로 갱신. | 2026_09_08_000096 |
| `is_required` | boolean |  | 필수 템플릿 여부. 1이면 삭제 불가(사용 중지만 가능). 거래성 알림 6종. 기본값 0. | 2026_09_08_000096 |
| `is_send_blocked` | boolean |  | 치환 변수 불일치로 인한 발송 차단 여부. 1이면 알림톡을 건너뛰고 LMS 대체로 넘긴다. 알림 자체는 누락되지 않는다. 기본값 0. | 2026_09_08_000097 |
| `block_reason` | string(500) | nullable | 발송 차단 사유. 매핑이 없는 치환 변수명을 담는다. 화면 경고 박스에 무엇을 고쳐야 하는지 변수명까지 노출한다. | 2026_09_08_000097 |
| `sens_synced_at` | timestamp | nullable | SENS 템플릿 원본 최종 동기화 일시. 목록의 최종 동기화 컬럼 표시값. | 2026_09_08_000097 |
| `buttons` | json | nullable | 카카오 승인 템플릿 버튼(SENS 동기화본). 발송 때 그대로 싣는다. [{type, name, linkMobile, linkPc, schemeIos, schemeAndroid}] · 없으면 NULL | 2026_10_21_000237 |

## notification_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 발송 이력 ID | 2026_08_14_000010 |
| `user_id` | unsignedBigInteger | nullable | users.id 참조. 비회원 발송 시 NULL | 2026_08_14_000010 |
| `template_id` | unsignedBigInteger | nullable | notification_templates.id 참조 | 2026_08_14_000010 |
| `channel` | string(20) |  | alimtalk / sms / email | 2026_08_14_000010 |
| `receiver` | string(255) |  | 수신 번호 또는 이메일 | 2026_08_14_000010 |
| `subject` | string(255) | nullable | 발송 제목 | 2026_08_14_000010 |
| `content` | text |  | 치환 완료된 실제 발송 내용 | 2026_08_14_000010 |
| `status` | string(30) |  | pending / sent / failed | 2026_08_14_000010 |
| `provider_message_id` | string(100) | nullable | 발송사 요청 ID | 2026_08_14_000010 |
| `error_message` | text | nullable | 실패 사유 | 2026_08_14_000010 |
| `retry_count` | unsignedTinyInteger |  | 재시도 횟수 | 2026_08_14_000010 |
| `sent_at` | timestamp | nullable | 발송 완료 일시 | 2026_08_14_000010 |
| `created_at` | timestamp |  | 기록 일시 | 2026_08_14_000010 |
| `campaign_id` | unsignedBigInteger | nullable | notification_campaigns.id 참조. 자동 발송(가입·결제 등)이면 NULL. | 2026_09_08_000096 |
| `is_fallback` | boolean |  | 대체 발송 건 여부. 1이면 주 채널 실패 후 전환된 건. 기본값 0. | 2026_09_08_000096 |
| `is_test` | boolean |  | 테스트 발송 여부. 통계 집계 제외. 기본값 0. | 2026_09_08_000096 |
| `fail_reason_code` | string(30) | nullable | 실패 사유 코드. unsubscribed / invalid_number / not_kakao_user / timeout / provider_error. 집계용. | 2026_09_08_000096 |
| `last_retry_at` | timestamp | nullable | 최종 재시도 일시. retry_count 만으로는 시점 추적이 안 된다. | 2026_09_08_000096 |
| `target_type` | string(30) | nullable | 알림 대상 종류(morphMap 별칭). inquiry / study_qna / product_qna 등. 대상이 없는 알림은 NULL | 2026_10_19_000219 |
| `target_id` | unsignedBigInteger | nullable | 알림 대상 ID — target_type 테이블의 id | 2026_10_19_000219 |

## delivery_batches
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 배치 ID | 2026_08_14_000012 |
| `batch_no` | string(50) |  | 회차 번호 | 2026_08_14_000012 |
| `type` | string(20) |  | export=출고지시 / import=송장회신 | 2026_08_14_000012 |
| `file_name` | string(255) | nullable | 원본 파일명 | 2026_08_14_000012 |
| `file_path` | string(500) | nullable | 저장 경로 | 2026_08_14_000012 |
| `total_count` | integer |  | 총 건수 | 2026_08_14_000012 |
| `success_count` | integer |  | 처리 성공 건수 | 2026_08_14_000012 |
| `fail_count` | integer |  | 처리 실패 건수 | 2026_08_14_000012 |
| `status` | string(30) |  | processing / completed / failed | 2026_08_14_000012 |
| `error_message` | text | nullable | 오류 메시지 | 2026_08_14_000012 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 users.id | 2026_08_14_000012 |
| `created_at` | timestamp |  | 생성 일시 | 2026_08_14_000012 |
| `completed_at` | timestamp | nullable | 완료 일시 | 2026_08_14_000012 |

## refund_claims
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 환급 신청 ID | 2026_08_14_000014 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000014 |
| `order_id` | unsignedBigInteger |  | 조회 편의용. FK는 Set 3 이후 추가 | 2026_08_14_000014 |
| `order_item_id` | unsignedBigInteger |  | 환급 대상 라인. FK는 Set 3 이후 추가 | 2026_08_14_000014 |
| `pass_proof_url` | string(500) | nullable | 합격 수기 아웃링크 | 2026_08_14_000014 |
| `bank_name` | string(50) |  | 입금 은행 | 2026_08_14_000014 |
| `account_no` | string(50) | nullable,change | 쓰지 않음 — 계좌번호는 account_no_enc 에 암호문으로 둔다 | 2026_10_07_000201 |
| `account_holder` | string(50) |  | 예금주 | 2026_08_14_000014 |
| `claim_amount` | integer |  | 신청 환급액 | 2026_08_14_000014 |
| `status` | string(30) |  | received / reviewing / approved / rejected | 2026_08_14_000014 |
| `reject_reason` | text | nullable | 반려 사유 | 2026_08_14_000014 |
| `admin_id` | unsignedBigInteger | nullable | 심사 관리자 users.id | 2026_08_14_000014 |
| `reviewed_at` | timestamp | nullable | 심사 일시 | 2026_08_14_000014 |
| `paid_at` | timestamp | nullable | 지급 일시 | 2026_08_14_000014 |
| `created_at` | timestamp |  | 신청 일시 | 2026_08_14_000014 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000014 |
| `progress_rate` | decimal(5, 2) | nullable | 심사 시점 진도율(%) 스냅샷 | 2026_08_14_000037 |
| `name_match_verified` | tinyInteger |  | 명의 3중 대조 통과 여부. 가입 회원명 = 합격증 성명 = 통장 예금주. 하나라도 불일치면 승인 불가. | 2026_09_08_000078 |
| `is_first_class_bank` | tinyInteger |  | 1금융권 계좌 여부. 0이면 상태를 계좌 보류로 두고 계좌 재등록을 요청한다. | 2026_09_08_000078 |
| `payout_method` | string(30) |  | 지급 방식. bank_transfer=무통장 계좌 이체(수동). | 2026_09_08_000078 |
| `reject_count` | unsignedInteger |  | 반려 차수. 회원이 재제출하면 누적되며 3회 이상이면 반복 반려로 표시한다. | 2026_09_08_000078 |
| `exam_round` | string(30) | nullable | 응시 회차. 예: 2026년 정기 산업안전기사 2회. 목록 필터 키. | 2026_09_08_000078 |
| `locked_by` | unsignedBigInteger | nullable | 심사 중인 관리자 users.id. 이중 승인은 곧 이중 지급이다. | 2026_09_08_000078 |
| `locked_at` | timestamp | nullable | 잠금 시각. 30분 무조작 시 자동 해제한다. | 2026_09_08_000078 |
| `review_url_platform` | string(500) | nullable | 외부 플랫폼 합격 수기 URL. 블로그·SNS 등. 게시글은 공개 상태여야 하며 심사 후 6개월간 유지해야 한다. | 2026_09_08_000105 |
| `review_url_cafe` | string(500) | nullable | 산준모 네이버 카페 합격 수기 URL. cafe.naver.com/sanjunmo 도메인 여부까지 검증한다. | 2026_09_08_000105 |
| `exam_year` | smallInteger | nullable | 합격 연도. 제출한 합격증의 응시 회차가 올패스 수강 기간과 일치하는지 심사할 때 사용한다. | 2026_09_08_000105 |
| `agree_fraud_terms_at` | timestamp | nullable | 부정 수급 동의 일시. 제출 서류가 사실과 다를 경우 환급 취소 및 부정 수급 환수에 동의. 미체크 시 제출 버튼이 비활성화된다. | 2026_09_08_000105 |
| `account_no_enc` | text | nullable | 계좌번호 암호문(Crypt). 평문 account_no 는 쓰지 않는다 | 2026_10_07_000201 |
| `verified_at` | timestamp | nullable | 증빙 · 진도율 · 수기 대조 완료 저장 시각. 일괄 승인 후보 조건 | 2026_10_07_000201 |
| `verified_by` | unsignedBigInteger | nullable | 대조 완료를 저장한 관리자 users.id | 2026_10_07_000201 |
| `payout_exported_at` | timestamp | nullable | 지급 대상 엑셀(대량이체) 최근 추출 시각. 재추출 경고 근거 | 2026_10_07_000201 |
| `payout_exported_by` | unsignedBigInteger | nullable | 지급 대상 엑셀을 최근 추출한 관리자 users.id | 2026_10_07_000201 |
| `review_url_platform_status` | unsignedSmallInteger | nullable | 플랫폼 수기 URL HTTP 응답 코드(배치 확인). 0=접속 실패 · NULL=미확인 또는 접속하지 않는 주소 | 2026_10_20_000233 |
| `review_url_cafe_status` | unsignedSmallInteger | nullable | 카페 수기 URL HTTP 응답 코드(배치 확인). 0=접속 실패 · NULL=미확인 | 2026_10_20_000233 |
| `review_url_checked_at` | timestamp | nullable | 수기 URL 응답 코드 최종 확인 시각 | 2026_10_20_000233 |
| `admin_memo` | text | nullable | 관리자 내부 메모(회원 비노출). 반려 사유와 별개 | 2026_10_20_000235 |
| `rs_deduct_amount` | integer | nullable | 4단계(DEDUCT) R/S 공제액. 옵션 A=0 확정 / B·C=NULL(분담비율 미정 · 113 ②) | 2026_10_26_000267 |
| `support_deduct_amount` | integer | nullable | 4·5단계 매출연동 개발지원금(Pipeline 5.1) 공제액. 옵션 A=0 확정 / B·C=NULL | 2026_10_26_000267 |
| `settlement_target_month` | char(7) | nullable | 정산 귀속월 YYYY-MM. 승인 확정일 기준이며 원 결제월로 소급하지 않는다 | 2026_10_26_000267 |
| `settle_review_status` | string(20) | nullable | 정산 차감 검수 상태. PENDING=검수 대기 / CONFIRMED=차감 확정 / HOLD=마감 보류(B·C 산식 미정) | 2026_10_26_000267 |
| `settle_reviewed_by` | unsignedBigInteger | nullable | 정산 차감 검수자 users.id | 2026_10_26_000267 |
| `settle_reviewed_at` | timestamp | nullable | 정산 차감 검수 일시 | 2026_10_26_000267 |

## logistics_settlements
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 물류 정산 ID | 2026_08_14_000015 |
| `settlement_month` | char(7) |  | 정산월 YYYY-MM | 2026_08_14_000015 |
| `our_delivery_count` | integer |  | 자사 집계 배송 건수 | 2026_08_14_000015 |
| `our_delivery_amount` | integer |  | 자사 집계 배송비 | 2026_08_14_000015 |
| `our_return_count` | integer |  | 자사 집계 반품 건수 | 2026_08_14_000015 |
| `our_return_amount` | integer |  | 자사 집계 반품비 | 2026_08_14_000015 |
| `billed_delivery_count` | integer |  | 3PL 청구 배송 건수 | 2026_08_14_000015 |
| `billed_delivery_amount` | integer |  | 3PL 청구 배송비 | 2026_08_14_000015 |
| `billed_return_count` | integer |  | 3PL 청구 반품 건수 | 2026_08_14_000015 |
| `billed_return_amount` | integer |  | 3PL 청구 반품비 | 2026_08_14_000015 |
| `book_cost_amount` | integer |  | 출판사 사입 원가 합계 | 2026_08_14_000015 |
| `diff_amount` | integer |  | 차액 | 2026_08_14_000015 |
| `status` | string(30) |  | draft / matched / mismatched / confirmed | 2026_08_14_000015 |
| `admin_id` | unsignedBigInteger | nullable | 확정 관리자 users.id | 2026_08_14_000015 |
| `confirmed_at` | timestamp | nullable | 확정 일시 | 2026_08_14_000015 |
| `memo` | text | nullable | 메모 | 2026_08_14_000015 |
| `created_at` | timestamp |  | 생성 일시 | 2026_08_14_000015 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000015 |
| `is_locked` | tinyInteger |  | 물류 정산 Lock. 재무 마감 순서 [2]단계. 매출 마감(SETT-004) 이후에만 잠글 수 있다. | 2026_09_08_000079 |

## pg_settlement_records
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | PG 원장 ID | 2026_08_14_000016 |
| `settlement_month` | char(7) |  | 정산월 YYYY-MM | 2026_08_14_000016 |
| `pg_provider` | string(50) |  | PG 제공자 | 2026_08_14_000016 |
| `payment_key` | string(255) | nullable | PG 결제 키 | 2026_08_14_000016 |
| `order_no` | string(50) | nullable | PG측 주문번호 | 2026_08_14_000016 |
| `approval_no` | string(100) | nullable | 승인번호 | 2026_08_14_000016 |
| `type` | string(20) |  | payment=승인 / cancel=취소 | 2026_08_14_000016 |
| `amount` | integer |  | PG 원장 금액 | 2026_08_14_000016 |
| `fee_amount` | integer |  | PG 수수료 | 2026_08_14_000016 |
| `approved_at` | dateTime | nullable | PG 승인 일시 | 2026_08_14_000016 |
| `raw_data` | json | nullable | PG 응답 원문 | 2026_08_14_000016 |
| `created_at` | timestamp |  | 적재 일시 | 2026_08_14_000016 |

## pg_reconciliations
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 매출 대사 ID | 2026_08_14_000017 |
| `settlement_month` | char(7) |  | 대사월 YYYY-MM | 2026_08_14_000017 |
| `our_count` | integer |  | 자사 DB 건수 | 2026_08_14_000017 |
| `our_amount` | integer |  | 자사 DB 금액 | 2026_08_14_000017 |
| `pg_count` | integer |  | PG 원장 건수 | 2026_08_14_000017 |
| `pg_amount` | integer |  | PG 원장 금액 | 2026_08_14_000017 |
| `mismatch_count` | integer |  | 불일치 건수 | 2026_08_14_000017 |
| `diff_amount` | integer |  | 차액 | 2026_08_14_000017 |
| `status` | string(30) |  | draft / matched / mismatched / confirmed | 2026_08_14_000017 |
| `is_locked` | boolean |  | 최종매출마감 확정 락 | 2026_08_14_000017 |
| `admin_id` | unsignedBigInteger | nullable | 확정 관리자 users.id | 2026_08_14_000017 |
| `confirmed_at` | timestamp | nullable | 확정 일시 | 2026_08_14_000017 |
| `created_at` | timestamp |  | 생성 일시 | 2026_08_14_000017 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000017 |

## pg_reconciliation_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 대사 상세 ID | 2026_08_14_000018 |
| `reconciliation_id` | unsignedBigInteger |  | pg_reconciliations.id 참조 | 2026_08_14_000018 |
| `pg_record_id` | unsignedBigInteger | nullable | pg_settlement_records.id 참조 | 2026_08_14_000018 |
| `payment_id` | unsignedBigInteger | nullable | payments.id 참조. FK는 Set 3 이후 추가 | 2026_08_14_000018 |
| `order_no` | string(50) | nullable | 매칭 키 | 2026_08_14_000018 |
| `our_amount` | integer | nullable | 자사 DB 금액 | 2026_08_14_000018 |
| `pg_amount` | integer | nullable | PG 원장 금액 | 2026_08_14_000018 |
| `diff_amount` | integer |  | 차액 | 2026_08_14_000018 |
| `match_status` | string(30) |  | matched / amount_diff / missing_ours / missing_pg | 2026_08_14_000018 |
| `memo` | text | nullable | 메모 | 2026_08_14_000018 |
| `created_at` | timestamp |  | 기록 일시 | 2026_08_14_000018 |
| `mismatch_reason_code` | string(30) | nullable | 차이 원인 코드. UNKNOWN_MISMATCH=미분류(마감 차단) / TIMING_GAP=기간 귀속차 / PARTIAL_CANCEL_PENDING=부분취소 대기 / PG_FEE_DIFF=PG 수수료 차감차 / REFUND_TIMING_DIFF=환불 처리 시차 (8.2절) | 2026_10_26_000266 |
| `explanation` | string(500) | nullable | 차이 소명 근거. 승인 시 최소 10자(감사 로그 필수 기록) | 2026_10_26_000266 |
| `approval_status` | string(20) |  | 소명 통제 상태. UNRESOLVED=미소명 / PENDING_APPROVAL=분류 완료·승인 대기 / APPROVED=소명 승인 완료 / MATCHED=차액 0원 | 2026_10_26_000266 |
| `approved_by` | unsignedBigInteger | nullable | 소명 승인 관리자 users.id | 2026_10_26_000266 |
| `approved_at` | timestamp | nullable | 소명 승인 일시 | 2026_10_26_000266 |
| `rights_holder_id` | unsignedBigInteger | nullable | 귀속 권리자 rights_holders.id. Gate 1 이 권리자 단위로 마감을 차단하는 축 | 2026_10_26_000266 |
| `pg_tid` | string(255) | nullable | PG 거래번호(토스 paymentKey). 화면 목록의 첫 칸이고 PG 문의 시 식별자다 | 2026_10_26_000266 |
| `paid_at` | dateTime | nullable | 결제 일시. 대사 축(paidOutDate)과 다르다 — 화면 정렬 · 월 경계 확인용 | 2026_10_26_000266 |

## cart_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 장바구니 항목 ID | 2026_08_14_000019 |
| `user_id` | unsignedBigInteger |  | users.id 참조 | 2026_08_14_000019 |
| `product_type` | string(20) |  | course / package / book | 2026_08_14_000019 |
| `product_id` | unsignedBigInteger |  | 상품 원본 ID | 2026_08_14_000019 |
| `quantity` | integer |  | book일 때만 수량 의미. course/package는 1 고정 | 2026_08_14_000019 |
| `created_at` | timestamp |  | 담은 일시 | 2026_08_14_000019 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_08_14_000019 |
| `package_id` | unsignedBigInteger | nullable | 패키지 구성품으로 담긴 경우 packages.id. 단품은 NULL. 분할 라인 그룹 키. | 2026_09_07_000070 |
| `line_price` | integer |  | 담는 시점 판매가 스냅샷. 패키지는 구성품 매핑으로 배분한 라인 금액을 고정한다. 이후 상품 판매가가 바뀌어도 장바구니 금액은 유지하며 주문서 진입 시 재검증한다. | 2026_09_08_000104 |
| `is_selected` | boolean |  | 선택 여부. 체크 해제는 삭제가 아니라 합산 대상에서만 빠진다. 서버에 저장해 새로고침·재접속에도 유지한다. | 2026_09_08_000104 |

## withdrawn_users_di
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_08_14_000039 |
| `withdrawn_at` | timestamp | nullable | 최근 탈퇴 일시. 30일 미경과 시 재가입 차단. 재가입 또는 30일 경과 배치로 NULL 처리 | 2026_08_14_000039 |
| `welcome_issued_at` | timestamp | nullable | 웰컴 혜택 최초 발급 일시. 생애 1회 제한 판정용. 초기화하지 않음 | 2026_08_14_000039 |
| `welcome_granted` | tinyInteger |  | 웰컴 혜택 지급 이력. 1이면 이 DI 로 가입 축하금·웰컴 쿠폰을 이미 받았다는 뜻이다. 재가입 시 지급하지 않는다. 생애 1회 판정 근거이므로 탈퇴 후에도 보존한다. | 2026_09_08_000085 |
| `di_hash` | string(64) | nullable,unique,change | 본인인증 DI의 SHA-256 해시(users.di_hash 와 같은 값). DI당 1행 유지 | 2026_09_29_000174 |
| `unpaid_paid_points` | integer |  | 미회수 유상 마이너스 포인트(절대값). 재가입 시 같은 유형으로 복원 후 0 초기화. 기본값 0. | 2026_10_22_000245 |
| `unpaid_free_points` | integer |  | 미회수 무상 마이너스 포인트(절대값). 재가입 시 같은 유형으로 복원 후 0 초기화. 기본값 0. | 2026_10_22_000245 |
| `rejoin_count` | unsignedInteger |  | 이 DI 로 재가입한 횟수. 탈퇴 후 다시 가입할 때 1 올린다. 부정 이용 판정 근거라 초기화하지 않는다. | 2026_10_22_000245 |

## user_agreements
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_08_14_000041 |
| `user_id` | foreignId |  | users.id 참조 | 2026_08_14_000041 |
| `type` | string(30) |  | 약관 구분. service=이용약관 / privacy=개인정보 수집·이용 / marketing=마케팅 수신 | 2026_08_14_000041 |
| `term_id` | foreignId | nullable | terms.id 참조. 동의 시점의 약관 원본 | 2026_08_14_000041 |
| `version` | string(20) | nullable | 동의 시점의 약관 버전. terms 삭제 시에도 이력 보존 | 2026_08_14_000041 |
| `is_agreed` | tinyInteger |  | 동의 여부. 선택 약관 철회 시 0으로 이력 추가 | 2026_08_14_000041 |
| `agreed_at` | timestamp |  | 동의 또는 철회 일시 | 2026_08_14_000041 |
| `ip` | string(45) | nullable | 동의 시점 접속 IP | 2026_08_14_000041 |
| `created_at` | timestamp |  | 등록 일시 | 2026_08_14_000041 |

## user_change_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_08_14_000042 |
| `user_id` | foreignId |  | users.id 참조 | 2026_08_14_000042 |
| `field` | string(50) |  | 변경 항목. email / phone / address / password 등 | 2026_08_14_000042 |
| `before_value` | text | nullable | 변경 전 값. 비밀번호 등 민감 항목은 마스킹 저장 | 2026_08_14_000042 |
| `after_value` | text | nullable | 변경 후 값. 비밀번호 등 민감 항목은 마스킹 저장 | 2026_08_14_000042 |
| `changed_by` | string(20) |  | 변경 주체. user=본인 / admin=관리자 | 2026_08_14_000042 |
| `admin_id` | foreignId | nullable | 관리자 변경 시 행위자 users.id | 2026_08_14_000042 |
| `ip` | string(45) | nullable | 접속 IP | 2026_08_14_000042 |
| `user_agent` | string(500) | nullable | 브라우저/기기 정보 | 2026_08_14_000042 |
| `created_at` | timestamp |  | 변경 일시 | 2026_08_14_000042 |

## inquiry_categories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_08_14_000043 |
| `code` | string(30) | unique | 분류 코드. payment / lecture / delivery / etc 등 | 2026_08_14_000043 |
| `name` | string(50) |  | 분류명. 사용자 화면 노출값 | 2026_08_14_000043 |
| `assign_role` | string(30) | nullable | 담당 부서 라우팅. admin_roles.code 참조값. NULL이면 미배정 | 2026_08_14_000043 |
| `sort_order` | integer |  | 노출 순서 | 2026_08_14_000043 |
| `is_active` | tinyInteger |  | 사용 여부. 0이면 신규 접수 시 선택 불가(기존 문의는 유지) | 2026_08_14_000043 |
| `parent_id` | unsignedBigInteger | nullable | 상위 대분류. inquiry_categories.id 자기참조. NULL이면 대분류. 하위 소분류가 남아 있는 대분류는 미사용으로 내릴 수 없다. | 2026_09_08_000087 |
| `target_screen` | string(50) | nullable | 자동 배정 화면코드. 이 분류로 접수되면 지정 관리자 화면의 처리 큐로 전개된다. 예) VOC-PAY-01(상담 필요)은 환불 관리 상세 뷰 ADMN-RFD-002-S1 로 간다. | 2026_09_08_000087 |

## verification_attempts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000050 |
| `tx_id` | string(100) | unique | 당사 발급 거래 식별자. PASS 콜백 대조용 멱등키. | 2026_09_07_000050 |
| `channel` | string(10) |  | pass=본인인증기관 / sms=자체 SMS 발송. | 2026_09_07_000050 |
| `purpose` | string(30) |  | find_id / find_pw / join / change_phone 등 인증 목적. | 2026_09_07_000050 |
| `user_type` | string(10) |  | user=사용자 / admin=관리자. | 2026_09_07_000050 |
| `phone` | string(20) | nullable | 인증된 휴대폰 번호. 요청 시점 미확보로 NULL 허용. | 2026_09_07_000050 |
| `di_hash` | string(64) | nullable | DI SHA-256 해시. 원문 미저장. | 2026_09_07_000050 |
| `ip` | string(45) | nullable | 요청 IP. TrustProxies 통과값 기준. | 2026_09_07_000050 |
| `user_agent` | string(500) | nullable | 브라우저/기기 정보. | 2026_09_07_000050 |
| `result` | string(20) |  | requested / success / fail / blocked. | 2026_09_07_000050 |
| `fail_reason` | string(100) | nullable | 실패·차단 사유 코드. | 2026_09_07_000050 |
| `reset_at` | timestamp | nullable | 카운트 초기화 일시. NULL이 아니면 하드캡 집계에서 제외. | 2026_09_07_000053 |
| `reset_by` | unsignedBigInteger | nullable | 초기화 처리 관리자 users.id. | 2026_09_07_000053 |

## password_histories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000052 |
| `user_id` | foreignId |  | users.id 참조. | 2026_09_07_000052 |
| `password_hash` | string(255) |  | 과거 비밀번호 해시. users.password 갱신 직전 값을 이관한다. | 2026_09_07_000052 |
| `created_at` | timestamp | nullable | 이력 적재 일시. | 2026_09_07_000052 |

## email_verifications
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000054 |
| `email` | string(100) |  | 수신 이메일 주소. | 2026_09_07_000054 |
| `type` | string(30) |  | admin_find_id / admin_find_pw 등 인증 목적. | 2026_09_07_000054 |
| `code_hash` | string(255) |  | 인증번호 해시. 평문 저장 금지. | 2026_09_07_000054 |
| `expires_at` | timestamp |  | 만료 일시. site_settings.verify_code_ttl_sec 기준. | 2026_09_07_000054 |
| `attempt_count` | unsignedTinyInteger |  | 검증 시도 횟수. verify_max_attempts 초과 시 세션 무효화. | 2026_09_07_000054 |
| `verified_at` | timestamp | nullable | 인증 완료 일시. | 2026_09_07_000054 |
| `invalidated_at` | timestamp | nullable | 세션 폐기 일시. 재발송 시 이전 행, 검증 성공 시 당해 행. | 2026_09_07_000054 |
| `ip` | string(45) | nullable | 요청 IP. TrustProxies 통과값 기준. | 2026_09_07_000054 |
| `created_at` | timestamp | nullable | 발송 일시. | 2026_09_07_000054 |

## remember_tokens
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000057 |
| `user_id` | foreignId |  | users.id 참조. | 2026_09_07_000057 |
| `token_hash` | string(255) | unique | 쿠키 토큰의 해시. 평문 저장 금지. | 2026_09_07_000057 |
| `rotated_from` | unsignedBigInteger | nullable | 직전 토큰 id. 회전 추적 및 재사용 탐지용. | 2026_09_07_000057 |
| `expires_at` | timestamp |  | 만료 일시. 사용자 30일 / 관리자 7일. | 2026_09_07_000057 |
| `revoked_at` | timestamp | nullable | 폐기 일시. 로그아웃·비밀번호 변경·탈퇴·재사용 탐지 시 세팅. | 2026_09_07_000057 |
| `last_used_at` | timestamp | nullable | 마지막 사용 일시. | 2026_09_07_000057 |
| `ip` | string(45) | nullable | 발급 시점 IP. TrustProxies 통과값 기준. | 2026_09_07_000057 |
| `user_agent` | string(500) | nullable | 발급 시점 브라우저/기기 정보. | 2026_09_07_000057 |
| `created_at` | timestamp | nullable | 발급 일시. | 2026_09_07_000057 |

## user_devices
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000060 |
| `user_id` | foreignId |  | users.id 참조. | 2026_09_07_000060 |
| `device_id` | string(100) |  | 플레이어 전달 Device UUID. | 2026_09_07_000060 |
| `device_type` | string(10) |  | 기기 구분. pc / mobile. | 2026_09_07_000060 |
| `os_version` | string(50) | nullable | OS 및 버전. windows / macos / android / ios 등. | 2026_09_07_000060 |
| `device_info` | string(255) | nullable | 브라우저·앱 버전 등 기기 상세 정보. | 2026_09_07_000060 |
| `ip` | string(45) | nullable | 최근 재생 IP. 접속 지역 추정 및 계정 공유 판단 참고. | 2026_09_07_000060 |
| `first_at` | timestamp | nullable | 최초 등록 일시. | 2026_09_07_000060 |
| `last_at` | timestamp | nullable | 최근 재생 일시. | 2026_09_07_000060 |
| `reset_at` | timestamp | nullable | 기기 리셋 처리 일시. | 2026_09_07_000060 |
| `reset_by` | unsignedBigInteger | nullable | 리셋 처리 관리자 users.id. | 2026_09_07_000060 |
| `reset_reason` | string(255) | nullable | 리셋 사유. 사유 없는 리셋은 불가. | 2026_09_07_000060 |

## instructor_profiles
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000063 |
| `instructor_id` | foreignId |  | instructors.id 참조. | 2026_09_07_000063 |
| `photo_path` | string(255) | nullable | 프로필 사진. 3:4 세로 비율 480×640 권장, 최대 2MB. | 2026_09_07_000063 |
| `display_name` | string(50) |  | 전시 강사명. 실명과 다른 활동명 사용 가능. 계약·정산은 항상 강사 ID 기준. | 2026_09_07_000063 |
| `title` | string(100) | nullable | 타이틀. 예: 산업안전 필기 대표강사. 프론트 탭 보조 문구로 사용. | 2026_09_07_000063 |
| `career` | text | nullable | 약력. 불릿 목록형. 외부 스크립트 금지. | 2026_09_07_000063 |
| `intro_text` | string(255) | nullable | 소개 텍스트. 목록 카드 요약 최대 120자. | 2026_09_07_000063 |
| `home_link_type` | string(10) |  | 강사 전용 홈 링크. internal=USER-INST-001 / external=아웃링크. | 2026_09_07_000063 |
| `home_url` | string(500) | nullable | 아웃링크 URL. external일 때만 사용하며 target=_blank로 연다. | 2026_09_07_000063 |
| `is_display` | boolean |  | 개별 전시 ON/OFF. 계약 상태가 우선하며 종료·해지 시 강제 숨김. | 2026_09_07_000063 |
| `sort_order` | integer |  | 강사 목록(USER-INST-002) 노출 순서. | 2026_09_07_000063 |
| `auto_preview` | boolean |  | 맛보기 자동 노출. 이 강사의 맛보기 ON 강의를 강사 홈에 자동 진열. | 2026_09_07_000063 |

## package_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000069 |
| `package_id` | foreignId |  | packages.id 참조. | 2026_09_07_000069 |
| `product_type` | string(20) |  | 구성품 유형. course=강좌 / book=교재. | 2026_09_07_000069 |
| `product_id` | unsignedBigInteger |  | courses.id 또는 books.id. | 2026_09_07_000069 |
| `sort_order` | integer |  | 구성품 노출 순서. | 2026_09_07_000069 |
| `original_price_snapshot` | integer |  | 저장 시점 구성품 원 정가 스냅샷. | 2026_09_07_000069 |
| `price_ratio` | decimal(5, 2) |  | 인강 라인 내 정가 비율(%). 할인 배분 기준. 교재는 0. | 2026_09_07_000069 |
| `discount_amount` | integer |  | 배분된 할인액(음수). 정가 비율대로 안분. 교재는 0. | 2026_09_07_000069 |
| `is_excluded_from_discount` | boolean |  | 할인 배분 제외 여부. 교재는 항상 1. 도서정가제 준수. | 2026_09_07_000069 |

## product_qnas
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000071 |
| `product_type` | string(20) |  | 문의 대상 상품 유형. book=교재 / course=강좌. | 2026_09_07_000071 |
| `product_id` | unsignedBigInteger |  | books.id 또는 courses.id. 상품 상세에서 문의 시 자동 매핑된다. | 2026_09_07_000071 |
| `user_id` | foreignId |  | 작성 회원 users.id. | 2026_09_07_000071 |
| `order_id` | unsignedBigInteger | nullable | 연결 주문 orders.id. 구매 이력이 있을 때만 세팅. | 2026_09_07_000071 |
| `inquiry_type` | string(30) | nullable,change | 문의 유형. composition=상품 구성 / price=가격·할인 / delivery=배송 / period=수강 기간 / etc=기타. 패키지 문의만 고르고 단과 · 교재는 NULL. 옛 문의는 damage=파손·오배송 / erratum=오탈자·내용오류 / stock=재고·재입고 / course=강좌수강 이 남아 있을 수 있다. | 2026_10_16_000217 |
| `title` | string(255) |  | 문의 제목. | 2026_09_07_000071 |
| `content` | longText |  | 문의 본문. | 2026_09_07_000071 |
| `assign_dept` | string(20) | nullable | 담당 부서. logistics=물류팀 / ta=조교 / cs=CS. | 2026_09_07_000071 |
| `assign_user_id` | unsignedBigInteger | nullable | 담당자 users.id. 미지정 건은 알림 대상이다. | 2026_09_07_000071 |
| `is_secret` | boolean |  | 비밀글 여부. 작성자 본인과 관리자만 열람. 파손·오배송 유형은 강제 1. | 2026_09_07_000071 |
| `status` | string(20) |  | 처리 상태. pending=미답변 / answered=답변완료 / hidden=숨김. | 2026_09_07_000071 |
| `answer_content` | longText | nullable | 답변 본문. | 2026_09_07_000071 |
| `answered_by` | unsignedBigInteger | nullable | 답변 등록 관리자 users.id. | 2026_09_07_000071 |
| `answered_at` | timestamp | nullable | 답변 등록 일시. | 2026_09_07_000071 |
| `deleted_at` | timestamp | nullable | 회원이 지운 시각. 사용자 화면에서만 빠지고 관리자 목록 · 집계에는 남는다. | 2026_10_16_000217 |

## study_qnas
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000072 |
| `user_id` | foreignId |  | 질문 회원 users.id. | 2026_09_07_000072 |
| `course_id` | foreignId |  | 질문 대상 강좌 courses.id. | 2026_09_07_000072 |
| `lecture_id` | foreignId |  | 질문 대상 강의 lectures.id. | 2026_09_07_000072 |
| `play_position_sec` | unsignedInteger | nullable | 질문 시점 재생 위치(초). 답변 화면에서 mm:ss로 표기. | 2026_09_07_000072 |
| `instructor_id` | foreignId |  | 담당 강사 instructors.id. 강사 계정은 본인 담당 강좌만 조회 가능. | 2026_09_07_000072 |
| `assign_ta_id` | unsignedBigInteger | nullable | 담당 조교 users.id. 조교 계정은 배정된 강사의 강좌만 조회 가능. | 2026_09_07_000072 |
| `title` | string(255) |  | 질문 제목. | 2026_09_07_000072 |
| `content` | longText |  | 질문 본문. | 2026_09_07_000072 |
| `status` | string(20) |  | 처리 상태. pending=미답변 / answered=답변완료 / escalated=강사확인(조교 에스컬레이션). | 2026_09_07_000072 |
| `answer_content` | longText | nullable | 답변 본문. 이미지·수식 첨부 지원. | 2026_09_07_000072 |
| `answered_by` | unsignedBigInteger | nullable | 답변 등록자 users.id. 답변자명은 답변 하단에 노출된다. | 2026_09_07_000072 |
| `answered_at` | timestamp | nullable | 답변 등록 일시. SLA(영업일 48시간) 판정 기준. | 2026_09_07_000072 |
| `is_public_qna` | boolean |  | 공개 Q&A 전환 여부. 1이면 강좌 상세에 마스킹 노출. | 2026_09_07_000072 |
| `is_secret` | boolean |  | 비밀글 여부. 1 = 작성자 본인 · 담당 강사 · 조교 · 최고 관리자만 열람. 공개 Q&A(is_public_qna) 전환 대상에서 제외 | 2026_10_20_000227 |
| `view_count` | unsignedInteger |  | 조회수. 회원 화면 상세를 연 횟수(같은 세션의 다시 열기는 세지 않는다). 목록 조회순 정렬 | 2026_10_20_000227 |

## reviews
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_07_000073 |
| `user_id` | foreignId |  | 작성 회원 users.id. 목록·상세에서 작성자명은 마스킹 노출. | 2026_09_07_000073 |
| `course_id` | foreignId |  | 수강 강좌 courses.id. | 2026_09_07_000073 |
| `instructor_id` | foreignId |  | 수강 강사 instructors.id. 강사 홈 노출 판정에 사용. | 2026_09_07_000073 |
| `title` | string(255) |  | 후기 제목. | 2026_09_07_000073 |
| `content` | longText |  | 후기 본문. | 2026_09_07_000073 |
| `rating` | unsignedTinyInteger | nullable | 별점(1~5). 회원 입력값. 관리자 수정 대상 아님. | 2026_09_07_000073 |
| `char_count` | unsignedInteger |  | 본문 글자수. 우수 후기 판정 기준(1,000자). | 2026_09_07_000073 |
| `exam_target_id` | unsignedBigInteger | nullable | 응시 종목 exam_targets.id. | 2026_09_07_000073 |
| `exam_round` | string(30) | nullable | 응시 회차. 예: 2026년 2회. | 2026_09_07_000073 |
| `pass_cert_path` | string(255) | nullable | 합격 증빙 이미지 경로. 성명·종목·회차 일치를 육안 검증한다. | 2026_09_07_000073 |
| `cafe_share_url` | string(500) | nullable | 네이버 카페 공유 아웃링크. | 2026_09_07_000073 |
| `cafe_verified_at` | timestamp | nullable | 카페 공유 확인 일시. HTTP 응답 코드로 판정하되 비공개글은 육안 확인. | 2026_09_07_000073 |
| `verify_status` | string(20) |  | 검증 상태. pending=검증대기 / verified=검증완료 / rejected=반려 / hidden=숨김. | 2026_09_07_000073 |
| `reject_reason` | string(255) | nullable | 반려 사유. 회원 마이페이지와 알림톡에 그대로 노출된다. | 2026_09_07_000073 |
| `verified_by` | unsignedBigInteger | nullable | 검증 처리 관리자 users.id. | 2026_09_07_000073 |
| `verified_at` | timestamp | nullable | 검증 처리 일시. | 2026_09_07_000073 |
| `is_best` | boolean |  | 베스트 선정 여부. | 2026_09_07_000073 |
| `display_site` | boolean |  | 사이트 후기 목록 노출 여부. | 2026_09_07_000073 |
| `display_instructor_home` | boolean |  | 강사 홈 노출 여부. 해당 강사 수강생 후기만 가능. | 2026_09_07_000073 |
| `refund_claim_id` | unsignedBigInteger | nullable | 연계 환급 신청 refund_claims.id. 반려 시 환급 심사도 함께 막힌다. | 2026_09_07_000073 |
| `point_granted_at` | timestamp | nullable | 우수 후기 포인트 지급 일시. 같은 후기에 대한 지급은 1회로 제한. | 2026_09_07_000073 |

## delivery_batch_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 배치 상세 ID. | 2026_09_08_000077 |
| `batch_id` | unsignedBigInteger |  | delivery_batches.id 참조. | 2026_09_08_000077 |
| `row_no` | unsignedInteger |  | 원본 엑셀 행 번호. 사용자가 파일에서 바로 찾을 수 있어야 한다. | 2026_09_08_000077 |
| `order_no` | string(50) | nullable | 입력된 주문번호. | 2026_09_08_000077 |
| `line_no` | unsignedInteger | nullable | 입력된 주문 라인번호. | 2026_09_08_000077 |
| `order_item_id` | unsignedBigInteger | nullable | 매칭 성공 시 order_items.id. | 2026_09_08_000077 |
| `carrier` | string(30) | nullable | 입력된 택배사 코드. | 2026_09_08_000077 |
| `tracking_no` | string(100) | nullable | 입력된 운송장번호. | 2026_09_08_000077 |
| `shipped_at` | date | nullable | 입력된 출고일자. | 2026_09_08_000077 |
| `shipped_qty` | unsignedInteger | nullable | 입력된 출고수량. | 2026_09_08_000077 |
| `result` | string(20) |  | 처리 결과. success / fail. | 2026_09_08_000077 |
| `error_code` | string(10) | nullable | 실패 코드. E01 주문번호 불일치 / E02 이미 처리됨 / E03 필수값 누락 / E04 형식 오류 / E05 상태 불일치 / E06 운송장 중복. | 2026_09_08_000077 |
| `error_message` | string(255) | nullable | 실패 사유·조치 안내. | 2026_09_08_000077 |
| `memo` | string(100) | nullable | 엑셀 비고 컬럼. 관리자 메모로 적재하며 고객에게 노출하지 않는다. | 2026_09_08_000077 |
| `created_at` | timestamp | nullable | 기록 일시. | 2026_09_08_000077 |

## logistics_settlement_items
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 물류 대사 상세 ID. | 2026_09_08_000079 |
| `settlement_id` | unsignedBigInteger |  | logistics_settlements.id 참조. | 2026_09_08_000079 |
| `shipped_at` | date | nullable | 출고일. | 2026_09_08_000079 |
| `tracking_no` | string(100) | nullable | 송장번호. 3PL 명세서와의 매칭 키. | 2026_09_08_000079 |
| `order_no` | string(50) | nullable | 주문번호. | 2026_09_08_000079 |
| `delivery_id` | unsignedBigInteger | nullable | deliveries.id 참조. 매칭 성공 시. | 2026_09_08_000079 |
| `receiver_name` | string(50) | nullable | 수령인. | 2026_09_08_000079 |
| `quantity` | unsignedInteger |  | 수량. | 2026_09_08_000079 |
| `type` | string(20) |  | 구분. delivery=출고 / return=반품. | 2026_09_08_000079 |
| `our_shipped` | tinyInteger |  | 자사 DB 출고 기록 존재 여부. | 2026_09_08_000079 |
| `billed` | tinyInteger |  | 3PL 청구 존재 여부. | 2026_09_08_000079 |
| `unit_price` | integer |  | 건당 단가. | 2026_09_08_000079 |
| `diff_amount` | integer |  | 차액. | 2026_09_08_000079 |
| `match_status` | string(30) |  | matched=일치 / billed_only=3PL만 존재 / ours_only=DB만 존재 / qty_diff=수량 차이 / price_diff=단가 차이. | 2026_09_08_000079 |
| `memo` | text | nullable | 불일치 처리 메모. 사유 없이 종결할 수 없다. | 2026_09_08_000079 |
| `created_at` | timestamp | nullable | 기록 일시. | 2026_09_08_000079 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000079 |

## book_purchase_costs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 도서 매입 원가 ID. | 2026_09_08_000079 |
| `settlement_id` | unsignedBigInteger |  | logistics_settlements.id 참조. | 2026_09_08_000079 |
| `book_id` | unsignedBigInteger |  | books.id 참조. | 2026_09_08_000079 |
| `book_name` | string(255) |  | 집계 시점 교재명 스냅샷. | 2026_09_08_000079 |
| `publisher` | string(100) | nullable | 출판사. | 2026_09_08_000079 |
| `sold_qty` | unsignedInteger |  | 판매 수량. | 2026_09_08_000079 |
| `returned_qty` | unsignedInteger |  | 반품 수량. | 2026_09_08_000079 |
| `net_qty` | integer |  | 순 판매 수량. 판매 − 반품. | 2026_09_08_000079 |
| `unit_cost` | integer |  | 권당 사입 원가. ADMN-PROD-004 등록값 기준. | 2026_09_08_000079 |
| `total_cost` | integer |  | 월 매입 원가. 순 판매 × 권당 원가. | 2026_09_08_000079 |
| `match_status` | string(30) |  | matched=일치 / calc_diff=계산서 차이. 출판사 세금계산서(매입 채무)와 대조한 결과. | 2026_09_08_000079 |
| `memo` | text | nullable | 차이 사유 메모. | 2026_09_08_000079 |
| `created_at` | timestamp | nullable | 기록 일시. | 2026_09_08_000079 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000079 |

## pg_fee_rates
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | PG 수수료율 ID. | 2026_09_08_000079 |
| `pg_provider` | string(50) |  | PG 제공자. | 2026_09_08_000079 |
| `payment_method` | string(30) |  | 결제 수단. card / naverpay / kakaopay. | 2026_09_08_000079 |
| `fee_rate` | decimal(5, 2) |  | 계약 수수료율(%). 정률 방식. | 2026_09_08_000079 |
| `fee_fixed` | integer |  | 건당 정액 수수료(원). 정액 방식일 때 사용하며 정률과 병용하지 않는다. | 2026_09_08_000079 |
| `applied_from` | date |  | 적용 시작일. 계약이 개정되어도 과거 월의 요율은 바뀌지 않는다. | 2026_09_08_000079 |
| `applied_to` | date | nullable | 적용 종료일. NULL이면 현재 적용 중. | 2026_09_08_000079 |
| `admin_id` | unsignedBigInteger | nullable | 등록 관리자 users.id. | 2026_09_08_000079 |
| `memo` | text | nullable | 메모. | 2026_09_08_000079 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000079 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000079 |

## promotions
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 기획전 ID. Auto Increment. | 2026_09_08_000083 |
| `code` | string(30) | unique | 기획전 코드. PRM-YYMM-{일련} 형식 자동 채번. 등록 후 수정 불가. 정산·통계 집계 키다. | 2026_09_08_000083 |
| `type` | string(20) |  | 구분자. promotion=기획전(기획상품) / event=이벤트(일반이벤트). 사용자 목록 카드 뱃지 색과 탭 필터가 이 값으로 갈린다. 기본값 promotion. | 2026_09_08_000083 |
| `title` | string(255) |  | 기획전명. 랜딩 상단 h1 과 목록 카드 제목에 동시 사용한다. | 2026_09_08_000083 |
| `slug` | string(40) | unique | URL 식별자. 영문 소문자·숫자·하이픈만 2~40자. sanjunmo.com/event/{slug} 로 Dynamic Routing 된다. 종료·중단 기획전의 slug 도 점유 상태로 본다. 재사용 시 옛 랜딩 링크가 오작동한다. | 2026_09_08_000083 |
| `started_at` | dateTime |  | 노출 시작. 분 단위까지 저장한다. 자정으로만 두면 0시 오픈 이벤트와 실제 전환 시점이 어긋난다. 서버 저장은 KST 고정. | 2026_09_08_000083 |
| `ended_at` | dateTime |  | 노출 종료. 종료 시각에 랜딩이 비노출된다. | 2026_09_08_000083 |
| `status` | string(20) |  | 상태. scheduled=예약 / active=진행중 / ended=종료 / stopped=중단(관리자 강제). 노출 기간과 배치로 자동 전환되며 직접 입력하지 않는다. | 2026_09_08_000083 |
| `thumbnail_path` | string(255) | nullable | 목록 썸네일. 720×405 16:9 권장, 1MB 이하. USER-PROM-001 카드에 쓰인다. | 2026_09_08_000083 |
| `banner_pc_path` | string(255) | nullable | 랜딩 배너 PC. 1920×480 권장, 2MB 이하. | 2026_09_08_000083 |
| `banner_mobile_path` | string(255) | nullable | 랜딩 배너 모바일. 750×600 권장. 미등록 시 PC 이미지를 축소 사용하되 저장 시 경고한다. | 2026_09_08_000083 |
| `headline` | string(255) | nullable | 상단 카피. 미입력 시 기획전명으로 자동 채운다. | 2026_09_08_000083 |
| `sort_type` | string(20) |  | 상품 진열 순서. manual=수동 정렬(드래그) / sales=판매량순 / price_asc=낮은 가격순 / created_desc=등록 역순. 기본값 manual. | 2026_09_08_000083 |
| `html_content` | longText | nullable | 랜딩 소스 HTML. CodeMirror 3분할 에디터 입력값을 가공 없이 그대로 적재한다. | 2026_09_08_000083 |
| `css_content` | longText | nullable | 랜딩 소스 CSS. 저장 시 #sanjunmo-promotion-wrapper 스코프를 자동 접두한다. body 등 전역 셀렉터가 GNB·푸터 레이아웃을 오염시키는 사고를 막는다. | 2026_09_08_000083 |
| `js_content` | longText | nullable | 랜딩 소스 JS. script 블록 안에서만 실행하며 document.write 와 z-index 900 초과 지정은 저장 시 경고한다. | 2026_09_08_000083 |
| `admin_id` | unsignedBigInteger | nullable | 최종 수정 관리자 users.id. | 2026_09_08_000083 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000083 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000083 |
| `css_scoped` | longText | nullable | 스코핑 변환 완료 CSS. #sanjunmo-promotion-wrapper 접두 + z-index 900 클램프 적용본. 렌더 전용이며 편집 화면은 css_content 를 읽는다. | 2026_09_08_000101 |

## promotion_products
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 기획전 대상 상품 ID. Auto Increment. | 2026_09_08_000083 |
| `promotion_id` | unsignedBigInteger |  | promotions.id 참조. | 2026_09_08_000083 |
| `product_type` | string(20) |  | 상품 유형. course=강좌 / package=패키지 / book=교재. | 2026_09_08_000083 |
| `product_id` | unsignedBigInteger |  | courses.id / packages.id / books.id. | 2026_09_08_000083 |
| `original_price_snapshot` | integer |  | 저장 시점 정가 스냅샷. 이후 원 정가가 바뀌어도 기획전 할인율 계산 근거는 변하지 않는다. | 2026_09_08_000083 |
| `promo_price` | integer |  | 기획전가. 교재 라인은 도서정가제로 입력이 비활성이며 정가가 그대로 들어온다. | 2026_09_08_000083 |
| `discount_rate` | decimal(5, 2) |  | 할인율(%). 기획전가 또는 할인율 중 한쪽 입력 시 나머지를 원 단위 절사로 자동 계산한다. | 2026_09_08_000083 |
| `sort_no` | integer |  | 진열 순서. promotions.sort_type 이 manual 일 때 드래그 순서를 그대로 저장한다. | 2026_09_08_000083 |
| `block_coupon` | tinyInteger |  | 쿠폰 사용 차단. 1이면 주문서 쿠폰 선택 레이어에서 해당 라인이 적용 대상에서 제외된다. 보유 쿠폰은 소멸되지 않는다. 기본값 0. | 2026_09_08_000083 |
| `block_point` | tinyInteger |  | 포인트 사용 차단. 1이면 해당 라인 금액만큼 포인트 사용 가능 한도에서 제외한다. 복합 주문이면 차단되지 않은 라인 금액 한도까지는 사용 가능하다. 기본값 0. | 2026_09_08_000083 |
| `block_earn` | tinyInteger |  | 구매 적립 차단. 1이면 결제는 되지만 유상 적립을 주지 않는다. 기본값 0(적립 지급). | 2026_09_08_000083 |
| `block_from` | dateTime | nullable | 차단 시작. 노출 기간과 독립적으로 잡을 수 있다. 예) 기획전은 한 달, 차단은 첫 2주만. NULL이면 노출 기간과 동일. | 2026_09_08_000083 |
| `block_to` | dateTime | nullable | 차단 종료. | 2026_09_08_000083 |
| `block_reason` | string(100) | nullable | 사용자 노출 차단 사유. 40자 이내 권장. 주문서(USER-PAY-001) 혜택 입력란 아래에 그대로 출력되므로 비활성만 시키고 사유를 안 쓰면 CS 문의가 폭증한다. | 2026_09_08_000083 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000083 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000083 |

## coupon_targets
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 쿠폰 적용 대상 ID. Auto Increment. | 2026_09_08_000084 |
| `coupon_id` | unsignedBigInteger |  | coupons.id 참조. | 2026_09_08_000084 |
| `target_type` | string(20) |  | 대상 유형. all=전체 상품 / category=카테고리 / course=강좌 / package=패키지 / book=교재. 카테고리와 개별 상품을 병용할 수 있다. | 2026_09_08_000084 |
| `target_id` | unsignedBigInteger | nullable | 대상 ID. target_type 에 따라 categories.id / courses.id / packages.id / books.id. target_type=all 이면 NULL. | 2026_09_08_000084 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000084 |

## inquiry_category_roles
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 분류-부서 매핑 ID. Auto Increment. | 2026_09_08_000087 |
| `category_id` | unsignedBigInteger |  | inquiry_categories.id 참조. | 2026_09_08_000087 |
| `role_code` | string(30) |  | 담당 부서 코드. admin_roles 코드 참조값. cs / finance / logistics / instructor 등. 화면은 복수 선택이며 선택한 부서 모두에 접수 알림이 발송되고 각 부서 처리 큐에 함께 올라간다. | 2026_09_08_000087 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000087 |

## inquiries
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 문의 ID. Auto Increment. | 2026_09_08_000087 |
| `inquiry_no` | string(30) | unique | 문의번호. QNA-YYYY-{일련} 형식 자동 채번. 사용자·관리자 화면과 알림톡에 공통 노출한다. | 2026_09_08_000087 |
| `category_id` | unsignedBigInteger | nullable | 문의 분류. inquiry_categories.id 참조. 소분류를 지정한다. 관리자가 분류를 바꾸면 담당 부서 큐가 실시간으로 이관된다. | 2026_09_08_000087 |
| `user_id` | unsignedBigInteger | nullable | 문의 회원 users.id. 제휴·광고 문의(USER-INFO-002)는 비회원 접수라 NULL이다. | 2026_09_08_000087 |
| `guest_company` | string(100) | nullable | 비회원 접수 회사·기관명. user_id 가 NULL 일 때 사용한다. | 2026_09_08_000087 |
| `guest_name` | string(50) | nullable | 비회원 담당자명. | 2026_09_08_000087 |
| `guest_phone` | string(20) | nullable | 비회원 연락처. | 2026_09_08_000087 |
| `guest_email` | string(100) | nullable | 비회원 이메일. | 2026_09_08_000087 |
| `title` | string(255) |  | 문의 제목. | 2026_09_08_000087 |
| `content` | longText |  | 문의 본문. | 2026_09_08_000087 |
| `assign_user_id` | unsignedBigInteger | nullable | 담당자 users.id. 미지정 건에 [답변] 진입 시 자동으로 본인에게 배정된다. 배정 대상은 운영자 권한 관리에서 지정한 계정으로 한정한다. | 2026_09_08_000087 |
| `status` | string(20) |  | 처리 상태. received=접수(미답변) / processing=처리중(담당자 확인 시작) / answered=답변완료 / hold=보류(타 부서 확인 대기). | 2026_09_08_000087 |
| `hold_reason` | string(255) | nullable | 보류 사유. 상태가 hold 일 때 필수다. 사유 없는 보류는 저장을 거부한다. | 2026_09_08_000087 |
| `hold_until` | date | nullable | 보류 재개 예정일. 필수다. 무기한 보류로 방치되는 것을 막는다. 보류 중에는 SLA 시계가 멈추고 알림톡도 나가지 않는다. | 2026_09_08_000087 |
| `answer_content` | longText | nullable | 답변 본문. | 2026_09_08_000087 |
| `draft_content` | longText | nullable | 답변 임시저장 초안. 상태·알림톡 변화 없이 작성자 본인만 조회한다. | 2026_09_08_000087 |
| `answered_by` | unsignedBigInteger | nullable | 답변 등록 관리자 users.id. | 2026_09_08_000087 |
| `answered_at` | timestamp | nullable | 답변 등록 일시. SLA(영업일 24시간) 판정 기준. | 2026_09_08_000087 |
| `internal_memo` | text | nullable | 내부 메모. 회원 화면에 노출하지 않으며 알림톡에도 포함하지 않는다. 물류팀 확인 요청 같은 내부 판단을 여기에 쓴다. | 2026_09_08_000087 |
| `created_at` | timestamp | nullable | 문의 접수 일시. 경과 시간 산출 기준. | 2026_09_08_000087 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000087 |
| `inquiry_type` | string(30) | nullable | 문의 분류. payment_refund / course_error / book_delivery / etc. 담당팀 라우팅 키. | 2026_09_08_000102 |
| `sub_type` | string(30) | nullable | 하위 분류. consult=상담필요(관리자 판단) / partial=부분 환불 / full=전액 환불. 결제·환불 유형에서만 사용. | 2026_09_08_000102 |
| `assign_board` | string(30) | nullable | 배정 게시판 화면코드. ADMN-BRD-002 / 003 / 004. inquiry_type 으로 자동 결정한다. | 2026_09_08_000102 |
| `order_id` | unsignedBigInteger | nullable | 관련 주문 orders.id. 결제·환불 및 파손·교재 배송 유형에서 선택한다. | 2026_09_08_000102 |
| `order_item_id` | unsignedBigInteger | nullable | 관련 주문 라인 order_items.id. 파손·교재 배송 유형에서 교재 상품을 특정한다. | 2026_09_08_000102 |
| `course_id` | unsignedBigInteger | nullable | 관련 강좌 courses.id. 수강 오류 유형에서 선택한다. | 2026_09_08_000102 |
| `privacy_agreed_at` | timestamp | nullable | 개인정보 수집·이용 동의 일시. 문의 처리 목적의 별도 동의이며 답변 완료 후 3년 보존한다. | 2026_09_08_000102 |
| `refund_hold_reason` | string(30) | nullable | 결제 · 환불 문의 판정 전 환불보류 사유 코드(refunds.hold_reason 과 같은 값). 판정 저장 시 비운다 | 2026_10_20_000232 |
| `refund_hold_memo` | string(500) | nullable | 판정 전 환불보류 메모(내부용 · 회원 비노출) | 2026_10_20_000232 |
| `refund_held_at` | timestamp | nullable | 판정 전 환불보류 시작 시각. 값이 있으면 환불보류. 답변 상태(status)와 별개 | 2026_10_20_000232 |

## faq_categories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | FAQ 카테고리 ID. Auto Increment. | 2026_09_08_000088 |
| `name` | string(50) |  | 카테고리명. 사용자 FAQ 목록(USER-CS-001) 좌측 트리에 그대로 노출한다. | 2026_09_08_000088 |
| `sort_order` | integer |  | 노출 순서. 기본값 0. | 2026_09_08_000088 |
| `is_active` | tinyInteger |  | 사용 여부. 하위 FAQ 가 남아 있는 카테고리는 삭제할 수 없다. 먼저 다른 카테고리로 옮겨야 한다. 기본값 1. | 2026_09_08_000088 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000088 |
| `updated_at` | timestamp | nullable | 수정 일시. | 2026_09_08_000088 |

## faqs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | FAQ ID. Auto Increment. | 2026_09_08_000088 |
| `category_id` | unsignedBigInteger |  | faq_categories.id 참조. | 2026_09_08_000088 |
| `question` | string(100) |  | 질문. 100자 이내. 아코디언 접힘 상태의 제목이 된다. 검색 대상은 이 값뿐이며 답변 본문은 HTML 이 섞여 있어 검색하지 않는다. | 2026_09_08_000088 |
| `answer` | longText |  | 답변 HTML. 사용자 FAQ 목록의 아코디언 확장 패널에 그대로 렌더링된다. 저장·출력 양쪽에서 script 태그와 on* 이벤트 속성을 제거한다. | 2026_09_08_000088 |
| `weight` | unsignedSmallInteger |  | 가중치 정렬. 0~999. 숫자가 클수록 위에 노출한다. 같은 값이면 최근 등록순. 드래그 정렬을 두지 않고 숫자 입력으로만 받는다. 카테고리를 넘나드는 정렬이라 드래그로는 의도를 표현할 수 없다. | 2026_09_08_000088 |
| `is_visible` | tinyInteger |  | 사용자 화면 노출 여부. 0이면 저장은 유지되고 사용자 FAQ 목록에서만 사라진다. 삭제와 구분한다. 기본값 1. | 2026_09_08_000088 |
| `admin_id` | unsignedBigInteger | nullable | 최종 수정 관리자 users.id. | 2026_09_08_000088 |
| `created_at` | timestamp | nullable | 등록 일시. | 2026_09_08_000088 |
| `updated_at` | timestamp | nullable | 최종 수정 일시. 목록에 노출한다. | 2026_09_08_000088 |
| `view_count` | unsignedInteger |  | 조회수. 아코디언 펼침 시 +1 하되 같은 세션에서는 1회만 증가시킨다. 목록 기본 정렬 키. | 2026_09_08_000102 |

## instructor_assistants
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000095 |
| `user_id` | unsignedBigInteger |  | 조교 계정 users.id. | 2026_09_08_000095 |
| `instructor_id` | unsignedBigInteger |  | 소속 강사 instructors.id. 학습 Q&A 조회 범위를 결정한다. | 2026_09_08_000095 |
| `created_at` | timestamp |  | 배정 일시. | 2026_09_08_000095 |

## notification_campaigns
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000096 |
| `template_id` | unsignedBigInteger |  | notification_templates.id 참조. 발송 템플릿. | 2026_09_08_000096 |
| `admin_id` | unsignedBigInteger |  | 등록 관리자 users.id. | 2026_09_08_000096 |
| `send_reason` | string(200) |  | 발송 사유(내부). 필수. 감사·정산 근거로 이력 목록에 노출한다. 고객에게는 나가지 않는다. | 2026_09_08_000096 |
| `filter_params` | json | nullable | 타겟 선정 조건. ADMN-USER-006 그룹/태그 필터를 그대로 사용한다. 재현 및 감사용 스냅샷. | 2026_09_08_000096 |
| `total_count` | integer |  | 필터 조회 총 인원. | 2026_09_08_000096 |
| `excluded_agree_count` | integer |  | 마케팅 수신 미동의 제외 인원. is_marketing_agreed=0. | 2026_09_08_000096 |
| `excluded_unsub_count` | integer |  | 광고 수신거부 제외 인원. 웹 수신거부(unsub_token) 처리분. | 2026_09_08_000096 |
| `target_count` | integer |  | 최종 발송 대상 인원. | 2026_09_08_000096 |
| `estimated_count` | integer |  | 예상 발송 건수. 대체 발송 전환분을 포함한 합계. | 2026_09_08_000096 |
| `scheduled_at` | timestamp | nullable | 예약 발송 일시. 즉시 발송이면 NULL. 광고성은 21:00~익일 08:00 지정 불가. | 2026_09_08_000096 |
| `status` | string(20) |  | scheduled=예약 / processing=발송중 / completed=완료 / canceled=취소 / failed=실패. 기본값 scheduled. | 2026_09_08_000096 |
| `success_count` | integer |  | 발송 성공 건수. | 2026_09_08_000096 |
| `fail_count` | integer |  | 발송 실패 건수. | 2026_09_08_000096 |
| `fallback_count` | integer |  | 대체 발송 전환 건수. 알림톡 → LMS. | 2026_09_08_000096 |
| `started_at` | timestamp | nullable | 발송 시작 일시. | 2026_09_08_000096 |
| `finished_at` | timestamp | nullable | 발송 종료 일시. | 2026_09_08_000096 |
| `canceled_at` | timestamp | nullable | 취소 일시. 예약 30분 전까지만 취소 가능하다. | 2026_09_08_000096 |

## player_settings
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000098 |
| `watermark_use` | boolean |  | 워터마크 사용 여부. 기본값 1. | 2026_09_08_000098 |
| `watermark_content` | string(30) |  | 표시 내용. email=로그인 수험생 이메일 ID. 유출본이 돌아다닐 때 어느 계정에서 나갔는지 특정한다. | 2026_09_08_000098 |
| `watermark_move_interval` | unsignedSmallInteger |  | positionChangeInterval. 초마다 무작위 좌표 이동. 기본값 10. | 2026_09_08_000098 |
| `watermark_display_duration` | unsignedSmallInteger |  | displayDuration. 초간 노출 후 숨김. move_interval 이하여야 하며 서버에서 검증한다. 기본값 5. | 2026_09_08_000098 |
| `watermark_opacity` | unsignedTinyInteger |  | 투명도(%). 너무 낮으면 억제 효과가 없고 높으면 학습을 방해한다. 권장 30~40. 기본값 35. | 2026_09_08_000098 |
| `watermark_font_size` | unsignedTinyInteger |  | 글자 크기(px). 기본값 14. | 2026_09_08_000098 |
| `watermark_mobile_same` | boolean |  | 모바일 앱 동일 적용 여부. 0이면 별도 설정. 기본값 1. | 2026_09_08_000098 |
| `limit_forward` | boolean |  | limitedForward. 앞으로 건너뛰기 제한. 전 강좌 일괄 적용이며 강좌별 예외는 두지 않는다. 기본값 1. | 2026_09_08_000098 |
| `limit_forward_free_off` | boolean |  | 무료 콘텐츠·맛보기 강의 예외. 구매 유도가 목적이므로 건너뛰기 제한을 적용하지 않는다. 기본값 1. | 2026_09_08_000098 |
| `speed_min` | decimal(3, 2) |  | 재생 배속 최소. 선택 가능 단계 0.5 / 0.75 / 1.0 / 1.25 / 1.5 / 1.75 / 2.0. | 2026_09_08_000098 |
| `speed_max` | decimal(3, 2) |  | 재생 배속 최대. min > max 는 저장 차단. 2.0 초과는 진도 인정 기준과 충돌한다. | 2026_09_08_000098 |
| `progress_speed_policy` | string(20) |  | 진도 인정 배속. all=전 배속 인정 / limited=일부 배속만 인정. 기본값 all. | 2026_09_08_000098 |
| `resume_use` | boolean |  | 이어보기 사용 여부. 기본값 1. | 2026_09_08_000098 |
| `resume_offset_sec` | unsignedSmallInteger |  | 마지막 재생 위치에서 N초 전부터 재생. 기본값 5. | 2026_09_08_000098 |
| `rewind_allow` | boolean |  | 10초 뒤로(되감기) 허용 여부. 복습을 막을 이유가 없어 제한 대상이 아니다. 기본값 1. | 2026_09_08_000098 |
| `device_pc_limit` | unsignedTinyInteger |  | 계정당 PC 등록 대수. DRM 라이선스 발급 조건이자 계정 공유를 막는 핵심 통제다. 기본값 1. | 2026_09_08_000098 |
| `device_mobile_limit` | unsignedTinyInteger |  | 계정당 모바일 등록 대수. 기본값 1. 합산 2대로 관리하지 않고 종류별 1대로 관리한다. | 2026_09_08_000098 |
| `device_reset_limit` | unsignedTinyInteger |  | 단말 초기화 허용 횟수(연 기준). 초과분은 CS 승인으로 처리한다. 기본값 1. | 2026_09_08_000098 |
| `concurrent_session` | unsignedTinyInteger |  | 동시 재생 허용 세션 수. 후속 로그인 시 이전 세션을 강제 종료한다. 기본값 1. | 2026_09_08_000098 |
| `drm_method` | string(50) |  | DRM 방식. StarPlayer+ Widevine / FairPlay 외부 연동. | 2026_09_08_000098 |
| `block_record_mobile` | boolean |  | 모바일 앱 화면 녹화 차단 여부. 기본값 1. | 2026_09_08_000098 |
| `warn_capture_pc` | boolean |  | PC 캡처 감지 경고 여부. 기본값 1. | 2026_09_08_000098 |
| `download_allow` | boolean |  | 다운로드 수강 허용 여부. DRM 정책·저작권과 직결되어 기본 미허용. 기본값 0. | 2026_09_08_000098 |

## book_restock_alerts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000100 |
| `book_id` | unsignedBigInteger |  | books.id 참조. 알림 대상 교재. | 2026_09_08_000100 |
| `user_id` | unsignedBigInteger |  | 신청자 users.id. 로그인 필수이며 가입 시 수집한 휴대전화로 발송한다. | 2026_09_08_000100 |
| `status` | string(20) |  | waiting=대기 / notified=발송 완료 / canceled=신청 취소. 기본값 waiting. | 2026_09_08_000100 |
| `notified_at` | timestamp | nullable | 알림 발송 일시. 재고가 0 -> 1 이상으로 변경되는 시점에 기록한다. | 2026_09_08_000100 |
| `canceled_at` | timestamp | nullable | 신청 취소 일시. | 2026_09_08_000100 |

## faq_search_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000102 |
| `keyword` | string(100) |  | 검색어. 결과 0건인 경우만 적재한다. | 2026_09_08_000102 |
| `category_id` | unsignedBigInteger | nullable | 검색 시 선택된 카테고리 faq_categories.id. 전체 검색이면 NULL. | 2026_09_08_000102 |
| `user_id` | unsignedBigInteger | nullable | 검색자 users.id. 비로그인 검색이면 NULL. FAQ 는 비로그인 열람이 가능하다. | 2026_09_08_000102 |
| `created_at` | timestamp |  | 검색 일시. | 2026_09_08_000102 |

## drm_violation_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000103 |
| `user_id` | unsignedBigInteger |  | 수강생 users.id. | 2026_09_08_000103 |
| `course_id` | unsignedBigInteger | nullable | 강좌 courses.id. | 2026_09_08_000103 |
| `lecture_id` | unsignedBigInteger | nullable | 차시 lectures.id. | 2026_09_08_000103 |
| `violation_type` | string(30) |  | 감지 유형. screen_record=화면 녹화 / screen_capture=캡처 도구 / virtual_machine=가상 PC / concurrent=중복 접속. | 2026_09_08_000103 |
| `detect_code` | string(30) | nullable | 감지 코드. DRM-CAP-0231 형식. 화면에 노출하며 CS 상담 시 이 코드로 로그를 즉시 대조한다. | 2026_09_08_000103 |
| `device_uuid` | string(100) | nullable | 단말 UUID. 단순 기기 교체와 계정 공유를 구분하는 지표다. | 2026_09_08_000103 |
| `ip` | string(45) | nullable | 감지 시점 IP. | 2026_09_08_000103 |
| `position_sec` | unsignedInteger | nullable | 감지 시점 재생 위치(초). 이 시점까지의 진도는 정상 저장한다. | 2026_09_08_000103 |
| `detected_at` | timestamp |  | 감지 일시. | 2026_09_08_000103 |

## order_agreements
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000104 |
| `order_id` | unsignedBigInteger |  | orders.id 참조. | 2026_09_08_000104 |
| `agreement_type` | string(30) |  | 동의 항목. pg_terms=결제 대행 및 전자금융거래 / privacy_third_party=개인정보 제3자 제공 / course_refund=강좌 수강 및 환불 규정. | 2026_09_08_000104 |
| `term_id` | unsignedBigInteger | nullable | terms.id 참조. 해당 시점 시행 중이던 약관 버전. | 2026_09_08_000104 |
| `version` | string(20) | nullable | 동의한 약관 버전 스냅샷. 분쟁 시 원문 재현용. | 2026_09_08_000104 |
| `agreed_at` | timestamp |  | 동의 일시. | 2026_09_08_000104 |

## user_addresses
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_08_000105 |
| `user_id` | unsignedBigInteger |  | 회원 users.id. | 2026_09_08_000105 |
| `label` | string(30) | nullable | 배송지 별칭. 집 / 회사 등. 사용자 자유 입력. | 2026_09_08_000105 |
| `receiver_name` | string(50) |  | 수령인. | 2026_09_08_000105 |
| `receiver_phone` | string(20) |  | 수령인 연락처. | 2026_09_08_000105 |
| `zipcode` | string(10) |  | 우편번호. 우편번호 검색 API 로 채우며 직접 타이핑을 허용하지 않는다. | 2026_09_08_000105 |
| `address` | string(255) |  | 기본주소(도로명). 검색 결과로만 채워지는 읽기전용 값이다. 직접 입력을 허용하면 3PL 엑셀 발주에서 주소 정규화가 깨져 오배송으로 이어진다. | 2026_09_08_000105 |
| `address_detail` | string(100) | nullable | 상세주소. 사용자가 직접 입력하는 유일한 주소 필드. | 2026_09_08_000105 |
| `delivery_request` | string(255) | nullable | 배송 요청사항. | 2026_09_08_000105 |
| `is_default` | boolean |  | 기본 배송지 여부. 회원당 1건만 1이며 삭제할 수 없다. 다른 주소를 기본으로 바꾼 뒤에만 삭제 가능하다. | 2026_09_08_000105 |

## rights_holders
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_15_000111 |
| `code` | string(20) | unique | 권리자 코드. AUTH-YYYY-NNNN. 등록 후 변경 불가. 채번은 RightsHolderCodeGenerator 단일 지점 | 2026_09_15_000111 |
| `name` | string(100) |  | 상호명 또는 실명. 국세청 등록명과 일치해야 한다 | 2026_09_15_000111 |
| `is_internal` | boolean |  | 자사 귀속 여부. true 면 정산 연산은 동일하게 하되 외부 이체·역발행에서 제외한다(합의서 02장) | 2026_09_15_000111 |
| `tax_type` | string(20) |  | personal=개인 / simplified=간이과세 / general=일반과세 / exempt=면세사업자 | 2026_09_15_000111 |
| `email` | string(100) | nullable | 정산 알림용 이메일 | 2026_09_15_000111 |
| `phone` | string(20) | nullable | 담당자 연락처 | 2026_09_15_000111 |
| `partnership_started_at` | date | nullable | 최초 파트너십 체결일 | 2026_09_15_000111 |
| `resident_no_enc` | text | nullable | 주민등록번호 13자리. AES-256 암호문. 평문 저장 금지(03장 3.2) | 2026_09_15_000111 |
| `is_resident` | boolean |  | 거주자 여부. 비거주자 정산은 합의서 12장 Phase 2 | 2026_09_15_000111 |
| `business_number` | string(30) | nullable | 사업자등록번호 | 2026_09_15_000111 |
| `ceo_name` | string(50) | nullable | 대표자명 | 2026_09_15_000111 |
| `biz_category` | string(100) | nullable | 업태 | 2026_09_15_000111 |
| `biz_item` | string(100) | nullable | 업종 | 2026_09_15_000111 |
| `biz_address` | string(255) | nullable | 사업장 주소 | 2026_09_15_000111 |
| `tax_invoice_eligible_yn` | boolean | nullable | 간이과세자의 세금계산서 발급 의무 여부. false 면 부가세 10%를 가산하지 않는다(합의서 02장) | 2026_09_15_000111 |
| `vat_treatment` | string(20) | nullable | 부가세 처리 방식. 간이·일반 대상. 상세 판정은 합의서 11장 | 2026_09_15_000111 |
| `tax_email` | string(100) | nullable | 세금계산서·계산서 수취 전용 이메일. 일반·면세 대상 | 2026_09_15_000111 |
| `bank_name` | string(50) | nullable | 정산 입금 은행 | 2026_09_15_000111 |
| `account_no_enc` | text | nullable | 정산 계좌번호. AES-256 암호문. 평문 저장 금지 | 2026_09_15_000111 |
| `account_holder` | string(50) | nullable | 예금주 | 2026_09_15_000111 |
| `payee_is_author` | boolean | nullable | 저작자 본인 여부. 개인(personal)만 사용한다. false 면 필요경비 의제 없음(합의서 2.3) | 2026_09_15_000117 |
| `address` | string(255) | nullable | 거주지 주소. 개인 권리자 지급명세서용 | 2026_09_15_000117 |
| `address_detail` | string(255) | nullable | 거주지 상세 주소 | 2026_09_15_000117 |
| `rights_holder_type` | string(20) |  | 주체 구분. RIGHTS_HOLDER=권리자 / CONSIGNOR=위탁자 (합의서 2.2). 매입처는 suppliers 로 분리 | 2026_09_18_000130 |
| `income_category` | string(20) | nullable | 소득 구분 상위 축. BUSINESS=사업소득 / OTHER=기타소득. 재화 공급 라인은 NULL (합의서 2.3) | 2026_09_18_000130 |
| `income_clause` | string(10) | nullable | 기타소득 호. C05·C15·C17·C19. income_category=OTHER 면 필수 (합의서 2.3) | 2026_09_18_000130 |
| `main_work_external_labor` | boolean |  | 주된 업무 외 노무 활용 여부. true 면 인적용역 면세 판정 보류 (합의서 6.4) | 2026_09_18_000130 |
| `business_status` | string(20) | nullable | 사업 상태. 계속 / 휴업 / 폐업. 국세청 API 응답 (합의서 2.1) | 2026_09_18_000130 |
| `tax_type_change_dt` | date | nullable | 최근 과세유형 전환일자. 국세청 API 응답 | 2026_09_18_000130 |
| `invoice_apply_dt` | date | nullable | 세금계산서 적용일자. 국세청 API 응답 | 2026_09_18_000130 |
| `api_checked_at` | timestamp | nullable | 국세청 조회 일시. 유효기간(기본 90일) 판정 기준 | 2026_09_18_000130 |
| `api_response_snapshot` | json | nullable | 국세청 API 응답 원문 | 2026_09_18_000130 |
| `consignment_fee_rate` | decimal(5, 2) | nullable | 위탁 수수료율(%). rights_holder_type=CONSIGNOR 전용 | 2026_09_18_000130 |
| `consignment_fee_type` | string(20) | nullable | 수수료 수취 방식. NET_DEDUCT=차감 지급(기본) / GROSS_SETTLE=총액 지급 후 청구 (합의서 6.6) | 2026_09_18_000130 |
| `consignment_cycle` | string(20) | nullable | 위탁 정산 주기 | 2026_09_18_000130 |
| `consignment_return_owner` | string(20) | nullable | 위탁 재고 회수 담당 주체 | 2026_09_18_000130 |
| `birth_date` | date | nullable | 개인 권리자 생년월일. 주민등록번호 앞 7자리에서 계산(App\Support\ResidentNo) · 화면 입력 칸 없음. | 2026_10_22_000246 |

## rights_holder_contracts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_15_000112 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_15_000112 |
| `code` | string(20) | unique | 계약 식별 번호. CT-YYYY-NNNN. 설계서 ADMN-INST-001 표기 | 2026_09_15_000112 |
| `title` | string(255) |  | 계약명 | 2026_09_15_000112 |
| `started_at` | date |  | 계약 개시일 | 2026_09_15_000112 |
| `ended_at` | date |  | 계약 만료일 | 2026_09_15_000112 |
| `status` | string(20) |  | pending=체결대기 / active=운용중 / expired=만료 / terminated=중도해지 | 2026_09_15_000112 |
| `terminated_at` | date | nullable | 중도해지일. status=terminated 일 때만 값이 있다 | 2026_09_15_000112 |
| `terminate_reason` | string(500) | nullable | 중도해지 사유. status=terminated 면 필수. 사유 없는 해지는 저장을 거부한다 | 2026_09_15_000112 |
| `auto_extend` | boolean |  | 자동 연장 여부. 연장 배치는 Set 4 | 2026_09_15_000112 |
| `is_locked` | boolean |  | 거래 발생 시 수정 차단. 거래 판정은 Set 4, 이번 차수는 플래그 저장·차단만 | 2026_09_15_000112 |
| `memo` | text | nullable | 메모 | 2026_09_15_000112 |
| `admin_id` | foreignId | nullable | 등록 관리자 users.id | 2026_09_15_000112 |
| `sequence_no` | unsignedInteger |  | 계약 차수. 권리자별 1부터 채번. 설계서 ⑤ 갱신 회차 | 2026_09_15_000116 |
| `prepayment_tax_type` | string(20) | nullable | 선급금 세무 처리. INCOME_PREPAY=소득 선지급(상계액을 과세표준에서 차감) / LOAN=대여금(차감 없음) (합의서 5.3) | 2026_09_18_000131 |
| `mmg_annual_cap` | integer | nullable | 연간 MMG 보전 총액 상한. 초과 시 알럿 후 재무 승인 대상 (합의서 5.3) | 2026_09_18_000131 |
| `refund_promo_burden_type` | string(1) |  | 환급 · 프로모션 부담 방식. A=플랫폼 전액 부담(기본) / B=R/S 지분율 비율 분담 / C=매출 취소 처리 (합의서 §15.1 · §15.3) | 2026_09_21_000150 |
| `successor_contract_id` | unsignedBigInteger | nullable | 승계 계약 rights_holder_contracts.id. 계약 종료 시 매핑 행의 contract_id 를 이 계약으로 교체한다(§5.4) | 2026_09_22_000161 |
| `succeeded_at` | date | nullable | 승계 실행일. 이 날 이후 발생분부터 승계 계약 요율이 적용된다. 이전 발생분의 환불 공제는 정산 스냅샷을 따른다(§5.4) | 2026_09_22_000161 |
| `origin_type` | string(20) |  | 계약 발생 구분 NEW(신규) / SUCCESSION(승계 — 선행 계약 이어받기) | 2026_10_02_000184 |
| `predecessor_contract_id` | unsignedBigInteger | nullable | 선행 계약 rights_holder_contracts.id. origin_type = SUCCESSION 일 때만. 요율은 이어받지 않는다 | 2026_10_02_000184 |
| `renewal_unit_years` | unsignedTinyInteger | nullable | 자동 갱신 단위(년) 1 · 2 · 3. auto_extend = 1 일 때만. 동일 조건 연장만 자동 갱신한다 | 2026_10_02_000184 |
| `vat_exception_reason` | string(255) | nullable | VAT 가산 예외 승인 사유. vat_exception_yn = 1 일 때 필수 | 2026_10_02_000186 |

## contract_rate_lines
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_15_000113 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_15_000113 |
| `started_at` | date |  | 요율 적용 개시일 | 2026_09_15_000113 |
| `ended_at` | date |  | 요율 적용 만료일 | 2026_09_15_000113 |
| `rate` | decimal(5, 2) |  | 수익 배분 요율(%) | 2026_09_15_000113 |
| `mmg_amount` | integer | nullable | 월 보장액(Minimum Monthly Guarantee). 보전 연산은 Set 4(합의서 08장) | 2026_09_15_000113 |
| `reason` | string(255) | nullable | 요율 적용 사유 | 2026_09_15_000113 |
| `rate_type` | string(20) |  | 요율 종류. BASIC=기본 R/S(8.3절 Step 3 바인딩 대상) / SUPPORT=지원금 S 라인 | 2026_09_18_000131 |
| `rate_basis` | string(30) | nullable | 산정 모수 NET_PG=순매출(PG 차감) / GROSS=결제 총액 / NET_PG_COUPON=순매출(PG+쿠폰 차감). 코드값 잠정 | 2026_10_02_000187 |
| `agreement_id` | unsignedBigInteger | nullable | support_fund_agreements.id 참조. SUPPORT 라인은 필수 · BASIC 은 NULL | 2026_10_22_000244 |

## instructor_categories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_17_000122 |
| `instructor_id` | unsignedBigInteger |  | 강사 instructors.id | 2026_09_17_000122 |
| `category_id` | unsignedBigInteger |  | 담당 과목. categories 1Depth(자격증 종목)만 허용한다 | 2026_09_17_000122 |

## suppliers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000126 |
| `code` | string(50) | unique | 매입처 코드 SUP-%05d(id). 채번은 Set 4 | 2026_09_18_000126 |
| `name` | string(100) |  | 상호 | 2026_09_18_000126 |
| `business_no` | string(20) | nullable | 사업자등록번호 | 2026_09_18_000126 |
| `ceo_name` | string(50) | nullable | 대표자명 | 2026_09_18_000126 |
| `open_date` | date | nullable | 개업일자 | 2026_09_18_000126 |
| `payee_tax_type` | string(20) | nullable | 국세청 과세유형 응답값. 매핑은 Set 4 | 2026_09_18_000126 |
| `business_status` | string(20) | nullable | 사업 상태. 계속 / 휴업 / 폐업 | 2026_09_18_000126 |
| `api_checked_at` | timestamp | nullable | 국세청 조회 일시 | 2026_09_18_000126 |
| `api_response_snapshot` | json | nullable | 국세청 API 응답 원문 | 2026_09_18_000126 |
| `bank_name` | string(50) | nullable | 은행명 | 2026_09_18_000126 |
| `account_no_enc` | text | nullable | 계좌번호 AES-256 암호화(제3장) | 2026_09_18_000126 |
| `account_holder` | string(50) | nullable | 예금주명 | 2026_09_18_000126 |
| `settlement_terms` | string(100) | nullable | 지급 조건. 예: 월말 마감 익월 15일 | 2026_09_18_000126 |
| `contact_email` | string(100) | nullable | 담당자 메일 | 2026_09_18_000126 |
| `cost_account_type` | string(30) |  | 원가 계정. INVENTORY_PURCHASE=재고자산 취득 / BUYOUT_RIGHT=무형 판권 취득 | 2026_09_18_000126 |
| `created_at` | timestamp |  |  | 2026_09_18_000126 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000126 |

## book_price_histories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000128 |
| `book_id` | foreignId |  | books.id 참조 | 2026_09_18_000128 |
| `price` | integer |  | 정가 | 2026_09_18_000128 |
| `effective_from` | date |  | 정가 시행일. 인세는 판매 확정일이 속한 버전을 바인딩한다 | 2026_09_18_000128 |
| `effective_to` | date | nullable | 적용 종료일. NULL 이면 현재 버전 | 2026_09_18_000128 |
| `price_owner` | string(20) |  | 정가 결정 권한. SELF=당사 / CONSIGNOR=위탁자(당사 화면에서 변경 불가) | 2026_09_18_000128 |
| `reason` | string(255) | nullable | 재정가 사유 | 2026_09_18_000128 |
| `admin_id` | unsignedBigInteger | nullable | 등록 관리자 users.id | 2026_09_18_000128 |
| `created_at` | timestamp |  |  | 2026_09_18_000128 |

## book_royalty_contracts
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000129 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_18_000129 |
| `book_id` | unsignedBigInteger |  | books.id 참조. book_supply_type=OWN_PUBLISHED 한정 | 2026_09_18_000129 |
| `royalty_rate` | decimal(5, 2) |  | 인세 기본 요율(%) | 2026_09_18_000129 |
| `royalty_basis` | string(20) |  | 인세 계산 기준선. LIST_PRICE=도서 정가 / ACTUAL_PAID=유저 실구매가(배송비 제외) | 2026_09_18_000129 |
| `started_at` | date |  | 적용 개시일 | 2026_09_18_000129 |
| `ended_at` | date |  | 적용 만료일 | 2026_09_18_000129 |
| `status` | string(20) |  | active=적용중 / ended=종료 | 2026_09_18_000129 |
| `memo` | string(255) | nullable | 비고 | 2026_09_18_000129 |
| `created_at` | timestamp |  |  | 2026_09_18_000129 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000129 |
| `temp_code` | string(20) | nullable | 출간 전 임시 관리코드 BK-REQ-YYYY-NNNN. SKU 연결 후에도 보존 | 2026_10_16_000215 |
| `book_title` | string(255) | nullable | 저서명(가제). SKU 미연결 구간의 표시 이름. 연결 후에는 books.title 을 쓴다 | 2026_10_16_000215 |
| `expected_publish_date` | date | nullable | 출간 예정일. 미정이면 NULL | 2026_10_16_000215 |

## support_fund_agreements
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000132 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_18_000132 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_18_000132 |
| `payee_id` | unsignedBigInteger | nullable | 2계층 수취인 rights_holders.id. NULL 이면 권리자 본인 | 2026_09_18_000132 |
| `payment_method` | string(20) |  | 지급 방식. LUMP_SUM=일시금 / INSTALLMENT=분할 / REVENUE_SHARE=매출연동(S 라인) | 2026_09_18_000132 |
| `total_cap_amount` | integer |  | 총 지원 한도. REVENUE_SHARE 는 필수 | 2026_09_18_000132 |
| `rate_basis` | string(30) | nullable | 요율 모수. 강좌 실결제액 / PG 차감 후 순매출 등 계약별 지정 | 2026_09_18_000132 |
| `settlement_scope` | string(20) |  | 모수 범위. TRACK_A_ONLY(기본) / TRACK_B1_ONLY / TRACK_A_B1. B-2 는 불가 (합의서 5.2) | 2026_09_18_000132 |
| `start_date` | date |  | 약정 개시일 | 2026_09_18_000132 |
| `end_date` | date |  | 약정 종료일 | 2026_09_18_000132 |
| `offset_type` | string(20) |  | 상계 여부. NON_OFFSET=비상계(기본) / CONDITIONAL=조건부 상계. REVENUE_SHARE 는 NON_OFFSET 고정 | 2026_09_18_000132 |
| `cap_restore_on_refund` | boolean |  | 환불 발생 시 한도 복원 여부. false 면 환불 많은 달에 한도가 영구 소실된다 | 2026_09_18_000132 |
| `on_termination_policy` | string(20) |  | 종료 시 미소진 잔액. FORFEIT=소멸(기본) / LUMP_SETTLE=일시 정산 / PRO_RATA=이행률 정산(수동) | 2026_09_18_000132 |
| `income_category` | string(20) | nullable | BUSINESS / OTHER. R/S 형 기본값 BUSINESS | 2026_09_18_000132 |
| `income_clause` | string(10) | nullable | 기타소득 호. income_category=OTHER 면 필수 | 2026_09_18_000132 |
| `status` | string(20) |  | ACTIVE=진행 / COMPLETED=한도 소진 / EXPIRED=미소진 만료 / TERMINATED=중도 해지 | 2026_09_18_000132 |
| `created_at` | timestamp |  |  | 2026_09_18_000132 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000132 |

## buyout_payments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000133 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_18_000133 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_18_000133 |
| `payee_id` | unsignedBigInteger | nullable | 2계층 수취인 rights_holders.id. NULL 이면 권리자 본인 | 2026_09_18_000133 |
| `buyout_amount` | integer |  | 매절 대금(세전) | 2026_09_18_000133 |
| `income_category` | string(20) |  | BUSINESS=사업소득 3.3%(기본) / OTHER=기타소득 | 2026_09_18_000133 |
| `income_clause` | string(10) | nullable | 기타소득 호. C15=저작자 본인(의제 60%) / C05=저작자 아닌 자(의제 없음) | 2026_09_18_000133 |
| `payee_is_author` | boolean |  | 저작자 본인 여부. false 면 C05 로 의제가 적용되지 않는다 | 2026_09_18_000133 |
| `milestone_id` | unsignedBigInteger | nullable | 약정금 마일스톤 ID. 검수 원장은 Set 4 | 2026_09_18_000133 |
| `target_month` | char(7) |  | 귀속월 YYYY-MM | 2026_09_18_000133 |
| `approval_status` | string(20) |  | 검수 상태. pending / approved / rejected. 소득 구분 미지정이면 승인할 수 없다(합의서 7.2) | 2026_09_18_000133 |
| `approver_id` | unsignedBigInteger | nullable | 승인 관리자 users.id | 2026_09_18_000133 |
| `taxable_base` | integer | nullable | 과세표준 | 2026_09_18_000133 |
| `withholding_income_tax` | integer | nullable | 원천징수 소득세 | 2026_09_18_000133 |
| `withholding_local_tax` | integer | nullable | 지방소득세. 소득세액의 10% | 2026_09_18_000133 |
| `payable_amount` | integer | nullable | 실지급액 | 2026_09_18_000133 |
| `created_at` | timestamp |  |  | 2026_09_18_000133 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000133 |

## carryover_ledgers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000134 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_18_000134 |
| `payee_id` | unsignedBigInteger | nullable | 수취인 rights_holders.id | 2026_09_18_000134 |
| `contract_id` | unsignedBigInteger | nullable | rights_holder_contracts.id | 2026_09_18_000134 |
| `origin_month` | char(7) |  | 발생 귀속월 YYYY-MM | 2026_09_18_000134 |
| `account_type` | string(10) |  | 계정 구분. PRE_TAX=세전(청구 하한 미달 음수) / POST_TAX=세후(지급 하한 미달 양수) | 2026_09_18_000134 |
| `track` | string(10) |  | 트랙 귀속. A=강의 R/S / B1=자사 인세 / B2=위탁 / S=지원금 / MIXED. 발생 월 값을 승계한다 | 2026_09_18_000134 |
| `income_category` | string(20) | nullable | 발생 월 소득 구분 승계 | 2026_09_18_000134 |
| `income_clause` | string(10) | nullable | 발생 월 기타소득 호 승계 | 2026_09_18_000134 |
| `reason` | string(30) |  | 이월 사유. payout_under=지급 하한 미달 / claim_under=청구 하한 미달 / post_close_fix=마감 후 정정 | 2026_09_18_000134 |
| `amount` | integer |  | 이월 금액. 세전 계정은 음수 | 2026_09_18_000134 |
| `is_expired` | boolean |  | 소멸 여부 | 2026_09_18_000134 |
| `expired_month` | char(7) | nullable | 소멸 반영월 YYYY-MM | 2026_09_18_000134 |
| `created_at` | timestamp |  |  | 2026_09_18_000134 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000134 |
| `payout_reservation_status` | string(10) |  | 지급 지시 예약 상태. NONE=예약 없음 / RESERVED=마감 시 예약 / SETTLED=이체 성공 확정. 기본값 NONE. | 2026_10_19_000224 |
| `settlement_line_id` | unsignedBigInteger | nullable | 이 이월을 만든 정산 라인 settlement_lines.id. NULL = 라인 없이 적재된 과거 행 | 2026_10_19_000224 |

## support_fund_ledgers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000138 |
| `agreement_id` | foreignId |  | support_fund_agreements.id 참조 | 2026_09_18_000138 |
| `target_month` | char(7) |  | 귀속월 YYYY-MM | 2026_09_18_000138 |
| `accrued_amount` | integer |  | 당월 발생액. 4단계(DEDUCT) 후 S 라인 순액 | 2026_09_18_000138 |
| `paid_amount` | integer |  | 당월 확정 지급액. MIN(발생액, 잔여 한도) | 2026_09_18_000138 |
| `cumulative_paid` | integer |  | 누계 지급액. 환불 복원 시 되돌린다 | 2026_09_18_000138 |
| `remaining_cap` | integer |  | 갱신 잔여 한도 = total_cap_amount − cumulative_paid | 2026_09_18_000138 |
| `status_change` | string(30) | nullable | 당월 상태 전이. 예: ACTIVE→COMPLETED, COMPLETED→ACTIVE(환불 복원) | 2026_09_18_000138 |
| `settlement_line_id` | unsignedBigInteger | nullable | 정산서 상세 라인 ID. 연결은 Set 4 | 2026_09_18_000138 |
| `created_at` | timestamp |  |  | 2026_09_18_000138 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000138 |
| `confirmed_amount` | integer |  | 당월 확정액(환불 공제 후). 세후 실제 지급액 paid_amount 와 구분한다 | 2026_10_19_000223 |
| `confirmed_net_total` | integer |  | 확정 · 환불 순누계. 한도 소진액(cap_consumed_amount)과 구분한다 | 2026_10_19_000223 |
| `cap_consumed_amount` | integer |  | 한도 소진액 누계. remaining_cap = total_cap_amount − 이 값 | 2026_10_19_000223 |
| `cash_paid_total` | integer |  | 실제 현금 지급 누계. 11단계 지급 확정분만 더한다 | 2026_10_19_000223 |

## mmg_subsidy_ledgers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000139 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_18_000139 |
| `contract_id` | unsignedBigInteger | nullable | rights_holder_contracts.id | 2026_09_18_000139 |
| `target_month` | char(7) |  | 귀속월 YYYY-MM | 2026_09_18_000139 |
| `mmg_amount` | integer |  | 약정 월 보장액. 요율 라인 스냅샷 | 2026_09_18_000139 |
| `accrued_amount` | integer |  | 판정 모수. Track A 순수 신규 R/S | 2026_09_18_000139 |
| `subsidy_amount` | integer |  | 보전금 = 월 보장액 − 판정 모수. 비상계 매몰 비용 | 2026_09_18_000139 |
| `promo_overlap_flag` | boolean |  | 환급반 옵션 B·C 차감과 동월 중복 발생. 재무 확인 대상(연산 차단 없음) | 2026_09_18_000139 |
| `annual_cumulative` | integer | nullable | 연간 누계 보전금. mmg_annual_cap 초과 시 알럿 | 2026_09_18_000139 |
| `created_at` | timestamp |  |  | 2026_09_18_000139 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000139 |

## prepayment_ledgers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000140 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_18_000140 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_18_000140 |
| `offset_payee_id` | unsignedBigInteger | nullable | 상계 귀속 수취인 rights_holders.id. NULL 이면 권리자 본인 (합의서 5.3) | 2026_09_18_000140 |
| `principal_amount` | integer |  | 선급금 원금(지급액) | 2026_09_18_000140 |
| `offset_amount` | integer |  | 누계 상계액 | 2026_09_18_000140 |
| `balance_amount` | integer |  | 미상계 잔액 = 원금 − 누계 상계액 | 2026_09_18_000140 |
| `prepayment_tax_type` | string(20) |  | 세무 처리 스냅샷. INCOME_PREPAY=소득 선지급(과세표준 차감) / LOAN=대여금(차감 없음). 정본은 계약 원장 | 2026_09_18_000140 |
| `paid_at` | date | nullable | 선지급 실행일 | 2026_09_18_000140 |
| `status` | string(20) |  | ACTIVE=상계 진행 / SETTLED=전액 상계 / LOCKED=계약 종료 후 영구 잠금 | 2026_09_18_000140 |
| `is_locked` | boolean |  | 영구 잠금. 계약 만료·해지 시 미상계 잔액이 남은 레코드를 보존한다 | 2026_09_18_000140 |
| `uncollectible_status` | string(20) | nullable | 대손 상태. NULL=정상 / PENDING=회수 불가 검토 / WRITTEN_OFF=대손상각. 파기 예외 대상으로 자동 등록된다 | 2026_09_18_000140 |
| `memo` | string(255) | nullable | 비고 | 2026_09_18_000140 |
| `created_at` | timestamp |  |  | 2026_09_18_000140 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000140 |

## tax_decision_matrices
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000141 |
| `matrix_case_id` | string(10) |  | 케이스 코드 TX-01 ~ TX-12. 정산 라인의 조인 키 | 2026_09_18_000141 |
| `payee_tax_type` | string(20) | nullable | 수취인 세무 유형. rights_holders.tax_type 과 같은 축 | 2026_09_18_000141 |
| `supply_nature` | string(30) | nullable | 공급 성격. 강의 R/S · 인세 · 매절 · 비정기 약정금 · 도서 재화 | 2026_09_18_000141 |
| `supply_category` | string(10) | nullable | GOODS=재화 / SERVICE=용역. 재화는 원천징수 비대상으로 먼저 분기 | 2026_09_18_000141 |
| `income_category` | string(20) | nullable | BUSINESS / OTHER | 2026_09_18_000141 |
| `income_clause` | string(10) | nullable | 기타소득 호. C05 / C15 / C17 / C19 | 2026_09_18_000141 |
| `payee_is_author` | boolean | nullable | 저작자 본인 여부. C15 와 C05 를 가르는 축 | 2026_09_18_000141 |
| `main_work_external_labor` | boolean | nullable | 주된 업무 외 노무 활용. 인적용역 면세 배제 축 | 2026_09_18_000141 |
| `is_resident` | boolean | nullable | 거주자 여부 | 2026_09_18_000141 |
| `tax_invoice_eligible_yn` | boolean | nullable | 세금계산서 발급 의무 여부 | 2026_09_18_000141 |
| `book_supply_type` | string(20) | nullable | 도서 공급 형태. 도서 라인 판정 축 | 2026_09_18_000141 |
| `vat_rate` | decimal(5, 2) | nullable | 부가가치세율(%). 면세는 0 | 2026_09_18_000141 |
| `vat_exemption_basis` | string(100) | nullable | 면세 근거. 재화(제26조①8 계통)와 인적용역(제26조①15 계통)을 구분 기록 | 2026_09_18_000141 |
| `evidence_type` | string(30) | nullable | 증빙 종류. 세금계산서 / 계산서 / 영수증 / 원천징수영수증 등 | 2026_09_18_000141 |
| `evidence_issuer` | string(20) | nullable | 증빙 발행 주체. SELF_ISSUE / REVERSE_ISSUE / RECEIVE | 2026_09_18_000141 |
| `correction_channel` | string(10) | nullable | 증빙 정정 채널. 제10장 10.4절 채널 1~4 | 2026_09_18_000141 |
| `income_tax_rate` | decimal(5, 2) | nullable | 소득세율(%) | 2026_09_18_000141 |
| `local_tax_rate` | decimal(5, 2) | nullable | 지방소득세율(%). 소득세액 대비 10% 고정 | 2026_09_18_000141 |
| `expense_deduction_rate` | decimal(5, 2) | nullable | 필요경비 의제율(%). C15·C19 는 60, C05·C17 은 0 | 2026_09_18_000141 |
| `min_tax_threshold_yn` | boolean | nullable | 과세최저한 적용 여부. 기타소득 전용 | 2026_09_18_000141 |
| `small_amount_exemption_yn` | boolean | nullable | 소액부징수 적용 여부. 인적용역 해당 여부에서 파생되며 독립 입력이 아니다 | 2026_09_18_000141 |
| `receipt_issue_required_yn` | boolean | nullable | 원천징수영수증 발급 필요 여부 | 2026_09_18_000141 |
| `simplified_statement_yn` | boolean | nullable | 간이지급명세서 제출 대상 여부 | 2026_09_18_000141 |
| `payment_statement_form` | string(50) | nullable | 지급명세서 서식 구분 | 2026_09_18_000141 |
| `payment_statement_deadline` | string(50) | nullable | 지급명세서 제출기한 | 2026_09_18_000141 |
| `firm_banking_yn` | boolean | nullable | 펌뱅킹 대상 여부 | 2026_09_18_000141 |
| `ap_payment_yn` | boolean | nullable | AP 결제 경로 대상 여부. 도서 매입 대금 등 | 2026_09_18_000141 |
| `local_tax_place` | string(50) | nullable | 지방소득세 납세지 구분 | 2026_09_18_000141 |
| `effective_start_date` | date |  | 적용 개시일. 지급일(또는 귀속월)이 속한 버전을 바인딩한다 | 2026_09_18_000141 |
| `effective_end_date` | date | nullable | 적용 종료일. NULL 이면 현재 버전 | 2026_09_18_000141 |
| `legal_basis` | text | nullable | 근거 조문. 항·호·목 단위 병기 | 2026_09_18_000141 |
| `verification_status` | string(20) |  | 검증 등급. VERIFIED=원문 확인 / INTERPRETED=해석 확인 / UNVERIFIED=미확인. 미확인은 자동 마감 경로를 타지 않는다 | 2026_09_18_000141 |
| `created_at` | timestamp |  |  | 2026_09_18_000141 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_18_000141 |

## lecture_play_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_18_000143 |
| `user_id` | unsignedBigInteger | nullable | 요청 회원 users.id. 맛보기 비로그인 재생이면 NULL (FK 없음 — 탈퇴 후에도 보존) | 2026_09_18_000143 |
| `user_course_id` | unsignedBigInteger | nullable | 판정에 쓴 수강권 user_courses.id. 같은 강의가 여러 강좌에 편성되고 재구매도 있어 course_id 만으로는 구분되지 않는다 (FK 없음) | 2026_09_18_000143 |
| `lecture_id` | unsignedBigInteger |  | 요청 강의 lectures.id (FK 없음 — 소프트 삭제 후에도 보존) | 2026_09_18_000143 |
| `course_id` | unsignedBigInteger | nullable | 판정에 쓴 강좌 courses.id. 강좌를 정하지 못하고 거절된 요청이면 NULL (FK 없음) | 2026_09_18_000143 |
| `context` | string(20) |  | 재생 맥락. member=회원 학습 / admin=관리자 확인 | 2026_09_18_000143 |
| `result_code` | string(30) | nullable | 거절 사유 코드. NULL 이면 성공(주소 발급). NO_ENROLLMENT / EXPIRED / PAUSED / NOT_IN_CURRICULUM / NOT_AVAILABLE / LOGIN_REQUIRED | 2026_09_18_000143 |
| `ip` | string(45) | nullable | 요청 IP | 2026_09_18_000143 |
| `user_agent` | string(500) | nullable | 브라우저/기기 정보 | 2026_09_18_000143 |
| `created_at` | timestamp |  | 요청 시각 | 2026_09_18_000143 |

## exclusive_contract_fees
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_19_000146 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_19_000146 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_19_000146 |
| `payee_id` | unsignedBigInteger | nullable | 2계층 수취인 rights_holders.id. NULL 이면 권리자 본인 | 2026_09_19_000146 |
| `fee_amount` | integer |  | 약정 전속계약금(세전) | 2026_09_19_000146 |
| `payment_method` | string(20) |  | 지급 방식. LUMP_SUM=일시 / INSTALLMENT=분할 (합의서 5.2) | 2026_09_19_000146 |
| `income_category` | string(20) |  | BUSINESS=사업소득(기본) / OTHER=기타소득. OTHER 는 재무 책임자 승인 대상 | 2026_09_19_000146 |
| `income_clause` | string(10) | nullable | 기타소득 호. C17=사례금 / C19=인적용역 대가. 호에 따라 의제경비·지급명세서 주기가 다르다 | 2026_09_19_000146 |
| `payee_is_author` | boolean |  | 저작자 본인 여부. 세무 판정 매트릭스 입력값 | 2026_09_19_000146 |
| `prepayment_tax_type` | string(20) | nullable | 상계 특약이 있는 건의 세무 구분. income_advance=소득 선지급 / loan=대여금. 비상계 원칙이므로 기본은 NULL (합의서 5.2 · 5.3) | 2026_09_19_000146 |
| `paid_at` | date | nullable | 지급 실행일. 분할이면 최초 지급일 | 2026_09_19_000146 |
| `target_month` | char(7) | nullable | 정산 인입 귀속월 YYYY-MM | 2026_09_19_000146 |
| `net_paid_amount` | integer | nullable | 기 지급 실지급액(세후). 반환 대상 금액 산식의 모수다(합의서 5.2) | 2026_09_19_000146 |
| `service_started_at` | date | nullable | 전속 의무 복무 개시일 | 2026_09_19_000146 |
| `service_ended_at` | date | nullable | 전속 의무 복무 종료일 | 2026_09_19_000146 |
| `total_service_days` | unsignedInteger | nullable | 총 약정 의무 복무 일수. 반환 산식의 분모라 날짜에서 재계산하지 않고 고정한다 | 2026_09_19_000146 |
| `approval_status` | string(20) |  | ADMN-INST-002 검수 상태. pending / approved / rejected. 소득 구분 미지정이면 승인할 수 없다 | 2026_09_19_000146 |
| `approver_id` | unsignedBigInteger | nullable | 승인 관리자 users.id | 2026_09_19_000146 |
| `status` | string(20) |  | 약정 상태. active=이행중 / terminated=중도 해지(반환 원장 발생) / closed=의무 기간 종료 | 2026_09_19_000146 |
| `memo` | string(255) | nullable | 비고 | 2026_09_19_000146 |
| `created_at` | timestamp |  |  | 2026_09_19_000146 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_19_000146 |
| `clawback_policy` | string(10) |  | 중도 해지 반환 조항. NONE=반환 없음 / PRO_RATA=잔여기간 일할 / FULL=전액 | 2026_10_03_000194 |

## exclusive_contract_clawbacks
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_19_000147 |
| `fee_id` | foreignId |  | exclusive_contract_fees.id 참조 | 2026_09_19_000147 |
| `payee_id` | unsignedBigInteger | nullable | 반환 채권 귀속 수취인 rights_holders.id. NULL 이면 권리자 본인 | 2026_09_19_000147 |
| `terminated_at` | date |  | 중도 해지 확정일. 잔여 의무 일수의 기산점 | 2026_09_19_000147 |
| `remaining_service_days` | unsignedInteger |  | 잔여 의무 복무 일수. 반환 산식의 분자 | 2026_09_19_000147 |
| `net_paid_amount` | integer |  | 기 지급 실지급액(세후) 스냅샷. 산식 모수라 원장 값 변경에 흔들리면 안 된다 | 2026_09_19_000147 |
| `clawback_amount` | integer |  | 반환 대상 금액(세후). Floor 절사 후 값 | 2026_09_19_000147 |
| `collected_amount` | integer |  | 누계 회수액 | 2026_09_19_000147 |
| `balance_amount` | integer |  | 반환 채권 잔액 = 반환 대상 금액 − 누계 회수액 | 2026_09_19_000147 |
| `collection_status` | string(20) |  | 회수 상태. pending=확정 전 / claimed=청구서 발행 / collecting=일부 회수 / collected=완결 / written_off=대손 | 2026_09_19_000147 |
| `claim_prereflected_yn` | boolean |  | 10단계(CLAIM) 청구 판정 선반영 여부. 반환액으로 음수 전환된 건의 청구 누락을 막는다 | 2026_09_19_000147 |
| `claim_month` | char(7) | nullable | 청구 판정 귀속월 YYYY-MM | 2026_09_19_000147 |
| `correction_channel` | string(20) | nullable | 11단계(PAYOUT) 증빙 정정 채널. channel_1=수정 전자세금계산서(TX-06·07·09) / channel_2=수정 전자계산서(TX-08) / channel_3a=원천세 수정신고(TX-02·03·04) / internal=자사 내부 대체 전표(TX-01) | 2026_09_19_000147 |
| `matrix_case_id` | string(10) | nullable | 채널 분기 근거가 된 세무 판정 케이스 TX-01~TX-12 | 2026_09_19_000147 |
| `memo` | string(255) | nullable | 비고 | 2026_09_19_000147 |
| `created_at` | timestamp |  |  | 2026_09_19_000147 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_19_000147 |

## payee_splits
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_21_000152 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_09_21_000152 |
| `rights_holder_id` | foreignId |  | 분할 대상 권리자 rights_holders.id 참조 | 2026_09_21_000152 |
| `payee_id` | unsignedBigInteger |  | 수취인 rights_holders.id. 권리자 본인도 한 행으로 등록한다 | 2026_09_21_000152 |
| `split_ratio` | decimal(5, 2) |  | 분할 비율(%). 권리자 기준 합계 100.00 이어야 저장된다(§4.2) | 2026_09_21_000152 |
| `start_date` | date |  | 적용 시작일 | 2026_09_21_000152 |
| `end_date` | date | nullable | 적용 종료일. NULL 이면 기한 없음 | 2026_09_21_000152 |
| `created_at` | timestamp |  |  | 2026_09_21_000152 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_21_000152 |
| `note` | string(255) | nullable | 비율 근거 메모. 계약 조항 · 상속재산분할협의서 등 운영자 입력 | 2026_10_26_000265 |

## settlement_adjustments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_21_000153 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_21_000153 |
| `contract_id` | unsignedBigInteger | nullable | rights_holder_contracts.id. 계약 단위가 아닌 조정이면 NULL | 2026_09_21_000153 |
| `payee_id` | unsignedBigInteger | nullable | 수취인 rights_holders.id. NULL 이면 권리자 본인(§10.2 수취인 ID) | 2026_09_21_000153 |
| `origin_month` | char(7) |  | 원 발생 귀속월 YYYY-MM. 오류가 실제로 발생한 월. 손익 분석 · 감사 추적용(§10.2) | 2026_09_21_000153 |
| `applied_month` | char(7) |  | 반영월 YYYY-MM. 조정이 정산서에 반영되는 월. 자금 집행 · 세무 신고용(§10.2) | 2026_09_21_000153 |
| `reason_type` | string(30) |  | 조정 사유 구분. rate_error=요율 오류 / share_error=지분율 오류 / payee_split_error=수취인 분할 오류 / refund_missing=환불 반영 누락 / lumpsum_month_error=약정금 귀속월 오류 / buyout_income_error=매절 소득 구분 오류 / tax_type_misjudge=과세유형 오인 / reconcile_diff=대사 차이 정정 / account_transfer=계정 간 대체 / book_supply_type_error=도서 공급 형태 오등록 / support_cap_error=지원금 한도 판정 오류 / consignment_fee_error=위탁 수수료율 오류 / etc=기타 (§10.2) | 2026_09_21_000153 |
| `explanation` | text |  | 소명 내용. 최소 20자 필수(§10.2) | 2026_09_21_000153 |
| `adjust_amount` | integer |  | 조정 금액. 부호 포함 — 음수는 차감이다 | 2026_09_21_000153 |
| `vat_type` | string(10) |  | 과·면세 구분. taxable=과세 / exempt=면세 | 2026_09_21_000153 |
| `income_category` | string(20) | nullable | BUSINESS=사업소득 / OTHER=기타소득 | 2026_09_21_000153 |
| `income_clause` | string(10) | nullable | 기타소득 호. C05 · C15 · C17 · C19 | 2026_09_21_000153 |
| `account_type` | string(10) |  | 계정 구분. PRE_TAX=세전 / POST_TAX=세후. 이월 잔액 원장과 같은 축이다(§7.4) | 2026_09_21_000153 |
| `created_by` | unsignedBigInteger | nullable | 등록 관리자 users.id | 2026_09_21_000153 |
| `approver1_id` | unsignedBigInteger | nullable | 1차 승인 관리자 users.id. 재무 운영자 | 2026_09_21_000153 |
| `approver2_id` | unsignedBigInteger | nullable | 2차 승인 관리자 users.id. 재무 책임자(§10.3 임계 초과 시) | 2026_09_21_000153 |
| `status` | string(20) |  | 상태. pending=승인 대기 / approved=승인 / rejected=반려 / applied=정산서 반영 완료 | 2026_09_21_000153 |
| `origin_settlement_id` | unsignedBigInteger | nullable | 원 정산서 참조 instructor_settlements.id(§10.2 원 정산서 링크) | 2026_09_21_000153 |
| `matrix_case_id` | string(10) | nullable | 세무 판정 케이스 TX-01~TX-12. 증빙 정정 채널 분기 근거(§10.4) | 2026_09_21_000153 |
| `correction_channel` | string(20) | nullable | 증빙 정정 채널. channel_1=수정 전자세금계산서 / channel_2=수정 전자계산서 / channel_3a=원천세 수정신고 / channel_3b=기록 정정(TX-05) / channel_4=수취 증빙 재요청 / internal=자사 내부 대체 전표 (§10.4) | 2026_09_21_000153 |
| `correction_channel_sub` | string(20) | nullable | 병기 채널. 위탁 거래는 수취 정정(채널 4)과 발행 정정(채널 1)이 동시에 필요할 수 있다(§10.4) | 2026_09_21_000153 |
| `transfer_pair_key` | string(40) | nullable | 대체 전표 쌍 식별자. 계정 간 대체 시 두 행이 같은 값을 갖는다 | 2026_09_21_000153 |
| `created_at` | timestamp |  |  | 2026_09_21_000153 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_21_000153 |
| `adjust_type` | string(20) | nullable | 조정 유형. CURRENT=당월 수동 조정 / PRIOR_FIX=전월 정정(마감 후 전기오류수정) /  | 2026_10_21_000242 |
| `approved_at` | timestamp | nullable | 확정 일시. 재무 담당자 단독 확정 시각. 확정자는 approver1_id(설계서 ADMN-SETT-005 · PO 2026-09-22) | 2026_10_21_000242 |
| `reject_reason` | text | nullable | 반려 사유. 반려 시 필수 입력(설계서 ADMN-SETT-005-S1 ⑦) | 2026_10_21_000242 |

## nts_verification_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_21_000154 |
| `subject_type` | string(20) |  | 대상 구분. RIGHTS_HOLDER=권리자 / CONSIGNOR=위탁자 / SUPPLIER=매입처 | 2026_09_21_000154 |
| `subject_id` | unsignedBigInteger |  | 대상 ID. subject_type 에 따라 rights_holders.id 또는 suppliers.id (다형 참조라 FK 없음) | 2026_09_21_000154 |
| `contract_id` | unsignedBigInteger | nullable | rights_holder_contracts.id. 계약 등록 시점 조회면 값이 있다 | 2026_09_21_000154 |
| `api_type` | string(10) |  | API 종류. VALIDATE=진위확인 / STATUS=상태조회 | 2026_09_21_000154 |
| `b_no` | string(20) |  | 사업자등록번호(하이픈 없는 10자리) | 2026_09_21_000154 |
| `request_payload` | json | nullable | 요청 원문. serviceKey 는 마스킹해 적재한다(§17.6) | 2026_09_21_000154 |
| `response_payload` | json | nullable | 응답 원문 그대로. 사후 소명 자료(§17.6) | 2026_09_21_000154 |
| `b_stt` | string(20) | nullable | 납세자 상태. 계속사업자 / 휴업자 / 폐업자 | 2026_09_21_000154 |
| `tax_type` | string(20) | nullable | 과세유형 문자열 응답값 | 2026_09_21_000154 |
| `tax_type_cd` | string(10) | nullable | 과세유형 코드 | 2026_09_21_000154 |
| `tax_type_change_dt` | date | nullable | 과세유형 전환일자 | 2026_09_21_000154 |
| `invoice_apply_dt` | date | nullable | 세금계산서 적용일자 | 2026_09_21_000154 |
| `end_dt` | date | nullable | 폐업일자 | 2026_09_21_000154 |
| `match_result` | string(20) | nullable | 일치 여부. match=일치 / mismatch=불일치 / not_found=확인 불가 | 2026_09_21_000154 |
| `checked_at` | timestamp | nullable | 조회 일시 | 2026_09_21_000154 |
| `checked_by` | unsignedBigInteger | nullable | 조회자 users.id. 배치면 NULL | 2026_09_21_000154 |
| `trigger_type` | string(24) |  | 조회 트리거. CONTRACT_REG=계약 등록 / PERIODIC=정기 / AD_HOC=수시 / MILESTONE_APPROVAL=약정금 승인 / PURCHASE_ORDER=발주 / CONSIGNMENT_REG=위탁 등록 (§17.6) | 2026_09_21_000154 |
| `change_review_status` | string(20) | nullable | 과세유형 변경 확인 상태(탭 2). unreviewed=미확인 / approved=승인 / held=보류. 승인 시 유효일자 버전 행이 생성된다 | 2026_09_21_000154 |
| `error_code` | string(40) | nullable | 실패 오류 코드(탭 4) | 2026_09_21_000154 |
| `retry_count` | unsignedInteger |  | 재시도 횟수. 지수 백오프 3회 후 큐 적재(§17.6) | 2026_09_21_000154 |
| `queue_status` | string(20) | nullable | 재시도 큐 상태(탭 4). queued=대기 / retrying=재시도 중 / resolved=해소 / abandoned=포기 | 2026_09_21_000154 |
| `created_at` | timestamp |  |  | 2026_09_21_000154 |

## consignment_returns
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_21_000155 |
| `book_id` | foreignId |  | books.id 참조. book_supply_type=CONSIGNMENT 인 도서만 | 2026_09_21_000155 |
| `consignor_id` | unsignedBigInteger |  | 위탁자 rights_holders.id 참조 | 2026_09_21_000155 |
| `order_item_id` | unsignedBigInteger | nullable | 원 주문 라인 order_items.id | 2026_09_21_000155 |
| `refund_id` | unsignedBigInteger | nullable | 원 환불 refunds.id | 2026_09_21_000155 |
| `quantity` | integer |  | 반품 수량(권). 위탁자 재고로 돌아가야 할 실물 수량 | 2026_09_21_000155 |
| `consignment_return_status` | string(20) |  | 실물 반환 상태. pending_recall=회수 대기 / recalled=회수 완료 / disposed=폐기 / lost=분실 (합의서 §6.6 · 변형 10-B) | 2026_09_21_000155 |
| `status_changed_at` | timestamp | nullable | 상태 변경 일시 | 2026_09_21_000155 |
| `target_month` | char(7) | nullable | 금액 차감이 반영된 정산 귀속월 YYYY-MM | 2026_09_21_000155 |
| `memo` | string(255) | nullable | 비고 | 2026_09_21_000155 |
| `created_at` | timestamp |  |  | 2026_09_21_000155 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_21_000155 |

## lecture_instructors
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_22_000157 |
| `lecture_id` | foreignId |  | lectures.id 참조 | 2026_09_22_000157 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_22_000157 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조. 요율 조회 경로가 이 행에서 종결된다(§4.2) | 2026_09_22_000157 |
| `share_ratio` | decimal(5, 2) |  | 지분율(%). 같은 강의 · 같은 기간 합계 100.00 이어야 한다(§4.1) | 2026_09_22_000157 |
| `start_date` | date |  | 유효 시작일 | 2026_09_22_000157 |
| `end_date` | date | nullable | 유효 종료일. NULL 이면 기한 없음 | 2026_09_22_000157 |
| `created_at` | timestamp |  |  | 2026_09_22_000157 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_22_000157 |

## book_authors
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_22_000158 |
| `book_id` | foreignId |  | books.id 참조. SKU 단위다(§4.2) | 2026_09_22_000158 |
| `rights_holder_id` | foreignId |  | rights_holders.id 참조 | 2026_09_22_000158 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조. 인세 요율 조회 경로가 이 행에서 종결된다(§4.2) | 2026_09_22_000158 |
| `share_ratio` | decimal(5, 2) |  | 공동 저자 배분율(%). 같은 도서 · 같은 기간 합계 100.00(§6.2) | 2026_09_22_000158 |
| `start_date` | date |  | 유효 시작일 | 2026_09_22_000158 |
| `end_date` | date | nullable | 유효 종료일. NULL 이면 기한 없음 | 2026_09_22_000158 |
| `created_at` | timestamp |  |  | 2026_09_22_000158 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_22_000158 |

## goods
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_22_000159 |
| `code` | string(50) |  | 상품 코드 GOODS-%06d(id). 채번은 Set 4 | 2026_09_22_000159 |
| `name` | string(255) |  | 상품명 | 2026_09_22_000159 |
| `maker` | string(100) | nullable | 제조사 · 공급사명(표시용) | 2026_09_22_000159 |
| `goods_supply_type` | string(20) |  | 공급 형태. PURCHASED_RESALE=매입 재판매 / DIRECT_SALE=자사 직접 판매. 판매 이력이 있으면 변경하지 않고 신규 SKU 를 발급한다(§18.1) | 2026_09_22_000159 |
| `original_price` | integer |  | 정가 | 2026_09_22_000159 |
| `cost_price` | integer | nullable | 매입 원가. 대외비 | 2026_09_22_000159 |
| `sale_price` | integer |  | 판매가 | 2026_09_22_000159 |
| `delivery_fee` | integer | nullable | 개별 배송비. NULL 이면 site_settings 기본값 적용 | 2026_09_22_000159 |
| `is_free_delivery` | boolean |  | 금액 조건과 무관하게 항상 무료배송 | 2026_09_22_000159 |
| `free_delivery_threshold` | integer | nullable | 조건부 무료배송 기준 금액. NULL 이면 미적용 | 2026_09_22_000159 |
| `island_delivery_fee` | integer | nullable | 도서산간 추가 배송비. NULL 이면 site_settings 값 적용 | 2026_09_22_000159 |
| `return_delivery_fee` | integer | nullable | 반품 왕복 배송비. NULL 이면 site_settings 기본값 적용 | 2026_09_22_000159 |
| `stock` | integer |  | 현재 재고. 재고 관리는 상품 관리 도메인이며 정산 엔진은 관여하지 않는다(§18.2) | 2026_09_22_000159 |
| `stock_alert_qty` | integer | nullable | 품절 임박 기준 수량 | 2026_09_22_000159 |
| `description` | text | nullable | 상품 설명 | 2026_09_22_000159 |
| `thumbnail_path` | string(255) | nullable | 썸네일 경로 | 2026_09_22_000159 |
| `display_status` | string(20) |  | 전시 상태. selling=전시·판매중 / hidden=비전시 / stopped=판매중지 | 2026_09_22_000159 |
| `supplier_id` | unsignedBigInteger | nullable | 매입처 suppliers.id. 매입 재판매의 AP 경로 연결(§2.4) | 2026_09_22_000159 |
| `created_at` | timestamp |  |  | 2026_09_22_000159 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_09_22_000159 |

## payment_cancels
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_28_000169 |
| `payment_id` | unsignedBigInteger |  | payments.id 참조 | 2026_09_28_000169 |
| `order_id` | unsignedBigInteger |  | orders.id 참조. 조회용 비정규화 | 2026_09_28_000169 |
| `refund_id` | unsignedBigInteger | nullable | 업무 환불 refunds.id. 망취소·관리자 직접 취소면 NULL | 2026_09_28_000169 |
| `cancel_type` | string(20) |  | full=전체취소 / partial=부분취소 / net=망취소 | 2026_09_28_000169 |
| `cancel_amount` | integer |  | 취소 요청 금액 | 2026_09_28_000169 |
| `reason` | string(100) |  | 취소 사유. PG ccMsg 로 전송 | 2026_09_28_000169 |
| `idempotency_key` | string(100) | nullable,unique | 중복 취소 차단 키 | 2026_09_28_000169 |
| `status` | string(20) |  | requested=전송 전·응답 대기 / succeeded=취소 완료 / failed=PG 거절·통신 실패 | 2026_09_28_000169 |
| `result_code` | string(10) | nullable | PG 결과 코드. 2001=취소 성공 | 2026_09_28_000169 |
| `result_message` | string(200) | nullable | PG 결과 메시지 | 2026_09_28_000169 |
| `cancel_tid` | string(30) | nullable | PG 가 돌려준 취소 거래 tid | 2026_09_28_000169 |
| `cc_seq` | unsignedSmallInteger | nullable | PG 부분취소 회차. 부분취소일 때만 온다 | 2026_09_28_000169 |
| `raw_response` | json | nullable | PG 취소 응답 원문. 매출 대사 근거 | 2026_09_28_000169 |
| `requested_by` | unsignedBigInteger | nullable | 요청자 users.id. 시스템 망취소면 NULL | 2026_09_28_000169 |
| `completed_at` | timestamp | nullable | PG 응답 수신 일시 | 2026_09_28_000169 |
| `created_at` | timestamp |  | 요청 일시 | 2026_09_28_000169 |

## pg_notifications
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_09_28_000170 |
| `pg_provider` | string(20) |  | PG사 | 2026_09_28_000170 |
| `pg_tid` | string(30) | nullable | 통보의 tid. 취소 통보면 취소 거래 tid | 2026_09_28_000170 |
| `pg_otid` | string(30) | nullable | 취소 통보의 원거래 tid | 2026_09_28_000170 |
| `ord_no` | string(50) | nullable | 통보의 주문번호(orders.order_no) | 2026_09_28_000170 |
| `kind` | string(20) |  | approval=승인 통보 / cancel=취소 통보 / unknown=판별 불가 | 2026_09_28_000170 |
| `result_code` | string(10) | nullable | 통보 결과 코드 | 2026_09_28_000170 |
| `amount` | integer | nullable | 통보 금액. 승인 goodsAmt / 취소 ccAmt | 2026_09_28_000170 |
| `payload` | json | nullable | 통보 원문. JSON 이 아니면 NULL | 2026_09_28_000170 |
| `source_ip` | string(45) |  | 발신 IP | 2026_09_28_000170 |
| `verdict` | string(30) |  | accepted=주문 확정 보정 / confirmed=이미 반영됨 / needs_review=사람 확인 필요 / rejected_ip=허용 외 발신 / rejected_payload=형식 오류 / unknown_order=주문 없음 | 2026_09_28_000170 |
| `note` | string(255) | nullable | 판정 근거 | 2026_09_28_000170 |
| `order_id` | unsignedBigInteger | nullable | 매칭된 orders.id | 2026_09_28_000170 |
| `created_at` | timestamp |  | 수신 일시 | 2026_09_28_000170 |

## order_no_sequences
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `seq_date` | date |  | 채번 기준일(Asia/Seoul, 주문 생성일) | 2026_09_30_000178 |
| `last_seq` | unsignedInteger |  | 그날 마지막으로 낸 일련번호. 7자리(9,999,999) 상한 | 2026_09_30_000178 |
| `updated_at` | timestamp | nullable |  | 2026_09_30_000178 |

## rights_holder_contract_memos
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_02_000185 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id | 2026_10_02_000185 |
| `admin_id` | unsignedBigInteger | nullable | 작성 관리자 users.id | 2026_10_02_000185 |
| `content` | text |  | 메모 본문. 등록 후 수정 · 삭제 불가 | 2026_10_02_000185 |
| `created_at` | timestamp | nullable |  | 2026_10_02_000185 |

## contract_milestones
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_03_000190 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id | 2026_10_03_000190 |
| `term_type` | string(10) |  | 조항. EXC=전속계약금 / DEV=개발지원금 / BUYOUT=매절 / ETC=기타 수당 | 2026_10_03_000190 |
| `sequence_no` | unsignedSmallInteger |  | 조항 안 회차 번호 1부터 | 2026_10_03_000190 |
| `title` | string(255) | nullable | 지급 마일스톤 · 지원 항목 · 지급 사유 | 2026_10_03_000190 |
| `target_month` | char(7) |  | 정산 반영 귀속월 YYYY-MM | 2026_10_03_000190 |
| `unit_count` | unsignedInteger | nullable | 기타 수당 건당 방식의 건수 | 2026_10_03_000190 |
| `unit_price` | unsignedInteger | nullable | 기타 수당 건당 단가 스냅샷 | 2026_10_03_000190 |
| `amount` | unsignedInteger |  | 지급 금액(세전) | 2026_10_03_000190 |
| `income_category` | string(20) | nullable | BUSINESS / OTHER. 미지정이면 검수 승인 불가 | 2026_10_03_000190 |
| `income_clause` | string(10) | nullable | 기타소득 호 | 2026_10_03_000190 |
| `approval_status` | string(20) |  | 검수 상태. pending / approved / rejected | 2026_10_03_000190 |
| `approver_id` | unsignedBigInteger | nullable | 승인 관리자 users.id | 2026_10_03_000190 |
| `paid_at` | date | nullable | 지급 실행일. 값이 있으면 지급완료 — 수정 · 삭제 불가 | 2026_10_03_000190 |
| `code` | string(30) | nullable | 스케줄 식별 코드. EXC-YYYY-NN · SUP-YYYY-NNN · MS-YYYY-NNN 형식의 표시용 번호 | 2026_10_21_000241 |
| `verify_method` | string(20) | nullable | 검수 방식(7.2절 이원화). EVIDENCE_FILE=증빙 파일 / MANUAL_NOTE=수기 소명 | 2026_10_21_000241 |
| `review_note` | text | nullable | 검수 의견 · 승인 근거. 승인 · 반려 시 필수 입력(프로토타입 INST-002) | 2026_10_21_000241 |
| `approved_at` | timestamp | nullable | 검수 승인 · 반려 처리 일시. 승인 경로 감사 추적용 | 2026_10_21_000241 |
| `transferred_at` | timestamp | nullable | 7단계(LUMPSUM_ADD) 이관 표시 일시. 이관 여부는 항상 이 칸으로 읽는다 | 2026_10_21_000241 |
| `settlement_line_id` | unsignedBigInteger | nullable | 이관된 정산 라인 settlement_lines.id. 표시용 — 재연산 때 끊기므로 멱등 판정에 쓰지 않는다 | 2026_10_21_000241 |

## contract_term_targets
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_03_000191 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id | 2026_10_03_000191 |
| `term_type` | string(10) |  | 조항. DEV=개발지원금 / BUYOUT=매절 | 2026_10_03_000191 |
| `target_type` | string(10) |  | LECTURE=강의(lectures.id) / BOOK=도서(books.id) | 2026_10_03_000191 |
| `target_id` | unsignedBigInteger |  | lectures.id 또는 books.id | 2026_10_03_000191 |
| `created_at` | timestamp | nullable |  | 2026_10_03_000191 |

## prepayment_ledger_lines
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_03_000196 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id | 2026_10_03_000196 |
| `line_no` | unsignedInteger |  | 계약 안 라인 번호 1부터 | 2026_10_03_000196 |
| `base_month` | char(7) |  | 정산 데이터 기준 월 YYYY-MM | 2026_10_03_000196 |
| `line_type` | string(10) |  | PAY=추가 지급(+) / OFFSET=수동 상계(−) / RETURN=반환 청구(−) / REVERSAL=정정 · 역분개(±) | 2026_10_03_000196 |
| `amount` | integer |  | 부호 포함 금액. 지급 +, 상계 · 청구 − | 2026_10_03_000196 |
| `status` | string(20) |  | AGREEMENT=약정 등록(검수 대기) / CLAIM=청구 등록(10단계 판정 대기) / APPROVAL=2차 승인 대기 / DONE=반영 | 2026_10_03_000196 |
| `nature` | string(20) | nullable | 추가 지급 라인의 성격. INHERIT=계약 기본값 / INCOME_PREPAY=소득 선지급 / LOAN=대여금 | 2026_10_03_000196 |
| `income_type` | string(10) | nullable | 수동 상계 대상 소득 구분. BIZ=사업자 / BUS · C05 · C15 · C17 · C19 | 2026_10_03_000196 |
| `origin_line_id` | unsignedBigInteger | nullable | 정정 대상 원 라인 prepayment_ledger_lines.id | 2026_10_03_000196 |
| `memo` | text | nullable | 운영자 메모. 음수 · 정정 · 음수 잔액 라인은 필수 | 2026_10_03_000196 |
| `admin_id` | unsignedBigInteger | nullable | 등록 관리자 users.id | 2026_10_03_000196 |

## goods_stock_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_14_000206 |
| `goods_id` | foreignId |  | goods.id 참조 | 2026_10_14_000206 |
| `type` | string(30) |  | 입고/출고/복구/조정 등 | 2026_10_14_000206 |
| `quantity` | integer |  | 변동 수량 | 2026_10_14_000206 |
| `before_stock` | integer |  | 변동 전 재고 | 2026_10_14_000206 |
| `after_stock` | integer |  | 변동 후 재고 | 2026_10_14_000206 |
| `order_id` | unsignedBigInteger | nullable | 관련 주문 ID | 2026_10_14_000206 |
| `order_item_id` | unsignedBigInteger | nullable | 관련 주문상품 ID | 2026_10_14_000206 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 ID | 2026_10_14_000206 |
| `memo` | text | nullable | 메모 | 2026_10_14_000206 |
| `created_at` | timestamp |  |  | 2026_10_14_000206 |

## signup_precheck_logs
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_14_000207 |
| `di_hash` | string(64) |  | 본인인증 DI 해시(users.di_hash 와 같은 방식) | 2026_10_14_000207 |
| `result` | string(1) |  | 중단 사유: A 탈퇴 30일 미경과 · B 같은 명의 계정 있음 · E 만 14세 미만 | 2026_10_14_000207 |
| `tried_at` | timestamp |  | 시도 시각 | 2026_10_14_000207 |

## contract_terms
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_15_000207 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id 참조 | 2026_10_15_000207 |
| `sequence_no` | unsignedInteger |  | 회차 번호. 1 이 최초 계약 기간 | 2026_10_15_000207 |
| `term_type` | string(20) |  | 회차 구분. INITIAL=최초 계약 / RENEWAL=갱신 | 2026_10_15_000207 |
| `confirmed_at` | date | nullable | 회차 확정일. 갱신을 실행한 날 | 2026_10_15_000207 |
| `start_date` | date |  | 회차 계약 구간 시작일 | 2026_10_15_000207 |
| `end_date` | date |  | 회차 계약 구간 종료일 | 2026_10_15_000207 |
| `reason` | string(255) | nullable | 회차 사유 | 2026_10_15_000207 |
| `created_at` | timestamp | nullable |  | 2026_10_15_000207 |

## contract_evidences
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_15_000207 |
| `contract_id` | unsignedBigInteger |  | rights_holder_contracts.id 참조 | 2026_10_15_000207 |
| `evidence_type` | string(30) |  | 증빙 유형. PERSON_ID=신분증 / BANKBOOK=통장 사본 / BIZ_LICENSE=사업자등록증 / CONTRACT=계약서 / SUCCESSION=권리 승계 증빙 | 2026_10_15_000207 |
| `file_name` | string(255) |  | 선택한 파일명. 실제 파일은 보관하지 않는다 (v16 미구현 범위) | 2026_10_15_000207 |
| `admin_id` | unsignedBigInteger | nullable | 등록 관리자 users.id | 2026_10_15_000207 |
| `created_at` | timestamp | nullable |  | 2026_10_15_000207 |

## post_winners
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_15_000208 |
| `post_id` | foreignId |  | 당첨자 발표 글(posts.id) | 2026_10_15_000208 |
| `seq` | unsignedInteger |  | 명단 순번(1부터) | 2026_10_15_000208 |
| `masked_name` | string(50) |  | 마스킹한 이름(홍*동). 원본은 저장하지 않는다 | 2026_10_15_000208 |
| `masked_login` | string(150) |  | 마스킹한 아이디. 원본은 저장하지 않는다 | 2026_10_15_000208 |
| `prize` | string(100) |  | 경품 | 2026_10_15_000208 |
| `created_at` | timestamp |  |  | 2026_10_15_000208 |

## settlement_lines
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_19_000221 |
| `rights_holder_id` | unsignedBigInteger |  | rights_holders.id 참조. 원 권리자 | 2026_10_19_000221 |
| `payee_id` | unsignedBigInteger | nullable | 수취인 rights_holders.id. NULL = 분할 없이 원 권리자에게 지급 | 2026_10_19_000221 |
| `contract_id` | unsignedBigInteger | nullable | rights_holder_contracts.id | 2026_10_19_000221 |
| `target_month` | char(7) |  | 데이터 기준월 YYYY-MM. 01권 7.0절 — 정산 실행월이 아니다 | 2026_10_19_000221 |
| `pipeline_id` | string(10) |  | 정산 입력 구분. P1_1=온라인 강좌 수익배분 / P2_1=자사 발행 도서 인세 / P5_1=매출연동 개발지원금 / LUMPSUM=7단계 비정기 가산금 | 2026_10_19_000221 |
| `tax_threshold_unit_key` | string(100) | nullable | 과세최저한 · 소액부징수 판정 단위 키. 같은 키의 라인을 합산해 한 번만 판정한다 | 2026_10_19_000221 |
| `payee_split_base` | integer |  | 8단계 수취인 분할 기준액(분할 적용 후 라인 귀속액) | 2026_10_19_000221 |
| `offset_amount` | integer |  | 이 라인에 귀속된 선급금 상계액. 원 권리자 라인에만 붙는다(01권 7.1 상계 귀속 통제) | 2026_10_19_000221 |
| `taxable_base` | integer |  | 9단계 과세표준 | 2026_10_19_000221 |
| `supply_amount` | integer |  | 공급가액. 부가세 대상이 아니면 0 | 2026_10_19_000221 |
| `vat_amount` | integer |  | 부가가치세. 일반과세자 역발행 대상만 값이 있다 | 2026_10_19_000221 |
| `withholding_income_tax` | integer |  | 원천 소득세 | 2026_10_19_000221 |
| `withholding_local_tax` | integer |  | 지방소득세. 소득세의 10% | 2026_10_19_000221 |
| `deemed_expense_amount` | integer | nullable | 기타소득 필요경비 의제액. 사업소득 라인은 NULL | 2026_10_19_000221 |
| `other_income_amount` | integer | nullable | 기타소득금액(과세표준 − 필요경비 의제액). 사업소득 라인은 NULL | 2026_10_19_000221 |
| `below_min_tax_yn` | boolean |  | 과세최저한 미달 여부. 기타소득금액이 하한 미달이면 원천징수하지 않는다 | 2026_10_19_000221 |
| `small_amount_exemption_yn` | boolean |  | 소액부징수 여부. 산출 원천세가 하한 미달이면 징수하지 않는다 | 2026_10_19_000221 |
| `payable_amount` | integer |  | 11단계 지급 예정액(원천세 차감 후) | 2026_10_19_000221 |
| `matrix_case_id` | string(10) | nullable | 세무 판정 매트릭스 케이스. 예: TX-02 · TX-07 | 2026_10_19_000221 |
| `tax_decision_status` | string(20) |  | 세무 판정 상태. DECIDED=판정 완료 / PENDING_REVIEW=수동 검토 필요(지급 보류) | 2026_10_19_000221 |
| `offset_protected_yn` | boolean |  | 비상계 보호 지급액 여부. 1이면 선급금 상계 모수에서 뺀다(01권 5.3 · 7.1) | 2026_10_19_000221 |
| `income_category` | string(20) | nullable | 소득 구분 상위 축. BUSINESS=사업소득 / OTHER=기타소득 | 2026_10_19_000221 |
| `income_clause` | string(10) | nullable | 기타소득 호 구분. 예: C15 · C19 | 2026_10_19_000221 |
| `created_at` | timestamp |  |  | 2026_10_19_000221 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_10_19_000221 |
| `payout_hold_reason` | string(30) | nullable | 당월 지급 보류 사유. NULL=당월 지급 대상 / TAX_PENDING=세무 판정 보류(조건4) / NTS_EXPIRED=사업자 확인 90일 경과(조건5) / PENDING_VERIFY=임시 등록 확인 대기(조건6) / PAYEE_SPLIT=수취인 분할 2차 지원(DECISIONS 113①) / REFUND_BURDEN=환급 부담 B·C 2차 지원(DECISIONS 113②). 보류 라인도 마감 원장에는 남고 지급 대상에서만 빠진다 | 2026_10_21_000229 |

## settlement_closings
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_19_000222 |
| `target_month` | char(7) | unique | 데이터 기준월 YYYY-MM. 월 1행(01권 7.0절 — 정산 실행월이 아니다) | 2026_10_19_000222 |
| `locked_yn` | boolean |  | 마감 잠금. 1=마감 확정(Locked). 정정 라인 외 신규 인입 · 재연산 거부. 해제 경로 없음 | 2026_10_19_000222 |
| `aggregated_at` | timestamp | nullable | 마지막 집계(재연산) 실행 일시. 재연산하면 갱신된다 | 2026_10_19_000222 |
| `confirmed_at` | timestamp | nullable | 마감 확정 일시 | 2026_10_19_000222 |
| `admin_id` | unsignedBigInteger | nullable | 마감 확정 관리자 users.id. 담당자 참조라 계정이 지워져도 마감 기록은 남는다 | 2026_10_19_000222 |
| `created_at` | timestamp |  |  | 2026_10_19_000222 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_10_19_000222 |

## progress_anomalies
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_20_000228 |
| `user_id` | unsignedBigInteger |  | 회원 users.id (FK 없음 — 탈퇴 후에도 보존) | 2026_10_20_000228 |
| `user_course_id` | unsignedBigInteger | nullable | 판정에 쓴 수강권 user_courses.id. 수강권을 정하지 못한 건이면 NULL (FK 없음) | 2026_10_20_000228 |
| `lecture_id` | unsignedBigInteger |  | 차시 lectures.id (FK 없음 — 소프트 삭제 후에도 보존) | 2026_10_20_000228 |
| `reason` | string(30) |  | 이상 사유. OVER_BUDGET=인정 한도 초과 / OVER_POSITION=최대 지점 상한 초과 / SESSION_REPLACED=밀린 세션으로 저장 시도 / LOCK_BUSY=인정 잠금 점유로 인정 0 | 2026_10_20_000228 |
| `requested_played` | unsignedInteger |  | 요청한 시청 시간(초) | 2026_10_20_000228 |
| `credited_played` | unsignedInteger |  | 실제 인정한 시청 시간(초) | 2026_10_20_000228 |
| `requested_position` | unsignedInteger |  | 요청한 재생 위치(초) | 2026_10_20_000228 |
| `credited_position` | unsignedInteger |  | 실제 반영한 재생 위치(초) | 2026_10_20_000228 |
| `created_at` | timestamp |  | 기록 시각 | 2026_10_20_000228 |

## refund_adjustments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_20_000231 |
| `refund_id` | unsignedBigInteger |  | 원 환불 refunds.id. 완료된 환불에만 붙는다 | 2026_10_20_000231 |
| `adjustment_type` | string(20) |  | extra_refund=추가 환불(현금 추가 지급) / clawback=환불 회수(과다 환불분 청구) / point=포인트 보정(유상 지급 · 차감) | 2026_10_20_000231 |
| `method` | string(20) |  | 처리 수단. pg_cancel=PG 추가 부분 취소 / bank_transfer=계좌 이체 / customer_claim=고객 청구 / point_grant=유상 포인트 지급 / point_deduct=유상 포인트 차감 | 2026_10_20_000231 |
| `amount` | unsignedInteger |  | 보정 금액(원) 또는 포인트(P). 항상 양수 — 방향은 유형 · 처리 수단이 정한다 | 2026_10_20_000231 |
| `bank_code` | string(10) | nullable | 계좌 이체 은행 코드(토스 은행 코드). 계좌 이체일 때만 | 2026_10_20_000231 |
| `account_no` | text | nullable | 계좌 이체 계좌번호 — 앱 키 암호문(평문 저장 금지). 계좌 이체일 때만 | 2026_10_20_000231 |
| `account_holder` | string(50) | nullable | 계좌 이체 예금주. 계좌 이체일 때만 | 2026_10_20_000231 |
| `reason` | text |  | 보정 사유(10자 이상). 감사 로그 · 회원 이력에 남고 고치지 않는다 | 2026_10_20_000231 |
| `payment_cancel_id` | unsignedBigInteger | nullable | PG 추가 부분 취소 payment_cancels.id. PG 취소일 때만 | 2026_10_20_000231 |
| `point_log_id` | unsignedBigInteger | nullable | 포인트 보정 point_logs.id. 포인트 보정일 때만 | 2026_10_20_000231 |
| `idempotency_key` | string(100) | unique | 중복 등록 방지 키 = 원 환불 ID + 보정 내용 해시. PG 취소 멱등 키와 같다 | 2026_10_20_000231 |
| `admin_id` | unsignedBigInteger | nullable | 처리 관리자 users.id | 2026_10_20_000231 |
| `created_at` | timestamp |  | 등록 일시. 정산 반영 월의 기준 | 2026_10_20_000231 |

## rights_holder_account_histories
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_21_000230 |
| `rights_holder_id` | unsignedBigInteger |  | rights_holders.id 참조. 개인정보 파기 대상이라 권리자와 함께 지워진다 | 2026_10_21_000230 |
| `bank_name` | string(50) | nullable | 변경 전 은행명. 개인정보 파기 대상 | 2026_10_21_000230 |
| `account_no_enc` | text | nullable | 변경 전 계좌번호 암호문. 복호화하지 않고 그대로 옮긴다. 평문 열람 경로 없음. 개인정보 파기 대상 | 2026_10_21_000230 |
| `account_holder` | string(50) | nullable | 변경 전 예금주명. 개인정보 파기 대상 | 2026_10_21_000230 |
| `changed_by` | unsignedBigInteger | nullable | 변경한 관리자 users.id. 담당자 참조라 계정이 지워져도 변경 이력은 남는다 | 2026_10_21_000230 |
| `changed_at` | timestamp |  | 계좌 변경 일시 | 2026_10_21_000230 |
| `created_at` | timestamp |  |  | 2026_10_21_000230 |

## settlement_review_memos
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_21_000238 |
| `settlement_month` | char(7) |  | 데이터 기준월 YYYY-MM. settlement_lines.target_month 와 같은 축(정산 실행월이 아니다) | 2026_10_21_000238 |
| `rights_holder_id` | unsignedBigInteger |  | 메모 대상 권리자 rights_holders.id. 검토 기록이라 권리자를 지울 수 없게 RESTRICT | 2026_10_21_000238 |
| `payee_id` | unsignedBigInteger | nullable | 수취인 rights_holders.id. NULL = 권리자 단위 메모(분할 없는 행). 값이 있으면 그 수취인 하위 행에 달린 메모 | 2026_10_21_000238 |
| `memo` | text |  | 검토 메모 본문. 등록 후 고치거나 지우지 않는다 | 2026_10_21_000238 |
| `created_by` | unsignedBigInteger | nullable | 작성 관리자 users.id. 담당자 참조라 계정이 지워져도 메모는 남는다 | 2026_10_21_000238 |
| `created_at` | timestamp |  | 작성 일시. 조회는 이 값 기준 최신순 | 2026_10_21_000238 |

## verification_ip_exceptions
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_23_000247 |
| `ip` | string(45) | unique | 예외 IPv4 또는 대역(CIDR). 대역은 네트워크 주소로 맞춰 저장한다. 예: 211.45.30.17 · 211.45.30.0/24 | 2026_10_23_000247 |
| `memo` | string(100) |  | 등록 사유 메모(필수) — 왜 열어 뒀는지 모르는 예외가 쌓이지 않게(설계서 ③) | 2026_10_23_000247 |
| `created_by` | foreignId | nullable | 등록 관리자 users.id | 2026_10_23_000247 |

## lecture_progress_adjustments
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 진도율 보정 이력 ID | 2026_10_23_000250 |
| `user_course_id` | unsignedBigInteger |  | user_courses.id 참조. 보정은 수강권 + 차시 단위다 | 2026_10_23_000250 |
| `lecture_id` | unsignedBigInteger |  | lectures.id 참조. 강좌 전체를 한 번에 보정하는 경로는 없다 | 2026_10_23_000250 |
| `user_id` | unsignedBigInteger |  | users.id 참조. 회원 단위 조회 · 이력 보존용 | 2026_10_23_000250 |
| `original_rate` | decimal(5, 2) |  | 보정 전 원 집계 진도율(%). 덮어쓰지 않고 보관한다 | 2026_10_23_000250 |
| `adjusted_rate` | unsignedTinyInteger |  | 보정 후 진도율(%). 0~100 정수만 받는다(소수점 없음) | 2026_10_23_000250 |
| `reason_code` | string(30) |  | 보정 사유 코드. log_lost=재생 로그 유실 / ingest_missed=적재 누락 / lecture_reorg=차시 재편 / etc=기타 | 2026_10_23_000250 |
| `reason_text` | string(100) | nullable | 기타 선택 시 직접 입력한 사유명. 그 밖에는 NULL | 2026_10_23_000250 |
| `detail` | text |  | 상세 설명. 최소 20자 — 감사 로그만 보고 경위를 판단할 수 있어야 한다 | 2026_10_23_000250 |
| `adjusted_by` | unsignedBigInteger | nullable | 보정자 users.id(관리자) | 2026_10_23_000250 |
| `created_at` | timestamp |  | 보정 시각 | 2026_10_23_000250 |

## user_group_exclusions
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 자동 태그 제외 ID | 2026_10_23_000252 |
| `user_group_id` | unsignedBigInteger |  | user_groups.id 참조 | 2026_10_23_000252 |
| `user_id` | unsignedBigInteger |  | users.id 참조. 이 태그의 자동 재부여를 막는 회원 | 2026_10_23_000252 |
| `excluded_by` | unsignedBigInteger | nullable | 수동 해제한 관리자 users.id | 2026_10_23_000252 |
| `created_at` | timestamp |  | 제외 등록 시각 | 2026_10_23_000252 |

## lecture_bookmarks
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | bigIncrements |  | 북마크 ID | 2026_10_23_000264 |
| `user_id` | unsignedBigInteger |  | users.id 참조. 소유자 | 2026_10_23_000264 |
| `user_course_id` | unsignedBigInteger |  | user_courses.id 참조. 수강권이 사라지면 북마크도 함께 지운다 | 2026_10_23_000264 |
| `lecture_id` | unsignedBigInteger |  | lectures.id 참조(FK 없음 — 강의는 소프트 삭제) | 2026_10_23_000264 |
| `position_sec` | unsignedInteger |  | 재생 지점(초). 저장 시 서버가 0 ~ 영상 길이로 다시 자른다 | 2026_10_23_000264 |
| `content` | string(100) | nullable | 메모(선택 · 100자). 비워도 저장된다 | 2026_10_23_000264 |
| `created_at` | timestamp |  | 저장 시각 | 2026_10_23_000264 |

## contract_co_signers
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_26_000265 |
| `contract_id` | foreignId |  | rights_holder_contracts.id 참조 | 2026_10_26_000265 |
| `payee_id` | unsignedBigInteger |  | 수취인 rights_holders.id. 원 권리자 본인도 한 행으로 등록한다 | 2026_10_26_000265 |
| `role` | string(50) |  | 이 계약에서의 지위. 원 저작자 · 공동서명 소속사 · 법정 상속인 등 운영자 입력 | 2026_10_26_000265 |
| `entity_type` | string(50) | nullable | 사업자 구분 표기. 법인 일반과세자 · 개인 프리랜서 등. 판정값이 아니라 화면 표기용 | 2026_10_26_000265 |
| `tax_case` | string(50) | nullable | 세무 케이스 표기(TX-02 등). 실제 판정은 tax_decision_matrices 가 한다 | 2026_10_26_000265 |
| `is_author` | boolean |  | 이 계약에서 저작자 본인인가. 기타소득 원천징수율이 갈린다 | 2026_10_26_000265 |
| `succession_yn` | boolean |  | 상속 승계인인가. true 면 SUCCESSION 증빙 없이 분할 저장을 막는다 | 2026_10_26_000265 |
| `succession_date` | date | nullable | 승계 확정일. 이 날짜 기준으로 payee_is_author 가 전환된다 | 2026_10_26_000265 |
| `created_at` | timestamp |  |  | 2026_10_26_000265 |
| `updated_at` | timestamp | nullable | 수정 일시 | 2026_10_26_000265 |

## pg_reconciliation_item_holders
| 컬럼 | 타입 | 플래그 | 주석 | 마이그레이션 |
|---|---|---|---|---|
| `id` | id |  | PK | 2026_10_26_000271 |
| `item_id` | foreignId |  | pg_reconciliation_items.id 참조 | 2026_10_26_000271 |
| `rights_holder_id` | unsignedBigInteger |  | 귀속 권리자 rights_holders.id | 2026_10_26_000271 |
| `share_rate_snapshot` | decimal(5, 2) | nullable | 적재 시점 지분율(%) 스냅샷. 이후 지분이 바뀌어도 이 값은 바뀌지 않는다 | 2026_10_26_000271 |
| `share_amount_snapshot` | integer | nullable | 적재 시점 그 권리자 몫(원) 스냅샷. 대표 권리자 판정 근거 | 2026_10_26_000271 |
| `is_primary` | boolean |  | 목록 표시용 대표 권리자(최대 지분)인가. 차단 판정은 이 칸을 보지 않는다(199 ④) | 2026_10_26_000271 |
| `created_at` | timestamp |  |  | 2026_10_26_000271 |

