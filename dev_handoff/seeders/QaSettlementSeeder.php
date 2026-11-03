<?php

namespace Database\Seeders;

use App\Services\Admin\RightsHolderCodeGenerator;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Crypt;
use Illuminate\Support\Facades\DB;

/**
 * dev / local 전용 정산 QA 권리자 · 계약 시더
 *
 * 정산 04권(QA 정산 케이스 스펙)의 Case 1 · 2 · 2-B · 3 · 3-B · 6 · 7 · 8 · 9 · 10 과
 * 세무 유형(간이 · 면세) · 매절 · 자사 권리자를 덮는 가짜 권리자 · 계약 · 약정 · 매핑을 만든다.
 * 매출(주문 · 결제 · 환불)은 만들지 않는다 — 테스트 결제로 만든다.
 *
 * 화면(ADMN-INST-001 · 002)으로 등록했을 때 쌓이는 행 모양을 dev DB(94aa56ac 시점)에서 읽어 그대로 따랐다.
 * 약정금 마일스톤은 pending 으로 넣는다 — 검수 승인(INST-002 Gate A · B · C)은 화면에서 한다.
 *
 * 운영 보호 — local·dev 가 아니면 아무것도 하지 않고 즉시 종료한다.
 * 멱등 — 같은 이름의 권리자가 이미 있으면 그 케이스는 건너뛴다.
 * 자사 권리자 — 이미 is_internal=1 이 있으면 그 행을 쓰고 새로 만들지 않는다(자사 권리자는 1건, DEV_TRANSFER 19-1 1-8).
 *
 * 매핑 — 강의 · 도서 id 는 환경마다 달라 .env 로 받는다. 비어 있거나 모자라면 그 케이스의 매핑만 건너뛴다.
 *   QA_SETTLE_LECTURE_IDS=1096,1097,...   (판매중 · published 강의, 다른 권리자 매핑이 없는 것, 9개)
 *   QA_SETTLE_BOOK_IDS=1205,1206,...      (자사 발행 도서, 3개)
 *
 * 실행:  docker compose exec php php artisan db:seed --class=QaSettlementSeeder
 * 정리:  이름이 'QA시더_' 로 시작하는 권리자와 그 계약에 딸린 행을 지운다(아래 cleanupSql() 참고).
 */
class QaSettlementSeeder extends Seeder
{
    private const PREFIX = 'QA시더_';

    private const START = '2026-11-01';

    private const END = '2027-10-31';

    /** 강의 매핑 순서 — QA_SETTLE_LECTURE_IDS 의 n번째 id 를 쓴다 */
    private const LECTURE_SLOTS = ['C1', 'C2', 'C3', 'C3B', 'C6', 'C7', 'C8', 'C9', 'BUY'];

    /** 도서 매핑 순서 — QA_SETTLE_BOOK_IDS 의 n번째 id 를 쓴다 */
    private const BOOK_SLOTS = ['C2', 'C2B', 'C8'];

    private RightsHolderCodeGenerator $codes;

    private array $lectureIds = [];

    private array $bookIds = [];

    private int $fakeSeq = 0;

    public function run(): void
    {
        if (! app()->environment(['local', 'dev'])) {
            $this->command?->warn('QaSettlementSeeder: local·dev 환경이 아니라 건너뜁니다.');

            return;
        }

        $this->codes = app(RightsHolderCodeGenerator::class);
        $this->lectureIds = $this->idsFromEnv('QA_SETTLE_LECTURE_IDS');
        $this->bookIds = $this->idsFromEnv('QA_SETTLE_BOOK_IDS');

        $internalId = $this->internalHolder();

        foreach ($this->cases($internalId) as $case) {
            if (DB::table('rights_holders')->where('name', self::PREFIX.$case['name'])->exists()) {
                $this->command?->line("이미 존재 → {$case['key']} (건너뜀)");

                continue;
            }

            DB::transaction(fn () => $this->seedCase($case, $internalId));
            $this->command?->info("생성 → {$case['key']} {$case['memo']}");
        }
    }

