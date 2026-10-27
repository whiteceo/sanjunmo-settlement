# ADMN-RFD-002 환불 요청 관리 (통합 목록 · 상세) — 개발 명세

- 프로토타입 파일: `prototype_clean/ADMN-RFD-002_baseline.html` (원본 상태: 18d66c1 v6.92. 본문 줄 번호 L… 는 v6.92 이전 기준이 남아 있을 수 있다 — 함수 · id 이름으로 찾는다)
- 맞춘 개발 커밋: `d562524a` (2026-10-26 19:52)
- 포함 화면: RFD-004 환불 요청 목록 · RFD-002 환불 처리 상세(부분 환불 계산기) · 002-S1 연관 1:1 결제 · 환불 문의 · 002-P1 마이너스 포인트 전환 확인 · 002-P2 포인트 사용 내역 · RFD-003 환불 완료 내역 · 003-S1 완료 상세 · 003-S2 보정 거래 등록
- 제외: RFD-001 올패스 합격 환급 심사(`admin.pass-refunds.*`)는 프로토에서 ADMN-SETT-006으로 보낸다(L449 링크) → SETT-006 명세 소관. 단 계좌 환불(`pass-refunds.account-refunds.update`)은 이 화면 케이스 4와 이어져 2절에 적는다
- 개발 진행: 구현(RFD-002 · 002-S1 · 003 라우트 · 화면 있음, 002-P1 · 002-P2 · 003-S2 · 004 커밋 언급, `_index/progress.md` 52~60행)
- 근거: 개발 `routes/admin.php:891-944`, `app/Http/Controllers/Admin/RefundController.php` · `RefundInquiryController.php` · `RefundHistoryController.php` · `RefundAdjustmentController.php`, `app/Services/Admin/RefundAdminService.php`, `app/Services/Refund/RefundCalculator.php` · `RefundService.php` · `RefundAdjustmentService.php`, `app/Services/Point/PointLedgerService.php`

프로토타입 view ↔ 개발 화면
| 프로토타입 view(id) | 개발 화면 | 개발 뷰 파일 |
|---|---|---|
| `view-list` (`sw-rfd-list`, data-subpage `list`) | RFD-004 환불 요청 목록(환불 건 + 판정 전 1:1 문의) | `resources/views/admin/refunds/index.blade.php` (Ajax 조각 `request-list`) |
| `view-detail` (`sw-rfd-detail`) · 왼쪽 `left-pane-reason` | RFD-002 환불 처리 상세 | `refunds/show.blade.php` (+ `partials/calc-table` · `lifo-table`, Ajax 조각 `refund-calc`) · `refunds/print.blade.php` |
| `view-detail` 왼쪽 `left-pane-inquiry` | RFD-002-S1 결제 · 환불 문의 상세 | `refunds/inquiry-show.blade.php` (+ `admin.inquiries.partials.inquiry-panel`) — 개발은 별도 화면 |
| `modal-p1` | RFD-002-P1 마이너스 전환 확인 | `refunds/show` `layerMinus` |
| `modal-p2` | RFD-002-P2 포인트 사용 내역 | `refunds/show` `layerPointUsages` ← `partials/point-usages.blade.php` |
| `view-done` (`sw-rfd-done`) | RFD-003 환불 완료 내역 | `refund-histories/index.blade.php` |
| data-subpage `done-detail`(`openRfdDonePage`) | RFD-003 상세 | `refund-histories/show.blade.php` |
| data-subpage `adjust`(`rfd-adjust-form`) | RFD-003-S2 보정 거래 등록 | `refund-histories/adjust.blade.php` |

## 1. 메뉴 · 권한

| 메뉴(admin_menus.route_name) | 메뉴명 | 프로토타입 view | 확인 방법 |
|---|---|---|---|
| `admin.refunds.index` | 환불 요청 관리(추정) | view-list · view-detail · P1 · P2 · S1 | 메뉴 = 라우트 이름 목록형(추정), 개발 서버 메뉴 관리 확인 필요 |
| `admin.refund-histories.index` | 환불 내역 조회(추정) | view-done · 완료 상세 · S2 보정 | 〃 |
| `admin.pass-refunds.index` | 합격 환급 심사(추정) | (케이스 4 계좌 환불만) | 〃 |

- 메뉴 권한 밖 추가 판정
  - 환불 승인 · PG 취소 전송 · 1:1 PG 즉시 취소: 재무팀 · 최고 관리자만(`RefundAdminService::canSettleMoney`, `RefundController.php:292-295`). CS는 메뉴 수정 권한이 있어도 접수 · 검수 · 보류 · 거절까지.
  - 보정 거래 등록: 재무팀 · 최고 관리자 + `admin.refund-histories.index` 등록 권한(`RefundAdminService::canRegisterAdjustment`, `routes/admin.php:941` 주석).
  - 상세를 수정 권한자가 처음 열면 접수 → 환불진행 자동 전환(`RefundController.php:112-115`).
- 재계산(`admin.refunds.recalculate`)은 README 접미사 예외대로 **수정** 권한(`_index/routes.md:340`). 라우트 주석은 "재계산은 다시 읽기라 조회 권한"이라 적혀 있어 주석과 실제가 다름(`routes/admin.php:892`) — 개발 확인 사항, 정책 아님.
- 반품 검수는 이 메뉴(`refunds.inspection.update`)와 배송 관리 메뉴(`deliveries.returns.update`, ADMN-ORD-001.md) 두 경로가 같은 서비스를 쓴다.

## 2. 화면별 라우트

