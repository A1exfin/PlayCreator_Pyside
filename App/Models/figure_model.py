from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from PySide6.QtCore import Signal, QObject, QPointF


if TYPE_CHECKING:
    from Config.Enums import FigureType


class FigureModel(QObject):
    coordsChanged = Signal(object)  # QPointF
    sizeChanged = Signal(float, float, float, float)
    styleChanged = Signal(bool, int, str, bool, str, str)

    def __init__(self, figure_type: 'FigureType', x: float, y: float, width: float, height: float,
                 border: bool, border_thickness: int, border_color: str,
                 fill: bool, fill_opacity: str, fill_color: str,
                 uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__()
        self._figure_type = figure_type
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._border = border
        self._border_thickness = border_thickness
        self._border_color = border_color
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
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

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()

    @property
    def figure_type(self):
        return self._figure_type

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
    def border(self) -> bool:
        return self._border

    @property
    def border_thickness(self) -> int:
        return self._border_thickness

    @property
    def border_color(self) -> str:
        return self._border_color

    @property
    def fill(self) -> bool:
        return self._fill

    @property
    def fill_color(self) -> str:
        return self._fill_color

    @property
    def fill_opacity(self) -> str:
        return self._fill_opacity

    def set_pos(self, x: float, y: float) -> None:
        self._x, self._y = x, y
        self.coordsChanged.emit(QPointF(self._x, self._y))

    def set_size(self, x: float, y: float, width: float, height: float) -> None:
        self._x, self._y, self._width, self._height = x, y, width, height
        self.sizeChanged.emit(self._x, self._y, self._width, self._height)

    def set_figure_style(self, border: bool, border_thickness: int, border_color: str,
                         fill: bool,  fill_opacity: str, fill_color: str) -> None:
        if not border and not fill:
            raise ValueError('У фигуры одновременно не могут отсутствовать граница и заливка.')
        self._border, self._border_thickness, self._border_color, self._fill, self._fill_opacity, self._fill_color = \
            border, border_thickness, border_color, fill, fill_opacity, fill_color,
        self.styleChanged.emit(self._border, self._border_thickness, self._border_color,
                               self._fill, self._fill_opacity, self._fill_color)

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid, 'figure_type': self._figure_type,
                'x': self._x, 'y': self._y, 'width': self._width, 'height': self._height,
                'border': self._border, 'border_thickness': self._border_thickness, 'border_color': self._border_color,
                'fill': self._fill, 'fill_color': self._fill_color, 'fill_opacity': self._fill_opacity}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'figure_type': self._figure_type,
                'x': self._x, 'y': self._y, 'width': self._width, 'height': self._height,
                'border': self._border, 'border_thickness': self._border_thickness, 'border_color': self._border_color,
                'fill': self._fill, 'fill_opacity': self._fill_opacity, 'fill_color': self._fill_color}

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self._uuid}; x: {self._x}; y: {self._y}; width: {self._width}; height: {self._height}; ' \
               f'figure_type: {self._figure_type}; border: {self._border}; border_thickness: {self._border_thickness}; ' \
               f'border_color: {self._border_color}; fill: {self._fill}; fill_opacity: {self._fill_opacity}; ' \
               f'fill_color: {self._fill_color}) at {hex(id(self))}>'
