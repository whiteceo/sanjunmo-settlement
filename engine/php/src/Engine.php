<?php
/**
 * 정산 단계 목록 · 추적 기록(trace) · 계산 상태 · 실행기.
 *
 * 입력 배열(input.schema.json, 한 정산월) → 0~13단계를 SPEC 2절 순서대로 실행 → 출력 배열(output.schema.json).
 * 단계 클래스는 run(Context) 하나만 가진다. 단계 사이 값은 ContractState · PayeeState에 담아 넘긴다.
 * 파이썬 판 engine/core/pipeline.py · steps.py · trace.py 와 1:1로 대응한다.
 */

namespace SettleCalc;

use BcMath\Number;

const ENGINE_VERSION = '1.0.0';
const CANON_VERSION = '정본 v4.0.x · main 2026-10-26(SPEC.md 기준)';

final class Step
{
    public function __construct(public int $no, public string $code, public string $name, public string $ref,
                                public string $cls)
    {
    }
}

final class Steps
{
    /** @var Step[] */
    public static array $all = [];
    /** @var array<string, Step> */
    public static array $byCode = [];

    public static function init(): void
    {
        if (self::$all) {
            return;
        }
        $rows = [
            [0, 'PIPELINE_IN', '상위 인입 파이프라인', 'V2 §8.3 1단계 L129~160 · SPEC 3절', S00PipelineIn::class],
            [1, 'CARRY_IN', '전월 이월 승계', 'V2 §8.3 1단계 L168 · L180~182 · SPEC 4절', S01CarryIn::class],
            [2, 'ACCRUAL', '순 발생액 산출', 'V2 §8.3 2단계 L169 · L183~191 · SPEC 5절', S02Accrual::class],
            [3, 'MMG_ADJ', '월 보장액 보정', 'V2 §8.3 3단계 L170 · L192~195 · SPEC 6절', S03MmgAdj::class],
            [4, 'DEDUCT', '환불 및 프로모션 공제', 'V2 §8.3 4단계 L171 · L196~203 · SPEC 7절', S04Deduct::class],
            [5, 'SUPPORT_CAP', '지원금 한도 · 순누계', 'V2 §8.3 5단계 L172 · L204~214 · SPEC 8절', S05SupportCap::class],
            [6, 'PREPAY_OFFSET', '선급금 상계', 'V2 §8.3 6단계 L173 · L215~236 · SPEC 9절', S06PrepayOffset::class],
            [7, 'LUMPSUM_ADD', '비정기 가산', 'V2 §8.3 7단계 L174 · L237~244 · SPEC 10절', S07LumpsumAdd::class],
            [8, 'PAYEE_SPLIT', '수취인 분할', 'V2 §8.3 8단계 L175 · L245~259 · SPEC 11절', S08PayeeSplit::class],
            [9, 'TAX', '세무 판정 · 원천세', 'V2 §8.3 9단계 L176 · L260~283 · 11장 · TAX.md', S09Tax::class],
            [10, 'CLAIM', '반환 반영 · 청구 판정', 'V2 §8.3 10단계 L177 · L284~298 · SPEC 13절', S10Claim::class],
            [11, 'PAYOUT', '최소 지급 검증', 'V2 §8.3 11단계 L178 · L299~308 · SPEC 14절', S11Payout::class],
            [12, 'CLOSE_CHECK', '마감 검증(이월 연속성)', 'V1 §7.4 L588~595 · SPEC 15.1', S12CloseCheck::class],
            [13, 'PASS_REFUND_PAYOUT', '합격환급 수강생 지급(권리자 정산 밖)', '통합 설계서 S6 L438~446 · S-02 · S-14',
                S13PassRefundPayout::class],
        ];
        foreach ($rows as [$no, $code, $name, $ref, $cls]) {
            $s = new Step($no, $code, $name, $ref, $cls);
            self::$all[] = $s;
            self::$byCode[$code] = $s;
        }
    }

    /** 스텝 코드 → 단계 번호. 모르는 코드는 99(맨 뒤 정렬). */
    public static function no(string $code): int
    {
        self::init();
        return isset(self::$byCode[$code]) ? self::$byCode[$code]->no : 99;
    }
}

