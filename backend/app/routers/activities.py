import dataclasses
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from .. import crud, schemas
from ..models import Activity, User
from ..deps import get_current_user, get_current_superuser, get_db


router = APIRouter()


@router.get("/", response_model=schemas.Pagination[schemas.ActivityDetail])
def read_activitis(
    db: Session = Depends(get_db),
    currend_user: User = Depends(get_current_user),
    *,
    skip: int = 0,
    limit: int = 100,
    filter: str = "",
) -> Any:
    db_activities = crud.activity.get_multi(db, skip=skip, limit=limit, filter=filter)
    return {
        "total": crud.activity.count(db, filter=filter),
        "list": [dataclasses.asdict(db_activity) | {"headcount": db_activity.headcount} for db_activity in db_activities]
    }


@router.put("/{id}", response_model=schemas.Activity)
def update_activity(
    db: Session = Depends(get_db),
    currend_user: User = Depends(get_current_superuser),
    *,
    id: int,
    activity_in: schemas.ActivityUpdate,
) -> Any:
    db_activity = db.get(Activity, id)
    if not db_activity:
        raise HTTPException(HTTP_404_NOT_FOUND, "activity not found")
    if db_activity.id != id:
        raise HTTPException(HTTP_403_FORBIDDEN, "different id of activity got")
    return crud.activity.update(db, db_obj=db_activity, obj_in=activity_in)


@router.delete("/{id}", response_model=schemas.Activity)
def delete_activity(
    db: Session = Depends(get_db),
    currend_user: User = Depends(get_current_superuser),
    *,
    id: int,
) -> Any:
    db_activity = db.get(Activity, id)
    if not db_activity:
        raise HTTPException(HTTP_404_NOT_FOUND, "activity not found")
    return crud.activity.remove(db, db_obj=db_activity)
