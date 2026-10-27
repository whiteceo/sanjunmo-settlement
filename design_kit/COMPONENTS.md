# COMPONENTS — 화면 요소 마크업 가이드 (1장)

새 화면을 만들거나 화면을 고칠 때 이 마크업을 쓴다. class 이름은 **개발 이름**이고 모양은 `sjm-dev-skin.css` 가 프로토타입대로 입힌다.
값은 `tokens.css` 의 `--sjm-*` 변수를 쓴다(화면 CSS 에 hex 를 직접 쓰지 않는다).

## 1. 페이지 틀
```blade
@include('admin.layouts.header')
<main>
  <div class="container">
    @include('admin.inc.snb')
    <div class="content">
      <div class="content__header">
        <h2 class="content__title">월간 정산 및 집행</h2>
        {{-- 제목 줄 오른쪽 버튼(있을 때만) — 키트가 세로 가운데 · 오른쪽 28px 에 맞춘다 --}}
        <div style="position:absolute;right:0;top:0"><button type="button" class="btn">감사 로그</button></div>
      </div>
      … 구획(아래 2~5) …
    </div>
  </div>
</main>
@include('admin.layouts.footer')
```
- 제목은 흰 띠(하단선 #E2E8F0) 안 16px/800. 프로토타입의 breadcrumb(메뉴 그룹 › 화면명)는 필요하면 제목 앞에 `<span class="text--small">메뉴 그룹 ›</span>` 로 넣는다.
- 구획은 카드(`.content__wrap` 또는 `.search .search__wrap`) — 흰 바탕 · 테두리 · 둥글기 10px · 카드 간격 10~18px(`mgT10` 등 개발 여백 class 사용).

## 2. 검색 구역
```blade
<section class="search">
  <form method="get" action="{{ route('admin.xxx.index') }}" id="xxxSearchForm">
    <div class="search__wrap">
      <table class="search__table">
        <colgroup><col style="width:12%"><col style="width:38%"><col style="width:12%"><col style="width:38%"></colgroup>
        <tbody><tr><th>상태</th><td><select name="status" class="select">…</select></td>
                   <th>기간</th><td><input type="date" name="date_from" class="input__text"> ~ <input type="date" name="date_to" class="input__text"></td></tr></tbody>
      </table>
    </div>
    <button type="button" class="btn mgR10">초기화</button>
    <button type="submit" class="btn button--search">조회</button>
  </form>
</section>
```
- 조건 이름(th)은 짧게, 칸 안 입력은 32px. 빠른 기간 버튼은 `btn__small btn--basic`.

## 3. 목록
```blade
<section class="content__wrap mgT10">
  <div class="list__detail"><div class="list__detail__total">
    <span>전체 <strong>{{ number_format($list->total()) }}</strong>건</span>
    <button type="button" class="btn__small btn--save mgL10 layer__open" data-target="layerXxxDownload">엑셀 다운로드</button>
  </div></div>
  <table class="table__list">
    <thead><tr><th><input type="checkbox" id="checkAll"></th><th>정산월</th><th class="align--right">금액</th><th>상태</th></tr></thead>
    <tbody><tr><td><input type="checkbox" name="ids[]"></td><td data-label="정산월">2026-10</td>
               <td data-label="금액" class="align--right">1,250,000</td>
               <td data-label="상태"><span class="badge badge--soft badge--progress">검토중</span></td></tr></tbody>
  </table>
  @include('admin.inc.pagination', ['paginator' => $list])
</section>
```
- 글자는 왼쪽 정렬이 기본, 금액 · 수량은 `align--right`, 체크박스 칸은 자동 가운데.
- 상태는 배지로만 표시한다(글자색만 바꾸지 않는다). 색 대응은 `CLASS_MAP.md` 6절.
- 행 이동은 `td[data-url]`(개발 JS) 또는 이름 칸 링크(`link--view`).

## 4. 버튼 역할
| 역할 | 기본 크기(32px) | 작은 크기(28px) |
| :--- | :--- | :--- |
| 주 동작(저장 · 조회 · 확인 · 다운로드) | `btn btn--save` · `btn button--search` · `btn__system` | `btn__small btn--save` |
| 보조(취소 · 초기화 · 닫기) | `btn` · `btn__system btn--basic` | `btn__small btn--basic` |
| 강조 보조(진한) | `btn__system btn--secondary` | `btn__small` · `btn__small btn--secondary` |
| 위험(삭제 · 반려 · 정지) | `btn__system btn--warning` | `btn__small btn--line` |
| 엑셀 · 성공 | `btn__system btn--success` | `btn__small btn--excel` |
- 한 구역에 주 동작 버튼은 하나. 순서는 [보조] [주 동작](주 동작이 오른쪽 끝).
- 아이콘은 글자 앞 이모지나 개발 아이콘 버튼(`btn__icon`, `btn__tiny`)을 쓴다.

## 5. 상세 · 등록 폼
```blade
<section class="content__wrap mgT10">
  <table class="table__view">
    <colgroup><col style="width:18%"><col style="width:32%"><col style="width:18%"><col style="width:32%"></colgroup>
    <tbody>
      <tr><th>제목 <span class="text--required">*</span></th>
          <td colspan="3"><input type="text" name="title" class="input__text @error('title') fld--err @enderror" style="width:100%">
              @error('title')<p class="text--warning">{{ $message }}</p>@enderror
              <p class="fm-help">100자 이내</p></td></tr>
    </tbody>
  </table>
  <div class="btn__group">
    <a href="{{ route('admin.xxx.index') }}" class="btn">취소</a>
    <button type="submit" class="btn btn--save">저장</button>
  </div>
</section>
```
- 필수는 빨강 `*`(`text--required`), 오류는 칸 테두리(`fld--err`) + 아래 문구(`text--warning`), 도움말은 `fm-help`.

## 6. 탭
```blade
<div class="tab__wrap">
  <ul class="tab__menu"><li class="tab__item" data-tab="paneA">기본 정보</li><li class="tab__item" data-tab="paneB">이력</li></ul>
  <div class="tab__content" id="paneA">…</div>
  <div class="tab__content" id="paneB">…</div>
</div>
```
- 밑줄 탭. 켜짐 class 는 개발 JS 가 붙인다. 서버가 켜는 모양만 탭은 `tab__list` + `tab__item active`.

## 7. 모달
```blade
<div class="layer-pop__overlay layer-pop--hidden" id="layerXxx">
  <div class="layer-pop__wrap w--s">
    <button type="button" class="btn--close layer-pop--close" aria-label="닫기">닫기</button>
    <div class="layer-pop__content"><section class="layer__section">
      <h5 class="service__title layer__title">정산서 재발행</h5>
      <table class="table__view">…</table>
      <div class="btn__group">
        <button type="button" class="btn__system btn--basic layer-pop--close">취소</button>
        <button type="button" class="btn__system">재발행</button>
      </div>
    </section></div>
  </div>
</div>
<button type="button" class="btn__small btn--basic layer__open" data-target="layerXxx">재발행</button>
```
- 폭: 확인 · 알림 `w--xs`, 입력 몇 개 `w--s`, 표가 들어가면 `w--m`/`w--l`, 큰 편집 `w--full`.
- 하단 버튼은 오른쪽 정렬(한 버튼 알림만 `align--c`). 열기 · 닫기 · ESC 는 개발 JS.
- 하위 화면(S)이 독립 페이지인지 모달인지는 프로토타입 기준(`PROJECT_STATE.md` 1절 · `findings/PAGE_PATTERN.md`)을 따른다.

## 8. 안내 · 숫자
- 운영자에게 보여야 하는 안내: 카드 안 문단에 `fm-help`(일반) / `fm__help--warn`(주의). 프로토타입의 `.ctx-note` · `.access-notice` 와 같은 역할.
- 금액 · 건수는 등폭 숫자(`font-variant-numeric: tabular-nums`)로 보이게 한다 — 표의 금액 칸에 `class="align--right"` 와 함께 쓰면 키트가 글꼴을 맞춘다.
- 음수 금액은 `txt--red`.

## 9. 프로토타입에만 있는 공통 요소(개발 대응 class 없음)
| 요소 | 프로토타입 | 값 | 쓸 때 |
| :--- | :--- | :--- | :--- |
| KPI 카드 | `.kpi-grid > .kpi-card > .k-title · .k-num · .k-sub` | 흰 카드 둥글기 10px, padding 15px 16px, 제목 12.5px/700, 숫자 22px/800, 보조 11.5px, 칸 최소 200px 자동 채움 | 대시보드 · 목록 위 요약 카드를 만들 때 이 값으로 화면 CSS 작성 |
| 하위 뷰 전환 세그먼트 | `.subview-switcher > .subview-btn.active` | 회색 틀 #F1F5F9, 켜짐 흰 바탕 · 글자 #1D4ED8 | 한 화면 안 보기 전환 |
| 하단 고정 저장 바 | `.savebar` | SNB 오른쪽부터 화면 아래 고정 | 긴 등록 폼 |
