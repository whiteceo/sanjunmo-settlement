# ADMN-BRD-001 공지사항 · FAQ · Q&A · 당첨자 통합 관리 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-BRD-001_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: a8016168 (2026-10-27) — d562524a 이후 이 화면 변경은 상품 Q&A 상세 주문 연결 칸(d235b739)뿐
- 포함 화면: ADMN-BRD-001 · 001-S1(공지), ADMN-BRD-006 · 006-S1(FAQ), ADMN-BRD-003 · 003-S1(상품 Q&A), ADMN-BRD-004 · 004-S1(학습 Q&A), ADMN-BRD-009 · 009-S1(당첨자 발표)
- 개발 진행: 구현(다섯 화면 모두 개발 라우트 · 컨트롤러 · 뷰 있음). 담당 이응민(`config/dev-progress.php`). BRD-009 는 progress 표에 "완료 9ec6059 · 1a92439 · ed10474"
- 구조 차이 요지: 프로토타입은 한 HTML 안 탭 5개(`switchTab('notice'|'faq'|'pqna'|'qna'|'winner')`) + 하위 화면 SJM_PAGE 페이지. 개발은 화면마다 별도 메뉴 · 별도 URL, 하위 화면(S1)도 별도 페이지(create/edit/show)다.

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.notices.index` | 공지사항 관리 | 뷰 `@adminCan('admin.notices.index', …)` (resources/views/admin/notices/index.blade.php:82-90). 메뉴 행 데이터는 저장소에 없음(DB) — 라우트 정규화 규칙 기준 |
| `admin.faqs.index` | FAQ 관리 | 라우트 정규화. FAQ 카테고리(`admin.faqs.categories.*`)는 별도 메뉴가 없으면 FAQ 메뉴로 폴백(routes/admin.php:763 주석) |
| `admin.product-qnas.index` | 상품 Q&A 관리 | 라우트 정규화 |
| `admin.study-qnas.index` | 학습 Q&A 관리 | 라우트 정규화. 강사 · 조교는 담당 범위만(study_qnas.instructor_id · assign_ta_id) |
| `admin.winners.index` | 당첨자 발표 관리 | progress 표 "메뉴 107 · 000208 적용 확인" |

- 권한은 라우트 이름 접미사로 판정(5축 조회 · 등록 · 수정 · 삭제 · 다운로드). 이 화면 라우트 중 ROUTE_PERMISSIONS 예외는 없다(app/Services/Admin/AdminPermissionService.php:358-367).

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`).

### ADMN-BRD-001 공지사항 관리 / 001-S1 공지사항 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/notices` | `admin.notices.index` | 조회 | NoticeController@index |
| 등록 폼(S1) | GET | `/{admin}/notices/create` | `admin.notices.create` | 등록 | NoticeController@create |
| 등록 저장 | POST | `/{admin}/notices` | `admin.notices.store` | 등록 | NoticeController@store |
| 선택 숨김 | PUT | `/{admin}/notices/status` | `admin.notices.status.update` | 수정 | NoticeController@bulkHide |
| 선택 삭제(소프트) | DELETE | `/{admin}/notices/selected` | `admin.notices.selected.destroy` | 삭제 | NoticeController@bulkDelete |
| 수정 폼(S1) | GET | `/{admin}/notices/{notice}/edit` | `admin.notices.edit` | 수정 | NoticeController@edit |
| 수정 저장 | PUT | `/{admin}/notices/{notice}` | `admin.notices.update` | 수정 | NoticeController@update |
| 단건 삭제 | DELETE | `/{admin}/notices/{notice}` | `admin.notices.destroy` | 삭제 | NoticeController@destroy |

