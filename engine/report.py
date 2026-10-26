"""권리자별 0→12단계 흐름 HTML 보고서.

    python engine/report.py --result out.json --out report.html

권리자 → 계약 → 단계(0 상위 인입 · 1~11 · 12 마감 검증) → 계산 줄(수취인 · 라인 · 필드 · 입력 · 수식 · 절사 전 · 절사 · 결과 · 근거).
잠정 규칙(SPEC 16절)을 쓴 줄은 '잠정' 표시와 질문 번호가 붙는다.
대조 결과 HTML(compare.py --html)도 같은 틀(render_compare_html)로 만든다.
"""

import argparse
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSS = """
:root{--bg:#fff;--fg:#1d2330;--muted:#5d6675;--line:#dfe3ea;--card:#f6f8fb;--ok:#1f7a3f;--ok-bg:#e5f4ea;
--bad:#b42318;--bad-bg:#fdecea;--warn:#8a5a00;--warn-bg:#fff4dc;--acc:#2456c7;--mono:Consolas,"D2Coding",monospace}
@media (prefers-color-scheme:dark){:root{--bg:#14171d;--fg:#e6e9ef;--muted:#9aa3b2;--line:#2b313c;--card:#1b2029;
--ok:#6fd394;--ok-bg:#16301f;--bad:#ff8a80;--bad-bg:#3a1a18;--warn:#f3c66b;--warn-bg:#352a12;--acc:#8fb0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 "Pretendard","Malgun Gothic",sans-serif}
main{max-width:1320px;margin:0 auto;padding:20px 16px 60px}h1{font-size:20px;margin:0 0 4px}h2{font-size:16px;margin:24px 0 8px}
h3{font-size:14px;margin:12px 0 6px}.meta{color:var(--muted);margin-bottom:12px}.bar{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
input[type=search]{background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:4px 8px;min-width:220px}
details{border:1px solid var(--line);border-radius:8px;margin:6px 0;background:var(--bg)}
details>summary{cursor:pointer;padding:8px 12px;list-style:none;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
details>summary::-webkit-details-marker{display:none}details>summary::before{content:"▸";color:var(--muted)}
details[open]>summary::before{content:"▾"}details.holder>summary{font-weight:600;background:var(--card);border-radius:8px}
details.contract{margin:6px 8px}details.step{margin:4px 12px}.body{padding:4px 12px 12px;overflow-x:auto}
.no{display:inline-block;min-width:26px;text-align:center;border-radius:12px;background:var(--card);border:1px solid var(--line);font-size:12px}
.code{font-family:var(--mono);font-size:12px;color:var(--acc)}.muted{color:var(--muted)}
.badge{font-size:12px;border-radius:10px;padding:0 8px;white-space:nowrap}.b-ok{color:var(--ok);background:var(--ok-bg)}
.b-bad{color:var(--bad);background:var(--bad-bg)}.b-warn{color:var(--warn);background:var(--warn-bg)}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:500;white-space:nowrap}td.num{text-align:right;font-family:var(--mono);white-space:nowrap}
td.f{font-size:12px;min-width:220px}td.f .c{display:block;font-family:var(--mono);color:var(--muted);font-size:11px}
tr.first td{background:var(--bad-bg)}tr.calc td{color:var(--muted)}
.kv{font-family:var(--mono);font-size:12px;white-space:pre-wrap;color:var(--muted)}
.chips{display:flex;gap:6px;flex-wrap:wrap;font-weight:400}.chip{font-size:12px;border:1px solid var(--line);border-radius:10px;padding:0 8px}
"""

JS = """
function setAll(o){document.querySelectorAll('details').forEach(d=>d.open=o)}
function filt(q){q=q.trim().toLowerCase();document.querySelectorAll('details.holder').forEach(d=>{
d.style.display=!q||d.dataset.key.toLowerCase().includes(q)?'':'none'})}
function onlyOut(on){document.querySelectorAll('tr.calc').forEach(r=>r.style.display=on?'none':'')}
"""

STEP_FALLBACK = [{"no": 0, "code": "PIPELINE_IN", "name": "상위 인입 파이프라인", "ref": ""}]


def esc(x):
    return html.escape("" if x is None else str(x))


