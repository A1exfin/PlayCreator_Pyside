from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QColor, QPen, QPainter, QCursor, QPixmap
from PySide6.QtCore import Qt

from Views import Graphics
from Config import HOVER_ITEM_COLOR, ERASER_CURSOR_PATH
from Config.Enums import Mode, ActionLineType

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
    from Views.Graphics import Field

__all__ = ('ActionLineView',)


class ActionLineView(QGraphicsLineItem):
    def __init__(self, line_type: 'ActionLineType', x1: float, y1: float, x2: float, y2: float,
                 thickness: int, color: str, action: Optional['Graphics.ActionView'] = None,
                 model_uuid: Optional['UUID'] = None):
        super().__init__(x1, y1, x2, y2)
        self._model_uuid = model_uuid
        self._action = action
        self._line_type = line_type
        # if action:
        #     self.object_name = f'{self._action.player.text}_{self._line_type.name}'
        self._default_pen = QPen(QColor(color), thickness, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._default_pen.setStyle(Qt.DashLine if self._line_type is ActionLineType.MOTION else Qt.SolidLine)
        self._hover_pen = QPen(HOVER_ITEM_COLOR, thickness, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._hover_pen.setStyle(Qt.DashLine if self._line_type is ActionLineType.MOTION else Qt.SolidLine)
        self._hover_state = False
        self.setAcceptHoverEvents(True)
        self.setZValue(1)

    def scene(self) -> 'Field':
        return super().scene()

    @property
    def model_uuid(self) -> 'UUID':
        return self._model_uuid

    @property
    def hover_state(self) -> bool:
        return self._hover_state

    @hover_state.setter
    def hover_state(self, value: bool) -> None:
        self._hover_state = value

    @property
    def action(self) -> 'Graphics.ActionView':
        return self._action

    @property
    def action_type(self) -> 'ActionLineType':
        return self._line_type

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None) -> None:
        painter.setRenderHints(QPainter.Antialiasing)
        if self._hover_state:
            self.setPen(self._hover_pen)
        else:
            self.setPen(self._default_pen)
        super().paint(painter, option, widget)
        # self.scene().update()  # Нужно для полного удаления действия со сцены СРАЗУ после клика по линии
        # self.update()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.ungrabMouse()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print(self)
        self.ungrabMouse()
        if self.scene().mode is Mode.ERASE and event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # Возврат стандартного курсора сразу после клика
            if self._action:
                self._action.set_hover_state(False)
                self._action.player.signals.actionRemoveClicked.emit(self._action.model_uuid)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode in (Mode.ERASE, Mode.ROUTE, Mode.BLOCK) or \
                (self.scene().mode is Mode.MOTION and self._line_type is ActionLineType.MOTION):
            if self._action:
                self._action.set_hover_state(True)
        if self.scene().mode is Mode.ERASE:
            self.setCursor(QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0))

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode in (Mode.ERASE, Mode.ROUTE, Mode.BLOCK) or \
                (self.scene().mode is Mode.MOTION and self._line_type is ActionLineType.MOTION):
            if self._action:
                self._action.set_hover_state(True)
        else:
            if self._action:
                self._action.set_hover_state(False)
        if self.scene().mode is Mode.ERASE:
            self.setCursor(QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0))
        else:
            self.setCursor(Qt.ArrowCursor)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self._action:
            self._action.set_hover_state(False)
        self.setCursor(Qt.ArrowCursor)

    def get_data(self) -> dict:
        return {'line_type': self._line_type, 'x1': self.line().x1(), 'y1': self.line().y1(),
                'x2': self.line().x2(), 'y2': self.line().y2(), 'thickness': self._default_pen.width(),
                'color': self._default_pen.color().name()}




