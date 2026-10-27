# Admin 요청 검증(rules) 색인

## AccountRefundRequest (extends FormRequest)
```php
        return [
            'bank_code' => ['required', 'string', Rule::in(array_keys(TossPaymentsGateway::banks()))],
            'account_no' => ['required', 'string', 'regex:/^[0-9-]{6,24}$/'],
            'account_holder' => ['required', 'string', 'max:50'],
            // 화면에 보인 이체할 금액 — 서버가 다시 계산한 금액과 같아야 기록한다
            'expected_cash' => ['required', 'integer', 'min:0', 'max:1000000000'],
            'minus_agree' => ['nullable', 'boolean'],
            'minus_reason' => ['nullable', 'string', 'max:'.RefundApprovalRequest::MAX_MINUS_REASON],
        ];
```

## AdminMenuRequest (extends FormRequest)
```php
        $adminMenu = $this->route('adminMenu');
        $adminMenuId = $adminMenu?->id;

        return [
            'parent_id' => [
                'nullable',
                'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(AdminMenuRepository::class)->menuIdExists($value)) {
                        $fail($this->messages()['parent_id.exists']);
                    }
                },
                Rule::notIn([$adminMenuId]),
            ],
            'name' => [
                'required',
                'string',
                'max:100',
            ],
            'route_name' => [
                'nullable',
                'string',
                'max:100',
            ],
            'url' => [
                'nullable',
                'string',
                'max:255',
            ],
            'icon' => [
                'nullable',
                'string',
                'max:50',
            ],
            'sort_order' => [
                'required',
                'integer',
                'min:0',
                'max:999999',
            ],
            'is_active' => [
                'required',
                'integer',
                Rule::in([0, 1]),
            ],
        ];
```

## AdminPasswordChangeRequest (extends FormRequest)
```php
        return [
            'current_password' => ['required', 'string'],
            'password'         => AdminPasswordPolicyService::rules(),
        ];
```
attributes:
```php
        return [
            'current_password' => '현재 비밀번호',
            'password'         => '새 비밀번호',
        ];
```

## AdminProfileRequest (extends FormRequest)
```php
        $adminId = (int) session('admin_id');

        return [
            'name' => [
                'required',
                'string',
                'max:50',
            ],
            'email' => [
                'nullable',
                'email',
                'max:100',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($adminId) {
                    if (! $validator->errors()->has($attribute) && app(ProfileRepository::class)->emailTaken($value, $adminId ?: null)) {
                        $fail($this->messages()['email.unique']);
                    }
                },
            ],
            'phone' => [
                'nullable',
                'string',
                'max:20',
            ],

            // 새 비밀번호 입력 시에만 현재 비밀번호 필수
            'current_password' => [
                'nullable',
                'required_with:password',
                'string',
            ],
            // 규칙은 재설정·본인 변경 화면과 같은 곳을 본다 (ADMN-LOGIN-B).
            // 비우면 기존 비밀번호를 유지하므로 required 만 빼고 나머지는 동일하다
            'password' => AdminPasswordPolicyService::rules(required: false),
        ];
```
attributes:
```php
        return [
            'current_password' => '현재 비밀번호',
            'password'         => '새 비밀번호',
        ];
```

## AdminRoleRequest (extends FormRequest)
```php
        $adminRole = $this->route('adminRole');

        return [
            // 시스템 식별자. inquiry_category_roles.role_code 등이 문자열로 참조한다.
            // 등록 시에만 받고 수정 시에는 무시한다 — 바꾸면 문의 자동 배정이 끊긴다.
            'code' => $adminRole
                ? ['nullable']
                : [
                    'required',
                    'string',
                    'max:30',
                    'regex:/^[a-z0-9_]+$/',
                    // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                    function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                        if (! $validator->errors()->has($attribute) && app(AdminRoleRepository::class)->codeTaken($value)) {
                            $fail($this->messages()['code.unique']);
                        }
                    },
                ],
            'name' => [
                'required',
                'string',
                'max:100',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($adminRole) {
                    if (! $validator->errors()->has($attribute) && app(AdminRoleRepository::class)->nameTaken($value, $adminRole?->id ?: null)) {
                        $fail($this->messages()['name.unique']);
                    }
                },
            ],
            'description' => [
                'nullable',
                'string',
                'max:500',
            ],
            'is_system' => [
                'nullable',
                'in:1',
            ],

            // 메뉴 권한 체크박스
            'permissions' => [
                'nullable',
                'array',
            ],
            'permissions.*' => [
                'nullable',
                'array',
            ],
            'permissions.*.can_view' => [
                'nullable',
                'in:1',
            ],
            'permissions.*.can_create' => [
                'nullable',
                'in:1',
            ],
            'permissions.*.can_update' => [
                'nullable',
                'in:1',
            ],
            'permissions.*.can_delete' => [
                'nullable',
                'in:1',
            ],
            'permissions.*.can_download' => [
                'nullable',
                'in:1',
            ],
        ];
```

## AdminUserRequest (extends FormRequest)
```php
        $adminUser = $this->route('adminUser');
        $isCreate = $this->isMethod('post');

        // 이미 배정된 소속 강사 — 권리자 미연결 검증에서 제외할 대상이다
        $alreadyAssigned = $adminUser
            ? app(AdminUserRepository::class)->instructorLinks($adminUser)['assistant_instructor_ids']
            : [];

        return [
            'login_id' => [
                'required',
                'string',
                'max:50',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($adminUser) {
                    if (! $validator->errors()->has($attribute) && app(AdminUserRepository::class)->loginIdTaken($value, $adminUser?->id ?: null)) {
                        $fail($this->messages()['login_id.unique']);
                    }
                },
            ],
            'name' => [
                'required',
                'string',
                'max:50',
            ],
            'email' => [
                'nullable',
                'email',
                'max:100',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($adminUser) {
                    if (! $validator->errors()->has($attribute) && app(AdminUserRepository::class)->emailTaken($value, $adminUser?->id ?: null)) {
                        $fail($this->messages()['email.unique']);
                    }
                },
            ],
            'phone' => [
                'nullable',
                'string',
                'max:20',
            ],
            /*
             * 관리자가 발급·재설정하는 비밀번호도 본인 변경과 같은 규칙을 탄다 (ADMN-LOGIN-B-FIX).
             * 여기만 min:8 · max:100 으로 느슨하면 발급 경로로 정책이 우회된다.
             * 재사용 이력 대조는 하지 않는다 — 초기 비밀번호를 주는 자리라
             * "예전에 쓴 값" 을 막으면 발급 자체가 막히는 상황이 생긴다.
             */
            'password' => AdminPasswordPolicyService::rules(required: $isCreate),
            'admin_role_id' => [
                'required',
                'integer',
                // 존재 여부만 본다. 최고관리자 부여 가능 여부는 로그인 관리자에 따라
                // 달라지므로 AdminUserService 가 판정한다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(AdminUserRepository::class)->roleIdExists($value)) {
                        $fail($this->messages()['admin_role_id.exists']);
                    }
                },
            ],
            'is_locked' => [
                'nullable',
                'in:1',
            ],
            // 강사 역할의 연결 강사 · 조교 역할의 소속 강사 (역할이 다르면 서비스가 무시하고 연결을 푼다)
            'linked_instructor_id' => [
                'nullable', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(AdminUserRepository::class)->instructorIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'assistant_instructor_ids' => ['nullable', 'array'],
            'assistant_instructor_ids.*' => [
                'integer', 'distinct',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(AdminUserRepository::class)->instructorIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                /*
                 * 권리자가 연결되지 않은 강사는 새로 배정하지 않는다 (ADMN-PROD-006-S1 ①)
                 *
                 * 이미 배정된 건은 통과시킨다 — 권리자 없는 기존 강사(inst#14)에 붙은 조교가
                 * 있고, 그 계정의 이름만 고쳐도 저장이 거절되면 계정을 손볼 수 없다.
                 * 화면은 체크박스를 잠그지만 판정은 서버가 다시 한다(DECISIONS 103).
                 */
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($alreadyAssigned) {
                    if ($validator->errors()->has($attribute) || in_array((int) $value, $alreadyAssigned, true)) {
                        return;
                    }

                    if (! app(AdminUserRepository::class)->instructorHasRightsHolder($value)) {
                        $fail($this->messages()['assistant_instructor_ids.*.rights_holder']);
                    }
                },
            ],
            /*
             * 잠금 해제 사유 (설계서 보안 정책표 '잠금 해제')
             *
             * 잠긴 계정을 해제로 바꿀 때만 필수다. 이 Request 는 "지금 잠겨 있는가" 를
             * 알 수 있어(라우트 모델) 여기서 조건을 세운다.
             * 최종 판정은 AdminUserService 가 한 번 더 한다 — 폼을 직접 만든 요청도 막아야 한다.
             */
            'unlock_reason' => [
                ($adminUser?->is_locked && ! $this->boolean('is_locked')) ? 'required' : 'nullable',
                'string',
                'max:200',
            ],
        ];
```

## BadgeRequest (extends FormRequest)
```php
        // 등록: null, 수정: 정수 문자열 (Route Model Binding 미사용 컨벤션)
        $badgeId = $this->route('badge');

        return [
            'code'       => [
                'required', 'string', 'max:20',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($badgeId) {
                    if (! $validator->errors()->has($attribute) && app(BadgeRepository::class)->codeTaken($value, $badgeId ?: null)) {
                        $fail($this->messages()['code.unique']);
                    }
                },
            ],
            'label'      => ['required', 'string', 'max:50'],
            'slot'       => ['required', 'integer', Rule::in([1, 2])],
            'image'      => ['nullable', 'image', 'mimes:jpg,jpeg,png,gif,webp', 'max:2048', new RealFileType(['jpg','jpeg','png','gif','webp'])], // svg 는 스크립트 삽입(XSS) 벡터라 허용 목록에서 제외
            'color'      => ['nullable', 'string', 'max:20', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'text_color' => ['nullable', 'string', 'max:20', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'icon'       => ['nullable', 'string', 'max:50'],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active'  => ['required', 'boolean'],

            // 이미지 삭제 컨트롤
            'delete_image' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'code'       => '배지 코드',
            'label'      => '표시명',
            'slot'       => '슬롯',
            'image'      => '배지 이미지',
            'color'      => '배경색',
            'text_color' => '텍스트색',
            'icon'       => '아이콘',
            'sort_order' => '정렬 순서',
            'is_active'  => '활성 여부',
        ];
```

## BannerReorderRequest (extends FormRequest)
```php
        return [
            // 통합 화면 순서저장은 전시영역(hero=메인슬라이드) 탭 범위로만 허용. 띠배너는 StripBannerReorderRequest
            'position' => ['required', Rule::in(array_values(Banner::DISPLAY_AREAS))],
            'orders' => ['required', 'array', 'min:1'],
            'orders.*.id' => ['required', 'integer', 'distinct'],
            'orders.*.sort_order' => ['required', 'integer', 'min:0'],
        ];
```

## BannerRequest (extends FormRequest)
```php
        return [
            'position' => ['required', Rule::in(array_keys(Banner::POSITIONS))],
            'device' => ['required', Rule::in(array_keys(Banner::DEVICES))],
            'title' => ['required', 'string', 'max:255'],
            'image' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp'])], // svg 확장자 차단
            'mobile_image' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp'])],
            'delete_image' => ['nullable', 'boolean'],
            'delete_mobile_image' => ['nullable', 'boolean'],
            'alt_text' => ['required', 'string', 'max:255'],
            'mobile_alt_text' => ['nullable', 'string', 'max:255'],
            'link_url' => ['nullable', 'string', 'max:500', new DisplayLinkUrl],
            'link_target' => ['required', Rule::in(array_keys(Banner::LINK_TARGETS))],
            'start_at' => ['nullable', 'date'],
            'end_at' => ['nullable', 'date', 'after_or_equal:start_at'],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'position' => '노출 위치',
            'device' => '노출 기기',
            'title' => '배너명',
            'alt_text' => '대체 텍스트',
            'end_at' => '노출 종료',
        ];
```

## BoardRequest (extends FormRequest)
```php
        $boardId = $this->route('board');

        return [
            'name'       => ['required', 'string', 'max:100'],
            'code'       => [
                'nullable', 'string', 'max:50',
                // 제외 id 는 원래 문자열 규칙처럼 문자열로 넘긴다(등록이면 빈 문자열)
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($boardId) {
                    if (! $validator->errors()->has($attribute) && app(BoardRepository::class)->codeTaken($value, (string) $boardId)) {
                        $fail($this->messages()['code.unique']);
                    }
                },
            ],
            'type'       => ['required', Rule::in(array_keys(Board::TYPES))],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active'  => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'name'       => '게시판명',
            'code'       => '게시판 코드',
            'type'       => '게시판 유형',
            'sort_order' => '정렬순서',
            'is_active'  => '사용여부',
        ];
```

## BookPriceRequest (extends FormRequest)
```php
        return [
            'price' => ['required', 'integer', 'min:0', 'max:10000000'],
            'effective_from' => ['required', 'date_format:Y-m-d'],
            'price_owner' => ['required', 'string', Rule::in(array_keys(BookPriceHistory::OWNER_LABELS))],
            // 미확정: 위탁자 통보 근거의 형식 — 설계서는 파일 또는 메모, 첨부 칸이 없어 메모(사유 칸)로 받음 · 첨부 칸이 생기면 파일도 받는다
            'reason' => ['required_if:price_owner,'.BookPriceHistory::OWNER_CONSIGNOR, 'nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return ['price' => '신규 정가', 'effective_from' => '유효 시작일', 'price_owner' => '정가 결정 주체', 'reason' => '사유 · 통보 근거'];
```

## BookRequest (extends FormRequest)
```php
        // 등록: route('book') 없음. 수정: route('book') 존재.
        $bookId = $this->route('book');

        return [
            // 기본정보
            'title'             => ['required', 'string', 'max:255'],
            // 노출 카테고리는 2Depth 1건 (설계서 ADMN-PROD-004 ⑥ 자격증 종류 매핑).
            // 저장은 books 컬럼이 아니라 category_products 로 간다
            'category_id'       => ['required', 'integer',
                // 삭제된 카테고리는 셀렉트에 없지만 id 를 직접 실어 보내면 통과한다
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(BookRepository::class)->activeCategoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                $this->categoryDepthRule(),
            ],
            // 자격증 종류 매핑 — 1Depth 복수 선택 (설계서 ADMN-PROD-004-S1 공통 :372, 확정 · PO 2026-10-02)
            // 노출 카테고리(2Depth 1건)와 축이 다르다. 저장은 둘 다 category_products 로 가되 is_primary 로 가른다
            'cert_category_ids'   => ['nullable', 'array'],
            'cert_category_ids.*' => [
                'integer', 'distinct',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if ($validator->errors()->has($attribute)) {
                        return;
                    }

                    if (! app(BookRepository::class)->activeCategoryIdExists($value)) {
                        $fail('validation.exists')->translate();

                        return;
                    }

                    if (app(CategoryService::class)->isSelectableCategory($value)) {
                        $fail('자격증 종류는 자격증 종목(1Depth)만 선택할 수 있습니다.');
                    }
                },
            ],
            // ISBN 은 도서정가제 적용 대상을 식별하는 키라 필수다. 부속(BUNDLED) 도서만 예외 —
            // 사은품은 ISBN 을 발급받지 않는다(설계서 :371 확정 · PO 2026-10-01)
            // 미확정: 등록 시점에는 공급 형태가 아직 없다(원본이 도서 공급 원장) — 부속 도서는 원장에서 먼저 등록한다
            'isbn'              => [
                $this->isbnOptional() ? 'nullable' : 'required', 'string', 'max:30',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($bookId) {
                    if (! $validator->errors()->has($attribute) && app(BookRepository::class)->isbnTaken($value, $bookId ?: null)) {
                        $fail($this->messages()['isbn.unique']);
                    }
                },
                $this->isbnRule(),
            ],
            // 저자 · 출판사는 상세페이지 노출값이자 인세 · 매입 대사의 식별 정보다(설계서 :380)
            'author'            => ['required', 'string', 'max:100'],
            'publisher'         => ['required', 'string', 'max:100'],
            'published_at'      => ['nullable', 'date'],
            'edition'           => ['nullable', 'string', 'max:50'],
            // 정가 · 판매가 · 무료 여부는 등록 때만 받는다 — 수정은 도서 공급 원장에서(교재 관리는 읽기 전용).
            // 무료 여부까지 잠그는 까닭: 수정에서 무료를 풀면 정가 칸이 버려져 유료 교재가 0원에 팔린다
            // 미확정: 무료 ↔ 유료 전환 — 설계서에 전환 규칙이 없어 등록 때만 정함(사용자 결정 10-10) · 전환 규칙이 정해지면 원장에 경로를 둔다
            'original_price'    => $this->routeIs('admin.books.update') ? ['exclude'] : ['required', 'integer', 'min:0'],
            // 사입 원가는 공급 정보(매입 재판매)에서만 넣는다 — 원가 계정과 함께 정해져야 해서 등록에서도 받지 않는다
            'cost_price'        => ['exclude'],
            'sale_price'        => $this->routeIs('admin.books.update') ? ['exclude'] : ['required', 'integer', 'min:0', 'lte:original_price', $this->fixedBookPriceRule()],
            'is_free'           => $this->routeIs('admin.books.update') ? ['exclude'] : ['nullable', 'boolean'],

            // 재고 (설계서 ③ — 수기 재고)
            // 초기 재고는 등록 때만 받는다. 수정에서 재고를 바꾸는 경로는 [재고 조정] 하나뿐이고
            // 거기서만 사유가 함께 남는다(:394). 폼으로 덮으면 그 사이 결제로 빠진 재고가 되살아난다
            'stock'             => $this->routeIs('admin.books.update') ? ['exclude'] : ['required', 'integer', 'min:0'],
            'stock_alert_qty'   => ['nullable', 'integer', 'min:0'],
            'is_preorder'       => ['nullable', 'boolean'],
            'restock_date'      => ['nullable', 'date'],

            // 배송 정책 (설계서 ⑧)
            'delivery_fee'            => ['nullable', 'integer', 'min:0'],
            'is_free_delivery'        => ['nullable', 'boolean'],
            'free_delivery_threshold' => ['nullable', 'integer', 'min:0'],
            'island_delivery_fee'     => ['nullable', 'integer', 'min:0'],
            'return_delivery_fee'     => ['nullable', 'integer', 'min:0'],
            // 패키지 구성품으로 팔릴 때도 위 배송 정책을 그대로 적용한다 (설계서 ④ :407)
            'package_bundled_yn'      => ['nullable', 'boolean'],

            'page_count'        => ['nullable', 'integer', 'min:0'],
            'book_size'         => ['nullable', 'string', 'max:50'],

            // 전시 상태 — 정본은 display_status 다 (06_pending D-3)
            'display_status'    => ['required', Rule::in(Book::displayStatusValues())],

            // 서지 정보
            'description'       => ['nullable', 'string'],
            'table_of_contents' => ['nullable', 'string'],

            // 이미지 파일 (신규 업로드). 표지는 700×980 이상 · 5:7
            'thumbnail'         => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp']), $this->coverRule()],
            'preview_images'    => ['nullable', 'array'],
            'preview_images.*'  => ['image', 'mimes:jpg,jpeg,png,gif,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','gif','webp'])],
            'detail_images'     => ['nullable', 'array'],
            'detail_images.*'   => ['image', 'mimes:jpg,jpeg,png,gif,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','gif','webp'])],

            // 이미지 삭제 컨트롤
            'delete_thumbnail'      => ['nullable', 'boolean'],
            'deleted_attachments'   => ['nullable', 'array'],
            'deleted_attachments.*' => ['integer'],

            // 강사 다중 매핑
            'instructors'                    => ['nullable', 'array'],
            'instructors.*.instructor_id'    => [
                'required_with:instructors', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(BookRepository::class)->instructorIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                'distinct',
            ],
            'instructors.*.role'             => ['required_with:instructors', Rule::in(['m', 's', 'a'])],
        ];
```
attributes:
```php
        return [
            'title'                   => '교재명',
            'category_id'             => '노출 카테고리',
            'cert_category_ids'       => '자격증 종류',
            'cert_category_ids.*'     => '자격증 종류',
            'package_bundled_yn'      => '패키지 동봉',
            'isbn'                    => 'ISBN',
            'author'                  => '저자',
            'publisher'               => '출판사',
            'published_at'            => '발행일',
            'edition'                 => '판쇄',
            'original_price'          => '판매 정가',
            'cost_price'              => '사입 원가',
            'sale_price'              => '실판매가',
            'is_free'                 => '무료 도서',
            'stock'                   => '현재 재고',
            'stock_alert_qty'         => '품절 임계치',
            'is_preorder'             => '예약 주문 허용',
            'restock_date'            => '재입고 예정일',
            'delivery_fee'            => '기본 배송비',
            'is_free_delivery'        => '조건부 무료배송 적용 대상',
            'free_delivery_threshold' => '무료배송 기준액',
            'island_delivery_fee'     => '도서산간 추가 배송비',
            'return_delivery_fee'     => '반품 배송비',
            'page_count'              => '페이지 수',
            'book_size'               => '판형',
            'display_status'          => '전시 상태',
            'thumbnail'               => '표지 이미지',
            'preview_images.*'        => '미리보기 이미지',
            'detail_images.*'         => '세부 이미지',
        ];
```

