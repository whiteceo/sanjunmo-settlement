# ADMN-PROD-003 단과 강좌 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-003_baseline.html` (원본 상태: `84c22e2` + 미커밋 작업 트리 — 2026-10-27 다른 세션 수정 중. 통합 커밋 후 줄 번호를 다시 맞춘다)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PROD-003 강좌 목록 · 강좌 상세 · 강좌 등록/수정(커리큘럼 섹션 · 교재 매핑 포함) + 모달 2개(`modal-lecture-picker` · `modal-textbook-picker`)
- 개발 진행: 구현(목록 · 등록/수정 · 커리큘럼 구성 라우트 · 화면 있음). 강좌 상세(읽기 전용 화면)는 개발 미구현

하위 화면 코드가 프로토타입과 개발에서 다르다(개발 = 화면설계서 v12 기준).
| 프로토타입 view(digest) | 프로토 코드 | 개발 코드 · 화면 | 개발 뷰 파일 |
|---|---|---|---|
| 강좌 목록 | 003 | PROD-003 목록 | `resources/views/admin/courses/index.blade.php` |
| 강좌 상세(조회 전용 카드 + 교재 · 판매상태 변경 이력) | 003-S2 | 없음 — 개발 미구현 | — |
| 단과 강좌 등록/수정 | 003-S1 | PROD-003-S2 등록 · 수정 | `courses/form.blade.php` |
| 등록/수정 안의 커리큘럼 섹션 + `modal-lecture-picker` | 003-S1 일부 | PROD-003-S1 커리큘럼 구성(별도 페이지) | `courses/curriculum.blade.php` |
| `modal-textbook-picker` | 003-S1 일부 | S2 폼 안 교재 선택(`admin.api.books`) | `courses/form.blade.php:975` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.courses.index` | 단과 강좌 관리(추정) | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 권한 축 5개. 화면 판정: [+ 강좌 등록] 등록, 행 [수정] 수정, [엑셀 다운로드] 다운로드, [판매중지] 수정(`stop.update`), [삭제] 삭제, 커리큘럼 페이지 열람 조회 · 저장 수정.
- 강좌 폼의 강의 · 교재 · 강사 선택 API(`admin.api.lectures` · `api.books` · `api.instructors`)는 메뉴 권한 밖이지만 상품 메뉴 4종(`books` · `courses` · `instructor-profiles` · `packages`) 중 하나라도 조회 권한이 있어야 쓴다(`AdminPermissionService.php:315-321`).

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{course}` = `courses.id`. 근거 `routes/admin.php:390-412`.

### PROD-003 강좌 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 · 정렬 | GET | `/courses` | `admin.courses.index` | 조회 | CourseController@index |
| 엑셀 다운로드(사유 레이어) | GET | `/courses/download` | `admin.courses.download` | 다운로드 | CourseController@download |
| 강좌 복사 | POST | `/courses/{course}/copy` | `admin.courses.copy.store` | 등록 | CourseController@copy — 화면 버튼 없음 |
| 선택 레이어용 목록(패키지 등) | GET | `/api/courses` | `admin.api.courses` | 로그인 + 상품 메뉴 조회 | CourseController@apiList |

### 프로토 003-S2 강좌 상세 (개발 미구현, 규칙 기반 명명)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세 조회 | GET | `/courses/{course}` (규칙) | `admin.courses.show` (규칙) | 조회 | 개발 미구현 — 개발은 목록 행 클릭이 바로 수정 폼 |
| 판매 상태 변경 이력(주교재 연동) | GET | `/courses/{course}/status-logs` (규칙) | `admin.courses.status-logs.index` (규칙) | 조회 | 개발 미구현(변경은 `admin_logs` subAction `stop_selling`에만 남음) |

