from typing import TYPE_CHECKING, Union, Optional, Any
from datetime import datetime
from math import radians, cos, sin
from dataclasses import dataclass
from collections import namedtuple

from PySide6.QtWidgets import QGraphicsScene, QGraphicsItemGroup
from PySide6.QtCore import Qt, Signal, QPointF, QLineF
from PySide6.QtGui import QPen, QBrush, QColor, QTransform

from .field_parts import FieldTriangle, FieldNumber
from Config import football_field_data as football_field, flag_field_data as flag_field
from Core.Enums import PlaybookType, Mode, FigureType, ActionLineType
from Views import Graphics

if TYPE_CHECKING:
    from PySide6.QtWidgets import QGraphicsSceneMouseEvent
    from PySide6.QtGui import QFocusEvent

__all__ = ('Field', )

tmp_painted_action_data = namedtuple('TmpActionData', 'action_lines final_actions')


def timeit(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        print(datetime.now() - start)
        return result
    return wrapper


@dataclass
class SceneConfig:
    mode: 'Mode' = Mode.MOVE
    line_thickness: int = 4
    color: str = '#000000'
    font_type: str = 'Times New Roman'
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    underline: bool = False


class Field(QGraphicsScene):
    modeChanged = Signal(Mode)
    figurePainted = Signal(dict)  # figure_type, x, y, width, height, border, border_thickness, border_color, fill, fill_color, fill_opacity
    figureRemoveClicked = Signal(object)  # .model_uuid
    pencilPainted = Signal(list)
    labelPlaced = Signal(dict)  # x, y, width, height, font_type, font_size, bold, italic, underline, color
    labelRemoveClicked = Signal(object)  # .model_uuid
    labelSelected = Signal(object)  # Graphics.ProxyTextEdit
    labelDeselected = Signal()

    def __init__(self, playbook_type: 'PlaybookType', parent=None):
        super().__init__(parent)
        self._playbook_type = playbook_type
        getattr(self, f'draw_{self._playbook_type.name.lower()}_field')()

        self._config = SceneConfig()

        self._first_team_players: list['Graphics.FirstTeamPlayerView'] = []  # Представления игроков первой комманды
        self._second_team_players: list['Graphics.SecondTeamPlayerView'] = []  # Представления игроков второй комманды
        self._additional_offence_player: Optional['Graphics.FirstTeamPlayerView'] = None  # Представление дополнительного игрока

        self._figures: list[Union['Graphics.RectangleView', 'Graphics.EllipseView']] = []  # Представления фигур
        self._labels: list['Graphics.ProxyWidgetLabel'] = []  # Представления надписей
        self._pencil_lines: list['Graphics.PencilLineView'] = []  # Представления линий карандаша
        self._tmp_figure: Optional['Graphics.RectangleView', 'Graphics.EllipseView'] = None  # Используется при интерактивном рисовании новой фигуры
        self._tmp_painted_pencil_lines: list['Graphics.PencilLineView'] = []  # Используется при интерактивном рисовании карандашом
        self._tmp_painted_pencil_lines_data: list[dict] = []  # Используется при интерактивном рисовании карандашом. Эти данные получаются из нарисованной линии и передаются сигналом в презентер

        self._allow_action_painting_process: bool = False  # Флаг разрешения рисования, активируется по клику на игрока или на действия игрока. Процесс рисования действий заканчивается при клике правой кнопкой мыши
        self._action_painting_process: bool = False  # Флаг показывает что сейчас идёт процесс рисования линия за линией. Процесс рисования действий заканчивается при клике правой кнопкой мыши
        self._painting_process_mouse_pressed: bool = False  # Флаг нажатия кнопки мыши. Нужен для того, чтобы при рисовании действия игрока исключить нажатие другой кнопки мыши (правой), при нажатой левой
        self._first_painting_action_line: bool = False  # Флаг рисования первого действия от игрока. Нужен для расчёта стартовой точки, рисуемого действия. Стартовая располагается на границе игрока.
        self._current_player_action_painting: Union[None, 'Graphics.FirstTeamPlayerView', 'Graphics.SecondTeamPlayerView'] = None  # Текущий игрок, для которого рисуется действие.
        self._current_action_action_painting: Optional['Graphics.ActionView'] = None
        self._start_pos: Optional['QPointF'] = None  # Координаты начала рисования действий, фигур и тд.
        self._last_start_pos: Optional['QPointF'] = None  # Координаты предыдущей стартовой точки. Используется при завершении рисования действия, для вычисления угла поворота стрелки маршрута или линии блока.
        self._current_action_line: Optional['Graphics.ActionLineView'] = None  # Текущая линия действия.
        self._tmp_painted_action_group: Optional['QGraphicsItemGroup'] = None
        self._tmp_painted_action_data = tmp_painted_action_data(list(), list())

    @property
    def mode(self) -> 'Mode':
        return self._config.mode

    @property
    def color(self) -> str:
        return self._config.color

    @property
    def line_thickness(self) -> int:
        return self._config.line_thickness

    @property
    def font_type(self) -> str:
        return self._config.font_type

    @property
    def font_size(self) -> int:
        return self._config.font_size

    @property
    def bold(self) -> bool:
        return self._config.bold

    @property
    def italic(self) -> bool:
        return self._config.italic

    @property
    def underline(self) -> bool:
        return self._config.underline

    @property
    def first_team_players(self) -> list['Graphics.FirstTeamPlayerView']:
        return self._first_team_players.copy()

    @property
    def second_team_players(self) -> list['Graphics.SecondTeamPlayerView']:
        return self._second_team_players.copy()

    @property
    def additional_player(self) -> Optional['Graphics.FirstTeamPlayerView']:
        return self._additional_offence_player

    @property
    def figures(self) -> list[Union['Graphics.RectangleView', 'Graphics.EllipseView']]:
        return self._figures.copy()

    @property
    def labels(self) -> list['Graphics.ProxyWidgetLabel']:
        return self._labels.copy()

    @property
    def pencil_lines(self) -> list['Graphics.PencilLineView']:
        return self._pencil_lines.copy()

    def set_config(self, key: str, value: Any) -> None:
        '''Установка конфига. Мод, Цвет, толщина линий, размер текста и тд.'''
        if not hasattr(self._config, key):
            raise ValueError(f'{key} - неправильное значение ключа конфига сцены.')
        setattr(self._config, key, value)
        if key == 'mode':
            self.modeChanged.emit(self._config.mode)

    def place_first_team_player_item(self, player_data: dict) -> 'Graphics.FirstTeamPlayerView':
        '''Размещение представления игрока первой команды на сцене.
        Возвращает представление этого игрока'''
        player_item = Graphics.FirstTeamPlayerView(**player_data)
        self.addItem(player_item)
        self._first_team_players.append(player_item)
        return player_item

    def place_second_team_player_item(self, player_data: dict) -> 'Graphics.SecondTeamPlayerView':
        '''Размещение представления игрока второй команды на сцене.
        Возвращает представление этого игрока'''
        player_item = Graphics.SecondTeamPlayerView(**player_data)
        self.addItem(player_item)
        self._second_team_players.append(player_item)
        return player_item

    def place_additional_player_item(self, player_data: dict) -> 'Graphics.FirstTeamPlayerView':
        '''Размещение представления дополнительного игрока команды нападения на сцене.
        Возвращает представление этого игрока'''
        player_item = Graphics.FirstTeamPlayerView(**player_data)
        self.addItem(player_item)
        self._additional_offence_player = player_item
        return player_item

    def remove_first_team_player_items(self) -> None:
        '''Удаление со сцены представлений игроков первой команды.'''
        removed_group = self.createItemGroup(self._first_team_players)
        self.removeItem(removed_group)
        self._first_team_players.clear()

    def remove_second_team_player_items(self) -> None:
        '''Удаление со сцены представлений игроков второй команды.'''
        removed_group = self.createItemGroup(self._second_team_players)
        self.removeItem(removed_group)
        self._second_team_players.clear()

    def remove_additional_player_item(self) -> None:
        '''Удаление со сцены представления дополнительного игрока команды нападения.'''
        self.removeItem(self._additional_offence_player)
        self._additional_offence_player = None

    def place_figure_item(self, figure_data: dict) -> Union['Graphics.RectangleView', 'Graphics.EllipseView']:
        if figure_data['figure_type'] is FigureType.RECTANGLE:
            figure_item = Graphics.RectangleView(**figure_data)
        if figure_data['figure_type'] is FigureType.ELLIPSE:
            figure_item = Graphics.EllipseView(**figure_data)
        self.addItem(figure_item)
        self._figures.append(figure_item)
        return figure_item

    def remove_figure_item(self, figure_item: Union['Graphics.RectangleView', 'Graphics.EllipseView']) -> None:
        self.removeItem(figure_item)
        self._figures.remove(figure_item)

    def remove_all_figure_items(self) -> None:
        figures_group = self.createItemGroup(self._figures)
        self.removeItem(figures_group)
        self._figures.clear()

    def place_pencil_line_item(self, pencil_line_data: dict) -> 'Graphics.PencilLineView':
        pencil_line_item = Graphics.PencilLineView(**pencil_line_data)
        self.addItem(pencil_line_item)
        self._pencil_lines.append(pencil_line_item)
        return pencil_line_item

    def remove_pencil_line_item(self, pencil_line_item: 'Graphics.PencilLineView') -> None:
        self.removeItem(pencil_line_item)
        self._pencil_lines.remove(pencil_line_item)

    def remove_all_pencil_line_items(self) -> None:
        pencil_lines_group = self.createItemGroup(self._pencil_lines)
        self.removeItem(pencil_lines_group)
        self._pencil_lines.clear()

    def place_label_item(self, label_data: dict) -> 'Graphics.ProxyWidgetLabel':
        label_item = Graphics.ProxyWidgetLabel(**label_data)
        self.addItem(label_item)
        self._labels.append(label_item)
        return label_item

    def remove_label_item(self, label_item: 'Graphics.ProxyWidgetLabel') -> None:
        self.removeItem(label_item)
        self._labels.remove(label_item)

    def remove_all_label_items(self) -> None:
        labels_group = self.createItemGroup(self._labels)
        self.removeItem(labels_group)
        self._labels.clear()

    def focusOutEvent(self, event: 'QFocusEvent') -> None:
        self._allow_action_painting_process = False
        self._action_painting_process = False
        self._painting_process_mouse_pressed = False
        self._first_painting_action_line = False
        if self._current_player_action_painting:
            self._current_player_action_painting.setSelected(False)
            self._current_player_action_painting.hover_state = False
            self._current_player_action_painting = None
        if self._current_action_action_painting:
            self._current_action_action_painting.set_hover_state(False)
            self._current_action_action_painting = None
        self._start_pos = None
        self._last_start_pos = None
        self._current_action_line = None
        if self._tmp_painted_action_group:
            self.removeItem(self._tmp_painted_action_group)
            self._tmp_painted_action_group = None
        self._tmp_painted_action_data.action_lines.clear()
        self._tmp_painted_action_data.final_actions.clear()
        if self._tmp_figure:
            self.removeItem(self._tmp_figure)
            self._tmp_figure = None
        if self._tmp_painted_pencil_lines:
            pencil_lines_group = self.createItemGroup(self._tmp_painted_pencil_lines)
            self.removeItem(pencil_lines_group)
            self._tmp_painted_pencil_lines.clear()
        if self._tmp_painted_pencil_lines_data:
            self._tmp_painted_pencil_lines_data.clear()
        super().focusOutEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Обработка нажатия кнопки мыши и перенаправление на другие методы в зависимости от mode
        if self._config.mode is Mode.MOVE:
            super().mousePressEvent(event)
        elif self._config.mode in (Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            if self._allow_action_painting_process:
                self.action_mousePressEvent(event)
            elif event.button() == Qt.LeftButton:  # Это условие для выбора игрока или действия от которого будут рисоваться действия
                super().mousePressEvent(event)
                item = self.itemAt(event.scenePos(), QTransform())
                if isinstance(item, Graphics.PlayerView):
                    self._allow_action_painting_process = True
                    self._current_player_action_painting = item
                    self._current_player_action_painting.setSelected(True)
                    self._first_painting_action_line = True
                    self._tmp_painted_action_group = QGraphicsItemGroup()
                    self.addItem(self._tmp_painted_action_group)
                elif isinstance(item, Graphics.ActionLineView) and \
                        (self._config.mode in (Mode.ROUTE, Mode.BLOCK) or
                         (self._config.mode.MOTION and item.action_type is ActionLineType.MOTION)):
                    self._allow_action_painting_process = True
                    self._current_action_action_painting = item.action
                    self._current_player_action_painting = item.action.player
                    self._current_player_action_painting.setSelected(True)
                    self._tmp_painted_action_group = QGraphicsItemGroup()
                    self.addItem(self._tmp_painted_action_group)
                    self._start_pos = event.scenePos()
        elif self._config.mode is Mode.ERASE:
            super().mousePressEvent(event)
        elif self._config.mode in (Mode.RECTANGLE, Mode.ELLIPSE):
            self.figure_mousePressEvent(event)
        elif self._config.mode is Mode.LABEL:
            self.label_mousePressEvent(event)
        elif self._config.mode is Mode.PENCIL:
            self.pencil_mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Обработка движения курсора мыши и перенаправление на другие методы в зависимости от mode
        if self.mode is Mode.MOVE:
            super().mouseMoveEvent(event)
        elif self.mode in (Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            if self._allow_action_painting_process:
                self.action_mouseMoveEvent(event)
            else:
                super().mouseMoveEvent(event)
        elif self.mode is Mode.ERASE:
            super().mouseMoveEvent(event)
        elif self.mode in (Mode.RECTANGLE, Mode.ELLIPSE):
            self.figure_mouseMoveEvent(event)
        elif self.mode is Mode.PENCIL:
            self.pencil_mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Обработка отпускания кнопки мыши и перенаправление на другие методы в зависимости от mode
        if self.mode is Mode.MOVE:
            super().mouseReleaseEvent(event)
        elif self.mode in (Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            if self._allow_action_painting_process:
                self.action_mouseReleaseEvent(event)
            # else:
            #     super().mouseReleaseEvent(event)
        elif self.mode in (Mode.RECTANGLE, Mode.ELLIPSE):
            self.figure_mouseReleaseEvent(event)
        elif self.mode is Mode.PENCIL:
            self.pencil_mouseReleaseEvent(event)

    def action_mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование действий игроков
        if not self._action_painting_process and event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                if self._first_painting_action_line and not self._start_pos:
                    self._start_pos = self._get_action_line_start_pos(self._current_player_action_painting, event.scenePos())
                self._current_action_line = Graphics.ActionLineView(getattr(ActionLineType, self._config.mode.name),
                                                                    self._start_pos.x(), self._start_pos.y(),
                                                                    event.scenePos().x(), event.scenePos().y(),
                                                                    self._config.line_thickness, self._config.color)
                self._tmp_painted_action_group.addToGroup(self._current_action_line)
                self._action_painting_process = True
                self._painting_process_mouse_pressed = True
        elif self._action_painting_process and not self._current_action_line and event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                self._current_action_line = Graphics.ActionLineView(getattr(ActionLineType, self._config.mode.name),
                                                                    self._start_pos.x(), self._start_pos.y(),
                                                                    event.scenePos().x(), event.scenePos().y(),
                                                                    self._config.line_thickness, self._config.color)
                self._tmp_painted_action_group.addToGroup(self._current_action_line)
                self._painting_process_mouse_pressed = True
        elif self._action_painting_process and not self._painting_process_mouse_pressed and \
                event.button() == Qt.RightButton:
            final_action_item = self._get_final_action(self.mode, self._last_start_pos, self._start_pos)
            if final_action_item:
                self._tmp_painted_action_group.addToGroup(final_action_item)
                self._tmp_painted_action_data.final_actions.append(final_action_item.get_data())
            if self._current_action_action_painting:
                self._current_action_action_painting.optionalActionPainted.emit(self._tmp_painted_action_data)
            else:
                self._current_player_action_painting.signals.actionPainted.emit(self._tmp_painted_action_data)
            self.removeItem(self._tmp_painted_action_group)
            self._tmp_painted_action_group = None
            self._tmp_painted_action_data.action_lines.clear()
            self._tmp_painted_action_data.final_actions.clear()
            self._current_player_action_painting.setSelected(False)
            self._current_player_action_painting.hover_state = False
            self._current_player_action_painting.ungrabMouse()
            self._current_player_action_painting = None
            if self._current_action_action_painting:
                self._current_action_action_painting.set_hover_state(False)
                self._current_action_action_painting = None
            self._current_action_line = None
            self._start_pos = None
            self._last_start_pos = None
            self._action_painting_process = False
            self._allow_action_painting_process = False
            # self.update()

    def action_mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование действий игроков
        if self._current_action_line:
            if self._first_painting_action_line:
                self._start_pos = self._get_action_line_start_pos(self._current_player_action_painting, event.scenePos())
            if self.check_field_borders(event.scenePos()):
                self._current_action_line.setLine(self._start_pos.x(), self._start_pos.y(), event.scenePos().x(), event.scenePos().y())
            else:
                self._current_action_line.setLine(self._start_pos.x(), self._start_pos.y(), self._start_pos.x(), self._start_pos.y())

    def action_mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование действий игроков
        if self._current_action_line and event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                self._current_action_line.setLine(self._start_pos.x(), self._start_pos.y(),
                                                  event.scenePos().x(), event.scenePos().y())
                self._tmp_painted_action_data.action_lines.append(self._current_action_line.get_data())
                self._tmp_painted_action_group.addToGroup(self._current_action_line)
                self._last_start_pos = self._start_pos
                self._start_pos = event.scenePos()
                self._current_action_line = None
                self._painting_process_mouse_pressed = False
                self._first_painting_action_line = False
            else:
                self._current_action_line.setLine(self._start_pos.x(), self._start_pos.y(),
                                                  self._start_pos.x(), self._start_pos.y(),)

    def _get_action_line_start_pos(self, player: Union['Graphics.FirstTeamPlayerView', 'Graphics.SecondTeamPlayerView'],
                                   line_finish_pos: 'QPointF') -> 'QPointF':
        '''Расчёт начальной точки, находящейся на границе игрока, при рисовании первой линии действия игрока'''
        angle = QLineF(player.center, line_finish_pos).angle()
        radius = player.size / 2
        x = cos(radians(angle)) * radius
        y = sin(radians(angle)) * radius
        return QPointF(player.center.x() + x, player.center.y() - y)

    def _get_final_action(self, mode: 'Mode', start_pos: 'QPointF', finish_pos: 'QPointF') -> Union[None, 'Graphics.FinalActionRouteView', 'Graphics.FinalActionBlockView']:
        '''Получение финала (стрелка для маршрута и линия для блока) действия игрока'''
        angle = QLineF(start_pos, finish_pos).angle()
        if mode is Mode.ROUTE:
            arrow = Graphics.FinalActionRouteView(finish_pos.x(), finish_pos.y(),
                                                  angle, self._config.line_thickness, self._config.color)
            return arrow
        elif mode is Mode.BLOCK:
            line = Graphics.FinalActionBlockView(finish_pos.x(), finish_pos.y(), angle, self._config.line_thickness,
                                                 self._config.color)
            return line
        return None

    def figure_mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование фигур
        if not self._action_painting_process and event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                self._start_pos = event.scenePos()
                if self.mode is Mode.RECTANGLE:
                    self._tmp_figure = Graphics.RectangleView(self._start_pos.x(), self._start_pos.y(), 0, 0,
                                                              True, self._config.line_thickness, self._config.color)
                elif self.mode is Mode.ELLIPSE:
                    self._tmp_figure = Graphics.EllipseView(self._start_pos.x(), self._start_pos.y(), 0, 0,
                                                            True, self._config.line_thickness, self._config.color)
                if self._tmp_figure:
                    self.addItem(self._tmp_figure)
                self._action_painting_process = True

    def figure_mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование фигур
        if self._action_painting_process and self._tmp_figure:
            if self.check_field_borders(event.scenePos()):
                self._tmp_figure.set_rect(self._start_pos.x(), self._start_pos.y(),
                                          event.scenePos().x() - self._start_pos.x(),
                                          event.scenePos().y() - self._start_pos.y())
            else:
                self._tmp_figure.set_rect(self._start_pos.x(), self._start_pos.y(), 0, 0)
            self.update()

    def figure_mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование фигур
        if self._action_painting_process and self._tmp_figure and event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                self._tmp_figure.set_rect(self._start_pos.x(), self._start_pos.y(),
                                          event.scenePos().x() - self._start_pos.x(),
                                          event.scenePos().y() - self._start_pos.y())
                self._tmp_figure.normalizate()
                figure_data = self._tmp_figure.get_data()
                self.removeItem(self._tmp_figure)
                self._action_painting_process = False
                self._start_pos = None
                self._tmp_figure = None
                self.figurePainted.emit(figure_data)

    def label_mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        '''Размещение надписи на сцене'''
        if event.button() == Qt.LeftButton:
            self.set_config('mode', Mode.MOVE)
            default_width = Graphics.ProxyWidgetLabel.default_width
            default_height = Graphics.ProxyWidgetLabel.default_height
            if event.scenePos().x() < 0:
                x = 0
            elif event.scenePos().x() + default_width > self.sceneRect().width():
                x = event.scenePos().x() - (event.scenePos().x() + default_width - self.sceneRect().width())
            else:
                x = event.scenePos().x()
            if event.scenePos().y() < 0:
                y = 0
            elif event.scenePos().y() + default_height > self.sceneRect().height():
                y = event.scenePos().y() - (event.scenePos().y() + default_height - self.sceneRect().height())
            else:
                y = event.scenePos().y()
            tmp_proxy_label = Graphics.ProxyWidgetLabel(x, y, '', self._config.font_type, self._config.font_size,
                                                        self._config.bold, self._config.italic, self._config.underline,
                                                        self._config.color, tmp_label=True)
            self.addItem(tmp_proxy_label)
            tmp_proxy_label.widget()
            tmp_proxy_label.widget().setReadOnly(False)
            tmp_proxy_label.widget().setFocus()
            tmp_proxy_label.widget().update_height()
            self.labelSelected.emit(tmp_proxy_label.widget())

    def pencil_mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование карандашом
        if event.button() == Qt.LeftButton:
            if self.check_field_borders(event.scenePos()):
                self._start_pos = event.scenePos()

    def pencil_mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование карандашом
        if self.check_field_borders(event.scenePos()):
            if self._start_pos:
                line = Graphics.PencilLineView(self._start_pos.x(), self._start_pos.y(), event.scenePos().x(),
                                               event.scenePos().y(), self._config.line_thickness, self._config.color)
                self.addItem(line)
                self._tmp_painted_pencil_lines.append(line)
                self._tmp_painted_pencil_lines_data.append(line.get_data())
                self._start_pos = event.scenePos()
                # self.update()

    def pencil_mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:  # Рисование карандашом
        if event.button() == Qt.LeftButton:
            self._start_pos = None
            painted_pencil_lines_group = self.createItemGroup(self._tmp_painted_pencil_lines)
            self.removeItem(painted_pencil_lines_group)
            self._tmp_painted_pencil_lines.clear()
            self.pencilPainted.emit(self._tmp_painted_pencil_lines_data)
            self._tmp_painted_pencil_lines_data.clear()

    def check_field_x(self, pos_x: float) -> bool:
        '''Проверка попадания координаты в границы поля по оси X (при рисовании фигур, действий и тд.)'''
        return True if 0 < pos_x < self.sceneRect().width() else False

    def check_field_y(self, pos_y: float) -> bool:
        '''Проверка попадания координаты в границы поля по оси Y (при рисовании фигур, действий и тд.)'''
        return True if 0 < pos_y < self.sceneRect().height() else False

    def check_field_borders(self, mouse_pos: 'QPointF') -> bool:
        '''Проверка попадания координаты в границы поля по осям X и Y (при рисовании фигур, действий и тд.)'''
        return True if self.check_field_x(mouse_pos.x()) and self.check_field_y(mouse_pos.y()) else False

    def draw_football_field(self) -> None:
        '''Отрисовка всего футбольного поля размерами 120 ярдов на 53 ярда. Расстояние между хэш-марками 13 ярдов.
        Пропорция length / width должна быть 1200 / 534'''
        field_length = football_field.length
        field_width = football_field.width
        vertical_one_yard = football_field.vertical_one_yard
        vertical_five_yards = football_field.vertical_five_yards
        vertical_ten_yards = football_field.vertical_ten_yards
        vertical_field_center = football_field.vertical_field_center
        horizontal_one_yard = football_field.horizontal_one_yard
        hash_line_center = football_field.hash_line_center
        side_one_yard_line_length = football_field.side_one_yard_line_length
        hash_one_yard_line_length = football_field.hash_one_yard_line_length
        self.setSceneRect(football_field.rect)
        self.addRect(football_field.rect, QPen(Qt.white), QBrush(QColor(Qt.white)))
        # Отрисовка номеров
        numbers_left_1 = [[f'{i}', 90, 14 * horizontal_one_yard] for i in range(10, 60, 10)]
        numbers_left_2 = [[f'{i}', 90, 14 * horizontal_one_yard] for i in range(40, 0, -10)]
        numbers_right_1 = [[f'{i}', -90, 40 * horizontal_one_yard] for i in range(10, 60, 10)]
        numbers_right_2 = [[f'{i}', -90, 40 * horizontal_one_yard] for i in range(40, 0, -10)]
        numbers_left_y = [16.9 * vertical_one_yard + i * vertical_ten_yards for i in range(9)]
        numbers_right_y = [23 * vertical_one_yard + i * vertical_ten_yards for i in range(9)]
        # self.addRect(0, 0, self.field_data.football_field_width, self.field_data.football_field_length, QPen(Qt.transparent), QBrush(QColor('#004400')))
        for i, number in enumerate(numbers_left_1):
            self.addItem(FieldNumber(*number, numbers_left_y[i]))
        for i, number in enumerate(numbers_left_2):
            self.addItem(FieldNumber(*number, numbers_left_y[5 + i]))
        for i, number in enumerate(numbers_right_1):
            self.addItem(FieldNumber(*number, numbers_right_y[i]))
        for i, number in enumerate(numbers_right_2):
            self.addItem(FieldNumber(*number, numbers_right_y[5 + i]))
        # Отрисовка стрелок около номеров
        polygon_top = football_field.number_arrow_polygon_top
        polygon_bot = football_field.number_arrow_polygon_bot
        arrows_right_coordinates_1 = [[43 * horizontal_one_yard, 16 * vertical_one_yard + i * vertical_ten_yards] for i in range(4)]
        arrows_left_coordinates_1 = [[10 * horizontal_one_yard, 16 * vertical_one_yard + i * vertical_ten_yards] for i in range(4)]
        arrows_right_coordinates_2 = [[43 * horizontal_one_yard, 23 * vertical_one_yard + i * vertical_ten_yards] for i in range(5, 9)]
        arrows_left_coordinates_2 = [[10 * horizontal_one_yard, 23 * vertical_one_yard + i * vertical_ten_yards] for i in range(5, 9)]
        for coordinates in arrows_left_coordinates_1:
            self.addItem(FieldTriangle(polygon_top, *coordinates))
        for coordinates in arrows_left_coordinates_2:
            self.addItem(FieldTriangle(polygon_bot, *coordinates))
        for coordinates in arrows_right_coordinates_1:
            self.addItem(FieldTriangle(polygon_top, *coordinates))
        for coordinates in arrows_right_coordinates_2:
            self.addItem(FieldTriangle(polygon_bot, *coordinates))
        # Линия верхней энд-зоны
        self.addLine(0, vertical_ten_yards, field_width, vertical_ten_yards, football_field.ten_yards_line_style)
        # Линия нижней энд-зоны
        self.addLine(0, field_length - vertical_ten_yards, field_width, field_length - vertical_ten_yards, football_field.ten_yards_line_style)
        # Центральная линия
        self.addLine(0, vertical_field_center, field_width, vertical_field_center, football_field.ten_yards_line_style)
        # Десятиярдовые линии
        for j in range(2 * vertical_ten_yards, field_length, vertical_field_center - vertical_ten_yards):
            for i in range(0, vertical_field_center - 2 * vertical_ten_yards, vertical_ten_yards):
                self.addLine(0, j + i, field_width, j + i, football_field.ten_yards_line_style)
        # Пятиярдовые линии
        for i in range(vertical_ten_yards + vertical_five_yards, field_length - vertical_ten_yards, vertical_ten_yards):
            self.addLine(0, i, field_width, i, football_field.other_lines_style)
        # Одноярдовые хэши и боковые линии
        for j in range(vertical_ten_yards, field_length - vertical_ten_yards, vertical_five_yards):
            for i in range(vertical_one_yard, vertical_five_yards, vertical_one_yard):
                # Одноярдовые боковые линии слева
                self.addLine(0, j + i, side_one_yard_line_length, j + i, football_field.other_lines_style)
                # Одноярдовые боковые линии справа
                self.addLine(field_width - side_one_yard_line_length, j + i, field_width, j + i, football_field.other_lines_style)
                # Одноярдовые хеш-линии слева
                self.addLine(QLineF((hash_line_center - hash_one_yard_line_length / 2), j + i,
                                    hash_line_center + hash_one_yard_line_length / 2, j + i),
                             football_field.other_lines_style)
                # Одноярдовые хеш-линии справа
                self.addLine(QLineF(field_width - (hash_line_center - hash_one_yard_line_length / 2), j + i,
                                    field_width - (hash_line_center + hash_one_yard_line_length / 2), j + i),
                             football_field.other_lines_style)
        # Линия конверсии сверху
        self.addLine(QLineF(field_width / 2 - hash_one_yard_line_length / 2,
                            vertical_ten_yards + 3 * vertical_one_yard,
                            field_width / 2 + hash_one_yard_line_length / 2,
                            vertical_ten_yards + 3 * vertical_one_yard),
                     football_field.other_lines_style)
        # Линия конверсии снизу
        self.addLine(QLineF(field_width / 2 - hash_one_yard_line_length / 2,
                            field_length - (vertical_ten_yards + 3 * vertical_one_yard),
                            field_width / 2 + hash_one_yard_line_length / 2,
                            field_length - (vertical_ten_yards + 3 * vertical_one_yard)),
                     football_field.other_lines_style)
        # Граница
        self.addRect(football_field.rect, football_field.border_style)
        # self.addRect(football_field.rect, QPen(QColor(Qt.red), 4))

    def draw_flag_field(self) -> None:
        '''Отрисовка всего поля для флаг футбола размерами 70 ярдов на 25 ярдов.
        Пропорция length / width должна быть 1400 / 508'''
        field_length = flag_field.length
        field_width = flag_field.width
        vertical_one_yard = flag_field.vertical_one_yard
        vertical_five_yards = flag_field.vertical_five_yards
        vertical_ten_yards = flag_field.vertical_ten_yards
        vertical_field_center = flag_field.vertical_field_center
        horizontal_one_yard = flag_field.horizontal_one_yard
        hash_line_center = flag_field.hash_line_center
        hash_one_yard_line_length = flag_field.hash_one_yard_line_length
        side_one_yard_line_length = flag_field.side_one_yard_line_length

        self.setSceneRect(flag_field.rect)
        self.addRect(flag_field.rect, QPen(Qt.white), QBrush(QColor(Qt.white)))
        # Отрисовка номеров
        numbers_left = (('10', 90, 6 * horizontal_one_yard), ('20', 90, 6 * horizontal_one_yard),
                        ('20', 90, 6 * horizontal_one_yard), ('10', 90, 6 * horizontal_one_yard),)
        numbers_right = (('10', -90, 19 * horizontal_one_yard), ('20', -90, 19 * horizontal_one_yard),
                         ('20', -90, 19 * horizontal_one_yard), ('10', -90, 19 * horizontal_one_yard),)
        numbers_left_y = [18.5 * vertical_one_yard + i * vertical_ten_yards for i in range(4)]
        numbers_right_y = [21.5 * vertical_one_yard + i * vertical_ten_yards for i in range(4)]
        for i, number in enumerate(numbers_left):
            self.addItem(FieldNumber(*number, numbers_left_y[i]))
        for i, number in enumerate(numbers_right):
            self.addItem(FieldNumber(*number, numbers_right_y[i]))
        # Отрисовка стрелок около номеров
        polygon_top = flag_field.number_arrow_polygon_top
        polygon_bot = flag_field.number_arrow_polygon_bot
        arrows_left_coordinates_1 = [[4 * horizontal_one_yard, 18 * vertical_one_yard + i * vertical_ten_yards] for i in range(2)]
        arrows_left_coordinates_2 = [[4 * horizontal_one_yard, 11.5 * vertical_one_yard + i * vertical_ten_yards] for i in range(3, 5)]
        arrows_right_coordinates_1 = [[20.5 * horizontal_one_yard, 18 * vertical_one_yard + i * vertical_ten_yards] for i in range(2)]
        arrows_right_coordinates_2 = [[20.5 * horizontal_one_yard, 11.5 * vertical_one_yard + i * vertical_ten_yards] for i in range(3, 5)]
        for coordinates in arrows_left_coordinates_1:
            self.addItem(FieldTriangle(polygon_top, *coordinates))
        for coordinates in arrows_left_coordinates_2:
            self.addItem(FieldTriangle(polygon_bot, *coordinates))
        for coordinates in arrows_right_coordinates_1:
            self.addItem(FieldTriangle(polygon_top, *coordinates))
        for coordinates in arrows_right_coordinates_2:
            self.addItem(FieldTriangle(polygon_bot, *coordinates))
        #  Центральная линия
        self.addLine(0, vertical_field_center, field_width, vertical_field_center, flag_field.ten_yards_line_style)
        # Линия верхней энд-зоны
        self.addLine(0, vertical_ten_yards, field_width, vertical_ten_yards, flag_field.ten_yards_line_style)
        # Линия нижней энд-зоны
        self.addLine(0, field_length - vertical_ten_yards, field_width, field_length - vertical_ten_yards, flag_field.ten_yards_line_style)
        # Пятиярдовые линии
        for j in range(vertical_ten_yards, field_length - vertical_ten_yards, vertical_field_center - vertical_ten_yards):
            for i in range(vertical_five_yards, vertical_field_center - vertical_ten_yards, vertical_five_yards):
                self.addLine(0, j + i, field_width, j + i, flag_field.other_lines_style)
        # Одноярдовые хеши и боковые линии
        for j in range(vertical_ten_yards, field_length - vertical_ten_yards, vertical_five_yards):
            for i in range(vertical_one_yard, vertical_five_yards, vertical_one_yard):
                # Одноярдовые боковые линии слева
                self.addLine(0, j + i, hash_one_yard_line_length, j + i, flag_field.other_lines_style)
                # Одноярдовые боковые линии справа
                self.addLine(field_width - hash_one_yard_line_length, j + i, field_width, j + i, flag_field.other_lines_style)
                # Одноярдовые хеш-линии
                self.addLine(hash_line_center - hash_one_yard_line_length / 2, j + i,
                             hash_line_center + hash_one_yard_line_length / 2, j + i, flag_field.other_lines_style)
        #  Граница
        self.addRect(flag_field.rect, flag_field.border_style)
