from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsProxyWidget, QTextEdit, QFrame, QApplication
from PySide6.QtCore import Qt, QRectF, QPointF, QObject, Signal
from PySide6.QtGui import QCursor, QPen, QBrush, QPixmap, QFont, QTextCursor, QPainter

from Config import HOVER_ITEM_COLOR, ERASER_CURSOR_PATH
from Config.Enums import Mode

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtWidgets import QWidget, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem
    from PySide6.QtGui import QMouseEvent, QKeyEvent, QFocusEvent
    from Views.Graphics import Field


__all__ = ('ProxyWidgetLabel', 'ProxyTextEdit')


class LabelSignals(QObject):
    itemMoved = Signal(object)  # QPointF
    itemResized = Signal(float, float, float, float)  # x, y, width, height
    itemEdited = Signal(str, str, int, bool, bool, bool, str, float, float)  # text, font_type, font_size, font_bold, font_italic, font_underline, font_color, y, height


class ProxyTextEdit(QTextEdit):
    def __init__(self, proxy: 'ProxyWidgetLabel', text: str, font: 'QFont', color: str, tmp_label: bool, parent=None):
        super().__init__(parent=parent)
        self._proxy = proxy
        self._tmp_label = tmp_label
        self.signals = LabelSignals()
        self.setFont(font)
        self.setTextColor(color)
        self.setText(text)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f'''background-color: transparent;\n''')
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.setMinimumSize(self._proxy.min_width, self._proxy.min_height)
        self.setMaximumSize(self._proxy.max_width, self._proxy.max_height)
        self.textChanged.connect(self.update_height)

    def mouseDoubleClickEvent(self, event: 'QMouseEvent') -> None:
        if self._proxy.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and self.isReadOnly():
            self.setReadOnly(False)
            text_cursor = self.textCursor()
            text_cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(text_cursor)
            self._proxy.scene().labelSelected.emit(self)
        elif self._proxy.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and not self.isReadOnly():
            super().mouseDoubleClickEvent(event)

    def _clear_focus(self) -> None:
        text_cursor = self.textCursor()
        text_cursor.clearSelection()
        self.setTextCursor(text_cursor)
        self.setReadOnly(True)
        self.releaseKeyboard()
        self.clearFocus()
        if self._tmp_label:
            self._proxy.scene().labelPlaced.emit(self._proxy.get_data())
            self._proxy.scene().labelDeselected.emit()
            self._proxy.scene().removeItem(self._proxy)
            self._proxy.deleteLater()
        else:
            self.signals.itemEdited.emit(self.toPlainText(), self.font().family(), self.font().pointSize(),
                                         self.font().bold(), self.font().italic(), self.font().underline(),
                                         self.textColor().name(), self._proxy.y(), self._proxy.rect().height())
            self._proxy.scene().labelDeselected.emit()

    def focusOutEvent(self, event: 'QFocusEvent') -> None:
        if QApplication.focusWidget():
            object_name = QApplication.focusWidget().objectName()
            if '_color_' in object_name or '_font_' in object_name:
                self.setFocus()
                self.grabKeyboard()
                return
            self._clear_focus()
        super().focusOutEvent(event)

    def keyPressEvent(self, event: 'QKeyEvent') -> None:
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            super().keyPressEvent(event)
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self._clear_focus()
        else:
            super().keyPressEvent(event)

    def update_height(self) -> None:
        lines_number = 0
        line_height = self.fontMetrics().height()
        margin = self.document().documentMargin()
        for block_number in range(self.document().blockCount()):
            block = self.document().findBlockByNumber(block_number)
            lines_number_in_block = block.layout().lineCount()
            lines_number += lines_number_in_block
        height = line_height * lines_number + 2 * (margin + 4)
        if height > self._proxy.max_height:
            height = self._proxy.max_height
        if self._proxy.y() + height > self._proxy.scene().sceneRect().height():
            y = self._proxy.y() - (self._proxy.y() + height - self._proxy.scene().sceneRect().height())
        else:
            y = self._proxy.y()
        self._proxy.setGeometry(self._proxy.x(), y, self._proxy.rect().width(), height)
        self._proxy._update_borders_pos()

    def __repr__(self):
        return f'<{self.__class__.__name__} (text: {self.toPlainText()}; font: {self.font().family()}; font_size: {self.font().pointSize()};' \
               f' color: {self.textColor().name()}; B: {self.font().bold()}; I: {self.font().italic()}; U: {self.font().underline()}) at {hex(id(self))}>'


