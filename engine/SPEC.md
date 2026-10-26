# 정산엔진 기준 계산기 — 수식 명세 (SPEC)

> 작성: calc-spec(수식 설계) · 2026-10-26 · 대상 정본 v4.0.x(00~04권, 2026-10-26 `main` 기준)
> 이 문서는 정본 수식을 **구현 가능한 형태로 옮긴 것**이다. 정본에 없는 규칙은 만들지 않았고, 정본이 비어 있거나 서로 어긋나는 곳은 끝의 **16절 '정본 확인 필요'** 에 모았다. 세무 세부 판정(9단계 내부)은 `engine/TAX.md`(세무 담당)가 정본이며, 여기서는 9단계의 입력 · 출력 인터페이스만 정한다.
> 스키마: `engine/schema/input.schema.json`, `engine/schema/output.schema.json`.

---

## 0. 표기 · 근거 약어

| 약어 | 문서 |
| :--- | :--- |
| `V1` | `docs/[산준모 정산시스템]_01_비즈니스정책_계약_도서_이월_기획서.md` |
| `V2` | `docs/[산준모 정산시스템]_02_SSOT_정산연산엔진_및_세무증빙_명세서.md` |
| `V3` | `docs/[산준모 정산시스템]_03_백오피스화면_외부연동_및_데이터사전.md` |
| `V4` | `docs/[산준모 정산시스템]_04_QA_정산케이스스펙_및_회귀테스트_법령근거.md` |

근거 표기: `V2 §8.3 5단계 L207` = 02권 8.3절 5단계, 파일 207번째 줄(2026-10-26 기준 줄 번호. 줄이 바뀌면 절 이름으로 찾는다).

정본 우선순위(V2 머리 L9, `PROJECT_STATE.md` 1절): 연산 수식 · 상태 전이 = V2 §8.3, 세무 판정 = V2 11장 · §10.4, 절사 · 역산 = V2 13장(13장이 개별 장 서술과 충돌하면 13장 우선, V2 §13 L561). V1 4~7 · 15장은 §8.3을 참조하는 정책 서술이다(V2 L164).

의사코드 규약:
- 모든 금액은 `Decimal`. float 금지.
- `floor(x)` = **원 단위 내림, 음수는 절대값 내림 후 부호 복원**(V2 §13.1 L569). 즉 `floor(-1234.7) = -1234`. 파이썬 `ROUND_DOWN`(0 방향)과 같다. 수학적 내림(`ROUND_FLOOR`)은 쓰지 않는다.
- `q4(x)` = 소수 4자리 보존(DECIMAL(18,4), V2 §13.1 L565). 4자리 밖의 처리 방식은 정본에 없다 → 16절 Q-01.
- `alloc_last_remainder(total, items, key_sort)` = 13.2 총액 역산: 정렬 순서상 마지막을 뺀 항목은 `floor(total × w_i)`, 마지막 항목은 `total − Σ선행`(V2 §13.2 L573).
- `[신규 명명]` = 03권 데이터 사전 · 01권 테이블 컬럼 정의에 없는 이름(스키마 설명란에도 같은 표시).

---

## 1. 계산 단위와 라인 키

| 단위 | 정의 | 근거 |
| :--- | :--- | :--- |
| 정산월 | 데이터 기준 월(구매확정일시 · 승인 확정일이 속한 월). '당월' = 이 월 | V1 §7.0 L521 |
| 권리자 | `rights_holder_id`. 재연산 단위(승인 이벤트 시 권리자 단위 전량 재연산) | V2 §10.1 L353 |
| 계약 | `contract_id`. 1~7단계 집계 단위. 선급금 상계 범위 = 동일 계약 | V2 §8.3 6단계 L224, V1 §5.3 L326 |
| 수취인 | `payee_id`(권리자 원장의 `rights_holder_id` 참조). 8단계 이후 단위 | V1 §4.2 L179, V3 데이터 사전 L112 |
| 정산 라인 | 아래 라인 키로 구분되는 행. 절사 · 분할 · 세무 계산의 최소 단위 | V2 §8.3 8단계 L248, §13.1 L566~567 |

**라인 키**(이 문서에서 '라인'은 다음 조합이 같은 금액의 묶음):
`(contract_id, pipeline_id, rate_type, agreement_id, approval_id, income_category, income_clause, tax_threshold_unit_key)`
- `pipeline_id` 값: `1.1`, `2.1`, `2.2`, `2.3`, `5.1`, `LUMPSUM`(7단계 비정기 가산 — `[신규 명명]` 값), 이월은 원장 값(`MIXED` 포함).
- R/S 라인과 지원금 라인, 2.1과 2.2는 반드시 분리 절사(V2 §13.1 L567).
- `OTHER` 소득은 `tax_threshold_unit_key`별 행 분리 유지(V2 §8.3 2단계 L184, V1 §6.3 L436).
- 근거: 8단계 "라인(정산 입력 구분 · 소득 구분 · 과세최저한 판정 단위 키 · 증빙 단위)"(V2 L248), 6단계 "약정 · 승인 식별자로 분리"(V2 L233). 증빙 단위의 구체 키는 정본에 정의가 없다 → 16절 Q-02.

---

## 2. 전체 데이터 흐름도 (1~11단계)

```
[상위 인입 파이프라인 V2 §8.3 1단계 L129~160]
  order_items(LECTURE) ─Step1 안분─Step2 차시분할─Step3 요율바인딩─Step4 1계층지분─► P1.1 라인(q4)
  book_sales(OWN_PUBLISHED, 구매확정월) ─6.3 절사 시퀀스─────────────────────► P2.1 라인(원)
  consignment_sales(CONSIGNMENT, 구매확정월) ─6.6 인입 공식─────────────────► P2.2 라인(원)
  rate_basis(P1.1 기준금 / P2.1 부수×기준가) × 지원금 요율 ──────────────────► P5.1 신규 발생(원)
  goods(Pipeline 2.3) ─► 자사 집계 전용(엔진 비인입, 출력 internal_only)
  PURCHASED_RESALE · BUNDLED 도서 ─► 비인입(0원)

 carryover_ledger(미소멸·NONE)
        │
  ①CARRY_IN ── PRE_TAX(+) 원귀속 미지급 소득 ──────────────────────────────┐
        │      PRE_TAX(−) 미확정 조정액 ──────────────────────────────┐   │
        │      POST_TAX(+) 지급대기액 ───────────────────────────┐   │   │
        │      POST_TAX(−) 반환채권 ────────────────────────┐   │   │   │
        │      위탁 전용 잔액 ─────────────┐               │   │   │   │
        ▼                                │               │   │   │   │
  ②ACCRUAL  P1.1, P2.1, P2.2, P5.1(신규)  │               │   │   │   │
        │   (+ 이월 포함 세전 처리잔액: 표시 전용)          │   │   │   │
        ▼                                │               │   │   │   │
  ③MMG_ADJ  P1.1 순수신규 < MMG → P1.1 = MMG, 보전금      │   │   │   │
        ▼                                ▼               │   │   │   │
  ④DEDUCT   P1.1 −환불−옵션B−옵션C / P2.1 −반품 / P2.2 −반품 + 위탁 전용 잔액
            P5.1 공제액 합계(원거래 역참조) ─────┐          │   │   │   │
        ▼                                     ▼          │   │   │   │
  ⑤SUPPORT_CAP  신규확정 = min(신규발생, 복원 후 한도); confirmed = 신규확정 − P5.1 공제
        ▼                                                │   │   │   │
  ⑥PREPAY_OFFSET  적격 세전액 → 상계 가능액 → 당월 상계액 → 라인별 안분 (차감은 8단계)
        ▼                                                │   │   │   │
  ⑦LUMPSUM_ADD  승인 약정금 · 매절 · 수당 · 지원금 일시/분할 · LUMP_SETTLE
        ▼                                                │   │   │   │
  ⑧PAYEE_SPLIT  라인별 floor(세전×split) + 마지막 수취인 역산 │   │   │   │
                세전 지급액 = 분할액 − 상계액, taxable_base 배열   │   │   ◄─┘(원귀속 유지, 재분할 금지)
                위탁 순액 패스스루 ───────────────────┐      │   │   ◄─┘(pending_negative_base)
        ▼                                         ▼      │   │
  ⑨TAX  (TAX.md) VAT · 원천세 · NET_DEDUCT 수수료 부가세 → 실정산액(상계허용분/보호분), PRE_TAX 세후 환산액
        ▼                                                │   │
  ⑩CLAIM  −전속계약금 반환(동의분) · 미상계 선급금 청구 전환 · 청구 판정 ◄┘(반환채권: 청구·회수)
        │  청구 확정 / 청구 이월(PRE_TAX 또는 POST_TAX) / 위탁 음수 → 위탁 전용 잔액
        ▼                                                    │
  ⑪PAYOUT  판정 금액 = 지급채무 순액(+PRE_TAX 세후 환산) + POST_TAX 지급대기액 ◄┘
           ≥ min_payout_limit 또는 강제 트리거 → 지급 확정(기존 이월행 RESERVED)
           미달 → 지급 이월(PRE_TAX 기초금액 / POST_TAX 유지)
        ▼
  [마감 검증] 세전 · 세후 · 위탁 전용 잔액 연속성 등식 3종(V1 §7.4 L588~595)
```

단계 묶음: 집계(1~2) / 보정(3~5) / 분배(6~8) / 과세 · 집행(9~11) — 배치 모니터링 · 재시도 단위(V2 §8.3 L117).

---

## 3. 상위 인입 파이프라인 (8.3절 1단계, 엔진 입력 전처리)

### 3.1 P1.1 온라인 강좌 R/S (V2 L131~136)
- **원천**: `order_items.item_type = LECTURE`.
- **Step 1 패키지 혜택 소급 안분**: 쿠폰 · 포인트 할인액을 강좌 정가 비율로 안분 → 실결제액. 잔여 1원은 13장: 정렬 `강좌 정가 내림차순 → product_id 오름차순`의 마지막 행이 잔여 차액(V2 §13.3 L577).
  ```
  for order in orders_with_discount:
      rows = sort(order.items, key=(-list_price, product_id))
      alloc = alloc_last_remainder(order.discount_total, rows, weight=list_price/Σlist_price)
      paid_amount[row] = list_price[row] − alloc[row]
  ```
  입력에 `paid_amount`(안분 후)가 이미 있으면 Step 1은 건너뛴다(`allocation_applied = true`).
