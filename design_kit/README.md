# design_kit — 산준모 관리자 디자인 키트 (개발팀 · 개발 AI용)

개발 관리자 화면(`lcampus/sanjunmo`, Laravel Blade)을 **프로토타입 디자인**으로 바꾸기 위한 키트다.
프로토타입(`prototype_clean/`)이 디자인 정본이고, 개발 코드의 **id · 폼 name · JS 동작은 그대로 둔다**.

- 기준: 프로토타입 `prototype_clean` (2026-10-27) · 개발 `dev` `ee0d5abd` (2026-10-27)
- 만든 곳: 정본 저장소 `whiteceo/sanjunmo-settlement` `design_kit/`

## 원칙
1. **디자인 = 프로토타입.** 색 · 글꼴 · 크기 · 여백 · 둥글기 · 그림자 · 상태 색은 이 키트를 따른다. 개발 화면의 기존 모양은 따르지 않는다.
2. **동작 = 개발.** 마크업 구조 · id · name · data-* · JS 가 붙이고 떼는 상태 class 는 바꾸지 않는다.
   - SNB 는 **모양만** 바꾸고 접기 · 펼치기(아코디언, `custom.js` 722~806줄)는 그대로 쓴다.
   - 모달(`layer__open` · `layer-pop--close` · `layer-pop--hidden` · `layer_pop--show`), 탭(`tab__item--active` · `tab__content--active`), 프로필 드롭다운, 세션 연장, 선택 레이어, 사유 모달, 마스킹 해제, 드래그 정렬 모두 그대로.
   - 바꾸면 안 되는 이름 전체 목록: `CLASS_MAP.md` 의 "JS 의존" 열.
3. **class 를 바꾸지 말고 CSS 를 덮는다.** `sjm-dev-skin.css` 는 개발 class 이름에 프로토타입 모양을 입힌다. 그래서 1단계는 Blade 를 거의 고치지 않고 끝난다.
4. 화면 배치(어느 항목이 어느 칸에 있는지)는 화면별 명세 `dev_spec/<화면코드>.md` 와 프로토타입 HTML 을 본다. 이 키트는 **공통 모양**만 다룬다.

## 파일
| 파일 | 내용 |
| :--- | :--- |
| `tokens.css` | 디자인 토큰(CSS 변수 `--sjm-*`): 색 · 글꼴 · 글자 크기 · 컨트롤 높이 · 둥글기 · 그림자 · 골격 폭 |
| `sjm-dev-skin.css` | 개발 class 이름 그대로 프로토타입 모양을 입히는 CSS(머리 · SNB · 본문 · 버튼 · 입력 · 검색 · 표 · 페이지 번호 · 탭 · 모달 · 배지) |
| `CLASS_MAP.md` | 개발 class ↔ 프로토타입 기준 대응표 + JS 의존 표시 |
| `COMPONENTS.md` | 화면 요소별 마크업 가이드 1장(새 화면 · 화면 개편 때 쓰는 마크업과 규칙) |
| `img/sjm_logo-horizontal-white.png` | 남색 바탕용 흰 로고(머리 왼쪽 로고 칸) |
| `preview/dev-markup-sample.html` | 개발 마크업 표본. 키트를 넣은 뒤 열면 적용 모습 확인, `?skin=0` 은 적용 전 |

프로토타입 JS(`common-snb.js` · `common-master.js`)는 **넣지 않았다.** SNB 를 그리는 코드 · 문구 치환 · localStorage 시드 · 모달 사후 보정 등 프로토타입 시연용 장치라 개발에는 필요 없다(개발은 자기 JS 를 쓴다).

## 적용 순서
### 1단계 — 공통 모양(한 번에, Blade 거의 안 고침)
1. 이 폴더를 개발 저장소 `public/admin/assets/sjm-kit/` 로 복사한다(`img/` · `preview/` 포함).
2. `resources/views/admin/layouts/header.blade.php` 의 CSS 로드 줄에서 `admin-custom.css` **바로 뒤**, `{$currentCss}` · `@stack('styles')`(화면 CSS) **앞**에 두 줄을 추가한다.
   ```blade
   <link rel="stylesheet" href="{{ asset('admin/assets/css/admin-custom.css') }}">
   <link rel="stylesheet" href="{{ asset('admin/assets/sjm-kit/tokens.css') }}">      {{-- 추가 --}}
   <link rel="stylesheet" href="{{ asset('admin/assets/sjm-kit/sjm-dev-skin.css') }}"> {{-- 추가 --}}
   …(currentCss · @stack('styles') 는 그 뒤 그대로)
   ```
   - 화면 CSS 를 키트 뒤에 두는 이유: 3단계에서 화면을 재배치할 때 화면 CSS 가 키트를 덮을 수 있어야 한다.