class ProxyWidgetLabel(QGraphicsProxyWidget):
    border_width = 5
    default_width = 200
    default_height = 33
    min_width = 52
    min_height = 20
    max_width = 500
    max_height = 195

    def __init__(self, x: float, y: float, text: str, font_type: str, font_size: int,
                 font_bold: bool, font_italic: bool, font_underline: bool, font_color: str,
                 width: float = None, height: float = None, model_uuid: Optional['UUID'] = None, tmp_label: bool = False):
        super().__init__()
        self._model_uuid = model_uuid
        font = QFont(font_type)
        font.setPointSize(font_size)
        font.setBold(font_bold)
        font.setItalic(font_italic)
        font.setUnderline(font_underline)
        self.setWidget(ProxyTextEdit(self, text, font, font_color, tmp_label))
        self.setGeometry(x, y, width if width else self.default_width, height if height else self.default_height)
        self._start_pos = None
        self._borders = {}
        self._selected_border = None
        self._cursor = {'left': Qt.SizeHorCursor,
                        'right': Qt.SizeHorCursor,
                        'move': Qt.SizeAllCursor,
                        'edited': Qt.IBeamCursor,
                        'erase': QCursor(QPixmap(ERASER_CURSOR_PATH), 0, 0)}
        self.setAcceptHoverEvents(True)
        self._hover = False
        self._update_borders_pos()
        self.setZValue(3)

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        super().paint(painter, option, widget)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setBrush(QBrush(Qt.transparent))
        # for border, rect in self.borders.items():  # Отладка прямоугольников изменния размера
        #     painter.drawRect(QRectF(rect.x() - self.scenePos().x(), rect.y() - self.scenePos().y(), rect.width(), rect.height()))
        if not self.widget().isReadOnly():
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine, c=Qt.RoundCap))
            painter.drawRect(self.rect())
        elif self._hover:
            painter.setPen(QPen(HOVER_ITEM_COLOR, 2, Qt.DashLine, c=Qt.RoundCap))
            painter.drawRect(self.rect())
        rect = QRectF(self.x() - 10, self.y() - 10, self.rect().width() + 20, self.rect().height() + 20)
        self.scene().update(rect)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print(self)
        self.setZValue(20)
        if self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and not self.widget().isReadOnly():
            self._selected_border = self._check_border_under_cursor(event.scenePos())
        if self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and self.widget().isReadOnly():
            self._start_pos = event.scenePos()
        elif self.scene().mode is Mode.ERASE and event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)  # Возврат стандартного курсора сразу после клика
            self.scene().labelRemoveClicked.emit(self._model_uuid)
        elif self.scene().mode is Mode.MOVE and not self.widget().isReadOnly() and not self._selected_border:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.scene().mode is Mode.MOVE and self._selected_border and not self.widget().isReadOnly():
            self._interactive_resize(event.scenePos())
        elif self.scene().mode is Mode.MOVE and self._start_pos and self.widget().isReadOnly():
            delta = event.scenePos() - self._start_pos
            if self.scene().check_field_x(self.x() + delta.x()) \
                    and self.scene().check_field_x(self.x() + self.rect().width() + delta.x()):
                self.moveBy(delta.x(), 0)
            if self.scene().check_field_y(self.y() + delta.y())\
                    and self.scene().check_field_y(self.y() + self.rect().height() + delta.y()):
                self.moveBy(0, delta.y())
            self._start_pos = event.scenePos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setZValue(3)
        self._update_borders_pos()
        if self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and self.widget().isReadOnly() and not self._selected_border:
            self._start_pos = None
            self.widget().signals.itemMoved.emit(self.pos())
        elif self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton and not self.widget().isReadOnly() and self._selected_border:
            self._selected_border = None
            self.widget().signals.itemResized.emit(self.x(), self.y(), self.rect().width(), self.rect().height())
        else:
            super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode is Mode.MOVE or self. scene().mode == Mode.ERASE:
            self._hover = True
            # self.update()
            # super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if not self.widget().isReadOnly() and self.scene().mode is Mode.MOVE:
            border_under_cursor = self._check_border_under_cursor(event.scenePos())
            if border_under_cursor:
                cursor = self._cursor[border_under_cursor]
            else:
                cursor = self._cursor['edited']
        elif self.widget().isReadOnly() and self.scene().mode is Mode.MOVE:
            cursor = self._cursor['move']
            self._hover = True
        elif self.scene().mode is Mode.ERASE:
            cursor = self._cursor['erase']
            self._hover = True
        else:
            cursor = Qt.ArrowCursor
            self._hover = False
        self.setCursor(cursor)
        # self.update()
        # super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode is Mode.MOVE or self.scene().mode is Mode.ERASE:
            self._hover = False
            # self.update()

    def _update_borders_pos(self) -> None:
        self._borders['left'] = QRectF(self.x(), self.y(), self.border_width, self.rect().height())
        self._borders['right'] = QRectF(self.x() + self.rect().width() - self.border_width, self.y(),
                                        self.border_width, self.rect().height())

    def _check_border_under_cursor(self, point: 'QPointF') -> Optional['QRectF']:
        for border, rect in self._borders.items():
            if rect.contains(point):
                return border
        return None

    def _interactive_resize(self, mouse_pos: 'QPointF') -> None:
        x = self.x()
        width = self.rect().width()
        if self._selected_border == 'left':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.x()
                if delta_x < 0 and self.rect().width() >= self.max_width:
                    pass
                elif delta_x > 0 and self.rect().width() <= self.min_width:
                    pass
                else:
                    x += delta_x
                    width -= delta_x
        elif self._selected_border == 'right':
            if self.scene().check_field_x(mouse_pos.x()):
                delta_x = mouse_pos.x() - self.rect().width() - self.x()
                if delta_x > 0 and self.rect().width() >= self.max_width:
                    pass
                elif delta_x < 0 and self.rect().width() <= self.min_width:
                    pass
                else:
                    width += delta_x
        self.setGeometry(x, self.y(), width, self.rect().height())
        self.widget().update_height()
        self._update_borders_pos()
        self.update()

    def widget(self) -> 'ProxyTextEdit':
        return super().widget()

    def scene(self) -> 'Field':
        return super().scene()

    @property
    def model_uuid(self) -> Optional['UUID']:
        return self._model_uuid

    def set_pos(self, new_pos: 'QPointF') -> None:
        self.setPos(new_pos)

    def set_rect(self, x: float, y: float, width: float, height: float) -> None:
        self.setGeometry(x, y, width, height)

    def set_text_attributes(self, text: str, font_type: str, font_size: int, font_bold: bool, font_italic: bool,
                            font_underline: bool, font_color: str, y: float, height: float) -> None:
        self.widget().setText(text)
        font = QFont(font_type, font_size)
        font.setBold(font_bold)
        font.setItalic(font_italic)
        font.setUnderline(font_underline)
        self.widget().setFont(font)
        text_cursor = self.widget().textCursor()
        self.widget().selectAll()
        self.widget().setTextColor(font_color)
        self.widget().setTextCursor(text_cursor)
        self.setGeometry(self.x(), y, self.rect().width(), height)

    def get_data(self) -> dict:
        return {'x': self.x(), 'y': self.y(), 'width': self.rect().width(), 'height': self.rect().height(),
                'text': self.widget().toPlainText(), 'font_type': self.widget().font().family(),
                'font_size': self.widget().font().pointSize(), 'font_bold': self.widget().font().bold(),
                'font_italic': self.widget().font().italic(), 'font_underline': self.widget().font().underline(),
                'font_color': self.widget().textColor().name()}
