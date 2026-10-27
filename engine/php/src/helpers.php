<?php
/**
 * 금액 · 절사 도구(정산 02권 13장, SPEC 0절 의사코드 규약) + 파이썬 판과 같은 결과를 내기 위한 보조 함수.
 *
 * - 금액은 모두 BcMath\Number(float 금지). 사칙연산은 add · sub · mul · div 로만 한다.
 *   파이썬 판(Decimal 기본 문맥: 유효숫자 28자리 · ROUND_HALF_EVEN)과 끝자리까지 같게 하려고
 *   연산 결과가 유효숫자 28자리를 넘으면 같은 규칙으로 반올림한다.
 * - floor_won(x) = 원 단위 내림, 음수는 절대값 내림 후 부호 복원(V2 §13.1 L569) = 0 방향 버림.
 * - q4(x) = 소수 4자리 보존(DECIMAL(18,4), V2 §13.1 L565). 4자리 밖은 버림(SPEC Q-01 잠정).
 * - alloc_last_remainder = 13.2 총액 역산: 선행 항목 floor, 마지막 항목 = 총액 − Σ선행(V2 §13.2 L573).
 */

namespace SettleCalc;

use BcMath\Number;
use RoundingMode;

const PREC = 28;   // 파이썬 Decimal 기본 유효숫자
const WORK = 80;   // 나눗셈 작업 자릿수

// ------------------------------------------------------------------ Decimal

/** 입력값 → Number. null · '' 는 0. float은 파이썬 repr과 같은 문자열을 거친다. */
function D($x): Number
{
    if ($x instanceof Number) {
        return $x;
    }
    if ($x === null || $x === '') {
        return new Number(0);
    }
    if (is_bool($x)) {
        return new Number($x ? 1 : 0);
    }
    if (is_int($x)) {
        return new Number($x);
    }
    if (is_float($x)) {
        return new Number(float_str($x));
    }
    $s = trim((string)$x);
    if (preg_match('/^([+-]?)(\d*)\.?(\d*)[eE]([+-]?\d+)$/', $s, $m)) {
        return new Number(sci_to_plain($s));
    }
    if ($s !== '' && $s[0] === '+') {
        $s = substr($s, 1);
    }
    if ($s !== '' && $s[0] === '.') {
        $s = '0' . $s;
    }
    if (str_starts_with($s, '-.')) {
        $s = '-0' . substr($s, 1);
    }
    return new Number($s);
}

/** null은 null로 두는 변환. */
function Dn($x): ?Number
{
    return ($x === null || $x === '') ? null : D($x);
}

function float_str(float $f): string
{
    $s = (string)$f;
    if (stripos($s, 'e') !== false) {
        return sci_to_plain($s);
    }
    return $s;
}

function sci_to_plain(string $s): string
{
    [$mant, $exp] = preg_split('/[eE]/', $s);
    $exp = (int)$exp;
    $neg = str_starts_with($mant, '-');
    $mant = ltrim($mant, '+-');
    [$ip, $fp] = array_pad(explode('.', $mant), 2, '');
    $digits = $ip . $fp;
    $point = strlen($ip) + $exp;
    if ($point <= 0) {
        $r = '0.' . str_repeat('0', -$point) . $digits;
    } elseif ($point >= strlen($digits)) {
        $r = $digits . str_repeat('0', $point - strlen($digits));
    } else {
        $r = substr($digits, 0, $point) . '.' . substr($digits, $point);
    }
    $r = ltrim($r, '0');
    if ($r === '' || $r[0] === '.') {
        $r = '0' . $r;
    }
    return ($neg ? '-' : '') . $r;
}

function scale_of(string $v): int
{
    $p = strpos($v, '.');
    return $p === false ? 0 : strlen($v) - $p - 1;
}

/** 유효숫자 PREC자리 초과분을 ROUND_HALF_EVEN으로 반올림(파이썬 Decimal 문맥과 같게). */
function ctx_round(Number $x): Number
{
    $v = $x->value;
    $neg = str_starts_with($v, '-');
    $a = ltrim($v, '-');
    [$ip, $fp] = array_pad(explode('.', $a), 2, '');
    $ipn = ltrim($ip, '0');
    if ($ipn !== '') {
        $sig = strlen($ipn) + strlen($fp);
        $keep = PREC - strlen($ipn);
    } else {
        $fpn = ltrim($fp, '0');
        if ($fpn === '') {
            return $x;
        }
        $lead = strlen($fp) - strlen($fpn);
        $sig = strlen($fpn);
        $keep = PREC + $lead;
    }
    if ($sig <= PREC || $keep < 0) {
        return $x;
    }
    $r = $x->round($keep, RoundingMode::HalfEven);
    return new Number(bcadd($r->value, '0', $keep));
}

