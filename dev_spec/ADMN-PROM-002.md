# ADMN-PROM-002 쿠폰 마스터 관리 · 포인트 정책 — 개발 명세

- 프로토타입 파일: prototype_clean/ADMN-PROM-002_baseline.html (원본 상태: 18d66c1 v6.92)
- 맞춘 개발 커밋: d562524a (2026-10-26)
- 포함 화면: ADMN-PROM-002(쿠폰 마스터 등록 · 목록), ADMN-PROM-002-P1(정액 감면 Cap 초과 경고), ADMN-PROM-003(포인트 정책 설정 · 원장 내역)
- 개발 진행: PROM-002 · P1 구현(담당 노승원). PROM-003 일부 — 별도 화면 없이 사이트 설정(`admin.site-settings`)의 "③ 포인트" 구획으로 구현, 포인트 원장 목록 화면은 개발 미구현(d562524a 기준)
- 구조 차이 요지: 프로토타입은 한 HTML 안 서브뷰 3개(`view-list` 쿠폰 목록 · `view-form` 등록/수정 · `view-point` 포인트 정책 · 원장) + 모달 `modal-p1` · `modal-point`. 개발은 쿠폰 목록 · 등록/수정 · 상세가 별도 페이지, 포인트 정책은 사이트 설정 화면.

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |
|---|---|---|
| `admin.coupons.index` | 쿠폰 관리 | CouponController 엑셀 `menuKey: 'admin.coupons.index'`(:67). 메뉴 행 데이터는 DB |
| `admin.site-settings.index` | 사이트 설정(포인트 정책 포함) | routes/admin.php:1163-1164. 별도 포인트 정책 메뉴는 없음 |
| `admin.members.index`(회원관리) | — | 관리자 수동 무상 포인트 지급 · 차감은 회원 상세 `admin.members.points.store`(회원관리 등록 권한, ADMN-USER-002-P1) |

- ROUTE_PERMISSIONS 예외 없음.
- 접미사 판정 주의: 지급 양식 `admin.coupons.issue-template.create`(빈 양식이라 등록 권한), 대상 수 미리보기 `target-count.index`(조회), 지급 `issue.store`(등록), 발급 중지 `status.update` · 긴급 사용 중지 `emergency-status.update` · 공개 전환 `visibility.update` · 비고 `memo.update`(수정), 비고 이력 `memo-history.index`(조회).
- 긴급 사용 중지는 최고 관리자만(CouponService::emergencySuspend:592 `abort_unless isSuperAdmin`). 목록은 `isSuper` 로 버튼 표시를 가린다(CouponController:42).
- 엑셀(발급 · 사용 현황)은 회원 식별정보가 들어가 다운로드 권한 + 반출 사유.

## 2. 화면별 라우트
URL 접두사 `/{admin}` = `config('admin.prefix')`(기본 `sj-admin`).

### ADMN-PROM-002 쿠폰 목록 · 상세
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 목록 · 현황 | GET | `/{admin}/coupons` | `admin.coupons.index` | 조회 | CouponController@index |
| 발급 · 사용 현황 엑셀(사유) | GET | `/{admin}/coupons/download` | `admin.coupons.download` | 다운로드 | CouponController@download |
| 상세(지급 회원 목록) | GET | `/{admin}/coupons/{coupon}` | `admin.coupons.show` | 조회 | CouponController@show |
| 지급(ID 입력 · 엑셀) | POST | `/{admin}/coupons/{coupon}/issue` | `admin.coupons.issue.store` | 등록 | CouponController@issue |
| 지급 대상 엑셀 양식 | GET | `/{admin}/coupons/issue-template` | `admin.coupons.issue-template.create` | 등록 | CouponController@issueTemplate |
| 발급 중지 | PUT | `/{admin}/coupons/{coupon}/status` | `admin.coupons.status.update` | 수정 | CouponController@suspend |
| 긴급 사용 중지(최고 관리자) | PUT | `/{admin}/coupons/{coupon}/emergency-status` | `admin.coupons.emergency-status.update` | 수정 | CouponController@emergencySuspend |
| 공개/비공개 전환 | PUT | `/{admin}/coupons/{coupon}/visibility` | `admin.coupons.visibility.update` | 수정 | CouponController@updateVisibility |
| 비고 저장(JSON) | PUT | `/{admin}/coupons/{coupon}/memo` | `admin.coupons.memo.update` | 수정 | CouponController@updateMemo |
| 비고 이력(JSON) | GET | `/{admin}/coupons/{coupon}/memo-history` | `admin.coupons.memo-history.index` | 조회 | CouponController@memoHistories |

