"""ADMN-INST-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-INST-001.md
apply_dev_map.py가 읽는다. 각 항목의 기대 건수가 원본과 다르면 전체를 멈춘다.
"""
"""ADMN-USER-001 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-USER-001.md
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


def DA(action, count=1, **kw):
    """data-action="X" 버튼(이 화면은 onclick 대신 data-action 위임)에 개발 속성을 단다"""
    R(f'data-action="{action}"', f'data-action="{action}"' + attrs(**kw), count)


H = A + "/rights-holders/{rightsHolder}"
C = H + "/contracts/{contract}"

# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-INST-001",
    "devCommit": DEV_COMMIT,
    "progress": "구현(권리자 목록 · 등록 · 수정 · 국세청 진위 확인 · 계약 등록/수정/열람 · 메모 · 저서 원장 · 선급 원장 라인 · 상태 동기화 · 엑셀). 탭 4 변경 · 열람 이력 · 업무 외 노무 · 모의 승인 흐름은 개발 미구현, 위탁 조항 · 환급 부담 B · C는 1차 저장 거부 — 주황 표시",
    "menus": [
        {"route": "admin.rights-holders.index", "label": "권리자 계약 원장"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ── 모달 id → 개발 레이어 id ────────────────────────────
RENAME_ID("modalInst001RateLockP1", "layerContractLock", 3)

# ── 상단 도구 · 탭 ──────────────────────────────────
R('id="role"', 'id="role" data-dev-flag="proto-only" data-dev-note="역할 시연 — 개발은 메뉴 권한 + 재무 판정"')
NAME("contractStatus", "status", value="pending 작성 중 · active 계약 중 · expired 만료 · terminated 중도 해지 (프로토 DRAFT · ACTIVE · EXPIRED · TERMINATED)",
     note="상태 변경 확인 layerContractStatus(csIdentifier → confirm_identifier)")
R('data-tab="list">', 'data-tab="list"' + attrs(route="admin.rights-holders.index", method="GET", url=A + "/rights-holders", perm="조회",
                                                note="개발 목록 단위는 권리자(계약은 이력 레이어 layerContractHistory)") + '>')
R('data-tab="contract">', 'data-tab="contract"' + attrs(route="admin.rights-holders.edit + admin.rights-holders.contracts.edit", method="GET",
                                                        url=H + "/edit | " + C + "/edit", perm="수정",
                                                        note="상단 권리자 · 세무 = INST-001-S1, 하단 계약 조건 = INST-001-S2") + '>')
R('data-tab="nts">', 'data-tab="nts"' + attrs(route="admin.rights-holders.edit", method="GET", url=H + "/edit?tab=nts", perm="수정") + '>')
R('data-tab="audit">', 'data-tab="audit"' + attrs(flag="proto-only", route="admin.rights-holders.logs.index (규칙)", method="GET", url=H + "/logs", perm="조회",
                                                  note="변경 · 열람 이력 전용 화면 — 개발 미구현(현재 공통 admin.admin-logs.index)") + '>')

# ── 탭 1 목록 ──────────────────────────────────────
DA("newContractDraft", route="admin.rights-holders.contracts.create", method="GET", url=H + "/contracts/create", perm="등록",
   note="개발은 layerNewContract에서 대상 권리자 선택 → 계약 등록. 신규 권리자는 admin.rights-holders.create")
R('<button class="btn pr" type="button" data-action="newContractDraft"',
  '<button class="btn" type="button" data-dev-flag="dev-only" data-dev-route="admin.rights-holders.status-sync" data-dev-method="POST" data-dev-url="' + A + '/rights-holders/status-sync" data-dev-perm="수정(접미사 예외)" '
  'onclick="toast(\'[개발] 계약 상태 일괄 동기화(만료 반영) — POST /rights-holders/status-sync\')">계약 상태 동기화</button>\n'
  '              <button class="btn" type="button" data-dev-flag="dev-only" data-dev-route="admin.rights-holders.download" data-dev-method="GET" data-dev-url="' + A + '/rights-holders/download" data-dev-perm="다운로드" data-dev-note="사유 레이어 layerReason · 선택 행 ids[]" '
  'onclick="toast(\'[개발] 엑셀 다운로드 — GET /rights-holders/download\')">엑셀 다운로드</button>\n'
  '              <button class="btn pr" type="button" data-action="newContractDraft"')
NAME("clFilterStatus", "contract_status[]", value="pending · active · expired · terminated (첫 진입 pending + active). ALERT는 alert · expiry_soon · tax_pending · api_expired")
NAME("clFilterParty", "holder_types[]", value="개인 · 사업자 · 위탁자 · 자사 권리자 (프로토 CORP · SOLE · PERSON)")
NAME("clSearch", "keyword", note="이름 · 코드 · 계약")
R('<div class="tablewrap" id="contractListTableWrap"></div>',
  '<div class="row c4" style="margin-bottom:12px" data-dev-flag="dev-only" data-dev-note="RightsHolderController.php:35-40 검색 보조 필드">\n'
  '            <div><label class="lbl" for="fBirth">생년월일</label><input class="fc" id="fBirth" name="birth_date" type="date"></div>\n'
  '            <div><label class="lbl" for="fPhone">휴대폰 뒤 4자리</label><input class="fc" id="fPhone" name="phone_tail" maxlength="4"></div>\n'
  '            <div><label class="lbl" for="fTax">세무 유형</label><select class="fc" id="fTax" name="tax_type"><option value="">전체</option><option value="personal">개인(인적용역 3.3%)</option><option value="simplified">간이과세자</option><option value="general">일반과세자</option><option value="exempt">면세사업자</option></select></div>\n'
  '            <div><label class="lbl" for="fValidOn">기준일</label><input class="fc" id="fValidOn" name="valid_on" type="date"></div>\n'
  '          </div>\n\n'
  '          <div class="tablewrap" id="contractListTableWrap"></div>')
R('data-open-contract="${esc(c.id)}">', 'data-open-contract="${esc(c.id)}"' + attrs(route="admin.rights-holders.contracts.edit", method="GET", url=C + "/edit", perm="수정",
                                                                                     note="개발 행 = 권리자 → 계약 이력 레이어(GET admin.rights-holders.contracts, 조회)에서 계약 선택") + '>', 2)
R('onclick="openInst001RateLockModalP1()"', attrs(note="개발 #layerContractLock(_lock-modal) · 상태 변경 #layerContractStatus").lstrip() + ' onclick="openInst001RateLockModalP1()"')

# ── 탭 2 상단: 권리자 · 세무 (INST-001-S1) ──────────────────
DA("backToContractList", route="admin.rights-holders.index", method="GET", url=A + "/rights-holders", perm="조회")
R('<select class="fc" id="quickContractSwitch"', '<select class="fc" id="quickContractSwitch"' + attrs(note="개발 계약 이력 레이어 layerContractHistory(chTitle · chBody · chGoDetail)"))
DEVNAME('name="partyType" value="BUSINESS"', "tax_type", value="simplified · general · exempt (국세청 자동)")
DEVNAME('name="partyType" value="PERSON"', "tax_type", value="personal")
NAME("bizType", "business_subtype", value="SOLE 개인사업자 · CORP 법인·단체 (자사 귀속은 is_internal=1)")
R('</select>\n              </div>\n              <label class="lbl" for="holderName">',
  '</select>\n              </div>\n'
  '              <label class="lbl" for="rightsHolderType" data-dev-flag="dev-only">권리자 구분</label>\n'
  '              <select class="fc" id="rightsHolderType" name="rights_holder_type" data-dev-flag="dev-only" data-dev-note="CONSIGNOR는 사업자만 · 자사와 동시 불가">\n'
  '                <option value="RIGHTS_HOLDER">권리자</option>\n'
  '                <option value="CONSIGNOR">위탁자</option>\n'
  '              </select>\n'
  '              <label class="lbl" for="holderName">')
NAME("holderName", "name", note="max 100")
NAME("payeeAccount", "account_no_enc", note="bank_name · account_no_enc · account_holder (비자사면 필수)")
NAME("accountHolder", "account_holder")
DA("pii", count=2, note="개인정보 열람(마스킹 해제) — 개발 경로 확인 필요")
NAME("bizNumber", "business_number", note="숫자 10자리")
NAME("representative", "ceo_name")
NAME("openingDate", "open_date")
R('id="corpNo"', 'id="corpNo"' + attrs(note="법인등록번호 — 개발 RightsHolderRequest 필드 확인 필요"))
NAME("bizCategory", "biz_category")
NAME("bizItem", "biz_item")
NAME("bizAddress", "biz_address")
DA("verify", count=2, route="admin.rights-holders.nts-verify", method="POST", url=H + "/nts-verify", perm="수정(접미사 예외)")
NAME("residentId", "resident_no_enc", note="개인 · 비자사 · 등록이면 필수 13자리")
NAME("payeeAuthor", "payee_is_author", value="1 본인 · 0 본인 아님")
NAME("settleEmail", "email")
NAME("mobilePhone", "phone")
NAME("homeAddress", "address", note="+ address_detail")
R('id="contactPhone"', 'id="contactPhone"' + attrs(note="담당자 연락처 — 개발 필드 확인 필요"))
R('id="contactEmail"', 'id="contactEmail"' + attrs(note="담당자 이메일 — 개발 필드 확인 필요"))
NAME("invoiceEmail", "tax_email", note="general · exempt면 필수")
NAME("resident", "is_resident", value="1 거주자 · 0 비거주자")
NAME("incomeCategory", "income_category", value="BUSINESS 사업소득 · OTHER 기타소득")
NAME("incomeClause", "income_clause", value="C05 · C15 · C17 · C19 (OTHER면 필수)")
R('id="externalLabor"', 'id="externalLabor" data-dev-flag="proto-only" data-dev-note="업무 외 노무 활용 — 개발 없음"')
NAME("suspendedReason", "suspended_approval_reason", note="max 255")
DA("approveSuspended", flag="proto-only", note="휴업자 저장 예외 승인 모의 — 개발은 suspended_approval_reason 입력만")
NAME("taxDecision", "tax_decision_status", value="PENDING_REVIEW 검토 보류 · DECIDED 판정 완료")
NAME("matrixCase", "matrix_case_id", note="DECIDED면 필수")
NAME("taxDecisionReason", "tax_decision_reason", note="DECIDED면 필수")

# ── 탭 2 하단: 계약 공통 (INST-001-S2) ─────────────────────
R('<b id="currentContractBannerTitle">', '<button class="btn sm" type="button" data-dev-flag="dev-only" data-dev-route="admin.rights-holders.contracts.show" data-dev-method="GET" data-dev-url="' + C + '" data-dev-perm="조회" '
  'onclick="toast(\'[개발] 계약 읽기 전용 열람 — GET /rights-holders/{rightsHolder}/contracts/{contract}\')">열람</button>\n'
  '            <b id="currentContractBannerTitle">')
NAME("contractStart", "started_at")
R('id="currentEndView"', 'id="currentEndView"' + attrs(name="ended_at", note="종료 ≥ 시작"))
NAME("initialEnd", "initial_end_date")
NAME("terminationDate", "terminated_at", note="terminated면 필수 + terminate_reason")
NAME("renewalMode", "auto_extend", value="1 자동 갱신 · 0 수동 종료")
NAME("renewalMonths", "renewal_unit_years", value="1 · 2 · 3 (년)")
NAME("renewalStop", "renewal_stop_yn")
NAME("expiryAlert", "contract_expiry_alert_days", note="1~365")
NAME("minPayout", "min_payout_limit")
NAME("minClaim", "min_claim_limit")
NAME("originType", "origin_type", value="NEW 신규 계약 · SUCCESSION 승계 계약")
NAME("predecessor", "predecessor_contract_id", note="승계면 필수")
NAME("refundBurden", "refund_promo_burden_type", value="A만 저장(1차) — B · C는 표시만(정책 질문 Q-INST001-1)")
R('<option value="B">옵션 B', '<option value="B" data-dev-flag="proto-only" data-dev-note="1차 저장 거부">옵션 B')
R('<option value="C">옵션 C', '<option value="C" data-dev-flag="proto-only" data-dev-note="1차 저장 거부">옵션 C')

# ── 강좌 R/S ──────────────────────────────────────
NAME("onOnline", "term_course_yn")
R('id="basicRateTable"', 'id="basicRateTable"' + attrs(name="rate_lines[n][started_at|ended_at|rate|rate_type|rate_basis|mmg_amount|reason]", value="rate_type BASIC · SUPPORT"))
DA("rate", count=2, note="rate_lines[n] 행 추가 — BASIC 기본 R/S · SUPPORT 지원금 R/S")
NAME("mmgEnabled", "mmg_enabled")
R('id="mmgAnnualCap"', 'id="mmgAnnualCap"' + attrs(note="MMG 연 상한 — 개발은 rate_lines[n][mmg_amount]"))
NAME("vatTreatment", "vat_treatment")
NAME("vatException", "vat_exception_yn")
NAME("vatExceptionReason", "vat_exception_reason")
DA("approveVat", flag="proto-only", note="재무 책임자 승인 모의 — 개발 없음")

# ── 도서 인세 · 저서 원장 ─────────────────────────────
NAME("onRoyalty", "term_book_yn")
NAME("royaltyDefaultRate", "royalty_rate")
NAME("royaltyDefaultBasis", "royalty_basis", value="LIST_PRICE 도서 정가 · ACTUAL_PAID 실구매가(배송비 제외)")
R('id="bookTable"', 'id="bookTable"' + attrs(note="개발 layerBookRoyalty · bookRoyaltyForm — 저서 수정 PUT · 삭제 DELETE …/book-royalties/{bookRoyalty}"))
DA("bookNew", route="admin.rights-holders.contracts.book-royalties.store", method="POST", url=C + "/book-royalties", perm="등록",
   note="임시코드 BK-REQ-YYYY-NNNN + 가제 · 출간 예정일, royalty_rate · royalty_basis")
DA("bookExisting", route="admin.rights-holders.contracts.book-royalties.store", method="POST", url=C + "/book-royalties", perm="등록", note="book_id 지정")

# ── 위탁 ──────────────────────────────────────────
NAME("onConsignment", "term_cons_yn", value="0만 허용(1차 위탁 미개방 — 정책 질문 Q-INST001-2)")
DEVNAME('name="consignmentBasePrice" value="PAID_AMOUNT"', "(위탁 정산 기준가)", value="PAID_AMOUNT", note="위탁 조항 — 1차 저장 제외, 개발 필드 확인 필요")
DEVNAME('name="consignmentBasePrice" value="LIST_PRICE"', "(위탁 정산 기준가)", value="LIST_PRICE")
NAME("consignmentFeeType", "consignment_fee_type", note="위탁 조항 — 1차 저장 제외")
NAME("consignmentRate", "consignment_fee_rate")
NAME("consignmentOverride", "consignment_promo_override_yn")
NAME("returnTracking", "consignment_return_tracking_yn")
NAME("returnOwner", "consignment_return_owner")
NAME("returnDeadline", "consignment_return_deadline_days")

# ── 전속계약금 · 위약 ─────────────────────────────────
NAME("onExclusive", "term_exc_yn")
NAME("exclusiveTotal", "exc_fee_amount")
NAME("exclusiveStart", "exc_service_started_at")
NAME("exclusiveEnd", "exc_service_ended_at")
NAME("exclusiveStructure", "exc_payment_method", value="INSTALLMENT 회차 분할 · LUMP_SUM 일시 지급 (일시면 exc_target_month)")
NAME("exclusiveClawback", "exc_clawback_policy", value="PRO_RATA 잔여기간 일할 · FULL 전액 · NONE 없음")
R('id="exclusiveIncome"', 'id="exclusiveIncome"' + attrs(note="전속계약금 소득 구분 — 개발 필드 확인 필요"))
DA("approveExclusiveIncome", flag="proto-only", note="재무 책임자 승인 모의 — 개발 없음")
DA("milestone", count=2, note="exc_rows[n][title|target_month|amount] · dev_rows[n] 회차 행 추가(INST-002 검수 대상 contract_milestones)")
DA("clawback", flag="proto-only", note="중도해지 일할 반환 산출 — 개발 없음")
NAME("penaltyEnabled", "exc_penalty_clause_yn")
NAME("penaltyMethod", "exc_penalty_calc_type", value="배율 · 정액")
NAME("penaltyRate", "exc_penalty_multiple_rate")
NAME("penaltyFixed", "exc_penalty_fixed_amount")
NAME("penaltyBasis", "exc_penalty_base", value="약정 총액 · 기 지급액")
NAME("penaltyRelation", "exc_penalty_clawback_relation", value="위약금에 포함 · 반환과 별도 병과")
NAME("penaltyTrigger", "exc_penalty_trigger_text")
NAME("penaltyConsent", "exc_penalty_offset_consent_yn")

# ── 개발지원금 ─────────────────────────────────────
NAME("onDevelopment", "term_dev_yn")
NAME("supportMethod", "dev_payment_method", value="REVENUE_SHARE 매출 쉐어 · INSTALLMENT 확정금액 분할 · LUMP_SUM 일시금")
NAME("supportOffset", "dev_offset_type", value="CONDITIONAL 상계 허용(기본) · NON_OFFSET 비상계")
NAME("supportCapType", "dev_cap_type", value="CAPPED · UNLIMITED")
NAME("supportCap", "dev_total_cap_amount")
R('id="supportRateTable"', 'id="supportRateTable"' + attrs(name="dev_rate_basis", value="SAME_AS_BASIC · NET_PG · CUSTOM (SUPPORT 라인)"))
NAME("supportEndBasis", "dev_end_basis", value="FIXED_DATE 지정일 · CONTRACT_LINKED 모계약 연동")
NAME("supportEndDate", "dev_end_month")
NAME("supportScope", "dev_lecture_scope", note="dev_lecture_* · dev_book_* 약정 대상(전체 · 선택)")
R('id="supportTargets"', 'id="supportTargets"' + attrs(name="dev_*_targets[]"))
NAME("supportRestore", "dev_cap_restore")
NAME("supportTerminationPolicy", "dev_termination_policy")
R('id="supportFixed"', 'id="supportFixed"' + attrs(name="dev_total_amount · dev_auto_split"))
R('id="supportSchedule"', 'id="supportSchedule"' + attrs(name="dev_rows[] · dev_lump_*"))
R('id="supportAgreement"', 'id="supportAgreement"' + attrs(note="지원금 약정 식별자 자동(support_fund_agreements)"))
DA("mapping", count=3, note="약정 대상 선택 → dev_*_targets[] · buyout_*_targets[] (1계층 매핑 자체는 SETT-001 admin.settlement.rights-mapping.index)")

# ── 매절 · 수당 · 선급 ────────────────────────────────
NAME("onBuyout", "term_buyout_yn")
NAME("buyoutAmount", "buyout_amount")
NAME("buyoutUntil", "buyout_target_month")
NAME("buyoutScope", "buyout_rights_scope")
R('id="buyoutTargets"', 'id="buyoutTargets"' + attrs(name="buyout_*_targets[]"))
NAME("buyoutIncome", "buyout_income")
NAME("onAllowance", "term_etc_yn")
NAME("allowanceType", "etc_amount_type", value="FIXED 정액 · PER_UNIT 건당")
NAME("allowanceUnit", "etc_unit_price")
R('id="allowanceTable"', 'id="allowanceTable"' + attrs(name="etc_rows[]"))
DA("allowance", note="etc_rows[n] 행 추가")
NAME("onAdvance", "term_adv_yn")
NAME("advanceNature", "adv_nature")
NAME("advanceTarget", "adv_offset_target", note="+ adv_payee_type · adv_offset_payee_id")
R('id="advanceTable"', 'id="advanceTable"' + attrs(note="선급 원장 prepayment_ledgers · prepayment_ledger_lines"))
DA("advance", route="admin.rights-holders.contracts.prepayment-lines.store", method="POST", url=C + "/prepayment-lines", perm="등록",
   note="수정은 PUT …/prepayment-lines/{prepaymentLine} (admin.rights-holders.contracts.prepayment-lines.update) — advLineForm")
DA("split", flag="proto-only", note="분할 상태 시연 — 개발 없음")
DA("payeeLink", note="수취인 연결 — 수취인 분할(SETT-007 PayeeSplitController)")
DA("payeeNew", route="admin.rights-holders.create", method="GET", url=A + "/rights-holders/create", perm="등록", note="신규 수취인 권리자 등록")

# ── 증빙 · 메모 · 저장 ────────────────────────────────
R('id="evidenceTable"', 'id="evidenceTable"' + attrs(name="evidences[n][evidence_type|file_name] · docs[] · deleted_*", note="증빙 50건 · 파일 10MB"))
DA("evidence", note="개발 evidenceModal(_evidence-modal) — 계약 저장(contracts.update)에 함께 전송")
NAME("memoText", "memo", note="RightsHolderContractMemoRequest — memoForm")
DA("memo", route="admin.rights-holders.contracts.memos.store", method="POST", url=C + "/memos", perm="등록")
DA("snapshot", note="최근 저장 내용 보기 — 개발 대응 확인 필요")
DA("validation", note="개발 #layerInstValidation(_savebar)")
DA("save", route="admin.rights-holders.contracts.update", method="PUT", url=C, perm="수정",
   note="RightsHolderContractRequest — 권리자 · 세무는 PUT " + H + " (admin.rights-holders.update)")

# ── 검증(check_dev_screen.py): (라벨, 실행할 JS, 보여야 할 선택자 — '|'로 여럿) ──
VERIFY = [
    ("탭 1 목록", "document.getElementById('tab-list').click()", "#page-list"),
    ("탭 2 계약 상세", "document.getElementById('tab-contract').click()", "#page-contract"),
    ("탭 3 국세청 이력", "document.getElementById('tab-nts').click()", "#page-nts"),
    ("탭 4 변경 · 열람 이력", "document.getElementById('tab-audit').click()", "#page-audit"),
    ("목록 행 → 계약 상세", "document.getElementById('tab-list').click(); document.querySelector('[data-open-contract]').click()", "#page-contract"),
    ("P1 요율 잠금 안내", "document.getElementById('tab-list').click(); openInst001RateLockModalP1()", "#layerContractLock|#modalInst001RateLockP1"),
    ("요율 라인 모달", "document.getElementById('tab-contract').click(); document.querySelector('[data-action=\"rate\"][data-kind=\"BASIC\"]').click()", "#modalBack"),
    ("P2 검증 상세", "document.getElementById('tab-contract').click(); document.querySelector('[data-action=\"validation\"]').click()", "#modalBack"),
    ("증빙 모달", "document.getElementById('tab-contract').click(); document.querySelector('[data-action=\"evidence\"]').click()", "#modalBack"),
]