공통 접두사 `/{admin}` = `/sj-admin`. `{refund}` = `refunds.id`, `{inquiry}` = `inquiries.id`, `{photo}` · `{file}` = `attachments.id`, `{adjustment}` = `refund_adjustments.id`.

### RFD-004 환불 요청 목록
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(탭 · 필터, 탭 전환은 Ajax 조각) | GET | `/refunds?tab=&from=&to=&type=&inflow=&product=&deadline=&keyword=` | `admin.refunds.index` | 조회 | RefundController@index |
| 엑셀(사유 레이어 `layerReason`, 회원명 마스킹) | GET | `/refunds/download` | `admin.refunds.download` | 다운로드 | RefundController@download |
| 행 열기 — 환불 건 / 판정 전 1:1 문의 | → | `/refunds/{refund}` · `/refunds/inquiries/{inquiry}` | `admin.refunds.show` · `admin.refunds.inquiries.show` | 조회 | |

### RFD-002 환불 처리 상세 · P1 · P2
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 상세(`?inspection_result=&liability=` 주면 저장 없이 재계산 미리보기, Ajax 조각) | GET | `/refunds/{refund}` | `admin.refunds.show` | 조회 | RefundController@show |
| 환불금 계산 명세 인쇄 | GET | `/refunds/{refund}/print` | `admin.refunds.print.show` | 조회 | RefundController@showPrint |
| 회원 첨부 사진 열람 | GET | `/refunds/{refund}/photos/{photo}` | `admin.refunds.photos.show` | 조회 | RefundController@showPhoto |
| 3PL 창고 입고 확인 | PUT | `/refunds/{refund}/receipt` | `admin.refunds.receipt.update` | 수정 | RefundController@updateReceipt |
| 반품 검수 · 귀책 판정(사진) | PUT | `/refunds/{refund}/inspection` | `admin.refunds.inspection.update` | 수정 | RefundController@updateInspection |
| 재계산(스냅샷 · 예정액 갱신) | POST | `/refunds/{refund}/recalculate` | `admin.refunds.recalculate` | 수정(접미사 예외) | RefundController@recalculate |
| 승인 · PG 취소 전송(+ P1 마이너스 동의 · 수동 보정) | PUT | `/refunds/{refund}/approval` | `admin.refunds.approval.update` | 수정 + 재무 | RefundController@updateApproval |
| 환불 거절 · 기각 | PUT | `/refunds/{refund}/rejection` | `admin.refunds.rejection.update` | 수정 | RefundController@updateRejection |
| 환불 보류 | PUT | `/refunds/{refund}/hold` | `admin.refunds.hold.update` | 수정 | RefundController@updateHold |
| P2 포인트 사용 내역(레이어 본문) | GET | `/refunds/{refund}/point-usages` | `admin.refunds.point-usages.index` | 조회 | RefundController@pointUsages |
| 마스킹 해제(환불 계좌) | POST | `/masking/unmask` | `admin.masking.unmask` | 메뉴 권한 밖(MaskingService) | MaskingController@unmask |

### RFD-002-S1 결제 · 환불 문의 상세
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 문의 상세(문의 원문 + 환불 연산기) | GET | `/refunds/inquiries/{inquiry}` | `admin.refunds.inquiries.show` | 조회 | RefundInquiryController@show |
| 답변 임시저장 · 등록 · 보류(`action=draft\|answer\|hold`) | PUT | `/refunds/inquiries/{inquiry}` | `admin.refunds.inquiries.update` | 수정 | RefundInquiryController@update |
| 분류 변경 · 타 부서 이관 | PUT | `/refunds/inquiries/{inquiry}/category` | `admin.refunds.inquiries.category.update` | 수정 | RefundInquiryController@updateCategory |
| 하위 분류 판정(상담필요 · 부분 · 전액) + 주문 연결 + 라인 | PUT | `/refunds/inquiries/{inquiry}/sub-type` | `admin.refunds.inquiries.sub-type.update` | 수정 | RefundInquiryController@updateSubType |
| 문의에서 환불 건 만들기 | POST | `/refunds/inquiries/{inquiry}/refund` | `admin.refunds.inquiries.refund.store` | 등록 | RefundInquiryController@storeRefund |
| PG 즉시 취소 실행 | PUT | `/refunds/inquiries/{inquiry}/cancel` | `admin.refunds.inquiries.cancel.update` | 수정 + 재무 | RefundInquiryController@updateCancel |
| 환불 보류 | PUT | `/refunds/inquiries/{inquiry}/hold` | `admin.refunds.inquiries.hold.update` | 수정 | RefundInquiryController@updateHold |
| PG 기간 초과 건 계좌 환불 [이체 완료] | PUT | `/pass-refunds/account-refunds/{refund}` (목록 `/pass-refunds?view=account`) | `admin.pass-refunds.account-refunds.update` | 수정(합격 환급 메뉴) | PassRefundController@updateAccountRefund |

