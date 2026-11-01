# [AI 에이전트 전용 명세서] AI 에이전틱 개발 · 정합성 검증 환경 구축 (v1.1.0)

> **문서 용도**: 이 문서는 **AI 에이전트(Claude Code · 안티그래비티)**가 프로젝트 환경을 세팅하거나, 각자의 역할(**PO/PM** 정본 개정 / **UIX 디자이너** Figma 연동 / **개발자** 화면 구현 / 정본↔코드 대조 검수 / 레거시 역공학 문서화)을 수행할 때 직접 읽고 따르는 **AI 실행 명세서(Executable Spec)**다.
> 사람(**PO/PM · UIX 디자이너 · 개발자**)에게 설명하고 브리핑하기 위한 시각 자료는 동일 폴더의 **`AI_에이전틱_환경_가이드.html`**을 사용한다.

---

## 0. 핵심 용어 사전 (Glossary)

문서 전반에서 사용되는 약어와 핵심 개념의 정의다. 본문에서도 첫 등장 시 한글 풀이를 병기한다.

| 용어 (약어) | 한글 명칭 | 쉬운 풀이 및 실무 역할 |
| :--- | :--- | :--- |
| **계층형 SSOT** (`Hierarchical SSOT`) | **계층형 단일 정본 체계** | 비즈니스 기획을 최상위 원천(Root)으로 두고, 디자인 시스템(Visual)과 인터페이스 계약(Code)을 파생 정본으로 삼아 전체 일관성을 유지하는 3각 정본 체계. |
| **Root Logic SSOT** (`Root SSOT`) | **최상위 비즈니스 정본** | PO/PM이 작성·승인하는 비즈니스 정책 및 요구사항 정본(`spec-repo/docs/`). 왜(Why), 규칙, 데이터, 화면 기능 요구사항의 유일한 절대 기준점. |
| **Visual SSOT** (`Visual SSOT`) | **시각 정본 (디자인 시스템 & 시안)** | 관행적 화면설계서 대신 기획 요구사항을 Figma AI로 레이아웃화하고, 프로젝트 고유의 디자인 시스템(토큰 & 컴포넌트)에 바인딩하여 확정한 UI 정본(`Ready for Dev`). |
| **Code/Interface SSOT** (`Code SSOT`) | **인터페이스 정본 (API 계약)** | 프론트엔드와 백엔드가 서로를 기다리지 않고 병렬 개발하기 위해 사전에 확정하는 인터페이스 계약(`00_domain_contracts.md`, `contracts/openapi.yaml` 및 Mock JSON). |
| **Contract-First** (`Contract-First Development`) | **계약 우선 개발** | 백엔드 API 완성을 기다리지 않고, 사전에 확정된 API 스키마/Mock JSON(인터페이스 정본)을 기준으로 FE와 BE가 즉시 병렬 구현에 착수하는 개발 방식. |
| **추적 ID** (`Traceability ID / POL-*`) | **정책 추적 식별자** | 비즈니스 정책 항목마다 PO/PM이 부여하는 영구 식별자(`POL-<도메인>-<번호>`). PRD ↔ Figma 색인 ↔ API 스키마 ↔ 테스트 함수 ↔ Git 커밋에 동일 부여하여 AI가 영향 범위를 즉시 추출하는 열쇠. |
| **질문 등급** (`Blocking vs ASSUMPTION`) | **질문 등급 분리 규칙** | 질문 병목을 막는 이원화 규칙. 금액·권한·상태전이 등 핵심은 작업을 멈추는 `Blocking`, 단순 문구·정렬은 `[ASSUMPTION: Q-ID]` 태그를 달고 선진행한 뒤 사후 승인받는 `Non-blocking`. |
| **가정 진행** (`🟡 Assumption Validated`) | **검수 5대 등급 (임시 선진행)** | 비차단 질문에 대해 `[ASSUMPTION: Q-ID]` 주석을 달고 개발을 선진행한 상태. 작업 브랜치에서는 허용되나 main 병합 시에는 반드시 정본 반영 후 해소되어야 함. |
| **화면 상태 매트릭스** (`Screen State Matrix`) | **화면 5대 상태 체크리스트** | 와이어프레임 생략 시 해피패스만 남는 문제를 차단하기 위해, 각 화면의 5대 상태(정상·로딩·빈화면·오류·권한없음)를 규격화한 디자인 확정(`Ready for Dev`) 필수 체크리스트. |
| **Figma Code Connect** | **코드 컴포넌트 매핑 도구** | Figma 컴포넌트와 실제 프로덕션 코드 컴포넌트를 1:1로 매핑하여, AI가 시안을 단순한 '그림 레이어'가 아니라 실제 코드 컴포넌트(`Button`, `Modal` 등)로 직결 인식하게 하는 도구. |
| **AGENTS.md** | **에이전트 공통 행동 헌법** | 모든 코딩 에이전트(Claude Code, 안티그래비티 등)가 공통으로 따르는 프로젝트 최상위 행동 규약. 정본 우선순위, 질문 등급 기준, ASSUMPTION 표기법, 추적 ID 작성 규칙이 명시됨. |
| **ADR** (`Architecture / Decision Record`) | **정책 및 아키텍처 결정 기록** | 질문(Q-ID) 및 정책 협의 과정에서 도출된 핵심 비즈니스·기술 의사결정의 배경과 근거를 영구 보존하는 결정 기록 문서(`docs/adr/`). |
| **PO / PM** (`Product Owner / Manager`) | **프로덕트 오너 / 매니저** | 비즈니스 정책·화면 기획·우선순위를 결정하고 정본(SSOT)의 최종 승인 권한을 갖는 기획 책임자 그룹(다수 도메인 PM + 리드 PO/PM 포함). |
| **MCP** (`Model Context Protocol`) | **모델 컨텍스트 프로토콜 (외부 도구 직결 통로)** | AI 에이전트가 로컬 파일뿐 아니라 **Figma 디자인 시안, 사내 업무 게시판, DB 스키마 등 외부 도구의 실시간 데이터를 직접 읽어오는 표준 연결 규격**. |
| **Digest** (`Screen Digest`) | **화면별 1장 요약본** | 수천 줄짜리 전체 정본 문서 중 **특정 화면 코드 1개에 필요한 데이터 필드·상태값·모달·핵심 수식만 1~2장으로 자동 추출한 AI용 요약 카드**. |
| **Archetype** (`UI Archetype`) | **표준 UI 템플릿 (4종 화면 골격)** | 프로토타입 HTML 없이도 백오피스 화면의 통일성을 유지하도록 미리 정해둔 **4가지 표준 레이아웃 템플릿** (`List-Modal`, `Detail-Form`, `Stats-Dashboard`, `Tabs-Complex`). |
| **Auto Layout & Design Token** | **자동 반응형 배치 & 디자인 변수** | UIX 디자이너가 Figma에서 여백·정렬·반응형 크기(Auto Layout)와 색상·폰트·간격 변수(Design Token)를 규격화해 두어 AI가 오차 없이 코드로 변환하게 하는 설정. |
| **Greenfield / Brownfield** | **신규 구축 / 레거시 유지보수** | **Greenfield**는 백지상태에서 새로 만드는 프로젝트, **Brownfield**는 기존에 돌아가는 레거시 코드 위에 기능을 고치거나 덧붙이는 프로젝트. |
| **Fast-Track** (`Level 1~3`) | **변경 등급별 경량 경로** | 모든 수정을 똑같은 무거운 절차로 돌리지 않고, **신규/대규모(L1) · 로직만 변경(L2, UIX 생략) · 단순문구/긴급장애(L3, 선조치 후동기화)**로 나누어 처리 속도를 높이는 규칙. |

---

## 1. 아키텍처 개요 및 핵심 원칙

