# user-auth Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 회원가입
시스템은 이메일과 비밀번호를 받아 계정을 생성하고 JWT를 발급해야 한다. 비밀번호는 bcrypt로 해시하여 저장해야 한다(평문 저장 금지). 비밀번호는 8자 이상이며 대문자·소문자·특수문자를 각각 1자 이상 포함해야 한다.

#### Scenario: 정상 회원가입
- **WHEN** 유효한 이메일과 규칙을 만족하는 비밀번호(8자 이상, 대문자·소문자·특수문자 포함)로 POST /auth/signup 요청
- **THEN** 201 Created + { token, user: { id, email } } 반환

#### Scenario: 중복 이메일 가입 시도
- **WHEN** 이미 존재하는 이메일로 POST /auth/signup 요청
- **THEN** 409 Conflict + { error: { code: "EMAIL_TAKEN", message: "이미 사용 중인 이메일입니다" } }

#### Scenario: 비밀번호 8자 미만
- **WHEN** 7자 이하 비밀번호로 POST /auth/signup 요청
- **THEN** 400 Bad Request + { error: { code: "INVALID_PASSWORD", message: "비밀번호는 8자 이상이어야 합니다" } }

#### Scenario: 대문자 미포함
- **WHEN** 대문자 없이 POST /auth/signup 요청 (예: "abcd1234!")
- **THEN** 400 Bad Request + { error: { code: "INVALID_PASSWORD", message: "비밀번호에 대문자를 포함해야 합니다" } }

#### Scenario: 소문자 미포함
- **WHEN** 소문자 없이 POST /auth/signup 요청 (예: "ABCD1234!")
- **THEN** 400 Bad Request + { error: { code: "INVALID_PASSWORD", message: "비밀번호에 소문자를 포함해야 합니다" } }

#### Scenario: 특수문자 미포함
- **WHEN** 특수문자 없이 POST /auth/signup 요청 (예: "Abcd1234")
- **THEN** 400 Bad Request + { error: { code: "INVALID_PASSWORD", message: "비밀번호에 특수문자를 포함해야 합니다" } }

### Requirement: 로그인
시스템은 이메일/비밀번호를 검증하고 JWT(24h 만료)를 발급해야 한다.

#### Scenario: 정상 로그인
- **WHEN** 등록된 이메일과 올바른 비밀번호로 POST /auth/login 요청
- **THEN** 200 OK + { token, user: { id, email } } 반환

#### Scenario: 잘못된 비밀번호
- **WHEN** 등록된 이메일에 틀린 비밀번호로 POST /auth/login 요청
- **THEN** 401 Unauthorized + { error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 올바르지 않습니다" } }

#### Scenario: 존재하지 않는 이메일
- **WHEN** 등록되지 않은 이메일로 POST /auth/login 요청
- **THEN** 401 Unauthorized + { error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 올바르지 않습니다" } }

### Requirement: 내 정보 조회
JWT가 유효한 경우 현재 로그인한 사용자의 정보를 반환해야 한다.

#### Scenario: 유효한 토큰으로 조회
- **WHEN** 유효한 JWT Bearer 토큰으로 GET /auth/me 요청
- **THEN** 200 OK + { id, email, created_at } 반환

#### Scenario: 토큰 없이 조회
- **WHEN** Authorization 헤더 없이 GET /auth/me 요청
- **THEN** 401 Unauthorized + { error: { code: "UNAUTHORIZED" } }

#### Scenario: JWT 만료
- **WHEN** 24시간 경과한 토큰으로 GET /auth/me 요청
- **THEN** 401 Unauthorized + { error: { code: "TOKEN_EXPIRED" } } → 클라이언트는 로그인 화면으로 redirect

### Requirement: 로그아웃
서버는 stateless이므로 200만 반환한다. 토큰 블랙리스트는 구현하지 않는다.

#### Scenario: 로그아웃 요청
- **WHEN** POST /auth/logout 요청 (토큰 유무 무관)
- **THEN** 200 OK + { message: "logged out" }

