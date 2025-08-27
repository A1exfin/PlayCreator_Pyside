from typing import TYPE_CHECKING, Union

from Core import log_method, logger
from Commands import MoveFigureCommand, ChangeFigureStyleCommand, ChangeFigureSizeCommand
from Views.Dialog_windows import DialogEditFigure

if TYPE_CHECKING:
    from PySide6.QtCore import QPointF
    from PlayCreator_main import PlayCreatorApp
    from Views import Graphics
    from View_Models import FigureModel


class FigurePresenter:
    @log_method()
    def __init__(self, execute_command_func: callable, figure_model: 'FigureModel', view: 'PlayCreatorApp',
                 figure_view: Union['Graphics.RectangleView', 'Graphics.EllipseView']):
        self._execute_command_func = execute_command_func
        self._view = view
        self._figure_view = figure_view
        self._model = figure_model
        self._connect_signals()

    @log_method()
    def _connect_signals(self) -> None:
        self._figure_view.signals.itemMoved.connect(self._handle_figure_item_moved)
        self._model.coordsChanged.connect(self._move_figure_item)
        self._figure_view.signals.itemDoubleClicked.connect(self._handle_edit_figure_item)
        self._model.styleChanged.connect(self._change_figure_item_style)
        self._figure_view.signals.itemResized.connect(self._handle_figure_item_resized)
        self._model.sizeChanged.connect(self._change_figure_item_size)

    @log_method()
    def _handle_figure_item_moved(self, new_pos: 'QPointF') -> None:
        if self._model.x != new_pos.x() or self._model.y != new_pos.y():
            move_figure_command = MoveFigureCommand(self._model, new_pos.x(), new_pos.y())
            self._execute_command_func(move_figure_command)

    def _move_figure_item(self, new_pos: 'QPointF') -> None:
        self._figure_view.setPos(new_pos)

    @log_method()
    def _handle_edit_figure_item(self) -> None:
        dialog_edit_figure_config = DialogEditFigure(self._model.figure_type, self._model.border,
                                                     self._model.border_color, self._model.border_thickness,
                                                     self._model.fill, self._model.fill_opacity, self._model.fill_color,
                                                     parent=self._view)
        dialog_edit_figure_config.exec()
        if dialog_edit_figure_config.result():
            data = dialog_edit_figure_config.get_data()
            if self._model.border != data.border or self._model.border_thickness != data.border_thickness or \
                    self._model.border_color != data.border_color or self._model.fill != data.fill or \
                    self._model.fill_opacity != data.fill_opacity or self._model.fill_color != data.fill_color:
                change_figure_config_command = ChangeFigureStyleCommand(self._model,
                                                                        new_border=data.border,
                                                                        new_border_thickness=data.border_thickness,
                                                                        new_border_color=data.border_color,
                                                                        new_fill=data.fill,
                                                                        new_fill_opacity=data.fill_opacity,
                                                                        new_fill_color=data.fill_color)
                self._execute_command_func(change_figure_config_command)

    def _change_figure_item_style(self, new_border: bool, new_border_thickness: int, new_border_color: str,
                                  new_fill: bool, new_fill_opacity: str, new_fill_color: str) -> None:
        self._figure_view.set_figure_style(new_border, new_border_thickness, new_border_color, new_fill,
                                           new_fill_opacity, new_fill_color)

    @log_method()
    def _handle_figure_item_resized(self, new_x: float, new_y: float, new_width: float, new_height: float) -> None:
        if self._model.x != new_x or self._model.y != new_y or self._model.width != new_width or self._model.height != new_height:
            change_figure_size_command = ChangeFigureSizeCommand(self._model, new_x, new_y, new_width, new_height)
            self._execute_command_func(change_figure_size_command)

    def _change_figure_item_size(self, new_x: float, new_y: float, new_width: float, new_height: float) -> None:
        self._figure_view.set_rect(new_x, new_y, new_width, new_height)

