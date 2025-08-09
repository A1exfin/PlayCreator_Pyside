from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QFont
from PySide6.QtCore import Qt

from Config import FieldData


class FieldTriangle(QGraphicsPolygonItem):
    def __init__(self, polygon, x: float, y: float):
        super().__init__(polygon)
        self.setPos(x, y)
        self.setPen(QPen(FieldData.light_gray_color, 1, s=Qt.SolidLine, c=Qt.RoundCap, j=Qt.RoundJoin))
        self.setBrush(QBrush(FieldData.light_gray_color))
        self.setOpacity(0.6)
        self.setEnabled(False)


class FieldNumber(QGraphicsTextItem):
    def __init__(self, text: str, angle: float, x: float, y: float):
        super().__init__(text)
        font = QFont('Times New Roman', 40)
        font.setBold(True)
        self.setFont(font)
        self.setDefaultTextColor(FieldData.light_gray_color)
        self.setRotation(angle)
        self.setPos(x, y)
        self.setOpacity(0.6)
        self.setEnabled(False)