### RFD-003 환불 완료 내역 · 상세 · S2 보정 거래
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록(탭 · 필터) | GET | `/refund-histories` | `admin.refund-histories.index` | 조회 | RefundHistoryController@index |
| 엑셀 · PG 대사용 엑셀(사유 레이어 `historyExcel` · `historyPgExcel`) | GET | `/refund-histories/download` | `admin.refund-histories.download` | 다운로드 | RefundHistoryController@download |
| 완료 상세(계산 명세 레이어 `layerCalcSpec`) | GET | `/refund-histories/{refund}` | `admin.refund-histories.show` | 조회 | RefundHistoryController@show |
| S2 보정 등록 폼 | GET | `/refund-histories/{refund}/adjustments/create` | `admin.refund-histories.adjustments.create` | 등록 + 재무 | RefundAdjustmentController@create |
| S2 보정 등록 | POST | `/refund-histories/{refund}/adjustments` | `admin.refund-histories.adjustments.store` | 등록 + 재무 | RefundAdjustmentController@store |
| 보정 근거 파일 열람 | GET | `/refund-histories/{refund}/adjustments/{adjustment}/files/{file}` | `admin.refund-histories.adjustments.files.show` | 조회 | RefundAdjustmentController@showFile |
| 목록에서 원 환불 고르고 보정(`openRefundAdjustPage(null,'list')`) | → | 개발은 완료 상세에서만 진입(원 환불 고정) | | | 개발 미구현(목록 진입) |

## 3. 폼 필드 · 검증

### 004 목록 검색 (GET, RefundAdminService::normalizeRequestFilters `RefundAdminService.php:150`)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `tab` | REQUEST_TABS, 기본 `all` | `all` 전체 · `requested` 접수 · `consult` 상담필요 · `progress` 환불진행 · `held` 환불보류 · `completed` 환불완료 · `rejected` 환불거절 · 반품기각 | `.status-tab` `filterListByStatus('ALL'\|'접수'\|'상담필요'\|'환불진행'\|'환불보류'\|'환불완료'\|'거절기각')` |
| `from` · `to` | Y-m-d, 기본 최근 30일 | | 접수일자(L483, id 없음 — 1칸 범위 텍스트) |
| `type` | | `cancel` 취소(전액) · `partial` 환불(부분) · `return` 반품 | 프로토 없음(개발에만) |
| `inflow` | | `mypage` 마이페이지 · `inquiry` 1:1 문의 | 유입 경로 select(L487) |
| `product` | | `within` 1개월 이내 · `over` 1개월 초과 · `book` 교재 포함 | 상품 구분 select(L495) 패키지 복합 · 인강 단과 · 실물 교재 포함 — 값 다름 |
| `deadline` | | `overdue` 기한 초과 건만 · `due` 기한 D-1 이하 | 프로토는 임박 · 초과 상단 고정 배지만 |
| `keyword` | 50자 | 주문번호 · 회원명 · 요청번호 | 검색어(L504) |

### 002 입고 확인 (RefundReceiptRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `return_tracking_no` | nullable · max 100 | 프로토 없음 |
| `received_at` | nullable · date · 현재 이전(비우면 지금) | `#sel-book-inspect` WAIT → 판정 선택이 입고를 겸함 |

### 002 반품 검수 (RefundInspectionRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `inspection_result` | required | `normal` 정상(재판매 가능) · `defective` 파본 · 불량(규칙, D-ORD-09 — 회사 귀책 고정 · 재고 미입고 · 교재비 차감 없음) · `damaged` 고객 훼손(재판매 불가) | `#sel-book-inspect` WAIT(입고 대기) · PASS(정상) · DAMAGED(파본/불량 → `defective`) · REJECT(고객 훼손 → `damaged`) → Q-RFD-9 |
| `liability` | normal일 때 required | `customer` 고객 귀책 · `company` 회사 귀책 | `#sel-fault` CUSTOMER_ONEWAY · CUSTOMER · COMPANY → Q-RFD-7 |
| `inspection_memo` | nullable · max 2000 | | 프로토 없음(배송 관리 `#inpInspectMemo`에만) |
| `photos[]` | 훼손 또는 고객 귀책이면 required → D-ORD-02로 고객 훼손(`damaged`)만 required · jpg/png · 10MB · 최대 INSPECTION_PHOTO_MAX | | `#btn-inspect-photo` · `attachRfdInspectPhoto()` · `#inspect-photo-txt`(v6.92 추가, 고객 훼손 + 사진 없음이면 승인 잠금) → ADMN-ORD-001.md Q-ORD-3 |

### 002 라인 선택
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| (환불 라인) | 개발은 환불 건 생성 때 라인 확정(`refunds` + `itemIds()`), 상세에서 체크 변경 없음. 1:1 문의는 `item_ids[]` | `#chk-lec` · `#chk-book`(상세에서 체크 토글) |

### 002 승인 · PG 취소 + P1 마이너스 전환 (RefundApprovalRequest)
| 필드 name | 규칙 | 코드값 | 프로토타입 대응 |
|---|---|---|---|
| `manual_amount` | nullable · integer 0~100,000,000. **최종 환불 현금을 덮어씀**(상한 = 산출 상한, `RefundService.php:596-618`) | | `#c-admin-adj` (프로토는 ± 가감액, Step 12) |
| `manual_reason` | manual_amount 있으면 required · 10~500자 | | `#c-admin-adj` 옆 사유 input(L916, id 없음) |
| `minus_agree` | boolean. 마이너스 전환 조건이면 필수(서버 재판정) | | `#p1-chk` |
| `minus_reason` | 공백 제외 10자 이상 · 최대 150자(MAX_MINUS_REASON) | | `#p1-reason` |
| (제출) | | | `#btn-final-submit` → `submitFinalRefund()` · P1 `confirmP1()` |

### 002 거절 (MemberReasonRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `reason` | 공백 제외 10자 · 서로 다른 글자 3개 · 200자 이하 | `#reject-notice`(고객 안내 문구 10자 이상) — `#btn-rfd-reject` → `openRfdReject()` → 모달 `#modal-rfd-reject` → `confirmRfdReject()` (v6.92, S-11) |
| `reject_reason` (규칙, S-11) | required | `legal_no_refund` 법정 환불 불가 · `inspection_fail` 교재 반품 검수 불량 · `duplicate` 중복 신청 | radio `reject-reason` LEGAL_NO_REFUND · INSPECTION_FAIL · DUPLICATE — 개발은 사유 코드 없음 |