## BookRoyaltyContractRequest (extends FormRequest)
```php
        return [
            'book_id' => ['nullable', 'integer', 'min:1'],
            // SKU 가 없으면 화면에 적을 이름이 없다. 연결된 저서는 도서명을 books 에서 읽는다
            'book_title' => ['required_without:book_id', 'nullable', 'string', 'max:255'],
            'expected_publish_date' => ['nullable', 'date'],
            'royalty_rate' => ['required', 'numeric', 'min:0', 'max:100'],
            'royalty_basis' => ['required', 'string', Rule::in(array_keys(RightsHolderContractRequest::ROYALTY_BASES))],
            // 상태는 조건 변경에서만 쓴다(종료로 닫는 경로)
            'status' => ['nullable', 'string', Rule::in([BookRoyaltyContract::STATUS_ACTIVE, BookRoyaltyContract::STATUS_ENDED])],
            'memo' => ['nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return [
            'book_id' => 'SKU 연결 도서',
            'book_title' => '저서명',
            'expected_publish_date' => '출간 예정일',
            'royalty_rate' => '인세 요율',
            'royalty_basis' => '인세 산정 기준',
            'status' => '적용 상태',
            'memo' => '비고',
        ];
```

## BookStockAdjustRequest (extends FormRequest)
```php
        return [
            // 입고 / 반품 입고 / 파본 폐기 / 실사 조정 — 운영자가 고를 수 있는 사유만
            'type' => ['required', Rule::in(array_keys(BookStockLog::ADJUST_TYPE_LABELS))],
            // 증감이라 음수를 허용한다. 0 은 이력만 남고 아무것도 바뀌지 않아 막는다
            'quantity' => ['required', 'integer', 'not_in:0'],
            'memo' => ['nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return [
            'type' => '조정 사유',
            'quantity' => '증감 수량',
            'memo' => '메모',
        ];
```

## BookSupplyRequest (extends FormRequest)
```php
        return [
            // 등록은 교재를 고른다 — 수정은 경로의 교재
            'book_id' => [$this->routeIs('admin.book-supply.store') ? 'required' : 'prohibited', 'integer', 'min:1'],
            // 기본값을 두지 않는다 — 담당자가 반드시 고른다
            // 위탁(CONSIGNMENT)은 2차라 저장을 받지 않는다(결정 2026-10-19) — 화면에서 선택지를 빼도
            // 폼을 직접 만든 요청은 여기서 떨어뜨린다. 이미 위탁으로 저장된 행의 표시는 그대로 둔다
            'book_supply_type' => ['required', 'string', Rule::in(array_keys(BookSupplyService::SELECTABLE_SUPPLY_LABELS))],
            // 형식만 본다 — 공급 형태별 필수는 '판매 이력 거부' 다음 순서라 서비스가 판정한다
            'own_copyright_yn' => ['nullable', 'boolean'],
            'supplier_id' => ['nullable', 'integer', 'min:1'],
            'cost_price' => ['nullable', 'integer', 'min:0', 'max:100000000'],
        ];
```
attributes:
```php
        return ['book_id' => '도서', 'book_supply_type' => '공급 형태', 'own_copyright_yn' => '저작권 귀속', 'supplier_id' => '매입처', 'cost_price' => '사입 원가'];
```

## CategoryRequest (extends FormRequest)
```php
        $categoryId = $this->route('category');

        return [
            'parent_id'  => [
                'nullable', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CategoryRepository::class)->activeIdExists($value)) {
                        $fail($this->messages()['parent_id.exists']);
                    }
                },
                $this->parentDepthRule($categoryId),
            ],
            // 프론트 GNB · 수강신청 탭 라벨로 그대로 나간다. 길면 탭이 깨진다 (설계서 :46)
            'name'       => ['required', 'string', 'max:30', $this->uniqueNameRule($categoryId)],
            // slug 는 화면에서 받지 않는다 (설계서 §2 입력 항목에 없다) — Service 가 카테고리명으로 만든다
            'slug'       => ['exclude'],
            // 순서는 트리 드래그 저장으로만 바꾼다 — 폼이 보낸 값은 버리고 신규는 맨 뒤에 둔다
            'sort_order' => ['exclude'],
            'is_active'  => ['required', 'boolean'],
        ];
```

## CategorySortRequest (extends FormRequest)
```php
        return [
            'items'              => ['required', 'array', 'min:1'],
            'items.*.id'         => ['required', 'integer', 'min:1', 'distinct'],
            'items.*.parent_id'  => ['nullable', 'integer', 'min:1'],
            'items.*.sort_order' => ['required', 'integer', 'min:1'],
        ];
```

## ContractCoSignerRequest (extends FormRequest)
```php
        return [
            'payee_id' => ['required', 'integer', 'min:1', 'exists:rights_holders,id'],
            'role' => ['required', 'string', 'max:50'],
            'entity_type' => ['nullable', 'string', 'max:50'],
            'tax_case' => ['nullable', 'string', 'max:50'],
            'is_author' => ['nullable', 'boolean'],
            'succession_yn' => ['nullable', 'boolean'],
            // 승계 표시가 있으면 확정일이 있어야 한다 — payee_is_author 전환 기준일이다
            'succession_date' => ['nullable', 'required_if:succession_yn,1', 'date_format:Y-m-d'],
        ];
```
attributes:
```php
        return [
            'payee_id' => '수취인',
            'role' => '계약상 지위',
            'entity_type' => '사업자 구분',
            'tax_case' => '세무 케이스',
            'is_author' => '저작자 본인 여부',
            'succession_yn' => '상속 승계 여부',
            'succession_date' => '승계 확정일',
        ];
```

## CouponIssueRequest (extends FormRequest)
```php
        return [
            'user_ids_text' => ['nullable', 'string', 'max:20000'],
            'user_ids_file' => [
                'nullable',
                'file',
                'max:2048', // 2MB
                'extensions:xlsx',
                // 내용 판정. 확장자는 클라이언트가 붙인 값이라 그대로 믿지 않는다
                new RealFileType(['xlsx']),
            ],
        ];
```

## CouponRequest (extends FormRequest)
```php
        return [
            // 쿠폰명은 회원 쿠폰함 · 주문서에 그대로 보인다
            'name' => ['required', 'string', 'max:'.Coupon::MAX_NAME_LENGTH],
            'is_public' => ['nullable', 'boolean'], // 1=공개/0=비공개
            'code' => [
                'nullable', 'string', 'max:50', 'regex:/^[A-Z0-9_]+$/',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && app(CouponRepository::class)->couponCodeTaken($value)) {
                        $fail($this->messages()['code.unique']);
                    }
                },
            ], // 대문자 정규화 후 영문 대문자/숫자/언더바(_)만 허용
            'type' => ['required', Rule::in(array_keys(Coupon::TYPES))],
            // 적용 대상 — 전체 상품, 또는 카테고리 · 개별 상품(강좌 · 패키지)을 함께 지정. 강사 · 배송비 방식은 없앴다
            'target_scope' => ['required', Rule::in([Coupon::TARGET_SCOPE_ALL, Coupon::TARGET_SCOPE_SELECTED])],
            'target_category_ids' => ['nullable', 'array', 'max:200'],
            'target_category_ids.*' => ['integer', 'min:1', $this->existingTarget('category')],
            'target_course_ids' => ['nullable', 'array', 'max:500'],
            'target_course_ids.*' => ['integer', 'min:1', $this->existingTarget('course')],
            'target_package_ids' => ['nullable', 'array', 'max:500'],
            'target_package_ids.*' => ['integer', 'min:1', $this->existingTarget('package')],
            // 정률 1~40% 정수, 정액 1,000~200,000원 1,000원 단위 — 상한은 프론트가 아니라 여기서 막는다
            'discount_value' => $this->input('type') === 'fixed'
                ? ['required', 'integer', 'min:'.Coupon::FIXED_DISCOUNT_UNIT, 'max:'.$this->maxDiscount(), 'multiple_of:'.Coupon::FIXED_DISCOUNT_UNIT]
                : ['required', 'integer', 'min:1', 'max:'.$this->maxDiscount()],
            // 유효기간은 발급일 기준 D+N 과 절대 기간(종료일) 중 하나 — 고른 쪽 값만 필수
            'expire_mode' => ['required', Rule::in([Coupon::EXPIRE_MODE_DAYS, Coupon::EXPIRE_MODE_FIXED])],
            'expire_days' => ['nullable', 'required_if:expire_mode,'.Coupon::EXPIRE_MODE_DAYS, 'integer', 'min:1', 'max:'.Coupon::MAX_EXPIRE_DAYS],
            'expire_at' => ['nullable', 'required_if:expire_mode,'.Coupon::EXPIRE_MODE_FIXED, 'date', 'after_or_equal:today'], // 그날 자정까지 유효
            'max_issue_count' => ['nullable', 'integer', 'min:1'], // 발급 한도: 미입력 시 무제한(기간 지속 지급형)
            'unlimited' => ['nullable', 'boolean'], // [무제한] 체크 — 총량을 비운다
            // 발급 방식 3종. 타겟 그룹은 수동 대량에서 고를 수 있다(고르면 예약 시각, 비우면 저장 즉시 그룹 전체 발급 · 안 고르면 ID 지급만)
            'issue_method' => ['required', Rule::in(array_keys(Coupon::ISSUE_METHOD_FORM_LABELS))],
            'target_group_id' => [
                'nullable', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CouponRepository::class)->activeGroupExists((int) $value)) {
                        $fail('사용 중인 회원 그룹 · 태그를 골라주세요.');
                    }
                },
            ],
            'scheduled_at' => ['nullable', 'date', 'after:now'],
            // 등록 폼 1회용 토큰 — 그룹 즉시 발급이 붙은 저장이 두 번 실행되면 쿠폰과 발급이 두 벌 생긴다
            'form_token' => ['required', 'string', 'size:40'],
            'allow_with_point' => ['nullable', 'boolean'], // 포인트와 함께 사용 허용 — 보내지 않으면 기본 허용
            // 최소 결제금액: 0 · 비움 = 제한 없음. 상한은 칸(int) 범위
            'min_order_amount' => ['nullable', 'integer', 'min:0', 'max:2147483647'],
            // 1인당 발급 매수: 비우면 1. 상한은 칸(unsigned int) 범위
            'max_per_user' => ['nullable', 'integer', 'min:1', 'max:4294967295'],
            'memo' => ['nullable', 'string', 'max:500'],
        ];
```
attributes:
```php
        return [
            'name' => '쿠폰명',
            'is_public' => '공개 여부',
            'code' => '쿠폰 코드',
            'type' => '쿠폰 종류',
            'target_scope' => '적용 대상',
            'target_category_ids' => '카테고리',
            'target_course_ids' => '강좌',
            'target_package_ids' => '패키지',
            'discount_value' => '할인값',
            'expire_mode' => '유효기간',
            'issue_method' => '발급 방식',
            'target_group_id' => '타겟 그룹',
            'scheduled_at' => '발급 예약',
            'expire_days' => '발급일 기준 일수',
            'expire_at' => '절대 기간 종료일',
            'max_issue_count' => '발급 수량 한도',
            'min_order_amount' => '최소 결제금액',
            'max_per_user' => '1인당 발급 매수',
            'memo' => '비고',
        ];
```

## CouponUpdateRequest (extends CouponRequest)
```php
        $rules = parent::rules();
        // 코드는 바꾸지 않고, 수정은 같은 행을 덮어써 두 번 실행돼도 결과가 같아 1회용 토큰이 필요 없다(그룹 발급은 잠금 안에서 한 번만)
        unset($rules['code'], $rules['form_token']);

        $coupon = $this->route('coupon');
        if (! $coupon instanceof Coupon) {
            return $rules;
        }

        // 없앤 방식(강사 · 배송비) 대상의 옛 쿠폰은 대상을 받지 않는다 — 폼에도 대상 입력이 없고 서버도 바꾸지 않는다
        if ($this->retiredTargets($coupon)) {
            unset($rules['target_scope'], $rules['target_category_ids'], $rules['target_category_ids.*'], $rules['target_course_ids'],
                $rules['target_course_ids.*'], $rules['target_package_ids'], $rules['target_package_ids.*']);
        }

        if ($this->sameAsStored('scheduled_at', $coupon->scheduled_at?->format('Y-m-d H:i'))) {
            $rules['scheduled_at'] = ['nullable', 'date'];
        }
        if ($this->sameAsStored('expire_at', $coupon->expire_at?->toDateString())) {
            $rules['expire_at'] = ['nullable', 'required_if:expire_mode,'.Coupon::EXPIRE_MODE_FIXED, 'date'];
        }
        $groupId = $this->input('target_group_id');
        if ($coupon->target_group_id !== null && is_scalar($groupId) && (string) $groupId === (string) $coupon->target_group_id) {
            $rules['target_group_id'] = ['nullable', 'integer'];
        }

        return $rules;
```

## CourseCurriculumRequest (extends FormRequest)
```php
        return [
            // 0강 저장은 서버에서 거부한다 (설계서 :254)
            'lectures' => ['required', 'array', 'min:1'],
            'lectures.*' => [
                'required', 'integer', 'min:1', 'distinct',
                // 분모가 없는 강의를 편성하면 진도율이 계산되지 않는다 (설계서 :294).
                // 화면이 체크박스를 잠그지만 요청을 직접 만들면 뚫리므로 서버가 다시 본다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if ($validator->errors()->has($attribute)) {
                        return;
                    }

                    if (! app(CourseRepository::class)->lectureIsPlayable($value)) {
                        $fail('VOD Key 가 없거나 재생시간이 입력되지 않은 강의는 편성할 수 없습니다.');
                    }
                },
            ],
        ];
```

## CourseExtendRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'member_id' => ['required', 'integer', 'min:1'],
            // 최대 4자리 — 상한 판정은 Service 가 하고 여기서는 자릿수 오입력만 막는다
            'days' => ['required', 'regex:/^[1-9]\d{0,3}$/'],
            'reason_code' => ['required', 'in:'.implode(',', array_keys(UserCourseControlService::REASONS))],
        ]);
```
attributes:
```php
        return ['reason' => '상세 사유'];
```

## CoursePauseRequest (extends MemberReasonRequest)
```php
        $rules = array_merge(parent::rules(), [
            'member_id' => ['required', 'integer', 'min:1'],
            'reason_code' => ['required', 'in:'.implode(',', array_keys(UserCourseControlService::REASONS))],
        ]);

        // 해제에는 정지 기간이 없다. 같은 규칙을 걸면 사유만 받는 해제 폼이 항상 거절된다
        if ($this->isResume()) {
            return $rules;
        }

        return $rules + [
            'indefinite' => ['required', 'in:0,1'],
            'days' => ['exclude_if:indefinite,1', 'required', 'regex:/^[1-9]\d{0,3}$/'],
        ];
```
attributes:
```php
        return ['reason' => '상세 사유'];