/** 단계 추적 기록 — output.schema.json #trace_row 규격(SPEC 15.10). 출력 값 목록(values)은 trace에서 뽑는다. */
final class Trace
{
    public array $entries = [];

    public function add(string $step, string $field, $value, $holder = null, $contract = null, $payee = null,
                        $line = null, $agreement = null, $ref_id = null, $line_key = null, ?array $inputs = null,
                        string $formula = '', string $code = '', $before = null, string $rounding = 'NONE',
                        string $ref = '', bool $provisional = false, ?string $note = null, bool $output = true)
    {
        $s = Steps::$byCode[$step];
        $this->entries[] = [
            'seq' => count($this->entries) + 1,
            'step' => $s->no,
            'step_code' => $s->code,
            'scope' => ['rights_holder_id' => $holder, 'contract_id' => $contract, 'payee_id' => $payee,
                'line_id' => $line, 'line_key' => $line_key, 'agreement_id' => $agreement, 'ref_id' => $ref_id],
            'field' => $field,
            'inputs' => new Obj(to_json($inputs ?? [])),
            'formula' => $formula,
            'formula_code' => $code,
            'before_rounding' => to_json($before),
            'rounding' => $rounding,
            'result' => to_json($value),
            'canon_ref' => $ref !== '' ? $ref : $s->ref,
            'provisional' => $provisional,
            'note' => $note ?? '',
            'output' => $output,
        ];
        return $value;
    }

    /** 출력 값 목록(대조 · 테스트 기준). 키 = (권리자, 계약, 수취인, 라인, 단계, 필드). */
    public function values(): array
    {
        $out = [];
        foreach ($this->entries as $e) {
            if (!$e['output']) {
                continue;
            }
            $sc = $e['scope'];
            $out[] = ['rights_holder_id' => $sc['rights_holder_id'], 'contract_id' => $sc['contract_id'],
                'payee_id' => $sc['payee_id'], 'line_id' => $sc['line_id'], 'step_code' => $e['step_code'],
                'field' => $e['field'], 'value' => $e['result']];
        }
        return $out;
    }
}

final class EngineStop extends \Exception
{
    public function __construct(public string $status, public string $stopCode, public string $msg, public string $ref = '')
    {
        parent::__construct($msg);
    }
}

// ---------------------------------------------------------------- 날짜 · 기간

function month_of($d): ?string
{
    return truthy($d) ? head(pystr($d), 7) : null;
}

function month_last(string $m): string
{
    $y = (int)substr($m, 0, 4);
    $mo = (int)substr($m, 5, 2);
    $days = (int)(new \DateTimeImmutable(sprintf('%04d-%02d-01', $y, $mo)))->format('t');
    return sprintf('%s-%02d', $m, $days);
}

/** 월 차이 b − a (YYYY-MM). */
function months_between(string $a, string $b): int
{
    return ((int)substr($b, 0, 4) - (int)substr($a, 0, 4)) * 12 + (int)substr($b, 5, 2) - (int)substr($a, 5, 2);
}

/** 유효 종료일: FIXED_DATE면 end_date, CONTRACT_LINKED면 계약 current_end_date(V1 §5.1 L210). */
function period_end(array $row, ?array $contractRow)
{
    if (g($row, 'end_basis') === 'CONTRACT_LINKED') {
        return g($contractRow ?? [], 'current_end_date');
    }
    return g($row, 'end_date');
}

/** date가 row의 [start_date, 유효 종료일] 안인가. 날짜가 없으면 통과. */
function valid_on(array $row, $date, ?array $contractRow = null): bool
{
    if (!truthy($date)) {
        return true;
    }
    $s = g($row, 'start_date');
    $e = period_end($row, $contractRow);
    return (!truthy($s) || strcmp(pystr($s), pystr($date)) <= 0) && (!truthy($e) || strcmp(pystr($date), pystr($e)) <= 0);
}

// ---------------------------------------------------------------- 상태

