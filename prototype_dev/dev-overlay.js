/* prototype_dev 전용 — 개발 이름 보기
 * 화면 디자인은 prototype_clean 그대로 두고, 개발 코드 기준 이름(라우트 · 권한 · 필드 name · id)을 겹쳐 보여 준다.
 * - 오른쪽 아래 [개발 매핑] 버튼으로 켜고 끈다(켜짐 상태는 이 브라우저에만 저장).
 * - 켜면: data-dev-flag="dev-only"(개발에만 있음, 초록) · "proto-only"(프로토타입에만 있음 = 백엔드 필요, 주황) 요소에 테두리,
 *         요소에 마우스를 올리면 name · id · data-dev-route · data-dev-method · data-dev-url · data-dev-perm 을 띄운다.
 * - 화면 요약(메뉴 · 기준 커밋 · 명세 문서)은 <script type="application/json" id="dev-map"> 에서 읽는다.
 */
(function () {
  var KEY = 'sjm_dev_overlay';
  function read() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function save(v) { try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) { /* 저장 불가여도 동작 */ } }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var map = {};
  try { map = JSON.parse((document.getElementById('dev-map') || {}).textContent || '{}'); } catch (e) { map = {}; }

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'devx-toggle';
  var panel = document.createElement('div');
  panel.className = 'devx-panel';
  var tip = document.createElement('div');
  tip.className = 'devx-tip';

  function renderPanel() {
    var menus = (map.menus || []).map(function (m) { return '<li><code>' + esc(m.route) + '</code> ' + esc(m.label) + '</li>'; }).join('');
    var nDev = document.querySelectorAll('[data-dev-flag="dev-only"]').length;
    var nProto = document.querySelectorAll('[data-dev-flag="proto-only"]').length;
    var nRoute = document.querySelectorAll('[data-dev-route]').length;
    var nName = document.querySelectorAll('[data-dev-name], input[name], select[name], textarea[name]').length;
    panel.innerHTML =
      '<div class="devx-h">개발 매핑 · ' + esc(map.code || '') + '</div>' +
      '<div class="devx-row">기준 개발 커밋 <code>' + esc(map.devCommit || '?') + '</code></div>' +
      '<div class="devx-row">진행: ' + esc(map.progress || '') + '</div>' +
      (menus ? '<div class="devx-row">메뉴 권한 단위<ul>' + menus + '</ul></div>' : '') +
      '<div class="devx-row"><span class="devx-key devx-key-dev"></span>개발에만 있음 ' + nDev + ' · <span class="devx-key devx-key-proto"></span>프로토타입에만 있음(백엔드 필요) ' + nProto + '</div>' +
      '<div class="devx-row">라우트 연결 ' + nRoute + ' · 필드 name ' + nName + '</div>' +
      '<div class="devx-row devx-sub">요소에 마우스를 올리면 개발 이름이 보입니다. 명세: dev_spec/' + esc(map.code || '') + '.md</div>';
  }

  function set(on) {
    document.documentElement.classList.toggle('devx-on', on);
    btn.textContent = on ? '개발 매핑 끄기' : '개발 매핑';
    panel.style.display = on ? 'block' : 'none';
    if (on) renderPanel();
    if (!on) tip.style.display = 'none';
    save(on);
  }

  function describe(el) {
    var rows = [];
    var tag = el.tagName.toLowerCase();
    if (el.getAttribute('data-dev-flag') === 'dev-only') rows.push('<b class="devx-c-dev">개발에만 있음</b>');
    if (el.getAttribute('data-dev-flag') === 'proto-only') rows.push('<b class="devx-c-proto">프로토타입에만 있음 · 개발 미구현</b>');
    var nm = el.getAttribute('name') || el.getAttribute('data-dev-name');
    if (nm) rows.push('name <code>' + esc(nm) + '</code>' + (el.value && (tag === 'option' || el.type === 'radio' || el.type === 'checkbox') ? ' = <code>' + esc(el.value) + '</code>' : ''));
    var dv = el.getAttribute('data-dev-value');
    if (dv) rows.push('개발 값 ' + esc(dv));
    if (el.id) rows.push('id <code>' + esc(el.id) + '</code>');
    var r = el.getAttribute('data-dev-route');
    if (r) rows.push('route <code>' + esc(r) + '</code>');
    var mu = (el.getAttribute('data-dev-method') || '') + ' ' + (el.getAttribute('data-dev-url') || '');
    if (mu.trim()) rows.push('<code>' + esc(mu.trim()) + '</code>');
    var p = el.getAttribute('data-dev-perm');
    if (p) rows.push('권한 <code>' + esc(p) + '</code>');
    var n = el.getAttribute('data-dev-note');
    if (n) rows.push(esc(n));
    return rows.join('<br>');
  }

  document.addEventListener('mouseover', function (e) {
    if (!document.documentElement.classList.contains('devx-on')) return;
    var el = e.target.closest('[data-dev-route],[data-dev-flag],[data-dev-name],[data-dev-note],input[name],select[name],textarea[name],form[id]');
    if (!el || panel.contains(el) || el === btn) { tip.style.display = 'none'; return; }
    var html = describe(el);
    if (!html) { tip.style.display = 'none'; return; }
    tip.innerHTML = html;
    var b = el.getBoundingClientRect();
    tip.style.display = 'block';
    tip.style.left = Math.min(window.innerWidth - tip.offsetWidth - 8, Math.max(8, b.left)) + 'px';
    tip.style.top = (b.bottom + 6 + tip.offsetHeight > window.innerHeight ? b.top - tip.offsetHeight - 6 : b.bottom + 6) + 'px';
  });

  btn.addEventListener('click', function () { set(!document.documentElement.classList.contains('devx-on')); });

  function mount() {
    document.body.appendChild(btn);
    document.body.appendChild(panel);
    document.body.appendChild(tip);
    set(read());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
