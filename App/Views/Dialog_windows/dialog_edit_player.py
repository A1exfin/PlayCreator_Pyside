from typing import TYPE_CHECKING
from collections import namedtuple

from PySide6.QtWidgets import QDialog, QColorDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,\
    QButtonGroup, QGroupBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from Config import DEFAULT_COLORS
from .widgets.buttons_for_player_edit_dialog import CustomPushButtonFillType, CustomPushButtonSymbolType
from .widgets.button_box import ButtonBox
from Config.Enums import FillType, SymbolType

if TYPE_CHECKING:
    from Config.Enums import PlayerPositionType

__all__ = ('DialogEditFirstTeamPlayer', 'DialogEditSecondTeamPlayer')

first_team_player_data = namedtuple('FirstTeamPlayerData', 'text text_color player_color fill_type')
second_team_player_data = namedtuple('SecondTeamPlayerData', 'text text_color player_color symbol_type')


class DialogEditPlayer(QDialog):
    def __init__(self, text: str, text_color: str, player_color: str, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(390, 400)
        self.setWindowTitle('Настройки игрока')

        groupbox_stylesheet = '''
        QGroupBox {border: 2px solid gray; border-radius: 5px; padding-top: 3px; margin-top: 8px;}
        QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top LEFT; LEFT: 15px;}'''
        # self.setStyleSheet('''QDialog {color: %s;}
        # QGroupBox {border: 2px solid gray; border-radius: 5px; padding-top: 3px; margin-top: 8px;}
        # QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top LEFT; LEFT: 15px;}''' % window_text_color)

        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        self.group_box_position = QGroupBox('Позиция игрока')
        self.group_box_position.setFont(font)
        self.group_box_position.setFixedSize(244, 73)
        self.group_box_position.setStyleSheet(groupbox_stylesheet)

        self.group_box_text_color = QGroupBox('Цвет текста')
        self.group_box_text_color.setFont(font)
        self.group_box_text_color.setFixedSize(244, 73)
        self.group_box_text_color.setStyleSheet(groupbox_stylesheet)

        self.group_box_player_color = QGroupBox()
        self.group_box_player_color.setFont(font)
        self.group_box_player_color.setFixedSize(244, 73)
        self.group_box_player_color.setStyleSheet(groupbox_stylesheet)

        self.group_box_fill_symbol_type = QGroupBox()
        self.group_box_fill_symbol_type.setFont(font)
        self.group_box_fill_symbol_type.setFixedSize(244, 73)
        self.group_box_fill_symbol_type.setStyleSheet(groupbox_stylesheet)

        self.button_group_fill_symbol_type = QButtonGroup(parent=self)
        self.button_group_fill_symbol_type.setExclusive(True)

        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.line_edit_player_position = QLineEdit(parent=self.group_box_position)
        self.line_edit_player_position.setFont(font)
        self.line_edit_player_position.setMaxLength(2)
        self.line_edit_player_position.setText(text)
        self.line_edit_player_position.setContentsMargins(5, 5, 5, 0)
        self.line_edit_player_position.setStyleSheet('QLineEdit:disabled{color: #334e3a;}')

        confirmation_button_box = ButtonBox(self, True, Qt.AlignCenter)

        self.push_button_current_text_color = QPushButton(parent=self.group_box_text_color)
        self.push_button_current_text_color.setFixedSize(40, 40)
        self.push_button_current_text_color.setStyleSheet(f'background-color: {text_color}')

        self.push_button_current_player_color = QPushButton(parent=self.group_box_player_color)
        self.push_button_current_player_color.setFixedSize(40, 40)
        self.push_button_current_player_color.setStyleSheet(f'background-color: {player_color}')

        vertical_layout_position = QVBoxLayout(self.group_box_position)
        vertical_layout_position.addWidget(self.line_edit_player_position)

        grid_layout_text_colors = QGridLayout()
        grid_layout_text_colors.setVerticalSpacing(4)
        grid_layout_text_colors.setHorizontalSpacing(2)
        for i, color in enumerate(DEFAULT_COLORS):
            setattr(self, f'button_text_color_{i}', QPushButton(parent=self.group_box_text_color))
            getattr(self, f'button_text_color_{i}').setFixedSize(18, 18)
            getattr(self, f'button_text_color_{i}').setStyleSheet(f'background-color: {color}')
            row, column = (0, i + 1) if i < len(DEFAULT_COLORS) / 2 else (1, i + 1 - len(DEFAULT_COLORS) / 2)
            grid_layout_text_colors.addWidget(getattr(self, f'button_text_color_{i}'), row, column, 1, 1)

        grid_layout_player_colors = QGridLayout()
        grid_layout_player_colors.setVerticalSpacing(4)
        grid_layout_player_colors.setHorizontalSpacing(2)
        for i, color in enumerate(DEFAULT_COLORS):
            setattr(self, f'button_player_color_{i}', QPushButton(parent=self.group_box_player_color))
            getattr(self, f'button_player_color_{i}').setFixedSize(18, 18)
            getattr(self, f'button_player_color_{i}').setStyleSheet(f'background-color: {color}')
            row, column = (0, i + 1) if i < len(DEFAULT_COLORS) / 2 else (1, i + 1 - len(DEFAULT_COLORS) / 2)
            grid_layout_player_colors.addWidget(getattr(self, f'button_player_color_{i}'), row, column, 1, 1)

        horizontal_layout_text_color = QHBoxLayout(self.group_box_text_color)
        horizontal_layout_text_color.setAlignment(Qt.AlignCenter)
        horizontal_layout_text_color.addWidget(self.push_button_current_text_color)
        horizontal_layout_text_color.addLayout(grid_layout_text_colors)

        horizontal_layout_player_colors = QHBoxLayout(self.group_box_player_color)
        horizontal_layout_player_colors.setAlignment(Qt.AlignCenter)
        horizontal_layout_player_colors.addWidget(self.push_button_current_player_color)
        horizontal_layout_player_colors.addLayout(grid_layout_player_colors)

        self.horizontal_layout_fill_symbol_type = QHBoxLayout(self.group_box_fill_symbol_type)
        self.horizontal_layout_fill_symbol_type.setAlignment(Qt.AlignCenter)

        vertical_layout_main = QVBoxLayout(self)
        vertical_layout_main.setAlignment(Qt.AlignCenter)
        vertical_layout_main.addWidget(self.group_box_position)
        vertical_layout_main.addWidget(self.group_box_text_color)
        vertical_layout_main.addWidget(self.group_box_player_color)
        vertical_layout_main.addWidget(self.group_box_fill_symbol_type)
        vertical_layout_main.addWidget(confirmation_button_box)

        confirmation_button_box.accepted.connect(self.accept)
        confirmation_button_box.declined.connect(self.reject)


class DialogEditFirstTeamPlayer(DialogEditPlayer):
    def __init__(self, position: 'PlayerPositionType', text: str, player_color: str, text_color: str,
                 fill_type: 'FillType', parent=None, flags=Qt.WindowFlags()):
        super().__init__(text, text_color, player_color, parent, flags)
        self._text = text
        self._text_color = text_color
        self._player_color = player_color

        self.group_box_player_color.setTitle('Цвет контура и заливки')
        self.group_box_fill_symbol_type.setTitle('Тип заливки')
        self.push_button_white_fill = CustomPushButtonFillType(position, self._text, self._text_color, self._player_color, FillType.WHITE, parent=self.group_box_fill_symbol_type)
        self.push_button_full_fill = CustomPushButtonFillType(position, self._text, self._text_color, self._player_color, FillType.FULL, parent=self.group_box_fill_symbol_type)
        self.push_button_left_fill = CustomPushButtonFillType(position, self._text, self._text_color, self._player_color, FillType.LEFT, parent=self.group_box_fill_symbol_type)
        self.push_button_right_fill = CustomPushButtonFillType(position, self._text, self._text_color, self._player_color, FillType.RIGHT, parent=self.group_box_fill_symbol_type)
        self.push_button_mid_fill = CustomPushButtonFillType(position, self._text, self._text_color, self._player_color, FillType.MID, parent=self.group_box_fill_symbol_type)

        self.button_group_fill_symbol_type.addButton(self.push_button_white_fill)
        self.button_group_fill_symbol_type.addButton(self.push_button_full_fill)
        self.button_group_fill_symbol_type.addButton(self.push_button_left_fill)
        self.button_group_fill_symbol_type.addButton(self.push_button_right_fill)
        self.button_group_fill_symbol_type.addButton(self.push_button_mid_fill)

        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_white_fill)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_full_fill)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_left_fill)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_right_fill)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_mid_fill)

        getattr(self, f'push_button_{fill_type.name}_fill'.lower()).setChecked(True)

        self.line_edit_player_position.textChanged.connect(lambda text: self.set_text(text))

        for i, color in enumerate(DEFAULT_COLORS):
            getattr(self, f'button_text_color_{i}').pressed.connect(lambda color=color: self.set_text_color(color))

        for i, color in enumerate(DEFAULT_COLORS):
            getattr(self, f'button_player_color_{i}').pressed.connect(lambda color=color: self.set_player_color(color))

        self.push_button_current_text_color.clicked.connect(self.set_user_text_color)
        self.push_button_current_player_color.clicked.connect(self.set_user_player_color)

        self.set_text(text)
        self.set_text_color(text_color)
        self.set_player_color(player_color)

    def set_text(self, text: str) -> None:
        self._text = text
        self.push_button_white_fill.text = text
        self.push_button_full_fill.text = text
        self.push_button_left_fill.text = text
        self.push_button_right_fill.text = text
        self.push_button_mid_fill.text = text

    def set_user_text_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self.set_text_color(user_color_dialog.selectedColor().name())

    def set_text_color(self, color: str) -> None:
        self._text_color = color
        self.push_button_current_text_color.setStyleSheet(f'background-color: {color};')
        self.push_button_white_fill.text_color = color
        self.push_button_full_fill.text_color = color
        self.push_button_left_fill.text_color = color
        self.push_button_right_fill.text_color = color
        self.push_button_mid_fill.text_color = color

    def set_user_player_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self.set_player_color(user_color_dialog.selectedColor().name())

    def set_player_color(self, color: str) -> None:
        self._player_color = color
        self.push_button_current_player_color.setStyleSheet(f'background-color: {color};')
        self.push_button_white_fill.set_gradient(color)
        self.push_button_full_fill.set_gradient(color)
        self.push_button_left_fill.set_gradient(color)
        self.push_button_right_fill.set_gradient(color)
        self.push_button_mid_fill.set_gradient(color)

    def get_data(self) -> 'first_team_player_data':
        return first_team_player_data(
            self._text, self._text_color, self._player_color,
            self.button_group_fill_symbol_type.checkedButton().fill_type
        )


