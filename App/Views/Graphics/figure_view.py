from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent
from PySide6.QtGui import QColor, QPainter, QPen, QCursor, QPixmap, QBrush
from PySide6.QtCore import Qt, QRectF, QObject, Signal

from Config import HOVER_SCENE_ITEM_COLOR, ERASER_CURSOR_PATH
from Core.Enums import Mode, FigureType

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtCore import QPointF
    from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget
    from .field_view import Field

__all__ = ('RectangleView', 'EllipseView')


class FigureSignals(QObject):
    itemMoved = Signal(object)  # QPointF
    itemResized = Signal(float, float, float, float)
    itemDoubleClicked = Signal()


class FigureView:
    def __init__(self, model_uuid: Optional['UUID'], figure_type: 'FigureType', x: float, y: float, width: float, height: float,
                 border: bool, border_thickness: int, border_color: str,
                 fill: bool, fill_opacity: str, fill_color: str):
        self._model_uuid = model_uuid
        self.signals = FigureSignals()
        self._figure_type = figure_type
        self._border = border
        self._border_color = border_color
        self._border_thickness = border_thickness
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
        self._pen = QPen(QColor(border_color if border else Qt.transparent), border_thickness, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._brush = QBrush(f'{fill_opacity}{fill_color[1:]}' if fill else Qt.transparent)
        self._start_pos = None
        self._borders = {}
        self._border_selected = None
        self.setAcceptHoverEvents(True)
        self._hover = False
        self.setZValue(0)
        self.setPen(self._pen)
        self.setBrush(self._brush)
        self.set_rect(x, y, width, height)

    def scene(self) -> 'Field':
        return super().scene()

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None) -> None:
        painter.setRenderHints(QPainter.Antialiasing)
        self.setBrush(self._brush)
        if self._hover:
            self.setPen(QPen(HOVER_SCENE_ITEM_COLOR, self._border_thickness if self._border else 2, self._pen.style(), self._pen.capStyle(), self._pen.joinStyle()))
        else:
            self.setPen(self._pen)
        super().paint(painter, option, widget)

        # painter.setPen(QPen(QColor(Qt.red), 1))
        # painter.setBrush(QBrush(Qt.red))
        # for border, rect in self._borders.items():
        #     painter.drawRect(QRectF(rect.x() - self.x(), rect.y() - self.y(), rect.width(), rect.height()))
        self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print(self)
        self._border_selected = self.check_border_under_cursor(event.scenePos())
        if self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and not self._border_selected:
            self.setZValue(20)
            self._start_pos = event.scenePos()
        if self.scene().mode is Mode.ERASE and event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # Возврат стандартного курсора сразу после клика
            self.scene().figureRemoveClicked.emit(self._model_uuid)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.scene().mode is Mode.MOVE and self._border_selected:
            self.interactive_resize(event.scenePos())
        elif self.scene().mode is Mode.MOVE:
            if self._start_pos:
                delta = event.scenePos() - self._start_pos
                if self.scene().check_field_x(self.x() + delta.x()) \
                        and self.scene().check_field_x(self.x() + self.rect().width() + delta.x()):
                    self.moveBy(delta.x(), 0)
                if self.scene().check_field_y(self.y() + delta.y())\
                        and self.scene().check_field_y(self.y() + self.rect().height() + delta.y()):
                    self.moveBy(0, delta.y())
                self._start_pos = event.scenePos()
        # super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.normalizate()
        self.update_borders_pos()
        if self.scene().mode is Mode.MOVE:
            if self._border_selected:
                self.signals.itemResized.emit(self.x(), self.y(), self.rect().width(), self.rect().height())
            self._border_selected = None
            self._start_pos = None
            self.setZValue(0)
            self.signals.itemMoved.emit(self.pos())
        # super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.scene().mode is Mode.MOVE:
            self.signals.itemDoubleClicked.emit()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.update_borders_pos()
        if self.scene().mode in (Mode.MOVE, Mode.ERASE):
            self._hover = True

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        border_under_cursor = self.check_border_under_cursor(event.scenePos())
        if self.scene().mode is Mode.ERASE:
            self._hover = True
            cursor = self.cursors['erase']
        elif self.scene().mode is Mode.MOVE:
            if border_under_cursor:
                cursor = self.cursors[border_under_cursor]
            else:
                cursor = self.cursors['move']
                # cursor = Qt.ArrowCursor
            self._hover = True
        else:
            cursor = Qt.ArrowCursor
            self._hover = False
        self.setCursor(cursor)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setCursor(Qt.ArrowCursor)
        self._hover = False

    def check_border_under_cursor(self, point: 'QPointF') -> Optional['QRectF']:
        for border, rect in self._borders.items():
            if rect.contains(point):
                return border
        return None

    def normalizate(self) -> None:
        if self.rect().width() < 0:
            x, width = self.x() + self.rect().width(), - self.rect().width()
            self.set_rect(x, self.y(), width, self.rect().height())
        if self.rect().height() < 0:
            y, height = self.y() + self.rect().height(), - self.rect().height()
            self.set_rect(self.x(), y, self.rect().width(), height)

    def set_rect(self, x: float, y: float, width: float, height: float) -> None:
        self.setPos(x, y)
        self.setRect(QRectF(0, 0, width, height))

    def set_figure_style(self, border: bool, border_thickness: int, border_color: str,
                         fill: bool, fill_opacity: str, fill_color: str) -> None:
        self._border, self._border_thickness, self._border_color, self._fill, self._fill_opacity, self._fill_color = \
            border, border_thickness, border_color, fill, fill_opacity, fill_color
        self._pen.setColor(border_color if border else Qt.transparent)
        self._pen.setWidth(border_thickness)
        self._brush.setColor(f'{fill_opacity}{fill_color[1:]}' if fill else Qt.transparent)

    @property
    def model_uuid(self) -> Optional['UUID']:
        return self._model_uuid

    def get_data(self) -> dict:
        return {'figure_type': self._figure_type, 'x': self.x(), 'y': self.y(),
                'width': self.rect().width(), 'height': self.rect().height(),
                'border': self._border, 'border_thickness': self._border_thickness, 'border_color': self._border_color,
                'fill': self._fill, 'fill_color': self._fill_color, 'fill_opacity': self._fill_opacity}


