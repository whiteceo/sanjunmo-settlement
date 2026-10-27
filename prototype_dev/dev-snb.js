/* prototype_dev 전용 — SNB 동작을 개발 기준으로 맞춘다(white 2026-10-27: SNB는 디자인만 프로토타입, 접기 · 펼치기 같은 동작은 개발 유지).
 * 개발 근거: lcampus/sanjunmo public/admin/assets/js/custom.js "관리자메뉴(좌측)"
 *   - 1Depth(그룹 제목)를 누르면 그 그룹의 2Depth 목록을 펼치고, 다른 그룹은 접는다(아코디언 — 한 번에 하나만 열림).
 *   - 열린 그룹을 다시 누르면 접는다.
 *   - 처음 열 때는 현재 화면이 든 그룹(active)만 펼친다.
 *   - 펼치고 접을 때 높이 0.2초 애니메이션(slideDown · slideUp).
 * 디자인(색 · 글꼴 · 간격 · 그룹 구성)은 prototype_clean의 common-snb.js · common-v84.css 그대로이고,
 * 여기서는 접힘 표시용 화살표와 커서만 더한다. common-snb.js가 SNB를 그린 뒤에 붙는다.
 */
(function () {
  var DUR = 200;
  var css = '' +
    '#v4-master-snb .snb-group-title{cursor:pointer;position:relative;padding-right:22px;user-select:none;}' +
    '#v4-master-snb .snb-group-title::after{content:"";position:absolute;right:8px;top:50%;width:6px;height:6px;margin-top:-4px;' +
    'border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg);opacity:.6;transition:transform .2s ease;}' +
    '#v4-master-snb .snb-group.devsnb-closed .snb-group-title::after{transform:rotate(-45deg);margin-top:-3px;}' +
    '#v4-master-snb .snb-group.devsnb-closed .snb-item-list{display:none !important;}';

  // 공통 CSS가 목록에 display:flex !important를 걸어 두므로 접힘은 클래스(devsnb-closed)로 표시하고, 높이만 애니메이션한다
  function animate(list, from, to, done) {
    list.style.overflow = 'hidden';
    list.style.height = from + 'px';
    list.style.transition = 'height ' + DUR / 1000 + 's ease';
    requestAnimationFrame(function () { requestAnimationFrame(function () { list.style.height = to + 'px'; }); });
    setTimeout(function () { list.style.height = ''; list.style.overflow = ''; list.style.transition = ''; if (done) done(); }, DUR + 30);
  }

  function open(g) {
    var list = g.querySelector('.snb-item-list');
    g.classList.remove('devsnb-closed');
    if (list) animate(list, 0, list.scrollHeight);
  }

  function close(g) {
    var list = g.querySelector('.snb-item-list');
    if (g.classList.contains('devsnb-closed')) return;
    if (!list) { g.classList.add('devsnb-closed'); return; }
    animate(list, list.scrollHeight, 0, function () { g.classList.add('devsnb-closed'); });
    g.classList.add('devsnb-closing');
    setTimeout(function () { g.classList.remove('devsnb-closing'); }, DUR + 30);
  }

  function setup(snb) {
    var groups = snb.querySelectorAll('.snb-group');
    if (!groups.length || groups[0].__devSnb) return;
    if (!document.getElementById('devsnb-style')) {
      var style = document.createElement('style');
      style.id = 'devsnb-style';
      style.textContent = css;
      document.head.appendChild(style);
    }
    var anyActive = false;
    groups.forEach(function (g) {
      g.__devSnb = true;
      var isOpen = !!g.querySelector('.snb-item.active');
      anyActive = anyActive || isOpen;
      g.classList.toggle('devsnb-closed', !isOpen);
    });
    // 현재 화면이 SNB에 없으면(안내 화면 등) 첫 그룹만 펼쳐 둔다
    if (!anyActive) groups[0].classList.remove('devsnb-closed');
    groups.forEach(function (g) {
      var title = g.querySelector('.snb-group-title');
      if (!title) return;
      title.addEventListener('click', function () {
        var wasOpen = !g.classList.contains('devsnb-closed');
        groups.forEach(function (o) { if (o !== g || wasOpen) close(o); });
        if (!wasOpen) open(g);
      });
    });
  }

  function tryStart() {
    var snb = document.getElementById('v4-master-snb');
    if (snb && snb.querySelector('.snb-group')) { setup(snb); return true; }
    return false;
  }

  function start() {
    tryStart();
    // common-snb.js가 나중에 그리면 그때 붙인다
    var mo = new MutationObserver(function () { tryStart(); });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
