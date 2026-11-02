"""ADMN-BRD-005 → prototype_dev 변경 목록. 근거: dev_spec/ADMN-BRD-005.md
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


# ── 머리: 개발 매핑 표시 ───────────────────────────────
DEV_MAP = {
    "code": "ADMN-BRD-005",
    "devCommit": DEV_COMMIT,
    "progress": "구현(BRD-005 · 005-S1 · BRD-010 · 010-S1). 수강후기/합격수기 분리 탭 · 진도율 · 별점 · 후기 보상 회수 · 버전 이력은 개발 없음 — 주황 표시. v3.2.32(2026-11-02) 무료콘텐츠 SHORTS 구분 · 매일 1문제 머리말(head_code) · 유튜브 영상 ID(video_id) · 기출문제 명칭은 개발 미구현",
    "menus": [
        {"route": "admin.reviews.index", "label": "수기 / 합격 후기 관리"},
        {"route": "admin.free-contents.index", "label": "무료콘텐츠 관리"},
    ],
}
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <link rel="stylesheet" href="dev-overlay.css" />\n'
    '  <script type="application/json" id="dev-map">' + json.dumps(DEV_MAP, ensure_ascii=False) + "</script>\n"
    '  <script src="dev-overlay.js" defer></script>\n')))

# ══ v3.2.32 정본 변경(설계서 b017da2, 2026-11-02 white) — 무료콘텐츠 3구분 · 기출문제 명칭 · 무료강의 가림 ══════════
# prototype_clean은 아직 안 바뀜 → prototype_dev에만 반영. 아래 항목은 clean 원문 기준으로 먼저 바꾸고, 뒤의 개발 이름 항목이 그 결과에 붙는다.
V = "v3.2.32"
OPS.append(dict(kind="insert_before", anchor="</head>", html=(
    '  <style>/* v3.2.32 SHORTS 썸네일 자리 — 프로토는 네트워크 없이 자리만, 개발은 i.ytimg.com/vi/{video_id}/mqdefault.jpg */\n'
    '    .fl-yt-thumb { width:36px; height:64px; flex:none; border-radius:6px; background:#0f172a; color:#fff; display:flex; align-items:center; justify-content:center; font-size:13px; }\n'
    '  </style>\n')))
# 화면 이름 · 탭 · 설명 — '빈출자료' → '기출문제'(S2-08 기출문제 표기 금지 폐지), 구분 3종
R("수강후기·합격수기·무료콘텐츠(빈출자료·매일 1문제) 관리", "수강후기·합격수기·무료콘텐츠(기출문제·매일 1문제·출퇴근 1분 산안기) 관리")
R("무료콘텐츠(빈출자료 · 매일 1문제)</h1>", "무료콘텐츠(기출문제 · 매일 1문제 · 출퇴근 1분 산안기)</h1>")
R("빈출자료 · 매일 1문제 무료콘텐츠를 관리합니다. 무료특강 영상은 강의 · 강좌 관리에서 등록합니다.",
  "기출문제 · 정조교의 매일 1문제 · 나나조교의 출퇴근 1분 산안기 무료콘텐츠를 관리합니다. 무료강의(맛보기 강의) 영상은 강의 관리에서 등록하며 프론트 메뉴는 1차에서 가립니다.")
R("📝 무료콘텐츠 (빈출자료 · 매일 1문제) (ADMN-BRD-010)", "📝 무료콘텐츠 (기출문제 · 매일 1문제 · 출퇴근 1분 산안기) (ADMN-BRD-010)")
R("<!-- ==================== 3. 무료콘텐츠 — 빈출자료 · 매일 1문제 (ADMN-BRD-010) ==================== -->",
  "<!-- ==================== 3. 무료콘텐츠 — 기출문제 · 매일 1문제 · 출퇴근 1분 산안기 (ADMN-BRD-010, v3.2.32) ==================== -->")
R("freeLecture: ['ADMN-BRD-010', '무료콘텐츠 관리 (빈출자료 · 매일 1문제)']",
  "freeLecture: ['ADMN-BRD-010', '무료콘텐츠 관리 (기출문제 · 매일 1문제 · 출퇴근 1분 산안기)']")
RE(r"        <strong>\[ADMN-BRD-010\] 무료콘텐츠 운영 정책:</strong>[^\n]*\n",
   "        <strong>[ADMN-BRD-010] 무료콘텐츠 운영 정책:</strong> 사용자 웹 <code>USER-FREE-000 ~ 004</code>에 노출되는 무료 학습 자료입니다. 콘텐츠 구분은 <strong>[기출문제]</strong>(EXAM, 구 빈출자료 — 연도 · 회차 · PDF · 본문) · <strong>[정조교의 매일 1문제]</strong>(DAILY, 머리말 5종) · <strong>[나나조교의 출퇴근 1분 산안기]</strong>(SHORTS, 가제 — 유튜브 쇼츠 게시글) 3가지입니다(2026-11-02 white 결정, 설계서 v3.2.32). 본문은 누구나 열람하고 PDF는 로그인 회원만 받습니다. 무료강의(맛보기 강의, <code>USER-FREE-001</code>)는 이 화면에서 등록하지 않고 강의 관리(<code>ADMN-PROD-002</code> 맛보기)에서 유지하며, 프론트 메뉴는 1차에서 가립니다.\n", 1)
RE(r'      <div class="ctx-note" id="fl-scope-note">\n[^\n]*\n[^\n]*\n      </div>',
   '      <div class="ctx-note" id="fl-scope-note">\n'
   '        이 탭은 <strong>기출문제</strong>(연도 · 회차별 PDF · 본문) · <strong>정조교의 매일 1문제</strong>(머리말 5종) · <strong>나나조교의 출퇴근 1분 산안기</strong>(유튜브 쇼츠 게시글, 가제)를 등록합니다. 본문은 누구나 볼 수 있고 <strong>PDF는 로그인 회원만</strong> 받습니다.\n'
   '        <br/><span class="badge badge-slate" id="fl-free-lecture-hidden" data-dev-flag="proto-only" data-dev-note="무료강의(USER-FREE-001)는 1차 프론트 메뉴 가림 — 개발 프론트 /free/lectures 메뉴 숨김 필요. 관리 화면에는 무료강의 구분 없음(맛보기 is_preview)">무료강의 1차 가림</span> '
   '무료강의(맛보기 강의)는 이 탭의 구분이 아닙니다. 영상은 <a href="ADMN-PROD-002_baseline.html" target="_blank" rel="noopener">강의 관리</a>의 맛보기 설정으로 유지하고, 프론트 무료콘텐츠 메뉴에서는 1차에 가립니다(무료강의 기획 때 별도 페이지로 오픈).\n'
   '      </div>', 1)
# 목록 필터 — 구분 3종 + 머리말 필터
R('              <option value="EXAM">빈출자료</option>\n\n              <option value="DAILY">매일 1문제</option>\n\n            </select>',
  '              <option value="EXAM">기출문제</option>\n\n              <option value="DAILY">정조교의 매일 1문제</option>\n\n'
  '              <option value="SHORTS">나나조교의 출퇴근 1분 산안기</option>\n\n            </select>\n\n'
  '            <select id="fl-head-filter" name="head_code" onchange="renderFreeLectures()" data-dev-flag="proto-only" data-dev-note="(규칙) 머리말 필터 head_code — 개발 FreeContentIndexRequest에 없음">\n'
  '              <option value="ALL">머리말 전체 (매일 1문제)</option>\n'
  '              <option value="electric">전기 1문제</option>\n'
  '              <option value="chemistry">화학 1문제</option>\n'
  '              <option value="ergonomics">인간공학 1문제</option>\n'
  '              <option value="written">필답형 빈출</option>\n'
  '              <option value="practical">작업형 빈출</option>\n'
  '            </select>')
R('<th style="width:160px;">자격증 종목 / 대비연도</th>', '<th style="width:170px;">자격증 종목 / 연도 · 회차</th>')
R('<th style="width:200px;">PDF 첨부 (로그인 회원만)</th>', '<th style="width:200px;">PDF 첨부 (로그인 회원만) · 영상</th>')
# 등록 · 수정 S1 — 구분 · 머리말 · 유튜브 주소
R('            <select id="fl-form-type">\n              <option value="EXAM">빈출자료</option>\n              <option value="DAILY">매일 1문제</option>\n            </select>\n'
  '            <div style="font-size:11.5px; color:var(--text-muted); margin-top:4px;">무료특강 영상은 여기서 등록하지 않습니다 — 강의 관리(맛보기) · 강좌 관리(무료 강좌)에서 등록합니다.</div>\n'
  '          </div>\n',
  '            <select id="fl-form-type" onchange="toggleFlTypeFields()">\n'
  '              <option value="EXAM">기출문제</option>\n'
  '              <option value="DAILY">정조교의 매일 1문제</option>\n'
  '              <option value="SHORTS">나나조교의 출퇴근 1분 산안기 (가제)</option>\n'
  '            </select>\n'
  '            <div style="font-size:11.5px; color:var(--text-muted); margin-top:4px;">무료강의(맛보기 강의) 영상은 여기서 등록하지 않습니다 — 강의 관리(맛보기)에서 등록하며, 프론트 무료강의 메뉴는 1차에서 가립니다. 쇼츠 게시판 이름은 가제입니다(설정값, 바뀔 수 있음).</div>\n'
  '          </div>\n'
  '          <div class="form-group" id="fl-head-group">\n'
  '            <label class="form-label">머리말 * (매일 1문제)</label>\n'
  '            <select id="fl-form-head" name="head_code" data-dev-flag="proto-only" data-dev-note="(규칙) posts.head_code string(20) · FreeContent::HEADS — DAILY면 required, 그 밖 구분은 서비스가 비움. 개발 미구현">\n'
  '              <option value="">머리말 선택</option>\n'
  '              <option value="electric">전기 1문제</option>\n'
  '              <option value="chemistry">화학 1문제</option>\n'
  '              <option value="ergonomics">인간공학 1문제</option>\n'
  '              <option value="written">필답형 빈출</option>\n'
  '              <option value="practical">작업형 빈출</option>\n'
  '            </select>\n'
  '          </div>\n'
  '          <div class="form-group full" id="fl-video-group">\n'
  '            <label class="form-label">유튜브 영상 주소 * (쇼츠)</label>\n'
  '            <input type="text" id="fl-form-video" name="video_url" placeholder="예: https://youtube.com/shorts/aB3dE5fG7hJ" oninput="renderFlVideoPreview()" data-dev-flag="proto-only" data-dev-note="(규칙) 입력 video_url(SHORTS면 required, 유튜브 주소 형식) → 서비스가 영상 ID 11자만 posts.video_id string(20)에 저장. 개발 미구현" />\n'
  '            <div id="fl-video-preview" style="font-size:11.5px; color:var(--text-muted); margin-top:4px;"></div>\n'
  '          </div>\n')
R('<label class="form-label">대상 자격증 종목 / 대비 연도 *</label>', '<label class="form-label" id="fl-cert-label">대상 자격증 종목 / 대비 연도 *</label>')
R("placeholder=\"예: [빈출문제] 2026 산업안전기사 필기 최빈출 핵심 50선 해설 / [매일 1문제] 10월 27일 — 안전보건관리책임자 선임 기준\" />\n"
  "            <div style=\"font-size:11.5px; color:var(--text-muted); margin-top:4px;\">'정답지' 콘텐츠는 제목에 '정답지'를 붙여 표기합니다. 저작권 보호를 위해 제목에는 '빈출문제'로 표기합니다.</div>",
  "placeholder=\"예: [기출문제] 2025년 산업안전기사 필기 제3회 해설 / [매일 1문제] 11월 2일 — 안전보건관리책임자 선임 기준\" />\n"
  "            <div style=\"font-size:11.5px; color:var(--text-muted); margin-top:4px;\">'정답지' 콘텐츠는 제목에 '정답지'를 붙여 표기합니다(기출문제 · 매일 1문제). 연도 · 회차별 자료는 '기출문제'로 표기합니다(S2-08, 2026-11-02 개정).</div>")
R('          <div class="form-group">\n            <label class="form-label">PDF 파일명 (빈출자료 · 정답지)</label>\n            <input type="text" id="fl-form-pdf" placeholder="예: 2026_산안기_빈출문제_50선.pdf" />',
  '          <div class="form-group" id="fl-pdf-group">\n            <label class="form-label">PDF 파일명 (기출문제 · 정답지)</label>\n            <input type="text" id="fl-form-pdf" placeholder="예: 2025_산안기_필기_3회_기출문제.pdf" />')
R('<label class="form-label">본문 — 문항 · 해설 요약 (웹 에디터, 누구나 열람)</label>', '<label class="form-label" id="fl-body-label">본문 — 문항 · 해설 요약 (웹 에디터, 누구나 열람)</label>')
# 합격수기 샘플 문구의 '빈출문제'
R("산준모 빈출문제 특강과", "산준모 기출문제 특강과")
R("빈출문제 무료특강, 정답지 해설을", "기출문제 무료강의, 정답지 해설을")
# 스크립트 — 구분 · 머리말 상수, 유튜브 ID 추출
RE(r"  // 3\. 무료콘텐츠 \(ADMN-BRD-010\) — 제목 표기는[^\n]*\n  // 콘텐츠 구분\(S-22[^\n]*\n",
   "  // 3. 무료콘텐츠 (ADMN-BRD-010) — v3.2.32(2026-11-02 white): '기출문제' 표기 허용(S2-08 기출문제 표기 금지 폐지, 구 빈출자료)\n"
   "  // 콘텐츠 구분 3종: 기출문제(EXAM, 연도 · 회차 · PDF · 본문) · 정조교의 매일 1문제(DAILY, 머리말 5종) · 나나조교의 출퇴근 1분 산안기(SHORTS, 가제 — 유튜브 URL 필수 · 영상 ID만 저장). 개발 FreeContent::TYPES는 EXAM · DAILY뿐(SHORTS 추가 필요).\n", 1)
R("  const FL_TYPES = { EXAM: ['badge-purple', '📝 빈출자료'], DAILY: ['badge-blue', '📅 매일 1문제'] };", r"""  const FL_TYPES = { EXAM: ['badge-purple', '📝 기출문제'], DAILY: ['badge-blue', '📅 정조교의 매일 1문제'], SHORTS: ['badge-amber', '▶ 나나조교의 출퇴근 1분 산안기'] };
  // 매일 1문제 머리말 5종 — 코드는 개발 명명 규칙(소문자 snake, 규칙). 개발 FreeContent::HEADS(규칙)
  const FL_HEADS = { electric: '전기 1문제', chemistry: '화학 1문제', ergonomics: '인간공학 1문제', written: '필답형 빈출', practical: '작업형 빈출' };
  // 유튜브 주소에서 영상 ID(11자)만 뽑는다 — shorts/ · watch?v= · youtu.be/ · embed/ · live/. 못 뽑으면 ''
  function flYoutubeId(url) {
    const m = String(url || '').trim().match(/^(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:shorts\/|watch\?(?:[^#]*&)?v=|embed\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11})(?:[?&#\/].*)?$/);
    return m ? m[1] : '';
  }""")
# 샘플 — 쇼츠 2건 추가, 매일 1문제 머리말, 기출문제 연도 · 회차
OPS.append(dict(kind="insert_after", anchor="  let FREE_LECTURES = [\n", html=(
    "\n    { id: 'FL-2607', type: 'SHORTS', cert: '산업안전기사', year: '', round: '', head: '', videoId: 'aB3dE5fG7hJ', postDate: '2026-11-02', title: '[출퇴근 1분] 안전인증 대상 기계 8종 한 번에 외우기', pdf: '-', views: 1204, visible: true, body: '', versions: [{ ver: 1, date: '2026-11-02', pdf: '-', body: '영상 aB3dE5fG7hJ', note: '최초 등록' }] },\n"
    "\n    { id: 'FL-2606', type: 'SHORTS', cert: '건설안전기사', year: '', round: '', head: '', videoId: 'Qw9_Er8-Ty7', postDate: '2026-10-31', title: '[출퇴근 1분] 비계 벽이음 간격 30초 정리', pdf: '-', views: 865, visible: true, body: '수직 5m · 수평 5m — 강관비계 벽이음 간격을 짧게 정리했습니다.', versions: [{ ver: 1, date: '2026-10-31', pdf: '-', body: '수직 5m · 수평 5m — 강관비계 벽이음 간격을 짧게 정리했습니다.', note: '최초 등록' }] },\n")))
R("{ id: 'FL-2605', type: 'DAILY', ", "{ id: 'FL-2605', type: 'DAILY', head: 'written', ")
R("{ id: 'FL-2603', type: 'DAILY', ", "{ id: 'FL-2603', type: 'DAILY', head: 'ergonomics', ")
RE(r"    \{ id: 'FL-2604', type: 'EXAM'[^\n]*",
   "    { id: 'FL-2604', type: 'EXAM', round: 3, cert: '산업안전기사', year: '2025', postDate: '2026-09-25', title: '[기출문제] 2025년 산업안전기사 필기 제3회 기출문제 해설', pdf: '2025_산안기_필기_3회_기출문제.pdf', views: 2410, visible: true, body: '2025년 제3회 산업안전기사 필기 기출문제와 해설입니다.', versions: [{ ver: 1, date: '2026-09-25', pdf: '2025_산안기_필기_3회_기출문제.pdf', body: '2025년 제3회 필기 기출문제와 해설입니다.', note: '최초 등록' }, { ver: 2, date: '2026-10-12', pdf: '2025_산안기_필기_3회_기출문제.pdf', body: '2025년 제3회 산업안전기사 필기 기출문제와 해설입니다.', note: '본문 수정' }] },", 1)
RE(r"    \{ id: 'FL-2602', type: 'EXAM'[^\n]*",
   "    { id: 'FL-2602', type: 'EXAM', round: 2, cert: '건설안전기사', year: '2025', postDate: '2026-09-05', title: '[기출문제] 2025년 건설안전기사 실기 필답형 제2회 기출문제 정답지', pdf: '2025_건안기_실기_2회_기출문제_정답지.pdf', views: 1520, visible: true, body: '2025년 제2회 건설안전기사 실기 필답형 기출문항과 모범 답안입니다.', versions: [{ ver: 1, date: '2026-09-05', pdf: '2025_건안기_실기_2회_기출문제_정답지.pdf', body: '2025년 제2회 건설안전기사 실기 필답형 기출문항과 모범 답안입니다.', note: '최초 등록' }] },", 1)
RE(r"    \{ id: 'FL-2601', type: 'EXAM'[^\n]*",
   "    { id: 'FL-2601', type: 'EXAM', round: 1, cert: '위험물산업기사', year: '2025', postDate: '2026-08-20', title: '[기출문제] 2025년 위험물산업기사 필기 제1회 기출문제 해설', pdf: '2025_위험물_필기_1회_기출문제.pdf', views: 980, visible: true, body: '2025년 제1회 위험물산업기사 필기 기출문제 해설입니다.', versions: [{ ver: 1, date: '2026-08-20', pdf: '2025_위험물_필기_1회_기출문제.pdf', body: '2025년 제1회 위험물산업기사 필기 기출문제 해설입니다.', note: '최초 등록' }] }", 1)
# 목록 렌더 · 폼 채우기 · 저장 — 함수 통째 교체(자리표 → 코드, 정규식 치환문에 역슬래시가 들어가지 않게 두 단계)
RE(r"  // 3\. 무료콘텐츠 — 빈출자료 · 매일 1문제 \(ADMN-BRD-010\)\n  function renderFreeLectures\(\) \{[\s\S]*?`\)\.join\(''\);\n\n  \}\n", "/*@@FL_RENDER@@*/\n", 1)
R("/*@@FL_RENDER@@*/\n", r"""  // 3. 무료콘텐츠 — 기출문제 · 정조교의 매일 1문제 · 나나조교의 출퇴근 1분 산안기 (ADMN-BRD-010, v3.2.32)
  function renderFreeLectures() {
    const tp = document.getElementById('fl-type-filter').value;
    const hd = document.getElementById('fl-head-filter').value;
    const cert = document.getElementById('fl-cert-filter').value;
    const list = FREE_LECTURES.filter(item =>
      (tp === 'ALL' || item.type === tp) &&
      (hd === 'ALL' || item.head === hd) &&
      (cert === 'ALL' || item.cert === cert)
    );
    document.getElementById('cnt-freeLecture').textContent = FREE_LECTURES.length;
    document.getElementById('fl-tbody').innerHTML = list.map(item => `
      <tr>
        <td style="font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, 'Malgun Gothic', sans-serif; font-variant-numeric: tabular-nums; font-weight:700;">${item.id}</td>
        <td>
          <span class="badge ${(FL_TYPES[item.type] || ['badge-slate'])[0]}">${(FL_TYPES[item.type] || ['', item.type])[1]}</span>
          ${item.head && FL_HEADS[item.head] ? `<br/><span class="badge badge-slate" style="margin-top:3px;">${FL_HEADS[item.head]}</span>` : ''}
        </td>
        <td><strong>${item.cert}</strong>${item.year ? ` (${item.year}${item.round ? ' · ' + item.round + '회' : ''})` : ''}</td>
        <td style="font-weight:700;">${item.type === 'SHORTS' && item.videoId
          ? `<div style="display:flex; gap:8px; align-items:center;"><div class="fl-yt-thumb" title="유튜브 썸네일 i.ytimg.com/vi/${item.videoId}/mqdefault.jpg">▶</div><div>${item.title}<div style="font-size:11px; font-weight:600; color:var(--text-muted);">유튜브 썸네일 · 영상 ID ${item.videoId}</div></div></div>`
          : item.title}</td>
        <td style="font-size:12px;">${item.postDate || '-'}</td>
        <td style="color:var(--primary); font-weight:600;">${item.type === 'SHORTS'
          ? '<span style="color:var(--text-muted); font-weight:600;">▶ 유튜브 영상 (PDF 없음)</span>'
          : `📥 ${item.pdf}${item.pdf && item.pdf !== '-' ? '<br/><span class="badge badge-slate" style="margin-top:3px;">🔒 로그인 회원만</span>' : ''}`}</td>
        <td>${item.views.toLocaleString()}</td>
        <td><span class="badge ${item.visible ? 'badge-green' : 'badge-slate'}">${item.visible ? '노출중' : '비노출'}</span></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="openFreeLecturePage('${item.id}')">수정</button>
        </td>
      </tr>
    `).join('');
  }
""")
RE(r"  function fillFreeLectureForm\(id\) \{[\s\S]*?    renderFlVersions\(item \|\| null\);\n\n  \}\n", "/*@@FL_FILL@@*/\n", 1)
R("/*@@FL_FILL@@*/\n", r"""  function fillFreeLectureForm(id) {
    const item = FREE_LECTURES.find(f => f.id === id);
    document.getElementById('fl-edit-id').value = item ? item.id : '';
    document.getElementById('fl-modal-title').textContent = item ? `[ADMN-BRD-010] 무료콘텐츠 수정 (${item.id})` : '[ADMN-BRD-010] 무료콘텐츠 신규 등록';
    document.getElementById('fl-form-type').value = item && FL_TYPES[item.type] ? item.type : 'EXAM';
    document.getElementById('fl-form-head').value = item && item.head ? item.head : '';
    document.getElementById('fl-form-video').value = item && item.videoId ? 'https://youtube.com/shorts/' + item.videoId : '';
    const rd = document.getElementById('fl-form-round');
    if (rd) rd.value = item && item.round ? item.round : '';
    document.getElementById('fl-form-cert').value = item ? item.cert : '산업안전기사';
    document.getElementById('fl-form-year').value = item && item.year ? item.year : '2026 대비';
    document.getElementById('fl-form-title').value = item ? item.title : '';
    document.getElementById('fl-form-date').value = item && item.postDate ? item.postDate : '2026-11-02';
    document.getElementById('fl-form-pdf').value = item ? (item.pdf === '-' ? '' : item.pdf) : '';
    document.getElementById('fl-form-body').innerHTML = item ? (item.body ? `<p>${item.body}</p>` : '') : '<p>문항과 해설을 입력하세요. 본문은 로그인하지 않아도 보입니다.</p>';
    toggleFlTypeFields();
    renderFlVersions(item || null);
  }
  // 구분별 입력 칸 — 기출문제: 연도 · 회차 · PDF · 본문 / 매일 1문제: 머리말 · 연도 · PDF · 본문 / 쇼츠: 유튜브 주소(필수) · 본문(선택), 연도 · 회차 · PDF 숨김
  function toggleFlTypeFields() {
    const type = document.getElementById('fl-form-type').value;
    const shorts = type === 'SHORTS', daily = type === 'DAILY', exam = type === 'EXAM';
    document.getElementById('fl-head-group').style.display = daily ? '' : 'none';
    document.getElementById('fl-video-group').style.display = shorts ? '' : 'none';
    document.getElementById('fl-pdf-group').style.display = shorts ? 'none' : '';
    document.getElementById('fl-form-year').style.display = shorts ? 'none' : '';
    const rw = document.getElementById('fl-round-wrap');
    if (rw) rw.style.display = exam ? '' : 'none';
    document.getElementById('fl-cert-label').textContent = shorts ? '대상 자격증 종목 *' : exam ? '대상 자격증 종목 / 연도 · 회차 *' : '대상 자격증 종목 / 대비 연도 *';
    document.getElementById('fl-body-label').textContent = shorts ? '본문 — 영상 설명 (선택, 누구나 열람)' : '본문 — 문항 · 해설 요약 (웹 에디터, 누구나 열람)';
    document.getElementById('fl-form-access').innerHTML = shorts
      ? '본문 · 영상: <strong>누구나 열람</strong> (유튜브 퍼가기 재생 — 우리 채널 영상은 퍼가기 허용 유지)'
      : '본문: <strong>누구나 열람</strong> · PDF: <strong>🔒 로그인 회원만 다운로드</strong> (다운로드 기록을 남깁니다. 바꿀 수 없음)';
    renderFlVideoPreview();
  }
  function renderFlVideoPreview() {
    const box = document.getElementById('fl-video-preview');
    const raw = document.getElementById('fl-form-video').value.trim();
    const vid = flYoutubeId(raw);
    if (!raw) { box.innerHTML = '쇼츠 · 일반 유튜브 주소를 붙여 넣으면 영상 ID만 저장합니다. 프론트는 /embed/영상ID 세로(9:16)로 보여 주고, 목록 썸네일은 유튜브 썸네일을 씁니다.'; return; }
    box.innerHTML = vid
      ? `<div style="display:flex; gap:10px; align-items:center;"><div class="fl-yt-thumb">▶</div><div>저장 값(영상 ID): <strong id="fl-video-id">${vid}</strong><br/>프론트 재생: youtube.com/embed/${vid} (세로 9:16)<br/>목록 썸네일: i.ytimg.com/vi/${vid}/mqdefault.jpg</div></div>`
      : '<span style="color:var(--danger); font-weight:700;">유튜브 영상 주소가 아닙니다. youtube.com/shorts/… · youtu.be/… 주소를 넣어 주세요.</span>';
  }
""")
RE(r"  function saveFreeLecture\(\) \{[\s\S]*?showToast\('무료콘텐츠가 저장되었습니다\.[^\n]*\n\n  \}\n", "/*@@FL_SAVE@@*/\n", 1)
R("/*@@FL_SAVE@@*/\n", r"""  function saveFreeLecture() {
    const editId = document.getElementById('fl-edit-id').value;
    const type = document.getElementById('fl-form-type').value;
    const shorts = type === 'SHORTS';
    const cert = document.getElementById('fl-form-cert').value;
    const year = shorts ? '' : document.getElementById('fl-form-year').value.trim();
    const rd = document.getElementById('fl-form-round');
    const round = type === 'EXAM' && rd ? rd.value.trim() : '';
    const head = type === 'DAILY' ? document.getElementById('fl-form-head').value : '';
    const videoRaw = document.getElementById('fl-form-video').value.trim();
    const videoId = shorts ? flYoutubeId(videoRaw) : '';
    const title = document.getElementById('fl-form-title').value.trim();
    const postDate = document.getElementById('fl-form-date').value || '2026-11-02';
    const pdf = shorts ? '-' : (document.getElementById('fl-form-pdf').value.trim() || '-');
    const body = document.getElementById('fl-form-body').innerText.trim();

    if (!title) { alert('콘텐츠 제목을 입력해주세요.'); return; }
    if (!shorts && !year) { alert('연도를 입력해 주세요.'); return; }
    if (type === 'EXAM' && rd && !(Number(round) >= 1 && Number(round) <= 999)) { alert('기출문제는 회차(1~999)를 입력해 주세요.'); return; }
    if (type === 'DAILY' && !FL_HEADS[head]) { alert('매일 1문제는 머리말을 골라 주세요.'); return; }
    if (shorts && !videoRaw) { alert('나나조교의 출퇴근 1분 산안기는 유튜브 영상 주소가 필수입니다.'); return; }
    if (shorts && !videoId) { alert('유튜브 영상 주소가 아닙니다. youtube.com/shorts/… · youtu.be/… 주소를 넣어 주세요.'); return; }

    const verBody = body || (videoId ? '영상 ' + videoId : '');
    if (editId) {
      const target = FREE_LECTURES.find(f => f.id === editId);
      if (target) {
        // PDF 파일 · 본문 · 영상이 바뀌면 새 버전으로 기록
        const changed = [];
        if (target.pdf !== pdf) changed.push('PDF 교체');
        if ((target.body || '') !== body) changed.push('본문 수정');
        if ((target.videoId || '') !== videoId) changed.push('영상 교체');
        target.versions = target.versions || [];
        if (changed.length) target.versions.push({ ver: target.versions.length + 1, date: '2026-11-02', pdf, body: verBody, note: changed.join(' · ') });
        Object.assign(target, { type, cert, year, round, head, videoId, postDate, title, pdf, body });
      }
    } else {
      FREE_LECTURES.unshift({
        id: 'FL-' + (2606 + FREE_LECTURES.length),
        type, cert, year, round, head, videoId, postDate, title, pdf, views: 0, visible: true, body,
        versions: [{ ver: 1, date: '2026-11-02', pdf, body: verBody, note: '최초 등록' }]
      });
    }
    renderFreeLectures();
    backToList();
    showToast(shorts ? '무료콘텐츠가 저장되었습니다. 유튜브 영상 ID(' + videoId + ')만 저장합니다.' : '무료콘텐츠가 저장되었습니다. 본문은 누구나, PDF는 로그인 회원만 받을 수 있습니다.');
  }
""")
R('<option value="SHORTS">', '<option value="SHORTS" data-dev-flag="proto-only" data-dev-name="content_type" data-dev-value="SHORTS" data-dev-note="(규칙) FreeContent::TYPES에 SHORTS 추가 필요 — 개발 미구현">', 2)

# 합격수기 검수 모달(modal-pass-audit)은 id 유지 — 개발 005-S1은 별도 페이지(admin.reviews.show)의 modForm, 레이어 id 없음

# ── 탭 → 개발 메뉴 ──────────────────────────────────
R('onclick="switchTab(\'courseReview\')"', attrs(route="admin.reviews.index", method="GET", url=A + "/reviews", perm="조회",
  note="개발은 수기 · 합격 후기를 한 목록(reviews)에서 처리 — 수강후기 탭 분리는 프로토타입 구성").lstrip() + ' onclick="switchTab(\'courseReview\')"')
R('onclick="switchTab(\'passEssay\')"', attrs(route="admin.reviews.index", method="GET", url=A + "/reviews", perm="조회",
  note="개발 필터 verify_status · exam_target_id · exam_round · instructor_id · cafe · display · is_best · point · refund · keyword").lstrip() + ' onclick="switchTab(\'passEssay\')"')
R('onclick="switchTab(\'freeLecture\')"', attrs(route="admin.free-contents.index", method="GET", url=A + "/free-contents", perm="조회",
  note="개발 BRD-010 무료콘텐츠 관리(별도 메뉴)").lstrip() + ' onclick="switchTab(\'freeLecture\')"')

# ── 005 수강후기 ────────────────────────────────────
NAME("cr-best-filter", "is_best", value="1 = 베스트만 (일반 필터는 개발 없음)")
DEVNAME('<option value="BEST">', "is_best", value="1")
NAME("cr-keyword", "keyword", note="개발 keyword = 제목 검색")
ACT("toggleBestCourseReview", route="admin.reviews.best.update", method="PUT", url=A + "/reviews/best", perm="수정",
    note="bulkForm: ids[] · best(bulkBest) 1 · 0 — 베스트 동시 최대 12")
ACT("toggleCourseReviewVisible", route="admin.reviews.display.update", method="PUT", url=A + "/reviews/display", perm="수정",
    note="bulkForm: ids[] · show(bulkShow) 1 · 0 → reviews.display_site")

# ── 005 합격수기 · 005-S1 검증 ─────────────────────────
NAME("pe-status-filter", "verify_status", value="pending · verified · rejected · hidden(개발에만)")
DEVNAME('<option value="PENDING">', "verify_status", value="pending")
DEVNAME('<option value="APPROVED">', "verify_status", value="verified")
DEVNAME('<option value="REJECTED">', "verify_status", value="rejected")
NAME("pe-keyword", "keyword", note="개발 keyword = 제목 검색. 종목 · 회차는 exam_target_id · exam_round 필터")
ACT("openPassAuditModal", count=2, route="admin.reviews.show", method="GET", url=A + "/reviews/{review}", perm="조회",
    note="개발 005-S1은 별도 페이지(modForm)")
R('onclick="decidePassEssay(\'REJECTED\')"', attrs(route="admin.reviews.update", method="PUT", url=A + "/reviews/{review}", perm="수정",
  name="verify_status", value="rejected", note="reject_reason 10~255자 필수(회원 마이페이지 · 알림에 노출)").lstrip() + ' onclick="decidePassEssay(\'REJECTED\')"')
R('onclick="decidePassEssay(\'APPROVED\')"', attrs(route="admin.reviews.update", method="PUT", url=A + "/reviews/{review}", perm="수정",
  name="verify_status", value="verified", note="검증만(지급 없음) — 지급은 따로 admin.members.review-points.store(v6.92 D-BRD-02로 개발과 같아짐)").lstrip() + ' onclick="decidePassEssay(\'APPROVED\')"')
# v6.92: pe-reward-note 아래 dev-only 반려 사유 · 우수 후기 포인트 폼 삭제(결정 반영, D-BRD-02 · S-21) — 원본에 반려 사유 · 후기 보상 지급 모달이 생겨 그 요소에 개발 이름을 단다
DEVNAME('id="pe-reject-chip"', "reject_reason", note="개발 공통 사유 칩(Review::REJECT_REASONS) — 고르면 reject_reason 앞에 채움, 별도 필드 없음. '증빙 식별 불가'는 개발 칩에 없음")
NAME("pe-reject-text", "reject_reason", note="rejected일 때 required · 10~255자(rejectReason)")
ACT("openReviewRewardModal", route="admin.members.review-points.store", method="POST", url=A + "/members/review-points/{review}", perm="등록(회원관리 메뉴)",
    note="ReviewService::pointPanel ready일 때만(검증 완료 · 미지급). 후기당 1회(reviews.point_granted_at)")
NAME("rw-amount", "amount", note="required · 1~999,999,999 정수. 기본값 = 포인트 정책 후기 보상값")
NAME("rw-reason", "reason", note="개발은 항상 required 10~200자 · 공백 제외 10자 · 서로 다른 글자 3개(프로토는 금액을 바꿀 때만)")
ACT("confirmReviewReward", route="admin.members.review-points.store", method="POST", url=A + "/members/review-points/{review}", perm="등록(회원관리 메뉴)",
    note="ReviewPointRequest amount · reason")
ACT("openReviewRevokeModal", flag="proto-only", note="후기 보상 회수(S-21) — 개발 없음")
ACT("confirmReviewRevoke", flag="proto-only", note="후기 보상 회수 — 개발 없음(무상 P 잔액 한도 회수 라우트 없음)")

# ── BRD-010 무료콘텐츠 목록 ───────────────────────────
NAME("fl-type-filter", "type", value="EXAM 기출문제(구 빈출자료) · DAILY 정조교의 매일 1문제 · SHORTS 나나조교의 출퇴근 1분 산안기(규칙, 개발 TYPES에 없음)")
# 10-27 v6.84: 원본에서 FREE_LECTURE 구분 삭제(개발 구분과 같아짐)
NAME("fl-cert-filter", "cert", note="값 = categories.id (1Depth 자격증)")
R('<button class="btn btn-primary" onclick="openFreeLecturePage(null)">',
  '<button class="btn btn-outline" data-dev-flag="dev-only"' + attrs(route="admin.free-contents.download", method="GET", url=A + "/free-contents/download", perm="다운로드",
  note="개인정보 없음 — 사유 입력 없이 다운로드") + '>엑셀 다운로드</button>\n'
  '            <button class="btn btn-primary"' + attrs(route="admin.free-contents.create", method="GET", url=A + "/free-contents/create", perm="등록") + ' onclick="openFreeLecturePage(null)">')
R("onclick=\"openFreeLecturePage('${item.id}')\"",
  attrs(route="admin.free-contents.edit", method="GET", url=A + "/free-contents/{freeContent}/edit", perm="수정").lstrip() + " onclick=\"openFreeLecturePage('${item.id}')\"")

# ── BRD-010-S1 등록 · 수정 (freeContentForm) ─────────────
NAME("fl-form-type", "content_type", value="EXAM 기출문제 · DAILY 정조교의 매일 1문제 · SHORTS 나나조교의 출퇴근 1분 산안기(가제)", note="개발 FreeContent::TYPES = EXAM 빈출자료 · DAILY 매일 1문제 — v3.2.32: EXAM 라벨 기출문제로, SHORTS 추가 필요(규칙)")
# v6.92: FREQ_EXAM 옵션 삭제(결정 반영, S-22 · D-BRD-01) — 원본 구분이 EXAM · DAILY로 개발과 같아짐
DEVNAME('<option value="EXAM">', "content_type", value="EXAM", count=2)
DEVNAME('<option value="DAILY">', "content_type", value="DAILY", count=2)
NAME("fl-form-cert", "cert_category_id", note="값 = categories.id (1Depth)")
R('id="fl-form-year" value="2026 대비" style="width:120px;" />',
  'id="fl-form-year" value="2026 대비" style="width:120px;" />\n'
  '              <span id="fl-round-wrap" style="display:inline-flex; align-items:center; gap:4px;"><input type="number" id="fl-form-round" name="round_no" min="1" max="999" placeholder="회차" style="width:80px;" data-dev-note="roundNo — EXAM이면 필수 · 1~999, DAILY · SHORTS는 비움(v3.2.32 기출문제 연도 · 회차별 자료게시판 — 프로토에도 입력 칸)" /> 회</span>')
NAME("fl-form-year", "year", note="정수 2000~2100 (프로토타입 '2026 대비' 문구). v3.2.32: SHORTS는 연도 없음 — 개발 required를 required_unless:content_type,SHORTS로 바꿔야 함")
NAME("fl-form-title", "title", note="max:100")
# v6.92: fl-form-vod(VOD 에셋 · 러닝타임) 삭제(결정 반영, S-22 · D-BRD-01) — 무료특강 영상은 PROD-002 · 003에서 등록
NAME("fl-form-date", "started_at", note="개발 전시 시작일 nullable Y-m-d — 프로토 게시일(필수)")
NAME("fl-form-pdf", "attachments[]", note="PDF만 · 최대 5개 · 개당 10MB (프로토타입은 파일명 텍스트). 삭제는 delete_attachments[]. v3.2.32: SHORTS는 PDF 없음(prohibited_if)")
R('id="fl-form-body"', 'id="fl-form-body"' + attrs(name="content", note="nullable(에디터)"))
R('<div style="font-weight:800; font-size:13.5px; margin-bottom:6px;">파일 · 본문 버전 이력</div>',
  '<div style="font-weight:800; font-size:13.5px; margin-bottom:6px;" data-dev-flag="proto-only" data-dev-note="버전 이력 — 개발 없음">파일 · 본문 버전 이력</div>')
ACT("saveFreeLecture", route="admin.free-contents.store | admin.free-contents.update", method="POST | PUT",
    url=A + "/free-contents | /free-contents/{freeContent}", perm="등록 | 수정",
    note="저장 전 중복 경고 GET admin.free-contents.duplicates.index(JSON). 개발 추가 필드: status(published · hidden) · started_at · related_course_id")

# ── 검증 ──────────────────────────────────────────
VERIFY = [
    ("합격수기 탭", "switchTab('passEssay')", "#view-passEssay"),
    ("무료콘텐츠 탭", "switchTab('freeLecture')", "#view-freeLecture"),
    ("수강후기 탭", "switchTab('passEssay'); switchTab('courseReview')", "#view-courseReview"),
    ("합격수기 검수 모달", "switchTab('passEssay'); openPassAuditModal(PASS_ESSAYS[0].id)", "#modal-pass-audit"),
    ("무료콘텐츠 등록 S1", "switchTab('freeLecture'); openFreeLecturePage(null)", "[data-subpage='free-lecture']"),
    ("무료콘텐츠 수정 S1", "switchTab('freeLecture'); openFreeLecturePage(FREE_LECTURES[0].id)", "[data-subpage='free-lecture']"),
]
