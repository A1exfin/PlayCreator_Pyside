from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from Core.Enums import StorageType


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

    def reset_id(self, storage_type: 'StorageType') -> None:
        if hasattr(self, f'_id_{storage_type.value}'):
            setattr(self, f'_id_{storage_type.value}', None)

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()

    @property
    def changed(self) -> bool:
        return self._changed

    @changed.setter
    def changed(self, value: bool) -> None:
        self._changed = value

    def set_changed_flag(self) -> None:
        self._changed = True

    def reset_changed_flag(self) -> None:
        self._changed = False

