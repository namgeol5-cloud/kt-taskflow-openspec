from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth as auth_utils

router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def user_token_response(user: models.User) -> dict:
    token = auth_utils.create_access_token(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "email": user.email}}


@router.post("/signup", status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    error_msg = auth_utils.validate_password(body.password)
    if error_msg:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_PASSWORD", "message": error_msg}},
        )
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "EMAIL_TAKEN", "message": "이미 사용 중인 이메일입니다"}},
        )
    user = models.User(
        email=body.email,
        hashed_password=auth_utils.hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_token_response(user)


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth_utils.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 올바르지 않습니다"}},
        )
    return user_token_response(user)


@router.get("/me")
def me(current_user: models.User = Depends(auth_utils.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat(),
    }


@router.post("/logout")
def logout():
    return {"message": "logged out"}
