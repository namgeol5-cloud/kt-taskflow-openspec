## 1. 프로젝트 초기 설정

- [x] 1.1 FastAPI 프로젝트 디렉토리 구조 생성 (backend/, frontend/, vercel.json)
- [x] 1.2 Python 의존성 설치 (fastapi, uvicorn, sqlalchemy, python-jose, bcrypt, python-dotenv)
- [x] 1.3 SQLAlchemy 모델 정의 (users, teams, tasks, messages) — assignee_id, team_id 포함
- [x] 1.4 DATABASE_URL 환경변수 기반 DB 연결 설정 (SQLite 로컬 / Neon 배포 분기)
- [x] 1.5 Alembic 또는 create_all()로 테이블 초기화

## 2. 인증 API (user-auth)

- [x] 2.1 POST /auth/signup — bcrypt 해시, 중복 이메일 409, JWT 발급
- [x] 2.2 POST /auth/login — 비밀번호 검증, JWT 발급 (HS256, 24h)
- [x] 2.3 GET /auth/me — JWT 검증 미들웨어, 사용자 정보 반환
- [x] 2.4 POST /auth/logout — 200 반환 (stateless)
- [x] 2.5 JWT 의존성 함수 구현 (get_current_user) — 401/TOKEN_EXPIRED 처리

## 3. 팀 API (team-management)

- [x] 3.1 POST /teams — 팀 생성, XXXX-XXXX 초대코드 자동 발급
- [x] 3.2 GET /teams — 내 팀 목록 (users.team_id 기준)
- [x] 3.3 POST /teams/join — 초대코드 검증, team_id 갱신, 이미 소속 시 409
- [x] 3.4 GET /teams/{id}/members — 멤버만 접근 가능, role(owner/member) 포함

## 4. 칸반 태스크 API (kanban-tasks)

- [x] 4.1 POST /teams/{id}/tasks — 태스크 생성 (title, assignee_id nullable)
- [x] 4.2 GET /teams/{id}/tasks — 목록 조회, filter(me/unassigned) + created_at DESC 정렬
- [x] 4.3 PATCH /tasks/{id}/status — 상태 변경 (TODO/DOING/DONE 검증)
- [x] 4.4 PUT /tasks/{id} — 제목 수정
- [x] 4.5 DELETE /tasks/{id} — creator 또는 owner만 삭제, 타인 403

## 5. 채팅 API (team-chat)

- [x] 5.1 POST /teams/{id}/messages — 메시지 전송, 1000자 초과 시 400/TOO_LONG
- [x] 5.2 GET /teams/{id}/messages — 최근 50개 조회 / since 파라미터 증분 조회

## 6. 프론트엔드 — 인증 화면

- [x] 6.1 docs/publishing/login.html → frontend/login.html 기반으로 API 연동
- [x] 6.2 docs/publishing/signup.html → frontend/signup.html 기반으로 API 연동
- [x] 6.3 JWT localStorage 저장/삭제 유틸 함수 구현
- [x] 6.4 401 응답 시 자동 로그인 화면 리다이렉트 처리

## 7. 프론트엔드 — 팀 선택 화면

- [x] 7.1 docs/publishing/team.html → frontend/team.html 기반으로 GET /teams API 연동
- [x] 7.2 팀 만들기 POST /teams 연동
- [x] 7.3 초대코드 합류 POST /teams/join 연동 + 에러 처리

## 8. 프론트엔드 — 칸반 화면

- [x] 8.1 docs/publishing/kanban-chat.html → frontend/index.html 기반으로 GET /teams/{id}/tasks 연동
- [x] 8.2 필터(전체/@me/미할당) 클라이언트 사이드 적용
- [x] 8.3 인라인 태스크 추가 — POST /teams/{id}/tasks 연동
- [x] 8.4 드래그앤드롭 상태 변경 — PATCH /tasks/{id}/status 연동
- [x] 8.5 카드 상세 모달 — PUT /tasks/{id} (제목수정), DELETE /tasks/{id} (권한 확인) 연동
- [x] 8.6 빈 상태(empty state) 처리

## 9. 프론트엔드 — 채팅 화면

- [x] 9.1 채팅 탭 — GET /teams/{id}/messages 최초 로드
- [x] 9.2 5초 폴링 구현 (setInterval, since 파라미터)
- [x] 9.3 메시지 전송 POST /teams/{id}/messages 연동
- [x] 9.4 1000자 카운터 실시간 표시 + 초과 시 전송 버튼 비활성화
- [x] 9.5 빈 채팅 empty state 처리

## 10. FastAPI StaticFiles 서빙 (로컬 일체형)

- [x] 10.1 FastAPI에서 frontend/ 디렉토리를 StaticFiles로 마운트
- [x] 10.2 루트 경로(/) → login.html 리다이렉트 설정
- [x] 10.3 CORS 미들웨어 설정 (로컬 localhost + Vercel 배포 도메인)

## 11. Vercel 배포

- [x] 11.1 vercel.json 작성 (FastAPI → Python serverless function)
- [ ] 11.2 Vercel Storage에서 Neon PostgreSQL 프로비저닝  ← 사용자 직접 (Vercel 대시보드)
- [ ] 11.3 환경변수 설정 (DATABASE_URL, JWT_SECRET)  ← 사용자 직접 (Vercel 대시보드)
- [ ] 11.4 vercel deploy 실행 및 동작 확인 (회원가입 → 팀생성 → 칸반 → 채팅 전체 흐름)  ← 사용자 직접
