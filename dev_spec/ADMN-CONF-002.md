# ADMN-CONF-002 약관 및 개인정보처리방침 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-CONF-002_baseline.html (원본 상태: 84c22e2 + 미커밋 작업 트리)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-CONF-002 약관 목록 · 버전 이력 · 개정 등록/편집 · 버전 상세
- 개발 진행: 구현(담당 이응민, `_index/progress.md` 107행)

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.terms.index` | 약관·정책 관리 | routes/admin.php:1170 (주석 :1166 "약관·정책 관리"). 하위 `history` 는 `admin.terms.history.index` → 부모 메뉴로 판정 |

## 2. 화면별 라우트
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 약관 종류 목록(6종 현황) | GET | `/{admin}/terms` | `admin.terms.index` | can_view | TermController@index |
| 종류별 버전 이력 | GET | `/{admin}/terms/history?type=` | `admin.terms.history.index` | can_view | TermController@history |
| 개정 시작(작성중 있으면 그 편집으로) | GET | `/{admin}/terms/create?type=` | `admin.terms.create` | can_create | TermController@create |
| 개정본 저장(임시/확정) | POST | `/{admin}/terms` | `admin.terms.store` | can_create | TermController@store |
| 버전 상세(전문 열람) | GET | `/{admin}/terms/{term}` | `admin.terms.show` | can_view | TermController@show |
| 작성중 편집 | GET | `/{admin}/terms/{term}/edit` | `admin.terms.edit` | can_update | TermController@edit |
| 작성중 저장(임시/확정) | PUT | `/{admin}/terms/{term}` | `admin.terms.update` | can_update | TermController@update |
| 작성중 개정본 버리기 | DELETE | `/{admin}/terms/{term}` | `admin.terms.destroy` | can_delete | TermController@destroy |

- `type` 쿼리는 6종 키(아래 코드값)만 받고, 아니면 목록으로 "약관 종류를 다시 골라 주세요." — TermController.php:181-187
- 확정(`draft` 아님)된 버전의 edit 는 show 로 돌려보냄("확정된 버전은 고칠 수 없습니다…") — TermController.php:98-108
- 새 개정 차단: 작성중 개정본이 있거나 공시중(시행 전) 버전이 있으면 — TermService.php:176-186
- 임시저장 후 편집 화면 유지, 확정 후 목록 — TermController.php:133-140

## 3. 폼 필드 · 검증

### 개정본 `#termForm` (TermRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소 |
|---|---|---|---|
| `action` | required · in | `draft` 임시저장 / `confirm` 확정 | [임시저장 (DRAFT)] · [약관 저장 및 공시 확정] |
| `type` | POST 일 때만 required · in CODES 키 | `service` T01 이용약관 · `privacy_consent` T02 개인정보 수집·이용 동의 · `privacy` T03 개인정보처리방침 · `refund` T04 환불·청약철회 규정 · `marketing` T05 마케팅 정보 수신 동의(선택) · `age14` T06 만 14세 이상 확인 | `#dt-term-switcher` |
| `revision` | nullable · in | `minor` 일반 개정(v1.4→v1.5) · `major` 전면 개정(v1.4→v2.0) | `#ed-rev-type` |
| `title` | required · max:255 | — | (없음) |
| `content` | required | — | `#ed-body` |
| `notice_date` | confirm 이면 required · date | 공시 일자 | `#ed-announce-date` |
| `effective_date` | confirm 이면 required · date · ≥ notice_date | 시행 일자 | `#ed-effective-date` |
| `is_unfavorable` | nullable · boolean | 1 불리(공시 30일) / 0 일반(7일) — 기준 미달은 경고만 | `#ed-adverse` |
| `change_reason` | confirm 이면 required · max:500 | 사용자 공지 · 재동의 안내 요약문으로 재사용 | `#ed-reason` |

- 버전 번호는 서버가 `revision` 으로 채번(문자열 `'1.5'`) — app/Models/Term.php:12, :50-55, :122-126. 화면 `#termVersion` · `[data-term-version]` 은 표시용.

## 4. 목록 필터 · 정렬 · 표 컬럼
- 목록(`terms/index.blade.php:35-36`) 컬럼: 구분 · 약관명 · 필수 · 현행 버전 · 공시 일자 · 시행 일자 · 상태 · 최종 수정자 …(필터 없음, 6종 고정 행)
- 이력(`terms/history.blade.php:22-23`) 컬럼: 버전 · 상태 · 공시 일자 · 시행 일자 · 개정 사유 · 최종 수정자 · 등록…
- 쿼리: `type`(history · create)

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| terms.type | string(30) | 약관 종류 키(위 6종, 옛 `bookprice` 는 관리 대상 아님) | 구분 |
| terms.code | string(10) | `T01`~`T06` 고정 | 약관 코드 |
| terms.version | VARCHAR(10) `'major.minor'`(000098 · Term.php:12) | 버전 | 현행 버전 · 이력 |
| terms.title · content | string · longText | 제목 · 본문 | 편집 |
| terms.is_required | boolean | 필수(가입 STEP1 체크박스와 1:1, `marketing` 만 선택) | 필수 |
| terms.notice_date · effective_date | date | 공시 일자 · 시행 일자 | 목록 · 이력 |
| terms.change_reason | string(500) | 개정 사유 | 이력 |
| terms.is_unfavorable | boolean | 불리한 개정(30일) / 일반(7일) | — |
| terms.status | string(20) | `active` 시행중 · `pending` 공시중(시행 전) · `expired` 폐지 · `draft` 작성중 | 상태 |
| terms.is_active | tinyInteger | 현재 시행 버전 여부 | — |
| terms.admin_id | unsignedBigInteger | 최종 수정자 users.id | 최종 수정자 |
| user_agreements (연계) | — | 회원 동의 이력 — 동의 이력 있는 버전은 삭제 불가 | — |

