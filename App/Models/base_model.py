from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from PySide6.QtCore import QObject

if TYPE_CHECKING:
    pass


class BaseModel(QObject):
    def __init__(self, parent: Optional['QObject'] = None, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__(parent=parent)
        self._uuid: 'UUID' = uuid if uuid else uuid4()
        self._id_local_db: int = id_local_db
        self._id_api: int = id_api
        self._changed: bool = False

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

    @property
    def changed(self) -> bool:
        return self._changed

    @changed.setter
    def changed(self, value: bool) -> None:
        self._changed = value

