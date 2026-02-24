# MoodPing 백엔드 백로그

---

## [MP-04] authentication 도메인 생성 (JWT)

카카오 로그인 후 JWT를 발급받은 사용자가 앱 진입 시 Bearer 토큰으로 현재 사용자 정보를 7일간 유효하게 조회한다. [MP-04]

| 항목 | 내용 |
|------|------|
| **담당** | 이후겸 (개발자 A) |
| **우선순위** | 🔴 Critical |
| **의존성** | MP-01 (account 도메인 필요) |
| **예상 시간** | 3시간 |

### 생성/수정 파일

- [ ] **authentication/jwt/jwt_handler.py**
  - `create_access_token(user_id, kakao_id)` → JWT 문자열 반환
  - `decode_token(token)` → payload dict 또는 None
- [ ] **authentication/service/authentication_service.py** (ABC)
  - `create_session(user_id, kakao_id)` → access token 문자열
  - `validate_session(token)` → user_id 또는 None
- [ ] **authentication/service/authentication_service_impl.py** (Singleton)
  - `AuthenticationService` 구현체, `get_instance()` 클래스 메서드
- [ ] **authentication/controller/authentication_controller.py**
  - `GET /auth/me` — 현재 로그인 사용자 정보 (Authorization: Bearer \<token\>)
- [ ] **app/main.py**
  - `authentication_router` import 및 `app.include_router(authentication_router)` 등록

### 비즈니스 규칙

- **JWT 만료**: 7일 (10080분)
- **Payload 필드**: `sub`(user_id), `kakao_id`, `exp`

### Success criteria

- [ ] **SC-1** 로그인 후 발급된 유효한 JWT를 `Authorization: Bearer <token>`으로 보내면 `GET /auth/me`가 200을 반환하고, 응답 본문에 해당 사용자의 `user_id`, `kakao_id`가 포함된다.
- [ ] **SC-2** Bearer 토큰 없이 또는 잘못된/만료된 토큰으로 `GET /auth/me`를 호출하면 401 Unauthorized가 반환된다.
- [ ] **SC-3** 발급 시점으로부터 7일(10080분) 이내의 토큰으로 `/auth/me`를 호출하면 정상적으로 사용자 정보가 반환되고, 7일이 지난 토큰으로 호출하면 401이 반환된다.
- [ ] **SC-4** JWT payload에 `sub`(user_id), `kakao_id`, `exp`가 포함되어 발급·검증된다.

### 완료 기준

- [ ] JWT 발급/검증이 7일 만료, 지정 payload로 동작
- [ ] `GET /auth/me` 호출 시 Bearer 토큰 검증 후 user_id, kakao_id 반환
- [ ] Service는 ABC + Singleton 구현체 구조 유지
- [ ] main.py에 라우터 등록되어 `/auth/me` 접근 가능

### 참고

- MP-01 완료 시 `account_service` 주입하여 `/auth/me` 응답에 nickname, profile_image 등 확장 가능 (authentication_controller 주석 참고)

---

*다른 티켓(MP-01, MP-02 등)은 동일 형식으로 이 문서에 추가하면 됩니다.*