- 공시 기준 일수 상수 `Term::NOTICE_DAYS_UNFAVORABLE`=30 · `NOTICE_DAYS_GENERAL`=7 (주석 "미확정: 설정 분리 확인필요") — Term.php:68-72
- `version` 은 마이그레이션 000098 이 raw SQL 로 INT → VARCHAR(10)(기본 '1.0', 기존 값에 '.0' 붙임)로 바꿨다. `_index/schema.md` 도 10-27 재색인으로 varchar(10) NOT NULL 로 반영됨 — database/migrations/2026_09_08_000098_extend_site_config_tables.php:141-160

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `#termForm` | 개정본 폼 | 편집 탭 |
| `#termAction` · `[data-term-action]` | 임시저장/확정 버튼이 `action` 값을 넣음 | `saveTermDraft()` · `openSaveConfirmModal()` |
| `#termVersion` · `[data-term-version]` · `[data-term-version-label]` | 개정 유형 따라 다음 버전 표시 | `#ed-ver-num` · `calcNextVersion()` |
| `#termNoticeDate` | 공시일(기준 일수 경고) | `validateNoticePeriod()` |
| `#termCurrent` · `#termCompare` · `#termCompareToggle` | 현행 본문 대조 | `openDiffModal()` / `modal-diff` |
| `#layerTermPreview` · `#termPreviewFrame` · `#termPreviewOpen` | 사용자 화면 미리보기 레이어 | (없음) |
| `[data-flash-warning]` | 저장 후 경고(공시 기준 미달 등) | — |

- 하위 화면 표현: 목록 · 이력 · 편집 · 상세가 각각 별도 페이지. 프로토타입은 한 페이지 안 뷰 전환 + 상세 탭(`switchDetailTab`) + 모달 3개.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 사용자 화면 미리보기 레이어 `#layerTermPreview`.
- 작성중 개정본 버리기(`admin.terms.destroy`).
- 제목 `title` 입력.
- 종류 T02 개인정보 수집·이용 동의, T06 만 14세 이상 확인(프로토타입 switcher 는 T01~T05 5종).

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- [유형 2] 현행/공시예정 본문 직접 수정(`DIRECT_FIX`) — 개발은 확정 버전 수정 불가(새 개정만).
- [전체 회원 개정 고지 발송 (CONF-004-S1)] 바로가기 `goTermsNoticeSend()`.
- 에디터 도구(굵게 · 밑줄 · 조항 추가 · 개정 강조), [현행 조문으로 초기화], 이력에서 [이 버전 본문을 편집창으로 불러오기].
- [신규 약관 종류 추가 안내] — 개발은 6종 고정.
- 목록 컬럼 "수집 구분 / DB 매핑 · 프론트 노출 위치 · 보관 버전 수".

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 개정 유형 `#ed-rev-type` → `revision` = `minor`/`major`.
- 불리한 변경 `#ed-adverse`(아니오/예) → `is_unfavorable` 0/1.
- 공고일자 `#ed-announce-date` → `notice_date`, 시행일자 → `effective_date`, 사유 `#ed-reason` → `change_reason`, 본문 `#ed-body` → `content`.
- 저장: 확인 모달 `modal-save-confirm` → 개발은 같은 폼 `action=confirm` 제출.
- 상태 라벨: 개발 `active` 시행중 · `pending` 공시중 · `expired` 폐지 · `draft` 작성중.

## 8. 정책 질문 (white 확인 필요)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_CONF.md` 의 D-CONF 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 공시중(시행 전) 버전 본문 수정 허용 여부: 프로토타입 [유형 2] 허용, 개발은 불가(TermService.php:182 주석 "미확정") — 확인 필요.
- 약관 종류: 정본이 T01~T06 6종인지(프로토타입 5종 표시) — 확인 필요.

## 출처
- routes/admin.php:1166-1179
- app/Http/Controllers/Admin/TermController.php:24-187
- app/Services/Admin/TermService.php:176-191
- `_index/requests.md` TermRequest
- app/Models/Term.php:12, :24-72, :122-146
- resources/views/admin/terms/form.blade.php · index.blade.php:35-36 · history.blade.php:22-23
- `_index/schema.md` terms (마이그레이션 2026_09_08_000098 · 2026_10_02_000182 · 2026_10_23_000262)
- 프로토타입: prototype_clean/ADMN-CONF-002_baseline.html:409-1878 (digest 기준)
