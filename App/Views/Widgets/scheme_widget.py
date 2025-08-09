from typing import TYPE_CHECKING

from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from uuid import UUID

__all__ = ('SchemeWidget', )


class SchemeWidget(QListWidgetItem):
    def __init__(self, model_uuid: 'UUID', name: str):
        super().__init__(name)
        self._model_uuid = model_uuid
        self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

    @property
    def model_uuid(self) -> 'UUID':
        return self._model_uuid