```

## CourseRequest (extends FormRequest)
```php
        return [
            // 기본정보
            'title'          => ['required', 'string', 'max:255'],
            // 노출 카테고리는 2Depth 1건이다. 다중 노출은 정산·통계 귀속을 모호하게 만든다
            // (설계서 ADMN-PROD-003 ①). 저장은 category_products 로 간다
            'category_id'    => ['required', 'integer',
                // 삭제된 카테고리는 셀렉트에 없지만 id 를 직접 실어 보내면 통과한다
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->activeCategoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                $this->categoryDepthRule(),
            ],
            'duration_days'  => ['required', 'integer', 'min:1'],
            // 사전판매(오픈 예정 강좌)는 결제일이 아니라 지정일부터 일수를 센다 (설계서 :301)
            'start_type'     => ['nullable', 'in:immediate,scheduled'],
            'start_date'     => ['nullable', 'date', 'required_if:start_type,scheduled'],

            // 가격
            'original_price' => ['required', 'integer', 'min:0'],
            'cost_price'     => ['nullable', 'integer', 'min:0'],
            'sale_price'     => ['required', 'integer', 'min:0', $this->salePriceRule()],

            // 전시 상태 — 정본은 display_status 다 (06_pending D-3)
            'display_status' => ['required', Rule::in(Course::displayStatusValues())],

            // 판매 설정 (ADMN-PROD-SALE)
            // tax_type · start_type 은 화면이 값을 보내도 무시한다. 서비스가 고정값으로 덮는다
            'allow_coupon'   => ['nullable', 'boolean'],
            'allow_point'    => ['nullable', 'boolean'],

            // 대표 이미지 720×405(16:9) — 저장 시 필수 (설계서 :328 · :409)
            //
            // required 냐 nullable 이냐를 미리 정해 문자열로 넣는다. 클로저로 판정하면
            // nullable 이 값 없음에서 뒤 규칙을 건너뛰어(암묵 규칙이 아니다) 검사 자체가 돌지 않는다.
            'thumbnail'        => [$this->thumbnailIsRequired() ? 'required' : 'nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp']), $this->thumbnailRule()],
            'delete_thumbnail' => ['nullable', 'boolean'],

            // 강조 배지
            'badge_slot_1_code' => ['nullable', 'string', 'max:50'],
            'badge_slot_2_code' => ['nullable', 'string', 'max:50'],

            // 소개 영상 / 샘플 강의 (커리큘럼 외 단건 매핑)
            'intro_lecture_id'  => [
                'nullable', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->activeLectureIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'sample_lecture_id' => [
                'nullable', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->activeLectureIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],

            // 강사 매핑 (필수, 최소 1명, 대표 정확히 1명, 대표는 계약 유효)
            'instructors'                       => ['required', 'array', 'min:1', $this->mainInstructorRule(), $this->mainContractRule()],
            // distinct — 같은 강사를 두 행으로 넣으면 정산 배분이 중복 계상된다
            'instructors.*.instructor_id'       => [
                'required', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->instructorIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                'distinct',
            ],
            'instructors.*.role'                => ['required', 'in:m,s,a'],

            // 교재 매핑
            'books'              => ['nullable', 'array'],
            'books.*.book_id'    => [
                'required', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->activeBookIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'books.*.book_type'  => ['required', 'in:main,sub'],

            // 강의 매핑 (커리큘럼 1강 이상 필수)
            'lectures'   => ['required', 'array', 'min:1', $this->playableLectureRule(), $this->inactiveLectureRule()],
            'lectures.*' => [
                'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(CourseRepository::class)->activeLectureIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],

            // 강좌 정보 에디터
            'description'     => ['nullable', 'string'],       // 강좌소개
            'target_audience' => ['nullable', 'string'],       // 수강대상
            'content'         => ['nullable', 'string'],       // 내용 및 특징
        ];
```
attributes:
```php
        return [
            'title'             => '강좌명',
            'category_id'       => '노출 카테고리',
            'duration_days'     => '수강기간',
            'original_price'    => '정가',
            'cost_price'        => '원가',
            'sale_price'        => '판매가',
            'display_status'    => '전시 상태',
            'allow_coupon'      => '쿠폰 사용 허용',
            'allow_point'       => '포인트 사용 허용',
            'thumbnail'         => '대표 이미지',
            'intro_lecture_id'  => '강좌 소개 영상',
            'sample_lecture_id' => '샘플 강의',
            'instructors'       => '강사',
            'books'             => '교재',
            'lectures'          => '강의',
            'description'       => '강좌소개',
            'target_audience'   => '수강대상',
            'content'           => '내용 및 특징',
        ];
```

## DeliveryBatchRequest (extends FormRequest)
- const `TYPES` = ['all' => '전체', 'export' => '발주 다운로드', 'import' => '송장 업로드']
- const `DEFAULT_DAYS` = 30
```php
        return [];
```

## DeliveryDeliveredRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'ids' => ['required', 'array', 'min:1'],
            'ids.*' => ['integer'],
            'delivered_at' => ['required', 'date_format:Y-m-d', 'before_or_equal:today'],
        ]);
```

## DeliveryTrackingImportRequest (extends FormRequest)
```php
        return [
            'file' => ['required', 'file', 'mimes:xlsx', 'max:'.(int) config('delivery.import_max_kb')],
            'batch_id' => ['nullable', 'integer'],
            'overwrite' => ['nullable', 'boolean'],
            'notify' => ['nullable', 'boolean'],
        ];
```

## DeliveryTrackingRequest (extends FormRequest)
```php
        return [
            'courier' => ['required', Rule::in(array_keys(config('delivery.couriers')))],
            'tracking_no' => ['required', 'regex:/^\d{10,14}$/'],
            'shipped_at' => ['required', 'date_format:Y-m-d', 'before_or_equal:today'],
            'reason_code' => ['required', Rule::in(array_keys(DeliveryService::TRACKING_REASONS))],
            'reason_memo' => ['nullable', 'string', 'max:200', Rule::requiredIf($this->input('reason_code') === 'etc')],
            'notify' => ['nullable', 'boolean'],
        ];
```

## ExamTargetRequest (extends FormRequest)
```php
        $examTargetId = $this->route('examTarget');

        return [
            'type'       => ['required', Rule::in(array_keys(ExamTarget::typeLabels()))],
            'name'       => ['required', 'string', 'max:100'],
            'code'       => [
                'nullable', 'string', 'max:50',
                // 제외 id 는 원래 문자열 규칙처럼 문자열로 넘긴다(등록이면 빈 문자열)
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($examTargetId) {
                    if (! $validator->errors()->has($attribute) && app(ExamTargetRepository::class)->codeTaken($value, (string) $examTargetId)) {
                        $fail($this->messages()['code.unique']);
                    }
                },
            ],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active'  => ['required', 'boolean'],
        ];
```

## FaqBulkRequest (extends FormRequest)
```php
        $rules = [
            'ids' => ['required', 'array', 'min:1', 'max:'.FaqService::MAX_BULK],
            'ids.*' => ['integer', 'min:1'],
        ];

        if ($this->routeIs('admin.faqs.status.update')) {
            $rules['is_visible'] = ['required', 'boolean'];
        } else {
            $rules['category_id'] = [
                'required', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(FaqRepository::class)->categoryIdExists($value)) {
                        $fail($this->messages()['category_id.exists']);
                    }
                },
            ];
        }

        return $rules;
```

## FaqCategoryRequest (extends FormRequest)
```php
        return [
            'name' => ['required', 'string', 'max:50'],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'name' => '카테고리명',
            'sort_order' => '정렬 순서',
            'is_active' => '활성 여부',
        ];
```

## FaqRequest (extends FormRequest)
```php
        return [
            'category_id' => [
                'required', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(FaqRepository::class)->categoryIdExists($value)) {
                        $fail($this->messages()['category_id.exists']);
                    }
                },
            ],
            // 클수록 위. 같은 값이면 최근 등록순(정렬은 조회 측)
            'weight' => ['required', 'integer', 'min:0', 'max:999'],
            // 초과분은 잘라 저장하지 않고 오류로 되돌린다
            'question' => ['required', 'string', 'max:100'],
            'answer' => ['required', 'string'],
            'is_visible' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'category_id' => '카테고리',
            'weight' => '가중치',
            'question' => '질문',
            'answer' => '답변',
            'is_visible' => '노출 여부',
        ];
```

## FindIdSendCodeRequest (extends FormRequest)
```php
        // 형식 검사만 한다. 계정 존재 여부는 Service 가 판정한다
        return [
            'name'  => ['required', 'string', 'min:2', 'max:20'],
            'phone' => ['required', 'string', 'digits_between:10,11'],
        ];
```

## FindIdVerifyCodeRequest (extends FormRequest)
```php
        return [
            'code' => ['required', 'digits:6'],
        ];
```

## FreeContentDuplicateRequest (extends FormRequest)
```php
        return [
            'content_type' => ['required', Rule::in(array_keys(FreeContent::TYPES))],
            'cert_category_id' => ['required', 'integer', 'min:1'],
            'year' => ['required', 'integer', 'min:2000', 'max:2100'],
            'round_no' => ['nullable', 'integer', 'min:1', 'max:999'],
            'except_id' => ['nullable', 'integer', 'min:1'],
        ];
```
attributes:
```php
        return ['content_type' => '구분', 'cert_category_id' => '자격증', 'year' => '연도', 'round_no' => '회차'];
```

## FreeContentIndexRequest (extends FormRequest)
- const `LIST_KEYS` = ['type', 'cert', 'year', 'round', 'display', 'keyword', 'sort', 'page']
```php
        return [];
```

## FreeContentRequest (extends FormRequest)
- const `ATTACHMENT_MAX` = 5
- const `ATTACHMENT_MAX_KB` = 10240
```php
        return [
            'content_type' => ['required', Rule::in(array_keys(FreeContent::TYPES))],
            'cert_category_id' => ['required', 'integer'],
            'year' => ['required', 'integer', 'min:2000', 'max:2100'],
            // 회차는 숫자 입력이고 범위를 고정하지 않는다(설계서 ① — 자격증마다 시행 횟수가 다르다). 매일 1문제는 서비스가 비운다
            'round_no' => ['nullable', 'required_if:content_type,'.FreeContent::TYPE_EXAM, 'integer', 'min:1', 'max:999'],
            'title' => ['required', 'string', 'max:100'],
            'content' => ['nullable', 'string'],
            'status' => ['required', Rule::in(array_keys(FreeContent::DISPLAYS))],
            'started_at' => ['nullable', 'date_format:Y-m-d'],
            'related_course_id' => ['nullable', 'integer'],
            'attachments' => ['nullable', 'array', 'max:'.self::ATTACHMENT_MAX],
            'attachments.*' => ['file', 'mimes:pdf', 'max:'.self::ATTACHMENT_MAX_KB, new RealFileType(['pdf'])],
            'delete_attachments' => ['nullable', 'array'],
            'delete_attachments.*' => ['integer'],
            'list_query' => ['nullable', 'string', 'max:1000'],
        ];
```
attributes:
```php
        return [
            'content_type' => '구분',
            'cert_category_id' => '자격증',
            'year' => '연도',
            'round_no' => '회차',
            'title' => '제목',
            'content' => '본문',
            'status' => '전시 여부',
            'started_at' => '전시 시작일',
            'related_course_id' => '관련 강좌',
            'attachments' => 'PDF 첨부',
            'attachments.*' => 'PDF 첨부',
        ];
```

## FreeContentStatusRequest (extends SelectedIdsRequest)
```php
        return parent::rules() + ['status' => ['required', Rule::in(array_keys(FreeContent::DISPLAYS))]];
```
attributes:
```php
        return parent::attributes() + ['status' => '전시 여부'];
```

## GoodsRequest (extends FormRequest)
```php
        // 일괄 판매중지는 고른 상품 id 만 받는다 — 같은 화면의 쓰기라 이 Request 가 함께 맡는다
        if ($this->routeIs('admin.goods.bulk-stop.update')) {
            return [
                'ids' => ['required', 'array', 'min:1', 'max:500'],
                'ids.*' => ['integer', 'min:1'],
            ];
        }

        $creating = $this->routeIs('admin.goods.store');

        return [
            'name' => ['required', 'string', 'max:255'],
            'goods_supply_type' => ['required', 'string', Rule::in(array_keys(Goods::SUPPLY_LABELS))],
            'display_status' => ['required', 'string', Rule::in(array_keys(Goods::STATUS_LABELS))],
            'sale_price' => ['required', 'integer', 'min:0', 'max:100000000'],
            'cost_price' => ['nullable', 'integer', 'min:0', 'max:100000000'],
            'stock' => ['required', 'integer', 'min:0', 'max:1000000'],
            'stock_alert_qty' => ['nullable', 'integer', 'min:0', 'max:1000000'],
            // 노출 카테고리 — 교재구매와 분리된 일반상품 진열 영역 (설계서 :805). 미지정 허용
            'category_id' => ['nullable', 'integer', 'min:1'],
            // 매입 재판매는 매입처가 있어야 한다. 매입처가 실제로 있는지는 서비스가 본다
            'supplier_id' => ['nullable', 'required_if:goods_supply_type,'.Goods::SUPPLY_PURCHASED, 'integer', 'min:1'],
            // 공개 구획이라 svg 는 받지 않는다(스크립트 실행)
            'thumbnail' => [$creating ? 'required' : 'nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg', 'jpeg', 'png', 'webp'])],
            // 칸이 TEXT(65,535바이트)라 글자 수가 아니라 바이트로 잰다 — 한글은 3바이트라 글자 수 검사로는 저장에서 터진다
            'description' => ['nullable', 'string', function (string $attribute, mixed $value, \Closure $fail) {
                if (is_string($value) && strlen($value) > 65535) {
                    $fail('상세 설명이 너무 깁니다. 내용을 줄여 주세요.');
                }
            }],
        ];
```
attributes:
```php
        return [
            'name' => '상품명',
            'goods_supply_type' => '공급 형태',
            'display_status' => '판매 상태',
            'sale_price' => '판매가',
            'cost_price' => '사입 원가',
            'stock' => '현재 재고',
            'stock_alert_qty' => '재고 알림 임계치',
            'supplier_id' => '매입처',
            'thumbnail' => '대표 이미지',
            'description' => '상세 설명',
        ];
```

## GoodsStockAdjustRequest (extends FormRequest)
```php
        return [
            // 입고 / 복구 / 수기 조정 / 파손 / 분실 — 운영자가 고를 수 있는 사유만
            'type' => ['required', Rule::in(array_keys(GoodsStockLog::ADJUST_TYPE_LABELS))],
            // 증감이라 음수를 허용한다. 0 은 이력만 남고 아무것도 바뀌지 않아 막는다
            'quantity' => ['required', 'integer', 'not_in:0'],
            'memo' => ['nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return [
            'type' => '조정 사유',
            'quantity' => '증감 수량',
            'memo' => '메모',
        ];
```

## InquiryBulkAssignRequest (extends FormRequest)
```php
        return [
            'ids' => ['required', 'array', 'min:1'],
            'ids.*' => ['integer'],
            'assign_user_id' => ['required', 'integer'],
        ];
```
attributes:
```php
        return [
            'ids' => '문의',
            'assign_user_id' => '담당자',
        ];
```

## InquiryCategoryRequest (extends FormRequest)
```php
        return [
            'parent_id' => [
                'required', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InquiryCategoryRepository::class)->categoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'name' => ['required', 'string', 'max:40'],
            'target_screen' => ['required', 'string', Rule::in(array_keys(InquiryCategory::TARGET_SCREENS))],
            // 담당 부서 큐: 스키마가 단일이라 단일 역할코드로 받는다(설계서 복수선택은 스키마 미지원)
            'assign_role' => [
                'required', 'string',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InquiryCategoryRepository::class)->roleCodeExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'is_active' => ['required', 'boolean'],
            'sort_order' => ['nullable', 'integer', 'min:0'],
        ];
```
attributes:
```php
        return [
            'parent_id' => '대분류',
            'name' => '소분류 명칭',
            'target_screen' => '자동 배정 화면',
            'assign_role' => '담당 부서 큐',
            'is_active' => '상태',
            'sort_order' => '노출 순서',
        ];
```

## InquiryMajorCategoryRequest (extends FormRequest)
```php
        $id = $this->route('inquiryCategory');

        return [
            'name' => ['required', 'string', 'max:50'],
            // 소분류 코드 약어(VOC-{code}-NN)로 쓰인다. 최초 지정 후 바꾸면 지난 문의 분류가 어긋난다
            'code' => [
                'required', 'string', 'max:20', 'regex:/^[A-Z0-9]+$/',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($id) {
                    if (! $validator->errors()->has($attribute) && app(InquiryCategoryRepository::class)->codeTaken($value, $id ?: null)) {
                        $fail($this->messages()['code.unique']);
                    }
                },
            ],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'name' => '대분류명',
            'code' => '대분류 약어',
            'sort_order' => '노출 순서',
            'is_active' => '상태',
        ];
```

## InquiryProcessRequest (extends FormRequest)
```php
        return [
            'action' => ['required', Rule::in(['draft', 'hold', 'answer'])],

            // 답변 등록
            // 10자 규칙은 답변 등록에만 — 임시 저장은 쓰다 만 글도 남긴다
            'answer_content' => [
                'nullable', 'required_if:action,answer', 'string',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (($validator->getData()['action'] ?? null) === 'answer' && mb_strlen(trim((string) $value)) < 10) {
                        $fail($this->messages()['answer_content.min']);
                    }
                },
            ],

            // 보류: 사유·재개 예정일 필수(무기한 방치 방지)
            'hold_reason' => ['nullable', 'required_if:action,hold', 'string', 'max:255'],
            'hold_until' => ['nullable', 'required_if:action,hold', 'date', 'after_or_equal:today'],

            // 임시저장 초안 · 내부 메모(회원 미노출)
            'draft_content' => ['nullable', 'string'],
            'internal_memo' => ['nullable', 'string'],

            // 답변완료 건 수정 사유(필수 여부는 서비스가 저장된 상태를 보고 정한다)
            'edit_reason' => ['nullable', 'string', 'max:255'],

            // 회원 컨텍스트 모달 [회원 상세로 이동] — 임시 저장 후 회원 상세로
            'go_member' => ['nullable', 'boolean'],

            // 답변 알림(설계서 ④) — 보내지 않으면 기본 ON. 새 답변에서 끌 때 사유가 필요한지는 서비스가 저장된 상태를 보고 정한다
            'notify' => ['nullable', 'boolean'],
            'notify_skip_reason' => ['nullable', 'string', 'max:200'],
        ];
```
attributes:
```php
        return [
            'answer_content' => '답변 본문',
            'hold_reason' => '보류 사유',
            'hold_until' => '보류 재개 예정일',
            'edit_reason' => '수정 사유',
            'notify_skip_reason' => '알림 미발송 사유',
        ];
```

## InquiryReleaseRequest (extends FormRequest)
```php
        return [
            'release_reason' => ['required', 'string', 'max:255'],
        ];
```
attributes:
```php
        return [
            'release_reason' => '해제 사유',
        ];
```

## InstructorProfileRequest (extends FormRequest)
```php
        $profileId = $this->route('instructorProfile');

        return [
            // 권리자 계약 원장이 원천이다. 이 화면은 고른 권리자의 강사 행을 찾거나 만든다 —
            // 권리자 없이 새 강사를 만드는 경로는 없다(ADMN-PROD-006-S1 ① · admin-product :660)
            'rights_holder_id' => [
                'required', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InstructorProfileRepository::class)->profileEligibleRightsHolderExists($value)) {
                        $fail($this->messages()['rights_holder_id.eligible']);
                    }
                },
                // 1차 오픈은 1인 1프로필이다. 두 번째 프로필은 저장 단계에서 막는다.
                // 판정 기준은 권리자다 — 강사 id 로 보면 강사를 이제 만드는 경로에서 빠져나간다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($profileId) {
                    if (! $validator->errors()->has($attribute) && app(InstructorProfileRepository::class)->rightsHolderProfileTaken($value, $profileId ?: null)) {
                        $fail($this->messages()['rights_holder_id.unique']);
                    }
                },
            ],

            // 자격증 분류 — 필수 · 복수 선택(admin-product :722). 강사 목록(USER-INST-003)에서
            // 이 강사가 나오는 자격증 탭을 정하므로, 비면 어느 탭에도 나오지 않는 프로필이 저장된다
            'categories' => ['required', 'array', 'min:1'],
            'categories.*' => [
                'integer',
                // 선택지는 카테고리 관리(ADMN-PROD-001)의 1Depth 자격증이다. 2Depth(필기 · 실기)는
                // 과정 분류라 자격증 탭이 될 수 없고, FK 로는 depth 를 걸 수 없어 여기서 막는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InstructorRepository::class)->rootCategoryIdExists($value)) {
                        $fail($this->messages()['categories.*.exists']);
                    }
                },
            ],

            // 강사 구분 정/부 2종 고정. 표시 · 통계용이며 요율 · 지분에 개입하지 않는다
            // (admin-instructor :566 확인 필요 사항 5)
            'instructor_type' => ['required', Rule::in([Instructor::TYPE_MAIN, Instructor::TYPE_SUB])],

            'photo'        => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:2048', new RealFileType(['jpg','jpeg','png','webp']), $this->photoRule()],
            'delete_photo' => ['nullable', 'boolean'],

            'display_name'   => ['required', 'string', 'max:50'],
            'title'          => ['nullable', 'string', 'max:100'],
            // 약력은 필수다 (설계서 ⑥ :705 *). 강사 홈 · 강좌 상세의 소개 영역이 비면 화면이 비어 보인다.
            // 에디터가 빈 문단(<p><br></p>)을 보내므로 태그를 걷어낸 알맹이로 판정한다
            'career'         => ['required', 'string', $this->careerNotEmptyRule()],
            // 목록 카드 요약이라 길이를 넘기면 카드가 깨진다(설계서 ⑥ 최대 120자)
            'intro_text'     => ['nullable', 'string', 'max:120'],
            'home_link_type' => ['required', Rule::in(array_keys(InstructorProfile::HOME_LINK_LABELS))],
            'home_url'       => [
                $this->input('home_link_type') === InstructorProfile::HOME_EXTERNAL ? 'required' : 'nullable',
                'url', 'max:500',
            ],

            'is_display'   => ['nullable', 'boolean'],
            'sort_order'   => ['nullable', 'integer', 'min:0'],
            'auto_preview' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'rights_holder_id' => '연동 권리자',
            'categories'       => '자격증 분류',
            'instructor_type'  => '강사 구분',
            'photo'          => '프로필 사진',
            'display_name'   => '전시 강사명',
            'title'          => '타이틀',
            'career'         => '약력',
            'intro_text'     => '소개 텍스트',
            'home_link_type' => '강사 전용 홈',
            'home_url'       => '아웃링크 URL',
            'sort_order'     => '목록 정렬 순서',
        ];
```

## InstructorRequest (extends FormRequest)
```php
        return [
            // 관리자 계정 연결(user_id)은 관리자 계정 폼에서만 바꾼다 — 여기서 받지 않는다
            // 권리자 연결(설계서 :2387 — 강사 ID 원천은 권리자 원장). 해제 · 변경 사유는 서비스가 판정한다
            'rights_holder_id' => [
                'nullable', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InstructorRepository::class)->activeRightsHolderIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'rights_holder_change_reason' => ['nullable', 'string', 'max:200'],
            'name' => ['required', 'string', 'max:50'],
            // 생년월일 · 연락처는 동명이인 식별키다(설계서 :116 · S1 목업 :174-180 필수).
            // 비워 두면 같은 이름의 강사를 구분할 수단이 사라진다
            'birth_date' => ['required', 'date', 'after_or_equal:1900-01-01', 'before_or_equal:today'],
            'phone' => ['required', 'string', 'digits_between:9,11'],
            // 정강사 / 부강사 2종 고정. 표시 · 통계용이며 요율은 계약이 정한다 (설계서 :243-245)
            'instructor_type' => ['required', Rule::in(['main', 'sub'])],
            'email' => ['nullable', 'email', 'max:100'],
            // 요율은 받지 않는다. 정본은 contract_rate_lines 다 (합의서 05장 5.1)
            'intro_lecture_id' => [
                'nullable', 'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InstructorRepository::class)->activeLectureIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],

            // 담당 과목 — categories 1Depth 만 받는다.
            // 2Depth(필기 · 실기)는 과정 분류라 담당 과목이 될 수 없다.
            // FK 로는 depth 를 걸 수 없어 여기서 막는다.
            'categories' => ['nullable', 'array'],
            'categories.*' => [
                'integer',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InstructorRepository::class)->rootCategoryIdExists($value)) {
                        $fail($this->messages()['categories.*.exists']);
                    }
                },
            ],
        ];
```
attributes:
```php
        return [
            'name' => '강사명',
            'birth_date' => '생년월일',
            'instructor_type' => '강사 구분',
            'phone' => '연락처',
            'email' => '이메일',
            'categories' => '담당 과목',
        ];
```

## LectureRequest (extends FormRequest)
- const `CDN_KEY_PATTERN` = '/^(?!.*\.\.)[A-Za-z0-9._-]+(?:\/[A-Za-z0-9._-]+)*$/'
```php
        $lectureId = $this->route('lecture');
        $lectureId = is_object($lectureId) ? $lectureId->id : $lectureId;

        return [
            'title'           => ['required', 'string', 'max:255'],
            'instructor_id'   => [
                'required', 'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(LectureRepository::class)->instructorIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
            'year'            => ['nullable', 'integer', 'min:2020', 'max:2040'],
            // 상품 분류 정본은 categories 다(ERD). 2Depth(과정 분류)만 붙는다
            'category_id'     => ['required', 'integer',
                // 삭제된 카테고리는 셀렉트에 없지만 id 를 직접 실어 보내면 통과한다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(LectureRepository::class)->activeCategoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                $this->categoryDepthRule(),
            ],
            'type'            => ['required', 'in:normal,ot,sample,product_intro,instructor_intro,free'],
            'source_type'     => ['required', 'in:cdn,youtube'],
            // Key 는 시스템 전체 유일하다. 같은 영상이 두 Unit 으로 존재하면 진도율이 이중 집계된다
            'cdn_key'         => [
                'nullable',
                'string',
                'min:5',
                'max:255',
                'regex:' . self::CDN_KEY_PATTERN,
                // 삭제분까지 본다 — 저장소가 deleted_at 조건 없이 세므로 소프트 삭제된 행도 걸린다.
                // 삭제한 강의의 Key 를 다시 쓰면 같은 영상이 두 Unit 으로 되살아나 진도가 이중 집계된다 (설계서 :217 · :248)
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($lectureId) {
                    if ($validator->errors()->has($attribute)) {
                        return;
                    }

                    // 어느 강의가 쥐고 있는지 밝힌다 — 그래야 운영자가 어디를 풀지 안다 (설계서 :217)
                    $owner = app(LectureRepository::class)->cdnKeyOwnerTitle($value, $lectureId ?: null);

                    if ($owner !== null) {
                        $fail('이미 [' . $owner . '] 에 등록된 Key 입니다.');
                    }
                },
            ],
            // DRM 콘텐츠 ID — OVP 가 발급한 식별자다. cdn_key(CDN 경로)와 별개 값이고
            // 같은 이유로 전체 유일이다. 선택 입력이라 비워도 저장은 된다(그 강의는 DRM 재생 불가)
            'drm_content_id'  => [
                'nullable',
                'string',
                'max:100',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) use ($lectureId) {
                    if ($validator->errors()->has($attribute)) {
                        return;
                    }

                    $owner = app(LectureRepository::class)->drmContentIdOwnerTitle($value, $lectureId ?: null);

                    if ($owner !== null) {
                        $fail('이미 [' . $owner . '] 에 등록된 DRM 콘텐츠 ID 입니다.');
                    }
                },
            ],
            // 이 값은 Lecture::playbackUrl() 이 플레이어에 그대로 넘긴다(Lecture:175). 스킴을 제한하지 않으면
            // javascript: · data: 를 저장할 수 있고, 재생 화면에서 그 URL 이 실행된다.
            // 받는 것은 http · https 뿐이다. 이미 저장된 값은 손대지 않는다 — 그 강의를 수정할 때 다시 받는다
            'source_url'      => ['nullable', 'string', 'max:500', 'url:http,https'],
            // 초 단위 정수 직접 입력이다. 진도율이 SUM(watched_sec) / SUM(duration_sec) 이라
            // 분:초로 받으면 화면과 계산 단위가 갈린다 (설계서 :221).
            // DRM 연결 강의는 prepareForValidation() 이 값을 걷어내고 OVP 값으로 채우므로
            // 수기 입력은 DRM 콘텐츠 ID 가 없을 때만 요구한다
            'duration_sec'    => ['required_without:drm_content_id', 'nullable', 'integer', 'min:1'],
            // 맛보기 Y 면 수강권 · 로그인 없이 재생된다 (설계서 :230)
            'is_preview'      => ['required', 'boolean'],
            // 미사용은 신규 커리큘럼 편성 후보에서 빠진다 (설계서 :246)
            'is_active'       => ['required', 'boolean'],
            // 설계서 ADMN-PROD-002 는 "강의 1건당 PDF 1개(20MB 이하). 다중 첨부 · 기타 확장자는
            // 받지 않는다" 로 확정이다.
            //
            // 개수 판정은 여기 한 곳에만 둔다. 서비스에도 같은 상한을 두면
            // 한쪽만 고쳐졌을 때 화면은 통과시키고 저장은 조용히 버리는 상태가 된다.
            'attachments'     => ['nullable', 'array', 'max:1'],
            // mimes 는 클라이언트가 보낸 값까지만 본다. 내용 판정은 RealFileType 이 한다
            'attachments.*'   => ['nullable', 'file', 'mimes:pdf', 'max:20480', new RealFileType(['pdf'])],
        ];
```

## LogSearchRequest (extends FormRequest)
- const `MAX_PERIOD_DAYS` = 90
- const `DEFAULT_PERIOD_DAYS` = 7
- const `PERIOD_PRESETS` = [ ['label' => '오늘', 'days' => 1], ['label' => '7일', 'days' => 7], ['label' => '30일', 'days' => 30], ['label' => '90일', 'days' => 90], ]
- const `ACTION_TYPES` = [ 'personal_view' => '개인정보 열람', 'unmask' => '마스킹 해제', 'member_update' => '회원 정보 수정', 'excel_download' => '엑셀 다운로드', 'setting_change' => '설정 변경', 'role_change' => '권한 변경', ]
- const `TAB_AUDIT` = 'audit'
- const `TAB_AUDIT_MONTHLY` = 'audit-monthly'
- const `TAB_ACCESS` = 'access'
- const `TABS` = [ self::TAB_AUDIT => '1. 감사 이벤트 건별 상세 원장 (Before / After JSON 비교)', self::TAB_AUDIT_MONTHLY => '2. 정산월별 감사 통계 요약 및 월마감 스냅샷 아카이브', self::TAB_ACCESS => '3. 운영자 접근 · 권한 · 다운로드 로그 (계정 단위)', ]
```php
        return [
            'start_date' => ['nullable', 'date_format:Y-m-d'],
            'end_date' => ['nullable', 'date_format:Y-m-d', 'after_or_equal:start_date'],
            'keyword' => ['nullable', 'string', 'max:100'],
            'ip' => ['nullable', 'string', 'max:45'],
            'per_page' => ['nullable', 'integer'],
            'period' => ['nullable', 'integer', 'in:' . implode(',', array_column(self::PERIOD_PRESETS, 'days'))],

            // 관리자 로그 전용
            'type' => ['nullable', 'string', 'in:' . implode(',', array_keys(self::ACTION_TYPES))],
            'result_status' => ['nullable', 'in:success,fail'],
            'target_type' => ['nullable', 'string', 'max:50'],
            'target_member' => ['nullable', 'string', 'max:191'],
            'admin_role_code' => ['nullable', 'string', 'max:30'],
            'disallowed_ip_only' => ['nullable', 'in:0,1'],

            // 로그인 로그 전용
            'status' => ['nullable', 'in:success,fail'],
            'event' => ['nullable', 'string', 'max:30'],

            // 정산 감사 로그 전용 (ADMN-CONF-010)
            //
            // 탭 · 감사 영역 · 발생 화면 · 귀속월은 `in:` · `regex:` 로 거절하지 않고
            // prepareForValidation 에서 정의되지 않은 값을 **걷어낸다**.
            // failedValidation 이 같은 주소로 되돌리므로(목록 화면이 GET 이라 그래야 한다)
            // 거절 규칙을 걸면 조작된 값이 쿼리에 남아 리다이렉트가 되돌이표가 된다.
            // 값의 출처는 우리 셀렉트뿐이고, 알 수 없는 값은 "전체" 로 떨어진다.
            'audit_keyword' => ['nullable', 'string', 'max:100'],
            'audit_page' => ['nullable', 'integer', 'min:1'],
        ];
```
attributes:
```php
        return [
            'start_date' => '시작일',
            'end_date' => '종료일',
            'keyword' => '검색어',
            'ip' => '접속 IP',
            'target_member' => '대상 회원',
        ];
```

## LoginRequest (extends FormRequest)
```php
        return [
            'login_id' => ['required', 'string'],
            'password' => ['required', 'string', 'min:6'],
        ];
```

## MaskingUnmaskRequest (extends FormRequest)
```php
        return [
            'target_type' => ['required', 'string', 'max:30'],
            'target_id'   => ['required', 'integer', 'min:1'],
            'field'       => ['required', 'string', 'max:30'],
            // 등급. 보내지 않으면 high 로 본다 — 기존 화면의 동작을 바꾸지 않기 위해서다
            'level'       => ['nullable', 'string', 'in:' . implode(',', MaskingService::LEVELS)],
            // basic 등급은 사유를 받지 않는다. 문자열 룰로 미리 정해야 한다 —
            // nullable 뒤에 클로저를 붙이면 값이 없을 때 룰 자체를 건너뛴다
            'reason'      => array_merge(
                [$this->requiresReason() ? 'required' : 'nullable', 'string'],
                ['in:' . implode(',', array_keys(ReasonRequest::REASONS))],
            ),
            'reason_ref'  => ['nullable', 'string', 'max:50', 'regex:/^[A-Za-z0-9\-]+$/'],
            // 기타(직접 입력)를 골랐을 때만 필수다. 규칙은 ReasonRequest 한 곳에서 온다
            'reason_etc'  => ReasonRequest::etcRules(),
            // 어느 화면에서 열었는지. 감사 때 "상세 화면인가 목록인가" 가 위험도를 가른다
            'screen'      => ['nullable', 'string', 'max:100'],
        ];
```

## MemberBlacklistRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'member_id' => ['required', 'integer', 'min:1'],
            'reason_type' => ['required', 'string', 'in:'.implode(',', array_keys(UserSanction::REASON_TYPES))],
            'duration' => ['required', 'string', 'in:'.implode(',', array_keys(UserSanction::DURATIONS))],
            'refund_confirm' => ['nullable', 'boolean'],
        ]);
