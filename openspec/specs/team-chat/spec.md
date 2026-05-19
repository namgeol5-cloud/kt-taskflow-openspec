# team-chat Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 메시지 전송
팀 멤버는 1000자 이내의 텍스트 메시지를 팀 채팅에 전송할 수 있어야 한다.

#### Scenario: 정상 메시지 전송
- **WHEN** 팀 멤버가 1000자 이내 content로 POST /teams/{id}/messages 요청
- **THEN** 201 Created + { id, team_id, user_id, user_email, content, created_at } 반환

#### Scenario: 1000자 초과 메시지
- **WHEN** 1001자 이상의 content로 POST /teams/{id}/messages 요청
- **THEN** 400 Bad Request + { error: { code: "TOO_LONG", message: "메시지는 1000자 이내", limit: 1000, actual: <실제글자수> } }

#### Scenario: 비멤버의 메시지 전송 시도
- **WHEN** 해당 팀에 속하지 않은 사용자가 POST /teams/{id}/messages 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN" } }

### Requirement: 메시지 목록 조회 (5초 폴링)
팀 멤버는 팀의 채팅 메시지를 조회할 수 있어야 한다. 처음 진입 시 최근 50개, 이후 since 파라미터로 새 메시지만 증분 수신해야 한다.

#### Scenario: 최초 진입 - 전체 메시지 조회
- **WHEN** since 파라미터 없이 GET /teams/{id}/messages 요청
- **THEN** 200 OK + 최근 50개 메시지 배열 (created_at ASC 정렬)

#### Scenario: since 파라미터로 증분 조회
- **WHEN** GET /teams/{id}/messages?since=2026-05-13T14:30:00Z 요청
- **THEN** 200 OK + since 이후 생성된 메시지만 반환 (새 메시지 없으면 [] 반환)

#### Scenario: 빈 채팅방
- **WHEN** 메시지가 0건인 팀에 GET /teams/{id}/messages 요청
- **THEN** 200 OK + [] 빈 배열 반환

#### Scenario: 비멤버의 메시지 조회 시도
- **WHEN** 해당 팀에 속하지 않은 사용자가 GET /teams/{id}/messages 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN" } }

