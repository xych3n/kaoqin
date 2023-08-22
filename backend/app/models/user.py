import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base
from .activity import ActivityCategory
if TYPE_CHECKING:
    from .particip import Particip


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    student_number: Mapped[str] = mapped_column(String(length=11), unique=True)
    id_number: Mapped[str] = mapped_column(String(length=18), repr=False)
    name: Mapped[str] = mapped_column(index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(init=False, repr=False)

    activities: Mapped[List["Particip"]] = relationship(backref="participant", init=False, repr=False)

    @hybrid_property
    def default_password(self) -> str:
        return self.id_number[-6:]

    @hybrid_property
    def involvements(self) -> Dict[str, int]:
        involvements = {category.value: 0 for category in ActivityCategory}
        for particip in self.activities:
            category = particip.activity.category.value
            if category == "研会活动" and particip.activity.date <= datetime.date(2022, 9, 1):
                continue
            involvements[category] += particip.involvement
        return involvements