### 1.1 왜 이 체계가 필요한가?
1. **다수 작업자 로컬 AI의 정본 이탈(Drift) 차단**: 여러 명의 개발자가 각자 로컬에서 AI로 코딩할 때, 정본(SSOT, 단일 정본)을 안 읽거나 AI가 빈틈을 임의로 추론해 정본과 다른 로직·상태값·코드를 만드는 현상을 원천 차단한다.
2. **다중 도메인 간 비즈니스 로직 충돌 방지**: 다수의 **PO/PM**과 다수의 **개발자(프론트엔드·백엔드)**가 도메인(회원·권리자·정산 ↔ 주문·환불·쿠폰 ↔ 권한·로그 등)을 나누어 병렬 작업할 때 상태값·식별자·계산식·API 스키마가 어긋나는 것을 막는다.
3. **화면·UI 파편화 방지 및 UIX(Figma) 직결**: 정적 HTML 프로토타입을 수작업으로 유지보수하지 않으면서도, 백오피스(Track A: AI 표준 골격 구현)와 유저 프론트(Track B: UIX 디자이너 Figma MCP 협업) 각각의 화면 통일성을 100% 보장한다.
4. **PO/PM의 수동 검수 병목 제거**: 각 파트 작업자가 로컬에서 **5대 스킬(`/doc-init`, `/doc-rule`, `/doc-update`, `/dev-screen`, `/spec-check`)**을 거치고 중앙 CI 자동 테스트를 통과한 코드만 병합되게 하여, 사람이 일일이 눈으로 대조하는 병목을 없앤다.

### 1.2 범용 저장소 구조 (모든 프로젝트 공통 규격)
- **정본 저장소 (`spec-repo`, 예: `sanjunmo-settlement`)**:
  - `docs/specs/`: 도메인별 기획 정본 (`01_회원_권한.md`, `02_상품_주문.md`, `03_정산_환불.md`)
  - `docs/contracts/`: 공통 도메인 계약 및 서술 문서 (`00_domain_contracts.md`, `00_ui_system.md`)
  - `contracts/`: 기계 검증 가능한 API 스키마 정본 (`contracts/openapi.yaml` 또는 JSON Schema)
  - `docs/questions/<도메인>/`: 1질문 1파일 분산 질문 목록 (`Q-<도메인>-YYYYMMDD-<short_hash>.md`)
  - `docs/adr/`: 정책 및 아키텍처 결정 기록 (`ADR-<번호>-<제목>.md`)
  - `docs/digest/`: 화면별 1장 요약본 (`digest/*.md`), 위치 색인 (`canon_index.md`)
  - `docs/changes/`: 안건별 작업 지시서 (`LATEST_TASK.md`)
  - `engine/`: 도메인 기준 계산기 + 검증 시나리오 JSON
  - `AGENTS.md`: 모든 코딩 에이전트(Claude Code 등)가 읽는 공통 행동 헌법
  - `.github/CODEOWNERS`: 도메인별 PO/PM 및 테크리드 자동 할당 규칙 파일
- **개발 저장소 (`app-repo`, 예: `sanjunmo`)**:
  - 실제 백엔드·프론트엔드 애플리케이션 코드.
  - `.gitignore`에 등록된 `/docs` 폴더 아래로 정본 저장소의 색인·요약본·계약서·정본을 로컬 동기화(`scripts/sync-spec.sh`)해 참조.
- **검수 실행 위치 원칙 ("각자 로컬 스킬 실행 + 중앙 CI 코드 테스트")**:
  - 별도 유료 외부 서버 구축 없이 **PO/PM, UIX 디자이너(핸드오프 검증), 개발자가 각자 로컬 환경에서 스킬을 실행**해 정합성을 맞춘다.
  - GitHub 서버(CI)는 **결정론적 코드 검사(`check.sh`: 코드 스타일 + Prism 기반 OpenAPI 계약 테스트 + 임시 DB 병렬 테스트 + 도메인 계산기 정답 대조)**만 수행한다.

---

### 1.2.1 계층형 단일 정본 체계 (Hierarchical SSOT Architecture) 및 파트별 정본 역할

단일 정본(SSOT)은 모든 문서와 코드가 수평적으로 나열된 평면 구조가 아니라, **기획의 비즈니스 정책이 최상위 원천(Root)이 되고 그로부터 디자인과 개발의 파생 정본이 뻗어나가는 계층형 삼각 구조(Hierarchical SSOT Triangle)**로 운영된다.

```
                  ┌────────────────────────────────────────┐
                  │   최상위 비즈니스 정본 (Root Logic SSOT)   │
                  │   PO/PM PRD · 정책서 (spec-repo/docs/) │
                  └───────────────────┬────────────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│     시각 정본 (Visual SSOT)     │   │   인터페이스 정본 (Code SSOT)   │
│  UIX Figma 디자인 시스템 & 시안   │   │  Contract-First API 스키마 & Mock │
│  • Figma AI로 PRD 기반 초안 생성 │   │  • contracts/openapi.yaml     │
│  • 프로젝트 디자인 토큰 바인딩      │   │  • FE / BE 무대기 병렬 개발      │
│  • 화면 상태 매트릭스 체크리스트   │   │  • Prism Mock 자동 서버 구동    │
│  • Code Connect 컴포넌트 매핑   │   │  • FE/BE 상호 승인 머지 거버넌스  │
└───────────────┬───────────────┘   └───────────────┬───────────────┘
                │                                   │
                └─────────────────┬─────────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │  실제 프로덕션 코드 & 화면 구현   │
                    │  FE 뷰 바인딩 + BE API 구현  │
                    └───────────────────────────┘
```

#### 1. 최상위 비즈니스 정본 (Root Logic SSOT) — 기획 (PO/PM PRD & 정책서)
- **역할 및 위상**: 프로젝트의 비즈니스 목적, 법적/회계적 도메인 규칙, 데이터 엔티티 정의, 화면 기능 요구사항을 규정하는 **모든 파생 정본의 출발점이자 유일한 절대 기준점(Root)**이다.
- **운영 원칙**:
  - 기획이 변경되면 반드시 Root SSOT가 먼저 개정(`doc-update`)되어야 하며, UIX와 개발 파트의 모든 산출물은 Root SSOT로부터 파생된다.
  - Root SSOT에 정의되지 않은 상태값이나 비즈니스 로직을 디자인이나 코드에서 임의로 창작할 수 없으며, 발견 시 버그(`❌ 위반` 또는 `⚠️ 임의 구현`)로 간주된다. 단, 경미한 UI 분기에 대해 `[ASSUMPTION: Q-ID]` 태그를 달고 선진행한 경우는 `🟡 가정 진행` 등급으로 분류하여 개발을 허용하되, main 병합 전 반드시 정본에 반영해야 한다.

#### 2. 좌측 날개: 시각 정본 (Visual SSOT) — UIX 디자인 시스템 & 확정 시안
- **관행적 화면설계서(와이어프레임)의 완전 생략 원리**:
  - 과거에는 기획자가 PPT나 피그마로 화면설계서(스토리보드)를 수작업으로 그려 디자이너에게 넘겼으나, 이는 기획서와 화면설계서 간의 잦은 불일치(Drift)와 막대한 수정 공수를 초래했다.
  - 에이전틱 환경에서는 기획 PRD(Root SSOT)의 구조화된 텍스트 요구사항(화면 목적, 입력 항목, 상태 배지, 모달 명세)을 **Figma AI 프롬프트/명세로 직접 전달하여 기본 화면 레이아웃과 컴포넌트 초안을 즉시 자동 생성(Scaffolding)**한다.
  - UIX 디자이너는 AI가 생성한 뼈대를 바탕으로, 프로젝트마다 별도로 구축·버전 관리되는 **디자인 시스템(Design Token & UI Kit)**에 바인딩하고 반응형 오토레이아웃(Auto Layout)을 적용하여 완성도를 극대화한다.
  - 완성된 시안에 **`Ready for Dev`** 상태를 부여하면, 프로젝트 디자인 시스템과 해당 Figma 프레임 자체가 UIX 파트의 **시각 정본(Visual SSOT)**으로 확립된다.

