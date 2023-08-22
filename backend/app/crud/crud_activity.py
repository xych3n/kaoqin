from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.activity import Activity
from ..models import *
from ..schemas import ActivityCreate, ActivityUpdate
from .base import CRUDBase


class CRUDActivity(CRUDBase[Activity, ActivityCreate, ActivityUpdate]):
    def _filter_expression(self, filter: str = ""):
        return (Activity.title.like(f"%{filter}%")
                | Activity.date.like(f"%{filter}%")
                | (Activity.category == filter))

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, filter: str = "") -> Sequence[Activity]:
        return db.scalars(
            select(Activity)
            .where(self._filter_expression(filter))
            .order_by(Activity.date.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def remove(self, db: Session, *, db_obj: Activity) -> Activity:
        db.execute(
            delete(Particip)
            .where(Particip.activity_id == db_obj.id)
        )
        db.commit()
        return super().remove(db, db_obj=db_obj)


activity = CRUDActivity(Activity)
