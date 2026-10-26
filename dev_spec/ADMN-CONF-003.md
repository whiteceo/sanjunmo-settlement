# ADMN-CONF-003 플레이어/DRM · 인증 발송 설정 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-003_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-003 플레이어/DRM 설정 · ADMN-CONF-008 인증 발송 설정(프로토타입 2번째 탭) · 프로토타입 탭 안의 개인정보 재마스킹 · 수동 포인트 유효기간 · 학습 Q&A 운영 방식
- 개발 진행: CONF-003 구현(담당 박성민, `_index/progress.md` 108행) · CONF-008 구현(담당 이응민, 114행). 재마스킹 · 포인트 유효기간 선택지 · 학습 Q&A 운영 방식 설정 화면은 개발 미구현(7절)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.player-settings.index` | 플레이어/DRM 설정 | routes/admin.php:1153. 메뉴 권한에 더해 컨트롤러가 최고 관리자만 허용(`isSuperAdmin`, 아니면 403 — URL 직접 호출 포함) — PlayerSettingController.php:95-101 |
| `admin.verify-settings.index` | 인증 발송 설정 | routes/admin.php:1141 |

## 2. 화면별 라우트

### ADMN-CONF-003 플레이어/DRM 설정 (단일 설정 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 설정 화면(+ 최근 변경 3건) | GET | `/{admin}/player-settings` | `admin.player-settings.index` | can_view + 최고 관리자 | PlayerSettingController@index |
| 변경 이력 전체(조회 전용) | GET | `/{admin}/player-settings/history` | `admin.player-settings.history.index` | can_view + 최고 관리자 | PlayerSettingController@history |
| 재생 중 인원(저장 확인 모달이 열릴 때 JSON) | GET | `/{admin}/player-settings/playing-count` | `admin.player-settings.playing-count.index` | can_view + 최고 관리자 | PlayerSettingController@playingCount |
| 저장 | PUT | `/{admin}/player-settings` | `admin.player-settings.update` | can_update + 최고 관리자 | PlayerSettingController@update |

- playing-count 응답: `{ok, count, window_minutes}` — 최근 2분(`PLAYING_WINDOW_MINUTES`) 재생 수강생 — PlayerSettingController.php:81-92
- 저장 성공 문구: "플레이어 설정을 저장했습니다. 수강생 화면에는 다음 강의를 열 때 반영됩니다."

### ADMN-CONF-008 인증 발송 설정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 화면(`?account=` 수동 초기화 대상 조회) | GET | `/{admin}/verify-settings` | `admin.verify-settings.index` | can_view | VerifySettingController@index |
| 한도 저장(즉시 사용자단 반영) | PUT | `/{admin}/verify-settings` | `admin.verify-settings.update` | can_update | VerifySettingController@update |
| 예외 IP 등록 | POST | `/{admin}/verify-settings/ip-exceptions` | `admin.verify-settings.ip-exceptions.store` | can_create | VerifySettingController@storeIpException |
| 예외 IP 삭제 | DELETE | `/{admin}/verify-settings/ip-exceptions/{ipException}` | `admin.verify-settings.ip-exceptions.destroy` | can_delete | VerifySettingController@destroyIpException |
| 계정 발송 횟수 수동 초기화 | POST | `/{admin}/verify-settings/resets` | `admin.verify-settings.resets.store` | can_create | VerifySettingController@storeReset |

## 3. 폼 필드 · 검증

### 플레이어 설정 `#playerSettingForm` (PlayerSettingRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `watermark_use` | required · boolean | — | (없음 — 항상 사용) |
| `watermark_content` | required · in | `email` 로그인 계정 이메일 전체 | `#pl-wm-text` |
| `watermark_move_interval` | required · 1~300 초 | 기본 10 | `#pl-wm-interval` |
| `watermark_display_duration` | required · 1~300 · ≤ move_interval | 기본 5 | `#pl-wm-duration` |
| `watermark_opacity` | required · 1~100 % | 기본 35 | `#pl-wm-opacity` |
| `watermark_font_size` | required · 8~48 px | 기본 14 | `#pl-wm-size` |
| `watermark_mobile_same` | required · boolean | 모바일 앱 동일 적용 | (없음) |
| `limit_forward` | required · boolean | 첫 수강 건너뛰기 제한 | 라디오 `ON`/`OFF` |
| `limit_forward_free_off` | required · boolean | 무료 · 맛보기 예외 | (OFF 라벨 문구에 포함) |
| `speed_min` | required · in 배속 단계(0.5 · 0.75 · 1.0 · 1.25 · 1.5 · 1.75 · 2.0) | — | (없음) |
| `speed_max` | required · in 배속 단계 · ≥ speed_min | — | `#pl-max-speed`(2.0 · 1.5 · 2.5) |
| `progress_speed_policy` | required · in | `all` 전 배속 인정 · `limited` 일부 배속만 인정 | `#pl-credit-speed`(숫자) |
| `resume_use` | required · boolean | 이어보기 | (없음) |
| `resume_offset_sec` | required · 0~600 초 | 기본 5 | number(L214) |
| `rewind_allow` | required · boolean | 10초 뒤로 허용 | (없음) |