#### 3. 우측 날개: 인터페이스 정본 (Code/Interface SSOT) — 개발 계약 우선(Contract-First) 스키마
- **FE/BE 무대기 병렬 개발 원리**:
  - 기존 폭포수 개발에서는 백엔드 API 개발이 완료되어 배포될 때까지 프론트엔드가 대기하거나, 나중에 서로의 입출력 데이터가 맞지 않아 대대적인 수정이 발생했다.
  - 에이전틱 환경에서는 기능 개발 시작 단계에서 `contracts/openapi.yaml`(기계 정본) 및 `00_domain_contracts.md`(해설서)에 **표준 API 엔드포인트 규격과 요청/응답 Mock JSON 스키마를 인터페이스 정본(Code SSOT)으로 먼저 확정(Contract-First)**한다.
  - 백엔드 개발자는 이 스키마 계약에 맞춰 DB 쿼리와 비즈니스 로직을 구축하고, 프론트엔드 개발자는 백엔드 완성을 기다릴 필요 없이 사전 확정된 Mock 데이터를 바인딩하여 화면 UI와 상태 인터랙션을 즉시 완성한다.
  - **계약 변경 승인 거버넌스**: `contracts/openapi.yaml`의 변경은 프론트엔드와 백엔드 모두에 파급되므로, 반드시 **FE 테크리드와 BE 테크리드 양측의 상호 승인(Mutual Review Required)**을 거쳐야만 병합될 수 있도록 GitHub CODEOWNERS로 강제한다.

#### 4. 삼각 계층 동기화 및 검수 원칙
- **하향식 동기화**: PO/PM이 정책을 변경하면 `/doc-update`가 `LATEST_TASK.md`를 발행하여 Visual SSOT(**해당 POL ID가 바인딩된 Figma 프레임 구성 및 5대 화면 상태 매트릭스 갱신**)와 Code SSOT(**OpenAPI 스펙 갱신 및 Mock 동기화**)로 변경 요구사항을 동시에 전파한다. (디자인 토큰은 브랜드나 시각 스타일 변경 시에만 갱신).
- **삼각 대조 검수**: `/spec-check`는 실제 구현 코드를 검수할 때, **Root SSOT의 비즈니스 규칙 일치 여부**와 **Visual SSOT(Figma MCP)의 UI 요소 누락 여부**, **Code SSOT의 OpenAPI 스키마 준수 여부**를 삼각으로 대조하여 위반 사항을 0건으로 통제한다.

---

### 1.2.2 엔드투엔드 정책 추적 ID (`POL-*`) 체계 및 영향도 추적 메커니즘

문서와 코드가 방대해졌을 때 정책 하나가 바뀌면 어디까지 수정해야 하는지 파악하기 위해, 모든 비즈니스 정책 항목에 영구 불변의 **정책 추적 ID (`POL-<도메인>-<3자리 번호>`)**를 부여한다.

```
[PRD 정책서 헤더]
### [POL-SETT-001] 플랫폼 기본 중개 수수료율 및 원천징수 공제 산식

  │ (동일 ID 바인딩)
  ├── 1. 로컬 정본 색인: canon_index.md 매핑표에 Figma Node URL 등록 ➔ Figma MCP로 시안 실시간 조회
  ├── 2. OpenAPI 스펙 description: "POL-SETT-001: 플랫폼 기본 수수료 필드"
  ├── 3. 테스트 코드 주석: // @policy POL-SETT-001 원형 명시 (함수명: test_POL_SETT_001_calculation)
  └── 4. Git 커밋 메시지: feat(settlement): 수수료 산식 보강 (Ref: POL-SETT-001)
```

1. **채번 및 바인딩 규칙**:
   - **채번 권한**: `POL-*` ID는 **오직 PO/PM만이 `main` 브랜치의 정본(`docs/specs/`)에서만 채번**한다. 개발자나 AI 에이전트가 임의로 채번할 수 없게 하여 번호 충돌을 원천 차단한다. 한 번 부여된 ID는 삭제되더라도 영구 결번으로 두고 재사용하지 않는다.
   - **PRD 정본**: 정책이 기술된 문단 헤더에 `### [POL-SETT-001] <정책명>`을 명시한다.
   - **Figma 시안 연결**: Figma Dev Mode 주석은 로컬 저장소 외부에 있으므로, 정본의 `canon_index.md` 및 화면 명세표에 `POL-SETT-001`과 매핑된 **Figma Node URL**을 명기하여 에이전트가 Figma MCP로 직결 조회하도록 한다.
   - **API 스키마 (`openapi.yaml`)**: 필드 또는 엔드포인트의 `description` 속성에 `[POL-SETT-001]`을 포함한다.
   - **테스트 코드**: 테스트 함수 상단 주석에 `// @policy POL-SETT-001`을 **원형 그대로** 명시하고, 함수명에도 `test_POL_SETT_001_<설명>()`을 사용한다.
   - **Git 커밋 메시지**: 커밋 메시지 본문에 `Ref: POL-SETT-001`을 기록한다.
2. **AI 에이전트의 영향도 전수 추출 (grep + Figma MCP 2단계 연동)**:
   - **1단계 (로컬 정본 및 코드 grep)**: 대소문자 및 하이픈/언더스코어를 모두 커버하는 정규식 검색 명령을 실행하여 로컬 파일의 영향 범위를 1초 만에 추출한다:
     ```bash
     grep -rniE "POL[-_]SETT[-_]001" .
     ```
   - **2단계 (Figma 시안 MCP 조회)**: 1단계 검색으로 추출된 정본 색인(`canon_index.md`)의 Figma Node URL을 확인하고, **Figma MCP(`get_node`)**를 호출하여 해당 프레임의 컴포넌트 구성과 변경 필요 여부를 실시간 확인한다.

---

### 1.3 프론트엔드·화면 설계 2-Track 이원화 전략 (프로토타입 관리 부담 제거 & UIX Figma 직결)

별도의 HTML 프로토타입 파일을 수십 개씩 만들고 유지보수하는 부담을 없애기 위해, 화면의 성격에 따라 **Track A**와 **Track B**로 명확히 구분해 운영한다.

| 구분 | **Track A: AI 프론트 자체 구현 트랙** (백오피스 · 어드민 · 사내 툴) | **Track B: UIX 디자이너 협업 트랙** (유저 프론트 · 브랜드 웹/앱) |
| :--- | :--- | :--- |
| **시각적 기준 (SSOT)** | **`00_ui_system.md` (표준 화면 골격 4종 아키타입)** + 정본 `[B] 화면 명세` 표 | **UIX 디자이너의 Figma 시안 (Figma MCP 서버 직결)** + 정본 `[B] 데이터/상태 명세` |
| **HTML 프로토타입 관리** | **생략** (필요시 PO/PM이 4종 골격 기반 1회성 임시 프리뷰만 띄워 보고 폐기) | **생략** (화면설계서 없이 Figma AI로 생성 후 디자인 시스템에 바인딩하여 Visual SSOT 확립) |
| **연결 열쇠 (Key)** | 화면 코드(`ADMN-*`) + 골격 유형(`List-Modal`, `Detail-Form`, `Stats-Dashboard`, `Tabs-Complex`) | Figma 프레임명에 **`[USER-MY-011]`** 화면 코드 표기 + 정본에 Figma Node URL 기록 |
| **`/dev-screen` 작동 방식** | 지정된 표준 UI 컴포넌트 골격에 검색필터·컬럼·모달·비즈니스 로직을 일괄 생성 | **Figma MCP**로 실제 DOM/Auto Layout(자동 반응형 배치)/Design Token(디자인 변수)을 읽어 마크업 생성 + 정본의 비즈니스 로직·데이터 바인딩만 결합 (**AI 임의 UI 변형 금지**) |
| **`/spec-check` 검수 기준** | 정본 `[B]`의 필터·컬럼·모달 구성 및 `[C]` 비즈니스 로직 일치 여부 | **Figma(MCP) 시안의 입력폼·버튼·배지 누락 여부** + **정본 `[C]` 비즈니스 로직 일치 여부** 동시 대조 |

