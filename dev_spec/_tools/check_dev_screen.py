"""prototype_dev 화면이 prototype_clean과 똑같이 동작하는지 확인한다.

사용: python dev_spec/_tools/check_dev_screen.py ADMN-USER-001 [ADMN-...]
  1. 두 폴더 화면을 각각 새 브라우저 컨텍스트로 열어 JS 오류 · 콘솔 오류를 모은다.
  2. 탭 · 서브뷰 · 하위 화면 전환 버튼을 차례로 눌러 오류를 모은다(두 폴더 같은 순서).
  3. dev_spec/_maps/<코드>.py 의 VERIFY 목록(라벨, JS, 보여야 할 선택자)을 두 폴더에서 돌려 결과를 비교한다.
  4. onclick 함수 이름 집합이 줄지 않았는지, 개발 표시(라우트 · 개발에만 · 프로토타입에만 · name) 수를 센다.
통과 기준: 두 폴더 모두 오류 0, VERIFY 결과 같음, onclick 함수 누락 0.
"""
import asyncio
import importlib.util
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
TAB_SEL = ".subview-tab, .subview-btn, .tab-btn, [onclick^=\"switchView(\"], [onclick^=\"switchTab(\"], [onclick^=\"switchCsTab(\"], [onclick^=\"SJM_PAGE\"]"


def load_verify(code):
    p = ROOT / "dev_spec" / "_maps" / f"{code}.py"
    if not p.exists():
        return []
    spec = importlib.util.spec_from_file_location(code.replace("-", "_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, "VERIFY", [])


async def run(pw, folder, code, verify):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={"width": 1440, "height": 900})
    pg = await ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)[:200]))
    pg.on("console", lambda m: errs.append("console: " + m.text[:200]) if m.type == "error" else None)
    pg.on("dialog", lambda d: asyncio.ensure_future(d.dismiss()))
    await pg.goto((ROOT / folder / f"{code}_baseline.html").as_uri())
    await pg.wait_for_timeout(500)
    fns = set(await pg.evaluate("""() => Array.from(document.querySelectorAll('[onclick]')).map(e => (e.getAttribute('onclick').match(/^\\s*([\\w.$]+)\\s*\\(/) || [])[1]).filter(Boolean)"""))
    n_tabs = await pg.evaluate(f"() => document.querySelectorAll({TAB_SEL!r}).length")
    for i in range(n_tabs):
        try:
            await pg.evaluate(f"(i) => {{ const el = document.querySelectorAll({TAB_SEL!r})[i]; if (el && el.offsetParent !== null) el.click(); }}", i)
            await pg.wait_for_timeout(60)
        except Exception as e:
            errs.append(f"tab {i}: {str(e)[:120]}")
    await pg.goto((ROOT / folder / f"{code}_baseline.html").as_uri())
    await pg.wait_for_timeout(400)
    vres = []
    for label, js, sel in verify:
        try:
            await pg.evaluate(f"() => {{ if (typeof closeAllModals === 'function') closeAllModals(); {js}; }}")
            await pg.wait_for_timeout(120)
            ok = True
            if sel:
                ok = await pg.evaluate("(s) => s.split('|').some(q => { const e = document.querySelector(q); return !!e && getComputedStyle(e).display !== 'none' && e.offsetParent !== null || (!!e && getComputedStyle(e).position === 'fixed' && getComputedStyle(e).display !== 'none'); })", sel)
            vres.append((label, ok))
        except Exception as e:
            vres.append((label, "오류 " + str(e)[:100]))
    counts = await pg.evaluate("""() => ({
      route: document.querySelectorAll('[data-dev-route]').length,
      devOnly: document.querySelectorAll('[data-dev-flag="dev-only"]').length,
      protoOnly: document.querySelectorAll('[data-dev-flag="proto-only"]').length,
      name: document.querySelectorAll('[name],[data-dev-name]').length,
      devMap: !!document.getElementById('dev-map')
    })""")
    await b.close()
    return dict(errs=errs, fns=fns, tabs=n_tabs, verify=vres, counts=counts)


async def main(codes):
    ok_all = True
    async with async_playwright() as pw:
        for code in codes:
            verify = load_verify(code)
            c = await run(pw, "prototype_clean", code, verify)
            d = await run(pw, "prototype_dev", code, verify)
            missing = sorted(c["fns"] - d["fns"])
            vdiff = [(a[0], a[1], b[1]) for a, b in zip(c["verify"], d["verify"]) if a[1] != b[1] or b[1] is not True]
            ok = not c["errs"] and not d["errs"] and not missing and not vdiff and d["counts"]["devMap"]
            ok_all &= ok
            print(f"[{code}] {'통과' if ok else '실패'} — 탭 {d['tabs']} · VERIFY {len(verify)} · onclick 함수 {len(d['fns'])} · 개발 표시 {d['counts']}")
            for e in c["errs"]:
                print("   clean", e)
            for e in d["errs"]:
                print("   dev  ", e)
            if missing:
                print("   dev에서 사라진 onclick 함수:", missing)
            for v in vdiff:
                print("   VERIFY 차이:", v)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main(sys.argv[1:])) else 1)