- **Step 2 강의 차시별 분할**: 강좌 실결제액 × (차시 러닝타임 / Σ러닝타임). 러닝타임 0초 → `default_weight_seconds`(기본 60, 계약별 덮어쓰기 가능). 결과 `q4`(V2 L134, V3 부록B L466).
  ```
  w_i = runtime_i if runtime_i > 0 else default_weight_seconds
  lecture_base[i] = q4(paid_amount × w_i / Σw)
  ```
  차시 분할의 잔여 처리(13.4는 '강의 차시별 분할'을 13장 적용 범위에 포함, V2 L588)의 정렬 기준이 13.3에 없다 → 16절 Q-03.
- **Step 3 요율 바인딩**: 결제 승인 시점 스냅샷. 조회 키 = `lecture_instructors.contract_id`. `rate_type = BASIC` 라인만 바인딩. 지원금 요율은 `agreement_id`로 `rate_type = SUPPORT` 행을 결제 승인 시점 스냅샷으로 바인딩(V2 L135). 유효 라인은 단수(V1 §5.1 L210 중첩 차단).
  ```
  basic_rate = rate_lines.find(contract_id, rate_type=BASIC, start_date ≤ approved_at ≤ eff_end_date).rate_value
  eff_end_date = end_date if end_basis == FIXED_DATE else contract.current_end_date   # V1 L210
  ```
  유효 매핑 = 매핑 행 기간 ∩ 계약 유효 기간. 밖이면 미매핑(정산 0원, 판매 중단 대상)(V1 §4.2 L177~178).
- **Step 4 강의별 1계층 지분 연산**: `강의 기준금 × 권리자 지분율 × 계약 요율`. 강의 레벨 `q4`, **권리자별 월 합산 단계에서 1회 내림**(V2 L136).
  ```
  rs_q4[lecture, holder] = q4(lecture_base × share_ratio/100 × basic_rate/100)
  P1_1_new[line] = floor( Σ_{lectures in line, month} rs_q4 )        # 라인 = 1절 라인 키
  ```
  2계층 수취인 분할은 여기서 하지 않는다.
- **자사 권리자 산출액**(재원 한도 검증용, 발생액 아님): `기준금 × 자사 1계층 지분율`(자사 BASIC 요율 100% 고정, V2 §2.1 L24, V1 L263).

### 3.2 P2.1 자사 발행 도서 인세 (V2 L137~140, V1 §6.3 L427~436)
- 원천: `item_type = BOOK` 이고 `book_supply_type_snapshot = OWN_PUBLISHED`. 집계월 = 구매확정일시(배송 완료 D+7) 연월.
- 인세 기준가 = 판매 확정일이 속한 정가 버전(V2 L140). 자사 발행 인세 모수는 할인 후 실결제액(`sale_price`) 기준(V1 §5.5 박스 L389).
- **요율 · 기준선이 같은 공동 저자**(SKU 총액 → 총액 역산):
  ```
  line_q4 = q4(confirmed_qty × royalty_base_price × basic_rate/100)
  sku_total = floor( Σ line_q4 )                                    # V1 §6.3 1단계 L433
  authors = sort(authors, key=(-share_ratio, rights_holder_id))      # V2 §13.3 L580
  royalty[author] = alloc_last_remainder(sku_total, authors, w=share_ratio/100)   # V1 L434
  ```
- **요율 · 기준선이 다르면**: `royalty[author] = floor( Σ q4(line × share_ratio/100) )`, 총액 역산 미적용(V1 L435).
- 권리자별 월 합산: `BUSINESS`면 SKU별 배분액 합산(추가 절사 없음), `OTHER`(C15 · C05)면 `tax_threshold_unit_key = contract_id + book_sku_id`별 분리 유지(V1 L436).

### 3.3 P2.2 위탁 도서 판매대금 (V2 L141~147, V1 §6.6 L493~502)
- 원천: `book_supply_type_snapshot = CONSIGNMENT`. 집계월 = 구매확정일시.
- 정산 기준가: `consignment_base_price_type`(PAID_AMOUNT 기본 / LIST_PRICE)(V1 §5.5 박스 L390, V3 L43).
  ```
  monthly_sales      = Σ(confirmed_qty × consignment_price)                         # 월 판매대금
  net_before_fee_vat = floor( Σ(confirmed_qty × consignment_price × (1 − fee_rate)) ) # 1회 절사
  fee_supply         = monthly_sales − net_before_fee_vat                            # 별도 절사 금지(V1 L498)
  consignment_input  = net_before_fee_vat   if consignment_fee_type == NET_DEDUCT
                       monthly_sales        if consignment_fee_type == GROSS_SETTLE  # V2 L147
  ```
- 수수료 부가세(`floor(fee_supply × 10%)`)는 9단계에서 산출(V2 L266).
- **품목별 배분 고정**(환불 역참조용, V1 §6.6 L513): 월 확정 위탁 순액을 판매대금 비율로 `order_item_id → 낱권 순번 오름차순` 정렬, 마지막 품목이 잔여 부담(V2 §13.3 L582). 품목별 `수수료 공급가액 = 품목 판매대금 − 배분 위탁 순액`. 수수료 부가세는 월 확정세액을 별도 배분(배분 규칙의 가중치 · 정렬은 위와 같다고 읽음 → 16절 Q-04).

### 3.4 P2.3 일반 상품 (V2 L148~152)
- `공급가액 = floor( Σ(확정 수량 × VAT 포함 판매가) × 100/110 )`, `부가세 = Σ판매대금 − 공급가액`.
- 권리자 지급 엔진 비인입: 2단계 신규 발생 · 지원금 모수 · 선급금 상계 · MMG · 지급 하한 판정에 포함하지 않는다. 출력 `internal_only` 블록에만 기록.

### 3.5 비인입 (V2 L153~155)
- `PURCHASED_RESALE` · `BUNDLED` 도서는 어떤 파이프라인에도 인입하지 않는다(Case 11: 권리자 모수 0원). 출력에 `excluded_lines`로 사유와 함께 남긴다.

### 3.6 P5.1 매출연동 개발지원금 (V2 L156~160)
- 대상: `support_fund_agreements.payment_method = REVENUE_SHARE` 이고 `status = ACTIVE`(신규 발생). `COMPLETED · EXPIRED · TERMINATED`도 기확정 원거래의 환불 · 옵션 B · C 공제와 한도 복원은 4 · 5단계에 인입(V2 L158).
- 모수(`rate_basis = SAME_AS_BASIC`): P1.1 대상은 Step 2 강의 기준금, P2.1 대상은 확정 부수 × 약정 기준가(V1 L273). **자사 지분율을 곱하지 않는다**(V2 L159).
- `settlement_scope`: `PIPELINE_1_1_ONLY`(기본) / `PIPELINE_2_1_ONLY` / `PIPELINE_1_1_2_1`. P2.2 · P2.3은 어떤 경우도 제외.
- 약정 대상(`support_fund_agreement_targets`)의 유효 기간 안 · 자사 지분 > 0 인 대상만. 자사 지분 0% 구간은 발생 0원 · 상태 ACTIVE 유지 · 정산서 '자사 지분 없음으로 미발생'(V1 L274).
  ```
  basis = Σ_{targets ∩ scope} rate_basis_amount              # q4 유지
  support_new[agreement] = floor( basis × support_rate/100 )  # V2 L160, 2단계 L188
  ```
- 모수가 복수 파이프라인(`PIPELINE_1_1_2_1`)이면: 표시 순서 P1.1 → P2.1, **산출은 P2.1 몫을 먼저 내림, 잔여 차액을 P1.1에 귀속**(V2 §13.3 L581).
  ```
  part_2_1 = floor( support_new × basis_2_1 / basis )
  part_1_1 = support_new − part_2_1
  ```
- 재원 한도: `자사 배분가능액 = 기준금 × 자사 지분율`, `자사 최종 잔여액 = 자사 배분가능액 − 지원금 확정액 합계`(V1 L262~264). 동일 콘텐츠 · 기간 지원금 요율 합계 ≤ 자사 지분율 검증은 등록 시 수행(V1 L279) — 엔진은 위반 시 경고만 출력(`warnings`).

---

## 4. 1단계 CARRY_IN — 전월 이월 승계

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 §8.3 표 L168, 본문 L180~182 · V1 §7.4 L576~587 |
| 입력 | `carryover_ledger` 행 중 `extinguished_yn = false` 이고 `payout_reservation_status = NONE`, 해당 계약 · 수취인 |
| 처리 | 1회만 조회, 분리 전달. 재분할 · 재투입 금지 |
| 출력 | `carry_pre_tax_pos[]`(8 · 9단계), `carry_pre_tax_neg[]`(9단계 보류), `carry_post_tax_pos[]`(11단계), `carry_post_tax_neg[]`(10단계 청구 · 회수), `consignment_balance[contract]`(4단계 P2.2 상쇄 전용) |

```
rows = carryover_ledger.filter(contract_id, extinguished_yn == false, payout_reservation_status == NONE)
for r in rows:
    if r.consignment_balance_yn:            consignment_balance[r.contract_id] += r.carryover_amount   # account_type NULL
    elif r.account_type == PRE_TAX  and r.carryover_amount > 0: carry_pre_tax_pos.append(r)
    elif r.account_type == PRE_TAX  and r.carryover_amount < 0: carry_pre_tax_neg.append(r)
    elif r.account_type == POST_TAX and r.carryover_amount > 0: carry_post_tax_pos.append(r)
    elif r.account_type == POST_TAX and r.carryover_amount < 0: carry_post_tax_neg.append(r)
```
- 각 행은 원장에 기록된 `payee_id`, `pipeline_id`, `income_category`, `income_clause`, `tax_threshold_unit_key`를 그대로 유지한다(V2 L181).
- 현재 분할 설정이 바뀌어도 과거 확정 이월액은 다시 분할하지 않는다(V2 L181).
- 이월액은 3단계 MMG 모수, 6단계 상계 적격, 5단계 재투입 어디에도 넣지 않는다(V1 §7.4 L581, L583).
- P5.1 귀속 이월은 P5.1 전용 구분값을 유지(V1 L583).
- 이종 소득 구분 간 자동 상쇄 금지(V1 L582).
- 절사: 없음(원장 금액 그대로).