/** 계약 단위 정산 라인(SPEC 1절 라인 키). */
final class Line
{
    public $rate_type;
    public $agreement_id;
    public $approval_id;
    public $income_category;
    public $income_clause;
    public $tax_threshold_unit_key;
    public $payee_is_author;
    public $supply_nature;
    public $offset_type;
    public $item_kind;
    public $fixed_payee;            // Q-15: 약정 · 승인 원장 수취인(권리자와 다르면 단독 귀속)
    public bool $protected = false; // 상계 비대상 보호분(SPEC 12.1)
    public Number $new;             // 2단계 신규 세전액
    public array $deduct_components = [];
    public ?Number $adjusted = null; // 3단계 보정 후 금액(P1.1)
    public Number $mmg_subsidy;
    public ?Number $net = null;     // 4 · 5단계 후 세전 순액(분할 대상)
    public Number $offset;          // 6단계 라인별 상계 배분
    public Number $eligible;        // 6단계 상계 적격액
    public bool $conditional = false;
    public ?Number $support_deduct = null;
    public ?array $support_txs = null;
    public ?Number $new_confirmed = null;
    public ?Number $deduct_1_1 = null;

    public function __construct(public string $label, public $contract_id, public string $pipeline_id, array $kw = [])
    {
        foreach (['rate_type', 'agreement_id', 'approval_id', 'income_category', 'income_clause',
                     'tax_threshold_unit_key', 'payee_is_author', 'supply_nature', 'offset_type', 'item_kind',
                     'fixed_payee'] as $k) {
            $this->$k = $kw[$k] ?? null;
        }
        $this->protected = (bool)($kw['protected'] ?? false);
        $this->new = new Number(0);
        $this->mmg_subsidy = new Number(0);
        $this->offset = new Number(0);
        $this->eligible = new Number(0);
    }

    public function key(): array
    {
        return ['contract_id' => $this->contract_id, 'pipeline_id' => $this->pipeline_id, 'rate_type' => $this->rate_type,
            'agreement_id' => $this->agreement_id, 'approval_id' => $this->approval_id,
            'income_category' => $this->income_category, 'income_clause' => $this->income_clause,
            'tax_threshold_unit_key' => $this->tax_threshold_unit_key];
    }
}

final class PayeeState
{
    public array $lines = []; // 8 · 9단계 payee × 라인 결과(output.schema payees[].lines[])
    public array $out = ['TAX' => [], 'CLAIM' => [], 'PAYOUT' => []];

    public function __construct(public $payee_id)
    {
    }
}

final class ContractState
{
    public $id;
    public $holder_id;
    /** @var array<string, Line> */
    public array $lines = [];
    public array $out = [];
    /** @var array<string, PayeeState> */
    public array $payees = [];
    public array $carry;
    public array $return_claims = [];
    public ?array $prepay = null;
    public ?Number $prepay_balance_after = null;
    public array $splits = [];
    public ?array $consignment = null;
    public ?array $consignment_return = null;
    public Number $mmg_subsidy;
    public array $support = [];
    public array $lumpsum_rows = [];

    public function __construct(public array $row)
    {
        $this->id = $row['contract_id'];
        $this->holder_id = $row['rights_holder_id'];
        $this->carry = ['pre_pos' => [], 'pre_neg' => [], 'post_pos' => [], 'post_neg' => [], 'cons' => new Number(0),
            'cons_rows' => []];
        $this->mmg_subsidy = new Number(0);
    }

    public function line(string $label, string $pipeline, array $kw = []): Line
    {
        if (!isset($this->lines[$label])) {
            $this->lines[$label] = new Line($label, $this->id, $pipeline, $kw);
        }
        return $this->lines[$label];
    }

    /** @return Line[] */
    public function linesOf(string $pipeline): array
    {
        return array_values(array_filter($this->lines, fn(Line $l) => $l->pipeline_id === $pipeline));
    }

    public function payee($pid): PayeeState
    {
        $k = (string)$pid;
        if (!isset($this->payees[$k])) {
            $this->payees[$k] = new PayeeState($pid);
        }
        return $this->payees[$k];
    }

    public function &stepOut(string $code): array
    {
        if (!isset($this->out[$code])) {
            $this->out[$code] = [];
        }
        return $this->out[$code];
    }

