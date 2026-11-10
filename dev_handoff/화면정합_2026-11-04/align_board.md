# 화면 정합 비교 — 게시판 · 사이트 · 관리자 그룹 (2026-11-04)

- 기준: `prototype_dev/*_baseline.html`(줄 번호는 prototype_dev 기준) ↔ 개발 `D:\Work\sanjunmo` dev `94aa56ac` `resources/views/admin/…`
- 이미 결정된 정책은 다시 묻지 않고 근거로 썼다: `findings/devspec/DEV_DECISIONS_2026-10-27.md`(D-·S- 번호), `findings/devspec/POLICY_D_BRD.md` · `POLICY_D_CONF.md`의 "질문이 아닌 것"(A = 정본대로 개발팀 전달, B = 권고대로), `PROJECT_STATE.md` 1절.
- "기존 전달"이라고 적은 항목은 10-27에 이미 개발팀에 넘긴 것인데, 11-03 코드에 아직 반영되지 않은 것을 확인한 것이다.

## 공통 (여러 화면에 같은 원인)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| COM-1 | 1 적용 | 화면만 | 목록 | 텍스트 입력 칸에 `input__text`가 없다. `admin.css`의 `input[type=text]{border:none}` 때문에 테두리 없이 placeholder 글자만 남아 입력 칸이 아니라 안내 문구처럼 보인다(스크린숏 `_admin_logs.png`의 '대상 회원' · '접속 IP'). 날짜 칸은 dev-skin이 `input[type=date]`를 직접 칠해 문제없다 | CONF-010 `#dateFrom` 주변 필터(L314~435)는 모두 테두리 칸 | `admin-logs/index.blade.php:229`(target_member) · `:242`(ip), `login-logs/index.blade.php:142`(ip) | 이력/보안 로그 · 로그인 로그 검색 영역에서 '대상 회원' · '접속 IP'가 다른 칸처럼 테두리가 있는 입력 칸으로 보이는지 |
| COM-2 | 1 적용 | 화면만 | 목록 | 상태 열이 글자만 있고 배지가 없다(공지 노출상태 · 1:1 문의 처리 상태 · 학습 Q&A · 당첨자 · 후기 · 문의 분류 · 배너 · 메시지 템플릿 · 권한 그룹). 프로토는 상태마다 색 배지. 상태 값은 그대로 두고 `badge badge--soft badge--{상태 class}`로 감싼다(색 대응은 `design_kit/CLASS_MAP.md` 6절) | BRD-001 `renderNotices` L1969~(노출중 green · 비노출 slate) 등 | `notices/index.blade.php:126` · `inquiries/index.blade.php:166` · `study-qnas/index` · `winners/index` · `reviews/index` · `inquiry-categories/index` · `display/index` · `message-templates/index` · `admin-roles/index`(`badge` 사용 0회) | 각 목록 상태 열이 알약 배지로 보이는지(숨김 · 임시 저장 · 종료는 회색) |
| COM-3 | 1 적용 | 화면만 | 목록 | 처리 현황 카드가 `btn__small btn--basic` 버튼 줄이다. 프로토는 KPI 카드(제목 · 큰 숫자 · 보조 문구). `COMPONENTS.md` `.kpi-grid > .kpi-card`로 바꾸고 링크(`$card['query']`)는 유지 | BRD-002 L508~532 `kpi-card` | `inquiries/index.blade.php:23~31`, `reviews/index.blade.php:24~`(스코어 카드) | 1:1 문의 · 후기 목록 맨 위가 카드 4~5개로 보이고 누르면 같은 필터로 이동하는지 |

