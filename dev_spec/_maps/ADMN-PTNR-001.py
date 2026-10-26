"""ADMN-PTNR-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-PTNR-001.md
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
# 파트너 전용 화면 — common-snb.js를 로드하지 않는다. 개발 표시 파일은 common-master.js 바로 뒤에 둔다
DEV_MAP = {
    "code": "ADMN-PTNR-001",
    "devCommit": DEV_COMMIT,
    "progress": "개발 미구현(dev-progress에 ADMN-PTNR 없음) — 이름은 (규칙). 학습 Q&A 처리(admin.study-qnas.*) · 강사/조교 범위 제한(instructorScope)만 기존 기능",
    "menus": [
        {"route": "admin.partner-center.index (규칙)", "label": "파트너 센터"},
        {"route": "admin.study-qnas.index", "label": "학습 Q&A 관리(기존 — 강사 · 조교는 본인 강사 건만)"},
    ],
}
OPS.append(dict(kind="insert_after", anchor='<script id="v4-common-master" src="common-master.js"></script>\n', html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

B = A + "/partner-center"
RT = "admin.partner-center"

# ── 모달 · 버튼 id → 개발 id(규칙) ───────────────────────
RENAME_ID("modalQnaDetail", "layerStudyQnaAnswer", 3)
RENAME_ID("btnQnaSubmit", "studyQnaAnswerSubmit", 2)
RENAME_ID("btnTaxSubmit", "taxDocumentSubmit", 1)

# ── 메뉴(탭 = 하위 자원) ───────────────────────────────
for tab, route, url in (
    ("home", RT + ".index (규칙)", B),
    ("stmt", RT + ".statements.index (규칙)", B + "/statements"),
    ("qna", RT + ".study-qnas.index (규칙)", B + "/study-qnas"),
    ("tax", RT + ".tax-documents.index (규칙)", B + "/tax-documents"),
    ("me", RT + ".profile.show (규칙)", B + "/profile"),
):
    R(f'data-tab="{tab}" ', f'data-tab="{tab}"' + attrs(flag="proto-only", route=route, method="GET", url=url, perm="조회") + ' ', 1)

# ── 본인 정산서 ──────────────────────────────────────
NAME("stmtMonth", "month", value="YYYY-MM = settlement_lines.target_month")
ACT("shiftStmtMonth", count=2, flag="proto-only", route=RT + ".statements.index (규칙)", method="GET", url=B + "/statements?month=", perm="조회")
R("onclick=\"viewStatementMonth(\\'", attrs(flag="proto-only", route=RT + ".statements.index (규칙)", method="GET", url=B + "/statements?month=", perm="조회").lstrip() + " onclick=\"viewStatementMonth(\\'")
ACT("downloadStatementPdf", flag="proto-only", route=RT + ".statements.download (규칙)", method="GET", url=B + "/statements/download", perm="다운로드",
    note="관리자 화면 규칙과 같게 하면 사유(공통 #layerReason) — 정산서 열은 settlement_lines taxable_base · vat_amount · withholding_income_tax · offset_amount · payable_amount")

# ── 학습 Q&A ────────────────────────────────────────
NAME("qnaCourseFilter", "course_id", note="(규칙)")
NAME("qnaStatusFilter", "status", value="pending 미답변 · answered 답변완료 · escalated 강사확인 (프로토타입 값 WAIT · DONE · HOLD 유지)")
R('<option value="HOLD">보류</option>', '<option value="HOLD" data-dev-flag="proto-only" data-dev-note="개발 StudyQna 상태에 보류 없음(가까운 값 escalated 강사확인) — 정책 질문 D-SETT">보류</option>')
ACT("resetQnaFilter", flag="proto-only", route=RT + ".study-qnas.index (규칙)", method="GET", url=B + "/study-qnas", perm="조회")
R("onclick=\"openQnaModal(\\'", attrs(route="admin.study-qnas.show", method="GET", url=A + "/study-qnas/{studyQna}", perm="조회",
                                      note="파트너 센터 경로는 (규칙) admin.partner-center.study-qnas.show — 기존 관리자 Q&A 재사용 가능").lstrip() + " onclick=\"openQnaModal(\\'")
NAME("qnaAnswerInput", "answer_content", note="StudyQnaProcessRequest — action=answer면 10자 이상")
ACT("submitQnaAnswer", route="admin.study-qnas.update", method="PUT", url=A + "/study-qnas/{studyQna}", perm="수정",
    note="action=answer + answer_content · is_public_qna · notify — 파트너 센터 경로는 (규칙) admin.partner-center.study-qnas.update")
ACT("holdQna", route="admin.study-qnas.update", method="PUT", url=A + "/study-qnas/{studyQna}", perm="수정",
    note="보류 대응 값 없음 — 가장 가까운 action=escalate(강사확인). 정책 질문 D-SETT")
# 개발 Q&A 처리 옵션(공개 여부 · 답변 알림) — 모달 바닥 위에 정본 디자인(.ptnr-modal-foot 줄)으로 추가
R('<div class="ptnr-modal-foot">',
  '<div class="ptnr-modal-foot" data-dev-flag="dev-only" data-dev-note="개발 StudyQnaProcessRequest is_public_qna · notify(기본 ON)" style="justify-content:flex-start; border-bottom:0;">\n'
  '      <label style="display:flex; align-items:center; gap:6px; font-size:12.5px;"><input type="checkbox" name="is_public_qna" value="1" /> 공개 Q&amp;A로 게시</label>\n'
  '      <label style="display:flex; align-items:center; gap:6px; font-size:12.5px;"><input type="checkbox" name="notify" value="1" checked /> 답변 알림 보내기</label>\n'
  '    </div>\n'
  '    <div class="ptnr-modal-foot">')

# ── 세금계산서 · 증빙 제출 ─────────────────────────────
R("onclick=\"openTaxForm(\\'", attrs(flag="proto-only", note="대상 정산서 settlement_month (규칙)").lstrip() + " onclick=\"openTaxForm(\\'")
NAME("tiApproval", "approval_no", note="(규칙)")
NAME("tiDate", "issued_date", note="(규칙)")
NAME("tiSupply", "supply_amount", note="(규칙) settlement_lines.supply_amount와 같은 이름")
NAME("tiVat", "vat_amount", note="(규칙) settlement_lines.vat_amount와 같은 이름")
NAME("tiFile", "file", note="(규칙) PDF")
ACT("submitTaxDoc", flag="proto-only", route=RT + ".tax-documents.store (규칙)", method="POST", url=B + "/tax-documents", perm="등록",
    note="저장 테이블 없음 — 이름 규칙상 tax_document_submissions (규칙)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("홈", "switchPtnrTab('home')", "#tab-home"),
    ("본인 정산서", "switchPtnrTab('stmt')", "#tab-stmt"),
    ("학습 Q&A", "switchPtnrTab('qna')", "#tab-qna"),
    ("Q&A 답변 모달", "switchPtnrTab('qna'); openQnaModal('LQ-2610-0418')", "#layerStudyQnaAnswer|#modalQnaDetail"),
    ("세금계산서 · 증빙", "switchPtnrTab('tax')", "#tab-tax"),
    ("내 정보", "switchPtnrTab('me')", "#tab-me"),
]