def fmt(v):
    if isinstance(v, bool):
        return "예" if v else "아니오"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, str):
        s = v.lstrip("-")
        if s.isdigit():
            return f"{int(v):,}"
        if s.replace(".", "", 1).isdigit() and s.count(".") == 1:
            i, f = v.split(".")
            return f"{int(i):,}.{f}" if i not in ("", "-") else esc(v)
    if isinstance(v, (list, dict)):
        return esc(json.dumps(v, ensure_ascii=False))
    return esc(v)


def kv(d):
    if not d:
        return ""
    return "\n".join(f"{esc(k)} = {fmt(v)}" for k, v in d.items())


def page(title, meta, body):
    return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(title)}</title>"
            f"<style>{CSS}</style><script>{JS}</script></head><body><main>"
            f"<h1>{esc(title)}</h1><div class='meta'>{meta}</div>"
            f"<div class='bar'><button onclick='setAll(true)'>모두 펼치기</button>"
            f"<button onclick='setAll(false)'>모두 접기</button>"
            f"<label class='muted'><input type='checkbox' onchange='onlyOut(this.checked)'> 결과 값 줄만</label>"
            f"<input type='search' placeholder='권리자 · 수취인 검색' oninput='filt(this.value)'></div>"
            f"{body}</main></body></html>")


def trace_rows(entries, mark_seq=()):
    out = ["<table><tr><th>#</th><th>수취인</th><th>라인</th><th>필드</th><th>입력값</th>"
           "<th>적용 수식(정본 표기) · 의사코드</th><th>절사 전</th><th>절사</th><th>결과값</th><th>근거</th></tr>"]
    for e in entries:
        sc = e.get("scope") or {}
        cls = []
        if e["seq"] in mark_seq:
            cls.append("first")
        if not e.get("output", True):
            cls.append("calc")
        prov = (f" <span class='badge b-warn' title='{esc(e.get('note'))}'>잠정 {esc(e.get('note'))}</span>"
                if e.get("provisional") else (f" <span class='muted'>{esc(e.get('note'))}</span>" if e.get("note") else ""))
        ref_id = f"<br><span class='muted'>{esc(sc.get('ref_id'))}</span>" if sc.get("ref_id") else ""
        out.append(f"<tr class='{' '.join(cls)}'><td class='muted'>{e['seq']}</td><td>{esc(sc.get('payee_id') or '—')}</td>"
                   f"<td>{esc(sc.get('line_id') or '—')}{ref_id}</td><td class='code'>{esc(e['field'])}</td>"
                   f"<td class='kv'>{kv(e.get('inputs'))}</td>"
                   f"<td class='f'>{esc(e.get('formula'))}<span class='c'>{esc(e.get('formula_code'))}</span></td>"
                   f"<td class='num'>{fmt(e.get('before_rounding'))}</td><td class='muted'>{esc(e.get('rounding'))}</td>"
                   f"<td class='num'>{fmt(e.get('result'))}{prov}</td><td class='muted'>{esc(e.get('canon_ref'))}</td></tr>")
    out.append("</table>")
    return "".join(out)


def step_block(step, entries, extra_badge="", open_=False, mark_seq=()):
    outs = [e for e in entries if e.get("output", True)]
    prov = sum(1 for e in entries if e.get("provisional"))
    if not entries:
        badge = "<span class='badge muted'>기록 없음</span>"
    else:
        badge = f"<span class='muted'>결과 {len(outs)} · 계산 {len(entries) - len(outs)}줄</span>"
    if prov:
        badge += f" <span class='badge b-warn'>잠정 {prov}</span>"
    body = trace_rows(entries, mark_seq) if entries else "<span class='muted'>이 단계에서 남긴 계산 줄이 없습니다.</span>"
    return (f"<details class='step'{' open' if open_ else ''}><summary><span class='no'>{step['no']}</span>"
            f"<span class='code'>{esc(step['code'])}</span>{esc(step['name'])} {badge} {extra_badge}"
            f"<span class='muted'>{esc(step['ref'])}</span></summary><div class='body'>{body}</div></details>")