    /** 만료 · 해지 귀속월이 당월인가(V2 L287 · SPEC 13.2). */
    public function endInMonth(string $month): bool
    {
        foreach (['termination_date', 'current_end_date'] as $k) {
            if (truthy(g($this->row, $k)) && month_of($this->row[$k]) === $month) {
                return true;
            }
        }
        return false;
    }
}

final class Context
{
    public const LIST_KEYS = ['pass_refund_payouts', 'rights_holders', 'contracts', 'rate_lines', 'lecture_instructors',
        'book_authors', 'payee_splits', 'support_fund_agreements', 'support_fund_agreement_targets',
        'support_fund_ledger_prev', 'prepayments', 'order_items', 'orders', 'refund_lines', 'pass_refund_deductions',
        'lumpsum_approvals', 'clawbacks', 'carryover_ledger', 'carryover_prev_end_balances', 'adjustments',
        'payout_results'];

    // V3 부록 B 기본값(SPEC 12.1 · 15.2). 입력 params가 있으면 덮어쓴다.
    public const DEFAULT_PARAMS = [
        'default_min_payout_limit' => 100000,
        'default_min_claim_limit' => -100000,
        'payout_threshold_basis' => 'VAT_INCLUDED',
        'default_weight_seconds' => 60,
        'other_income_min_tax_amount' => 50000,
        'local_income_tax_rate' => '0.10',
        'small_amount_exemption_limit' => 1000,
        'local_tax_small_exemption_apply_yn' => false,
        'carryover_force_settle_month' => 12,
        'carryover_max_months' => 6,
        'manual_adj_approval_threshold' => 1000000,
        'support_fund_mmg_include_yn' => false,
        'adj_two_step_approval_yn' => false, // 1차 오픈 재무 담당자 단독 확정(V2 §10.3 · D-SETT-01), 2차에 true
        'month_closed_at' => [],             // {귀속월: 마감 일시} — 보정 전표 반영 기준월 판정(V2 §10.2 · S-10)
    ];

    public static ?array $taxTableCache = null;

    public array $input;
    public string $month;
    public array $params;
    public array $tax_table;
    public Trace $trace;
    public array $errors = [];
    public array $warnings = [];
    public array $issues = [];
    public array $holders = [];
    /** @var array<string, ContractState> */
    public array $contracts = [];
    public array $internal_only = [];
    public array $excluded_lines = [];
    public array $pending_adjustments = []; // adjustment_mode = hold
    public array $applied_adjustments = []; // adjustment_mode = apply(기본) — 8 · 10단계에서 계산에 넣은 전월 정산 조정
    public array $auto_adjustments = [];    // 마감된 달의 환불 보정 전표 → 전월 정산 조정(4단계에서 생성)
    public array $continuity = [];
    public array $ledgers = ['support_fund_ledger' => [], 'mmg_subsidy_ledger' => [], 'carryover_ledger' => [],
        'prepayment_ledger' => []];
    public array $own_holder = [];          // agreement_id → 자사 재원 검증
    public array $pass_refund_payouts = []; // 13 합격환급 수강생 지급
    public array $basis = [];               // agreement_id → 지원금 모수 · 자사 산출액(0단계)

    public function __construct(array $data, array $taxTable)
    {
        $this->input = $data;
        foreach (self::LIST_KEYS as $k) {
            $this->input[$k] = array_values((array)(truthy(g($data, $k)) ? $data[$k] : []));
        }
        $this->month = head(pystr(either(g($data, 'settlement_month'), '')), 7);
        $this->params = self::DEFAULT_PARAMS;
        foreach ((array)(either(g($data, 'params'), [])) as $k => $v) {
            if ($v !== null) {
                $this->params[$k] = $v;
            }
        }
        $this->tax_table = $taxTable;
        $this->trace = new Trace();
        foreach ($this->input['rights_holders'] as $h) {
            $this->holders[(string)$h['rights_holder_id']] = $h;
        }
        foreach ($this->input['contracts'] as $c) {
            $this->contracts[(string)$c['contract_id']] = new ContractState($c);
        }
    }

    public function holder($hid): array
    {
        return $this->holders[(string)$hid] ?? ['rights_holder_id' => $hid];
    }

