<?php
/**
 * 정산엔진 기준 계산기 PHP판 — 불러오기(프레임워크 · composer 없이 require 한 줄로 쓴다).
 *
 *   require __DIR__ . '/engine.php';
 *   $out = SettleCalc\Engine::run($input);   // $input = json_decode(입력 JSON, true)
 *
 * 파이썬 판(engine/core)과 같은 입력 · 출력 스키마(engine/schema)를 쓴다. PHP 8.4 이상 · bcmath 확장 필요.
 */

require_once __DIR__ . '/src/helpers.php';
require_once __DIR__ . '/src/Engine.php';
require_once __DIR__ . '/src/Tax.php';
require_once __DIR__ . '/src/steps/S00PipelineIn.php';
require_once __DIR__ . '/src/steps/S01to03.php';
require_once __DIR__ . '/src/steps/S04Deduct.php';
require_once __DIR__ . '/src/steps/S05to07.php';
require_once __DIR__ . '/src/steps/S08PayeeSplit.php';
require_once __DIR__ . '/src/steps/S09Tax.php';
require_once __DIR__ . '/src/steps/S10to13.php';