### ADMN-BRD-006 FAQ 관리 / 006-S1 FAQ 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/faqs` | `admin.faqs.index` | 조회 | FaqController@index |
| 등록 폼(S1) | GET | `/{admin}/faqs/create` | `admin.faqs.create` | 등록 | FaqController@create |
| 등록 저장 | POST | `/{admin}/faqs` | `admin.faqs.store` | 등록 | FaqController@store |
| 선택 노출 전환 | PUT | `/{admin}/faqs/status` | `admin.faqs.status.update` | 수정 | FaqController@updateVisibility |
| 선택 카테고리 이동 | PUT | `/{admin}/faqs/category` | `admin.faqs.category.update` | 수정 | FaqController@updateCategory |
| 카테고리 추가 | POST | `/{admin}/faqs/categories` | `admin.faqs.categories.store` | 등록 | FaqController@storeCategory |
| 카테고리 삭제 | DELETE | `/{admin}/faqs/categories/{faqCategory}` | `admin.faqs.categories.destroy` | 삭제 | FaqController@destroyCategory |
| 수정 폼(S1) | GET | `/{admin}/faqs/{faq}/edit` | `admin.faqs.edit` | 수정 | FaqController@edit |
| 수정 저장 | PUT | `/{admin}/faqs/{faq}` | `admin.faqs.update` | 수정 | FaqController@update |
| 삭제 | DELETE | `/{admin}/faqs/{faq}` | `admin.faqs.destroy` | 삭제 | FaqController@destroy |

### ADMN-BRD-003 상품 Q&A 관리 / 003-S1 상품 Q&A 답변 등록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(탭 `?tab=`) | GET | `/{admin}/product-qnas` | `admin.product-qnas.index` | 조회 | ProductQnaController@index |
| 담당자 일괄 지정 | PUT | `/{admin}/product-qnas/assignees` | `admin.product-qnas.assignees.update` | 수정 | ProductQnaController@bulkAssign |
| 상세 · 답변(S1) | GET | `/{admin}/product-qnas/{productQna}` | `admin.product-qnas.show` | 조회 | ProductQnaController@show |
| 처리(답변 · 숨김 · 비밀글) | PUT | `/{admin}/product-qnas/{productQna}` | `admin.product-qnas.update` | 수정 | ProductQnaController@update |
| 알림 재발송 | PUT | `/{admin}/product-qnas/{productQna}/notifications/{notificationLog}` | `admin.product-qnas.notifications.update` | 수정 | ProductQnaController@resendNotification |