    public function contract($cid): ?ContractState
    {
        return $cid === null ? null : ($this->contracts[(string)$cid] ?? null);
    }

    /** 요율 라인 조회(V2 L135 · V1 L210). pipeline_id는 같은 계약에 파이프라인별 요율이 있을 때(스키마 확장). */
    public function rate($contractId, string $rateType, $date = null, ?string $pipelineId = null, $agreementId = null): ?array
    {
        $c = $this->contract($contractId);
        $rows = array_values(array_filter($this->input['rate_lines'], fn($r) => $r['contract_id'] === $contractId
            && $r['rate_type'] === $rateType && ($agreementId === null || g($r, 'agreement_id') === $agreementId)
            && valid_on($r, $date, $c?->row)));
        if ($pipelineId !== null) {
            $exact = array_values(array_filter($rows, fn($r) => g($r, 'pipeline_id') === $pipelineId));
            $rows = $exact ?: array_values(array_filter($rows, fn($r) => !truthy(g($r, 'pipeline_id'))));
        }
        if (count($rows) > 1) {
            $this->warn('RATE_LINE_OVERLAP', sprintf('%s %s 유효 요율 라인이 %d건 — 첫 행 사용', pystr($contractId), $rateType,
                count($rows)), 'V1 §5.1 L210');
        }
        return $rows[0] ?? null;
    }

    /** 기록. kw: holder · contract(없으면 계약에서) · agreement · ref_id · line_key · inputs · formula · code · before · rounding · ref · provisional · note · output */
    public function emit(string $step, string $field, $value, ?ContractState $c = null, $payee = null, $line = null, ...$kw)
    {
        $holder = array_key_exists('holder', $kw) ? $kw['holder'] : ($c ? $c->holder_id : null);
        $contract = array_key_exists('contract', $kw) ? $kw['contract'] : ($c ? $c->id : null);
        unset($kw['holder'], $kw['contract']);
        return $this->trace->add($step, $field, $value, $holder, $contract, $payee, $line, ...$kw);
    }

    public function warn(string $code, string $message, string $ref = ''): void
    {
        $this->warnings[] = ['code' => $code, 'message' => $message, 'canon_ref' => $ref];
    }

    /** kind: INPUT_MISSING · CANON_GAP(잠정 규칙 사용) · CANON_CONFLICT. */
    public function issue(string $kind, string $message, ?string $step = null, $holder = null, ?string $ref = null,
                          ?string $q = null): void
    {
        $item = ['kind' => $kind, 'step_code' => $step, 'rights_holder_id' => $holder, 'message' => $message,
            'ref' => $ref, 'question' => $q];
        if (!in_array($item, $this->issues, true)) {
            $this->issues[] = $item;
        }
    }

    public function stop(string $status, string $code, string $message, string $ref = ''): never
    {
        throw new EngineStop($status, $code, $message, $ref);
    }

    public function p(string $name)
    {
        return $this->params[$name] ?? null;
    }
}

/**
 * 전월 정산 조정 라인(마감 후 정정) — 차월 정산서 반영(V2 §10.1 L353 · §10.2).
 * 인입 위치(2026-10-27 white 결정, SPEC Q-23 해소): 세금 계산 직전.
 *   PRE_TAX · 위탁(2.2) → 8단계 뒤 비분할 라인(origin = ADJUSTMENT) → 9단계에서 원천세 · VAT
 *   POST_TAX → 10단계: 양수는 지급채무에 가산, 음수는 반환채권(청구 음수 항, 자동 상계 없음 — Q-19와 같음)
 * adjustment_mode = "hold"이면 계산에 넣지 않고 pending_adjustments로만 낸다.
 */
final class Adjust
{
    const PIPE_SUPPLY = ['1.1' => 'LECTURE_RS', '2.1' => 'ROYALTY', '5.1' => 'SUPPORT_RS', '2.2' => 'BOOK_GOODS',
        'LUMPSUM' => 'NONRECURRING'];

    /** apply(기본) · provisional(예전 잠정안 이름, apply와 같음) → 반영, hold → 보류. */
    public static function mode(Context $ctx): string
    {
        return g($ctx->input, 'adjustment_mode') === 'hold' ? 'hold' : 'apply';
    }

