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
        { code: "BRD-005", label: "수강·합격수기 · 무료특강(빈출)", href: "ADMN-BRD-005_baseline.html?view=review", screenCode: "ADMN-BRD-005" },
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
      <div class="snb-brand-sub">상품 · 권리자 · 정산 통합 어드민</div>
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
    if (el.code) el.code.textContent = name === 'list' ? base.code : (def.code || base.code);
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