### ADMN-BRD-004 학습 Q&A 관리 / 004-S1 질문 상세 · 답변
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/study-qnas` | `admin.study-qnas.index` | 조회 | StudyQnaController@index |
| 상세 · 답변(S1) | GET | `/{admin}/study-qnas/{studyQna}` | `admin.study-qnas.show` | 조회 | StudyQnaController@show |
| 처리(답변 · 강사 확인 요청) | PUT | `/{admin}/study-qnas/{studyQna}` | `admin.study-qnas.update` | 수정 | StudyQnaController@update |
| 알림 재발송 | PUT | `/{admin}/study-qnas/{studyQna}/notifications/{notificationLog}` | `admin.study-qnas.notifications.update` | 수정 | StudyQnaController@resendNotification |
| 회원 첨부 받기 | GET | `/{admin}/study-qnas/{studyQna}/files/{file}` | `admin.study-qnas.files.show` | 조회 | StudyQnaController@file |
| 본문 이미지(secure) | GET | `/{admin}/study-qnas/{studyQna}/images/{name}` | `admin.study-qnas.images.show` | 조회 | StudyQnaController@image |

### ADMN-BRD-009 당첨자 발표 관리 / 009-S1 당첨자 발표 등록 · 수정
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 | GET | `/{admin}/winners` | `admin.winners.index` | 조회 | WinnerController@index |
| 등록 폼(S1) | GET | `/{admin}/winners/create` | `admin.winners.create` | 등록 | WinnerController@create |
| 등록 저장 | POST | `/{admin}/winners` | `admin.winners.store` | 등록 | WinnerController@store |
| 선택 숨김 | PUT | `/{admin}/winners/status` | `admin.winners.status.update` | 수정 | WinnerController@bulkHide |
| 명단 엑셀 양식 | GET | `/{admin}/winners/template/download` | `admin.winners.template.download` | 다운로드 | WinnerController@template |
| 수정 폼(S1) | GET | `/{admin}/winners/{winner}/edit` | `admin.winners.edit` | 수정 | WinnerController@edit |
| 수정 저장 | PUT | `/{admin}/winners/{winner}` | `admin.winners.update` | 수정 | WinnerController@update |

## 3. 폼 필드 · 검증
### 공지 등록 · 수정 `noticeForm` (NoticeRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `title` | required · string · max:100 | | `notice-form-title` 공지 제목 |
| `content` | required · string (저장 시 Purifier) | 에디터 `admin.inc.editor`(type=notices) | `notice-form-body`(contenteditable) |
| `device_pc` / `device_mobile` | 둘 중 하나 required_without · boolean | 저장값 device_scope `all`(공통) · `pc`(PC만) · `mobile`(모바일만) | 없음 |
| `publish_mode` | required · in:immediate,scheduled,draft | immediate=즉시 발행 · scheduled=예약 발행 · draft=임시 저장 | `notice-form-visible`(즉시 노출 체크) — 끄면 숨김 저장 |
| `published_at` | required_if:publish_mode,scheduled · date. 과거 시각 거부(서비스) | datetime-local `publishedAt` step 300 | 없음 |
| `started_at` / `ended_at` | nullable date · ended_at after_or_equal:started_at. 종료일은 그날 23:59:59 로 저장 | | 없음 |
| `is_pinned` | nullable boolean. 고정 최대 5건(Post::PIN_MAX, 서비스 검증) | | `notice-form-pin` 상단 고정 공지 |
| `pin_order` | nullable integer 1~5. 비우면 맨 뒤 | | 없음 |
| `allow_comment` | nullable boolean | | 없음 |
| `attachments[]` | array max:5 · 개당 10MB · jpg,jpeg,png,pdf,hwp,zip(실제 바이트 검사). 기존 + 새 파일 합계 5개(서비스) | | 없음(목록 "첨부파일" 열만 있음) |
| `delete_attachments[]` | integer | 지울 첨부 id | 없음 |
| `list_query` | hidden | 저장 후 돌아갈 목록 조건 | 없음 |
| (없음) | | 게시판은 code=notice 하나로 고정, 분류 선택 없음(NoticeService prepare) | `notice-form-cat` 공지 분류(일반공지 · 시험일정 · 시스템점검) |

### 공지 일괄 처리 `bulkForm` (컨트롤러 인라인 검증)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `ids[]` | required array min:1 · integer | 선택 숨김 → PUT status, 선택 삭제 → DELETE selected(`bulkMethod` 값 교체) | 없음(행 단위 `toggleNoticePin` 만) |

### FAQ 등록 · 수정 `faqForm` (FaqRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `category_id` | required integer · faq_categories 존재 | | `faq-form-cat` |
| `weight` | required integer 0~999 (클수록 위) | | `faq-form-top`(자주 찾는 질문 TOP 고정 체크) — 의미 다름 |
| `question` | required string max:100 | | `faq-form-q` |
| `answer` | required string(에디터) | | `faq-form-a` |
| `is_visible` | required boolean | | `faq-form-visible` 프론트 노출 |

### FAQ 일괄 `bulkForm` (FaqBulkRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `ids[]` | required array 1~200(FaqService::MAX_BULK) | | 없음 |
| `is_visible` | status.update 일 때 required boolean | | 없음 |
| `category_id` | category.update 일 때 required · 존재 | | 없음 |

### FAQ 카테고리 추가 (FaqCategoryRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `name` | required string max:50 | `new-faq-cat-name` |
| `sort_order` | nullable integer min:0 | ▲▼ `moveFaqCat` |
| `is_active` | nullable boolean | `toggleFaqCatVisible` |

### 상품 Q&A 처리 `processForm` (ProductQnaProcessRequest) · 일괄 지정 `bulkAssignForm` (ProductQnaBulkAssignRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `action` | required in:answer,hide,secret (`actionField`) | answer=답변 등록 · hide=숨김 · secret=비밀글 전환 | 버튼 `savePqnaAnswer` · `hidePqna` |
| `answer_content` | required_if:action,answer · min:10 | | `pqna-modal-answer` |
| `assign_dept` | nullable in ProductQna::ASSIGN_DEPTS | logistics=물류팀 · ta=조교 · cs=CS | `pqna-modal-owner`(SJM_MASTER 역할 그룹) |
| `is_secret` | nullable boolean | | `pqna-modal-open`(공개/비밀글) |
| `ids[]` · `assign_user_id` | 일괄: required · integer (담당자 = 사람) | | `pqna-bulk-owner`(부서) — 대상 다름 |

### 학습 Q&A 처리 `processForm` (StudyQnaProcessRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `action` | required in:answer,escalate | answer=답변 등록 · escalate=강사 확인 요청 | `saveLqnaAnswer` |
| `answer_content` | required_if:action,answer · min:10 | | `lqna-answer` |
| `is_public_qna` | nullable boolean | 공개 Q&A 전환 | 없음 |
| `notify` | nullable boolean(기본 ON) | 답변 알림 | 없음 |
| (없음) | | | `lqna-role` 처리 역할 그룹(시연용) |

### 당첨자 발표 등록 · 수정 `winnerForm` (WinnerRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `promotion_id` | required integer (이벤트 1:1) | `promotionSelect` | `winpost-event-code` |
| `title` | required string max:100 | `titleInput` | `winpost-title` |
| `content` | nullable string | | 본문 + `insertWinnerTemplateText` |
| `publish_mode` | required in:immediate,scheduled | immediate=즉시 · scheduled=예약 | `winpost-status`(즉시 · 예약 · 임시저장) |
| `published_at` | required_if:publish_mode,scheduled · date | `publishedAt` | `winpost-date` |
| `winners_text` | nullable string max:200000 (줄마다 아이디 · 경품) | 저장 시 회원 아이디 대조 → 마스킹 값만 저장 | `winrow-*` 행 추가 폼. v6.92: `winrow-member`(아이디 또는 회원번호 — 회원번호 입력은 (규칙)) + [회원 원장 조회] `previewWinnerMember()`(개발 별도 조회 라우트 없음, 저장 시 대조) |
| `winners_file` | nullable xlsx max 2MB(실제 바이트 검사) | 양식 `admin.winners.template.download` | "엑셀 추가" 라벨만 |
| `list_query` | hidden | | 없음 |

## 4. 목록 필터 · 정렬 · 표 컬럼
### 공지 목록 (NoticeController@index:28-58, NoticeRepository::buildQuery:176-205)
- 필터(쿼리 파라미터): `status`(published 게시중 · scheduled 예약 발행 · ended 종료 · hidden 숨김 · draft 임시 저장) · `pinned`(1/0) · `device_scope`(all/pc/mobile) · `date_from` · `date_to`(등록일) · `keyword`(제목+본문) · `author`(작성자 login_id) · `per_page`(20/50/100).
- 기본: 필터가 없으면 등록일 최근 90일. 임시 저장 글은 작성자 본인에게만 보인다.
- 정렬: is_pinned desc → pin_order → created_at desc (NoticeRepository:53-55).
- 표 컬럼(개발): 선택 · 번호(고정은 📌) · 제목 · 노출 기기 · 상단 고정(`고정 N순위`) · 게시 기간 · 조회수 · 상태 · 관리.
- 표 컬럼(프로토타입): 번호/고정 · 분류 · 제목 · 첨부파일 · 조회수 · 노출상태 · 등록일 · 관리. 필터는 `notice-cat-filter` · `notice-keyword`.

### FAQ 목록 (FaqController@index:23-40)
- 필터: `category_id` · `keyword`(질문만 검색) · `per_page`. 정렬 weight desc → id desc (FaqRepository:21-22).
- 표 컬럼(개발): 선택 · No · 카테고리 · 질문 · 가중치 · 노출 · 최종 수정 · 관리. 프로토타입: 노출순서 · FAQ 카테고리 · 질문 · 자주 찾는 TOP · 노출상태 · 최종 수정일 · 관리.

### 상품 Q&A 목록 (ProductQnaController@index:26-62)
- 필터: `product_type`(book 교재 · course 강좌 · package 패키지) · `product_id` · `inquiry_type` · `assign_dept` · `status`(pending 미답변 · answered 답변완료 · hidden 숨김) · `is_secret` · `date_from` · `date_to` · `keyword` · `per_page`.
- 탭 `tab`: all 전체 · book 교재 · course 강좌 · package 패키지 · pending 미답변 (페이지 이동, 탭별 건수).
- 표 컬럼(개발): 문의일 · 구분 · 상품(자동 매핑) · 제목 · 회원 · 담당 · 공개 · 상태 · 처리. 프로토타입은 여기에 선택 · 첨부 열.

### 학습 Q&A 목록 (StudyQnaController@index:29-50)
- 필터: `course_id` · `status`(pending 미답변 · answered 답변완료 · escalated 강사확인) · `date_from` · `date_to` · `mine`(1) · `keyword`. 정렬 created_at desc.
- 표 컬럼(개발): 질문일 · 질문한 강의 · 제목 · 수강생 · 진도율 · 담당 조교 · 상태 · 처리. 프로토타입: 질문번호 · 대상 강좌/담당 강사 · 강의 타임스탬프 · 질문 제목 · 작성 수강생 · 답변상태 · 관리.

### 당첨자 발표 목록 (WinnerController@index:30-48)
- 필터: `promotion_id` · `status`(published 게시중 · scheduled 예약 발행 · hidden 숨김) · `date_from` · `date_to` · `keyword`. 정렬 published_at desc → id desc.
- 표 컬럼(개발): 선택 · 번호 · 제목 · 연결 이벤트 · 당첨 인원 · 발표일 · 상태 · 관리. 프로토타입: 발표 번호 · 연결 이벤트 · 제목 · 발표 상태 · 발표일 · 노출 위치 · 당첨자/지급 · 관리.

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| boards.code | string(50) unique | 게시판 코드. `notice` = 공지, `winner` = 당첨자 발표, `event…` = 이벤트 | 공지 · 당첨자 글의 소속(선택 UI 없음) |
| posts.board_id | bigint | 소속 게시판 | — |
| posts.title / content | string(255) / longText | 제목 · 본문(Purifier) | 공지 · 당첨자 제목/본문 |
| posts.author_id | bigint | 작성 관리자 users.id | 공지 작성자 검색(login_id) |
| posts.device_scope | string(10) | all 공통 · pc PC만 · mobile 모바일만 | 노출 기기 |
| posts.status | string(20) | draft 임시 저장 · scheduled 예약 발행 · published 게시중 · hidden 숨김 (저장값) | 상태 |
| (계산) display_status | — | 저장값 + 기간으로 published · scheduled · ended(종료) · hidden · draft (Post::DISPLAY_STATUSES) | 목록 상태 열 |
| posts.published_at | dateTime | 발행(예약) 시각 | 예약 시각 · 발표일 |
| posts.started_at / ended_at | dateTime | 게시 기간(종료 NULL=무기한) | 게시 기간 |
| posts.is_pinned / pin_order | tinyint / int | 상단 고정 · 순위(최대 5) | 상단 고정 |
| posts.allow_comment | tinyint | 댓글 허용 | 게시 설정 |
| posts.view_count | int | 조회수 | 조회수 |
| posts.promotion_id | bigint | 당첨자 발표 ↔ 이벤트 1:1 | 연결 이벤트 |
| posts.deleted_at | timestamp nullable (SoftDeletes, 2026_09_08_000086) | 소프트 삭제(Post 모델 `use SoftDeletes`) | — |
| attachments.* | attachable_type/id · original_name · file_path · disk(media) · size | 공지 첨부(저장명 UUID, `notices/{id}/`) | 첨부파일 |
| post_winners.seq / masked_name / masked_login / prize | | 당첨자 명단 — 마스킹 값만 저장(원본 미저장) | 당첨자 명단 |
| (규칙) post_winners.member_id | bigint | v6.92 S-17: 프로토타입 명단 행의 `memberNo`(내부 키, 화면 비표시) — 지급 · 연락 때 회원 원장 조회용. 개발 컬럼 없음(개발은 마스킹 값만) | 당첨자 명단(비표시) |
| faq_categories.name / sort_order / is_active | string(50) / int / tinyint | FAQ 카테고리(하위 FAQ 있으면 삭제 불가) | 카테고리 팝업 |
| faqs.category_id / question(100) / answer / weight(0~999) / is_visible / admin_id / view_count / updated_at | | FAQ | FAQ 목록 · 폼 |
| product_qnas.product_type / product_id / order_id / inquiry_type / title / content / assign_dept / assign_user_id / is_secret / status / answer_content / answered_by / answered_at / deleted_at | | 상품 Q&A. inquiry_type: composition 상품 구성 · price 가격·할인 · delivery 배송 · period 수강 기간 · etc 기타(패키지만), 옛 값 damage · erratum · stock · course | 상품 Q&A 목록 · 답변 |
| (계산값) `purchase` | — | 003-S1 주문 연결 = `order_items` ⨝ `orders`(`paid_at` 있음) ⟕ `deliveries`(`order_item_id`) 중 그 회원 · 그 상품(`product_type` · `product_id`)의 가장 최근 결제 주문 → `order_id` · `order_no` · 라벨 `MM.DD 배송 상태`(교재: `deliveries.delivered_at` → `shipped_at`, 라벨 `Delivery::STATUS_LABELS`) 또는 `MM.DD 결제`(강좌 · 패키지). 문의에 `order_id`가 있으면 그 주문 안에서 먼저 찾고 없으면 전체 구매 이력에서 다시 찾는다. 없으면 '구매 전 문의' — `ProductQnaRepository.php:125-143`, `ProductQnaService.php:69-91`, `product-qnas/show.blade.php:30-39`(d235b739) | 003-S1 주문 연결 |
| study_qnas.course_id / lecture_id / play_position_sec / instructor_id / assign_ta_id / title / content / status / answer_content / answered_by / answered_at / is_public_qna / is_secret / view_count | | 학습 Q&A. SLA 48h(StudyQna::SLA_HOURS) | 학습 Q&A 목록 · 상세 |
| notification_logs.target_type | string(30) | 알림 대상(product_qna · study_qna 등) — 발송 이력 · 재발송 | 상세 하단 발송 이력 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `noticeForm` | 공지 등록 · 수정 폼(enctype multipart) | 서브페이지 `data-subpage="notice-form"` |
| `publishedAt` · `toggleSchedule()` | 예약 시각 입력 · 예약일 때만 활성 | 없음 |
| `bulkForm` · `bulkMethod` · `submitBulk('hide'/'delete')` · `toggleAll()` | 공지 목록 일괄 숨김 · 삭제 | 없음 |
| `nt-row--saved` | 방금 저장한 행 강조 | 없음 |
| beforeunload 확인(noticeForm dirty · tinymce) | 저장 안 하고 나가기 확인 | 없음 |
| `faqForm` · `faqCategory` · `faqWeight` · `faqQuestion` · `faqQuestionCount` | FAQ 폼 | `faq-form-*` |
| `bulkForm` · `bulkVisible` · `bulkCategory` · `filter_category_id` · `filter_keyword` | FAQ 목록 일괄(노출 · 카테고리 이동) | 없음 |
| `processForm` · `actionField` | 상품/학습 Q&A 처리 폼(action 값 교체 제출) | `pqna-answer` · `lqna-detail` 서브페이지 |
| `bulkAssignForm` | 상품 Q&A 담당자 일괄 지정 | `bulkAssignPqna()` |
| 주문 연결 칸 `a.link--view` → `admin.orders.show`(새 탭, `target="_blank"`) · '구매 전 문의' | 003-S1 주문 연결 | `#pqna-modal-order`(`주문 연결: 주문번호 · 배송 상태` / `구매 전 문의`, 프로토 L2536) |
| `winnerForm` · `promotionSelect` · `titleInput` · `publishedAt` | 당첨자 발표 폼 | 서브페이지 `winner-form`(`winpost-*`) |
| `hideForm` | 당첨자 발표 선택 숨김 | 없음 |
| `admin.inc._notify-history` | 알림 발송 이력 · 재발송 공용 조각 | 없음 |
| 공통 클래스 `search__table` · `table__list` · `btn__small btn--basic` · `btn--save` · `input__text` · `fm-help` · `text--warning` | 개발 공통 | — |

