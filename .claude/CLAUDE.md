# CLAUDE.md — 산준모닷컴 정산·백오피스

> 이 문서는 **어떻게 작업하나**를 정한다. 프로젝트 문서는 세 개로 역할을 나눈다.
> | 문서 | 역할 |
> | :--- | :--- |
> | `README.md` | 프로젝트가 무엇인가 — 정본 문서 구조, 핵심 정책·용어, 폴더·마크업 규격, 화면 목록 |
> | `.claude/CLAUDE.md` (이 문서) | 어떻게 작업하나 — 작업 규칙, 검증, 커밋, 동기화 |
> | `PROJECT_STATE.md` | 지금 어디까지 왔나 — 확정 기준, QA 도구, 기준선, 현재 상태·미결, 작업 로그 |
> | `.agents/rules/RULES.md` | 안티그래비티 예비 사용 시 추가 제한 (안티그래비티가 자동으로 읽음) |

## 기본 원칙
- 모든 응답·진행 메시지·요약은 **한국어**로 작성한다.
- 작업 공간은 `D:\Work\` 이다. C 드라이브에 파일·패키지·메모리 등을 설치하거나 저장하지 않는다.
  - 임시 파일, 설정, 메모, 리포트는 모두 프로젝트 폴더(`D:\Work\Settlement\`) 안에 둔다.
  - 기억해야 할 사항은 이 `CLAUDE.md`에 추가한다.
- 폴더 원칙
  - 에이전트·도구 전용 파일은 그 도구의 점 폴더에, 공용 파일(문서·코드·QA 도구)은 그 밖에 둔다.
  - 점 폴더 이름은 도구가 스스로 읽는 이름을 따른다: Claude Code `.claude/`, 안티그래비티 `.agents/`(이름이 일반적이지만 안티그래비티 전용), VS Code `.vscode/`. 이름을 바꾸면 도구가 못 찾는다.
  - 새 도구를 쓰면 그 도구의 점 폴더만 추가하고, 그만 쓰면 그 폴더만 지운다.
- C 드라이브 예외: Claude 앱·계정 설정(`C:\Users\white\.claude`), 안티그래비티 전역 설정(`C:\Users\white\.gemini`), Python과 패키지, Playwright 브라우저처럼 PC에 한 번 설치해 여러 에이전트가 같이 쓰는 도구.

## 작업 시작 전
1. `git pull origin main` — Apps Script가 구글 드라이브에서 고친 문서를 GitHub에 커밋하므로 반드시 먼저 받는다. 안 받으면 드라이브 수정분을 옛 버전으로 덮어쓸 수 있다.
2. `PROJECT_STATE.md`의 확정 기준(1절)과 현재 상태·미결(4절)을 확인한다. 정책·화면 목록은 `README.md`.
3. 대형 HTML(1,000줄 이상)은 통째로 읽지 않고 grep으로 필요한 줄만 본다.

## 역할 (2026-10-22 확정)
| 주체 | 역할 |
| :--- | :--- |
| Claude Code | 주 작업자. 진단, 패치 작성·실행, Playwright 검증, 커밋·푸시까지 한곳에서 수행 |
| 안티그래비티 | 예비. Claude 사용 한도가 소진됐을 때만 QA 실행·조사·단순 문구 교체. 범위와 제한은 `.agents/rules/RULES.md` |
| white | 요구사항·증상 지정, 커밋 전 diff 승인, 드라이브에서 문서 직접 수정 |

젠스파크(이전 설계·스크립트 작성 담당)는 2026-10-22부로 사용하지 않는다.

## 구글 드라이브 동기화 (2026-10-22 가동)
- Apps Script(`scripts/gas/sync_settlement.gs`)가 GitHub `main` ↔ 공유 문서함 `산준모 닷컴/04.설계서/정산시스템`을 6시간마다 양방향 동기화한다. `_archive/backup/`은 제외.
  - 드라이브에서 고친 파일은 `drive-sync:` 커밋으로 올라온다 → 작업 전 `git pull` 필수.
  - 양쪽이 같은 파일을 고치면 원래 이름엔 GitHub 버전, 드라이브 버전은 `_drive충돌_` 사본으로 남고 메일이 온다.
  - 동기화 스크립트를 고치면 `sync_settlement.gs`와 Apps Script 편집기 양쪽에 반영한다. 토큰(`GH_TOKEN`)은 스크립트 속성에만 둔다.
- 예전 방식은 쓰지 않는다.
  - `sync_to_gdrive.ps1`: 커밋마다 `04.설계서/docs`에 덮어쓰던 스크립트. v6.4에서 삭제(git 이력에만 있음). 되살려 실행하지 않는다.
  - 이 PC의 `.git/hooks/post-commit`은 `post-commit.disabled`로 꺼둠. 되살리지 않는다.
  - 예전 사본 폴더 `04.설계서/docs`는 2026-10-22 삭제했다. 이제 `04.설계서` 아래에는 `정산시스템/`(동기화 대상)과 `User_Wireframe/`(저장소와 무관)만 있다.

## 문서 정본 위치
- `docs/산준모닷컴 구축 통합 상세 설계서.md`는 프론트와 백오피스를 함께 다루는 상위 문서지만, 정본은 이 저장소 `docs/`에 둔다(드라이브에서는 `04.설계서/정산시스템/docs/`). 다른 곳에 사본을 만들지 않는다(2026-10-22 결정).
- 문서 우선순위는 `PROJECT_STATE.md` 1절을 따른다.

## 수정 작업 규칙
- 기능 패치는 `prototype/`·`prototype_clean/` 동명 파일에 동시 반영한다. 두 폴더의 성격 차이와 확정 기준은 `PROJECT_STATE.md` 1절을 따른다.
- 줄 번호가 아니라 문구로 찾는다. 대상 건수가 기대값과 다르면 전체 중단하고 파일을 바꾸지 않는다.
- 스크립트로 일괄 수정할 때
  - 저장 전 `_archive/backup/v<버전>_<시각>/` 에 백업한다(`.gitignore` 등록, 로컬 전용).
  - 저장 후 Playwright로 해당 동작을 검증하고, 실패하면 원본으로 되돌린다.
  - 상단에 `sys.stdout.reconfigure(encoding="utf-8")`, 파일 입출력은 `newline=""`로 CRLF/LF를 보존한다.
  - 패치·진단 스크립트와 리포트는 저장소에 남기지 않는다. 검증 결과 요약은 커밋 메시지 본문과 `PROJECT_STATE.md` 작업 로그에 적는다. 지난 산출물은 git 이력에서 꺼내 본다(2026-10-22 v6.4에서 `_archive/`와 예전 리포트 정리).
  - QA 스크립트 출력은 `scripts/qa/reports/`에 쌓이며 `.gitignore`에 등록돼 있다.
- 화면 문구 검사는 HTML grep이 아니라 Playwright 렌더링 기준으로 한다(`prototype_clean/common-snb.js`가 로드 후 문구를 런타임 치환).

## 읽기 · 수정 효율 (2026-10-26, 문서 · HTML이 크고 두 폴더라서)
- `docs/screen_spec/`(화면설계서)는 프로토타입을 따라가는 문서로, 별도 에이전트가 프로토타입 기준으로 고친다. 여기서는 수정하지 않고, 프로토타입을 바꾸면 화면별 변경 요지를 `scripts/qa/reports/review/SPEC_SYNC.md`에 남긴다(2026-10-26 white). 화면설계서와 프로토타입이 다르면 프로토타입(정본 기준)이 맞다.
- 정본 · screen_spec은 통째로 읽지 않는다. 화면 코드별 위치 색인(`scripts/qa/reports/review/canon_index.md`)에서 문서 · 절 · 줄을 찾아 그 근처만 읽는다. 색인이 낡았으면 다시 만든다(생성 방법은 `PROJECT_STATE.md` 2절).
- HTML도 통째로 읽지 않는다. `python scripts/qa/build_screen_digest.py`로 만든 화면 요약본(`scripts/qa/reports/digest/<파일>.md`, 원본의 약 6%, 원본 줄 번호 포함)을 먼저 보고 필요한 줄만 연다.
- 두 폴더 수정은 `prototype_clean`을 한 번 고치고 `python scripts/qa/mirror_patch.py --from prototype_clean --to prototype`로 같은 변경을 옮긴다. 건너뛴 hunk(문구가 다른 줄)만 손으로 옮긴다. 마지막에 `python scripts/qa/skill_pair_diff.py`로 두 폴더 로직 · 구조 차이 0을 확인한다.
- 에이전트 분업: 조사 결과는 파일(`scripts/qa/reports/review/findings/`), 최종 응답은 한 줄. 총괄이 건수는 파일에서 세고 근거는 원문과 대조한 뒤 판정(`decisions.md`). 수정은 파일이 겹치지 않게 나눠 맡기고, E2E · QA는 마지막에 한 번. 진행은 `STATUS.md` 한 줄씩.
- 개발팀은 이 저장소의 프로토타입과 문서를 기준으로 개발한다(개발 버전과의 동기화는 사람이 오프라인으로 함, 2026-10-26 white). 그래서 기존 값 · 상태 · 코드의 의미를 바꾸기보다 추가를 우선하고, 바꿀 때는 작업 로그와 `SPEC_SYNC.md`에 바뀐 점을 분명히 적는다.
- 정책(정본에 없는 업무 규칙 · 값의 의미)이 아닌 화면 구성 · 표시 방식 · UX 선택은 목적에 맞게 스스로 정해 구현하고 결과만 보고한다. 묻는 것은 정책 판단뿐(2026-10-26 white).
- 멀티 세션 · 에이전트는 작업마다 효율(파일 겹침 없음, 맥락을 가진 세션에 배정, 대기 시간)을 따져 필요한 만큼 늘려 처리한다(2026-10-26 white).
- 같은 폴더를 다른 세션과 함께 쓴다(화면설계서 살펴보기 세션 등): 작업 전 `git pull`, 수정 전 `STATUS.md`에 담당 파일 기록, 공용 파일(`common-*.js` · `common-v84.css` · `PROJECT_STATE.md` · `README.md`)은 작은 단위로 고치고 커밋 직전 다시 pull, 버전 번호는 커밋 직전 `git log`로 확인 후 +1, `stash` · `reset` · 브랜치 전환 금지. 분담은 `scripts/qa/reports/review/HANDOFF.md`.

## 검증
- E2E(폴더별 2회, UTF-8 출력):
  - `PYTHONIOENCODING=utf-8 python scripts/qa/skill_playwright_e2e.py prototype`
  - `PYTHONIOENCODING=utf-8 python scripts/qa/skill_playwright_e2e.py prototype_clean`
- 기준선: 양쪽 40/40 PASS(v6.51 파트너 센터 추가 후), 콘솔 에러 0건.
- 그 밖의 QA 도구(정적 문법 검사·금지어·화면 간 데이터 대조·괄호 중복 스캔)는 `PROJECT_STATE.md` 2절. 기준선: 정적 문법 오류·에셋 경고 0건, 데이터 대조 오류 0건.

## 커밋 규칙
- 커밋 전에 white에게 diff 본문을 보여주고 승인을 받는다(작성자와 검수자가 같아진 데 대한 교차 검증).
  - 예외(2026-10-26 white): white가 작업 전권을 맡긴 일괄 작업은 E2E · QA가 기준선을 통과하면 승인 없이 커밋 · 푸시하고, 보고에 커밋 목록을 붙인다. 정본에 없는 정책 판단은 이 예외에 들지 않으며 모아서 묻는다.
- `git add`는 경로를 지정한다. `git add -A` / `git add .` 금지(로컬 백업·개인 설정 파일이 섞이는 것 방지).
- `main`에 직접 커밋한다. 메시지 형식: `v<버전> <화면 코드> <요약>`.
- 작업이 끝나면 `PROJECT_STATE.md` 5절 작업 로그에 1줄, 상태가 바뀌면 4절도 갱신한다.

## 알려진 함정
- 공통 모달 닫기 핫픽스(`UNIVERSAL-MODAL-CLOSER-HOTFIX`, 각 HTML 두 번째 `<script>`)는 로드 시 모든 모달 백드롭에 인라인 `display:none !important`를 건다. `hidden` 클래스만 떼서 여는 모달은 열리지 않는다. 열 때 `open` 클래스를 붙이고 인라인 `display`를 지우고, 닫을 때 `open`을 뗀다(SETT-005 v6.0·v6.1 참고).
- clean 공통 CSS(`prototype_clean/common-v84.css` "SAFE CSS PRESENTATION LAYER")는 `.info-callout`, `.policy-banner`, `.policy-note`, `.rule-banner` 등을 기획 설명으로 보고 숨긴다. 운영자에게 보여야 하는 안내(경고 배너, 모달 안 대상 정보, 권한 안내)는 이 클래스를 쓰지 않는다(BRD-001 `.ctx-note`, BRD-007 `.access-notice` 참고).
- 역할 그룹 · 1:1 문의 분류 이름을 화면에 직접 적지 않는다. `common-master.js`(`window.SJM_MASTER`)에서 읽는다. 관리 화면에서 바꾼 값은 브라우저 localStorage에 남으므로, Playwright 검증은 새 브라우저 컨텍스트로 시작하고 화면 간 반영은 같은 컨텍스트 안에서 확인한다.
- 일부 HTML은 줄 끝(CRLF/LF)이 섞여 있다. 일괄 수정 스크립트가 줄 끝을 한 가지로 맞추면 내용 변화 없는 파일까지 바뀐다. 한 줄 안의 치환은 원문 그대로(`newline=""`) 적용하고, 여러 줄 치환이 필요하면 대상 파일의 줄 끝이 한 가지인지 먼저 확인한다(v6.24).
- clean 문구 치환기는 원문자(`①~⑭`)를 지우므로 샘플 데이터에도 쓰지 않는다("3번"처럼 쓴다).
- 여러 세션이 같은 작업 폴더를 쓰므로 `mirror_patch.py`는 옮길 파일 이름을 반드시 지정한다. 생략하면 다른 세션이 고치는 중인 clean 파일까지 prototype에 옮긴다. 공통 파일(`common-*.js` · `common-v84.css`)은 폴더별 내용이 달라 mirror 대상에 넣지 않는다(2026-10-27).
- Git Bash의 `grep -c $'\r'`는 CRLF 파일에서도 0을 낼 수 있다. 줄 끝은 Python(`b.count(b'\r\n')`)으로 확인한다(2026-10-27).
- 하위 화면(S) 페이지 전환은 공통 `SJM_PAGE`(`common-snb.js`)로 한다. 사용법 · 함정은 `scripts/qa/reports/review/findings/PAGE_PATTERN.md`(2026-10-27).
- 앱 파일 미리보기 · 앱 브라우저에 HTML을 파일로 바로 열거나 구글 드라이브 미리보기로 보면 정적 사본이라 `common-snb.js` 등 옆 파일이 안 붙어 SNB가 보이지 않는다. 앱에서는 미리보기 설정 `prototype`(`.claude/launch.json`, `http://localhost:8765/prototype_clean/...`)으로, 그 밖에는 크롬으로 파일을 직접 연다(2026-10-26).