---

## 5. 2단계 ACCRUAL — 순 발생액 산출

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L169, 본문 L183~191 |
| 입력 | 3절 파이프라인 결과(P1.1 · P2.1 · P2.2 · P5.1), 1단계 PRE_TAX 이월 합계(표시용) |
| 출력 | 라인별 신규 세전액, `당월 신규 세전 발생액`, `이월 포함 세전 처리잔액`(표시용), `mmg_basis_1_1`(P1.1 순수 신규 R/S) |

```
new_1_1[line] = P1_1_new[line]                     # 당월 발생 R/S 합계
new_2_1[line] = P2_1_royalty[line]                 # 당월 확정 인세액
new_2_2[line] = consignment_input[contract]        # NET_DEDUCT/GROSS_SETTLE 분기 반영값
new_5_1[agr]  = support_new[agr] if agreement.status == ACTIVE else 0   # V2 L188, 5단계 3) L209
accrual_total = Σnew_1_1 + Σnew_2_1 + Σnew_2_2 + Σnew_5_1              # 당월 신규 세전 발생액
pre_tax_balance_incl_carry = accrual_total + Σcarry_pre_tax(pos+neg)    # 표시 전용(L190)
mmg_basis_1_1[contract] = Σnew_1_1                                       # 이월 · P5.1 제외(L191)
```
- 환불 · 프로모션은 반영하지 않는다(L184).
- 이월 합산값을 '신규 발생액'이라 부르지 않는다(L190) — 출력 필드명 분리.
- 절사: 3절에서 각 파이프라인이 라인별 1회 절사를 마친 값. 2단계에서 추가 절사 없음.

---

## 6. 3단계 MMG_ADJ — 월 보장액 보정

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L170, 본문 L192~195 · V1 §5.3 MMG L329~340 · V1 §15.2 L610~618 |
| 입력 | `mmg_basis_1_1`(2단계), 계약의 BASIC 요율 라인 `mmg_amount`, 옵션 B · C 발생 여부(플래그용) |
| 출력 | `adjusted_1_1`, `mmg_subsidy`(→ `mmg_subsidy_ledger`), `mmg_promo_overlap_flag` |

```
mmg = rate_line(BASIC, 유효).mmg_amount or 0
if mmg > 0 and mmg_basis_1_1 < mmg:
    adjusted_1_1 = mmg
    mmg_subsidy  = mmg − mmg_basis_1_1          # V2 L193
else:
    adjusted_1_1 = mmg_basis_1_1; mmg_subsidy = 0
mmg_promo_overlap_flag = (mmg_subsidy > 0) and (option_B_count + option_C_count > 0)   # V1 L617: 동일 월 동시 발생
```
- 판정 모수에서 제외: 환불 공제액, 옵션 B 분담액, 옵션 C 차감액, 전월 세전 이월액, P5.1(V1 L331~336, `support_fund_mmg_include_yn = false` 변경 불가 V3 L488).
- P1.1에만 적용. 차감은 4단계에서(순서 위반 시 플랫폼 이중 부담, V1 §15.2 L612~616 예시: R/S 300,000 · MMG 1,500,000 · 옵션 C 200,000 → 보전금 1,200,000, 최종 1,300,000).
- `mmg_annual_cap` 초과 시 알럿 · 재무 승인 전환(V1 L339) — 엔진은 `warnings`에 기록, 금액은 바꾸지 않는다(초과분 처리 방식은 승인 결과 입력이 없으면 정본 수식 없음 → 16절 Q-05).
- MMG 보전금은 6단계 상계 모수 · 10단계 미상계 선급금 차감 대상에서 제외(L193).
- 다중 라인 · 복수 강의일 때 `adjusted_1_1`을 어느 P1.1 라인에 귀속하는지 정본에 없다 → 16절 Q-06.
- 절사: 없음(정수끼리 차).

---

## 7. 4단계 DEDUCT — 환불 및 프로모션 공제

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L171, 본문 L196~203 · V1 §5.1 환불 대칭 L211 · V1 §6.3 반품 L430 · V1 §15.1 L602~608 · V1 §15.3 L620~625 |
| 입력 | 3단계 `adjusted_1_1`, 2단계 `new_2_1 · new_2_2 · new_5_1`, 환불 · 반품 라인(원거래 `settlement_line_snapshot` 포함), 합격 환급 공제 라인(옵션 B · C), 1단계 `consignment_balance` |
| 출력 | 라인별 세전 순액(`net_1_1 · net_2_1 · net_2_2`), `support_deduct_total[agr]`(P5.1 공제 합계), 공제 구성요소 배열(`deduct_components[]`: 원거래 · 경로 · 원거래 수취인 배분) |

### 7.1 수식
```
net_1_1 = adjusted_1_1 − refund_deduct_1_1 − optB_deduct_1_1 − optC_deduct_1_1   # V2 L198
net_2_1 = new_2_1 − return_deduct_2_1                                             # V2 L199
net_2_2 = new_2_2 − return_deduct_2_2 + consignment_balance[contract]            # V2 L200 (잔액은 음수 상쇄분)
support_deduct_total[agr] = refund_5_1 + optB_5_1 + optC_5_1                     # V2 L201
```
### 7.2 공제 단가 — 원거래 스냅샷 역참조
- 환불 공제 단가는 **환불 처리일이 아니라 원 결제 건의 `settlement_line_snapshot`**(당시 요율 · 지분율 · `rate_type` · 수취인 분할 비율)으로 대칭 공제(V1 §5.1 L211, V2 L202).
- P1.1 환불: `refund_deduct_1_1 = Σ q4(환불 기준금 × snap.share_ratio/100 × snap.rate_value/100)` → 라인 월 합산 후 `floor`(절대값 내림, V2 §13.1). 예: Case 9-B `2,000,000 × 60% × 50% = 600,000`(V4 L241).
- P2.1 반품: 원 판매 확정 시점의 정가 · 요율 · 지분율 스냅샷(V1 §6.3 L430).
- P2.2 반품: 원판매에 확정 · 배분된 판매대금 · 수수료 공급가액 · 수수료 부가세를 각각 참조(V1 L509). NET_DEDUCT 지급 조정 = `−판매대금 − (−수수료 공급가액) − (−수수료 부가세)`(Case 10-B, V4 L253: −125,000 + 31,250 + 3,125 = −90,625). 4단계 P2.2 순액에는 **수수료 부가세 차감 전 위탁 순액 기준** 조정분(−125,000 + 31,250 = −93,750)을 반영하고 수수료 부가세 조정(−3,125)은 9단계에서 반영한다(6.6절 '수수료 부가세는 세무 단계' L501과 맞춤 — 해석, 16절 Q-07).
- P5.1 공제(원거래 지원금 확정 배분액 역참조, 당월 요율로 재산정 금지, 각 원거래 미환불 확정액 초과 금지 — V2 L201):
  ```
  refund_5_1 = Σ_tx min( floor(tx.support_confirmed_alloc × tx.refund_ratio), tx.unrefunded_support_confirmed )
  optB_5_1   = Σ_tx min( floor(tx.support_confirmed_alloc × tx.optB_burden_ratio), tx.unrefunded_support_confirmed )
  optC_5_1   = Σ_tx min( tx.support_confirmed_alloc × tx.optC_cancel_ratio,  tx.unrefunded_support_confirmed )  # 정본에 내림 없음 → Q-08
  ```
  예: Case 9-B 원거래 확정 150,000 × 절반 = 75,000(V4 L241).

### 7.3 합격 환급반 옵션 (V1 §15.1 L602~608, §15.3 L622~625)
| `refund_promo_burden_type` | 처리 | 4단계 공제 | 재연산 |
| :--- | :--- | :--- | :--- |
| `A`(기본값) | 플랫폼 전액 부담 | 0원(R/S 모수 · MMG 모수 영향 없음) | 하지 않음 |
| `B` 비율 공동 부담 | 환급금을 계약상 R/S 지분율과 같은 비율로 분담 | `optB_deduct_1_1`, `optB_5_1` | 권리자별 1회 |
| `C` 매출 취소 | 원 매출 취소로 간주, 해당 결제액 전액 차감 | `optC_deduct_1_1`, `optC_5_1` | 권리자별 1회 |
- 귀속월 = 환급 승인 확정일이 속한 월(원 결제월로 소급하지 않음, V1 L623).
- 단가: 원 결제 스냅샷의 요율 · 지분율 · 원거래 지원금 확정 배분액 한도(V1 L625). `rate_type`별로 BASIC과 SUPPORT를 각각 공제, 신규 지원금 기준금에서 중복 차감 금지.
- 옵션 B의 P1.1 분담액 산식(“R/S 지분율과 동일한 비율”의 수치 정의 · 절사)은 정본에 산식으로 없다 → 16절 Q-09. 옵션 C P1.1 = 결제액 기준 R/S 스냅샷 대칭 공제(“해당 결제액을 전액 차감”, V1 L606)로 읽는다.
- 옵션 B · C 차감은 선급금 상계 모수 제외 대상이 아니다 — 차감 후 세전액이 상계 기준(V1 §15.2 L618).

