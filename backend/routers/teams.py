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


def get_membership(db: Session, user_id: int, team_id: int):
    return db.query(models.TeamMember).filter(
        models.TeamMember.user_id == user_id,
        models.TeamMember.team_id == team_id,
    ).first()


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

    membership = models.TeamMember(
        user_id=current_user.id,
        team_id=team.id,
        role=models.TeamRole.owner,
    )
    db.add(membership)
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
    memberships = db.query(models.TeamMember).filter(
        models.TeamMember.user_id == current_user.id
    ).all()
    result = []
    for m in memberships:
        team = db.query(models.Team).filter(models.Team.id == m.team_id).first()
        if team:
            result.append({
                "id": team.id,
                "name": team.name,
                "invite_code": team.invite_code,
                "role": m.role,
            })
    return result


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
    existing = get_membership(db, current_user.id, team.id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "ALREADY_MEMBER", "message": "이미 해당 팀에 소속되어 있습니다"}},
        )
    membership = models.TeamMember(
        user_id=current_user.id,
        team_id=team.id,
        role=models.TeamRole.member,
    )
    db.add(membership)
    db.commit()
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "role": "member"}


@router.get("/{team_id}/members")
def list_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not get_membership(db, current_user.id, team_id):
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    memberships = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id
    ).all()
    return [
        {"id": m.user.id, "email": m.user.email, "role": m.role}
        for m in memberships
    ]
