# ADMN-PROD-006 강사 노출 정보 관리(강사 프로필 · 전시) — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-006_baseline.html` (원본 상태: `84c22e2`, 미커밋 변경 없음)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PROD-006 목록 · 006-S2 프로필 상세(프로토에만) · 006-S1 등록 · 수정
- 개발 진행: 구현(목록 · 등록 · 수정 · 삭제 · 권리자 검색 · 엑셀). 006-S2 읽기 전용 상세는 개발 미구현(수정 화면이 겸함). `_index/progress.md` PROD-006 라우트 주석 있음

프로토타입 view ↔ 개발 화면
| 프로토타입 view | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 006 강사 노출 목록(`switchSubview`, L538) | PROD-006 목록 | `resources/views/admin/instructor-profiles/index.blade.php` |
| 006-S2 강사 프로필 상세(L542) | (없음 — 목록 강사명 링크가 바로 수정 화면) | — |
| 006-S1 등록 · 수정(L546) | PROD-006-S1 | `instructor-profiles/create.blade.php` · `edit.blade.php` + `form.blade.php` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 |
|---|---|---|---|
| `admin.instructor-profiles.index` | 강사 프로필 / 전시 관리(추정) | 006 · S1 · S2 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |
| (참고) `admin.instructors.index` | 강사관리(개발 라우트 주석 `routes/admin.php:333`) | 대응 프로토 파일 없음 — 확인 필요 | 같은 방법으로 확인 필요 |

- 버튼 노출: `@adminCan('admin.instructor-profiles.index', can_download|can_create|can_update|can_delete)` (`index.blade.php:110,126,164,206,211`).
- 권리자 검색 API `admin.instructor-profiles.instructors.index`는 접미사 `index` → 이 메뉴 조회 권한(`routes/admin.php:650-651`).
- 정산 요율 표시는 재무 권한자만 서버가 값을 만든다(`InstructorProfileController.php:86-87`, `form.blade.php:95-110`).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{instructorProfile}` = `instructor_profiles.id`.

### PROD-006 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 · 정렬 | GET | `/instructor-profiles` | `admin.instructor-profiles.index` | 조회 | InstructorProfileController@index |
| 엑셀(사유 레이어) | GET | `/instructor-profiles/download` | `admin.instructor-profiles.download` | 다운로드 | InstructorProfileController@download |
| 삭제 | DELETE | `/instructor-profiles/{instructorProfile}` | `admin.instructor-profiles.destroy` | 삭제 | InstructorProfileController@destroy |
| 노출 순서 일괄 저장 | PUT | `/instructor-profiles/sort` (규칙) | `admin.instructor-profiles.sort.update` (규칙) | 수정 | 개발 미구현, 규칙 기반 명명 |

### PROD-006-S2 프로필 상세
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 읽기 전용 상세 | GET | `/instructor-profiles/{instructorProfile}` (규칙) | `admin.instructor-profiles.show` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명 |

### PROD-006-S1 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/instructor-profiles/create` | `admin.instructor-profiles.create` | 등록 | InstructorProfileController@create |
| 권리자 검색(JSON) | GET | `/instructor-profiles/search-instructors?name=&birth_date=&business_number=&exclude_profile_id=` | `admin.instructor-profiles.instructors.index` | 조회 | InstructorProfileController@apiSearch |
| 등록 | POST | `/instructor-profiles` | `admin.instructor-profiles.store` | 등록 | InstructorProfileController@store |
| 수정 폼 | GET | `/instructor-profiles/{instructorProfile}/edit` | `admin.instructor-profiles.edit` | 수정 | InstructorProfileController@edit |
| 수정 | PUT | `/instructor-profiles/{instructorProfile}` | `admin.instructor-profiles.update` | 수정 | InstructorProfileController@update |
| 홍보 영상 미디어키 확인 | → | 강의 관리 조회 사용(확인 필요) | — | — | 개발 미구현(폼에 영상 칸 없음) |

## 3. 폼 필드 · 검증

