from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from Models import FigureModel


__all__ = ('MoveFigureCommand', 'ChangeFigureStyleCommand', 'ChangeFigureSizeCommand')


class MoveFigureCommand(QUndoCommand):
    def __init__(self, figure_model: 'FigureModel', new_pos_x: float, new_pos_y: float):
        super().__init__('Перемещение фигуры.')
        self._figure_model = figure_model
        self._last_pos_x = self._figure_model.x
        self._last_pos_y = self._figure_model.y
        self._new_pos_x = new_pos_x
        self._new_pos_y = new_pos_y

    def redo(self) -> None:
        self._figure_model.set_pos(self._new_pos_x, self._new_pos_y)

    def undo(self) -> None:
        self._figure_model.set_pos(self._last_pos_x, self._last_pos_y)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, MoveFigureCommand):
            return False
        if other._figure_model is not self._figure_model:
            return False
        self._new_pos_x, self._new_pos_y = other._new_pos_x, other._new_pos_y
        return True


class ChangeFigureStyleCommand(QUndoCommand):
    def __init__(self, figure_model: 'FigureModel',
                 new_border: bool, new_border_color: str, new_border_thickness: int,
                 new_fill: bool, new_fill_color: str, new_fill_opacity: str):
        super().__init__('Изменение фигуры (границы, заливка, и тд.')
        self._figure_model = figure_model
        self._last_border = self._figure_model.border
        self._last_border_thickness = self._figure_model.border_thickness
        self._last_border_color = self._figure_model.border_color
        self._last_fill = self._figure_model.fill
        self._last_fill_color = self._figure_model.fill_color
        self._last_fill_opacity = self._figure_model.fill_opacity
        self._new_border = new_border
        self._new_border_color = new_border_color
        self._new_border_thickness = new_border_thickness
        self._new_fill = new_fill
        self._new_fill_color = new_fill_color
        self._new_fill_opacity = new_fill_opacity

    def redo(self) -> None:
        self._figure_model.set_figure_style(self._new_border, self._new_border_thickness, self._new_border_color,
                                            self._new_fill, self._new_fill_opacity, self._new_fill_color)

    def undo(self) -> None:
        self._figure_model.set_figure_style(self._last_border, self._last_border_thickness, self._last_border_color,
                                            self._last_fill, self._last_fill_opacity, self._last_fill_color)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, ChangeFigureStyleCommand):
            return False
        if other._figure_model is not self._figure_model:
            return False
        self._new_border, self._new_border_color, self._new_border_thickness, self._new_fill,\
            self._new_fill_color, self._new_fill_opacity = \
            other._new_border, other._new_border_color, other._new_border_thickness, other._new_fill, \
            other._new_fill_color, other._new_fill_opacity
        return True


class ChangeFigureSizeCommand(QUndoCommand):
    def __init__(self, figure_model: 'FigureModel', new_pos_x: float, new_pos_y: float,
                 new_width: float, new_height: float):
        super().__init__('Изменение размера фигуры.')
        self._figure_model = figure_model
        self._last_pos_x = self._figure_model.x
        self._last_pos_y = self._figure_model.y
        self._last_width = self._figure_model.width
        self._last_height = self._figure_model.height
        self._new_pos_x = new_pos_x
        self._new_pos_y = new_pos_y
        self._new_width = new_width
        self._new_height = new_height

    def redo(self) -> None:
        self._figure_model.set_size(self._new_pos_x, self._new_pos_y, self._new_width, self._new_height)

    def undo(self) -> None:
        self._figure_model.set_size(self._last_pos_x, self._last_pos_y, self._last_width, self._last_height)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, ChangeFigureSizeCommand):
            return False
        if other._figure_model is not self._figure_model:
            return False
        self._new_pos_x, self._new_pos_y, self._new_width, self._new_height = \
            other._new_pos_x, other._new_pos_y, other._new_width, other._new_height
        return True