## ADMN-BRD-001 공지사항 (+ FAQ · 상품 Q&A · 학습 Q&A · 당첨자 · 게시판)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| BRD-001-1 | 2 유지 | — | 목록 · 등록 | 프로토의 공지 '분류'(일반 · 시험일정 · 정정 등) 필터 · 열 · 폼 칸이 개발에 없다. 결정: 분류 없이 개발대로(POLICY_D_BRD "질문이 아닌 것" BRD-001 B, 프로토에서 지울 대상) | L881 `notice-cat-filter`, L1271 `notice-form-cat`(proto-only) | `notices/index.blade.php` · `form.blade.php` | — |
| BRD-001-2 | 1 적용 | 화면만 | 목록 | 공지 목록에 '등록일' · '첨부' 열이 없다. 개발은 노출 기기 · 상단 고정 · 게시 기간을 더 보여 줘 그대로 두고, 첨부 수(📎 n)와 등록일만 더한다. `attachments`는 이미 관계가 있다(form에서 사용) | th L917 | `notices/index.blade.php:102` · 행 `:110~133` | 공지 목록에 첨부 수 · 등록일 열이 보이는지 |
| BRD-001-3 | 2 유지 | — | 등록 | 등록 폼 구성은 같다(제목 · 노출 기기 · 발행 3택 · 예약 시각 · 상단 고정 · 본문). 개발이 게시 기간 · 고정 순서 · 댓글 · 첨부를 더 갖고 있어 개발이 낫다 | L1262~1320 | `notices/form.blade.php:27~116` | — |
| BRD-001-4 | 1 적용 | 화면만 | 목록 · 등록 | FAQ '자주 찾는 질문 TOP' 표시가 없다. 결정: 별도 플래그 없이 weight 상위 N개를 TOP으로 표시(POLICY_D_BRD B). 목록 '가중치' 열 옆에 TOP 배지만 붙인다 | L1339 `faq-form-top`, th L995 '자주 찾는 TOP' | `faqs/index.blade.php:159` | FAQ 목록에서 가중치 상위 건에 TOP 배지가 보이는지 |
| BRD-001-5 | 2 유지 | — | 상세 | 상품 Q&A · 학습 Q&A 답변을 프로토는 모달, 개발은 별도 페이지(show)로 연다. 본문 · 첨부 · 기존 답변 · 주문 연결까지 한 화면에 있어 페이지가 맞다(PAGE_PATTERN 기준: 첨부 · 이력이 있으면 페이지). 담당자 개인 지정(`assign_user_id`)도 개발에만 있어 개발이 낫다 | modal-pqna L1579, modal-lqna L1624 | `product-qnas/show.blade.php` · `study-qnas/show.blade.php` | — |
| BRD-001-6 | 1 적용 | 기능 수정 | 목록 · 상세 | 상품 Q&A 문의 유형에 '파손/오배송' · '오탈자/내용 오류'가 현재 값에 없다(옛 값 `damage` · `erratum`은 `LEGACY_INQUIRY_TYPES`에만). 정본 L431의 파손 다발 경고 · 정정 공지 규칙이 이 두 유형을 전제로 한다(기존 전달 POLICY_D_BRD 개발팀 전달 2번). 영향: `ProductQna::INQUIRY_TYPES`에 두 값을 현재 값으로 올리고 사용자 작성 화면 선택지에도 반영, 기존 행은 그대로 읽힘(마이그레이션 없음) | L1060 `pqna-type`, ctx-note `pqna-modal-damage` · `pqna-modal-errata` L1588 · L1612 | `app/Models/ProductQna.php:23~34`, `product-qnas/index.blade.php:55` | 상품 Q&A 유형 필터에 파손/오배송 · 오탈자/내용 오류가 보이고, 파손 건 답변 화면에 다발 경고가 뜨는지 |
| BRD-001-7 | 1 적용 | 화면만 | 목록 | 학습 Q&A 목록 '질문한 강의' 칸에 재생 지점이 없다. 상세(show:35~44)는 `play_position_label`을 이미 보여 주므로 목록 칸에 같은 값을 붙인다 | th L1125 '강의 타임스탬프' | `study-qnas/index.blade.php:98` | 학습 Q&A 목록에 "강의명 · 12:34" 형태로 재생 지점이 보이는지 |
| BRD-001-8 | 1 적용 | 기능 수정 | 등록 · 목록 | 당첨자 명단에 경품 유형(포인트 · 기프티콘 · 실물) · 지급 상태 · 지급일시/송장이 없다. 정본 L408 "경품 지급 원장"(기존 전달 POLICY_D_BRD 1번). 영향: `post_winners`에 prize_type · grant_status · granted_at · tracking_no 컬럼 추가 마이그레이션, 기존 행은 prize_type 비움 · 지급대기로 채움. 원본 이름 · 연락처 미저장 원칙은 유지 | 명단 표 L1486(지급 상태 · 송장), L1456 `winrow-type`, L1440~1441 일괄 지급 · 포인트 넘기기 | `winners/form.blade.php:51~80`(명단 순번 · 이름 · 아이디 · 경품만) | 당첨자 발표 수정 화면 명단 표에 경품 유형 · 지급 상태 열이 있고 포인트 당첨자를 포인트 일괄 지급으로 넘길 수 있는지 |
| BRD-001-9 | 2 유지 | — | 등록 | 당첨자 입력을 프로토는 한 명씩 행 폼(등수 · 회원 · 경품), 개발은 엑셀 업로드 + "아이디, 경품" 줄 입력. 저장 시 회원 대조 · 마스킹은 같고 대량 입력엔 개발이 빠르다. BRD-001-8의 경품 유형이 들어오면 줄 형식에 유형 칸만 더한다 | L1450~1484 | `winners/form.blade.php:68~77` | — |
| BRD-001-10 | 2 유지 | — | 등록 | 당첨자 '노출 위치(이벤트 탭 · 공지 상단)' · '게시와 동시에 알림톡' 체크가 개발에 없다(proto-only, 정본 근거 없음). 공지 상단 노출은 공지 상단 고정으로, 개별 알림은 BRD-001-8 지급 처리 쪽에서 다룬다 | L1400~1402 | `winners/form.blade.php` | — |
| BRD-001-11 | 2 유지 | — | 목록 · 등록 | 범용 게시판(boards · posts)은 프로토에 대응 화면이 없다(자유게시판 1차 제외, PROJECT_STATE 1절). 손대지 않는다 | — | `boards/*` · `posts/*` | — |

