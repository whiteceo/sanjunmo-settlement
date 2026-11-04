/**
 * [GitHub ↔ 공유 문서함] 산준모 정산시스템 양방향 동기화
 * - 파일별 기준점(마지막 동기화 시 blob SHA) 대비 바뀐 쪽만 반영
 * - GitHub만 변경 → 드라이브 내용 교체(파일 ID 유지) / 드라이브만 변경 → 커밋 1개로 묶어 push
 * - 양쪽 모두 변경 → 원래 이름엔 GitHub 버전, 드라이브 버전은 _drive충돌_ 사본으로 보존 + 메일
 * - previewSync() : 아무것도 바꾸지 않고 계획만 로그로 출력
 * 준비: 서비스에 "Drive API" 추가, 스크립트 속성 GH_TOKEN (해당 저장소 Contents 읽기/쓰기 토큰)
 */
const SYNC = {
  repo: 'whiteceo/sanjunmo-settlement',
  branch: 'main',
  folderId: '1ubVGRBK3DWcrMZglMaA_Yt1lyCNYFQ4a',  // 공유 문서함 산준모 닷컴/04.설계서/정산시스템
  exclude: ['.git/', '.claude/', '_archive/backup/'],  // 양쪽 모두 제외할 경로 접두어
  driveDeleteToGithub: false,  // false: 드라이브에서 지운 파일은 GitHub 버전으로 복구
  // 드라이브에서 바뀐 기존 .md는 커밋하지 않고 _drive충돌_ 사본 + 메일로만 남긴다.
  // 구글 문서로 열었다 저장하면 \[ \~ 이스케이프 · ~~ 취소선 · 목록 번호 변형이 생긴다(2026-11-04 3e0d4c2).
  mdDriveEditToConflict: true,
  maxMs: 4 * 60 * 1000,
  conflictTag: '_drive충돌_',
};

function syncSettlement() { runSync_(false); }
function previewSync() { runSync_(true); }

function runSync_(dry) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(0)) { Logger.log('>>> 이전 실행 진행 중 — 건너뜀'); return; }
  try {
    const t0 = Date.now();
    const props = PropertiesService.getScriptProperties();
    const token = props.getProperty('GH_TOKEN');
    if (!token) throw new Error('스크립트 속성 GH_TOKEN 없음');
    const gh = gh_(token);

    const head = gh.get(`/commits/${SYNC.branch}`);
    const tree = gh.get(`/git/trees/${head.commit.tree.sha}?recursive=1`);
    if (tree.truncated) throw new Error('트리 응답 잘림 — 저장소가 너무 큼');
    const remote = {}, modes = {};
    tree.tree.filter(e => e.type === 'blob' && keep_(e.path))
      .forEach(e => { remote[e.path] = e.sha; modes[e.path] = e.mode; });

    const root = DriveApp.getFolderById(SYNC.folderId);
    const drive = {};
    walk_(root, '', drive);

    const M = loadManifest_(props);
    const paths = new Set([...Object.keys(remote), ...Object.keys(drive), ...Object.keys(M)]);
    const plan = [];
    for (const p of paths) {
      const a = decide_(p, remote[p], drive[p], M[p]);
      if (a) plan.push(a);
    }
    Logger.log(`>>> 커밋 ${head.sha.slice(0, 7)} / 계획 ${plan.length}건` + (dry ? ' (미리보기)' : ''));
    if (dry) { plan.forEach(a => Logger.log(` [${a.op}] ${a.p}`)); return; }

    const ups = [], conflicts = [];
    let cut = false;
    try {
      for (const a of plan) {
        if (Date.now() - t0 > SYNC.maxMs) { cut = true; break; }
        switch (a.op) {
          case 'record': M[a.p] = mf_(a.r, a.d.file); break;
          case 'forget': delete M[a.p]; break;
          case 'down': M[a.p] = mf_(a.r, writeDrive_(gh, root, a.p, a.r, a.d)); break;
          case 'trashDrive': a.d.file.setTrashed(true); delete M[a.p]; break;
          case 'up': case 'delRemote': ups.push(a); break;
          case 'conflict': {
            const keep = conflictName_(a.d.file.getName());
            a.d.file.setName(keep);
            if (a.r) M[a.p] = mf_(a.r, writeDrive_(gh, root, a.p, a.r, null));
            else delete M[a.p];
            conflicts.push(`${a.p} → 드라이브 버전 보존: ${keep}`);
            break;
          }
        }
        if (a.op !== 'up' && a.op !== 'delRemote') Logger.log(` [${a.op}] ${a.p}`);
      }

      if (ups.length) {
        const entries = ups.map(a => ({
          path: a.p, mode: modes[a.p] || '100644', type: 'blob',
          sha: a.op === 'delRemote' ? null : gh.post('/git/blobs', {
            content: Utilities.base64Encode(a.d.file.getBlob().getBytes()), encoding: 'base64' }).sha,
        }));
        const nt = gh.post('/git/trees', { base_tree: head.commit.tree.sha, tree: entries });
        const c = gh.post('/git/commits', {
          message: `drive-sync: 드라이브 수정 ${ups.length}건 반영\n\n` + ups.map(a => `${a.op === 'up' ? 'M' : 'D'} ${a.p}`).join('\n'),
          tree: nt.sha, parents: [head.sha] });
        const res = gh.patchRef({ sha: c.sha });  // fast-forward만 허용
        if (res.getResponseCode() < 300) {
          ups.forEach(a => { if (a.op === 'delRemote') delete M[a.p]; else M[a.p] = mf_(a.dSha, a.d.file); });
          ups.forEach(a => Logger.log(` [${a.op}] ${a.p}`));
          Logger.log(`>>> GitHub 커밋 ${c.sha.slice(0, 7)}`);
        } else {
          Logger.log(`>>> 그 사이 push 발생(${res.getResponseCode()}) — 업로드는 다음 실행에서 재시도`);
        }
      }
    } finally {
      saveManifest_(props, M);  // 중간에 끊겨도 처리한 만큼은 기억
    }

    if (conflicts.length) {
      MailApp.sendEmail(Session.getEffectiveUser().getEmail(),
        `[정산 동기화] 충돌 ${conflicts.length}건`, conflicts.join('\n'));
    }
    Logger.log(cut ? '>>> 안전 중단 — 다음 실행에서 이어서 처리' : '>>> 동기화 완료');
  } finally {
    lock.releaseLock();
  }
}