### 7.4 환불의 세무 경로 분리 (V2 L197)
원거래 지급 상태로 구성요소를 나눈다(부분 지급이면 지급분 · 미지급분 각각). 한 거래를 일괄 처리하지 않는다.
| 경로 | 조건 | 처리 |
| :--- | :--- | :--- |
| `UNPAID_REDUCTION` 미지급 대가 감액 | 실제 지급 · 적법한 상계 · 법령상 지급 의제 미성립분 | 해당 원거래의 미지급 잔액 직접 감액. 원거래 미지급 잔액이 PRE_TAX 이월행이면 그 행을 감액(동일 원거래 내 감액 — 비상계 원칙 예외, V1 §7.3 L574) |
| `PAID_RETURN` 기지급 소득 반환 | 원천징수 사건 성립분 | 원거래 세무 정정 + 세후 반환채권(`POST_TAX`) — 10단계로 전달, 당월 신규 과세표준에서 자동 차감하지 않음(V4 Case 4 L146) |
- 경로별 금액 산정식(특히 원거래 미지급 잔액을 포함한 '원장 등식', 반환채권의 세전 · 세후 구성)은 정본이 기대값 확정을 보류했다(V4 Case 4 L113, Case 5 L162) → 16절 Q-10. 구현은 입력 스냅샷의 `payment_state`별 금액을 받아 경로만 분리하고, 금액 계산식은 Q-10 확정 전까지 아래 잠정 규칙을 trace에 `provisional=true`로 남긴다.
  - 잠정: `UNPAID_REDUCTION`분 → 7.1 라인 수식에서 차감. `PAID_RETURN`분 → 라인 차감에서 제외하고 `return_claims[]`(세후 반환채권 후보, 금액 = 입력 `paid_return_post_tax_amount`)로 10단계 전달.

### 7.5 8단계용 구성요소 보존
- 원거래에 귀속이 확정된 환불 · 반환 라인은 **원거래 수취인 귀속을 유지**하며 재분할하지 않는다(V2 §8.3 8단계 L249, V4 D-1 · D-2). 따라서 4단계는 라인 순액과 별도로 공제 구성요소를 `snapshot_payee_splits`와 함께 8단계에 넘긴다(9절 참조).
- 절사: 공제액은 라인별 월 합산 후 1회 `floor`(음수 규칙). P5.1 일반 환불 · 옵션 B는 원거래 단위 내림이 정본에 명시(V2 L201) — 13.1(월 합산 1회)과의 관계는 16절 Q-08.

---

## 8. 5단계 SUPPORT_CAP — 지원금 한도 · 순누계

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L172, 본문 L204~214 · V1 §5.2 L280~308 · V2 §10.1 지원금 원장 재연산 L356 |
| 입력 | 약정별 `new_5_1`(2단계), `support_deduct_total`(4단계), 전월 `support_fund_ledger`(`cap_consumed_amount`, `confirmed_net_total`, `cash_paid_total`), 약정(`cap_type`, `total_cap_amount`, `cap_restore_on_refund`, `status`, `end_date`/`end_basis`), 7단계 `LUMP_SETTLE` 승인 |
| 출력 | `confirmed_amount`, `remaining_cap`, `cap_consumed_amount`, `confirmed_net_total`, `status`(전이 · 감사 로그), 소진 원장 행 |

### 8.1 CAPPED
```
deduct        = support_deduct_total[agr]                                   # 1) 공제 합계
restore       = Σ_tx min(tx.deduct_5_1, tx.unrefunded_support_confirmed) if cap_restore_on_refund else 0   # 1) 복원액(원거래 미환불 확정액 초과 금지)
avail_cap     = total_cap_amount − prev.cap_consumed_amount + restore      # 2) cash_paid_total 사용 금지
new_confirmed = min(new_5_1, avail_cap) if status_at_start == ACTIVE else 0 # 3) 순수 신규(≥0)에 한도 먼저
confirmed_amount = new_confirmed − deduct                                   # 4) 순액 양수여도 3)과 1)·4) 각각 수행
cap_consumed  = prev.cap_consumed_amount + new_confirmed − restore + lump_settle_applied   # 5) (LUMP_SETTLE는 7단계 인입 시)
confirmed_net_total = prev.confirmed_net_total + new_confirmed − deduct     # 5) 복원 옵션과 무관
remaining_cap = total_cap_amount − cap_consumed
expired_excess = new_5_1 − new_confirmed                                    # 한도 초과분: 이월 없이 소멸(V4 Case 9 L232)
```
상태 전이:
```
if remaining_cap == 0 and status == ACTIVE:           status → COMPLETED (차월 신규 발생 중단)       # L211
if status == COMPLETED and remaining_cap > 0 and settlement_month ≤ 약정 종료월:  status → ACTIVE (감사 로그)  # L212
if status in (EXPIRED, TERMINATED): 잔여 한도 기록만 복원, ACTIVE 재개 금지                         # L212
```
- 완료 판정에 공제 후 확정액 · 송금액을 쓰지 않는다(L211).
- `LUMP_SETTLE` 승인액은 7단계 인입 시점에 '종료 승인액' 별도 항목으로 소진액에 가산, 승인 건 식별자로 중복 방지, 종료 승인 시점에는 소진액 미갱신(L211, V1 L303).
- 검증: D-9(V4 L291) `new 400,000 · avail 150,000 · 옵션B 100,000 → new_confirmed 150,000, confirmed 50,000, remaining 100,000`. Case 9(V4 L232) `confirmed 150,000, cap_consumed 3,000,000 → COMPLETED`.

### 8.2 UNLIMITED
```
confirmed_amount = new_5_1 − deduct          # 한도 판정 · 소진액 · COMPLETED 전이 생략
cap_consumed_amount = NULL; remaining_cap = NULL
confirmed_net_total = prev.confirmed_net_total + new_5_1 − deduct
```
- 확정액이 음수이면 한도 복원 없이 음수 라인(원거래 지급 상태에 따라 미지급 감액 / 기지급 반환채권)(L205).
- UNLIMITED는 COMPLETED로 전이하지 않음. 종료 시 EXPIRED/TERMINATED, `on_termination_policy = NONE` 고정(V1 L305~307).

### 8.3 원장 · 재연산
- `support_fund_ledger` 당월 행: `accrued_amount = new_5_1`, `confirmed_amount`, `confirmed_net_total`, `cap_consumed_amount`, `cash_paid_total`(실제 지급 이력 기준 유지 — 엔진은 입력값 그대로 전달), `remaining_cap`(L213).
- 재연산 멱등성: 해당 월 행을 삭제 후 재생성. 누계는 **대상월 이전 행 합계(입력 `prev`)에 당월분만 반영**, 증분 갱신 금지(V2 §10.1 L356). 엔진 입력은 반드시 '전월 말 원장 상태'여야 한다.
- 절사: 없음(2 · 4단계 원 단위 값의 가감).
- `confirmed_amount`가 CAPPED에서 음수가 되는 경우(복원 후)의 경로 처리 서술은 UNLIMITED만 명시 → 16절 Q-11.

---

## 9. 6단계 PREPAY_OFFSET — 선급금 상계

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L173, 본문 L215~236 · V1 §5.3 L316~328 · V1 §7.1 L525~531 · V2 §13.3 L579 |
| 입력 | 계약의 선급금(미상계 잔액, `prepayment_tax_type`, `offset_payee_id`), 2 · 3 · 4 · 5 · 7단계 결과(동일 계약), 9단계 세무 규격(예상 원천세 산출 함수) |
| 출력 | `offset_eligible_total`, `offset_withholding_equiv`, `offset_capacity`(상계 가능액), `offset_amount`(라인별 배분 포함), `prepay_balance_after`(예정), `taxable_reduction_flag` |

### 9.1 적격 세전액 (동일 `contract_id` 라인만)
```
e_1_1   = max(0, new_1_1_pure − deduct_1_1_total)      # = max(0, net_1_1 − mmg_subsidy) (L218, D-10)
e_2_1   = max(0, net_2_1)                              # L219
e_5_1   = Σ_{agr: offset_type == CONDITIONAL} max(0, confirmed_amount[agr])          # L220
e_ls    = Σ_{LUMP_SETTLE 승인, 약정 offset_type == CONDITIONAL} amount              # L221
e_inst  = Σ_{일시금·분할형 지원금 승인, offset_type == CONDITIONAL} amount           # L222
offset_eligible_total = e_1_1 + e_2_1 + e_5_1 + e_inst + e_ls                       # L223
```
- 절대 제외: MMG 보전금, 확정 이월액, 자사 내부 매출 · 잔여 귀속액, P2.2, `NON_OFFSET` 지원금(매출연동 · 일시 · 분할), 전속계약금 · 매절 · 정액 수당, 다른 수취인 금액(L225).
- 위탁 정산액 제외 사유: 위탁자 귀속 판매대금(L226).
- `deduct_1_1_total`이 7.4의 `PAID_RETURN`분까지 포함하는지는 16절 Q-12.

### 9.2 상계 가능액 · 당월 상계액
```
if prepayment_tax_type == LOAN:
    offset_withholding_equiv = TAX.estimate_withholding(eligible_lines_by_pipeline_income)   # 9단계와 같은 순차 산식(L227~228)
else:  # EARNED
    offset_withholding_equiv = 0
# 원천징수 비대상 라인은 0원(L227)
offset_capacity = offset_eligible_total − offset_withholding_equiv                         # L229
if offset_capacity <= 0:  offset_amount = 0; balance 유지                                   # L230 실행 가드
else:                     offset_amount = min(offset_capacity, prepay_unoffset_balance)    # L231
```
- 검증: Case 1(V4 L40) LOAN `2,500,000 − 82,500 = 2,417,500 → min(·, 1,500,000) = 1,500,000`. Case 1-B(V4 L51) `500,000 − 16,500 = 483,500 → 483,500`, 잔액 1,016,500. EARNED는 상계 가능액 500,000 전부 상계.

### 9.3 라인별 안분 (V2 L232~233, §13.3 L579)
```
pos = [l for l in eligible_lines if l.eligible > 0]          # 음수 · 0원 라인 배분 0원
den = Σ pos.eligible
order = sort(pos, key=(eligible ASC, is_1_1 ASC /*동률이면 P1.1을 뒤로*/, pipeline_id, agreement_or_approval_id, line_id))
for l in order[:-1]: l.offset = floor(offset_amount × l.eligible / den)
order[-1].offset = offset_amount − Σ선행                    # 적격액 최대 라인이 잔여
```
- CONDITIONAL 매출연동 P5.1(5단계 확정액) 라인과 CONDITIONAL 일시 · 분할형 라인은 각각의 `pipeline_id` · 약정 · 승인 식별자로 분리 안분(L233).
- 검증: Case 2(V4 L61~63) P2.1 `floor(500,000 × 200,000/1,200,000) = 83,333`, P1.1 `416,667`. D-6 동률 결정성(V4 L288).