### ADMN-PROM-002 쿠폰 등록 · 수정 (별도 페이지) / 002-P1 Cap 초과 경고(저장 응답 모달)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 등록 폼 | GET | `/{admin}/coupons/create` | `admin.coupons.create` | 등록 | CouponController@create |
| 등록 저장 | POST | `/{admin}/coupons` | `admin.coupons.store` | 등록 | CouponController@store |
| 수정 폼 | GET | `/{admin}/coupons/{coupon}/edit` | `admin.coupons.edit` | 수정 | CouponController@edit |
| 수정 저장 | PUT | `/{admin}/coupons/{coupon}` | `admin.coupons.update` | 수정 | CouponController@update |
| 타겟 그룹 대상 수(JSON) | GET | `/{admin}/coupons/target-count` | `admin.coupons.target-count.index` | 조회 | CouponController@targetCount |

- P1 은 별도 라우트가 없다. 저장 검증에서 할인값이 상한을 넘으면 `cap_alert` 오류를 붙여 돌려보내고, 폼이 `couponCapAlert` 레이어를 띄운다(CouponRequest:125-143, coupons/form.blade.php:236-).

### ADMN-PROM-003 포인트 정책 설정 (사이트 설정 화면의 구획)
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |
|---|---|---|---|---|---|
| 설정 화면(포인트 정책 · 변경 이력) | GET | `/{admin}/site-settings` | `admin.site-settings.index` | 조회 | SiteSettingController@edit |
| 설정 저장 | PUT | `/{admin}/site-settings` | `admin.site-settings.update` | 수정 | SiteSettingController@update |
| 수동 무상 포인트 지급 · 차감 | POST | `/{admin}/members/{member}/points` | `admin.members.points.store` | 등록(회원관리) | MemberController@storePoint |
| 포인트 원장 목록 | — | 개발 미구현, 규칙 기반 명명: `GET /{admin}/points` · `admin.points.index`(규칙) | 조회(규칙) | PointController@index(규칙) |