    /**
     * 케이스 정의. 금액 · 요율은 정산 04권 각 Case 의 입력 데이터를 따른다.
     *
     * holder.kind: personal(개인 3.3%) · general(일반과세) · simplified(간이) · exempt(면세) · consignor(위탁자)
     */
    private function cases(int $internalId): array
    {
        return [
            [
                'key' => 'C1', 'name' => 'Case1_개인_선급금대여금', 'memo' => '개인 3.3% · R/S 50% · 선급금 150만(대여금) 자동 상계',
                'holder' => ['kind' => 'personal'],
                'contract' => ['term_adv_yn' => 1, 'prepayment_tax_type' => 'LOAN', 'prepayment_offset_target' => 'RS_BOOK'],
                'rate' => 50, 'prepay' => 1500000,
                'lecture' => [['holder' => 'self', 'share' => 100]],
            ],
            [
                'key' => 'C2', 'name' => 'Case2_개인_강의인세복합', 'memo' => '개인 저작자 · R/S 50% + 자사 발행 인세 10%(실결제액) · 사업소득',
                'holder' => ['kind' => 'personal', 'income_category' => 'BUSINESS'],
                'contract' => ['term_book_yn' => 1],
                'rate' => 50, 'royalty' => 10,
                'lecture' => [['holder' => 'self', 'share' => 100]], 'book' => true,
            ],
            [
                'key' => 'C2B', 'name' => 'Case2B_개인_인세기타소득', 'memo' => '일시적 저술 · 인세 기타소득 C15(경비 60%) · 저작자 본인',
                'holder' => ['kind' => 'personal', 'income_category' => 'OTHER', 'income_clause' => 'C15'],
                'contract' => ['term_course_yn' => 0, 'term_book_yn' => 1],
                'royalty' => 10, 'book' => true,
            ],
            [
                'key' => 'C3', 'name' => 'Case3_일반과세_전속금MMG', 'memo' => '일반과세 법인(TX-07) · R/S 60% · MMG 150만 · 전속계약금 2회 분할(회차당 100만)',
                'holder' => ['kind' => 'general', 'business_subtype' => 'CORP'],
                'contract' => ['term_exc_yn' => 1],
                'rate' => 60, 'mmg' => 1500000,
                'exclusive' => ['amount' => 2000000, 'method' => 'INSTALLMENT', 'clawback' => 'NONE', 'milestones' => [1000000, 1000000]],
                'lecture' => [['holder' => 'self', 'share' => 100]],
            ],
            [
                'key' => 'C3B', 'name' => 'Case3B_개인_전속금반환', 'memo' => '개인 3.3% · 전속계약금 일시 600만 · 중도 해지 시 일할 반환(PRO_RATA)',
                'holder' => ['kind' => 'personal'],
                'contract' => ['term_exc_yn' => 1],
                'rate' => 50,
                'exclusive' => ['amount' => 6000000, 'method' => 'LUMP_SUM', 'clawback' => 'PRO_RATA', 'milestones' => [6000000]],
                'lecture' => [['holder' => 'self', 'share' => 100]],
            ],
            [
                'key' => 'C6', 'name' => 'Case6_개인_매출0개발지원금', 'memo' => '매출 0원 · 개발지원금 50만 일시금(비상계) · 대상 강의 자사 지분 공존',
                'holder' => ['kind' => 'personal'],
                'contract' => ['term_dev_yn' => 1],
                'rate' => 50,
                'support' => ['method' => 'LUMP_SUM', 'cap' => 500000, 'offset' => 'NON_OFFSET', 'milestones' => [500000]],
                'lecture' => [['holder' => 'self', 'share' => 50], ['holder' => 'internal', 'share' => 50]],
            ],
            [
                'key' => 'C7', 'name' => 'Case7_개인_수취인분할', 'memo' => 'R/S 50% · 2계층 분할 강사 70% / 소속사(일반과세 법인) 30%',
                'holder' => ['kind' => 'personal'],
                'payee' => ['name' => 'Case7_소속사법인', 'kind' => 'general', 'business_subtype' => 'CORP', 'self_ratio' => 70, 'payee_ratio' => 30],
                'rate' => 50,
                'lecture' => [['holder' => 'self', 'share' => 100]],
            ],
            [
                'key' => 'C8', 'name' => 'Case8_개인사업자_두과세라인', 'memo' => '개인 일반과세(TX-07) · 강의 R/S 50% + 인세 10% 동시 수취 · VAT 별도',
                'holder' => ['kind' => 'general', 'business_subtype' => 'SOLE'],
                'contract' => ['term_book_yn' => 1],
                'rate' => 50, 'royalty' => 10,
                'lecture' => [['holder' => 'self', 'share' => 100]], 'book' => true,
            ],
            [
                'key' => 'C9', 'name' => 'Case9_개인_지원금RS한도', 'memo' => '강의 지분 강사 60% / 자사 40% · R/S 50% · 지원금 R/S 10% 한도 100만 · 환불 시 한도 복원',
                'holder' => ['kind' => 'personal'],
                'contract' => ['term_dev_yn' => 1],
                'rate' => 50,
                'support' => ['method' => 'REVENUE_SHARE', 'cap' => 1000000, 'offset' => 'CONDITIONAL', 'rate' => 10, 'milestones' => []],
                'lecture' => [['holder' => 'self', 'share' => 60], ['holder' => 'internal', 'share' => 40]],
            ],
            [
                'key' => 'C10', 'name' => 'Case10_위탁자_면세', 'memo' => '위탁자 면세사업자(TX-11) · 위탁 수수료 25% NET_DEDUCT — 위탁 도서 공급 형태는 도서 화면에서 지정',
                'holder' => ['kind' => 'consignor', 'consignment_fee_rate' => 25.00, 'consignment_fee_type' => 'NET_DEDUCT'],
                'contract' => ['term_course_yn' => 0, 'term_cons_yn' => 1],
            ],
            [
                'key' => 'TX-SIMPLE', 'name' => '간이과세_세금계산서발급', 'memo' => '간이과세자(세금계산서 발급 사업자) · R/S 50%',
                'holder' => ['kind' => 'simplified', 'tax_invoice_eligible_yn' => 1],
                'rate' => 50,
            ],
            [
                'key' => 'TX-EXEMPT', 'name' => '면세사업자_판정보류', 'memo' => '면세사업자 — 정본은 판정 보류(DEV_TRANSFER 19-1 1-4 확인용)',
                'holder' => ['kind' => 'exempt'],
                'rate' => 50,
            ],
            [
                'key' => 'BUY', 'name' => '매절_기타소득', 'memo' => '매절 대금 50만 · 기타소득 C15 · 대상 강의 지정',
                'holder' => ['kind' => 'personal'],
                'contract' => ['term_buyout_yn' => 1],
                'rate' => 50,
                'buyout' => ['amount' => 500000, 'income_category' => 'OTHER', 'income_clause' => 'C15'],
                'lecture' => [['holder' => 'self', 'share' => 100]],
            ],
        ];
    }

