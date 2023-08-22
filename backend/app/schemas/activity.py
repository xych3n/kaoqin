import datetime

from pydantic import BaseModel

from ..models import ActivityCategory


class ActivityBase(BaseModel):
    title: str
    date: datetime.date
    category: ActivityCategory


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    id: int


class ActivityInDBBase(ActivityUpdate):
    class Config:
        orm_mode = True


class Activity(ActivityInDBBase):
    pass


class ActivityDetail(Activity):
    headcount: int