// r: GitHub blob SHA, d: 드라이브 {file, updated}, m: 기준점 {s, t, i}
function decide_(p, r, d, m) {
  let dSha = null, dState;  // none | new | same | changed | gone
  if (!d) dState = m ? 'gone' : 'none';
  else if (!m) { dSha = gitSha_(d.file.getBlob()); dState = 'new'; }
  else if (d.file.getId() === m.i && d.updated <= m.t) dState = 'same';
  else { dSha = gitSha_(d.file.getBlob()); dState = dSha === m.s ? 'same' : 'changed'; }

  if (!m) {
    if (r && d) return dSha === r ? { op: 'record', p, r, d } : { op: 'conflict', p, r, d };
    if (r) return { op: 'down', p, r };
    return { op: 'up', p, d, dSha };
  }
  const rChanged = (r || null) !== m.s;
  if (!rChanged) {
    if (dState === 'same') return dSha ? { op: 'record', p, r, d } : null;  // 시각만 바뀐 경우 기준점 갱신
    if (dState === 'changed') {
      if (SYNC.mdDriveEditToConflict && r && /\.md$/i.test(p)) return { op: 'conflict', p, r, d };
      return { op: 'up', p, d, dSha };
    }
    return SYNC.driveDeleteToGithub ? { op: 'delRemote', p } : { op: 'down', p, r };  // gone
  }
  if (dState === 'same' || dState === 'gone') {
    if (r) return { op: 'down', p, r, d };
    return d ? { op: 'trashDrive', p, d } : { op: 'forget', p };
  }
  if (r && dSha === r) return { op: 'record', p, r, d };  // 양쪽이 같은 내용으로 바뀜
  return { op: 'conflict', p, r, d };
}

function gh_(token) {
  const base = `https://api.github.com/repos/${SYNC.repo}`;
  const call = (method, path, body, accept) => {
    const opt = { method, muteHttpExceptions: true,
      headers: { Authorization: 'Bearer ' + token, Accept: accept || 'application/vnd.github+json', 'User-Agent': 'gas-sync' } };
    if (body) { opt.contentType = 'application/json'; opt.payload = JSON.stringify(body); }
    return UrlFetchApp.fetch(base + path, opt);
  };
  const ok = (r, what) => {
    if (r.getResponseCode() >= 300) throw new Error(`${what} → ${r.getResponseCode()} ${r.getContentText().slice(0, 300)}`);
    return r;
  };
  return {
    get: p => JSON.parse(ok(call('get', p), p).getContentText()),
    post: (p, b) => JSON.parse(ok(call('post', p, b), p).getContentText()),
    raw: sha => ok(call('get', `/git/blobs/${sha}`, null, 'application/vnd.github.raw'), sha).getBlob(),
    patchRef: b => call('patch', `/git/refs/heads/${SYNC.branch}`, b),
  };
}

