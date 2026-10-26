"""ADMN-SETT-009 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-SETT-009.md
apply_dev_map.py가 읽는다. 각 항목의 기대 건수가 원본과 다르면 전체를 멈춘다.
"""
import json

DEV_COMMIT = "d562524a"
A = "/sj-admin"
OPS = []


def R(find, replace, count=1):
    OPS.append(dict(kind="replace", find=find, replace=replace, count=count))


def RE(find, replace, count):
    OPS.append(dict(kind="regex", find=find, replace=replace, count=count))


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def attrs(route=None, method=None, url=None, perm=None, flag=None, note=None, name=None, value=None):
    out = ""
    for k, v in (("route", route), ("method", method), ("url", url), ("perm", perm), ("flag", flag), ("note", note), ("name", name), ("value", value)):
        if v:
            out += f' data-dev-{k}="{esc(v)}"'
    return out


def ACT(fn, count=1, **kw):
    """onclick="fn( 앞에 개발 라우트 속성을 단다"""
    R(f'onclick="{fn}(', attrs(**kw).lstrip() + f' onclick="{fn}(', count)


def NAME(id_, name, value=None, note=None):
    """JS가 id로 찾는 입력 — 실제 name 속성을 개발 이름으로 넣는다"""
    R(f'id="{id_}"', f'id="{id_}" name="{name}"' + attrs(value=value, note=note), 1)


def DEVNAME(find, name, value=None, note=None, count=1):
    """JS가 name · value에 기대는 라디오 등 — data-dev-name · data-dev-value만 단다"""
    R(find, find + attrs(name=name, value=value, note=note), count)


def RENAME_ID(old, new, count):
    """id 와 그 참조(getElementById · 문자열)를 모두 바꾼다"""
    RE(r"(?<![\w-])" + old.replace("-", r"\-") + r"(?![\w-])", new, count)


def FLAG(id_, flag, note=None):
    """id 요소에 개발 표시(dev-only · proto-only)만 단다"""
    R(f'id="{id_}"', f'id="{id_}"' + attrs(flag=flag, note=note), 1)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-SETT-009",
    "devCommit": DEV_COMMIT,
    "progress": "구현(조회 전용 · 산출물 다운로드는 사유 필수). 전사 대사표 CSV · 검색어 · 홈택스 TXT 추출은 개발 미구현 — 주황 표시",
    "menus": [
        {"route": "admin.settlement.internal.index", "label": "내부 정산 조회"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

LIST = dict(route="admin.settlement.internal.index", method="GET", url=A + "/settlement/internal", perm="조회")
DL = dict(route="admin.settlement.internal.download", method="GET", url=A + "/settlement/internal/download?month=&output=", perm="다운로드")
DL_NOTE = "사유 필수(ReasonRequest reason · reason_ref · reason_etc, 공통 #layerReason) — 엑셀(산출물 시트)로 나감"

# ── 상단 ────────────────────────────────────────────
NAME("monthSelect", "month", value="YYYY-MM", note="개발은 월 버튼 + #monthPick")
ACT("exportInternalReport", flag="proto-only", route="admin.settlement.internal.report.download (규칙)", method="GET", url=A + "/settlement/internal/report/download", perm="다운로드",
    note="전사 내부 손익 · 정산 대사표 — 개발은 산출물별 다운로드만")

# ── KPI · 탭 · 필터 ──────────────────────────────────
ACT("setPipelineFilter", count=5, note="개발 ?pipeline= — KPI 'INTERNAL' · 'EXTERNAL'(귀속 필터)은 개발 값 없음", **LIST)
R('id="tabBtn-overview" onclick="switchTab(', 'id="tabBtn-overview"' + attrs(name="tab", value="pipeline", **LIST) + ' onclick="switchTab(')
R('id="tabBtn-support" onclick="switchTab(', 'id="tabBtn-support"' + attrs(name="tab", value="support", **LIST) + ' onclick="switchTab(')
R('id="tabBtn-goods" onclick="switchTab(', 'id="tabBtn-goods"' + attrs(name="tab", value="goods", **LIST) + ' onclick="switchTab(')
R('id="tabBtn-taxreport" onclick="switchTab(', 'id="tabBtn-taxreport"' + attrs(name="tab", value="tax", **LIST) + ' onclick="switchTab(')
NAME("pipeFilterSelect", "pipeline", value="'' 전체 · P1_1 · P2_1 · P2_2 · P2_3 · P5_1 · P7_1")
R('<option value="INTERNAL">자사 귀속(RH-INTERNAL) 포함 건만</option>',
  '<option value="P7_1" data-dev-flag="dev-only" data-dev-note="개발 파이프라인 값(비정기 가산금) — settlement_lines.pipeline_id 주석은 LUMPSUM(정책 질문 D-SETT)">비정기 가산금</option>\n'
  '              <option value="INTERNAL" data-dev-flag="proto-only" data-dev-note="귀속 필터 — 개발 pipeline 값 없음">자사 귀속(RH-INTERNAL) 포함 건만</option>')
R('<option value="EXTERNAL">외부 권리자 지급 포함 건만</option>',
  '<option value="EXTERNAL" data-dev-flag="proto-only" data-dev-note="귀속 필터 — 개발 pipeline 값 없음">외부 권리자 지급 포함 건만</option>')
R('id="searchKeyword"', 'id="searchKeyword"' + attrs(flag="proto-only", note="검색어 — 개발 없음(파이프라인 · 귀속 단위 집계)"))

# ── 산출물 다운로드(output) ─────────────────────────────
for fn, out, extra in (
    ("원천징수이행상황신고서_기초자료_202610.csv", "withholding", {}),
    ("사업소득_간이지급명세서_홈택스전산매체_202610.txt", "business_income", {"note": "홈택스 TXT 추출 — 개발 버튼 disabled, 엑셀로 나감. " + DL_NOTE}),
    ("기타소득_C19_간이지급명세서_202610.txt", "other_income", {"note": "홈택스 TXT 추출 — 개발 버튼 disabled, 엑셀로 나감. " + DL_NOTE}),
    ("과세표준_실지급액_차액검증명세_202610.csv", "base_diff", {}),
    ("면세3계통_및_과세매출_분리명세_202610.csv", "exempt_sales", {}),
    ("위탁수수료_및_매입계산서_수취명세_202610.csv", "consignment", {}),
):
    R(f"onclick=\"downloadTaxFile('{fn}')", attrs(name="output", value=out, note=extra.get("note", DL_NOTE), **DL).lstrip() + f" onclick=\"downloadTaxFile('{fn}')")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("손익 대조표 탭", "switchTab('overview')", "#tabPanel-overview"),
    ("개발지원금 탭", "switchTab('support')", "#tabPanel-support"),
    ("소비재 · 비인입 도서 탭", "switchTab('goods')", "#tabPanel-goods"),
    ("세무 산출물 탭", "switchTab('taxreport')", "#tabPanel-taxreport"),
    ("파이프라인 필터", "switchTab('overview'); setPipelineFilter('P5_1')", "#pipeFilterSelect"),
    ("월 변경", "changeMonth('2026-09')", "#monthSelect"),
]
