# dev_spec · prototype_dev 인수인계 (새 세션은 이 파일만 읽고 이어간다)

갱신: 2026-10-27 01:40 · 담당 스레드 "개발 서버 환경에 접속하고 테스트 진행"(총괄)

## 목표 (white · 코디네이터 합의 2026-10-27)
- 개발 코드 기준으로 맞춘 프로토타입을 만든다.
  - 디자인 · 배치 · 업무 규칙 = `prototype_clean` + 정본(README · PROJECT_STATE 우선순위)
  - 이름 · 연결(라우트 · 필드명 · DB 컬럼 · 권한 단위 · JS id) = 개발 코드 `D:\Work\sanjunmo`(읽기 전용, `git pull origin dev`만)
  - 개발 화면 배치는 따르지 않는다.
- 산출물(새 폴더만)
  - `dev_spec/<프로토타입 파일 코드>.md` — 화면별 개발 명세(형식: `dev_spec/README.md`)
  - `prototype_dev/<파일>.html` — prototype_clean 사본에 개발 이름을 입힘. 화면마다 "개발에만 있음 / 프로토타입에만 있음" 표시
- 개발 미구현 화면도 기다리지 않는다(white 10-27): 프로토타입 그대로 + 개발 명명 규칙만 적용, "개발 미구현, 규칙 기반 명명" 표시.
- 2차 개발 항목이라도 프로토타입이 있으면 포함(white 10-27): 권리자(강사) 로그인 화면 · 파트너 센터(PTNR-001) · 공급사(VEND-001) · 역할별 시작 화면 등 → 규칙 기반 명명.
- UI · 디자인은 언제나 프로토타입 것(white 10-27: 개발 UI 요소는 기준에 안 맞는 게 많다). 개발 화면 배치 · 요소를 가져오지 않는다. 모달 ↔ 별도 화면 판단은 Prototype check 세션의 `scripts/qa/reports/review/findings/PAGE_PATTERN.md` · `PAGE_INVENTORY.md` 결정을 따른다(prototype_clean 통합 커밋에 반영되어 오므로 다시 맞추면 따라온다).
- 정책 질문은 별도 보고 없이 `scripts/qa/reports/review/findings/POLICY_QUEUE.md`에 white 형식(개요 표: 번호 · 메뉴/화면 · 정책 · 권고 · 긴급도 / 항목별: 정본 문구 · 현재 상태 · 선택지 장단점 · 권고 근거 · 유사 서비스 사례 · 법령 + 출처, 근거가 약하면 그렇게 적기)으로 추가한다. 이 작업 번호 접두사 `D-`.

- 후순위(white 10-27): 프로토타입이 있는 화면을 모두 끝낸 뒤, 정본(통합 설계서 · 정산 00~04권)에 정의됐지만 프로토타입이 없는 2차 기능 화면(권리자/강사 화면 등)도 새로 만든다 — 정본 내용 + 프로토타입 디자인 + 개발 명명 규칙, "정본 기반 신규, 프로토타입 없음" 표시. 먼저 후보 목록을 아래 "신규 후보"에 적고, 정본 빈틈은 POLICY_QUEUE로.

- 더 후순위(white 10-27): 정본에 근거가 아예 없는 화면(예: 물류대행사(3PL)용 화면)도 관련 기능(주문 · 배송 · 교재 출고 등)에서 추론해 만든다. "추론 기반 신규, 정본 근거 없음" 표시 + 화면마다 추론 근거 목록. 핵심 가정은 POLICY_QUEUE(`D-`)에 확인 항목으로 올리되 막히지 않는다.
- 로컬 커밋은 `dev_spec/` · `prototype_dev/`만. 푸시는 이 세션 권한 설정에서 막혀 있어 white가 직접 하거나 권한을 연다(v6.68 · v6.69는 Prototype check 세션이 푸시함. 새 커밋은 코디네이터에게 알리고 푸시를 맡긴다. 통합 커밋은 v6.70 예약 → 이 작업은 v6.71부터).

