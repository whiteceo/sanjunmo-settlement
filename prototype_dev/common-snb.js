/* v5.6 코드뿐인 괄호 제거 — 치환표 적용 전에 실행 (clean 전용) */
(function () {
  if (window.__wfStripCodeParens) return;
  var ADMN = /^(?:ADMN-)?[A-Z]{2,5}-\d{3}(?:-[A-Z0-9]+)?(?:\/\d{3})?$/;
  var USNAKE = /^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$/;
  var LSNAKE = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$/;
  var CODEKEY = /^[A-Z0-9_\-\/]+$/;
  var cache = new WeakMap();
  function keySet(src) {
    if (!src || typeof src !== "object") return null;
    if (cache.has(src)) return cache.get(src);
    var arr = Array.isArray(src)
      ? src.map(function (r) { return Array.isArray(r) ? r[0] : r; })
      : Object.keys(src);
    var s = new Set(arr.filter(function (k) {
      return typeof k === "string" && k.length >= 4 && /[A-Z]/.test(k) && CODEKEY.test(k);
    }));
    cache.set(src, s);
    return s;
  }
  function isCode(inner, src) {
    var parts = inner.replace(/[`'"]/g, "").split(/\s*[·,]\s*|\s+\/\s+/);
    var ks = keySet(src);
    return parts.length > 0 && parts.every(function (p) {
      p = p.trim();
      return !!p && (ADMN.test(p) || USNAKE.test(p) || LSNAKE.test(p) || (ks && ks.has(p)));
    });
  }
  var PAREN = /\s*\(\s*([^()]{2,80}?)\s*\)/g;
  var CODE_OUT = /\b(?:ADMN-)?[A-Z]{2,5}-\d{3}(?:-S\d+)?\s*\(\s*([^()]{2,40}?)\s*\)/g;
  var LEAD = /[가-힣A-Za-z0-9%)\]]\s*$/;
  window.__wfStripCodeParens = function (str, src) {
    if (!str || typeof str !== "string" || str.indexOf("(") === -1) return str; str = str.replace(CODE_OUT, function (m, inner) { return /[가-힣]/.test(inner) && !isCode(inner, src) ? inner : m; });
    return str.replace(PAREN, function (m, inner, off, whole) {
      var pre = whole.slice(0, off); if (pre.trim() && !LEAD.test(pre)) return m;
      return isCode(inner, src) ? "" : m;
    });
  };
  window.__wfStripCodeElParens = function (root, src) {
    if (!root || !root.querySelectorAll) return;
    var els = root.querySelectorAll("code,strong,b,small");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      // id가 있는 요소는 스크립트가 값을 채우는 자리라 지우지 않는다(예: LOGIN-001 #lockout-account — v6.75)
      if (el.classList.contains("raw-keep") || el.children.length || el.id) continue;
      var prev = el.previousSibling, next = el.nextSibling;
      if (!prev || !next || prev.nodeType !== 3 || next.nodeType !== 3) continue;
      if (!/\(\s*$/.test(prev.nodeValue) || !/^\s*\)/.test(next.nodeValue)) continue;
      var before = prev.nodeValue.replace(/\s*\(\s*$/, "");
      if (before.trim() && !LEAD.test(before)) continue;
      if (!isCode(el.textContent.trim(), src)) continue;
      prev.nodeValue = before;
      next.nodeValue = next.nodeValue.replace(/^\s*\)/, "");
      el.parentNode.removeChild(el);
    }
  };
})();

/**
 * SANJUNMO BACKOFFICE v8.4 FINAL — MASTER SNB INJECTOR (common-snb.js)
 */
(function () {
  const SNB_GROUPS = [
    {
      title: "대시보드 · 통계",
      items: [
        { code: "GUIDE", label: "전체 업무 플로우 가이드", href: "00_WORKFLOW_GUIDE_baseline.html", screenCode: "WORKFLOW-GUIDE" },
        { code: "DASH-001", label: "통합 대시보드 홈 (현황·큐·연동)", href: "ADMN-DASH-001_baseline.html?view=dash", screenCode: "ADMN-DASH-001" },
        { code: "STAT-001", label: "매출 · 상품 통계 (결제·환불·순위)", href: "ADMN-DASH-001_baseline.html?view=stat-sales", screenCode: "ADMN-STAT-001" },
        { code: "LOGIN-001", label: "관리자 · 파트너 로그인 게이트", href: "ADMN-LOGIN-001_baseline.html", screenCode: "ADMN-LOGIN-001" }
      ]
    },
    {
      title: "회원 · 수강 관리",
      items: [
        { code: "USER-001", label: "일반 회원 관리 (목록·상세)", href: "ADMN-USER-001_baseline.html?view=list", screenCode: "ADMN-USER-001" },
        { code: "USER-003", label: "회원 수강 · 기간 · 기기 제어", href: "ADMN-USER-001_baseline.html?view=course", screenCode: "ADMN-USER-003" },
        { code: "USER-006", label: "회원 그룹 · 다중 태그 관리", href: "ADMN-USER-001_baseline.html?view=tags", screenCode: "ADMN-USER-006" },
        { code: "USER-005", label: "블랙리스트 · 부정사용 제재 관리", href: "ADMN-USER-001_baseline.html?view=blacklist", screenCode: "ADMN-USER-005" },
      ]
    },
    {
      title: "주문 · 환불 · CS · 프로모션",
      items: [
        { code: "ORD-001", label: "주문 · 배송 · 3PL 관리", href: "ADMN-ORD-001_baseline.html" },
        { code: "RFD-002", label: "환불 요청 · 심사 관리", href: "ADMN-RFD-002_baseline.html" },
        { code: "BRD-002", label: "1:1 문의 관리 (문의 분기 허브)", href: "ADMN-BRD-002_baseline.html", screenCode: "ADMN-BRD-002" },
        { code: "BRD-007", label: "1:1 문의 분류 관리", href: "ADMN-BRD-007_baseline.html", screenCode: "ADMN-BRD-007" },
        { code: "BRD-001", label: "공지 · FAQ · Q&A · 당첨자 발표", href: "ADMN-BRD-001_baseline.html?view=notice", screenCode: "ADMN-BRD-001" },
        { code: "BRD-005", label: "수강·합격수기 · 무료콘텐츠", href: "ADMN-BRD-005_baseline.html?view=review", screenCode: "ADMN-BRD-005" },
        { code: "PROM-001", label: "이벤트 · 기획전 관리 (Slug·특가)", href: "ADMN-PROM-001_baseline.html", screenCode: "ADMN-PROM-001" },
        { code: "PROM-002", label: "쿠폰 마스터 등록 · 발급 관리", href: "ADMN-PROM-002_baseline.html?view=list", screenCode: "ADMN-PROM-002" },
        { code: "PROM-003", label: "포인트 적립 정책 및 원장 관리", href: "ADMN-PROM-002_baseline.html?view=point", screenCode: "ADMN-PROM-003" }
      ]
    },
    {
      title: "상품 · 강좌 · 교재 관리",
      items: [
        { code: "PROD-001", label: "카테고리 관리", href: "ADMN-PROD-001_baseline.html", screenCode: "ADMN-PROD-001" },
        { code: "PROD-002", label: "강의 관리 (영상 단품)", href: "ADMN-PROD-002_baseline.html", screenCode: "ADMN-PROD-002" },
        { code: "PROD-003", label: "단과 강좌 관리", href: "ADMN-PROD-003_baseline.html", screenCode: "ADMN-PROD-003" },
        { code: "PROD-004", label: "교재 관리", href: "ADMN-PROD-004_baseline.html", screenCode: "ADMN-PROD-004" },
        { code: "PROD-005", label: "패키지 · 환급반 상품 관리", href: "ADMN-PROD-005_baseline.html", screenCode: "ADMN-PROD-005" },
        { code: "PROD-006", label: "강사 노출 정보 관리", href: "ADMN-PROD-006_baseline.html", screenCode: "ADMN-PROD-006" },
        { code: "PROD-007", label: "일반상품 관리", href: "ADMN-PROD-007_baseline.html", screenCode: "ADMN-PROD-007" }
      ]
    },
    {
      title: "권리자 · 거래처 · 지분 매핑",
      items: [
        { code: "INST-001", label: "권리자 계약 원장", href: "ADMN-INST-001_baseline.html", screenCode: "ADMN-INST-001" },
        { code: "SETT-007", label: "수취인 분할 관리", href: "ADMN-SETT-007_baseline.html", screenCode: "ADMN-SETT-007" },
        { code: "BOOK-001", label: "도서 공급 원장", href: "ADMN-BOOK-001_baseline.html", screenCode: "ADMN-BOOK-001" },
        { code: "VEND-001", label: "거래처 관리", href: "ADMN-VEND-001_baseline.html", screenCode: "ADMN-VEND-001" },
        { code: "SETT-001", label: "상품별 권리자 매핑", href: "ADMN-SETT-001_baseline.html", screenCode: "ADMN-SETT-001" }
      ]
    },
    {
      title: "정산 마감 전 사전 대사",
      items: [
        { code: "SETT-004", label: "PG 정산 원장 대사", href: "ADMN-SETT-004_baseline.html", screenCode: "ADMN-SETT-004" },
        { code: "SETT-011", label: "물류비 대사 (3PL)", href: "ADMN-SETT-011_baseline.html", screenCode: "ADMN-SETT-011" },
        { code: "INST-002", label: "약정금 마일스톤 검수", href: "ADMN-INST-002_baseline.html", screenCode: "ADMN-INST-002" },
        { code: "SETT-006", label: "합격 환급반 관리", href: "ADMN-SETT-006_baseline.html", screenCode: "ADMN-SETT-006" },
        { code: "SETT-008", label: "사업자등록 확인 이력", href: "ADMN-SETT-008_baseline.html", screenCode: "ADMN-SETT-008" }
      ]
    },
    {
      title: "월간 정산 · 지급 · 조회",
      items: [
        { code: "SETT-002", label: "월간 정산 및 집행", href: "ADMN-SETT-002_baseline.html", screenCode: "ADMN-SETT-002" },
        { code: "SETT-005", label: "정산 수동 조정", href: "ADMN-SETT-005_baseline.html", screenCode: "ADMN-SETT-005" },
        { code: "SETT-009", label: "내부 정산 조회 · 조회 전용", href: "ADMN-SETT-009_baseline.html", screenCode: "ADMN-SETT-009" }
      ]
    },
    {
      title: "권한 · 개인정보 · 보안 감사",
      items: [
        { code: "CONF-005", label: "운영자 권한 관리 (계정 · 역할 그룹)", href: "ADMN-CONF-005_baseline.html", screenCode: "ADMN-CONF-005" },
        { code: "USER-007", label: "민감 정보 열람 통제", href: "ADMN-USER-007_baseline.html", screenCode: "ADMN-USER-007" },
        { code: "CONF-010", label: "시스템 감사 로그", href: "ADMN-CONF-010_baseline.html", screenCode: "ADMN-CONF-010" },
      ]
    },
    {
      title: "사이트 · 약관 · 메시지 설정",
      items: [
        { code: "CONF-001", label: "전시 배너 · 띠배너 · 팝업 관리", href: "ADMN-CONF-001_baseline.html?view=banner", screenCode: "ADMN-CONF-001" },
        { code: "CONF-002", label: "약관 · 개인정보처리방침 관리", href: "ADMN-CONF-002_baseline.html", screenCode: "ADMN-CONF-002" },
        { code: "CONF-003", label: "플레이어 · 동시접속 · 인증 설정", href: "ADMN-CONF-003_baseline.html?view=player", screenCode: "ADMN-CONF-003" },
        { code: "CONF-004", label: "메시지 템플릿 관리 (알림톡·문자·메일)", href: "ADMN-CONF-004_baseline.html?view=template", screenCode: "ADMN-CONF-004" },
        { code: "CONF-004-S1", label: "타겟 메시지 발송 · 내역", href: "ADMN-CONF-004_baseline.html?view=send", screenCode: "ADMN-CONF-004-S1" }
      ]
    }
  ];

  function buildSnbHtml(currentFileWithQuery, currentFileOnly) {
    const groupsHtml = SNB_GROUPS.map(group => {
      const itemsHtml = group.items.map(item => {
        // 1순위: 파일명 + 쿼리스트링 완전 일치 (?view=course 등)
        // 2순위: 쿼리가 없는 일반 페이지의 경우 파일명 일치
        // 3순위: screenCode 부분 일치
        let isActive = false;
        if (item.href.indexOf("?") !== -1) {
          isActive = (currentFileWithQuery === item.href);
          // 쿼리 없이 들어온 경우 list 기본 매칭
          if (!isActive && currentFileWithQuery === item.href.split("?")[0] && item.href.indexOf("view=list") !== -1) {
            isActive = true;
          }
        } else {
          isActive = (currentFileOnly === item.href || (currentFileOnly && currentFileOnly.indexOf(item.screenCode) !== -1));
        }

        return `
        <a href="${item.href}" class="snb-item${isActive ? ' active' : ''}" data-screen-code="${item.screenCode}">
          <span class="snb-code">${item.code}</span>
          <span class="snb-label">${item.label}</span>
        </a>`;
      }).join("");
      return `
      <div class="snb-group">
        <div class="snb-group-title">${group.title || group.groupTitle}</div>
        <div class="snb-item-list">${itemsHtml}</div>
      </div>`;
    }).join("");

    return `
    <div class="snb-brand" onclick="window.location.href='00_WORKFLOW_GUIDE_baseline.html'">
      <div class="snb-brand-top">
        <div class="snb-brand-title">
          <img class="snb-brand-logo" src="img/sjm_logo-horizontal-white.png" alt="산준모">
          <span>백오피스</span>
        </div>
        <span class="snb-version-pill">v4.0.0</span>
      </div>
      <div class="snb-brand-sub">산준모닷컴 통합 관리자 센터</div>
    </div>
    <div class="snb-scroll-area">${groupsHtml}</div>
    <div class="snb-footer">
      <span>PROD &amp; SETTLEMENT</span>
      <span>SSOT Verified</span>
    </div>`;
  }

  function initMasterSnb() {
    const pathParts = window.location.pathname.replace(/\\/g, "/").split("/");
    const currentFileOnly = decodeURIComponent(pathParts[pathParts.length - 1] || "");
    const currentFileWithQuery = currentFileOnly + window.location.search;

    let snbEl = document.getElementById("v4-master-snb");
    if (!snbEl) {
      snbEl = document.createElement("aside");
      snbEl.id = "v4-master-snb";
      snbEl.setAttribute("role", "navigation");
      snbEl.setAttribute("aria-label", "산준모 마스터 사이드바");
      document.body.insertBefore(snbEl, document.body.firstChild);
    }
    snbEl.innerHTML = buildSnbHtml(currentFileWithQuery, currentFileOnly);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMasterSnb);
  } else {
    initMasterSnb();
  }
})();


/* === [PROTOTYPE-CLEAN: DOM TEXT-NODE ONLY TRANSLATOR (ZERO CODE MUTATION)] === */
(function () {
  // 1) 긴 구문부터 먼저 치환하여 동어반복("권리자 계약 원장 ([권리자 계약 원장])") 원천 방지
  const TEXT_REPLACEMENTS = [
    // 동어반복 방지를 위한 복합 문구 우선 치환
    ["권리자 계약 원장 (ADMN-INST-001)", "권리자 계약 원장"],
    ["권리자 계약 원장(ADMN-INST-001)", "권리자 계약 원장"],
    ["도서 공급 원장 (ADMN-BOOK-001)", "도서 공급 원장"],
    ["도서 공급 원장(ADMN-BOOK-001)", "도서 공급 원장"],
    ["상품별 권리자 매핑 (ADMN-SETT-001)", "상품별 권리자 매핑"],
    ["상품별 권리자 매핑(ADMN-SETT-001)", "상품별 권리자 매핑"],
    ["월간 정산(ADMN-SETT-002)", "월간 정산"],
    ["정산 원장(ADMN-SETT-002)", "월간 정산 원장"],
    ["정산 원장(SETT-002)", "월간 정산 원장"],
    ["감사 로그(ADMN-CONF-010)", "시스템 감사 로그"],
    ["수동 무상 포인트 지급/차감 (002-P1)", "수동 포인트 지급 · 차감"],
    ["엑셀 다운로드 (001-P1)", "엑셀 다운로드"],
    ["이월 발생 내역 원장 (ADMN-SETT-002-P1)", "이월 발생 내역 원장"],
    ["통합 정산서 상세·마감 (S1)", "통합 정산서 상세 · 마감"],
    ["상세·마감 워크스페이스 (S1)", "통합 정산서 상세"],
    ["권리자 제공 정산서 (S2)", "권리자 제공 정산서"],
    ["권리자 정산서 (S2)", "권리자 정산서"],
    ["합격 심사 (S1)", "합격 증빙 심사"],
    ["1. 환불 요청 목록 (RFD-004)", "환불 요청 목록"],
    ["2. 합격환급반 심사 (RFD-001)", "합격환급반 심사"],
    ["3. 환불 처리 상세 (RFD-002)", "환불 처리 상세"],
    ["4. 환불 완료 내역 (RFD-003)", "환불 완료 내역"],
    ["1. 주문 내역 관리 (ORD-001)", "주문 내역 관리"],
    ["2. 3PL 배송·출고·반품검수 (ORD-002)", "3PL 배송 · 출고 · 반품검수"],
    ["3. 주문 상세 · 배송지 Lock (ORD-001-S1)", "주문 상세 · 배송지 관리"],
    ["수강권 직권 부여 (0원 주문 · 구 ORD-003)", "수강권 직권 부여 (0원 주문)"],
    ["3PL 물류 격리 (ROLE_PARTNER_3PL)", "3PL 물류 파트너 뷰"],
    ["빈출특강 (FREQ_EXAM)", "빈출특강"],
    ["무료특강 영상 (FREE_LECTURE)", "무료특강 영상"],
    ["빈출문제 해설 (FREQ_EXAM)", "빈출문제 해설"],
    ["정산 매핑 (SETT-001)", "정산 지분 매핑"],
    ["권리자 지분 매핑 (SETT-001)", "권리자 지분 매핑"],
    ["공급원가(BOOK-001)", "공급원가"],
    ["합격수기 검수 (BRD-005)", "합격수기 검수"],
    ["BRD-005 검수완료 (우수)", "검수 완료 (우수)"],
    ["옵션 B (강사 50% 분담 · SETT-006 C-01)", "강사 50% 분담 약정"],
    ["차월 전기오류수정 대기 (SETT-005)", "차월 정산 반영 대기"],
    ["재무 권한(FIN_MANAGER) 시뮬레이션 (사입원가 열람)", "재무 담당자 원가 표시"],
    ["재무/정산책임자 (FIN_MANAGER)", "재무/정산 책임자"],
    ["매입 재판매 (PURCHASED_RESALE)", "매입 재판매"],
    ["자사 직접 판매 (DIRECT_SALE)", "자사 직접 제작·판매"],
    ["OWN_PUBLISHED (자사발행 인세 · Pipeline 2.1)", "자사발행 도서 (인세)"],
    ["OWN_PUBLISHED (자사발행)", "자사 발행 도서"],
    ["OWN_PUBLISHED (자사저작권)", "자사 저작권 도서"],
    ["CONSIGNMENT (위탁 판매 · Pipeline 2.2)", "위탁 판매 도서"],
    ["CONSIGNMENT (위탁판매)", "위탁 판매 도서"],
    ["PURCHASED_RESALE (사입)", "매입 재판매 도서"],
    ["BUNDLED (강좌포함 비매품)", "강좌 포함 비매품"],
    ["CONDITIONAL (상계 허용 · v4.0.0)", "상계 허용"],
    ["NON_OFFSET (비상계 보장)", "비상계 보장 (MMG)"],
    ["원인 미분류 불일치 (UNKNOWN_MISMATCH)", "원인 미분류 불일치"],
    ["UNKNOWN_MISMATCH (미분류)", "원인 미분류 불일치"],
    ["TIMING_GAP (기간 귀속차)", "기간 귀속 차이 (월말·월초)"],
    ["PARTIAL_CANCEL_PENDING (부분취소 대기)", "부분취소 처리 대기"],
    ["PG_FEE_DIFF (PG 수수료 차감차)", "PG 수수료 차액"],
    ["REFUND_TIMING_DIFF (환불 처리 시차)", "환불 처리 시차"],
    ["계약 중 (ACTIVE)", "계약 중"],
    ["작성 중 (DRAFT)", "작성 중"],
    ["만료 / 해지 (EXPIRED · TERMINATED)", "만료 / 해지"],
    ["정상 (ACTIVE)", "정상"],
    ["정상 활성 (ACTIVE)", "정상 활성"],
    ["잠김/중지 (LOCKED)", "잠김 / 중지"],
    ["[내부] 최고관리자 (ROLE_SUPER_ADMIN)", "[내부] 최고관리자"],
    ["[내부] 정산/재무 담당 (ROLE_FINANCE_ADMIN)", "[내부] 정산 · 재무 담당자"],
    ["[내부] 정산/재무 관리자 (ROLE_FINANCE_ADMIN)", "[내부] 정산 · 재무 관리자"],
    ["[내부] 서비스/콘텐츠 운영 (ROLE_OPS_ADMIN)", "[내부] 서비스 · 콘텐츠 운영자"],
    ["[내부] 서비스/콘텐츠 운영자 (ROLE_OPS_ADMIN)", "[내부] 서비스 · 콘텐츠 운영자"],
    ["[내부] 고객센터 CS 전담 (ROLE_CS_ADMIN)", "[내부] 고객센터(CS) 담당자"],
    ["[파트너] 강사 전용 (ROLE_PARTNER_INST)", "[파트너] 강사 전용 계정"],
    ["[파트너] 교재 저작권자 (ROLE_PARTNER_COPYRIGHT)", "[파트너] 교재 저작권자 계정"],
    ["[파트너] 외부 물류 3PL (ROLE_PARTNER_3PL)", "[파트너] 외부 물류(3PL) 계정"],
    ["시연 권한", "열람 권한"],
    ["국세청 진위 확인 · 모의", "국세청 진위 확인"],
    ["휴업자 저장 예외 승인 · 모의", "휴업자 예외 승인"],
    ["세무 판정 상태 · 시연", "세무 판정 상태"],
    ["🧪 QA D-13 시연: 은행 계좌오류 송금 실패 시뮬레이션", "⚠️ 이체 실패(계좌오류) 재처리 테스트"],
    ["[P1 시연] 정액 250,000원 초과 입력", "한도 초과 입력 테스트 (250,000원)"],
    ["[P1 시연] 정률 45% 초과 입력", "한도 초과 입력 테스트 (45%)"],
    // 단독 코드 치환
    ["USER-PROM-001", "프론트 이벤트/기획전"],
    ["USER-CS-001", "프론트 공지사항"],
    ["USER-CS-002", "프론트 FAQ"],
    ["USER-LECT-002-S1", "프론트 강좌상세"],
    ["USER-LECT-002", "프론트 강좌상세"],
    ["USER-CRS-002", "프론트 강좌상세"],
    ["USER-MY-003", "내 강의실"],
    ["USER-MY-007", "내 쿠폰함"],
    ["USER-PAY-001", "주문/결제서"],
    ["USER-FREE-001", "무료특강"],
    ["USER-INST-001", "강사 소개"],
    ["USER-JOIN-002", "회원가입 화면"],
    ["USER-INFO-001", "하단 푸터"],
    ["ADMN-SETT-001", "상품별 권리자 매핑"],
    ["ADMN-SETT-002-S1", "통합 정산서 원장"],
    ["ADMN-SETT-002-S2", "권리자 정산내역서"],
    ["ADMN-SETT-002-P1", "이월 내역 원장"],
    ["ADMN-SETT-002", "월간 정산 관리"],
    ["ADMN-SETT-004", "PG 정산 대사"],
    ["ADMN-SETT-005", "정산 수동 조정"],
    ["ADMN-SETT-006", "합격환급반 정산"],
    ["ADMN-SETT-007", "수취인 분할 관리"],
    ["ADMN-SETT-008", "사업자 과세유형 확인"],
    ["ADMN-SETT-009", "내부 정산 조회"],
    ["ADMN-SETT-011", "물류비 대사(3PL)"],
    ["ADMN-INST-001", "권리자 계약 원장"],
    ["ADMN-INST-002", "약정금 마일스톤 검수"],
    ["ADMN-BOOK-001", "도서 공급 원장"],
    ["ADMN-VEND-001", "거래처 관리"],
    ["ADMN-ORD-001", "통합 주문 관리"],
    ["ADMN-ORD-002", "배송·3PL 관리"],
    ["ADMN-RFD-002", "환불 심사 관리"],
    ["ADMN-USER-001", "회원 목록"],
    ["ADMN-USER-002", "회원 상세"],
    ["ADMN-USER-003", "수강·기기 제어"],
    ["ADMN-USER-005", "블랙리스트 관리"],
    ["ADMN-USER-006", "그룹·태그 관리"],
    ["ADMN-USER-007", "민감정보 열람통제"],
    ["ADMN-PROM-001", "이벤트·기획전 관리"],
    ["ADMN-PROM-002", "쿠폰 마스터 관리"],
    ["ADMN-PROM-003", "포인트 원장 관리"],
    ["ADMN-BRD-001", "공지사항 관리"],
    ["ADMN-BRD-002", "1:1 문의 허브"],
    ["ADMN-BRD-003", "상품 Q&A 관리"],
    ["ADMN-BRD-005", "후기·무료콘텐츠"],
    ["ADMN-BRD-009", "당첨자 발표 관리"],
    ["ADMN-CONF-004-S1", "타겟 메시지 발송"],
    ["ADMN-CONF-004", "메시지 템플릿 관리"],
    ["ADMN-CONF-010", "시스템 감사로그"],
    ["Pipeline 1.1", "강좌 수익배분"],
    ["Pipeline 2.1", "자사발행 도서 인세"],
    ["Pipeline 2.2", "위탁 도서 판매대금"],
    ["Pipeline 2.3", "일반상품 매출"],
    ["Pipeline 5.1", "매출연동 개발지원금"],
    ["— 산준모 백오피스 v4.0.0", "— 산준모 관리자 센터"],
    ["— 산준모닷컴 백오피스 v8.4 Final", "— 산준모 관리자 센터"],
    ["— 산준모닷컴 백오피스 v8.4 FINAL", "— 산준모 관리자 센터"],
    ["— 산준모닷컴 백오피스", "— 산준모 관리자 센터"],
    // 권한(ROLE) 코드 번역
    ["ROLE_SUPER_ADMIN", "최고 관리자"],
    ["ROLE_MASTER_ADMIN", "최고 관리자"],
    ["ROLE_FINANCE_DIRECTOR", "재무 총괄 책임자"],
    ["ROLE_FINANCE_ADMIN", "재무/정산 담당자"],
    ["ROLE_SETT_ADMIN", "정산 관리자"],
    ["ROLE_OPS_ADMIN", "서비스 운영자"],
    ["ROLE_CS_ADMIN", "고객센터 담당자"],
    ["ROLE_PARTNER_INST", "강사/학원 파트너"],
    ["ROLE_PARTNER_COPYRIGHT", "저작권 파트너"],
    ["ROLE_PARTNER_3PL", "물류(3PL) 파트너"],
    ["ROLE_STUDENT", "일반 회원"],
    // 미등록 화면 코드 번역
    ["ADMN-STAT-001", "매출·정산 통계"],
    ["ADMN-DASH-001", "대시보드"],
    ["ADMN-CONF-001-S1", "약관 개정 이력"],
    ["ADMN-CONF-001-S2", "신규 약관 등록"],
    ["ADMN-CONF-001", "배너/팝업 관리"],
    ["ADMN-CONF-002", "약관/개인정보 관리"],
    ["ADMN-CONF-003", "시스템 환경설정"],
    ["ADMN-CONF-005", "관리자 권한 관리"],
    ["ADMN-CONF-008", "환경설정 연동"],
    ["ADMN-LOGIN-001-P1", "2차 인증 OTP"],
    ["ADMN-LOGIN-001", "관리자 로그인"],
    ["ADMN-LOGIN-002", "비밀번호 재설정"],
    ["ADMN-LOGIN-003", "계정 잠금 해제"],
    ["ADMN-BRD-004", "학습 Q&A 관리"],
    ["ADMN-BRD-006", "FAQ 관리"],
    ["ADMN-BRD-007", "1:1 문의 분류 관리"],
    ["ADMN-BRD-010", "무료콘텐츠"],
    // 기술 파라미터 및 DB 컬럼명
    ["tax_type", "과세유형"],
    ["utcc_yn", "확인여부"],
    ["origin_settlement_id", "참조 정산서 ID"],
    ["origin_month", "원 발생 귀속월"],
    ["applied_month", "반영 기준월"],
    ["adj_reason_code", "조정 사유 구분"],
    ["adj_account_type", "이월/반영 계정"],
    ["adj_tax_type", "과·면세 구분"],
    ["adj_explanation", "조정 소명 내용"]
  ];

  const REGEX_CLEANERS = [
    // [ADMN-...] 또는 [Term-...] 또는 [테이블 A~G] 또는 [8.3절...] 대괄호 태그 제거
    /\[\s*(?:ADMN-[A-Z]+-\d+[^\]]*|Term-[A-Z]+|테이블\s*[A-G]|(?:제?\d+장|\d+(?:\.\d+)?절|부록)[^\]]*)\]\s*/g,
    // (ADMN-...), (SETT-001), (001-P1), (S1), (P2) 등 화면코드 괄호 제거
    /\s*\(\s*(?:ADMN-|USER-)?(?:SETT|INST|BOOK|PROD|ORD|RFD|USER|PROM|BRD|CONF|DASH|STAT|CRS|MY|FREE|LECT)-\d+(?:-[A-Z0-9]+)?[^)]*\)/g,
    /\s*\(\s*(?:\d{3}-[SP]\d+|[SP]\d+)\s*\)/g,
    // (6.5절 · 8.3절), (제15장 15.2절), (Case 7), (부록 D-15) 등 기획서 장/절/케이스 괄호 제거
    /\s*\(\s*(?:합의서\s*)?(?:제?\d+장\s*)?\d+(?:\.\d+)?절[^)]*\)/g,
    /\s*·\s*\d+(?:\.\d+)?절/g,
    /\s*\(\s*(?:Case\s*\d+[^)]*|부록\s*[A-Z][^)]*|QA\s*D-\d+[^)]*)\)/gi,
    // (member_status), (goods_stock_log), (own_copyright_yn) 등 영문 snake_case DB 컬럼 괄호 제거
    // — 컬럼 꼴 접미사로 끝나는 것만 지운다. 회원 아이디(safe_choi 등)처럼 운영자가 봐야 하는 값은 남긴다(v6.68)
    /\s*\(\s*(?:[a-z]+_[a-z0-9]+_[a-z0-9_]+|[a-z]+(?:_[a-z0-9]+)*_(?:yn|cd|code|status|state|type|log|id|at|date|dt|amount|amt|rate|ratio|flag|key|no|cnt|count|basis|scope|policy|method|category|clause|base|total|balance|limit|reason|unit|mode|channel|account|ledger|snapshot|history|treatment|owner|price|qty))(?:\s*=\s*[^)]+)?\s*\)/g,
    // Table: xxx 배지 텍스트 제거
    /^\s*Table:\s*[a-z0-9_]+\s*$/i,
    // 잔여 화면코드 접두사 및 기술 코드 제거
    /\b(?:ADMN|USER)-[A-Z]+-\d+(?:-[A-Z0-9]+)?\b/g,
    /\bROLE_[A-Z0-9_]+\b/g,
    /\b[a-z]+_(?:yn|type|status|mode|limit|flag|scope)\b/g
  ];

  function transformText(str) {
    if (!str || typeof str !== "string" || !str.trim()) return str;
    let out = str;
    out = window.__wfStripCodeParens(out, TEXT_REPLACEMENTS);
    for (let i = 0; i < TEXT_REPLACEMENTS.length; i++) {
      const target = TEXT_REPLACEMENTS[i][0];
      if (out.indexOf(target) !== -1) {
        out = out.split(target).join(TEXT_REPLACEMENTS[i][1]);
      }
    }
    for (let j = 0; j < REGEX_CLEANERS.length; j++) {
      out = out.replace(REGEX_CLEANERS[j], "");
    }
    return out;
  }

  function walkAndClean(root) {
    if (!root) return;
    window.__wfStripCodeElParens(root, TEXT_REPLACEMENTS);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    let node;
    while ((node = walker.nextNode())) {
      const p = node.parentNode;
      if (!p) continue;
      const tag = p.tagName;
      // 코드/스타일/입력창 내부 텍스트는 절대 건드리지 않음
      if (tag === "SCRIPT" || tag === "STYLE" || tag === "TEXTAREA" || tag === "CODE" && p.classList.contains("raw-keep")) continue;
      textNodes.push(node);
    }
    for (let i = 0; i < textNodes.length; i++) {
      const orig = textNodes[i].nodeValue;
      const cleaned = transformText(orig);
      if (cleaned !== orig) {
        textNodes[i].nodeValue = cleaned;
      }
    }
    if (document.title) {
      const ct = transformText(document.title);
      if (ct !== document.title) document.title = ct;
    }
  }

  function startSafeCleaner() {
    walkAndClean(document.body);
    let pending = false;
    const obs = new MutationObserver(function () {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () {
        pending = false;
        walkAndClean(document.body);
      });
    });
    obs.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startSafeCleaner);
  } else {
    startSafeCleaner();
  }
})();

/* [PHASE1_CLEAN_ENHANCEMENT_V4] */
(function enhanceCleanDomTranslator() {
  const EXTRA_MAP = {
  "CARRY_IN": "전월 이월 승계",
  "ACCRUAL": "순 발생액 산출",
  "MMG_ADJ": "월 보장액 보정",
  "DEDUCT": "환불·할인 공제",
  "SUPPORT_CAP": "지원금 한도 캡",
  "PREPAY_OFFSET": "선급금 상한선 상계",
  "LUMPSUM_ADD": "비정기 약정·매절 가산",
  "PAYEE_SPLIT": "수취인 분할",
  "CLAIM": "반환·최소 청구 검증",
  "PAYOUT": "최소 지급 검증·대량이체 확정",
  "UNKNOWN_MISMATCH": "원인 미분류 불일치",
  "REVENUE_SHARE": "매출 비례 정산",
  "LUMP_SUM": "일시금",
  "LUMP_SETTLE": "종료 일시정산",
  "PRO_RATA": "이행률 비례 정산",
  "ACCOUNT_TRANSFER": "계정 간 대체",
  "NON_OFFSET": "비상계 순수 지원",
  "CONDITIONAL": "조건부 상계 허용",
  "UNCONDITIONAL": "무조건 상계 허용",
  "FORBIDDEN": "상계 불가",
  "PENDING_REVIEW": "판정 보류(검토 대기)",
  "PRE_TAX": "세전 이월",
  "POST_TAX": "세후 이월",
  "CONSIGNMENT_BAL": "위탁 도서 잔액",
  "VAT_EXCLUDED": "부가세 별도",
  "VAT_INCLUDED": "부가세 포함",
  "NET_DEDUCT": "수수료 차감지급",
  "OWN_PUBLISHED": "자사발행 도서",
  "PURCHASED_RESALE": "매입 재판매",
  "ROYALTY_BOOK": "인세 도서",
  "DIRECT_SALE": "자사 직접 판매",
  "INVENTORY_PURCHASE": "재고 매입",
  "GOODS_ITEM": "일반상품(굿즈)",
  "SHIPPING_FEE": "배송비",
  "MARKETING_EXPENSE": "판촉비",
  "CONTRACT_LINKED": "계약 종료일 연동",
  "CLAIMED_ON_TERMINATION": "중도해지 반환청구",
  "TOTAL_AGREED": "총 약정액 기준",
  "DIRECT_GRANT": "수강권 직권부여",
  "ORDER_TYPE": "주문 유형",
  "SHIPPING_DEDUCT": "반품 회수택배비 차감",
  "PG_DIFF_ADJ": "PG 부분취소 차액 보정",
  "LECTURE_PRORATE_ADJ": "수강일수·진도율 재산정 보정",
  "MINUS_POINT_ADJ": "마이너스 포인트 사후 보정",
  "TIMING_GAP": "기간 귀속 시차",
  "PARTIAL_CANCEL_PENDING": "부분취소 대기",
  "PG_FEE_DIFF": "PG 수수료 차감 차액",
  "REFUND_TIMING_DIFF": "환불 처리 시차",
  "RATE_ERR": "요율 오류",
  "SHARE_ERR": "지분율 오류",
  "REFUND_OMIT": "환불 반영 누락",
  "BOOK_SUPPLY_ERR": "도서 공급형태 오등록",
  "CONSIGN_FEE_ERR": "위탁 수수료율 오류",
  "TAX_TYPE_ERR": "과세유형 오인",
  "PREPAY_OFFSET_ERR": "선급금 상계액 오류",
  "MMG_CALC_ERR": "최저보장 산출 오류",
  "SUPPORT_CAP_ERR": "지원금 한도 판정 오류",
  "WITHHOLDING_RATE_ERR": "원천징수 세율 오류",
  "BOOK_COUNT_DIFF": "도서 확정 판매부수 차이",
  "SPLIT_ERR": "수취인 분할 오류",
  "TARGET_MONTH_ERR": "약정금 귀속월 오류",
  "BUYOUT_INC_ERR": "매절 소득 구분 오류",
  "PG_RECON_ADJ": "대사 차이 정정",
  "SIMPLIFIED_RECEIPT": "간이과세자(영수증발급)",
  "SIMPLIFIED_INVOICE": "간이과세자(세금계산서발급)",
  "NON_PROFIT_ORG": "비영리·고유번호 단체",
  "CLOSED_BY_TRANSITION": "과세전환 종결",
  "CANCELLED_BILLED": "출고회수건 과오청구",
  "EVIDENCE_FILE": "증빙 첨부파일",
  "MANUAL_NOTE": "수기 확인 소명",
  "ADMN_AUDIT_LOG": "시스템 감사 로그",
  "FREE_LECTURE": "무료특강 영상",
  "FREQ_EXAM": "빈출문제 해설",
  "COURSE_REVIEW": "수강후기",
  "PASS_ESSAY": "합격수기",
  "INSPECT_REQ": "카카오 검수중",
  "FIN_MANAGER": "재무·정산책임자",
  "SUPER_ADMIN": "최고관리자",
  "OP_ADMIN": "운영관리자",
  "CS_ADMIN": "CS담당자",
  "LOGIS_ADMIN": "물류담당자",
  "SETT_ADMIN": "정산관리자",
  "ROLE_SUPER_ADMIN": "최고관리자",
  "ROLE_FINANCE_DIRECTOR": "재무 총괄 책임자",
  "ROLE_FINANCE_ADMIN": "재무·정산 관리자",
  "ROLE_OPS_ADMIN": "서비스·콘텐츠 운영자",
  "ROLE_CS_ADMIN": "고객센터 CS 전담",
  "ROLE_CONTENT_ADMIN": "콘텐츠·상품 관리자",
  "ROLE_PARTNER_INST": "파트너 강사",
  "ROLE_PARTNER_COPYRIGHT": "교재 저작권자·출판사",
  "ROLE_PARTNER_3PL": "외부 물류(3PL)",
  "PARTNER_INST": "파트너 강사",
  "PARTNER_3PL": "외부 물류(3PL)",
  "TPL_PAY_DONE": "결제완료 알림톡",
  "PAY_DONE": "결제완료 알림톡",
  "EML_TERMS_NOTICE": "약관개정 안내 메일",
  "TPL_DLV_START": "출고·송장 안내 알림톡",
  "TPL_CS_GUIDE": "고객센터 안내 알림톡",
  "TPL_VBANK_ISSUED": "가상계좌 안내 알림톡",
  "TPL_RFD_DONE": "환불완료 안내 알림톡",
  "order_items": "주문 품목",
  "order_item_id": "주문품목번호",
  "refund_promo_burden_type": "환불·할인 분담유형",
  "origin_month": "원 발생 귀속월",
  "applied_month": "반영 기준월",
  "origin_settlement_id": "참조 원 정산서",
  "adj_reason_code": "조정 사유 코드",
  "adj_account_type": "반영 계정 구분",
  "carryover_ledger": "이월 원장",
  "payment_event_date": "원천징수 성립일",
  "pii_unmask_ttl_seconds": "열람 유지시간",
  "book_price_history": "도서 정가 이력",
  "book_supply_type": "도서 공급형태",
  "book_supply_type_snapshot": "도서 공급형태 스냅샷",
  "book_supply_ledger": "도서 공급 원장",
  "own_copyright_yn": "자사 저작권 여부",
  "effective_from": "적용 시작일",
  "effective_to": "적용 종료일",
  "ship_ordered_at": "출고지시 일시",
  "preview_token": "미리보기 토큰",
  "term_code": "약관 코드",
  "user_agreements": "회원 약관동의 원장",
  "terms_version_history": "약관 버전 이력",
  "is_marketing_agreed": "마케팅 수신동의",
  "before_snapshot_json": "변경 전 스냅샷",
  "after_snapshot_json": "변경 후 스냅샷",
  "contract_status": "계약 상태",
  "contract_id": "적용 계약",
  "end_basis": "매핑 종료 기준",
  "payment_method": "지급 방식",
  "offset_type": "상계 처리 유형",
  "cap_type": "한도 유형",
  "on_termination_policy": "약정 종료 처리 정책",
  "cap_restore_on_refund": "환불 시 한도 복원",
  "agreement_id": "약정 번호",
  "target_month": "귀속월",
  "penalty_calc_type": "위약벌 산정방식",
  "penalty_base": "위약벌 기준금액",
  "paid_amount": "실결제금액",
  "book_discount_rate_limit": "도서 할인율 상한",
  "is_preorder": "예약판매 여부",
  "release_date": "출고 예정일",
  "package_product": "패키지 상품 원장",
  "instructor_display": "강사 노출 원장",
  "goods_supply_type": "상품 공급 형태",
  "is_internal": "자사 귀속 여부",
  "goods_stock_log": "재고 수불 이력",
  "html_content": "HTML 소스",
  "css_content": "CSS 스타일",
  "js_content": "JS 스크립트",
  "user_coupon": "회원 발급 쿠폰",
  "cap_applied": "최대할인 캡 적용",
  "order_discount": "주문 할인 원장",
  "exclude_book": "도서 적용 제외",
  "payment_status": "지급 상태",
  "pg_recon_unclassified_max": "미분류 허용 상한",
  "pg_recon_tolerance_company": "단수차 허용 오차",
  "item_type": "품목 유형",
  "mmg_promo_overlap_flag": "최저보장·환급반 중복 감지",
  "payee_is_author": "저작자 본인 여부",
  "payee_split_base": "2계층 분할 기준",
  "payee_id": "수취인 번호",
  "split_ratio": "분할 지분율",
  "active_contracts": "유효 계약 원장",
  "tax_type_cd": "국세청 과세유형",
  "nts_tax_type_map": "국세청 과세유형 매핑표",
  "nts_check_validity_days": "국세청 조회 유효기간(90일)",
  "nts_batch_chunk_size": "배치 묶음 단위(100건)",
  "nts_batch_interval_ms": "호출 간격(200ms)",
  "nts_retry_max_count": "최대 재시도 횟수(3회)",
  "nts_periodic_check_schedule": "정기 휴폐업 점검 스케줄",
  "tax_type_change_dt": "과세유형 전환일자",
  "book_authors": "도서 저자 매핑",
  "goods_master": "일반상품 마스터",
  "taxable_base": "과세표준",
  "pending_negative_base": "음수 이월 과세표준",
  "income_clause": "기타소득 구분코드",
  "tracking_no": "운송장번호",
  "admin_access_log": "개인정보 접근 감사 로그",
  "is_locked": "계정 잠금 상태",
  "cafe_member_id": "카페 연동 ID",
  "unpaid_points_blacklist": "마이너스 포인트 미납 제재",
  "destruction_hold": "파기 보류 예외",
  "pii_destruction_field_map": "개인정보 파기 기준표",
  "rights_holder_id": "권리자 고유번호",
  "rights_holders": "권리자 원장",
  "rrn_encrypted": "주민등록번호(암호화)",
  "bank_account_enc": "계좌번호(암호화)",
  "holder_name": "권리자 성명",
  "id_cards": "신분증 사본",
  "settlement_statements": "정산서 원장",
  "settlement_recipient_id": "권리자 대체 식별번호"
};
  const MARKER_RE = /\[\s*마커\s*\d+\s*\]\s*/g;
  const CIRCLED_RE = /[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]\s*/g;
  const TRACK_RE = /\bTrack\s+[A-G]\b\s*[:·-]?\s*/gi;

  function cleanString(str) {
    if (!str || typeof str !== 'string') return str;
    let out = str;
    out = window.__wfStripCodeParens(out, EXTRA_MAP);
    for (const [k, v] of Object.entries(EXTRA_MAP)) {
      if (out.includes(k)) out = out.split(k).join(v);
    }
    out = out.replace(MARKER_RE, '').replace(CIRCLED_RE, '').replace(TRACK_RE, '');
    return out;
  }

  function runEnhancedClean(root) {
    if (!root) return;
    window.__wfStripCodeElParens(root, EXTRA_MAP);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
      const parentTag = node.parentNode && node.parentNode.tagName;
      if (parentTag === 'SCRIPT' || parentTag === 'STYLE') continue;
      const cleaned = cleanString(node.nodeValue);
      if (cleaned !== node.nodeValue) node.nodeValue = cleaned;
    }
    if (root.querySelectorAll) {
      root.querySelectorAll('[placeholder],[title],[data-tooltip]').forEach(el => {
        ['placeholder', 'title', 'data-tooltip'].forEach(attr => {
          const val = el.getAttribute(attr);
          if (val) {
            const cleaned = cleanString(val);
            if (cleaned !== val) el.setAttribute(attr, cleaned);
          }
        });
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    runEnhancedClean(document.body);
    let timer = null;
    const observer = new MutationObserver(() => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => runEnhancedClean(document.body), 80);
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();

/* === [UNIVERSAL-MODAL-CLOSER-HOTFIX] === */
(function() {
  if (window.__sjmModalCloserInstalled) return;
  window.__sjmModalCloserInstalled = true;

  function forceCloseModalEl(backdrop) {
    if (!backdrop) return;
    backdrop.classList.remove('show', 'open', 'active');
    backdrop.style.setProperty('display', 'none', 'important');
    backdrop.setAttribute('aria-hidden', 'true');
  }

  function forceOpenModalEl(backdrop) {
    if (!backdrop) return;
    backdrop.classList.remove('force-closed');
    backdrop.classList.add('show');
    backdrop.style.setProperty('display', 'flex', 'important');
    backdrop.setAttribute('aria-hidden', 'false');
  }

  // 전역 헬퍼 등록 (기존 페이지 함수 보강)
  window.closeAllModals = function() {
    document.querySelectorAll('.modal-backdrop, .p1-modal-backdrop, .s1-modal-backdrop, .s2-modal-backdrop, [id*="Modal"], [id*="modal"]').forEach(function(el) {
      if (el.classList.contains('modal-backdrop') || el.classList.contains('p1-modal-backdrop') || el.classList.contains('s1-modal-backdrop') || el.classList.contains('s2-modal-backdrop') || getComputedStyle(el).position === 'fixed') {
        forceCloseModalEl(el);
      }
    });
  };

  // 페이지 로드 후 ADMN-BRD-002 등 고유 모달 열기/닫기 함수 래핑
  window.addEventListener('DOMContentLoaded', function() {
    if (typeof window.closeTransferModal === 'function') {
      var origClose = window.closeTransferModal;
      window.closeTransferModal = function() {
        try { origClose.apply(this, arguments); } catch (e) {}
        window.closeAllModals();
      };
    } else {
      window.closeTransferModal = function() {
        window.closeAllModals();
      };
    }

    if (typeof window.openTransferModal === 'function') {
      var origOpen = window.openTransferModal;
      window.openTransferModal = function() {
        document.querySelectorAll('.modal-backdrop').forEach(function(m) {
          m.style.removeProperty('display');
        });
        try { origOpen.apply(this, arguments); } catch (e) {}
        var modal = document.getElementById('transfer-modal') || document.getElementById('transferModal') || document.getElementById('modal-transfer') || document.querySelector('.modal-backdrop');
        if (modal) forceOpenModalEl(modal);
      };
    }
  });

  // 1) 닫기/취소/X 버튼 및 배경 클릭 시 즉시 닫기 (이벤트 위임)
  document.addEventListener('click', function(e) {
    // (A) 배경(backdrop) 자체를 클릭한 경우
    if (e.target && (
      e.target.classList.contains('modal-backdrop') ||
      e.target.classList.contains('p1-modal-backdrop') ||
      e.target.classList.contains('s1-modal-backdrop') ||
      e.target.classList.contains('s2-modal-backdrop')
    )) {
      forceCloseModalEl(e.target);
      return;
    }

    // (B) 모달 내부의 닫기 버튼(✕, ×, 취소, 닫기, [onclick*="close"]) 클릭 시
    var btn = e.target.closest('button, a, span, [role="button"]');
    if (!btn) return;
    var backdrop = btn.closest('.modal-backdrop, .p1-modal-backdrop, .s1-modal-backdrop, .s2-modal-backdrop');
    if (!backdrop) return;

    var txt = (btn.textContent || '').trim();
    var onclickAttr = (btn.getAttribute('onclick') || '');
    var isCloseBtn = (
      txt === '✕' || txt === '×' || txt === 'X' || txt === 'x' ||
      txt === '취소' || txt === '닫기' || txt === '창 닫기' ||
      onclickAttr.indexOf('close') !== -1 ||
      onclickAttr.indexOf('Close') !== -1 ||
      btn.classList.contains('modal-close') ||
      btn.classList.contains('btn-close')
    );

    if (isCloseBtn) {
      setTimeout(function() {
        forceCloseModalEl(backdrop);
      }, 0);
    }
  }, true);

  // 2) ESC 키 입력 시 열려 있는 모든 모달 닫기
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      window.closeAllModals();
    }
  });
})();

/* =========================================================================
   SJM_PAGE (v6.68) — 하위 화면(S)을 같은 HTML 안의 페이지로 전환하는 공통 도구
   화면설계서 v12가 별도 페이지(S)로 정한 등록 · 상세는 모달이 아니라 이 방식으로 연다.
   사용법 · 함정: scripts/qa/reports/review/findings/PAGE_PATTERN.md
   - 패널: #v4-page-body 안의 <section class="subview-panel" data-subpage="이름">
   - 목록 패널 이름은 'list'(처음부터 active). 상단 화면 코드 · 제목은 목록일 때 원래 값으로 돌아간다.
   - 주소: ?view=이름(&id=…) — 새로 고침 · 다른 화면 링크로 바로 들어오고, 브라우저 뒤로 가기로 목록에 돌아간다.
   ========================================================================= */
(function () {
  var pages = {};
  var base = null;
  var current = 'list';
  var pageKeys = {}; // go()로 주소에 넣은 화면 고유 키(holder 등) — 목록으로 돌아갈 때 함께 지운다

  function crumbEls() {
    return {
      code: document.getElementById('top-crumb-code') || document.querySelector('.top-bar .crumb-code'),
      title: document.querySelector('.top-bar .crumb-title')
    };
  }

  function show(name, params) {
    var def = pages[name];
    if (!def) return false;
    var el = crumbEls();
    // 목록을 떠날 때마다 그 순간의 상단 코드 · 제목을 기억한다 — 탭 묶음 화면은 탭마다 제목이 달라서(v6.68)
    if (!base || (current === 'list' && name !== 'list')) base = { code: el.code ? el.code.textContent : '', title: el.title ? el.title.textContent : '' };
    document.querySelectorAll('#v4-page-body > .subview-panel[data-subpage]').forEach(function (p) {
      p.classList.toggle('active', p.getAttribute('data-subpage') === name);
    });
    // clean: 상단 화면 코드 자리는 화면 이름으로 치환돼 있으므로 그대로 두고 제목만 바꾼다(prototype은 코드도 S 코드로 바꿈)
    if (el.title) el.title.textContent = name === 'list' ? base.title : (typeof def.title === 'function' ? def.title(params || {}) : (def.title || base.title));
    current = name;
    if (typeof def.onShow === 'function') def.onShow(params || {});
    window.scrollTo(0, 0);
    return true;
  }

  function urlFor(name, params) {
    var q = new URLSearchParams(window.location.search);
    ['view', 'id', 'mode'].concat(Object.keys(pageKeys)).forEach(function (k) { q.delete(k); });
    pageKeys = {};
    if (name !== 'list') {
      q.set('view', name);
      Object.keys(params || {}).forEach(function (k) { if (params[k] !== null && params[k] !== undefined && params[k] !== '') { q.set(k, params[k]); pageKeys[k] = true; } });
    }
    var s = q.toString();
    return window.location.pathname + (s ? '?' + s : '') + window.location.hash;
  }

  window.SJM_PAGE = {
    /** 하위 화면 등록: name = data-subpage 값, def = { code: 'ADMN-…-S1', title: '…' 또는 function(params), onShow: function(params) } */
    register: function (name, def) { pages[name] = def || {}; },
    /** 하위 화면으로 이동(주소 기록). opts.replace = 기록 대신 바꾸기 */
    go: function (name, params, opts) {
      if (!show(name, params)) return;
      try {
        var st = { sjmPage: name, params: params || {} };
        if (opts && opts.replace) history.replaceState(st, '', urlFor(name, params));
        else history.pushState(st, '', urlFor(name, params));
      } catch (e) { /* file:// 등에서 주소 기록이 막혀도 화면 전환은 유지 */ }
    },
    /** 목록으로 돌아가기 */
    back: function () { this.go('list'); },
    current: function () { return current; },
    /** 등록이 끝난 뒤 한 번 호출: 목록을 등록하고 ?view= 진입을 처리한다 */
    start: function (listDef) {
      if (!pages.list) pages.list = listDef || {};
      var q = new URLSearchParams(window.location.search);
      var v = q.get('view');
      if (v && pages[v]) {
        var params = {};
        q.forEach(function (val, key) { if (key !== 'view') params[key] = val; });
        this.go(v, params, { replace: true });
        pageKeys = {}; // 직접 진입 주소에 원래 있던 키(role 등)는 목록으로 돌아가도 지우지 않는다
      }
    }
  };

  window.addEventListener('popstate', function (e) {
    var st = e.state;
    if (st && st.sjmPage) show(st.sjmPage, st.params);
    else show('list');
  });
})();

/* =========================================================================
   MODAL-OPEN-GUARD (v6.75) — 모달 열기 근본 수정
   각 화면의 UNIVERSAL-MODAL-CLOSER-HOTFIX는 로드 · 닫기 때 모달 백드롭에 인라인 display:none !important를 건다.
   화면 코드가 클래스(open · show · active)만 붙이거나 hidden만 떼서 여는 경우 그 인라인 값이 남아 모달이 열리지 않았다.
   → 백드롭의 클래스가 '열림'으로 바뀌는 순간 인라인 display를 지운다(화면별 수정 불필요).
   ========================================================================= */
(function () {
  if (window.__sjmModalOpenGuard) return;
  window.__sjmModalOpenGuard = true;
  var SEL = '.modal-backdrop, .p1-modal-backdrop, .s1-modal-backdrop, .s2-modal-backdrop';
  function isOpen(el) { return el.classList.contains('open') || el.classList.contains('show') || el.classList.contains('active'); }
  function release(el) { if (el.style.display === 'none') el.style.removeProperty('display'); el.removeAttribute('aria-hidden'); }
  var mo = new MutationObserver(function (list) {
    list.forEach(function (m) {
      var el = m.target;
      if (!el.matches || !el.matches(SEL)) return;
      var old = ' ' + (m.oldValue || '') + ' ';
      var wasOpen = /\s(open|show|active)\s/.test(old);
      var hiddenRemoved = old.indexOf(' hidden ') !== -1 && !el.classList.contains('hidden');
      if ((isOpen(el) && !wasOpen) || hiddenRemoved) release(el);
    });
  });
  function start() { mo.observe(document.body, { attributes: true, attributeFilter: ['class'], attributeOldValue: true, subtree: true }); }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();

/* ===== SNB-ACCORDION (2026-10-27 white: SNB는 디자인만 프로토타입, 동작은 개발 기준) =====
 * 그룹 제목을 누르면 그 그룹만 펼치는 아코디언, 처음엔 현재 화면 그룹만 펼침, 높이 0.2초 애니메이션.
 * prototype_dev/dev-snb.js와 같은 코드(개발 lcampus/sanjunmo public/admin/assets/js/custom.js '관리자메뉴(좌측)').
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