### 개발 PROD-003-S2 (프로토 003-S1) 강좌 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/courses/create` | `admin.courses.create` | 등록 | CourseController@create |
| 수정 폼 | GET | `/courses/{course}/edit` | `admin.courses.edit` | 수정 | CourseController@edit |
| 저장(신규) | POST | `/courses` | `admin.courses.store` | 등록 | CourseController@store |
| 저장(수정) | PUT | `/courses/{course}` | `admin.courses.update` | 수정 | CourseController@update |
| 판매중지 | POST | `/courses/{course}/stop-selling` | `admin.courses.stop.update` | 수정 | CourseController@stopSelling |
| 삭제(소프트) | DELETE | `/courses/{course}` | `admin.courses.destroy` | 삭제 | CourseController@destroy |
| 프론트 미리보기 | → | 프론트 강좌 상세 | `front.course.show` | | `form.blade.php:595` |
| 강의 선택 · 교재 선택 · 강사 선택 | GET | `/api/lectures` · `/api/books` · `/api/instructors` | `admin.api.lectures` · `.books` · `.instructors` | 로그인 + 상품 메뉴 조회 | `modal-lecture-picker` · `modal-textbook-picker` 대응 |

### 개발 PROD-003-S1 커리큘럼 구성 (프로토는 등록/수정 안 섹션)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 구성 화면(후보 필터 `category_id` · `instructor_id` · `keyword`, `all=1` 필터 해제) | GET | `/courses/{course}/curriculum` | `admin.courses.curriculum.index` | 조회 | CourseController@curriculum |
| 저장 | PUT | `/courses/{course}/curriculum` | `admin.courses.curriculum.update` | 수정 | CourseController@curriculumUpdate |

## 3. 폼 필드 · 검증

### 003 목록 검색 (GET, `CourseController.php:37-40`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `root_category_id` · `category_id` | 1Depth · 2Depth `categories.id` (`#searchRoot` · `#searchChild`) | `#filter-cat1` · `#filter-cat2` |
| `display_status` | `selling` 전시 · 판매중 · `hidden` 비전시 · `stopped` 판매중지 | `#filter-sale-status`(판매중 · 판매대기 · 판매중지 · 판매종료) + `#filter-display`(Y · N) |
| `keyword` | 강좌명 또는 강좌 코드 | `#filter-keyword`(강좌명 / 강좌코드 / 담당 강사명) |
| `instructor_id` | 대표 강사 | `#filter-instructor` |
| `book_mapped` | `''` · `1` 매핑됨 · `0` 미매핑 | 프로토 없음 |
| `sort` · `direction` | `title` · `duration_days` · `sale_price` · `created_at` / asc · desc | 프로토 없음 |
| (등록일 기간) | 개발 없음 | `#filter-date-from` · `#filter-date-to` |