### 002 · S1 보류 (RefundHoldRequest)
| 필드 | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `hold_reason` | required | `customer_reply` 고객 회신 대기 · `return_wait` 증정품 · 교재 반환 대기 · `payment_check` 결제 정보 확인 중 · `other` 기타 | `#hold-reason`(값 같음) — `#btn-rfd-hold`(S1 문의 패널 → `inquiries.hold.update`) · `#btn-rfd-hold2`(계산기 → `refunds.hold.update`) → 모달 `#modal-rfd-hold` → `confirmRfdHold()` (v6.92, S-11) |
| `hold_memo` | required · max 500 | | `#hold-memo` — 프로토는 기타만 필수(10자 이상) |

### S1 하위 분류 판정 (RefundInquirySubTypeRequest) · 환불 건 생성 (RefundInquiryRefundRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `sub_type` | required | `consult` 상담필요(관리자 판단) · `partial` 부분 · `full` 전액 | `inq_mode` `#radio-mode-consult` CONSULT · `#radio-mode-refund` REFUND |
| `order_id` | nullable(부분 · 전액이면 서비스가 필수 판정) | | `#unlinked-inq-bar` 🔗 이 주문에 연결 |
| `item_ids[]` | 최대 100 | | `#chk-lec` · `#chk-book` |
| `judge_reason` | max 500 | | 없음 |

### S1 분류 · 이관 (RefundInquiryCategoryRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `category_id` | required · 문의 분류 존재 | 분류 select(L743) [결제·환불] · [배송·교재 일반] · [수강·시스템] + 타 부서 이관(L748). 분류 이름은 `SJM_MASTER`에서 읽는다(CLAUDE.md 함정) |

### S1 답변 (InquiryProcessRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `action` | `draft` · `hold` · `answer` | 📨 문의 답변 저장(L789) |
| `answer_content` | answer일 때 10자 이상 | `#inq-reply-textarea` |
| `hold_reason` · `hold_until` | hold일 때 required(재개 예정일 오늘 이후) | 없음 |
| `draft_content` · `internal_memo` · `edit_reason` | nullable | 없음 |
| `notify` · `notify_skip_reason` | 답변 알림 기본 ON, 끌 때 사유 | "저장 시 고객 알림톡 자동" 문구 |

### S1 계좌 환불 [이체 완료] (AccountRefundRequest)
| 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|
| `bank_code` | 토스 은행 코드 | 케이스 4 등록 환불계좌(`#bank-mask-txt`) |
| `account_no` | `^[0-9-]{6,24}$` (숫자만 저장, 암호화) | 〃 · `unmaskBank()` |
| `account_holder` | max 50 | 〃 |
| `expected_cash` | 화면 금액 = 서버 재계산값이어야 기록 | `#c-step13` |
| `minus_agree` · `minus_reason` | 승인과 같은 기준 | P1 |

### 003 목록 검색 (GET, normalizeHistoryFilters `RefundAdminService.php:768`)
| 필드 name | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|
| `tab` | `all` 전체 · `course` 인강 · `book` 실물 교재 · `rejected` 반품 기각 · `minus` 마이너스 전환 · `grace` D+7 유예 적용 · `adjusted` 보정 거래 | 프로토 없음(필터 없는 표 L971) |
| `date_from` · `date_to` | 기본 이번 달 1일 ~ 오늘 | 없음 |
| `scope` | `full` 전액 · `partial` 부분 · `return` 반품 | 없음 |
| `pg` | `normal` · `failed` | 없음 |
| `target` · `keyword` | `name` 회원명 · `order` 주문번호 · `refund` 환불번호 | 없음 |
| `restored` · `grace` · `minus` | 체크 | 없음 |
| `admin` | 담당 관리자 id | 없음 |

### 003-S2 보정 거래 등록 (RefundAdjustmentRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| (원 환불) | URL `{refund}` 고정(완료 건만) | | `#m3f-ra-rfd` select |
| `adjustment_type` | required | `extra_refund` 추가 환불 · `clawback` 환불 회수 · `point` 포인트 보정 | `m3f-ra-type` ADD · RECOVER · POINT |
| `method` | required · 유형별 허용(METHODS_BY_TYPE) | extra_refund → `pg_cancel` PG 추가 부분 취소 · `bank_transfer` 계좌 이체 / clawback → `customer_claim` 고객 청구 / point → `point_grant` 유상 포인트 지급 · `point_deduct` 유상 포인트 차감 | `#m3f-ra-exec` 토스페이먼츠 PG 추가 부분취소 · 고객 환불계좌 무통장 입금 · 고객 과오납 환수 입금 확인 · 포인트 원장만 조정 |
| `amount` | required · 1~100,000,000 · 콤마 허용. 원 또는 P(수단으로 구분) | | `#m3f-ra-amount`(원) · `#m3f-ra-point`(P, ±) — 개발은 한 칸 |
| `reason` | required · 공백 제외 10자 · max 2000 | | `#m3f-ra-reason` · `#m3f-ra-reason-count` |
| `bank_code` · `account_no` · `account_holder` | bank_transfer일 때 서비스가 필수 판정 | | 없음 |
| `evidences[]` | jpg · png · pdf · 10MB · 최대 3개(EVIDENCE_MAX) | | 없음 |
| (정산 반영 월) | 등록일이 속한 월, 마감 월 소급 없음(`RefundAdjustmentService.php:71-74`) | | `#m3f-ra-settle` · `#m3f-ra-settle-rule` — S-10: 승인 시점 미마감 가장 이른 귀속월, 원 발생월 보존 |
| `point_kind` (규칙, S-09) | adjustment_type=point일 때 required | `paid` 적립 P · `free` 무상 P | `#m3f-ra-pkind` PAID · FREE — 개발은 유상 P만 |
| `point_expires_at` (규칙, S-09) | adjustment_type=point일 때 required · date | | `#m3f-ra-pexp` |

