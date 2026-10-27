// php-wasm(node)으로 PHP 스크립트 실행: node phprun.mjs <D:/Work 아래 php 파일> [인수...]
// D:/Work를 /work로 붙이고 인수는 $_SERVER['argv']로 넘긴다. @php-wasm/node는 PHPWASM_DIR(기본 현재 폴더)의 node_modules에서 읽는다.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const req = createRequire(pathToFileURL((process.env.PHPWASM_DIR || process.cwd()) + '/x.js'));
const { loadNodeRuntime, createNodeFsMountHandler } = await import(pathToFileURL(req.resolve('@php-wasm/node')));
const { PHP } = await import(pathToFileURL(req.resolve('@php-wasm/universal')));
const php = new PHP(await loadNodeRuntime('8.4', { emscriptenOptions: { processId: 1 } }));
php.mkdir('/work');
await php.mount('/work', createNodeFsMountHandler('D:/Work'));
const toVfs = p => p.split(String.fromCharCode(92)).join('/').replace(/^(\/d|D:)\/Work/i, '/work');
const [script, ...args] = process.argv.slice(2);
php.writeFile('/tmp/argv.json', JSON.stringify([toVfs(script), ...args.map(toVfs)]));
let code = 0;
try {
  const r = await php.run({ code: `<?php $_SERVER['argv'] = json_decode(file_get_contents('/tmp/argv.json'), true); $argv = $_SERVER['argv']; require $argv[0];` });
  process.stdout.write(r.text);
  if (r.errors) process.stderr.write(r.errors);
  code = r.exitCode || 0;
} catch (e) {
  process.stdout.write(e.response?.text ?? '');
  process.stderr.write(String(e.message).slice(0, 4000) + '\n');
  code = 1;
}
process.exit(code);
