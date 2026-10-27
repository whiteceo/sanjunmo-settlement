# ADMN-SETT-001 상품별 권리자 매핑 — 개발 명세
- 프로토타입 파일: prototype_clean/ADMN-SETT-001_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-SETT-001 · ADMN-SETT-001-S1 · ADMN-SETT-001-P1
- 개발 진행: 구현 (담당 박성민, `_index/progress.md` 라우트 주석 있음 · 커밋 언급 6건). S1 은 별도 페이지, P1 은 S1 안의 모달

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.settlement.rights-mapping.index` | 상품별 권리자 매핑 | tests/Feature/Admin/RightsMappingTest.php:63-65 (테스트가 이 route_name 으로 메뉴 행을 찾거나 만든다). 운영 DB 의 admin_menus 행은 저장소에 시드가 없어 미확인 |

- 하위 라우트(`…rights-mapping.show` · `.store` · `.contracts`)는 모두 `admin.settlement.rights-mapping.index` 로 정규화돼 같은 메뉴 권한 행을 쓴다(app/Services/Admin/AdminPermissionService.php:291).
- 조회 · 요율 노출 · 저장은 전부 관리자 감사 로그(admin_logs, sub_action `rights_mapping_list` · `rights_mapping_rate_view`)에 남는다(app/Http/Controllers/Admin/RightsMappingController.php:44-51, 82-89, 110-117).

## 2. 화면별 라우트
### ADMN-SETT-001 상품별 권리자 매핑(목록)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 검색 · 스코어카드 | GET | `/{admin}/settlement/rights-mapping` | `admin.settlement.rights-mapping.index` | can_view | RightsMappingController@index |

### ADMN-SETT-001-S1 권리자 매핑 편집(별도 페이지)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 편집 화면 열기 `?type=course|book&id=` | GET | `/{admin}/settlement/rights-mapping/edit` | `admin.settlement.rights-mapping.show` | can_view | RightsMappingController@show |
| 적용 계약 후보(JSON) | GET | `/{admin}/settlement/rights-mapping/contracts` | `admin.settlement.rights-mapping.contracts` | can_view | RightsMappingController@contracts |
| 매핑 저장(AJAX, 즉시 확정) | POST | `/{admin}/settlement/rights-mapping` | `admin.settlement.rights-mapping.store` | can_create | RightsMappingController@store |

- URL 은 `/edit` 이지만 이름은 `show` 다 — 조회 권한만으로 열리게 하려는 의도(routes/admin.php:535 주석, RightsMappingController.php:63-68).
- 저장 성공 응답 `{ok, message, redirect}` — redirect 는 목록의 직전 검색 조건(LIST_KEYS) 그대로(RightsMappingController.php:141-146).

### ADMN-SETT-001-P1 지분율 100% 검증 실패(모달)
- 별도 라우트 없음. store 가 422 `{ok:false, violations:[...]}` 를 돌려주면 S1 안의 `#layerMappingViolation` 모달이 위반 코드로 유형을 고른다(RightsMappingController.php:136-139, resources/views/admin/settlement/rights-mapping/_violation-modal.blade.php).

## 3. 폼 필드 · 검증
### 매핑 저장 (RightsMappingRequest) — JSON 본문
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `type` | required · in | `course`(강좌) · `book`(도서 SKU) | 상품 구분(`fType`) |
| `id` | required · integer ≥1 | courses.id / books.id | 선택 상품 |
| `lecture_ids[]` | array · integer ≥1 | 강좌일 때 편집 단위 강의 | 강의 단위 선택 · "전체 강의 일괄적용" |
| `rows[]` | required · array · min:1 | 권리자 행 | 권리자 지분 행 표 |
| `rows.*.id` | nullable · integer | 기존 행 id. 값이 바뀌면 서비스가 닫고 새 행 삽입 | — |
| `rows.*.rights_holder_id` | required · integer | rights_holders.id | 권리자 선택 |
| `rows.*.contract_id` | required · integer | rights_holder_contracts.id (필수) | 적용 계약 |
| `rows.*.share_ratio` | required · numeric 0~100 · decimal:0,2 | 지분율(%) | 지분율 |
| `rows.*.start_date` | required · Y-m-d | 유효 시작일 | 유효 시작 |
| `rows.*.end_date` | nullable · Y-m-d · ≥ start_date | 유효 종료일(NULL=기한 없음) | 유효 종료 |
| `list[...]` | (컨트롤러가 읽음) | 목록 복귀용 검색 조건 | — |

