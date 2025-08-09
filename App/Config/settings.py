import os
from dataclasses import dataclass

from PySide6.QtCore import QRect, QPointF
from PySide6.QtGui import QPen, QPolygonF, QColor

from Config.Enums import TeamType, FillType, SymbolType, PlayerPositionType


__all__ = ('ORGANIZATION', 'APP_NAME', 'DEBUG', 'VERSION', 'DEFAULT_COLORS', 'HOVER_ITEM_COLOR',
           'DARK_THEME_LIST_WIDGET_ITEM_DEFAULT_COLOR', 'DARK_THEME_LIST_WIDGET_ITEM_SELECTED_COLOR',
           'LIGHT_THEME_LIST_WIDGET_ITEM_DEFAULT_COLOR', 'LIGHT_THEME_LIST_WIDGET_ITEM_SELECTED_COLOR',
           'ERASER_CURSOR_PATH', 'DB_URL',
           'FieldData', 'FootballFieldData', 'FlagFieldData',
           'PlayerData', 'FootballPlayersData', 'FlagPlayersData')

ORGANIZATION = 'alexfin_dev'

APP_NAME = 'PlayCreator'

DEBUG = True

VERSION = '4.0'

DEFAULT_COLORS = ('#000000', '#800000', '#400080', '#0004ff', '#8d8b9a', '#22b14c',
                  '#ff0000', '#ff00ea', '#ff80ff', '#ff8000', '#dcdc00', '#00ff00')

HOVER_ITEM_COLOR = QColor('#ffcb30')

DARK_THEME_LIST_WIDGET_ITEM_DEFAULT_COLOR = QColor('#b1b1b1')
DARK_THEME_LIST_WIDGET_ITEM_SELECTED_COLOR = QColor('#27c727')
LIGHT_THEME_LIST_WIDGET_ITEM_DEFAULT_COLOR = QColor('#000000')
LIGHT_THEME_LIST_WIDGET_ITEM_SELECTED_COLOR = QColor('#1a6aa7')

ERASER_CURSOR_PATH = '://cursors/cursors/eraser.cur'

DB_NAME = 'PlayCreator.db'
DB_URL = f'sqlite:///{os.getcwd()}/{DB_NAME}'

# Field settings
@dataclass(frozen=True)
class FieldData:
    number_arrow_polygon_top: QPolygonF = QPolygonF([QPointF(5, 0), QPointF(0, 10), QPointF(10, 10)])
    number_arrow_polygon_bot: QPolygonF = QPolygonF([QPointF(5, 10), QPointF(0, 0), QPointF(10, 0)])
    side_one_yard_line_length: int = 14
    hash_one_yard_line_length: int = 10
    black_color: QColor = QColor(0, 0, 0, 255)
    dark_gray_color: QColor = QColor(140, 140, 140, 255)
    light_gray_color: QColor = QColor(228, 228, 228, 255)
    border_style: QPen = QPen(black_color, 4)  # Цвет, толщина линии
    ten_yards_line_style: QPen = QPen(dark_gray_color, 2)  # Цвет, толщина линии
    end_zone_and_center_line_style: QPen = QPen(black_color, 3)  # Цвет, толщина линии
    other_lines_style: QPen = QPen(light_gray_color, 2)  # Цвет, толщина линии


@dataclass(frozen=True)
class FootballFieldData(FieldData):
    rect: QRect = QRect(0, 0, 534, 1200)  # x, y, w, l
    length: int = rect.height()
    width: int = rect.width()
    vertical_one_yard: int = int(length / 120)
    vertical_five_yards: int = int(length / 24)
    vertical_ten_yards: int = int(length / 12)
    vertical_field_center: int = int(length / 2)
    horizontal_one_yard: float = width / 53
    horizontal_field_center: float = width / 2
    hash_line_center: float = width / 2.65

    def __repr__(self):
        return f'<{self.__class__.__name__} (length: {self.length}, width: {self.width}) at {hex(id(self))}>'


@dataclass(frozen=True)
class FlagFieldData(FieldData):
    rect: QRect = QRect(0, 0, 508, 1400)  # x, y, w, l
    length: int = rect.height()
    width: int = rect.width()
    vertical_one_yard: int = int(length / 70)
    vertical_five_yards: int = int(length / 14)
    vertical_ten_yards: int = int(length / 7)
    vertical_field_center: int = int(length / 2)
    horizontal_one_yard: float = width / 25
    horizontal_field_center: float = width / 2
    hash_line_center: float = width / 2

    def __repr__(self):
        return f'<{self.__class__.__name__} (length: {self.length}, width: {self.width}) at {hex(id(self))}>'


