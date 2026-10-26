# 개발 DB 문서 사이트 ↔ 마이그레이션 색인 대조

- 대상: https://sanjunmo-db-docs.vercel.app/index.html (white 공유 2026-10-27). 테이블 정의서 10쪽 + 상태값 정의서만 읽음
- 비교 기준: `dev_spec/_index/schema.md`(dev d562524a 마이그레이션 누적, `_tools/extract_dev.py` 생성) + 개발 저장소 원본 마이그레이션 · 코드 grep(읽기 전용)
- 작성 2026-10-27, 보조 스레드. 대조 스크립트는 저장소에 남기지 않음(규칙)

## 1. 사이트 정체
- **DB에서 뽑은 문서가 아니다.** 페이지마다 "JSON 원본 기반 자동 생성 문서 · 수정 원본 `data/*.json`", 상태값 정의서는 "`data/codes.json` 을 원본으로 관리 … JSON 에 먼저 추가한 뒤 문서를 재생성"이라고 적혀 있다. 즉 사람이 관리하는 JSON 을 HTML 로 렌더링한 정의서(SchemaSpy · tbls 류의 DB 역추출 흔적 없음). 생성기 · 저장소는 개발 저장소(sanjunmo)에 없다(`git ls-files` 에 `codes.json` · 정의서 없음).
- 버전: 테이블 정의서 10쪽 모두 `2.6.26`, 상태값 정의서 `2.6.23`. DB `MySQL 8.x`, `Laravel + Eloquent`. 테이블 150개(색인 153개).
- 생성 시점(추정): 마이그레이션 `2026_10_23_000264`(lecture_bookmarks, 문서의 '미분류'에 있음)까지 반영, `2026_10_26_000265` 이후 4개는 없음 → 10-23 ~ 10-26 사이 생성. dev d562524a(10-26 19:52)보다 하루 이상 뒤처짐.
- 쓸모: 테이블 · 컬럼 **설명(한국어 주석)과 상태값 · 구분값 허용값이 정리돼 있어** 우리 색인보다 읽기 좋다. 컬럼 구성은 아래처럼 우리 색인보다 정확한 곳이 많다.

## 2. 결론 요약
| 구분 | 건수 | 판정 |
| :--- | ---: | :--- |
| 문서에만 있는 테이블 | 0 | |
| 색인에만 있는 테이블 | 3 | 2개는 10-26 신규(문서가 뒤처짐, 코드 사용 중), 1개는 이름이 바뀐 옛 테이블(색인 오류) |
| 문서에만 있는 컬럼 | 119 | **모두 마이그레이션에 실제로 있음 → 우리 색인 누락**(추출기 한계). 문서가 맞다 |
| 색인에만 있는 컬럼 | 35 | 15개는 10-26 신규(문서 뒤처짐, 코드 사용 중 → **진짜 문서 공백**), 20개는 이미 삭제된 컬럼(색인 오류) |
| 타입 다름 | 8 | 표본 확인 결과 문서가 맞음(`widen()` · 원시 SQL 변경을 색인이 못 따라감) |
| NULL 여부 다름 | 14 | 확인 필요 — 표본(admin_logs.admin_id)은 문서가 맞음 |

**진짜 공백(코드에서 쓰는데 문서에 없음) = 테이블 2 · 컬럼 15, 모두 2026-10-26 마이그레이션.** 나머지 차이는 우리 색인 쪽 문제다. white 말대로 안 쓰는 테이블 · 컬럼은 오류로 보지 않고 아래 표에 '미사용 추정'으로만 표시했다.

코드 사용 표시: 개발 저장소 `app` · `resources` · `config` · `routes` · `database/seeders` · `factories` 를 `git grep` 해서 판정. `사용 중`(따옴표 · `->컬럼` · `컬럼 =>` 형태로 나옴) / `미사용 추정`(이름이 아예 없음) / `확인 불가`(id · status · code 처럼 흔한 이름, 또는 주석에만 나옴).

