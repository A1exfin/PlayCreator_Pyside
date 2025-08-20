from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from .base_model import BaseModel

if TYPE_CHECKING:
    from Config.Enums import StorageType
    from .player_model import PlaybookModel
    from .scheme_model import SchemeModel


class PencilLineModel(BaseModel):
    def __init__(self, playbook_model: 'PlaybookModel',  x1: float, y1: float, x2: float, y2: float,
                 thickness: int, color: str, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['SchemeModel'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._playbook_model = playbook_model
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._thickness = thickness
        self._color = color

    def _set_changed(self) -> None:
        super().set_changed()
        self._playbook_model.changed = True

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