## 3. 폼 필드 · 검증
### 쿠폰 등록 · 수정 (CouponRequest · CouponUpdateRequest)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |
|---|---|---|---|
| `name` | required max:30(Coupon::MAX_NAME_LENGTH) | 쿠폰함 · 주문서 노출 | `f-name` |
| `code` | 등록만 · nullable max:50 · `^[A-Z0-9_]+$`(대문자 정규화) · 중복 불가. 수정 불가 | 코드 입력형 쿠폰 코드 | `f-code` · 사용자 입력 코드 |
| `is_public` | nullable boolean | 1=공개 · 0=비공개 | 없음 |
| `type` | required in percent,fixed | percent=정률(%) · fixed=정액(원) | `setCouponType('RATE'/'FIXED')` |
| `discount_value` | 정률 1~40 정수 / 정액 1,000~200,000 · 1,000원 단위. 초과 시 `cap_alert`(P1) | 할인값 (`coupon-discount`) | `f-val` |
| (감면 한도 Cap) | 입력 없음 — 200,000원 고정(Coupon::DISCOUNT_CAP, 결제 시 강제) | | 감면 한도(Cap) 표시 |
| (도서정가제) | 입력 없음 — exclude_book 서버가 1 고정 | | 도서정가제 체크(잠금) |
| `min_order_amount` | nullable integer ≥0 (0 · 비움 = 제한 없음) | | `f-min-order` |
| `expire_mode` | required in days,fixed | days=발급일 기준 D+N · fixed=절대 기간(종료일) | `setExpMode('DN'/'ABS')` |
| `expire_days` | days 일 때 required 1~3650 (기본 21) | | `f-exp-days` |
| `expire_at` | fixed 일 때 required · 오늘 이후(그날 자정까지) | 종료일 하나 | `f-exp-start` · `f-exp-end`(시작 · 종료 두 칸) |
| `max_issue_count` (`coupon-max-issue`) | nullable ≥1 (비우면 무제한) | 총 발급 한도 | `f-limit-total` |
| `unlimited` (`coupon-unlimited`) | nullable boolean | 무제한 체크 | `f-limit-unlim` |
| `max_per_user` | nullable ≥1 (비우면 1) | 1인당 발급 매수 | `f-limit-per` |
| `allow_with_point` | nullable boolean(기본 허용) | 포인트와 함께 사용 | `f-dup-point` |
| (다른 쿠폰 중복) | 폼 입력 없음 — allow_stack_coupon 기본 0(1주문 1쿠폰) | | v6.92: `f-one-coupon-fixed` '1주문 1쿠폰 (다른 쿠폰과 함께 쓸 수 없음 · 고정)' 표시만(`f-dup-coupon` 삭제) — 개발과 같음 |
| `target_scope` | required in all,selected | all=전체 상품 · selected=카테고리 · 개별 상품 지정 | `setTargetScope('ALL'/'CAT'/'ITEM')` |
| `target_category_ids[]` / `target_course_ids[]` / `target_package_ids[]` | selected 일 때 하나 이상 · 각각 최대 200/500/500 · 존재 | 카테고리 · 강좌 · 패키지(교재 없음) | 카테고리 select + "추가" |
| `issue_method` | required in auto,bulk,code | auto=자동 발급(가입 웰컴) · bulk=수동 대량 발급 · code=코드 입력형 | `setIssueMethod('AUTO'/'BULK'/'CODE')` |
| `target_group_id` (`coupon-target-group`) | nullable · 사용 중 회원 그룹 · 태그 | 수동 대량의 타겟 그룹(ADMN-USER-006) | `tg-select` |
| `scheduled_at` | nullable · 지금 이후(수정 때 같은 값은 허용) | 발급 예약 시각 | 발급 예약 datetime |
| `send_notification` | (폼 필드 있음, 검증 규칙 목록에는 없음 — 확인 필요) | 발급 알림톡 동시 발송 | 알림톡 체크박스 |
| `memo` | nullable max:500 | 비고 | 없음 |
| `form_token` | 등록만 required size:40 (1회용, 중복 저장 방지) | | 없음 |
- 발급 이력이 있으면 종류 · 할인값 · 유효기간을 잠근다(Coupon::LOCKED_AFTER_ISSUE).

### 지급 `couponIssueForm` (CouponIssueRequest)
| 필드 name | 규칙 | 프로토타입 대응 |
|---|---|---|
| `user_ids_text` | nullable max:20000 (회원 식별자 줄 입력) | 없음(수동 대량은 그룹 선택만) |
| `user_ids_file` | nullable xlsx 2MB(실제 바이트) · 양식 `issue-template.create` | 없음 |

### 목록 행 동작 (컨트롤러 인라인 검증)
| 폼 | 필드 | 규칙 | 프로토타입 대응 |
|---|---|---|---|
| 발급 중지 `couponSuspendForm` | `memo` | nullable max:500(중지 사유 → 비고) | `pauseCurrentCoupon()`(폼 안 버튼) |
| 긴급 사용 중지 `couponEmergencyForm` | `reason` | required 10~500 | 없음 |
| 공개 전환 | `is_public` | required boolean | 없음 |
| 비고 저장 | `memo` | nullable max:500 | 없음 |