## 4. 목록 필터 · 정렬 · 표 컬럼

### RFD-004 요청 목록 (`refunds/index.blade.php:111`)
| 개발 컬럼 | 프로토타입 컬럼(`#rfd-list-table` L526) |
|---|---|
| 접수일 · 요청번호 | 접수번호 / 접수일시 |
| 처리 기한(반환 사유 발생일 + 5영업일, `config('admin.refund_deadline_business_days')`) | 처리기한 (5영업일) |
| 유입 | 유입 경로 |
| 회원 | 회원명 |
| 주문 / 상품 | 주문번호 · 주문 상품명 |
| 유형(취소 · 부분 · 반품) | (없음) |
| 환불(예정)액 | 원 결제금액 |
| (없음) | 고객 작성 내용 · 연관 문의 |
| 상태 · 처리 | 상태 · 처리 |

엑셀 헤더(`REQUEST_EXCEL_HEADERS`): 접수일 · 요청번호 · 유입 · 회원 · 주문번호 · 상품 · 유형 · 환불(예정)액 · 처리 기한 · 상태.

### RFD-003 완료 내역 (`refund-histories/index.blade.php:132`)
| 개발 컬럼 | 프로토타입 컬럼(L971) |
|---|---|
| 환불일 · 환불번호 | 환불완료번호 / 완료일시 |
| 주문 / 상품 · PG | 주문번호 / 토스 취소 TID |
| 회원 | 회원명 |
| (없음) | 원 결제금액 |
| 환불 현금 | 최종 PG 취소액 |
| 공제 내역 | (없음) |
| 복원 포인트 | 포인트 처리 결과 (LIFO 복원 / 마이너스 전환) |
| (상세에서 '원 결제 월 정산은 마감되어 이번 달 정산에서 공제', `CLOSED_MONTH_NOTICE`) | 정산 차감 반영월 |
| 상세 | 상세 · 사후 보정 |

엑셀 헤더(`HISTORY_EXCEL_HEADERS` `RefundAdminService.php:1310`) 24열 — 환불번호 … 적용 산식 · 규칙 버전 · 보정 합계(현금) · 보정 합계(P). PG 대사용 엑셀(`PG_EXCEL_HEADERS`): 주문번호 · PG 거래키 · 취소 요청액 · 취소 승인액 · 취소 일시.

### RFD-002 계산 명세 단계 (개발 `RefundCalculator` → `calc_snapshot.steps`, 프로토 '법정 13단계' `#c-*`)
| 개발 단계(step 라벨) | 프로토타입 대응 id |
|---|---|
| 실결제액 (인강 라인) · 인강 전액 요건 / 수강 차시 비례 차감 · 1차 환불 예정액 (인강) | `#c-lec-base` · `#c-lec-deduct` · `#c-lec-net` |
| 실결제액 (교재 라인 · 검수 정상) · (배송비 라인) | `#c-book-base` · `#c-book-net` |
| 반품 배송비 공제 (고객 귀책, 왕복 · 주문당 1회) | `#c-ship-deduct` |
| 1차 환불 예정액 합계 | `#c-step9` |
| 적립 포인트 회수 (A · B) | `#pt-a-txt` · `#pt-b-txt` · `#pt-diff-txt` · `#pt-rule-txt` |
| 포인트 보전 공제 (1P = 1원) | `#c-step10` |
| 마이너스 전환 | `#c-step11` |
| (수동 보정 — `calc.manual`) | `#c-admin-adj` · `#c-step12` |
| 최종 환불 현금 (PG 취소 전송액) | `#c-step13` |
| LIFO 포인트 복원 예정 | 완료 상세 `card('2. 포인트 처리 …')` |
| 결정 라벨 `DECISION_LABELS` full · partial · pre_shipment · awaiting_inspection · rejected · customer_fault · company_fault · with_books · kept | 라인 표(L637) '전액환불 요건' 열 |

