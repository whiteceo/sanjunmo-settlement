# 정산엔진 기준 계산기 (settle-calc)

정본 수식대로만 계산하는 독립 계산기. 개발 시스템(PHP · 라라벨 · MySQL)의 정산 결과가 정본과 맞는지 **단계별로** 대조하는 데 쓴다.
수식 · 절사 위치 · 단계 순서는 `SPEC.md`(정산 02권 8.3절 1~11단계 · 13장), 세무는 `TAX.md` · `tax_table.json`(02권 11장)을 따른다.
정본에 없거나 서로 어긋나는 곳은 지어내지 않고 잠정 규칙으로 표시하며, `OPEN_ISSUES.md`에 모았다.

- 엔진 1.0.0 · Python 3.10 이상 · 표준 라이브러리만(금액은 모두 `Decimal`, float 금지)
- fixture 테스트: 42건(변형 포함) 중 판정 대상 22건 — **PASS 19 · FAIL 3**(입력 부족 2 · 정본 모순 1, 엔진 오류 0) · 보류 20 → `OPEN_ISSUES.md`

## 폴더

| 경로 | 내용 | 담당 |
| :--- | :--- | :--- |
| `SPEC.md` · `schema/` | 수식 명세 · 입출력 스키마 | 1단계 수식 설계 |
| `TAX.md` · `tax_table.json` | 세무 판정표 · 9단계 의사코드 · 세율 | 1단계 세무 |
| `tests/fixtures/` · `tests/CASES.md` | 04권 Case 1~12 · 부록 D fixture | 1단계 검증 케이스 |
| `core/` | 엔진. `pipeline.py`(실행기 · 상태) · `s00_pipeline_in.py` ~ `s12_close_check.py`(단계별) · `tax.py`(세무 판정 · 세액) · `money.py`(절사) · `trace.py` · `steps.py` · `csvio.py` | 2단계 |
| `run.py` · `report.py` · `compare.py` | 실행 · HTML 단계표 · 개발 결과 대조 CLI | 2단계 |
| `tests/run_tests.py` · `adapter.py` · `aliases.py` · `judgments.json` | fixture 회귀 테스트 · 입력 변환 · 기대값 이름 연결 · 불일치 원인 판정 | 2단계 |
| `samples/sample/` | 입력 예시(가상 값) · 개발 출력 예시 · 대조 매핑 예시 | 2단계 |
| `OPEN_ISSUES.md` | 테스트 결과 · 불일치 원인 · 정본 확인 필요 · 스키마 보완 요청 | 2단계 |
| `out/` | 실행 산출물(git 제외) | — |

## 사용법

저장소 루트(`D:\Work\Settlement`)에서 실행한다.

계산(JSON 출력 + CSV + 권리자별 단계표 HTML):

```bash
python engine/run.py --input engine/samples/sample/input.json --out engine/out/sample.json --csv engine/out/sample_csv --html engine/out/sample.html
```

fixture 회귀 테스트(케이스별 HTML 포함):

```bash
python engine/tests/run_tests.py --html-dir engine/out/cases
```

개발 결과 대조(처음 갈라진 단계 표시):

```bash
python engine/compare.py --input engine/samples/sample/input.json --dev engine/samples/sample/dev_output.csv --map engine/samples/sample/dev_map.json --html engine/out/compare.html --csv engine/out/compare.csv
```

| 명령 | 하는 일 |
| :--- | :--- |
| `run.py --input in.json` | 계산. `--out` JSON · `--csv` 폴더(values · trace · payees · continuity · issues) · `--html` 단계표. 연속성 불일치 · 오류가 있으면 종료 코드 1 |
| `run.py --input-csv 폴더/` | CSV 입력(`<표 이름>.csv` + `_meta.json`, 중첩 배열은 JSON 문자열 칸)으로 계산 |
| `run.py --input in.json --to-csv 폴더/` | 계산 없이 입력 JSON을 CSV 폴더로 변환(왕복해도 같은 결과) |
| `report.py --result out.json --out r.html` | 이미 계산한 결과로 단계표 HTML |
| `compare.py (--input in.json \| --calc out.json) --dev 개발출력 --map 매핑.json` | 개발 결과 대조. `--html` · `--csv` · `--json`. 차이가 있으면 종료 코드 1 |
| `tests/run_tests.py [-k CASE-09] [-v] [--json r.json]` | fixture 전부(+변형) 계산 → 기대값 비교. `-v`는 서술 기대값 · 입력 변환 가정까지 출력. FAIL · ERROR가 없으면 종료 코드 0 |