출처: app/Http/Requests/Admin/RightsMappingRequest.php:23-44 · 47-70.

- v6.92(S-06): 프로토 [+ 자사 권리자 행 추가](`#internalRowBtn` · `data-action="addInternalRow"`)는 같은 `rows[]` 행을 자사 권리자(`rows.*.rights_holder_id` = `rights_holders.is_internal=1`)로 연다 — 지분 `share_ratio`는 직접 입력, 사유 칸에 계약 근거. 새 필드 없음. 저장 때 새 자사 지분 행이 있으면 확인 모달(`#internalShareConfirm`, 화면 전용 — 개발 없음).

### 적용 계약 후보 (RightsMappingContractRequest) — GET 쿼리
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `rights_holder_id` | required · integer | | 권리자 행 추가 시 선택한 권리자 |
| `type` | required · in course/book | | |
| `id` | required · integer | | |

### 서버 판정 위반 코드 (P1 유형) — RightsMappingService 상수
| 코드 | 뜻 |
|---|---|
| `SHARE_SUM` | 날짜 구간별 지분 합계가 100.00 이 아니다 |
| `SIGNER_SCOPE` | 그 계약의 공동 서명인이 아닌 권리자 |
| `CONTRACT_INVALID` | 계약이 active 아님 · 후보 조건 · 요율 출처 불충족 |
| `PERIOD_RANGE` | 행 기간이 저장 허용 구간 밖 (`#mvFitWindow` "허용 구간으로 맞추기" 노출) |
| `LOCKED_MONTH` | 유효 시작일이 마감월에 걸림(site_settings.settlement_closed_month) |
| `PERIOD_DUP` | 같은 상품 · 같은 권리자 기간 겹침 |
| `NOT_TARGET` | 정산 비대상 교재 — 차단이 아니라 안내(자사 100% 자동) |
| `CONSIGNMENT_SINGLE` | 위탁 교재는 위탁자 1인 100.00% 고정 |
| `SUPPLY_TYPE_MISSING` | 공급 형태 미지정 교재 — 도서 원장에서 지정 필요 |

출처: app/Services/Admin/RightsMappingService.php:27-80.

## 4. 목록 필터 · 정렬 · 표 컬럼
### 검색 쿼리(GET, `#searchForm`) — LIST_KEYS
| name | 값 | 프로토타입 대응 |
|---|---|---|
| `product_type` | ''(전체) · `course`(강좌) · `book`(도서 SKU) | `fType` (프로토타입은 "일반 상품" 옵션도 있음) |
| `supply_type` | ''(전체) · `OWN_PUBLISHED`(자사 발행) · `PURCHASED_RESALE`(매입 재판매) · `CONSIGNMENT`(위탁) · `BUNDLED`(부속) | 없음 |
| `keyword` | 강좌: title · code / 도서: title · code · isbn LIKE | `fKeyword` (프로토타입은 권리자명도 검색) |
| `rights_holder_id` | 권리자 select | 없음(키워드에 포함) |
| `valid_on` | 매핑 유효일(기본 오늘) — 이 날짜 기준으로 현행 지분 판정 | 없음 |
| `verify_state` | ''(전체) · `unmapped`(미매핑) · `share_error`(지분 합계 오류) · `expiring`(계약 만료 임박, 30일) · `auto`(자사 자동 매핑) · `ok`(정상) | `fStatus` |
| `page` | 페이지 | |