```

## MemberDownloadRequest (extends ReasonRequest)
- const `FIELDS` = [ 'joined_at' => '가입일', 'name' => '이름', 'email' => '이메일', 'phone' => '휴대폰', 'address' => '배송 주소', 'points' => '보유 포인트', 'status' => '회원 상태', ]
- const `DEFAULT_FIELDS` = ['joined_at', 'name', 'email', 'points', 'status']
```php
        return array_merge(parent::rules(), [
            'fields' => ['required', 'array', 'min:1'],
            'fields.*' => ['string', 'in:'.implode(',', array_keys(self::FIELDS))],
            'pledge_purpose' => ['accepted'],
            'pledge_destroy' => ['accepted'],
        ]);
```

## MemberGroupBulkRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'group_id' => ['required', 'integer', 'min:1'],
            'action' => ['required', 'string', 'in:'.implode(',', array_keys(MemberGroupService::ACTIONS))],
            // upload = 엑셀 명단(매칭 결과를 먼저 확인한 세션 명단)
            'scope' => ['required', 'string', 'in:selected,filter,upload'],
            'member_ids' => ['required_if:scope,selected', 'array', 'max:'.MemberGroupService::MAX_BULK],
            'member_ids.*' => ['integer', 'min:1'],
            // 조건 없는 '조건 전체' 는 전체 회원이라 의도를 알 수 없다
            'filter' => ['required_if:scope,filter', 'array'],
        ]);
```

## MemberGroupRequest (extends FormRequest)
```php
        return [
            'name' => ['required', 'string', 'max:100'],
            'description' => ['nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return ['name' => '태그명', 'description' => '정의 · 부여 조건'];
```

## MemberPointRequest (extends MemberReasonRequest)
- const `DIRECTION_GRANT` = 'grant'
- const `DIRECTION_DEDUCT` = 'deduct'
- const `REASONS` = [ 'cs_outage' => 'CS 보상(서비스 장애)', 'cs_delivery' => 'CS 보상(배송 지연)', 'event' => '이벤트 당첨', 'promotion' => '프로모션 보상', 'correction' => '오지급 정정', 'partner' => '제휴 정산', 'other' => '기타', ]
- const `EXPIRE_PRESETS` = [30, 90, 180]
- const `DEFAULT_EXPIRE_DAYS` = 90
```php
        return array_merge(parent::rules(), [
            'direction' => ['required', 'in:'.self::DIRECTION_GRANT.','.self::DIRECTION_DEDUCT],
            'amount' => ['required', 'regex:/^[1-9]\d{0,8}$/'],
            'reason_code' => ['required', 'in:'.implode(',', array_keys(self::REASONS))],
            'expire_preset' => ['exclude_unless:direction,'.self::DIRECTION_GRANT, 'required', 'in:'.implode(',', [...self::EXPIRE_PRESETS, 'custom'])],
            'expire_date' => ['exclude_unless:expire_preset,custom', 'required', 'date', 'after:today'],
        ]);
```
attributes:
```php
        return ['reason' => '상세 사유'];
```

## MemberProgressRequest (extends FormRequest)
```php
        return [
            'user'   => ['nullable', 'string', 'max:100'],
            'course' => ['nullable', 'string', 'regex:/^(course|package):\d+$/'],
        ];
```

## MemberReasonRequest (extends FormRequest)
- const `MIN_LENGTH` = 10
```php
        return [
            'reason' => [
                'required', 'string', 'min:'.self::MIN_LENGTH, 'max:200',
                function (string $attribute, mixed $value, \Closure $fail) {
                    $compact = preg_replace('/\s+/u', '', (string) $value);

                    if (mb_strlen($compact) < self::MIN_LENGTH || count(array_unique(mb_str_split($compact))) < 3) {
                        $fail('사유를 구체적으로 입력해 주세요.');
                    }
                },
            ],
        ];
```

## MemberRequest (extends FormRequest)
```php
        return [
            'is_marketing_agreed' => ['required', 'boolean'],
            'address' => ['nullable', 'string', 'max:255'],
            'address_detail' => ['nullable', 'string', 'max:100'],
            'admin_memo' => ['nullable', 'string', 'max:2000'],
            'exam_target_ids' => ['nullable', 'array'],
            'exam_target_ids.*' => [
                'integer',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(MemberRepository::class)->examTargetIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
        ];
```
attributes:
```php
        return [
            'is_marketing_agreed' => '수신 동의',
            'address' => '배송지',
            'address_detail' => '배송지 상세',
            'admin_memo' => '관리자 메모',
        ];
```

## MemberStatusRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'status' => ['required', 'string', 'in:'.implode(',', MemberService::EDITABLE_STATUSES)],
        ]);
```

## MemberTagRequest (extends FormRequest)
```php
        return [
            'name' => ['required', 'string', 'max:100'],
            'axis' => ['required', 'string', 'in:'.implode(',', array_keys(UserGroup::AXES))],
            'assign_method' => ['required', 'string', 'in:'.UserGroup::ASSIGN_MANUAL.','.UserGroup::ASSIGN_AUTO],
            'badge_color' => ['required', 'string', 'in:'.implode(',', array_keys(UserGroup::BADGE_COLORS))],
            'description' => ['nullable', 'string', 'max:255'],
            // 자동 태그만 쓰는 칸. 필수 판정은 서비스가 한다(수동 탭에서는 아예 오지 않는다)
            'eval_cycle' => ['nullable', 'string', 'in:'.implode(',', array_keys(UserGroup::EVAL_CYCLES))],
            'on_exit' => ['nullable', 'string', 'in:'.UserGroup::ON_EXIT_KEEP.','.UserGroup::ON_EXIT_RELEASE],
            'conditions' => ['nullable', 'array'],
            'conditions.*.field' => ['nullable', 'string'],
            'conditions.*.op' => ['nullable', 'string'],
            'conditions.*.value' => ['nullable', 'string', 'max:50'],
            'conditions.*.join' => ['nullable', 'string'],
        ];
