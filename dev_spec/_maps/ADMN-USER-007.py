"""ADMN-USER-007 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-USER-007.md
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


def ACTX(head, count=1, **kw):
    """onclick="<head> 앞에 개발 속성을 단다 — 같은 함수를 인자 · 문구로 구분할 때"""
    R(f'onclick="{head}', attrs(**kw).lstrip() + f' onclick="{head}', count)


def ALERT(prefix, count=1, **kw):
    """alert 버튼은 문구 앞부분으로 구분한다"""
    ACTX(f"alert('{prefix}", count, **kw)


def NAME(id_, name, value=None, note=None):
    """JS가 id로 찾는 입력 — 실제 name 속성을 개발 이름으로 넣는다"""
    R(f'id="{id_}"', f'id="{id_}" name="{name}"' + attrs(value=value, note=note), 1)


def DEVNAME(find, name, value=None, note=None, count=1):
    """JS가 name · value에 기대는 라디오 등 — data-dev-name · data-dev-value만 단다"""
    R(find, find + attrs(name=name, value=value, note=note), count)


def RENAME_ID(old, new, count):
    """id 와 그 참조(getElementById · 문자열)를 모두 바꾼다"""
    RE(r"(?<![\w-])" + old.replace("-", r"\-") + r"(?![\w-])", new, count)


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-USER-007",
    "devCommit": DEV_COMMIT,
    "progress": "미구현(규칙 기반 명명). 개발에 있는 것은 마스킹 해제 API(admin.masking.unmask) · 비공개 첨부 다운로드 · 관리자 로그뿐 — 나머지 주황 표시",
    "menus": [
        {"route": "admin.pii-records.index (규칙)", "label": "민감 정보 열람 통제"},
        {"route": "admin.admin-logs.index", "label": "관리자 로그 (열람 이력 원본)"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 · 입력 id → 개발 id ─────────────────────────────
RENAME_ID("unmaskReasonModal", "layerReason", 4)
RENAME_ID("docViewerModal", "layerDocViewer", 5)
RENAME_ID("modal-pii-destruction-result", "layerPiiDestructionResult", 3)
RENAME_ID("unmaskReasonInput", "reasonEtc", 5)
RENAME_ID("btnConfirmUnmask", "reasonSubmit", 2)
RENAME_ID("reasonCharCount", "reasonEtcCount", 2)
RENAME_ID("modalTargetSummary", "reasonLead", 2)
RENAME_ID("holderTypeFilter", "piiHolderType", 2)
RENAME_ID("kpiUnmaskedCount", "piiUnmaskedCount", 2)
RENAME_ID("kpiDestructCandidate", "piiDestructCandidateCount", 2)

# ── 상단 버튼 · 탭 ───────────────────────────────────
ACT("maskAllNow", flag="proto-only", route="admin.masking.grants.destroy (규칙)", method="DELETE", url=A + "/masking/grants", perm="메뉴 권한 밖(본인 세션 해제 기록)",
    note="개발은 화면 타이머(maskedScheduleRemask)로만 다시 가림 — id (규칙) remaskAllButton")
ACT("goNav", route="admin.admin-logs.index", method="GET", url=A + "/admin-logs?type=unmask", perm="조회(관리자 로그 메뉴)")
ACTX("switchTab('vault')", count=3, flag="proto-only", route="admin.pii-records.index (규칙)", method="GET", url=A + "/pii-records", perm="조회")
ACTX("switchTab('retention')", count=3, flag="proto-only", route="admin.pii-records.retention.index (규칙)", method="GET", url=A + "/pii-records/retention", perm="조회")
ACTX("switchTab('fieldmap')", flag="proto-only", route="admin.pii-records.field-maps.index (규칙)", method="GET", url=A + "/pii-records/field-maps", perm="조회",
     note="열람 이력 표는 admin.pii-records.access-logs.index (규칙) — 데이터는 admin_logs(sub_action unmask · download)")

# ── 탭1 금고 ────────────────────────────────────────
NAME("piiHolderType", "target_type", note="(규칙) + holder_type personal · business · consignor · internal — 폼 id (규칙) piiRecordSearchForm")
DEVNAME('<option value="ALL">전체 수취 주체', "target_type", value="(전체)")
DEVNAME('<option value="INDIVIDUAL"', "target_type", value="rights_holder + holder_type=personal")
DEVNAME('<option value="BIZ"', "target_type", value="rights_holder + holder_type=business")
DEVNAME('<option value="REFUND"', "target_type", value="refund_claim")
ACTX("requestUnmask('${r.id}', 'UNMASK')", route="admin.masking.unmask", method="POST", url=A + "/masking/unmask", perm="메뉴 권한 밖(canUnmask = 최고관리자)",
     note="개발은 필드마다 1회 호출: field = resident_no_enc · account_no_enc (프로토는 한 번에 둘 다) · target_type · target_id · level=high · TTL 30초 상수")
ACTX("requestUnmask('${r.id}', 'DOC')", route="admin.attachments.download", method="GET", url=A + "/attachments/{attachment}/download", perm="대상 메뉴 조회(admin.rights-holders.index)",
     note="개발은 사유 없이 기록만(sub_action=download) · S3 임시 URL 300초 — 사유 전달 ?reason=&reason_etc=&reason_ref= 는 (규칙)")

# ── 열람 사유 모달(공용 layerReason) ─────────────────────
ACT("setQuickReason", count=4, note="프로토 칩은 문장을 채움 — 개발은 정형 사유 reason(ReasonRequest::REASONS) 선택")
R('      <div>\n        <label style="font-weight:800; font-size:12.5px; display:flex; justify-content:space-between;">',
  '      <div style="display:flex; gap:8px; margin-bottom:10px;"' + attrs(flag="dev-only", note="개발 공용 사유 모달 reasonSelect(name reason) · reasonRef(name reason_ref) — 상세 10자 칸은 정본대로 유지") + '>\n'
  '        <select id="reasonSelect" name="reason" class="select" style="flex:1;">'
  '<option value="settlement_check">정산 · 지급 확인</option><option value="refund_account">환불 계좌 확인</option>'
  '<option value="identity_check">본인 확인 요청</option><option value="payment_inquiry">결제 오류 조사</option>'
  '<option value="delivery_error">배송 오류 확인</option><option value="legal_request">법적 요청 대응</option>'
  '<option value="etc">기타(직접 입력)</option></select>\n'
  '        <input type="text" id="reasonRef" name="reason_ref" class="input" maxlength="50" placeholder="근거 번호 (선택)" style="width:160px;" />\n'
  '      </div>\n'
  '      <div>\n        <label style="font-weight:800; font-size:12.5px; display:flex; justify-content:space-between;">')
R('<textarea id="reasonEtc"', '<textarea id="reasonEtc" name="reason_etc" data-dev-note="개발 reason=etc일 때 10~150자 — 정본은 모든 해제에 10자"')
ACT("confirmUnmaskAction", route="admin.masking.unmask", method="POST", url=A + "/masking/unmask", perm="메뉴 권한 밖(canUnmask)",
    note="응답 {success, value, level, ttl} — 로그 적재 실패 시 원문 미반환(500), 복호화 실패 422, TTL 만료 재조회 410")
ACT("closeUnmaskModal", count=2)

# ── 탭2 보존 · 파기 ─────────────────────────────────
ACT("approveTier1Destruction", flag="proto-only", route="admin.pii-records.retention.destruction.store (규칙)", method="POST",
    url=A + "/pii-records/retention/{rightsHolder}/destruction", perm="등록",
    note="reason(MemberReasonRequest) · fields[] — 확인 레이어 (규칙) layerPiiDestruction. 보류는 admin.pii-records.retention.hold.update (규칙) destruction_hold · hold_reason")
ALERT("[국세청 감사 증빙 다운로드]", flag="proto-only", route="admin.pii-records.destructions.download (규칙)", method="GET",
      url=A + "/pii-records/destructions/{batch}/download", perm="다운로드")
ACT("closeDestructionResultModal", count=2)

# ── 탭3 필드 매핑 · 이름이 다른 컬럼 ─────────────────────
R('<td class="code">rights_holders.rrn_encrypted</td>', '<td class="code" data-dev-note="프로토 이름 rights_holders.rrn_encrypted">rights_holders.resident_no_enc</td>')
R('<td class="code">rights_holders.bank_account_enc</td>', '<td class="code" data-dev-note="프로토 이름 rights_holders.bank_account_enc">rights_holders.account_no_enc</td>')
R('<td class="code">rights_holders.holder_name</td>', '<td class="code" data-dev-note="프로토 이름 rights_holders.holder_name">rights_holders.name</td>')
R('<td class="code">s3://private-bucket/id_cards/*</td>', '<td class="code" data-dev-note="개발 attachments(disk secure, attachable rights_holder)">s3://private-bucket/id_cards/*</td>')
R('(`ADMN_AUDIT_LOG` 실시간 적재 내역)', '(`admin_logs` 실시간 적재 내역)')

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("보존 탭", "switchTab('retention')", "#tabPanel-retention"),
    ("매핑 탭", "switchTab('fieldmap')", "#tabPanel-fieldmap"),
    ("금고 탭", "switchTab('fieldmap'); switchTab('vault')", "#tabPanel-vault"),
    ("열람 사유 모달", "switchTab('vault'); document.querySelector(\"[onclick*=\\\"'UNMASK'\\\"]\").click()", "#layerReason|#unmaskReasonModal"),
    ("증빙 사유 모달", "switchTab('vault'); document.querySelector(\"[onclick*=\\\"'DOC'\\\"]\").click()", "#layerReason|#unmaskReasonModal"),
    ("P2 파기 결과", "switchTab('retention'); document.querySelectorAll('.modal-backdrop').forEach(m => m.style.removeProperty('display')); openDestructionResultModal()", "#layerPiiDestructionResult|#modal-pii-destruction-result"),
]
