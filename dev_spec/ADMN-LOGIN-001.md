# ADMN-LOGIN-001 관리자 로그인 · 계정 찾기 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-LOGIN-001_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-LOGIN-001 관리자 로그인 · ADMN-LOGIN-001-P1 5회 오입력 잠금 안내 · 세션 만료 안내(연장) · 비밀번호 주기 변경(개발 ADMN-LOGIN-B) · ADMN-LOGIN-002 아이디 찾기 · ADMN-LOGIN-003 비밀번호 찾기 · 재설정
- 개발 진행: 구현(담당 박성민, `_index/progress.md` 7~10행). P1 은 로그인 화면 안 레이어로 구현

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| (없음) | — | 로그인 · 계정 찾기 · 세션 연장 · 비밀번호 변경은 메뉴 권한 밖. 로그인 전 라우트는 `admin.ip` 만, 세션 연장 · 비밀번호 변경은 `admin.auth`(로그인)만 건다 — routes/admin.php:103-163 |

- 모든 관리자 라우트에 `admin.ip`(허용 IP) 미들웨어가 걸린다. 허용 IP 밖이면 로그인 폼 대신 `admin.errors.ip-denied` 403 화면 + `login_logs.event=IP_DENIED` 적재(local 환경 제외) — app/Http/Middleware/AdminIpMiddleware.php:18-36
- 로그인 POST 는 `throttle:10,1`(같은 출처 분당 10회) — routes/admin.php:117
- URL 접두사 `{admin}` = `config('admin.prefix')`(기본 `sj-admin`) — config/admin.php:5

## 2. 화면별 라우트

### ADMN-LOGIN-001 관리자 로그인 (+ P1 · 세션 연장)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 관리자 루트 → 대시보드 | GET | `/{admin}` | `admin.` | 로그인 밖 | closure |
| 로그인 폼 | GET | `/{admin}/login` | `admin.login` | 로그인 밖 | AuthController@loginForm |
| 로그인 처리 | POST | `/{admin}/login` | `admin.login.post` | 로그인 밖(분당 10회) | AuthController@login |
| 로그아웃 | POST | `/{admin}/logout` | `admin.logout` | 로그인 밖 | AuthController@logout |
| 세션 연장(만료 안내 [연장]) | POST | `/{admin}/session/extend` | `admin.session.extend` | 로그인만 | AuthController@extendSession |
| P1 [비밀번호 재설정하기] | POST | `/{admin}/password-reset/from-lock` | `admin.password-reset.from-lock` | 로그인 밖 | PasswordResetController@fromLock |

- 로그인 성공 후 이동 순서(AuthController.php:68-95): ① `must_change_password` 이면 `admin.password-change.form` ② 로그인 전에 가려던 경로(세션 키 `admin_intended`)가 안전하고 그 라우트 권한이 있으면 그곳 ③ 역할별 랜딩 `AuthService::landingRoute()`.
- 이미 로그인한 상태로 로그인 폼을 열면 랜딩으로 보낸다 — AuthController.php:31-33
- 역할별 랜딩(config/admin.php:35-51, 키 = `admin_roles.code`): super · cs · finance → `admin.dashboard`, logistics → `admin.deliveries.index`, instructor · assistant → `admin.study-qnas.index`. 매핑 라우트에 권한이 없으면 SNB 순서 첫 메뉴, 그것도 없으면 `admin.dashboard` — app/Services/Admin/AuthService.php:339-395

### 비밀번호 주기 변경 (개발 ADMN-LOGIN-B, 프로토타입 MODE 4 대응)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 변경 폼 | GET | `/{admin}/password-change` | `admin.password-change.form` | 로그인만 | PasswordChangeController@form |
| 변경 저장 | PUT | `/{admin}/password-change` | `admin.password-change.update` | 로그인만 | PasswordChangeController@update |

- 강제 대상(`admin_must_change_password` 세션 플래그)은 이 두 라우트와 로그아웃만 통과, 나머지 요청은 변경 폼으로 리다이렉트 — app/Http/Middleware/AdminAuthMiddleware.php:95-100, :136-145
- 저장 성공 시 플래그 제거 → 역할별 랜딩 + `success` 플래시 — PasswordChangeController.php:47-52

