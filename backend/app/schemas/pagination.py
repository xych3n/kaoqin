from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class Pagination(GenericModel, Generic[ModelType]):
    total: int
    list: Sequence[ModelType]
