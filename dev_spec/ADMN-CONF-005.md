# ADMN-CONF-005 운영자 권한 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-005_baseline.html (원본 상태: 84c22e2)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-005 탭 1 관리자 계정 · 탭 2 역할 그룹 · 권한(+ 모달 역할 그룹 추가 · 변경 영향 확인 · 계정 발급) · 개발 메뉴 관리(`admin-menus`, 프로토타입 없음)
- 개발 진행: 구현(담당 이응민, `_index/progress.md` 111행). 역할 그룹 추가 · 미사용 전환 · 변경 이력은 개발 미구현(7절)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.admin-users.index` | 관리자 계정 | routes/admin.php:213 |
| `admin.admin-roles.index` | 권한 그룹 | routes/admin.php:228 |
| `admin.admin-menus.index` | 메뉴 관리 | routes/admin.php:236 |

- 권한 판정(AdminPermissionService.php:261-306, :358-379): 라우트 이름 접미사 → `index`·`show` can_view, `create`·`store` can_create, `edit`·`update` can_update, `destroy` can_delete, `download` can_download, 그 밖 예외 접미사(`recalculate` · `status-sync` · `reset-verify-cap` · `nts-verify` → can_update, `contracts` → can_view). 매핑 밖 접미사는 차단. 메뉴는 이름을 `…index` 로 정규화해 `admin_menus.route_name` 과 맞추고 없으면 하위 자원 세그먼트를 걷어 부모로 올라간다. `ROUTE_PERMISSIONS` 예외 3건(`admin.deliveries.dispatch.download` · `admin.pass-refunds.payouts.download` · `admin.settlement.board.download`)은 can_download + can_update 둘 다 요구.
- 최고관리자(`super`) 권한 그룹 편집은 최고관리자만(아니면 목록으로 "최고관리자 권한 그룹은 최고관리자만 수정할 수 있습니다.") — AdminRoleController.php:59-67
- 인증번호 발송 횟수 초기화 버튼은 최고관리자에게만 노출(`canResetVerifyCap`) — AdminUserController.php:98

## 2. 화면별 라우트

### 탭 1 관리자 계정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/admin-users` | `admin.admin-users.index` | can_view | AdminUserController@index |
| 발급 폼 | GET | `/{admin}/admin-users/create` | `admin.admin-users.create` | can_create | AdminUserController@create |
| 발급 | POST | `/{admin}/admin-users` | `admin.admin-users.store` | can_create | AdminUserController@store |
| 수정 폼 | GET | `/{admin}/admin-users/{adminUser}/edit` | `admin.admin-users.edit` | can_update | AdminUserController@edit |
| 수정(잠금 · 해제 포함) | PUT | `/{admin}/admin-users/{adminUser}` | `admin.admin-users.update` | can_update | AdminUserController@update |
| 인증번호 발송 횟수 초기화 | POST | `/{admin}/admin-users/{adminUser}/reset-verify-cap` | `admin.admin-users.reset-verify-cap` | can_update | AdminUserController@resetVerifyCap |

- 삭제 경로 없음 — 계정은 정지(잠금)로만 막는다(로그의 행위자 추적 유지) — routes/admin.php:218-220 주석

### 탭 2 역할 그룹 · 권한
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 권한 그룹 목록 | GET | `/{admin}/admin-roles` | `admin.admin-roles.index` | can_view | AdminRoleController@index |
| 그룹 정보 · 메뉴 권한 편집 | GET | `/{admin}/admin-roles/{adminRole}/edit` | `admin.admin-roles.edit` | can_update | AdminRoleController@edit |
| 저장 | PUT | `/{admin}/admin-roles/{adminRole}` | `admin.admin-roles.update` | can_update | AdminRoleController@update |

- 권한 그룹 등록 · 삭제 라우트 없음(AdminRoleRequest 는 등록용 `code` 규칙을 갖고 있으나 store 라우트가 없다).

### 메뉴 관리 (개발에만)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/admin-menus` | `admin.admin-menus.index` | can_view | AdminMenuController@index |
| 등록 폼 · 등록 | GET · POST | `/{admin}/admin-menus/create` · `/{admin}/admin-menus` | `admin.admin-menus.create` · `.store` | can_create | AdminMenuController@create · store |
| 수정 폼 · 수정 | GET · PUT | `/{admin}/admin-menus/{adminMenu}/edit` · `/{admin}/admin-menus/{adminMenu}` | `admin.admin-menus.edit` · `.update` | can_update | AdminMenuController@edit · update |
| 삭제 | DELETE | `/{admin}/admin-menus/{adminMenu}` | `admin.admin-menus.destroy` | can_delete | AdminMenuController@destroy |

## 3. 폼 필드 · 검증

