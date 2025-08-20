from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsLineItem
from PySide6.QtGui import QColor, QPen, QPainter, QBrush, QPolygonF, QCursor, QPixmap
from PySide6.QtCore import QPointF, Qt, QLineF

from Config import HOVER_ITEM_COLOR, ERASER_CURSOR_PATH
from Config.Enums import Mode, FinalActionType

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
    from .field_view import Field
    from .action_view import ActionView

__all__ = ('FinalActionRouteView', 'FinalActionBlockView')


class FinalActionView:
    def __init__(self, action_type: 'FinalActionType', x: float, y: float, angle: float,
                 line_thickness: int, color: str, action: Optional['ActionView'], model_uuid: Optional['UUID']):
        self._model_uuid = model_uuid
        self._action = action
        self._action_type = action_type
        # if action:
        #     self.object_name = f'{self._action.player.text}_{self._action_type.name}'
        self._default_pen = QPen(QColor(color), line_thickness, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._hover_pen = QPen(HOVER_ITEM_COLOR, line_thickness, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self.setRotation(-angle)
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self._hover_state = False
        self.setZValue(1)

    @property
    def model_uuid(self) -> 'UUID':
        return self._model_uuid

    @property
    def hover_state(self) -> bool:
        return self._hover_state

    @hover_state.setter
    def hover_state(self, value: bool) -> None:
        self._hover_state = value

    def scene(self) -> 'Field':
        return super().scene()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.ungrabMouse()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print(self)
        if self.scene().mode is Mode.ERASE and event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # Возврат стандартного курсора сразу после клика
            if self._action:
                self._action.set_hover_state(False)
                self._action.player.signals.actionRemoveClicked.emit(self._action.model_id)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode is Mode.ERASE:
            self.setCursor(QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0))
            if self._action:
                self._action.set_hover_state(True)
        else:
            self.setCursor(Qt.ArrowCursor)
            if self._action:
                self._action.set_hover_state(False)

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode is Mode.ERASE:
            self.setCursor(QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0))
            if self._action:
                self._action.set_hover_state(True)
        else:
            self.setCursor(Qt.ArrowCursor)
            if self._action:
                self._action.set_hover_state(False)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setCursor(Qt.ArrowCursor)
        if self._action:
            self._action.set_hover_state(False)

    def get_data(self) -> dict:
        return {'action_type': self._action_type, 'x': self.x(), 'y': self.y(), 'angle': - self.rotation(),
                'line_thickness': self._default_pen.width(), 'color': self._default_pen.color().name()}


class FinalActionRouteView(FinalActionView, QGraphicsPolygonItem):
    def __init__(self, x: float, y: float, angle: float, line_thickness: int, color: str,
                 action_type: 'FinalActionType' = FinalActionType.ARROW, action: Optional['ActionView'] = None,
                 model_uuid: Optional['UUID'] = None):
        polygon = QPolygonF([QPointF(0, 0), QPointF(-10, -4), QPointF(-10, 4)])
        QGraphicsPolygonItem.__init__(self, polygon)
        FinalActionView.__init__(self, action_type, x, y, angle, line_thickness, color, action, model_uuid)
        self._default_brush = QBrush(color)
        self._hover_brush = QBrush(HOVER_ITEM_COLOR)

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        if self._hover_state:
            self.setPen(self._hover_pen)
            self.setBrush(self._hover_brush)
        else:
            self.setPen(self._default_pen)
            self.setBrush(self._default_brush)
        super().paint(painter, option, widget)


class FinalActionBlockView(FinalActionView, QGraphicsLineItem):
    def __init__(self, x: float, y: float, angle: float, line_thickness: int, color: str,
                 action_type: 'FinalActionType' = FinalActionType.LINE, action: Optional['ActionView'] = None,
                 model_uuid: Optional['UUID'] = None):
        line = QLineF(QPointF(0, -7), QPointF(0, 7))
        QGraphicsLineItem.__init__(self, line)
        FinalActionView.__init__(self, action_type, x, y, angle, line_thickness, color, action, model_uuid)

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        if self._hover_state:
            self.setPen(self._hover_pen)
        else:
            self.setPen(self._default_pen)
        super().paint(painter, option, widget)