#### 관행적 화면설계서(와이어프레임) 생략을 지탱하는 3대 안전장치 (Track B 필수 규칙)
와이어프레임을 생략할 때 발생할 수 있는 시안의 상태 누락 및 컴포넌트 파편화를 방지하기 위해 다음 3대 규약을 강제한다:

1. **화면 상태 매트릭스 (Screen State Matrix) 필수화**:
   - Figma AI로 화면 초안을 생성하면 정상적인 데이터가 채워진 해피패스(Happy-path) 한 장만 생성되어 빈 화면이나 에러 처리가 누락되기 쉽다.
   - 따라서 UIX 디자이너는 시안을 `Ready for Dev`로 확정하기 전에 반드시 **5대 화면 상태(정상 데이터 · 로딩 스켈레톤 · 빈 데이터 Empty · 오류 Error · 권한 없음/세션만료 Unauthorized)**가 프레임에 완비되었는지 화면 상태 매트릭스 체크리스트를 확인해야 한다.
2. **Figma Code Connect 기반 컴포넌트 직결**:
   - Figma MCP가 디자인 시안을 단순한 '그림(레이어 더미)'으로 읽으면, AI가 이미 프로덕션 코드에 존재하는 공통 컴포넌트(예: `<PrimaryButton>`)를 무시하고 인라인 스타일의 새로운 버튼을 중복 생성하는 문제가 발생한다.
   - Figma Code Connect를 설정하여 Figma 컴포넌트와 실제 리포지토리의 UI 컴포넌트를 1:1로 연결한다. 개발자 AI는 시안을 읽을 때 매핑된 실제 코드 컴포넌트를 직접 호출하여 마크업을 완성한다.
3. **W3C DTCG 표준 기반 단방향 토큰 거버넌스 및 린트(Lint)**:
   - 디자인 토큰은 W3C Design Tokens Community Group(DTCG 2025.10) 표준 포맷을 따르며, **Figma Variables를 원본(Source)**으로 삼고 코드용 토큰은 자동 빌드한다.
   - **Primitive 토큰**(`blue-500`, `gray-100`)과 **Semantic 토큰**(`color-bg-danger`, `color-text-primary`)을 엄격히 분리하며, AI 에이전트에게는 오직 Semantic 토큰만 사용하도록 규칙을 강제한다.
   - 시안 확정 린트: `Ready for Dev` 전환 시 "디자인 변수에 바인딩되지 않은 하드코딩 값 0개, 분리(Detach)된 인스턴스 0개"를 통과해야 한다.

---

### 1.4 다중 작업자(N:M:K) 협업 및 작업 지시·질문 전달 구조

PO/PM, UIX 디자이너, 개발자가 각각 **여러 명(N:M:K)**인 조직에서 **동시 다발적 AI 작업 시 Git 충돌이 나지 않고 질문이 특정 1인에게 병목되지 않도록** 하는 협업 아키텍처다.

#### (1) 질문 병목(Bottleneck) 해소 및 N:M:K 동시성 제어 4대 규칙
단일 마크다운 파일에 모든 에이전트가 질문을 쓰면 브랜치 머지 충돌이 나고, 번호 채번 충돌 및 알림 누락이 발생한다. 이를 다음 4대 규칙으로 해결한다.

##### 1. 도메인별 폴더 분리 및 고유 ID 채번 (`docs/questions/<도메인>/Q-<도메인>-YYYYMMDD-<hash>.md`)
- 질문을 단일 파일에 모으지 않고 도메인별 하위 폴더로 분리하여 관리한다:
  - 경로: `docs/questions/settlement/`, `docs/questions/order/`, `docs/questions/auth/`
- 여러 에이전트가 브랜치에서 동시에 질문 파일을 생성해도 번호 충돌이 없도록 **날짜와 단축 해시**를 조합해 파일명과 ID를 부여한다:
  - 파일명 예: `Q-SETT-20261101-a3f.md` (또는 GitHub Issue 연동 시 `Q-ISSUE-142.md`)
- **CODEOWNERS 기반 자동 할당 및 슬랙 알림**:
  - 저장소 루트의 `.github/CODEOWNERS`에 도메인별 디렉터리와 담당 PO/PM을 매핑한다:
    ```text
    /docs/questions/settlement/ @po-settlement @pm-lead
    /docs/questions/order/      @po-order
    /contracts/openapi.yaml     @fe-lead @be-lead @po-lead
    ```
  - 에이전트가 해당 폴더에 질문 파일을 생성하고 PR을 올리면, GitHub 규칙에 따라 담당 PO/PM이 **PR 리뷰어로 자동 지정되어 슬랙/이메일 알림이 즉시 발송**된다.
- 파일 상단에 메타데이터(YAML frontmatter)를 명시한다:
  ```markdown
  ---
  id: Q-SETT-20261101-a3f
  pol_id: POL-SETT-005
  screen_id: USER-MY-011
  domain: settlement
  owner: @po-settlement
  created_at: 2026-11-01
  status: OPEN # OPEN | IN_REVIEW | RESOLVED
  blocking: true # true (작업 차단) | false (가정 수립 후 선진행)
  ---
  ### [질문 제목] 정산 중도 해지 시 일할 계산 올림/버림 정책 미정의
  - 현상: 정산 기준일에 중도 해지 시 일할 계산 단위가 명시되지 않음.
  - 임시 가정(Non-blocking 시): 소수점 첫째 자리 올림 처리로 가정함.
  ```

##### 2. 질문 등급 분리 (`Blocking` vs `ASSUMPTION:` 선진행) 및 출구 조건(Exit Gate)
모든 질문에서 AI 코딩을 멈추면 Contract-First로 확보한 개발 속도가 다시 지연된다. 따라서 질문의 성격에 따라 처리 경로를 이원화한다.
- **차단 등급 (`Blocking = true`)**:
  - 대상: 결제 금액 산식, 정산 수수료, 회원 권한/인가, 상태 전이 조건, 개인정보 및 PG 연동.
  - 처리: 비즈니스 핵심 정책이므로 AI는 즉시 코딩을 멈추고 `Q-*.md`를 생성한 뒤 PO/PM 승인을 기다린다.
- **비차단 등급 (`Blocking = false`, 선진행) 및 🟡 가정 진행 게이트**:
  - 대상: 단순 라벨 문구, 목록 정렬 기본값, 사소한 레이아웃 여백, 예외 발생 시 안내 텍스트.
  - 처리: AI 에이전트는 가장 합리적인 기준을 세워 코드에 `// [ASSUMPTION: Q-SETT-20261101-a3f] 문구는 결제 취소로 임의 가정하고 진행` 주석을 달고 작업을 멈추지 않고 선진행한다.
  - **출구 조건(Exit Gate)**:
    - 피처 작업 브랜치에서는 `/spec-check`가 이를 `🟡 가정 진행` 상태로 통과시켜 개발을 지속할 수 있다.
    - **단, main/릴리스 브랜치 병합(PR) 시**: 미해결(`OPEN`) 상태인 `ASSUMPTION` 주석이 코드에 1건이라도 남아 있으면 CI에서 병합이 엄격히 차단된다. 반드시 PO/PM이 정본에 반영하고 질문을 `RESOLVED` 처리해야만 최종 통과된다.