def payee_table(contract):
    rows = []
    for p in contract.get("payees", []):
        t, c, o = p.get("TAX", {}), p.get("CLAIM", {}), p.get("PAYOUT", {})
        rows.append(f"<tr><td>{esc(p['payee_id'])}</td><td class='num'>{fmt(t.get('pre_tax_payable_total'))}</td>"
                    f"<td class='num'>{fmt(t.get('withholding_total'))}</td><td class='num'>{fmt(t.get('vat_total'))}</td>"
                    f"<td class='num'>{fmt(t.get('net_settle_amount'))}</td><td class='num'>{fmt(c.get('claim_negative_net'))}</td>"
                    f"<td class='num'>{fmt(c.get('payable_net_for_payout'))}</td>"
                    f"<td class='num'>{fmt(o.get('payout_judgement_amount'))}</td>"
                    f"<td>{badge_yn(o.get('payout_confirmed_yn'), '지급', '이월')}</td>"
                    f"<td class='num'>{fmt(o.get('payout_amount'))}</td></tr>")
    if not rows:
        return ""
    return ("<h3>수취인 요약</h3><table><tr><th>수취인</th><th>세전 지급액</th><th>원천세</th><th>부가세</th><th>9단계 실정산액</th>"
            "<th>청구 대상 음수</th><th>지급 판정 전달액</th><th>판정 금액</th><th>판정</th><th>지급 확정액</th></tr>"
            + "".join(rows) + "</table>")


def badge_yn(v, yes, no):
    if v is None:
        return ""
    return f"<span class='badge {'b-ok' if v else 'b-warn'}'>{yes if v else no}</span>"


def render_html(result, title="정산 기준 계산기 — 단계표", case=None):
    trace = result.get("trace", [])
    steps = result.get("steps") or STEP_FALLBACK
    issues = result.get("issues", [])
    cont = result.get("continuity", [])
    bad = [c for c in cont if not c.get("ok")]
    by_holder = defaultdict(lambda: defaultdict(list))
    for e in trace:
        sc = e.get("scope") or {}
        by_holder[sc.get("rights_holder_id")][sc.get("contract_id")].append(e)
    status = result.get("status")
    sbadge = f"<span class='badge {'b-ok' if status == 'OK' else 'b-warn'}'>{esc(status)}</span>"
    meta = (f"정산월 {esc(result.get('settlement_month'))} · 엔진 {esc(result.get('engine_version'))} · {sbadge}"
            f" · 권리자 {len([h for h in by_holder if h])} · trace {len(trace)}줄"
            f" · 이월 연속성 {len(cont) - len(bad)}/{len(cont)} · 확인 필요 {len(issues)}건")
    parts = [case_block(case)] if case else []
    contracts_out = {c["contract_id"]: c for h in result.get("rights_holders", []) for c in h.get("contracts", [])}
    for holder in sorted(by_holder, key=lambda x: (x is None, str(x))):
        cblocks = []
        payees = set()
        for cid, entries in by_holder[holder].items():
            by_step = defaultdict(list)
            for e in entries:
                by_step[e["step_code"]].append(e)
                if (e.get("scope") or {}).get("payee_id"):
                    payees.add(e["scope"]["payee_id"])
            body = "".join(step_block(s, by_step.get(s["code"], [])) for s in steps)
            body += payee_table(contracts_out.get(cid, {}))
            chips = summary_chips(contracts_out.get(cid, {}))
            if cid is None:
                cblocks.append(body)
            else:
                cblocks.append(f"<details class='contract' open><summary>계약 <span class='code'>{esc(cid)}</span>"
                               f"<span class='chips'>{chips}</span></summary><div class='body'>{body}</div></details>")
        label = holder or "(공통 · 자사 집계 · 권리자 미귀속)"
        key = " ".join([str(holder)] + sorted(payees))
        parts.append(f"<details class='holder' data-key='{esc(key)}'{' open' if holder else ''}><summary>"
                     f"{esc(label)}<span class='muted'>수취인 {len(payees)}</span></summary>"
                     f"<div class='body'>{''.join(cblocks)}</div></details>")
    parts.append(continuity_table(cont))
    parts.append(simple_table("내부 집계 전용(Pipeline 2.3 · 비인입)", result.get("internal_only", [])))
    parts.append(simple_table("비인입 라인", result.get("excluded_lines", [])))
    parts.append(issues_table(issues))
    parts.append(simple_table("경고", result.get("warnings", [])))
    parts.append(simple_table("오류", result.get("errors", [])))
    return page(title, meta, "".join(parts))