## ADMN-BRD-002 1:1 문의
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| BRD-002-1 | 1 적용 | 화면만 | 목록 | KPI 카드 모양 — COM-3 | L508~532 | `inquiries/index.blade.php:23~31` | COM-3 |
| BRD-002-2 | 1 적용 | 화면만 | 목록 | 유형(대분류) 칩 줄이 없다(전체 · 결제/환불 · 배송/교재 · 수강/동시접속 · 합격환급/포인트 · 학습질문 오인입). 개발 필터 `category_id`는 소분류 select 하나. 칩은 대분류별 `category_id` 묶음 링크로 만들고, 대분류로 거르는 값이 없으면 BRD-002-3 | L612~617 `filterByCategory` | `inquiries/index.blade.php:58~64` | 목록 위에 대분류 칩과 건수가 보이고 누르면 그 대분류 문의만 남는지 |
| BRD-002-3 | 1 적용 | 기능 수정 | 목록 | 목록에 '문의 유형(대분류)' · '담당 부서 큐' 열과 담당자 '미지정' 필터가 없다. 담당 부서 큐 표시는 정본(설계서 L430), 미지정 필터는 이관 후 받은 부서가 찾는 경로(POLICY_D_BRD B 권고). 영향: 검색 요청에 `parent_category_id` · `assignee=none` 파라미터 추가(쿼리만, 데이터 변경 없음) | th L648 '문의 유형' · '담당 부서 큐 · 담당자', L630 `filter-assignee`(미지정) | `inquiries/index.blade.php:139`(열), `:67~71`(전체/내 담당만) | 목록에 대분류 · 담당 부서 열이 있고 담당자 '미지정'으로 거를 수 있는지 |
| BRD-002-4 | 1 적용 | 기능 수정 | 상세 | 이관하면 상태가 '타부서 이관중'이 되고 담당자가 비워져야 하는데, 개발 상태는 접수 · 처리중 · 답변완료 · 보류 4개뿐이고 분류 변경은 상태를 바꾸지 않는다. 정본 설계서 L430 · PROJECT_STATE 1절(기존 전달 3번). 영향: `Inquiry::STATUS`에 `transferred` 추가, 분류 변경 처리에서 상태 · 담당자 초기화, 목록 · 대시보드 미처리 집계에 포함 | 상태 옵션 L622 '타부서 이관중' | `app/Models/Inquiry.php:16~21`, `partials/inquiry-panel.blade.php:43~58` | 다른 부서 분류로 바꾸면 상태 '타부서 이관중' · 담당 미지정이 되고 받은 부서가 열면 그 사람이 담당이 되는지 |
| BRD-002-5 | 1 적용 | 기능 수정 | 상세 | 분류 변경(이관)에 '내부 이관 메모'(필수)가 없다. PROJECT_STATE 1절 "이관 메모 필수". 영향: 분류 변경 요청에 `transfer_memo` required 추가, 답변 폼 `internal_memo`와 별개로 이관 이력에 남김. 모달로 바꿀 필요는 없고 지금 분류 변경 폼 옆에 메모 칸을 둔다 | transfer-modal L1046, `modal-memo` L1072 | `partials/inquiry-panel.blade.php:53~58` | 분류 변경 시 메모 없이 저장하면 막히고, 받은 부서 상세에 메모가 보이는지 |
| BRD-002-6 | 1 적용 | 기능 수정 | 상세 | 주문번호 없이 들어온 환불 · 배송 문의에 최근 14일 결제 주문을 찾아 붙이는 기능이 없다(정본 설계서 L429, 기존 전달 3번). 영향: 라우트 `admin.inquiries.order.update` 신설, `inquiries.order_id` 갱신 · 감사 로그 | L880대 `bindDetectedOrder`(proto-only, '주문번호 바인딩') | `partials/inquiry-panel.blade.php:66~71`(연결 주문 표시만) | 주문 미연결 문의 상세에 '최근 결제 주문' 후보와 [연결] 버튼이 보이는지 |
| BRD-002-7 | 2 유지 | — | 상세 | 유형별 분기 패널(환불 큐 이관 · 3PL 출고 Lock 안내 · 세션 강제 로그아웃 · 합격환급 안내)과 매크로 칩이 개발에 없다. 이관은 분류 변경 하나로 되고(dev-note), 세션 초기화는 회원 수강 · 기기 화면(USER-003) 몫이라 기능 차이는 매크로뿐이다. 매크로는 정본에 없는 편의 기능 | `branch-*` 패널, `macro-chips`(proto-only) | `partials/inquiry-panel.blade.php` | — |
| BRD-002-8 | 2 유지 | — | 목록 | 개발이 경과(시간) · SLA 초과 강조 · 알림 성공 여부 · 보류/재개를 더 갖고 있다. 개발이 낫다 | — | `inquiries/index.blade.php:160~166`, `inquiry-panel:168~203` | — |

