/**
 * SANJUNMO BACKOFFICE — 공통 기준정보 (common-master.js)
 *
 * 역할 그룹 · 1:1 문의 분류는 고정값이 아니라 운영 중 관리 화면에서 바뀌는 변수 데이터다.
 *   - 역할 그룹(권한 묶음)      : 운영자 권한 관리 (ADMN-CONF-005)
 *   - 1:1 문의 분류(라우팅)     : 1:1 문의 분류 관리 (ADMN-BRD-007)
 *   - 거래처 · 거래처 유형      : 거래처 관리 (ADMN-VEND-001)
 *   - 권리자 원장 요약(읽기 전용): 원천은 권리자 계약 원장 (ADMN-INST-001)
 * 아래 SEED는 최초 기본값일 뿐이다. 다른 화면은 이름을 직접 적지 말고 이 목록을 읽는다.
 * 프로토타입에서는 관리 화면에서 바꾼 값을 브라우저 localStorage에 저장해 다른 화면이 같은 값을 읽게 한다
 * (실서비스에서는 서버 기준정보 API가 이 역할을 한다).
 */
(function () {
  if (window.SJM_MASTER) return;

  function clone(o) { return JSON.parse(JSON.stringify(o)); }

  function store(key, seed) {
    var data = null;
    try {
      var s = window.localStorage.getItem(key);
      if (s) data = JSON.parse(s);
    } catch (e) {}
    if (!data) data = clone(seed);
    return {
      get: function () { return data; },
      set: function (v) {
        data = v;
        try { window.localStorage.setItem(key, JSON.stringify(v)); } catch (e) {}
      },
      reset: function () {
        data = clone(seed);
        try { window.localStorage.removeItem(key); } catch (e) {}
      }
    };
  }

  // 권한 매트릭스의 메뉴 축 — 메뉴(화면) 구성은 시스템이 정하고, 역할 그룹별 읽기(R) · 쓰기(W) · 엑셀(X) 값만 운영에서 바꾼다
  var MENUS = [
    { key: "dash", label: "운영 현황 대시보드", screens: "DASH-001" },
    { key: "stat", label: "매출 · 상품 통계", screens: "STAT-001" },
    { key: "user", label: "회원 · 수강 관리", screens: "USER-001~006" },
    { key: "order", label: "주문 · 배송 관리", screens: "ORD-001" },
    { key: "shipout", label: "출고 지시 · 송장 업로드", screens: "ORD-001 (출고 지시 · 송장)" },
    { key: "refund", label: "환불 요청 · 심사", screens: "RFD-002" },
    { key: "inquiry", label: "1:1 문의 · 공지 · FAQ · 후기", screens: "BRD-001 · 002 · 005 (후기)" },
    { key: "pqna", label: "상품 Q&A", screens: "BRD-003" },
    { key: "lqna", label: "학습 Q&A", screens: "BRD-004 · PTNR-001 (학습 Q&A)" },
    { key: "freecon", label: "무료 콘텐츠 · 교재 정답지", screens: "BRD-005 (무료특강) · BRD-010" },
    { key: "promo", label: "이벤트 · 쿠폰 · 포인트", screens: "PROM-001 · 002 · 003" },
    { key: "product", label: "상품 · 강좌 · 교재", screens: "PROD-001~007" },
    { key: "contract", label: "권리자 계약 · 지분 매핑", screens: "INST-001 · SETT-001 · 007 · BOOK-001" },
    { key: "vendor", label: "거래처 관리", screens: "VEND-001" },
    { key: "presettle", label: "정산 마감 전 사전 대사", screens: "SETT-004 · 011 · 008 · INST-002" },
    { key: "refundpass", label: "합격 환급반 관리 · 서류 보완", screens: "SETT-006" },
    { key: "settle", label: "월간 정산 · 지급 · 조회", screens: "SETT-002 · 005 · 009" },
    { key: "statement", label: "본인 정산서 확인 · 세금계산서 제출", screens: "SETT-002-S2 · PTNR-001" },
    { key: "privacy", label: "민감 정보 · 시스템 감사 로그", screens: "USER-007 · CONF-010" },
    { key: "site", label: "사이트 · 약관 · 메시지 설정", screens: "CONF-001~004" },
    { key: "inqcat", label: "1:1 문의 분류", screens: "BRD-007" },
    { key: "rbac", label: "운영자 권한 관리", screens: "CONF-005" }
  ];

  var ALL = {};
  MENUS.forEach(function (m) { ALL[m.key] = "RWX"; });

  // 역할 그룹 최초값 — 화면설계서 v12 예시 6종 + README 외부 파트너 2종(2026-10-22). 이름 · 구성 · 권한은 운영 중 바뀐다
  // side: INTERNAL 내부 관리자 / EXTERNAL 외부 계정, queue: 1:1 문의 담당 부서 큐로 선택 가능 여부
  // dashArea: 대시보드 기본 영역(맨 위에 펼침) — ALL 전체 · SALES 매출 · 성과 · CS CS · 회원 · LOGI 물류 · SETTLE 정산 · SYS 시스템 · 보안 · NONE 대시보드 미사용. CONF-005에서 그룹별로 바꾸는 변수(v6.53)
  // startScreen: 로그인 후 시작 화면(운영자가 CONF-005에서 그룹별로 바꾸는 변수). 착지 순서: 원래 가려던 화면 → 비밀번호 변경 → 시작 화면,
  // aff: 이 그룹을 줄 수 있는 계정 소속 종류(STAFF 내부 직원 / RH 권리자 / VENDOR 거래처) — 없으면 CONF-005가 side로만 검사
  var ROLE_SEED = [
    { id: "RG-01", name: "최고 관리자", side: "INTERNAL", queue: false, aff: ["STAFF"], on: true, order: 1, dashArea: "ALL", startScreen: { code: "ADMN-DASH-001", label: "운영 현황 대시보드", url: "ADMN-DASH-001_baseline.html?view=dash" },
      desc: "전 메뉴 · 권한 · 감사 관리", perms: ALL },
    { id: "RG-02", name: "CS담당자", side: "INTERNAL", queue: true, aff: ["STAFF"], on: true, order: 2, dashArea: "CS", startScreen: { code: "ADMN-DASH-001", label: "운영 현황 대시보드", url: "ADMN-DASH-001_baseline.html?view=dash" },
      desc: "회원 응대 · 1:1 문의 · 환불 접수",
      perms: { dash: "R", user: "RW", order: "RW", refund: "RW", inquiry: "RW", pqna: "RW", lqna: "R", freecon: "RW", refundpass: "RW", promo: "R", product: "R" } },
    { id: "RG-03", name: "물류팀", side: "INTERNAL", queue: true, aff: ["STAFF"], on: true, order: 3, dashArea: "LOGI", startScreen: { code: "ADMN-DASH-001", label: "운영 현황 대시보드", url: "ADMN-DASH-001_baseline.html?view=dash" },
      desc: "출고 지시 · 송장 · 반품 검수",
      perms: { dash: "R", order: "RW", shipout: "RWX", refund: "R", inquiry: "RW", pqna: "RW", product: "R" } },
    { id: "RG-04", name: "재무팀", side: "INTERNAL", queue: true, aff: ["STAFF"], on: true, order: 4, dashArea: "SETTLE", startScreen: { code: "ADMN-DASH-001", label: "운영 현황 대시보드", url: "ADMN-DASH-001_baseline.html?view=dash" },
      desc: "환불 승인 · 지급 · 정산 · 세무",
      perms: { dash: "R", stat: "RX", user: "R", order: "R", refund: "RWX", product: "R", inquiry: "RW", contract: "RWX", vendor: "RWX", presettle: "RWX", refundpass: "RWX", settle: "RWX", privacy: "RW" } },
    { id: "RG-05", name: "강사", side: "EXTERNAL", queue: true, aff: ["RH"], on: true, order: 5, dashArea: "NONE", startScreen: { code: "ADMN-PTNR-001", label: "파트너 센터", url: "ADMN-PTNR-001_baseline.html?role=RG-05" },
      desc: "본인 강좌 학습 Q&A 답변 · 본인 정산서 확인",
      perms: { lqna: "RW", statement: "RW" } },
    { id: "RG-06", name: "조교", side: "INTERNAL", queue: true, aff: ["STAFF"], on: true, order: 6, dashArea: "NONE", startScreen: { code: "ADMN-BRD-001", label: "학습 Q&A 관리", url: "ADMN-BRD-001_baseline.html?view=qna" },
      desc: "소속 강사 강좌 학습 Q&A · 상품 Q&A 내용 오류 답변",
      perms: { lqna: "RW", pqna: "RW", freecon: "RW" } },
    { id: "RG-07", name: "저작권자", side: "EXTERNAL", queue: false, aff: ["RH"], on: true, order: 7, dashArea: "NONE", startScreen: { code: "ADMN-PTNR-001", label: "파트너 센터", url: "ADMN-PTNR-001_baseline.html?role=RG-07" },
      desc: "본인 도서 인세 정산서 확인 · 세금계산서 제출",
      perms: { statement: "RW" } },
    { id: "RG-08", name: "외부 3PL", side: "EXTERNAL", queue: false, aff: ["VENDOR"], on: true, order: 8, dashArea: "NONE", startScreen: { code: "ADMN-ORD-001", label: "출고 · 송장", url: "ADMN-ORD-001_baseline.html?view=ord002&role=ROLE_PARTNER_3PL" },
      desc: "출고 대상 조회 · 송장 업로드 (금액 비노출)",
      perms: { shipout: "RW" } }
  ];

  // 1:1 문의 분류 최초값 — 담당 부서 큐(depts)는 역할 그룹 ID로 가리킨다(그룹 이름이 바뀌어도 연결 유지)
  var MAJOR_SEED = [
    { prefix: "PAY", name: "결제 · 환불", on: true },
    { prefix: "SHIP", name: "배송 · 교재", on: true },
    { prefix: "LECT", name: "수강 · 기기", on: true },
    { prefix: "PASS", name: "합격환급 · 혜택", on: true },
    { prefix: "STUDY", name: "학습 · 자료", on: true },
    { prefix: "ETC", name: "회원 · 기타", on: true }
  ];
  var CAT_SEED = [
    { code: "VOC-PAY-01", major: "PAY", name: "카드 · 간편결제 취소", screen: "ADMN-RFD-002-S1", depts: ["RG-04"], on: true, order: 1 },
    { code: "VOC-PAY-02", major: "PAY", name: "가상계좌 · 무통장 입금 확인", screen: "ADMN-RFD-002-S1", depts: ["RG-02", "RG-04"], on: true, order: 2 },
    { code: "VOC-PAY-03", major: "PAY", name: "휴대폰 결제 환불", screen: "ADMN-RFD-002-S1", depts: ["RG-04"], on: true, order: 3 },
    { code: "VOC-PAY-04", major: "PAY", name: "영수증 · 증빙 발급", screen: "ADMN-BRD-002", depts: ["RG-02"], on: true, order: 4 },
    { code: "VOC-PAY-05", major: "PAY", name: "상담 필요 (관리자 판단)", screen: "ADMN-BRD-002", depts: ["RG-02"], on: true, order: 5 },
    { code: "VOC-SHIP-01", major: "SHIP", name: "배송지 변경", screen: "ADMN-ORD-001-S1", depts: ["RG-03"], on: true, order: 1 },
    { code: "VOC-SHIP-02", major: "SHIP", name: "배송 지연 · 배송 조회", screen: "ADMN-ORD-002", depts: ["RG-03", "RG-02"], on: true, order: 2 },
    { code: "VOC-SHIP-03", major: "SHIP", name: "파손 · 오배송 교환", screen: "ADMN-ORD-002", depts: ["RG-03"], on: true, order: 3 },
    { code: "VOC-SHIP-04", major: "SHIP", name: "교재 낙장 · 인쇄 불량", screen: "ADMN-ORD-002", depts: ["RG-03"], on: true, order: 4 },
    { code: "VOC-LECT-01", major: "LECT", name: "동시접속 · 세션 차단", screen: "ADMN-USER-003", depts: ["RG-02"], on: true, order: 1 },
    { code: "VOC-LECT-02", major: "LECT", name: "수강 기간 연장", screen: "ADMN-USER-003", depts: ["RG-02"], on: true, order: 2 },
    { code: "VOC-LECT-03", major: "LECT", name: "진도율 누락 · 플레이어 오류", screen: "ADMN-USER-004", depts: ["RG-02"], on: true, order: 3 },
    { code: "VOC-LECT-04", major: "LECT", name: "기기 등록 초기화 (2차 고도화)", screen: "ADMN-USER-003", depts: ["RG-02"], on: false, order: 4 },
    { code: "VOC-PASS-01", major: "PASS", name: "합격환급 서류 보완", screen: "ADMN-SETT-006", depts: ["RG-02", "RG-04"], on: true, order: 1 },
    { code: "VOC-PASS-02", major: "PASS", name: "포인트 · 쿠폰 누락", screen: "ADMN-USER-002", depts: ["RG-02"], on: true, order: 2 },
    { code: "VOC-PASS-03", major: "PASS", name: "이벤트 경품 미수령", screen: "ADMN-USER-002", depts: ["RG-02"], on: true, order: 3 },
    { code: "VOC-STUDY-01", major: "STUDY", name: "강의 내용 질문", screen: "ADMN-BRD-004", depts: ["RG-05", "RG-06"], on: true, order: 1 },
    { code: "VOC-STUDY-02", major: "STUDY", name: "교재 정답지 요청", screen: "ADMN-BRD-010", depts: ["RG-06", "RG-02"], on: true, order: 2 },
    { code: "VOC-ETC-01", major: "ETC", name: "회원정보 변경", screen: "ADMN-BRD-002", depts: ["RG-02"], on: true, order: 1 },
    { code: "VOC-ETC-02", major: "ETC", name: "탈퇴 · 개인정보 처리", screen: "ADMN-BRD-002", depts: ["RG-02"], on: true, order: 2 },
    { code: "VOC-ETC-03", major: "ETC", name: "기타 문의", screen: "ADMN-BRD-002", depts: ["RG-02"], on: false, order: 3 }
  ];

  // 거래처 유형 최초값 — 권리자(계약 원장의 계약 당사자)가 아닌 거래 상대방의 분류. 공급 파트너가 늘면 거래처 관리에서 유형을 추가한다
  // form: 거래 조건 입력 양식 — PURCHASE 매입(공급률 · 결제 조건) / LOGISTICS 물류 대행(건당 단가 · 회수 · 보관) / GENERAL 일반
  var VENDOR_TYPE_SEED = [
    { id: "VT-01", name: "도서 매입처", form: "PURCHASE", evidence: "전자계산서(면세)", on: true, order: 1 },
    { id: "VT-02", name: "상품 매입처", form: "PURCHASE", evidence: "전자세금계산서(과세)", on: true, order: 2 },
    { id: "VT-03", name: "물류 대행사(3PL)", form: "LOGISTICS", evidence: "전자세금계산서(과세)", on: true, order: 3 }
  ];

  // 거래처 최초값 — 화면들에 흩어져 있던 매입처 · 3PL을 한 원장으로 모은 것(코드 SUP-NNNN은 기존 화면 표기를 따름)
  var VENDOR_SEED = [
    { id: "SUP-0003", type: "VT-01", name: "한국자격교재총판", bizNo: "214-81-33201", ceo: "권총판", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "65", pay: "월말 마감 · 익월 10일 지급" }, contact: "02-555-1203", since: "2024-03-01" },
    { id: "SUP-0004", type: "VT-01", name: "예문사", bizNo: "105-81-12345", ceo: "정예문", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "70", pay: "월말 마감 · 익월 10일 지급" }, contact: "02-701-4410", since: "2023-01-10" },
    { id: "SUP-0005", type: "VT-01", name: "구민사", bizNo: "101-81-22987", ceo: "조구민", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "68", pay: "월말 마감 · 익월 15일 지급" }, contact: "02-333-1200", since: "2023-06-01" },
    { id: "SUP-0006", type: "VT-01", name: "성안당", bizNo: "110-81-40018", ceo: "이성안", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "70", pay: "월말 마감 · 익월 10일 지급" }, contact: "031-950-6300", since: "2024-01-15" },
    { id: "SUP-0008", type: "VT-01", name: "(주)한빛도서유통", bizNo: "124-86-77120", ceo: "한빛남", taxType: "일반과세", status: "폐업", checkedAt: "2026-06-01", on: false,
      terms: { rate: "66", pay: "월말 마감 · 익월 10일 지급" }, contact: "031-221-0090", since: "2022-09-01" },
    { id: "SUP-0007", type: "VT-02", name: "(주)세이프기프트", bizNo: "220-87-10293", ceo: "안세이", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "55", pay: "입고 후 30일" }, contact: "02-6010-7788", since: "2025-04-01" },
    { id: "SUP-0012", type: "VT-02", name: "카시오코리아 공식총판", bizNo: "211-88-55031", ceo: "김카시", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { rate: "72", pay: "입고 후 45일" }, contact: "02-2222-3456", since: "2025-07-01" },
    { id: "SUP-0020", type: "VT-03", name: "CJ대한통운 파주 물류센터", bizNo: "110-81-05034", ceo: "신물류", taxType: "일반과세", status: "계속", checkedAt: "2026-10-02", on: true,
      terms: { outFee: "2000", returnFee: "4000", storage: "300000", cycle: "월 1회 (익월 초 명세서)" }, contact: "031-940-1100", since: "2025-11-01" }
  ];

  // 권리자 원장 요약 — 원천은 권리자 계약 원장(ADMN-INST-001)의 계약 당사자. 외부 계정의 소속(본인 데이터 범위) 지정에 쓴다.
  // 해지 · 종료 계약(contracts[].status = "TERMINATED")만 있는 권리자도 정산 · 청구가 남아 있으면 원장에 둔다(v6.60 RH-0015 · 0049 · 0055).
  //   list()(외부 계정 소속 후보)는 현행 계약이 하나라도 있는 권리자만 돌려주고, get() · all()은 모두 돌려준다.
  // 강사 · 저자 · 위탁사 같은 구분은 고정 분류가 아니라 계약 유형(정산 입력 구분)에서 나온다
  // caseLabel = 화면에서 이름 뒤에 붙이는 케이스 표기(소속 형태 · 세무 유형, INST-001 계약 기준). 화면마다 다르게 쓰지 않는다
  var RIGHTS_HOLDER_SEED = [
    { id: "RH-0012", name: "산준교육 콘텐츠 주식회사", caseLabel: "법인 · 일반과세", contracts: [{ no: "CT-2026-0412", types: ["강의 수익배분", "교재 인세", "개발지원금"] }] },
    { id: "RH-0018", name: "고(故) 박위생 (상속 승계)", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2025-1102", types: ["교재 인세", "강의 수익배분"] }] },
    { id: "RH-0019", name: "김안전 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0715", types: ["강의 수익배분", "월 최저보장", "문항 매절", "교재 인세"] }] },
    { id: "RH-0025", name: "정종대 강사 (정종대 안전연구소)", caseLabel: "개인 면세사업자", contracts: [{ no: "CT-2026-0501", types: ["강의 수익배분", "교재 인세", "개발지원금"] }] },
    { id: "RH-0031", name: "이안전 저자", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0610", types: ["교재 인세"] }] },
    { id: "RH-0046", name: "이건설 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0712", types: ["강의 수익배분", "교재 인세", "개발지원금", "월 최저보장"] }] },
    { id: "RH-0047", name: "박보건 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2024-1101", types: ["강의 수익배분"] }] },
    { id: "RH-0048", name: "최지도 강사 · 저자", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0405", types: ["교재 인세", "강의 수익배분"] }] },
    { id: "RH-0042", name: "최그래픽 (기여자)", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0702", types: ["개발지원금", "공동제작"] }] },
    { id: "RH-0044", name: "안전기술출판 (위탁사)", caseLabel: "도서 위탁", contracts: [{ no: "CT-2026-0705", types: ["도서 위탁"] }] },
    { id: "RH-0051", name: "사단법인 한국소방학회", caseLabel: "도서 위탁", contracts: [{ no: "CT-2026-0801", types: ["도서 위탁"] }] },
    { id: "RH-0063", name: "한도해 작가", caseLabel: "일시 삽화·자문 · 기타소득", contracts: [{ no: "CT-2026-0919", types: ["일시 용역 (삽화 · 자문)"] }] },
    { id: "RH-0088", name: "최신규 강사 (신규 영입)", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-NEW", types: ["강의 수익배분", "개발지원금"] }] },
    { id: "RH-0049", name: "정기계 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2025-0115", types: ["강의 수익배분"], status: "TERMINATED" }] },
    { id: "RH-0055", name: "이중도 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2026-0322", types: ["강의 수익배분", "월 최저보장"], status: "TERMINATED" }] },
    { id: "RH-0015", name: "이전기 강사", caseLabel: "개인 프리랜서", contracts: [{ no: "CT-2025-0911", types: ["강의 수익배분", "전속계약금"], status: "TERMINATED" }] }
  ];

  var roleStore = store("sjm.master.roleGroups.v1", ROLE_SEED);
  // v6.38 새 메뉴 키 호환 — 이전 버전이 localStorage에 저장한 역할 그룹에는 새 키가 없으므로 최초값에서 한 번 채운다(기존 키 값은 건드리지 않음)
  (function () {
    var cur = roleStore.get(), changed = false;
    cur.forEach(function (g) {
      ROLE_SEED.forEach(function (sg) {
        if (sg.id !== g.id) return;
        g.perms = g.perms || {};
        if (sg.aff && !g.aff) { g.aff = sg.aff.slice(); changed = true; }
        // v6.40 조교는 내부 직원 — 이전에 저장된 외부 · 권리자 소속 값을 내부 · 직원으로 갱신
        if (g.id === "RG-06" && (g.side !== "INTERNAL" || !g.aff || g.aff.join() !== "STAFF")) { g.side = "INTERNAL"; g.aff = ["STAFF"]; changed = true; }
        // v6.49 역할 그룹 시작 화면(로그인 착지 3순위) — 저장된 값에 없으면 최초값으로 보충
        if (sg.dashArea && !g.dashArea) { g.dashArea = sg.dashArea; changed = true; }
        if (sg.startScreen && !g.startScreen) { g.startScreen = Object.assign({}, sg.startScreen); changed = true; }
        // v6.52 강사 · 저작권자 기본 시작 화면을 파트너 센터로 — 운영자가 바꾸지 않은(옛 기본값 그대로인) 경우만 갱신
        if (sg.startScreen && g.startScreen && g.startScreen.code === "ADMN-SETT-002" && String(g.startScreen.url || "").indexOf("partner-stmt") !== -1 && sg.startScreen.code === "ADMN-PTNR-001") { g.startScreen = Object.assign({}, sg.startScreen); changed = true; }
        ["refundpass", "freecon"].forEach(function (k) {
          if (sg.perms[k] && g.perms[k] === undefined) { g.perms[k] = sg.perms[k]; changed = true; }
        });
      });
    });
    if (changed) roleStore.set(cur);
  })();
  var vendorTypeStore = store("sjm.master.vendorTypes.v1", VENDOR_TYPE_SEED);
  var vendorStore = store("sjm.master.vendors.v1", VENDOR_SEED);
  var majorStore = store("sjm.master.inquiryMajors.v1", MAJOR_SEED);
  var catStore = store("sjm.master.inquiryCats.v1", CAT_SEED);

  function byOrder(a, b) { return (a.order || 0) - (b.order || 0); }

  var roles = {
    list: function () { return roleStore.get().slice().sort(byOrder); },
    active: function () { return roles.list().filter(function (g) { return g.on; }); },
    queues: function () { return roles.active().filter(function (g) { return g.queue; }); },
    get: function (id) {
      var all = roleStore.get();
      for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
      return null;
    },
    name: function (id) { var g = roles.get(id); return g ? g.name : id; },
    perm: function (id, menu) { var g = roles.get(id); return (g && g.perms && g.perms[menu]) || ""; },
    has: function (id, menu, flag) { return roles.perm(id, menu).indexOf(flag) !== -1; },
    save: function (list) { roleStore.set(clone(list)); },
    reset: function () { roleStore.reset(); },
    nextId: function () {
      var max = 0;
      roleStore.get().forEach(function (g) { var n = parseInt(String(g.id).split("-")[1], 10); if (n > max) max = n; });
      return "RG-" + (max + 1 < 10 ? "0" : "") + (max + 1);
    }
  };

  var inquiry = {
    majors: function () { return majorStore.get(); },
    cats: function () { return catStore.get(); },
    save: function (majors, cats) { majorStore.set(clone(majors)); catStore.set(clone(cats)); },
    reset: function () { majorStore.reset(); catStore.reset(); },
    // 역할 그룹을 담당 부서 큐로 쓰는 사용 중 분류 — 그룹 변경 · 미사용 전환의 영향 확인에 쓴다
    catsUsingRole: function (roleId) {
      return catStore.get().filter(function (c) { return c.on && c.depts.indexOf(roleId) !== -1; });
    },
    // 대분류에 속한 사용 중 분류의 담당 부서 큐 합집합 — 1:1 문의 허브에서 접수 건이 올라가는 큐
    queuesForMajor: function (prefix) {
      var seen = {};
      var out = [];
      catStore.get().forEach(function (c) {
        if (!c.on || c.major !== prefix) return;
        c.depts.forEach(function (d) { if (!seen[d]) { seen[d] = true; out.push(d); } });
      });
      return out;
    }
  };

  var vendors = {
    types: function () { return vendorTypeStore.get().slice().sort(byOrder); },
    activeTypes: function () { return vendors.types().filter(function (t) { return t.on; }); },
    type: function (id) {
      var all = vendorTypeStore.get();
      for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
      return null;
    },
    list: function () { return vendorStore.get().slice(); },
    get: function (id) {
      var all = vendorStore.get();
      for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
      return null;
    },
    name: function (id) { var v = vendors.get(id); return v ? v.name : id; },
    // 양식(form)으로 고른다 — 유형 이름이 바뀌거나 늘어도 '물류 대행' 거래처를 찾을 수 있게
    byForm: function (form) {
      return vendorStore.get().filter(function (v) { var t = vendors.type(v.type); return t && t.form === form; });
    },
    byType: function (typeId) { return vendorStore.get().filter(function (v) { return v.type === typeId; }); },
    save: function (list) { vendorStore.set(clone(list)); },
    saveTypes: function (list) { vendorTypeStore.set(clone(list)); },
    reset: function () { vendorStore.reset(); vendorTypeStore.reset(); },
    nextId: function () {
      var max = 0;
      vendorStore.get().forEach(function (v) { var n = parseInt(String(v.id).split("-")[1], 10); if (n > max) max = n; });
      var s = String(max + 1);
      while (s.length < 4) s = "0" + s;
      return "SUP-" + s;
    },
    nextTypeId: function () {
      var max = 0;
      vendorTypeStore.get().forEach(function (t) { var n = parseInt(String(t.id).split("-")[1], 10); if (n > max) max = n; });
      return "VT-" + (max + 1 < 10 ? "0" : "") + (max + 1);
    }
  };

  // 2계층 수취인 — 계약 당사자는 아니지만 그 계약의 정산금을 나눠 받는 권리자(공동 서명 수취인 · 상속 승계인).
  // 수취인도 권리자 계약 원장(ADMN-INST-001)에 권리자로 등록하고 계약에 연결한다(payeeOf). 수취인 분할(ADMN-SETT-007)은 연결된 권리자만 고른다.
  // ratio는 수취인 분할의 현재 몫(시연값). 개인 · 사업자 모두 계정을 받을 수 있고, 세금계산서 · 계산서 제출 기능은 사업자에게만 붙는다(biz)
  var PAYEE_HOLDER_SEED = [
    { id: "RH-0071", name: "(주)스타에듀매니지먼트", entity: "법인 일반과세자 (106-81-55210)", biz: true, taxCase: "일반과세 세금계산서 권리자 발행 (TX-07 · 부가세 10%)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2026-0715", holderId: "RH-0019", holderName: "김안전", role: "공동서명 소속사", kind: "CO_SIGNER", since: "", ratio: 30 }] },
    { id: "RH-0072", name: "한국기술콘텐츠에이전시", entity: "개인 일반과세자 (211-08-33190)", biz: true, taxCase: "일반과세 세금계산서 권리자 발행 (TX-07 · 부가세 10%)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2026-0715", holderId: "RH-0019", holderName: "김안전", role: "공동서명 기획사", kind: "CO_SIGNER", since: "", ratio: 0 }] },
    { id: "RH-0073", name: "(주)안전교육파트너스", entity: "법인 일반과세자 (119-86-11203)", biz: true, taxCase: "일반과세 세금계산서 권리자 발행 (TX-07)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2026-0501", holderId: "RH-0025", holderName: "정종대", role: "공동서명 후보 소속사", kind: "CO_SIGNER", since: "", ratio: 0 }] },
    { id: "RH-0074", name: "(주)산준미디어제작센터", entity: "법인 일반과세자 (105-81-99120)", biz: true, taxCase: "일반과세 세금계산서 권리자 발행 (TX-07)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2026-0412", holderId: "RH-0012", holderName: "산준교육 콘텐츠 주식회사", role: "공동서명 제작계열사", kind: "CO_SIGNER", since: "", ratio: 0 }] },
    { id: "RH-0075", name: "스튜디오픽셀아트", entity: "개인 일반과세자 (142-19-88210)", biz: true, taxCase: "일반과세 세금계산서 권리자 발행 (TX-07)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2026-0702", holderId: "RH-0042", holderName: "최그래픽", role: "공동서명 스튜디오", kind: "CO_SIGNER", since: "", ratio: 0 }] },
    { id: "RH-0076", name: "박승계", entity: "개인 비사업자 (상속 승계)", biz: false, taxCase: "기타소득 C05 (payee_is_author=false · 필요경비 0% · 세율 22% TX-03 확정)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2025-1102", holderId: "RH-0018", holderName: "고(故) 박위생", role: "법정 상속인 · 배우자", kind: "SUCCESSOR", since: "2026-09-01", ratio: 60 }] },
    { id: "RH-0077", name: "박자녀", entity: "개인 비사업자 (상속 승계)", biz: false, taxCase: "기타소득 C05 (payee_is_author=false · 필요경비 0% · 세율 22% TX-03 확정)", isAuthor: false, contracts: [],
      payeeOf: [{ contract: "CT-2025-1102", holderId: "RH-0018", holderName: "고(故) 박위생", role: "법정 상속인 · 자녀", kind: "SUCCESSOR", since: "2026-09-01", ratio: 40 }] }
  ];
  var holderStore = store("sjm.master.rightsHolders.v1", RIGHTS_HOLDER_SEED.concat(PAYEE_HOLDER_SEED));
  // v6.60 시드 보충 — 이전 버전이 저장한 원장에 없는 권리자 · 계약 유형 · 계약 상태를 최초값에서 채운다(저장된 값은 지우거나 바꾸지 않음)
  (function () {
    var cur = holderStore.get(), byId = {}, changed = false;
    cur.forEach(function (h) { byId[h.id] = h; });
    RIGHTS_HOLDER_SEED.concat(PAYEE_HOLDER_SEED).forEach(function (s) {
      var h = byId[s.id];
      if (!h) { cur.push(clone(s)); changed = true; return; }
      (s.contracts || []).forEach(function (sc) {
        (h.contracts || []).forEach(function (hc) {
          if (hc.no !== sc.no) return;
          sc.types.forEach(function (t) { if (hc.types.indexOf(t) === -1) { hc.types.push(t); changed = true; } });
          if (sc.status && !hc.status) { hc.status = sc.status; changed = true; }
        });
      });
    });
    if (changed) holderStore.set(cur);
  })();

  function findHolder(id) {
    var list = holderStore.get();
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  var rightsHolders = {
    all: function () { return clone(holderStore.get()); },
    // 계약 당사자(현행 계약이 있는 권리자) — 외부 계정 소속의 '계약 당사자' 묶음. 해지 · 종료 계약만 남은 권리자는 뺀다
    list: function () { return clone(holderStore.get().filter(function (h) { return h.contracts && h.contracts.some(function (c) { return c.status !== "TERMINATED"; }); })); },
    get: function (id) { var h = findHolder(id); return h ? clone(h) : null; },
    // 계약 유형 합집합 — 이 권리자가 어떤 성격의 파트너인지는 계약 유형으로 판단한다
    types: function (id) {
      var h = findHolder(id);
      var seen = {};
      var out = [];
      if (!h) return out;
      (h.contracts || []).forEach(function (c) { c.types.forEach(function (t) { if (!seen[t]) { seen[t] = true; out.push(t); } }); });
      return out;
    },
    // 본인 계약 없이 다른 계약의 수취인으로만 연결된 권리자인지
    isPayeeOnly: function (id) {
      var h = findHolder(id);
      return !!h && !(h.contracts && h.contracts.length) && !!(h.payeeOf && h.payeeOf.length);
    },
    // 계약에 연결된 2계층 수취인 — 각 항목에 link(그 계약과의 관계)를 붙여 돌려준다
    coSigners: function (contractNo) {
      var out = [];
      holderStore.get().forEach(function (h) {
        (h.payeeOf || []).forEach(function (l) { if (l.contract === contractNo) { var c = clone(h); c.link = clone(l); out.push(c); } });
      });
      return out;
    },
    // 현재 분할 몫이 있는 2계층 수취인 — 외부 계정 소속의 '2계층 수취인' 묶음(데이터 범위는 본인 수취 몫)
    payees: function () {
      var out = [];
      holderStore.get().forEach(function (h) {
        (h.payeeOf || []).forEach(function (l) {
          if (l.ratio > 0) out.push({ id: h.id, name: h.name, entity: h.entity, biz: !!h.biz, contract: l.contract, holderId: l.holderId, holderName: l.holderName, ratio: l.ratio, evidence: h.biz ? "세금계산서 제출" : "원천징수 영수증 조회" });
        });
      });
      return out;
    },
    payee: function (id) {
      var p = rightsHolders.payees().filter(function (x) { return x.id === id; });
      return p.length ? p[0] : null;
    },
    // 신규 수취인 권리자 등록 — 번호는 원장 전체의 다음 RH 번호(실제 채번은 서버에서 중복 없이)
    addPayee: function (rec, link) {
      var list = clone(holderStore.get());
      rec.id = rightsHolders.nextId();
      rec.contracts = [];
      rec.payeeOf = [link];
      list.push(rec);
      holderStore.set(list);
      return rec.id;
    },
    link: function (id, link) {
      var list = clone(holderStore.get());
      list.forEach(function (h) { if (h.id === id) h.payeeOf = (h.payeeOf || []).concat([link]); });
      holderStore.set(list);
    },
    nextId: function () {
      var max = 0;
      holderStore.get().forEach(function (h) { var n = parseInt(String(h.id).replace("RH-", ""), 10); if (n > max) max = n; });
      return "RH-" + ("000" + (max + 1)).slice(-4);
    },
    reset: function () { holderStore.reset(); }
  };

  // 운영 설정값 — 운영자가 관리 화면에서 바꾸는 변수(고정값 아님). 화면은 값을 직접 적지 않고 여기서 읽는다(v6.40)
  //   remaskMemberSec · remaskHolderSec: 민감정보 열람 후 자동 재마스킹 시간(초) — 설정 화면 CONF-003
  //   playbackMaxCreditedSpeed · limitedForward: 진도 인정 최대 배속 · 앞으로 건너뛰기 제한 — 설정 화면 CONF-003
  //   lqnaMode: 학습 Q&A 운영 방식 CAFE(네이버 카페 아웃링크) / INTERNAL(자체 학습 Q&A, 파트너 센터에서 강사 답변) — 설정 화면 CONF-003
  //   reviewRewardP · reviewBestRewardP · freePointCapP: 후기 보상 · 베스트 후기 보상 · 무상 포인트 잔액 상한 — 설정 화면 PROM-002 포인트 정책
  //   manualPointExpiryDays · manualPointExpiryDefault: 수동 포인트 지급 만료 기간 선택지(일) · 기본 선택 — 설정 화면 CONF-003, 쓰는 화면 USER-001(white 결정 2026-10-27)
  var SETTINGS_SEED = {
    remaskMemberSec: 600, remaskHolderSec: 30,
    playbackMaxCreditedSpeed: 2.0, limitedForward: true,
    reviewRewardP: 1000, reviewBestRewardP: 5000, freePointCapP: 200000,
    lqnaMode: "CAFE",
    manualPointExpiryDays: [30, 90, 180], manualPointExpiryDefault: 90
  };
  var settingsStore = store("sjm.master.settings.v1", SETTINGS_SEED);
  var settings = {
    get: function (k) { var v = settingsStore.get()[k]; return v === undefined ? SETTINGS_SEED[k] : v; },
    set: function (k, v) { var cur = settingsStore.get(); cur[k] = v; settingsStore.set(cur); },
    all: function () { var o = clone(SETTINGS_SEED), cur = settingsStore.get(); for (var k in cur) o[k] = cur[k]; return o; },
    reset: function () { settingsStore.reset(); }
  };

  // 회원 저장 그룹(ADMN-USER-006-S2) — 쿠폰 대상(PROM-002) · 알림톡 대상(CONF-004)이 같은 목록을 읽는다(v6.68, 회원관리 스레드 요청)
  //   mode: DYNAMIC(사용 시점 조건 재평가) / STATIC(저장 시점 명단 고정), op: 태그 조합 AND / OR, consent: 광고성 수신 동의 인원
  var GROUP_SEED = [
    { code: "GRP-2026-01", name: "환급반 중도이탈 위험군 케어 그룹", tags: ["TAG-PASS-2026", "TAG-LOW-PROG", "TAG-INACTIVE-14D"], op: "AND", mode: "DYNAMIC", members: 412, consent: 388, updated: "2026.10.18 06:00" },
    { code: "GRP-2026-02", name: "카페 인증 미결제 전환 타겟 그룹", tags: ["TAG-CAFE-AUTH", "TAG-FREE-30D"], op: "AND", mode: "DYNAMIC", members: 1204, consent: 1089, updated: "2026.10.18 06:00" },
    { code: "GRP-2026-03", name: "2026년 2회 정기시험 응시자 스냅샷", tags: ["TAG-PASS-2026", "TAG-CAFE-AUTH"], op: "OR", mode: "STATIC", members: 2140, consent: 1950, updated: "2026.09.15 11:20" }
  ];
  var groupStore = store("sjm.master.groups.v1", GROUP_SEED);
  var groups = {
    list: function () { return clone(groupStore.get()); },
    get: function (code) { var g = groupStore.get().filter(function (x) { return x.code === code; })[0]; return g ? clone(g) : null; },
    /** 저장(같은 code면 갱신, 없으면 추가) */
    save: function (g) { var cur = groupStore.get(), i = cur.map(function (x) { return x.code; }).indexOf(g.code); if (i >= 0) cur[i] = g; else cur.push(g); groupStore.set(cur); },
    remove: function (code) { groupStore.set(groupStore.get().filter(function (x) { return x.code !== code; })); },
    reset: function () { groupStore.reset(); }
  };

  window.SJM_MASTER = { menus: MENUS, roles: roles, inquiry: inquiry, vendors: vendors, rightsHolders: rightsHolders, settings: settings, groups: groups };
})();