하위 화면 표현: 개발은 S1 모두 별도 페이지(create/edit/show 라우트). 프로토타입은 SJM_PAGE 서브페이지(`notice-form` · `faq-form` · `pqna-answer` · `lqna-detail` · `winner-form`)이고 FAQ 카테고리만 모달(`modal-faq-cat`). 개발 FAQ 카테고리는 목록 화면 안 인라인 폼(`name` 입력 + 삭제 버튼).

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 공지: 노출 기기(PC · 모바일), 발행 방식 3택(즉시 · 예약 · 임시 저장) + 예약 시각, 게시 기간, 고정 순서, 댓글 허용, 첨부(최대 5개), 선택 숨김 · 선택 삭제, 상태 필터(게시중 · 예약 · 종료 · 숨김 · 임시) · 고정 · 기기 · 작성자 검색, 저장 후 목록 조건 유지(`list`/`list_query`).
- FAQ: 가중치(0~999) 정렬, 선택 노출 전환 · 선택 카테고리 이동.
- 상품 Q&A: 상품 구분 탭(전체 · 교재 · 강좌 · 패키지 · 미답변), 비밀글 전환(action=secret), 알림 재발송.
- 학습 Q&A: 강사 확인 요청(escalate), 공개 Q&A 전환, 답변 알림 on/off, 진도율 · 담당 조교 열, 내 담당(`mine`), 첨부 · 본문 이미지 보호 경로.
- 당첨자 발표: 명단 엑셀 업로드(xlsx) + 양식 다운로드, 저장 시 회원 아이디 대조 · 마스킹 저장, 선택 숨김.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 공지 분류(일반공지 · 시험일정 · 시스템점검 · 당첨자발표 연동) 선택 · 필터 · 열.
- 공지 목록 행의 상단 고정/해제 즉시 토글(`toggleNoticePin`).
- FAQ "자주 찾는 질문 TOP" 고정, 카테고리 이름 변경 · 순서 ▲▼ · 노출 토글(개발은 추가 · 삭제만, sort_order · is_active 는 추가 때만 받음).
- 상품 Q&A 엑셀 다운로드, 선택 숨김 일괄.
- 당첨자 경품 지급 관리 전체: 경품 유형(포인트 · 기프티콘 · 실물), 지급 상태 · 지급일시 · 송장번호, 개별 즉시 지급 · 일괄 지급, 노출 위치(이벤트 탭 · 공지사항 상단) 선택, 발표 시 당첨자 개별 알림톡, 임시저장 발표 상태, 원본 이름 · 휴대폰 입력(개발은 원본 미저장). **→ 결정(v6.92 white, S-17)**: 원본 이름 · 아이디 · 휴대폰 입력 · 저장 삭제, 명단은 회원번호 + 마스킹 값(`maskedName` · `maskedLogin`)만 — 개발 post_winners 마스킹 저장과 같아짐(경품 지급 관리는 그대로 프로토타입에만)

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 공지 노출: 프로토타입 `notice-form-visible`(즉시 노출 on/off → 숨김) → 개발 `publish_mode`(immediate/scheduled/draft). 숨김은 목록 일괄 숨김으로만 된다.
- 상품 Q&A 문의 유형: 프로토타입 파손/오배송 · 배송문의 · 오탈자 · 재고 · 강좌 수강 → 개발 현재 값 composition · price · delivery · period · etc(패키지만), 프로토타입 값은 개발에서 옛 값(LEGACY_INQUIRY_TYPES)이다.
- 상품 Q&A 담당: 프로토타입은 SJM_MASTER 역할 그룹 → 개발 `assign_dept` logistics · ta · cs, 일괄 지정은 부서가 아니라 담당자(`assign_user_id`).
- 상품 Q&A 003-S1 주문 연결: 프로토 `#pqna-modal-order`(주문번호 · 배송 상태, 구매 이력 없으면 '구매 전 문의', L2536)와 같은 내용으로 맞춤(a8016168에서 개발 구현, d235b739) — 전에는 개발이 `주문 #id` / '연결 없음'만 보였다. 개발은 주문번호를 주문 상세 새 탭 링크로 둔다.
- 상태 코드: 상품 Q&A pending/answered/hidden, 학습 Q&A pending/answered/escalated (프로토타입 스크립트의 `WAITING` 등 대문자 코드 → 개발 소문자).
- 당첨자 발표 발표 상태: 프로토타입 3택(즉시 · 예약 · 임시저장) → 개발 2택(immediate · scheduled), 목록 상태 published · scheduled · hidden.
- 화면 단위: 프로토타입 탭 하나 화면 → 개발 메뉴 5개(`notices` · `faqs` · `product-qnas` · `study-qnas` · `winners`).

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_BRD.md` 의 D-BRD 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 공지 분류(일반공지 · 시험일정 · 시스템점검)를 둘지 확인 필요 — 개발은 분류 없이 공지 게시판 하나로 확정(NoticeService::prepare 주석 "ADMN-BRD-001-S1 ① 구분 선택 없음"). **→ 정책 아님(POLICY_D_BRD B)**: 화면 · 이름 문제로 처리 — 개발대로 분류 없음, 점검 공지는 상단 고정 + 제목으로 구분
- 당첨자 경품 지급(포인트 · 기프티콘 · 실물 송장)을 BRD-009 에서 처리할지 확인 필요 — 개발은 발표 · 마스킹 명단만, 원본 이름 · 연락처를 저장하지 않는다(PostWinner 주석 · DECISIONS #72). **→ 결정(v6.92 white, S-17)**: 명단 저장은 개발처럼 회원번호 + 마스킹 값만, 알림톡 · 배송 연락은 지급 때 회원번호로 회원 원장 조회(경품 지급을 BRD-009에서 할지는 이 결정 범위 밖) · 경품 지급 원장 자체는 **→ 정본대로(POLICY_D_BRD A, 통합설계서 L408)**: BRD-009가 경품(포인트 · 기프티콘 · 실물) 지급 원장 — 개발팀 전달(경품 유형 · 지급 상태 · 송장 추가, 연락처 · 주소는 회원 정보에서)
- FAQ "자주 찾는 TOP 고정"과 개발 가중치(weight) 정렬의 관계 확인 필요. **→ 정책 아님(POLICY_D_BRD B)**: 화면 · 이름 문제로 처리 — 개발 weight 하나로 정렬, 'TOP'은 weight 상위 N개 표시(별도 플래그 없음)
- 상품 Q&A 문의 유형 체계(프로토타입 5종 vs 개발 composition 등 5종 + 옛 값) 확인 필요. **→ 정본대로(POLICY_D_BRD A, 통합설계서 L431)**: 유형에 '파손/오배송' · '오탈자/내용 오류'가 있어야 함(개발팀 전달 — 현재 값으로 되살림), 나머지 유형 이름은 개발 이름 사용(B)

## 출처
- routes/admin.php:677-768, 795-814 (dev_spec/_index/routes.md 줄 번호)
- app/Http/Controllers/Admin/NoticeController.php:14, 28-58, 70-118, 152-186
- app/Http/Requests/Admin/NoticeRequest.php:22-50
- app/Services/Admin/NoticeService.php:22, 148-206, 218-245
- app/Repositories/Admin/NoticeRepository.php:40-43, 53-55, 176-205
- app/Models/Post.php:13-45, 47-77
- app/Http/Controllers/Admin/FaqController.php:23-40, 108-133 · app/Http/Requests/Admin/FaqRequest.php · FaqBulkRequest.php · FaqCategoryRequest.php · app/Services/Admin/FaqService.php:18 · app/Repositories/Admin/FaqRepository.php:21-22, 115-116
- app/Http/Controllers/Admin/ProductQnaController.php:26-62, 104-115 · app/Http/Requests/Admin/ProductQnaProcessRequest.php · ProductQnaBulkAssignRequest.php · app/Models/ProductQna.php:14-47
- app/Http/Controllers/Admin/StudyQnaController.php:29-50, 103 · app/Http/Requests/Admin/StudyQnaProcessRequest.php · app/Models/StudyQna.php:15-22
- app/Http/Controllers/Admin/WinnerController.php:16-48, 78-103 · app/Http/Requests/Admin/WinnerRequest.php · app/Services/Admin/WinnerService.php:88-230 · app/Models/PostWinner.php:9 · app/Repositories/Admin/WinnerRepository.php:30-31
- app/Services/Admin/AdminPermissionService.php:358-367
- resources/views/admin/notices/index.blade.php:75-140, 148-169 · notices/form.blade.php:19-159 · faqs/* · product-qnas/* · study-qnas/* · winners/*
- database: dev_spec/_index/schema.md posts · attachments · boards · faqs · faq_categories · product_qnas · study_qnas · post_winners
- 프로토타입: prototype_clean/ADMN-BRD-001_baseline.html:830-856(탭), 870-1240(목록), 1249-1570(서브페이지), 1570-1630(modal-faq-cat)