## ADMN-BRD-005 후기 (+ 무료콘텐츠)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| BRD-005-1 | 1 적용 | 기능 수정 | 목록 | 프로토는 수강후기 · 합격수기 탭, 개발은 한 목록. 결정: 데이터는 reviews 한 테이블, 탭 = 합격 증빙 유무 필터(POLICY_D_BRD B). 영향: 목록 요청에 `has_pass_cert`(1/0) 필터 추가(쿼리만), 위에 탭 줄(`tab__list`) 두 개 | 탭 L755 · L761 | `reviews/index.blade.php:49~116`(필터에 증빙 유무 없음) | 후기 목록 위 '수강후기 · 합격수기' 탭을 누르면 합격증 X / O 건만 남는지 |
| BRD-005-2 | 1 적용 | 화면만 | 목록 | 수강후기 탭에 '별점' 열이 없다. `rating`은 모델에 있고 상세(show:37)에서 별로 그린다 — 목록 칸만 추가 | th L818 '별점 평점' | `reviews/index.blade.php:153` | 수강후기 탭 목록에 ★ 별점이 보이는지 |
| BRD-005-3 | 3 판단 | — | 목록 | 수강후기 '수강 진도율' 열 — 후기에 수강 이력을 이어 붙이는 범위(강좌 id로 enrollment 조회)라 1차에 넣을지 white 결정 필요. 정본 L408은 "수강 · 합격후기 검수"까지만 | th L818 '수강 진도율' | `reviews/index.blade.php:153` | — |
| BRD-005-4 | 1 적용 | 화면만 | 목록 | 보상을 준 후기에 '포인트 지급 후기' 배지가 없다(S-21 결정). 목록 '포인트' 열 값에 배지로 표시 | th L818 '베스트 선정 / 포인트' | `reviews/index.blade.php:153` '포인트' 열 | 포인트를 준 후기 행에 '포인트 지급 후기' 배지가 보이는지 |
| BRD-005-5 | 2 유지 | — | 상세 | 합격수기 증빙 검수를 프로토는 모달, 개발은 검증 페이지(show: 본문 · 첨부 · 증빙 · 처리). 첨부가 많아 페이지가 맞다 | modal-pass-audit L1159 | `reviews/show.blade.php` | — |
| BRD-005-6 | 2 유지 | — | 목록 · 등록 | 무료콘텐츠는 11-02~03 커밋으로 구분 3종 · 머리말 5종 · 쇼츠 유튜브 주소까지 프로토와 맞다. 개발이 관련 강좌 · 다중 PDF · 중복 경고를 더 갖고 있다 | L1064~1111 | `free-contents/form.blade.php:8~126` | — |
| BRD-005-7 | 3 판단 | — | 등록 | 무료콘텐츠 '버전 이력 표'(버전 · 저장일 · PDF · 변경 내용)가 개발에 없다. 정본에 보관 요구가 없어 1차에 둘지 white 결정 필요 | th L1132 | `free-contents/form.blade.php` | — |

## ADMN-BRD-007 1:1 문의 분류
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| BRD-007-1 | 1 적용 | 기능 수정 | 등록 | 담당 부서 큐가 단일 select다. 확정 기준은 복수 선택(PROJECT_STATE 1절 2026-10-22, 기존 전달 4번). 스키마 `inquiry_category_roles`는 이미 복수라 요청 검증(`assign_role` → `assign_roles[]`)과 폼(체크박스 묶음)만 바꾼다. 기존 행은 그대로 1건짜리 목록으로 읽힘 | `cf-depts` check-group L247 | `inquiry-categories/index.blade.php:251~257`, `app/Http/Requests/Admin/InquiryCategory*Request.php:36` | 분류 등록에서 부서 큐를 두 개 골라 저장하고 목록 '담당 부서 큐' 열에 둘 다 보이는지 |
| BRD-007-2 | 1 적용 | 화면만 | 목록 | 분류 변경 이력 표가 없다. 결정: 목록 아래에 변경 이력(일시 · 작업자 · 전후 값), 원천은 감사 로그(POLICY_D_BRD B). 화면 표만 어렵다면 이력/보안 로그(대상 유형 = 문의 분류)로 가는 링크로 대체 가능 | 카드 '분류 변경 이력' L200~208 | `inquiry-categories/index.blade.php`(이력 없음) | 분류 목록 아래에서 최근 변경 이력이나 감사 로그 바로가기가 보이는지 |
| BRD-007-3 | 2 유지 | — | 등록 | 프로토는 등록 · 수정을 별도 페이지(S1), 개발은 같은 화면 아래 펼침 폼(`subForm`). 항목 · 자동 채번 · 라우팅 변경 확인(confirm, :355)이 같아 기능 차이 없다 | L211~ `subFormSection` | `inquiry-categories/index.blade.php:199~282` | — |

