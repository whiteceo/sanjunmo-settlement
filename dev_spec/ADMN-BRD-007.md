# ADMN-BRD-007 1:1 문의 분류 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-BRD-007_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-BRD-007(분류 목록), ADMN-BRD-007-S1(분류 등록 · 수정)
- 개발 진행: 구현. 담당 이응민. progress 표 비고 "ADMN-BRD-007-S1 dev 반영 724a7a0(ADMN-BRD-007 로만 표기)에서 분류 등록 · 수정까지 구현"

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.inquiry-categories.index` | 1:1 문의 분류 관리 | 라우트 정규화(대분류 `admin.inquiry-categories.majors.*` 는 하위 자원 세그먼트를 걷어 이 메뉴로 올라감). 메뉴 행 데이터는 DB |

- ROUTE_PERMISSIONS 예외 없음. 담당 부서 큐 후보는 admin_roles 중 `super` 를 뺀 전부(InquiryCategoryRepository:119-122).

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`).

### ADMN-BRD-007 분류 목록 (+ 대분류 관리)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/inquiry-categories` | `admin.inquiry-categories.index` | 조회 | InquiryCategoryController@index |
| 선택 사용/미사용 | PUT | `/{admin}/inquiry-categories/status` | `admin.inquiry-categories.status.update` | 수정 | InquiryCategoryController@bulkStatus |
| 대분류 추가 | POST | `/{admin}/inquiry-categories/majors` | `admin.inquiry-categories.majors.store` | 등록 | InquiryCategoryController@storeMajor |
| 대분류 수정 | PUT | `/{admin}/inquiry-categories/majors/{inquiryCategory}` | `admin.inquiry-categories.majors.update` | 수정 | InquiryCategoryController@updateMajor |

### ADMN-BRD-007-S1 분류(소분류) 등록 · 수정 (같은 페이지 안 폼 구획)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 소분류 등록 | POST | `/{admin}/inquiry-categories` | `admin.inquiry-categories.store` | 등록 | InquiryCategoryController@store |
| 소분류 수정 | PUT | `/{admin}/inquiry-categories/{inquiryCategory}` | `admin.inquiry-categories.update` | 수정 | InquiryCategoryController@update |

- 등록 · 수정 폼을 여는 GET 라우트(create/edit)는 없다. 목록 행의 `data-*` 값을 JS 가 폼에 채운다.

## 3. 폼 필드 · 검증
### 소분류 `subForm` (InquiryCategoryRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `parent_id` (`subParent`) | required integer · 존재. 수정 때는 서버가 무시(잠금) | 대분류 | `cf-major` |
| (코드 `subCode`, 전송 안 함) | 등록 시 서버가 `VOC-{대분류code}-{2자리 일련}` 자동 채번, 수정 불가 | | `cf-code`(readonly) |
| `name` (`subName`) | required string max:40 · 같은 대분류 안 중복 불가(서비스) | 소분류 명칭 | `cf-name` |
| `target_screen` (`subTarget`) | required in InquiryCategory::TARGET_SCREENS | ADMN-BRD-002 1:1 문의 관리 · ADMN-BRD-002-S1 1:1 문의 답변 상세 · ADMN-RFD-002-S1 환불 관리 상세 · ADMN-USER-003 회원 기기 관리 | `cf-screen` |
| `assign_role` (`subRole`) | required string · admin_roles.code 존재. 단일 선택 | cs · logistics · finance · instructor · assistant 등(super 제외) | `cf-depts`(체크박스 복수 선택) |
| `is_active` (`subActive1`/`subActive0`) | required boolean | 1=사용 · 0=미사용 | `cf-status` ON/OFF |
| `sort_order` (`subSort`) | nullable integer min:0 | 노출 순서 | `cf-order`(min 1) |
| `editing_id` (`subEditingId`) | hidden, 폼 동작 전환용 | | 없음 |

### 대분류 `majorForm` (InquiryMajorCategoryRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `name` (`majorName`) | required string max:50 | 대분류명 | `new-major-name` |
| `code` (`majorCode`) | required · max:20 · `^[A-Z0-9]+$` · 중복 불가. 대문자 저장, 등록 후 잠금 | 소분류 코드 약어(VOC-{code}-NN) | `new-major-prefix` |
| `sort_order` (`majorSort`) | nullable integer min:0 | | 없음 |
| `is_active` (`majorActive1`/`majorActive0`) | nullable boolean. 하위 소분류가 있으면 미사용 불가(서비스) | | 표 "상태" |

### 일괄 상태 `bulkForm` (컨트롤러 인라인 검증)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `ids[]` | required array min:1 · integer | `cat-check-all` + 행 체크 |
| `is_active` (`bulkActive`) | required boolean | `bulkSetStatus('ON'/'OFF')` |

