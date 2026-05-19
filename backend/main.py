import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect as sa_inspect
from .database import engine
from . import models
from .routers import auth, teams, tasks, messages

# team_members 테이블이 없으면 구 스키마 → 전체 리셋 후 재생성
_inspector = sa_inspect(engine)
if "team_members" not in _inspector.get_table_names():
    models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(messages.router, tags=["messages"])

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def root():
        return RedirectResponse(url="/static/login.html")