```

## MessageCampaignRequest (extends FormRequest)
```php
        // 화면 조회 · 엑셀 · 테스트 발송은 대상 입력만 읽는다(문자열만 걸러 targetInput · templateId)
        if (! $this->routeIs('admin.message-templates.campaigns.store')) {
            return [];
        }

        return [
            'template_id' => ['required', 'integer'],
            'target_type' => ['required', 'string'],
            'expected_target' => ['required', 'integer', 'min:1'],
            'scheduled_at' => ['required', 'date_format:Y-m-d\TH:i', 'after:now'],
            'send_reason' => ['required', 'string', 'max:200'],
        ];
```
attributes:
```php
        return [
            'template_id' => '발송 템플릿',
            'target_type' => '발송 대상',
            'expected_target' => '최종 발송 대상',
            'scheduled_at' => '예약 일시',
            'send_reason' => '발송 사유',
        ];
```

## MessageTemplateRequest (extends FormRequest)
- const `ALIMTALK_MAX_CHARS` = 1000
- const `LMS_MAX_BYTES` = 2000
- const `LMS_SUBJECT_MAX_BYTES` = 40
- const `EMAIL_MAX_CHARS` = 10000
```php
        $channels = array_keys(TemplateCatalog::CHANNELS['phone'] + TemplateCatalog::CHANNELS['email']);

        return [
            // 코드는 등록 때만 받는다 — 수정은 보내와도 쓰지 않는다(발송 코드가 이 코드로 템플릿을 찾는다)
            'code' => [Rule::requiredIf(fn () => $this->isMethod('post')), 'nullable', 'string', Rule::in(array_keys(TemplateCatalog::all()))],
            'channel' => ['required', 'string', Rule::in($channels)],
            'use_fallback' => ['nullable', 'boolean'],
            'subject' => ['nullable', 'string', 'max:255', Rule::requiredIf($this->input('channel') === 'email'), $this->subjectRule()],
            'content' => ['required', 'string', $this->contentRule()],
            'fallback_content' => ['nullable', 'string', $this->smsTextRule('LMS 대체 본문')],
            'is_active' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'code' => '발송 조건',
            'channel' => '채널',
            'use_fallback' => '대체 발송',
            'subject' => '제목',
            'content' => '본문',
            'fallback_content' => 'LMS 대체 본문',
            'is_active' => '사용 여부',
        ];
```

## MilestoneReviewRequest (extends FormRequest)
```php
        return [
            'milestone_id' => ['required', 'integer', 'min:1'],
            'decision' => ['required', Rule::in(['approve', 'reject'])],
            'review_note' => ['required', 'string', 'min:'.MilestoneReviewService::MIN_REVIEW_NOTE, 'max:2000'],
            'verify_method' => ['required', Rule::in(array_keys(ContractMilestone::VERIFY_METHOD_LABELS))],
        ];
```
attributes:
```php
        return [
            'milestone_id' => '마일스톤',
            'decision' => '검수 결과',
            'review_note' => '검수 의견 및 승인 근거',
            'verify_method' => '검수 방식',
        ];
```

## NoticeRequest (extends FormRequest)
```php
        return [
            // 목록 · 사용자 화면 · 팝업 연결에 같은 이름으로 보인다(① 최대 100자)
            'title' => ['required', 'string', 'max:100'],
            'content' => ['required', 'string'],

            // 노출 기기: 최소 1개 (체크박스 · 둘 다 해제 시 저장 거부)
            'device_pc' => ['nullable', 'required_without:device_mobile', 'boolean'],
            'device_mobile' => ['nullable', 'required_without:device_pc', 'boolean'],

            // 발행: 즉시/예약/임시. 예약이면 시각 필수(과거 판정은 서비스)
            'publish_mode' => ['required', Rule::in(['immediate', 'scheduled', 'draft'])],
            'published_at' => ['nullable', 'required_if:publish_mode,scheduled', 'date'],

            // 게시 기간 (종료 비우면 무기한)
            'started_at' => ['nullable', 'date'],
            'ended_at' => ['nullable', 'date', 'after_or_equal:started_at'],

            'is_pinned' => ['nullable', 'boolean'],
            'pin_order' => ['nullable', 'integer', 'min:1', 'max:'.Post::PIN_MAX],
            'allow_comment' => ['nullable', 'boolean'],

            // 첨부(⑤) — 개당 10MB · jpg/png/pdf/hwp/zip. 실제 바이트로 형식을 다시 본다(RealFileType)
            'attachments' => ['nullable', 'array', 'max:5'],
            'attachments.*' => ['file', 'mimes:jpg,jpeg,png,pdf,hwp,zip', 'max:10240', new RealFileType(['jpg', 'jpeg', 'png', 'pdf', 'hwp', 'zip'])],
            'delete_attachments' => ['nullable', 'array'],
            'delete_attachments.*' => ['integer'],
        ];
```
attributes:
```php
        return [
            'title' => '제목',
            'content' => '본문',
            'publish_mode' => '발행 방식',
            'published_at' => '예약 발행 시각',
            'pin_order' => '고정 순서',
            'attachments' => '첨부파일',
            'attachments.*' => '첨부파일',
        ];
```

## NtsTaxTypeReviewRequest (extends FormRequest)
- const `MIN_EXPLANATION` = 20
```php
        return [
            'log_id' => ['required', 'integer', 'min:1'],
            'explanation' => ['required', 'string', 'min:'.self::MIN_EXPLANATION, 'max:2000'],
            // 보류는 원장을 바꾸지 않고 마감 보류를 그대로 남긴다
            'hold' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'log_id' => '확인 이력',
            'explanation' => '소명 내용',
        ];
```

## NtsVerifyRequest (extends FormRequest)
```php
        return [
            'business_number' => ['required', 'string', 'digits:10'],
            'ceo_name' => ['required', 'string', 'max:50'],
            'open_date' => ['required', 'date'],
            // 확인 후 복귀 지점 — 계약 상세(탭 2)에서 실행했을 때만 들어온다
            'return_contract_id' => ['nullable', 'integer', 'min:1'],
        ];
```
attributes:
```php
        return [
            'business_number' => '사업자등록번호',
            'ceo_name' => '대표자명',
            'open_date' => '개업일',
        ];
```

## OrderAddressRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'receiver_name' => ['required', 'string', 'min:2', 'max:30'],
            'receiver_phone' => ['required', 'regex:/^\d{10,11}$/'],
            'receiver_zipcode' => ['required', 'regex:/^\d{5}$/'],
            // 주문서와 같은 배송 불가 주소 차단 — 관리자가 고쳐도 3PL 이 보내지 못하는 주소는 받지 않는다
            'receiver_address' => ['required', 'string', 'max:200', 'not_regex:'.Delivery::UNSHIPPABLE_ADDRESS_PATTERN],
            'receiver_address_detail' => ['nullable', 'string', 'max:200', 'not_regex:'.Delivery::UNSHIPPABLE_ADDRESS_PATTERN],
            'delivery_memo' => ['nullable', 'string', 'max:100'],
        ]);
```

## OrderDownloadRequest (extends ReasonRequest)

## OrderMemoRequest (extends FormRequest)
```php
        return ['content' => ['required', 'string', 'max:'.OrderService::MEMO_MAX]];
```

## PackageRequest (extends FormRequest)
```php
        return [
            'title' => ['required', 'string', 'max:255'],
            // 노출 카테고리는 2Depth 1건. 판정은 CategoryService 가 한다(강좌 · 교재와 같은 규칙)
            'category_id' => ['required', 'integer',
                // 삭제된 카테고리는 셀렉트에 없지만 id 를 직접 실어 보내면 통과한다
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(PackageRepository::class)->activeCategoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
                $this->categoryDepthRule(),
            ],
            // 패키지 수강일수는 구성 강좌 각각의 기간을 덮어쓴다(설계서 ④)
            'duration_days' => ['required', 'integer', 'min:1'],
            'sale_price' => ['required', 'integer', 'min:0'],
            'display_status' => ['required', Rule::in(Package::displayStatusValues())],
            // 합격 환급 인정 진도율은 패키지 단위(PO 2026-09-22). 대상일 때만 필수
            'is_pass_refund' => ['required', 'boolean'],
            'refund_min_progress' => ['nullable', Rule::requiredIf(fn () => $this->boolean('is_pass_refund')), 'integer', 'min:1', 'max:100'],
            'description' => ['nullable', 'string'],

            'thumbnail' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg', 'jpeg', 'png', 'webp']), $this->thumbnailRule()],
            'delete_thumbnail' => ['nullable', 'boolean'],

            // 구성품
            'items' => ['required', 'array', 'min:1', $this->compositionRule()],
            'items.*.product_type' => ['required', Rule::in([PackageItem::TYPE_COURSE, PackageItem::TYPE_BOOK])],
            'items.*.product_id' => ['required', 'integer', 'min:1'],
            'items.*.sort_order' => ['nullable', 'integer', 'min:0'],
        ];
```
attributes:
```php
        return [
            'title' => '패키지명',
            'category_id' => '노출 카테고리',
            'duration_days' => '수강일수',
            'sale_price' => '판매 기획가',
            'display_status' => '전시 상태',
            'is_pass_refund' => '합격 환급 대상',
            'refund_min_progress' => '인정 진도율',
            'description' => '패키지 소개',
            'thumbnail' => '대표 이미지',
            'items' => '구성품',
        ];
```

## PassRefundBulkRequest (extends FormRequest)
```php
        return [
            'ids' => ['required', 'array', 'min:1', 'max:500'],
            'ids.*' => ['integer', 'min:1', 'max:999999999999999999'],
            'paid_at' => ['nullable', 'date', 'before_or_equal:today'],
        ];
```

## PassRefundReviewRequest (extends FormRequest)
- const `CHECKS` = [ 'cert_name' => '합격증 성명 = 가입 회원명 일치', 'cert_exam' => '합격증 종목 · 회차 = 환급 대상 상품과 일치', 'cert_number' => '큐넷 발급 진위확인번호 육안 확인', 'id_name' => '신분증 성명 = 가입 회원명 일치', 'bank_holder' => '통장 예금주 = 회원 실명 일치', 'review_public' => '정상 게시물(비공개·삭제 아님) 확인', 'review_length' => '지정 글자 수 규정 충족', 'review_self' => '본인 작성(카페 ID 대조) 확인', ]
- const `EXAM_YEAR_MIN` = 2000
- const `EXAM_YEAR_MAX` = 2099
- const `EXAM_ROUND_MAX` = 9
- const `ACTION_VERIFY` = 'verify'
- const `ACTION_APPROVE` = 'approve'
- const `ACTION_REJECT` = 'reject'
- const `ACTION_MEMO` = 'memo'
```php
        $reject = $this->input('action') === self::ACTION_REJECT;
        // '종목 · 회차 일치'를 체크했다면 무엇과 맞췄는지 남아야 한다 — 승인은 모든 체크가 필요하니 승인 건에는 항상 회차가 남는다
        $examChecked = ! $reject && in_array('cert_exam', (array) $this->input('checks', []), true);

        return [
            'action' => ['required', 'string', Rule::in([self::ACTION_VERIFY, self::ACTION_APPROVE, self::ACTION_REJECT, self::ACTION_MEMO])],
            'admin_memo' => ['nullable', 'string', 'max:2000'],
            'checks' => ['nullable', 'array'],
            'checks.*' => ['string', Rule::in(array_keys(self::CHECKS))],
            'verified' => ['nullable', 'boolean'],
            // [보정 사유 · 근거 확인] — 진도율 보정 차시가 있는 건만 의미가 있다. 필요한지는 서버가 진도를 다시 집계해 판정한다
            'adjustment_confirmed' => ['nullable', 'boolean'],
            // 반려는 회차를 저장하지 않는다 — 같은 폼에 반쯤 적힌 회차가 반려를 막지 않게 검증 · 값에서 뺀다
            'exam_year' => ['exclude_if:action,'.self::ACTION_REJECT, Rule::requiredIf($examChecked), 'nullable', 'required_with:exam_round', 'integer', 'between:'.self::EXAM_YEAR_MIN.','.self::EXAM_YEAR_MAX],
            'exam_round' => ['exclude_if:action,'.self::ACTION_REJECT, Rule::requiredIf($examChecked), 'nullable', 'required_with:exam_year', 'integer', 'between:1,'.self::EXAM_ROUND_MAX],
            'reject_reason' => [Rule::requiredIf($reject), 'nullable', 'string', Rule::in(array_keys(PassRefundService::REJECT_REASONS))],
            'reject_detail' => [Rule::requiredIf($reject), 'nullable', 'string', 'min:'.PassRefundService::REJECT_DETAIL_MIN, 'max:1000'],
        ];
```

## PassRefundSettleRequest (extends FormRequest)
```php
        return [
            'opinion' => ['required', 'string', 'min:'.PassRefundSettleService::REVIEW_MIN, 'max:500'],
        ];
```
attributes:
```php
        return ['opinion' => '검수 의견'];
```

## PasswordResetRequest (extends FormRequest)
```php
        return [
            'password' => [
                'required',
                'string',
                'min:8',
                'max:12',
                Password::min(8)->max(12)->letters()->numbers()->symbols(),
                'confirmed',
            ],
        ];
```
attributes:
```php
        return [
            'password' => '비밀번호',
        ];
```

## PasswordResetSendCodeRequest (extends FormRequest)
```php
        // 형식 검사만 한다. 계정 존재 여부는 검증하지 않는다 —
        // 여기서 걸러내면 응답 차이로 계정 존재 여부가 드러난다
        return [
            'login_id' => ['required', 'string', 'max:60'],
        ];
```

## PasswordResetSmsSendRequest (extends FormRequest)
```php
        // 형식 검사만 한다. 계정 소유자 대조는 Service 가 한다
        return [
            'name'  => ['required', 'string', 'min:2', 'max:20'],
            'phone' => ['required', 'string', 'digits_between:10,11'],
        ];
```

## PasswordResetSmsVerifyRequest (extends FormRequest)
```php
        return [
            'code' => ['required', 'digits:6'],
        ];
```

## PasswordResetVerifyCodeRequest (extends FormRequest)
```php
        return [
            'code' => ['required', 'digits:6'],
        ];
```

## PayeeSplitRequest (extends FormRequest)
```php
        return [
            'reason' => ['required', 'string', 'min:10', 'max:255'],

            'splits' => ['required', 'array', 'min:1', 'max:20'],
            'splits.*.payee_id' => ['required', 'integer', 'min:1'],
            // DECIMAL(5,2) 라 0.01 ~ 100.00. 음수 · 0 은 수취인을 빼는 것이지 분할이 아니다
            'splits.*.split_ratio' => ['required', 'numeric', 'min:0.01', 'max:100', 'decimal:0,2'],
            'splits.*.start_date' => ['required', 'date_format:Y-m-d'],
            'splits.*.end_date' => ['nullable', 'date_format:Y-m-d', 'after_or_equal:splits.*.start_date'],
            'splits.*.note' => ['nullable', 'string', 'max:255'],
        ];
```
attributes:
```php
        return [
            'reason' => '변경 사유',
            'splits' => '수취인 분할',
            'splits.*.payee_id' => '수취인',
            'splits.*.split_ratio' => '분할 비율',
            'splits.*.start_date' => '적용 시작일',
            'splits.*.end_date' => '적용 종료일',
            'splits.*.note' => '비율 근거 메모',
        ];
```

## PgReconciliationApproveRequest (extends FormRequest)
```php
        return [
            'mismatch_reason_code' => ['required', 'string', Rule::in(array_keys(PgReconciliationItem::REASON_LABELS))],
            // 승인 소명은 감사 로그 필수 기록이라 최소 10자다(프로토 approveReconciliation)
            'explanation' => ['required', 'string', 'min:'.PgReconciliationItem::EXPLANATION_MIN, 'max:500'],
        ];
```
attributes:
```php
        return [
            'mismatch_reason_code' => '차이 원인 코드',
            'explanation' => '차이 소명 근거',
        ];
```

## PgReconciliationRunRequest (extends FormRequest)
```php
        return [
            // YYYY-MM 만 받는다. 형식이 어긋나면 월 범위 계산이 엉뚱한 달을 훑는다
            'month' => ['required', 'string', 'date_format:Y-m'],
        ];
```
attributes:
```php
        return ['month' => '대사 귀속월'];
```

## PiiDestructionApproveRequest (extends FormRequest)
```php
        return [
            'reason' => ['required', 'string', 'min:'.PiiControlService::REASON_MIN, 'max:500'],
        ];
```
attributes:
```php
        return ['reason' => '파기 승인 사유'];
```

## PlayerSettingRequest (extends FormRequest)
- const `MAX_SECONDS` = 300
- const `MAX_RESUME_OFFSET` = 600
```php
        return [
            // ② 동적 워터마크
            'watermark_use' => ['required', 'boolean'],
            'watermark_content' => ['required', Rule::in(array_keys(PlayerSetting::WATERMARK_CONTENTS))],
            'watermark_move_interval' => ['required', 'integer', 'min:1', 'max:'.self::MAX_SECONDS],
            // 설계서 ② — displayDuration ≤ positionChangeInterval 을 서버에서 검증한다.
            // 노출 시간이 주기보다 길면 숨는 구간이 없어 "이동하는 고정 워터마크" 가 된다
            'watermark_display_duration' => ['required', 'integer', 'min:1', 'max:'.self::MAX_SECONDS, 'lte:watermark_move_interval'],
            'watermark_opacity' => ['required', 'integer', 'min:1', 'max:100'],
            'watermark_font_size' => ['required', 'integer', 'min:8', 'max:48'],
            'watermark_mobile_same' => ['required', 'boolean'],

            // ④ 재생 제어
            'limit_forward' => ['required', 'boolean'],
            'limit_forward_free_off' => ['required', 'boolean'],
            'speed_min' => ['required', Rule::in($this->speedOptions())],
            // 설계서 ④ — 최소 > 최대 입력은 저장 차단. 통과하면 플레이어 배속 메뉴가 빈다
            'speed_max' => ['required', Rule::in($this->speedOptions()), 'gte:speed_min'],
            'progress_speed_policy' => ['required', Rule::in(array_keys(PlayerSetting::PROGRESS_SPEED_POLICIES))],
            'resume_use' => ['required', 'boolean'],
            'resume_offset_sec' => ['required', 'integer', 'min:0', 'max:'.self::MAX_RESUME_OFFSET],
            'rewind_allow' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return PlayerSetting::FIELD_LABELS;
```

## PopupReorderRequest (extends FormRequest)
```php
        return [
            'orders' => ['required', 'array', 'min:1'],
            'orders.*.id' => ['required', 'integer', 'distinct'],
            'orders.*.sort_order' => ['required', 'integer', 'min:0'],
        ];
```