##### 3. 정본 반영 연동 종결 규칙 (Drift 원천 차단)
- 메신저나 슬랙, 구두로 질문에 답변했다고 해서 질문을 종결(`RESOLVED`)하지 않는다.
- PO/PM이 정본 문서(`docs/specs/`)에 해당 정책을 정식으로 보완하고 커밋해야만 질문 파일의 상태를 `RESOLVED`로 전환할 수 있다. "답변은 오갔으나 정본은 방치되는 현상"을 시스템적으로 원천 봉쇄한다.

##### 4. 계층 간 역류(Reverse Feedback) 통로 일반화
- 질문 등록 권한은 개발자뿐만 아니라 **모든 직군에게 동등하게 개방**된다.
- **UIX 디자이너**: Figma 디자인 중 PRD에 누락된 화면 상태(빈 화면, 부분 실패 등) 발견 시 동일한 `Q-*.md` 파일로 Root SSOT 보완을 요청한다.
- **백엔드 개발자**: DB 성능이나 레거시 연동 제약으로 OpenAPI 스키마 조정이 필요할 때 동일한 통로로 기획 및 프론트엔드에 계약 변경을 요청한다.

---

#### (2) 정책 및 아키텍처 의사결정 기록 (ADR — Architecture / Decision Record)
질문(Q-ID)을 해결하는 과정에서 도출된 핵심 정책 결정이나 아키텍처 변경(예: *"부분 환불 시 플랫폼 수수료 전액 환급 정책 확정"*)은 정본 본문뿐 아니라 **`docs/adr/ADR-<번호>-<제목>.md`**에 결정 배경, 고려한 대안, 최종 결정 이유를 독립 문서로 영구 보존한다. ADR 번호는 PO/PM과 테크리드가 main에 머지하는 시점에 확정 순번으로 채번하여 번호 충돌을 방지한다.

---

#### (3) 다중 인원 동시 작업 시 충돌 방지 규칙
1. **다수의 PO/PM (도메인별 PM 분담 시)**:
   - 정본 마크다운 파일을 도메인별로 분리(`01_회원_권한.md`, `02_상품_주문.md`, `03_정산_환불.md`)하여 담당 PM 오너십을 지정한다.
   - 여러 도메인에 걸치는 공통 계약 수정 시에는 반드시 리드 PO/PM의 승인을 거친다.
2. **다수의 UIX 디자이너**:
   - Figma 프레임 이름에 **`[<화면코드>] 화면명` (예: `[USER-MY-011] 환불신청모달`)**을 부여하고, 디자인 작업 중(`WIP`)과 확정(`Ready for Dev`) 상태를 구분한다.
   - `Ready for Dev`가 찍히지 않은 프레임은 개발자 AI(`/dev-screen`)가 코드 생성을 거부하여 미완성 시안 구현을 방지한다.
3. **다수의 개발자 (FE/BE 병렬 개발 — Contract-First Code SSOT)**:
   - 백엔드 API 개발이 끝나기 전에 프론트엔드 개발자가 먼저 화면을 구현할 수 있도록, `/doc-rule`이 `contracts/openapi.yaml`에 **표준 API 요청/응답 Mock JSON 스키마를 인터페이스 정본(Code SSOT)으로 사전 확정(Contract-First)**한다.
   - FE와 BE는 서로의 완료를 기다리지 않고 이 확정된 스키마 계약에 따라 병렬로 즉시 구현에 착수한다.

---

#### (4) 변경 규모별 3단계 패스트트랙 (Fast-Track) 전달 경로

| 변경 등급 | 해당 케이스 | 전달 및 실행 경로 (라우팅) |
| :---: | :--- | :--- |
| **Level 1 (Full Track)** | • 신규 화면 추가<br>• 정책 변경으로 **화면 UI 요소(입력창·버튼·배지)와 비즈니스 로직이 함께 바뀔 때** | `PO/PM 요구사항 정의 (/doc-update)` ➔ **`UIX/개발 변경 작업 지시서(LATEST_TASK.md) 동시 배포`** ➔ `UIX Figma 반영(Ready for Dev)` ➔ `개발자 (/dev-screen)` ➔ `양방향 검수 (/spec-check)` |
| **Level 2 (Logic Fast-Track)** | • 화면 레이아웃·UI 변경 없이 **정산 수식·할인율·유효성 조건·DB 로직만 바뀔 때** | `PO/PM 요구사항 정의 (/doc-update)` ➔ **`UIX 단계 생략 (개발 작업 지시서만 생성)`** ➔ `개발자 (/dev-screen)` ➔ `정본 검수 (/spec-check)` |
| **Level 3 (Micro / Hotfix)** | • 단순 문구·오탈자 수정<br>• 운영 긴급 장애(Hotfix) 선조치 | 선(先) 수정 조치 후 **`/doc-update --sync-from-code`**로 정본 및 개정이력 사후 동기화 |

---

#### (5) 소통 채널: [기본(Core) Git 내장 MD 파일] vs [확장 제안(Option) 사내 업무플랫폼 API 직결]

| 구분 | **[기본 (Core)] Git 내장 작업 지시서 & 질문 MD (외부 의존성 0)** | **[확장 제안 (Option A)] 사내 업무플랫폼 경량 API 직결** | **[대안 (Option B)] Google Workspace 연동** |
| :--- | :--- | :--- | :--- |
| **작동 원리** | • PO/PM이 `/doc-update`로 요구사항을 정의하면 정본 개정과 함께 **`docs/changes/LATEST_TASK.md`** 파일이 Git에 자동 생성·배포됨<br>• 개발자의 로컬 AI가 `sync-spec.sh` 후 **`LATEST_TASK.md`를 직접 읽어** 이번 작업 지시를 즉시 파악하고 구현 착수 | • 사내 업무플랫폼(자체 구축 게시판)에 **AI 전용 경량 REST API 3종(`POST 안건등록`, `GET 피드백조회`, `PATCH 상태변경`)** 개방<br>• 초기 1회 동기화한 **`project-meta.json`**을 읽고 AI가 프로젝트 선택 및 담당자 지정을 자동 세팅해 게시 | • 사내 플랫폼 API 개방 전 과도기 또는 외부 협업 시, AI에 기본 내장된 **GWS MCP/CLI**로 Google Sheets 및 Google Chat 스페이스에 자동 등록·조회 |
| **미정의 항목 질문 처리** | • 예외 케이스 발견 시 `/dev-screen`이 **`docs/questions/<도메인>/Q-*.md`**를 생성<br>• `Blocking` 여부에 따라 대기 또는 `ASSUMPTION` 선진행<br>• CODEOWNERS로 담당 PO/PM PR 리뷰어 자동 지정<br>• PO/PM이 정본 반영 후 `RESOLVED` 처리 | • 개발자·UIX가 사내 플랫폼 안건에 댓글을 달면, PO/PM의 AI가 `GET` API로 댓글을 직접 읽어와 브리핑 | • Google Sheets 행 코멘트 또는 Chat 스레드를 AI가 직접 읽어와 브리핑 |
| **장점** | **추가 개발 공수 0건**, 즉시 가동 가능, 코드·정본·작업 지시서가 Git 히스토리에 완벽히 일치 | 전 직원이 익숙한 사내 공식 플랫폼으로 일원화, 비개발자(UIX·타부서) 웹 접근성 최상 | 별도 API 개발 없이 즉시 외부 협업 가능 |

---

### 1.5 파이프라인 전(Before) vs 후(After): 파트별 사람이 직접 하는 일