### 9.4 귀속 · 과세표준 · 확정 시점
- 상계액은 원 권리자 단일 수취인(`offset_payee_id`, 시스템 자동 · 수정 불가)에 귀속. 세전 순액에서 직접 차감하지 않고 8단계로 전달(L234, V1 L322).
- `taxable_reduction_flag = (prepayment_tax_type == EARNED)`(L235).
- **9단계 재검증**: 9단계에서 확정한 상계 적격 라인 기준 '계산상 현금 가용액'이 회수액보다 작으면 회수액을 축소하고 선급금 잔액 · 라인 배분을 다시 맞춘다(L228, L231). 현금 가용액의 정확한 산식은 정본에 없다 → 16절 Q-13. 잠정: `cash_avail = Σ_{eligible lines}(분할액 − 라인 원천세)`; `offset_amount = min(offset_amount, cash_avail)` 후 9.3 재안분, trace `provisional=true`.
- `Locked = False`이면 '상계 예정액'으로만 표기, 실제 잔액 차감은 마감 확정 트랜잭션에서(V1 §7.1 L531). 엔진 출력은 항상 '예정' 값.
- 선급금 계약에는 수취인 분할이 없어야 한다(V1 L323). 입력에 둘 다 있으면 엔진은 `input_error`로 중단(서버 공통 검증과 같은 규칙).

---

## 10. 7단계 LUMPSUM_ADD — 비정기 가산

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L174, 본문 L237~244 · V1 §5.1 매절 L229~239 · V1 §5.2 L243~308 · V1 §7.2 L533~548 |
| 입력 | ADMN-INST-002에서 당월 귀속(`target_month = 정산월`)으로 검수 승인된 항목(`approval_status = APPROVED`) |
| 출력 | 라인별 가산액(소득 구분 키 유지), `lumpsum_total`, 분할 전 정산 공급가액(상계 전) |

```
lumpsum_total = Σ signing_bonus + Σ support_lump_sum_installment + Σ buyout + Σ fixed_fee + Σ lump_settle   # L239
```
- 매출연동형 지원금의 월 지급분은 인입하지 않음(L240).
- 각 항목의 `income_category`, `income_clause`, `payee_is_author`, `tax_threshold_unit_key`(OTHER이면 `contract_id + milestone_id`)를 라인 단위로 유지하여 9단계 전달(L242).
- `LUMP_SETTLE` 인입 시 5단계 소진액에 종료 승인액 가산 · 약정 종결 전이, 승인 건 식별자 중복 방지(L241).
- 전속계약금 반환액은 세후 항목 → 여기서 차감하지 않고 10단계에서 1회(L243).
- 분할 전 정산 공급가액 = `Σnet_1_1 + Σnet_2_1 + Σconfirmed_amount(5.1) + lumpsum_total`(상계 전). 표시 · 분할 기준용(V4 Case 1 L41, Case 3 L94).
- 위약금은 어느 단계에도 인입하지 않는다(V1 L253) — 입력에 와도 `excluded_lines`.
- 절사: 없음(승인 금액은 원 단위).

---

## 11. 8단계 PAYEE_SPLIT — 수취인 분할

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L175, 본문 L245~259 · V1 §4.1 L157~170 · V1 §4.2 L179 · V2 §13.2~13.4 |
| 입력 | 4단계 라인 순액(P1.1 · P2.1) + 공제 구성요소, 5단계 `confirmed_amount`, 7단계 라인, 6단계 라인별 상계액, `payee_splits`(유효 버전), 1단계 PRE_TAX 이월 배열, 4단계 P2.2 순 위탁 정산액 |
| 출력 | `payee_split_base`(표시용 합계), payee × 라인 `split_amount`, `pre_tax_payable`(당월 신규 세전 지급액), `taxable_base` / `pending_negative_base`, 원귀속 PRE_TAX 배열, 위탁자별 순 위탁 정산액, 라인 세무 속성 키 |

### 11.1 분할 기준액 (표시용)
```
payee_split_base = Σnet_1_1 + Σnet_2_1 + Σconfirmed_amount(5.1) + lumpsum_total   # L247
# 제외: 상계액, PRE_TAX/POST_TAX 이월, 전속계약금 반환, 만료·해지 미상계 선급금 청구 전환액, P2.2
```
### 11.2 라인 우선 분할 (13.2 · 13.3)
```
splits = payee_splits.valid(contract_id, rights_holder_id, settlement_month) or [{payee_id: rights_holder_id, split_ratio: 100}]  # L258
order  = sort(splits, key=(-split_ratio, payee_id))                       # V2 §13.3 L578
for line in new_lines:                      # 신규 분할 대상 라인(라인별 판정)
    for p in order[:-1]: split[p, line] = floor(line.amount × p.split_ratio/100)
    split[order[-1], line] = line.amount − Σ선행                          # L248
```
- 검증: Case 7(V4 L203~204) `floor(2,000,000 × 70%) = 1,400,000`, 소속사 `600,000`.
- **원거래 귀속 라인**(환불 · 반환 · 이월): 합산 기준액 부호와 무관하게 원거래 수취인 귀속 유지, 재분할 금지(L249). 4단계 공제 구성요소는 `snapshot_payee_splits` 비율로 같은 13.2 규칙을 적용해 수취인별 음수 금액을 만든다(V1 L211 '원 결제 시점 비율로 수취인별 배분', V4 D-1). 신규분과 공제분을 따로 분할하므로 단일 수취인이 아닌 계약은 '순액을 한 번에 분할'한 값과 1원 차이가 날 수 있다 → 16절 Q-14.
- 원거래 귀속이 없는 음수 조정액은 승인된 귀속 기준, 미확정이면 판정 보류(L249).
- **비분할 귀속**: 선급금 상계액(원 권리자), 이월액(원장 수취인), 전속계약금 반환(지정 수취인)은 13장 배분 대상이 아님(V2 §13.4 L589, V1 L164~167).
- **P2.2**: 분할하지 않고 위탁자 단독 수취인에게 패스스루(L250, V1 L170).
- P5.1 · 7단계 라인에 약정 · 승인 원장의 `payee_id`가 따로 있는 경우의 처리 → 16절 Q-15.

### 11.3 세전 지급액 · 과세표준
```
pre_tax_payable[p, line] = split[p, line] − offset[p, line]               # L251 (상계는 원 권리자 라인에만)
if prepayment_tax_type == LOAN:   taxable_base[p, line] = split[p, line]                    # L253
if prepayment_tax_type == EARNED: taxable_base[p, line] = split[p, line] − offset[p, line]   # L254 (당월 상계 적격 금액 한정, L257)
선급금 없음:                       taxable_base[p, line] = split[p, line]
if taxable_base < 0: pending_negative_base[p, line] = taxable_base; taxable_base = 0        # 9단계 L281 (보류)
```
- `POST_TAX` 이월 · 전속계약금 반환 · 미상계 선급금 청구 전환액은 과세표준에 산입하지 않음(L255).
- P2.2 · P2.3 라인은 과세표준 미생성(L256, V2 §2.1 L40).
- **원귀속 PRE_TAX 결합**: `carry_pre_tax_pos`는 별도 배열로 9단계 전달. `원귀속 세전 이월 세전 지급액[payee, carry_line] = 원귀속 세전 미지급 소득 기초금액`. 현재 분할 비율 미적용. 다른 원거래의 당월 환불 · 반환채권 음수와 자동 교차 상쇄 금지(해당 원거래 직접 감액 제외). `carry_pre_tax_neg`는 확정 전 과세표준 합산 금지 → `pending_negative_base`(L257, V4 D-3).
- 절사: 분할 시 선행 수취인 `floor`, 마지막 역산. 그 밖에 없음.

---

## 12. 9단계 TAX — 인터페이스 (세부 판정은 `engine/TAX.md`)

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L176, 본문 L260~283 · V2 11장(L399~) · V1 §6.3 3단계 L437~448 · V1 §6.6 L501~502 |
| 호출 | ① 6단계에서 `estimate_withholding()`(LOAN 상계 원천세 상당액) ② 8단계 후 `compute()` |

### 12.1 입력 (payee × 라인 배열 3종)
| 배열 | 필드 |
| :--- | :--- |
| `new_lines[]`(당월 신규) | `payee_id`, 라인 키 전체, `supply_nature`(LECTURE_RS / ROYALTY / BUYOUT / NONRECURRING / BOOK_GOODS — 11.1 '공급 성격' `[신규 명명]` 값), `industry_code`, `split_amount`, `offset_amount`, `pre_tax_payable`, `taxable_base`, `pending_negative_base`, `protected_yn`(상계 비대상 보호분: MMG 보전금 몫 · NON_OFFSET 지원금 · 비정기 약정금), `payment_event_date`(세율 기준일) |
| `carry_pre_tax_lines[]`(원귀속) | 원장 행 키 + `carryover_amount`(기초금액) |
| `consignment_lines[]` | `payee_id`(위탁자), `contract_id`, `net_consignment`(4단계 순액), `fee_supply_net`(당월 순 수수료 공급가액), `consignment_fee_type` |
| 수취인 속성 | `payee_tax_type`, `tax_invoice_eligible_yn`, `is_resident`, `payee_is_author`, `main_work_external_labor`, `is_internal`, `vat_treatment`, `book_supply_type`, `business_status` |
| 파라미터 | 부록 B: `local_income_tax_rate`, `other_income_min_tax_amount`, `deemed_expense_rate_c15_c19`, `deemed_expense_rate_c05_c17`, `small_amount_exemption_limit`, `small_amount_exemption_excluded_types`, `local_tax_small_exemption_apply_yn` + `engine/tax_table.json` |

