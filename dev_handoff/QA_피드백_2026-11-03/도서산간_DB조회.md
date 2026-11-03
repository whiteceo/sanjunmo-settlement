# 도서산간 · 배송비 개발 DB 조회 (2026-11-03)

- 대상: `sanjunmo_dev`(테이블 168개), `.tools/devdb.py` 읽기 전용(SET SESSION TRANSACTION READ ONLY). 데이터 변경 없음.

## 1. 테이블 이름 검색 (zip · post · island · region · area · shipping · delivery · fee)

| 테이블 | 행(추정) |
| :--- | ---: |
| delivery_batch_items | 43 |
| delivery_batches | 29 |
| delivery_logs | 84 |
| exclusive_contract_fees | 0 |
| pg_fee_rates | 0 |
| post_comments | 0 |
| post_winners | 0 |
| posts | 12 |

zip · island · region · area · shipping 이 이름에 든 테이블은 없다. posts 계열은 게시글, 나머지는 배송 배치 · 수수료로 도서산간과 무관하다. 테이블 코멘트에 "도서 · 산간 · 우편 · 배송"이 든 테이블을 따로 찾아도 우편번호 목록 테이블은 없었다.

## 2. 컬럼 이름 검색 (zip · post · island · region)

| 테이블 | 컬럼 | 타입 | 코멘트 |
| :--- | :--- | :--- | :--- |
| books | island_delivery_fee | int | 도서산간 추가 배송비. 주소 판정으로 자동 가산. NULL이면 site_settings 값 적용 |
| deliveries | zipcode | varchar(5) | 우편번호 스냅샷. 도서산간 판정 기준값(3PL 발주 엑셀) |
| goods | island_delivery_fee | int | 도서산간 추가 배송비. NULL 이면 site_settings 값 적용 |
| orders | receiver_zipcode | varchar(5) | 수령지 우편번호. 도서산간 판정 · 3PL 발주 필수값 |
| popups | post_id | bigint unsigned | |
| post_comments | post_id | bigint unsigned | |
| post_winners | post_id | bigint unsigned | |
| posts | related_post_id | bigint unsigned | |
| site_settings | island_delivery_fee | int | 도서산간 추가 배송비 |
| user_addresses | zipcode | varchar(10) | 우편번호. 우편번호 검색 API 로 채우며 직접 타이핑을 허용하지 않는다 |

참고: `deliveries.fee_type` varchar(20), 코멘트 "FREE 무료 / PREPAID 선불 / ISLAND 도서산간 (3PL 발주 엑셀)". 현재 값 분포는 PREPAID 30건뿐(ISLAND 0건).

## 3. 도서산간 우편번호 목록 테이블

없다. DESC · COUNT · 샘플 대상 없음. 코멘트상 판정은 우편번호(`orders.receiver_zipcode`, `deliveries.zipcode`)로 하지만, 판정 기준 목록은 DB에 없고 코드나 외부 API에 있을 것으로 보인다(DB만 보고 한 추정).

## 4. 배송비 설정

별도 shipping 테이블은 없고 `site_settings`(단일 행, COUNT 1)의 컬럼이 기본값이다. 상품별 덮어쓰기는 `books` · `goods`의 같은 이름 컬럼(NULL이면 site_settings 값).

site_settings 배송 관련 컬럼 정의:

| 컬럼 | 타입 | Null | 기본값 | 코멘트 |
| :--- | :--- | :--- | :--- | :--- |
| delivery_fee | int | NO | 0 | 기본 배송비 |
| free_delivery_threshold | int | YES | NULL | 무료배송 기준 금액. NULL이면 조건부 무료배송 미적용 |
| island_delivery_fee | int | NO | 0 | 도서산간 추가 배송비 |
| return_delivery_fee | int | NO | 6000 | 반품 왕복 배송비 기본값 |
| package_delivery_notice | text | YES | NULL | 패키지 상세 배송 안내 |

현재 값(id 1, updated_at 2026-10-30 09:00:56):

| delivery_fee | free_delivery_threshold | island_delivery_fee | return_delivery_fee |
| ---: | ---: | ---: | ---: |
| 3000 | 30000 | **0** | 6000 |

package_delivery_notice 원문: "출고: 결제 완료 후 2~3 영업일 내 출고. 주말 · 공휴일은 제외됩니다 / 배송비: 무료 (패키지 가격에 포함) · 제주 · 도서산간 추가 배송비 없음 / 배송 조회: 출고 후 마이페이지 > 주문 내역에서 송장번호를 확인할 수 있습니다 / 교환 · 반품: 배송된 날로부터 7일 이내에만 가능합니다. … 단순 변심 시 왕복 배송비 6,000원이 공제됩니다"

상품별 값: books 7행 · goods 7행 모두 `island_delivery_fee` NULL → 전부 site_settings의 0원을 따른다.

books · goods 배송 관련 컬럼(참고): delivery_fee, is_free_delivery, free_delivery_threshold, island_delivery_fee, return_delivery_fee. 주문 쪽은 `orders.delivery_fee`(기본 0), `refunds.delivery_fee_deduction`.

## 요약

- 도서산간 우편번호 목록 테이블은 개발 DB에 없다.
- 도서산간 추가 배송비는 site_settings 0원, 상품별 지정 없음 → 현재 어떤 주문에도 도서산간 가산이 0원이다. 배송 건 중 ISLAND 구분도 0건.