- 스코어카드 4종(unmapped · share_error · expiring · auto)은 검색 조건과 무관한 전체 건수, 클릭 시 `verify_state` 로 목록을 거른다(index.blade.php:7-12, 123-128; RightsMappingRepository.php:65-77).
- 정렬: 강좌 · 도서 UNION 후 `created_at` desc, `product_id` desc. 30건/페이지(RightsMappingRepository.php:46-57).
- 표 컬럼: No · 구분 · 공급 형태 · 상품명(상품코드) · 매핑 단위 · 배정 권리자 · 지분(%) · 지분 합계 · 매핑 유효 기간 · 상태 · 관리([조회]/[매핑]/[수정] → S1)(index.blade.php:162-172, 262-266).
- 준비 중(disabled) 버튼: 매핑 일괄 업로드(엑셀) · 전체 엑셀 다운로드 · 양식 다운로드(index.blade.php:147-149).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| lecture_instructors.lecture_id | foreignId | 강의(강좌 매핑 단위 = 강의) | S1 강의 구간 |
| lecture_instructors.rights_holder_id | foreignId | 권리자 | 배정 권리자 |
| lecture_instructors.contract_id | foreignId | 적용 계약(요율 조회 경로 종결) | 적용 계약 |
| lecture_instructors.share_ratio | decimal(5,2) | 지분율 — 같은 강의 · 같은 기간 합계 100.00 | 지분(%) |
| lecture_instructors.start_date / end_date | date / date null | 유효 기간 | 매핑 유효 기간 |
| book_authors.book_id · rights_holder_id · contract_id · share_ratio · start_date · end_date | 위와 같음 | 도서 SKU 단위 매핑 | 도서 행 |
| books.book_supply_type | string(20) null | OWN_PUBLISHED / PURCHASED_RESALE / CONSIGNMENT / BUNDLED | 공급 형태 |
| books.settlement_required_yn | boolean | 정산 대상 여부(OWN_PUBLISHED · CONSIGNMENT=1). 0 이면 자사 자동 | 상태(자사 자동) |
| courses.code · title · sale_price · display_status | | 강좌 기본 정보 | 상품명 · 판매가 |
| contract_rate_lines · book_royalty_contracts | | 계약 정산요율 · 인세 요율 출처(읽기) | S1 "계약 정산요율 🔒" |
| site_settings.settlement_closed_month | char(7) | 마감 완료월 — 이 달까지 시작일 저장 불가 | S1 마감 경계 |

출처: dev_spec/_index/schema.md lecture_instructors(2404) · book_authors(2417) · books(245-246) · site_settings(1010); app/Repositories/Admin/RightsMappingRepository.php:105-162, 500-561.
- 참고: 마이그레이션 2026_08_14_000013 의 `product_instructor_shares` 도 주석에 ADMN-SETT-001 이 있으나 현재 리포지토리는 lecture_instructors · book_authors 를 쓴다(추정: 구 테이블).

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#searchForm` | 목록 검색 폼(GET) | fType · fStatus · fKeyword 를 감싼 영역 |
| `.link--view` / `.rm-warn` | 스코어카드 링크 · 경고색 | 스코어카드 |
| `#mappingForm` | S1 편집 영역 | 상세 탭(2) |
| `#checkAllLectures` / `.js-lecture-group`(value=강의 id 콤마, `data-rows`) | 강의 구간 선택 | 강의 단위 선택 · "전체 강의 일괄적용" |
| `#shareRows` · `#shareEmpty` | 권리자 행 tbody · 빈 행 | 지분 행 표 |
| `tr[data-key]` · `.js-contract` · `.js-share` · `.js-rate` · `.js-start` · `.js-end` · `.js-remove` | 행 단위 입력 | 행 입력 |
| `#shareSum` · `#shareSumHint` | 합계 · 안내 | 합계 표시 |
| `.layer__open[data-target="layerHolderPick"]` / `#layerHolderPick` · `#holderKeyword` · `#holderRows` · `.js-holder-row` · `.js-holder-pick`(data-id · data-name · data-code) | 권리자 행 추가 모달 | "+ 권리자 지분 행 추가" 모달 |
| `#btnSave` | 매핑 저장(fetch POST) | "현재 단위(강의/SKU) 매핑 저장" |
| `#layerMappingViolation` · `#mvTitle` · `#mvInfo` · `#mvInfoText` · `#mvTable` · `#mvBody` · `#mvGoLedger` · `#mvFitWindow` | P1 위반 모달 | 검증 상세 모달 |
| `.layer-pop--close` | 모달 닫기 | 닫기 |

