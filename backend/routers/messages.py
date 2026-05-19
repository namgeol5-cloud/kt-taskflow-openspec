from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth as auth_utils

router = APIRouter()


class SendMessageRequest(BaseModel):
    content: str


def get_membership(db: Session, user_id: int, team_id: int):
    return db.query(models.TeamMember).filter(
        models.TeamMember.user_id == user_id,
        models.TeamMember.team_id == team_id,
    ).first()


def message_to_dict(msg: models.Message) -> dict:
    return {
        "id": msg.id,
        "team_id": msg.team_id,
        "user_id": msg.user_id,
        "user_email": msg.user.email if msg.user else None,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }


@router.post("/teams/{team_id}/messages", status_code=201)
def send_message(
    team_id: int,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not get_membership(db, current_user.id, team_id):
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    actual = len(body.content)
    if actual > 1000:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "TOO_LONG", "message": "메시지는 1000자 이내", "limit": 1000, "actual": actual}},
        )
    msg = models.Message(content=body.content, team_id=team_id, user_id=current_user.id)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return message_to_dict(msg)


@router.get("/teams/{team_id}/messages")
def list_messages(
    team_id: int,
    since: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not get_membership(db, current_user.id, team_id):
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    q = db.query(models.Message).filter(models.Message.team_id == team_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            q = q.filter(models.Message.created_at > since_dt)
        except ValueError:
            pass
    else:
        q = q.order_by(models.Message.created_at.desc()).limit(50)
        messages = q.all()
        messages.reverse()
        return [message_to_dict(m) for m in messages]

    messages = q.order_by(models.Message.created_at.asc()).all()
    return [message_to_dict(m) for m in messages]