### ADMN-LOGIN-002 아이디 찾기
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 폼(`?restart=1` 이면 진행 상태 초기화) | GET | `/{admin}/find-id` | `admin.find-id.form` | 로그인 밖 | FindIdController@form |
| 인증번호 발송(SMS) | POST | `/{admin}/find-id/send-code` | `admin.find-id.send-code` | 로그인 밖 | FindIdController@sendCode |
| 인증번호 확인 | POST | `/{admin}/find-id/verify-code` | `admin.find-id.verify-code` | 로그인 밖 | FindIdController@verifyCode |
| 찾은 아이디로 로그인 화면 | POST | `/{admin}/find-id/to-login` | `admin.find-id.to-login` | 로그인 밖 | FindIdController@toLogin |
| 찾은 아이디로 비밀번호 찾기 | POST | `/{admin}/find-id/to-password-reset` | `admin.find-id.to-password-reset` | 로그인 밖 | FindIdController@toPasswordReset |

### ADMN-LOGIN-003 비밀번호 찾기 · 재설정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 폼(`?restart=1` 초기화) | GET | `/{admin}/password-reset` | `admin.password-reset.form` | 로그인 밖 | PasswordResetController@form |
| 1단계 이메일 인증번호 발송 | POST | `/{admin}/password-reset/send-code` | `admin.password-reset.send-code` | 로그인 밖 | PasswordResetController@sendCode |
| 1단계 인증번호 확인 | POST | `/{admin}/password-reset/verify-code` | `admin.password-reset.verify-code` | 로그인 밖 | PasswordResetController@verifyCode |
| 2단계 휴대전화 인증번호 발송 | POST | `/{admin}/password-reset/sms/send-code` | `admin.password-reset.sms.send-code` | 로그인 밖 | PasswordResetController@sendSmsCode |
| 2단계 인증번호 확인 | POST | `/{admin}/password-reset/sms/verify-code` | `admin.password-reset.sms.verify-code` | 로그인 밖 | PasswordResetController@verifySmsCode |
| 3단계 새 비밀번호 저장 | POST | `/{admin}/password-reset` | `admin.password-reset.store` | 로그인 밖 | PasswordResetController@reset |

## 3. 폼 필드 · 검증

### 로그인 폼 `#loginForm` (LoginRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `login_id` | required · string (화면 maxlength 60) | — | `#inp-login-email` 관리자 아이디 |
| `password` | required · string · min:6 | — | `#inp-login-pw` 비밀번호 |

- 오류 문구: 없는 아이디 · 관리자 역할 그룹 미지정 · 비밀번호 오류 모두 "아이디 또는 비밀번호가 올바르지 않습니다." 비밀번호 오류만 `(n/5회)` 를 붙이고 `fail_count` 를 화면에 넘긴다 — AuthService.php:149-230
- 실패 응답이 세션 플래시로 넘기는 값: `lock_reason` · `fail_count` · `locked_at`, 오류 키 `login` — AuthController.php:58-66
- 로그아웃 사유 플래시 `logout_reason`: `idle` · `session_expired`(같은 문구 "장시간 조작이 없어 자동 로그아웃되었습니다…") · `session_kicked`(다른 기기 로그인) · `account_disabled`(잠긴 계정) — resources/views/admin/auth/login.blade.php:20-28, AdminAuthMiddleware.php:21-31

### P1 [비밀번호 재설정하기] (Request 없음)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `login_id` (hidden, `old('login_id')`) | 컨트롤러가 trim | — | `#lockout-account` 의 아이디 |

### 비밀번호 변경 `#passwordChangeForm` (AdminPasswordChangeRequest, authorize = 세션 admin_id)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `current_password` | required · string | — | `#inp-chg-cur` 임시 비밀번호 |
| `password` | required · string · min:8 · max:12 · 영문+숫자+특수문자 · confirmed (`AdminPasswordPolicyService::rules()`) | — | `#inp-chg-pw1` |
| `password_confirmation` | (confirmed 대상) | — | `#inp-chg-pw2` |

- 서비스 추가 판정(AdminPasswordPolicyService.php:89-200): 아이디(이메일 로컬파트) · 이름 3자 이상 포함 금지, 연속 문자열 4자(1234 · qwer) 금지, 현재 + 최근 `site_settings.password_history_count`(기본 3)개 재사용 금지. 실패 시 오류 키 `password_change`, 입력값은 돌려주지 않음.
- 저장: 직전 해시를 `password_histories` 로 옮기고 개수 정리 → `users.password` 갱신 → `login_logs.event=PASSWORD_RESET` → 메일 + 휴대전화 변경 알림 — app/Services/Admin/AdminPasswordChangeService.php:40-85