    private function seedCase(array $case, int $internalId): void
    {
        $holderId = $this->createHolder($case['name'], $case['holder']);
        $contractId = $this->createContract($holderId, $case);
        $now = now();

        if (isset($case['rate'])) {
            DB::table('contract_rate_lines')->insert([
                'contract_id' => $contractId, 'rate_type' => 'BASIC', 'started_at' => self::START, 'ended_at' => self::END,
                'rate' => $case['rate'], 'mmg_amount' => $case['mmg'] ?? null, 'rate_basis' => 'NET_PG',
                'reason' => 'QA 시더 '.$case['key'], 'created_at' => $now, 'updated_at' => $now,
            ]);
        }

        if (isset($case['prepay'])) {
            $this->createPrepayment($contractId, $holderId, $case['prepay'], $case['contract']['prepayment_tax_type']);
        }

        if (isset($case['exclusive'])) {
            $this->createExclusive($contractId, $holderId, $case['exclusive']);
        }

        if (isset($case['support'])) {
            $this->createSupport($contractId, $holderId, $case['support']);
        }

        if (isset($case['buyout'])) {
            $this->milestone($contractId, 'BUYOUT', 1, '매절 대금', $case['buyout']['amount'], $case['buyout']['income_category'], $case['buyout']['income_clause']);
        }

        if (isset($case['payee'])) {
            $p = $case['payee'];
            $payeeId = $this->createHolder($p['name'], ['kind' => $p['kind'], 'business_subtype' => $p['business_subtype']]);
            foreach ([[$holderId, 'QA 원 권리자', '개인', 'TX-02', 1, $p['self_ratio']], [$payeeId, 'QA 소속사', '법인', 'TX-07', 0, $p['payee_ratio']]] as [$pid, $role, $entity, $tx, $author, $ratio]) {
                DB::table('contract_co_signers')->insert([
                    'contract_id' => $contractId, 'payee_id' => $pid, 'role' => $role, 'entity_type' => $entity, 'tax_case' => $tx,
                    'is_author' => $author, 'succession_yn' => 0, 'created_at' => $now, 'updated_at' => $now,
                ]);
                DB::table('payee_splits')->insert([
                    'contract_id' => $contractId, 'rights_holder_id' => $holderId, 'payee_id' => $pid, 'split_ratio' => $ratio,
                    'start_date' => self::START, 'note' => 'QA 시더 '.$case['key'], 'created_at' => $now, 'updated_at' => $now,
                ]);
            }
        }

        if (isset($case['lecture'])) {
            $this->mapLecture($case['key'], $contractId, $holderId, $internalId, $case['lecture']);
        }

        if (isset($case['royalty'])) {
            $bookId = $this->slotId($this->bookIds, self::BOOK_SLOTS, $case['key']);
            DB::table('book_royalty_contracts')->insert([
                'contract_id' => $contractId, 'book_id' => $bookId, 'temp_code' => $this->codes->forBookRoyalty(),
                'book_title' => $bookId ? null : 'QA 시더 교재 '.$case['key'], 'royalty_rate' => $case['royalty'],
                'royalty_basis' => 'ACTUAL_PAID', 'started_at' => self::START, 'ended_at' => self::END, 'status' => 'active',
                'memo' => 'QA 시더 '.$case['key'], 'created_at' => $now, 'updated_at' => $now,
            ]);
            if ($bookId) {
                DB::table('book_authors')->insert([
                    'book_id' => $bookId, 'rights_holder_id' => $holderId, 'contract_id' => $contractId, 'share_ratio' => 100,
                    'start_date' => self::START, 'end_basis' => 'CONTRACT_LINKED', 'end_date' => self::END,
                    'change_reason' => 'QA 시더 '.$case['key'], 'created_at' => $now, 'updated_at' => $now,
                ]);
            } else {
                $this->command?->warn("  {$case['key']}: QA_SETTLE_BOOK_IDS 가 모자라 도서 매핑을 건너뜀(출간 전 저서로만 등록)");
            }
        }
    }