function add($a, $b): Number
{
    return ctx_round(D($a)->add(D($b)));
}

function sub($a, $b): Number
{
    return ctx_round(D($a)->sub(D($b)));
}

function mul($a, $b): Number
{
    return ctx_round(D($a)->mul(D($b)));
}

function neg($a): Number
{
    $a = D($a);
    return new Number(bcsub('0', $a->value, $a->scale));
}

/** 나눗셈: 나누어떨어지면 이상 지수(피제수 자릿수 − 제수 자릿수)까지 0을 줄이고, 아니면 유효숫자 28자리. */
function div($a, $b): Number
{
    $a = D($a);
    $b = D($b);
    if (bccomp($b->value, '0', WORK) === 0) {
        throw new \DivisionByZeroError('Decimal division by zero');
    }
    $q = bcdiv($a->value, $b->value, WORK);
    $exact = bccomp(bcmul($q, $b->value, WORK + $b->scale), $a->value, WORK + $b->scale) === 0;
    if ($exact) {
        $ideal = max(0, $a->scale - $b->scale);
        $q = strip_zeros($q, $ideal);
        return ctx_round(new Number($q));
    }
    return ctx_round(new Number($q));
}

function strip_zeros(string $v, int $minScale = 0): string
{
    if (!str_contains($v, '.')) {
        return $v;
    }
    [$ip, $fp] = explode('.', $v);
    $fp = rtrim($fp, '0');
    if (strlen($fp) < $minScale) {
        $fp = str_pad($fp, $minScale, '0');
    }
    $r = $fp === '' ? $ip : $ip . '.' . $fp;
    if ($r === '-0' || preg_match('/^-0(\.0+)?$/', $r)) {
        $r = ltrim($r, '-');
    }
    return $r;
}

/** 중간값 소수 4자리 보존. 넘는 자리는 버림(SPEC Q-01 잠정). */
function q4($x): Number
{
    return new Number(bcadd(D($x)->value, '0', 4));
}

/** 원 단위 내림 — 음수는 절대값 내림 후 부호 복원(V2 §13.1 L569). */
function floor_won($x): Number
{
    return new Number(bcadd(D($x)->value, '0', 0));
}

/** 소수 자리 반올림(ROUND_HALF_EVEN, 파이썬 quantize 기본). */
function quantize_half_even($x, int $places): Number
{
    $r = D($x)->round($places, RoundingMode::HalfEven);
    return new Number(bcadd($r->value, '0', $places));
}

/** 백분율 수치(50 = 50%) → 비율. */
function pct($x): Number
{
    return div(D($x), 100);
}

function dabs($x): Number
{
    $x = D($x);
    return $x < 0 ? neg($x) : $x;
}

/** 파이썬 sum(): 0에서 시작. */
function dsum(iterable $xs, $start = null): Number
{
    $t = $start === null ? new Number(0) : D($start);
    foreach ($xs as $x) {
        $t = add($t, $x);
    }
    return $t;
}

/** 파이썬 min(a, b): 같으면 앞의 값. */
function dmin($a, $b)
{
    return pycmp($b, $a) < 0 ? $b : $a;
}

/** 파이썬 max(a, b): 같으면 앞의 값. */
function dmax($a, $b)
{
    return pycmp($b, $a) > 0 ? $b : $a;
}

function is_zero($x): bool
{
    return bccomp(D($x)->value, '0', WORK) === 0;
}

/** 13.2 총액 역산. weights는 이미 13.3 정렬된 [가중치]. 반환: [배분액]. */
function alloc_last_remainder($total, array $weights): array
{
    $total = D($total);
    if (!$weights) {
        return [];
    }
    $den = dsum($weights);
    $out = [];
    $n = count($weights);
    for ($i = 0; $i < $n - 1; $i++) {
        $out[] = !is_zero($den) ? floor_won(div(mul($total, $weights[$i]), $den)) : new Number(0);
    }
    $out[] = sub($total, dsum($out));
    return $out;
}