| 직책 (다수 인원) | **[파이프라인 전 (Before)] 사람이 직접 하는 일** | **[AI 파이프라인 자동 처리 구간]** | **[파이프라인 후 (After)] 사람이 직접 하는 일** |
| :--- | :--- | :--- | :--- |
| **PO / PM**<br>(기획·정책 그룹) | • 비즈니스 요구사항 정의 및 정책 결정<br>• 로컬 AI에 `/doc-update`로 요구사항 정의 실행 (`POL-*` 채번 및 갱신) | • 기존 정책과의 정합성 체크, 변경 등급(L1~L3) 판별 및 영향받는 정본 절·화면코드 전수 스캔 (`POL-*` 추적)<br>• 정본 MD·계산기·색인·Digest·OpenAPI 일괄 개정 및 개정이력 기록<br>• **`docs/changes/LATEST_TASK.md` 변경 작업 지시서 생성** | • AI가 스캔한 영향 범위 및 정본 개정이력(diff) 최종 승인 후 Git 푸시<br>• CODEOWNERS로 할당된 **질문(`docs/questions/**/Q-*.md`) 검토·결정 및 정본 반영** |
| **UIX 디자이너**<br>(디자인 그룹) | • 변경 작업 지시서(`LATEST_TASK.md`) 확인 (`L2 로직변경` 시 생략)<br>• Figma에서 `[화면코드]` 프레임 디자인, 5대 화면 상태 매트릭스 확인 및 Design Token 적용 | • **Figma MCP 서버**가 확정된(`Ready for Dev`) 프레임의 구조·스타일·토큰·Code Connect 정보를 개발자 AI에게 실시간 공급 | • 완료된 프레임을 **`Ready for Dev`** 상태로 전환 (미바인딩 값 0개 린트 확인) 및 Figma 노드 URL 공유<br>• 디자인 중 발견된 누락 상태는 `Q-*.md`로 등록, 배포 후 `/spec-check` 시각 리포트 확인 |
| **개발자**<br>(FE / BE 그룹) | • `sync-spec.sh` 실행 후 로컬 AI에 `/dev-screen` 실행 지시 | • **`LATEST_TASK.md`에서 내 담당 화면코드 및 `POL-*` 자동 인식**<br>• 화면별 요약본(Digest, 6%) 로드 + Track A(표준 UI 템플릿) / Track B(Figma Code Connect) 결합 코딩<br>• 단위/기능 테스트 작성, Prism 기반 계약 검증, `check.sh` 및 `/spec-check` 자동 대조 | • 코딩 중 발견된 정책 공백은 등급 판별 후 **`Blocking` 질문 등록 또는 `// [ASSUMPTION: Q-ID]` 태그 달고 선진행**<br>• main 병합 전 `🟡 가정 진행` 항목 0건 해소 및 `/spec-check` `❌ 위반/누락 0건` 확인 후 PR 병합 |

---

## 2. 5대 핵심 스킬(Skill) 체계 및 직관적 명칭

- **`/doc-*` 계열 (문서·정본 관련 3종)**: `/doc-init`(01. 초기 정본 만들기), `/doc-rule`(02. 공통 규칙 뽑기), `/doc-update`(03. PO/PM 정책 변경)
- **`/dev-*` 계열 (개발자 코딩 1종)**: `/dev-screen`(04. 개발자 화면 구현)
- **`/spec-*` 계열 (검수·대조 1종)**: `/spec-check`(05. 정본 대조 검수)

| 번호 | 스킬 명령어 | 한글 명칭 | 누가 · 언제 쓰는가 | 한 줄 요약 |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **`/doc-init`** | **초기 정본 만들기** | • 정본 없는 레거시 서비스(Brownfield) 온보딩 시<br>• 신규 프로젝트(Greenfield) 초안을 표준 정본화할 때 | 코드/초안을 읽어 표준 3단 포맷(`[A]·[B]·[C]`) 정본 `v1.0.0` + 정책 ID(`POL-*`) 초안 + 색인(`canon_index`) + 요약본(`digest`) 생성 |
| **02** | **`/doc-rule`** | **공통 규칙 뽑기** | • 초기 세팅 시 & 공통 코드·DB·API·UI 골격 변경 시 | 기계 검증 API 계약(`contracts/openapi.yaml`, **Prism Mock 연동**) 및 표준 화면 골격(`00_ui_system.md`), Semantic 토큰 규약 추출·갱신 |
| **03** | **`/doc-update`** | **PO/PM 요구사항 정의 및 정본 개정** | • **PO/PM 상시 사용**<br>• 비즈니스 요구사항이나 정책·화면 규칙을 추가·수정할 때 | 변경 등급(L1~L3) 판별 + `POL-*` 영향 스캔 → 정본·계산기·OpenAPI 개정 → **변경 작업 지시서(`LATEST_TASK.md`) 자동 배포** |
| **04** | **`/dev-screen`** | **개발자 화면 구현** | • **FE/BE 개발자 상시 사용**<br>• 담당 화면(`ADMN-*`, `USER-*`)을 개발·수정할 때 | Track A(표준 UI 템플릿) / **Track B(Figma Code Connect)** + 화면별 요약본(6%) 로드 → `ASSUMPTION` 분기 처리 → 계층 코딩 → `check.sh` 실행 |
| **05** | **`/spec-check`** | **정본 대조 검수** | • **개발자**(커밋 직전 셀프 검수)<br>• **PO/PM · UIX**(병합 전후 총괄 검수) | 정본 명세(+ Track B Figma MCP 노드 + OpenAPI 스키마)와 현재 코드를 대조해 **`✅ 일치` / `❌ 위반·누락` / `⚠️ 임의 구현` / `🟡 가정 진행` / `❓ 미정의 질문`** 5대 판정 |

---

## 3. 각 스킬별 상세 명세 (AI 주입용 `SKILL.md` 원문 규격)

각 저장소의 `.claude/skills/<스킬명>/SKILL.md`(또는 `.claude/commands/<스킬명>.md`)에 그대로 생성할 수 있는 표준 프롬프트 명세다.

---

### 3.1 `/doc-init` — 초기 정본 만들기 스킬 (신규 초안 포매팅 · 레거시 역공학)

```markdown
---
name: doc-init
description: 정본(SSOT)이 없는 레거시 프로젝트 코드나 신규 프로젝트의 비정형 기획 초안을 분석하여 표준 정본 문서(v1.0.0), 화면 요약본(digest), 위치 색인(canon_index), 정책 ID(POL-*)를 최초 생성한다.
---

# /doc-init (초기 정본 만들기) 실행 절차

## 1. 목적
정본(SSOT, 단일 정본)이 없는 기존 유지보수 서비스(Brownfield)나 신규 구축(Greenfield) 초안을 에이전틱 파이프라인이 읽을 수 있는 **표준 정본 포맷**으로 구조화한다. 코드는 수정하지 않는다.

## 2. 단계별 실행 규칙
1. **화면·기능 인벤토리 스캔 및 코드 채번**:
   - 대상 프로젝트의 라우트, 컨트롤러, 뷰, DB 마이그레이션을 스캔(또는 기획 초안 분석)한다.
   - 각 화면·모달·하위 페이지에 표준 화면 코드(`ADMN-<도메인>-<NNN>`, `USER-<도메인>-<NNN>`)를 부여한다.
   - 각 비즈니스 정책 문단에 영구 정책 ID(`POL-<도메인>-<NNN>`)를 최초 채번한다.
2. **표준 3단 템플릿 포매팅 (`docs/specs/`)**:
   - 상단 헤더: `## 문서 개정 이력 (Revision History)` 표 (`v1.0.0 | YYYY-MM-DD | 담당 PO/PM | 초기 정본 구축`)
   - `[A] 프론트엔드(USER-*) ↔ 백오피스(ADMN-*) 1:1 페어 매핑표`
   - `[B] 화면별 상세 데이터 필드, UI 트랙, 5대 화면 상태 매트릭스, 입출력/모달 제어 명세`
   - `[C] 핵심 비즈니스 정책 및 POL-* 하드락 가드레일`