### 포인트 정책 (SiteSettingRequest 의 ③ 포인트, ADMN-PROM-003)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 |
|---|---|---|---|
| `welcome_point` | required 0~100000 (0=미지급) | 신규 가입 축하금(DI 생애 1회) | 웰컴 포인트 지급액 |
| `point_earn_rate` | nullable 0~10(%) | 유상 적립율 | 강좌 결제 기본 적립률 |
| `earn_rounding` | in CODE_OPTIONS | ceil 올림 · floor 버림 · round 반올림 | 없음 |
| `earn_confirm_timing` | in paid 만 | 결제 승인 즉시 | 없음 |
| `free_point_expire_years` / `paid_point_expire_years` | required 1~10 | 무상 · 유상(포인트) 유효기간(년) | "포인트 사용 기준 · 유효기간" |
| `deduct_priority` | in CODE_OPTIONS | expire_asc_free_first(만료 임박순 · 같은 날 무상 우선) | 없음 |
| `expire_notice_days` | 0~90 (0=미발송) | 소멸 사전 안내 일수 | 없음 |
| `expire_notice_alimtalk` / `expire_notice_lms` / `expire_notice_email` | boolean | 소멸 안내 채널 | 없음 |
| `paid_restore_grace_days` | 0~255 | 만료 유상 포인트 부활 유예 | 없음 |
| `book_point_rate_limit` | 0~100 | 도서 적립률 상한(교재 라인 적립, ⑤ 도서 구획) | "교재 · 배송비 적립 제외" 문구 |
| `point_change_reason` | max:200. 포인트 항목이 바뀌면 필수(서비스) | 변경 사유 → admin_logs | 없음 |
| (없음) | | | `pol-review`(일반 후기 승인 P) · `pol-best`(베스트 · 합격수기 P) · `pol-cap`(무상 잔액 상한) |

### 수동 무상 포인트 지급 (MemberPointRequest, 회원 상세)
`pt-member` · `pt-amt` 모달에 대응. 개발은 회원 상세(ADMN-USER-002-P1)에서 `admin.members.points.store`, 사유 `reason`(MemberReasonRequest 10~200자).

## 4. 목록 필터 · 정렬 · 표 컬럼
### 쿠폰 목록 (CouponService::normalizeFilters:46-64)
- 필터: `keyword`(쿠폰명 · 코드, 100자) · `type`(percent/fixed) · `issue_method`(auto/bulk/code) · `status`(issuing 발급중 · suspended 발급중지 · ended 기간종료) · `date_from` · `date_to`(등록일).
- 현황(scorecard): operating 운영중 쿠폰 · issued 총 발급 · used 사용 · rate 사용률 · expired 미사용 소멸.
- 표 컬럼(개발): No · 쿠폰명 · 종류 · 할인값 · Cap · 발급방식 · 유효기간 · 발급/사용/소멸 · 사용률 · 상태 · 비고 · 관리(행 메뉴 `rowActionMenu`: 지급 · 발급 중지 · 긴급 중지 · 공개 전환 · 비고 이력).
- 프로토타입: No · 쿠폰명 · 종류 · 할인값 · Cap(고정) · 발급방식 · 유효기간 · 발급/사용/소멸 · 사용률 · 상태 · 관리 — 비고 열만 개발에 더 있음. 필터 `q-keyword` · `q-type` · `q-method` · `q-status` · 등록일.

### 쿠폰 상세 (coupons/view.blade.php)
- 지급 회원 표: No · 아이디 · 회원명 · 지급일 · 만료일 · 사용여부 · 사용일. 필터 `uc_status`.

