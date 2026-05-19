## Context

TaskFlow MVP는 3-5인 소규모 팀을 위한 칸반+채팅 협업 도구다. Day 2 안에 완성해야 하므로 기술 선택의 기준은 "학습 단순 + 실전 배포 가능"이다. 현재 코드베이스 없음(그린필드). 로컬 개발 환경은 Windows + PowerShell이며, 배포 타깃은 Vercel + Neon이다.

## Goals / Non-Goals

**Goals:**
- FastAPI 단일 서버에서 HTML/JS 서빙 + API 제공 (로컬 일체형)
- 배포 시 Vercel Functions로 FastAPI 실행, Neon PostgreSQL 연결
- JWT 기반 인증, bcrypt 비밀번호 해시
- 칸반 드래그앤드롭 (Vanilla JS Drag API)
- 5초 폴링 채팅 (since 파라미터 증분 수신)
- 퍼블리싱 파일(docs/publishing/) 기반으로 프론트엔드 구현

**Non-Goals:**
- WebSocket 실시간 통신
- 파일 첨부, 전문 검색, 다국어
- pytest/jest 자동화 테스트
- 이메일/SMS/푸시 알림
- 마이크로서비스 분리

## Decisions

### 1. 백엔드: FastAPI (Python)
- **선택 이유**: SQLAlchemy ORM으로 SQLite↔PostgreSQL 전환이 connection string 하나로 처리됨. Node.js 대비 Neon 연동이 단순.
- **대안**: Express.js — ORM 설정 복잡도 증가, 선택 안 함.

### 2. DB: 로컬 SQLite / 배포 Neon
- **선택 이유**: `DATABASE_URL` 환경변수 하나로 양쪽 대응. Neon은 Vercel Storage에서 Pooled Connection URL 자동 주입.
- **스키마 변경 (스토리보드 결정 추적표 반영)**:
  - `users` 테이블에 `team_id` 컬럼 추가 (1인 1팀 제약 유지, DB 4테이블 유지)
  - `tasks` 테이블에 `assignee_id` 컬럼 추가 (nullable, FK → users)

### 3. API 설계 변경 (스토리보드 v2 결정)
- `PUT /tasks/{id}` 분리 → `PATCH /tasks/{id}/status` + `PUT /tasks/{id}` (title 수정)
- `GET /messages/{id}` 제거 → `GET /teams/{id}/messages?since=` 로 대체 (총 18개 유지)
- `POST /auth/logout` → 서버 stateless, 200만 반환 (블랙리스트 없음)

### 4. 인증: JWT HS256, 24h 만료, localStorage
- **선택 이유**: MVP 범위. refresh token 없음(만료 시 재로그인).
- CORS: Vercel 배포 도메인만 허용.

### 5. 프론트엔드: Vanilla JS + Tailwind CDN
- **선택 이유**: 빌드 툴 없이 StaticFiles 직접 서빙 가능. 학습 복잡도 최소화.
- 퍼블리싱 파일(`docs/publishing/`)을 그대로 `frontend/` 디렉토리로 이동하여 구현.
- 탭 구조: 칸반 / 채팅 / 멤버 (분리된 탭, 분할 화면 아님).

### 6. 배포: Vercel + Neon
- `vercel.json`으로 FastAPI를 Serverless Function으로 실행.
- Neon Pooled Connection URL은 Vercel 환경변수로 자동 주입.
- 로컬: `uvicorn main:app --reload`, 배포: Vercel Functions.

## Risks / Trade-offs

- **5초 폴링 부하** → MVP 범위(동시 50명 이내)에서는 Neon Free 티어 충분. 확장 시 WebSocket으로 교체.
- **JWT localStorage 저장** → XSS 취약. MVP 전제 조건(ACME Assumptions)으로 명시, 프로덕션 전 httpOnly cookie로 전환 필요.
- **SQLite → Neon 타입 불일치** → SQLAlchemy의 `String` 타입은 양쪽 호환. `AUTOINCREMENT` vs `SERIAL` 차이는 ORM이 추상화.
- **Vercel Function 콜드 스타트** → FastAPI 초기화 시간 ~500ms. 채팅 폴링 첫 호출 지연 가능. Fluid Compute로 인스턴스 재사용.

## Open Questions

- (해결됨) 칸반+채팅 레이아웃: 분할 화면 → **탭 전환** (스토리보드 v2 확정)
- (해결됨) PUT /tasks/{id} 중복: → **PATCH /status + PUT /title 분리** (스토리보드 결정)