## PopupRequest (extends FormRequest)
```php
        return [
            'title' => ['required', 'string', 'max:255'],
            'image' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp'])],
            'mobile_image' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120', new RealFileType(['jpg','jpeg','png','webp'])],
            'delete_image' => ['nullable', 'boolean'],
            'delete_mobile_image' => ['nullable', 'boolean'],
            'alt_text' => ['required', 'string', 'max:255'],
            'mobile_alt_text' => ['nullable', 'string', 'max:255'],
            // 연결 방식은 하나만 — post 면 게시글 필수, url 이면 링크(없어도 됨). 반대쪽 값은 서비스가 비운다
            'link_type' => ['required', Rule::in(array_keys(Popup::LINK_TYPES))],
            'post_id' => [
                'nullable', 'integer', 'required_if:link_type,post',
                // exists · unique 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(PopupRepository::class)->postIdExists($value)) {
                        $fail($this->messages()['post_id.exists']);
                    }
                },
            ],
            'link_url' => ['nullable', 'string', 'max:500', new DisplayLinkUrl],
            'link_target' => ['required', Rule::in(array_keys(Popup::LINK_TARGETS))],
            'position_type' => ['required', Rule::in(array_keys(Popup::POSITION_TYPES))],
            'pos_x' => ['nullable', 'integer'],
            'pos_y' => ['nullable', 'integer'],
            'width' => ['nullable', 'integer', 'min:0'],
            'height' => ['nullable', 'integer', 'min:0'],
            'start_at' => ['nullable', 'date'],
            'end_at' => ['nullable', 'date', 'after_or_equal:start_at'],
            'device' => ['required', Rule::in(array_keys(Popup::DEVICES))],
            'use_today_close' => ['required', 'boolean'],
            'use_week_close' => ['required', 'boolean'],
            'use_close_button' => ['required', 'boolean'],
            'sort_order' => ['nullable', 'integer', 'min:0'],
            'is_active' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'title' => '팝업명',
            'device' => '노출 대상',
            'alt_text' => '대체 텍스트',
            'end_at' => '노출 종료',
            'start_at' => '노출 시작',
        ];
```

## PostRequest (extends FormRequest)
```php
        return [
            'title'     => ['required', 'string', 'max:255'],
            'content'   => ['required', 'string'],
            'is_pinned' => ['required', 'boolean'],
            'is_public' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'title'     => '제목',
            'content'   => '본문',
            'is_pinned' => '상단 고정',
            'is_public' => '공개 여부',
        ];
```

## ProductQnaBulkAssignRequest (extends FormRequest)
```php
        return [
            'ids' => ['required', 'array', 'min:1'],
            'ids.*' => ['integer'],
            'assign_user_id' => ['required', 'integer'],
        ];
```
attributes:
```php
        return [
            'ids' => '문의',
            'assign_user_id' => '담당자',
        ];
```

## ProductQnaProcessRequest (extends FormRequest)
```php
        return [
            'action' => ['required', Rule::in(['answer', 'hide', 'secret'])],
            'answer_content' => ['nullable', 'required_if:action,answer', 'string', 'min:10'],
            'assign_dept' => ['nullable', Rule::in(array_keys(ProductQna::ASSIGN_DEPTS))],
            'is_secret' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'answer_content' => '답변 본문',
            'assign_dept' => '담당 부서',
        ];
```

## ProductStatRequest (extends SalesStatRequest)

## ProgressAdjustmentRequest (extends FormRequest)
```php
        return [
            // 0~100 정수만 받는다. 소수점은 입력받지 않는다(설계서 :456)
            'adjusted_rate' => ['required', 'integer', 'min:0', 'max:100'],
            'reason_code' => ['required', 'string', 'in:'.implode(',', array_keys(LectureProgressAdjustment::REASONS))],
            // 기타를 고르면 사유명을 직접 받는다(설계서 :466)
            'reason_text' => ['nullable', 'string', 'max:100', 'required_if:reason_code,'.LectureProgressAdjustment::REASON_ETC],
            // 최소 20자 — 감사 로그만 보고도 경위를 판단할 수 있어야 한다(설계서 :469).
            // 상한을 넘으면 잘라 저장하지 않고 오류로 되돌린다(설계서 :470)
            'detail' => ['required', 'string', 'min:'.LectureProgressAdjustment::DETAIL_MIN, 'max:'.LectureProgressAdjustment::DETAIL_MAX],
            // 근거 파일 필수 · 1개 이상. 금전(환급)에 직결되는 값이라 근거 없는 보정을 남기지 않는다(설계서 :473)
            'evidence' => ['required', 'array', 'min:1', 'max:5'],
            'evidence.*' => [
                'required',
                'file',
                'max:'.ProgressAdjustmentService::EVIDENCE_MAX_KB,
                'mimes:'.implode(',', ProgressAdjustmentService::EVIDENCE_EXTENSIONS),
                new RealFileType(ProgressAdjustmentService::EVIDENCE_EXTENSIONS),
            ],
        ];
```

## PromotionAssetRequest (extends FormRequest)
```php
        $extensions = PromotionAssetService::EXTENSIONS;

        return [
            'files' => ['required', 'array', 'min:1', 'max:20'],
            'files.*' => ['file', 'mimes:'.implode(',', $extensions), 'max:'.PromotionAssetService::MAX_FILE_KB, new RealFileType($extensions)],
        ];
```
attributes:
```php
        return ['files' => '에셋 파일', 'files.*' => '에셋 파일'];
```

## PromotionBlockRequest (extends FormRequest)
```php
        $on = fn () => $this->input('enabled') === '1';

        return [
            'enabled' => ['required', Rule::in(['0', '1'])],
            'benefits' => ['nullable', 'array'],
            'benefits.*' => [Rule::in(['coupon', 'point', 'earn'])],
            'block_from' => [Rule::requiredIf($on), 'nullable', 'date'],
            'block_to' => [Rule::requiredIf($on), 'nullable', 'date'],
            'target' => [Rule::requiredIf($on), 'nullable', Rule::in(['all', 'selected'])],
            'product_ids' => ['nullable', 'array'],
            'product_ids.*' => ['integer'],
            // 주문서 입력칸 아래에 그대로 나간다(⑤) — 40자 권장, 칸은 100자
            'reason' => [Rule::requiredIf($on), 'nullable', 'string', 'max:100'],
        ];
```
attributes:
```php
        return [
            'enabled' => '차단 사용',
            'block_from' => '차단 시작',
            'block_to' => '차단 종료',
            'target' => '대상 상품군',
            'reason' => '사용자 노출 사유',
        ];
```

## PromotionRequest (extends FormRequest)
- const `MAX_SOURCE_LENGTH` = 1_000_000
```php
        $creating = $this->route('promotion') === null;

        return [
            'type' => ['required', Rule::in(array_keys(Promotion::TYPES))],
            'title' => ['required', 'string', 'max:'.Promotion::MAX_TITLE_LENGTH],
            'slug' => [
                'required', 'string', 'between:2,40', 'regex:/^[a-z0-9]+(?:-[a-z0-9]+)*$/',
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    $exceptId = $this->route('promotion')?->id;
                    if (! $validator->errors()->has($attribute) && app(PromotionRepository::class)->slugTaken($value, $exceptId)) {
                        $fail($this->messages()['slug.taken']);
                    }
                },
            ],
            'started_at' => ['required', 'date_format:Y-m-d\TH:i'],
            'ended_at' => ['required', 'date_format:Y-m-d\TH:i', 'after:started_at'],
            'thumbnail' => [$creating ? 'required' : 'nullable', 'image', 'mimes:jpg,jpeg,png,webp', 'max:1024', new RealFileType(['jpg', 'jpeg', 'png', 'webp'])],
            'headline' => ['nullable', 'string', 'max:255'],
            'sort_type' => ['required', Rule::in(array_keys(Promotion::SORT_TYPES))],
            'html_content' => ['required', 'string', 'max:'.self::MAX_SOURCE_LENGTH],
            'css_content' => ['nullable', 'string', 'max:'.self::MAX_SOURCE_LENGTH],
            'js_content' => ['nullable', 'string', 'max:'.self::MAX_SOURCE_LENGTH],
            'products' => ['required', 'array', 'min:1', 'max:500'],
            'products.*.type' => ['required', Rule::in(array_keys(PromotionProduct::PRODUCT_TYPES))],
            'products.*.id' => ['required', 'integer', 'min:1'],
            'products.*.promo_price' => ['nullable', 'integer', 'min:0'],
            'products.*.discount_rate' => ['nullable', 'numeric', 'between:0,100'],
        ];
```
attributes:
```php
        return [
            'type' => '구분자',
            'title' => '기획전명',
            'slug' => 'URL 식별자(Slug)',
            'started_at' => '노출 시작',
            'ended_at' => '노출 종료',
            'thumbnail' => '목록 썸네일',
            'headline' => '상단 카피',
            'sort_type' => '상품 진열 순서',
            'html_content' => '랜딩 소스(HTML)',
            'css_content' => '랜딩 소스(CSS)',
            'js_content' => '랜딩 소스(JS)',
            'products' => '대상 상품',
            'products.*.type' => '대상 상품 구분',
            'products.*.id' => '대상 상품',
            'products.*.promo_price' => '기획전가',
            'products.*.discount_rate' => '할인율',
        ];
```

## PromotionStopRequest (extends FormRequest)
```php
        return [
            'reason' => ['required', 'string', 'min:2', 'max:200'],
        ];
```
attributes:
```php
        return ['reason' => '중단 사유'];
```

## QaAgentResultRequest (extends FormRequest)
```php
        return [
            // csv 는 환경에 따라 text/plain 으로 올라와 mimes 판정이 흔들린다 — 확장자까지 함께 본다
            'file' => ['required', 'file', 'mimes:csv,txt', 'max:'.(int) config('qa.upload_max_kb')],
            'set_code' => ['required', 'string', 'max:50'],
            'version' => ['required', 'string', 'max:20'],
            'round' => ['required', 'integer', 'min:1', 'max:999'],
        ];
```

## QaChecklistUploadRequest (extends FormRequest)
```php
        return [
            'file' => ['required', 'file', 'mimes:xlsx', 'max:'.(int) config('qa.upload_max_kb')],
            'set_code' => ['required', 'string', 'max:50', 'regex:/^[A-Za-z0-9가-힣._-]+$/u'],
            'version' => ['required', 'string', 'max:20', 'regex:/^[A-Za-z0-9가-힣._-]+$/u'],
            'import_results' => ['nullable', 'boolean'],
        ];
```

## QaFindingRequest (extends FormRequest)
```php
        return [
            'set_code' => ['required', 'string', 'max:50'],
            'version' => ['required', 'string', 'max:20'],
            'round' => ['required', 'integer', 'min:1', 'max:999'],
            'screen' => ['required', 'string', 'max:255'],
            'note' => ['required', 'string', 'max:2000'],
            'remark' => ['nullable', 'string', 'max:2000'],
        ] + QaShotRules::rules();
```

## QaFixLogRequest (extends FormRequest)
```php
        return [
            'set_code' => ['required', 'string', 'max:50'],
            'version' => ['required', 'string', 'max:20'],
            'item_no' => ['required', 'string', 'max:30'],
            'status' => ['required', 'string', 'in:'.implode(',', QaFixLog::STATUSES)],
            // 커밋을 적지 못하는 조치가 있다(설정 변경 · 의도된 동작 판정) — 비워 둘 수 있다.
            // 다만 적었다면 형식은 본다. 'abc' · '나중에' 가 들어오면 커밋 칸이 아무 뜻도 없어진다
            'commit_hash' => ['nullable', 'string', 'regex:'.QaFixLog::COMMIT_PATTERN],
            'note' => ['required', 'string', 'max:'.QaFixLog::NOTE_MAX],
            // 저장 후 돌아갈 화면. 화이트리스트로 받는다 — 주소를 그대로 받으면 열린 전달이 된다
            'back' => ['nullable', 'string', 'in:index,histories'],
        ];
```

## QaFixUploadRequest (extends FormRequest)
```php
        return [
            // csv 는 환경에 따라 text/plain 으로 올라와 mimes 판정이 흔들린다 — 확장자까지 함께 본다
            'file' => ['required', 'file', 'mimes:xlsx,csv,txt', 'max:'.(int) config('qa.fix_upload_max_kb')],
        ];
```

## QaResultRequest (extends FormRequest)
```php
        return [
            'set_code' => ['required', 'string', 'max:50'],
            'version' => ['required', 'string', 'max:20'],
            'item_no' => ['required', 'string', 'max:30'],
            'round' => ['required', 'integer', 'min:1', 'max:999'],
            'result' => ['required', 'string', 'in:'.implode(',', QaResult::ITEM_RESULTS)],
            // 이상 · 막힘은 비고가 없으면 고치는 사람이 재현할 수 없다 — 서버에서 막는다
            'note' => [
                Rule::requiredIf(fn () => in_array(
                    $this->input('result'),
                    [QaResult::RESULT_FAIL, QaResult::RESULT_BLOCKED],
                    true
                )),
                'string',
                // 계정 · 개인정보를 적지 않게 화면에서 안내한다. 길이는 넉넉히 두되 무한은 아니다
                'max:2000',
            ],
        ] + QaShotRules::rules();
```

## QaResultUploadRequest (extends FormRequest)
```php
        return [
            // csv 는 환경에 따라 text/plain 으로 올라온다 — 확장자와 실제 내용을 함께 본다
            'file' => ['required', 'file', 'mimes:csv,txt', new RealFileType(['csv', 'txt']), 'max:'.(int) config('qa.upload_max_kb')],
        ];
```
attributes:
```php
        return ['file' => '결과 CSV'];
```

## QaShotRules
```php
        $extensions = implode(',', QaResultAttachment::EXTENSIONS);

        return [
            'shots' => ['nullable', 'array', 'max:'.QaResultAttachment::MAX_COUNT],
            'shots.*' => [
                'image',
                'mimes:'.$extensions,
                'max:'.QaResultAttachment::MAX_KB,
                new RealFileType(QaResultAttachment::EXTENSIONS),
            ],
        ];
```

## ReasonRequest (extends FormRequest)
- const `REASON_ETC` = 'etc'
- const `REASONS` = [ 'refund_account' => '환불 계좌 확인', 'delivery_error' => '배송 오류 확인', 'identity_check' => '본인 확인 요청', 'payment_inquiry' => '결제 오류 조사', 'legal_request' => '법적 요청 대응', 'settlement_check' => '정산 · 지급 확인', self::REASON_ETC => '기타(직접 입력)', ]
- const `MIN_ETC_LENGTH` = 10
- const `MAX_ETC_LENGTH` = 150
- const `NOTICE` = '관리자 ID · 접속 IP · 열람 시각 · 대상 회원이 함께 기록되며 기록은 삭제할 수 없습니다.'
```php
        return [
            'reason' => ['required', 'string', 'in:' . implode(',', array_keys(self::REASONS))],
            'reason_ref' => ['nullable', 'string', 'max:50', 'regex:/^[A-Za-z0-9\-]+$/'],
            // 기타를 골랐을 때만 필수다. 모달을 건너뛴 요청도 여기서 막힌다(DECISIONS 103)
            'reason_etc' => self::etcRules(),
        ];
```
attributes:
```php
        return [
            'reason' => '열람 사유',
            'reason_ref' => '관련 문의 · 주문번호',
            'reason_etc' => '기타 사유',
        ];
```

## RefundAdjustmentRequest (extends FormRequest)
```php
        return [
            'adjustment_type' => ['required', 'string', Rule::in(array_keys(RefundAdjustment::TYPES))],
            'method' => ['required', 'string', Rule::in(array_keys(RefundAdjustment::METHOD_LABELS))],
            'amount' => ['required', 'integer', 'min:1', 'max:100000000'],
            'reason' => [
                'required', 'string', 'max:2000',
                function (string $attribute, mixed $value, \Closure $fail) {
                    if (mb_strlen(preg_replace('/\s+/u', '', (string) $value)) < RefundAdjustmentService::MIN_REASON) {
                        $fail('보정 사유를 '.RefundAdjustmentService::MIN_REASON.'자 이상 입력해 주세요.');
                    }
                },
            ],
            'bank_code' => ['nullable', 'string', Rule::in(array_keys(TossPaymentsGateway::banks()))],
            'account_no' => ['nullable', 'string', 'regex:/^[0-9-]{6,24}$/'],
            'account_holder' => ['nullable', 'string', 'max:50'],
            'evidences' => ['nullable', 'array', 'max:'.RefundAdjustmentService::EVIDENCE_MAX],
            'evidences.*' => ['file', 'mimes:jpg,jpeg,png,pdf', 'max:10240', new RealFileType(['jpg', 'jpeg', 'png', 'pdf'])],
        ];
```

## RefundApprovalRequest (extends FormRequest)
- const `MIN_REASON` = 10
- const `MAX_MINUS_REASON` = 150
```php
        return [
            'manual_amount' => ['nullable', 'integer', 'min:0', 'max:100000000'],
            'manual_reason' => ['nullable', 'string', 'required_with:manual_amount', 'min:'.self::MIN_REASON, 'max:500'],
            'minus_agree' => ['nullable', 'boolean'],
            'minus_reason' => ['nullable', 'string', 'max:'.self::MAX_MINUS_REASON],
        ];
```

## RefundHoldRequest (extends FormRequest)
```php
        return [
            'hold_reason' => ['required', 'string', Rule::in(array_keys(Refund::HOLD_REASONS))],
            'hold_memo' => ['required', 'string', 'max:500'],
        ];
```

## RefundInquiryCategoryRequest (extends FormRequest)
```php
        return [
            'category_id' => [
                'required', 'integer', 'min:1', 'max:999999999999999999',
                // exists 규칙처럼 앞 규칙이 이미 실패한 필드는 질의하지 않는다
                function (string $attribute, mixed $value, \Closure $fail, Validator $validator) {
                    if (! $validator->errors()->has($attribute) && ! app(InquiryRepository::class)->categoryIdExists($value)) {
                        $fail('validation.exists')->translate();
                    }
                },
            ],
        ];
```

## RefundInquiryRefundRequest (extends FormRequest)
```php
        return [
            'item_ids' => ['nullable', 'array', 'max:100'],
            'item_ids.*' => ['integer', 'min:1', 'max:999999999999999999'],
        ];
```

## RefundInquirySubTypeRequest (extends FormRequest)
```php
        return [
            'sub_type' => ['required', 'string', Rule::in(array_keys(Inquiry::SUB_TYPES))],
            'order_id' => ['nullable', 'integer', 'min:1', 'max:999999999999999999'],
            // 부분 환불로 저장할 때 환불할 라인 — 고르면 판정 저장과 함께 환불 건을 만든다
            'item_ids' => ['nullable', 'array', 'max:100'],
            'item_ids.*' => ['integer', 'min:1', 'max:999999999999999999'],
            'judge_reason' => ['nullable', 'string', 'max:500'],
        ];
```