### 포인트 원장 (ADMN-PROM-003)
- 개발 미구현, 규칙 기반 명명. 프로토타입 표: 거래 ID/일시 · 회원명(ID) · 원장 구분 · 변동 유형 · 변동 포인트 · 거래 후 잔액 · 상세 사유. 개발 데이터는 point_logs(action · amount · balance_after · order_id · refund_id · admin_id · reason). 회원별 내역은 회원 상세에 있음 — 추정.
- 사이트 설정 화면의 포인트 정책 변경 이력: `pointHistory`(SiteSettingService::pointPolicyHistory, admin_logs 기반, 쪽 이름 `point_log_page`).

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |
|---|---|---|---|
| coupons.name / code / type | | 쿠폰명 · 코드(코드형) · percent/fixed | 목록 · 폼 |
| coupons.discount_value / max_discount_amount | int | 할인값 · (정률 상한, 현재 Cap 상수로 강제) | 할인값 · Cap |
| coupons.min_order_amount | int | 최소 결제금액 | 사용 조건 |
| coupons.expire_days / expire_at | int / date | D+N 일수 · 종료일 | 유효기간 |
| coupons.status | string(20) | active 사용중 · disabled 발급중지(저장값). 목록 표시는 issuing · suspended · ended(종료일 반영) | 상태 |
| coupons.emergency_suspended_at | timestamp | 긴급 사용 중지(보유분 사용 불가) | 상태 |
| coupons.max_issue_count / issued_count / max_per_user | unsignedInteger(max_issue_count만 nullable) | 총 한도(NULL=무제한) · 발급 수 · 1인당 | 수량 한도 · 발급 |
| coupons.is_public | tinyint | 사용자 페이지 공개 | 공개 |
| coupons.memo | string(500) | 비고(중지 사유 등) | 비고 |
| coupons.exclude_book | tinyint | 도서정가제 자동 바인딩(서버 1 고정) | 도서정가제 |
| coupons.allow_stack_coupon / allow_with_point | tinyint | 다른 쿠폰 중복(기본 0) · 포인트 병용(기본 1) | 중복 사용 |
| coupons.issue_method / target_group_id / scheduled_at / send_notification | string(20) 기본 bulk / unsignedBigInteger nullable / dateTime nullable(NULL=즉시) / tinyint 기본 0 | auto · bulk · code / user_groups.id / 발급 예약 / 알림톡 | 발급 방식 |
| coupons.target_type / target_id | | 옛 단일 대상(all · course · package · category, 옛 instructor · delivery 는 폐지) | — |
| coupon_targets.target_type / target_id | | 대상(all · category · course · package · book) 복수 | 적용 대상 |
| coupon_issue_batches.* | | 지급 배치(수동 · 엑셀 · 텍스트, 성공 · 실패 수) | 지급 결과 |
| user_coupons.status / issued_at / expires_at / used_at / used_order_id / discount_amount | | 회원 보유 쿠폰(issued · used · expired 등) | 상세 지급 회원 표 · 발급/사용/소멸 |
| coupon_memo_histories.memo / admin_id / created_at | | 비고 변경 이력 | 비고 이력 모달 |
| order_items.coupon_cap_applied | boolean | Cap 에 깎였는지(P1 사양 · 정산 대사) | — |
| site_settings.welcome_point · point_earn_rate · earn_rounding · earn_confirm_timing · free_point_expire_years · paid_point_expire_years · deduct_priority · expire_notice_days · expire_notice_alimtalk · expire_notice_lms · expire_notice_email · paid_restore_grace_days · book_point_rate_limit · earn_book_line | | 포인트 정책값(SiteSetting::POINT_POLICY_FIELDS) | 포인트 정책 |
| withdrawn_users_di.welcome_granted | tinyint | 웰컴 혜택 DI 생애 1회 판정 | — |
| points.type / amount / balance / source / expires_at / admin_id / memo | | 적립 건(paid · free, signup · purchase · event · cs · restore · clawback) | 원장 |
| point_logs.action / amount / balance_after / order_id / refund_id / admin_id / reason | | 원장(earn · use · expire · clawback · restore · offset) | 원장 표 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |
|---|---|---|
| `coupon-discount` · `discount-unit` · `discount-max` · `discount-inline-error` · `cap-sim` · `sync()` · `currentType()` | 할인값 입력 · 단위 · 상한 · Cap 예시 | `f-val` · `sim-lec` · `sim-book` |
| `coupon-auto-expire` | 유효기간 방식 | `setExpMode()` |
| `coupon-max-issue` · `coupon-unlimited` · `syncUnlimited()` | 발급 한도 | `f-limit-total` · `f-limit-unlim` |
| `coupon-target-pick` | 대상 지정 구획 | `setTargetScope()` |
| `coupon-target-group` · `coupon-target-count` · `previewCount()` · `syncIssueMethod()` | 타겟 그룹 · 대상 수 | `tg-select` · "그룹 선택 · 미리보기" |
| `couponCapAlert` · `couponCapAlertOk` (`.layer-pop__overlay.layer_pop--show`) | P1 Cap 초과 경고 | `modal-p1` · `modal-p1-body` · `focusBackToDiscountInput()` |
| `couponIssueModal` · `couponIssueForm` · `issueCouponName` · `openIssue()` | 지급 모달 | 없음 |
| `couponSuspendModal` · `couponSuspendForm` · `suspendCouponName` · `openSuspend()` | 발급 중지 모달 | `pauseCurrentCoupon()` |
| `couponEmergencyModal` · `couponEmergencyForm` · `emergencyCouponName` · `openEmergency()` | 긴급 사용 중지 | 없음 |
| `memoHistoryModal` · `memoHistoryCoupon` · `memoHistoryList` · `memoHistoryMore` · `saveMemo()` · `openHist()` · `loadHist()` | 비고 · 이력 | 없음 |
| `rowActionMenu` · `openRowMenu()` · `positionRowMenu()` · `closeRowMenu()` | 행 동작 메뉴 | 행 "상세/수정" 버튼 |
| `submitVisibility()` | 공개 전환 | 없음 |
| `couponSuspendLayer`(edit 페이지) | 수정 화면의 발급 중지 | `pauseCurrentCoupon()` |
| `.layer__open[data-target="layerReason"]` | 엑셀 반출 사유 | `downloadExcelReport()` |