def summary_chips(c):
    s = c.get("steps", {})
    pay = c.get("payees", [])
    chips = []
    if s.get("ACCRUAL", {}).get("accrual_total") is not None:
        chips.append(("신규 세전 발생액", s["ACCRUAL"]["accrual_total"]))
    if s.get("LUMPSUM_ADD", {}).get("pre_split_supply") is not None:
        chips.append(("분할 전 공급가액", s["LUMPSUM_ADD"]["pre_split_supply"]))
    if pay:
        chips.append(("9단계 실정산액", sum(int(p.get("TAX", {}).get("net_settle_amount") or 0) for p in pay)))
        chips.append(("지급 확정액", sum(int(p.get("PAYOUT", {}).get("payout_amount") or 0) for p in pay)))
    return "".join(f"<span class='chip'>{esc(k)} {fmt(v)}</span>" for k, v in chips)


def continuity_table(rows):
    if not rows:
        return ""
    body = "".join(f"<tr><td>{badge_yn(r['ok'], '일치', '불일치')}</td><td>{esc(r['account_type'])}</td><td>{esc(r['key'])}</td>"
                   f"<td class='num'>{fmt(r['prev_end'])}</td><td class='num'>{fmt(r['new'])}</td>"
                   f"<td class='num'>{fmt(r['extinguished'])}</td><td class='num'>{fmt(r['end'])}</td></tr>" for r in rows)
    return (f"<h2>이월 연속성 등식(마감 검증)</h2><table><tr><th>결과</th><th>계정</th><th>키</th><th>전월 말</th><th>당월 신규</th>"
            f"<th>당월 소멸 · 변동</th><th>당월 말</th></tr>{body}</table>")


def simple_table(heading, rows):
    if not rows:
        return ""
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    body = "".join("<tr>" + "".join(f"<td>{fmt(r.get(k))}</td>" for k in cols) + "</tr>" for r in rows)
    return f"<h2>{esc(heading)}</h2><table><tr>{''.join(f'<th>{esc(k)}</th>' for k in cols)}</tr>{body}</table>"


def issues_table(issues):
    if not issues:
        return ""
    rows = "".join(f"<tr><td><span class='badge b-warn'>{esc(i['kind'])}</span></td><td class='code'>{esc(i['step_code'])}</td>"
                   f"<td>{esc(i.get('question'))}</td><td>{esc(i['rights_holder_id'])}</td><td>{esc(i['message'])}</td>"
                   f"<td class='muted'>{esc(i['ref'])}</td></tr>" for i in issues)
    return (f"<h2>잠정 규칙 사용 · 입력 부족(SPEC 16절 질문 번호)</h2><table><tr><th>구분</th><th>단계</th><th>질문</th>"
            f"<th>권리자</th><th>내용</th><th>근거</th></tr>{rows}</table>")


def case_block(case):
    res = case["result"]
    cls = {"PASS": "b-ok", "FAIL": "b-bad", "ERROR": "b-bad"}.get(res, "b-warn")
    rows = "".join(
        f"<tr><td><span class='no'>{d['step_no']}</span> <span class='code'>{esc(d['step_code'])}</span></td>"
        f"<td class='code'>{esc(d['path'])}</td><td class='num'>{fmt(d['expected'])}</td>"
        f"<td class='num'>{fmt(d['calc']) if d['found'] else '(없음)'}</td><td>{esc(d.get('cause'))} {esc(d.get('issue') or '')}</td>"
        f"<td class='muted'>{esc(d.get('engine_field'))}</td></tr>" for d in case["diffs"])
    narr = "".join(f"<tr><td class='code'>{esc(d['step_code'])}</td><td class='code'>{esc(d['path'])}</td>"
                   f"<td>{esc(d['expected'])}</td><td>{esc(d['calc'])}</td></tr>" for d in case["narrative"])
    notes = "".join(f"<li>{esc(n)}</li>" for n in case.get("adapter_notes", []))
    out = (f"<h2>fixture 판정 <span class='badge {cls}'>{esc(res)}</span> <span class='muted'>"
           f"정본 상태 {esc(case['expected_status'])} · 일치 {case['matched']}/{case['expected_count']}</span></h2>"
           f"<div class='muted'>{esc(case.get('ref'))}</div>")
    if rows:
        out += ("<h3>차이(수치 · 불리언)</h3><table><tr><th>단계</th><th>기대값 경로</th><th>기대</th><th>계산</th><th>원인</th>"
                f"<th>엔진 필드</th></tr>{rows}</table>")
    if narr:
        out += f"<h3>서술 기대값(비교 제외)</h3><table><tr><th>단계</th><th>경로</th><th>기대</th><th>계산</th></tr>{narr}</table>"
    if notes:
        out += f"<h3>입력 변환 가정(tests/adapter.py)</h3><ul>{notes}</ul>"
    return out