    /** 이 정산월에 반영할 조정(입력 adjustments의 applied_month = 정산월 + 보정 전표 자동 조정). */
    public static function monthAdjustments(Context $ctx): array
    {
        $rows = array_values(array_filter($ctx->input['adjustments'],
            fn($a) => head(pystr(either(g($a, 'applied_month'), $ctx->month)), 7) === $ctx->month));
        return array_merge($rows, $ctx->auto_adjustments);
    }

    public static function account(array $a)
    {
        if (pystr(g($a, 'pipeline_id')) === '2.2' || truthy(g($a, 'consignment_balance_yn'))) {
            return 'CONSIGNMENT';
        }
        return either(g($a, 'account_type'), 'PRE_TAX');
    }
}

final class Engine
{
    /** 정산 실행. $taxTable 생략 시 engine/tax_table.json. */
    public static function run(array $data, ?array $taxTable = null): array
    {
        Steps::init();
        if ($taxTable === null) {
            if (Context::$taxTableCache === null) {
                Context::$taxTableCache = json_decode(file_get_contents(__DIR__ . '/../../tax_table.json'), true);
            }
            $taxTable = Context::$taxTableCache;
        }
        $ctx = new Context($data, $taxTable);
        $status = 'OK';
        try {
            if (truthy(g($data, 'locked'))) {
                $ctx->stop('LOCKED_MONTH', 'LOCKED_MONTH', '마감된 정산월 — 마감 취소 금지, 차월 조정 라인으로', 'V2 §10.1 L350');
            }
            foreach (Steps::$all as $s) {
                ($s->cls)::run($ctx);
            }
            foreach ($ctx->contracts as $c) {
                foreach ($c->payees as $p) {
                    foreach ($p->lines as $ln) {
                        if (g($ln, 'tax_decision_status') === 'PENDING_REVIEW') {
                            $status = 'BLOCKED_PENDING_REVIEW';
                        }
                    }
                }
            }
        } catch (EngineStop $ex) {
            $status = $ex->status;
            $ctx->errors[] = ['code' => $ex->stopCode, 'message' => $ex->msg, 'canon_ref' => $ex->ref];
        }
        return self::buildOutput($ctx, $status, $data);
    }

    private static function buildOutput(Context $ctx, string $status, array $data): array
    {
        $holders = [];
        foreach ($ctx->contracts as $c) {
            $hk = (string)$c->holder_id;
            if (!isset($holders[$hk])) {
                $holders[$hk] = ['rights_holder_id' => $c->holder_id,
                    'is_internal' => truthy(g($ctx->holder($c->holder_id), 'is_internal')), 'contracts' => []];
            }
            $payees = [];
            foreach ($c->payees as $p) {
                $payees[] = array_merge(['payee_id' => $p->payee_id, 'lines' => $p->lines], $p->out);
            }
            $holders[$hk]['contracts'][] = ['contract_id' => $c->id, 'steps' => new Obj($c->out), 'payees' => $payees];
        }
        $steps = array_map(fn(Step $s) => ['no' => $s->no, 'code' => $s->code, 'name' => $s->name, 'ref' => $s->ref],
            Steps::$all);
        return to_json([
            'settlement_month' => $ctx->month,
            'engine_version' => ENGINE_VERSION,
            'canon_version' => CANON_VERSION,
            'run_reason' => g($data, 'run_reason'),
            'status' => $status,
            'errors' => $ctx->errors,
            'warnings' => $ctx->warnings,
            'rights_holders' => array_values($holders),
            'ledgers' => $ctx->ledgers,
            'continuity' => $ctx->continuity,
            'internal_only' => $ctx->internal_only,
            'excluded_lines' => $ctx->excluded_lines,
            'pending_adjustments' => $ctx->pending_adjustments,
            'applied_adjustments' => $ctx->applied_adjustments,
            'pass_refund_payouts' => $ctx->pass_refund_payouts,
            'issues' => $ctx->issues,
            'steps' => $steps,
            'values' => $ctx->trace->values(),
            'trace' => $ctx->trace->entries,
        ]);
    }
}
