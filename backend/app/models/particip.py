from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base
if TYPE_CHECKING:
    from .activity import Activity
    from .user import User


class Particip(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activity.id"), primary_key=True)
    involvement: Mapped[int] = mapped_column(default=0)
    is_stuff: Mapped[bool] = mapped_column(index=True, default=False)

    if TYPE_CHECKING:
        # if no `if TYPE_CHECKING`, it'll cause RecursionError because a bug of `dataclass`,
        # see https://github.com/sqlalchemy/sqlalchemy/issues/9785
        activity: Mapped["Activity"] = relationship(back_populates="participants", init=False)
        participant: Mapped["User"] = relationship(back_populates="activities", init=False)
