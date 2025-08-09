from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QColor, QLinearGradient, QPen, QPainter, QFont, QPolygonF, QBrush
from PySide6.QtCore import QPointF, QRectF, QLineF, Qt, QObject, Signal

from Config import PlayerData
from Views import Graphics
from Config.Enums import TeamType, FillType, SymbolType, Mode, PlayerPositionType

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtWidgets import QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent,\
        QStyleOptionGraphicsItem, QWidget
    from .field_view import Field

__all__ = ('PlayerView', 'FirstTeamPlayerView', 'SecondTeamPlayerView')


class PlayerSignals(QObject):
    itemMoved = Signal(object)  # QPointF
    itemDoubleClicked = Signal()
    actionPainted = Signal(object)  # PaintedActionData
    actionRemoveClicked = Signal(object)  # model_id


class PlayerView(QGraphicsItem):
    '''Класс для отрисовки игроков'''
    _size = PlayerData.size
    _border_width = PlayerData.border_width

    def __init__(self, model_uuid: 'UUID', x: float, y: float, team_type: 'TeamType', position: 'PlayerPositionType',
                 text: str, text_color: str, player_color: str):
        super().__init__()
        self.signals = PlayerSignals()
        self._model_uuid = model_uuid
        self._team_type = team_type
        self._position = position
        self._object_name = f'{team_type.name}_player_{position}'
        self._text = text
        self._player_color = player_color
        self._text_color = text_color
        self._default_pen = QPen(QColor(player_color), self._border_width,
                                 s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._selected_pen = QPen(QColor(Qt.red), self._border_width,
                                  s=Qt.DotLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._hover_pen = QPen(QColor(player_color),
                               self._border_width, s=Qt.DotLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        self._text_pen = QPen(QColor(text_color))
        self._actions = []
        self._start_pos = None
        self._hover_state = False
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)
        self._rect = self.boundingRect().\
            adjusted(self._border_width / 2, self._border_width / 2, - self._border_width / 2, - self._border_width / 2)

    def scene(self) -> 'Field':
        return super().scene()

    def boundingRect(self) -> 'QRectF':
        return QRectF(0, 0, self._size, self._size)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setZValue(20)
        if self.scene().mode is Mode.MOVE and event.button() == Qt.LeftButton:
            self._start_pos = event.scenePos()
            super().mousePressEvent(event)
            self.setSelected(True)
        elif event.button() == Qt.RightButton:  # Для того чтобы маршрут не рисовался от игрока по которому кликнули правой кнопкой
            self.ungrabMouse()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.scene().mode is Mode.MOVE:
            if self._start_pos:
                delta = event.scenePos() - self._start_pos
                if self.scene().check_field_x(self.x() + delta.x()) \
                        and self.scene().check_field_x(self.x() + self._size + delta.x()):
                    self.moveBy(delta.x(), 0)
                if self.scene().check_field_y(self.y() + delta.y())\
                        and self.scene().check_field_y(self.y() + self._size + delta.y()):
                    self.moveBy(0, delta.y())
                self._start_pos = event.scenePos()
            super().mouseMoveEvent(event)
            self.signals.itemMoved.emit(self.pos())

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setZValue(2)
        if self.scene().mode is Mode.MOVE:
            self._start_pos = None
            super().mouseReleaseEvent(event)
            self.setSelected(False)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.ungrabMouse()
        if self.scene().mode is Mode.MOVE:
            self.signals.itemDoubleClicked.emit()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode in (Mode.MOVE, Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            self._hover_state = True
        # super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if self.scene().mode in (Mode.MOVE, Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            self._hover_state = True
        else:
            self._hover_state = False
        # super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._hover_state = False
        # super().hoverLeaveEvent(event)

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
    def center(self) -> 'QPointF':
        return QPointF(self.x() + self._size / 2, self.y() + self._size / 2)

    @property
    def position(self) -> 'PlayerPositionType':
        return self._position

    @property
    def size(self) -> int:
        return self._size

    @property
    def text(self) -> str:
        return self._text

    @property
    def text_color(self) -> str:
        return self._text_color

    @property
    def player_color(self) -> str:
        return self._player_color

    @property
    def actions(self) -> list['Graphics.ActionView']:
        return self._actions

    @property
    def rect(self) -> 'QRectF':
        return self._rect

    def add_action_item(self, action_data: dict) -> 'Graphics.ActionView':
        action_item = Graphics.ActionView(**action_data, scene=self.scene(), player=self)
        self._actions.append(action_item)
        return action_item

    def remove_action_item(self, action_item: 'Graphics.ActionView') -> None:
        action_item.remove_all_action_parts()
        self._actions.remove(action_item)

    def remove_all_action_items(self) -> None:
        if self._actions:
            for action in self._actions:
                action.remove_all_action_parts()
            self._actions.clear()


class FirstTeamPlayerView(PlayerView):
    font = QFont('Times New Roman', 5, QFont.Bold)

    def __init__(self, model_uuid: 'UUID', x: float, y: float, team_type: 'TeamType', position: 'PlayerPositionType',
                 text: str, text_color: str, fill_type: 'FillType', player_color: str):
        super().__init__(model_uuid, x, y, team_type, position, text, text_color, player_color)
        self._gradient_fill: 'QBrush' = QBrush()
        self._fill_type = fill_type
        self._set_linear_gradient()

    @property
    def fill_type(self) -> 'FillType':
        return self._fill_type

    def set_player_style(self, fill_type: 'FillType', text: str, text_color: str, player_color: str) -> None:
        self._text = text
        self._text_color = text_color
        self._text_pen.setColor(text_color)
        self._player_color = player_color
        self._default_pen.setColor(player_color)
        self._hover_pen.setColor(player_color)
        self._fill_type = fill_type
        self._set_linear_gradient()

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None):
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setFont(self.font)
        painter.setBrush(self._gradient_fill)
        if self.isSelected():
            painter.setPen(self._selected_pen)
        elif self._hover_state:
            painter.setPen(self._hover_pen)
        else:
            painter.setPen(self._default_pen)
        if self._position is PlayerPositionType.CENTER:
            painter.drawRect(self._rect)
        else:
            painter.drawEllipse(self._rect)
        if self._text.strip():
            painter.setPen(self._text_pen)
            painter.drawText(self._rect, Qt.AlignCenter, self._text)
        self.update()

    def _set_linear_gradient(self) -> None:
        if self._fill_type is FillType.WHITE:
            gradient = QLinearGradient()
            gradient.setStart(0, 0)
            gradient.setFinalStop(self._size, 0)
            gradient.setColorAt(0, QColor(f'#afffffff'))
        elif self._fill_type is FillType.FULL:
            gradient = QLinearGradient()
            gradient.setStart(0, 0)
            gradient.setFinalStop(self._size, 0)
            gradient.setColorAt(0, QColor(f'#9f{self._player_color[1:]}'))
        elif self._fill_type is FillType.LEFT:
            gradient = QLinearGradient()
            gradient.setStart(self._size / 2, 0)
            gradient.setFinalStop(self._size / 2 + 0.001, 0)
            gradient.setColorAt(0, QColor(f'#9f{self._player_color[1:]}'))
            gradient.setColorAt(1, QColor('#afffffff'))
        elif self._fill_type is FillType.RIGHT:
            gradient = QLinearGradient()
            gradient.setStart(self._size / 2, 0)
            gradient.setFinalStop(self._size / 2 + 0.001, 0)
            gradient.setColorAt(0, QColor('#afffffff'))
            gradient.setColorAt(1, QColor(f'#9f{self._player_color[1:]}'))
        elif self._fill_type is FillType.MID:
            gradient = QLinearGradient()
            gradient.setStart(0, 0)
            gradient.setFinalStop(self._size, 0)
            gradient.setColorAt(0, QColor('#afffffff'))
            gradient.setColorAt(0.355, QColor('#afffffff'))
            gradient.setColorAt(0.356, QColor(f'#9f{self._player_color[1:]}'))
            gradient.setColorAt(0.650, QColor(f'#9f{self._player_color[1:]}'))
            gradient.setColorAt(0.651, QColor('#afffffff'))
            gradient.setColorAt(1, QColor('#afffffff'))
        self._gradient_fill = QBrush(gradient)


class SecondTeamPlayerView(PlayerView):
    _letter_symbol_font = QFont('Times New Roman', 10, QFont.Bold)
    _triangle_symbol_font = QFont('Times New Roman', 5, QFont.Bold)

    def __init__(self, model_uuid: 'UUID', x: float, y: float, team_type: 'TeamType', position: 'PlayerPositionType',
                 text: str, text_color: str, symbol_type: 'SymbolType', player_color: str):
        super().__init__(model_uuid, x, y, team_type, position, text, text_color, player_color)
        self._symbol_type = symbol_type
        self._blank_letter_pen = QPen(QColor(player_color), self._border_width,
                                      s=Qt.DashDotLine, c=Qt.RoundCap, j=Qt.RoundJoin)
        # Треугольник вершиной вверх
        self._polygon_top = QPolygonF((QPointF(self._size / 2, 2),  # Вершина
                                       QPointF(2, self._size - 3),  # Основание левая точка
                                       QPointF(self._size - 2, self._size - 3),))  # Основание правая точка
        # Параметры отрисовки текста внутри треугольника вершиной вверх
        self._polygon_top_text_config = (QRectF(0, 4, self._size, self._size - 4), Qt.AlignCenter, self._text)
        # Треугольник вершиной вниз
        self._polygon_bot = QPolygonF((QPointF(self._size / 2, self._size - 2),  # Вершина
                                       QPointF(2, 3),  # Основание левая точка
                                       QPointF(self._size - 2, 3),))  # Основание правая точка
        # Параметры отрисовки текста внутри треугольника вершиной вниз
        self._polygon_bot_text_config = (QRectF(0, - 3, self._size, self._size + 3), Qt.AlignCenter, self._text)
        # Крест
        self._cross = (QLineF(QPointF(5, 5), QPointF(self._size - 5, self._size - 5)),
                       QLineF(QPointF(self._size - 5, 5), QPointF(5, self._size - 5)))

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: Optional['QWidget'] = None) -> None:
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.brush().setColor(QColor('#bfffffff'))
        if self.isSelected():
            painter.setPen(self._selected_pen)
        elif self._hover_state:
            painter.setPen(self._hover_pen)
        elif self._symbol_type is SymbolType.LETTER and not self._text.strip():
            painter.setPen(self._blank_letter_pen)
            painter.drawEllipse(self._rect)
        else:
            painter.setPen(self._default_pen)

        if self._symbol_type is SymbolType.LETTER:
            if self.isSelected() or self._hover_state:
                painter.drawEllipse(self._rect)
            if self._text.strip():
                painter.setPen(self._text_pen)
                painter.setFont(self._letter_symbol_font)
                painter.drawText(self._rect, Qt.AlignCenter, self._text)
        elif self._symbol_type is SymbolType.TRIANGLE_TOP:
            painter.drawPolygon(self._polygon_top)
            if self._text.strip():
                painter.setPen(self._text_pen)
                painter.setFont(self._triangle_symbol_font)
                painter.drawText(*self._polygon_top_text_config)
        elif self._symbol_type is SymbolType.TRIANGLE_BOT:
            painter.drawPolygon(self._polygon_bot)
            if self._text.strip():
                painter.setPen(self._text_pen)
                painter.setFont(self._triangle_symbol_font)
                painter.drawText(*self._polygon_bot_text_config)
        elif self._symbol_type is SymbolType.CROSS:
            painter.drawLines(self._cross)
        self.update()

    @property
    def symbol_type(self) -> 'SymbolType':
        return self._symbol_type

    def set_player_style(self, symbol_type: 'SymbolType', text: Optional[str], text_color: str,
                         player_color: str) -> None:
        self._symbol_type = symbol_type
        self._text = text
        self._text_color = text_color
        self._text_pen.setColor(text_color)
        self._player_color = player_color
        self._default_pen.setColor(player_color)
        self._hover_pen.setColor(player_color)
        self._blank_letter_pen.setColor(player_color)





