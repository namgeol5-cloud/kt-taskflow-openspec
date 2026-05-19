import random
import string
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth as auth_utils

router = APIRouter()


def generate_invite_code() -> str:
    chars = string.ascii_uppercase + string.digits
    part = lambda: "".join(random.choices(chars, k=4))
    return f"{part()}-{part()}"


class CreateTeamRequest(BaseModel):
    name: str


class JoinTeamRequest(BaseModel):
    invite_code: str


@router.post("", status_code=201)
def create_team(
    body: CreateTeamRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    invite_code = generate_invite_code()
    while db.query(models.Team).filter(models.Team.invite_code == invite_code).first():
        invite_code = generate_invite_code()

    team = models.Team(name=body.name, invite_code=invite_code)
    db.add(team)
    db.flush()

    current_user.team_id = team.id
    current_user.role = models.TeamRole.owner
    db.commit()
    db.refresh(team)

    return {
        "id": team.id,
        "name": team.name,
        "invite_code": team.invite_code,
        "role": "owner",
    }


@router.get("")
def list_teams(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not current_user.team_id:
        return []
    team = db.query(models.Team).filter(models.Team.id == current_user.team_id).first()
    if not team:
        return []
    return [{"id": team.id, "name": team.name, "invite_code": team.invite_code, "role": current_user.role}]


@router.post("/join")
def join_team(
    body: JoinTeamRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    team = db.query(models.Team).filter(models.Team.invite_code == body.invite_code).first()
    if not team:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "TEAM_NOT_FOUND", "message": "유효하지 않은 초대코드입니다"}},
        )
    if current_user.team_id == team.id:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "ALREADY_MEMBER", "message": "이미 해당 팀에 소속되어 있습니다"}},
        )
    current_user.team_id = team.id
    current_user.role = models.TeamRole.member
    db.commit()
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "role": "member"}


@router.get("/{team_id}/members")
def list_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    members = db.query(models.User).filter(models.User.team_id == team_id).all()
    return [{"id": m.id, "email": m.email, "role": m.role} for m in members]
