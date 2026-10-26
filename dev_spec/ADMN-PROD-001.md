# ADMN-PROD-001 카테고리 관리 — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-PROD-001_baseline.html` (원본 상태: `84c22e2`, 이 파일 마지막 변경 `c0ee5a4`, 미커밋 변경 없음)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: PROD-001(트리 · 카테고리 정보 · 연결 현황 · 저장/삭제가 한 화면). 하위 S · P 없음. 개발은 비활성 전환 확인 레이어(`layerCatDeactivate`)가 하나 더 있다
- 개발 진행: 구현(라우트 · 화면 있음, `_index/progress.md` 커밋 언급 8건). 엑셀 다운로드는 라우트만 있고 화면 버튼 없음

프로토타입 view ↔ 개발 화면
| 프로토타입 영역(id) | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| 검색 표(`#filterActive` · `#filterKeyword`) | PROD-001 검색 | `resources/views/admin/categories/index.blade.php:37-69` |
| 트리(`#treeContainer`) | ① 카테고리 트리 | `index.blade.php:73-163` (`#catTree`) |
| 상세(`#detailContainer`) 카테고리 정보 · 연결 현황 · 버튼 | ②③④ 우측 폼 | `index.blade.php:165-344` (`#catForm`) |
| (없음 — 저장 시 바로 반영) | 비활성 전환 영향 확인 레이어 | `index.blade.php:361-398` (`#layerCatDeactivate`) |
| — | (구 등록 폼, 미사용) | `categories/form.blade.php` — `create` · `edit` 라우트는 index 로 리다이렉트만 한다(`CategoryController.php:59-104`) |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.categories.index` | 카테고리 관리(추정) | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |

- 권한 축 5개(조회 · 등록 · 수정 · 삭제 · 다운로드). 화면은 권한이 없으면 버튼을 숨기지 않고 `disabled`로 둔다(`index.blade.php:152-161, 319, 326`): [+ 1Depth 추가] = 등록, [정렬 저장] = 수정, [삭제] = 삭제, [저장] = 신규면 등록 · 기존이면 수정.
- 정본(화면설계서 05 :107)은 "상품 롤(PRD_MANAGER)만 등록 · 수정 · 삭제". 개발은 롤 이름이 아니라 메뉴 권한 행으로 판정 → prototype_dev는 버튼마다 `data-dev-perm`(위 축)을 적는다.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{category}` = `categories.id`.

### PROD-001 카테고리 관리
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 화면 · 검색 · 노드 선택(`?id=`) · 신규 모드(`?parent=0` 1Depth / `?parent={id}` 2Depth) | GET | `/categories` | `admin.categories.index` | 조회 | CategoryController@index |
| 엑셀 다운로드(사유 필수) | GET | `/categories/download` | `admin.categories.download` | 다운로드 | CategoryController@download — 화면 버튼 없음 |
| 등록 폼(구) → index `?parent=` 로 리다이렉트 | GET | `/categories/create` | `admin.categories.create` | 등록 | CategoryController@create |
| 정렬 저장 | POST | `/categories/sort` | `admin.categories.sort.update` | 수정 | CategoryController@sort |
| 저장(신규) | POST | `/categories` | `admin.categories.store` | 등록 | CategoryController@store |
| 수정 폼(구) → index `?id=` 로 리다이렉트 | GET | `/categories/{category}/edit` | `admin.categories.edit` | 수정 | CategoryController@edit |
| 저장(수정) | PUT | `/categories/{category}` | `admin.categories.update` | 수정 | CategoryController@update |
| 삭제(소프트) | DELETE | `/categories/{category}` | `admin.categories.destroy` | 삭제 | CategoryController@destroy |
| 연결 현황 [상세] 이동 | → | `/courses/{course}/edit` | `admin.courses.edit` | 수정(강좌 메뉴) | CourseController@edit |

근거: `routes/admin.php:319-332`.

## 3. 폼 필드 · 검증