    private function createHolder(string $name, array $h): int
    {
        $kind = $h['kind'];
        $isBiz = in_array($kind, ['general', 'simplified', 'exempt', 'consignor'], true);
        $n = ++$this->fakeSeq;
        $now = now();

        $row = [
            'code' => $this->codes->forHolder(),
            'name' => self::PREFIX.$name,
            'rights_holder_type' => $kind === 'consignor' ? 'CONSIGNOR' : 'RIGHTS_HOLDER',
            'is_internal' => 0,
            'tax_type' => match ($kind) { 'personal' => 'personal', 'consignor' => 'exempt', default => $kind },
            'email' => "qa-seed-{$n}@e2e.invalid",
            'partnership_started_at' => self::START,
            'is_resident' => 1,
            'main_work_external_labor' => 0,
            'bank_name' => '테스트은행',
            // 가짜 계좌 — 실제 번호 형식과 겹치지 않게 0 으로 채운다
            'account_no_enc' => Crypt::encryptString(sprintf('000-0000-%04d', $n)),
            'account_holder' => self::PREFIX.$name,
            'destruction_hold' => 0,
            'consignment_promo_override_yn' => 0,
            'created_at' => $now,
            'updated_at' => $now,
        ];

        if ($isBiz) {
            $row += [
                // 가짜 사업자번호 — 999 로 시작해 실제 번호와 겹치지 않게 한다. 국세청 조회는 하지 않는다
                'business_number' => sprintf('999%07d', $n),
                'ceo_name' => 'QA대표',
                'biz_category' => '서비스',
                'biz_item' => '교육',
                'business_status' => '계속',
                'business_subtype' => $h['business_subtype'] ?? 'SOLE',
                'open_date' => '2020-01-01',
                'vat_treatment' => 'ADD',
                'tax_email' => "qa-seed-tax-{$n}@e2e.invalid",
                'tax_invoice_eligible_yn' => $h['tax_invoice_eligible_yn'] ?? null,
                'consignment_fee_rate' => $h['consignment_fee_rate'] ?? null,
                'consignment_fee_type' => $h['consignment_fee_type'] ?? null,
            ];
        } else {
            $row += [
                // 가짜 주민번호 — 000000 으로 시작해 실제 번호와 겹치지 않는다
                'resident_no_enc' => Crypt::encryptString(sprintf('000000-%07d', $n)),
                'birth_date' => '1990-01-01',
                'payee_is_author' => 1,
                'income_category' => $h['income_category'] ?? null,
                'income_clause' => $h['income_clause'] ?? null,
            ];
        }

        return (int) DB::table('rights_holders')->insertGetId($row);
    }

