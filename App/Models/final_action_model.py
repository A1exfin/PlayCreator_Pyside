from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from Config.Enums import ActionLineType


class FinalActionModel:
    def __init__(self, action_type: 'ActionLineType', x: float, y: float, angle: float,
                 line_thickness: int, color: str, uuid: Optional['UUID'] = None):
        self._action_type = action_type
        self._x = x
        self._y = y
        self._angle = angle
        self._line_thickness = line_thickness
        self._color = color
        self._uuid = uuid if uuid else uuid4()

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()

    @property
    def action_type(self) -> 'ActionLineType':
        return self._action_type

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def line_thickness(self) -> int:
        return self._line_thickness

    @property
    def color(self) -> str:
        return self._color

    def __hash__(self) -> int:
        return hash(id(self))

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid, 'action_type': self._action_type,
                'x': self._x, 'y': self._y, 'angle': self._angle,
                'line_thickness': self._line_thickness, 'color': self._color}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'action_type': self._action_type,
                'x': self._x, 'y': self._y, 'angle': self._angle,
                'line_thickness': self._line_thickness, 'color': self._color}

    def __repr__(self):
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (uuid: {self._uuid}; ' \
               f'x: {self._x}; y: {self._y}; action_type: {self._action_type}; angle: {self._angle}; ' \
               f'line_thickness: {self._line_thickness}; color: {self._color}; ' \
               f'at {hex(id(self))}>'