class DialogEditSecondTeamPlayer(DialogEditPlayer):
    def __init__(self, text: str, text_color: str, player_color: str, symbol: 'SymbolType', parent=None, flags=Qt.WindowFlags()):
        super().__init__(text, text_color, player_color, parent=parent)
        self._text = text
        self._player_color = player_color
        self._text_color = text_color
        self._symbol = symbol

        self.group_box_player_color.setTitle('Цвет контура')
        self.group_box_fill_symbol_type.setTitle('Символ')
        self.line_edit_player_position.setMaxLength(1)

        self.push_button_letter_symbol = CustomPushButtonSymbolType(self._text, self._text_color, self._player_color,
                                                                    SymbolType.LETTER,
                                                                    parent=self.group_box_fill_symbol_type)
        self.push_button_letter_symbol.pressed.connect(lambda symbol=SymbolType.LETTER: self.set_symbol(symbol))

        self.push_button_cross_symbol = CustomPushButtonSymbolType(self._text, self._text_color, self._player_color,
                                                                   SymbolType.CROSS,
                                                                   parent=self.group_box_fill_symbol_type)
        self.push_button_cross_symbol.pressed.connect(lambda symbol=SymbolType.CROSS: self.set_symbol(symbol))

        self.push_button_triangle_bot_symbol = CustomPushButtonSymbolType(self._text, self._text_color,
                                                                          self._player_color, SymbolType.TRIANGLE_BOT,
                                                                          parent=self.group_box_fill_symbol_type)
        self.push_button_triangle_bot_symbol.pressed.connect(lambda symbol=SymbolType.TRIANGLE_BOT: self.set_symbol(symbol))

        self.push_button_triangle_top_symbol = CustomPushButtonSymbolType(self._text, self._text_color,
                                                                          self._player_color, SymbolType.TRIANGLE_TOP,
                                                                          parent=self.group_box_fill_symbol_type)
        self.push_button_triangle_top_symbol.pressed.connect(lambda symbol=SymbolType.TRIANGLE_TOP: self.set_symbol(symbol))

        self.button_group_fill_symbol_type.addButton(self.push_button_letter_symbol)
        self.button_group_fill_symbol_type.addButton(self.push_button_cross_symbol)
        self.button_group_fill_symbol_type.addButton(self.push_button_triangle_bot_symbol)
        self.button_group_fill_symbol_type.addButton(self.push_button_triangle_top_symbol)

        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_letter_symbol)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_cross_symbol)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_triangle_bot_symbol)
        self.horizontal_layout_fill_symbol_type.addWidget(self.push_button_triangle_top_symbol)

        getattr(self, f'push_button_{symbol.name}_symbol'.lower()).setChecked(True)

        self.line_edit_player_position.textChanged.connect(lambda text: self.set_text(text))

        for i, color in enumerate(DEFAULT_COLORS):
            getattr(self, f'button_text_color_{i}').pressed.connect(lambda color=color: self.set_text_color(color))

        for i, color in enumerate(DEFAULT_COLORS):
            getattr(self, f'button_player_color_{i}').pressed.connect(lambda color=color: self.set_player_color(color))

        self.push_button_current_text_color.clicked.connect(self.set_user_text_color)
        self.push_button_current_player_color.clicked.connect(self.set_user_player_color)

        self.set_symbol(self._symbol)

    def set_text(self, text: str) -> None:
        self._text = text
        self.push_button_letter_symbol.text = self.line_edit_player_position.text()
        self.push_button_triangle_bot_symbol.text = self.line_edit_player_position.text()
        self.push_button_triangle_top_symbol.text = self.line_edit_player_position.text()

    def set_user_text_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self.set_text_color(user_color_dialog.selectedColor().name())

    def set_text_color(self, color: str) -> None:
        self._text_color = color
        self.push_button_current_text_color.setStyleSheet(f'background-color: {self._text_color};')
        self.push_button_letter_symbol.text_color = color
        self.push_button_triangle_bot_symbol.text_color = color
        self.push_button_triangle_top_symbol.text_color = color

    def set_user_player_color(self) -> None:
        user_color_dialog = QColorDialog(parent=self)
        if user_color_dialog.exec():
            self.set_player_color(user_color_dialog.selectedColor().name())

    def set_player_color(self, color: str) -> None:
        self._player_color = color
        self.push_button_current_player_color.setStyleSheet(f'background-color: {self._player_color};')
        self.push_button_letter_symbol.player_color = color
        self.push_button_triangle_bot_symbol.player_color = color
        self.push_button_triangle_top_symbol.player_color = color
        self.push_button_cross_symbol.player_color = color

    def set_symbol(self, symbol: 'SymbolType') -> None:
        self._symbol = symbol
        if symbol is SymbolType.LETTER:
            self.group_box_position.setEnabled(True)
            self.group_box_text_color.setEnabled(True)
            self.group_box_player_color.setEnabled(False)
        elif symbol is SymbolType.CROSS:
            self.group_box_position.setEnabled(False)
            self.group_box_text_color.setEnabled(False)
            self.group_box_player_color.setEnabled(True)
        elif symbol is SymbolType.TRIANGLE_BOT:
            self.group_box_position.setEnabled(True)
            self.group_box_text_color.setEnabled(True)
            self.group_box_player_color.setEnabled(True)
        elif symbol is SymbolType.TRIANGLE_TOP:
            self.group_box_position.setEnabled(True)
            self.group_box_text_color.setEnabled(True)
            self.group_box_player_color.setEnabled(True)

    def get_data(self) -> 'second_team_player_data':
        return second_team_player_data(self._text, self._text_color, self._player_color, self._symbol)