    private function createContract(int $holderId, array $case): int
    {
        $now = now();
        $id = (int) DB::table('rights_holder_contracts')->insertGetId(array_merge([
            'rights_holder_id' => $holderId,
            'code' => $this->codes->forContract(),
            'sequence_no' => 1,
            'title' => 'QA 시더 '.$case['key'].' — '.$case['memo'],
            'started_at' => self::START,
            'ended_at' => self::END,
            'initial_end_date' => self::END,
            'status' => 'active',
            'auto_extend' => 0,
            'is_locked' => 0,
            'refund_promo_burden_type' => 'A',
            'origin_type' => 'NEW',
            'term_course_yn' => 1,
            'min_payout_limit' => 100000,
            'min_claim_limit' => -100000,
            'contract_expiry_alert_days' => 30,
            'memo' => 'QA 시더(정산 04권 '.$case['key'].')',
            'created_at' => $now,
            'updated_at' => $now,
        ], $case['contract'] ?? []));

        DB::table('contract_terms')->insert([
            'contract_id' => $id, 'sequence_no' => 1, 'term_type' => 'INITIAL', 'confirmed_at' => now()->toDateString(),
            'start_date' => self::START, 'end_date' => self::END, 'reason' => '최초 계약', 'created_at' => $now,
        ]);

        return $id;
    }