## RefundInspectionRequest (extends FormRequest)
```php
        return [
            'inspection_result' => ['required', 'string', Rule::in([Refund::INSPECTION_NORMAL, Refund::INSPECTION_DAMAGED])],
            'liability' => ['nullable', 'string', Rule::requiredIf($this->input('inspection_result') === Refund::INSPECTION_NORMAL), Rule::in([Refund::LIABILITY_CUSTOMER, Refund::LIABILITY_COMPANY])],
            'inspection_memo' => ['nullable', 'string', 'max:2000'],
            // 사진 규칙은 배송 관리 반품 탭 검수 입력과 같다(같은 판정을 두 화면에서 받는다)
            'photos' => [Rule::requiredIf(fn () => Refund::inspectionNeedsPhoto($this->input('inspection_result'), $this->input('liability'))), 'array', 'max:'.RefundService::INSPECTION_PHOTO_MAX],
            'photos.*' => ['file', 'mimes:jpg,jpeg,png', 'max:10240', new RealFileType(['jpg', 'jpeg', 'png'])],
        ];
```

## RefundReceiptRequest (extends FormRequest)
```php
        return [
            'return_tracking_no' => ['nullable', 'string', 'max:100'],
            'received_at' => ['nullable', 'date', 'before_or_equal:now'],
        ];
```

## ReturnInspectionRequest (extends FormRequest)
- const `PHOTO_REQUIRED_MESSAGE` = '불합격 판정 · 고객 귀책은 검수 사진을 첨부해야 저장할 수 있습니다.'
```php
        return [
            'inspection_result' => ['required', 'string', Rule::in([Refund::INSPECTION_NORMAL, Refund::INSPECTION_DAMAGED])],
            'liability' => ['nullable', 'string', Rule::requiredIf($this->input('inspection_result') === Refund::INSPECTION_NORMAL), Rule::in([Refund::LIABILITY_CUSTOMER, Refund::LIABILITY_COMPANY])],
            'inspection_memo' => ['nullable', 'string', 'max:2000'],
            // 미확정: 검수 사진 필수 범위 — 이 화면 제안(훼손 시)과 환불 관리 제안(고객 귀책 또는 불합격 시)이 달라 둘 다 받는 쪽(Refund::inspectionNeedsPhoto)을 따름 · 하나로 정해지면 그 판정만 남긴다
            'photos' => ['nullable', 'array', 'max:'.RefundService::INSPECTION_PHOTO_MAX],
            'photos.*' => ['file', 'mimes:jpg,jpeg,png', 'max:10240', new RealFileType(['jpg', 'jpeg', 'png'])],
        ];
```

## ReviewModerationRequest (extends FormRequest)
```php
        return [
            'verify_status' => ['required', Rule::in(['verified', 'rejected', 'hidden'])],
            'reject_reason' => ['nullable', 'required_if:verify_status,rejected', 'string', 'min:10', 'max:255'],
            'display_site' => ['nullable', 'boolean'],
            'is_best' => ['nullable', 'boolean'],
            'display_instructor_home' => ['nullable', 'boolean'],
            'cafe_verified' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return [
            'verify_status' => '검증 상태',
            'reject_reason' => '반려 사유',
        ];
```

## ReviewPointRequest (extends MemberReasonRequest)
```php
        return array_merge(parent::rules(), [
            'amount' => ['required', 'regex:/^[1-9]\d{0,8}$/'],
        ]);
```

## RightsHolderContractMemoRequest (extends FormRequest)
```php
        return [
            'content' => ['required', 'string', 'max:2000'],
        ];
```
attributes:
```php
        return [
            'content' => '메모',
        ];
```

## RightsHolderContractPrepaymentLineRequest (extends FormRequest)
```php
        if ($this->isMethod('put')) {
            return [
                'nature' => ['required', Rule::in([PrepaymentLedgerLine::NATURE_INHERIT, ...array_keys(PrepaymentLedgerLine::NATURE_LABELS)])],
            ];
        }

        return [
            'line_type' => ['required', Rule::in(array_keys(PrepaymentLedgerLine::TYPE_LABELS))],
            'origin_line_id' => ['nullable', 'required_if:line_type,'.PrepaymentLedgerLine::TYPE_REVERSAL, 'integer'],
            'base_month' => ['required', 'date_format:Y-m'],
            'amount' => ['required', 'integer', 'min:1', 'max:2147483647'],
            'amount_sign' => ['nullable', Rule::in(['+', '-'])],
            'nature' => ['nullable', Rule::in([PrepaymentLedgerLine::NATURE_INHERIT, ...array_keys(PrepaymentLedgerLine::NATURE_LABELS)])],
            'income_type' => ['nullable', 'string', Rule::in(array_keys(PrepaymentLedgerLine::INCOME_LABELS))],
            'memo' => ['nullable', 'string', 'max:2000'],
            'evidence' => ['nullable', 'array'],
            'evidence.*' => ['file', 'mimes:jpg,jpeg,png,pdf', 'max:10240', new RealFileType(['jpg', 'jpeg', 'png', 'pdf'])],
        ];
```
attributes:
```php
        return [
            'line_type' => '라인 유형',
            'origin_line_id' => '정정 대상 원 라인',
            'base_month' => '정산 데이터 기준 월',
            'amount' => '금액',
            'nature' => '성격',
            'income_type' => '상계 대상 소득 구분',
            'memo' => '운영자 메모',
            'evidence.*' => '증빙 첨부',
        ];
```

