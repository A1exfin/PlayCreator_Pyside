import re
from pydantic import ValidationError

from Config.Enums import PlaybookType
from Config import football_field_data as football_field, flag_field_data as flag_field


def get_field_width(playbook_type: 'PlaybookType') -> float:
    if playbook_type is PlaybookType.FOOTBALL:
        field_width = football_field.width
    elif playbook_type is PlaybookType.FLAG:
        field_width = flag_field.width
    return field_width


def get_field_length(playbook_type: 'PlaybookType') -> float:
    if playbook_type is PlaybookType.FOOTBALL:
        field_length = football_field.length
    elif playbook_type is PlaybookType.FLAG:
        field_length = flag_field.length
    return field_length


def validate_playbook_type(value):
    if value not in PlaybookType:
        raise ValueError('Неверный тип плейбука - "{value}".'.format(value=value))
    return value


def validate_x(x: float, playbook_type: 'PlaybookType') -> float:
    field_width = get_field_width(playbook_type)
    if not 0 <= x <= field_width:
        raise ValueError('Координата по оси X должна быть в диапазоне от 0 до {field_width}. Сейчас "{x}".'.format(field_width=field_width, x=x))
    return x


def validate_y(y: float, playbook_type: 'PlaybookType') -> float:
    field_length = get_field_length(playbook_type)
    if not 0 <= y <= field_length:
        raise ValueError('Координата по оси Y должна быть в диапазоне от 0 до {field_length}. Сейчас "{y}".'.format(field_length=field_length, y=y))
    return y


def validate_right_border(x: float, width: float, playbook_type: 'PlaybookType') -> float:
    field_width = get_field_width(playbook_type)
    if not 0 <= x + width <= field_width:
        raise ValueError('Координата по оси X + ширина, не должна превышать {field_width}. Сейчас "{value}".'.format(field_width=field_width, value=x+width))
    return width


def validate_bot_border(y: float, height: float, playbook_type: 'PlaybookType') -> float:
    field_length = get_field_length(playbook_type)
    if not 0 <= y + height <= field_length:
        raise ValueError('Координата по оси Y + высота, не должна превышать {field_length}. Сейчас "{value}".'.format(field_length=field_length, value=y+height))
    return height


def validate_first_team_position(value: int, playbook_type: 'PlaybookType') -> int:
    if playbook_type is PlaybookType.FOOTBALL:
        max_value = 100
    elif playbook_type is PlaybookType.FLAG:
        max_value = 50
    if not 0 <= value <= max_value:
        raise ValueError('Позиция первой команды на поле должна быть в диапазоне от 0 до {max_value}. Сейчас "{value}".'.format(max_value=max_value, value=value))
    return value


def validate_hex_color(color):
    if not re.fullmatch(r'^#[A-F\d]{6}$', color):
        raise ValueError('Некорректный формат HEX-цвета. Пример "#FF00FF".')
    return color


def validate_opacity_hex_value(opacity: str) -> str:
    if not re.fullmatch(r'^#[A-F\d]{2}$', opacity):
        raise ValueError('Некорректный формат HEX-прозрачности. Пример "#5A".')
    return opacity