## 4. 목록 필터 · 정렬 · 표 컬럼
- 필터(쿼리 파라미터, InquiryCategoryController::buildIndexData:96-111): `parent_id`(대분류) · `is_active` · `per_page`(20/50/100).
- 요약 수치: 대분류 수 · 소분류 수 · 미사용 수(`counts` majors · subs · inactive).
- 소분류 표(개발): 선택 · 분류 코드 · 대분류 · 소분류 명칭 · 자동 배정 화면 · 담당 부서 큐 · 상태 · 순서 · 관리.
- 대분류 표(개발): 약어(code) · 대분류명 · 순서 · 상태 · 관리.
- 프로토타입: KPI 5종(`kpi-major` · `kpi-major-sub` · `kpi-minor` · `kpi-off` · `kpi-screens`), 필터 `flt-major` · `flt-status`, 소분류 표는 개발과 같은 열 구성, 분류 변경 이력 표(변경 일시 · 관리자 · 대상 · 변경 내용).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| inquiry_categories.id | id | | — |
| inquiry_categories.parent_id | bigint nullable | NULL=대분류, 값=소분류의 대분류 | 대분류 |
| inquiry_categories.code | string(30) unique | 대분류: 약어(대문자) / 소분류: VOC-{약어}-NN 자동 채번 | 분류 코드 |
| inquiry_categories.name | string(50) | 분류명(소분류 입력은 40자 제한) | 명칭 |
| inquiry_categories.target_screen | string(50) | 자동 배정 화면코드 | 자동 배정 화면 |
| inquiry_categories.assign_role | string(30) | 담당 부서 admin_roles.code(단일) | 담당 부서 큐 |
| inquiry_categories.is_active | tinyint | 0=신규 접수 선택 불가(기존 문의 유지) | 상태 |
| inquiry_categories.sort_order | int | 노출 순서 | 순서 |
| inquiry_category_roles.category_id / role_code | | 분류-부서 복수 매핑 테이블(스키마에 있음). 이 화면의 저장은 assign_role 단일(InquiryCategoryRequest 주석 "설계서 복수선택은 스키마 미지원") — 이 테이블을 쓰는지는 확인 필요 | — |
| admin_roles.code | string | super · cs · logistics · finance · instructor · assistant | 담당 부서 후보 |
| admin_logs | | 분류 등록 · 수정 · 일괄 상태 이력 | (화면에 이력 표 없음) |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `bulkForm` · `bulkActive` · `toggleAll()` · `submitBulk()` | 선택 사용/미사용 | `bulkSetStatus()` |
| 행 `data-id` · `data-parent` · `data-name` · `data-code` · `data-target` · `data-role` · `data-visible` · `data-sort` | 수정 폼 채우기 원천 | `openCatPage(code)` |
| `subFormSection` · `subFormTitle` · `subForm` · `subMethod` · `subEditingId` · `subParent` · `subCode` · `subName` · `subTarget` · `subRole` · `subActive1/0` · `subSort` | 소분류 등록 · 수정 폼(같은 페이지 구획) | 서브페이지 S1 `cf-*` |
| `beforeSubmit` 의 `confirm('변경 시 이후 접수되는 문의가 해당 화면·부서로 배정됩니다…')` | 수정 시 라우팅 변경 경고 | `modal-route-confirm` · `confirmRouteChange()` |
| `majorPanelSection` · `majorForm` · `majorMethod` · `majorName` · `majorCode` · `majorSort` · `majorActive1/0` · `majorSubmit` | 대분류 관리(같은 페이지 구획) | `modal-major` · `addMajor()` |
| `changePerPage()` | 쪽 크기 | 없음 |

하위 화면: 개발 S1 은 별도 페이지가 아니라 목록 페이지 안 폼 구획(`subFormSection`), 대분류도 구획(`majorPanelSection`). 프로토타입은 S1 = SJM_PAGE 서브페이지, 대분류 = 모달.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 대분류 수정(이름 · 순서 · 상태) — 프로토타입 대분류 모달은 추가만.
- 대분류 노출 순서 · 상태 입력, 쪽 크기 선택.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 분류 변경 이력 표(개발은 admin_logs 에 남기지만 화면 표시 없음).
- 담당 부서 큐 복수 선택(개발은 단일 `assign_role`).
- KPI "자동 배정 화면 수".

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 상태: `cf-status` ON/OFF → `is_active` 1/0, 일괄 `bulkSetStatus('ON'/'OFF')` → `bulkActive` 1/0.
- 대분류 접두: `new-major-prefix` → `code`(대문자 · 숫자만, 20자).
- 자동 배정 화면 값: 화면코드 4종(ADMN-BRD-002 · 002-S1 · RFD-002-S1 · USER-003)만 허용. 프로토타입 이력 샘플의 "학습 Q&A"는 개발 목록에 없음(1:1 문의는 상품 · 학습 Q&A 로 이관 불가, Inquiry::CLOSED_BOARDS).
- 소분류 명칭 최대 40자(대분류 50자).

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_BRD.md` 의 D-BRD 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 담당 부서 큐 복수 선택(프로토타입 · 설계서)과 개발 단일 저장의 차이 확인 필요 — 스키마에는 inquiry_category_roles(복수)가 있으나 요청 검증은 단일.
- 분류 변경 이력을 화면에 보여 줄지 확인 필요.

## 출처
- routes/admin.php:821-830 (dev_spec/_index/routes.md)
- app/Http/Controllers/Admin/InquiryCategoryController.php:22-111
- app/Http/Requests/Admin/InquiryCategoryRequest.php · InquiryMajorCategoryRequest.php
- app/Services/Admin/InquiryCategoryService.php:24, 37, 48-62, 89-94, 116-123, 142-152, 180
- app/Repositories/Admin/InquiryCategoryRepository.php:31, 119-122
- app/Models/InquiryCategory.php:19-29, 70
- app/Models/Inquiry.php:35-50 (CLOSED_BOARDS · REFUND_BOARD)
- resources/views/admin/inquiry-categories/index.blade.php:38-66, 97-115, 132-273, 295-360
- database: dev_spec/_index/schema.md inquiry_categories · inquiry_category_roles · admin_roles
- 프로토타입: prototype_clean/ADMN-BRD-007_baseline.html:116-205(목록 · 이력), 209-262(S1 서브페이지), 268-306(modal-major · modal-route-confirm), 339-346(스크립트)
