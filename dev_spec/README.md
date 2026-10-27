# dev_spec — 화면별 개발 명세

개발 코드(`lcampus/sanjunmo` dev, 로컬 `D:\Work\sanjunmo`, 읽기 전용)에서 화면마다 이름 · 연결을 뽑아 둔 문서다.
`prototype_dev/`는 이 문서를 보고 prototype_clean 사본의 name · id · 링크 · 권한 단위를 개발 이름으로 바꾼다.

- 디자인 · 배치 · 업무 규칙은 prototype_clean + 정본이 기준이다. 개발 화면 배치는 따르지 않는다.
- 예외: SNB는 디자인만 프로토타입, 접기 · 펼치기 같은 동작은 개발 기준(`public/admin/assets/js/custom.js` "관리자메뉴(좌측)" 아코디언). v6.92부터 `common-snb.js`가 아코디언을 직접 하므로 prototype_dev는 공통 파일 사본으로 따라간다(white 2026-10-27, 임시로 쓰던 `dev-snb.js`는 삭제).
- 이름 · 연결(라우트 · 필드명 · DB 컬럼 · 권한 단위 · JS id)은 개발 코드가 기준이다.
- 진행 · 분업 · 질문은 `_STATUS.md`.

## 폴더
| 경로 | 내용 |
|---|---|
| `_tools/extract_dev.py` | 개발 저장소에서 색인을 다시 뽑는다. dev를 pull한 뒤 `python dev_spec/_tools/extract_dev.py` |
| `_index/routes.md` | 관리자 라우트 전체(이름 · URL · 컨트롤러 · 권한 단위 · 주석) |
| `_index/requests.md` | Admin 요청 검증 rules() 원문 |
| `_index/schema.md` | 마이그레이션 누적 테이블 · 컬럼 |
| `_index/progress.md` | 개발 진행표(config/dev-progress.php) + 커밋 언급 |
| `_index/meta.md` | 색인 기준 dev 커밋 |
| `<파일 코드>.md` | 화면별 명세. 파일 하나 = 프로토타입 HTML 하나(예: `ADMN-USER-001.md`는 `ADMN-USER-001_baseline.html` 안의 USER-001~006 전부) |

## 개발 명명 규칙 (미구현 화면에 그대로 적용)
- 라우트 이름: `admin.<자원 복수형 kebab>.<하위 자원>.<접미사>`. URL은 `/{admin}/<자원>/{id}/<하위>`. 관리자 접두사 `{admin}` = `config('admin.prefix')`(기본 `sj-admin`).
- 접미사 → 권한(AdminPermissionService::SUFFIX_PERMISSIONS): `index` · `show` → 조회, `create` · `store` → 등록, `edit` · `update` → 수정, `destroy` → 삭제, `download` → 다운로드. 예외 `recalculate` · `status-sync` · `reset-verify-cap` · `nts-verify` → 수정, `contracts` → 조회. 매핑 밖 접미사는 차단(fail-closed).
- 추가 쓰기 동작은 하위 자원으로 쓴다(지급 = `issue.store`, 복사 = `copy.store`, 중단 = `status.update`).
- 메뉴 권한은 라우트 이름을 목록형(`…index`)으로 정규화해 `admin_menus.route_name`과 맞춘다. 메뉴 1개 = 권한 행 1개(조회 · 등록 · 수정 · 삭제 · 다운로드 5축).
- 폼 필드: snake_case(`reason_code`, `expire_date`), 배열은 `ids[]` · `fields[]`, 여러 행은 `conditions[0][field]`. 사유 입력은 `reason`(MemberReasonRequest: 공백 제외 10자 이상 · 서로 다른 글자 3개 이상 · 200자 이하).
- 코드값: 영문 소문자 snake(`active` · `dormant` · `withdrawn`, `grant` · `deduct`). 화면 라벨은 모델 상수 `*_LABELS`.
- DB: 테이블 복수형 snake, FK `<단수>_id`, 처리자 `admin_id` · `created_by` · `released_by`, 시각 `*_at`.
- 개발 JS id: camelCase. 모달 레이어 `layer<기능>`(예 `layerPointGrant`), 폼 `<기능>Form`(예 `pointGrantForm`), 제출 버튼 `<기능>Submit`. 공통 클래스 `input__text` · `select` · `link--view` · `mgL10`.

## 화면 명세 형식 (`<파일 코드>.md`)
```
# <파일 코드> <화면명> — 개발 명세
- 프로토타입 파일: prototype_clean/<파일>.html (원본 상태: <커밋 또는 '커밋 + 미커밋 작업 트리'>)
- 맞춘 개발 커밋: <dev 커밋 해시> (<날짜>)
- 포함 화면: <개발 화면 코드 목록>
- 개발 진행: <구현 / 일부 / 미구현(규칙 기반 명명)>  ← _index/progress.md 근거

## 1. 메뉴 · 권한
| 메뉴(admin_menus.route_name) | 메뉴명 | 확인 방법 |

## 2. 화면별 라우트            ← 개발 화면 코드마다 소절
### <화면 코드> <화면명>
| 동작 | 메서드 | URL | 라우트 이름 | 권한 | 컨트롤러@메서드 |

## 3. 폼 필드 · 검증
### <폼 이름> (<Request 클래스>)
| 필드 name | 규칙 | 코드값(라벨) | 프로토타입 대응 요소(id · 라벨) |

## 4. 목록 필터 · 정렬 · 표 컬럼   (목록 화면만)

## 5. DB 테이블 · 컬럼
| 테이블.컬럼 | 타입 | 뜻 | 화면 표시 위치 |

## 6. 개발 JS · 마크업 이름
| 개발 id/class | 역할 | 프로토타입 대응 id |

## 7. 기능 차이
### 개발에만 있음 (prototype_dev에 정본 디자인으로 추가)
### 프로토타입에만 있음 (백엔드 필요 · 개발 미구현)
### 이름 · 값이 다름 (prototype_dev에서 개발 이름으로 바꿈)

## 8. 정책 질문 (white 확인 필요 — _STATUS.md에도 옮긴다)
```
- 근거는 `파일:줄` 로 적는다(개발 저장소 기준 상대 경로).
- 개발에 아직 없으면 2~6절에 "개발 미구현, 규칙 기반 명명"이라고 적고 위 규칙으로 지은 이름을 쓴다. 지은 이름은 `(규칙)` 표시.
