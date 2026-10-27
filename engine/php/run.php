<?php
/**
 * 정산엔진 기준 계산기 PHP판 실행.
 *
 *   php engine/php/run.php 입력.json [출력.json]
 *
 * 출력을 생략하면 요약 한 줄만 찍는다. 이월 연속성 불일치 · 오류가 있으면 종료 코드 1.
 */

require __DIR__ . '/engine.php';

$argv = $_SERVER['argv'];
if (count($argv) < 2) {
    fwrite(STDERR, "사용법: php run.php 입력.json [출력.json]\n");
    exit(2);
}
$data = json_decode(file_get_contents($argv[1]), true, 512, JSON_BIGINT_AS_STRING | JSON_THROW_ON_ERROR);
$result = SettleCalc\Engine::run($data);
if (isset($argv[2])) {
    file_put_contents($argv[2], json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_PRESERVE_ZERO_FRACTION));
}
$bad = count(array_filter($result['continuity'], fn($c) => !$c['ok']));
$prov = count(array_filter($result['trace'], fn($e) => $e['provisional']));
printf("정산월 %s · 상태 %s · 값 %d건 · trace %d줄(잠정 %d) · 이월 연속성 불일치 %d건 · 확인 필요 %d건 · 오류 %d건\n",
    $result['settlement_month'], $result['status'], count($result['values']), count($result['trace']), $prov, $bad,
    count($result['issues']), count($result['errors']));
foreach ($result['errors'] as $e) {
    printf("  오류 %s: %s\n", $e['code'], $e['message']);
}
exit(($bad || $result['errors']) ? 1 : 0);
