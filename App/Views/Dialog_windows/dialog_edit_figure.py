from typing import TYPE_CHECKING
from collections import namedtuple

from PySide6.QtWidgets import QDialog, QColorDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,\
    QGroupBox, QSlider, QLabel, QComboBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from Config import DEFAULT_COLORS
from .widgets.widget_for_figure_edit_dialog import FigurePix
from .widgets.button_box import ButtonBox

if TYPE_CHECKING:
    from Core.Enums import FigureType

__all__ = ('DialogEditFigure',)

figure_data = namedtuple('FigureData', 'border border_thickness border_color fill fill_opacity fill_color')


class DialogEditFigure(QDialog):
    def __init__(self, figure_type: 'FigureType', border: bool, border_color: str, border_thickness: int,
                 fill: bool, fill_opacity: str, fill_color: str,
                 parent, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self._border = border
        self._border_color = border_color
        self._border_thickness = border_thickness
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(572, 322)
        self.setWindowTitle('Настройки фигуры')

        groupbox_stylesheet = '''
        QGroupBox {border: 2px solid gray; border-radius: 5px; padding-top: 3px; margin-top: 8px;}
        QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top LEFT; LEFT: 15px}
        QGroupBox::indicator {}'''
        # QGroupBox {border: 2px solid gray; border-radius: 5px; padding-top: 3px; margin-top: 8px;}
        # QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top LEFT; LEFT: 15px;}''' % window_text_color)
        font = QFont()
        font.setPointSize(10)
        self.group_box_border = QGroupBox('Граница')  # , parent=self
        self.group_box_border.setFont(font)
        self.group_box_border.setFixedSize(244, 73)
        self.group_box_border.setStyleSheet(groupbox_stylesheet)
        self.group_box_border.setCheckable(True)
        self.group_box_border.setChecked(border)
        self.group_box_border.toggled.connect(self._set_border)

        self.group_box_fill = QGroupBox('Заливка')  # parent=self
        self.group_box_fill.setFont(font)
        self.group_box_fill.setFixedSize(244, 111)
        self.group_box_fill.setStyleSheet(groupbox_stylesheet)
        self.group_box_fill.setCheckable(True)
        self.group_box_fill.setChecked(fill)
        self.group_box_fill.toggled.connect(self._set_fill)

        self.combo_box_border_width = QComboBox(parent=self.group_box_border)
        self.combo_box_border_width.addItems(['2', '3', '4', '5', '6'])
        self.combo_box_border_width.setCurrentText(str(self._border_thickness))
        self.combo_box_border_width.setFixedSize(40, 25)
        self.combo_box_border_width.currentTextChanged.connect(self._set_border_thickness)

        self.label_opacity = QLabel()
        self.label_opacity.setFont(font)
        self.label_opacity.setFixedSize(40, 40)
        self.label_opacity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_fill_opacity = QSlider(Qt.Orientation.Horizontal, parent=self.group_box_fill)
        self.slider_fill_opacity.setMinimum(0)
        self.slider_fill_opacity.setMaximum(255)
        self.slider_fill_opacity.setValue(int(fill_opacity[1:], 16))
        self.slider_fill_opacity.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.slider_fill_opacity.setTickInterval(10)
        self.slider_fill_opacity.valueChanged.connect(self._set_opacity)

        confirmation_button_box = ButtonBox(self, True, Qt.AlignCenter)

        self.push_button_current_border_color = QPushButton(parent=self.group_box_border)
        self.push_button_current_border_color.setFixedSize(40, 40)
        self.push_button_current_border_color.setStyleSheet(f'background-color: {border_color}')
        self.push_button_current_border_color.clicked.connect(self._set_user_border_color)

        self.push_button_current_fill_color = QPushButton(parent=self.group_box_fill)
        self.push_button_current_fill_color.setFixedSize(40, 40)
        self.push_button_current_fill_color.setStyleSheet(f'background-color: {fill_color}')
        self.push_button_current_fill_color.clicked.connect(self._set_user_fill_color)

        grid_layout_border_colors = QGridLayout()
        grid_layout_border_colors.setVerticalSpacing(4)
        grid_layout_border_colors.setHorizontalSpacing(2)
        for i, color in enumerate(DEFAULT_COLORS):
            setattr(self, f'button_border_color_{i}', QPushButton(parent=self.group_box_border))
            getattr(self, f'button_border_color_{i}').setFixedSize(18, 18)
            getattr(self, f'button_border_color_{i}').setStyleSheet(f'background-color: {color}')
            getattr(self, f'button_border_color_{i}').pressed.connect(lambda color=color: self._set_border_color(color))
            row, column = (0, i + 1) if i < len(DEFAULT_COLORS) / 2 else (1, i + 1 - len(DEFAULT_COLORS) / 2)
            grid_layout_border_colors.addWidget(getattr(self, f'button_border_color_{i}'), row, column, 1, 1)

        grid_layout_fill_colors = QGridLayout()
        grid_layout_fill_colors.setVerticalSpacing(4)
        grid_layout_fill_colors.setHorizontalSpacing(2)
        for i, color in enumerate(DEFAULT_COLORS):
            setattr(self, f'button_fill_color_{i}', QPushButton(parent=self.group_box_fill))
            getattr(self, f'button_fill_color_{i}').setFixedSize(18, 18)
            getattr(self, f'button_fill_color_{i}').setStyleSheet(f'background-color: {color}')
            getattr(self, f'button_fill_color_{i}').pressed.connect(lambda color=color: self._set_fill_color(color))
            row, column = (0, i + 1) if i < len(DEFAULT_COLORS) / 2 else (1, i + 1 - len(DEFAULT_COLORS) / 2)
            grid_layout_fill_colors.addWidget(getattr(self, f'button_fill_color_{i}'), row, column, 1, 1)

        self._pix = FigurePix(figure_type, border, border_color, border_thickness, fill, fill_color, fill_opacity, self)

        horizontal_layout_border = QHBoxLayout(self.group_box_border)
        horizontal_layout_border.setAlignment(Qt.AlignCenter)
        horizontal_layout_border.addWidget(self.combo_box_border_width)
        horizontal_layout_border.addWidget(self.push_button_current_border_color)
        horizontal_layout_border.addLayout(grid_layout_border_colors)

        horizontal_layout_fill_colors = QHBoxLayout()
        horizontal_layout_fill_colors.addWidget(self.label_opacity)
        horizontal_layout_fill_colors.addWidget(self.push_button_current_fill_color)
        horizontal_layout_fill_colors.addLayout(grid_layout_fill_colors)

        vertical_layout_fill = QVBoxLayout(self.group_box_fill)
        vertical_layout_fill.setAlignment(Qt.AlignCenter)
        vertical_layout_fill.addLayout(horizontal_layout_fill_colors)
        vertical_layout_fill.addWidget(self.slider_fill_opacity)

        vertical_layout_main = QVBoxLayout()
        vertical_layout_main.setAlignment(Qt.AlignCenter)
        vertical_layout_main.addWidget(self.group_box_border)
        vertical_layout_main.addWidget(self.group_box_fill)
        vertical_layout_main.addWidget(confirmation_button_box)

        horizontal_layout_main = QHBoxLayout(self)
        horizontal_layout_main.addLayout(vertical_layout_main)
        horizontal_layout_main.addWidget(self._pix)

        self._set_opacity(int(fill_opacity[1:], 16))

        confirmation_button_box.accepted.connect(self.accept)
        confirmation_button_box.declined.connect(self.reject)

    def _set_border(self, value: bool) -> None:
        if not value:
            self._border = False
            self._pix.border = False
            self.group_box_fill.setChecked(True)
        else:
            self._border = True
            self._pix.border = True
        self._pix.update()

    def _set_border_thickness(self, value: str) -> None:
        self._border_thickness = int(value)
        self._pix.border_thickness = int(value)
        self._pix.update()

    def _set_border_color(self, color: str) -> None:
        self._border_color = color
        self._pix.border_color = color
        self.push_button_current_border_color.setStyleSheet(f'background-color: {color};')
        self._pix.update()

    def _set_user_border_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self._set_border_color(user_color_dialog.selectedColor().name())

    def _set_fill(self, value: bool) -> None:
        if not value:
            self._fill = False
            self._pix.fill = False
            self.group_box_border.setChecked(True)
        else:
            self._fill = True
            self._pix.fill = True
        self._pix.update()

    def _set_fill_color(self, color: str) -> None:
        self._fill_color = color
        self._pix.fill_color = color
        self.push_button_current_fill_color.setStyleSheet(f'background-color: {color};')
        self._pix.update()

    def _set_user_fill_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self._set_fill_color(user_color_dialog.selectedColor().name())

    def _set_opacity(self, opacity: int) -> None:
        opacity_str = f'#{str(hex(opacity))[2:].zfill(2)}'
        opacity_percent = opacity / 255 * 100
        self.label_opacity.setText(f'{int(opacity_percent)} %')
        self._fill_opacity = opacity_str
        self._pix.fill_opacity = opacity_str
        self._pix.update()

    def get_data(self) -> 'figure_data':
        return figure_data(
            self._border, self._border_thickness, self._border_color,
            self._fill, self._fill_opacity, self._fill_color
        )

