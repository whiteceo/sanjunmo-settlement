# ADMN-PROD-002 강의(영상) 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-002_baseline.html` (원본 상태: 18d66c1 v6.92. 본문 줄 번호 :NNN 은 v6.92 이전 기준이 남아 있을 수 있다 — id 이름으로 찾는다)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PROD-002 강의 목록 · 002-S1 강의 등록/수정(프로토는 한 파일 안 view 2개 `#viewList` · `#viewForm`, 개발은 페이지 2개)
- 개발 진행: 구현(002 · 002-S1 라우트 · 화면 있음, `_index/progress.md` 라우트 주석 있음)

프로토타입 view ↔ 개발 화면
| 프로토타입 view(id) | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| `#viewList` | PROD-002 강의 목록 | `resources/views/admin/lectures/index.blade.php` |
| `#viewForm` | PROD-002-S1 강의 등록 · 수정 | `resources/views/admin/lectures/form.blade.php` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.lectures.index` | 강의 관리(추정) | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 권한 축 5개. 화면 판정: [+ 강의 등록] 등록, 행 [수정] 수정, [삭제] 삭제, [저장] 신규 등록 · 기존 수정, [엑셀 다운로드] · [선택 다운로드] 다운로드(`@adminCan('admin.lectures.index','can_download')`, `index.blade.php:130`).
- 수정 권한이 없으면 목록 VOD Key 뒤 4자리를 `****`로 가린다(`index.blade.php:204-210`, 정본 화면설계서 05 PROD-002 "조회 전용 롤 마스킹").
- 교안 첨부 다운로드(`admin.attachments.download`)는 메뉴 권한 밖 라우트지만 AttachmentController가 `lecture` → `admin.lectures.index` 메뉴로 다시 묻는다(`AttachmentController.php:34`).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{lecture}` = `lectures.id`. 근거 `routes/admin.php:347-366`.

### PROD-002 강의 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색(`reset=1` 초기화) | GET | `/lectures` | `admin.lectures.index` | 조회 | LectureController@index |
| 엑셀 다운로드(사유 레이어 `layerReason`) | GET | `/lectures/download` | `admin.lectures.download` | 다운로드 | LectureController@download |
| 선택 다운로드(`ids[]`) | POST | `/lectures/download-selected` | `admin.lectures.selected.download` | 다운로드 | LectureController@downloadSelected |
| 강의 복사 | POST | `/lectures/{lecture}/copy` | `admin.lectures.copy.store` | 등록 | LectureController@copy — 화면 버튼 없음 |
| 선택 레이어용 목록(강좌 폼 · 패키지) | GET | `/api/lectures` | `admin.api.lectures` | 로그인 + 상품 메뉴 4종 중 조회 1개(`AdminPermissionService::SELECT_API_MENUS`) | LectureController@apiList |

### PROD-002-S1 강의 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/lectures/create` | `admin.lectures.create` | 등록 | LectureController@create |
| 수정 폼 | GET | `/lectures/{lecture}/edit` | `admin.lectures.edit` | 수정 | LectureController@edit |
| 저장(신규) | POST | `/lectures` | `admin.lectures.store` | 등록 | LectureController@store |
| 저장(수정) | PUT | `/lectures/{lecture}` | `admin.lectures.update` | 수정 | LectureController@update |
| 삭제(소프트) | DELETE | `/lectures/{lecture}` | `admin.lectures.destroy` | 삭제 | LectureController@destroy |
| [유효성 검사] · [DRM 메타에서 가져오기] (OVP 조회, JSON) — `verifyDrmId()` · `fetchFromVodMeta()` | GET | `/lectures/vod-info?drm_content_id=` | `admin.lectures.vod-info.index` | 조회 | LectureController@vodInfo |
| 재생시간 변경 영향(저장 전, JSON) | GET | `/lectures/duration-impact?lecture_id=&duration_sec=` | `admin.lectures.duration-impact.index` | 조회 | LectureController@durationImpact |
| 권리자 지분 매핑 이동 | → | SETT-001 | `admin.settlement…`(SETT-001 명세 참조) | | 개발 폼에 링크 없음 |
| 연결 강좌 · 패키지 목록 | GET | `/lectures/{lecture}/products` (규칙) | `admin.lectures.products.index` (규칙) | 조회 | 개발 미구현, 규칙 기반 명명(개발은 편성 강좌 수 `courseCount`만) |

## 3. 폼 필드 · 검증