/** Number → JSON 값. 정수면 int, 소수면 문자열(정밀도 보존). 연관 배열 · 목록은 재귀. */
function to_json($x)
{
    if ($x instanceof Number) {
        $v = $x->value;
        if (bccomp($v, bcadd($v, '0', 0), WORK) === 0) {
            $i = bcadd($v, '0', 0);
            return (strlen(ltrim($i, '-')) < 19) ? (int)$i : $i;
        }
        return strip_zeros($v);
    }
    if ($x instanceof Obj) {
        return $x->toJson();
    }
    if (is_array($x)) {
        $o = [];
        foreach ($x as $k => $v) {
            $o[$k] = to_json($v);
        }
        return $o;
    }
    return $x;
}

/** 빈 dict도 JSON 객체({})로 내보내기 위한 표식. */
final class Obj
{
    public function __construct(public array $a = [])
    {
    }

    public function toJson()
    {
        $o = to_json($this->a);
        return $o === [] ? new \stdClass() : $o;
    }
}

// ------------------------------------------------------------------ 파이썬 동작 맞춤

/** 파이썬 진릿값. */
function truthy($v): bool
{
    if ($v instanceof Number) {
        return !is_zero($v);
    }
    if (is_array($v)) {
        return count($v) > 0;
    }
    if (is_string($v)) {
        return $v !== '';
    }
    return (bool)$v;
}

/** 파이썬 `a or b`. */
function either($a, $b)
{
    return truthy($a) ? $a : $b;
}

/** 파이썬 str(). */
function pystr($v): string
{
    if ($v === null) {
        return 'None';
    }
    if ($v === true) {
        return 'True';
    }
    if ($v === false) {
        return 'False';
    }
    if ($v instanceof Number) {
        return $v->value;
    }
    if (is_float($v)) {
        $s = float_str($v);
        return str_contains($s, '.') ? $s : $s . '.0';
    }
    return (string)$v;
}

/** 파이썬 dict.get(k, default): 키가 있으면 값이 null이어도 그 값. */
function g($arr, string $k, $default = null)
{
    if (is_array($arr) && array_key_exists($k, $arr)) {
        return $arr[$k];
    }
    return $default;
}

/** 파이썬 비교(정렬 키 튜플 포함). */
function pycmp($a, $b): int
{
    if (is_array($a) && is_array($b)) {
        $n = min(count($a), count($b));
        $a = array_values($a);
        $b = array_values($b);
        for ($i = 0; $i < $n; $i++) {
            $c = pycmp($a[$i], $b[$i]);
            if ($c !== 0) {
                return $c;
            }
        }
        return count($a) <=> count($b);
    }
    $na = $a instanceof Number || is_int($a) || is_float($a) || is_bool($a);
    $nb = $b instanceof Number || is_int($b) || is_float($b) || is_bool($b);
    if ($na && $nb) {
        return bccomp(D($a)->value, D($b)->value, WORK);
    }
    if ($a === null && $b === null) {
        return 0;
    }
    return strcmp((string)$a, (string)$b) <=> 0;
}

/** 안정 정렬(파이썬 sorted(key=...)). */
function sort_by(array $xs, callable $key, bool $reverse = false): array
{
    $xs = array_values($xs);
    $keys = array_map($key, $xs);
    $idx = array_keys($xs);
    usort($idx, function ($i, $j) use ($keys, $reverse) {
        $c = pycmp($keys[$i], $keys[$j]);
        return $reverse ? -$c : $c;
    });
    return array_map(fn($i) => $xs[$i], $idx);
}

/** 파이썬 max(xs, key=...): 최댓값 중 첫 항목. */
function max_by(array $xs, callable $key)
{
    $best = null;
    $bk = null;
    foreach ($xs as $x) {
        $k = $key($x);
        if ($best === null || pycmp($k, $bk) > 0) {
            $best = $x;
            $bk = $k;
        }
    }
    return $best;
}

/** 파이썬 min(xs, key=...): 최솟값 중 첫 항목. */
function min_by(array $xs, callable $key)
{
    $best = null;
    $bk = null;
    foreach ($xs as $x) {
        $k = $key($x);
        if ($best === null || pycmp($k, $bk) < 0) {
            $best = $x;
            $bk = $k;
        }
    }
    return $best;
}

/** 파이썬 str 슬라이스 str(x)[:n]. */
function head(string $s, int $n): string
{
    return mb_substr($s, 0, $n);
}

/** 이동 키(파이썬 튜플 키 dict 대신). */
function tkey(...$parts): string
{
    return json_encode(array_map(fn($p) => $p instanceof Number ? $p->value : $p, $parts), JSON_UNESCAPED_UNICODE);
}

function untkey(string $k): array
{
    return json_decode($k, true);
}
