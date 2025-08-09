from typing import Generic, TypeVar, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel

T = TypeVar('T')
M = TypeVar('M', bound=BaseModel)
O = TypeVar('O')


class BaseMapper(ABC, Generic[T, M]):
    @abstractmethod
    def _app_obj_to_dict(self, item: T) -> dict[str, Any]:
        pass

    @abstractmethod
    def _app_obj_to_dto(self, item: T) -> M:
        pass

    @abstractmethod
    def _dto_to_app_obj(self, item: M) -> T:
        pass