### 002 목록 검색 (GET, `LectureController.php:37-39`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `root_category_id` | 1Depth `categories.id` (`#searchRoot`) | `#fCat1` |
| `category_id` | 2Depth `categories.id` (`#searchChild`, root로 좁힘) | `#fCat2` |
| `instructor_id` | 강사 id | `#fInst` |
| `is_preview` | `''` · `1` · `0` | `#fSample` ALL · Y · N |
| `keyword` | 제목 또는 `cdn_key` 부분 일치(`LectureRepository.php:102-108`) | `#fKeyword` "제목 · CDN 경로 · DRM ID 검색"(v6.92 — DRM ID 검색은 개발에 없음) |
| `year` · `type` | 연도 · 강의 구분(`Lecture::TYPE_LABELS`) | 프로토 없음(개발에만) |
| `page` | 페이지 | `.pagination` |
| (최근 작업 카테고리) | 질의 없이 들어오면 세션 `admin.lectures.recent_category` 값으로 채움 | 없음 |

### 002-S1 저장 (LectureRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (1Depth 셀렉트, 전송 안 함) | `#formRoot` | | `#s1Cat1` |
| `category_id` | required · 살아 있는 카테고리 · 2Depth만 | | `#s1Cat2` |
| `instructor_id` | required · 강사 존재. 후보 = 프로필 등록 + 계약 유효(수정 중 강사는 유지) | | `#s1Inst` |
| `title` | required · max 255 (화면 maxlength 80) | | `#s1Title` (maxlength 80) |
| `cdn_key` | nullable · 5~255 · CDN 경로 정규식 `CDN_KEY_PATTERN`(`..` 금지) · 삭제분 포함 전체 유일("이미 [강의명] 에 등록된 Key 입니다.") | 예 `2026/LEC_00001.mp4` | `#s1CdnPath`(v6.92, 프로토 예 `lecture/2026/safety-pe/0341.mp4` · 도메인 · `?` 서명 URL 거부, `cdnPathError()`) |
| `drm_content_id` | nullable · max 100 · 전체 유일. 값이 있으면 `duration_sec`을 버리고 OVP 값으로 채움. D-PROD-01: 유료(맛보기 N) 강의는 required — 개발 반영 필요 | OVP DRM 콘텐츠 ID | `#s1DrmId` · `#s1DrmReq` · `#s1DrmVerifiedBadge`(v6.92) |
| `duration_sec` | `drm_content_id` 없을 때 required · integer · min 1 | 초 | `#s1Duration` (+ `#s1DurationFormatted`) |
| `is_preview` | required · boolean | `1` Y 전체 공개 · `0` N 수강권 보유자만 | `setSampleYn('Y'/'N')` `#chkSampleY` · `#chkSampleN` |
| `is_active` | required · boolean | `1` 사용 · `0` 미사용 | `setUseYn(true/false)` `#chkUseY` · `#chkUseN` |
| `attachments[]` | nullable · array · max 1 · pdf · **max 20480KB(20MB)** · 내용 검사 RealFileType | | `attachSamplePdf()` · `#s1PdfBox` (프로토 50MB) |
| `delete_attachments[]` | 기존 첨부 id | | `removePdf()` |
| `year` | nullable · 2020~2040 | | 프로토 없음 |
| `type` | required | `normal` 일반 강의 · `ot` OT · `sample` 샘플 강의 · `product_intro` 상품 소개 영상 · `instructor_intro` 강사 소개 영상 · `free` 무료 공개 (`Lecture::TYPE_LABELS`) | 프로토 없음 |
| `source_type` | required | `cdn` · `youtube`(맛보기 Y 강의만) | `#s1Source` CDN · YOUTUBE · `onSourceChange()`(v6.92) |
| `source_url` | nullable · max 500 · http/https만 | youtube일 때 | `#s1YtUrl`(v6.92, youtube.com · youtu.be만) |
| `list[*]` | 목록 복귀 질의(화이트리스트) | | `backToList()` |
| (강의 코드) | 서버 채번 `LEC_00001` | | 프로토 없음 |

### vod-info 응답 · duration-impact 응답
| 요청 | 응답 | 프로토타입 대응 |
|---|---|---|
| `drm_content_id` | `ok` · `message` · 재생 가능 여부 · 러닝타임(초) | `verifyDrmId()` · `fetchFromVodMeta()` · `#s1DrmVerifiedBadge` |
| `lecture_id` · `duration_sec` | 영향 수강생 수 · 인정 진도율(사이트 기본 `refund_claim_min_progress`) 미달 전환 예상 | 프로토 없음(경고 문구만) |

## 4. 목록 필터 · 정렬 · 표 컬럼 (002)
| 개발 컬럼 | 프로토타입 컬럼 |
|---|---|
| 선택 체크(`#checkAll` · `ids[]`) | 없음 |
| 번호(전체 기준 역순) | 번호 |
| 분류(`category.name`) | 분류 |
| 강의 제목 | 강의 제목 |
| 강사 | 강사 |
| VOD Key(`cdn_key`, 비면 `미등록` 배지, 조회 전용은 뒤 4자리 마스킹) | VOD Key |
| 재생시간(`2,940초 (49:00)`, 0이면 `미입력` 배지) | 재생시간 |
| 교안 O/X | 교안 |
| 맛보기 Y/N | 맛보기 |
| (없음) | 정산 매핑 (SETT-001) — 프로토에만 |
| 관리 [수정] (행 클릭도 수정 폼) | 관리 |

