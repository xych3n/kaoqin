import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from ..db.base import Base
if TYPE_CHECKING:
    from .particip import Particip


class ActivityCategory(str, Enum):
    LECT = "学术讲座"   # lecture
    ASSN = "研会活动"   # association

    def __repr__(self) -> str:
        return "'{}'".format(self.value)


class Activity(Base):
    __table_args__ = (
        UniqueConstraint("title", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(index=True)
    date: Mapped[datetime.date] = mapped_column(index=True)
    category: Mapped[ActivityCategory] = mapped_column(index=True)

    participants: Mapped[List["Particip"]] = relationship(backref="activity", init=False, repr=False)

    @hybrid_property
    def headcount(self) -> int:
        return len(self.participants)