    /**
     * 선급금 — 잔액은 반영(DONE) 라인의 합이다(RightsHolderContractPrepaymentService).
     * 화면 등록은 AGREEMENT 로 남아 잔액이 0 이 되는 결함(DEV_TRANSFER 19-1 1-3)이 있어, 시더는 DONE 으로 넣는다.
     */
    private function createPrepayment(int $contractId, int $holderId, int $amount, string $nature): void
    {
        $now = now();
        DB::table('prepayment_ledger_lines')->insert([
            'contract_id' => $contractId, 'line_no' => 1, 'base_month' => '2026-10', 'line_type' => 'PAY', 'amount' => $amount,
            'status' => 'DONE', 'nature' => $nature, 'memo' => 'QA 시더 선급금 지급', 'created_at' => $now, 'updated_at' => $now,
        ]);
        DB::table('prepayment_ledgers')->insert([
            'contract_id' => $contractId, 'rights_holder_id' => $holderId, 'principal_amount' => $amount, 'offset_amount' => 0,
            'balance_amount' => $amount, 'prepayment_tax_type' => $nature, 'paid_at' => '2026-10-31', 'status' => 'ACTIVE',
            'is_locked' => 0, 'destruction_hold' => 0, 'created_at' => $now, 'updated_at' => $now,
        ]);
    }

    private function createExclusive(int $contractId, int $holderId, array $e): void
    {
        $now = now();
        DB::table('exclusive_contract_fees')->insert([
            'contract_id' => $contractId, 'rights_holder_id' => $holderId, 'fee_amount' => $e['amount'],
            'payment_method' => $e['method'], 'income_category' => 'BUSINESS', 'payee_is_author' => 0, 'target_month' => '2026-11',
            'service_started_at' => self::START, 'service_ended_at' => self::END, 'total_service_days' => 365,
            'clawback_policy' => $e['clawback'], 'penalty_clause_yn' => 0, 'penalty_offset_consent_yn' => 0,
            'approval_status' => 'pending', 'status' => 'active', 'memo' => 'QA 시더', 'created_at' => $now, 'updated_at' => $now,
        ]);
        foreach ($e['milestones'] as $i => $amount) {
            $this->milestone($contractId, 'EXC', $i + 1, '전속계약금 '.($i + 1).'회차', $amount, 'BUSINESS', null, sprintf('2026-%02d', 11 + $i));
        }
    }

    private function createSupport(int $contractId, int $holderId, array $s): void
    {
        $now = now();
        $agreementId = (int) DB::table('support_fund_agreements')->insertGetId([
            'contract_id' => $contractId, 'rights_holder_id' => $holderId, 'payment_method' => $s['method'],
            'total_cap_amount' => $s['cap'], 'rate_basis' => $s['method'] === 'REVENUE_SHARE' ? 'SAME_AS_BASIC' : null,
            'settlement_scope' => 'PIPELINE_1_1_ONLY', 'start_date' => self::START, 'end_basis' => 'CONTRACT_LINKED',
            'offset_type' => $s['offset'], 'cap_restore_on_refund' => 1, 'on_termination_policy' => 'FORFEIT',
            'income_category' => 'BUSINESS', 'status' => 'ACTIVE', 'lecture_target_scope' => 'ALL', 'book_target_scope' => 'ALL',
            'destruction_hold' => 0, 'created_at' => $now, 'updated_at' => $now,
        ]);
        if (isset($s['rate'])) {
            DB::table('contract_rate_lines')->insert([
                'contract_id' => $contractId, 'rate_type' => 'SUPPORT', 'agreement_id' => $agreementId, 'started_at' => self::START,
                'ended_at' => self::END, 'rate' => $s['rate'], 'rate_basis' => 'NET_PG', 'reason' => 'QA 시더 지원금 R/S',
                'created_at' => $now, 'updated_at' => $now,
            ]);
        }
        foreach ($s['milestones'] as $i => $amount) {
            $this->milestone($contractId, 'DEV', $i + 1, '개발지원금 일시금', $amount, 'BUSINESS', null);
        }
    }

    private function milestone(int $contractId, string $term, int $seq, string $title, int $amount, string $income, ?string $clause, string $month = '2026-11'): void
    {
        $now = now();
        DB::table('contract_milestones')->insert([
            'contract_id' => $contractId, 'term_type' => $term, 'sequence_no' => $seq, 'title' => $title, 'target_month' => $month,
            'amount' => $amount, 'income_category' => $income, 'income_clause' => $clause, 'verify_method' => 'MANUAL_NOTE',
            'approval_status' => 'pending', 'created_at' => $now, 'updated_at' => $now,
        ]);
    }