class RectangleView(FigureView, QGraphicsRectItem):
    def __init__(self, x: float, y: float, width: float, height: float,
                 border: bool, border_thickness: int, border_color: str,
                 fill: bool = False, fill_opacity: str = '#22', fill_color: str = '#000000',
                 figure_type: 'FigureType' = FigureType.RECTANGLE, model_uuid: Optional['UUID'] = None):
        QGraphicsRectItem.__init__(self, 0, 0, 0, 0)
        FigureView.__init__(self, model_uuid, figure_type, x, y, width, height, border, border_thickness, border_color,
                            fill, fill_opacity, fill_color)
        self.cursors = {'left': Qt.SizeHorCursor,
                        'right': Qt.SizeHorCursor,
                        'top': Qt.SizeVerCursor,
                        'bot': Qt.SizeVerCursor,
                        'top_left': Qt.SizeFDiagCursor,
                        'bot_right': Qt.SizeFDiagCursor,
                        'top_right': Qt.SizeBDiagCursor,
                        'bot_left': Qt.SizeBDiagCursor,
                        'move': Qt.SizeAllCursor,
                        'erase': QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0)}

    def update_borders_pos(self) -> None:
        self._borders['left'] = QRectF(self.x() - self._border_thickness / 2 - 1, self.y() + self._border_thickness / 2,
                                       self._border_thickness + 1, self.rect().height() - self._border_thickness)
        self._borders['right'] = QRectF(self.x() + self.rect().width() - self._border_thickness / 2, self.y() + self._border_thickness / 2,
                                        self._border_thickness, self.rect().height() - self._border_thickness)
        self._borders['top_left'] = QRectF(self.x() - self._border_thickness / 2 - 1, self.y() - self._border_thickness / 2 - 1,
                                           self._border_thickness + 1, self._border_thickness + 1)  # top_left
        self._borders['top'] = QRectF(self.x() + self._border_thickness / 2, self.y() - self._border_thickness / 2 - 1,
                                      self.rect().width() - self._border_thickness, self._border_thickness + 1)  # top_mid

        self._borders['top_right'] = QRectF(self.x() + self.rect().width() - self._border_thickness / 2, self.y() - self._border_thickness / 2 - 1,
                                            self._border_thickness, self._border_thickness + 1)  # top_right

        self._borders['bot_left'] = QRectF(self.x() - self._border_thickness / 2 - 1, self.y() + self.rect().height() - self._border_thickness / 2,
                                           self._border_thickness + 1, self._border_thickness)  # bot_left
        self._borders['bot'] = QRectF(self.x() + self._border_thickness / 2, self.y() + self.rect().height() - self._border_thickness / 2,
                                      self.rect().width() - self._border_thickness, self._border_thickness)  # bot_mid
        self._borders['bot_right'] = QRectF(self.x() + self.rect().width() - self._border_thickness / 2, self.y() + self.rect().height() - self._border_thickness / 2,
                                            self._border_thickness, self._border_thickness)  # bot_right

    def interactive_resize(self, mouse_pos: 'QPointF') -> None:
        if self._border_selected == 'left':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.x()
                x = self.x() + delta_x
                width = self.rect().width() - delta_x
                self.set_rect(x, self.y(), width, self.rect().height())
        elif self._border_selected == 'right':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.rect().width() - self.x()
                width = self.rect().width() + delta_x
                self.set_rect(self.x(), self.y(), width, self.rect().height())
        elif self._border_selected == 'top':
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.y()
                y = self.y() + delta_y
                height = self.rect().height() - delta_y
                self.set_rect(self.x(), y, self.rect().width(), height)
        elif self._border_selected == 'bot':
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.rect().height() - self.y()
                height = self.rect().height() + delta_y
                self.set_rect(self.x(), self.y(), self.rect().width(), height)
        elif self._border_selected == 'top_left':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.x()
                x = self.x() + delta_x
                width = self.rect().width() - delta_x
                self.set_rect(x, self.y(), width, self.rect().height())
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.y()
                y = self.y() + delta_y
                height = self.rect().height() - delta_y
                self.set_rect(self.x(), y, self.rect().width(), height)
        elif self._border_selected == 'top_right':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.rect().width() - self.x()
                width = self.rect().width() + delta_x
                self.set_rect(self.x(), self.y(), width, self.rect().height())
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.y()
                y = self.y() + delta_y
                height = self.rect().height() - delta_y
                self.set_rect(self.x(), y, self.rect().width(), height)
        elif self._border_selected == 'bot_left':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.x()
                x = self.x() + delta_x
                width = self.rect().width() - delta_x
                self.set_rect(x, self.y(), width, self.rect().height())
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.rect().height() - self.y()
                height = self.rect().height() + delta_y
                self.set_rect(self.x(), self.y(), self.rect().width(), height)
        elif self._border_selected == 'bot_right':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.rect().width() - self.x()
                width = self.rect().width() + delta_x
                self.set_rect(self.x(), self.y(), width, self.rect().height())
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.rect().height() - self.y()
                height = self.rect().height() + delta_y
                self.set_rect(self.x(), self.y(), self.rect().width(), height)
        self.update_borders_pos()
        self.scene().update()  # Для корректной отрисовки фигуры при отрицательной ширине и высоте фигуры