### 12.2 출력 (라인별 + payee 합계)
| 필드 | 정의(정본 표기) | 근거 |
| :--- | :--- | :--- |
| `matrix_case_id`, `tax_decision_status` | TX-01~13 / DECIDED · PENDING_REVIEW | V2 §11.1 L407~411 |
| `supply_amount`, `vat_amount`, `vat_applied_amount` | VAT_EXCLUDED: `공급가액 = 세전 지급액(상계 전 공급가액 기준)`, `부가세 = 내림(공급가액 × 10%)`, `부가세 반영 후 정산액 = 세전 지급액 + 부가세` / VAT_INCLUDED: `공급가액 = 내림(총액 × 100/110)`, `부가세 = 총액 − 공급가액` | V2 L263~265 |
| `income_tax`, `local_income_tax`, `withholding_total` | `소득세 = 내림(과세표준 × 소득세율)`, `지방소득세 = 내림(소득세 × 10%)` 순차(합산세율 금지) | V2 L268~271 |
| `deemed_expense`, `other_income_amount`, `threshold_exempt_yn` | OTHER: `필요경비 = 내림(판정 단위 과세표준 × 의제율)`, `기타소득금액 = 과세표준 − 필요경비`, `≤ 50,000`이면 세액 0 | V2 L273~278 |
| `small_amount_exempt_yn` | 소득세 1천 원 미만 비징수, 인적용역 사업소득 제외 | V2 L279 |
| `consignment_fee_vat`, `consignment_settle_amount` | `위탁 수수료 부가세 = 내림(당월 순 위탁 수수료 공급가액 × 10%)`, NET_DEDUCT: `위탁 실정산액 = 순 위탁 정산액 − 수수료 부가세`, GROSS_SETTLE: `= 순 위탁 정산액`(수수료 · 부가세 별도 청구) | V2 L266 |
| `pending_negative_base` | 음수 과세표준은 원천세 미산출 · 보류 | V2 L281 |
| `net_settle_amount` | `payee별 당월 9단계 실정산액 = (당월 신규 세전 지급액 − 당월 신규 원천징수세액 + 당월 부가가치세) + 위탁 실정산액` | V2 L282 |
| `net_settle_offsettable`, `net_settle_protected` | 실정산액 중 상계 허용분 / 비상계 보호분(MMG 보전금 · 비상계 지원금 · 비정기 약정금의 세후 해당액) 태깅 | V2 L282~283 |
| `carry_pre_tax_after_tax[]` | `원귀속 PRE_TAX 세후 환산액 = 기초금액 − 해당 원귀속분 원천징수세액` | V2 L271, L282 |
| `cash_avail_offset_lines` | 6단계 재검증용 상계 적격 라인 현금 가용액 | V2 L228 |
| `canon_refs`, `trace[]` | 세무 담당 trace 규격(13절)과 동일 | — |
- 보호분의 '세후 해당액' 안분 방식은 정본 산식 없음 → 16절 Q-16. 자사 권리자(TX-01)는 증빙 · 대량이체 제외(L280).
- VAT 공급가액이 상계 전 금액인지 상계 후 세전 지급액인지 문장이 두 가지로 읽힌다 → 16절 Q-17(세무 담당과 공동 확인).

---

## 13. 10단계 CLAIM — 반환 반영 · 청구 판정

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L177, 본문 L284~298 · V1 §5.2 일할 반환 L247~250 · V1 §5.3 만료 · 해지 L328 · V1 §7.3 L568~574 |
| 입력 | 9단계 `net_settle_amount`(상계허용/보호), `carry_pre_tax_after_tax`, 전속계약금 일할 반환(세후, 상계 동의 여부), 미상계 선급금 잔액(6단계 후), 계약 만료 · 해지 · 폐업 트리거, `min_claim_limit`, 1단계 `carry_post_tax_neg`, 4단계 `return_claims` |
| 출력 | `net_after_return`, `claim_negative_net`, `claim_issued_yn`, 청구 · 반환채권 확정액, `payable_net_for_payout`, 청구 이월 적재(PRE_TAX/POST_TAX), 위탁 음수 → 위탁 전용 잔액, 선급금 원장 `CLAIMED_ON_TERMINATION` 예정 |

### 13.1 전속계약금 일할 반환액 (V1 §5.2 L248~249)
```
total_days     = obligation_end_date − obligation_start_date + 1
remaining_days = obligation_end_date − termination_date          # 해지일 당일은 복무 일수에 포함
clawback = floor( paid_signing_bonus_net × remaining_days / total_days )   # 세후 실지급액 기준
```
### 13.2 반환 반영 · 청구 판정
```
# 1) 동일 계약·동일 수취인 + 반환 상계 동의가 연결된 경우만 1회 차감        L286
net_after_return = net_settle_amount − (clawback if clawback_offset_consent_yn else 0)
# 2) 만료·해지 귀속월(current_end_date 또는 해지일이 당월), 6단계 후 미상계 잔액 > 0, 승계 미이관   L287
unoffset_claim = 0
if contract_end_in_month and prepay_balance_after > 0 and not transferred_to_successor:
    unoffset_claim = prepay_balance_after                       if LOAN    # 원금 전액
                     (세후 미상계 상당액 — 산식 Q-18)            if EARNED
    # 비상계 보호 지급액과 자동 교차 상계 금지(L287, D-11)
claim_negative_net = min(0, net_after_return) − (clawback if not clawback_offset_consent_yn else 0) − unoffset_claim   # L288
payable_net_for_payout = max(0, net_after_return) + Σcarry_pre_tax_after_tax                                       # L289
force_claim = contract_end_in_month or business_closed                                     # 강제 청구 트리거 L292
claim_issued_yn = claim_negative_net < 0 and (abs(claim_negative_net) > abs(min_claim_limit) or force_claim)   # L292, V1 L570
```
- 검증: Case 3-B(V4 L107~108) `483,500 − 3,000,000 = −2,516,500`, `|−2,516,500| > 100,000` → 청구 발행. V1 L571 예: `−120,000` 청구, `−30,000` 이월(만료 · 해지 · 폐업이면 −30,000도 청구).
- 비상계 보호분 침해 차단: `unoffset_claim`은 `net_settle_protected`와 상계하지 않는다. 위 식은 `net_after_return`(보호분 포함)이 양수이면 `max(0, ·)`로 지급 판정에 그대로 가고, `unoffset_claim`은 청구 음수에만 들어간다(L288~289, D-11).
- 정상 유지 계약의 소액 음수(`|·| ≤ |min_claim_limit|`): 청구서 미발행, 이월 원장에 청구 이월. **계정은 세무 상태로**: 원거래 지급 · 세무 경로 미확정 → `PRE_TAX`, 기지급 소득 환불 반환채권 · 전속계약금 반환 기인 → `POST_TAX` 음수(L294~295, V1 L572).
- 12월 발생 음수: 연말 정리 검토 대상 표시만, 잔액은 승계(L294).
- 청구 확정이어도 1단계 지급 이월 대기액(POST_TAX(+), PRE_TAX(+))은 소멸 · 상계하지 않고 11단계로(L296, V1 L574).
- 기지급 소득 환불 반환채권(4단계 `return_claims`, 1단계 `carry_post_tax_neg`)이 10단계 식의 어느 항에 들어가는지 정본 식에 없다(식에는 전속계약금 반환만 명시) → 16절 Q-19. 잠정: 상계 동의 · 적법 상계 성립 플래그가 있으면 전속계약금 1)과 같은 위치에서 차감(V4 Case 4 L131~143 예시), 없으면 청구 음수 항에 가산하고 trace `provisional=true`.
- **위탁 라인 음수**(L298): 청구 판정 대상 아님. 미지급분 → 위탁 전용 잔액(`consignment_balance_yn = true`, 사유 '위탁 반품 초과'), 기지급분 → 위탁자 반환 채권. 과세표준 생성 금지, 세전 계정 적재 금지, 12월 이관 규칙 미적용.
- 반환 · EARNED 미상계 정정 채널은 `matrix_case_id`로 10.4 채널 분기(LOAN 원금 청구는 정정 대상 아님)(L290) → 출력 `correction_channels`(TAX.md 정의).
- 위약금은 10단계 청구 판정 대상이 아님(V1 L253).
- 절사: 일할 반환 `floor` 1회. 그 밖에 없음.

---

## 14. 11단계 PAYOUT — 최소 지급 검증

| 항목 | 내용 |
| :--- | :--- |
| 근거 | V2 표 L178, 본문 L299~308 · V1 §7.3 L556~567 · V1 §7.4 L588~589 |
| 입력 | 10단계 `payable_net_for_payout`, 1단계 `carry_post_tax_pos`, `min_payout_limit`, 강제 정산 트리거 입력, `first_payable_confirmed_month` |
| 출력 | `payout_judgement_amount`, `payout_confirmed_yn`, 지급 확정액, 기존 이월행 `RESERVED` 예정, 지급 이월 적재(PRE_TAX 기초금액 / POST_TAX), 잔여 반환 채권 |

