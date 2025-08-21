from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QPen, QColor
from PySide6.QtCore import Qt

from Core.Enums import FigureType

if TYPE_CHECKING:
    from PySide6.QtGui import QPaintEvent


class FigurePix(QWidget):
    def __init__(self, figure_type: 'FigureType', border: bool, border_color: str, border_thickness: int,
                 fill: bool, fill_color: str, fill_opacity: str,
                 parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self._figure_type = figure_type
        self._border = border
        self._border_thickness = border_thickness
        self._border_color = border_color
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
        self._pen = QPen(QColor(border_color), border_thickness)
        self._brush = QBrush(QColor(f'{fill_opacity}{fill_color[1:]}'))
        self.setFixedSize(300, 300)

    @property
    def border(self) -> bool:
        return self._border

    @border.setter
    def border(self, value: bool) -> None:
        self._border = value
        self._pen.setColor(self._border_color if value else Qt.transparent)

    @property
    def border_color(self) -> str:
        return self._border_color

    @border_color.setter
    def border_color(self, value: str):
        self._border_color = value
        self._pen.setColor(value if self._border else Qt.transparent)

    @property
    def border_thickness(self) -> int:
        return self._border_thickness

    @border_thickness.setter
    def border_thickness(self, value: int) -> None:
        self._border_thickness = value
        self._pen.setWidth(value)

    @property
    def fill(self) -> bool:
        return self._fill

    @fill.setter
    def fill(self, value: bool) -> None:
        self._fill = value
        self._brush.setColor(f'{self._fill_opacity}{self._fill_color[1:]}' if value else Qt.transparent)

    @property
    def fill_color(self) -> str:
        return self._fill_color

    @fill_color.setter
    def fill_color(self, value: str) -> None:
        self._fill_color = value
        self._brush.setColor(f'{self._fill_opacity}{value[1:]}' if self._fill else Qt.transparent)

    @property
    def fill_opacity(self) -> str:
        return self._fill_opacity

    @fill_opacity.setter
    def fill_opacity(self, value: str) -> None:
        self._fill_opacity = value
        self._brush.setColor(f'{value}{self._fill_color[1:]}' if self._fill else Qt.transparent)

    def paintEvent(self, event: 'QPaintEvent') -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QBrush(QColor(Qt.white)))
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        if self._figure_type is FigureType.RECTANGLE:
            painter.drawRect(50, 50, 200, 200)
        elif self._figure_type is FigureType.ELLIPSE:
            painter.drawEllipse(50, 50, 200, 200)

