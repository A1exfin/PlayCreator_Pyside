from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from PySide6.QtCore import QObject, Signal, QPointF

if TYPE_CHECKING:
    pass


class LabelModel(QObject):
    coordsChanged = Signal(object)  # QPointF
    sizeChanged = Signal(float, float, float, float)  # x, y, width, height
    textAttributesChanged = Signal(str, str, int, bool, bool, bool, str, float, float)  # text, font_type, font_size, bold, italic, underline, color, y, height

    def __init__(self, x: float, y: float, width: float, height: float, text: str, font_type: str, font_size: int,
                 font_bold: bool, font_italic: bool, font_underline: bool, font_color: str,
                 uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__()
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._font_type = font_type
        self._font_size = font_size
        self._font_bold = font_bold
        self._font_italic = font_italic
        self._font_underline = font_underline
        self._font_color = font_color
        self._text = text
        self._uuid = uuid if uuid else uuid4()
        self._id_local_db = id_local_db
        self._id_api = id_api

    @property
    def id_local_db(self) -> int:
        return self._id_local_db

    @id_local_db.setter
    def id_local_db(self, value: int) -> None:
        self._id_local_db = value

    @property
    def id_api(self) -> int:
        return self._id_api

    @id_api.setter
    def id_api(self, value: int) -> None:
        self._id_api = value

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def font_type(self) -> str:
        return self._font_type

    @property
    def font_size(self) -> int:
        return self._font_size

    @property
    def font_bold(self) -> bool:
        return self._font_bold

    @property
    def font_italic(self) -> bool:
        return self._font_italic

    @property
    def font_underline(self) -> bool:
        return self._font_underline

    @property
    def font_color(self) -> str:
        return self._font_color

    @property
    def text(self) -> str:
        return self._text

    def set_pos(self, x: float, y: float) -> None:
        self._x, self._y = x, y
        self.coordsChanged.emit(QPointF(self._x, self._y))

    def set_size(self, x: float, y: float, width: float, height: float) -> None:
        self._x, self._y, self._width, self._height = x, y, width, height
        self.sizeChanged.emit(self._x, self._y, self._width, self._height)

    def set_text_attributes(self, text: str, font_type: str, font_size: int,
                            font_bold: bool, font_italic: bool, font_underline: bool, font_color: str,
                            y: float, height: float) -> None:
        self._y, self._height = y, height
        self._text, self._font_color = text, font_color
        self._font_type, self._font_size = font_type, font_size
        self._font_bold, self._font_italic, self._font_underline = font_bold, font_italic, font_underline
        self.textAttributesChanged.emit(self._text, self._font_type, self._font_size, self._font_bold,
                                        self._font_italic, self._font_underline, self._font_color, self._y, self._height)

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid, 'x': self._x, 'y': self._y, 'width': self._width, 'height': self._height,
                'text': self._text, 'font_type': self._font_type, 'font_size': self._font_size,
                'font_bold': self._font_bold, 'font_italic': self._font_italic, 'font_underline': self._font_underline,
                'font_color': self._font_color}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'x': self._x, 'y': self._y, 'width': self._width, 'height': self._height,
                'text': self._text, 'font_type': self._font_type, 'font_size': self._font_size,
                'font_bold': self._font_bold, 'font_italic': self._font_italic, 'font_underline': self._font_underline,
                'font_color': self._font_color}