```
evaluate = (payable_net_for_payout > 0) or has_carry_pre_tax_pos or has_carry_post_tax_pos or force_settle   # L300 평가 대상
judgement = payable_net_for_payout + Σcarry_post_tax_pos.carryover_amount                                     # L302
force_settle = months_since(first_payable_confirmed_month) ≥ carryover_max_months(6)   # 산정 기준 Q-20
               or settlement_month.month == carryover_force_settle_month(12)
               or contract_end_in_month or business_closed                                                  # V1 L561~565
if judgement >= min_payout_limit or force_settle:
    payout_confirmed = true; payout_amount = judgement
    기존 이월행(carry_pre_tax_pos, carry_post_tax_pos) → payout_reservation_status = RESERVED (마감 시)       # L306
else:
    payout_confirmed = false
    당월 신규분 → carryover_ledger PRE_TAX(원천징수 미성립 기초금액, carryover_reason='지급 하한 미달')
    기존 POST_TAX(+) → POST_TAX 유지, 기존 PRE_TAX(+) → 그대로 유지(재적재 아님)                            # L305
```
- 판정 기준 = 부가세 포함 총액(`payout_threshold_basis = VAT_INCLUDED`)(L304, V3 L463). 예: Case 3 `1,300,000 + 130,000 = 1,430,000`(V4 L98).
- 10단계 청구 확정 · 반환채권 분리액은 부호와 무관하게 판정에 넣지 않음, 지급 이월과 자동 상계 금지(L302).
- 재차감 금지: 전속계약금 반환 · 미상계 선급금 청구 전환액은 10단계에서 1회만(L301).
- 현금 순액 전달 시 부가세 · 원천세 · 상계를 다시 가감하지 않는다(L303).
- '6개월 경과' 기산점은 최초 실제 지급 대상 확정월. 한 번도 하한을 넘지 못한 소액 잔액은 6개월 대상 아님(연말 · 만료 · 해지 · 폐업으로만)(V1 L561~562). 지급 실패 · 계좌 변경 · 승계로 기산점 재설정 금지.
- 지급 보류는 원천징수 성립이 아님. 미지급분은 PRE_TAX로 유지, 신고 산출물에 확정 반영하지 않음(L307).
- 이월 적재 시 '원금과 구성요소 보존': PRE_TAX 신규 적재 행은 라인 키(파이프라인 · 소득 구분 · 판정 단위 키 · 수취인)별로 `pre_tax_payable` 기초금액을 적재한다(VAT 구성요소의 이월 보존 방식은 정본 산식 없음 → 16절 Q-21).
- 이체 결과(마감 후): 성공 → `SETTLED`(`extinguished_yn = true`, `extinguished_month = 당월`), 실패 → `RESERVED → NONE` 해제 + 당월 신규 미지급분 PRE_TAX('지급 실패 이월') 신규 적재(V1 L589, D-13). 엔진은 마감 전 계산기이므로 결과 반영은 별도 입력(`payout_results`)이 있을 때만 수행.
- 절사: 없음.

---

## 15. 공통 규칙 모음

### 15.1 이월 연속성 등식 (V1 §7.4 L588~595) — 마감 차단 검증
계정별 · 권리자(또는 수취인)별로 독립 검증, 하나라도 불일치하면 `continuity.ok = false`(마감 차단).
```
PRE_TAX : prev_end_pre  + new_pre  − extinguished_pre(RESERVED·상계 확정)          == end_pre
POST_TAX: prev_end_post + new_post − extinguished_post(RESERVED·회수·상계 확정)    == end_post
위탁 전용(계약별): prev_end_cons + new_cons − offset_change_cons                    == end_cons
```
- 위탁 상쇄 · 정정 변동은 **제거되는 원잔액의 부호 그대로** 기록(−100 전액 상쇄 → 변동 −100, D-8 V4 L290). 정정에 의한 잔액 증가는 신규 적재로만 기록(이중 반영 금지).
- 위탁 전용 잔액은 세전 · 세후 등식과 합산하지 않음.
- 이체 실패 시 예약 해제로 차월 기초 세전 이월 잔액에 자동 복귀(L591).
- 무인 배치의 PRE_TAX ↔ POST_TAX 임의 전환 금지(지급 의제 · 승인 수동 대체 전표 예외)(V1 L596). 엔진은 전환 로직을 두지 않는다.

출력 `continuity[]`: `{account_type, key, prev_end, new, extinguished, end, ok}`.

### 15.2 최소 지급 · 청구 하한 (V1 §7.3, V3 부록B L461~463)
| 파라미터 | 기본값 | 판정 | 경계 |
| :--- | :--- | :--- | :--- |
| `min_payout_limit` | 100,000 | `판정 금액 ≥ 한도` → 지급 | 같으면 지급 |
| `min_claim_limit` | −100,000 | `음수 AND |음수| > |한도|` → 청구 | 같으면 이월 |
- 계약 원장 개별 설정, 분할 계약은 수취인 단위 판정(V1 L558). 단위(계약×수취인 / 수취인 전체) → 16절 Q-22.

### 15.3 선급금 상계 요약
- 상계 필수 자산, 원천세 뺀 지급 가능액 한도, 잔액 0원까지(V1 L324). 적격 · 제외는 9.1. 계약 단위 범위(V1 L326). LOAN/EARNED 과세표준 차이(V1 L320~321, V4 L16~28 비교표: 당월 소득 150,000 · 소진 100,000 → EARNED 과세표준 50,000 · 현금 48,350 / LOAN 150,000 · 45,050).
- 만료 · 해지 미상계 잔액 → 10단계 청구 전환, 마감 시 `CLAIMED_ON_TERMINATION` 0원 종결(V1 L328).

### 15.4 지원금 한도 · 순누계 요약
- `remaining_cap = total_cap_amount − cap_consumed_amount`. `cap_consumed`는 세전 확정 기준, 6단계 상계와 무관(V1 L287). `confirmed_net_total`과 `cap_consumed_amount`는 다른 누계(V3 L65~67). `cumulative_paid` 사용 금지.

### 15.5 MMG 요약
- P1.1 순수 신규 R/S만, 보정 후 4단계 차감, 보전금 비상계(6 · 10단계 보호), `mmg_promo_overlap_flag`는 연산 차단 없음.

### 15.6 수취인 분할 · 마지막 수취인 역산
- 11.2. 선급금과 수취인 분할 동시 존재 금지(V1 L323). 위탁 분할 금지(복수 위탁자는 계약 분리, V1 L170). 수취인별 세무 속성 독립(V1 L163).

### 15.7 합격 환급 옵션 A/B/C
- 7.3. 재연산 트리거: B · C만(V2 §10.1 L355). MMG 모수 제외(V1 §15.2).

### 15.8 마감 · 재연산 (V2 10장)
- 마감 취소 금지, 마감 월 입력이면 엔진 중단(`locked = true` → `input_error: LOCKED_MONTH`)(V2 L350).
- 오류는 차월 '전월 정산 조정' 라인으로(L351). 조정 레코드: `origin_month`, `applied_month`, `adj_reason_code`, `adj_explanation`(≥20자), `adj_amount`, `adj_tax_type`, `income_category`, `income_clause`, `tax_threshold_unit_key`, `payee_id`, `account_type`, `approver_id`, `origin_settlement_id`(V2 §10.2 L362).
- **조정 라인이 1~11단계 중 어디로 들어가는지 정본에 없다** → 16절 Q-23. 엔진 기본값 `adjustment_mode = "hold"`: 조정 라인을 계산에 넣지 않고 `pending_adjustments[]`로 출력. `"provisional"`이면 PRE_TAX 계정 조정을 해당 수취인 · 라인 키의 8단계 결과에 비분할 라인으로 추가(9단계 과세 입력), POST_TAX 계정 조정을 10단계 반환 항으로 추가하고 trace `provisional=true`.
- 재연산 멱등: 같은 입력 → 같은 출력. 누계는 입력의 전월 말 상태에 당월분만 반영(V2 L352, L356). 정렬은 13.3 고정 키만 사용(입력 순서에 의존 금지).
- 승인 권한 · 금액 구간(10.3)은 엔진 범위 밖(출력에 `adj_amount` 절대값 > `manual_adj_approval_threshold`이면 `requires_second_approval` 표시만).

### 15.9 13장 절사 위치 일람
| 위치 | 방식 | 근거 |
| :--- | :--- | :--- |
| P1.1 Step 1 패키지 안분 | 선행 floor, 마지막(정가↓ · product_id↑) 역산 | V2 L133, §13.3 L577 |
| P1.1 Step 2 · 4 중간 | q4 보존 | V2 L134, L136, §13.1 L565 |
| P1.1 권리자 · 라인 월 합산 | floor 1회 | V2 L136, §13.1 L566 |
| P2.1 SKU 총액 / 공동 저자 | floor(Σ) → 선행 floor, 마지막(지분↓ · rights_holder_id↑) 역산 | V1 L433~434, §13.3 L580 |
| P2.2 위탁 순액 | floor(Σ) 1회, 수수료 = 차액 | V1 L495~498 |
| P2.2 품목 배분 | 선행 floor, 마지막(order_item_id · 낱권↑) 역산 | V1 L513, §13.3 L582 |
| P2.3 공급가액 | floor(Σ × 100/110), 부가세 = 차액 | V2 L151 |
| P5.1 발생 | floor(기준금 × 요율) | V2 L160 |
| P5.1 복수 파이프라인 | P2.1 floor 먼저, 잔여 P1.1 | V2 §13.3 L581 |
| 4단계 공제 | 절대값 floor 후 부호 복원(P5.1 일반 · B는 원거래 단위 floor) | V2 §13.1 L569, L201 |
| 6단계 상계 안분 | 적격액↑ 선행 floor, 최대 라인 역산 | V2 L233 |
| 6단계 원천세 상당액 | 9단계 순차 산식 | V2 L227 |
| 8단계 수취인 분할 | 선행 floor, 마지막(split_ratio↓ · payee_id↑) 역산 | V2 L248, §13.3 L578 |
| 9단계 VAT | floor(공급가액 × 10%) / floor(총액×100/110), 부가세=차액 | V2 L264~265 |
| 9단계 원천세 | floor(과표×세율) → floor(소득세×10%) | V2 L269~270, §13.1 L568 |
| 9단계 필요경비 | floor(과표 × 의제율) | V2 L276 |
| 9단계 수수료 부가세 | floor(순 수수료 공급가액 × 10%) | V2 L266 |
| 10단계 일할 반환 | floor | V1 L248 |
| 반환 상당 과세표준(정정용) | floor(반환액 ÷ (1 − 당초 실효율)) — 자문 대상 | V1 L250 |

### 15.10 trace 규격 (white 추가 요건, BRIEF)
권리자 · 수취인 · 라인마다 단계 하나에 한 행 이상:
```
{ "step": 5, "step_code": "SUPPORT_CAP", "scope": {"rights_holder_id","contract_id","payee_id","line_key","agreement_id"},
  "inputs": {...}, "formula": "신규 확정액 = min(신규 발생액, 복원 후 한도)", "formula_code": "new_confirmed = min(new_5_1, avail_cap)",
  "before_rounding": "400000.0000", "rounding": "NONE|FLOOR_WON|Q4|ALLOC_LAST_REMAINDER", "result": 150000,
  "canon_ref": "V2 §8.3 5단계 3) L209", "provisional": false, "note": "" }
```
`formula`는 정본 표기 그대로, `formula_code`는 위 의사코드. 잠정 규칙을 쓴 행은 `provisional = true`와 16절 질문 번호를 `note`에.

