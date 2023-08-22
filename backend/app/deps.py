from typing import Generator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED,HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from . import crud
from .core.security import SECRET_KEY
from .db.session import SessionLocal
from .models import User


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(OAuth2PasswordBearer("/api/v1/login/test-token")),
) -> User:
    try:
        payload = jwt.decode(token, key=SECRET_KEY)
        student_number = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    db_user = crud.user.get_by_student_number(db, student_number=student_number)
    if db_user is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return db_user


def get_current_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(HTTP_403_FORBIDDEN)
    return current_user