function writeDrive_(gh, root, path, sha, d) {
  const name = path.slice(path.lastIndexOf('/') + 1);
  const blob = gh.raw(sha).setName(name).setContentType(mime_(name));
  if (d) {
    Drive.Files.update({}, d.file.getId(), blob, { supportsAllDrives: true });
    return DriveApp.getFileById(d.file.getId());
  }
  const dir = path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '';
  return folderAt_(root, dir).createFile(blob);
}

function walk_(folder, prefix, out) {
  const fi = folder.getFiles();
  while (fi.hasNext()) {
    const f = fi.next(), p = prefix + f.getName();
    if (!keep_(p) || f.getName().includes(SYNC.conflictTag) || f.getMimeType().startsWith('application/vnd.google-apps')) continue;
    if (out[p]) { Logger.log(' [중복 이름 무시] ' + p); continue; }
    out[p] = { file: f, updated: f.getLastUpdated().getTime() };
  }
  const di = folder.getFolders();
  while (di.hasNext()) {
    const sub = di.next(), p = prefix + sub.getName() + '/';
    if (keep_(p)) walk_(sub, p, out);
  }
}

function keep_(p) { return !SYNC.exclude.some(x => p.startsWith(x)); }

function folderAt_(root, dir) {
  return !dir ? root : dir.split('/').reduce((f, n) => {
    const it = f.getFoldersByName(n);
    return it.hasNext() ? it.next() : f.createFolder(n);
  }, root);
}

function gitSha_(blob) {
  const b = blob.getBytes();
  const h = Utilities.newBlob('blob ' + b.length + '\0').getBytes();
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, h.concat(b))
    .map(x => ((x + 256) % 256).toString(16).padStart(2, '0')).join('');
}

function mf_(sha, file) { return { s: sha, t: file.getLastUpdated().getTime(), i: file.getId() }; }

function conflictName_(n) {
  const stamp = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyyMMdd_HHmm');
  const i = n.lastIndexOf('.');
  return i > 0 ? n.slice(0, i) + SYNC.conflictTag + stamp + n.slice(i) : n + SYNC.conflictTag + stamp;
}

function mime_(name) {
  const ext = name.split('.').pop().toLowerCase();
  return ({ md: 'text/markdown', html: 'text/html', htm: 'text/html', css: 'text/css', js: 'text/javascript',
    json: 'application/json', py: 'text/x-python', txt: 'text/plain', svg: 'image/svg+xml',
    png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', pdf: 'application/pdf' })[ext] || 'application/octet-stream';
}

// 기준점(경로→{s,t,i})을 속성 값 크기 제한에 맞게 쪼개 저장
function loadManifest_(props) {
  const n = parseInt(props.getProperty('SY_MF_N') || '0', 10);
  let s = '';
  for (let i = 0; i < n; i++) s += props.getProperty('SY_MF_' + i) || '';
  return s ? JSON.parse(s) : {};
}

function saveManifest_(props, m) {
  const s = JSON.stringify(m), size = 2500;
  const n = Math.ceil(s.length / size);
  const oldN = parseInt(props.getProperty('SY_MF_N') || '0', 10);
  const obj = { SY_MF_N: String(n) };
  for (let i = 0; i < n; i++) obj['SY_MF_' + i] = s.substr(i * size, size);
  props.setProperties(obj);
  for (let i = n; i < oldN; i++) props.deleteProperty('SY_MF_' + i);
}

// 기준점 초기화 (다음 실행은 최초 실행처럼 전체 비교)
function resetSync() {
  const props = PropertiesService.getScriptProperties();
  Object.keys(props.getProperties()).filter(k => k.startsWith('SY_')).forEach(k => props.deleteProperty(k));
  Logger.log('동기화 기준점 초기화');
}

// 한 번만 실행 → 6시간 트리거 등록
function installSyncTrigger() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'syncSettlement')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('syncSettlement').timeBased().everyHours(6).create();
}
