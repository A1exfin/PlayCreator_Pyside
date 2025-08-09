from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QPolygonF, QColor, QLinearGradient
from PySide6.QtCore import Qt, QLineF, QPointF, QRectF
from Config.Enums import FillType, SymbolType, PlayerPositionType

if TYPE_CHECKING:
    from PySide6.QtGui import QPaintEvent


class CustomPushButtonFillType(QPushButton):
    def __init__(self, position: 'PlayerPositionType', text: str, text_color: str, player_color: str,
                 fill_type: 'FillType', parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self._position = position
        self._text = text
        self._text_color = text_color
        self._player_color = player_color
        self._fill_type = fill_type
        self.setFixedSize(40, 40)
        if self._position is PlayerPositionType.CENTER:
            self.rec = QRectF(7.5, 7.5, 25, 25)
        else:
            self.rec = QRectF(5, 5, 30, 30)
        self.font = QFont('Times New Roman', 9, QFont.Bold)
        self._gradient = None
        self.setStyleSheet('''
        QPushButton{
        background-color: WHITE;}
        QPushButton:hover {
        border-color: #bbb}
        QPushButton:checked {
        border-color: red;}
        ''')
        self.set_gradient(player_color)

    def paintEvent(self, event: 'QPaintEvent') -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setFont(self.font)
        painter.setBrush(QBrush(self._gradient))
        painter.setPen(QPen(QColor(self._player_color), 2))
        if self._position is PlayerPositionType.CENTER:
            painter.drawRect(self.rec)
        else:
            painter.drawEllipse(self.rec)
        painter.setPen(QPen(QColor(self._text_color), 2))
        painter.drawText(self.rec, Qt.AlignCenter, self._text)
        self.update()

    def set_gradient(self, player_color: str) -> None:
        self._player_color = player_color
        if self._fill_type is FillType.WHITE:
            self._gradient = QLinearGradient()
            self._gradient.setStart(0, 0)
            self._gradient.setFinalStop(self.rect().right(), 0)
            self._gradient.setColorAt(0, QColor(f'#afffffff'))
        elif self._fill_type is FillType.FULL:
            self._gradient = QLinearGradient()
            self._gradient.setStart(0, 0)
            self._gradient.setFinalStop(self.rect().right(), 0)
            self._gradient.setColorAt(0, QColor(f'#9f{player_color[1:]}'))
        elif self._fill_type is FillType.LEFT:
            self._gradient = QLinearGradient()
            self._gradient.setStart(self.rect().center().x(), 0)
            self._gradient.setFinalStop(self.rect().center().x() + 0.001, 0)
            self._gradient.setColorAt(0, QColor(f'#9f{player_color[1:]}'))
            self._gradient.setColorAt(1, QColor('#afffffff'))
        elif self._fill_type is FillType.RIGHT:
            self._gradient = QLinearGradient()
            self._gradient.setStart(self.rect().center().x(), 0)
            self._gradient.setFinalStop(self.rect().center().x() + 0.001, 0)
            self._gradient.setColorAt(0, QColor('#afffffff'))
            self._gradient.setColorAt(1, QColor(f'#af{player_color[1:]}'))
        elif self._fill_type is FillType.MID:
            self._gradient = QLinearGradient()
            self._gradient.setStart(0, 0)
            self._gradient.setFinalStop(self.rect().right() + 0.001, 0)
            self._gradient.setColorAt(0, QColor('#afffffff'))
            self._gradient.setColorAt(0.355, QColor('#afffffff'))
            self._gradient.setColorAt(0.356, QColor(f'#af{player_color[1:]}'))
            self._gradient.setColorAt(0.650, QColor(f'#af{player_color[1:]}'))
            self._gradient.setColorAt(0.651, QColor('#afffffff'))
            self._gradient.setColorAt(1, QColor('#afffffff'))

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, value: str) -> None:
        self._text_color = value

    @property
    def player_color(self) -> str:
        return self._player_color

    @player_color.setter
    def player_color(self, value: str) -> None:
        self._player_color = value

    @property
    def fill_type(self) -> 'FillType':
        return self._fill_type


class CustomPushButtonSymbolType(QPushButton):
    def __init__(self, text: str, player_text_color: str, player_color: str,  symbol: 'SymbolType', parent=None):
        super().__init__(parent)
        self._text = text
        self._text_color = player_text_color
        self._player_color = player_color
        self._symbol = symbol
        self.setCheckable(True)
        self.setFixedSize(40, 40)
        self._rec = QRectF(0, 0, self.width(), self.height())
        self._font_letter = QFont('Times New Roman', 18)
        self._font_triangle = QFont('Times New Roman', 12)
        # Треугольник вершиной вверх
        self._polygon_top = (QPointF(self.width() / 2, 7),  # Вершина
                             QPointF(5, self.height() - 7),  # Основание левая точка
                             QPointF(self.width() - 5, self.height() - 7),)  # Основание правая точка
        # Треугольник вершиной вниз
        self._polygon_bot = (QPointF(self.width() / 2, self.height() - 7),  # Вершина
                             QPointF(5, 7),  # Основание левая точка
                             QPointF(self.width() - 5, 7),)  # Основание правая точка
        # Крест
        self._line1 = QLineF(QPointF(9, 9), QPointF(self.width() - 9, self.height() - 9))
        self._line2 = QLineF(QPointF(self.width() - 9, 9), QPointF(9, self.height() - 9))
        self.setStyleSheet('''
        QPushButton{
        background-color: WHITE;}
        QPushButton:hover {
        border-color: #bbb}
        QPushButton:checked {
        border-color: red;}''')

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, value: str) -> None:
        self._text_color = value

    @property
    def player_color(self) -> str:
        return self._player_color

    @player_color.setter
    def player_color(self, value: str) -> None:
        self._player_color = value

    @property
    def symbol(self) -> 'SymbolType':
        return self._symbol

    def paintEvent(self, event: 'QPaintEvent') -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setBrush(Qt.white)
        if self._symbol is SymbolType.LETTER:
            if self._text == '' or self._text == ' ':
                painter.setPen(QPen(QColor(self._player_color), 2, s=Qt.DashDotLine, c=Qt.RoundCap, j=Qt.RoundJoin))
                painter.drawEllipse(QRectF(self._rec.x() + 6, self._rec.y() + 6, self._rec.width() - 12, self._rec.height() - 12))
            else:
                painter.setPen(QPen(QColor(self._text_color)))
                painter.setFont(self._font_letter)
                painter.drawText(self._rec, Qt.AlignCenter, self._text)
        elif self._symbol is SymbolType.CROSS:
            painter.setPen(QPen(QColor(self._player_color), 2, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin))
            painter.drawLines([self._line1, self._line2])
        elif self._symbol is SymbolType.TRIANGLE_BOT:
            painter.setPen(QPen(QColor(self._player_color), 2, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin))
            painter.drawPolygon(QPolygonF(self._polygon_bot))
            painter.setPen(QPen(QColor(self._text_color)))
            painter.setFont(self._font_triangle)
            painter.drawText(QRectF(0, -12, self.width(), self.height() + 12), Qt.AlignCenter, self._text)
        elif self._symbol is SymbolType.TRIANGLE_TOP:
            painter.setPen(QPen(QColor(self._player_color), 2, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin))
            painter.drawPolygon(QPolygonF(self._polygon_top))
            painter.setPen(QPen(QColor(self._text_color)))
            painter.setFont(self._font_triangle)
            painter.drawText(QRectF(0, 10, self.width(), self.height() - 10), Qt.AlignCenter, self._text)
        self.update()