### 목록 검색 (GET, `InstructorProfileController.php:38`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `keyword` | 강사명 | `#filter-keyword` (프로토: 강사명 / 권리자코드 / 슬로건) |
| `contract_status` | `active`(계약중) · `expired`(종료) · `terminated`(정지). `pending`(계약 예정)은 필터에 없음, 기본 목록은 pending+active(`RightsHolderContract::DEFAULT_LIST_STATUSES`) | `#filter-contract` `정상` · `갱신대기`(만료임박) · `계약종료`(해지) |
| `is_display` | `1` 노출 · `0` 숨김 | `#filter-display` `Y` · `N` |
| `category_id` | categories 1Depth id | `#filter-cat` (고정 3종) |
| `sort` · `direction` | `name` · `contract_status` · `updated_at` / `asc` · `desc` (표 머리 링크) | `#filter-sort` `ORDER`(노출 순서) · `RECENT`(최근 등록) |
| (메인 추천 필터) | 개발 없음 | `#filter-featured` `Y` · `N` |

### S1 권리자 연동 검색 (apiSearch, `InstructorProfileController.php:127-147`)
| 파라미터 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `name` + `birth_date` | 개인: 이름으로 후보 조회, [선택]은 생년월일 일치 시만 | `#f-ins-master` select(권리자 목록 고정) |
| `business_number` | 사업자 · 법인. 대조 컬럼은 `rights_holders.business_number`(`instructors.business_number`는 삭제됨(2026_09_15_000114_move_settlement_columns_from_instructors_to_rights_holders)) | 〃 |
| `exclude_profile_id` | 수정 중인 자기 프로필 제외 | — |
| 결과 | 위탁자 · 자사 권리자 제외, 요율 미포함 | — |

### S1 등록 · 수정 (InstructorProfileRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (프로필 코드) | 없음 — `instructor_profiles.id` | | `#f-prof-code` `PRF-2601`(readonly) |
| `rights_holder_id` | required · integer · 프로필 대상 권리자 · 1권리자 1프로필 | | `#f-ins-master` (`RH-0019` 등) |
| (계약 연동 상태) | 읽기 전용 `#linkedContract` (계약 유효 · 계약 예정 · 계약 종료 · 해지) | `PROFILE_DETAIL_STATUS_LABELS` | `#f-contract-gate-box` · `#f-contract-gate-title` · `#f-contract-gate-desc` |
| `display_name` | required · max 50 | | `#f-inst-name` |
| `title` | nullable · max 100 | | (대응 없음 — 프로토 슬로건과 성격이 가장 가까움, 확인 필요) |
| `intro_text` | nullable · max 120 (목록 카드 요약) | | `#f-inst-slogan` 강사 한줄 슬로건(필수, 100자) — 대응 확인 필요 |
| `categories[]` | required · array · min 1 · 1Depth 카테고리 | categories.id | `#f-inst-cat` 대표 담당 카테고리(단일, 고정 3종) |
| `instructor_type` | required | `main` 정강사 · `sub` 부강사 | 프로토 없음(개발에만) |
| `photo` | nullable · jpg/jpeg/png/webp · 2MB · 480×640 이상 3:4 | | 강사 목록용 프로필 사진(480x600 PNG 권장, '파일 변경' L932) |
| `delete_photo` | boolean | | — |
| (상단 배너 이미지) | 개발 없음 | | 강사 상세 상단 배너(1200x360, L938) |
| (대표 홍보 영상) | 개발 없음(`instructors.intro_lecture_id` 칸은 있음) | | `#f-intro-vod` · '미디어키 확인' |
| `career` | required · 에디터 HTML · 빈 문단 불가 | | 약력 행 빌더 `#career-builder-wrap` · `addCareerLine()` |
| (인사말 · 학습 가이드) | 개발 없음 | | `#f-inst-greeting` |
| `home_link_type` | required | `internal` 내부링크(USER-INST-001) · `external` 아웃링크 | 프로토 없음(개발에만) |
| `home_url` | external이면 required · url · max 500 | | 프로토 없음 |
| `is_display` | nullable · boolean (등록 기본 OFF) | `1` 전시 ON · `0` 전시 OFF | `f-inst-display` `#radio-inst-disp-y`(Y) · `#radio-inst-disp-n`(N) |
| `sort_order` | nullable · integer ≥ 0 (전체 목록 오름차순) | | `#f-inst-order` (1~99, '위') |
| (메인 추천) | 개발 없음 | | `#f-inst-featured` 메인 홈 추천 강사 캐러셀 |
| `auto_preview` | boolean (기본 ON, 현재 건수 표시) | | 프로토 없음(개발에만) |

## 4. 목록 필터 · 정렬 · 표 컬럼