- 단말 · DRM 항목(`device_pc_limit` · `device_mobile_limit` · `device_reset_limit` · `concurrent_session` · `drm_method` · `block_record_mobile` · `warn_capture_pc` · `download_allow`)은 "콘솔 소관"으로 요청에 담지 않는다(화면 표시만) — PlayerSettingController.php:43-45 주석

### 인증 한도 `#verifySettingForm` (VerifySettingRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `verify_daily_limit` | required · 1~99 | 계정(DI) 기준 24시간 롤링 한도 | "계정/휴대폰당 24시간 발송" |
| `verify_ip_daily_limit` | required · 1~99 | IP 기준 24시간 롤링 한도 | "동일 IP 24시간 발송" |
| `verify_session_ttl_user_min` | required · 5~60 분 | 사용자 인증 유효 시간(저장은 초 `verify_session_ttl_user_sec`, 화면은 분으로 환산 — VerifySettingService.php:64, :83) | (없음) |

### 예외 IP `#verifyIpLayer` (VerificationIpExceptionRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `mode` | required · in | `single` 단일 IP · `cidr` IP 대역(CIDR, 최소 /16) | (없음) |
| `ip` | required · max:45 · mode 별 형식 | — | `#new-ip-val` |
| `memo` | required · max:100 | 등록 사유 | `#new-ip-memo` |

### 수동 초기화 (VerifyCapResetRequest)
| 필드 name | 규칙 | 프로토타입 대응 요소 |
|---|---|---|
| `user_id` | required · integer ≥1 | (없음) |
| `reason` | required · max:200 | (없음) |
| 조회 쿼리 `account` | 이메일 또는 회원번호(maxlength 100) | (없음) |

## 4. 목록 필터 · 정렬 · 표 컬럼
- 플레이어 변경 이력: admin_logs 원장을 읽는다(조회 전용, 20건 페이지 · 쿼리 `history_page`) — PlayerSettingService.php:128-185. 프로토타입 표 "변경 일시 · 변경 관리자 · 변경 항목 · 변경 전 · 변경 후" 와 같은 정보.
- 인증 설정: 예외 IP 목록(IP · 메모 · 등록자), `account` 조회 결과로 초기화 대상 표시.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| player_settings.watermark_* | — | 워터마크 사용 · 내용 · 이동 주기 · 노출 시간 · 투명도 · 글자 크기 · 모바일 동일 | ② 워터마크 |
| player_settings.limit_forward · limit_forward_free_off | boolean | 건너뛰기 제한 · 무료 예외 | ④ 재생 제어 |
| player_settings.speed_min · speed_max | decimal(3,2) | 배속 범위 | 〃 |
| player_settings.progress_speed_policy | string(20) | `all` / `limited` | 〃 |
| player_settings.resume_use · resume_offset_sec · rewind_allow | — | 이어보기 · N초 전 · 되감기 | 〃 |
| player_settings.device_pc_limit · device_mobile_limit · device_reset_limit · concurrent_session | tinyint | 단말 대수(종류별 1) · 연 초기화 횟수 · 동시 재생 세션 | 단말 · 동시접속(표시만) |
| player_settings.drm_method · block_record_mobile · warn_capture_pc · download_allow | — | DRM 방식 · 녹화 차단 · 캡처 경고 · 다운로드 허용(기본 0) | 〃 |
| admin_logs | — | 플레이어 설정 변경 이력 원장 | 변경 이력 |
| site_settings.verify_daily_limit · verify_ip_daily_limit | tinyint/smallint | 계정 · IP 24시간 한도(기본 10) | 인증 한도 |
| site_settings.verify_session_ttl_user_sec | smallint | 사용자 인증 세션(기본 1800초) | 인증 유효 시간 |
| site_settings.verify_ip_hourly_limit · verify_max_attempts · verify_code_ttl_sec · verify_resend_cooldown_sec · verify_session_ttl_admin_sec | — | 시간당 소프트캡 · 오입력 횟수 · 코드 유효(300초) · 재발송 쿨다운(30초) · 관리자 세션 | 화면 입력 없음 |
| verification_ip_exceptions.ip · memo · created_by | — | 예외 IP/대역 · 사유 · 등록자 | 예외 IP 목록 |
| verification_attempts.reset_at · reset_by · users.verify_cap_reset_at | — | 수동 초기화 기록 | 수동 초기화 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#playerSettingForm` · `[data-ps-field]` | 플레이어 폼 · 변경 감지 | 플레이어 탭 |
| `#conf-watermark` · `#conf-control` · `#conf-device` · `#conf-preview` | 섹션 앵커 | 표 행 |
| `#playerSettingPreview` · `#playerSettingPreviewMark` | 워터마크 미리보기 | `updateWmPreview()` |
| `#playerSettingOpenSave` → `#layerPlayerSettingSave`(`#playerSettingDiff` 변경 전/후 · `#playerSettingImpact` 영향 안내 · `#playerSettingPlaying` 재생 중 인원) · `#playerSettingConfirm` | 저장 확인 레이어 | `savePlayerConfig()` 즉시 저장 |
| `#playerSettingRestore` | 기본값 복원 | (없음) |
| `#verifySettingForm` · `#verifySaveOpen` → `#verifySaveLayer`(`#verifySaveChanges` · `#verifySaveImpact`) | 한도 저장 확인 | [인증 정책 저장] |
| `#verifyIpLayer` | 예외 IP 등록 레이어 | `addWhitelistIp()` 인라인 |
| `[data-current]` · `[data-usage]` · `[data-labels]` | 현재값 · 사용량 표시 | — |