## 3. 진짜 공백 — 코드 사용 중인데 문서에 없음 (개발팀에 정의서 갱신 요청 대상)
| 테이블 | 컬럼 | 타입 | 코드 사용 | 마이그레이션 |
| :--- | :--- | :--- | :--- | :--- |
| `contract_co_signers` (테이블 전체, 컬럼 11개) | | | 사용 중 — 테이블명 0 · 모델(ContractCoSigner) 6 | 2026_10_26_000265 |
| `pg_reconciliation_item_holders` (테이블 전체, 컬럼 7개) | | | 사용 중 — 테이블명 0 · 모델(PgReconciliationItemHolder) 5 | 2026_10_26_000271 |
| `payee_splits` | `note` | string(255) | 사용 중 (70곳) | 2026_10_26_000265 |
| `pg_reconciliation_items` | `mismatch_reason_code` | string(30) | 사용 중 (28곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `explanation` | string(500) | 사용 중 (29곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `approval_status` | string(20) | 사용 중 (56곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `approved_by` | unsignedBigInteger | 사용 중 (3곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `approved_at` | timestamp | 사용 중 (33곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `rights_holder_id` | unsignedBigInteger | 사용 중 (218곳, 이름이 흔해 다른 테이블 포함) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `pg_tid` | string(255) | 사용 중 (12곳) | 2026_10_26_000266 |
| `pg_reconciliation_items` | `paid_at` | dateTime | 사용 중 (93곳) | 2026_10_26_000266 |
| `refund_claims` | `rs_deduct_amount` | integer | 사용 중 (5곳) | 2026_10_26_000267 |
| `refund_claims` | `support_deduct_amount` | integer | 사용 중 (3곳) | 2026_10_26_000267 |
| `refund_claims` | `settlement_target_month` | char(7) | 사용 중 (4곳) | 2026_10_26_000267 |
| `refund_claims` | `settle_review_status` | string(20) | 사용 중 (5곳) | 2026_10_26_000267 |
| `refund_claims` | `settle_reviewed_by` | unsignedBigInteger | 사용 중 (3곳) | 2026_10_26_000267 |
| `refund_claims` | `settle_reviewed_at` | timestamp | 사용 중 (5곳) | 2026_10_26_000267 |

## 4. 우리 색인 오류 — 문서가 맞음 (`_tools/extract_dev.py` 보완 필요, 총괄 스레드 몫)
추출기가 놓치는 마이그레이션 패턴(원문 확인):
- `$table->timestamps()` · `softDeletes()` 를 `created_at` · `updated_at` · `deleted_at` 으로 펼치지 않음
- 컬럼명 → 클로저 배열로 추가하는 패턴(`'tax_decision_status' => fn (Blueprint $t) => …`, 예 `2026_10_15_000207`)과 `Schema::table($table, fn … => $define(...))` 헬퍼
- `foreach ([...] as $column) { … dropColumn($column) }`, 여러 줄 `dropColumn([...])` 배열(예 `2026_09_15_000114` instructors 정산 칸 6개 · `2026_09_08_000076` payments 옛 PG 칸 12개 · `2026_09_08_000091` instructors bio · profile_image)
- `$this->widen(...)->change()` 헬퍼로 길이를 늘린 것(`2026_10_12_000203`), `DB::statement` 원시 ALTER, `Schema::rename`(package_instructors → product_instructors, `2026_07_10_200000`)

### 4-1. 색인에만 있는 컬럼 중 이미 삭제된 것 (20)
| 테이블 | 컬럼 | 코드 사용 | 삭제 마이그레이션 |
| :--- | :--- | :--- | :--- |
| `instructors` | `bio` | 미사용 추정 | 2026_09_08_000091 |
| `instructors` | `profile_image` | 확인 불가 | 2026_09_08_000091 |
| `instructors` | `tax_type` | 사용 중 | 2026_09_21_000154 |
| `instructors` | `business_number` | 사용 중 | 2026_10_15_000211 |
| `instructors` | `bank_name` | 사용 중 | 2026_10_21_000230 |
| `instructors` | `account_no` | 사용 중 | 2026_10_20_000231 |
| `instructors` | `account_holder` | 사용 중 | 2026_10_21_000230 |
| `instructors` | `tax_email` | 사용 중 | 2026_09_15_000114 |
| `payments` | `imp_uid` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `merchant_uid` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `pay_method` | 사용 중 | 2026_09_08_000076 |
| `payments` | `vbank_name` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `vbank_num` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `vbank_due` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `virtual_account_bank` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `virtual_account_no` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `virtual_account_holder` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `virtual_account_due_at` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `depositor_name` | 미사용 추정 | 2026_09_08_000076 |
| `payments` | `deposited_at` | 미사용 추정 | 2026_09_08_000076 |
| `package_instructors`(테이블) | | 미사용 추정 | 2026_07_10_200000 에서 product_instructors 로 이름 변경 |

### 4-2. 문서에만 있는 컬럼 (색인 누락, 119)
| 테이블 | 컬럼 | 문서 타입 | 코드 사용 | 원인 |
| :--- | :--- | :--- | :--- | :--- |
| `banners` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `book_authors` | `change_reason` | VARCHAR(500) | 사용 중 | 마이그레이션에 있음 2026_09_08_000098,2026_10_15_000209 |
| `book_authors` | `end_basis` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_03_000193,2026_10_15_000209 |
| `book_restock_alerts` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `book_restock_alerts` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `books` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `books` | `display_status` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_09_18_000127,2026_09_22_000159 |
| `buyout_payments` | `exclusive_ended_at` | DATE | 사용 중 | 마이그레이션에 있음 2026_10_03_000195 |
| `buyout_payments` | `exclusive_started_at` | DATE | 사용 중 | 마이그레이션에 있음 2026_10_03_000195 |
| `buyout_payments` | `rights_scope` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_03_000195 |
| `categories` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `contract_milestones` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `contract_milestones` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `contract_rate_lines` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `contract_rate_lines` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `coupons` | `allow_stack_coupon` | TINYINT | 미사용 추정 | 마이그레이션에 있음 2026_09_08_000084 |
| `coupons` | `allow_with_point` | TINYINT | 사용 중 | 마이그레이션에 있음 2026_09_08_000084 |
| `coupons` | `exclude_book` | TINYINT | 사용 중 | 마이그레이션에 있음 2026_09_08_000084 |
| `coupons` | `issue_method` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_09_08_000084 |
| `coupons` | `max_per_user` | INT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_09_08_000084 |
| `coupons` | `scheduled_at` | DATETIME | 사용 중 | 마이그레이션에 있음 2026_09_08_000084,2026_09_08_000096 |
| `coupons` | `send_notification` | TINYINT | 사용 중 | 마이그레이션에 있음 2026_09_08_000084,2026_09_28_000171 |
| `coupons` | `target_group_id` | BIGINT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_09_08_000084,2026_09_08_000089 |
| `courses` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `courses` | `display_status` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_09_18_000127,2026_09_22_000159 |
| `exclusive_contract_clawbacks` | `destruction_hold` | TINYINT(1) | 미사용 추정 | 마이그레이션에 있음 2026_09_21_000151 |
| `exclusive_contract_fees` | `penalty_base` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_calc_type` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_clause_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_clawback_relation` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_fixed_amount` | INT | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_multiple_rate` | DECIMAL(5,2) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_offset_consent_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `exclusive_contract_fees` | `penalty_trigger_text` | VARCHAR(500) | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `goods` | `deleted_at` | TIMESTAMP | 확인 불가 | softDeletes() 미전개 |
| `inquiry_categories` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `inquiry_categories` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `instructor_categories` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `instructor_categories` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `instructor_profiles` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `instructor_profiles` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `lecture_instructors` | `change_reason` | VARCHAR(500) | 사용 중 | 마이그레이션에 있음 2026_09_08_000098,2026_10_15_000209 |
| `lecture_instructors` | `end_basis` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_03_000193,2026_10_15_000209 |
| `lectures` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `notification_campaigns` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `notification_campaigns` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `notification_templates` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `nts_verification_logs` | `b_stt_cd` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `package_items` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `package_items` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `packages` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `packages` | `display_status` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_09_18_000127,2026_09_22_000159 |
| `player_settings` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `player_settings` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `popups` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `posts` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `prepayment_ledger_lines` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `prepayment_ledger_lines` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `prepayment_ledgers` | `destruction_hold` | TINYINT(1) | 미사용 추정 | 마이그레이션에 있음 2026_09_21_000151 |
| `product_instructors` | `created_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_10_26_000265,2026_10_26_000271 |
| `product_instructors` | `id` | BIGINT UNSIGNED | 확인 불가 | 마이그레이션에 있음 2026_10_23_000264,2026_10_26_000265 |
| `product_instructors` | `instructor_id` | BIGINT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_09_17_000122,2026_09_22_000163 |
| `product_instructors` | `sort_order` | INT | 확인 불가 | 마이그레이션에 있음 2026_09_08_000095,2026_10_21_000239 |
| `product_qnas` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `product_qnas` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `reviews` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `reviews` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `rights_holder_contracts` | `contract_expiry_alert_days` | SMALLINT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_10_15_000214 |
| `rights_holder_contracts` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `rights_holder_contracts` | `etc_amount_type` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `etc_unit_price` | INT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `initial_end_date` | DATE | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holder_contracts` | `min_claim_limit` | INT | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holder_contracts` | `min_payout_limit` | INT | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holder_contracts` | `prepayment_offset_target` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_03_000197 |
| `rights_holder_contracts` | `renewal_stop_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_15_000207,2026_10_15_000214 |
| `rights_holder_contracts` | `term_adv_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_03_000197 |
| `rights_holder_contracts` | `term_book_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_02_000186 |
| `rights_holder_contracts` | `term_buyout_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `term_cons_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_02_000186 |
| `rights_holder_contracts` | `term_course_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_02_000186 |
| `rights_holder_contracts` | `term_dev_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `term_etc_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `term_exc_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_03_000192 |
| `rights_holder_contracts` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `rights_holder_contracts` | `vat_exception_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_02_000186 |
| `rights_holders` | `business_subtype` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holders` | `consignment_ended_at` | DATE | 사용 중 | 마이그레이션에 있음 2026_10_02_000188 |
| `rights_holders` | `consignment_promo_override_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_10_02_000188 |
| `rights_holders` | `consignment_return_days` | SMALLINT UNSIGNED | 사용 중 | 마이그레이션에 있음 2026_10_02_000188 |
| `rights_holders` | `consignment_return_tracking_yn` | TINYINT(1) | 사용 중 | 마이그레이션에 있음 2026_09_18_000137,2026_10_02_000188 |
| `rights_holders` | `consignment_started_at` | DATE | 사용 중 | 마이그레이션에 있음 2026_10_02_000188 |
| `rights_holders` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `rights_holders` | `deleted_at` | TIMESTAMP | 확인 불가 | softDeletes() 미전개 |
| `rights_holders` | `destruction_hold` | TINYINT(1) | 미사용 추정 | 마이그레이션에 있음 2026_09_21_000151 |
| `rights_holders` | `matrix_case_id` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_15_000207,2026_10_19_000221 |
| `rights_holders` | `open_date` | DATE | 사용 중 | 마이그레이션에 있음 2026_09_18_000126,2026_10_15_000207 |
| `rights_holders` | `suspended_approval_reason` | VARCHAR(255) | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holders` | `tax_decision_reason` | TEXT | 사용 중 | 마이그레이션에 있음 2026_10_15_000207 |
| `rights_holders` | `tax_decision_status` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_19_000221,2026_10_21_000229 |
| `rights_holders` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `study_qnas` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `study_qnas` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `suppliers` | `deleted_at` | TIMESTAMP | 확인 불가 | softDeletes() 미전개 |
| `support_fund_agreements` | `book_target_scope` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_03_000193 |
| `support_fund_agreements` | `destruction_hold` | TINYINT(1) | 미사용 추정 | 마이그레이션에 있음 2026_09_21_000151 |
| `support_fund_agreements` | `end_basis` | VARCHAR(20) | 사용 중 | 마이그레이션에 있음 2026_10_03_000193,2026_10_15_000209 |
| `support_fund_agreements` | `lecture_target_scope` | VARCHAR(10) | 사용 중 | 마이그레이션에 있음 2026_10_03_000193 |
| `terms` | `deleted_at` | TIMESTAMP | 확인 불가 | 마이그레이션에 있음 2026_09_18_000126,2026_10_16_000217 |
| `user_addresses` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `user_addresses` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `user_devices` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `user_devices` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `verification_attempts` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `verification_attempts` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `verification_ip_exceptions` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `verification_ip_exceptions` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `withdrawn_users_di` | `created_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |
| `withdrawn_users_di` | `updated_at` | TIMESTAMP | 확인 불가 | timestamps() 미전개 |

### 4-3. 타입 다름 (8)
| 테이블.컬럼 | 색인 | 문서 | 판정 |
| :--- | :--- | :--- | :--- |
| `lecture_progresses.duration_sec` | integer | INT UNSIGNED | 확인 필요 |
| `payment_cancels.result_code` | string(10) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `payment_cancels.cancel_tid` | string(30) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `payment_cancels.idempotency_key` | string(100) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `pg_notifications.pg_otid` | string(30) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `pg_notifications.pg_tid` | string(30) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `pg_notifications.result_code` | string(10) | VARCHAR(255) | 문서가 맞음 — `2026_10_12_000203` widen() 로 255 |
| `terms.version` | integer | VARCHAR(10) | 확인 필요 — `2026_09_08_000098` 원시 SQL 이 version 을 다룸(문서 쪽 추정) |

### 4-4. NULL 여부 다름 (14)
| 테이블.컬럼 | 색인 | 문서 | 판정 |
| :--- | :--- | :--- | :--- |
| `admin_logs.admin_id` | NOT NULL | NULL | 문서가 맞음(create_remaining_tables 에서 nullable) |
| `attachments.disk` | NULL | NOT NULL | 확인 필요 |
| `attachments.original_name` | NULL | NOT NULL | 확인 필요 |
| `book_royalty_contracts.ended_at` | NOT NULL | NULL | 확인 필요 |
| `book_royalty_contracts.book_id` | NOT NULL | NULL | 확인 필요 |
| `excel_download_logs.admin_id` | NOT NULL | NULL | 확인 필요 |
| `lecture_progresses.user_course_id` | NULL | NOT NULL | 확인 필요 |
| `order_items.product_id` | NOT NULL | NULL | 확인 필요 |
| `order_items.line_no` | NULL | NOT NULL | 확인 필요 |
| `study_qnas.lecture_id` | NOT NULL | NULL | 확인 필요 |
| `support_fund_agreements.end_date` | NOT NULL | NULL | 확인 필요 |
| `support_fund_agreements.total_cap_amount` | NOT NULL | NULL | 확인 필요 |
| `support_fund_agreements.cap_restore_on_refund` | NOT NULL | NULL | 확인 필요 |
| `withdrawn_users_di.di_hash` | NULL | NOT NULL | 확인 필요 |

## 5. 메뉴 · 권한 데이터
- 사이트에 **메뉴 · 권한 데이터(행)는 없다.** 06 관리자 권한 · 메뉴 · 로그 정의서는 테이블 구조와 설명만 있다.
- 구조로 새로 알게 된 것: `admin_menus.screen_code` VARCHAR(30) UNIQUE — "화면 설계 코드(ADMN-USER-001 형식). 권한 매트릭스 행 식별자이며 `excel_download_logs.menu_key` 도 이 값을 참조". 즉 개발 메뉴 1행 = 화면 코드 1개이고, 엑셀 다운로드 로그도 화면 코드로 묶인다. `admin_roles.code` 는 super · cs · logistics · finance · instructor · assistant 6종(색인과 같음).
- 메뉴 목록(어떤 route_name 이 어떤 화면 코드인지)은 여전히 개발 서버 DB 또는 백오피스 메뉴 관리 화면 열람이 필요하다.

## 6. dev_spec 에서 쓰는 법
- 컬럼 이름 · 타입은 **문서 사이트 + 10-26 이후 마이그레이션(3절)** 을 함께 본다. 우리 `schema.md` 는 4절 패턴이 고쳐질 때까지 누락이 있다.
- 상태값 · 구분값 허용값은 문서 `10_상태값_구분값_정의서` 가 가장 정리돼 있다(단 2.6.23 이라 10-26 신규 값은 없음).

## 7. 추출기 보완 후 다시 대조 (2026-10-27, 같은 dev d562524a)
`_tools/extract_dev.py` 스키마 파서를 4절 패턴에 맞게 고치고 `_index/` 를 다시 만들었다. 이번에 추가로 처리한 패턴은 다음과 같다.
- `timestamps()` · `softDeletes()` · `rememberToken()` · `morphs()`
- `'컬럼' => fn (Blueprint $t) => …` 배열과 `$this->헬퍼('테이블', …)` 호출(`widen` 포함)
- `foreach (리터럴 | self::상수 | $변수 as …)` 안의 `Schema::table($table, …)`, `$t->타입($column)`, `dropColumn($column)`
- 여러 줄 `dropColumn([...])`, `$cols = array_filter([...])` 뒤 `dropColumn($cols)`
- `if (! Schema::hasColumn(…))` 로 감싼 추가는 이미 있는 컬럼이면 건너뜀
- `Schema::rename`, `DB::statement("ALTER TABLE … MODIFY …")`(값이 foreach 변수로 들어오는 경우 포함)

| 항목 | 처음 | 보완 후 |
| :--- | ---: | ---: |
| 테이블(색인 / 문서) | 153 / 150 | 152 / 150 |
| 색인에만 있는 테이블 | 3 | **2**(10-26 신규 contract_co_signers · pg_reconciliation_item_holders) |
| 문서에만 있는 컬럼 | 119 | **0** |
| 색인에만 있는 컬럼 | 35 | **15**(10-26 신규 3절 그대로) |
| 타입 다름 | 8 | **0** |
| NULL 여부 다름 | 14 | **0** |

이제 남은 차이는 3절의 진짜 공백(10-26 마이그레이션 4개)뿐이다. 문서와 색인 양쪽에 있으면서 코드에서 안 쓰는 컬럼은 오류로 치지 않는다. 그런 컬럼(예: `*.destruction_hold` 4개, `coupons.allow_stack_coupon`)은 두 쪽이 같아 차이로 잡히지 않는다.
4절의 "색인 오류" 표들은 처음 대조의 기록으로 남긴다. 바뀐 색인을 인용한 dev_spec 파일 목록은 `schema_reindex_impact.md` 에 있다.
