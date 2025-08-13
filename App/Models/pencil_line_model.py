from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4


if TYPE_CHECKING:
    pass


class PencilLineModel:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, thickness: int, color: str,
                 uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._thickness = thickness
        self._color = color
        self._uuid = uuid if uuid else uuid4()
        self._id_local_db = id_local_db
        self._id_api = id_api

    @property
    def id_local_db(self) -> int:
        return self._id_local_db

    @id_local_db.setter
    def id_local_db(self, value: int) -> None:
        self._id_local_db = value

    @property
    def id_api(self) -> int:
        return self._id_api

    @id_api.setter
    def id_api(self, value: int) -> None:
        self._id_api = value

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()

    @property
    def x1(self) -> float:
        return self._x1

    @property
    def y1(self) -> float:
        return self._y1

    @property
    def x2(self) -> float:
        return self._x2

    @property
    def y2(self) -> float:
        return self._y2

    @property
    def thickness(self) -> int:
        return self._thickness

    @property
    def color(self) -> str:
        return self._color

    def __hash__(self) -> int:
        return hash(id(self))

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid, 'x1': self._x1, 'y1': self._y1, 'x2': self._x2, 'y2': self._y2,
                'thickness': self._thickness, 'color': self._color}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'x1': self._x1, 'y1': self._y1, 'x2': self._x2, 'y2': self._y2,
                'thickness': self._thickness, 'color': self._color}

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self.uuid}; x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2}; ' \
               f'thickness: {self.thickness}; color: {self.color}) at {hex(id(self))}>'
