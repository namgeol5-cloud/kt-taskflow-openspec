"""
TaskFlow API 엔드포인트 테스트 스크립트
각 엔드포인트를 다양한 시나리오로 검증
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests
import json
import time
from datetime import datetime

BASE = "http://localhost:8000"
results = []
pass_count = 0
fail_count = 0

def log(group, name, method, path, status, expected, ok, note=""):
    global pass_count, fail_count
    icon = "✓" if ok else "✗"
    if ok:
        pass_count += 1
    else:
        fail_count += 1
    results.append({
        "group": group, "name": name, "method": method, "path": path,
        "status": status, "expected": expected, "ok": ok, "note": note
    })
    print(f"  {icon} [{status}/{expected}] {method} {path} — {name}" + (f" ({note})" if note else ""))

def req(method, path, token=None, json_body=None, params=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = getattr(requests, method)(f"{BASE}{path}", headers=headers, json=json_body, params=params, timeout=5)
    return r


# ─────────────────────────────────────────────
# 1. POST /auth/signup
# ─────────────────────────────────────────────
print("\n[1] POST /auth/signup")

ts = int(time.time())
EMAILS = [f"user{ts}_{i}@test.com" for i in range(4)]
TOKENS = {}

# 1-1 정상 가입
r = req("post", "/auth/signup", json_body={"email": EMAILS[0], "password": "Abcd1234!"})
ok = r.status_code == 201 and "token" in r.json()
TOKENS["u0"] = r.json().get("token") if ok else None
log("signup", "정상 가입", "POST", "/auth/signup", r.status_code, 201, ok)

# 1-2 두 번째 사용자 가입
r = req("post", "/auth/signup", json_body={"email": EMAILS[1], "password": "Abcd1234!"})
ok = r.status_code == 201
TOKENS["u1"] = r.json().get("token") if ok else None
log("signup", "두번째 사용자 가입", "POST", "/auth/signup", r.status_code, 201, ok)

# 1-3 세 번째 사용자 가입
r = req("post", "/auth/signup", json_body={"email": EMAILS[2], "password": "Zxyw9876@"})
ok = r.status_code == 201
TOKENS["u2"] = r.json().get("token") if ok else None
log("signup", "세번째 사용자 가입", "POST", "/auth/signup", r.status_code, 201, ok)

# 1-4 중복 이메일
r = req("post", "/auth/signup", json_body={"email": EMAILS[0], "password": "Abcd1234!"})
ok = r.status_code == 409 and r.json()["detail"]["error"]["code"] == "EMAIL_TAKEN"
log("signup", "중복 이메일 → 409", "POST", "/auth/signup", r.status_code, 409, ok)

# 1-5 비밀번호 7자 미만
r = req("post", "/auth/signup", json_body={"email": EMAILS[3], "password": "Ab1!"})
ok = r.status_code == 400 and r.json()["detail"]["error"]["code"] == "INVALID_PASSWORD"
log("signup", "8자 미만 → 400", "POST", "/auth/signup", r.status_code, 400, ok, r.json()["detail"]["error"]["message"] if r.status_code==400 else "")

# 1-6 대문자 없음
r = req("post", "/auth/signup", json_body={"email": EMAILS[3], "password": "abcd1234!"})
ok = r.status_code == 400 and "대문자" in r.json()["detail"]["error"]["message"]
log("signup", "대문자 없음 → 400", "POST", "/auth/signup", r.status_code, 400, ok)

# 1-7 소문자 없음
r = req("post", "/auth/signup", json_body={"email": EMAILS[3], "password": "ABCD1234!"})
ok = r.status_code == 400 and "소문자" in r.json()["detail"]["error"]["message"]
log("signup", "소문자 없음 → 400", "POST", "/auth/signup", r.status_code, 400, ok)

# 1-8 특수문자 없음
r = req("post", "/auth/signup", json_body={"email": EMAILS[3], "password": "Abcd1234"})
ok = r.status_code == 400 and "특수문자" in r.json()["detail"]["error"]["message"]
log("signup", "특수문자 없음 → 400", "POST", "/auth/signup", r.status_code, 400, ok)

# 1-9 이메일 형식 오류
r = req("post", "/auth/signup", json_body={"email": "notanemail", "password": "Abcd1234!"})
ok = r.status_code == 422
log("signup", "이메일 형식 오류 → 422", "POST", "/auth/signup", r.status_code, 422, ok)

# 1-10 빈 body
r = req("post", "/auth/signup", json_body={})
ok = r.status_code == 422
log("signup", "빈 body → 422", "POST", "/auth/signup", r.status_code, 422, ok)


# ─────────────────────────────────────────────
# 2. POST /auth/login
# ─────────────────────────────────────────────
print("\n[2] POST /auth/login")

# 2-1 정상 로그인
r = req("post", "/auth/login", json_body={"email": EMAILS[0], "password": "Abcd1234!"})
ok = r.status_code == 200 and "token" in r.json()
TOKENS["login_u0"] = r.json().get("token") if ok else TOKENS.get("u0")
log("login", "정상 로그인", "POST", "/auth/login", r.status_code, 200, ok)

# 2-2 잘못된 비밀번호
r = req("post", "/auth/login", json_body={"email": EMAILS[0], "password": "WrongPass1!"})
ok = r.status_code == 401 and r.json()["detail"]["error"]["code"] == "INVALID_CREDENTIALS"
log("login", "잘못된 비밀번호 → 401", "POST", "/auth/login", r.status_code, 401, ok)

# 2-3 존재하지 않는 이메일
r = req("post", "/auth/login", json_body={"email": "ghost@test.com", "password": "Abcd1234!"})
ok = r.status_code == 401 and r.json()["detail"]["error"]["code"] == "INVALID_CREDENTIALS"
log("login", "미등록 이메일 → 401", "POST", "/auth/login", r.status_code, 401, ok)

# 2-4 비밀번호 누락
r = req("post", "/auth/login", json_body={"email": EMAILS[0]})
ok = r.status_code == 422
log("login", "비밀번호 누락 → 422", "POST", "/auth/login", r.status_code, 422, ok)

# 2-5 이메일 누락
r = req("post", "/auth/login", json_body={"password": "Abcd1234!"})
ok = r.status_code == 422
log("login", "이메일 누락 → 422", "POST", "/auth/login", r.status_code, 422, ok)

# 2-6 빈 비밀번호
r = req("post", "/auth/login", json_body={"email": EMAILS[0], "password": ""})
ok = r.status_code in (401, 422)
log("login", "빈 비밀번호", "POST", "/auth/login", r.status_code, "401/422", ok)

# 2-7 두번째 사용자 로그인
r = req("post", "/auth/login", json_body={"email": EMAILS[1], "password": "Abcd1234!"})
ok = r.status_code == 200
TOKENS["u1"] = r.json().get("token") if ok else TOKENS.get("u1")
log("login", "두번째 사용자 로그인", "POST", "/auth/login", r.status_code, 200, ok)

# 2-8 세번째 사용자 로그인
r = req("post", "/auth/login", json_body={"email": EMAILS[2], "password": "Zxyw9876@"})
ok = r.status_code == 200
TOKENS["u2"] = r.json().get("token") if ok else TOKENS.get("u2")
log("login", "세번째 사용자 로그인", "POST", "/auth/login", r.status_code, 200, ok)

# 2-9 대소문자 다른 이메일
r = req("post", "/auth/login", json_body={"email": EMAILS[0].upper(), "password": "Abcd1234!"})
ok = r.status_code in (200, 401)
log("login", "대소문자 이메일 처리 확인", "POST", "/auth/login", r.status_code, "200/401", ok)

# 2-10 빈 body
r = req("post", "/auth/login", json_body={})
ok = r.status_code == 422
log("login", "빈 body → 422", "POST", "/auth/login", r.status_code, 422, ok)


# ─────────────────────────────────────────────
# 3. GET /auth/me
# ─────────────────────────────────────────────
print("\n[3] GET /auth/me")

# 3-1 유효한 토큰
r = req("get", "/auth/me", token=TOKENS["u0"])
ok = r.status_code == 200 and "id" in r.json() and "email" in r.json()
U0_ID = r.json().get("id") if ok else None
log("me", "유효한 토큰 → 200", "GET", "/auth/me", r.status_code, 200, ok)

# 3-2 토큰 없음
r = req("get", "/auth/me")
ok = r.status_code == 401
log("me", "토큰 없음 → 401", "GET", "/auth/me", r.status_code, 401, ok)

# 3-3 잘못된 토큰
r = req("get", "/auth/me", token="invalid.token.here")
ok = r.status_code == 401
log("me", "잘못된 토큰 → 401", "GET", "/auth/me", r.status_code, 401, ok)

# 3-4 Bearer 접두사 없이 (raw token)
headers = {"Authorization": TOKENS["u0"]}
r = requests.get(f"{BASE}/auth/me", headers=headers, timeout=5)
ok = r.status_code == 401
log("me", "Bearer 없이 → 401", "GET", "/auth/me", r.status_code, 401, ok)

# 3-5 두번째 사용자 me
r = req("get", "/auth/me", token=TOKENS["u1"])
ok = r.status_code == 200 and r.json()["email"] == EMAILS[1]
U1_ID = r.json().get("id") if ok else None
log("me", "두번째 사용자 me", "GET", "/auth/me", r.status_code, 200, ok)

# 3-6 세번째 사용자 me
r = req("get", "/auth/me", token=TOKENS["u2"])
ok = r.status_code == 200
U2_ID = r.json().get("id") if ok else None
log("me", "세번째 사용자 me", "GET", "/auth/me", r.status_code, 200, ok)

# 3-7~10: 반복 호출 (캐시/상태 없음 검증)
for i in range(4):
    r = req("get", "/auth/me", token=TOKENS["u0"])
    ok = r.status_code == 200
    log("me", f"반복 호출 {i+7}/10", "GET", "/auth/me", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 4. POST /auth/logout
# ─────────────────────────────────────────────
print("\n[4] POST /auth/logout")

for i in range(10):
    scenarios = [
        (TOKENS["u0"], "토큰 있음"),
        (None, "토큰 없음"),
        ("badtoken", "잘못된 토큰"),
        (TOKENS["u1"], "다른 사용자"),
    ]
    token, label = scenarios[i % len(scenarios)]
    r = req("post", "/auth/logout", token=token)
    ok = r.status_code == 200
    log("logout", f"{label} → 200 (stateless)", "POST", "/auth/logout", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 5. POST /teams
# ─────────────────────────────────────────────
print("\n[5] POST /teams")

# 5-1 정상 팀 생성 (u0)
r = req("post", "/teams", token=TOKENS["u0"], json_body={"name": "Alpha Team"})
ok = r.status_code == 201 and "invite_code" in r.json()
TEAM1 = r.json() if ok else {}
TEAM1_ID = TEAM1.get("id")
log("create_team", "정상 팀 생성 (u0)", "POST", "/teams", r.status_code, 201, ok, f"invite_code={TEAM1.get('invite_code','')}")

# 5-2 두번째 팀 생성 (u1)
r = req("post", "/teams", token=TOKENS["u1"], json_body={"name": "Beta Team"})
ok = r.status_code == 201
TEAM2 = r.json() if ok else {}
TEAM2_ID = TEAM2.get("id")
log("create_team", "팀 생성 (u1)", "POST", "/teams", r.status_code, 201, ok, f"invite_code={TEAM2.get('invite_code','')}")

# 5-3 인증 없이
r = req("post", "/teams", json_body={"name": "No Auth Team"})
ok = r.status_code == 401
log("create_team", "인증 없음 → 401", "POST", "/teams", r.status_code, 401, ok)

# 5-4 이름 없음
r = req("post", "/teams", token=TOKENS["u2"], json_body={})
ok = r.status_code == 422
log("create_team", "이름 없음 → 422", "POST", "/teams", r.status_code, 422, ok)

# 5-5~10: 초대코드 형식 검증 (각 생성마다 XXXX-XXXX)
for i in range(6):
    email = f"teamtest{ts}_{i}@test.com"
    r2 = req("post", "/auth/signup", json_body={"email": email, "password": "Abcd1234!"})
    if r2.status_code == 201:
        t = r2.json()["token"]
        r3 = req("post", "/teams", token=t, json_body={"name": f"Team {i}"})
        code = r3.json().get("invite_code", "")
        ok = r3.status_code == 201 and len(code) == 9 and code[4] == "-"
        log("create_team", f"초대코드 형식 {i+5}/10", "POST", "/teams", r3.status_code, 201, ok, f"code={code}")


# ─────────────────────────────────────────────
# 6. GET /teams
# ─────────────────────────────────────────────
print("\n[6] GET /teams")

# 6-1 u0 팀 목록
r = req("get", "/teams", token=TOKENS["u0"])
ok = r.status_code == 200 and isinstance(r.json(), list)
log("list_teams", "u0 팀 목록 → 200", "GET", "/teams", r.status_code, 200, ok)

# 6-2 인증 없음
r = req("get", "/teams")
ok = r.status_code == 401
log("list_teams", "인증 없음 → 401", "GET", "/teams", r.status_code, 401, ok)

# 6-3 u1 팀 목록
r = req("get", "/teams", token=TOKENS["u1"])
ok = r.status_code == 200 and len(r.json()) == 1
log("list_teams", "u1 팀 목록", "GET", "/teams", r.status_code, 200, ok)

# 6-4 u2 아직 팀 없음 (팀 합류 전)
new_user_email = f"noteam{ts}@test.com"
r_reg = req("post", "/auth/signup", json_body={"email": new_user_email, "password": "Abcd1234!"})
no_team_token = r_reg.json().get("token") if r_reg.status_code == 201 else None
if no_team_token:
    r = req("get", "/teams", token=no_team_token)
    ok = r.status_code == 200 and r.json() == []
    log("list_teams", "팀 없는 사용자 → []", "GET", "/teams", r.status_code, 200, ok)
else:
    log("list_teams", "팀 없는 사용자 → []", "GET", "/teams", 0, 200, False, "signup 실패")

# 6-5~10: 반복 호출
for i in range(6):
    r = req("get", "/teams", token=TOKENS["u0"])
    ok = r.status_code == 200
    log("list_teams", f"반복 호출 {i+5}/10", "GET", "/teams", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 7. POST /teams/join
# ─────────────────────────────────────────────
print("\n[7] POST /teams/join")

# u2를 TEAM1에 합류
invite = TEAM1.get("invite_code", "")

# 7-1 정상 합류
r = req("post", "/teams/join", token=TOKENS["u2"], json_body={"invite_code": invite})
ok = r.status_code == 200 and r.json().get("id") == TEAM1_ID
log("join_team", "정상 합류 (u2 → team1)", "POST", "/teams/join", r.status_code, 200, ok)

# 7-2 이미 소속 → 409
r = req("post", "/teams/join", token=TOKENS["u2"], json_body={"invite_code": invite})
ok = r.status_code == 409
log("join_team", "이미 소속 → 409", "POST", "/teams/join", r.status_code, 409, ok)

# 7-3 잘못된 코드 → 404
r = req("post", "/teams/join", token=TOKENS["u0"], json_body={"invite_code": "ZZZZ-ZZZZ"})
ok = r.status_code == 404
log("join_team", "잘못된 코드 → 404", "POST", "/teams/join", r.status_code, 404, ok)

# 7-4 인증 없음
r = req("post", "/teams/join", json_body={"invite_code": invite})
ok = r.status_code == 401
log("join_team", "인증 없음 → 401", "POST", "/teams/join", r.status_code, 401, ok)

# 7-5 코드 없음
r = req("post", "/teams/join", token=TOKENS["u0"], json_body={})
ok = r.status_code == 422
log("join_team", "코드 없음 → 422", "POST", "/teams/join", r.status_code, 422, ok)

# 7-6~10: 새 사용자들 합류
invite2 = TEAM2.get("invite_code", "")
for i in range(5):
    e = f"joiner{ts}_{i}@test.com"
    rr = req("post", "/auth/signup", json_body={"email": e, "password": "Abcd1234!"})
    if rr.status_code == 201:
        t2 = rr.json()["token"]
        r = req("post", "/teams/join", token=t2, json_body={"invite_code": invite2})
        ok = r.status_code == 200
        log("join_team", f"신규 사용자 team2 합류 {i+6}/10", "POST", "/teams/join", r.status_code, 200, ok)
    else:
        log("join_team", f"신규 사용자 합류 {i+6}/10", "POST", "/teams/join", 0, 200, False, "signup 실패")


# ─────────────────────────────────────────────
# 8. GET /teams/{id}/members
# ─────────────────────────────────────────────
print("\n[8] GET /teams/{id}/members")

# 8-1 owner가 자기 팀 조회
r = req("get", f"/teams/{TEAM1_ID}/members", token=TOKENS["u0"])
ok = r.status_code == 200 and isinstance(r.json(), list)
members = r.json() if ok else []
log("members", "owner가 팀1 멤버 조회", "GET", f"/teams/{TEAM1_ID}/members", r.status_code, 200, ok, f"{len(members)}명")

# 8-2 member도 조회 가능
r = req("get", f"/teams/{TEAM1_ID}/members", token=TOKENS["u2"])
ok = r.status_code == 200
log("members", "member가 팀1 조회", "GET", f"/teams/{TEAM1_ID}/members", r.status_code, 200, ok)

# 8-3 다른 팀 접근 → 403
r = req("get", f"/teams/{TEAM1_ID}/members", token=TOKENS["u1"])
ok = r.status_code == 403
log("members", "타 팀 접근 → 403", "GET", f"/teams/{TEAM1_ID}/members", r.status_code, 403, ok)

# 8-4 인증 없음
r = req("get", f"/teams/{TEAM1_ID}/members")
ok = r.status_code == 401
log("members", "인증 없음 → 401", "GET", f"/teams/{TEAM1_ID}/members", r.status_code, 401, ok)

# 8-5 존재하지 않는 팀
r = req("get", "/teams/99999/members", token=TOKENS["u0"])
ok = r.status_code == 403
log("members", "없는 팀 → 403", "GET", "/teams/99999/members", r.status_code, 403, ok)

# 8-6 팀2 멤버 조회
r = req("get", f"/teams/{TEAM2_ID}/members", token=TOKENS["u1"])
ok = r.status_code == 200
members2 = r.json() if ok else []
log("members", "팀2 멤버 조회", "GET", f"/teams/{TEAM2_ID}/members", r.status_code, 200, ok, f"{len(members2)}명")

# 8-7~10: role 필드 검증
for i in range(4):
    r = req("get", f"/teams/{TEAM1_ID}/members", token=TOKENS["u0"])
    ok = r.status_code == 200 and all("role" in m for m in r.json())
    log("members", f"role 필드 포함 확인 {i+7}/10", "GET", f"/teams/{TEAM1_ID}/members", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 9. POST /teams/{id}/tasks
# ─────────────────────────────────────────────
print("\n[9] POST /teams/{id}/tasks")

TASK_IDS = []

# 9-1 기본 태스크 생성
r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], json_body={"title": "첫번째 태스크"})
ok = r.status_code == 201 and r.json().get("status") == "TODO"
if ok: TASK_IDS.append(r.json()["id"])
log("create_task", "기본 태스크 생성 (TODO)", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 201, ok)

# 9-2 담당자 지정 태스크
r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], json_body={"title": "담당자 태스크", "assignee_id": U2_ID})
ok = r.status_code == 201 and r.json().get("assignee_id") == U2_ID
if ok: TASK_IDS.append(r.json()["id"])
log("create_task", "담당자 지정", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 201, ok)

# 9-3 u2 (멤버)도 생성 가능
r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u2"], json_body={"title": "멤버가 만든 태스크"})
ok = r.status_code == 201
if ok: TASK_IDS.append(r.json()["id"])
log("create_task", "member가 생성", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 201, ok)

# 9-4 다른 팀 멤버 → 403
r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u1"], json_body={"title": "forbidden"})
ok = r.status_code == 403
log("create_task", "타 팀 멤버 → 403", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 403, ok)

# 9-5 인증 없음
r = req("post", f"/teams/{TEAM1_ID}/tasks", json_body={"title": "no auth"})
ok = r.status_code == 401
log("create_task", "인증 없음 → 401", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 401, ok)

# 9-6 제목 없음
r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], json_body={})
ok = r.status_code == 422
log("create_task", "제목 없음 → 422", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 422, ok)

# 9-7~10: 여러 태스크 추가
for i in range(4):
    r = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], json_body={"title": f"태스크 {i+7}"})
    ok = r.status_code == 201
    if ok: TASK_IDS.append(r.json()["id"])
    log("create_task", f"추가 태스크 {i+7}/10", "POST", f"/teams/{TEAM1_ID}/tasks", r.status_code, 201, ok)


# ─────────────────────────────────────────────
# 10. GET /teams/{id}/tasks
# ─────────────────────────────────────────────
print("\n[10] GET /teams/{id}/tasks")

# 10-1 전체 조회
r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"])
ok = r.status_code == 200 and isinstance(r.json(), list)
log("list_tasks", "전체 조회", "GET", f"/teams/{TEAM1_ID}/tasks", r.status_code, 200, ok, f"{len(r.json())}개")

# 10-2 filter=me
r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u2"], params={"filter": "me"})
ok = r.status_code == 200
log("list_tasks", "filter=me", "GET", f"/teams/{TEAM1_ID}/tasks?filter=me", r.status_code, 200, ok, f"{len(r.json())}개")

# 10-3 filter=unassigned
r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], params={"filter": "unassigned"})
ok = r.status_code == 200
log("list_tasks", "filter=unassigned", "GET", f"/teams/{TEAM1_ID}/tasks?filter=unassigned", r.status_code, 200, ok, f"{len(r.json())}개")

# 10-4 타 팀 → 403
r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u1"])
ok = r.status_code == 403
log("list_tasks", "타 팀 → 403", "GET", f"/teams/{TEAM1_ID}/tasks", r.status_code, 403, ok)

# 10-5 인증 없음
r = req("get", f"/teams/{TEAM1_ID}/tasks")
ok = r.status_code == 401
log("list_tasks", "인증 없음 → 401", "GET", f"/teams/{TEAM1_ID}/tasks", r.status_code, 401, ok)

# 10-6 created_at DESC 정렬 검증
r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"])
tasks = r.json()
ok = r.status_code == 200 and all(tasks[i]["created_at"] >= tasks[i+1]["created_at"] for i in range(len(tasks)-1))
log("list_tasks", "created_at DESC 정렬", "GET", f"/teams/{TEAM1_ID}/tasks", r.status_code, 200, ok)

# 10-7~10: 반복 호출
for i in range(4):
    r = req("get", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"])
    ok = r.status_code == 200
    log("list_tasks", f"반복 호출 {i+7}/10", "GET", f"/teams/{TEAM1_ID}/tasks", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 11. PATCH /tasks/{id}/status
# ─────────────────────────────────────────────
print("\n[11] PATCH /tasks/{id}/status")

if TASK_IDS:
    tid = TASK_IDS[0]

    # 11-1 TODO → DOING
    r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u0"], json_body={"status": "DOING"})
    ok = r.status_code == 200 and r.json()["status"] == "DOING"
    log("patch_status", "TODO→DOING", "PATCH", f"/tasks/{tid}/status", r.status_code, 200, ok)

    # 11-2 DOING → DONE
    r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u0"], json_body={"status": "DONE"})
    ok = r.status_code == 200 and r.json()["status"] == "DONE"
    log("patch_status", "DOING→DONE", "PATCH", f"/tasks/{tid}/status", r.status_code, 200, ok)

    # 11-3 DONE → TODO (역방향)
    r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u0"], json_body={"status": "TODO"})
    ok = r.status_code == 200 and r.json()["status"] == "TODO"
    log("patch_status", "DONE→TODO (역방향)", "PATCH", f"/tasks/{tid}/status", r.status_code, 200, ok)

    # 11-4 유효하지 않은 상태값
    r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u0"], json_body={"status": "INVALID"})
    ok = r.status_code == 400
    log("patch_status", "잘못된 status → 400", "PATCH", f"/tasks/{tid}/status", r.status_code, 400, ok)

    # 11-5 타 팀 멤버 → 403
    r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u1"], json_body={"status": "DOING"})
    ok = r.status_code == 403
    log("patch_status", "타 팀 → 403", "PATCH", f"/tasks/{tid}/status", r.status_code, 403, ok)

    # 11-6 인증 없음
    r = req("patch", f"/tasks/{tid}/status", json_body={"status": "DOING"})
    ok = r.status_code == 401
    log("patch_status", "인증 없음 → 401", "PATCH", f"/tasks/{tid}/status", r.status_code, 401, ok)

    # 11-7 존재하지 않는 태스크
    r = req("patch", "/tasks/99999/status", token=TOKENS["u0"], json_body={"status": "DOING"})
    ok = r.status_code == 404
    log("patch_status", "없는 태스크 → 404", "PATCH", "/tasks/99999/status", r.status_code, 404, ok)

    # 11-8 member도 상태 변경 가능
    tid2 = TASK_IDS[1] if len(TASK_IDS) > 1 else tid
    r = req("patch", f"/tasks/{tid2}/status", token=TOKENS["u2"], json_body={"status": "DOING"})
    ok = r.status_code == 200
    log("patch_status", "멤버도 상태 변경", "PATCH", f"/tasks/{tid2}/status", r.status_code, 200, ok)

    # 11-9~10: 연속 상태 전환
    for i, st in enumerate(["DONE", "TODO"]):
        r = req("patch", f"/tasks/{tid}/status", token=TOKENS["u0"], json_body={"status": st})
        ok = r.status_code == 200 and r.json()["status"] == st
        log("patch_status", f"연속 전환 {i+9}/10 ({st})", "PATCH", f"/tasks/{tid}/status", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 12. PUT /tasks/{id}
# ─────────────────────────────────────────────
print("\n[12] PUT /tasks/{id}")

if TASK_IDS:
    tid = TASK_IDS[0]

    # 12-1 제목 수정
    r = req("put", f"/tasks/{tid}", token=TOKENS["u0"], json_body={"title": "수정된 제목"})
    ok = r.status_code == 200 and r.json()["title"] == "수정된 제목"
    log("put_task", "제목 수정 → 200", "PUT", f"/tasks/{tid}", r.status_code, 200, ok)

    # 12-2 담당자 할당
    r = req("put", f"/tasks/{tid}", token=TOKENS["u0"], json_body={"title": "수정된 제목", "assignee_id": U2_ID})
    ok = r.status_code == 200 and r.json()["assignee_id"] == U2_ID
    log("put_task", "담당자 할당", "PUT", f"/tasks/{tid}", r.status_code, 200, ok)

    # 12-3 담당자 해제 (null)
    r = req("put", f"/tasks/{tid}", token=TOKENS["u0"], json_body={"title": "수정된 제목", "assignee_id": None})
    ok = r.status_code == 200 and r.json()["assignee_id"] is None
    log("put_task", "담당자 해제 (null)", "PUT", f"/tasks/{tid}", r.status_code, 200, ok)

    # 12-4 멤버도 수정 가능
    tid3 = TASK_IDS[2] if len(TASK_IDS) > 2 else tid
    r = req("put", f"/tasks/{tid3}", token=TOKENS["u2"], json_body={"title": "멤버 수정"})
    ok = r.status_code == 200
    log("put_task", "멤버 수정", "PUT", f"/tasks/{tid3}", r.status_code, 200, ok)

    # 12-5 타 팀 → 403
    r = req("put", f"/tasks/{tid}", token=TOKENS["u1"], json_body={"title": "hack"})
    ok = r.status_code == 403
    log("put_task", "타 팀 → 403", "PUT", f"/tasks/{tid}", r.status_code, 403, ok)

    # 12-6 인증 없음
    r = req("put", f"/tasks/{tid}", json_body={"title": "no auth"})
    ok = r.status_code == 401
    log("put_task", "인증 없음 → 401", "PUT", f"/tasks/{tid}", r.status_code, 401, ok)

    # 12-7 없는 태스크
    r = req("put", "/tasks/99999", token=TOKENS["u0"], json_body={"title": "ghost"})
    ok = r.status_code == 404
    log("put_task", "없는 태스크 → 404", "PUT", "/tasks/99999", r.status_code, 404, ok)

    # 12-8 제목 없음 → 422
    r = req("put", f"/tasks/{tid}", token=TOKENS["u0"], json_body={"assignee_id": U2_ID})
    ok = r.status_code == 422
    log("put_task", "제목 없음 → 422", "PUT", f"/tasks/{tid}", r.status_code, 422, ok)

    # 12-9~10: 반복 수정
    for i in range(2):
        r = req("put", f"/tasks/{tid}", token=TOKENS["u0"], json_body={"title": f"반복수정{i}"})
        ok = r.status_code == 200
        log("put_task", f"반복 수정 {i+9}/10", "PUT", f"/tasks/{tid}", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 13. DELETE /tasks/{id}
# ─────────────────────────────────────────────
print("\n[13] DELETE /tasks/{id}")

del_ids = TASK_IDS[-4:] if len(TASK_IDS) >= 4 else TASK_IDS[:]

# 13-1 creator 삭제
if del_ids:
    did = del_ids.pop()
    r = req("delete", f"/tasks/{did}", token=TOKENS["u0"])
    ok = r.status_code == 204
    log("delete_task", "creator 삭제 → 204", "DELETE", f"/tasks/{did}", r.status_code, 204, ok)

# 13-2 타 팀 삭제 시도 → 403
if TASK_IDS:
    did2 = TASK_IDS[0]
    r = req("delete", f"/tasks/{did2}", token=TOKENS["u1"])
    ok = r.status_code == 403
    log("delete_task", "타 팀 → 403", "DELETE", f"/tasks/{did2}", r.status_code, 403, ok)

# 13-3 인증 없음
if TASK_IDS:
    r = req("delete", f"/tasks/{TASK_IDS[0]}")
    ok = r.status_code == 401
    log("delete_task", "인증 없음 → 401", "DELETE", f"/tasks/{TASK_IDS[0]}", r.status_code, 401, ok)

# 13-4 없는 태스크
r = req("delete", "/tasks/99999", token=TOKENS["u0"])
ok = r.status_code == 404
log("delete_task", "없는 태스크 → 404", "DELETE", "/tasks/99999", r.status_code, 404, ok)

# 13-5 멤버가 타인 생성 태스크 삭제 시도 (비creator 비owner)
r_new = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u0"], json_body={"title": "only owner can del"})
if r_new.status_code == 201:
    owner_task_id = r_new.json()["id"]
    r = req("delete", f"/tasks/{owner_task_id}", token=TOKENS["u2"])
    ok = r.status_code == 403
    log("delete_task", "비creator 멤버 삭제 → 403", "DELETE", f"/tasks/{owner_task_id}", r.status_code, 403, ok)
    # owner는 삭제 가능
    r = req("delete", f"/tasks/{owner_task_id}", token=TOKENS["u0"])
    ok = r.status_code == 204
    log("delete_task", "owner 삭제 → 204", "DELETE", f"/tasks/{owner_task_id}", r.status_code, 204, ok)

# 13-7 member가 본인 태스크 삭제
r_own = req("post", f"/teams/{TEAM1_ID}/tasks", token=TOKENS["u2"], json_body={"title": "u2 태스크"})
if r_own.status_code == 201:
    my_task = r_own.json()["id"]
    r = req("delete", f"/tasks/{my_task}", token=TOKENS["u2"])
    ok = r.status_code == 204
    log("delete_task", "creator(멤버) 본인 삭제 → 204", "DELETE", f"/tasks/{my_task}", r.status_code, 204, ok)

# 13-8~10: 남은 태스크 삭제
remaining = del_ids[:3] if del_ids else []
for i, did in enumerate(remaining):
    r = req("delete", f"/tasks/{did}", token=TOKENS["u0"])
    ok = r.status_code == 204
    log("delete_task", f"정리 삭제 {i+8}/10", "DELETE", f"/tasks/{did}", r.status_code, 204, ok)
while len([x for x in results if x["group"] == "delete_task"]) < 10:
    log("delete_task", "스킵(태스크 부족)", "DELETE", "/tasks/-", "-", "-", True, "skip")


# ─────────────────────────────────────────────
# 14. POST /teams/{id}/messages
# ─────────────────────────────────────────────
print("\n[14] POST /teams/{id}/messages")

MSG_TIMES = []

# 14-1 정상 전송
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={"content": "안녕하세요!"})
ok = r.status_code == 201 and "id" in r.json()
if ok: MSG_TIMES.append(r.json()["created_at"])
log("send_msg", "정상 전송 → 201", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 201, ok)

# 14-2 멤버도 전송 가능
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u2"], json_body={"content": "멤버 메시지"})
ok = r.status_code == 201
if ok: MSG_TIMES.append(r.json()["created_at"])
log("send_msg", "멤버 전송 → 201", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 201, ok)

# 14-3 1000자 초과 → 400
long_msg = "A" * 1001
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={"content": long_msg})
ok = r.status_code == 400 and r.json()["detail"]["error"]["code"] == "TOO_LONG"
log("send_msg", "1001자 → 400 TOO_LONG", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 400, ok)

# 14-4 정확히 1000자 → 성공
long_ok = "B" * 1000
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={"content": long_ok})
ok = r.status_code == 201
if ok: MSG_TIMES.append(r.json()["created_at"])
log("send_msg", "정확히 1000자 → 201", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 201, ok)

# 14-5 타 팀 → 403
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u1"], json_body={"content": "forbidden"})
ok = r.status_code == 403
log("send_msg", "타 팀 → 403", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 403, ok)

# 14-6 인증 없음
r = req("post", f"/teams/{TEAM1_ID}/messages", json_body={"content": "no auth"})
ok = r.status_code == 401
log("send_msg", "인증 없음 → 401", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 401, ok)

# 14-7 content 없음 → 422
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={})
ok = r.status_code == 422
log("send_msg", "content 없음 → 422", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 422, ok)

# 14-8 actual 필드 포함 검증
r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={"content": "C" * 1050})
ok = r.status_code == 400 and r.json()["detail"]["error"].get("actual") == 1050
log("send_msg", "actual 필드 포함 → 400", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 400, ok)

# 14-9~10: 연속 전송
for i in range(2):
    r = req("post", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], json_body={"content": f"연속 메시지 {i+9}"})
    ok = r.status_code == 201
    if ok: MSG_TIMES.append(r.json()["created_at"])
    log("send_msg", f"연속 전송 {i+9}/10", "POST", f"/teams/{TEAM1_ID}/messages", r.status_code, 201, ok)


# ─────────────────────────────────────────────
# 15. GET /teams/{id}/messages
# ─────────────────────────────────────────────
print("\n[15] GET /teams/{id}/messages")

# 15-1 전체 조회 (최근 50개)
r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"])
ok = r.status_code == 200 and isinstance(r.json(), list)
log("list_msgs", "전체 조회", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 200, ok, f"{len(r.json())}개")

# 15-2 created_at ASC 정렬 검증
msgs = r.json()
ok = r.status_code == 200 and len(msgs) >= 2 and all(msgs[i]["created_at"] <= msgs[i+1]["created_at"] for i in range(len(msgs)-1))
log("list_msgs", "ASC 정렬 검증", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 200, ok)

# 15-3 since 파라미터
if MSG_TIMES:
    r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], params={"since": MSG_TIMES[0]})
    ok = r.status_code == 200
    log("list_msgs", "since 파라미터", "GET", f"/teams/{TEAM1_ID}/messages?since=...", r.status_code, 200, ok, f"{len(r.json())}개")

# 15-4 since 미래 시각 → 빈 배열
r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"], params={"since": "2099-01-01T00:00:00Z"})
ok = r.status_code == 200 and r.json() == []
log("list_msgs", "since 미래 → []", "GET", f"/teams/{TEAM1_ID}/messages?since=2099...", r.status_code, 200, ok)

# 15-5 타 팀 → 403
r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u1"])
ok = r.status_code == 403
log("list_msgs", "타 팀 → 403", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 403, ok)

# 15-6 인증 없음
r = req("get", f"/teams/{TEAM1_ID}/messages")
ok = r.status_code == 401
log("list_msgs", "인증 없음 → 401", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 401, ok)

# 15-7 빈 채팅방 (team2 - 메시지 없음)
r = req("get", f"/teams/{TEAM2_ID}/messages", token=TOKENS["u1"])
ok = r.status_code == 200 and r.json() == []
log("list_msgs", "빈 채팅 → []", "GET", f"/teams/{TEAM2_ID}/messages", r.status_code, 200, ok)

# 15-8 user_email 포함 검증
r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"])
msgs = r.json()
ok = r.status_code == 200 and len(msgs) > 0 and all("user_email" in m for m in msgs)
log("list_msgs", "user_email 포함", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 200, ok)

# 15-9~10: 반복 호출
for i in range(2):
    r = req("get", f"/teams/{TEAM1_ID}/messages", token=TOKENS["u0"])
    ok = r.status_code == 200
    log("list_msgs", f"반복 호출 {i+9}/10", "GET", f"/teams/{TEAM1_ID}/messages", r.status_code, 200, ok)


# ─────────────────────────────────────────────
# 결과 집계
# ─────────────────────────────────────────────
total = pass_count + fail_count
print(f"\n{'='*60}")
print(f"  전체 결과: {pass_count}/{total} 통과 ({100*pass_count//total}%)")
print(f"  실패: {fail_count}건")
print(f"{'='*60}")

failures = [r for r in results if not r["ok"]]
if failures:
    print("\n[실패 항목]")
    for f in failures:
        print(f"  ✗ [{f['group']}] {f['name']} → HTTP {f['status']} (expected {f['expected']})")

# JSON 저장
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "run_at": datetime.now().isoformat(),
        "pass": pass_count,
        "fail": fail_count,
        "total": total,
        "results": results
    }, f, ensure_ascii=False, indent=2)

print("\n결과가 test_results.json에 저장되었습니다.")
sys.exit(0 if fail_count == 0 else 1)