## 5. DB 테이블 · 컬럼 (화면에 쓰는 것만, 전체는 `_index/schema.md`)
| 테이블.컬럼 | 뜻 | 화면 |
|---|---|---|
| `refunds.id` · `order_id` · `inquiry_id` · `status`(requested 접수 · in_progress 환불진행 · held 환불보류 · pg_pending 환불진행 · PG 응답 대기 · completed 환불완료 · rejected 환불거절) · `requested_at` · `approved_at` · `completed_at` | 환불 건 | 004 · 002 · 003 |
| `refunds.refund_scope`(full · partial) · `reason` · `refund_amount` | 범위 · 사유 · 예정/확정액 | 004 · 002 |
| `refunds.progress_deduction` · `delivery_fee_deduction` · `point_clawback_amount` · `point_shortage_amount` · `minus_point_amount` · `restored_point_amount` · `calc_snapshot`(rules_version · formula · steps · totals · flags · manual) | 계산 결과 · 근거 스냅샷 | 002 계산 명세 · 003 |
| `refunds.return_tracking_no` · `warehouse_received_at` · `inspection_result` · `liability` · `inspection_memo` | 반품 입고 · 검수 | 002 ③ |
| `refunds.hold_reason` · `hold_memo` · `held_at` | 보류 | 002 · S1 |
| `refunds.locked_by` · `locked_at` | 심사 중 잠금(30분) | 002 |
| `refunds.pg_cancel_no` · `pg_cancel_status`(normal · failed) | PG 취소 | 003 |
| `refunds.refund_bank_code` · `refund_account_no`(암호문) · `refund_account_holder` | 환불 계좌 | 002 `#bank-mask-txt` |
| `refunds.settlement_status` · `settlement_reflected_at` | 정산 반영 | 003 정산 차감 반영월 |
| `payment_cancels` (`refund_id`, `cancel_type`, `cancel_amount`, `idempotency_key`, `status`, `cancel_tid`, `completed_at`) | PG 취소 거래. `cancel_tid` · `idempotency_key` · `result_code`는 string(255) nullable로 넓힘(2026_10_12_000203, idempotency_key unique 인덱스는 000169 그대로) | 003 토스 취소 TID |
| `refund_adjustments` (`refund_id`, `adjustment_type`, `method`, `amount`, `bank_code`, `account_no`, `account_holder`, `reason`, `payment_cancel_id`, `point_log_id`, `idempotency_key`, `admin_id`, `created_at`=정산 반영 월 기준) | 보정 거래(원 거래 불변) | 003-S2 · `#m3f-rfd-adj-body` |
| `point_logs` (`action` clawback 등, `amount`, `balance_after`, `order_id`, `refund_id`, `idempotency_key`) · `points` | 회수 · 마이너스 · 복원 원장 | P2 `#p2-tbody` |
| `inquiries` (`category_id`, `sub_type` consult · partial · full, `assign_board`=`ADMN-RFD-002-S1`, `status` received · processing · answered · hold) | 결제 · 환불 문의 | S1 |
| `attachments` (type `inspection_photo` · `member_photo` · `adjustment_evidence`, disk `secure`) | 사진 · 근거 | 002 · S2 |
| `site_settings.return_delivery_fee` · `delivery_fee` | 반품 왕복 배송비(비면 편도 × 2) | 002 배송비 공제 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `requestArea` (Ajax 조각 `request-list`) | 004 목록 영역 | `#rfd-list-table` |
| `requestExcel` + `layerReason` | 004 엑셀 | 📥 엑셀 다운로드(L508) |
| `refundCalcArea` (Ajax 조각 `refund-calc`) | 002 계산 영역 | `#right-calc-lock` 이하 `#c-*` |
| `inspectionForm` | 002 검수 | `#sel-book-inspect` · `#sel-fault` |
| `recalculateForm` | 재계산 | 없음 |
| `approveButton` (`data-target` = `layerMinus` 또는 `layerApprove`) | 승인 | `#btn-final-submit` |
| `layerApprove` | 승인 확인(+ 수동 보정) | 없음(바로 실행) · `#c-admin-adj` |
| `layerMinus` · `minusForm` · `minusReason` · `minusAgree` · `minusSubmit` | P1 | `modal-p1` · `#p1-reason` · `#p1-chk` · `#p1-shortage` · `#p1-step9` · `#p1-minus` |
| `layerPointUsages` | P2 | `modal-p2` · `#btn-point-history` · `#p2-title` · `#p2-summary` · `#p2-tbody` |
| `layerPointLog{point_id}` | LIFO 표 행 상세 | 없음 |
| `layerHold` | 보류 | ⏸️ 환불 보류 전환 |
| `layerReject` | 거절 | 🚫 환불 거절·기각 |
| `categoryForm` · `subTypeForm` · `inquiryRecalculate` | S1 | 분류 select(L743) · `inq_mode` 라디오 · `#left-pane-inquiry` · `#inq-reply-textarea` |
| `historyArea` · `historyExcel` · `historyPgExcel` | 003 | `#view-done` 표 · 📥 PG 대사용 엑셀(L967) |
| `layerCalcSpec` | 003 상세 계산 명세 | `#rfd-done-body` |
| `adjustForm` · `adjustFields` · `bankFields` · `adjustPreview` · `adjustOpen` · `layerAdjustConfirm` · `adjustSubmit` | 003-S2 | `#rfd-adjust-form` · `#m3f-ra-*` · `#m3f-ra-preview` · `#m3f-ra-submit` |

마크업 공통: 레이어 `.layer-pop__overlay` + `id="layer…"`, 열기 `.layer__open` + `data-target`, 폼 `method="post"` + `@method('PUT')`, 입력 `.input__text` · `.select`, 버튼 `.btn__small` · `.btn__system`, 표 `.table__list`, 도움말 `.fm__help`.

## 7. 기능 차이

### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 002 3PL 창고 입고 확인(수거 송장 · 입고 일시) 단계 분리 — `RefundController.php:147-161`
- 002 검수 결과 라디오 전환 시 서버 재계산 미리보기(저장 없음) — `RefundController.php:97-110`
- 002 [재계산] · 계산 명세 인쇄 · 회원 첨부 사진 열람 — `routes/admin.php:906-911`
- 002 PG 응답 대기(`pg_pending`) 상태와 재전송 — `RefundController.php:330-332`
- 002 · S1 보류 사유 4종 + 메모 — `Refund.php:56-61` **→ 결정(v6.92 white, S-11)**: 프로토도 보류 모달(사유 4종 · 기타 메모 필수) · 거절 모달(사유 3종 + 고객 안내) 추가, 보류는 법정 · 처리 기한을 멈추지 않음. 거절 사유 코드 `reject_reason`은 개발에 없음
- 004 요청 유형(취소 · 부분 · 반품) · 처리 기한 필터 — `RefundAdminService.php:55-62`
- S1 하위 분류 판정 사유(`judge_reason`) · 답변 임시저장 · 보류 재개 예정일 · 알림 미발송 사유 — `RefundInquirySubTypeRequest.php`, `InquiryProcessRequest.php`
- 003 탭 7개 · 상세 필터(PG 실패 · 복원 · 유예 · 마이너스 · 담당자) — `RefundAdminService.php:78-86,768-786`
- 003-S2 보정 근거 파일 최대 3개 · 계좌 이체 계좌 입력 · 중복 등록 방지 · 회원 안내 알림(`TPL_RFD_ADJUST`) — `RefundAdjustmentService.php:37-43`

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 002 상세에서 라인 체크(`#chk-lec` · `#chk-book`)로 환불 범위 변경 — 개발은 신청 때 라인 확정
- 002 수동 보정 ± 가감(`#c-admin-adj`) — 개발은 최종액 덮어쓰기(이름 · 값 다름 표 참고)
- 002 법정 환불 불가 하드락(인정진도율 50% 초과 · 기간 1/2 경과) — 프로토 `recalcDetail()` L1380 · L1440 → Q-RFD-3 **→ 결정(v6.87 white, D-ORD-03): 인강 부분환불 = 실결제 × (전체 − 학습 회차) ÷ 전체, 원 단위 절사(평생교육법 시행령 별표 3 비고 4). 위약금 · 기간 경과 차감 · 1/2 경과 환불 불가 삭제 — 개발 산식과 같아짐(통합 설계서 v3.2.22).**
- 002 왼쪽 탭 '고객 환불 신청서 원문' · '연관 1:1 문의 원문 & 답변'을 한 화면에 — 개발은 환불 상세 / 문의 상세 두 화면
- 003 목록에서 원 환불을 골라 보정 등록(`openRefundAdjustPage(null,'list')` L966) — 개발은 완료 상세에서만
- 003-S2 금액 · 포인트 동시 입력, 무상 P 포인트 보정 — 개발은 한 거래 = 한 수단, 포인트는 유상만(`refund-histories/adjust.blade.php:61`) **→ 결정(v6.92 white, S-09)**: 포인트 단독 보정은 현금 0 · 포인트 구분(적립 P / 무상 P) · 만료일 필수 — 개발 `point_kind` · `point_expires_at` 추가 필요
- 003-S2 보정 전표 반영 기준월 — 개발은 등록일이 속한 월 **→ 결정(v6.92 white, S-10)**: 승인 시점 미마감 가장 이른 귀속월(원 발생월이 미마감이면 그 달), 원 발생월을 전표에 보존
- 002 계산기 Step 7-1 강좌 사용 포인트 복원(v6.92 신설) **→ 결정(v6.92 white, S-12)**: 복원 P = ⌊라인 사용 포인트 × 인강 환불액 ÷ 라인 결제액⌋, 나머지 현금 — 개발 '유상만 미수강 비율 복원'과 비율 방식은 같음(무상 P 처리는 Q-RFD-6)
- 002 케이스 4 마이페이지 직접 신청 건의 휴대폰 익월 계좌 폴백 — 개발은 1:1 문의 건만 계좌 환불 경로 → Q-RFD-8

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
| 프로토타입 | 개발 |
|---|---|
| 상태 탭 한글(접수 · 상담필요 · 환불진행 · 환불보류 · 환불완료 · 거절기각) | `tab` `requested` · `consult` · `progress` · `held` · `completed` · `rejected` |
| 상품 구분 패키지 복합 · 인강 단과 · 실물 교재 포함 | `product` `within`(1개월 이내) · `over`(1개월 초과) · `book`(교재 포함) |
| 유입 경로 3옵션 | `inflow` `mypage` · `inquiry` |
| `#sel-book-inspect` WAIT · PASS · DAMAGED · REJECT | 입고 `received_at`(WAIT 해제) + `inspection_result` `normal` · `defective`(규칙, D-ORD-09) · `damaged` — 프로토 DAMAGED = 개발 `defective`, 프로토 REJECT = 개발 `damaged` |
| `#sel-fault` CUSTOMER_ONEWAY · CUSTOMER · COMPANY | `liability` `customer` · `company` |
| `inq_mode` CONSULT · REFUND | `sub_type` `consult` · `partial` · `full` |
| `#c-admin-adj` (± 가감, 사유 1칸) | `manual_amount`(최종 현금 절대값) · `manual_reason`(10~500자) |
| `#p1-reason` · `#p1-chk` | `minus_reason`(10~150자) · `minus_agree` |
| `m3f-ra-type` ADD · RECOVER · POINT | `adjustment_type` `extra_refund` · `clawback` · `point` |
| `#m3f-ra-exec` 4옵션 | `method` `pg_cancel` · `bank_transfer` · `customer_claim` · `point_grant` · `point_deduct` |
| 보정 번호 `ADJ-YYYYMMDD-NNN` (`nextAdjId` L1716) | `refund_adjustments.id`(채번 형식 없음, 확인 필요) |
| 환불 번호 `RFD-2026-001098` | `Refund::displayNo()`(S1 메시지 `RFD-{id}`, 형식 확인 필요) |
| 법정 13단계 | 개발 `RULES_VERSION` `v12-2026-10-19` 단계(17단계 규칙 기반, 4절 표) |

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)

