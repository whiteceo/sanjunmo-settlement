# schema.md 재생성 영향 — 바뀐 컬럼을 인용한 dev_spec 파일

- 2026-10-27 `_tools/extract_dev.py` 스키마 파서 보완 후 재생성(dev d562524a 그대로). 이 목록은 **검토 대상**이다. 파일은 고치지 않았다(각 파일 담당이 고친다).
- 색인 변화 185건: 새로 잡힌 컬럼 119 · 이미 삭제된 컬럼 제거 20 · 타입/NULL 정정 45 · 이름 바뀐 옛 테이블 제거 1(package_instructors).
- 판정 기준: 파일에 `테이블.컬럼` 이 있거나, 테이블 이름과 `` `컬럼` `` 이 함께 나오면 인용으로 봤다(흔한 이름 id · status · code 등 제외). 같은 이름의 다른 테이블 컬럼일 수 있으니 열어서 확인한다.
- 우선순위: **삭제**(없는 컬럼을 있다고 적었을 수 있음) > **추가**("개발에 없음 · 미구현"으로 적었을 수 있음) > 타입·NULL(길이 · 필수 여부 표기).

| 파일 | 삭제 | 추가 | 타입·NULL | 항목 |
| :--- | ---: | ---: | ---: | :--- |
| `ADMN-ORD-001.md` | 1 | 0 | 4 | payments.virtual_account_due_at: 삭제(이미 drop 된 컬럼)<br>deliveries.batch_id: unsignedBigInteger nullable → bigint unsigned nullable<br>excel_download_logs.admin_id: unsignedBigInteger NOT NULL → bigint unsigned nullable<br>order_items.line_no: unsignedInteger nullable → int unsigned NOT NULL<br>order_items.product_id: unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `ADMN-PROD-006.md` | 1 | 0 | 0 | instructors.business_number: 삭제(이미 drop 된 컬럼) |
| `ADMN-INST-001.md` | 0 | 23 | 3 | rights_holder_contracts.contract_expiry_alert_days: 추가 unsignedSmallInteger<br>rights_holder_contracts.etc_amount_type: 추가 string(10)<br>rights_holder_contracts.etc_unit_price: 추가 unsignedInteger<br>rights_holder_contracts.initial_end_date: 추가 date<br>rights_holder_contracts.min_claim_limit: 추가 integer<br>rights_holder_contracts.min_payout_limit: 추가 integer<br>rights_holder_contracts.renewal_stop_yn: 추가 boolean<br>rights_holder_contracts.term_adv_yn: 추가 boolean<br>rights_holder_contracts.term_book_yn: 추가 boolean<br>rights_holder_contracts.term_buyout_yn: 추가 boolean<br>rights_holder_contracts.term_cons_yn: 추가 boolean<br>rights_holder_contracts.term_course_yn: 추가 boolean<br>rights_holder_contracts.term_dev_yn: 추가 boolean<br>rights_holder_contracts.term_etc_yn: 추가 boolean<br>rights_holder_contracts.term_exc_yn: 추가 boolean<br>rights_holder_contracts.vat_exception_yn: 추가 boolean<br>rights_holders.business_subtype: 추가 string(20)<br>rights_holders.consignment_promo_override_yn: 추가 boolean<br>rights_holders.matrix_case_id: 추가 string(10)<br>rights_holders.open_date: 추가 date<br>rights_holders.suspended_approval_reason: 추가 string(255)<br>rights_holders.tax_decision_reason: 추가 text<br>rights_holders.tax_decision_status: 추가 string(20)<br>book_royalty_contracts.book_id: unsignedBigInteger NOT NULL → bigint unsigned nullable<br>book_royalty_contracts.ended_at: date NOT NULL → date nullable<br>rights_holders.tax_type: string(20) NOT NULL → varchar(20) NOT NULL |
| `ADMN-PROM-002.md` | 0 | 8 | 1 | coupons.allow_stack_coupon: 추가 tinyInteger<br>coupons.allow_with_point: 추가 tinyInteger<br>coupons.exclude_book: 추가 tinyInteger<br>coupons.issue_method: 추가 string(20)<br>coupons.max_per_user: 추가 unsignedInteger<br>coupons.scheduled_at: 추가 dateTime<br>coupons.send_notification: 추가 tinyInteger<br>coupons.target_group_id: 추가 unsignedBigInteger<br>site_settings.deduct_priority: string(30) NOT NULL → varchar(30) NOT NULL |
| `ADMN-PROD-003.md` | 0 | 6 | 0 | books.display_status: 추가 string(20)<br>courses.deleted_at: 추가 timestamp<br>courses.display_status: 추가 string(20)<br>packages.display_status: 추가 string(20)<br>product_instructors.instructor_id: 추가 foreignId<br>product_instructors.sort_order: 추가 integer |
| `ADMN-USER-007.md` | 0 | 4 | 2 | exclusive_contract_clawbacks.destruction_hold: 추가 boolean<br>prepayment_ledgers.destruction_hold: 추가 boolean<br>rights_holders.destruction_hold: 추가 boolean<br>support_fund_agreements.destruction_hold: 추가 boolean<br>attachments.disk: string(20) nullable → varchar(20) NOT NULL<br>attachments.original_name: string(255) nullable → string(255) NOT NULL |
| `ADMN-PROD-005.md` | 0 | 4 | 1 | books.display_status: 추가 string(20)<br>courses.display_status: 추가 string(20)<br>package_instructors(테이블): 테이블 삭제(색인에서)<br>packages.display_status: 추가 string(20)<br>site_settings.refund_claim_min_progress: unsignedTinyInteger NOT NULL → tinyint unsigned NOT NULL |
| `ADMN-PROD-004.md` | 0 | 3 | 1 | books.deleted_at: 추가 timestamp<br>books.display_status: 추가 string(20)<br>product_instructors.instructor_id: 추가 foreignId<br>books.is_free_delivery: boolean NOT NULL → tinyint(1) NOT NULL |
| `ADMN-CONF-010.md` | 0 | 0 | 3 | admin_logs.admin_id: unsignedBigInteger NOT NULL → bigint unsigned nullable<br>excel_download_logs.admin_id: unsignedBigInteger NOT NULL → bigint unsigned nullable<br>login_logs.event: string(30) NOT NULL → varchar(30) NOT NULL |
| `ADMN-PROM-001.md` | 0 | 0 | 3 | promotions.banner_pc_path: string(255) nullable → varchar(255) nullable<br>promotions.slug: string(40) unique → varchar(40) NOT NULL<br>promotions.thumbnail_path: string(255) nullable → varchar(255) nullable |
| `ADMN-LOGIN-001.md` | 0 | 0 | 2 | admin_allowed_ips.ip: string(45) unique → varchar(45) NOT NULL<br>login_logs.event: string(30) NOT NULL → varchar(30) NOT NULL |
| `ADMN-PROD-001.md` | 0 | 2 | 0 | categories.deleted_at: 추가 timestamp<br>courses.display_status: 추가 string(20) |
| `ADMN-PTNR-002.md` | 0 | 0 | 2 | deliveries.batch_id: unsignedBigInteger nullable → bigint unsigned nullable<br>deliveries.status: string(30) NOT NULL → varchar(30) NOT NULL |
| `ADMN-RFD-002.md` | 0 | 0 | 2 | payment_cancels.cancel_tid: string(30) nullable → string(255) nullable<br>payment_cancels.idempotency_key: string(100) nullable,unique → string(255) nullable |
| `ADMN-SETT-005.md` | 0 | 0 | 2 | settlement_adjustments.origin_settlement_id: unsignedBigInteger nullable → bigint unsigned nullable<br>settlement_adjustments.status: string(20) NOT NULL → varchar(20) NOT NULL |
| `ADMN-SETT-008.md` | 0 | 1 | 1 | rights_holders.open_date: 추가 date<br>rights_holders.tax_type: string(20) NOT NULL → varchar(20) NOT NULL |
| `ADMN-BOOK-001.md` | 0 | 0 | 1 | book_royalty_contracts.book_id: unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `ADMN-BRD-001.md` | 0 | 1 | 0 | posts.deleted_at: 추가 timestamp |
| `ADMN-CONF-002.md` | 0 | 0 | 1 | terms.version: integer NOT NULL → varchar(10) NOT NULL |
| `ADMN-CONF-003.md` | 0 | 0 | 1 | users.email: string(100) nullable,unique → varchar(100) nullable |
| `ADMN-CONF-005.md` | 0 | 0 | 1 | users.email: string(100) nullable,unique → varchar(100) nullable |
| `ADMN-INST-002.md` | 0 | 0 | 1 | contract_milestones.approval_status: string(20) NOT NULL → varchar(20) NOT NULL |
| `ADMN-PROD-002.md` | 0 | 1 | 0 | lectures.deleted_at: 추가 timestamp |
| `ADMN-SETT-002.md` | 0 | 0 | 1 | carryover_ledgers.reason: string(30) NOT NULL → varchar(30) NOT NULL |
| `ADMN-SETT-011.md` | 0 | 0 | 1 | deliveries.batch_id: unsignedBigInteger nullable → bigint unsigned nullable |
| `ADMN-USER-001.md` | 0 | 0 | 1 | users.email: string(100) nullable,unique → varchar(100) nullable |
| `ADMN-VEND-001.md` | 0 | 1 | 0 | suppliers.deleted_at: 추가 timestamp |