### 아이디 찾기 (FindIdSendCodeRequest · FindIdVerifyCodeRequest)
| 필드 name | 규칙 | 프로토타입 대응 요소 |
|---|---|---|
| `name` | required · string · 2~20자 | `#inp-find-name` |
| `phone` | required · string · 숫자 10~11자리(하이픈 없음) | `#inp-find-phone` |
| `code` | required · digits:6 | `#inp-find-otp` |

### 비밀번호 찾기 (PasswordResetSendCodeRequest · PasswordResetVerifyCodeRequest · PasswordResetSmsSendRequest · PasswordResetSmsVerifyRequest · PasswordResetRequest)
| 단계 | 필드 name | 규칙 | 프로토타입 대응 요소 |
|---|---|---|---|
| 1 이메일 | `login_id` | required · string · max:60 | `#inp-reset-email` |
| 1 이메일 | `code` | required · digits:6 | (없음 — 프로토타입은 이메일 인증 단계 없음) |
| 2 휴대전화 | `name` | required · string · 2~20자 | (없음) |
| 2 휴대전화 | `phone` | required · digits_between:10,11 | `#inp-reset-phone` |
| 2 휴대전화 | `code` | required · digits:6 | `#inp-reset-otp` |
| 3 저장 | `password` · `password_confirmation` | required · 8~12자 · 영문+숫자+특수문자 · confirmed | `#inp-reset-pw1` · `#inp-reset-pw2` |

- 인증번호 한도(config/admin.php:59-81): 계정 · IP 각 24시간 롤링 3회 발송, IP 실패 시도 24시간 10회, SMS 유효 180초(이메일은 별도 — 설계서 5분 주석).

## 4. 목록 필터 · 정렬 · 표 컬럼
해당 없음(목록 화면 아님).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| users.login_id | string(50) | 관리자 로그인 아이디(이메일 형식) | 아이디 입력 · P1 계정 |
| users.password | string(255) | 해시 | — |
| users.login_fail_count | unsignedTinyInteger | 연속 실패 횟수, 성공 시 0 | `(n/5회)` 문구 |
| users.is_locked | boolean | 로그인 차단(5회 자동 잠금 · 관리자 정지 공용) | P1 / 정지 Alert |
| users.lock_reason | string(20) | `auto_5fail`=5회 실패(재설정으로 해제) / `admin_block`=관리자 정지(재설정으로 안 풀림) / NULL=미잠금 | `auto_5fail` 만 P1, `admin_block` 은 공통 Alert |
| users.locked_until | timestamp | 자동 해제 예정 시각(영구 잠금 NULL) | — |
| users.last_login_at | timestamp | 최종 로그인 | — |
| users.must_change_password | boolean | 비밀번호 변경 강제(첫 로그인 · 90일 경과) | 변경 화면 진입 |
| users.password_changed_at | dateTime | 마지막 변경 일시, 90일 판정 기준(`admin.password_max_age_days`) | — |
| password_histories.user_id · password_hash · created_at | — | 재사용 금지 대조용 과거 해시 | — |
| login_logs.event | string(30) | 로그인 관련 `LOGIN_SUCCESS` · `LOGIN_FAIL` · `ACCOUNT_LOCKED` · `LOGIN_BLOCKED`(잠긴 계정 재시도) · `ACCOUNT_UNLOCKED` · `PASSWORD_RESET` · `IP_DENIED` · `SESSION_EXPIRED` 등 18종(전체 app/Models/LoginLog.php:23-42, ADMN-CONF-010.md 4절) | CONF-010 로그인 로그 |
| login_logs.status · fail_reason | string | success/fail · 사유(`unknown_account` · `no_admin_role` · `invalid_password` 등) | 〃 |
| login_logs.fail_count · login_id · ip · user_agent · country · detail | — | 시점 실패 횟수 · 시도 아이디 원문 · 잠금 시 직전 실패 스냅샷(JSON) | P1 잠금 일시 = 최신 `ACCOUNT_LOCKED.created_at` |
| admin_allowed_ips.ip · admin_role_id · user_id · is_active | — | 관리자 접속 허용 IP(전역 · 역할 · 계정) | IP 차단 화면 |
| admin_roles.code | string(30) | `super` · `cs` · `logistics` · `finance` · `instructor` · `assistant` | 랜딩 결정 |
| site_settings.cs_tel · cs_hours · email | — | 문의처(값 없으면 줄 숨김) | 로그인 하단 · P1 해제 방법 |
| site_settings.password_history_count | — | 재사용 금지 비교 개수(기본 3) | — |
| verification_attempts.* (`user_type=admin`, `purpose` find_id · find_pw) | — | 인증번호 발송 · 실패 집계 | — |

