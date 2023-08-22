from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions as func
from sqlalchemy.sql.elements import BooleanClauseList

from ..db.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, db_obj: ModelType) -> ModelType:
        db.delete(db_obj)
        db.commit()
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        for field, value in obj_in.dict().items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @abstractmethod
    def _filter_expression(self, filter: str = "") -> BooleanClauseList:
        pass

    def count(self, db: Session, *, filter: str = "") -> Optional[int]:
        return db.scalar(
            select(func.count())
            .where(self._filter_expression(filter))
            .select_from(self.model)
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, filter: str = "",
    ) -> Sequence[ModelType]:
        return db.scalars(
            select(self.model)
            .where(self._filter_expression(filter))
            .offset(skip)
            .limit(limit)
        ).all()
