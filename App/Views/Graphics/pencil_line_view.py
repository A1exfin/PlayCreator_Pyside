from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from uuid import UUID

__all__ = ('PencilLineView',)


class PencilLineView(QGraphicsLineItem):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, thickness: int, color: str,
                 model_uuid: Optional['UUID'] = None):
        super().__init__(x1, y1, x2, y2)
        self._model_uuid = model_uuid
        self.setPen(QPen(QColor(color), thickness, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin))
        self.setZValue(0)

    @property
    def model_uuid(self) -> Optional['UUID']:
        return self._model_uuid

    def get_data(self) -> dict:
        return {'x1': self.line().x1(), 'y1': self.line().y1(), 'x2': self.line().x2(), 'y2': self.line().y2(),
                'thickness': self.pen().width(), 'color': self.pen().color().name()}