- 설정값(config/admin.php): `login_max_attempts` 5 · `login_lockout_minutes` 30 · `idle_minutes` 30(무조작 로그아웃) · `password_max_age_days` 90(0 이하면 강제 안 함).
- 세션 키: `admin_id` · `admin_login_id` · `admin_name` · `admin_role` · `admin_email` · `admin_phone` · `admin_last_activity` · `admin_must_change_password` · `admin_intended`. Redis `admin_session:{userId}` = 중복 로그인 판정(TTL = idle 분) — AuthService.php:265-298

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#loginForm` (POST `admin.login.post`) | 로그인 폼 | (폼 없음, `handleAdminLogin()`) |
| `#login_id` · `#password` (`.input__account`) | 입력 | `#inp-login-email` · `#inp-login-pw` |
| `#passwordToggle` (`.account__password-toggle`, aria-pressed) | 비밀번호 표시 토글 | (없음) |
| `#capsLockWarn` (`.fm__help--warn`, hidden) | Caps Lock 경고 | `#caps-lock-warn` |
| `.fm__help--count` | 실패 횟수 문구 | `#lbl-fail-cnt` |
| `#loginSubmit` (`.btn__system.login__submit`) | 로그인 버튼 · 이중 제출 방지 | `#btn-do-login` |
| `.login__expired` | 로그아웃 사유 문구 | `#banner-session-expired` |
| `.login__link` → `admin.find-id.form?restart=1` · `admin.password-reset.form?restart=1` | 찾기 링크(페이지 이동) | `switchAuthMode()` 탭 전환 |
| `#layerAccountLock` (`.layer-pop__overlay.layer-pop--hidden`, 열면 `layer_pop--show` + body `layer--open`) | P1 잠금 안내 레이어 | `#box-lockout-p1`(인라인 경고 박스) |
| `#lockTargetId` · `.lockpop__info`(잠금 일시 · 접속 IP 마스킹 · 계정 상태) · `.lockpop__guide` | P1 내용 | `#lockout-account` |
| `#layerSessionExpire` `data-remain`(남은 초) | 만료 1분 전 안내 레이어 — [연장] `admin.session.extend` / [로그아웃] `admin.logout` (layouts/footer.blade.php:31 에서 전 화면 포함) | (없음) |
| 헤더 `X-Admin-Background: 1` | 주기 요청은 활동 시각을 늘리지 않음 | — |
| `#passwordChangeForm` · `#current_password` · `#password` · `#password_confirmation` · `#confirmMismatch` | 비밀번호 변경 | `#inp-chg-cur` · `#inp-chg-pw1` · `#inp-chg-pw2` |
| `.pwreset__step`(is-on · is-done) · `#sendCodeBtn` · `#verifyForm` · `#code` · `#codeTimer` · `#codeExpired` · `#sessionTimer` · `#findIdResult` | 아이디 찾기 · 비밀번호 찾기 공용 단계 UI | `#inp-find-*` · `#box-found-id-result` |
| `#owner_name` · `#owner_phone` · `#smsSendBtn` · `#smsVerifyForm` · `#sms_code` · `#smsCodeTimer` · `#pwResetForm` · `#pwRule` · `#pwMatch` · `#pwResetSubmit` | 비밀번호 찾기 2 · 3단계 | `#inp-reset-*` |

