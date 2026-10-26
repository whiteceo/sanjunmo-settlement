#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Skill 7] 모달 열림 전수 검사기 (읽기 전용 QA 도구 — HTML을 수정하지 않음, Playwright 렌더링 기준)

배경
  각 화면의 UNIVERSAL-MODAL-CLOSER-HOTFIX는 모달 백드롭에 인라인 display:none !important를 건다.
  화면 코드가 클래스(open · show · active)만 붙이거나 hidden만 떼서 열면 모달이 안 열리던 결함이 있었고,
  v6.75에서 common-snb.js 끝의 MODAL-OPEN-GUARD로 근본 수정했다. 이 도구는 그 회귀를 전수로 잡는다.

검사 (화면마다 새 브라우저 컨텍스트, 클릭마다 페이지 새로 로드)
  (a) 트리거 클릭  onclick에 open/Open/Modal/modal/show/Show가 있고 close/Close가 없는 요소,
                  data-target · data-bs-target · data-modal · data-open, id에 open/Modal이 든 버튼 · 링크.
                  같은 함수 · 같은 인자 모양(숫자가 든 문자열 인자는 무시)은 한 번만 누른다.
                  화면에 보이는 것만 실제 클릭으로 누른다. 탭 · 하위 페이지 · 모달을 한 단계 열어
                  새로 보이게 된 트리거도 누른다(최대 2단계). 끝까지 숨은 트리거는 '숨김(미검사)'.
                  판정  열림 = 새로 보이는 백드롭(또는 role=dialog · *modal* · *drawer* 레이어)
                        페이지 전환 = SJM_PAGE.current()가 바뀌고 그 패널이 보임 → 성공
                        제외 = 알림(alert · confirm) · 토스트 · 다른 파일로 이동 · 새 창 · 화면 내 변화(탭 등)
                        안 열림 = 대상 백드롭이 있는데 안 보임, 또는 아무 변화 없음
                        (이름에 open이 없는 저장 · 승인 버튼이 조건에 따라서만 여는 경우, 여는 구문까지 안 갔으면 제외)
  (b) 백드롭별 직접 열기  화면의 백드롭마다, 그 id를 문자열로 담거나(onclick · data-target)
                  onclick 함수 본문(Function.toString)에 그 id가 든 트리거를 찾아 onclick 코드를
                  직접 호출한다(문서 click 위임 = HOTFIX의 열기 해제를 거치지 않음 → 가드만으로 열리는지).
                  트리거 찾기: id 문자열 + 여는 구문(classList.add('open') 등)이 같은 함수에 있거나, 공통 도우미
                  (openModalById('id') 등)에 id를 넘기면 연다고 본다. 부르는 함수는 2단계까지 따라간다.
                  트리거가 없으면 전역 함수 중 그 id를 여는 것을 인자가 없을 때만 호출.
                  판정  열림 / 안 열림(여는 구문은 실행됐는데 안 보임 = 결함) / 미실행(인자 · 조건 때문에 여는 구문까지 안 감)
  (c) 열림 클래스 부여  새로 로드 → 백드롭에 open → show → active를 차례로 붙여(hidden이 있으면 뗌) 한 틱 뒤 보이는지.
                  (a)(b)에서 조건 때문에 판정 못 한 모달도 "여는 구문에 도달하면 열리는지"를 확인한다.
                  (a)(b)로 안 열렸고 (c)로도 안 보이면 조치 대상.

사용법:
  python scripts/qa/skill_modal_open_check.py                       # 양쪽(prototype, prototype_clean)
  python scripts/qa/skill_modal_open_check.py prototype_clean       # 한쪽만
  python scripts/qa/skill_modal_open_check.py prototype_clean --only SETT-002,PROD-003
  python scripts/qa/skill_modal_open_check.py --jobs 8              # 동시에 띄울 브라우저 수(기본 6, 1이면 순차) — 양쪽 약 4분
  python scripts/qa/skill_modal_open_check.py --strict              # 안 열림 · (b) 실패 · 어떤 방법으로도 안 보임 · JS 에러가 있으면 exit 1