### 개발 003-S2 강좌 저장 (CourseRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (1Depth 셀렉트, 전송 안 함) | `#formRoot` | | `#f-cat1` |
| `category_id` | required · 2Depth만(`CategoryService::isSelectableCategory`) · `category_products` 대표 1건으로 저장 | | `#f-cat2` |
| `title` | required · max 255 | | `#f-title` |
| (한줄 요약 · 검색 태그) | 개발 없음 | | `#f-summary` · `#f-tags` |
| `instructors[0][instructor_id]` · `instructors[0][role]=m` | 대표 강사 1명 필수 · 계약 유효(기존 값은 통과) · distinct | `m` 대표 | `#f-instructor` |
| `instructors[n][instructor_id]` · `[role]` | n≥1 참여 강사 | `s` 부강사 · `a` 참여 (`ProductInstructor::ROLE_*`) | 프로토 없음 |
| `display_status` | required · `Course::displayStatusValues()` | `selling` 전시 · 판매중 · `hidden` 비전시 · `stopped` 판매중지 (`HasDisplayStatus::DISPLAY_STATUS_LABELS`) | `f-sale-status` 판매중 · 판매대기 · 판매중지 · 판매종료 + `f-display-yn` Y · N (8절 Q-PROD003-1) |
| `duration_days` | required · integer · min 1 | | `#f-period-days` (`f-period-type=DAYS`) |
| `start_type` | nullable · `immediate` 결제 승인 즉시 · `scheduled` 지정일 시작(사전판매) | | 프로토 없음. 프로토 `f-period-type=FIXED_DATE` + `#f-period-enddate`(만료일 고정)은 개발 없음 (Q-PROD003-2) |
| `start_date` | scheduled일 때 required · date | | 없음 |
| `original_price` | required · integer ≥ 0(콤마 제거) | | `#f-list-price` |
| `sale_price` | required · integer ≥ 0 · ≤ 정가 | 화면은 할인율 표시 `#discountRateDisplay` | `#f-sale-price-display`(자동 계산). 프로토 `#f-discount-type` NONE · RATE · AMOUNT + `#f-discount-val`은 개발 없음(판매가 직접 입력) |
| `cost_price` | nullable · integer ≥ 0 | 원가 | 프로토 없음 |
| (과세 구분) | 받지 않음 — 서버가 `tax_type=exempt` 고정(`CourseService.php:46`) | | 면세 배지 표시만 |
| `allow_coupon` · `allow_point` | nullable · boolean (기본 1) | | 프로토 없음 |
| `lectures[]` | required · min 1 · 존재 · 편성 가능(VOD Key + 재생시간) 1강 이상 · 미사용 강의 신규 편성 불가 | 순서 = 배열 순서 | 커리큘럼 섹션 `curriculumSections[].lectures` (섹션 구분은 개발 없음) |
| `books[n][book_id]` · `books[n][book_type]` | 존재 · `main` 주교재 · `sub` 부교재 (`CourseBook::TYPE_*`) | | `modal-textbook-picker` '교재구분 지정' 주교재 · 부교재 |
| `thumbnail` | 신규 · 삭제 후 required · jpg/png/webp · 5MB · 720×405(16:9) 이상 | | `#f-thumb` |
| `delete_thumbnail` | boolean | | |
| `description` · `target_audience` · `content` | nullable · string(에디터) | 강좌 소개 · 수강대상 · 내용 및 특징 | `#f-desc`(1칸) |
| `intro_lecture_id` · `sample_lecture_id` | nullable · 살아 있는 강의 | 소개 영상 · 샘플 강의 | 프로토 없음 |
| `badge_slot_1_code` · `badge_slot_2_code` | nullable · max 50 | 강조 배지 | 프로토 없음 |
| (강좌 코드) | 서버 채번 `CRS_00001` | | `#f-code`(예 `CRS-2601`, 신규 `AUTO`) |
| (등록일) | `created_at` | | `#f-created-at` |
| (일시정지 허용 정책) | 개발 없음 | | `#f-pause-allow` · `#f-pause-count`(3) · `#f-pause-days`(30) (Q-PROD003-4) |
| (정산 1계층 매핑 검증) | 개발 없음 | | `#f-settlement-sim` · `applySettlementHardLock()` (Q-PROD003-3) |
| `list[*]` | 목록 복귀 질의 | | `switchSubview('list')` |

### 개발 003-S1 커리큘럼 저장 (CourseCurriculumRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `lectures[]` | required · min 1 · distinct · 편성 가능 강의만. 판매 이력이 있으면 기존 강의 제외 불가(추가만, `CourseService.php:714-724`) | `confirmAddLecturesToSection()` · `removeLectureFromSection()` · `moveLecture()` |
| 후보 검색 `category_id` · `instructor_id` · `keyword` · `all` | GET | `#modal-lec-keyword` · `renderLectureModalRows()` |

## 4. 목록 필터 · 정렬 · 표 컬럼 (003)
| 개발 컬럼(정렬 키) | 프로토타입 컬럼 |
|---|---|
| No(역순) | No |
| (없음) | 강좌코드 |
| 카테고리(1Depth / 2Depth) | 카테고리 (1차 > 2차) |
| 단과 강좌명(`title`) | 강좌명 |
| 대표 강사 + "강사 계약 종료" 배지 | 담당 강사 |
| 수강 기간(`duration_days`) N일 | 수강기간 |
| (없음) | 정가 |
| 판매가(`sale_price`) | 판매가 (할인율) |
| (없음) | 총 강의수 |
| 교재 매핑 매핑/미매핑 | (없음) |
| (없음) | 정산 매핑 (1계층) |
| 전시(`display_status` 라벨 배지) | 판매상태 · 노출여부(2컬럼) |
| 등록일(`created_at`) | 등록일 |
| 관리 [수정] (행 클릭도 수정 폼) | 관리 |

