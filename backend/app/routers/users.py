import dataclasses
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from .. import crud, schemas
from ..models import User
from ..deps import get_current_user, get_current_superuser, get_db


router = APIRouter()


@router.get("/", response_model=schemas.Pagination[schemas.UserDetail])
def read_users(
    db: Session = Depends(get_db),
    currend_user: User = Depends(get_current_user),
    *,
    skip: int = 0,
    limit: int = 100,
    filter: str = "",
) -> Any:
    db_users = crud.user.get_multi(db, skip=skip, limit=limit, filter=filter)
    return {
        "total": crud.user.count(db, filter=filter),
        "list": [dataclasses.asdict(db_user) | {"involvements": db_user.involvements} for db_user in db_users]
    }


@router.get("/me", response_model=schemas.UserDetail)
def read_me(
    db: Session = Depends(get_db),
    currend_user: User = Depends(get_current_user),
) -> Any:
    db_user = crud.user.get_by_student_number(db, student_number=currend_user.student_number)
    assert db_user is not None
    return dataclasses.asdict(db_user) | {"involvements": db_user.involvements}


@router.put("/{student_number}/reset-password", response_model=schemas.User)
def reset_password(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    *,
    student_number: str,
    new_password: str = "",
) -> Any:
    db_user = crud.user.get_by_student_number(db, student_number=student_number)
    if db_user is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User not exists")
    if current_user.id != db_user.id and not current_user.is_superuser:
        raise HTTPException(HTTP_403_FORBIDDEN, detail="No permission to perform this operation")
    return crud.user.reset_password(db, db_user=db_user, new_password=new_password)


@router.put("/{student_number}/set-superuser", response_model=schemas.User)
def set_superuser(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    *,
    student_number: str,
    is_superuser: bool = False,
) -> Any:
    db_user = crud.user.get_by_student_number(db, student_number=student_number)
    if db_user is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User not exists")
    db_user.is_superuser = is_superuser
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
