# kanban-tasks Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 태스크 생성
팀 멤버는 TODO 컬럼에 태스크를 생성할 수 있어야 한다. assignee는 선택적이다(nullable).

#### Scenario: 정상 태스크 생성
- **WHEN** 팀 멤버가 title과 선택적 assignee_id로 POST /teams/{id}/tasks 요청
- **THEN** 201 Created + { id, team_id, title, status: "TODO", creator_id, assignee_id, created_at }

#### Scenario: 비멤버의 태스크 생성 시도
- **WHEN** 해당 팀에 속하지 않은 사용자가 POST /teams/{id}/tasks 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN" } }

### Requirement: 태스크 목록 조회 및 필터
팀 멤버는 팀의 태스크 목록을 조회할 수 있어야 한다. 전체/내 카드(@me)/미할당 필터와 최근 생성순 정렬을 지원해야 한다.

#### Scenario: 전체 태스크 조회
- **WHEN** GET /teams/{id}/tasks 요청 (filter 파라미터 없음)
- **THEN** 200 OK + 전체 태스크 배열, created_at DESC 정렬

#### Scenario: @me 필터
- **WHEN** GET /teams/{id}/tasks?filter=me 요청
- **THEN** 200 OK + assignee_id가 현재 사용자인 태스크만 반환

#### Scenario: 미할당 필터
- **WHEN** GET /teams/{id}/tasks?filter=unassigned 요청
- **THEN** 200 OK + assignee_id가 NULL인 태스크만 반환

### Requirement: 태스크 상태 변경 (드래그앤드롭)
팀 멤버는 태스크 상태를 TODO/DOING/DONE 간에 변경할 수 있어야 한다.

#### Scenario: 정상 상태 변경
- **WHEN** 팀 멤버가 { status: "DOING" }으로 PATCH /tasks/{id}/status 요청
- **THEN** 200 OK + 변경된 태스크 객체 반환

#### Scenario: 유효하지 않은 상태값
- **WHEN** TODO/DOING/DONE 외의 값으로 PATCH /tasks/{id}/status 요청
- **THEN** 400 Bad Request + { error: { code: "INVALID_STATUS" } }

### Requirement: 태스크 제목 수정
팀 멤버는 태스크 제목을 수정할 수 있어야 한다.

#### Scenario: 정상 제목 수정
- **WHEN** 팀 멤버가 { title: "새 제목" }으로 PUT /tasks/{id} 요청
- **THEN** 200 OK + 변경된 태스크 객체 반환

### Requirement: 태스크 삭제 및 권한
태스크 삭제는 생성자(creator) 또는 팀 owner만 가능하다. 그 외 멤버의 삭제 시도는 403을 반환해야 한다.

#### Scenario: 생성자가 삭제
- **WHEN** 태스크 creator_id와 일치하는 사용자가 DELETE /tasks/{id} 요청
- **THEN** 200 OK + { message: "deleted" }

#### Scenario: owner가 타인 카드 삭제
- **WHEN** 팀 owner가 타인 태스크에 DELETE /tasks/{id} 요청
- **THEN** 200 OK + { message: "deleted" }

#### Scenario: 일반 멤버가 타인 카드 삭제 시도
- **WHEN** creator도 owner도 아닌 멤버가 DELETE /tasks/{id} 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }

#### Scenario: 비멤버의 삭제 시도
- **WHEN** 해당 팀에 속하지 않은 사용자가 DELETE /tasks/{id} 요청
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN" } }