class EllipseView(FigureView, QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, width: float, height: float,
                 border: bool, border_thickness: int, border_color: str,
                 fill: bool = False, fill_opacity: str = '#22', fill_color: str = '#000000',
                 figure_type: 'FigureType' = FigureType.ELLIPSE, model_uuid: Optional['UUID'] = None):
        QGraphicsEllipseItem.__init__(self, 0, 0, 0, 0)
        FigureView.__init__(self, model_uuid, figure_type, x, y, width, height, border, border_thickness, border_color,
                            fill, fill_opacity, fill_color)
        self.cursors = {'left': Qt.SizeHorCursor,
                        'right': Qt.SizeHorCursor,
                        'top': Qt.SizeVerCursor,
                        'bot': Qt.SizeVerCursor,
                        'move': Qt.SizeAllCursor,
                        'erase': QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0)}

    def update_borders_pos(self) -> None:
        self._borders['left'] = QRectF(self.x() - self._border_thickness / 2 - 1, self.y() + self._border_thickness / 2,
                                       self._border_thickness + 1, self.rect().height() - self._border_thickness)
        self._borders['right'] = QRectF(self.x() + self.rect().width() - self._border_thickness / 2, self.y() + self._border_thickness / 2,
                                        self._border_thickness, self.rect().height() - self._border_thickness)
        self._borders['top'] = QRectF(self.x() + self._border_thickness / 2, self.y() - self._border_thickness / 2 - 1,
                                      self.rect().width() - self._border_thickness, self._border_thickness + 1)  # top_mid
        self._borders['bot'] = QRectF(self.x() + self._border_thickness / 2, self.y() + self.rect().height() - self._border_thickness / 2,
                                      self.rect().width() - self._border_thickness, self._border_thickness)  # bot_mid

    def interactive_resize(self, mouse_pos: 'QPointF') -> None:
        if self._border_selected == 'left':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.x()
                x = self.x() + delta_x
                width = self.rect().width() - delta_x
                self.set_rect(x, self.y(), width, self.rect().height())
        elif self._border_selected == 'right':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.rect().width() - self.x()
                width = self.rect().width() + delta_x
                self.set_rect(self.x(), self.y(), width, self.rect().height())
        elif self._border_selected == 'top':
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.y()
                y = self.y() + delta_y
                height = self.rect().height() - delta_y
                self.set_rect(self.x(), y, self.rect().width(), height)
        elif self._border_selected == 'bot':
            if self.scene().check_field_y(mouse_pos.y()):
                delta_y = mouse_pos.y() - self.rect().height() - self.y()
                height = self.rect().height() + delta_y
                self.set_rect(self.x(), self.y(), self.rect().width(), height)
        self.update_borders_pos()