## ADMN-CONF-001 배너 · 팝업
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-001-1 | 2 유지 | — | 목록 | 탭 구성(메인 슬라이드 · 이벤트 목록 상단 · 띠배너 · 모달 팝업)이 개발 `display/index` 탭(`DisplayController::TABS`)과 같다 | L143~146 | `display/_head.blade.php` · `display/index.blade.php` | — |
| CONF-001-2 | 2 유지 | — | 등록 | 노출 기간을 프로토는 글자 칸("2026.10.01 ~ 2026.11.30"), 개발은 시작 · 종료 `datetime-local` 두 칸. 개발이 낫다(프로토가 고칠 쪽) | L242 `bd-period` · L465 `pd-period` | `banners/form.blade.php:95~104`, `popups/form.blade.php:138~147` | — |
| CONF-001-3 | 1 적용 | 화면만 | 목록 | 목록 '이미지' 칸이 비어 보인다(screen.md 참고, 썸네일 경로 · 데이터 문제일 수 있음 — (추정)). 프로토는 PC / 모바일 규격 칸. 썸네일이 없으면 'PC ✓ · MO ✓' 글자로라도 표시 | th L174 'PC / 모바일 규격' | `display/index.blade.php:91` | 배너 목록 이미지 칸에 썸네일 또는 PC · MO 등록 여부가 보이는지 |
| CONF-001-4 | 2 유지 | — | 등록 | 팝업 폼 항목(연결 방식 · 위치 · 크기 · 닫기 옵션 · PC/MO 이미지)이 같다. 개발 '이미지 대체 텍스트' 칸은 이미지 칸 안에 있어 프로토와 배치만 다르다 | L411 | `popups/form.blade.php:13~180` | — |

## ADMN-CONF-002 약관
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-002-1 | 1 적용 | 기능 수정 | 등록 | 공시중(시행 전) 버전의 오탈자 보정이 없다(개발은 확정 버전 수정 불가). 결정 D-CONF-01: 시행중은 새 개정만, 공시중만 사유 · 전후 본문 이력을 남기고 버전 유지 보정. 영향: `term_corrections`(term_id · before · after · reason · admin_id) 테이블 · `admin.terms.corrections.store` 라우트 신설, 공시 기간 검사 제외 | L682 `DIRECT_FIX`, `term-correction-box` | `TermService.php:176~186`, `routes/admin.php:1292~1305`(corrections 없음) | 공시중 약관 보기에 [오탈자 보정]이 있고 저장 후 이력에 전후 본문이 남는지, 시행중 약관엔 버튼이 없는지 |
| CONF-002-2 | 1 적용 | 화면만 | 목록 | 목록에 '프론트 노출 · 동의 수집 위치' 열이 없다. 종류 6종 고정이라 종류별 고정 문구(예: T01 회원가입 · 결제)로 채운다 | th L522 | `terms/index.blade.php:36` | 약관 목록에 각 약관의 노출 · 동의 위치가 보이는지 |
| CONF-002-3 | 2 유지 | — | 목록 | 프로토 '사전 공고(시행 예정)' · '보관 버전 수' 열은 개발 상태(공시중) · [이력] 버튼으로 같은 정보에 닿는다. 프로토 '공고일' ↔ 개발 '공시 일자'는 이름만 다름 | th L522 | `terms/index.blade.php:36~67` | — |
| CONF-002-4 | 2 유지 | — | 등록 | 프로토 '현행 조문으로 초기화' · '이 버전 본문 불러오기' · '전체 회원 개정 고지 발송' 바로가기가 개발에 없다(proto-only 편의). 개발 '현행본 나란히 보기' · 미리보기로 비교는 된다 | L806 · L967 · L604 | `terms/form.blade.php:89~139` | — |

## ADMN-CONF-003 인증 · 플레이어 설정
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-003-1 | 1 적용 | 기능 수정 | 설정 | 진도 인정 배속이 '전 배속 인정 / 일부 배속만 인정' 2택이다. 정본은 숫자 값(기본 2.0x, 설계서 L273 · v3.2.14, 기존 전달 POLICY_D_CONF A). 영향: `progress_speed_policy` → `progress_credit_max_speed`(decimal) 추가, 기존 'all'은 재생 최대 배속값, 'limited'는 2.0으로 이관, 진도 계산(`LectureProgressService`)이 이 값으로 자름 | L204 `pl-credit-speed` | `player-settings/index.blade.php:155~160`, `app/Models/PlayerSetting.php:81~84` | 플레이어 설정 '진도 인정 최대 배속'이 숫자 선택이고, 2.0x로 두면 2.5x 재생 구간이 진도에 안 잡히는지 |
| CONF-003-2 | 1 적용 | 기능 수정 | 설정 | 재생 배속 단계에 2.5x가 없다(최대 2.0). 권고대로 2.5 추가(POLICY_D_CONF B). 영향: `LectureProgressService::SPEED_STEPS`에 2.5 추가 — 사용자 플레이어 배속 메뉴에도 나타남 | L193 `pl-max-speed` '2.5x' | `app/Services/Learning/LectureProgressService.php:45` | 재생 배속 최대 select에 2.5x가 있는지 |
| CONF-003-3 | 2 유지 | — | 설정 | 재마스킹(해제 유효) 시간 회원 · 권리자 2값은 개발 인증 발송 설정에 이미 있다(`pii_unmask_ttl_*`). 프로토는 플레이어 화면 카드, 개발은 인증 설정 화면 — 위치만 다름. 이름은 정본 '재마스킹 시간'이 프로토, 개발 '해제 유효시간'도 뜻이 같아 그대로 | L274 | `verify-settings/index.blade.php:59~72` | — |
| CONF-003-4 | 3 판단 | — | 설정 | 프로토에만 있는 설정 카드 3개: '학습 Q&A 운영 방식(카페 아웃링크 / 자체)', '수동 무상 포인트 유효기간 선택지', '24시간 접속 IP 급증 감지'. 정본은 학습 Q&A 1차 카페 아웃링크만 정함 — 운영자가 바꾸는 설정으로 1차에 둘지 white 결정 필요 | L330 `card-lqna-mode` · L304 · L160대(proto-only) | 개발 없음 | — |
| CONF-003-5 | 2 유지 | — | 화면 구성 | 프로토는 한 화면 탭 2개(플레이어 / SMS · IP), 개발은 메뉴 2개(플레이어/DRM 설정 · 인증 발송 설정). 각 화면 항목이 같아 기능 차이 없다 | L136~137 | `player-settings` · `verify-settings` | — |