하위 화면: 개발 등록 · 수정 = 별도 페이지(create/edit), 상세 = 별도 페이지(show, view.blade.php), P1 = 저장 응답으로 뜨는 레이어. 프로토타입은 `view-list` · `view-form` · `view-point` 섹션 전환(`switchSubView`) + `modal-p1`(입력 중 시연) · `modal-point`.

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
- 쿠폰 상세(지급 회원 목록 · 사용여부 필터), 지급(회원 ID 텍스트 · 엑셀 업로드 + 양식).
- 긴급 사용 중지(최고 관리자, 보유분까지), 공개/비공개 전환, 비고 · 비고 이력, 행 동작 메뉴.
- 발급 이력 후 종류 · 할인값 · 유효기간 잠금, 1회용 form_token.
- 포인트 정책: 단수 처리 · 적립 확정 시점 · 차감 우선순위 · 소멸 안내(일수 · 채널) · 부활 유예 · 도서 적립률 상한 · 변경 사유 · 정책 변경 이력.

### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
- 포인트 원장 전체 목록(ADMN-PROM-003 원장 표).
- 포인트 정책의 후기 보상 금액(`pol-review` · `pol-best`)과 무상 포인트 잔액 상한(`pol-cap`) — 개발 site_settings 에 해당 칸 없음(우수 후기 포인트는 BRD-005-S1 에서 금액 직접 입력).
- 다른 쿠폰과 중복 사용 허용 체크(`f-dup-coupon`) — 개발은 컬럼만 있고 폼 입력 없음. **→ 결정(v6.92 white, D-BRD-04)**: 체크 삭제 → '1주문 1쿠폰' 고정 표시, 포인트 병용만 쿠폰별 — 차이 없음. '기획전 차단(PROM-001-S1) 우선' 안내도 삭제
- 절대 기간의 시작일(`f-exp-start`) — 개발은 종료일만.
- Cap 시뮬레이터 입력(`sim-lec` · `sim-book`) — 개발은 고정 예시 문구(`cap-sim`).
- P1 입력 중 즉시 경고(개발은 저장 시 서버 검증 후 경고).

### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)
- 쿠폰 종류: RATE → `percent`, FIXED → `fixed`.
- 발급 방식: AUTO → `auto`, BULK → `bulk`, CODE → `code`.
- 유효기간: DN → `expire_mode=days`(`expire_days`), ABS → `expire_mode=fixed`(`expire_at`).
- 적용 대상: ALL → `target_scope=all`, CAT · ITEM → `target_scope=selected` + `target_category_ids[]` · `target_course_ids[]` · `target_package_ids[]`.
- 사용 상태: 발급중/ACTIVE → `issuing`, 발급중지 → `suspended`(저장 disabled), 기간종료 → `ended`.
- 정률 상한 · 정액 상한: 프로토타입 P1 시연값(정액 250,000 · 정률 45%) 기준 → 개발 정률 40% · 정액 200,000원(1,000원 단위) · Cap 200,000원.
- 포인트 정책 화면 위치: 쿠폰 화면 서브뷰 → 개발 사이트 설정 `admin.site-settings`.
- 쿠폰명 최대 30자.