    private function mapLecture(string $key, int $contractId, int $holderId, int $internalId, array $shares): void
    {
        $lectureId = $this->slotId($this->lectureIds, self::LECTURE_SLOTS, $key);
        if (! $lectureId) {
            $this->command?->warn("  {$key}: QA_SETTLE_LECTURE_IDS 가 모자라 강의 매핑을 건너뜀");

            return;
        }

        $internalContract = DB::table('rights_holder_contracts')->where('rights_holder_id', $internalId)
            ->where('status', 'active')->orderBy('id')->value('id');
        $now = now();

        if (! $internalContract && count($shares) > 1) {
            $this->command?->warn("  {$key}: 자사 권리자에 진행 중 계약이 없어 강의 매핑을 건너뜀");

            return;
        }

        foreach ($shares as $s) {
            $self = $s['holder'] === 'self';
            DB::table('lecture_instructors')->insert([
                'lecture_id' => $lectureId,
                'rights_holder_id' => $self ? $holderId : $internalId,
                'contract_id' => $self ? $contractId : $internalContract,
                'share_ratio' => $s['share'], 'start_date' => self::START, 'end_basis' => 'CONTRACT_LINKED', 'end_date' => self::END,
                'change_reason' => 'QA 시더 '.$key, 'created_at' => $now, 'updated_at' => $now,
            ]);
        }

        if ($key === 'BUY') {
            DB::table('contract_term_targets')->insert([
                'contract_id' => $contractId, 'term_type' => 'BUYOUT', 'target_type' => 'LECTURE', 'target_id' => $lectureId, 'created_at' => $now,
            ]);
        }
    }

    /**
     * 자사 권리자 — 이미 있으면 그대로 쓴다. 없을 때만(빈 dev DB) 1건과 자사 기본 계약(요율 100%)을 만든다.
     */
    private function internalHolder(): int
    {
        $existing = DB::table('rights_holders')->where('is_internal', 1)->whereNull('deleted_at')->orderBy('id')->value('id');
        if ($existing) {
            return (int) $existing;
        }

        $id = $this->createHolder('자사권리자', ['kind' => 'general', 'business_subtype' => 'CORP']);
        DB::table('rights_holders')->where('id', $id)->update(['is_internal' => 1]);
        $contractId = $this->createContract($id, ['key' => 'INTERNAL', 'memo' => '자사 기본 계약']);
        DB::table('contract_rate_lines')->insert([
            'contract_id' => $contractId, 'rate_type' => 'BASIC', 'started_at' => self::START, 'ended_at' => self::END, 'rate' => 100,
            'rate_basis' => 'NET_PG', 'reason' => 'QA 시더 자사 기본 요율', 'created_at' => now(), 'updated_at' => now(),
        ]);

        return $id;
    }

    private function idsFromEnv(string $key): array
    {
        return array_values(array_filter(array_map('intval', explode(',', (string) env($key, '')))));
    }

    private function slotId(array $ids, array $slots, string $key): ?int
    {
        $i = array_search($key, $slots, true);

        return $i === false ? null : ($ids[$i] ?? null);
    }

    /** 정리용 SQL — 참고로만 둔다(자동 실행하지 않음) */
    public static function cleanupSql(): string
    {
        return <<<'SQL'
SET @h := (SELECT GROUP_CONCAT(id) FROM rights_holders WHERE name LIKE 'QA시더\_%');
-- 아래는 rights_holder_contracts.rights_holder_id IN (@h 목록)의 계약 id 로 차례로 지운다:
-- lecture_instructors, book_authors, book_royalty_contracts, contract_term_targets, contract_milestones,
-- contract_rate_lines, support_fund_agreements, exclusive_contract_fees, prepayment_ledger_lines, prepayment_ledgers,
-- payee_splits, contract_co_signers, contract_terms → rights_holder_contracts → rights_holders
SQL;
    }
}