## RightsHolderContractRequest (extends FormRequest)
- const `OFF_COURSE` = 'exclude_if:term_course_yn,0'
- const `OFF_BOOK` = 'exclude_unless:term_book_yn,1'
- const `OFF_CONS` = 'exclude_unless:term_cons_yn,1'
- const `ROYALTY_BASES` = [ 'LIST_PRICE' => '도서 정가 · 과세 제외', // v16 은 "배송비 제외" 만 적지만 쿠폰 · 포인트 차감 여부를 묻는 문의가 있어 괄호로 남긴다 'ACTUAL_PAID' => '이용자 실구매가 · 배송비 제외 (쿠폰 · 포인트 차감 후)', ]
```php
        return array_merge($this->coreRules(), $this->paymentTermRules());
```
attributes:
```php
        return [
            'title' => '계약명',
            'status' => '계약 상태',
            'started_at' => '시작일',
            'ended_at' => '현재 종료일',
            'initial_end_date' => '최초 종료일',
            'contract_expiry_alert_days' => '만료 알림 기준',
            'min_payout_limit' => '최소 지급 기준액',
            'min_claim_limit' => '최소 청구 기준액',
            'evidences.*.evidence_type' => '증빙 유형',
            'evidences.*.file_name' => '증빙 파일명',
            'terminated_at' => '중도 해지일',
            'terminate_reason' => '중도 해지 사유',
            'renewal_unit_years' => '갱신 단위',
            'origin_type' => '계약 발생 구분',
            'refund_promo_burden_type' => '환급 부담 방식',
            'predecessor_contract_id' => '선행 계약',
            'successor_contract_id' => '승계 계약',
            'rate_lines.*.started_at' => '요율 라인 시작일',
            'rate_lines.*.ended_at' => '요율 라인 종료일',
            'rate_lines.*.rate' => '요율',
            'rate_lines.*.mmg_amount' => '월 최소보장',
            'docs.*' => '계약서 사본',
            'rate_lines.*.rate_basis' => '산정 모수',
            'vat_exception_reason' => 'VAT 가산 예외 승인 사유',
            'royalty_rate' => '인세 요율',
            'royalty_basis' => '인세 산정 기준선',
            'consignment_fee_type' => '위탁 수수료 방식',
            'consignment_fee_rate' => '위탁 기본 수수료율',
            'consignment_return_days' => '회수 기한',
            'consignment_ended_at' => '위탁 계약 종료일',
            'exc_fee_amount' => '전속계약금 총 약정액',
            'exc_service_started_at' => '전속 의무 복무 시작일',
            'exc_service_ended_at' => '전속 의무 복무 종료일',
            'exc_payment_method' => '전속계약금 지급 구조',
            'exc_target_month' => '전속계약금 정산 반영 귀속월',
            'exc_rows.*.target_month' => '전속계약금 회차 귀속월',
            'exc_rows.*.amount' => '전속계약금 회차 금액',
            'exc_clawback_policy' => '중도 해지 반환 조항',
            'exc_penalty_calc_type' => '위약금 산정 방식',
            'exc_penalty_multiple_rate' => '위약금 배율',
            'exc_penalty_fixed_amount' => '위약금 정액',
            'exc_penalty_base' => '위약금 산정 기준액',
            'exc_penalty_clawback_relation' => '일할 반환과의 관계',
            'exc_penalty_trigger_text' => '위약 조항 발동 조건 문언',
            'dev_payment_method' => '개발지원금 지급 방식',
            'dev_cap_type' => '한도 유형',
            'dev_total_cap_amount' => '개발지원금 총 한도',
            'dev_rate_basis' => '개발지원금 산정 모수',
            'dev_start_month' => '개발지원금 유효 시작월',
            'dev_end_basis' => '개발지원금 종료 기준',
            'dev_end_month' => '개발지원금 유효 종료월',
            'dev_offset_type' => '상계 처리 유형',
            'dev_total_amount' => '개발지원금 총 약정액',
            'dev_rows.*.target_month' => '개발지원금 회차 귀속월',
            'dev_rows.*.amount' => '개발지원금 회차 금액',
            'dev_lump_amount' => '개발지원금 지급 금액',
            'dev_lump_month' => '개발지원금 귀속월',
            'dev_lump_title' => '개발지원금 지급 사유',
            'buyout_amount' => '매입 대금',
            'buyout_target_month' => '매절 지급 예정월',
            'buyout_exclusive_ended_at' => '독점 이용 종료일',
            'buyout_income' => '매절 대금 소득 구분',
            'etc_amount_type' => '기타 수당 방식',
            'etc_unit_price' => '건당 단가',
            'etc_rows.*.target_month' => '기타 수당 귀속월',
            'etc_rows.*.title' => '기타 수당 사유',
            'etc_rows.*.unit_count' => '기타 수당 건수',
            'etc_rows.*.amount' => '기타 수당 금액',
            'adv_nature' => '선급금 기본 성격',
            'adv_offset_target' => '상계 대상',
            'adv_payee_type' => '상계 귀속 수취인',
            'adv_offset_payee_id' => '상계 귀속 소속 법인',
        ];
```

## RightsHolderRequest (extends FormRequest)
```php
        $isPersonal = $this->input('tax_type') === RightsHolder::TAX_PERSONAL;
        $isBusiness = in_array($this->input('tax_type'), RightsHolder::BUSINESS_TYPES, true);
        $isInternal = $this->boolean('is_internal');

        // 수정 화면은 암호화 컬럼의 기존 값을 되돌려 줄 수 없다(마스킹된 표시값뿐).
        // 그래서 빈 입력은 "지우겠다" 가 아니라 "그대로 두겠다" 로 읽고 필수에서 뺀다 —
        // required 를 그대로 두면 값을 다시 타이핑하지 않는 한 수정 자체가 막힌다.
        // 등록은 처음 받는 값이라 필수를 유지한다
        $isUpdate = filled($this->route('rightsHolder'));

        return [
            'name'        => ['required', 'string', 'max:100'],
            'tax_type'    => ['required', Rule::in(array_keys(RightsHolder::TAX_TYPE_LABELS))],
            'is_internal' => ['nullable', 'boolean'],
            // 위탁자 = 도서 위탁 판매 주체(정산 합의서). 사업자만 될 수 있고 자사 권리자와 겸할 수 없다
            'rights_holder_type' => [
                'nullable',
                Rule::in([RightsHolder::TYPE_RIGHTS_HOLDER, RightsHolder::TYPE_CONSIGNOR]),
                function (string $attribute, $value, callable $fail) use ($isBusiness, $isInternal) {
                    if ($value === RightsHolder::TYPE_CONSIGNOR && (! $isBusiness || $isInternal)) {
                        $fail('위탁자는 사업자 세무 유형이어야 하고 자사 귀속과 함께 지정할 수 없습니다.');
                    }
                },
            ],
            'email'       => ['nullable', 'email', 'max:100'],
            'phone'       => ['nullable', 'string', 'max:20'],
            'partnership_started_at' => ['nullable', 'date'],

            // 개인 — 주민등록번호로 원천징수 대상을 식별한다 (합의서 02장)
            'resident_no_enc' => [$isPersonal && !$isInternal && !$isUpdate ? 'required' : 'nullable', 'string', 'digits:13'],
            'is_resident'     => ['nullable', 'boolean'],

            // 저작자 본인 여부 — 기타소득 필요경비 의제가 갈린다 (합의서 2.3).
            // 기본값에 기대지 않고 개인일 때는 명시 선택을 받는다
            'payee_is_author' => [$isPersonal ? 'required' : 'nullable', 'boolean'],

            // 소득 구분 2축 (기획서 02권 2장 · 설계서 P2 저장 차단 「기타소득인데 호 구분 없음」).
            // 재화 공급 라인은 비워 두므로 상위 축 자체는 선택 항목이다
            'income_category' => ['nullable', Rule::in(array_keys(RightsHolder::INCOME_CATEGORY_LABELS))],
            'income_clause'   => [
                'required_if:income_category,'.RightsHolder::INCOME_OTHER,
                'nullable',
                Rule::in(array_keys(RightsHolder::INCOME_CLAUSE_LABELS)),
            ],

            // 거주지 주소 — 지급명세서 항목. 사업장 주소(biz_address)와 다르다
            'address'        => [$isPersonal ? 'required' : 'nullable', 'string', 'max:255'],
            'address_detail' => ['nullable', 'string', 'max:255'],

            // 사업자(간이 · 일반 · 면세)
            'business_number' => [$isBusiness ? 'required' : 'nullable', 'string', 'digits:10'],
            'ceo_name'        => [$isBusiness ? 'required' : 'nullable', 'string', 'max:50'],

            // 사업자 세부 유형 — 개인사업자와 법인은 저작권 사용료 과세 여부가 갈린다(합의서 6.4절 · TX-07 / TX-09).
            // 자사 귀속은 국세청 게이트 대상이 아니라 받지 않는다
            'business_subtype' => [
                $isBusiness && ! $isInternal ? 'required' : 'nullable',
                Rule::in(array_keys(RightsHolder::BUSINESS_SUBTYPE_LABELS)),
            ],

            // 개업일 — 국세청 진위확인이 사업자등록번호 · 대표자명과 함께 필수로 보내는 항목이다(합의서 17.4절).
            // 자사 권리자 · 개인 프리랜서는 게이트를 적용하지 않는다
            'open_date' => [$isBusiness && ! $isInternal ? 'required' : 'nullable', 'date'],

            // 휴업자 계약 승인 사유 — 필수 판정은 Service 가 한다.
            // 휴업 여부는 입력값이 아니라 국세청 응답으로 채워진 원장 상태다(business_status)
            'suspended_approval_reason' => ['nullable', 'string', 'max:255'],

            // 세무 판정 상태 — 권리자 단위 수동 표시값이다. 라인 판정은 정산 9단계(TAX)가 한다(합의서 11.1절).
            // 판정 완료로 두려면 케이스를 지정해야 한다 — 식별자 없는 DECIDED 는 마감 대상 판정에 쓸 수 없다
            'tax_decision_status' => ['nullable', Rule::in(array_keys(RightsHolder::TAX_DECISION_LABELS))],
            'matrix_case_id'      => [
                'nullable',
                'required_if:tax_decision_status,'.RightsHolder::TAX_DECISION_DECIDED,
                Rule::in(RightsHolder::MATRIX_CASE_IDS),
            ],
            // 설계서 v16 taxDecisionReason · v12 "판정 근거(최대 300자)" — 화면 maxlength 와 같은 수를 둔다.
            // 판정 완료는 케이스 식별자와 근거가 **모두** 있어야 저장된다(설계서 v12 S1 ⑧) —
            // 근거 없는 DECIDED 는 누가 왜 판정 완료로 뒀는지 되짚을 수 없다
            'tax_decision_reason' => [
                'nullable',
                'required_if:tax_decision_status,'.RightsHolder::TAX_DECISION_DECIDED,
                'string',
                'max:300',
            ],
            'biz_category'    => [$isBusiness ? 'required' : 'nullable', 'string', 'max:100'],
            'biz_item'        => [$isBusiness ? 'required' : 'nullable', 'string', 'max:100'],
            'biz_address'     => [$isBusiness ? 'required' : 'nullable', 'string', 'max:255'],

            // 간이과세자만 — 발급 의무 여부로 부가세 가산이 갈린다
            'tax_invoice_eligible_yn' => ['nullable', 'boolean'],
            'vat_treatment'           => ['nullable', 'string', 'max:20'],
            // 일반 · 면세는 계산서 수취 메일이 필요하다
            'tax_email' => [
                in_array($this->input('tax_type'), [RightsHolder::TAX_GENERAL, RightsHolder::TAX_EXEMPT], true) ? 'required' : 'nullable',
                'email', 'max:100',
            ],

            // 정산 계좌 — 자사 귀속은 외부 이체 대상이 아니라 받지 않는다
            'bank_name'      => [$isInternal ? 'nullable' : 'required', 'string', 'max:50'],
            'account_no_enc' => [$isInternal || $isUpdate ? 'nullable' : 'required', 'string', 'max:30'],
            'account_holder' => [$isInternal ? 'nullable' : 'required', 'string', 'max:50'],

            // 증빙 사본 — proofs[유형][] 로 온다. private 디스크에 저장한다 (03장 3.3)
            //
            // 개수 판정은 여기 한 곳에만 둔다. 서비스에도 같은 상한을 두면
            // 한쪽만 고쳐졌을 때 화면은 통과시키고 저장은 조용히 버린다.
            //
            // 단일 서류 3종은 1건이다. 설계서 ADMN-INST-001 이 유형마다 한 줄 +
            // 상태 뱃지 하나로 그리므로 같은 유형이 2건이면 어느 것이 검증완료인지
            // 표현할 수단이 없다. 권리 승계 증빙만 복수를 받는다 —
            // 양도계약서 + 가족관계증명서처럼 여러 장으로 나뉘는 것이 정상이다.
            'proofs'   => ['nullable', 'array'],
            'proofs.*' => ['nullable', 'array'],
            'proofs.' . ContractEvidence::TYPE_PERSON_ID     => ['nullable', 'array', 'max:1'],
            'proofs.' . ContractEvidence::TYPE_BANKBOOK    => ['nullable', 'array', 'max:1'],
            'proofs.' . ContractEvidence::TYPE_BIZ_LICENSE => ['nullable', 'array', 'max:1'],
            'proofs.*.*' => ['file', 'mimes:jpg,jpeg,png,pdf', 'max:10240', new RealFileType(['jpg','jpeg','png','pdf'])],
            'deleted_attachments'   => ['nullable', 'array'],
            'deleted_attachments.*' => ['integer'],

            // 저장 후 복귀 지점 — 계약 상세(탭 2)에서 권리자 정보를 저장했을 때만 들어온다.
            // 소속 검증은 하지 않는다. 복귀 경로가 소속을 다시 보고 아니면 404 로 끝낸다
            'return_contract_id' => ['nullable', 'integer', 'min:1'],
        ];
```
attributes:
```php
        return [
            'name'                    => '상호명(성명)',
            'tax_type'                => '세무 유형',
            'is_internal'             => '자사 귀속',
            'rights_holder_type'      => '위탁자',
            'email'                   => '이메일',
            'phone'                   => '연락처',
            'partnership_started_at'  => '최초 파트너십 체결일',
            'resident_no_enc'         => '주민등록번호',
            'payee_is_author'         => '저작자 본인 여부',
            'address'                 => '거주지 주소',
            'address_detail'          => '상세 주소',
            'business_number'         => '사업자등록번호',
            'business_subtype'        => '사업자 세부 유형',
            'open_date'               => '개업일',
            'suspended_approval_reason' => '휴업자 계약 승인 사유',
            'tax_decision_status'     => '세무 판정 상태',
            'matrix_case_id'          => '판정 케이스 식별자',
            'tax_decision_reason'     => '판정 근거 · 검토 메모',
            'income_category'         => '기본 소득 구분',
            'income_clause'           => '기타소득 호 구분',
            'ceo_name'                => '대표자명',
            'biz_category'            => '업태',
            'biz_item'                => '업종',
            'biz_address'             => '사업장 주소',
            'tax_email'               => '계산서 수취 이메일',
            'bank_name'               => '정산 입금 은행',
            'account_no_enc'          => '정산 계좌번호',
            'account_holder'          => '예금주',
        ];
```

## RightsMappingContractRequest (extends FormRequest)
```php
        return [
            'rights_holder_id' => ['required', 'integer', 'min:1'],
            'type' => ['required', 'string', Rule::in([RightsMappingService::TYPE_COURSE, RightsMappingService::TYPE_BOOK])],
            'id' => ['required', 'integer', 'min:1'],
        ];
```
attributes:
```php
        return [
            'rights_holder_id' => '권리자',
            'type' => '상품 구분',
            'id' => '상품',
        ];
```

## RightsMappingRequest (extends FormRequest)
```php
        return [
            'type' => ['required', 'string', Rule::in([RightsMappingService::TYPE_COURSE, RightsMappingService::TYPE_BOOK])],
            'id' => ['required', 'integer', 'min:1'],

            // 강좌는 편집 단위가 강의다. 하나도 고르지 않으면 저장할 대상이 없다
            'lecture_ids' => ['array'],
            'lecture_ids.*' => ['integer', 'min:1'],

            'rows' => ['required', 'array', 'min:1'],
            // 기존 행이면 id 가 실린다. 값이 바뀌면 Service 가 닫고 새 행을 넣는다
            'rows.*.id' => ['nullable', 'integer', 'min:1'],
            'rows.*.rights_holder_id' => ['required', 'integer', 'min:1'],
            // 적용 계약은 필수다 — 매핑 행이 contract_id 를 NOT NULL 로 물고 있어
            // 요율 조회 경로가 이 행에서 종결된다(합의서 §4.2)
            'rows.*.contract_id' => ['required', 'integer', 'min:1'],
            // 소수 둘째 자리까지. 셋째 자리를 받으면 합계가 100.00 인지 판정할 수 없다
            'rows.*.share_ratio' => ['required', 'numeric', 'min:0', 'max:100', 'decimal:0,2'],
            'rows.*.start_date' => ['required', 'date_format:Y-m-d'],
            'rows.*.end_date' => ['nullable', 'date_format:Y-m-d', 'after_or_equal:rows.*.start_date'],
        ];
```
attributes:
```php
        return [
            'type' => '상품 구분',
            'id' => '상품',
            'lecture_ids' => '강의 선택',
            'rows' => '권리자 지분',
            'rows.*.rights_holder_id' => '권리자',
            'rows.*.contract_id' => '적용 계약',
            'rows.*.share_ratio' => '지분율',
            'rows.*.start_date' => '유효 시작일',
            'rows.*.end_date' => '유효 종료일',
        ];
```

## SalesStatRequest (extends FormRequest)
```php
        return [];
```

## SavedGroupRequest (extends FormRequest)
```php
        return [
            'name' => ['required', 'string', 'max:100'],
            'group_type' => ['required', 'string', 'in:'.UserGroup::TYPE_STATIC.','.UserGroup::TYPE_DYNAMIC],
            'description' => ['nullable', 'string', 'max:255'],
            'share_scope' => ['required', 'string', 'in:'.UserGroup::SHARE_ALL.','.UserGroup::SHARE_OWNER],
            // 목록에서 들고 온 조건. 이 화면에서 고치지 않으므로 값만 실어 보낸다
            'tags' => ['nullable', 'array'],
            'tag_join' => ['nullable', 'string'],
            'exclude_tags' => ['nullable', 'array'],
        ];
```

## SelectedIdsRequest (extends FormRequest)
```php
        return [
            'ids' => ['required', 'array', 'min:1'],
            'ids.*' => ['integer', 'min:1'],
        ];
```
attributes:
```php
        return [
            'ids' => '선택 항목',
        ];
```

## SettlementAdjustmentDecisionRequest (extends FormRequest)
- const `MIN_REJECT_REASON` = 2
```php
        return [
            'reject_reason' => ['required_if:decision,reject', 'min:'.self::MIN_REJECT_REASON],
        ];
```

## SettlementAdjustmentRequest (extends FormRequest)
```php
        return [
            'rights_holder_id' => ['required', 'integer', 'min:1'],
            'payee_id' => ['nullable', 'integer', 'min:1'],
            'contract_id' => ['nullable', 'integer', 'min:1'],
            'adjust_type' => ['required', Rule::in(array_keys(SettlementAdjustment::TYPE_LABELS))],
            // YYYY-MM 두 칸을 따로 받는다 — 하나로 합치면 전월 정정의 추적 축이 사라진다
            'origin_month' => ['required', 'string', 'regex:/^\d{4}-(0[1-9]|1[0-2])$/'],
            'applied_month' => ['required', 'string', 'regex:/^\d{4}-(0[1-9]|1[0-2])$/'],
            'reason_type' => ['required', Rule::in(array_keys(SettlementAdjustment::REASON_LABELS))],
            'explanation' => ['required', 'string', 'min:'.SettlementAdjustment::MIN_EXPLANATION, 'max:2000'],
            // 부호 그대로 받는다. 0 은 조정이 아니다
            'adjust_amount' => ['required', 'integer', 'not_in:0'],
            'vat_type' => ['required', Rule::in(array_keys(SettlementAdjustment::VAT_LABELS))],
            'income_category' => ['nullable', Rule::in(['BUSINESS', 'OTHER'])],
            'income_clause' => ['nullable', Rule::in(['C05', 'C15', 'C17', 'C19'])],
            'account_type' => ['required', Rule::in(array_keys(SettlementAdjustment::ACCOUNT_LABELS))],
            'origin_settlement_id' => ['nullable', 'integer', 'min:1'],
            'transfer_pair_key' => ['nullable', 'string', 'max:40'],
        ];
```
attributes:
```php
        return [
            'rights_holder_id' => '권리자',
            'payee_id' => '수취인',
            'adjust_type' => '조정 유형',
            'origin_month' => '원 발생 귀속월',
            'applied_month' => '반영월',
            'reason_type' => '조정 사유 구분',
            'explanation' => '소명 내용',
            'adjust_amount' => '조정 금액',
            'vat_type' => '과·면세 구분',
            'income_category' => '소득 구분',
            'income_clause' => '기타소득 호',
            'account_type' => '계정 구분',
            'origin_settlement_id' => '원 정산서',
        ];
```

## SettlementBoardCloseRequest (extends FormRequest)
```php
        return [];
```

## SettlementBoardRecalculateRequest (extends FormRequest)
```php
        return [];
```

## SettlementMemoRequest (extends FormRequest)
```php
        return [
            'rights_holder_id' => ['required', 'integer', 'min:1'],
            // 분할 없는 행은 수취인이 비어 있다 — 그때는 권리자 단위 메모다
            'payee_id' => ['nullable', 'integer', 'min:1'],
            'memo' => ['required', 'string', 'min:2', 'max:2000'],
        ];
```
attributes:
```php
        return [
            'rights_holder_id' => '권리자',
            'payee_id' => '수취인',
            'memo' => '검토 메모',
        ];
```

## SiteSettingRequest (extends FormRequest)
```php
        return [
            'site_name' => ['nullable', 'string', 'max:100'],
            'company_name' => ['nullable', 'string', 'max:100'],
            'ceo_name' => ['nullable', 'string', 'max:50'],
            'privacy_officer' => ['nullable', 'string', 'max:50'],
            'business_number' => ['nullable', 'string', 'max:30'],
            'corporate_number' => ['nullable', 'string', 'max:30'],
            'mail_order_number' => ['nullable', 'string', 'max:50'],
            'publisher_number' => ['nullable', 'string', 'max:50'],
            'edu_facility_number' => ['nullable', 'string', 'max:50'],
            'address' => ['nullable', 'string', 'max:255'],
            'tel' => ['nullable', 'string', 'max:30'],
            'cs_tel' => ['nullable', 'string', 'max:30'],
            'cs_hours' => ['nullable', 'string', 'max:100'],
            'email' => ['nullable', 'email', 'max:100'],
            'partnership_email' => ['nullable', 'email', 'max:100'],
            'copyright' => ['nullable', 'string', 'max:255'],
            'hosting_provider' => ['nullable', 'string', 'max:100'],
            'sns_naver' => ['nullable', 'string', 'max:255', 'not_regex:/^\s*(?:javascript|data|vbscript):/i'],
            'sns_youtube' => ['nullable', 'string', 'max:255', 'not_regex:/^\s*(?:javascript|data|vbscript):/i'],
            'sns_instagram' => ['nullable', 'string', 'max:255', 'not_regex:/^\s*(?:javascript|data|vbscript):/i'],
            'logo' => ['nullable', 'image', 'mimes:jpg,jpeg,png,webp,gif', 'max:5120', new RealFileType(['jpg','jpeg','png','webp','gif'])],
            'favicon' => ['nullable', 'file', 'mimes:png,ico,jpg,jpeg,webp', 'max:2048', new RealFileType(['png','ico','jpg','jpeg','webp'])],
            'delete_logo' => ['nullable', 'boolean'],
            'delete_favicon' => ['nullable', 'boolean'],
        ] + $this->settingRules();
```
attributes:
```php
        return [
            'email' => '대표 이메일',
            'corporate_number' => '법인등록번호',
            'publisher_number' => '출판사등록번호',
            'partnership_email' => '제휴 수신 메일',
            'package_delivery_notice' => '패키지 상세 배송 안내',
            'virtual_account_valid_hours' => '가상계좌 입금 기한',
            'pass_review_min_chars' => '합격 수기 최소 글자 수',
            'pass_review_keep_months' => '합격 수기 게시 유지 기간',
            'pass_review_clawback_rule' => '합격 수기 회수 조건',
            'logo' => '로고',
            'welcome_point' => '신규 가입 축하금',
            'free_point_expire_years' => '가입 축하금 유효기간',
            'paid_point_expire_years' => '포인트 유효기간',
        ];
```

## StripBannerReorderRequest (extends FormRequest)
```php
        return [
            'orders' => ['required', 'array', 'min:1'],
            'orders.*.id' => ['required', 'integer', 'distinct'],
            'orders.*.sort_order' => ['required', 'integer', 'min:0'],
            // 저장 뒤 보던 위치 필터로 돌아가기용
            'position' => ['nullable', 'string', Rule::in(array_keys(Banner::STRIP_POSITIONS))],
        ];
```

## StripBannerRequest (extends FormRequest)
```php
        return [
            'position' => ['required', 'string', Rule::in(array_keys(Banner::STRIP_POSITIONS))],
            'target' => ['required', 'string', Rule::in(array_keys(Banner::TARGETS))],
            // 넘치는 문구를 말줄임으로 감추지 않고 입력 단계에서 막는다(④)
            'title' => ['required', 'string', 'max:'.Banner::STRIP_TEXT_MAX],
            'bg_color' => ['required', 'string', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'text_color' => ['required', 'string', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'link_url' => ['nullable', 'string', 'max:500', new DisplayLinkUrl],
            'link_blank' => ['nullable', 'boolean'],
            // 둘 다 해제할 수 없다 — 최소 1개(⑤)
            'devices' => ['required', 'array', 'min:1'],
            'devices.*' => ['string', Rule::in(['pc', 'mobile'])],
            'always' => ['nullable', 'boolean'],
            'start_at' => ['exclude_if:always,1', 'required', 'date'],
            'end_at' => ['exclude_if:always,1', 'required', 'date', 'after_or_equal:start_at'],
            'is_active' => ['required', 'boolean'],
        ];
```
attributes:
```php
        return [
            'position' => '노출 위치',
            'target' => '노출 대상',
            'title' => '노출 문구',
            'bg_color' => '배경색',
            'text_color' => '글자색',
            'link_url' => '클릭 시 이동 URL',
            'devices' => '노출 기기',
            'start_at' => '노출 시작',
            'end_at' => '노출 종료',
            'is_active' => '노출 여부',
        ];
```

## StudyQnaProcessRequest (extends FormRequest)
```php
        return [
            'action' => ['required', Rule::in(['answer', 'escalate'])],
            'answer_content' => ['nullable', 'required_if:action,answer', 'string', 'min:10'],
            'is_public_qna' => ['nullable', 'boolean'],
            // 답변 알림 — 보내지 않으면 기본 ON(설계서)
            'notify' => ['nullable', 'boolean'],
        ];
```
attributes:
```php
        return ['answer_content' => '답변 본문'];
```

## SupplierRequest (extends FormRequest)
```php
        return [
            'name' => ['required', 'string', 'max:100'],
            // 사업자등록번호 10자리 — 13자리(주민번호)는 받지 않는다
            'business_no' => ['required', 'string', 'digits:10'],
            'ceo_name' => ['nullable', 'string', 'max:50'],
            'open_date' => ['nullable', 'date_format:Y-m-d'],
            'bank_name' => ['nullable', 'string', 'max:50'],
            'account_no' => ['nullable', 'string', 'max:50', 'regex:/^[0-9-]+$/'],
            'account_holder' => ['nullable', 'string', 'max:50'],
            'settlement_terms' => ['nullable', 'string', 'max:100'],
            'contact_email' => ['nullable', 'email', 'max:100'],
        ];
```
attributes:
```php
        return [
            'name' => '상호', 'business_no' => '사업자등록번호', 'ceo_name' => '대표자명', 'open_date' => '개업일자', 'payee_tax_type' => '과세유형',
            'bank_name' => '은행', 'account_no' => '계좌번호', 'account_holder' => '예금주', 'settlement_terms' => '정산 조건', 'contact_email' => '담당 메일',
        ];
```

## TermRequest (extends FormRequest)
- const `ACTION_DRAFT` = 'draft'
- const `ACTION_CONFIRM` = 'confirm'
```php
        $confirm = $this->input('action') === self::ACTION_CONFIRM;

        return [
            'action' => ['required', 'string', Rule::in([self::ACTION_DRAFT, self::ACTION_CONFIRM])],
            // 종류는 처음 만들 때만 받는다 — 작성중 버전을 고칠 때는 그 버전의 종류를 쓴다
            'type' => [Rule::requiredIf(fn () => $this->isMethod('post')), 'nullable', 'string', Rule::in(array_keys(Term::CODES))],
            'revision' => ['nullable', 'string', Rule::in(array_keys(Term::REVISIONS))],
            'title' => ['required', 'string', 'max:255'],
            'content' => ['required', 'string'],
            // 공시 일자 · 시행 일자는 분리 입력. 시행일이 공시일보다 빠르면 저장을 막는다(기준 미달은 경고만)
            'notice_date' => [Rule::requiredIf($confirm), 'nullable', 'date'],
            'effective_date' => [Rule::requiredIf($confirm), 'nullable', 'date', 'after_or_equal:notice_date'],
            'is_unfavorable' => ['nullable', 'boolean'],
            // 사용자 공지 · 재동의 안내의 요약문으로 다시 쓴다(설계서 ③)
            'change_reason' => [Rule::requiredIf($confirm), 'nullable', 'string', 'max:500'],
        ];
```
attributes:
```php
        return [
            'action' => '저장 방식',
            'type' => '약관 종류',
            'revision' => '개정 유형',
            'title' => '제목',
            'content' => '본문',
            'notice_date' => '공시 일자',
            'effective_date' => '시행 일자',
            'is_unfavorable' => '불리한 개정',
            'change_reason' => '개정 사유',
        ];
```

## VerificationIpExceptionRequest (extends FormRequest)
- const `MODES` = ['single' => '단일 IP', 'cidr' => 'IP 대역(CIDR)']
- const `CIDR_MIN_PREFIX` = 16
```php
        return [
            'mode' => ['required', 'string', Rule::in(array_keys(self::MODES))],
            'ip' => ['required', 'string', 'max:45', $this->formatRule()],
            'memo' => ['required', 'string', 'max:100'],
        ];
```
attributes:
```php
        return [
            'mode' => '등록 방식',
            'ip' => 'IP / 대역',
            'memo' => '메모',
        ];
```

## VerifyCapResetRequest (extends FormRequest)
```php
        return [
            'user_id' => ['required', 'integer', 'min:1'],
            'reason' => ['required', 'string', 'max:200'],
        ];
```
attributes:
```php
        return [
            'user_id' => '대상 계정',
            'reason' => '초기화 사유',
        ];
```

## VerifySettingRequest (extends FormRequest)
- const `LIMIT_MIN` = 1
- const `LIMIT_MAX` = 99
- const `TTL_MIN` = 5
- const `TTL_MAX` = 60
```php
        $limit = ['required', 'integer', 'min:'.self::LIMIT_MIN, 'max:'.self::LIMIT_MAX];

        return [
            'verify_daily_limit' => $limit,
            'verify_ip_daily_limit' => $limit,
            'verify_session_ttl_user_min' => ['required', 'integer', 'min:'.self::TTL_MIN, 'max:'.self::TTL_MAX],
        ];
```
attributes:
```php
        return [
            'verify_daily_limit' => '계정 기준 한도',
            'verify_ip_daily_limit' => 'IP 기준 한도',
            'verify_session_ttl_user_min' => '인증 유효 시간',
        ];
```

## WinnerRequest (extends FormRequest)
```php
        return [
            'promotion_id' => ['required', 'integer'],
            // 목록 · 사용자 화면에 같은 이름으로 보인다(② 최대 100자)
            'title' => ['required', 'string', 'max:100'],
            'content' => ['nullable', 'string'],
            // 발표 시점(④) — 즉시 / 예약 2택
            'publish_mode' => ['required', Rule::in(['immediate', 'scheduled'])],
            'published_at' => ['nullable', 'required_if:publish_mode,scheduled', 'date'],
            // 명단(③) — 엑셀 또는 직접 추가. 등록 때 둘 다 비면 서비스가 막는다
            'winners_text' => ['nullable', 'string', 'max:200000'],
            // 확장자 · MIME · 실제 바이트를 같은 목록으로 본다(CLAUDE.md 10절)
            'winners_file' => ['nullable', 'file', 'max:2048', 'extensions:xlsx', 'mimes:xlsx', new RealFileType(['xlsx'])],
        ];
```
attributes:
```php
        return [
            'promotion_id' => '연결 이벤트',
            'title' => '제목',
            'publish_mode' => '발표 시점',
            'published_at' => '예약 발행 시각',
            'winners_text' => '당첨자 명단',
            'winners_file' => '명단 엑셀',
        ];
```