- 하위 화면 표현: P1 · 세션 만료 = 같은 페이지 레이어(공통 `layer-pop` 구조). 아이디 찾기 · 비밀번호 찾기 · 비밀번호 변경 = 별도 페이지(`admin.auth.find-id` · `password-reset` · `password-change` Blade).

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 만료 1분 전 안내 레이어 + [연장](`admin.session.extend`). 프로토타입은 로그아웃 뒤 배너만 있음.
- 로그아웃 사유 구분 문구(다른 기기 로그인 `session_kicked` · 계정 비활성 `account_disabled`).
- 관리자 정지(`admin_block`)는 P1 이 아니라 공통 Alert("사용이 중지된 계정입니다…").
- 비밀번호 표시 토글, P1 의 잠금 일시 · 접속 IP(뒤 2옥텟 마스킹) · 계정 상태, 문의처(site_settings).
- 90일 경과 강제 변경(같은 `password-change` 화면, 안내 문구만 `forced` 로 분기).
- 비밀번호 찾기 1단계 이메일 인증번호(이름 · 휴대전화 SMS 는 2단계).
- 허용 IP 밖 접속 차단 화면.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 시연용 계정 프리셋 `#sel-demo-account`, 시연 버튼(세션만료 배너 · 잠금) — 시연 전용, 개발 대응 불필요.
- 로그인 화면 안의 권한 없음 안내 `#box-noperm`, 만료 배너의 `return=` 표시(개발은 `admin_intended` 세션으로 복귀하되 화면에 표시하지 않음).
- "관리자 · 파트너 통합 게이트웨이" 문구(개발 역할 코드에 출판사 · 저작권자 파트너 없음 — 8절).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 필드 id: `inp-login-email`→`login_id`, `inp-login-pw`→`password`, `inp-chg-cur/pw1/pw2`→`current_password`/`password`/`password_confirmation`, `inp-find-name/phone/otp`→`name`/`phone`/`code`, `inp-reset-*`→`login_id`·`phone`·`code`·`password`.
- 비밀번호 길이: 프로토타입 8~20자, 개발 8~12자.
- 휴대전화: 프로토타입 하이픈 포함 샘플, 개발 숫자 10~11자리.
- P1: 프로토타입 인라인 경고 박스 → 개발 레이어 `#layerAccountLock`.
- 아이디 찾기 결과 → 로그인: 프로토타입 링크 클릭(아이디를 JS 로 채움), 개발 POST `admin.find-id.to-login`(URL 에 아이디를 싣지 않음).
- 화면 전환: 프로토타입 한 페이지 탭(`switchAuthMode`), 개발 페이지 3개.
- MODE 4 이름: 프로토타입 "첫 로그인 · 임시 비밀번호", 개발 `password-change`(첫 로그인 · 90일 공용, 플래그 `must_change_password`).

## 8. 정책 질문 (white 확인 필요)
- 비밀번호 길이 상한: 프로토타입 20자 vs 개발 12자 — 확인 필요.
- 비밀번호 찾기 인증 순서: 프로토타입은 아이디 + 휴대전화 SMS 1회, 개발은 이메일 인증번호 → 휴대전화 SMS 2단계 — 확인 필요.
- 파트너(출판사 · 저작권자) 로그인: 프로토타입은 통합 게이트웨이, 개발 역할 코드는 super · cs · logistics · finance · instructor · assistant 뿐 — 확인 필요.
- 로그인 비밀번호 min:6(LoginRequest) vs 정책 8자 — 로그인 입력 하한이 6자인 이유가 코드에 없음 — 확인 필요.

## 출처
- routes/admin.php:103-163 (인증 라우트 그룹 · throttle)
- app/Http/Controllers/Admin/AuthController.php:27-143
- app/Http/Controllers/Admin/PasswordChangeController.php:23-53
- app/Http/Controllers/Admin/FindIdController.php:31-148 · PasswordResetController.php:34-185
- app/Http/Requests/Admin/LoginRequest.php:14-28 · AdminPasswordChangeRequest.php:18-44 · `_index/requests.md` FindId* · PasswordReset*
- app/Services/Admin/AuthService.php:20-25, :142-258, :265-298, :339-401
- app/Services/Admin/AdminPasswordPolicyService.php:35-200 · AdminPasswordChangeService.php:40-85
- app/Http/Middleware/AdminAuthMiddleware.php:21-145, :198-237 · AdminIpMiddleware.php:18-36
- config/admin.php:5-81
- resources/views/admin/auth/login.blade.php:1-283 · password-change.blade.php:23-78 · find-id.blade.php:66-200 · password-reset.blade.php:72-299
- resources/views/admin/inc/session-expire.blade.php:1-50 · layouts/footer.blade.php:31
- `_index/schema.md` users · login_logs · password_histories · admin_allowed_ips · admin_roles · verification_attempts
- 프로토타입: prototype_clean/ADMN-LOGIN-001_baseline.html:262-394, :408-695