## ADMN-CONF-004 메시지 템플릿 (+ SENS 템플릿)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-004-1 | 1 적용 | 화면만 | 목록 | 프로토는 템플릿 · 타겟 발송 · 발송 이력 3탭, 개발은 버튼으로 각 페이지에 간다. `display/_head`처럼 세 라우트를 잇는 탭 줄(`tab__list`)을 세 화면 머리에 둔다(라우트 유지) | L405~411 | `message-templates/index.blade.php:115~120`, `campaigns/index` · `send-stats` 머리 | 세 화면 어디서든 위 탭으로 오가고 현재 화면 탭이 켜져 있는지 |
| CONF-004-2 | 1 적용 | 기능 수정 | 타겟 발송 | 즉시 발송이 없다("즉시 발송은 2차"). 결정 D-CONF-02 · S-23: 즉시 · 예약 둘 다(즉시는 재확인 모달), 광고성은 20:50~08:00 즉시 · 예약 시작 불가, 예약 취소 마감은 설정값(기본 30분). 영향: `MessageCampaignRequest` scheduled_at을 모드별 필수로, 즉시 모드 큐 디스패치, `CANCEL_LEAD_MINUTES` 상수 → 설정값 | L537 `send-schedule-mode`, modal-send-confirm L617 | `campaigns/index.blade.php:58~61`, `MessageCampaignService.php:49` | 타겟 발송에 즉시/예약 선택이 있고 즉시는 확인 모달 뒤 발송, 광고성 21시대엔 막히는지 |
| CONF-004-3 | 2 유지 | — | 등록 | 템플릿 등록을 프로토는 모달, 개발은 별도 페이지. 본문 · LMS 대체 · 미리보기가 있는 긴 폼이라 페이지가 맞다 | modal-template L655 | `message-templates/form.blade.php` | — |
| CONF-004-4 | 2 유지 | — | 목록 | 프로토 '연동 도메인 / 트리거' · 'SENS 검수 상태' · 'Fallback' 열 ↔ 개발 '발송 조건' · '심사' · 채널('알림톡 → LMS'). 검수 상세는 SENS 템플릿 화면(승인 상태 · 동기화)에 있어 정보가 같다. 탭 이름 'ADMN-CONF-007 = 발송 이력'은 프로토 쪽 오기(POLICY_D_CONF A) | th L485 | `message-templates/index.blade.php:129`, `sens-templates/index.blade.php:99` | — |