def render_compare_html(cmp, result, title="정산 대조 — 계산기 vs 개발"):
    """cmp = compare.compare() 결과. 권리자 · 수취인별로 처음 갈라진 단계를 펼쳐 둔다."""
    s = cmp["summary"]
    meta = (f"정산월 {esc(result.get('settlement_month'))} · 권리자 {len(cmp['groups'])} · 비교 {s['compared']}건 · 일치 {s['ok']}"
            f" · 차이 {s['diff']} · 계산기 값 없음 {s['calc_missing']} · 개발 값 없음 {s['dev_missing']}"
            f" · 허용 오차 {esc(s['tolerance'])}")
    trace = result.get("trace", [])
    steps = {x["code"]: x for x in result.get("steps", [])}
    parts = []
    for g in cmp["groups"]:
        fd = g["first_divergence"]
        badge = (f"<span class='badge b-bad'>처음 갈라진 단계 {fd['step_no']} {esc(fd['step_code'])}</span>" if fd
                 else "<span class='badge b-ok'>일치</span>")
        rows = "".join(
            f"<tr{' class=\"first\"' if fd and r['step_code'] == fd['step_code'] and r['status'] != 'OK' else ''}>"
            f"<td><span class='no'>{r['step_no']}</span> <span class='code'>{esc(r['step_code'])}</span></td>"
            f"<td>{esc(r['contract_id'] or '—')}</td><td>{esc(r['payee_id'] or '—')}</td><td>{esc(r['line_id'] or '—')}</td>"
            f"<td class='code'>{esc(r['field'])}</td>"
            f"<td class='num'>{fmt(r['calc'])}</td><td class='num'>{fmt(r['dev'])}</td><td class='num'>{fmt(r['diff'])}</td>"
            f"<td>{status_badge(r['status'])}</td><td class='muted'>{esc(r.get('dev_column'))}</td></tr>"
            for r in g["rows"])
        diff_tbl = (f"<table><tr><th>단계</th><th>계약</th><th>수취인</th><th>라인</th><th>필드</th><th>계산기</th><th>개발</th><th>차이</th>"
                    f"<th>판정</th><th>개발 컬럼</th></tr>{rows}</table>")
        detail = ""
        if fd and fd["step_code"] in steps:
            fpay = {r["payee_id"] for r in fd["rows"]}
            ents = [e for e in trace if (e.get("scope") or {}).get("rights_holder_id") == g["rights_holder_id"]
                    and e["step_code"] == fd["step_code"]
                    and (None in fpay or (e.get("scope") or {}).get("payee_id") in fpay | {None})]
            marks = {e["seq"] for e in ents if e["field"] in fd["fields"]}
            detail = ("<h3>처음 갈라진 단계의 계산기 추적(입력 · 수식 · 계산기 값) — 개발 값은 위 표</h3>"
                      + step_block(steps[fd["step_code"]], ents, open_=True, mark_seq=marks))
        pays = sorted({r["payee_id"] for r in g["rows"] if r["payee_id"]})
        key = " ".join([str(g["rights_holder_id"])] + pays)
        parts.append(f"<details class='holder' data-key='{esc(key)}'{' open' if fd else ''}><summary>"
                     f"{esc(g['rights_holder_id'])}<span class='muted'>수취인 {esc(', '.join(pays) or '—')}</span>{badge}"
                     f"</summary><div class='body'>{diff_tbl}{detail}</div></details>")
    return page(title, meta, "".join(parts) or "<p class='muted'>비교할 행이 없습니다.</p>")


def status_badge(st):
    cls = {"OK": "b-ok", "DIFF": "b-bad", "CALC_MISSING": "b-warn", "DEV_MISSING": "b-warn"}.get(st, "")
    label = {"OK": "일치", "DIFF": "차이", "CALC_MISSING": "계산기 값 없음", "DEV_MISSING": "개발 값 없음"}.get(st, st)
    return f"<span class='badge {cls}'>{label}</span>"


def main(argv=None):
    ap = argparse.ArgumentParser(description="계산기 출력 JSON → 권리자별 단계표 HTML")
    ap.add_argument("--result", required=True, help="engine/run.py 출력 JSON")
    ap.add_argument("--out", required=True, help="HTML 경로")
    args = ap.parse_args(argv)
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(render_html(result), encoding="utf-8")
    print(f"보고서: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
