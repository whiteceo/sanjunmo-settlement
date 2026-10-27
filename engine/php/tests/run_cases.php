<?php
/** parity.py가 부른다: argv[1] 폴더의 <이름>.in.json을 PHP판으로 계산해 <이름>.php.json으로 쓴다. */
require __DIR__ . '/../engine.php';
$dir = $_SERVER['argv'][1];
foreach (glob("$dir/*.in.json") as $f) {
    $name = basename($f, '.in.json');
    try {
        $data = json_decode(file_get_contents($f), true, 512, JSON_BIGINT_AS_STRING | JSON_THROW_ON_ERROR);
        file_put_contents("$dir/$name.php.json", json_encode(SettleCalc\Engine::run($data), JSON_UNESCAPED_UNICODE | JSON_PRESERVE_ZERO_FRACTION));
    } catch (Throwable $e) {
        echo "ERR $name: ", get_class($e), ': ', $e->getMessage(), ' @', basename($e->getFile()), ':', $e->getLine(), "\n";
    }
}
