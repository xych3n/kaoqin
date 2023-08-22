from typing import Dict

from pydantic import BaseModel


class UserBase(BaseModel):
    student_number: str
    # id_number: str
    name: str
    is_superuser: bool


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    id: int


class UserInDBBase(UserUpdate):
    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserDetail(User):
    involvements: Dict[str, str]