---

## 16. 정본 확인 필요 (지어내지 않은 곳 · 모순)

| 번호 | 위치 | 내용 | 근거 | 엔진 잠정 처리 |
| :--- | :--- | :--- | :--- | :--- |
| Q-01 | 13.1 중간 정밀도 | DECIMAL(18,4) '보존'만 있고 4자리 밖 처리(버림/반올림)가 없다 | V2 §13.1 L565, V2 L134 | 4자리 버림(ROUND_DOWN), trace 표시 |
| Q-02 | 라인 키 '증빙 단위' | 8단계 분할 라인에 '증빙 단위'가 있으나 키 정의 없음 | V2 L248 | 라인 키에서 제외, 경고 없음 |
| Q-03 | Step 2 차시 분할 잔여 | 13.4는 차시 분할을 13장 대상에 넣었으나 13.3에 정렬 기준이 없고, Step 2는 q4 유지만 말함 | V2 L134, §13.3 L575~582, §13.4 L588 | q4 유지, 잔여 배정 없음 |
| Q-04 | 위탁 수수료 부가세 품목 배분 | '월 확정세액을 별도 배분'의 가중치 · 정렬 미정 | V1 L513 | 판매대금 비율 · 같은 정렬로 잠정 |
| Q-05 | MMG 연간 상한 초과분 | 초과 시 '재무 승인 대상으로 전환'만 있고 승인 전 금액 처리 없음 | V1 L339 | 금액 그대로, 경고 |
| Q-06 | MMG 귀속 라인 · 판정 단위 | 계약에 P1.1 라인이 여럿(소득 구분 · 강의)일 때 보정 후 금액 · 보전금 귀속 라인, 월 중 BASIC 요율 라인(MMG) 변경 시 적용값, 계약 기간이 월 일부일 때 안분 여부 없음 | V2 L192~193, V1 L208 | 계약 단위 판정, 보전금은 금액 최대 P1.1 라인에 귀속(동률 시 라인 키 오름차순), 월말 유효 라인 MMG — 전부 provisional |
| Q-07 | P2.2 반품의 수수료 부가세 조정 위치 | 10-B는 지급 조정 −90,625(부가세 포함)로 보이나 4단계 식은 '반품 차감액'만, 수수료 부가세는 9단계 | V2 L200, L266, V1 L501, V4 L253 | 4단계는 부가세 제외분, 부가세 조정은 9단계 |
| Q-08 | 지원금 공제 절사 | 일반 환불 · 옵션 B는 원거래 단위 `내림(...)`, 옵션 C는 내림 없음. 13.1은 '라인 월 합산 직후 1회' | V2 L201, V1 L607, V2 §13.1 L566 | 정본 문구대로(B · 일반 원거래 floor, C는 q4 유지 후 라인 합산 floor) |
| Q-09 | 옵션 B P1.1 분담액 산식 | "R/S 지분율과 동일한 비율로 분담"의 수치(지분율×요율인지), 절사, 원거래 미지급 · 기지급 분리가 산식으로 없음 | V1 L605, L625 | `환급금 × snap.share_ratio × snap.rate_value` q4 → floor, provisional |
| Q-10 | 환불 세무 경로별 금액 | 미지급 감액(원거래 미지급 잔액 포함 원장 등식), 기지급 반환채권(세전 · 세후 구성) 산식 미확정. 04권이 기대값 확정 보류 | V2 L197, V4 Case 4 L113~158, Case 5 L162 | 7.4 잠정 규칙 |
| Q-11 | CAPPED 음수 확정액 | UNLIMITED 음수만 처리 서술. CAPPED에서 `confirmed_amount < 0`(Case 9-B −75,000)의 라인 경로 서술 없음 | V2 L205, V4 L241 | UNLIMITED와 같은 음수 라인 처리 |
| Q-12 | 6단계 P1.1 적격의 '4단계 공제' 범위 | 기지급 반환(PAID_RETURN)분을 포함하는지 | V2 L218, L197 | 라인에서 실제 차감된 공제만(UNPAID) |
| Q-13 | 6단계 9단계 재검증 '현금 가용액' | 산식 없음 | V2 L228, L231, V1 L550 | `Σ(분할액 − 라인 원천세)` |
| Q-14 | 신규분 · 공제분 분리 분할의 1원 차이 | 원거래 귀속 유지(재분할 금지)와 '라인 세전액 × split_ratio' 단일 분할이 같은 비율일 때 결과가 1원 다를 수 있음 | V2 L248~249, V1 L211 | 분리 분할(원거래 귀속 우선) |
| Q-15 | P5.1 · 7단계 라인의 수취인 | 약정(`support_fund_agreements.payee_id`) · 매절(`buyout_payments.payee_id`)에 수취인이 있는데 8단계는 7단계 가산금을 분할 대상에 포함 | V1 L288, L234, V2 L247 | 원장에 `payee_id`가 있고 권리자와 다르면 그 수취인 단독 귀속(분할 안 함), 같으면 분할 대상, provisional |
| Q-16 | 9단계 보호분 '세후 해당액' | 보호분에 원천세 · 부가세를 어떻게 배분하는지 산식 없음 | V2 L282 | 라인 단위 세액이 있으므로 해당 라인 세후액 합계 |
| Q-17 | VAT 공급가액 기준 | `공급가액 = 세전 지급액(상계 전 공급가액 기준)` — 상계 전 분할액인지 상계 후 세전 지급액인지. 바로 뒤 `부가세 반영 후 정산액 = 세전 지급액 + 부가세` | V2 L264 | TAX.md에 위임(세무 담당 판정) |
| Q-18 | EARNED 미상계 선급금 '세후 미상계 상당액' | 산식 없음 | V2 L287, V1 L328 | 계산하지 않고 입력값(`earned_unoffset_post_tax_amount`) 필요, 없으면 input_error |
| Q-19 | 10단계 기지급 소득 환불 반환채권 | 10단계 식에는 전속계약금 반환만. 기지급 반환채권 · 전월 POST_TAX(−)의 차감 위치 없음(이월 계정 규칙만 있음) | V2 L286~289, L295, V4 L131~146 | 13.2 잠정 |
| Q-20 | 6개월 경과 산정 | '6개월이 지난 경우' — 월 차이 ≥ 6인지 > 6인지 | V1 L562, V3 L491 | `월 차이 ≥ 6` provisional |
| Q-21 | 지급 이월 적재 구성요소 | '원금과 구성요소 보존'의 VAT · 상계 구성 보존 방식 | V2 L305 | 라인별 `pre_tax_payable` 기초금액 + 구성요소 JSON |
| Q-22 | 지급 · 청구 하한 판정 단위 | 한도는 계약 필드, 분할 계약은 수취인 단위 — 한 수취인이 여러 계약에서 받을 때 합산 여부 | V1 L558, V2 L304 | 계약 × 수취인 |
| Q-23 | 마감 후 조정 라인 인입 단계 | 10장은 '차월 전월 정산 조정 라인'만, 1~11단계 중 위치 없음. 13.4 '원거래 귀속이 없는 공통 세전 조정액의 Pipeline별 안분' 언급만 | V2 §10.1 L351, §10.2 L362, §13.4 L588 | `adjustment_mode = hold` 기본 |
| Q-24 | 지원금 '승인된' 한도 복원액 | 복원에 별도 승인이 필요한지, 자동인지(Case 9-B · D-9는 자동으로 계산) | V2 L207~208, V4 L241, L291 | 자동(공제액 = 복원액, 원거래 미환불 확정액 한도) |
| Q-25 | 지원금 상태 판정 시점 | `status = ACTIVE`가 아닌 약정 신규 0원 — 월초 상태인지, 같은 달 복원으로 ACTIVE 복귀 시 당월 신규 발생을 인정하는지 | V2 L209, L212 | 월초(전월 말 원장) 상태 |
| Q-26 | 일반 환불 · 반품 금액의 절사 단위 | P1.1 환불 공제를 원거래별 floor인지 라인 월 합산 floor인지(13.1은 월 합산 1회) | V2 §13.1 L566, V4 L241 | 라인 월 합산 1회 |

> 위 항목은 모두 정책 판단이 필요하므로 white 확인 대상이다(BRIEF '정책 판단은 모아서 묻는다'). 엔진은 잠정 처리 행에 `provisional = true`와 질문 번호를 남겨, 확정 후 해당 행만 고치면 되도록 한다.

---

## 17. 필드 명명 출처

| 출처 표시 | 의미 |
| :--- | :--- |
| `[03-DD]` | V3 데이터 사전(L41~176) 컬럼명 |
| `[03-CD]` | V3 코드값 사전(L182~281) 코드값 |
| `[03-B]` | V3 부록 B 파라미터(L452~502) |
| `[01-T]` | V1 테이블 컬럼 정의(4.2 `lecture_instructors` · `book_authors` · `payee_splits`, 5.1 요율 라인 · `buyout_payments`, 5.2 지원금 3종, 7.4 `carryover_ledger`) |
| `[02-T]` | V2 본문 식별자 |
| `[신규 명명]` | 정본에 snake 식별자가 없어 새로 붙인 이름 |

주요 `[신규 명명]`: `mmg_amount`(V1 L208 '월 보장액(MMG)' 컬럼), `prepay_unoffset_balance`(미상계 선급금 잔액), `consignment_fee_rate`(위탁 수수료율), `consignment_price`(위탁 판매가), `royalty_base_price`(인세 기준가), `confirmed_qty`(확정 부수), `lecture_base_amount`(강의 기준금), `runtime_seconds`, `refund_ratio`, `optB_burden_ratio`, `optC_cancel_ratio`, `support_confirmed_alloc`(원거래 지원금 확정 배분액), `unrefunded_support_confirmed`, `payment_state` · `paid_portion_amount` · `unpaid_portion_amount`, `paid_return_post_tax_amount`, `clawback_offset_consent_yn`, `paid_signing_bonus_net`, `obligation_start_date` · `obligation_end_date` · `termination_date`, `business_closed_yn`, `supply_nature`, `protected_yn`, `pipeline_id = LUMPSUM`, 출력 단계 결과 필드 대부분(스키마 설명에 표시).