### 검색 (GET 쿼리, `CategoryController.php:32-35`)
| 필드 name | 값 | 프로토타입 대응 |
|---|---|---|
| `is_active` | `''` 전체 · `1` 전시중 · `0` 비전시 | `#filterActive` ALL · ON · OFF |
| `keyword` | text | `#filterKeyword` |

주의: 개발은 검색 값을 받아 화면에 다시 채우기만 하고 트리에는 적용하지 않는다(`CategoryController.php:39` `getTopCategories()` 인자 없음). 프로토타입은 `getFilteredCategories()`로 트리를 거른다 — 7절.

### 카테고리 저장 (CategoryRequest, `app/Http/Requests/Admin/CategoryRequest.php`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `parent_id` | nullable · integer · 살아 있는 카테고리 · **1Depth만 부모로 허용**(새 3Depth 차단, :239-254) | 빈 값 = 최상위(1Depth) | '상위 카테고리' 읽기 전용 칸(🔒, `renderDetail()` `field-ro`). 개발은 2Depth일 때 `select name="parent_id"`로 상위를 바꿀 수 있다(`index.blade.php:201-209`) |
| `name` | required · string · max 30 · 같은 부모 아래 이름 중복 불가("같은 이름의 카테고리가 이미 있습니다", :217-228) | | `#inpCatName` (maxlength 30) |
| `is_active` | required · boolean | `1` 활성(전시) · `0` 비활성(비전시) | `setNodeActive(true/false)` 칩 2개 |
| `slug` | exclude — 서버가 이름으로 만들고 한글이면 code 소문자로 메움 | | 없음 |
| `sort_order` | exclude — 신규는 형제 맨 뒤, 순서는 정렬 저장으로만 | | '전시 정렬 순서' 읽기 전용 칸 |
| (카테고리 코드) | 요청으로 받지 않음. 저장 후 `CAT_%04d`(예 `CAT_0007`)로 채번, 수정 불가(`CategoryService.php:229-239`) | | '카테고리 코드' 🔒 칸(`AUTO_GEN_ON_SAVE`) |

### 정렬 저장 (CategorySortRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `items[n][id]` | required · integer · min 1 · distinct | 트리 노드 `c.id` |
| `items[n][parent_id]` | nullable · integer — 서버가 DB 값과 대조, 다르면 전체 거절("다른 상위 카테고리로는 옮길 수 없습니다", `CategoryService.php:288`) | 노드 `parentId` |
| `items[n][sort_order]` | required · integer · min 1 — 값은 믿지 않고 배열 순서로 형제끼리 1부터 재채번 | `moveOrder()` 결과 `order` |

화면 전송: 트리 행 `data-cat-id` · `data-cat-parent`를 읽어 `#catSortPayload`에 hidden을 만들고 `#catSortForm`을 제출(`index.blade.php:349-352`, 스크립트 `items[' + index + '][id]`).

### 삭제
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| URL `{category}` | 서버 거부 조건(`CategoryService.php:393-417`): Default(`is_default`) · 하위 카테고리 있음 · `category_products` 매핑 있음 · 강의(`lectures.category_id`) · 강사 담당 과목(`instructor_categories`) 참조 있음 → 모두 "하위 항목을 먼저 이동하거나 삭제해 주세요." (Default만 별도 문구) | `deleteCategory()` — 하위 2Depth · 연결 강좌만 검사 |

### 엑셀 다운로드 (ReasonRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` · `reason_etc` · `reason_ref` | ReasonRequest(정형 사유 + 기타 직접 입력 + 근거 번호) | 없음(프로토 엑셀 버튼 없음) |
| `keyword` · `is_active` | 검색과 같음 | |
| 출력 컬럼 | No · 구분(대분류/중분류) · 카테고리명 · slug · 정렬순서 · 사용여부 · 등록일 (`CategoryController.php:152`) | |

## 4. 목록 필터 · 정렬 · 표 컬럼