리포트: scripts/qa/reports/MODAL_OPEN_CHECK_REPORT.md
"""
import argparse
import datetime
import os
import re
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "scripts" / "qa" / "reports" / "MODAL_OPEN_CHECK_REPORT.md"
FOLDERS = ["prototype", "prototype_clean"]
MAX_TESTS = 160      # 화면당 (a) 클릭 상한
MAX_DEPTH = 2        # 탭 · 페이지 · 모달을 몇 단계까지 열어 숨은 트리거를 찾을지
WAIT_LOAD = 350
WAIT_CLICK = 300

HELPERS = r"""
window.__mc = (function () {
  var BSEL = '.modal-backdrop, .p1-modal-backdrop, .s1-modal-backdrop, .s2-modal-backdrop';
  var LSEL = '[role="dialog"], dialog, [class*="modal"], [class*="drawer"], [class*="popup"], [class*="overlay"], [class*="sheet"]';
  var TABSEL = '.subview-tab, .subview-btn, .tab-btn, [role="tab"], [data-tab]';
  var KW = /open|Open|[Mm]odal|show|Show/;
  var CL = /close|Close|classList\.remove\(\s*['"`](open|show|active)['"`]|classList\.add\(\s*['"`]hidden['"`]/;
  var OPENPAT = /classList\.add\(\s*['"`](open|show|active)['"`]|classList\.remove\(\s*['"`]hidden['"`]|\.style\.display\s*=\s*['"`](flex|block|grid)['"`]|removeProperty\(\s*['"`]display['"`]|classList\.toggle\(/;
  function srcOf(fn) {
    if (!fn || fn.indexOf('.') !== -1) return '';
    var f; try { f = window[fn]; } catch (e) { return ''; }
    if (typeof f !== 'function') return '';
    try { var s = Function.prototype.toString.call(f); return s.indexOf('[native code]') !== -1 ? '' : s; } catch (e) { return ''; }
  }
  function bids() { return Array.prototype.map.call(document.querySelectorAll(BSEL), function (b) { return b.id; }).filter(Boolean); }
  function hasLit(code, id) { return code.indexOf("'" + id + "'") !== -1 || code.indexOf('"' + id + '"') !== -1 || code.indexOf('`' + id + '`') !== -1; }
  // 코드(onclick 또는 함수 본문)가 여는 백드롭 id — id 문자열 + 여는 구문(classList.add('open') 등)이 같은 함수에 있으면 연다고 본다.
  // 호출하는 open · show 계열 함수는 depth 단계까지 따라간다.
  function calls(code) {
    var re = /([A-Za-z_$][\w$]*)\s*\(/g, m, out = [];
    while ((m = re.exec(code || ''))) if (!IGN[m[1]] && out.indexOf(m[1]) === -1) out.push(m[1]);
    return out;
  }
  // 부르는 함수를 이름과 상관없이 depth 단계까지 따라간다(approveX → openXModal, triggerDemo → save → 모달 같은 경우).
  // 저장 · 승인처럼 조건에 따라서만 여는 버튼은 (a)에서 '조건부 열기'로 제외한다.
  function opensIds(code, depth, seen, top) {
    seen = seen || {};
    var out = [];
    if (!code) return out;
    var cs = calls(code);
    // 공통 열기 도우미(openModalById('modal-x') 등): id 문자열 + 그 id를 받는 open · show 함수의 본문에 여는 구문
    var helper = cs.some(function (n) { var s = srcOf(n); return /open|show/i.test(n) && !/close/i.test(n) && (!s || OPENPAT.test(s)); });  // 지역 함수(IIFE 안 openModalEl 등)는 본문을 못 읽으므로 이름으로 본다
    if (OPENPAT.test(code) || helper) bids().forEach(function (id) { if (hasLit(code, id)) out.push(id); });
    if (depth > 0) {
      cs.forEach(function (n) {
        if (seen[n] || /close|Close/.test(n)) return;
        seen[n] = 1;
        opensIds(srcOf(n), depth - 1, seen, false).forEach(function (id) { if (out.indexOf(id) === -1) out.push(id); });
      });
    }
    return out;
  }
  var IGN = { 'if': 1, 'event.stopPropagation': 1, 'event.preventDefault': 1, 'return': 1, 'function': 1 };
  function vis(el) {
    if (!el || !el.isConnected) return false;
    if (el.checkVisibility && !el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) return false;
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function txt(el) {
    return ((el.innerText || el.value || el.getAttribute('aria-label') || el.title || '') + '').replace(/\s+/g, ' ').trim().slice(0, 40);
  }
  function fnName(code) {
    var re = /([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\(/g, m, first = null;
    while ((m = re.exec(code || ''))) {
      if (IGN[m[1]]) continue;
      if (!first) first = m[1];
      if (KW.test(m[1])) return m[1];
    }
    return first;
  }
  function normOc(oc) {
    return (oc || '').replace(/(['"`])([^'"`]*)\1/g, function (all, q, s) { return /\d/.test(s) && !document.getElementById(s) ? "''" : all; })
      .replace(/\b\d+\b/g, '#').replace(/\s+/g, ' ').trim().slice(0, 160);
  }
  function dataTarget(el) {
    return el.getAttribute('data-target') || el.getAttribute('data-bs-target') || el.getAttribute('data-modal') ||
      el.getAttribute('data-open') || el.getAttribute('data-modal-target') || '';
  }
  function excluded(el) {
    if (el.matches(BSEL)) return true;
    if (el.closest('[class*="snb"]')) return true;
    return false;
  }
  function keyOf(el, kind) {
    var oc = el.getAttribute('onclick') || '';
    var k = kind + '|' + el.tagName + '|' + normOc(oc) + '|' + dataTarget(el);
    if (!oc) k += '|' + (el.id || '').replace(/\d+/g, '#') + '|' + txt(el).replace(/\d+/g, '#');
    if (kind === 'tab') k += '|' + (el.getAttribute('data-tab') || '') + '|' + txt(el).replace(/\d+/g, '#');
    return k;
  }
  function trigList() {
    var out = [];
    document.querySelectorAll('[onclick], [data-target], [data-bs-target], [data-modal], [data-open], [data-modal-target], button[id], a[id], [role="button"][id]').forEach(function (el) {
      if (excluded(el)) return;
      var oc = el.getAttribute('onclick') || '', dt = dataTarget(el), id = el.id || '', why = '';
      if (oc && KW.test(oc) && !CL.test(oc)) why = 'onclick';
      else if (dt && !CL.test(oc)) why = 'data-target';
      else if (id && /open|Open|Modal/.test(id) && !CL.test(id) && !CL.test(oc) && !el.matches('div, section, form, table, tr, tbody')) why = 'id';
      else if (oc && !CL.test(oc) && opensIds(oc, 2, null, true).length) why = 'body';   // 이름엔 open이 없지만 함수 본문이 모달을 연다(HOTFIX 클릭 위임이 못 잡는 유형)
      if (!why) return;
      el.__mcWhy = why;
      out.push(el);
    });
    return out;
  }
  function tabList() {
    return Array.prototype.filter.call(document.querySelectorAll(TABSEL), function (el) { return !excluded(el) && !el.closest(BSEL); });
  }
  function backdrops() { return Array.prototype.slice.call(document.querySelectorAll(BSEL)); }
  function bkey(el, i) { return el.id ? el.id : ('(id 없음 #' + i + ' .' + (el.className || '').toString().trim().split(/\s+/)[0] + ')'); }
  function targetsOf(el) {
    var oc = el.getAttribute('onclick') || '', dt = dataTarget(el).replace(/^#/, '');
    var own = el.closest(BSEL);
    var out = opensIds(oc, 2, null, true);
    bids().forEach(function (id) { if ((hasLit(oc, id) || dt === id) && out.indexOf(id) === -1 && !CL.test(oc)) out.push(id); });
    return out.filter(function (id) { return !own || own.id !== id; });
  }
  function info(el, kind) {
    var oc = el.getAttribute('onclick') || '';
    return {
      key: keyOf(el, kind), kind: kind, tag: el.tagName.toLowerCase(), id: el.id || '', text: txt(el), onclick: oc.replace(/\s+/g, ' ').trim().slice(0, 140),
      fn: fnName(oc), dt: dataTarget(el), why: el.__mcWhy || '', vis: vis(el), disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true',
      inModal: !!el.closest(BSEL), targets: kind === 'trigger' ? targetsOf(el) : []
    };
  }
  function lpath(el) { return el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.className || '').toString().trim().split(/\s+/).join('.'); }
  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) | 0; } return h + ':' + s.length; }
  function activePanelVisible() {
    var p = document.querySelector('#v4-page-body > .subview-panel[data-subpage].active');
    return !!p && vis(p);
  }
  return {
    vis: vis,
    list: function () {
      var seen = {}, out = [];
      trigList().forEach(function (el) { var i = info(el, 'trigger'); out.push(i); });
      tabList().forEach(function (el) { out.push(info(el, 'tab')); });
      return out;
    },
    find: function (key, visibleOnly) {
      var kind = key.split('|')[0];
      var els = kind === 'tab' ? tabList() : trigList();
      for (var i = 0; i < els.length; i++) {
        if (keyOf(els[i], kind) === key && (!visibleOnly || vis(els[i]))) return els[i];
      }
      return null;
    },
    snap: function () {
      return {
        bd: backdrops().filter(vis).map(function (b) { return bkey(b, backdrops().indexOf(b)); }),
        layers: Array.prototype.filter.call(document.querySelectorAll(LSEL), function (el) {
          return !el.matches(BSEL) && !el.closest(BSEL) && !el.closest('[class*="snb"]') && vis(el);
        }).map(lpath).slice(0, 30),
        page: (window.SJM_PAGE && typeof SJM_PAGE.current === 'function') ? SJM_PAGE.current() : null,
        pageVisible: activePanelVisible(),
        path: location.pathname,
        text: hash(document.body ? document.body.innerText : ''),
        toast: Array.prototype.filter.call(document.querySelectorAll('[class*="toast"], [id*="toast"], [class*="snackbar"]'), vis)
          .map(function (e) { return (e.innerText || '').trim().slice(0, 50); }).filter(Boolean).join(' | ')
      };
    },
    backdropList: function () {
      return backdrops().map(function (b, i) { return { key: bkey(b, i), id: b.id || '', cls: (b.className || '').toString() }; });
    },
    diag: function (key) {
      var b = key.charAt(0) === '(' ? null : document.getElementById(key);
      if (!b) return { found: false };
      var cs = getComputedStyle(b), hid = null, p = b.parentElement;
      while (p && p !== document.body) { if (getComputedStyle(p).display === 'none') { hid = lpath(p); break; } p = p.parentElement; }
      return {
        found: true, cls: (b.className || '').toString(), inline: b.style.display ? (b.style.display + (b.style.getPropertyPriority('display') ? ' !' + b.style.getPropertyPriority('display') : '')) : '',
        computed: cs.display, visibility: cs.visibility, opacity: cs.opacity, hiddenAncestor: hid, vis: vis(b)
      };
    },
    openers: function (key) {
      // (b) 이 백드롭을 여는 트리거 — 문자열 id 또는 함수 본문에 id
      var out = [], seenFn = {};
      trigList().forEach(function (el) {
        if (targetsOf(el).indexOf(key) === -1) return;
        var i = info(el, 'trigger'), sig = (i.fn || '') + '|' + normOc(i.onclick);
        if (seenFn[sig]) return;
        seenFn[sig] = 1; out.push(i);
      });
      return out;
    },
    globalOpeners: function (key) {
      // 트리거가 없을 때: 전역 함수 중 이 백드롭을 여는 것. 인자가 필요한 함수는 호출하지 않고 이름만 돌려준다.
      var out = [];
      Object.keys(window).forEach(function (n) {
        if (n.indexOf('__') === 0) return;
        var s = srcOf(n);
        if (!s || /^close/i.test(n)) return;
        if (opensIds(s, 1).indexOf(key) === -1) return;
        out.push({ name: n, arity: window[n].length });
      });
      return out;
    },
    callOnclick: function (key) {
      var el = this.find(key, false);
      if (!el) return 'NO_ELEMENT';
      var code = el.getAttribute('onclick') || '';
      if (!code) { el.dispatchEvent(new MouseEvent('click', { bubbles: false })); return 'DISPATCH'; }
      var ev = { target: el, currentTarget: el, type: 'click', preventDefault: function () {}, stopPropagation: function () {} };
      try { (new Function('event', code)).call(el, ev); return 'OK'; } catch (e) { return 'ERR: ' + (e && e.message || e); }
    },
    callGlobal: function (n) { try { window[n](); return 'OK'; } catch (e) { return 'ERR: ' + (e && e.message || e); } }
  };
})();
"""


def short(s, n=60):
    s = (s or "").replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


class Screen:
    def __init__(self, browser, path):
        self.path = path
        self.url = path.as_uri()
        self.errors = []
        self.dialogs = []
        self.popups = []
        self.page = None
        self.ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        self.ctx.add_init_script(HELPERS)
        self.page = self.ctx.new_page()
        self.ctx.on("page", self._popup)
        self.page.on("pageerror", lambda e: self.errors.append("pageerror: " + str(e).split("\n")[0][:160]))
        self.page.on("console", lambda m: self.errors.append("console: " + m.text[:160]) if m.type == "error" else None)
        self.page.on("dialog", self._dialog)

    def _popup(self, p):
        if p is not getattr(self, "page", None):
            self.popups.append(p.url)
            try:
                p.close()
            except Exception:
                pass

    def _dialog(self, d):
        self.dialogs.append(f"{d.type}: {d.message[:80]}")
        try:
            d.dismiss()
        except Exception:
            pass

    def load(self):
        self.page.goto(self.url, wait_until="load")
        self.page.wait_for_timeout(WAIT_LOAD)

    def ev(self, js, arg=None):
        return self.page.evaluate(js, arg) if arg is not None else self.page.evaluate(js)

    def click_key(self, key):
        """보이는 첫 요소를 실제 클릭(실패 시 JS click). 없으면 False."""
        h = self.page.evaluate_handle("k => window.__mc.find(k, true)", key)
        el = h.as_element()
        if not el:
            return False
        try:
            el.click(timeout=1500)
        except Exception:
            try:
                el.evaluate("e => e.click()")
            except Exception:
                return False
        self.page.wait_for_timeout(WAIT_CLICK)
        try:
            self.page.wait_for_load_state("load", timeout=3000)
        except Exception:
            pass
        return True

    def replay(self, path):
        self.load()
        for k in path:
            if not self.click_key(k):
                return False
        return True

    def close(self):
        self.ctx.close()


def classify(sc, before, after, info, ne, nd, npop):
    """클릭 전후 비교 → (판정, 상세)"""
    errs = sc.errors[ne:]
    dlg = sc.dialogs[nd:]
    pops = sc.popups[npop:]
    new_bd = [b for b in after["bd"] if b not in before["bd"]]
    new_ly = [l for l in after["layers"] if l not in before["layers"]]
    tg = info["targets"]
    if new_bd:
        if tg and not any(t in new_bd for t in tg):
            return "열림", f"{', '.join(new_bd)} (함수 본문의 다른 백드롭 {', '.join(tg)}은 안 보임)", errs
        note = ", ".join(new_bd)
        if len(new_bd) > 1:
            note += f" — 동시에 {len(new_bd)}개 보임"
        return "열림", note, errs
    if tg:
        if dlg:
            return "제외", "알림: " + dlg[0], errs
        if after["toast"] and after["toast"] != before["toast"]:
            return "제외", "토스트: " + after["toast"][:50], errs
        if after["path"] != before["path"] or pops:
            return "제외", "다른 화면 이동/새 창", errs
        if after["page"] != before["page"] and after["pageVisible"]:
            return "페이지", f"SJM_PAGE {before['page']} → {after['page']} (대상 후보 {', '.join(tg)})", errs
        return "안 열림", "대상 " + ", ".join(tg), errs
    if new_ly:
        return "열림", "레이어 " + ", ".join(new_ly[:3]), errs
    if after["page"] != before["page"]:
        if after["pageVisible"]:
            return "페이지", f"SJM_PAGE {before['page']} → {after['page']}", errs
        return "안 열림", f"SJM_PAGE {before['page']} → {after['page']} 인데 패널이 안 보임", errs
    if after["path"] != before["path"] or pops:
        return "제외", "다른 화면 이동/새 창 " + (pops[0] if pops else after["path"].split("/")[-1]), errs
    if dlg:
        return "제외", "알림: " + dlg[0], errs
    if after["toast"] and after["toast"] != before["toast"]:
        return "제외", "토스트: " + after["toast"][:50], errs
    if after["text"] != before["text"]:
        return "제외", "화면 내 변화(모달 아님)", errs
    if info["inModal"]:
        return "제외", "모달 안 동작 · 변화 없음(검색 · 다시 그리기 등)", errs
    if not re.search(r"open|Open|show|Show", (info["fn"] or "") + " " + (info["dt"] or "") + " " + (info["id"] or "")):
        return "제외", f"변화 없음 · 여는 함수 아님({info['fn']})", errs
    return "안 열림", "클릭 후 변화 없음", errs


def cause_of(sc, info, errs):
    if errs:
        return "JS 에러: " + errs[0]
    if info["disabled"]:
        return "비활성 버튼"
    parts = []
    for t in info["targets"][:3]:
        d = sc.ev("k => window.__mc.diag(k)", t)
        if not d.get("found"):
            continue
        cls = d["cls"]
        opened = any(c in cls.split() for c in ("open", "show", "active"))
        if d["hiddenAncestor"]:
            parts.append(f"{t}: 숨은 부모 {d['hiddenAncestor']} 안")
        elif opened and d["inline"].startswith("none"):
            parts.append(f"{t}: 열림 클래스는 붙었는데 인라인 display:{d['inline']} 남음(가드 미작동)")
        elif "hidden" in cls.split():
            parts.append(f"{t}: hidden 클래스 그대로(여는 코드가 조건에서 멈춤?)")
        elif d["inline"].startswith("none"):
            parts.append(f"{t}: 인라인 display:{d['inline']} · 열림 클래스 없음(여는 코드가 실행 안 됨?)")
        elif opened and d["computed"] == "none":
            parts.append(f"{t}: 열림 클래스({cls})인데 CSS display:none")
        else:
            parts.append(f"{t}: class='{cls}' inline='{d['inline']}' display={d['computed']}")
    return "; ".join(parts) if parts else "변화 없음(대상 불명) — 버튼 동작 확인 필요"


def check_screen(browser, path):
    sc = Screen(browser, path)
    res = {"file": path.name, "tests": [], "hidden": [], "inModalHidden": 0, "backdrops": [], "loadErrors": [], "capped": False}
    try:
        sc.load()
        res["loadErrors"] = list(sc.errors)
        base_list = sc.ev("() => window.__mc.list()")
        bds = sc.ev("() => window.__mc.backdropList()")
        all_trig = {}
        for i in base_list:
            if i["kind"] == "trigger":
                all_trig.setdefault(i["key"], i)
        tested = set()
        used_steps = set()
        queue = [((), base_list)]   # (경로, 그 상태의 목록)
        opened_by = {}               # 백드롭 → 연 트리거 문구
        depth_seen = {}
        while queue:
            pth, lst = queue.pop(0)
            todo = []
            for i in lst:
                if i["kind"] != "trigger" or i["key"] in tested or not i["vis"]:
                    continue
                if any(t["key"] == i["key"] for t in todo):
                    continue
                todo.append(i)
            steps = []
            if len(pth) < MAX_DEPTH:
                for i in lst:
                    if i["kind"] == "tab" and i["vis"] and i["key"] not in used_steps and not any(s["key"] == i["key"] for s in steps):
                        steps.append(i)
            for i in todo:
                if len(res["tests"]) >= MAX_TESTS:
                    res["capped"] = True
                    break
                tested.add(i["key"])
                all_trig.setdefault(i["key"], i)
                if not sc.replay(pth):
                    res["tests"].append({"info": i, "path": pth, "verdict": "미검사", "detail": "경로 재현 실패", "errors": [], "cause": ""})
                    continue
                if i["disabled"]:
                    res["tests"].append({"info": i, "path": pth, "verdict": "제외", "detail": "비활성(disabled)", "errors": [], "cause": ""})
                    continue
                before = sc.ev("() => window.__mc.snap()")
                ne, nd, npop = len(sc.errors), len(sc.dialogs), len(sc.popups)
                ok = sc.click_key(i["key"])
                if not ok:
                    res["tests"].append({"info": i, "path": pth, "verdict": "미검사", "detail": "요소를 다시 찾지 못함", "errors": [], "cause": ""})
                    continue
                try:
                    after = sc.ev("() => window.__mc.snap()")
                except Exception:
                    sc.page.wait_for_timeout(500)
                    after = sc.ev("() => window.__mc.snap()")
                verdict, detail, errs = classify(sc, before, after, i, ne, nd, npop)
                cause = cause_of(sc, i, errs) if verdict == "안 열림" else ""
                if verdict == "안 열림" and i["why"] == "body" and not errs:
                    # 이름에 open이 없는 버튼(저장 · 승인 등)이 조건에 따라서만 모달을 여는 경우 — 여는 구문까지 안 갔으면 결함 아님
                    ran = False
                    for tid in i["targets"]:
                        d = sc.ev("k => window.__mc.diag(k)", tid)
                        if d.get("found") and set(d["cls"].split()) & {"open", "show", "active"}:
                            ran = True
                    if not ran:
                        verdict, detail, cause = "제외", f"조건부 열기 — 여는 구문까지 안 감({i['fn']} → {', '.join(i['targets'])})", ""
                res["tests"].append({"info": i, "path": pth, "verdict": verdict, "detail": detail, "errors": errs, "cause": cause})
                if verdict == "열림":
                    for b in after["bd"]:
                        if b not in before["bd"]:
                            opened_by.setdefault(b, i["text"] or i["onclick"][:30])
                # 다음 단계 탐색: 이 트리거가 페이지 · 모달 · 화면 내 변화를 만들면 그 상태의 새 트리거를 본다
                if len(pth) < MAX_DEPTH and (verdict in ("열림", "페이지") or detail.startswith("화면 내 변화")):
                    if i["key"] not in used_steps:
                        steps.append(i)
            for s in steps:
                if s["key"] in used_steps:
                    continue
                used_steps.add(s["key"])
                npth = pth + (s["key"],)
                if not sc.replay(npth):
                    continue
                nl = sc.ev("() => window.__mc.list()")
                for i in nl:
                    if i["kind"] == "trigger":
                        all_trig.setdefault(i["key"], i)
                if any(i["kind"] == "trigger" and i["vis"] and i["key"] not in tested for i in nl) or len(npth) < MAX_DEPTH:
                    queue.append((npth, nl))
        for k, i in all_trig.items():
            if k not in tested:
                if i["inModal"]:
                    res["inModalHidden"] += 1
                res["hidden"].append(i)
        # (b) 백드롭별 직접 열기
        for b in bds:
            key = b["key"]
            ent = {"key": key, "cls": b["cls"], "a": opened_by.get(key, ""), "b": "", "how": "", "cause": "", "c": ""}
            if not b["id"]:
                ent["b"] = "id 없음"
                res["backdrops"].append(ent)
                continue
            sc.load()
            ops = sc.ev("k => window.__mc.openers(k)", key)
            tried = []

            def attempt(call_js, arg, label):
                sc.load()
                d0 = sc.ev("k => window.__mc.diag(k)", key)
                ne, nd = len(sc.errors), len(sc.dialogs)
                toast0 = sc.ev("() => window.__mc.snap().toast")
                r = sc.ev(call_js, arg)
                sc.page.wait_for_timeout(WAIT_CLICK)
                d1 = sc.ev("k => window.__mc.diag(k)", key)
                toast1 = sc.ev("() => window.__mc.snap().toast")
                note = sc.dialogs[nd:][:1] or ([toast1[:40]] if toast1 and toast1 != toast0 else [])
                tried.append({"label": label, "r": r, "d0": d0, "d1": d1, "errs": sc.errors[ne:], "note": note})
                return d1.get("vis")

            for op in ops[:3]:
                if attempt("k => window.__mc.callOnclick(k)", op["key"], op["onclick"] or op["fn"] or op["id"]):
                    break
            if not ops:
                sc.load()
                for g in sc.ev("k => window.__mc.globalOpeners(k)", key)[:3]:
                    if g["arity"] > 0:
                        tried.append({"label": g["name"] + "(…)", "r": "ARITY", "d0": {}, "d1": {}, "errs": [], "note": []})
                        continue
                    if attempt("n => window.__mc.callGlobal(n)", g["name"], g["name"] + "()"):
                        break
            if not tried:
                ent["b"] = "여는 함수 못 찾음"
                ent["how"] = "onclick · 전역 함수 본문에서 이 id를 여는 구문을 못 찾음(동적 id · addEventListener · 변수 id 추정)"
            else:
                t = next((x for x in tried if x["d1"].get("vis")), None) or next((x for x in tried if x["r"] != "ARITY"), tried[-1])
                ent["how"] = short(t["label"], 70)
                if t["r"] == "ARITY":
                    ent["b"] = "인자 필요(미호출)"
                    ent["cause"] = "전역 함수만 찾음 — 인자가 필요해 직접 호출하지 않음(트리거가 화면에서 만들어질 때 (a)로 검사)"
                elif t["d1"].get("vis"):
                    ent["b"] = "열림"
                else:
                    d0, d1 = t["d0"], t["d1"]
                    c0, c1 = set((d0.get("cls") or "").split()), set((d1.get("cls") or "").split())
                    ran = bool((c1 - c0) & {"open", "show", "active"}) or ("hidden" in c0 and "hidden" not in c1)
                    if t["r"].startswith("ERR"):
                        ent["b"] = "미실행"
                        ent["cause"] = "호출 오류(인자 · 상태 필요 추정) " + t["r"][5:][:80]
                    elif t["errs"]:
                        ent["b"] = "안 열림"
                        ent["cause"] = "JS 에러: " + t["errs"][0]
                    elif ran:
                        ent["b"] = "안 열림"
                        ent["cause"] = cause_of(sc, {"targets": [key], "disabled": False}, []) + f" [호출 전 class='{d0.get('cls')}' inline='{d0.get('inline')}' → 후 class='{d1.get('cls')}' inline='{d1.get('inline')}' display={d1.get('computed')}]"
                    else:
                        ent["b"] = "미실행"
                        ent["cause"] = "여는 구문까지 가지 않음(인자 · 선택 상태 등 조건)" + (f" — {short(t['note'][0], 50)}" if t["note"] else "")
            # (c) 열림 클래스 직접 부여: 새로 로드한 뒤 open → show → active를 차례로 붙여(가드는 MutationObserver라 한 틱 기다림) 보이는지.
            #     여는 코드가 조건 · 인자 때문에 안 돌아도 '그 구문에 도달하면 열리는지'를 본다.
            sc.load()
            ent["c"] = sc.page.evaluate("""async id => {
              const e = document.getElementById(id), tick = () => new Promise(r => setTimeout(r, 60));
              const vis = () => e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) && e.getBoundingClientRect().width > 0;
              const had = e.classList.contains('hidden');
              for (const c of ['open', 'show', 'active']) {
                e.classList.add(c); if (had) e.classList.remove('hidden'); await tick();
                const ok = vis(); e.classList.remove(c); if (had) e.classList.add('hidden');
                if (window.closeAllModals) closeAllModals();
                if (ok) return c;
              }
              return '';
            }""", key)
            res["backdrops"].append(ent)
    finally:
        res["allErrors"] = list(dict.fromkeys(sc.errors))
        sc.close()
    return res


def summarize(res):
    t = res["tests"]
    c = lambda v: sum(1 for x in t if x["verdict"] == v)
    bd = res["backdrops"]
    return {
        "tests": len(t), "open": c("열림"), "page": c("페이지"), "excl": c("제외"), "fail": c("안 열림"), "skip": c("미검사"),
        "hidden": len(res["hidden"]), "bd": len(bd),
        "bd_ok": sum(1 for b in bd if b["a"] or b["b"] == "열림"),
        "bd_fail": sum(1 for b in bd if b["b"] == "안 열림" and not b["a"]),
        "bd_fail_direct": sum(1 for b in bd if b["b"] == "안 열림"),
        "bd_none": sum(1 for b in bd if b["b"] in ("여는 함수 못 찾음", "id 없음") and not b["a"]),
        "bd_c_ok": sum(1 for b in bd if b.get("c")),
        "bd_c_fail": sum(1 for b in bd if not b.get("c") and not b["a"] and b["b"] != "열림"),
        "bd_cond": sum(1 for b in bd if b["b"] in ("미실행", "인자 필요(미호출)") and not b["a"]),
        "errors": len(res["allErrors"]),
    }


def _worker(args):
    """프로세스 하나 = 브라우저 하나. 화면 하나를 새 컨텍스트로 검사."""
    folder, name = args
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        try:
            r = check_screen(br, ROOT / folder / name)
        except Exception as e:  # 도구 자체 오류는 화면 결과로 남긴다
            r = {"file": name, "tests": [], "hidden": [], "inModalHidden": 0, "backdrops": [], "loadErrors": [],
                 "capped": False, "allErrors": [f"도구 오류: {str(e).splitlines()[0][:150]}"]}
        br.close()
    r["folder"] = folder
    r["sum"] = summarize(r)
    s = r["sum"]
    flag = "FAIL" if (s["fail"] or s["bd_fail_direct"] or s["bd_c_fail"] or s["errors"]) else "PASS"
    print(f"[{flag}] {folder}/{name}  트리거 {s['tests']} (열림 {s['open']} · 페이지 {s['page']} · 제외 {s['excl']} · 안 열림 {s['fail']} · 미검사 {s['skip']} · 숨김 {s['hidden']}) "
          f"| 백드롭 {s['bd']} (열림 {s['bd_ok']} · 직접 호출 실패 {s['bd_fail_direct']} · 여는 함수 없음 {s['bd_none']} · 조건 {s['bd_cond']} · (c) {s['bd_c_ok']}/{s['bd']}) | JS 에러 {s['errors']}  {time.time() - t0:.0f}s", flush=True)
    return r


def run_all(folders, only, jobs):
    tasks = []
    for folder in folders:
        for f in sorted((ROOT / folder).glob("*.html")):
            if not only or any(o in f.name for o in only):
                tasks.append((folder, f.name))
    if jobs <= 1:
        out = [_worker(t) for t in tasks]
    else:
        from multiprocessing import Pool
        with Pool(jobs) as pool:
            out = pool.map(_worker, tasks, chunksize=1)
    results = {f: [] for f in folders}
    for r in out:
        results[r["folder"]].append(r)
    return results


def report(results, folders):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = ["# 모달 열림 전수 검사 리포트 (skill_modal_open_check.py)", "",
         f"- 생성: {now}", f"- 대상: {', '.join(folders)}", "- 판정 기준: 도구 머리말 참고. '안 열림'과 '(b) 직접 호출 실패'가 조치 대상, '제외'는 모달이 아닌 다른 동작.", ""]
    for folder in folders:
        rs = results[folder]
        tot = {k: sum(r["sum"][k] for r in rs) for k in rs[0]["sum"]} if rs else {}
        L += [f"## {folder}", "",
              f"- 화면 {len(rs)}개 · 트리거 클릭 {tot.get('tests', 0)} (열림 {tot.get('open', 0)} · 페이지 전환 {tot.get('page', 0)} · 제외 {tot.get('excl', 0)} · **안 열림 {tot.get('fail', 0)}** · 미검사 {tot.get('skip', 0)}) · 숨김(미검사) {tot.get('hidden', 0)}",
              f"- 백드롭 {tot.get('bd', 0)} (열림 {tot.get('bd_ok', 0)} · **안 열림 {tot.get('bd_fail', 0)}** · (b) 직접 호출 실패 {tot.get('bd_fail_direct', 0)} · 여는 함수 못 찾음 {tot.get('bd_none', 0)} · 조건 · 인자 필요 {tot.get('bd_cond', 0)}) · (c) 열림 클래스 부여로 보임 {tot.get('bd_c_ok', 0)}/{tot.get('bd', 0)} · **어떤 방법으로도 안 보임 {tot.get('bd_c_fail', 0)}** · JS 에러 {tot.get('errors', 0)}", "",
              "| 화면 | 트리거 | 열림 | 페이지 | 제외 | 안 열림 | 숨김 | 백드롭 | 백드롭 열림 | 백드롭 안 열림 | (b) 실패 | 여는 함수 없음 | 조건 · 인자 | (c) 클래스 | JS 에러 |",
              "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for r in rs:
            s = r["sum"]
            L.append(f"| {r['file'].replace('_baseline.html', '')} | {s['tests']} | {s['open']} | {s['page']} | {s['excl']} | {s['fail']} | {s['hidden']} | {s['bd']} | {s['bd_ok']} | {s['bd_fail']} | {s['bd_fail_direct']} | {s['bd_none']} | {s['bd_cond']} | {s['bd_c_ok']}/{s['bd']} | {s['errors']} |")
        L.append("")
        fails = [(r, t) for r in rs for t in r["tests"] if t["verdict"] == "안 열림"]
        L += [f"### {folder} — (a) 안 열림 {len(fails)}건", ""]
        if fails:
            L += ["| 화면 | 트리거 | onclick | 대상 | 원인 추정 |", "| :--- | :--- | :--- | :--- | :--- |"]
            for r, t in fails:
                i = t["info"]
                L.append(f"| {r['file'].replace('_baseline.html', '')} | {short(i['text'], 30)}{' (경로 ' + str(len(t['path'])) + '단계)' if t['path'] else ''} | `{short(i['onclick'] or i['dt'] or i['id'], 60)}` | {short(t['detail'], 50)} | {short(t['cause'], 120)} |")
        else:
            L.append("- 없음")
        L.append("")
        bf = [(r, b) for r in rs for b in r["backdrops"] if b["b"] == "안 열림"]
        L += [f"### {folder} — (b) 백드롭 직접 호출 실패 {len(bf)}건", ""]
        if bf:
            L += ["| 화면 | 백드롭 | (a) 클릭으로 열림 | 호출 | 원인 추정 |", "| :--- | :--- | :--- | :--- | :--- |"]
            for r, b in bf:
                L.append(f"| {r['file'].replace('_baseline.html', '')} | {b['key']} | {short(b['a'], 30) or '-'} | `{b['how']}` | {short(b['cause'], 120)} |")
        else:
            L.append("- 없음")
        L.append("")
        nf = [(r, b) for r in rs for b in r["backdrops"] if b["b"] in ("여는 함수 못 찾음", "id 없음", "미실행", "인자 필요(미호출)") and not b["a"]]
        L += [f"### {folder} — 참고: (a)에서 안 열렸고 (b)도 판정 못 한 백드롭 {len(nf)}개 — 여는 함수 못 찾음 · 조건 · 인자 필요(결함 아님일 수 있음, 회귀 스크립트로 개별 확인)", ""]
        for r, b in nf:
            L.append(f"- {r['file'].replace('_baseline.html', '')} `{b['key']}` — {b['b']} `{b['how']}` {b['cause']} → (c) " + (f"`{b['c']}` 클래스 부여 시 보임(여는 구문에 도달하면 열림)" if b.get("c") else "**열림 클래스로도 안 보임**"))
        L.append("")
        ex = [(r, t) for r in rs for t in r["tests"] if t["verdict"] in ("제외", "미검사")]
        L += [f"### {folder} — 제외 · 미검사 {len(ex)}건 (모달 아님)", "", "<details><summary>펼치기</summary>", "",
              "| 화면 | 트리거 | onclick | 판정 | 내용 |", "| :--- | :--- | :--- | :--- | :--- |"]
        for r, t in ex:
            i = t["info"]
            L.append(f"| {r['file'].replace('_baseline.html', '')} | {short(i['text'], 30)} | `{short(i['onclick'] or i['dt'] or i['id'], 60)}` | {t['verdict']} | {short(t['detail'], 70)} |")
        L += ["", "</details>", ""]
        er = [(r, e) for r in rs for e in r["allErrors"]]
        L += [f"### {folder} — JS · 콘솔 에러 {len(er)}건", ""]
        for r, e in er:
            L.append(f"- {r['file'].replace('_baseline.html', '')}: `{short(e, 150)}`")
        if not er:
            L.append("- 없음")
        L += ["", "<details><summary>숨김(미검사) 트리거 — 탭 · 페이지 · 모달 2단계 안에서 끝내 보이지 않은 것(백드롭 대상이면 (b)로 검사됨)</summary>", ""]
        for r in rs:
            if r["hidden"]:
                L.append(f"- {r['file'].replace('_baseline.html', '')} ({len(r['hidden'])}개, 모달 안 {r['inModalHidden']}): " +
                         ", ".join(short(i["text"] or i["fn"] or i["id"], 24) for i in r["hidden"][:25]) + (" …" if len(r["hidden"]) > 25 else ""))
        L += ["", "</details>", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="*")
    ap.add_argument("--only", default="", help="화면 코드 일부(쉼표 구분), 예: SETT-002,PROD-003")
    ap.add_argument("--jobs", type=int, default=6, help="동시에 띄울 브라우저 수(기본 6, 1이면 순차)")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    folders = a.folders or FOLDERS
    only = [o.strip() for o in a.only.split(",") if o.strip()]
    t0 = time.time()
    results = run_all(folders, only, a.jobs)
    print(f"\n소요 {time.time() - t0:.0f}s")
    report(results, folders)
    bad = 0
    for f in folders:
        fa = sum(r["sum"]["fail"] for r in results[f])
        fb = sum(r["sum"]["bd_fail_direct"] for r in results[f])
        er = sum(r["sum"]["errors"] for r in results[f])
        print(f"\n[{f}] 트리거 안 열림 {fa}건 · 백드롭 직접 호출 실패 {fb}건 · JS 에러 {er}건")
        bad += fa + fb
    print(f"[Skill 7 리포트 저장 완료] {REPORT.relative_to(ROOT)}")
    if a.strict and bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
