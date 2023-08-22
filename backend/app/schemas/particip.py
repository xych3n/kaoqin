from pydantic import BaseModel

from .activity import Activity
from .user import User


class ParticipBase(BaseModel):
    user_id: int
    activity_id: int
    involvement: int
    is_stuff: bool = False


class ParticipCreate(ParticipBase):
    pass


class ParticipUpdate(ParticipCreate):
    pass


class ParticipInDB(ParticipBase):
    class Config:
        orm_mode = True


class Particip(ParticipInDB):
    activity: Activity
    participant: User
