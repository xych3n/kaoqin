from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from .. import crud, schemas
from ..core.security import create_access_token
from ..models import User
from ..deps import get_current_user, get_db


router = APIRouter()


@router.post("/login/access-token")
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.user.authenticate(db, student_number=form_data.username, password=form_data.password)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="Username does not exist or password is wrong")
    expires_delta = timedelta(days=1)
    return {
        "access_token": create_access_token(db_user.student_number, expires_delta),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: User = Depends(get_current_user)):
    return current_user