## ADMN-CONF-005 관리자 계정 · 권한 · 메뉴
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-005-1 | 1 적용 | 화면만 | 목록 · 등록 | '권한 그룹' 표기 → '역할 그룹'(정책질문9건_결정경위 3번, 정본 표기). 메뉴명 '권한 그룹 관리' 포함. 내부 이름(admin_roles)은 유지 | 탭 L147 '역할 그룹 · 권한' | `admin-users/index.blade.php:36 · :135`, `admin-roles/index.blade.php:12 · :101`, `admin-roles/form.blade.php:47` | 관리자 · 권한 화면 어디에도 '권한 그룹'이 남지 않는지 |
| CONF-005-2 | 1 적용 | 기능 수정 | 목록 · 등록 | 역할 그룹 추가 · 미사용이 없다(6종 고정, 라우트 index · edit · update만). 정본: 운영 중 추가 · 수정 · 미사용 변수, 최초값 8종(저작권자 · 외부 3PL 포함, 기존 전달 POLICY_D_CONF A). 영향: `admin_roles`에 `is_active` · `is_inquiry_queue` · `start_route` · `dashboard_area` 컬럼, create/store 라우트, 소속 계정 · 문의 분류가 쓰는 그룹은 미사용 차단 | modal-role L241~261(구분 · 문의 큐 · 시작 화면 · 대시보드 영역 · 권한 시작값) | `routes/admin.php:238~245`, `app/Models/AdminRole.php:43~48` | 역할 그룹 목록에 [＋ 역할 그룹 추가] · 미사용 전환이 있고, 사용 중인 그룹은 미사용이 막히는지 |
| CONF-005-3 | 1 적용 | 기능 수정 | 등록 · 목록 | 계정 '소속(데이터 범위)' 축(내부 직원 / 권리자 / 거래처)이 없다. 확정 기준(PROJECT_STATE 1절, 기존 전달). 영향: `users`(관리자)에 `affiliation` · `affiliation_ref`(RH-* / SUP-*) 컬럼, 기존 계정은 내부 직원으로 채움, 권리자 · 거래처 계정의 조회 범위 필터 | L297~299 `af-kind`, th L166 '소속 (데이터 범위)' | `admin-users/form.blade.php:20~230`, `admin-users/index.blade.php:130~140` | 계정 발급에서 소속 3택과 대상(권리자 · 거래처)을 고르고 목록에 소속 열이 보이는지 |
| CONF-005-4 | 1 적용 | 화면만 | 목록 | 목록에 '최근 접속' 열이 없다. `last_login_at`이 이미 있어 칸만 추가 | th L166 '최근 접속' | `admin-users/index.blade.php:132~140` | 관리자 목록에 최근 접속 일시가 보이는지 |
| CONF-005-5 | 2 유지 | — | 등록 | 프로토 '접속 제한' 칸(proto-only) — 개발은 `admin_allowed_ips` 테이블로 따로 관리. 계정별 입력이 필요한지는 정본에 없음 | L304 `af-sec` | `admin-users/form.blade.php` | — |
| CONF-005-6 | 2 유지 | — | 화면 구성 | 프로토는 한 화면 탭(계정 / 역할 · 권한 / 메뉴)과 계정 발급 모달, 개발은 메뉴 3개 · 별도 페이지. 권한 축은 개발 5축(조회 · 등록 · 수정 · 삭제 · 다운로드)이 개발 구조로 결정돼 있다(M-02) | L146~148, modal-account L282 | `admin-users` · `admin-roles` · `admin-menus` | — |

## ADMN-CONF-010 감사 로그 (+ 로그인 로그)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CONF-010-1 | 1 적용 | 화면만 | 목록 | 검색 칸 테두리 없음 — COM-1 | — | `admin-logs/index.blade.php:229 · :242`, `login-logs/index.blade.php:142` | COM-1 |
| CONF-010-2 | 1 적용 | 화면만 | 목록 | '행위' · '대상' 열에 영문 코드가 그대로 나온다(view · download · user · refund_claim · instructor_profile). `@switch`에 create · update · delete · login · logout만 있다. 행위(view 열람, download 다운로드, unmask 마스킹 해제 등)와 대상 유형(회원 · 환급 신청 · 강사 프로필 …, `DashboardService::DOWNLOAD_TARGETS`와 같은 표)을 한글 라벨로 | th L441 '이벤트 유형' | `admin-logs/index.blade.php:400~435` | 이력/보안 로그 목록에 영문 행위 · 대상이 한 건도 없는지 |
| CONF-010-3 | 1 적용 | 화면만 | 목록 | 머리에 제목 h2가 두 개('관리자 로그' + '시스템 정산 감사 로그 — …') 붙어 한 줄로 이어 보인다(스크린숏). 프로토 제목 하나로 | 화면 제목 | `admin-logs/index.blade.php:42 · :49` | 화면 제목이 하나만 보이는지 |
| CONF-010-4 | 1 적용 | 화면만 | 목록 | 탭 3개가 있는데 처음 열면 3번(운영자 접근 로그)이 열린다. 프로토는 1번(감사 이벤트 상세 원장)이 기본. 기본 탭만 바꾸고 SNB 진입 주소에 `tab`이 없을 때 1번 | L361 첫 탭 | `admin-logs/index.blade.php:57~66`(탭바 주석 "처음 선택만 기존 운영자 접근 로그") | 메뉴로 들어오면 1번 탭이 켜지는지 |
| CONF-010-5 | 2 유지 | — | 목록 | 로그인 로그는 프로토 3번 탭 안, 개발은 별도 화면 + 머리 버튼. 오가는 길이 있어 기능 차이 없다. 해시 체인 검증은 2차(D-CONF-03)인데 개발 버튼이 이미 있음 — 동작하면 두어도 된다 | L422 `accessTypeSelect` | `admin-logs/index.blade.php:45~47`, `_tab-audit.blade.php:127` | — |