목록 표가 아니라 트리다.

| 개발 트리 행 | 프로토타입 트리 노드 |
|---|---|
| `tr.depth--1` / `tr.depth--2` (`data-cat-id` · `data-cat-parent` · `data-cat-href`) | `.tree-node.depth-1` / `.depth-2` (`onclick=selectCategory(id)`) |
| 핸들 `.cat__handle` ⋮⋮ (HTML5 드래그) | `.drag-handle` ⋮⋮ + ▲▼ `moveOrder(id, ±1)` |
| 번호 `.cat__no` (`1.` / `01.`) | `numLabel` |
| 태그 `.cat__tag--on` 전시중 · `--off` 비전시 · `--default` Default | `.badge b-on` · `b-off` · `b-default` |
| 강좌 수 `.cat__count` (1Depth도 하위 합계 표시) | `.tree-meta` "강좌 N" (2Depth만) |
| 빈 1Depth 안내 행 `tr.cat__empty-child` "하위 분류를 추가하세요" | 없음 |
| 비전시 회색 `cat-row--off` | `.inactive-node` |
| (없음) | 노드 메모 `note`(예 "오픈 준비") |

연결 현황 표(③): 순번 · 단과 강좌명(`courses.title`) · 판매가(`sale_price`) · 전시 ON/OFF(`display_status === Course::DISPLAY_SELLING`) · 이동[상세] — 프로토와 같은 5컬럼. 1Depth 선택 시 하위 2Depth 매핑 강좌까지 합친다(`CategoryRepository.php:239-248`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| `categories.id` | id | PK (프로토 `CAT-100` 형식 아님) | 트리 `data-cat-id` |
| `categories.parent_id` | bigint null | 상위. 최상위 NULL | 상위 카테고리 |
| `categories.name` | string(100), 요청은 30자 | 카테고리명 | 트리 · 카테고리명 |
| `categories.slug` | string(100) null | URL용. 자동 | 엑셀만 |
| `categories.depth` | tinyint | 1 대분류 · 2 중분류(3은 과거 1건만) | 트리 들여쓰기 |
| `categories.sort_order` | int | 같은 부모 안 순서 | 번호 · 전시 정렬 순서 |
| `categories.is_active` | tinyint | 전시 여부 | 태그 · 활성화 여부 |
| `categories.code` | string(50) unique | 집계 키, `CAT_%04d` 자동 · 수정 불가 | 카테고리 코드 🔒 |
| `categories.is_default` | boolean | 기본 종목(삭제 불가). 지정 UI 없음 | Default 태그 |
| `categories.deleted_at` | timestamp | 소프트 삭제(mig 2026_09_08_000094) | — |
| `category_products` (`category_id`, `product_type` course/package/book, `product_id`, `sort_order`, `is_primary`) | | 상품 ↔ 카테고리 매핑(대표 = `is_primary` 1) | 연결 현황 · 강좌 수 |
| `admin_logs` (AdminLogService, target_type `App\Models\Category`) | | 등록 · 수정 · 삭제 전후 값 | (화면 없음) |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `catTree` (`table.cat__tree__table`) | 트리 | `#treeContainer` |
| `catSortNotice` | "순서가 바뀌었습니다. [정렬 저장]을 눌러야 반영됩니다." | 없음 |
| `catAddChild` | + 2Depth 추가(1Depth 선택 시만 활성) | `startAddCategory(2)` 버튼 |
| (+ 1Depth 추가, id 없음 → `?parent=0`) | 1Depth 신규 | `startAddCategory(1)` 버튼 |
| `catSortSave` · `catSortForm` · `catSortPayload` | 정렬 저장 | `saveTreeOrder()` 버튼 |
| `catForm` | 카테고리 정보 폼(신규 POST / 수정 PUT) | `#detailContainer` |
| `name="name"` · `name="parent_id"` · `name="is_active"` | 입력 | `#inpCatName` · 상위 칸 · `setNodeActive()` |
| `catDelete` · `catDeleteForm` | 삭제(확인 후 DELETE 제출) | `deleteCategory()` 버튼 |
| `layerCatDeactivate` · `catDeactivateConfirm` | 활성 → 비활성 저장 시 영향 범위(하위 N · 강좌 N) 확인 | 없음(프로토는 경고 문구만) |
| `.cat__panel` · `.cat__blank` | 우측 패널 · 미선택 안내 | `#detailContainer` |

마크업 공통: 레이어 `.layer-pop__overlay` + `layer-pop--hidden`, 닫기 `.layer-pop--close`, 버튼 `.btn__small` · `.btn__system` + `.btn--basic`, 오류 `.fld--err` + `p.txt--red`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 비활성 전환 영향 확인 레이어(`layerCatDeactivate`, `index.blade.php:361-398`) — 하위 분류 수 · 소속 강좌 수 · "이미 결제한 회원 수강 유지". 정본(화면설계서 05 :131 "영향 범위를 저장 전에 모달로 명시")과 일치, 프로토는 경고 문구만
- 정렬 미저장 경고(`catSortNotice`, 다른 노드 클릭 시 confirm, `beforeunload`)
- 2Depth의 상위 카테고리 변경(`select name="parent_id"`, 1Depth만 후보 · 비전시 표시) — 정본(05 :123 "Depth 변경은 상세 폼의 [상위 카테고리] 셀렉트로만")과 일치. 옮기면 새 형제 맨 뒤(`CategoryService.php:370-373`)
- 삭제 거부 조건 추가: 강의 노출 분류(`lectures.category_id`) · 강사 담당 과목(`instructor_categories`) 참조, Default 카테고리(`CategoryService.php:401-417`)
- 빈 1Depth 안내 행 "하위 분류를 추가하세요"(정본 05 :112)
- 1Depth 행에도 하위 합계 강좌 수 표시
- 엑셀 다운로드 라우트(`admin.categories.download`) — 화면 버튼은 개발에도 없음

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 검색 조건으로 트리 거르기(`getFilteredCategories()`) — 개발은 폼만 있고 트리에 적용 안 함(`CategoryController.php:39`). 개발 결함으로 본다
- ▲▼ 버튼 순서 이동(`moveOrder()`) — 개발은 드래그만. 정본(05 :124)은 드래그로 통일이라 ▲▼는 보조 UI
- 1Depth 비활성 저장 시 하위 2Depth도 `active=false`로 바꿈(`saveCategory()`) — 개발은 하위 행 값을 바꾸지 않는다(프론트 숨김 처리 방식은 확인 필요)
- 노드 메모(`note`, "오픈 준비") — 개발 컬럼 없음

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `#filterActive` ALL · ON · OFF | `is_active` `''` · `1` · `0` |
| `#filterKeyword` | `keyword` |
| `#inpCatName` | `name` |
| 활성 칩 `setNodeActive(true/false)` | `is_active` 라디오 `1` · `0` |
| 노드 id `CAT-100` | `categories.id`(정수) |
| 카테고리 코드 `SAFE_PRACTICAL`(의미 있는 영문) | `CAT_0007`(id 기반 자동 채번). 형식 규칙(영문 대문자 + 언더스코어 · 수정 불가)은 같다 |
| `order` · `numLabel` | `sort_order` (번호는 화면에서 `1.` / `01.`로 만든다) |
| `isDefault` | `is_default` |
| 연결 강좌 `display: true/false` | `courses.display_status === selling` → ON |
| `saveTreeOrder()` | POST `admin.categories.sort.update` `items[n][id\|parent_id\|sort_order]` |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
없음. 위 차이는 모두 정본(화면설계서 05 PROD-001 절)이 개발 쪽과 같거나 표시 · UX 차이다. 1Depth 비활성 시 하위 값 동기화는 정책이 아니라 구현 방식이라 질문에 넣지 않았다(확인 필요로만 둠).