3. `public/admin/assets/sjm-kit/preview/dev-markup-sample.html` 을 열어 적용 모습을 본다(`?skin=0` 과 비교).
4. 로그인 · 대시보드 · 회원 목록 · 회원 상세 · 등록 폼 · 모달 하나씩 열어 확인한다. 확인할 것: SNB 그룹 열고 닫기, 모달 열기 · 닫기 · ESC, 탭 전환, 검색 · 페이지 이동, 엑셀 · 사유 모달.

### 2단계 — 공통 부품 정리(조금씩 Blade 수정)
- `CLASS_MAP.md` "정리 권장" 표대로 정의 없는 class(`txt--red`, `fm__help`, `text--desc`)를 그대로 써도 되게 키트에 정의해 두었다. 새 코드는 `COMPONENTS.md` 의 이름을 쓴다.
- 버튼 역할이 섞인 곳(취소에 진한 `btn`, 저장에 `btn btn--save` 등)은 키트가 역할별 색으로 맞춘다. 새 버튼은 `COMPONENTS.md` 4절 표를 따른다.
- 검색 버튼 줄, 목록 요약 줄, 폼 하단 버튼 줄은 화면마다 마크업이 같으면 그대로 둔다.

### 3단계 — 화면별(화면 CSS · 배치)
- 화면 전용 CSS(`settlement.css` 의 `st-*`, `admin-custom.css` 의 `fu-` · `promo-` · `dash-` 등)는 화면을 손볼 때 같이 `--sjm-*` 토큰 값으로 바꾼다.
- 배치 · 항목 · 문구는 `dev_spec/<화면코드>.md` 7절(기능 차이)과 프로토타입 HTML 을 따른다.

## 화면 CSS 쓰는 법(3단계)
- 키트 선택자는 `body .클래스` 무게다. 화면 CSS 에서 키트가 이미 다루는 class(`.select` · `.btn*` · `.input__text` · `.table__list` · `.badge` · `.text--warning` 등)를 고칠 때는 **화면 wrapper class 를 붙여** 같은 무게 이상으로 쓴다.
  ```css
  /* 회원 목록 화면 — <section class="mbr-list"> 안에서만 */
  body .mbr-list .select { width: 84px; min-width: 0; }
  body .mbr-list .table__list td { white-space: normal; }
  ```
- 새 class(화면 접두어, 예: `mbr-kpi__card`)는 키트와 겹치지 않으므로 그냥 쓴다. 값은 `var(--sjm-*)` 토큰을 쓴다.
- 개발 공통 CSS 의 예외 규칙도 확인한다(예: `admin-custom.css` 의 `.masked { font-family: 'Courier New' }` — 표 안에서 줄바꿈을 일으키면 화면 CSS 에서 `body .화면 .masked { font-family: inherit; }`).

## 개발 AI 에게 줄 지시 예
> `design_kit/README.md` · `CLASS_MAP.md` · `COMPONENTS.md` 를 읽고 1단계를 적용해라. id · name · data-* · JS 가 쓰는 class(`CLASS_MAP.md` JS 의존 열)는 바꾸지 마라. SNB 접기 · 펼치기는 지금 동작을 유지한다. 적용 후 `preview/dev-markup-sample.html` 과 실제 화면 다섯 개를 열어 확인해라.

## 고친 이력
- 2026-10-27 v6.91 첫판.
- 2026-10-27 보정(USER-001 Blade 시험에서 발견): ① `text--warning` · `txt--red` 는 색만 바꾸고 크기는 입력 아래 오류 문구에서만 11.5px(KPI 숫자 등이 작아지던 문제) ② `badge--soft` 앞 점 숨김(프로토타입 배지에 없음) ③ 로드 순서를 키트 → 화면 CSS 로 바꾸고 "화면 CSS 쓰는 법" 추가.

## 검증 기록(키트 작성 때)
- 개발 `admin.css` · `admin-custom.css` · `custom.js`(dev `ee0d5abd`) 위에 키트를 얹어 `preview/dev-markup-sample.html` 을 Chromium 1600×1100 으로 렌더링했다. 콘솔 오류 0건.
- 동작: SNB 그룹 클릭 → 그 그룹만 열리고 나머지 닫힘(아코디언 유지), 탭 클릭 → 해당 `tab__content` 만 표시, `layer__open` → `layer_pop--show` 로 열림(SNB 오른쪽 260px 부터) → `layer-pop--close` → `layer-pop--hidden` 으로 닫힘.
- 계산값: 주 버튼 #2563EB · 32px, 외곽선 버튼 흰 바탕 · #CBD5E1 테두리, 입력 32px · 6px 둥글기, 표 머리 #F8FAFC · 11.5px, SNB #0F172A · 260px, 페이지 제목 16px/800.