## 8. 정책 질문 (처리 결과 — 2026-10-27 white 전부 결정)
> 정본 대조 결과(2026-10-27): 아래 질문 중 정본에 답이 있는 것은 정본 근거로 처리했고, 결정이 필요한 것만 `scripts/qa/reports/review/findings/devspec/POLICY_D_BRD.md` 의 D-BRD 항목으로 올렸다. 분류표는 그 파일 "질문이 아닌 것" 절.

- 포인트 정책을 쿠폰 화면(프로토타입 PROM-003 서브뷰)에 둘지, 개발처럼 사이트 설정 안에 둘지 확인 필요. **→ 정본대로(POLICY_D_BRD A, 통합설계서 L166 · L113 · L163)**: 포인트 정책은 마케팅/프로모션 메뉴(PROM-003, 프로토는 PROM-002 서브뷰) — 저장소는 같게, 메뉴 · 권한을 프로모션으로(개발팀 전달)
- 후기 보상 포인트 고정액(일반 · 베스트)과 무상 포인트 잔액 상한을 정책값으로 둘지 확인 필요 — 개발에 없음. **→ 정본대로(POLICY_D_BRD A, 통합설계서 L166 · v3.2.14)**: 후기 보상 · 베스트 후기 보상 · 무상 P 잔액 상한(기본 200,000P)은 정책값 — 개발팀 전달(세 값 + 지급 때 상한 검증)
- 다른 쿠폰과 중복 사용(allow_stack_coupon)을 관리자가 켤 수 있게 할지 확인 필요 — 개발은 컬럼 기본 0, 폼 없음. **→ 결정(v6.92 white, D-BRD-04)**: 켤 수 없음 — 1차 '1주문 1쿠폰' 고정(개발 기본 0 그대로)
- 포인트 원장 전체 조회 화면이 필요한지 확인 필요. **→ 정본대로(POLICY_D_BRD A, 통합설계서 L113 · L155~165)**: 적립 P / 무상 P 분리 전체 원장 조회 필요 — 개발팀 전달

## 출처
- routes/admin.php:999, 1032-1053, 1163-1164 (dev_spec/_index/routes.md)
- app/Http/Controllers/Admin/CouponController.php:35-58, 60-98, 99-121, 122-146, 147-187, 188-242, 243-347
- app/Http/Requests/Admin/CouponRequest.php:125-143, 194 · CouponUpdateRequest.php · CouponIssueRequest.php · ReasonRequest.php
- app/Services/Admin/CouponService.php:46-64, 77-81, 546, 590-613
- app/Repositories/Admin/CouponRepository.php:389-392
- app/Models/Coupon.php:24-140
- database/migrations/2026_09_08_000084_add_coupon_columns.php:26-65 · 2026_09_08_000085_add_point_policy_settings.php · 2026_10_02_000183_add_coupon_cap_applied_to_order_items.php
- app/Http/Controllers/Admin/SiteSettingController.php:53 · app/Http/Requests/Admin/SiteSettingRequest.php:66-82, 98 · app/Services/Admin/SiteSettingService.php:21, 46-49, 114-122 · app/Models/SiteSetting.php:113, 121-136
- resources/views/admin/coupons/index.blade.php · form.blade.php:1, 56-60, 236-240 · edit.blade.php · view.blade.php · create.blade.php
- database: dev_spec/_index/schema.md coupons · coupon_targets · coupon_issue_batches · user_coupons · coupon_memo_histories · points · point_logs · order_items.coupon_cap_applied
- 프로토타입: prototype_clean/ADMN-PROM-002_baseline.html:383-391(서브뷰 전환), 405-549(목록), 550-960(폼 · P1 시연), 962-1095(포인트 정책 · 원장), 1096-1145(modal-p1 · modal-point)