3. **정상 정책 vs 레거시 의심 로직 분리 (Brownfield 중요 규칙)**:
   - 하드코딩·죽은 코드·모순으로 의심되는 부분은 정본으로 확정하지 말고 `docs/questions/<도메인>/Q-LEGACY-<hash>.md`로 1질문 1파일 분리해 PO/PM 판정을 요청한다.
4. **색인 및 요약본 생성**:
   - 화면 코드별 문서·줄 번호 색인(`canon_index.md`)과 화면별 요약본(`digest/<화면코드>.md`)을 함께 생성한다.
```

---

### 3.2 `/doc-rule` — 공통 규칙 뽑기 스킬 (OpenAPI 기계 계약 & UI 골격 & Semantic 토큰)

```markdown
---
name: doc-rule
description: 정본 문서와 기준정보에서 여러 도메인 작업자가 공유하는 기계 검증 API 계약(contracts/openapi.yaml)과 표준 UI 골격 계약(00_ui_system.md), W3C Semantic 디자인 토큰 린트 규칙을 추출·갱신한다.
---

# /doc-rule (공통 규칙 뽑기) 실행 절차

## 1. 목적
도메인 간 경계에서 절대 어긋나면 안 되는 **기계 검증 가능한 API 계약(`contracts/openapi.yaml`)**과 **2-Track 화면 통일성 계약(`00_ui_system.md`)**을 추출하여 CI 자동 검증 및 AI 에이전트의 필독 가드레일로 확립한다.

## 2. 기계 검증 API 계약 (`contracts/openapi.yaml`) 필수 포함 항목
1. **식별자 및 코드 채번 체계**: 도메인별 고유 식별자 프리픽스 규격.
2. **공통 상태값 사전 (Enum/Status)**: 전사 공통 상태코드와 한글 라벨 매핑.
3. **표준 API 엔드포인트 및 요청/응답 스키마**:
   - 백엔드·프론트엔드 무대기 병렬 개발을 위한 Mock 데이터 스펙 완비.
   - 각 필드의 `description`에 대응하는 정책 ID(`POL-*`) 명시.
   - CI에서 Prism을 통해 스펙 기반 임시 Mock 서버 자동 구동 지원.
4. **계약 머지 거버넌스**:
   - `contracts/openapi.yaml` 수정 시 반드시 FE 테크리드와 BE 테크리드 양측 승인을 거치도록 `.github/CODEOWNERS`에 명시.

## 3. UI 계약 (`docs/contracts/00_ui_system.md`) 및 토큰 거버넌스
1. **Track A (어드민)**: 4대 표준 화면 골격 컴포넌트 슬롯 규격 및 상태 배지 매핑.
2. **Track B (유저 프론트)**:
   - W3C DTCG 표준 기반 토큰 거버넌스: Primitive(`blue-500`) 대신 Semantic 토큰(`color-bg-danger`) 사용 강제.
   - Figma Code Connect 매핑 규칙 정의.
   - `Ready for Dev` 필수 린트 기준: "미바인딩 값 0개, Detach 인스턴스 0개, 5대 화면 상태 매트릭스 완비".
```

---

### 3.3 `/doc-update` — PO/PM 정책 변경 스킬 (영향도 스캔 → 패스트트랙 판별 → Git 지시서 생성)

```markdown
---
name: doc-update
description: PO/PM이 정책 변경을 안건 단위로 지시할 때, POL-* 기반으로 영향받는 모든 정본 절, 시안, API, 테스트, 화면 코드를 스캔해 보고하고, 승인 후 정본·계산기·OpenAPI 일괄 개정 및 LATEST_TASK.md를 자동 배포한다.
---

# /doc-update (PO/PM 정책 변경) 실행 절차

## Step 1. POL-* 기반 영향도 전수 스캔 및 변경 등급(Fast-Track) 판별 보고
1. PO/PM이 변경할 정책을 자연어로 입력하면 곧바로 파일을 수정하지 않는다.
2. `canon_index.md`, 정본 문서, `contracts/openapi.yaml`, 도메인 계산기(`engine/`)를 `grep -rniE "POL[-_]<도메인>[-_]<번호>"` 키워드로 검색하여 보고한다:
   - **변경 등급 판정**: `Level 1 (Full Track)` / `Level 2 (Logic Fast-Track)` / `Level 3 (Micro / Hotfix)`
   - **영향받는 정책 ID(`POL-*`) 및 정본 절/줄 번호**
   - **자동 추출된 영향 화면 코드 목록 (`ADMN-*`, `USER-*`) 및 Track A / Track B 구분**
   - **연결된 Figma Node URL 목록 (Figma MCP 조회 대상)**
   - **OpenAPI 스키마 및 도메인 계산기(`engine/`) 수정 필요 여부**
   - **해소 대상 미해결 질문(`docs/questions/**/Q-*.md`) 목록**

## Step 2. 정본 · 계산기 · OpenAPI 일괄 개정
1. PO/PM이 승인하면 정본 본문을 인라인 수정한다.
2. 도메인 계산기 로직이나 API 응답 필드가 바뀌면 `engine/` 시나리오와 `contracts/openapi.yaml`을 함께 갱신한다.
3. 중대한 정책 결정인 경우 `docs/adr/ADR-<번호>-<제목>.md`를 함께 생성한다.

## Step 3. 문서 개정이력 기록 및 색인 최신화
1. 수정된 정본 상단의 `## 문서 개정 이력` 표에 버전·일자·담당 PO/PM·영향 화면 코드·POL-* ID·변경 요약을 추가한다.
2. 색인(`canon_index.md`)과 화면별 요약본(`digest/*.md`)을 최신화한다.

## Step 4. Git 내장 변경 지시서(`docs/changes/LATEST_TASK.md`) 배포
1. 개발자와 UIX의 로컬 AI가 `sync-spec.sh` 직후 즉시 읽을 수 있도록 `docs/changes/LATEST_TASK.md`에 아래 내용을 기록하고 커밋한다:
   - **안건 제목 · 정본 버전 · 변경 등급(`L1~L3`) · 영향 화면코드 및 POL-* 태그**
   - **[UIX 파트 지시사항]**: 대상 화면코드, 5대 화면 상태 매트릭스 갱신 요청.
   - **[개발 파트 지시사항]**: 수정 대상 화면코드, 갱신된 OpenAPI 엔드포인트, 계산기 시나리오 번호.
```

---

### 3.4 `/dev-screen` — 개발자 화면 구현 스킬 (지시서 자동 인식 + Code Connect + ASSUMPTION 선진행)

```markdown
---
name: dev-screen
description: 동기화된 LATEST_TASK.md를 읽어 6% 요약본과 UI 소스(Track A 4대 골격 / Track B Figma Code Connect)를 결합 구현하며, 미정의 케이스는 Blocking 여부에 따라 대기 또는 ASSUMPTION 태그를 달고 선진행한다.
---

# /dev-screen (개발자 화면 구현) 실행 절차

## Step 1. 정본·지시서 최신화 및 필요한 요약본만 로드 (6%)
1. `bash scripts/sync-spec.sh`를 실행해 최신 정본을 동기화하고, `LATEST_TASK.md` 및 내 담당 화면 코드를 확인한다.
2. `00_domain_contracts.md`, `contracts/openapi.yaml`, 해당 화면의 `digest/<화면코드>_baseline.md`, `canon_index.md` 해당 구간(±50줄)만 선별 로드한다.

## Step 2. 화면 트랙별 UI 소스 결합
1. **Track A (`ADMN-*` 백오피스)**:
   - `00_ui_system.md`의 **4대 표준 화면 골격** 컴포넌트를 사용하여 정본 `[B]`의 검색필터·표 컬럼·모달을 배치한다.