| 번호 | 질문 | 정본 근거 | 개발 근거 |
|---|---|---|---|
| Q-RFD-1 | 인강 부분 환불 산식 — 정본은 `실결제액 − 위약금(10%) − 실결제액 × MAX(경과일/전체일, 인정진도율)`, 개발은 `실결제액 × (1 − 본 회차 ÷ 전체 회차)`(위약금 · 기간 비례 없음, 원 단위 절사). 개발 주석은 "결정이 우선"이라 하나 정본(설계서 · 프로토) 갱신 기록 확인 필요 | 프로토 `recalcDetail()` L1366 · L1380-1382, `docs/산준모닷컴 구축 통합 상세 설계서.md` L347(3.3.2 인강 부분환불) | `app/Services/Refund/RefundCalculator.php:23`, `:229` | **→ 결정(v6.87 white, D-ORD-03): 인강 부분환불 = 실결제 × (전체 − 학습 회차) ÷ 전체, 원 단위 절사(평생교육법 시행령 별표 3 비고 4). 위약금 · 기간 경과 차감 · 1/2 경과 환불 불가 삭제 — 개발 산식과 같아짐(통합 설계서 v3.2.22).**
| Q-RFD-2 | 인강 전액 환불 요건 — 정본 "결제 7일 이내 AND 맛보기 제외 2강 이하 수강", 개발 "7일 이내 AND 수강 0초(1초라도 재생하면 부분)" | 프로토 L647 '전액환불 요건 (7일 & 2강 이하)', 설계서 L346 | `RefundCalculator.php:207` |
| Q-RFD-3 | 법정 환불 불가 — 정본은 인정진도율 50% 초과 또는 수강기간 1/2 경과면 인강 환불 승인 불가(하드락). 개발은 막지 않고 진도 비례로 계산, 원 수강기간이 끝난 경우만 전액 차감 | 프로토 L1380 · L1440(`lecBlocked`), 설계서 L347 단서 | `RefundCalculator.php:219` | **→ 결정(v6.87 white, D-ORD-03): 인강 부분환불 = 실결제 × (전체 − 학습 회차) ÷ 전체, 원 단위 절사(평생교육법 시행령 별표 3 비고 4). 위약금 · 기간 경과 차감 · 1/2 경과 환불 불가 삭제 — 개발 산식과 같아짐(통합 설계서 v3.2.22).**
| Q-RFD-4 | 마이너스 전환 때 현금 — 정본은 부족분이 예정액보다 크면 **예정액 전액을 선차감(현금 0원)하고 초과분만** 마이너스 적재. 개발은 **현금 100% 지급 + 부족분 전액** 마이너스 적재 | 프로토 L1404-1412, P1 문구 L1161-1162, 설계서 L350 ③ | `RefundCalculator.php:139-140` |
| Q-RFD-5 | 원 주문 적립 회수 순서 — 정본은 보유 가용 포인트에서 **무상 P → 적립 P** 순으로 먼저 차감. 개발은 **이 주문 적립 건부터, 그다음 소멸 임박순** | 프로토 L1213 · L1946, 설계서 L350 ① | `app/Services/Point/PointLedgerService.php:451` |
| Q-RFD-6 | 결제에 쓴 무상 P의 환불 처리 — 정본은 사용 포인트를 **적립 P → 무상 P 순으로 LIFO 복원**(만료분 복원일 + 7일 유예). 개발은 **유상만 미수강 비율로 복원, 무상은 소멸** | 프로토 L1212 · L1938 | `RefundCalculator.php:25`, `refund-histories/adjust.blade.php:61` |
| Q-RFD-7 | 반품 배송비 고객 귀책 공제 — 정본은 단순변심 **편도 3,000원**(유료배송 주문) / 무료배송 혜택 취소 **왕복 6,000원**, 주문당 1회. 개발은 고객 귀책이면 **항상 왕복**(설정값, 비면 편도 × 2), 귀책 코드도 2종뿐 | 프로토 L834-838 `#sel-fault`, ORD-001 L939-943, 설계서 L348, `docs/screen_spec/07_환불관리_ADMN-RFD.md:1496` | `app/Services/Refund/RefundInputBuilder.php:74`, `RefundCalculator.php:110-117`, `app/Models/Refund.php:74-86` |
| Q-RFD-8 | PG 직취소 불가(휴대폰 익월 등) 계좌 폴백 범위 — 정본 케이스 4는 **마이페이지 직접 신청** 건도 등록 환불계좌로 현금 폴백. 개발은 **1:1 문의 유입 건만** 계좌 환불 경로가 있고, 마이페이지 건은 "관리자 수기 환불에서 그때 계좌를 받는다"는 주석뿐(경로 확인 필요) | 프로토 L1307-1310 · L1459, `submitFinalRefund()` L1479 | `RefundController.php:298`, `app/Services/Admin/RefundInquiryService.php:239-242`, `app/Services/Front/MyRefundService.php:493` |
| Q-RFD-9 | 파본 · 불량(회사 귀책) 반품 교재의 재고 — 정본은 '파본/불량 합격'을 **재고 미산입 · 폐기**로 따로 두고, 정상 합격만 재고 +1. 개발은 검수 2값(정상 · 훼손)이라 **정상 + 회사 귀책도 재입고** | 프로토 L825-829 `#sel-book-inspect` | `app/Services/Refund/RefundService.php:254` **→ 결정(v6.92 white, D-ORD-09)**: 검수 3값 정상 · 파본/불량(회사 귀책 고정 · 재고 미입고 · 교재비 차감 · 반품 배송비 없음) · 고객 훼손 — 개발 `inspection_result`에 `defective` 추가, 정상 + 회사 귀책 재입고와 분리 |