샘플 결과(2026-09, 가상 값): H-KIM 70:30 분할(소속사 법인 TX-07 VAT 10%) · 런타임 가중 차시 분할 · 원 결제 분할로 환불 공제 · 지원금 한도 복원 · PRE_TAX 이월 지급 예약, H-LEE 기타소득(C15) 과세최저한 0원 → 지급 하한 미달 이월, H-PARK 대여금 선급금 상계 200,000 → 하한 미달 이월. 이월 연속성 등식 3건 모두 일치. 대조 예시는 개발 출력에 일부러 넣은 오류 두 개(H-PARK 상계액 잔액 한도 미적용 → 6단계, H-LEE 과세최저한 미적용 → 9단계)를 처음 갈라진 단계로 잡는다.

## 입력

`schema/input.schema.json`(03권 데이터 사전 컬럼명). 한 정산월 전체: 권리자 · 계약 · 요율 라인 · 강의/도서 매핑 · 수취인 분할 · 지원금 약정 · 대상 · 전월 원장 · 선급금 · 주문 품목(강의 차시 · 도서 · 위탁 · 상품) · 환불(원거래 `settlement_line_snapshot`) · 합격 환급 공제 · 승인 약정금 · 전속계약금 반환 · 이월 원장 · 조정 라인 · 이체 결과.
엔진이 추가로 읽는 선택 필드(스키마 보완 요청 S-01~S-05): `rate_lines[].pipeline_id`, `rights_holders[].withholding_decision` · `corp_no` · `vat_treatment` · `matrix_case_id_hint`, `order_items[].sale_price_incl_vat` · `purchase_unit_cost`, `snapshot.confirmed_qty`.

## 출력

`schema/output.schema.json` 구조 + 대조 · 테스트용 평면 목록.

| 키 | 내용 |
| :--- | :--- |
| `status` · `errors` · `warnings` | OK / INPUT_ERROR / LOCKED_MONTH / BLOCKED_PENDING_REVIEW(세무 판정 보류 라인이 있으면 마감 차단) |
| `rights_holders[].contracts[].steps` | 계약 단위 1~8단계 결과(CARRY_IN · ACCRUAL · MMG_ADJ · DEDUCT · SUPPORT_CAP · PREPAY_OFFSET · LUMPSUM_ADD · PAYEE_SPLIT) |
| `rights_holders[].contracts[].payees[]` | 수취인 단위: `lines[]`(8 · 9단계 라인별 분할액 · 상계 · 세전 지급액 · 과세표준 · 케이스 · VAT · 원천세 · 실정산액) · `TAX` · `CLAIM` · `PAYOUT` |
| `ledgers` | 마감 시 반영할 원장 예정 행(지원금 · MMG 보전금 · 이월 · 선급금) |
| `continuity` | 이월 연속성 등식 3종(PRE_TAX · POST_TAX · 위탁 전용) |
| `internal_only` · `excluded_lines` · `pending_adjustments` | 자사 집계 전용(P2.3 · 매입 재판매) · 비인입 · 보류 조정 라인 |
| `values` | (권리자, 계약, 수취인, 라인, 단계, 필드) → 값. 대조 · 테스트의 기준 |
| `trace` | 계산 줄마다 `step` · `step_code` · `scope`(권리자 · 계약 · 수취인 · 라인 · 약정 · 원거래) · `inputs` · `formula`(정본 표기) · `formula_code`(SPEC 의사코드) · `before_rounding` · `rounding`(NONE / Q4 / FLOOR_WON / ALLOC_LAST_REMAINDER / ABS_FLOOR_SIGN) · `result` · `canon_ref` · `provisional` · `note`(SPEC 16절 질문 번호). `output = false`는 중간 계산 줄 |
| `issues` | 이번 계산에서 쓴 잠정 규칙 · 입력 부족(질문 번호 포함) |

단계: 0 PIPELINE_IN(상위 인입) → 1 CARRY_IN → 2 ACCRUAL → 3 MMG_ADJ → 4 DEDUCT → 5 SUPPORT_CAP → 6 PREPAY_OFFSET → 7 LUMPSUM_ADD → 8 PAYEE_SPLIT → 9 TAX(끝에 6단계 현금 가용액 재검증) → 10 CLAIM → 11 PAYOUT → 12 CLOSE_CHECK(이월 연속성).
절사: `floor` = 원 단위 내림, 음수는 절대값 내림 후 부호 복원(0 방향). 중간값은 소수 4자리 보존.