툴바: 전체 N건 · 전시중 N건(`sellingCount`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `courses.id` · `code` | id · string(50) | PK · `CRS_00001` | 코드 |
| `courses.title` | string(255) | 강좌명(결제 · 세금계산서 법적 표기) | 강좌명 |
| `courses.instructor_id` | FK | 대표 강사(정산 집계 키) | 대표 강사 |
| `product_instructors` (`role` m/s/a) | | 강사 매핑 | 참여 강사 |
| `category_products` (`product_type=course`, `is_primary`) | | 노출 카테고리 | 카테고리 |
| `courses.duration_days` | int | 수강 일수(결제 시 `user_courses`로 복사 고정) | 수강 기간 |
| `courses.start_type` · `start_date` | string · date | `immediate` · `scheduled` + 지정일 | 수강 시작 기준 |
| `courses.original_price` · `sale_price` · `cost_price` | int | 정가 · 판매가 · 원가 | 가격 |
| `courses.tax_type` | string(10) | `exempt` 고정 | 과세 구분 |
| `courses.allow_coupon` · `allow_point` | boolean | 쿠폰 · 포인트 허용 | 프로모션 |
| `courses.display_status` | string(20), 기본 `hidden` | `selling` · `hidden` · `stopped` (mig 2026_09_08_000092) | 전시 |
| `courses.is_public` · `is_featured` | tinyint | 구 공개 플래그(display_status로 이관) | — |
| `courses.thumbnail_path` · `description` · `target_audience` · `content` | | 상세 콘텐츠 | 대표 이미지 · 소개 |
| `courses.intro_lecture_id` · `sample_lecture_id` | FK lectures | 소개 · 샘플 영상 | 기타 |
| `courses.exam_target_id` | | 과정 매핑(구) | — |
| `courses.deleted_at` | | 소프트 삭제 | — |
| `course_lectures` (`course_id`, `lecture_id`, `sort_order`) | | 커리큘럼(섹션 없음) | 커리큘럼 |
| `course_books` (`book_id`, `book_type` main/sub, `sort_order`) | | 연관 교재 | 교재 매핑 |
| `product_badges` (`badge_slot`, `badge_type`) | | 강조 배지 | 기타 |
| `admin_logs` (target `App\Models\Course`, subAction `stop_selling` · `curriculum`) | | 변경 이력 | (프로토 상세 '판매 상태 변경 이력') |

삭제 거부 참조(`CourseRepository.php:180-202`): `user_courses` · `order_item_allocations` · `instructor_settlement_items` · `lecture_progresses` · `order_items` · `package_items` · `cart_items` → "… 삭제할 수 없습니다. 비전시 또는 판매중지 전환을 이용하세요."

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `searchRoot` · `searchChild` | 검색 1Depth → 2Depth | `#filter-cat1` · `#filter-cat2` (`syncCat2Filter()`) |
| `.crs-row--link` `data-href` | 행 클릭 → 수정 폼 | `openCourseDetail()` (프로토는 상세로) |
| `layerReason`(공통) | 엑셀 사유 | `exportCourseCsv()` |
| `courseForm` | 등록 · 수정 폼 | 003-S1 view `saveCourseForm()` |
| `formRoot` · `formChild` · `mainInstructor` | 카테고리 · 대표 강사 | `#f-cat1` · `#f-cat2` · `#f-instructor` |
| `durationDays` · `durationRange` · `startImmediate` · `startScheduled` · `startDateField` · `startDate` | 수강 기간 · 시작 기준 | `#f-period-days` · `period-days-wrap` · `period-date-wrap` · `#f-period-enddate` (`togglePeriodInput()`) |
| `originalPrice` · `salePrice` · `discountRateDisplay` | 가격 | `#f-list-price` · `#f-sale-price-display` · `#f-discount-*` (`recalcCoursePrice()`) |
| `clTable` · `clBody` · `clCount` · `clSeconds` · `clLabel` · `clEmptyRow` | 폼 안 커리큘럼 요약(드래그 순서 · 제외) | `form-sections-wrapper` (`renderFormSections()`) |
| `crsImpact` · `crsImpactCalc` | 커리큘럼 변경 영향(기존 수강생 분모) | 없음 |
| `bookTable` · `bookRows` · `bkEmptyRow` | 연관 교재 | 교재 표(:1242) · `renderFormTextbooks()` · `modal-textbook-picker` |
| `courseThumbBox` · `courseThumbCurrent` · `courseThumbSelector` · `course_delete_thumbnail` · `courseThumbNew` | 대표 이미지 | `#f-thumb` |
| `instructorTable` · `instructorRows` | 참여 강사 | 없음 |
| `intro_lecture_id` · `intro_lecture_name` · `sample_lecture_id` · `sample_lecture_name` · `badgePreview1/2` | 기타 | 없음 |
| `courseStop` · `courseStopForm` | 판매중지 | `f-sale-status=판매중지` 라디오 |
| `courseDelete` · `courseDeleteForm` | 삭제 | 없음 |
| `curriculumForm` · `curTable` · `curBody` · `curCount` · `curSeconds` · `curLabel` · `curRenumber` · `curInactiveWarn` · `curEmpty` · `curSave` | S1 커리큘럼 페이지 | 커리큘럼 섹션 · `addCurriculumSection()` |
| `candCheckAll` · `candAdd` | 후보 강의 선택 · 추가 | `modal-lecture-picker` · `confirmAddLecturesToSection()` |
| `curImpact` · `curImpactCalc` | 커리큘럼 영향 | 없음 |

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 커리큘럼 구성 전용 페이지(S1)와 판매 이력 강좌의 강의 제외 차단(추가만) — 정본 화면설계서 05 PROD-003-S1 "판매 개시 후 강의 제외 금지"와 일치
- 커리큘럼 변경 영향(기존 수강생 진도율 분모 증가) 미리 보기(`crsImpact` · `curImpact`)
- 교재 매핑 필터 · 컬럼(`book_mapped`), 표 머리 정렬, 전시중 건수
- 대표 강사 계약 종료 배지(자동 판매중지 없음, `CourseService.php:102-103`)
- 참여 강사(부강사 · 참여) 매핑, 원가, 쿠폰 · 포인트 허용, 수강 시작 기준(즉시 / 지정일), 소개 · 샘플 영상, 강조 배지, 강좌 소개 · 수강대상 · 내용 및 특징 3칸
- 판매중지 버튼 · 삭제(참조 7종 있으면 거부) · 복사 · 프론트 미리보기 · 엑셀(사유)

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 강좌 상세 조회 화면(프로토 003-S2: 기본 정보 카드 · 교재 · 판매 상태 변경 이력 :941-949)
- 판매 상태 4종(판매대기 · 판매종료 포함)과 프론트 노출 Y/N 분리 (Q-PROD003-1)
- 수강 만료일 고정(시험일 기준) (Q-PROD003-2)
- 일시정지 허용 정책(횟수 · 누적 일수) (Q-PROD003-4)
- 정산 1계층 매핑 100% 미달 시 판매중 잠금(Hard Lock) · 목록 '정산 매핑' 컬럼 (Q-PROD003-3)
- 주교재 판매중지 · 판매종료 시 강좌 자동 판매중지 · 판매중 잠금(:1686-1689) — PROD-004 Q-PROD004-1
- 할인 설정(정률 % / 정액 원)으로 판매가 자동 계산
- 커리큘럼 섹션(대단원) 구분 · 섹션별 맛보기 토글(`togglePreview()`)
- 한줄 요약 · 검색 태그 · 수강배수/기기제한 표시(:864) · 등록일 기간 검색 · 강사명 검색 · 목록 강좌코드 · 정가 · 총 강의수 컬럼

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 하위 화면 003-S1 등록/수정 · 003-S2 상세 | 003-S2 등록 · 수정 · 003-S1 커리큘럼 구성(상세 없음) |
| `#filter-cat1` · `#filter-cat2` · `#filter-instructor` · `#filter-keyword` | `root_category_id` · `category_id` · `instructor_id` · `keyword` |
| `#filter-sale-status` + `#filter-display` | `display_status` |
| 판매중 / 판매대기 / 판매중지 / 판매종료 + 노출 Y/N | `selling` 전시 · 판매중 / `hidden` 비전시 / `stopped` 판매중지 |
| `#f-title` · `#f-instructor` · `#f-list-price` · `#f-period-days` · `#f-thumb` · `#f-desc` | `title` · `instructors[0][instructor_id]` · `original_price` · `duration_days` · `thumbnail` · `description` |
| 교재구분 주교재 · 부교재 | `book_type` `main` · `sub` |
| 강좌 코드 `CRS-2601` | `CRS_00001` |
| 과세 "면세 상품 (VAT 0%)" | `tax_type=exempt` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
- **Q-PROD003-1 강좌 판매 상태 체계** — 정본 프로토타입: 판매 상태 4종(판매중 · 판매대기 · 판매중지 · 판매종료)과 프론트 노출 Y/N을 따로 둔다(`prototype_clean/ADMN-PROD-003_baseline.html:1177-1204`, 필터 :727 · :738). 개발: `display_status` 1칸 3값(`selling` 전시 · 판매중 / `hidden` 비전시 / `stopped` 판매중지, `app/Models/Concerns/HasDisplayStatus.php:19-31`, `CourseRequest.php:70`) — 화면설계서 05 PROD-003 목록 절 "전시 · 판매중 / 비전시 / 판매중지(전시 유지)"와 같다. 판매대기 · 판매종료를 두고 노출을 분리할지, 개발 3값으로 정본을 고칠지. (교재 · 패키지도 같은 trait를 쓴다 — PROD-004 Q-PROD004-2와 함께 결정)
- **Q-PROD003-2 수강기간 유형** — 정본: "결제일로부터 N일" 또는 "수강 만료일 고정(시험일 기준)"(프로토 :1111-1124). 개발: N일 + 수강 시작 기준(결제 즉시 / 지정일 시작 사전판매)이고 만료일 고정은 없다(`CourseRequest.php:59-62`, `courses.start_type` · `start_date`; 화면설계서 05 PROD-003-S2 "지정일 시작은 사전판매용"). 만료일 고정을 둘지, 지정일 시작으로 대체할지.
- **Q-PROD003-3 정산 1계층 매핑 미완성 강좌의 판매 차단** — 정본: SETT-001 1계층 지분 합계가 100.00%가 아니면 [판매중] 불가 · 판매대기 강제(프로토 :1155-1170, `applySettlementHardLock()`), 화면설계서 05 PROD-003-S2 "권리자 매핑이 유효하지 않은 기간에는 신규 판매를 자동 중단". 개발: 강좌 저장 · 전시 상태에 매핑 검사가 없다(`CourseRequest.php:42-147`, 전시 상태 판정 검색 결과 `PackageRequest.php:173` 외 없음). 저장 차단으로 할지, 판매 시점(결제) 차단으로 할지, 경고만 둘지. PROD-002 Q-PROD002-3과 같은 질문.
- **Q-PROD003-4 강좌별 일시정지 허용 정책** — 정본 프로토: 강좌마다 수강생 마이페이지 일시정지 허용 · 최대 3회 · 누적 30일(:1134-1144). 개발: 강좌에 설정 칸이 없고 일시정지는 관리자 USER-003에서 건별(`CoursePauseRequest`, 무기한 `indefinite` 허용), 화면설계서 05 PROD-003-S2도 "연장 · 일시정지는 USER-003에서 건별". 회원 셀프 일시정지와 강좌별 한도를 둘지. 회원관리 검토의 일시정지 상한 질문(`findings/member/회원관리_개발검토_종합.md` 4절)과 함께 답하면 된다.