## ADMN-LOGIN-001 로그인
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| LOGIN-001-1 | 1 적용 | 기능 수정 | 로그인 | 로그인 요청이 비밀번호 `min:6`을 검사해 6자 미만은 다른 오류 문구가 나고 5회 잠금 계산에서 빠질 수 있다. 권고대로 `required`만(POLICY_D_CONF B, 정본 L120 동일 오류 메시지). 영향: `LoginRequest` 규칙 한 줄, 화면 변화 없음 | — | `app/Http/Requests/Admin/LoginRequest.php:18` | 5자 비밀번호로 로그인하면 일반 오류 문구가 나오고 실패 횟수가 올라가는지 |
| LOGIN-001-2 | 2 유지 | — | 로그인 · 찾기 | 비밀번호 8~64자(D-CONF-05)는 반영됨. 비밀번호 찾기의 이메일 인증 → SMS 순서는 개발이 정본대로(프로토가 고칠 쪽). 세션 만료 문구 · Caps Lock 경고 · 5회 잠금 팝업 · 아이디/비밀번호 찾기 버튼이 프로토와 같다 | L381, L355~377 | `AdminPasswordPolicyService.php:30~37`, `auth/login.blade.php:24 · :93 · :113~116 · :135~` | — |
| LOGIN-001-3 | 2 유지 | — | 로그인 | 프로토 '접속 역할 프리셋(시연용)'은 시연 전용이라 개발에 두지 않는다 | L286 | — | — |

## ADMN-DASH-001 대시보드 (+ 매출 · 상품 통계)
| # | 분류 | 영향 | 위치 | 차이 | 프로토 근거 | 개발 위치 | 확인 방법 |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| DASH-001-1 | 1 적용 | 화면만 | 대시보드 | 처리 대기 큐가 표 하나에 섞여 있다. 프로토는 업무 영역별 접이식 구역(매출 · 성과 / CS · 회원 / 물류 / 정산 / 시스템 · 보안)마다 대기 큐 표. 큐 행 키(`queue.pass_refund` 등)를 영역에 붙이는 표를 Blade에 두고 영역별로 나눠 그린다 | L483 · L532 · L600 · L645 · L704 `toggleDashSec`, 큐 표 L569 · L621 · L659 | `dashboard/_body.blade.php:64~100` | 대시보드에 영역별 구역이 있고 접기/펴기가 되며 각 구역에 해당 큐만 있는지 |
| DASH-001-2 | 1 적용 | 기능 수정 | 대시보드 | 블록 노출이 역할 코드 하드코딩(`VISIBLE`: super · cs · logistics · finance)이다. 정본: 메뉴 권한 기준 + 역할 그룹의 대시보드 기본 영역(설계서 v3.2.19 L50 · L411, 기존 전달). 영향: 블록마다 연결 메뉴 권한(can_view)으로 판정, 새 역할 그룹(CONF-005-2)도 자동 적용. CONF-005-2의 `dashboard_area`와 함께 | — | `app/Services/Admin/DashboardService.php:38~44` | 새 역할 그룹에 1:1 문의 조회만 주면 대시보드에 CS 블록만 보이는지 |
| DASH-001-3 | 2 유지 | — | 대시보드 | 발송 실패 큐 모달 · 건별 재발송이 개발에 없다. 결정: 모달 구현이나 발송 이력 재발송으로 가는 링크 중 택일 — 업무 규칙 차이 없음(POLICY_D_CONF B). 개발 '알림 발송 현황' 블록에 실패 건 링크만 있으면 된다 | modal-fail-queue L989 | `dashboard/_body.blade.php:31~60` | — |
| DASH-001-4 | 2 유지 | — | 통계 | 매출 · 상품 통계는 프로토 대시보드 하위 뷰, 개발 별도 메뉴. 필터(기간 프리셋 · 단위 · 결제수단 · 상품 유형 · 환불 반영 기준)와 표 열이 같다. 통계 엑셀은 사유 없이 반출 기록만이 결정(POLICY_D_CONF A) — 개발이 맞고 프로토 사유 모달이 고칠 쪽 | L832~865 · L908 · L968, modal-stat-excel L1047 | `sales-stats/index.blade.php:24~147`, `product-stats/index.blade.php:24~120` | — |

## 그룹 요약
- 1 적용 37건(화면만 21 · 기능 수정 16, 그중 BRD-002-1 · CONF-010-1은 공통 COM-3 · COM-1을 가리키는 행) · 2 유지 27건 · 3 판단 3건(BRD-005-3 후기 진도율, BRD-005-7 무료콘텐츠 버전 이력, CONF-003-4 프로토 전용 설정 카드 3개).
- 화면만 중 가장 큰 것: COM-2 상태 배지(목록 9개 화면)와 COM-1 테두리 없는 검색 칸(입력 칸이 글자처럼 보임, 이력/보안 · 로그인 로그).
- 기능 수정 중 가장 큰 것: CONF-005-2 · 3 역할 그룹 추가 · 미사용과 계정 소속 축(DASH-001-2와 묶임) — 모두 10-27 개발팀 전달분이 아직 반영 안 됨. 1:1 문의 '타부서 이관중' 상태 · 이관 메모 · 주문 연결(BRD-002-4~6)이 그다음.