### 계정 발급 · 수정 (AdminUserRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `login_id` | required · max:50 · 중복 불가 | — | `#af-id` 계정 ID |
| `name` | required · max:50 | — | `#af-name` 성명 · 소속 |
| `email` | nullable · email · max:100 · 중복 불가 | — | (없음) |
| `phone` | nullable · max:20 | — | (없음) |
| `password` · `password_confirmation` | 발급 시 required, 수정 시 비우면 유지 · 8~12자 · 영문+숫자+특수문자 · confirmed (+ 아이디 · 이름 포함 · 연속 4자 금지, 이력 대조 없음) | — | (없음) |
| `admin_role_id` | required · admin_roles 존재(최고관리자 부여 가능 여부는 서비스가 판정) | admin_roles.id | 역할 그룹 |
| `is_locked` | nullable · in:1 | 체크 = 잠금 | 라디오 `ACTIVE` / `LOCKED` |
| `unlock_reason` | 잠긴 계정을 해제할 때 required · max:200 | 잠금 해제 사유 | (없음) |
| `linked_instructor_id` | nullable · instructors 존재 | 강사 역할의 연결 강사 | 소속(데이터 범위) |
| `assistant_instructor_ids[]` | nullable · 정수 · 중복 불가 · 권리자 연결된 강사만 새로 배정 | 조교 역할의 소속 강사 | 〃 |

### 인증번호 횟수 초기화 (`verify-cap.blade.php`, Request 없음)
| 필드 name | 규칙 | 비고 |
|---|---|---|
| `reason` | 컨트롤러 trim, 서비스가 판정 | 성공 "인증번호 발송 횟수를 초기화했습니다." → `users.verify_cap_reset_at` |

### 권한 그룹 (AdminRoleRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `code` | 등록 시만 required · max:30 · `^[a-z0-9_]+$` · 중복 불가(수정 시 무시) | `super` · `cs` · `logistics` · `finance` · `instructor` · `assistant` | `#rf-id` 그룹 코드 |
| `name` | required · max:100 · 중복 불가 | — | `#rf-name` |
| `description` | nullable · max:500 | — | `#rf-desc` |
| `is_system` | nullable · in:1 | 시스템 권한(삭제 불가) | (없음) |
| `permissions[{menuId}][can_view]` · `[can_create]` · `[can_update]` · `[can_delete]` · `[can_download]` | nullable · in:1 | 메뉴별 5축 | 표 "읽기 · 쓰기 · 엑셀" |

### 메뉴 (AdminMenuRequest)
| 필드 name | 규칙 |
|---|---|
| `parent_id` | nullable · 존재 · 자기 자신 불가 |
| `name` | required · max:100 |
| `route_name` | nullable · max:100 |
| `url` | nullable · max:255 |
| `icon` | nullable · max:50 |
| `sort_order` | required · 0~999999 |
| `is_active` | required · 0/1 |

## 4. 목록 필터 · 정렬 · 표 컬럼
| 화면 | 쿼리 name | 값 | 프로토타입 대응 |
|---|---|---|---|
| 계정 | `is_locked` | '' 전체 · `0` 정상 · `1` 잠금 | (상태 열) |
| 계정 | `admin_role_id` | admin_roles.id | `#acc-role-filter` |
| 계정 | `search_field` · `keyword` | `login_id` 아이디 · `name` 관리자명 · `email` · `phone` | `#acc-keyword` |
| 계정 | `per_page` | 10 · 20(기본) · 30 | — |
| 권한 그룹 | `is_system` · `keyword` · `per_page` | 시스템 여부 · 이름 · 쪽 크기 | — |

- 계정 표: No · 아이디 · 관리자명 · 이메일 · 전화번호 · 권한 그룹 · 잠금 · 등록일 · 관리 — admin-users/index.blade.php:132-140
- 권한 그룹 표: No · 권한 그룹명 · 설명 · 시스템 · 사용 관리자 · 등록일 · 관리 — admin-roles/index.blade.php:100-106
- 권한 매트릭스(편집 화면): 메뉴명(상위 / ㄴ하위) · 조회 · 등록 · 수정 · 삭제 · 다운로드 · 전체 — admin-roles/form.blade.php:118-152

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| users.login_id · name · email · phone | — | 관리자 계정 | 계정 목록 |
| users.is_locked · lock_reason | — | 잠금(`auto_5fail` 5회 실패 / `admin_block` 관리자 정지) | 잠금 |
| users.must_change_password · password_changed_at | — | 첫 로그인 · 90일 변경 강제 | — |
| users.verify_cap_reset_at | dateTime | 인증번호 발송 횟수 수동 초기화 시각 | 초기화 |
| users.last_login_at | timestamp | 최근 접속 | (개발 목록에 없음) |
| admin_roles.code · name · description · is_system · sort_order | — | 역할 그룹 | 권한 그룹 |
| admin_user_roles.user_id · admin_role_id | — | 계정 ↔ 역할(폼은 1개 선택, 테이블은 다중 가능) | 권한 그룹 |
| admin_role_menus.admin_role_id · admin_menu_id · can_view · can_create · can_update · can_delete · can_download · note | — | 메뉴 권한 5축 · 부여 사유 메모 | 매트릭스 |
| admin_menus.parent_id · name · route_name · url · icon · sort_order · is_active · screen_code | — | 메뉴 · 권한 단위(`screen_code` = ADMN-… 화면 코드, unique) | 메뉴 관리 · 매트릭스 행 |
| instructor_assistants (조교 ↔ 강사) · instructors (강사 연결) | — | 데이터 범위 | 소속 |
| inquiry_category_roles.role_code | — | 1:1 문의 분류 ↔ 역할 code(자동 배정) | 문의 큐 |
| admin_allowed_ips.admin_role_id · user_id | — | 역할 · 계정별 허용 IP | 접속 제한 |
| admin_logs (action · before_value · after_value) | — | 계정 · 권한 변경 기록 | 변경 이력(화면 미구현) |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#admin_role_id` · `[data-role]` · `[data-code]` | 역할 선택 → 강사 · 조교 연결 칸 토글 | `renderAffTarget()` |
| `#unlock_reason` | 잠금 해제 사유 칸 | (없음) |
| `#perPageForm` · `#per_page` · `#search_field` · `#is_locked` | 목록 검색 | `#acc-role-filter` · `#acc-keyword` |
| `[data-permission]` · `permissions[{id}][{key}]` | 매트릭스 체크박스 · 행 전체 선택 | `togglePerm()` |