| 개발 컬럼(`index.blade.php:141-150`) | 정렬 키 | 프로토타입 컬럼(L661-672) |
|---|---|---|
| No | | 노출순서 |
| (없음) | | 프로필코드 |
| 강사명(→ edit `.link--view`) | `name`(강사 실명 기준) | 프론트 노출 강사명 |
| 연동 강사 ID(권리자 코드) | | 권리자코드(SSOT) |
| 담당 과정(복수) | | 대표 카테고리 |
| (없음) | | 강사 한줄 슬로건 |
| (없음) | | 연결 강좌 / 교재 |
| 계약 상태 | `contract_status` | 계약상태 (INST-001) |
| (없음) | | 메인추천 |
| 전시 | | 노출여부 |
| 최종 수정 | `updated_at` | 등록일 |
| 관리(수정 · 삭제) | | 관리 |

기본 정렬 `id desc`, 20건 페이지. 툴바 '전체 N명 · 전시중 N명'(`displayCount`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `instructor_profiles.instructor_id` | FK instructors | 강사(권리자 연동은 `instructors.rights_holder_id`) | S1 |
| `instructor_profiles.photo_path` | string(255) | 프로필 사진 3:4 | S1 |
| `instructor_profiles.display_name` | string(50) | 전시 강사명 | 목록 · S1 |
| `instructor_profiles.title` | string(100) | 타이틀(탭 보조 문구) | S1 |
| `instructor_profiles.career` | text | 약력 | S1 |
| `instructor_profiles.intro_text` | string(255) | 소개 텍스트(카드 요약 120자) | S1 |
| `instructor_profiles.home_link_type` · `home_url` | | 강사 홈 내부/아웃링크 | S1 |
| `instructor_profiles.is_display` | boolean | 개별 전시. 계약 종료 · 해지면 강제 숨김 | 목록 · S1 |
| `instructor_profiles.sort_order` | integer | 강사 목록 노출 순서 | S1 |
| `instructor_profiles.auto_preview` | boolean | 맛보기 자동 진열 | S1 |
| `instructors` (`code` INST-%06d, `name`, `birth_date`, `instructor_type`, `rights_holder_id`, `intro_lecture_id`, `slug`) | | 강사 마스터 | S1 연동 정보 |
| `instructor_categories` (`instructor_id`, `category_id`) | | 담당 자격증(1Depth) | 목록 · S1 |
| `rights_holders.code` · `rights_holder_contracts.status` · `sequence_no` | | 권리자 코드 · 최신 계약 상태 · 갱신 회차 | 목록 · S1 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| 검색 form(GET, id 없음) · `.ip-sort` 정렬 링크 | 목록 검색 · 정렬 | `#filter-*` · `renderInstList()` |
| `layerReason` + `data-reason-*` | 엑셀 사유 | (프로토 엑셀 없음) |
| `actionForm` (`_method=DELETE`) · `deleteProfile()` | 삭제 | (없음) |
| `profileForm` | S1 폼 | 폼 영역(form 태그 없음) · `saveInstForm()` |
| `searchName` · `searchBirth` · `searchBizNo` · `searchRightsHolders()` · `searchResult` · `searchRows` | 권리자 검색 | `#f-ins-master` · `onChangeMasterInstructor()` |
| `rightsHolderId` (hidden `rights_holder_id`) | 연동 권리자 | `#f-ins-master` 값 |
| `linkedInfo` · `linkedCode` · `linkedName` · `linkedContract` · `clearInstructor()` | 연동 정보 · 해제 | `#f-contract-gate-box` |
| `photoBox` · `photoCurrent` · `photoSelector` · `delete_photo` · `onPhotoSelect()` | 프로필 사진 | 사진 '파일 변경'(L932) |
| `homeUrl` | 아웃링크 URL | (없음) |
| `verdictTable` · `[data-verdict-current]` · `.vd-row--current` | 노출 판정표 | (없음 — 프로토는 게이트 박스 문구) |
| `layerInstructorBlind` · `blindWarnReason` · `blindWarnConfirm` | 계약 무효 강사 선택 경고 | 게이트 박스 `locked` 상태 |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 권리자 검색: 개인 이름 + 생년월일 일치 시 선택, 사업자는 사업자등록번호. 위탁자 · 자사 권리자 제외 — `InstructorProfileController.php:115-147`
- 1권리자 1프로필 저장 차단 — `InstructorProfileRequest.php:53-59`
- 강사 구분(정강사 · 부강사) `instructor_type` — `InstructorProfileRequest.php:78`
- 강사 홈 링크 내부/아웃링크 · URL — `InstructorProfileRequest.php:90-94`
- 맛보기 자동 진열 `auto_preview` + 현재 건수 — `form.blade.php:310-318`
- 정산 요율(재무 권한자만) 읽기 전용 표시 — `form.blade.php:95-110`
- 노출 판정표(계약 × 전시 4경우) · 계약 무효 강사 선택 경고 레이어 — `form.blade.php:322-425`
- 엑셀 다운로드(사유) · 프로필 삭제 — `routes/admin.php:649,656`

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 006-S2 읽기 전용 프로필 상세(연결 강좌 · 교재 표 L763 포함)
- 프로필 코드 `PRF-YYNN`(L834)
- 메인 홈 추천 강사 캐러셀 `#f-inst-featured` · 메인추천 필터 · 컬럼 — 설계서 3.2.2 4항(`docs/산준모닷컴 구축 통합 상세 설계서.md:256`)에 있는 정본 항목
- 대표 홍보 영상(PROD-002 연동) · 미디어키 확인 — 설계서 `:256`
- 상단 배너 이미지 · 인사말 · 학습 가이드
- 목록 노출 순서 일괄 저장(L652)
- 계약 '만료임박 / 갱신대기' 구분 필터(L604)
- 계약 종료 권리자 선택 시 노출 Y · 메인 추천 입력 잠금(L1276-1283) — 개발은 저장 허용 + 프론트 강제 숨김(결과 노출은 같음)
- 참고(차이 아님): 계약 종료 강사의 강좌 블라인드는 개발도 판정 방식으로 구현 — 강좌 `display_status`는 그대로 두고 목록 · 상세 · 장바구니에서 제외(`app/Services/Order/CartLineResolver.php:394-400`, `app/Services/Front/CatalogService.php:31-32,340`). 관리 화면 안내 문구 "판매 중인 강좌는 자동으로 판매중지되지 않습니다"(`form.blade.php:416`)는 상태값 얘기. 맛보기(무료 강의) 블라인드 적용 여부는 확인 필요(정본 `설계서:277`)

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#f-ins-master` (`RH-xxxx` select) | `rights_holder_id` (검색 후 hidden) |
| `#f-inst-name` 프론트 노출 강사명 | `display_name` 전시 강사명 |
| `#f-inst-cat` 대표 카테고리(단일) | `categories[]` 자격증 분류(복수, 1Depth) |
| `#f-inst-slogan` 한줄 슬로건 | `intro_text`(소개 텍스트 120자) 또는 `title` — 확인 필요 |
| 약력 행 빌더(배열) | `career` 에디터 HTML 1칸 |
| `f-inst-display` Y · N | `is_display` 1 · 0 (전시 ON · OFF) |
| `#f-inst-order` 노출 순서(1~99) | `sort_order` (0 이상) |
| 계약상태 정상 · 갱신대기 · 계약종료 | `contract_status` `active` 계약중 · `expired` 종료 · `terminated` 정지 (+ `pending` 계약 예정) |
| 권리자코드(SSOT) | 연동 강사 ID = `rights_holders.code` |
| 사진 480x600 PNG 권장 | 480×640 이상 3:4 · 2MB |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)

| # | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-PROD006-1 | 노출 순서 단위: 정본은 '카테고리 내 노출 순서'. 개발 `sort_order`는 카테고리와 무관한 전체 1개 값(강사가 여러 자격증 탭에 같은 순서로 나옴) | 설계서 3.2.2 4항 `:256`, 프로토 `#f-inst-order` L901 | `app/Http/Requests/Admin/InstructorProfileRequest.php:97`, `form.blade.php:300-306`, `_index/schema.md` instructor_profiles.sort_order **→ 정본대로(POLICY_D_PROD A, 통합설계서 L257)**: 카테고리 내 노출 순서 — 개발팀 전달(강사 × 카테고리 연결 행에 순서 칸) |
| Q-PROD006-2 | 담당 카테고리 개수: 프로토는 '대표 담당 카테고리' 1개(필수). 개발은 자격증 분류 복수 선택(그 탭마다 노출). 강사가 여러 자격증 탭에 나오는 것을 허용하는지 | 프로토 L869-874 · 목록 '대표 카테고리' L665 | `InstructorProfileRequest.php:62-74` **→ 정책 아님(POLICY_D_PROD B)**: 화면 · 이름 문제로 처리 — 개발(복수)을 따르고 프로토는 대표 카테고리 1개 + 노출 카테고리 복수 2칸 |
