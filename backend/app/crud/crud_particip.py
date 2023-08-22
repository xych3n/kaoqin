from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions as func

from ..models import *
from ..schemas import ParticipCreate, ParticipUpdate
from .base import CRUDBase


class CRUDParticip(CRUDBase[Particip, ParticipCreate, ParticipUpdate]):
    def _filter_expression(self, filter: str = ""):
        return (
            User.student_number.like(f"%{filter}%")
            | User.name.like(f"%{filter}%")
            | Activity.title.like(f"%{filter}%")
            | Activity.date.like(f"%{filter}%")
            | (Activity.category == filter)
        )

    def count(self, db: Session, *, filter: str = "") -> Optional[int]:
        return db.scalar(
            select(func.count())
            .join(Activity)
            .join(User)
            .where(self._filter_expression(filter))
            .select_from(Particip)
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, filter: str = "",
    ) -> Sequence[Particip]:
        return db.scalars(
            select(Particip)
            .join(Activity)
            .join(User)
            .where(self._filter_expression(filter))
            .order_by(Activity.date.desc(), Activity.category, Activity.title, User.student_number)
            .offset(skip)
            .limit(limit)
        ).all()

    def get(self, db: Session, *, activity_id: int, user_id: int):
        return db.scalar(select(Particip).where((Particip.activity_id == activity_id) & (Particip.user_id == user_id)))


particip = CRUDParticip(Particip)