툴바: 전체 N건 · 맛보기 N건(`previewCount`). 정렬은 `id desc` 고정.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `lectures.id` · `code` | id · string(50) unique | PK · `LEC_00001` | 폼 '코드' |
| `lectures.title` | string(255) | 강의 제목 | 목록 · 폼 |
| `lectures.instructor_id` | FK instructors | 전시용 강사(정산 귀속 아님) | 강사 |
| `lectures.category_id` | FK categories(2Depth) | 노출 분류 | 분류 |
| `lectures.cdn_key` | string(255) | CDN 경로(VOD Key 칸) | VOD Key |
| `lectures.drm_content_id` | string(100) | OVP DRM 콘텐츠 ID | 폼 |
| `lectures.vod_verified_at` | timestamp | 유효성 검사 시각 | `#vodVerifyResult` "검증 완료 MM.DD HH:mm" |
| `lectures.duration_sec` | uint | 재생시간(진도율 분모) | 재생시간 |
| `lectures.is_preview` | boolean | 맛보기 | 맛보기 |
| `lectures.is_active` | tinyint | 사용 여부(미사용 = 신규 편성 후보 제외) | 사용 여부 |
| `lectures.type` · `source_type` · `source_url` · `year` | | 구분 · 소스 · YouTube URL · 연도 | 폼 '기타' |
| `lectures.view_count` | uint | 무료강의 조회수 | (화면 없음) |
| `lectures.deleted_at` | timestamp nullable | 소프트 삭제 | — |
| `attachments` (lecture 첨부, private 디스크) | | 교안 PDF | 교안 |
| `course_lectures` (`course_id`, `lecture_id`, `sort_order`) | | 편성 | 사용 여부 옆 "현재 N개 강좌의 커리큘럼에 편성됨" · 삭제 판정 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `searchRoot` · `searchChild` | 검색 1Depth → 2Depth | `#fCat1` · `#fCat2` |
| `listForm` · `checkAll` · `.check-item` | 목록 선택 | 없음 |
| `layerReason`(공통) · `data-reason-*` | 엑셀 사유 레이어 | 없음(`showToast`) |
| `.lec-row--link` `data-href` | 행 클릭 → 수정 폼 | `openFormView(id)` |
| `.lec-badge--err` · `--on` · `--off` | 미등록/미입력 · Y · N | `.mono-pill` · badge |
| `lectureForm` | S1 폼 | `#viewForm` `.s1-card` |
| `formRoot` · `formChild` · `instructorSelect` | 분류 · 강사 | `#s1Cat1` · `#s1Cat2` · `#s1Inst` |
| `drmContentId` · `vodVerify` · `vodVerifyResult` | DRM ID · 유효성 검사 · 결과 | `#s1VodKey` · `verifyVodKey()` · `#s1VodVerifiedBadge` |
| `durationSec` · `durationClock` · `vodMeta` · `durationAutoHelp` | 재생시간 · 환산 · 메타 가져오기 · DRM 자동 안내 | `#s1Duration` · `#s1DurationFormatted` · `fetchFromVodMeta()` |
| `existingAttachments` · `newFileList` · `fileSelector` · `fileCountText` | 교안 | `#s1PdfBox` · `attachSamplePdf()` · `removePdf()` |
| `sourceType` · `youtubeUrlField` | 소스 구분 | 없음 |
| `lectureDelete` · `lectureDeleteForm` | 삭제 | `#btnDeleteLesson` `deleteLesson()` |
| (저장 submit) | 저장 | `saveLesson()` |
| (없음) | 정산 매핑 배지 · 연결 상품 표 | `#s1MappingBadge` · `#s1LinkTable` `#s1LinkBody` · `#s1RefCourseCount` |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- DRM 콘텐츠 ID 칸(`drm_content_id`)과 OVP 재생시간 자동 반영(입력 잠금) — `LectureRequest.php:41-46, 101-116` **→ 결정(v6.92 white, D-PROD-01)**: 개발안(CDN 경로 + DRM 콘텐츠 ID)으로 정본을 고침, 유료(맛보기 N) 강의는 DRM ID 필수 — 프로토에 칸 추가됨
- 재생시간 변경 영향 조회(`duration-impact`) — 정본(화면설계서 05 PROD-002-S1 "회원 214명 진도율 재계산 경고", 확정)과 일치 **→ 결정(v6.92 white, S-14)**: 판매 후 재생시간을 바꿔도 기존 수강생 환급 판정에는 소급하지 않음(결제 시점 조건을 주문 라인에 박제) — 프로토 `#s1RetroNote` · 편성 강의 저장 확인 창. 개발 영향 조회의 '미달 전환 예상'은 신규 결제분 기준으로 바꿀지 확인 필요
- 강의 구분 `type` 6종 · 소스 `cdn`/`youtube` + YouTube URL · 연도 (v6.92: 소스 · YouTube URL은 프로토에도 생김 — D-PROD-01, 맛보기 Y만 YouTube)
- 엑셀 다운로드 · 선택 다운로드(사유 입력), 강의 복사 라우트
- 최근 작업 카테고리 기억(`applyRememberedCategory`, `LectureController.php:71-94`)
- 조회 전용 역할 VOD Key 마스킹, 미사용 강의 신규 편성 차단(CourseRequest)

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 목록 '정산 매핑 (SETT-001)' 컬럼 · S1 정산 매핑 배지(`#s1MappingBadge`, 프로토 :435 · :462) · SETT-001 이동 버튼(:573)
- S1 연결 강좌 · 패키지 표(`#s1LinkTable`, :559) — 개발은 편성 강좌 수만. 패키지 편성 여부 없음
- 삭제 차단 문구에 패키지 수 포함(`deleteLesson()`) — 개발은 강좌 편성 수만(`LectureService.php:365-368`)

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#fCat1` · `#fCat2` · `#fInst` · `#fSample` · `#fKeyword` | `root_category_id` · `category_id` · `instructor_id` · `is_preview` · `keyword` |
| 맛보기 Y · N | `is_preview` `1` · `0` |
| 사용 true · false | `is_active` `1` · `0` |
| `#s1Title` · `#s1Source` · `#s1CdnPath` · `#s1DrmId` · `#s1YtUrl` · `#s1Duration` | `title` · `source_type` · `cdn_key` · `drm_content_id` · `source_url` · `duration_sec` |
| CDN 경로 예 `lecture/2026/safety-pe/0341.mp4` | CDN 경로 예 `2026/LEC_00001.mp4`(형식만 다름) |
| 교안 50MB 이하 1개 | 20MB 이하 1개 (8절 Q-PROD002-1) |
| 강의 id(샘플) | `lectures.id`, 코드 `LEC_00001` |

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
- **Q-PROD002-1 교안 PDF 용량 상한** — 정본 프로토타입은 50MB(`prototype_clean/ADMN-PROD-002_baseline.html:536, 842`), 개발은 20MB(`app/Http/Requests/Admin/LectureRequest.php:137` `max:20480`, 근거로 화면설계서 05 PROD-002-S1 "PDF 1개(20MB 이하)"를 듦). 화면설계서와 프로토타입이 서로 다르다. 어느 값으로 맞출지. **→ 정본대로(POLICY_D_PROD A, 통합설계서 L234 '최대 50MB')**: 50MB — 개발 `max:20480` → 51200 전달(20MB는 화면설계서 제안값)
- **Q-PROD002-2 VOD 식별자로 무엇을 저장하나** — 정본: "StarPlayer+ 발급 VOD Key만 보관, 영상 원본 URL · 파일 경로는 DB에 저장하지 않는다"(프로토 :500, 화면설계서 05 PROD-002-S1 ③). 개발: 발급 Key가 없다는 벤더 회신(2026-09-14)을 근거로 `cdn_key`에 CDN 파일 경로(도메인 제외)를 저장하고 DRM 콘텐츠 ID를 별도 칸으로 둔다. YouTube URL(`source_url`)도 저장한다(`LectureRequest.php:12-26, 99-120`). 정본을 "CDN 경로 + DRM 콘텐츠 ID 2칸"으로 고칠지. **→ 결정(v6.92 white, D-PROD-01)**: 개발안으로 정본을 고침(CDN 경로 + DRM 콘텐츠 ID, 도메인 · 서명 URL 저장 안 함, YouTube는 맛보기 Y만) + 유료 강의는 DRM 콘텐츠 ID 필수(개발 `LectureRequest` nullable → 조건부 required)
- **Q-PROD002-3 강의 단위 정산 매핑 미완 시 판매 차단** — 정본: "미매핑 시 편성된 강좌의 판매가 차단됩니다"(프로토 :571). 개발: 강의 · 강좌 저장과 전시 상태에 권리자 매핑 검사 없음(`CourseRequest.php` 전체, `CourseService.php:239-262`). PROD-003 Q-PROD003-3과 같은 질문이라 한 번에 답하면 된다. **→ 정본대로(POLICY_D_PROD A, 통합설계서 S2-02 · 01권 4.2)**: 1계층 지분 100.00% 전까지 판매중 불가 — 저장 시점 잠금 + 결제 시점 재확인, 개발팀 전달