출처: resources/views/admin/settlement/rights-mapping/index.blade.php:45-149; edit.blade.php:103-211, 220-263, 274-500; _violation-modal.blade.php:8-137.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 목록 필터 `supply_type`(공급 형태) · `rights_holder_id`(권리자) · `valid_on`(매핑 유효일), 검증 상태 `expiring`(계약 만료 임박 D-30) · `ok`(정상).
- 스코어카드 4종(미매핑 판매 상품 · 지분 합계 오류 · 계약 만료 임박(D-30) · 자사 자동 매핑).
- 서버 위반 코드 9종(3절) 중 `SIGNER_SCOPE` · `CONTRACT_INVALID` · `PERIOD_RANGE` · `LOCKED_MONTH` · `SUPPLY_TYPE_MISSING` · `CONSIGNMENT_SINGLE` 안내, P1 의 "허용 구간으로 맞추기" · "권리자 계약 원장으로 이동".
- S1 머리 정보: 마감 경계 · 저장 허용 시작 · 계약 원장 링크.
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- "3. 지분 변경 · 감사 이력" 탭 — 개발은 `변경 이력` 버튼이 disabled "준비 중"(edit.blade.php:210).
- 모계약 종료일 일괄 동기화, 최근 저장 스냅샷 JSON 보기.
- ~~잔여 지분 자사(엘캠퍼스) 자동 채우기~~ **→ 결정(v6.92 white, S-06)**: 자동 채우기 삭제 → [자사 권리자 행 추가](지분 직접 입력) + 저장 시 자사 지분 확인 모달. 개발은 권리자 선택 레이어에서 자사 권리자를 고를 수 있으나 저장 전 자사 지분 확인은 없음(추가 필요)
- 상품 구분 "일반 상품(자사 매출)" — 개발 목록은 강좌 · 도서만.
- 매핑 일괄 업로드 · 엑셀 다운로드 — 개발은 버튼만 있고 disabled.
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| `fType` | `product_type` (course · book) |
| `fStatus` 미매핑·판매차단 / 계약 기간 불일치 / 100.00% 매핑 / 자사 100% 자동 | `verify_state` unmapped / (대응 없음, 서버 PERIOD_RANGE 위반으로만) / ok / auto, 추가 share_error · expiring |
| `fKeyword` | `keyword` |
| 목록 · 상세 · 이력 탭 한 페이지 | 목록 `…rights-mapping.index` + 편집 별도 페이지 `…rights-mapping.show` (`/edit?type=&id=`) |
| 샘플 권리자 코드 RH-xxxx · 계약 CT-xxxx | rights_holders.code · rights_holder_contracts.code (형식은 권리자 원장 명세 참조) |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_SETT.md` 의 D-SETT 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 확인 필요: 프로토타입 상태 "계약 기간 불일치"는 개발에 목록 필터 값이 없고 저장 시 `PERIOD_RANGE` 차단으로만 다룬다. 목록 상태로 둘지.
- 확인 필요: "일반 상품(자사 매출)"을 이 화면 대상에 넣을지 — 개발은 강좌 · 도서만 매핑한다.

## 출처
- routes/admin.php:530-536
- app/Http/Controllers/Admin/RightsMappingController.php:16-163
- app/Http/Requests/Admin/RightsMappingRequest.php:23-95 · RightsMappingContractRequest.php:18-30
- app/Services/Admin/RightsMappingService.php:27-130
- app/Repositories/Admin/RightsMappingRepository.php:32, 46-100, 105-300, 500-561
- app/Services/Admin/BookSupplyService.php:30-35
- app/Services/Admin/AdminPermissionService.php:261-300, 433-476
- resources/views/admin/settlement/rights-mapping/index.blade.php · edit.blade.php · _violation-modal.blade.php
- tests/Feature/Admin/RightsMappingTest.php:63-65