#Players settings
@dataclass(frozen=True)
class PlayerData:
    size: int = 20
    border_width = 2


@dataclass(frozen=True)
class FootballPlayersData:
    size: int = PlayerData.size
    center_x: float = FootballFieldData.horizontal_field_center - size / 2
    # Тип команды, Позиция, Текст, Тип заливки, X, Y
    offence: tuple = (
        (TeamType.OFFENCE, PlayerPositionType.CENTER, 'C', FillType.WHITE, center_x, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'RG', FillType.WHITE, center_x + 23, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'RT', FillType.WHITE, center_x + 46, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'LG', FillType.WHITE, center_x - 23, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'LT', FillType.WHITE, center_x - 46, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'X', FillType.WHITE, center_x + 230, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Y', FillType.WHITE, center_x + 130, - size / 2 + 13),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Z', FillType.WHITE, center_x - 230, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'H', FillType.WHITE, center_x - 130, - size / 2 + 13),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Q', FillType.WHITE, center_x, - size / 2 + 50),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'F', FillType.WHITE, center_x, - size / 2 + 75), )
    additional_player: tuple = (TeamType.OFFENCE_ADD, PlayerPositionType.OTHER, 'V', FillType.WHITE, center_x + 90, - size / 2 + 13)
    # Тип команды, Позиция, Текст, Тип символа, X, Y
    defence: tuple = (
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'Т', SymbolType.LETTER, center_x - 10, - size / 2 - 25),  # 1 tech
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'Т', SymbolType.LETTER, center_x + 33, - size / 2 - 25),  # 3 tech
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'E', SymbolType.LETTER, center_x + 56, - size / 2 - 25),  # RT
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'E', SymbolType.LETTER, center_x - 56, - size / 2 - 25),  # LE
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'M', SymbolType.LETTER, center_x + 33, - size / 2 - 50),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'S', SymbolType.LETTER, center_x - 33, - size / 2 - 50),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'W', SymbolType.LETTER, center_x - 130, - size / 2 - 50),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, '$', SymbolType.LETTER, center_x + 130, - size / 2 - 50),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'C', SymbolType.LETTER, center_x + 230, - size / 2 - 65),  # RC
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'C', SymbolType.LETTER, center_x - 230, - size / 2 - 65),  # LC
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'F', SymbolType.LETTER, center_x, - size / 2 - 120),)
    # Тип команды, Позиция, Текст, Тип заливки, X, Y
    kickoff: tuple = (
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 45, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 90, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 135, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 180, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 225, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 45, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 90, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 135, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 180, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 225, - size / 2),
        (TeamType.KICKOFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 25, - size / 2 + 75), )
    # Тип команды, Позиция, Текст, Тип символа, X, Y
    kick_ret: tuple = (
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 180, - size / 2 - 3 * FootballFieldData.vertical_five_yards),  # first line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 90, - size / 2 - 3 * FootballFieldData.vertical_five_yards),  # first line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x, - size / 2 - 3 * FootballFieldData.vertical_five_yards),  # first line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 90, - size / 2 - 3 * FootballFieldData.vertical_five_yards),  # first line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 180, - size / 2 - 3 * FootballFieldData.vertical_five_yards),  # first line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 135, - size / 2 - 3 * FootballFieldData.vertical_ten_yards),  # second line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x, - size / 2 - 3 * FootballFieldData.vertical_ten_yards),  # second line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 135, - size / 2 - 3 * FootballFieldData.vertical_ten_yards),  # second line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 95, - size / 2 - 9 * FootballFieldData.vertical_five_yards),  # third line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 95, - size / 2 - 9 * FootballFieldData.vertical_five_yards),  # third line
        (TeamType.KICK_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x, FootballFieldData.vertical_ten_yards + 2 * FootballFieldData.vertical_one_yard), )
    # Тип команды, Позиция, Текст, Тип заливки, X, Y
    punt: tuple = (
        (TeamType.PUNT, PlayerPositionType.CENTER, '', FillType.WHITE, center_x, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 23, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 46, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 23, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 46, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 230, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 69, - size / 2 + 13),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 230, - size / 2),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 69, - size / 2 + 13),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 25, - size / 2 + 75),
        (TeamType.PUNT, PlayerPositionType.OTHER, '', FillType.WHITE, center_x, - size / 2 + 150), )
    # Тип команды, Позиция, Текст, Тип символа, X, Y
    punt_ret: tuple = (
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 10, - size / 2 - 25),  # 1 tech
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 33, - size / 2 - 25),  # 3 tech
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 56, - size / 2 - 25),  # RT
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 56, - size / 2 - 25),  # LE
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 86, - size / 2 - 25),
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 86, - size / 2 - 25),
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 100, - size / 2 - 115),
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 100, - size / 2 - 115),
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 225, - size / 2 - 25),  # RC
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 225, - size / 2 - 25),  # LC
        (TeamType.PUNT_RET, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x, FootballFieldData.vertical_ten_yards + FootballFieldData.vertical_five_yards - size / 2), )
    # Тип команды, Позиция, Текст, Тип заливки, X, Y
    field_goal_off: tuple = (
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.CENTER, '', FillType.WHITE, center_x, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 23, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 46, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 23, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 46, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 92, - size / 2 + 13),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 69, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 92, - size / 2 + 13),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 69, - size / 2),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x + 12, - size / 2 + 75),
        (TeamType.FIELD_GOAL_OFF, PlayerPositionType.OTHER, '', FillType.WHITE, center_x - 20, - size / 2 + 90), )
    # Тип команды, Позиция, Текст, Тип символа, X, Y
    field_goal_def: tuple = (
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 10, - size / 2 - 25),  # 1 tech
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 33, - size / 2 - 25),  # 3 tech
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 56, - size / 2 - 25),  # RT
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 56, - size / 2 - 25),  # LE
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 86, - size / 2 - 25),
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 86, - size / 2 - 25),
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 75, - size / 2 - 65),
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 75, - size / 2 - 65),
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x + 109, - size / 2 - 25),  # RC
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x - 109, - size / 2 - 25),  # LC
        (TeamType.FIELD_GOAL_DEF, PlayerPositionType.OTHER, '', SymbolType.TRIANGLE_BOT, center_x, - size / 2 - 65), )

    def __repr__(self):
        return f'<{self.__class__.__name__} at {hex(id(self))}>'


