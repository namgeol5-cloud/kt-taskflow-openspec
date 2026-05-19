from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth as auth_utils

router = APIRouter()


class CreateTaskRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


class UpdateStatusRequest(BaseModel):
    status: str


class UpdateTitleRequest(BaseModel):
    title: str
    assignee_id: Optional[int] = None


def task_to_dict(task: models.Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "team_id": task.team_id,
        "creator_id": task.creator_id,
        "creator_email": task.creator.email if task.creator else None,
        "assignee_id": task.assignee_id,
        "assignee_email": task.assignee.email if task.assignee else None,
        "created_at": task.created_at.isoformat(),
    }


@router.post("/teams/{team_id}/tasks", status_code=201)
def create_task(
    team_id: int,
    body: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    task = models.Task(
        title=body.title,
        team_id=team_id,
        creator_id=current_user.id,
        assignee_id=body.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.get("/teams/{team_id}/tasks")
def list_tasks(
    team_id: int,
    filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    q = db.query(models.Task).filter(models.Task.team_id == team_id)
    if filter == "me":
        q = q.filter(models.Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        q = q.filter(models.Task.assignee_id == None)
    tasks = q.order_by(models.Task.created_at.desc()).all()
    return [task_to_dict(t) for t in tasks]


@router.patch("/tasks/{task_id}/status")
def update_status(
    task_id: int,
    body: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    valid_statuses = {"TODO", "DOING", "DONE"}
    if body.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_STATUS", "message": "유효하지 않은 상태값입니다"}},
        )
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND"}})
    if current_user.team_id != task.team_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    task.status = body.status
    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.put("/tasks/{task_id}")
def update_title(
    task_id: int,
    body: UpdateTitleRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND"}})
    if current_user.team_id != task.team_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    task.title = body.title
    if "assignee_id" in body.model_fields_set:
        task.assignee_id = body.assignee_id
    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND"}})
    is_creator = task.creator_id == current_user.id
    is_owner = current_user.role == models.TeamRole.owner and current_user.team_id == task.team_id
    if not is_creator and not is_owner:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN"}})
    db.delete(task)
    db.commit()