2. **Track B (`USER-*` 유저 프론트)**:
   - 정본 `[B]`의 Figma Node URL을 확인하고 **Figma MCP**로 시안을 읽는다.
   - 시안이 `Ready for Dev` 상태가 아니거나 5대 화면 상태 매트릭스가 누락된 경우 즉시 리포트한다.
   - **Figma Code Connect**에 매핑된 기존 UI 컴포넌트를 우선 바인딩하며, 임의로 레이아웃 클래스를 변경하지 않는다.
   - 백엔드가 미완성된 경우 `contracts/openapi.yaml`의 Mock 응답 데이터를 바인딩하여 뷰 구현을 완성한다.

## Step 3. 정책 질문 등급별 분기 처리 (Blocking vs ASSUMPTION)
1. 구현 중 미정의 예외 케이스를 발견하면:
   - **금액/권한/상태전이/보안**: 작업을 즉시 멈추고 `docs/questions/<도메인>/Q-<도메인>-YYYYMMDD-<hash>.md`(`blocking: true`)를 생성한 뒤 대기한다.
   - **단순 문구/정렬/경미한 UI 분기**: `docs/questions/<도메인>/Q-*.md`(`blocking: false`)를 남기고, 코드에 `// [ASSUMPTION: Q-ID] <가정 내용>` 주석을 달고 작업을 중단하지 않고 선진행한다 (`🟡 가정 진행` 상태).

## Step 4. 셀프 대조(`/spec-check`) 및 프리체크(`check.sh`)
1. 커밋 전 `/spec-check`를 실행하여 정본 명세, OpenAPI 스펙, Figma 컴포넌트 충족 여부를 점검한다.
2. `bash scripts/check.sh`를 실행해 Prism 기반 계약 테스트와 정답셋을 통과시킨다.
3. 테스트 코드 상단에 `// @policy POL-SETT-001`을 원형 그대로 남기고, 커밋 메시지에 화면 코드와 정책 ID를 남긴다:
   - 예: `feat(settlement): 정산 수동 라인 등록 유효성 보강 (ADMN-SETT-005 · Ref: POL-SETT-001)`
```

---

### 3.5 `/spec-check` — 정본 & Figma & OpenAPI 3각 대조 검수 스킬 (5대 판정 등급)

```markdown
---
name: spec-check
description: 특정 화면 코드 또는 변경분을 Root PRD(비즈니스 규칙), Visual SSOT(Figma MCP 노드), Code SSOT(contracts/openapi.yaml)와 3각 대조하여 5가지 등급으로 판정 리포트를 출력한다.
---

# /spec-check (정본 대조 검수) 실행 절차

## 1. 대조 기준 로드 (Root SSOT + Visual SSOT + Code SSOT)
1. **Root SSOT 로드**: 대상 화면의 `canon_index.md` 해당 절, 최근 개정이력, `digest`, 도메인 계산기 정답셋.
2. **Visual SSOT 로드 (Track별 분리)**:
   - Track A: `00_ui_system.md` 표준 골격 슬롯 준수 여부.
   - Track B: **Figma MCP 노드**를 조회하여 시안의 컴포넌트·입력폼·배지 및 5대 상태 매트릭스 요소 목록.
3. **Code SSOT 로드**: `contracts/openapi.yaml` 엔드포인트 및 요청/응답 스키마.
4. 대응하는 실제 애플리케이션 코드(라우트, 컨트롤러, 뷰, 테스트)를 읽는다.

## 2. 5대 판정 등급 및 리포트 출력 규칙 (파일 수정 금지)

| 판정 | 의미 | 후속 조치 (담당 파트) |
| :---: | :--- | :--- |
| **`❌ 위반/누락`** | • 정본에 명시된 필드·계산식·상태값·POL-* 규칙이 코드에 누락되거나 다르게 구현됨<br>• OpenAPI 스펙 계약 테스트(Pact/Prism) 실패<br>• Figma 시안에 있는 필수 UI 요소가 뷰 코드에 누락됨 | **개발자 코드 수정 필수** (커밋/병합 차단 사유) |
| **`⚠️ 임의 구현`** | • 정본이나 OpenAPI 스펙에 없는 비즈니스 규칙·임의 상태 분기가 질문 등록 없이 코드에 포함됨<br>• UIX 디자이너의 Figma 컴포넌트 구조를 임의 변형함 | **개발자 즉시 제거 또는 사후 승인 요청** (커밋/병합 차단 사유) |
| **`🟡 가정 진행`** | • 비차단 질문에 대해 `// [ASSUMPTION: Q-ID]` 주석을 명시하고 선진행한 상태<br>• 작업 브랜치에서는 통과되나 **main 병합 시에는 1건이라도 남아 있으면 병합 차단** | **피처 개발 지속 가능 / main 병합 전 PO 정본 반영 및 질문 RESOLVED 필수** |
| **`❓ 정본/시안 미정의`** | • 개발 중 발견된 엣지 케이스로, `Q-*.md`(`blocking: true`)가 등록되어 작업이 멈춘 상태 | **`docs/questions/**/Q-*.md` 승인 ➔ PO/PM 정본 보완 대기** |
| **`✅ 일치`** | Root SSOT 비즈니스 규칙, Visual SSOT Figma 컴포넌트, Code SSOT OpenAPI 스키마가 실제 코드 및 테스트와 100% 일치함 | **통과 (PR 병합 승인)** |
```

---

## 4. 파트별 사람이 지켜야 할 협업 규약 (Human Governance) & `AGENTS.md` 헌법

다수의 **PO/PM**, **UIX 디자이너**, **개발자(FE/BE)**가 함께 일할 때 파이프라인이 끊기지 않기 위한 핵심 약속이다. 이 규칙들은 저장소 루트의 **`AGENTS.md`**에 기록되어 모든 AI 에이전트(Claude Code 등)에게도 행동 헌법으로 강제된다.

1. **[전 파트 공통] 정책 변경 시 정책 추적 ID(`POL-*`)를 반드시 명기하고 전파한다**
   - PRD 수정, Figma 시안 색인, API 스키마 description, 테스트 코드 주석(`// @policy POL-*`), 커밋 메시지까지 동일한 `POL-*` 키를 남겨, AI가 1초 만에 전수 영향도를 파악할 수 있도록 한다.
2. **[PO/PM] 구두 지시 대신 `/doc-update`로 정본과 `LATEST_TASK.md`를 Git에 먼저 올린다**
   - 구두나 메신저 지시는 `/spec-check`에서 위반(`❌`)으로 차단된다. 질문(`Q-*.md`)에 대한 답변 역시 PRD 정본에 반영 커밋하기 전까지는 종결(`RESOLVED`)하지 않는다.
3. **[UIX 디자이너] 5대 화면 상태 매트릭스를 완비하고 `Ready for Dev`로 확정한다**
   - 와이어프레임이 없는 대신 정상·로딩·빈화면·에러·권한없음 5대 상태를 시안에 완비하고, "미바인딩 값 0개, Detach 인스턴스 0개" 린트를 통과한 시안만 `Ready for Dev`로 올린다.
4. **[개발자] `Blocking` 질문은 대기하고, 단순 분기는 `[ASSUMPTION:]` 태그를 달고 선진행한다**
   - 금액·권한·상태전이 등 비즈니스 핵심 규칙 공백은 즉시 멈추고 `Q-*.md`(`blocking: true`)로 올린다. 단순 문구·정렬은 `// [ASSUMPTION: Q-ID]` 태그를 달고 코딩을 선진행(`🟡 가정 진행`)하되, main 병합 전에 반드시 정본에 반영되게 한다.
5. **[에이전트 거버넌스] `AGENTS.md` 헌법을 준수하며, 임의로 정본과 다른 규칙을 창작하지 않는다**
   - 모든 AI 에이전트는 Root SSOT를 절대 기준으로 삼으며, 모호한 요구사항은 임의로 지어내지 않고 도메인별 질문 파일(`Q-*.md`)로 등록하여 인간의 승인을 받는다.