- 하위 화면 표현: 계정 · 권한 그룹 · 메뉴가 별도 메뉴 · 별도 페이지(목록 / create · edit 페이지). 프로토타입은 한 페이지 2탭 + 모달 3개(계정 발급 · 역할 그룹 추가 · 변경 영향 확인).

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 계정 이메일 · 전화번호 · 비밀번호 발급, 잠금 해제 사유, 인증번호 발송 횟수 초기화(최고관리자).
- 권한 5축(조회 · 등록 · 수정 · 삭제 · 다운로드) — 프로토타입은 읽기 · 쓰기 · 엑셀 3축.
- 메뉴 관리 화면(`admin-menus`).
- 최고관리자 그룹은 최고관리자만 편집.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 역할 그룹 추가 모달 · [미사용으로 변경] — 개발은 store · destroy · 상태 라우트 없음. 규칙 기반 명명: `admin.admin-roles.create` · `admin.admin-roles.store` (규칙), 미사용 `admin.admin-roles.status.update` (규칙) + `admin_roles.is_active` (규칙)
- 역할 그룹 속성: 내부/외부 구분(`INTERNAL`/`EXTERNAL`) · 문의 큐 사용(`#rf-queue`) · 노출 순서 · 시작 화면(`#rf-start`) · 대시보드 기본 영역(`#rf-dash-area`) · 권한 시작값 복사(`#rf-copy`). 개발은 시작 화면 · 대시보드 블록을 `config/admin.php` landing · `DashboardService::VISIBLE` 코드 상수로 둠. 규칙 기반 명명: `admin_roles.landing_route` · `admin_roles.is_external` (규칙)
- 계정 유형 내부 직원 / 권리자 / 거래처(`STAFF`·`RH`·`VENDOR`) — 개발 역할 코드에 권리자 · 거래처 없음.
- 변경 영향 확인 모달(영향 계정 · 문의 분류) · 권한 변경 이력 표(변경 일시 · 관리자 · 대상 · 전→후).
- 계정 목록 "소속(데이터 범위) · 접속 제한 · 최근 접속" 열.

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- `#af-id` → `login_id`, `#af-name` → `name`, 역할 → `admin_role_id`, 상태 라디오 → `is_locked`(체크 1).
- `#rf-name` · `#rf-id` · `#rf-desc` → `name` · `code` · `description`.
- 권한 체크 → `permissions[{admin_menu_id}][can_view|can_create|can_update|can_delete|can_download]`.
- 메뉴 행 식별: 프로토타입 화면 코드 → 개발 `admin_menus.screen_code` / `route_name`.

## 8. 정책 질문 (white 확인 필요)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 역할 그룹을 운영 중 추가 · 미사용으로 바꾸는 기능(README "운영 중 추가 · 수정 · 미사용하는 변수") — 개발은 6개 코드 고정, 추가 경로 없음. 확인 필요.
- 권리자 · 거래처 외부 계정(파트너 센터) 역할 코드 — 확인 필요.
- 권한 축 3(읽기 · 쓰기 · 엑셀) vs 5(조회 · 등록 · 수정 · 삭제 · 다운로드) — 확인 필요.

## 출처
- routes/admin.php:207-241
- app/Http/Controllers/Admin/AdminUserController.php:20-195 · AdminRoleController.php:22-135 · AdminMenuController.php:19-85
- app/Services/Admin/AdminPermissionService.php:261-306, :358-379
- `_index/requests.md` AdminUserRequest · AdminRoleRequest · AdminMenuRequest
- app/Models/AdminRole.php:15-27
- resources/views/admin/admin-users/index.blade.php:27-140 · form.blade.php · verify-cap.blade.php · admin-roles/index.blade.php:27-106 · form.blade.php:47-152 · admin-menus/*
- `_index/schema.md` users · admin_roles · admin_user_roles · admin_role_menus · admin_menus · admin_allowed_ips
- 프로토타입: prototype_clean/ADMN-CONF-005_baseline.html:129-793 (digest 기준)
