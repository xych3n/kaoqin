from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..models import User
from ..schemas import UserCreate, UserUpdate
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def _filter_expression(self, filter: str = ""):
        return User.student_number.like(f"%{filter}%") | User.name.like(f"%{filter}%")

    def get_by_student_number(self, db: Session, *, student_number: str):
        return db.scalar(select(User).where(User.student_number == student_number))

    def authenticate(self, db: Session, *, student_number: str, password: str):
        db_user = self.get_by_student_number(db, student_number=student_number)
        if db_user is not None:
            if db_user.hashed_password is None:
                db_user.hashed_password = get_password_hash(db_user.default_password)
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
            if verify_password(password, db_user.hashed_password):
                return db_user

    def reset_password(self, db: Session, *, db_user: User, new_password: str = ""):
        if new_password != "":
            db_user.hashed_password = get_password_hash(new_password)
        else:
            db_user.hashed_password = None
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


user = CRUDUser(User)
