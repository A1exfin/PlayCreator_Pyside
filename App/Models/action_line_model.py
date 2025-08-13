from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from Config.Enums import ActionLineType


class ActionLineModel:
    def __init__(self, line_type: 'ActionLineType', x1: float, y1: float, x2: float, y2: float,
                 thickness: int, color: str, uuid: Optional['UUID'] = None):
        self._line_type = line_type
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._thickness = thickness
        self._color = color
        self._uuid = uuid if uuid else uuid4()

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()

    @property
    def action_type(self) -> 'ActionLineType':
        return self._line_type

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
        return {'model_uuid': self._uuid, 'line_type': self._line_type,
                'x1': self._x1, 'y1': self._y1, 'x2': self._x2, 'y2': self._y2,
                'thickness': self._thickness, 'color': self._color}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'line_type': self._line_type,
                'x1': self._x1, 'y1': self._y1, 'x2': self._x2, 'y2': self._y2,
                'thickness': self._thickness, 'color': self._color}

    def __repr__(self):
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (uuid: {self._uuid}; ' \
               f'x1: {self._x1}; y1: {self._y1}; x2: {self._x2}; y2: {self._y2}; line_type: {self._line_type}; ' \
               f'thickness: {self._thickness}; color: {self._color}) ' \
               f'at {hex(id(self))}>'