## Why

소규모 팀이 태스크 진행 상황과 팀 채팅을 하나의 화면에서 관리할 수 있는 협업 도구가 없어, 칸반과 커뮤니케이션 도구를 별도로 사용해야 하는 비효율이 발생한다. TaskFlow MVP는 칸반 보드와 팀 채팅을 단일 서비스로 통합해 Day 2 안에 Vercel 배포 가능한 수준으로 구현한다.

## What Changes

- **신규**: 이메일/비밀번호 기반 회원가입 및 로그인 (JWT 발급, bcrypt 해시)
- **신규**: 팀 생성, 초대코드 발급/합류, 멤버 목록 조회
- **신규**: 칸반 보드 — TODO/DOING/DONE 3컬럼, 태스크 추가/상태변경/삭제, assignee 지정, 드래그앤드롭
- **신규**: 팀 단위 채팅 — 5초 폴링, since 파라미터로 증분 수신, 1000자 제한
- **신규**: Vercel 배포 — FastAPI StaticFiles 로컬 일체형, Vercel + Neon 배포 환경

## Capabilities

### New Capabilities

- `user-auth`: 회원가입·로그인·JWT 발급·로그아웃 (POST /auth/signup, POST /auth/login, GET /auth/me, POST /auth/logout)
- `team-management`: 팀 생성·초대코드 발급·합류·멤버 목록 (POST /teams, GET /teams, POST /teams/join, GET /teams/{id}/members)
- `kanban-tasks`: 태스크 CRUD·상태 변경·assignee·드래그앤드롭 (POST/GET /teams/{id}/tasks, PATCH /tasks/{id}/status, PUT /tasks/{id}, DELETE /tasks/{id})
- `team-chat`: 팀 채팅 송수신·5초 폴링·since 증분 (POST/GET /teams/{id}/messages)
- `frontend-ui`: Vanilla JS + Tailwind 4개 화면 (로그인·회원가입·팀선택·칸반/채팅/멤버 탭)

### Modified Capabilities

## Impact

- **Backend**: FastAPI (Python) — 로컬 SQLite / 배포 Neon(PostgreSQL), SQLAlchemy ORM
- **Frontend**: Vanilla JS + Tailwind CDN — StaticFiles로 FastAPI에서 서빙
- **API**: 18개 엔드포인트 (Auth 4 + Team 4 + Task 5 + Chat 2 + 기타 3)
- **배포**: Vercel Functions + Vercel Storage Neon (Pooled Connection 자동 주입)
- **보안**: JWT HS256 24h, bcrypt, CORS 허용 도메인 명시
- **범위 외**: WebSocket, 파일첨부, 전문검색, 다국어, 테스트자동화, 이메일/푸시 알림
