# frontend-ui Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 로그인/회원가입 화면
시스템은 로그인과 회원가입 화면을 제공해야 한다. 입력 검증은 클라이언트(실시간)와 서버(제출 시) 양쪽에서 수행해야 한다.

#### Scenario: 로그인 성공 후 리다이렉트
- **WHEN** 유효한 이메일/비밀번호로 로그인 성공
- **THEN** JWT를 localStorage에 저장하고 팀 선택 화면으로 이동

#### Scenario: 로그인 실패 메시지 표시
- **WHEN** 잘못된 자격증명으로 로그인 시도
- **THEN** 인라인 에러 메시지 표시 (화면 전환 없음)

#### Scenario: 버튼 처리 중 상태
- **WHEN** 로그인/가입하기 버튼 클릭 후 API 응답 대기 중
- **THEN** 버튼 텍스트 "처리 중..."으로 변경, 재클릭 불가

### Requirement: 팀 선택 화면
로그인 후 사용자는 자신이 속한 팀 목록을 보고 팀을 선택하거나, 새 팀을 만들거나, 초대코드로 합류할 수 있어야 한다.

#### Scenario: 팀 선택 후 칸반 이동
- **WHEN** 팀 목록에서 팀 카드를 클릭
- **THEN** 해당 팀의 칸반 화면(탭)으로 이동

#### Scenario: 초대코드 입력 및 합류
- **WHEN** 초대코드(XXXX-XXXX 형식) 입력 후 "팀 합류" 버튼 클릭
- **THEN** POST /teams/join 호출 성공 시 해당 팀 칸반으로 이동, 실패 시 인라인 에러

### Requirement: 칸반 화면 — 탭 구조
메인 화면은 칸반/채팅/멤버 3개 탭으로 구성되어야 한다. 칸반 탭이 기본 활성 상태다.

#### Scenario: 탭 전환
- **WHEN** 상단 탭 중 "채팅" 클릭
- **THEN** 채팅 탭 콘텐츠로 전환, 칸반 탭 숨김

#### Scenario: JWT 만료 시 자동 리다이렉트
- **WHEN** API 요청에서 401 응답 수신
- **THEN** localStorage에서 JWT 삭제 후 로그인 화면으로 이동

### Requirement: 칸반 보드 — 태스크 관리
칸반 탭은 TODO/DOING/DONE 3컬럼 보드를 표시해야 한다. 필터(전체/@me/미할당)와 정렬(최근 생성순)을 지원해야 한다.

#### Scenario: 태스크 드래그앤드롭 상태 변경
- **WHEN** 카드를 다른 컬럼으로 드래그해서 놓음
- **THEN** PATCH /tasks/{id}/status 호출, 성공 시 카드 해당 컬럼으로 이동, 목표 컬럼은 drag-over 하이라이트 + "↓ 여기에 놓기" 표시

#### Scenario: 인라인 태스크 추가
- **WHEN** 컬럼 헤더의 '+' 클릭 후 제목 입력, Enter 키 입력
- **THEN** POST /teams/{id}/tasks 호출, 성공 시 카드 추가, Esc로 취소

#### Scenario: 카드 클릭 — 상세 모달
- **WHEN** 태스크 카드 클릭
- **THEN** 상세 모달 열림 (상태 변경 버튼, 담당자, 생성자, 생성시각, 저장/삭제 버튼)

#### Scenario: 빈 컬럼 empty state
- **WHEN** 컬럼에 카드가 0개인 경우
- **THEN** TODO 컬럼은 "+ 첫 태스크 만들기" CTA 표시, DOING/DONE은 "드래그로 이동" 안내

### Requirement: 채팅 화면 — 폴링
채팅 탭은 말풍선 형태로 메시지를 표시하고 5초마다 새 메시지를 자동 수신해야 한다.

#### Scenario: 말풍선 레이아웃
- **WHEN** 채팅 탭 진입 시 메시지 목록 렌더링
- **THEN** 타인 메시지는 좌측, 본인 메시지는 우측 teal 색상 말풍선 표시. 각 말풍선 위에 "발신자 · 시각" 표시

#### Scenario: 5초 폴링 동작
- **WHEN** 채팅 탭 활성화 후 5초 경과
- **THEN** GET /teams/{id}/messages?since={마지막메시지시각} 호출, 새 메시지 있으면 화면 하단에 추가

#### Scenario: 1000자 초과 입력 시 전송 차단
- **WHEN** 입력창에 1000자 초과 입력
- **THEN** 글자수 카운터 빨간색 표시, 전송 버튼 비활성화

#### Scenario: 빈 채팅 empty state
- **WHEN** 메시지가 0건인 채팅 탭 진입
- **THEN** "아직 대화가 없습니다" + "첫 메시지를 보내 팀원과 대화를 시작하세요" 표시

