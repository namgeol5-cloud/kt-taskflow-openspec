## ADDED Requirements

### Requirement: 팀 생성
인증된 사용자는 팀을 생성할 수 있어야 하며, 시스템은 유일한 초대코드(XXXX-XXXX 형식)를 자동 발급해야 한다. 팀을 생성한 사용자는 owner가 된다.

#### Scenario: 정상 팀 생성
- **WHEN** 인증된 사용자가 팀 이름으로 POST /teams 요청
- **THEN** 201 Created + { id, name, invite_code, owner_id } 반환 (invite_code 형식: ABCD-1234)

#### Scenario: 팀 이름 누락
- **WHEN** name 필드 없이 POST /teams 요청
- **THEN** 400 Bad Request + { error: { code: "MISSING_FIELD", message: "팀 이름을 입력해주세요" } }

### Requirement: 내 팀 목록 조회
인증된 사용자는 자신이 속한 팀 목록을 조회할 수 있어야 한다.

#### Scenario: 팀이 있는 경우
- **WHEN** 인증된 사용자가 GET /teams 요청
- **THEN** 200 OK + [{ id, name, invite_code, member_count }] 배열 반환

#### Scenario: 팀이 없는 경우
- **WHEN** 팀에 속하지 않은 사용자가 GET /teams 요청
- **THEN** 200 OK + [] 빈 배열 반환

### Requirement: 초대코드로 팀 합류
사용자는 유효한 초대코드를 입력해 팀에 합류할 수 있어야 한다. 이미 팀에 속한 경우 재합류를 막는다.

#### Scenario: 정상 합류
- **WHEN** 유효한 초대코드로 POST /teams/join 요청
- **THEN** 200 OK + { id, name, invite_code } 반환, users.team_id 갱신

#### Scenario: 잘못된 초대코드
- **WHEN** 존재하지 않는 초대코드로 POST /teams/join 요청
- **THEN** 404 Not Found + { error: { code: "INVALID_INVITE_CODE" } }

#### Scenario: 이미 다른 팀에 속한 경우
- **WHEN** team_id가 이미 있는 사용자가 POST /teams/join 요청
- **THEN** 409 Conflict + { error: { code: "ALREADY_IN_TEAM" } }

### Requirement: 팀 멤버 목록 조회
팀 멤버만 해당 팀의 멤버 목록을 조회할 수 있어야 한다.

#### Scenario: 정상 멤버 목록 조회
- **WHEN** 팀 멤버가 GET /teams/{id}/members 요청
- **THEN** 200 OK + [{ id, email, role }] 반환 (role: owner | member)

#### Scenario: 비멤버의 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 GET /teams/{id}/members 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN" } }
