from typing import TYPE_CHECKING, Optional
from uuid import UUID

from Core import log_method_decorator, logger
from .base_model import BaseModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject
    from Core.Enums import FinalActionType
    from .playbook_model import PlaybookModel


class FinalActionModel(BaseModel):
    def __init__(self, playbook_model: 'PlaybookModel', action_type: 'FinalActionType', x: float, y: float,
                 angle: float, line_thickness: int, color: str, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['QObject'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._playbook_model = playbook_model
        self._action_type = action_type
        self._x = x
        self._y = y
        self._angle = angle
        self._line_thickness = line_thickness
        self._color = color

    @log_method_decorator()
    def _set_changed_flag(self) -> None:
        super().set_changed_flag()
        self._playbook_model.changed = True

    @property
    def action_type(self) -> 'FinalActionType':
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