## 색인 변화 전체
| 테이블 | 컬럼 | 변화 |
| :--- | :--- | :--- |
| `admin_allowed_ips` | `ip` | string(45) unique → varchar(45) NOT NULL |
| `admin_logs` | `admin_id` | unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `attachments` | `disk` | string(20) nullable → varchar(20) NOT NULL |
| `attachments` | `original_name` | string(255) nullable → string(255) NOT NULL |
| `banners` | `deleted_at` | 추가 timestamp |
| `book_authors` | `change_reason` | 추가 string(500) |
| `book_authors` | `end_basis` | 추가 string(20) |
| `book_restock_alerts` | `created_at` | 추가 timestamp |
| `book_restock_alerts` | `updated_at` | 추가 timestamp |
| `book_royalty_contracts` | `book_id` | unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `book_royalty_contracts` | `ended_at` | date NOT NULL → date nullable |
| `books` | `deleted_at` | 추가 timestamp |
| `books` | `display_status` | 추가 string(20) |
| `books` | `is_free_delivery` | boolean NOT NULL → tinyint(1) NOT NULL |
| `buyout_payments` | `exclusive_ended_at` | 추가 date |
| `buyout_payments` | `exclusive_started_at` | 추가 date |
| `buyout_payments` | `rights_scope` | 추가 string(20) |
| `carryover_ledgers` | `reason` | string(30) NOT NULL → varchar(30) NOT NULL |
| `categories` | `deleted_at` | 추가 timestamp |
| `contract_milestones` | `approval_status` | string(20) NOT NULL → varchar(20) NOT NULL |
| `contract_milestones` | `created_at` | 추가 timestamp |
| `contract_milestones` | `updated_at` | 추가 timestamp |
| `contract_rate_lines` | `created_at` | 추가 timestamp |
| `contract_rate_lines` | `updated_at` | 추가 timestamp |
| `coupons` | `allow_stack_coupon` | 추가 tinyInteger |
| `coupons` | `allow_with_point` | 추가 tinyInteger |
| `coupons` | `exclude_book` | 추가 tinyInteger |
| `coupons` | `issue_method` | 추가 string(20) |
| `coupons` | `max_per_user` | 추가 unsignedInteger |
| `coupons` | `scheduled_at` | 추가 dateTime |
| `coupons` | `send_notification` | 추가 tinyInteger |
| `coupons` | `target_group_id` | 추가 unsignedBigInteger |
| `courses` | `deleted_at` | 추가 timestamp |
| `courses` | `display_status` | 추가 string(20) |
| `deliveries` | `batch_id` | unsignedBigInteger nullable → bigint unsigned nullable |
| `deliveries` | `status` | string(30) NOT NULL → varchar(30) NOT NULL |
| `excel_download_logs` | `admin_id` | unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `exclusive_contract_clawbacks` | `destruction_hold` | 추가 boolean |
| `exclusive_contract_fees` | `penalty_base` | 추가 string(20) |
| `exclusive_contract_fees` | `penalty_calc_type` | 추가 string(20) |
| `exclusive_contract_fees` | `penalty_clause_yn` | 추가 boolean |
| `exclusive_contract_fees` | `penalty_clawback_relation` | 추가 string(20) |
| `exclusive_contract_fees` | `penalty_fixed_amount` | 추가 integer |
| `exclusive_contract_fees` | `penalty_multiple_rate` | 추가 decimal(5, 2) |
| `exclusive_contract_fees` | `penalty_offset_consent_yn` | 추가 boolean |
| `exclusive_contract_fees` | `penalty_trigger_text` | 추가 string(500) |
| `goods` | `deleted_at` | 추가 timestamp |
| `inquiry_categories` | `created_at` | 추가 timestamp |
| `inquiry_categories` | `updated_at` | 추가 timestamp |
| `instructor_categories` | `created_at` | 추가 timestamp |
| `instructor_categories` | `updated_at` | 추가 timestamp |
| `instructor_profiles` | `created_at` | 추가 timestamp |
| `instructor_profiles` | `updated_at` | 추가 timestamp |
| `instructors` | `account_holder` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `account_no` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `bank_name` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `bio` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `business_number` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `profile_image` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `tax_email` | 삭제(이미 drop 된 컬럼) |
| `instructors` | `tax_type` | 삭제(이미 drop 된 컬럼) |
| `lecture_instructors` | `change_reason` | 추가 string(500) |
| `lecture_instructors` | `end_basis` | 추가 string(20) |
| `lecture_progresses` | `duration_sec` | integer NOT NULL → int unsigned NOT NULL |
| `lecture_progresses` | `user_course_id` | unsignedBigInteger nullable → bigint unsigned NOT NULL |
| `lectures` | `deleted_at` | 추가 timestamp |
| `login_logs` | `event` | string(30) NOT NULL → varchar(30) NOT NULL |
| `notification_campaigns` | `created_at` | 추가 timestamp |
| `notification_campaigns` | `updated_at` | 추가 timestamp |
| `notification_templates` | `deleted_at` | 추가 timestamp |
| `nts_verification_logs` | `b_stt_cd` | 추가 string(10) |
| `order_items` | `cost_snapshot` | integer nullable → int nullable |
| `order_items` | `line_no` | unsignedInteger nullable → int unsigned NOT NULL |
| `order_items` | `product_id` | unsignedBigInteger NOT NULL → bigint unsigned nullable |
| `package_instructors` | `*` | 테이블 삭제(색인에서) |
| `package_items` | `created_at` | 추가 timestamp |
| `package_items` | `updated_at` | 추가 timestamp |
| `packages` | `deleted_at` | 추가 timestamp |
| `packages` | `display_status` | 추가 string(20) |
| `payment_cancels` | `cancel_tid` | string(30) nullable → string(255) nullable |
| `payment_cancels` | `idempotency_key` | string(100) nullable,unique → string(255) nullable |
| `payment_cancels` | `result_code` | string(10) nullable → string(255) nullable |
| `payments` | `deposited_at` | 삭제(이미 drop 된 컬럼) |
| `payments` | `depositor_name` | 삭제(이미 drop 된 컬럼) |
| `payments` | `imp_uid` | 삭제(이미 drop 된 컬럼) |
| `payments` | `merchant_uid` | 삭제(이미 drop 된 컬럼) |
| `payments` | `pay_method` | 삭제(이미 drop 된 컬럼) |
| `payments` | `vbank_due` | 삭제(이미 drop 된 컬럼) |
| `payments` | `vbank_name` | 삭제(이미 drop 된 컬럼) |
| `payments` | `vbank_num` | 삭제(이미 drop 된 컬럼) |
| `payments` | `virtual_account_bank` | 삭제(이미 drop 된 컬럼) |
| `payments` | `virtual_account_due_at` | 삭제(이미 drop 된 컬럼) |
| `payments` | `virtual_account_holder` | 삭제(이미 drop 된 컬럼) |
| `payments` | `virtual_account_no` | 삭제(이미 drop 된 컬럼) |
| `pg_notifications` | `pg_otid` | string(30) nullable → string(255) nullable |
| `pg_notifications` | `pg_tid` | string(30) nullable → string(255) nullable |
| `pg_notifications` | `result_code` | string(10) nullable → string(255) nullable |
| `player_settings` | `created_at` | 추가 timestamp |
| `player_settings` | `updated_at` | 추가 timestamp |
| `popups` | `deleted_at` | 추가 timestamp |
| `posts` | `deleted_at` | 추가 timestamp |
| `prepayment_ledger_lines` | `created_at` | 추가 timestamp |
| `prepayment_ledger_lines` | `updated_at` | 추가 timestamp |
| `prepayment_ledgers` | `destruction_hold` | 추가 boolean |
| `product_instructors` | `created_at` | 추가 timestamp |
| `product_instructors` | `id` | 추가 id |
| `product_instructors` | `instructor_id` | 추가 foreignId |
| `product_instructors` | `sort_order` | 추가 integer |
| `product_qnas` | `created_at` | 추가 timestamp |
| `product_qnas` | `updated_at` | 추가 timestamp |
| `promotions` | `banner_mobile_path` | string(255) nullable → varchar(255) nullable |
| `promotions` | `banner_pc_path` | string(255) nullable → varchar(255) nullable |
| `promotions` | `slug` | string(40) unique → varchar(40) NOT NULL |
| `promotions` | `thumbnail_path` | string(255) nullable → varchar(255) nullable |
| `reviews` | `created_at` | 추가 timestamp |
| `reviews` | `updated_at` | 추가 timestamp |
| `rights_holder_contracts` | `contract_expiry_alert_days` | 추가 unsignedSmallInteger |
| `rights_holder_contracts` | `created_at` | 추가 timestamp |
| `rights_holder_contracts` | `etc_amount_type` | 추가 string(10) |
| `rights_holder_contracts` | `etc_unit_price` | 추가 unsignedInteger |
| `rights_holder_contracts` | `initial_end_date` | 추가 date |
| `rights_holder_contracts` | `min_claim_limit` | 추가 integer |
| `rights_holder_contracts` | `min_payout_limit` | 추가 integer |
| `rights_holder_contracts` | `prepayment_offset_target` | 추가 string(10) |
| `rights_holder_contracts` | `renewal_stop_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_adv_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_book_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_buyout_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_cons_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_course_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_dev_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_etc_yn` | 추가 boolean |
| `rights_holder_contracts` | `term_exc_yn` | 추가 boolean |
| `rights_holder_contracts` | `updated_at` | 추가 timestamp |
| `rights_holder_contracts` | `vat_exception_yn` | 추가 boolean |
| `rights_holders` | `business_subtype` | 추가 string(20) |
| `rights_holders` | `consignment_ended_at` | 추가 date |
| `rights_holders` | `consignment_promo_override_yn` | 추가 boolean |
| `rights_holders` | `consignment_return_days` | 추가 unsignedSmallInteger |
| `rights_holders` | `consignment_return_tracking_yn` | 추가 boolean |
| `rights_holders` | `consignment_started_at` | 추가 date |
| `rights_holders` | `created_at` | 추가 timestamp |
| `rights_holders` | `deleted_at` | 추가 timestamp |
| `rights_holders` | `destruction_hold` | 추가 boolean |
| `rights_holders` | `matrix_case_id` | 추가 string(10) |
| `rights_holders` | `open_date` | 추가 date |
| `rights_holders` | `suspended_approval_reason` | 추가 string(255) |
| `rights_holders` | `tax_decision_reason` | 추가 text |
| `rights_holders` | `tax_decision_status` | 추가 string(20) |
| `rights_holders` | `tax_type` | string(20) NOT NULL → varchar(20) NOT NULL |
| `rights_holders` | `updated_at` | 추가 timestamp |
| `settlement_adjustments` | `approver1_id` | unsignedBigInteger nullable → bigint unsigned nullable |
| `settlement_adjustments` | `approver2_id` | unsignedBigInteger nullable → bigint unsigned nullable |
| `settlement_adjustments` | `origin_settlement_id` | unsignedBigInteger nullable → bigint unsigned nullable |
| `settlement_adjustments` | `status` | string(20) NOT NULL → varchar(20) NOT NULL |
| `site_settings` | `deduct_priority` | string(30) NOT NULL → varchar(30) NOT NULL |
| `site_settings` | `refund_claim_min_progress` | unsignedTinyInteger NOT NULL → tinyint unsigned NOT NULL |
| `site_settings` | `support_fund_scope_default` | string(20) NOT NULL → varchar(20) NOT NULL |
| `study_qnas` | `created_at` | 추가 timestamp |
| `study_qnas` | `lecture_id` | foreignId NOT NULL → unsignedBigInteger nullable |
| `study_qnas` | `updated_at` | 추가 timestamp |
| `suppliers` | `deleted_at` | 추가 timestamp |
| `support_fund_agreements` | `book_target_scope` | 추가 string(10) |
| `support_fund_agreements` | `cap_restore_on_refund` | boolean NOT NULL → tinyint(1) nullable |
| `support_fund_agreements` | `destruction_hold` | 추가 boolean |
| `support_fund_agreements` | `end_basis` | 추가 string(20) |
| `support_fund_agreements` | `end_date` | date NOT NULL → date nullable |
| `support_fund_agreements` | `lecture_target_scope` | 추가 string(10) |
| `support_fund_agreements` | `offset_type` | string(20) NOT NULL → varchar(20) NOT NULL |
| `support_fund_agreements` | `settlement_scope` | string(20) NOT NULL → varchar(20) NOT NULL |
| `support_fund_agreements` | `total_cap_amount` | integer NOT NULL → int nullable |
| `terms` | `deleted_at` | 추가 timestamp |
| `terms` | `version` | integer NOT NULL → varchar(10) NOT NULL |
| `user_addresses` | `created_at` | 추가 timestamp |
| `user_addresses` | `updated_at` | 추가 timestamp |
| `user_devices` | `created_at` | 추가 timestamp |
| `user_devices` | `updated_at` | 추가 timestamp |
| `users` | `email` | string(100) nullable,unique → varchar(100) nullable |
| `verification_attempts` | `created_at` | 추가 timestamp |
| `verification_attempts` | `updated_at` | 추가 timestamp |
| `verification_ip_exceptions` | `created_at` | 추가 timestamp |
| `verification_ip_exceptions` | `updated_at` | 추가 timestamp |
| `withdrawn_users_di` | `created_at` | 추가 timestamp |
| `withdrawn_users_di` | `di_hash` | string(64) nullable,unique → string(64) unique |
| `withdrawn_users_di` | `updated_at` | 추가 timestamp |