## 규칙
- `prototype/` · `prototype_clean/` · 공통 파일(`common-*.js` · `common-v84.css`) · 다른 세션 파일은 건드리지 않는다.
- 커밋은 `git add dev_spec prototype_dev`만. main 직접 커밋, 메시지 `v<버전> DEV-SPEC <요약>`(버전은 커밋 직전 `git log`로 +1). 다른 세션의 미커밋 변경을 섞지 않는다.
- 정책 질문(정본에 없는 업무 규칙 · 값 의미)은 아래 "white에게 물을 것"에 모으고 막히지 않는다. 정본 근거가 분명하면 그냥 한다.
- 개발 백오피스(https://dev.sanjunmo.com/sj-admin/)는 열람만. 비밀번호는 기록하지 않는다.

## 분업
| 그룹 | 화면 | dev_spec 담당 | prototype_dev 담당 |
|---|---|---|---|
| 1 회원 | USER-001(USER-001~006 포함) · USER-007 | 이 스레드 | 이 스레드 |
| 2 상품 · 강사 | PROD-001~007 · BOOK-001 · INST-001 · 002 | 이 스레드(에이전트) | 이 스레드 |
| 3 주문 · 환불 | ORD-001 · RFD-002 | 이 스레드(에이전트) | 이 스레드 |
| 4 정산 | SETT-001 · 002 · 004~009 · 011 · PTNR-001 · VEND-001 | "Check dev repo for API spec" 스레드(커밋 안 함) | 이 스레드 |
| 5 게시판 · 프로모션 | BRD-001 · 002 · 005 · 007 · PROM-001 · 002 | 같은 스레드 | 이 스레드 |
| 6 설정 · 기타 | CONF-001~005 · 010 · DASH-001 · LOGIN-001 | 같은 스레드 | 이 스레드 |
| 7 2차 · 역할별 화면 | PTNR-001 · VEND-001 · 00_WORKFLOW_GUIDE · 각 파일 안 권리자/강사 · 역할별 view | 그룹 4 스레드가 PTNR · VEND 명세, 나머지는 이 스레드 | 이 스레드(규칙 기반 명명) |

다른 스레드가 만든 dev_spec 파일은 이 스레드가 형식 확인 후 함께 커밋한다.

## 순서와 타이밍
1. 공용 색인 `python dev_spec/_tools/extract_dev.py` → `dev_spec/_index/` (routes · requests · schema · progress · meta). dev를 pull하면 다시 돌린다.
2. 시범 USER-001: dev_spec + prototype_dev. 원본은 prototype_clean 현재 작업 트리(다른 세션이 회원관리 수정 중, 미커밋) — 화면별 원본 상태를 기록하고 통합 커밋 후 다시 맞춘다.
3. dev_spec은 모든 그룹 병렬(prototype_clean과 무관).
4. prototype_dev 확장 사본은 prototype_clean 통합 커밋("Prototype check" 세션) 뒤에 만든다.

## 화면별 상태 (10-27 v6.85 기준 — 전 화면을 v6.84 원본으로 다시 맞춤, 39개 검사 통과, 모달 결함은 v6.84 공통 수정으로 해소)
- dev_spec 명세: 프로토타입 화면 38개 전부 + 신규 PTNR-002 · 003 (00_WORKFLOW_GUIDE는 안내 문서라 제외). 기준 dev d562524a.
- prototype_dev: 38개 전부 + 신규 2개. 모두 `check_dev_screen.py` 통과(clean과 같은 동작 · 오류 0 · onclick 누락 0). 원본 상태는 `prototype_dev/_SOURCES.md`.
- 원본이 v6.72 이후 다른 세션 미커밋 상태에서 맞춘 화면: BOOK-001 · INST-001(그 세션 커밋 후 apply 다시). SETT-008 · 009 · VEND-001은 v6.72 다음 커밋 기준.
- clean 원본 결함(코디네이터에 전달, prototype_dev는 clean 따라감 — 고쳐지면 apply 다시): 모달이 안 열림(핫픽스 인라인 display) — SETT-002 modalCarryoverP1 · SETT-008 전환 승인 · PROD-003 강의/교재 선택 · PROD-004 가채번/SKU/재고 · USER-007 파기 결과 · PROM-002 modal-p1/modal-point · BRD-001 modal-faq-cat · PROD-005 · 007 일부(버튼 클릭으로는 열림). LOGIN-001 [5회 실패 잠금 시연] TypeError(문구 치환기가 #lockout-account 괄호 삭제).
- 일괄 다시 맞추기: `for c in $(ls dev_spec/_maps | sed 's/.py//'); do python dev_spec/_tools/apply_dev_map.py $c; done` 후 `check_dev_screen.py` 전체. 건수 불일치는 그 map만 고친다.
- 알려진 도구 한계: 원본 줄 끝이 섞인 파일(PROD-004)은 prototype_dev에서 LF로 저장됨(새 파일이라 영향 없음).

## 결정 기록
- 2026-10-27 prototype_dev 이름 입히는 방식: 프로토타입 JS가 기대는 것(라디오 name · value, 내부 코드값, JS가 id로 찾는 입력)은 동작을 지키려고 그대로 두고 `data-dev-name` · `data-dev-value`로 개발 이름을 단다. JS가 안 쓰는 입력에는 실제 `name=`을 개발 이름으로 넣고, 모달 id는 개발 레이어 id로 바꾼다(참조 전부). 동작 버튼에는 `data-dev-route` · `data-dev-method` · `data-dev-url` · `data-dev-perm`. 개발에만 있음 = `data-dev-flag="dev-only"`(정본 디자인으로 추가), 프로토타입에만 있음 = `data-dev-flag="proto-only"`. 오른쪽 아래 [개발 매핑] 버튼(`prototype_dev/dev-overlay.js`)으로 겹쳐 본다.
- 2026-10-27 prototype_dev는 손으로 고치지 않는다. `dev_spec/_maps/<코드>.py`(찾을 문구 · 바꿀 문구 · 기대 건수) + `python dev_spec/_tools/apply_dev_map.py <코드>`로 만든다. prototype_clean이 바뀌면 다시 돌리고, 건수 불일치만 map을 고친다. 원본 상태는 `prototype_dev/_SOURCES.md`.
- 2026-10-27 dev_spec 파일 단위 = 프로토타입 HTML 1개(하위 S · P 화면 포함). 개발 화면 코드별로 절을 나눈다.
- 2026-10-27 추출 스크립트는 `dev_spec/_tools/`에 둔다(개발 커밋이 바뀔 때마다 다시 맞추는 산출물 생성기라 저장소에 남김).
- 메뉴 데이터는 DB에만 있다. 회원관리 5개 메뉴는 10-26 개발 서버에서 확인(`admin.members.index` · `members.course.index` · `member-progress.index` · `members.blacklist.index` · `members.group.index`). 나머지는 개발 백오피스 메뉴 관리 화면 열람이 필요.

## white에게 물을 것 (아침 확인용)
- (아직 없음)

## 신규 후보 (후순위 — 프로토타입 있는 화면을 끝낸 뒤)
개발 진행표 108개 화면 코드는 모두 어느 프로토타입 파일 안에 있다(10-27 대조, 하위 S · P 7개만 코드 표기 없이 들어 있음). 그래서 신규는 외부 소속(권리자 · 거래처) 화면 위주다.

| 후보 | 구분 | 근거 | 비고 |
|---|---|---|---|
| 거래처(3PL 물류 대행사) 파트너 화면 — 출고 대상 · 송장 등록/벌크 업로드 · 배송 상태 · 월 물류비 청구 내역 | 추론 기반 신규, 정본 근거 없음(소속 규칙만 있음) | README 1절 5항(소속 3종 · 거래처 유형 · 본인 바인딩 2단 통제), ORD-002 · ORD-002-P1 송장 벌크 업로드, SETT-011 물류비 대사, 개발 `config/admin.php` landing `logistics` → `admin.deliveries.index`(내부 물류팀) | 가정: 3PL은 자사 출고분만 보고, 개인정보는 배송에 필요한 범위(이름 · 연락처 · 주소)만 노출 → POLICY_QUEUE D- |
| 거래처(매입처 · 도서 공급사) 파트너 화면 — 공급 원장 · 입고/반품 · 매입 정산 확인 · 세금계산서 | 추론 기반 신규 | README 84줄(VEND-001 매입처), BOOK-001 도서 공급 원장, 정산 01권 도서 · 이월 | 가정: 매입 정산서는 권리자 정산서(SETT-002-S2) 형식을 따름 |
| 권리자 파트너 센터 확장 — 계약 상세 열람 · 마일스톤 증빙 제출(INST-002) | 정본 기반 신규(PTNR-001 보강) | INST-001-S2 · INST-002, 정산 03권 | PTNR-001 prototype_dev 끝난 뒤 판단 |
| 파트너 공통 로그인 · 비밀번호 찾기(외부 소속) | 정본 기반(LOGIN-001 규칙 재사용) | LOGIN-001, README 소속 규칙 | 개발은 관리자 로그인 하나 |

## prototype_dev 확장 (v6.72 통합 커밋 기준, 10-27 시작)
- 도구: `apply_dev_map.py <코드>`(map 적용) → `check_dev_screen.py <코드>`(clean과 같은 동작 · 오류 0 · onclick 누락 0 · VERIFY 같음). 견본 map `_maps/ADMN-USER-001.py`(VERIFY 포함).
- USER-001은 v6.72 원본으로 다시 맞춤(138항목 그대로 맞음, 검사 통과).
- 그룹별 에이전트가 `_maps/<코드>.py`를 쓰고 두 도구를 통과시킨다. 진행은 아래 화면별 상태 표.

## 정책 질문 정리 (10-27 진행 중)
- 그룹 4~6은 보조 스레드가 끝냄: `scripts/qa/reports/review/findings/devspec/POLICY_D_00_요약.md` · `_SETT` · `_BRD` · `_CONF`(git 제외 폴더, 로컬 전용). 나머지도 같은 폴더 · 형식(A/B/C 분류, 개요는 C만, 번호 D-<그룹>-NN)으로 맞춘다.
- 에이전트 2팀: 상품 · 강사 · 도서 → `dev_spec/_drafts/POLICY_D_PROD.md`(D-P..), 주문 · 정산 · 게시판 · 설정 → `_drafts/POLICY_D_OPS.md`(D-O..). 신규 화면 가정 → `_drafts/POLICY_D_PTNR-002/003.md`.
- 끝나면 총괄이 표본 대조 후 `scripts/qa/reports/review/findings/POLICY_QUEUE.md`에 D- 절로 합친다.
- USER-007 명세 에이전트 실행 중. 00_WORKFLOW_GUIDE는 작업 안내 문서라 명세 대상 아님.

## 신규 화면 진행
| 코드(규칙) | 화면 | 상태 | 산출물 |
|---|---|---|---|
| ADMN-PTNR-002 | 거래처(3PL) 파트너 센터 | 완료(검증 76항목 · 오류 0, 정책 D-PTNR2-01~09) | prototype_dev/ADMN-PTNR-002_baseline.html · dev_spec/ADMN-PTNR-002.md · dev_spec/_drafts/POLICY_D_PTNR-002.md |
| ADMN-PTNR-003 | 거래처(매입처 · 도서 공급사) 파트너 센터 | 완료(검증 36항목 · 오류 0, 정책 D-PTNR3-01~10) | 같은 형식 |
- 신규 화면 정책 가정은 `findings/devspec/POLICY_D_PTNR2.md`(9건) · `POLICY_D_PTNR3.md`(10건). 진입 파라미터는 개발 suppliers.code 형식 `?vendor=SUP-NNNN&role=RG-08|RG-09`. common-snb.js는 PTNR-001처럼 로드하지 않음.

## 다음 할 일
- 로컬 커밋만 함, 푸시는 white 확인 대기.
- 그룹 2 · 3 dev_spec 에이전트 3개를 한도 해제 후 이어서 실행 중(10-27 02:1x)(PROD-001~004 / PROD-005~007 · BOOK-001 · INST-001 · 002 / ORD-001 · RFD-002). dev_spec/에 파일이 생겼는지 보고, 없으면 같은 지시(README 형식 + USER-001 예시)로 다시 맡긴다.
- 그룹 4~6 dev_spec은 "Check dev repo for API spec" 스레드 산출물 — 형식 확인 후 함께 커밋.
- prototype_clean 통합 커밋 뒤: USER-001 apply 다시 + 나머지 화면 map 작성(`_maps/ADMN-USER-001.py`가 견본). 검증은 clean과 dev를 같은 동작으로 돌려 에러 0 · 결과 동일 확인.
- 정책 질문은 POLICY_QUEUE.md `D-` 접두사(회원관리는 M- 항목과 겹치므로 새로 만들지 않음).
- 그룹 2~6 메뉴는 개발 백오피스 메뉴 관리 열람으로 확인 필요.