@dataclass(frozen=True)
class FlagPlayersData:
    size: int = PlayerData.size
    center_x: float = FlagFieldData.horizontal_field_center - size / 2
    # Тип команды, Позиция, Текст, Тип заливки, X, Y
    offence: tuple = (
        (TeamType.OFFENCE, PlayerPositionType.CENTER, 'C', FillType.WHITE, center_x, - size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'X', FillType.WHITE, center_x + FlagFieldData.horizontal_one_yard * 10, -size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Z', FillType.WHITE, center_x - FlagFieldData.horizontal_one_yard * 10, -size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Y', FillType.WHITE, center_x + FlagFieldData.horizontal_one_yard * 5, -size / 2),
        (TeamType.OFFENCE, PlayerPositionType.OTHER, 'Q', FillType.WHITE, center_x, - size / 2 + FlagFieldData.horizontal_one_yard * 5), )
    additional_player: tuple = (TeamType.OFFENCE_ADD, PlayerPositionType.OTHER, 'H', FillType.WHITE, center_x + FlagFieldData.horizontal_one_yard * 2.5, - size / 2)
    # Тип команды, Позиция, Текст, Тип символа, X, Y
    defence: tuple = (
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'M', SymbolType.LETTER, center_x, -size / 2 - FlagFieldData.horizontal_one_yard * 7),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'C', SymbolType.LETTER, center_x + FlagFieldData.horizontal_one_yard * 10, -size / 2 - FlagFieldData.vertical_one_yard * 5),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'C', SymbolType.LETTER, center_x - FlagFieldData.horizontal_one_yard * 10, -size / 2 - FlagFieldData.vertical_one_yard * 5),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'S', SymbolType.LETTER, center_x + FlagFieldData.horizontal_one_yard * 7, -size / 2 - FlagFieldData.vertical_one_yard * 9),
        (TeamType.DEFENCE, PlayerPositionType.OTHER, 'S', SymbolType.LETTER, center_x - FlagFieldData.horizontal_one_yard * 7, -size / 2 - FlagFieldData.vertical_one_yard * 9), )

    def __repr__(self):
        return f'<{self.__class__.__name__} at {hex(id(self))}>'