- 하위 화면 표현: 플레이어 설정과 인증 발송 설정은 별도 페이지(메뉴 2개). 변경 이력 전체는 별도 페이지, 확인 · 등록은 레이어.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 저장 전 확인 레이어(변경 전/후 · 영향 안내 · 지금 재생 중 인원), 기본값 복원, 변경 이력 전체 페이지.
- `speed_min`, `progress_speed_policy`(all/limited), `resume_use` · `rewind_allow` · `watermark_mobile_same` · `limit_forward_free_off` 를 독립 필드로.
- 인증 설정: 사용자 인증 유효 시간(`verify_session_ttl_user_min`), 계정별 발송 횟수 수동 초기화(`resets`), 예외 IP 등록 방식 `single`/`cidr`.
- 최고 관리자 전용(플레이어 설정).

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 개인정보 재마스킹 시간 설정(`#pv-member-sec` · `#pv-holder-sec`) — 개발은 상수 `MaskingService::UNMASK_TTL_SECONDS`=30 (app/Services/MaskingService.php:103-106), 화면 없음. 이름(규칙): `site_settings.pii_unmask_ttl_member_sec` · `pii_unmask_ttl_holder_sec` (규칙)
- 수동 포인트 유효기간 선택지(`#mpe-days` · `#mpe-default`) — 개발 미구현, 규칙 기반 명명: `site_settings.manual_point_expire_options` · `manual_point_expire_default` (규칙)
- 학습 Q&A 운영 방식(`lqnaMode` CAFE/INTERNAL) — 개발 미구현, 규칙 기반 명명: `site_settings.study_qna_mode` = `cafe` · `internal` (규칙)
- "24시간 접속 IP 급증" 감지 행, 재발송 쿨다운 · 인증번호 유효 시간 입력(개발은 site_settings 값만 있고 화면 입력 없음).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- `#pl-wm-*` → `watermark_*`, `#pl-max-speed` → `speed_max`(선택지 0.5~2.0, 프로토타입 2.5x 없음), `#pl-credit-speed`(숫자) → `progress_speed_policy`(all/limited).
- 워터마크 내용 선택지 3종 → 개발 `email` 1종.
- 허용 IP `#new-ip-val` · `#new-ip-memo` → `ip` · `memo`(+ `mode`).
- 탭 2개 한 페이지 → 메뉴 2개 페이지(`player-settings` · `verify-settings`).

## 8. 정책 질문 (white 확인 필요)
- 재생 배속 상한 2.5x 허용 여부(프로토타입 선택지 있음, 개발 최대 2.0) — 확인 필요.
- 진도 인정 배속: 숫자 입력(프로토타입) vs 전/일부 인정 2택(개발) — 확인 필요.
- 재마스킹 시간을 회원 · 권리자 별도 설정으로 둘지(개발 30초 고정) — 확인 필요.

## 출처
- routes/admin.php:1137-1157
- app/Http/Controllers/Admin/PlayerSettingController.php:23-101 · VerifySettingController.php:19-70
- app/Services/Admin/PlayerSettingService.php:30-50, :128-185
- `_index/requests.md` PlayerSettingRequest · VerifySettingRequest · VerificationIpExceptionRequest · VerifyCapResetRequest
- app/Models/PlayerSetting.php:69-146
- app/Services/MaskingService.php:103-137
- resources/views/admin/player-settings/index.blade.php · history.blade.php · verify-settings/index.blade.php:121-127
- `_index/schema.md` player_settings · site_settings(verify_*) · verification_ip_exceptions · verification_attempts
- 프로토타입: prototype_clean/ADMN-CONF-003_baseline.html:103-587 (digest 기준)
