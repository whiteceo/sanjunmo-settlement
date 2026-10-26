# 관리자 라우트 색인

권한 단위 = 라우트 이름 접미사 → AdminPermissionService::SUFFIX_PERMISSIONS. 메뉴는 라우트 이름의 목록형(…index)으로 정규화해 admin_menus 와 맞춘다.

| 줄 | 메서드 | URL | 라우트 이름 | 컨트롤러@메서드 | 권한 | 주석 |
|---|---|---|---|---|---|---|
| 111 | GET | `/{admin}` | `admin.` | closure | 메뉴 권한 밖(로그인만) | 관리자 루트 접근 시 대시보드로 리다이렉트 |
| 114 | GET | `/{admin}/login` | `admin.login` | AuthController@loginForm | 메뉴 권한 밖(로그인만) | 로그인 / 로그아웃 |
| 117 | POST | `/{admin}/login` | `admin.login.post` | AuthController@login | 메뉴 권한 밖(로그인만) | 비밀번호 추측을 요청 수로 막는다(코드 점검 발견 8). 계정 잠금(계정당 실패 횟수)은 아이디를 바꿔 가며 시도하는 공격을 막지 못한다 — 같은 출처에서 분당 10회로 끊는다 |
| 118 | POST | `/{admin}/logout` | `admin.logout` | AuthController@logout | 메뉴 권한 밖(로그인만) |  |
| 125 | GET | `/{admin}/find-id` | `admin.find-id.form` | FindIdController@form | 메뉴 권한 밖(로그인만) |  |
| 126 | POST | `/{admin}/find-id/send-code` | `admin.find-id.send-code` | FindIdController@sendCode | 메뉴 권한 밖(로그인만) |  |
| 127 | POST | `/{admin}/find-id/verify-code` | `admin.find-id.verify-code` | FindIdController@verifyCode | 메뉴 권한 밖(로그인만) |  |
| 129 | POST | `/{admin}/find-id/to-login` | `admin.find-id.to-login` | FindIdController@toLogin | 메뉴 권한 밖(로그인만) | 아이디 원문을 URL 에 싣지 않기 위해 POST 로 받는다 |
| 130 | POST | `/{admin}/find-id/to-password-reset` | `admin.find-id.to-password-reset` | FindIdController@toPasswordReset | 메뉴 권한 밖(로그인만) |  |
| 137 | GET | `/{admin}/password-reset` | `admin.password-reset.form` | PasswordResetController@form | 메뉴 권한 밖(로그인만) |  |
| 139 | POST | `/{admin}/password-reset/from-lock` | `admin.password-reset.from-lock` | PasswordResetController@fromLock | 메뉴 권한 밖(로그인만) | 잠금 안내 팝업(P1) 진입 — 아이디를 URL 에 싣지 않기 위해 POST 로 받는다 |
| 140 | POST | `/{admin}/password-reset/send-code` | `admin.password-reset.send-code` | PasswordResetController@sendCode | 메뉴 권한 밖(로그인만) |  |
| 141 | POST | `/{admin}/password-reset/verify-code` | `admin.password-reset.verify-code` | PasswordResetController@verifyCode | 메뉴 권한 밖(로그인만) |  |
| 143 | POST | `/{admin}/password-reset/sms/send-code` | `admin.password-reset.sms.send-code` | PasswordResetController@sendSmsCode | 메뉴 권한 밖(로그인만) | 휴대전화 2차 인증 (ADMN-LOGIN-003-b) |
| 144 | POST | `/{admin}/password-reset/sms/verify-code` | `admin.password-reset.sms.verify-code` | PasswordResetController@verifySmsCode | 메뉴 권한 밖(로그인만) |  |
| 145 | POST | `/{admin}/password-reset` | `admin.password-reset.store` | PasswordResetController@reset | 메뉴 권한 밖(로그인만) |  |
| 150 | PUT | `/{admin}/profile` | `admin.profile.update` | ProfileController@update | 메뉴 권한 밖(로그인만) |  |
| 155 | POST | `/{admin}/session/extend` | `admin.session.extend` | AuthController@extendSession | 메뉴 권한 밖(로그인만) | 세션 연장 (ADMN-LOGIN-001 :289) — 만료 안내 레이어의 [연장] 전용. admin.auth 가 이미 활동 시각을 갱신하므로 이 요청 자체가 연장이다 |
| 161 | GET | `/{admin}/password-change` | `admin.password-change.form` | PasswordChangeController@form | 메뉴 권한 밖(로그인만) | 본인 비밀번호 변경 (ADMN-LOGIN-B · 설계서 :45). 90일이 지난 계정은 미들웨어가 이 두 라우트만 통과시킨다 — 권한 그룹 밖에 둔다. 메뉴 권한으로 판정하면 변경할 경로까지 막힌다 |
| 163 | PUT | `/{admin}/password-change` | `admin.password-change.update` | PasswordChangeController@update | 메뉴 권한 밖(로그인만) |  |
| 167 | GET | `/{admin}/guide/style` | `admin.guide.style` | closure | 메뉴 권한 밖(로그인만) | 스타일가이드 (독립 페이지, 권한 체크 불필요) |
| 171 | POST | `/{admin}/editor/upload` | `admin.editor.upload` | EditorController@upload | 메뉴 권한 밖(로그인만) | 에디터 이미지 업로드 |
| 178 | GET | `/{admin}/attachments/{attachment}/download` | `admin.attachments.download` | AttachmentController@download | 메뉴 권한 밖(로그인만) | 첨부파일 다운로드 (SEC-2) — private 디스크의 유일한 통로. AdminPermissionMiddleware 를 걸지 않는다. '첨부파일' 메뉴가 없어서 라우트명으로는 판정할 수 없고, 첨부가 매달린 대상의 메뉴 권한을 AttachmentController 가 직접 묻는다 |
| 183 | POST | `/{admin}/masking/unmask` | `admin.masking.unmask` | MaskingController@unmask | 메뉴 권한 밖(로그인만) | 마스킹 해제 (C-11-1) — 전 화면 공용이라 특정 메뉴 권한에 귀속되지 않는다. 판정은 MaskingService::canUnmask() 하나가 한다 |
| 187 | GET | `/{admin}/dashboard` | `admin.dashboard` | DashboardController@index | 메뉴 권한 밖(로그인만) | 대시보드 (메뉴 권한 대상 아님 — 로그인 공통 진입 화면) |
| 196 | GET | `/{admin}/api/instructors` | `admin.api.instructors` | InstructorController@apiList | 메뉴 권한 밖(로그인만) |  |
| 199 | GET | `/{admin}/api/lectures` | `admin.api.lectures` | LectureController@apiList | 메뉴 권한 밖(로그인만) | 강좌관리 팝업용 |
| 200 | GET | `/{admin}/api/books` | `admin.api.books` | BookController@apiList | 메뉴 권한 밖(로그인만) |  |
| 201 | GET | `/{admin}/api/courses` | `admin.api.courses` | CourseController@apiList | 메뉴 권한 밖(로그인만) |  |
| 213 | GET | `/{admin}/admin-users` | `admin.admin-users.index` | AdminUserController@index | can_view |  |
| 214 | GET | `/{admin}/admin-users/create` | `admin.admin-users.create` | AdminUserController@create | can_create |  |
| 215 | POST | `/{admin}/admin-users` | `admin.admin-users.store` | AdminUserController@store | can_create |  |
| 216 | GET | `/{admin}/admin-users/{adminUser}/edit` | `admin.admin-users.edit` | AdminUserController@edit | can_update |  |
| 217 | PUT | `/{admin}/admin-users/{adminUser}` | `admin.admin-users.update` | AdminUserController@update | can_update |  |
| 221 | POST | `/{admin}/admin-users/{adminUser}/reset-verify-cap` | `admin.admin-users.reset-verify-cap` | AdminUserController@resetVerifyCap | can_update | 삭제 경로는 두지 않는다 — 계정은 정지(비활성화)로만 막는다. 지우면 과거 로그의 '누가 했는가'가 끊긴다(설계서 ADMN-CONF-005 ⑤) 인증번호 발송 횟수 수동 초기화 (설계서 :266). 계정 수정과 별개 요청이다 — 저장과 묶으면 다른 항목의 유효성 오류에 함께 막혀 복구가 늦어진다 |
| 228 | GET | `/{admin}/admin-roles` | `admin.admin-roles.index` | AdminRoleController@index | can_view |  |
| 229 | GET | `/{admin}/admin-roles/{adminRole}/edit` | `admin.admin-roles.edit` | AdminRoleController@edit | can_update |  |
| 230 | PUT | `/{admin}/admin-roles/{adminRole}` | `admin.admin-roles.update` | AdminRoleController@update | can_update |  |
| 236 | GET | `/{admin}/admin-menus` | `admin.admin-menus.index` | AdminMenuController@index | can_view |  |
| 237 | GET | `/{admin}/admin-menus/create` | `admin.admin-menus.create` | AdminMenuController@create | can_create |  |
| 238 | POST | `/{admin}/admin-menus` | `admin.admin-menus.store` | AdminMenuController@store | can_create |  |
| 239 | GET | `/{admin}/admin-menus/{adminMenu}/edit` | `admin.admin-menus.edit` | AdminMenuController@edit | can_update |  |
| 240 | PUT | `/{admin}/admin-menus/{adminMenu}` | `admin.admin-menus.update` | AdminMenuController@update | can_update |  |
| 241 | DELETE | `/{admin}/admin-menus/{adminMenu}` | `admin.admin-menus.destroy` | AdminMenuController@destroy | can_delete |  |
| 244 | GET | `/{admin}/dev-progress` | `admin.dev-progress.index` | DevProgressController@index | can_view | 개발 진행률 (임시 — 운영 오픈 전 삭제). git 커밋에서 만든 파일을 읽기만 한다 |
| 257 | GET | `/{admin}/qa-checklist` | `admin.qa-checklist.index` | QaChecklistController@index | can_view |  |
| 259 | GET | `/{admin}/qa-checklist/download` | `admin.qa-checklist.download` | QaChecklistController@download | can_download | 정적 경로를 파라미터 경로보다 위에 둔다(팀 규칙 3절) |
| 261 | GET | `/{admin}/qa-checklist/histories` | `admin.qa-checklist.histories.index` | QaChecklistController@histories | can_view | 항목 이력 — 묶음 · 번호는 쿼리로 받는다(번호는 1 · 2-3 처럼 id 가 아니다) |
| 262 | POST | `/{admin}/qa-checklist/checklists` | `admin.qa-checklist.checklists.store` | QaChecklistController@storeChecklist | can_create |  |
| 263 | POST | `/{admin}/qa-checklist/agent-results` | `admin.qa-checklist.agent-results.store` | QaChecklistController@storeAgentResults | can_create |  |
| 265 | POST | `/{admin}/qa-checklist/fix-logs` | `admin.qa-checklist.fix-logs.store` | QaChecklistController@storeFixLog | can_create | 개발 조치 — 목록 · 이력 화면이 같은 라우트를 쓴다. 추가만 하므로 update · destroy 를 두지 않는다 |
| 267 | POST | `/{admin}/qa-checklist/fix-uploads` | `admin.qa-checklist.fix-uploads.store` | QaChecklistController@storeFixUpload | can_create | 조치 일괄 업로드 — 올리면 미리보기(저장 없음) · [반영] 을 눌러야 쌓인다 |
| 268 | POST | `/{admin}/qa-checklist/fix-uploads/confirm` | `admin.qa-checklist.fix-uploads.confirm.store` | QaChecklistController@confirmFixUpload | can_create |  |
| 277 | GET | `/{admin}/qa-checklist/my` | `admin.qa-checklist.my.index` | QaTesterController@index | can_view |  |
| 280 | GET | `/{admin}/qa-checklist/my/shots/{shot}` | `admin.qa-checklist.my.shots.show` | QaTesterController@showShot | can_view | 캡처 보기 — 파일은 비공개 디스크라 이 라우트로만 나간다. 관리 화면(이력 · 이슈 썸네일)도 이 라우트를 쓴다(최고관리자는 전부 통과) |
| 284 | POST | `/{admin}/qa-checklist/my/results` | `admin.qa-checklist.my.results.store` | QaTesterController@storeResult | can_create | 결과는 추가만 한다 — update · destroy 를 두지 않는다 |
| 285 | POST | `/{admin}/qa-checklist/my/findings` | `admin.qa-checklist.my.findings.store` | QaTesterController@storeFinding | can_create |  |
| 296 | GET | `/{admin}/qa-results` | `admin.qa-results.index` | QaResultController@index | can_view |  |
| 297 | GET | `/{admin}/qa-results/download` | `admin.qa-results.download` | QaResultController@download | can_download |  |
| 298 | POST | `/{admin}/qa-results` | `admin.qa-results.store` | QaResultController@store | can_create |  |
| 305 | GET | `/{admin}/admin-logs` | `admin.admin-logs.index` | AdminLogController@index | can_view |  |
| 306 | GET | `/{admin}/admin-logs/download` | `admin.admin-logs.download` | AdminLogController@download | can_download |  |
| 307 | GET | `/{admin}/admin-logs/{adminLog}` | `admin.admin-logs.show` | AdminLogController@show | can_view |  |
| 313 | GET | `/{admin}/login-logs` | `admin.login-logs.index` | LoginLogController@index | can_view |  |
| 315 | GET | `/{admin}/login-logs/download` | `admin.login-logs.download` | LoginLogController@download | can_download | download 를 {loginLog} 보다 위에 둔다. 아래로 내리면 파라미터로 먹힌다 |
| 316 | GET | `/{admin}/login-logs/{loginLog}` | `admin.login-logs.show` | LoginLogController@show | can_view |  |
| 322 | GET | `/{admin}/categories` | `admin.categories.index` | CategoryController@index | can_view |  |
| 323 | GET | `/{admin}/categories/download` | `admin.categories.download` | CategoryController@download | can_download |  |
| 324 | GET | `/{admin}/categories/create` | `admin.categories.create` | CategoryController@create | can_create |  |
| 327 | POST | `/{admin}/categories/sort` | `admin.categories.sort.update` | CategoryController@sort | can_update | 정렬 저장 — {category} 보다 먼저 둔다. 뒤에 두면 'sort' 가 id 로 잡힌다. 이름은 하위 자원 + 표준 접미사(sort.update → 카테고리 메뉴 수정 권한). 'sort' 만 쓰면 매핑 밖이라 최고 관리자 외 늘 차단된다 |
| 328 | POST | `/{admin}/categories` | `admin.categories.store` | CategoryController@store | can_create |  |
| 329 | GET | `/{admin}/categories/{category}/edit` | `admin.categories.edit` | CategoryController@edit | can_update |  |
| 330 | PUT | `/{admin}/categories/{category}` | `admin.categories.update` | CategoryController@update | can_update |  |
| 331 | DELETE | `/{admin}/categories/{category}` | `admin.categories.destroy` | CategoryController@destroy | can_delete |  |
| 337 | GET | `/{admin}/instructors` | `admin.instructors.index` | InstructorController@index | can_view |  |
| 338 | GET | `/{admin}/instructors/download` | `admin.instructors.download` | InstructorController@download | can_download |  |
| 339 | GET | `/{admin}/instructors/create` | `admin.instructors.create` | InstructorController@create | can_create |  |
| 340 | POST | `/{admin}/instructors` | `admin.instructors.store` | InstructorController@store | can_create |  |
| 341 | GET | `/{admin}/instructors/{instructor}/edit` | `admin.instructors.edit` | InstructorController@edit | can_update |  |
| 342 | PUT | `/{admin}/instructors/{instructor}` | `admin.instructors.update` | InstructorController@update | can_update |  |
| 350 | GET | `/{admin}/lectures` | `admin.lectures.index` | LectureController@index | can_view |  |
| 351 | GET | `/{admin}/lectures/download` | `admin.lectures.download` | LectureController@download | can_download |  |
| 352 | POST | `/{admin}/lectures/download-selected` | `admin.lectures.selected.download` | LectureController@downloadSelected | can_download |  |
| 353 | GET | `/{admin}/lectures/create` | `admin.lectures.create` | LectureController@create | can_create |  |
| 357 | GET | `/{admin}/lectures/vod-info` | `admin.lectures.vod-info.index` | LectureController@vodInfo | can_view | OVP 트랜스코딩 조회 — [유효성 검사] · [VOD 메타에서 가져오기] 공용 (ADMN-PROD-002-S1 ③ · ④). 하위 자원 + 표준 접미사(index → can_view). 외부 키는 서버에만 두고 화면은 이 경로만 부른다. 신규 등록 중에도 눌러야 해서 {lecture} 를 받지 않는다 |
| 360 | GET | `/{admin}/lectures/duration-impact` | `admin.lectures.duration-impact.index` | LectureController@durationImpact | can_view | 재생시간 변경 영향 조회 (ADMN-PROD-002-S1 ④) — 저장 전에 미달 전환 인원을 묻는다. vod-info 와 같은 이유로 하위 자원 + 표준 접미사(index → can_view) |
| 361 | POST | `/{admin}/lectures` | `admin.lectures.store` | LectureController@store | can_create |  |
| 362 | GET | `/{admin}/lectures/{lecture}/edit` | `admin.lectures.edit` | LectureController@edit | can_update |  |
| 363 | PUT | `/{admin}/lectures/{lecture}` | `admin.lectures.update` | LectureController@update | can_update |  |
| 364 | DELETE | `/{admin}/lectures/{lecture}` | `admin.lectures.destroy` | LectureController@destroy | can_delete |  |
| 365 | POST | `/{admin}/lectures/{lecture}/copy` | `admin.lectures.copy.store` | LectureController@copy | can_create |  |
| 373 | GET | `/{admin}/books` | `admin.books.index` | BookController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 374 | GET | `/{admin}/books/create` | `admin.books.create` | BookController@create | can_create |  |
| 375 | GET | `/{admin}/books/download` | `admin.books.download` | BookController@download | can_download |  |
| 376 | POST | `/{admin}/books/download-selected` | `admin.books.selected.download` | BookController@downloadSelected | can_download |  |
| 377 | POST | `/{admin}/books` | `admin.books.store` | BookController@store | can_create |  |
| 380 | GET | `/{admin}/books/{book}/edit` | `admin.books.edit` | BookController@edit | can_update | 파라미터 경로 |
| 381 | PUT | `/{admin}/books/{book}` | `admin.books.update` | BookController@update | can_update |  |
| 382 | DELETE | `/{admin}/books/{book}` | `admin.books.destroy` | BookController@destroy | can_delete |  |
| 383 | POST | `/{admin}/books/{book}/copy` | `admin.books.copy.store` | BookController@copy | can_create |  |
| 385 | PUT | `/{admin}/books/{book}/stock` | `admin.books.stock.update` | BookController@stockAdjust | can_update | 재고 조정 (ADMN-PROD-004-S1 ③) — 재고를 바꾸는 쓰기라 접미사를 update 로 둔다 |
| 387 | POST | `/{admin}/books/{book}/stop-selling` | `admin.books.stop.update` | BookController@stopSelling | can_update | 판매중지 — 전시 상태를 바꾸는 쓰기라 접미사를 update 로 둔다(강좌 · 패키지와 같다) |
| 394 | GET | `/{admin}/courses` | `admin.courses.index` | CourseController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 395 | GET | `/{admin}/courses/download` | `admin.courses.download` | CourseController@download | can_download |  |
| 396 | GET | `/{admin}/courses/create` | `admin.courses.create` | CourseController@create | can_create |  |
| 397 | POST | `/{admin}/courses` | `admin.courses.store` | CourseController@store | can_create |  |
| 399 | GET | `/{admin}/courses/{course}/edit` | `admin.courses.edit` | CourseController@edit | can_update |  |
| 400 | PUT | `/{admin}/courses/{course}` | `admin.courses.update` | CourseController@update | can_update |  |
| 401 | DELETE | `/{admin}/courses/{course}` | `admin.courses.destroy` | CourseController@destroy | can_delete |  |
| 402 | POST | `/{admin}/courses/{course}/copy` | `admin.courses.copy.store` | CourseController@copy | can_create |  |
| 405 | GET | `/{admin}/courses/{course}/curriculum` | `admin.courses.curriculum.index` | CourseController@curriculum | can_view | 커리큘럼 구성 (ADMN-PROD-003-S1) — 하위 자원 + 표준 접미사. 조회는 can_view, 저장은 can_update 로 잡힌다 |
| 407 | PUT | `/{admin}/courses/{course}/curriculum` | `admin.courses.curriculum.update` | CourseController@curriculumUpdate | can_update |  |
| 411 | POST | `/{admin}/courses/{course}/stop-selling` | `admin.courses.stop.update` | CourseController@stopSelling | can_update | 판매중지 — 전시 상태를 바꾸는 쓰기라 접미사를 update 로 둔다 (설계서 :408) |
| 419 | GET | `/{admin}/goods` | `admin.goods.index` | GoodsController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 420 | GET | `/{admin}/goods/download` | `admin.goods.download` | GoodsController@download | can_download |  |
| 421 | GET | `/{admin}/goods/create` | `admin.goods.create` | GoodsController@create | can_create |  |
| 422 | POST | `/{admin}/goods` | `admin.goods.store` | GoodsController@store | can_create |  |
| 424 | POST | `/{admin}/goods/bulk-stop` | `admin.goods.bulk-stop.update` | GoodsController@bulkStop | can_update | 일괄 판매중지 — 전시 상태를 바꾸는 쓰기라 접미사를 update 로 둔다 |
| 426 | GET | `/{admin}/goods/{goods}/edit` | `admin.goods.edit` | GoodsController@edit | can_update |  |
| 427 | PUT | `/{admin}/goods/{goods}` | `admin.goods.update` | GoodsController@update | can_update |  |
| 428 | POST | `/{admin}/goods/{goods}/stop-selling` | `admin.goods.stop.update` | GoodsController@stopSelling | can_update |  |
| 430 | PUT | `/{admin}/goods/{goods}/stock` | `admin.goods.stock.update` | GoodsController@stockAdjust | can_update | 재고 조정 — 증감 + 사유. goods_stock_logs 에 전건 적재 (설계서 ADMN-PROD-007-S1 ③) |
| 438 | GET | `/{admin}/book-supply` | `admin.book-supply.index` | BookSupplyController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 439 | GET | `/{admin}/book-supply/download` | `admin.book-supply.download` | BookSupplyController@download | can_download |  |
| 440 | GET | `/{admin}/book-supply/create` | `admin.book-supply.create` | BookSupplyController@create | can_create |  |
| 441 | POST | `/{admin}/book-supply` | `admin.book-supply.store` | BookSupplyController@store | can_create |  |
| 443 | POST | `/{admin}/book-supply/suppliers` | `admin.book-supply.suppliers.store` | SupplierController@store | can_create | 매입처 등록(탭 ③) — 국세청 확인 전 임시 등록 |
| 445 | GET | `/{admin}/book-supply/{book}/edit` | `admin.book-supply.edit` | BookSupplyController@edit | can_update |  |
| 446 | PUT | `/{admin}/book-supply/{book}` | `admin.book-supply.update` | BookSupplyController@update | can_update |  |
| 448 | PUT | `/{admin}/book-supply/{book}/reissue` | `admin.book-supply.reissue.update` | BookSupplyController@reissue | can_update | 신규 SKU 발급 — 기존 SKU 판매중지(새 등록은 교재 관리). 교재를 고치는 행위라 수정 권한으로 판정한다 |
| 450 | PUT | `/{admin}/book-supply/{book}/prices` | `admin.book-supply.prices.update` | BookSupplyController@storePrice | can_update | 정가 변경 등록 — 기존 행을 닫고 새 행을 더한다. 교재 정가를 바꾸므로 수정 권한 |
| 457 | GET | `/{admin}/packages` | `admin.packages.index` | PackageController@index | can_view |  |
| 459 | GET | `/{admin}/packages/download` | `admin.packages.download` | PackageController@download | can_download | 패키지 · 구성품 배분가 엑셀 — 가격이 들어가 반출(download) 권한 · 사유를 받는다 |
| 460 | GET | `/{admin}/packages/create` | `admin.packages.create` | PackageController@create | can_create |  |
| 462 | GET | `/{admin}/packages/books` | `admin.packages.books.index` | PackageController@books | can_view | 새로 고른 교재의 저자 · ISBN · 정산 경로 · 배송 조건(폼 배분표 · 장바구니 미리보기) |
| 463 | POST | `/{admin}/packages` | `admin.packages.store` | PackageController@store | can_create |  |
| 465 | POST | `/{admin}/packages/preview` | `admin.packages.preview.store` | PackageController@previewNew | can_create | [미리보기] — 저장하지 않고 폼 값으로 프론트 상세를 그린다. 등록 화면은 등록 권한, 수정 화면은 수정 권한 |
| 466 | MATCH | `/{admin}/packages/{package}/preview` | `admin.packages.preview.update` | PackageController@previewSaved | can_update |  |
| 468 | GET | `/{admin}/packages/{package}/edit` | `admin.packages.edit` | PackageController@edit | can_update |  |
| 469 | PUT | `/{admin}/packages/{package}` | `admin.packages.update` | PackageController@update | can_update |  |
| 470 | DELETE | `/{admin}/packages/{package}` | `admin.packages.destroy` | PackageController@destroy | can_delete |  |
| 471 | POST | `/{admin}/packages/{package}/copy` | `admin.packages.copy.store` | PackageController@copy | can_create |  |
| 473 | POST | `/{admin}/packages/{package}/stop-selling` | `admin.packages.stop.update` | PackageController@stopSelling | can_update | 판매중지 — 전시 상태를 바꾸는 쓰기라 접미사를 update 로 둔다(강좌와 같다) |
| 483 | GET | `/{admin}/rights-holders/milestones` | `admin.rights-holders.milestones.index` | MilestoneReviewController@index | can_view |  |
| 485 | PUT | `/{admin}/rights-holders/milestones` | `admin.rights-holders.milestones.update` | MilestoneReviewController@update | can_update | 검수 승인 · 반려 — 7단계 정산 인입을 열기 때문에 can_update 다 |
| 493 | GET | `/{admin}/rights-holders` | `admin.rights-holders.index` | RightsHolderController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 494 | GET | `/{admin}/rights-holders/create` | `admin.rights-holders.create` | RightsHolderController@create | can_create |  |
| 495 | GET | `/{admin}/rights-holders/download` | `admin.rights-holders.download` | RightsHolderController@download | can_download |  |
| 496 | POST | `/{admin}/rights-holders/status-sync` | `admin.rights-holders.status-sync` | RightsHolderController@statusSync | can_update |  |
| 497 | POST | `/{admin}/rights-holders` | `admin.rights-holders.store` | RightsHolderController@store | can_create |  |
| 499 | GET | `/{admin}/rights-holders/{rightsHolder}/contracts` | `admin.rights-holders.contracts` | RightsHolderController@contracts | can_view |  |
| 502 | GET | `/{admin}/rights-holders/{rightsHolder}/contracts/create` | `admin.rights-holders.contracts.create` | RightsHolderContractController@create | can_create | 계약 상세 — 권한은 상위 메뉴(권리자 계약 원장)를 따른다 |
| 503 | POST | `/{admin}/rights-holders/{rightsHolder}/contracts` | `admin.rights-holders.contracts.store` | RightsHolderContractController@store | can_create |  |
| 504 | GET | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/edit` | `admin.rights-holders.contracts.edit` | RightsHolderContractController@edit | can_update |  |
| 507 | GET | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}` | `admin.rights-holders.contracts.show` | RightsHolderContractController@show | can_view | 읽기 전용 열람 — edit 와 같은 Blade 를 쓰고 입력을 잠근다. 접미사 show 라 can_view 로 판정된다 (edit 는 can_update 라 조회 권한만 있는 담당자가 계약 조건을 열 수 없었다) |
| 508 | PUT | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}` | `admin.rights-holders.contracts.update` | RightsHolderContractController@update | can_update |  |
| 509 | POST | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/memos` | `admin.rights-holders.contracts.memos.store` | RightsHolderContractController@storeMemo | can_create |  |
| 511 | POST | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/book-royalties` | `admin.rights-holders.contracts.book-royalties.store` | RightsHolderContractController@storeBookRoyalty | can_create | 교재 인세 저서 원장 — 출간 전 저서는 SKU 없이 임시코드로 먼저 등록한다 |
| 512 | PUT | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/book-royalties/{bookRoyalty}` | `admin.rights-holders.contracts.book-royalties.update` | RightsHolderContractController@updateBookRoyalty | can_update |  |
| 513 | DELETE | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/book-royalties/{bookRoyalty}` | `admin.rights-holders.contracts.book-royalties.destroy` | RightsHolderContractController@destroyBookRoyalty | can_delete |  |
| 514 | POST | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/prepayment-lines` | `admin.rights-holders.contracts.prepayment-lines.store` | RightsHolderContractController@storePrepaymentLine | can_create |  |
| 515 | PUT | `/{admin}/rights-holders/{rightsHolder}/contracts/{contract}/prepayment-lines/{prepaymentLine}` | `admin.rights-holders.contracts.prepayment-lines.update` | RightsHolderContractController@updatePrepaymentLine | can_update |  |
| 519 | POST | `/{admin}/rights-holders/{rightsHolder}/nts-verify` | `admin.rights-holders.nts-verify` | RightsHolderController@ntsVerify | can_update | 국세청 진위 확인 (합의서 17.4절). 응답으로 과세유형 · 사업자 상태를 원장에 자동 채움 하므로 접미사 권한은 쓰기(can_update)다 — AdminPermissionService::SUFFIX_PERMISSIONS 참조 |
| 521 | GET | `/{admin}/rights-holders/{rightsHolder}/edit` | `admin.rights-holders.edit` | RightsHolderController@edit | can_update |  |
| 522 | PUT | `/{admin}/rights-holders/{rightsHolder}` | `admin.rights-holders.update` | RightsHolderController@update | can_update |  |
| 530 | GET | `/{admin}/settlement/rights-mapping` | `admin.settlement.rights-mapping.index` | RightsMappingController@index | can_view |  |
| 532 | GET | `/{admin}/settlement/rights-mapping/contracts` | `admin.settlement.rights-mapping.contracts` | RightsMappingController@contracts | can_view | 적용 계약 후보(JSON) — contracts 접미사는 can_view 로 매핑돼 있다 |
| 535 | GET | `/{admin}/settlement/rights-mapping/edit` | `admin.settlement.rights-mapping.show` | RightsMappingController@show | can_view | 편집 화면(S1). 이름은 show 다 — 접미사가 곧 권한이고 이 화면은 R 로 열린다. edit 으로 두면 can_update 가 걸려 조회 권한만 있는 담당자가 열 수 없다 |
| 536 | POST | `/{admin}/settlement/rights-mapping` | `admin.settlement.rights-mapping.store` | RightsMappingController@store | can_create |  |
| 543 | GET | `/{admin}/settlement/board` | `admin.settlement.board.index` | SettlementBoardController@index | can_view |  |
| 545 | GET | `/{admin}/settlement/board/download` | `admin.settlement.board.download` | SettlementBoardController@download | can_download | 이체 리스트 엑셀 — 정적 경로를 {rightsHolder} 보다 위에 둔다(아래로 내리면 파라미터로 먹힌다) |
| 547 | POST | `/{admin}/settlement/board/recalculate` | `admin.settlement.board.recalculate` | SettlementBoardController@update | can_update | 배치 재실행 — recalculate 접미사가 can_update 로 매핑돼 있다(DECISIONS #103) |
| 549 | POST | `/{admin}/settlement/board/close` | `admin.settlement.board.close.store` | SettlementBoardController@store | can_create | 마감 확정(002-P2) — 권한은 서비스가 재무팀 · 최고 관리자로 다시 판정한다 |
| 551 | POST | `/{admin}/settlement/board/memos` | `admin.settlement.board.memos.store` | SettlementBoardController@storeMemo | can_create | 재무팀 검토 메모(002-S1) — 마감 월에도 허용한다(금액이 아니다) |
| 553 | GET | `/{admin}/settlement/board/{rightsHolder}` | `admin.settlement.board.show` | SettlementBoardController@show | can_view | 통합 정산서 상세(002-S1) · 이월 발생 내역(002-P1) |
| 554 | GET | `/{admin}/settlement/board/{rightsHolder}/carryovers` | `admin.settlement.board.carryovers.show` | SettlementBoardController@carryover | can_view |  |
| 563 | GET | `/{admin}/settlement/statements` | `admin.settlement.statements.index` | SettlementStatementController@index | can_view |  |
| 564 | GET | `/{admin}/settlement/statements/download` | `admin.settlement.statements.download` | SettlementStatementController@download | can_download |  |
| 571 | GET | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.index` | SettlementAdjustmentController@index | can_view |  |
| 573 | GET | `/{admin}/settlement/adjustments/download` | `admin.settlement.adjustments.download` | SettlementAdjustmentController@download | can_download | 정적 경로를 파라미터보다 위에 둔다(TEAM_RULES §3) |
| 575 | GET | `/{admin}/settlement/adjustments/form` | `admin.settlement.adjustments.show` | SettlementAdjustmentController@show | can_view | 005-S1 — ?id 가 있으면 수정. 접미사 show 라 조회 권한으로 연다 |
| 576 | POST | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.store` | SettlementAdjustmentController@store | can_create |  |
| 578 | PUT | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.update` | SettlementAdjustmentController@update | can_update | 확정 · 반려 |
| 579 | DELETE | `/{admin}/settlement/adjustments` | `admin.settlement.adjustments.destroy` | SettlementAdjustmentController@destroy | can_delete |  |
| 586 | GET | `/{admin}/settlement/payee-splits` | `admin.settlement.payee-splits.index` | PayeeSplitController@index | can_view |  |
| 588 | GET | `/{admin}/settlement/payee-splits/create` | `admin.settlement.payee-splits.create` | PayeeSplitController@create | can_create | 정적 경로를 파라미터 경로보다 위에 둔다(TEAM_RULES §3) |
| 590 | GET | `/{admin}/settlement/payee-splits/{contract}/simulate` | `admin.settlement.payee-splits.show` | PayeeSplitController@show | can_view | 배분 시뮬레이터 — 저장하지 않는다. 접미사 show 라 조회 권한으로 연다 |
| 591 | GET | `/{admin}/settlement/payee-splits/{contract}` | `admin.settlement.payee-splits.edit` | PayeeSplitController@edit | can_update |  |
| 593 | PUT | `/{admin}/settlement/payee-splits/{contract}` | `admin.settlement.payee-splits.update` | PayeeSplitController@update | can_update | 분할 비율 저장 — 구성 전체 교체라 update 다 |
| 595 | POST | `/{admin}/settlement/payee-splits/{contract}/co-signers` | `admin.settlement.payee-splits.store` | PayeeSplitController@store | can_create | 공동 서명 수취인 풀 추가 · 제외 (DECISIONS 196 ①) |
| 597 | DELETE | `/{admin}/settlement/payee-splits/{contract}/co-signers/{coSigner}` | `admin.settlement.payee-splits.destroy` | PayeeSplitController@destroy | can_delete | coSigner 는 그룹 공통 whereId 목록에 없어 여기서 건다(숫자 18자리까지) |
| 605 | GET | `/{admin}/settlement/pg-reconciliations` | `admin.settlement.pg-reconciliations.index` | PgReconciliationController@index | can_view |  |
| 607 | POST | `/{admin}/settlement/pg-reconciliations` | `admin.settlement.pg-reconciliations.store` | PgReconciliationController@store | can_create | 정적 경로를 파라미터 경로보다 위에 둔다(TEAM_RULES §3) |
| 609 | GET | `/{admin}/settlement/pg-reconciliations/{item}` | `admin.settlement.pg-reconciliations.show` | PgReconciliationController@show | can_view | item 은 그룹 공통 whereId 목록에 없어 여기서 건다(숫자 18자리까지) |
| 610 | PUT | `/{admin}/settlement/pg-reconciliations/{item}` | `admin.settlement.pg-reconciliations.update` | PgReconciliationController@update | can_update |  |
| 617 | GET | `/{admin}/settlement/pass-refunds` | `admin.settlement.pass-refunds.index` | PassRefundSettleController@index | can_view |  |
| 619 | GET | `/{admin}/settlement/pass-refunds/{claim}` | `admin.settlement.pass-refunds.show` | PassRefundSettleController@show | can_view | claim 은 그룹 공통 whereId 목록에 없어 여기서 건다(숫자 18자리까지) |
| 620 | PUT | `/{admin}/settlement/pass-refunds/{claim}` | `admin.settlement.pass-refunds.update` | PassRefundSettleController@update | can_update |  |
| 628 | GET | `/{admin}/settlement/internal` | `admin.settlement.internal.index` | InternalSettlementController@index | can_view |  |
| 630 | GET | `/{admin}/settlement/internal/download` | `admin.settlement.internal.download` | InternalSettlementController@download | can_download | 금액이 나가므로 사유를 받는다. 접미사 download 라 can_download 로 판정된다 |
| 637 | GET | `/{admin}/settlement/nts` | `admin.settlement.nts.index` | NtsVerificationController@index | can_view |  |
| 639 | PUT | `/{admin}/settlement/nts/tax-type` | `admin.settlement.nts.update` | NtsVerificationController@update | can_update | 과세유형 전환 승인 · 보류 — 권리자 원장을 바꾸고 마감 보류를 풀어 can_update 다 |
| 647 | GET | `/{admin}/instructor-profiles` | `admin.instructor-profiles.index` | InstructorProfileController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 648 | GET | `/{admin}/instructor-profiles/create` | `admin.instructor-profiles.create` | InstructorProfileController@create | can_create |  |
| 649 | GET | `/{admin}/instructor-profiles/download` | `admin.instructor-profiles.download` | InstructorProfileController@download | can_download |  |
| 651 | GET | `/{admin}/instructor-profiles/search-instructors` | `admin.instructor-profiles.instructors.index` | InstructorProfileController@apiSearch | can_view | 강사 ID 연동 검색 — 이 메뉴 안에서만 쓰는 조회라 메뉴 권한에 귀속시킨다(instructors.index → 조회 권한) |
| 652 | POST | `/{admin}/instructor-profiles` | `admin.instructor-profiles.store` | InstructorProfileController@store | can_create |  |
| 654 | GET | `/{admin}/instructor-profiles/{instructorProfile}/edit` | `admin.instructor-profiles.edit` | InstructorProfileController@edit | can_update |  |
| 655 | PUT | `/{admin}/instructor-profiles/{instructorProfile}` | `admin.instructor-profiles.update` | InstructorProfileController@update | can_update |  |
| 656 | DELETE | `/{admin}/instructor-profiles/{instructorProfile}` | `admin.instructor-profiles.destroy` | InstructorProfileController@destroy | can_delete |  |
| 663 | GET | `/{admin}/badges` | `admin.badges.index` | BadgeController@index | can_view |  |
| 664 | GET | `/{admin}/badges/create` | `admin.badges.create` | BadgeController@create | can_create |  |
| 665 | POST | `/{admin}/badges` | `admin.badges.store` | BadgeController@store | can_create |  |
| 667 | GET | `/{admin}/badges/{badge}/edit` | `admin.badges.edit` | BadgeController@edit | can_update |  |
| 668 | PUT | `/{admin}/badges/{badge}` | `admin.badges.update` | BadgeController@update | can_update |  |
| 669 | DELETE | `/{admin}/badges/{badge}` | `admin.badges.destroy` | BadgeController@destroy | can_delete |  |
| 677 | GET | `/{admin}/boards` | `admin.boards.index` | BoardController@index | can_view | 게시판 CRUD |
| 678 | GET | `/{admin}/boards/create` | `admin.boards.create` | BoardController@create | can_create |  |
| 679 | POST | `/{admin}/boards` | `admin.boards.store` | BoardController@store | can_create |  |
| 680 | GET | `/{admin}/boards/{board}/edit` | `admin.boards.edit` | BoardController@edit | can_update |  |
| 681 | PUT | `/{admin}/boards/{board}` | `admin.boards.update` | BoardController@update | can_update |  |
| 682 | DELETE | `/{admin}/boards/{board}` | `admin.boards.destroy` | BoardController@destroy | can_delete |  |
| 689 | GET | `/{admin}/boards/{board}/posts` | `admin.boards.posts.index` | PostController@index | can_view | 정적 경로 |
| 690 | GET | `/{admin}/boards/{board}/posts/create` | `admin.boards.posts.create` | PostController@create | can_create |  |
| 691 | GET | `/{admin}/boards/{board}/posts/download` | `admin.boards.posts.download` | PostController@download | can_download |  |
| 692 | POST | `/{admin}/boards/{board}/posts/download-selected` | `admin.boards.posts.selected.download` | PostController@downloadSelected | can_download |  |
| 693 | POST | `/{admin}/boards/{board}/posts` | `admin.boards.posts.store` | PostController@store | can_create |  |
| 696 | GET | `/{admin}/boards/{board}/posts/{post}/edit` | `admin.boards.posts.edit` | PostController@edit | can_update | 파라미터 경로 (정적 경로보다 아래) |
| 697 | GET | `/{admin}/boards/{board}/posts/{post}` | `admin.boards.posts.show` | PostController@show | can_view |  |
| 698 | PUT | `/{admin}/boards/{board}/posts/{post}` | `admin.boards.posts.update` | PostController@update | can_update |  |
| 699 | DELETE | `/{admin}/boards/{board}/posts/{post}` | `admin.boards.posts.destroy` | PostController@destroy | can_delete |  |
| 708 | GET | `/{admin}/winners` | `admin.winners.index` | WinnerController@index | can_view |  |
| 709 | GET | `/{admin}/winners/create` | `admin.winners.create` | WinnerController@create | can_create |  |
| 710 | POST | `/{admin}/winners` | `admin.winners.store` | WinnerController@store | can_create |  |
| 711 | PUT | `/{admin}/winners/status` | `admin.winners.status.update` | WinnerController@bulkHide | can_update |  |
| 712 | GET | `/{admin}/winners/template/download` | `admin.winners.template.download` | WinnerController@template | can_download |  |
| 713 | GET | `/{admin}/winners/{winner}/edit` | `admin.winners.edit` | WinnerController@edit | can_update |  |
| 714 | PUT | `/{admin}/winners/{winner}` | `admin.winners.update` | WinnerController@update | can_update |  |
| 721 | GET | `/{admin}/free-contents` | `admin.free-contents.index` | FreeContentController@index | can_view |  |
| 722 | GET | `/{admin}/free-contents/create` | `admin.free-contents.create` | FreeContentController@create | can_create |  |
| 723 | POST | `/{admin}/free-contents` | `admin.free-contents.store` | FreeContentController@store | can_create |  |
| 724 | GET | `/{admin}/free-contents/download` | `admin.free-contents.download` | FreeContentController@download | can_download |  |
| 726 | GET | `/{admin}/free-contents/duplicates` | `admin.free-contents.duplicates.index` | FreeContentController@duplicates | can_view | 저장 전 중복 경고(조회) — 하위 자원 + 표준 접미사 |
| 727 | PUT | `/{admin}/free-contents/status` | `admin.free-contents.status.update` | FreeContentController@bulkStatus | can_update |  |
| 728 | DELETE | `/{admin}/free-contents/selected` | `admin.free-contents.selected.destroy` | FreeContentController@bulkDelete | can_delete |  |
| 729 | GET | `/{admin}/free-contents/{freeContent}/edit` | `admin.free-contents.edit` | FreeContentController@edit | can_update |  |
| 730 | PUT | `/{admin}/free-contents/{freeContent}` | `admin.free-contents.update` | FreeContentController@update | can_update |  |
| 736 | GET | `/{admin}/notices` | `admin.notices.index` | NoticeController@index | can_view |  |
| 737 | GET | `/{admin}/notices/create` | `admin.notices.create` | NoticeController@create | can_create |  |
| 738 | POST | `/{admin}/notices` | `admin.notices.store` | NoticeController@store | can_create |  |
| 741 | PUT | `/{admin}/notices/status` | `admin.notices.status.update` | NoticeController@bulkHide | can_update | 일괄 처리 |
| 742 | DELETE | `/{admin}/notices/selected` | `admin.notices.selected.destroy` | NoticeController@bulkDelete | can_delete |  |
| 744 | GET | `/{admin}/notices/{notice}/edit` | `admin.notices.edit` | NoticeController@edit | can_update |  |
| 745 | PUT | `/{admin}/notices/{notice}` | `admin.notices.update` | NoticeController@update | can_update |  |
| 746 | DELETE | `/{admin}/notices/{notice}` | `admin.notices.destroy` | NoticeController@destroy | can_delete |  |
| 753 | GET | `/{admin}/faqs` | `admin.faqs.index` | FaqController@index | can_view |  |
| 754 | GET | `/{admin}/faqs/create` | `admin.faqs.create` | FaqController@create | can_create |  |
| 755 | POST | `/{admin}/faqs` | `admin.faqs.store` | FaqController@store | can_create |  |
| 758 | PUT | `/{admin}/faqs/status` | `admin.faqs.status.update` | FaqController@updateVisibility | can_update | 체크박스 일괄 처리 — 노출 전환 · 카테고리 이동(일괄 삭제는 두지 않는다) |
| 759 | PUT | `/{admin}/faqs/category` | `admin.faqs.category.update` | FaqController@updateCategory | can_update |  |
| 763 | POST | `/{admin}/faqs/categories` | `admin.faqs.categories.store` | FaqController@storeCategory | can_create | 카테고리 (정적 경로 — 파라미터 경로보다 위) 별도 메뉴 미등록 시 권한은 FAQ 메뉴로 폴백, 등록 시 독립 권한 |
| 764 | DELETE | `/{admin}/faqs/categories/{faqCategory}` | `admin.faqs.categories.destroy` | FaqController@destroyCategory | can_delete |  |
| 766 | GET | `/{admin}/faqs/{faq}/edit` | `admin.faqs.edit` | FaqController@edit | can_update |  |
| 767 | PUT | `/{admin}/faqs/{faq}` | `admin.faqs.update` | FaqController@update | can_update |  |
| 768 | DELETE | `/{admin}/faqs/{faq}` | `admin.faqs.destroy` | FaqController@destroy | can_delete |  |
| 775 | GET | `/{admin}/inquiries` | `admin.inquiries.index` | InquiryController@index | can_view |  |
| 777 | GET | `/{admin}/inquiries/download` | `admin.inquiries.download` | InquiryController@download | can_download | 정적 경로는 {inquiry} 보다 위에 둔다 |
| 778 | POST | `/{admin}/inquiries/download-selected` | `admin.inquiries.selected.download` | InquiryController@downloadSelected | can_download |  |
| 779 | PUT | `/{admin}/inquiries/assignees` | `admin.inquiries.assignees.update` | InquiryController@bulkAssign | can_update |  |
| 780 | GET | `/{admin}/inquiries/{inquiry}` | `admin.inquiries.show` | InquiryController@show | can_view |  |
| 782 | GET | `/{admin}/inquiries/{inquiry}/member` | `admin.inquiries.member.show` | InquiryController@memberContext | can_view | 회원 컨텍스트 모달 내용(P1) — 조회 권한 |
| 783 | PUT | `/{admin}/inquiries/{inquiry}` | `admin.inquiries.update` | InquiryController@update | can_update |  |
| 784 | PUT | `/{admin}/inquiries/{inquiry}/category` | `admin.inquiries.category.update` | InquiryController@changeCategory | can_update |  |
| 786 | PUT | `/{admin}/inquiries/{inquiry}/assignee` | `admin.inquiries.assignee.update` | InquiryController@releaseLock | can_update | 동시 답변 잠금 해제(상위 권한 · 사유) — 담당자를 비운다 |
| 788 | PUT | `/{admin}/inquiries/{inquiry}/notifications/{notificationLog}` | `admin.inquiries.notifications.update` | InquiryController@resendNotification | can_update | 답변 알림 재발송(설계서 ⑤) — 답변과 같은 수정 권한 |
| 795 | GET | `/{admin}/product-qnas` | `admin.product-qnas.index` | ProductQnaController@index | can_view |  |
| 797 | PUT | `/{admin}/product-qnas/assignees` | `admin.product-qnas.assignees.update` | ProductQnaController@bulkAssign | can_update | 정적 경로는 {productQna} 보다 위에 둔다 |
| 798 | GET | `/{admin}/product-qnas/{productQna}` | `admin.product-qnas.show` | ProductQnaController@show | can_view |  |
| 799 | PUT | `/{admin}/product-qnas/{productQna}` | `admin.product-qnas.update` | ProductQnaController@update | can_update |  |
| 800 | PUT | `/{admin}/product-qnas/{productQna}/notifications/{notificationLog}` | `admin.product-qnas.notifications.update` | ProductQnaController@resendNotification | can_update |  |
| 807 | GET | `/{admin}/study-qnas` | `admin.study-qnas.index` | StudyQnaController@index | can_view |  |
| 808 | GET | `/{admin}/study-qnas/{studyQna}` | `admin.study-qnas.show` | StudyQnaController@show | can_view |  |
| 809 | PUT | `/{admin}/study-qnas/{studyQna}` | `admin.study-qnas.update` | StudyQnaController@update | can_update |  |
| 810 | PUT | `/{admin}/study-qnas/{studyQna}/notifications/{notificationLog}` | `admin.study-qnas.notifications.update` | StudyQnaController@resendNotification | can_update |  |
| 812 | GET | `/{admin}/study-qnas/{studyQna}/files/{file}` | `admin.study-qnas.files.show` | StudyQnaController@file | can_view | 회원 첨부 받기 — 첨부 공용 경로(AttachmentController)는 메뉴 권한만 봐서 다른 강사 질문의 파일이 열린다. 담당 범위를 보는 이 경로로 받는다 |
| 814 | GET | `/{admin}/study-qnas/{studyQna}/images/{name}` | `admin.study-qnas.images.show` | StudyQnaController@image | can_view | 회원 본문 이미지(secure) — 본문이 이 경로로 그려진다. 비밀글이어도 담당 범위 안이면 보인다(박성민 10-20) |
| 821 | GET | `/{admin}/inquiry-categories` | `admin.inquiry-categories.index` | InquiryCategoryController@index | can_view |  |
| 822 | POST | `/{admin}/inquiry-categories` | `admin.inquiry-categories.store` | InquiryCategoryController@store | can_create |  |
| 825 | POST | `/{admin}/inquiry-categories/majors` | `admin.inquiry-categories.majors.store` | InquiryCategoryController@storeMajor | can_create | 대분류 · 상태 일괄전환 |
| 826 | PUT | `/{admin}/inquiry-categories/majors/{inquiryCategory}` | `admin.inquiry-categories.majors.update` | InquiryCategoryController@updateMajor | can_update |  |
| 827 | PUT | `/{admin}/inquiry-categories/status` | `admin.inquiry-categories.status.update` | InquiryCategoryController@bulkStatus | can_update |  |
| 830 | PUT | `/{admin}/inquiry-categories/{inquiryCategory}` | `admin.inquiry-categories.update` | InquiryCategoryController@update | can_update | 소분류 수정 |
| 837 | GET | `/{admin}/reviews` | `admin.reviews.index` | ReviewController@index | can_view |  |
| 840 | PUT | `/{admin}/reviews/display` | `admin.reviews.display.update` | ReviewController@bulkDisplay | can_update | 일괄 처리 |
| 841 | PUT | `/{admin}/reviews/best` | `admin.reviews.best.update` | ReviewController@bulkBest | can_update |  |
| 844 | PUT | `/{admin}/reviews/{review}/notifications/{notificationLog}` | `admin.reviews.notifications.update` | ReviewController@resendNotification | can_update | 우수 후기 포인트 지급 알림 재발송 — 실패한 발송만(BRD-002 ~ 005 공용, 검증 처리와 같은 수정 권한) |
| 847 | GET | `/{admin}/reviews/{review}` | `admin.reviews.show` | ReviewController@show | can_view | 상세 · 검증 처리 |
| 848 | PUT | `/{admin}/reviews/{review}` | `admin.reviews.update` | ReviewController@update | can_update |  |
| 855 | GET | `/{admin}/orders` | `admin.orders.index` | OrderController@index | can_view |  |
| 856 | GET | `/{admin}/orders/download` | `admin.orders.download` | OrderController@download | can_download |  |
| 857 | GET | `/{admin}/orders/{order}` | `admin.orders.show` | OrderController@show | can_view |  |
| 859 | GET | `/{admin}/orders/{order}/print` | `admin.orders.print.show` | OrderController@showPrint | can_view | 주문서 인쇄(거래명세) — 조회 권한으로 연다. 인쇄 전용 화면이라 하위 자원 print + show |
| 860 | PUT | `/{admin}/orders/{order}/address` | `admin.orders.address.update` | OrderController@updateAddress | can_update |  |
| 862 | DELETE | `/{admin}/orders/{order}/dispatch` | `admin.orders.dispatch.destroy` | OrderController@destroyDispatch | can_delete | 출고지시 회수(잠금 해제) — 최고관리자 판정은 컨트롤러가 한 번 더 한다 |
| 863 | POST | `/{admin}/orders/{order}/memos` | `admin.orders.memos.store` | OrderController@storeMemo | can_create |  |
| 870 | GET | `/{admin}/deliveries` | `admin.deliveries.index` | DeliveryController@index | can_view |  |
| 872 | POST | `/{admin}/deliveries/dispatch` | `admin.deliveries.dispatch.download` | DeliveryController@storeDispatch | can_download | 발주 엑셀 = 출고지시(배송지 잠금). 상태를 바꾸므로 POST, 개인정보 반출이라 다운로드 권한(can_download) |
| 873 | GET | `/{admin}/deliveries/batches` | `admin.deliveries.batches.index` | DeliveryController@batches | can_view |  |
| 874 | GET | `/{admin}/deliveries/batches/{batch}/download` | `admin.deliveries.batches.download` | DeliveryController@downloadBatch | can_download |  |
| 876 | PUT | `/{admin}/deliveries/batches/{batch}/notifications` | `admin.deliveries.batches.notifications.update` | DeliveryController@updateNotifications | can_update | 송장 업로드의 배송출고 알림 발송 실패 재시도 |
| 877 | POST | `/{admin}/deliveries/tracking` | `admin.deliveries.tracking.store` | DeliveryController@storeTracking | can_create |  |
| 879 | POST | `/{admin}/deliveries/tracking/preview` | `admin.deliveries.tracking.preview.store` | DeliveryController@previewTracking | can_create | 송장 파일 사전 읽기 — 저장하지 않지만 업로드와 같은 권한(can_create)에 묶는다 |
| 880 | GET | `/{admin}/deliveries/tracking/template/download` | `admin.deliveries.template.download` | DeliveryController@downloadTemplate | can_download |  |
| 881 | GET | `/{admin}/deliveries/tracking/{batch}/failures/download` | `admin.deliveries.failures.download` | DeliveryController@downloadFailures | can_download |  |
| 882 | PUT | `/{admin}/deliveries/delivered` | `admin.deliveries.delivered.update` | DeliveryController@updateDelivered | can_update |  |
| 884 | PUT | `/{admin}/deliveries/returns/{refund}` | `admin.deliveries.returns.update` | RefundController@updateReturnInspection | can_update | 반품 수거 · 검수 탭의 검수 입력 — 판정은 환불 심사와 같은 RefundService, 권한은 배송 관리 메뉴를 따른다 |
| 885 | GET | `/{admin}/deliveries/returns/{refund}/photos/{photo}` | `admin.deliveries.returns.show` | RefundController@showReturnPhoto | can_view |  |
| 886 | PUT | `/{admin}/deliveries/{delivery}/tracking` | `admin.deliveries.tracking.update` | DeliveryController@updateTracking | can_update |  |
| 894 | GET | `/{admin}/refunds` | `admin.refunds.index` | RefundController@index | can_view |  |
| 895 | GET | `/{admin}/refunds/download` | `admin.refunds.download` | RefundController@download | can_download |  |
| 897 | GET | `/{admin}/refunds/inquiries/{inquiry}` | `admin.refunds.inquiries.show` | RefundInquiryController@show | can_view | 환불 관리 상세 뷰 — 1:1 결제 · 환불 문의 (ADMN-RFD-002-S1) |
| 898 | PUT | `/{admin}/refunds/inquiries/{inquiry}` | `admin.refunds.inquiries.update` | RefundInquiryController@update | can_update |  |
| 899 | PUT | `/{admin}/refunds/inquiries/{inquiry}/category` | `admin.refunds.inquiries.category.update` | RefundInquiryController@updateCategory | can_update |  |
| 900 | PUT | `/{admin}/refunds/inquiries/{inquiry}/sub-type` | `admin.refunds.inquiries.sub-type.update` | RefundInquiryController@updateSubType | can_update |  |
| 901 | POST | `/{admin}/refunds/inquiries/{inquiry}/refund` | `admin.refunds.inquiries.refund.store` | RefundInquiryController@storeRefund | can_create |  |
| 902 | PUT | `/{admin}/refunds/inquiries/{inquiry}/cancel` | `admin.refunds.inquiries.cancel.update` | RefundInquiryController@updateCancel | can_update |  |
| 903 | PUT | `/{admin}/refunds/inquiries/{inquiry}/hold` | `admin.refunds.inquiries.hold.update` | RefundInquiryController@updateHold | can_update |  |
| 904 | GET | `/{admin}/refunds/{refund}` | `admin.refunds.show` | RefundController@show | can_view |  |
| 906 | GET | `/{admin}/refunds/{refund}/print` | `admin.refunds.print.show` | RefundController@showPrint | can_view | 환불금 계산 명세 인쇄 — 조회 권한으로 연다. 인쇄 전용 화면이라 하위 자원 print + show |
| 907 | GET | `/{admin}/refunds/{refund}/point-usages` | `admin.refunds.point-usages.index` | RefundController@pointUsages | can_view |  |
| 908 | GET | `/{admin}/refunds/{refund}/photos/{photo}` | `admin.refunds.photos.show` | RefundController@showPhoto | can_view |  |
| 909 | PUT | `/{admin}/refunds/{refund}/receipt` | `admin.refunds.receipt.update` | RefundController@updateReceipt | can_update |  |
| 910 | PUT | `/{admin}/refunds/{refund}/inspection` | `admin.refunds.inspection.update` | RefundController@updateInspection | can_update |  |
| 911 | POST | `/{admin}/refunds/{refund}/recalculate` | `admin.refunds.recalculate` | RefundController@recalculate | can_update |  |
| 912 | PUT | `/{admin}/refunds/{refund}/approval` | `admin.refunds.approval.update` | RefundController@updateApproval | can_update |  |
| 913 | PUT | `/{admin}/refunds/{refund}/rejection` | `admin.refunds.rejection.update` | RefundController@updateRejection | can_update |  |
| 914 | PUT | `/{admin}/refunds/{refund}/hold` | `admin.refunds.hold.update` | RefundController@updateHold | can_update |  |
| 922 | GET | `/{admin}/pass-refunds` | `admin.pass-refunds.index` | PassRefundController@index | can_view |  |
| 923 | GET | `/{admin}/pass-refunds/download` | `admin.pass-refunds.download` | PassRefundController@download | can_download |  |
| 924 | PUT | `/{admin}/pass-refunds/approvals` | `admin.pass-refunds.approvals.update` | PassRefundController@updateApprovals | can_update |  |
| 925 | POST | `/{admin}/pass-refunds/payouts/download` | `admin.pass-refunds.payouts.download` | PassRefundController@downloadPayouts | can_download |  |
| 926 | PUT | `/{admin}/pass-refunds/payouts` | `admin.pass-refunds.payouts.update` | PassRefundController@updatePayouts | can_update |  |
| 928 | PUT | `/{admin}/pass-refunds/account-refunds/{refund}` | `admin.pass-refunds.account-refunds.update` | PassRefundController@updateAccountRefund | can_update | 1:1 문의 환불 중 PG 로 돌려줄 수 없는 건의 계좌 환불 — 기록은 환불 원장(refunds) |
| 929 | GET | `/{admin}/pass-refunds/{passRefund}` | `admin.pass-refunds.show` | PassRefundController@show | can_view |  |
| 930 | PUT | `/{admin}/pass-refunds/{passRefund}` | `admin.pass-refunds.update` | PassRefundController@update | can_update |  |
| 931 | GET | `/{admin}/pass-refunds/{passRefund}/files/{file}` | `admin.pass-refunds.files.show` | PassRefundController@showFile | can_view |  |
| 938 | GET | `/{admin}/refund-histories` | `admin.refund-histories.index` | RefundHistoryController@index | can_view |  |
| 939 | GET | `/{admin}/refund-histories/download` | `admin.refund-histories.download` | RefundHistoryController@download | can_download |  |
| 940 | GET | `/{admin}/refund-histories/{refund}` | `admin.refund-histories.show` | RefundHistoryController@show | can_view |  |
| 942 | GET | `/{admin}/refund-histories/{refund}/adjustments/create` | `admin.refund-histories.adjustments.create` | RefundAdjustmentController@create | can_create | 보정 거래 등록 — 완료된 환불을 별도 거래로 정정한다(원 거래 불변). 재무팀 · 최고 관리자만(컨트롤러가 다시 막는다) |
| 943 | POST | `/{admin}/refund-histories/{refund}/adjustments` | `admin.refund-histories.adjustments.store` | RefundAdjustmentController@store | can_create |  |
| 944 | GET | `/{admin}/refund-histories/{refund}/adjustments/{adjustment}/files/{file}` | `admin.refund-histories.adjustments.files.show` | RefundAdjustmentController@showFile | can_view |  |
| 951 | GET | `/{admin}/members` | `admin.members.index` | MemberController@index | can_view |  |
| 952 | GET | `/{admin}/members/download` | `admin.members.download` | MemberController@download | can_download |  |
| 955 | GET | `/{admin}/members/blacklist` | `admin.members.blacklist.index` | MemberBlacklistController@index | can_view | 블랙리스트 (정지 등재 · 해제) |
| 956 | GET | `/{admin}/members/blacklist/create` | `admin.members.blacklist.create` | MemberBlacklistController@create | can_create |  |
| 957 | POST | `/{admin}/members/blacklist` | `admin.members.blacklist.store` | MemberBlacklistController@store | can_create |  |
| 958 | PUT | `/{admin}/members/blacklist/{sanction}` | `admin.members.blacklist.update` | MemberBlacklistController@update | can_update |  |
| 962 | GET | `/{admin}/members/course` | `admin.members.course.index` | MemberCourseController@index | can_view | 수강 · 기기 제어 — 수강 기간 연장 · 일시정지 · 정지 해제 (ADMN-USER-003) 기기 해제는 SPK 관리 콘솔에서 하므로 이 화면에 리셋 경로를 두지 않는다 |
| 964 | POST | `/{admin}/members/course/{userCourse}/extend` | `admin.members.course.extend.update` | MemberCourseController@extend | can_update | 기간을 바꾸는 조작이라 전부 수정 권한(update)이다. 열람 전용 역할은 URL 직접 호출도 막힌다 |
| 965 | POST | `/{admin}/members/course/{userCourse}/pause` | `admin.members.course.pause.update` | MemberCourseController@pause | can_update |  |
| 966 | POST | `/{admin}/members/course/{userCourse}/resume` | `admin.members.course.resume.update` | MemberCourseController@resume | can_update |  |
| 969 | GET | `/{admin}/members/group` | `admin.members.group.index` | MemberGroupController@index | can_view | 그룹 · 태그 (수동 태그 · 일괄 부여) |
| 970 | POST | `/{admin}/members/group` | `admin.members.group.store` | MemberGroupController@store | can_create |  |
| 974 | GET | `/{admin}/members/group/tag/create` | `admin.members.group.tag.create` | MemberTagController@create | can_create | 태그 생성 · 수정 (ADMN-USER-006-S1) — 수동 · 자동이 ?mode=manual\|auto 탭 2개로 들어온다. 'group/tag' 보다 앞에 둬야 group/{group} 이 'tag' 를 id 로 집어먹지 않는다 |
| 975 | POST | `/{admin}/members/group/tag` | `admin.members.group.tag.store` | MemberTagController@store | can_create |  |
| 977 | GET | `/{admin}/members/group/tag/preview` | `admin.members.group.tag.preview.index` | MemberTagController@preview | can_view | 대상 미리보기 — 저장 전 인원 + 마스킹 명단. 세지만 저장하지 않아 조회 권한이다 |
| 978 | GET | `/{admin}/members/group/tag/{tag}/edit` | `admin.members.group.tag.edit` | MemberTagController@edit | can_update |  |
| 979 | PUT | `/{admin}/members/group/tag/{tag}` | `admin.members.group.tag.update` | MemberTagController@update | can_update |  |
| 982 | GET | `/{admin}/members/group/saved/create` | `admin.members.group.saved.create` | SavedGroupController@create | can_create | 조건 그룹 저장 (ADMN-USER-006-S2) — 목록의 태그 조합 필터를 들고 들어온다 |
| 983 | POST | `/{admin}/members/group/saved` | `admin.members.group.saved.store` | SavedGroupController@store | can_create |  |
| 984 | PUT | `/{admin}/members/group/member` | `admin.members.group.member.update` | MemberGroupController@updateMember | can_update |  |
| 986 | POST | `/{admin}/members/group/upload` | `admin.members.group.upload.store` | MemberGroupController@storeUpload | can_create | 엑셀 명단 업로드(매칭 결과 확인) · 미매칭 명단 내려받기 |
| 987 | GET | `/{admin}/members/group/unmatched/download` | `admin.members.group.unmatched.download` | MemberGroupController@downloadUnmatched | can_download |  |
| 988 | PUT | `/{admin}/members/group/{group}` | `admin.members.group.update` | MemberGroupController@update | can_update |  |
| 989 | DELETE | `/{admin}/members/group/{group}` | `admin.members.group.destroy` | MemberGroupController@destroy | can_delete |  |
| 993 | POST | `/{admin}/members/review-points/{review}` | `admin.members.review-points.store` | ReviewController@grantPoint | can_create | 우수 후기 포인트 수동 지급(ADMN-BRD-005-S1) — 화면은 후기 검증에 있지만 권한은 회원 상세 수동 지급과 같아야 해서(박성민 10-21) 이름을 회원관리 아래 둔다. 메뉴 권한은 라우트 이름으로 정해진다 — points.store 와 같은 회원관리 등록(store) 판정 |
| 995 | GET | `/{admin}/members/{member}` | `admin.members.show` | MemberController@show | can_view |  |
| 996 | PUT | `/{admin}/members/{member}` | `admin.members.update` | MemberController@update | can_update |  |
| 997 | PUT | `/{admin}/members/{member}/status` | `admin.members.status.update` | MemberController@updateStatus | can_update |  |
| 999 | POST | `/{admin}/members/{member}/points` | `admin.members.points.store` | MemberController@storePoint | can_create | 수동 무상 포인트 지급 · 차감 — 회원관리 등록 권한(store) |
| 1000 | DELETE | `/{admin}/members/{member}/social/{socialAccount}` | `admin.members.social.destroy` | MemberController@destroySocial | can_delete |  |
| 1001 | PUT | `/{admin}/members/{member}/coupons/{userCoupon}` | `admin.members.coupons.update` | MemberController@revokeCoupon | can_update |  |
| 1008 | GET | `/{admin}/member-progress` | `admin.member-progress.index` | MemberProgressController@index | can_view |  |
| 1012 | POST | `/{admin}/member-progress/recalculate` | `admin.member-progress.recalculate` | MemberProgressController@recalculate | can_update | 재집계는 저장이 아니라 파생값 재계산이라 조회 권한으로 연다. recalculate 접미사는 AdminPermissionService::SUFFIX_PERMISSIONS 에 can_view 로 등록돼 있다 |
| 1014 | GET | `/{admin}/member-progress/download` | `admin.member-progress.download` | MemberProgressController@download | can_download |  |
| 1019 | GET | `/{admin}/member-progress/{userCourse}/lectures/{lecture}/adjust` | `admin.member-progress.adjust.edit` | ProgressAdjustmentController@edit | can_update | 진도율 보정 (ADMN-USER-004-P1) — 차시 단위로만 연다. 보정 반영은 수정 권한(can_update)으로 판정해야 해서 이름을 adjust.update 로 둔다 — store 로 두면 등록 권한만 가진 역할이 환급 판정값을 바꿀 수 있다 |
| 1021 | GET | `/{admin}/member-progress/{userCourse}/lectures/{lecture}/adjust/history` | `admin.member-progress.adjust.history.index` | ProgressAdjustmentController@history | can_view |  |
| 1023 | PUT | `/{admin}/member-progress/{userCourse}/lectures/{lecture}/adjust` | `admin.member-progress.adjust.update` | ProgressAdjustmentController@update | can_update |  |
| 1032 | GET | `/{admin}/coupons` | `admin.coupons.index` | CouponController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 1033 | GET | `/{admin}/coupons/create` | `admin.coupons.create` | CouponController@create | can_create |  |
| 1034 | POST | `/{admin}/coupons` | `admin.coupons.store` | CouponController@store | can_create |  |
| 1036 | GET | `/{admin}/coupons/issue-template` | `admin.coupons.issue-template.create` | CouponController@issueTemplate | can_create | 지급 대상 엑셀 양식 — 개인정보가 없는 빈 양식이라 반출(download) 권한이 아니라 지급과 같은 등록 권한으로 연다 |
| 1038 | GET | `/{admin}/coupons/target-count` | `admin.coupons.target-count.index` | CouponController@targetCount | can_view | 타겟 그룹 대상 수 미리보기(등록 폼) — 회원 수만 돌려준다 |
| 1040 | GET | `/{admin}/coupons/download` | `admin.coupons.download` | CouponController@download | can_download | 발급 · 사용 현황 엑셀 — 회원 식별정보가 들어가 반출(download) 권한 · 사유를 받는다 |
| 1043 | GET | `/{admin}/coupons/{coupon}` | `admin.coupons.show` | CouponController@show | can_view | 파라미터 경로 |
| 1044 | GET | `/{admin}/coupons/{coupon}/edit` | `admin.coupons.edit` | CouponController@edit | can_update |  |
| 1045 | PUT | `/{admin}/coupons/{coupon}` | `admin.coupons.update` | CouponController@update | can_update |  |
| 1048 | POST | `/{admin}/coupons/{coupon}/issue` | `admin.coupons.issue.store` | CouponController@issue | can_create | 지급 = 발급 생성 / 발급 중지 = 상태 수정 / 긴급 사용 중지(최고 관리자) / 비고 = memo 수정 |
| 1049 | PUT | `/{admin}/coupons/{coupon}/status` | `admin.coupons.status.update` | CouponController@suspend | can_update |  |
| 1050 | PUT | `/{admin}/coupons/{coupon}/emergency-status` | `admin.coupons.emergency-status.update` | CouponController@emergencySuspend | can_update |  |
| 1051 | PUT | `/{admin}/coupons/{coupon}/visibility` | `admin.coupons.visibility.update` | CouponController@updateVisibility | can_update |  |
| 1052 | PUT | `/{admin}/coupons/{coupon}/memo` | `admin.coupons.memo.update` | CouponController@updateMemo | can_update |  |
| 1053 | GET | `/{admin}/coupons/{coupon}/memo-history` | `admin.coupons.memo-history.index` | CouponController@memoHistories | can_view |  |
| 1061 | GET | `/{admin}/promotions` | `admin.promotions.index` | PromotionController@index | can_view | 정적 경로 먼저 (파라미터 경로보다 위) |
| 1062 | GET | `/{admin}/promotions/create` | `admin.promotions.create` | PromotionController@create | can_create |  |
| 1063 | POST | `/{admin}/promotions` | `admin.promotions.store` | PromotionController@store | can_create |  |
| 1064 | GET | `/{admin}/promotions/download` | `admin.promotions.download` | PromotionController@download | can_download |  |
| 1066 | GET | `/{admin}/promotions/targets` | `admin.promotions.targets.index` | PromotionController@targets | can_view | 대상 상품 검색 · Slug 중복 확인 — 조회만 한다 |
| 1067 | GET | `/{admin}/promotions/slug` | `admin.promotions.slug.index` | PromotionController@slug | can_view |  |
| 1069 | POST | `/{admin}/promotions/preview` | `admin.promotions.preview.index` | PromotionController@previewDraft | can_view | 작성 중 소스 미리보기 — 소스가 길어 POST 로 받지만 저장하지 않으므로 조회 권한으로 연다 |
| 1072 | GET | `/{admin}/promotions/{promotion}` | `admin.promotions.show` | PromotionController@show | can_view | 파라미터 경로 |
| 1073 | GET | `/{admin}/promotions/{promotion}/edit` | `admin.promotions.edit` | PromotionController@edit | can_update |  |
| 1074 | PUT | `/{admin}/promotions/{promotion}` | `admin.promotions.update` | PromotionController@update | can_update |  |
| 1076 | PUT | `/{admin}/promotions/{promotion}/status` | `admin.promotions.status.update` | PromotionController@stop | can_update | 즉시 중단 = 상태 수정 |
| 1078 | GET | `/{admin}/promotions/{promotion}/blocks/edit` | `admin.promotions.blocks.edit` | PromotionController@blocksEdit | can_update | 중복 할인 일괄 차단(S1) — 하위 자원 blocks |
| 1079 | PUT | `/{admin}/promotions/{promotion}/blocks` | `admin.promotions.blocks.update` | PromotionController@blocksUpdate | can_update |  |
| 1080 | GET | `/{admin}/promotions/{promotion}/preview` | `admin.promotions.preview.show` | PromotionController@preview | can_view |  |
| 1082 | POST | `/{admin}/promotions/{promotion}/assets` | `admin.promotions.assets.store` | PromotionController@storeAssets | can_create | 랜딩 에셋 — 올리기는 등록, 지우기는 삭제 권한 |
| 1083 | DELETE | `/{admin}/promotions/{promotion}/assets` | `admin.promotions.assets.destroy` | PromotionController@destroyAsset | can_delete |  |
| 1088 | GET | `/{admin}/display` | `admin.display.index` | DisplayController@index | can_view | ── 사이트 관리 ── 전시/메뉴 관리 (배너·팝업 통합 3탭) — ADMN-CONF-001 |
| 1093 | GET | `/{admin}/display/strip-banners/create` | `admin.display.strip-banners.create` | StripBannerController@create | can_create |  |
| 1094 | POST | `/{admin}/display/strip-banners` | `admin.display.strip-banners.store` | StripBannerController@store | can_create |  |
| 1096 | PUT | `/{admin}/display/strip-banners/order` | `admin.display.strip-banners.order.update` | StripBannerController@reorder | can_update | 순서 일괄 저장 — 하위자원(order) + 표준 접미사(update)로 권한 매핑(can_update) |
| 1097 | GET | `/{admin}/display/strip-banners/{stripBanner}/edit` | `admin.display.strip-banners.edit` | StripBannerController@edit | can_update |  |
| 1098 | PUT | `/{admin}/display/strip-banners/{stripBanner}` | `admin.display.strip-banners.update` | StripBannerController@update | can_update |  |
| 1099 | DELETE | `/{admin}/display/strip-banners/{stripBanner}` | `admin.display.strip-banners.destroy` | StripBannerController@destroy | can_delete |  |
| 1105 | GET | `/{admin}/message-templates` | `admin.message-templates.index` | MessageTemplateController@index | can_view |  |
| 1106 | GET | `/{admin}/message-templates/create` | `admin.message-templates.create` | MessageTemplateController@create | can_create |  |
| 1107 | POST | `/{admin}/message-templates` | `admin.message-templates.store` | MessageTemplateController@store | can_create |  |
| 1113 | GET | `/{admin}/message-templates/campaigns` | `admin.message-templates.campaigns.index` | MessageCampaignController@index | can_view |  |
| 1114 | POST | `/{admin}/message-templates/campaigns` | `admin.message-templates.campaigns.store` | MessageCampaignController@store | can_create |  |
| 1116 | GET | `/{admin}/message-templates/campaigns/download` | `admin.message-templates.campaigns.download` | MessageCampaignController@download | can_download | 대상 명단 엑셀 — 개인정보 추출이라 사유 입력(ReasonRequest) |
| 1118 | POST | `/{admin}/message-templates/campaigns/test-sends` | `admin.message-templates.campaigns.test-sends.store` | MessageCampaignController@testSend | can_create | 나에게 테스트 발송 — 건당 비용이 드는 실발송이라 템플릿 화면과 같이 횟수를 묶는다 |
| 1119 | GET | `/{admin}/message-templates/campaigns/{campaign}` | `admin.message-templates.campaigns.show` | MessageCampaignController@show | can_view |  |
| 1121 | PUT | `/{admin}/message-templates/campaigns/{campaign}/status` | `admin.message-templates.campaigns.status.update` | MessageCampaignController@cancel | can_update | 예약 취소 — 하위 자원(status) + 표준 접미사(update) |
| 1124 | GET | `/{admin}/message-templates/{messageTemplate}` | `admin.message-templates.show` | MessageTemplateController@show | can_view | 상세 = 수정 화면. 조회 권한으로 열어 CS 는 문구만 보고(설계서 공통 — CS 읽기 전용), 저장은 수정 권한(PUT)이 본다 |
| 1125 | PUT | `/{admin}/message-templates/{messageTemplate}` | `admin.message-templates.update` | MessageTemplateController@update | can_update |  |
| 1127 | POST | `/{admin}/message-templates/{messageTemplate}/test-sends` | `admin.message-templates.test-sends.store` | MessageTemplateController@testSend | can_create | 테스트 발송 — 하위자원(test-sends) + 표준 접미사(store). 건당 비용이 드는 실발송이라 횟수를 묶는다 |
| 1133 | GET | `/{admin}/sens-templates` | `admin.sens-templates.index` | SensTemplateController@index | can_view |  |
| 1135 | POST | `/{admin}/sens-templates/sync` | `admin.sens-templates.sync.store` | SensTemplateController@sync | can_create | [SENS 동기화] — 하위 자원(sync) + 표준 접미사(store). 최고 관리자만 실행한다(서비스가 다시 본다) · SENS 호출 한도 보호 |
| 1141 | GET | `/{admin}/verify-settings` | `admin.verify-settings.index` | VerifySettingController@index | can_view |  |
| 1142 | PUT | `/{admin}/verify-settings` | `admin.verify-settings.update` | VerifySettingController@update | can_update |  |
| 1143 | POST | `/{admin}/verify-settings/ip-exceptions` | `admin.verify-settings.ip-exceptions.store` | VerifySettingController@storeIpException | can_create |  |
| 1144 | DELETE | `/{admin}/verify-settings/ip-exceptions/{ipException}` | `admin.verify-settings.ip-exceptions.destroy` | VerifySettingController@destroyIpException | can_delete |  |
| 1146 | POST | `/{admin}/verify-settings/resets` | `admin.verify-settings.resets.store` | VerifySettingController@storeReset | can_create | 수동 초기화 — 하위 자원(resets) + 표준 접미사(store) |
| 1153 | GET | `/{admin}/player-settings` | `admin.player-settings.index` | PlayerSettingController@index | can_view |  |
| 1155 | GET | `/{admin}/player-settings/history` | `admin.player-settings.history.index` | PlayerSettingController@history | can_view | 정적 경로를 먼저 둔다. 변경 이력 · 재생 중 인원은 하위 자원 + 표준 접미사(index → can_view) |
| 1156 | GET | `/{admin}/player-settings/playing-count` | `admin.player-settings.playing-count.index` | PlayerSettingController@playingCount | can_view |  |
| 1157 | PUT | `/{admin}/player-settings` | `admin.player-settings.update` | PlayerSettingController@update | can_update |  |
| 1163 | GET | `/{admin}/site-settings` | `admin.site-settings.index` | SiteSettingController@edit | can_view |  |
| 1164 | PUT | `/{admin}/site-settings` | `admin.site-settings.update` | SiteSettingController@update | can_update |  |
| 1170 | GET | `/{admin}/terms` | `admin.terms.index` | TermController@index | can_view |  |
| 1172 | GET | `/{admin}/terms/history` | `admin.terms.history.index` | TermController@history | can_view | 종류별 버전 이력(ADMN-CONF-002) — 하위 자원(history) + 표준 접미사(index), 정적 경로라 {term} 보다 위 |
| 1173 | GET | `/{admin}/terms/create` | `admin.terms.create` | TermController@create | can_create |  |
| 1174 | POST | `/{admin}/terms` | `admin.terms.store` | TermController@store | can_create |  |
| 1175 | GET | `/{admin}/terms/{term}` | `admin.terms.show` | TermController@show | can_view |  |
| 1176 | GET | `/{admin}/terms/{term}/edit` | `admin.terms.edit` | TermController@edit | can_update |  |
| 1177 | PUT | `/{admin}/terms/{term}` | `admin.terms.update` | TermController@update | can_update |  |
| 1179 | DELETE | `/{admin}/terms/{term}` | `admin.terms.destroy` | TermController@destroy | can_delete | 작성 중인 개정본만 지운다 — 확정된 버전은 서비스가 막는다(설계서 ⑦ 레코드를 삭제하지 않는다) |
| 1186 | GET | `/{admin}/popups` | `admin.display.popups.index` | PopupController@index | can_view |  |
| 1187 | GET | `/{admin}/popups/create` | `admin.display.popups.create` | PopupController@create | can_create |  |
| 1188 | POST | `/{admin}/popups` | `admin.display.popups.store` | PopupController@store | can_create |  |
| 1190 | PUT | `/{admin}/popups/order` | `admin.display.popups.order.update` | PopupController@reorder | can_update | 순서 일괄 저장 — 하위자원(order) + 표준 접미사(update)로 권한 매핑(can_update) |
| 1191 | GET | `/{admin}/popups/{popup}/edit` | `admin.display.popups.edit` | PopupController@edit | can_update |  |
| 1192 | PUT | `/{admin}/popups/{popup}` | `admin.display.popups.update` | PopupController@update | can_update |  |
| 1193 | DELETE | `/{admin}/popups/{popup}` | `admin.display.popups.destroy` | PopupController@destroy | can_delete |  |
| 1199 | GET | `/{admin}/banners` | `admin.display.banners.index` | BannerController@index | can_view |  |
| 1200 | GET | `/{admin}/banners/create` | `admin.display.banners.create` | BannerController@create | can_create |  |
| 1201 | POST | `/{admin}/banners` | `admin.display.banners.store` | BannerController@store | can_create |  |
| 1203 | PUT | `/{admin}/banners/order` | `admin.display.banners.order.update` | BannerController@reorder | can_update | 순서 일괄 저장 — 하위자원(order) + 표준 접미사(update)로 권한 매핑(can_update) |
| 1204 | GET | `/{admin}/banners/{banner}/edit` | `admin.display.banners.edit` | BannerController@edit | can_update |  |
| 1205 | PUT | `/{admin}/banners/{banner}` | `admin.display.banners.update` | BannerController@update | can_update |  |
| 1206 | DELETE | `/{admin}/banners/{banner}` | `admin.display.banners.destroy` | BannerController@destroy | can_delete |  |
| 1213 | GET | `/{admin}/exam-targets/exam` | `admin.exam-targets.exam.index` | ExamTargetController@index | can_view |  |
| 1214 | GET | `/{admin}/exam-targets/exam/create` | `admin.exam-targets.exam.create` | ExamTargetController@create | can_create |  |
| 1215 | POST | `/{admin}/exam-targets/exam` | `admin.exam-targets.exam.store` | ExamTargetController@store | can_create |  |
| 1216 | GET | `/{admin}/exam-targets/exam/{examTarget}/edit` | `admin.exam-targets.exam.edit` | ExamTargetController@edit | can_update |  |
| 1217 | PUT | `/{admin}/exam-targets/exam/{examTarget}` | `admin.exam-targets.exam.update` | ExamTargetController@update | can_update |  |
| 1218 | DELETE | `/{admin}/exam-targets/exam/{examTarget}` | `admin.exam-targets.exam.destroy` | ExamTargetController@destroy | can_delete |  |
| 1225 | GET | `/{admin}/exam-targets/subject` | `admin.exam-targets.subject.index` | ExamTargetController@index | can_view |  |
| 1226 | GET | `/{admin}/exam-targets/subject/create` | `admin.exam-targets.subject.create` | ExamTargetController@create | can_create |  |
| 1227 | POST | `/{admin}/exam-targets/subject` | `admin.exam-targets.subject.store` | ExamTargetController@store | can_create |  |
| 1228 | GET | `/{admin}/exam-targets/subject/{examTarget}/edit` | `admin.exam-targets.subject.edit` | ExamTargetController@edit | can_update |  |
| 1229 | PUT | `/{admin}/exam-targets/subject/{examTarget}` | `admin.exam-targets.subject.update` | ExamTargetController@update | can_update |  |
| 1230 | DELETE | `/{admin}/exam-targets/subject/{examTarget}` | `admin.exam-targets.subject.destroy` | ExamTargetController@destroy | can_delete |  |
| 1237 | GET | `/{admin}/exam-targets/course` | `admin.exam-targets.course.index` | ExamTargetController@index | can_view |  |
| 1238 | GET | `/{admin}/exam-targets/course/create` | `admin.exam-targets.course.create` | ExamTargetController@create | can_create |  |
| 1239 | POST | `/{admin}/exam-targets/course` | `admin.exam-targets.course.store` | ExamTargetController@store | can_create |  |
| 1240 | GET | `/{admin}/exam-targets/course/{examTarget}/edit` | `admin.exam-targets.course.edit` | ExamTargetController@edit | can_update |  |
| 1241 | PUT | `/{admin}/exam-targets/course/{examTarget}` | `admin.exam-targets.course.update` | ExamTargetController@update | can_update |  |
| 1242 | DELETE | `/{admin}/exam-targets/course/{examTarget}` | `admin.exam-targets.course.destroy` | ExamTargetController@destroy | can_delete |  |
| 1249 | GET | `/{admin}/sales-stats` | `admin.sales-stats.index` | SalesStatController@index | can_view |  |
| 1250 | GET | `/{admin}/sales-stats/download` | `admin.sales-stats.download` | SalesStatController@download | can_download |  |
| 1257 | GET | `/{admin}/product-stats` | `admin.product-stats.index` | ProductStatController@index | can_view |  |
| 1258 | GET | `/{admin}/product-stats/download` | `admin.product-stats.download` | ProductStatController@download | can_download |  |