## HTML 단계표

권리자 → 계약 → 단계 0~12를 펼쳐 계산 줄(입력 · 수식 · 의사코드 · 절사 전 · 절사 · 결과 · 근거)을 본다. 잠정 규칙 줄은 '잠정 Q-xx' 표시. '결과 값 줄만'을 켜면 중간 계산 줄을 숨긴다. 아래에 수취인 요약 · 이월 연속성 · 내부 집계 · 비인입 · 확인 필요 · 경고를 붙인다. fixture 테스트 HTML(`--html-dir`)은 맨 위에 판정 · 차이 · 서술 기대값 · 입력 변환 가정을 보여 준다.

## 대조 매핑(`--map`)

개발 출력 형식이 정해지지 않았으므로 설정 파일로 맞춘다. 예시: `samples/sample/dev_map.json`(long 형식).

```json
{
  "dev_format": "csv",
  "json_rows": "data.rows",
  "layout": "long",
  "keys": {"rights_holder_id": "holder_code", "contract_id": "contract_code", "payee_id": "payee_code", "line_id": null},
  "long": {"step_code": "step", "field": "item", "value": "amount", "step_alias": {}, "field_alias": {"net_pay": "net_settle_amount"}},
  "columns": {"income_tax": {"step_code": "TAX", "field": "income_tax_total"}},
  "id_alias": {"rights_holder_id": {"DEV-001": "H-KIM"}},
  "tolerance": 0,
  "include_calc_only": false
}
```

| 키 | 뜻 |
| :--- | :--- |
| `dev_format` · `json_rows` | `csv` 또는 `json`(생략 시 확장자로), JSON에서 행 배열 위치(점 경로) |
| `layout` | `wide`: 한 행 = 권리자 · 수취인 1명, 컬럼마다 `columns`로 (단계, 필드) 지정 / `long`: 한 행 = 값 하나 |
| `long` | 단계 컬럼(번호 · 코드 둘 다 받음) · 필드 컬럼 · 값 컬럼 · 별칭 |
| `keys` | 계산기 키 → 개발 컬럼. 계약 · 라인 컬럼이 없거나 비어 있으면 그 축은 가리지 않고 찾는다(라인 합계 행 우선, 없으면 라인 행 합) |
| `id_alias` · `tolerance` · `include_calc_only` | id 바꿔 읽기 · 허용 오차(원) · 개발 쪽에 없는 계산기 값도 나열 |

필드 이름은 `values`의 `field`(예: `accrual_total`, `offset_amount`, `withholding_total`, `net_settle_amount`, `payout_amount`)다. `run.py --csv`의 `values.csv`에서 전체 목록을 볼 수 있다.
판정: 일치 · 차이 · 계산기 값 없음 · 개발 값 없음. **권리자별로 단계 번호가 가장 작은 차이가 '처음 갈라진 단계'**이며, HTML은 그 단계의 계산기 trace(입력 · 수식 · 계산기 값)를 펼치고 개발 값은 위 표에 나란히 둔다.

## fixture 테스트

fixture는 04권 서술을 옮긴 형식이라 엔진 입력과 다르다.
- `tests/adapter.py`가 엔진 입력 스키마로 바꾸고, 정본에 없는 값을 채운 곳은 가정으로 남긴다(`-v` · HTML · `OPEN_ISSUES.md` 4절).
- `tests/aliases.py`가 기대값 경로(예: `TAX › P_AGENCY / vat`)를 엔진 필드(`TAX.vat_total`, 수취인 P_AGENCY)에 잇는다.

| 판정 | 뜻 |
| :--- | :--- |
| PASS | 수치 · 불리언 · null 기대값 모두 일치(문자열 '서술' 기대값은 목록만) |
| FAIL | 차이 있음 — 처음 갈라진 단계 · 경로 · 기대/계산 · 원인(엔진 오류 / 정본 모순 / 입력 부족, `tests/judgments.json`) |
| ERROR | 실행 오류 |
| HOLD | 보류 — 정본이 확정 보류(HELD) · 예시(ILLUSTRATIVE) · 일부만(PARTIAL) · 금액 없는 규칙(QUALITATIVE) 또는 계산 입력 없음. 비교는 하되 합격 집계에서 뺀다 |
