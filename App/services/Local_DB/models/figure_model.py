from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk, hex_color, scheme_fk
from .common import uuid_binary, EnumInt
from services.Local_DB import Base
from Config.Enums import FigureType

if TYPE_CHECKING:
    from .scheme_model import SchemeORM


__all_ = ('FigureORM',)


class FigureORM(Base):
    __tablename__ = 'figures'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    x: Mapped[float]
    y: Mapped[float]
    width: Mapped[float]
    height: Mapped[float]
    figure_type: Mapped[FigureType] = mapped_column(EnumInt(FigureType))
    # figure_type: Mapped[FigureType]
    border: Mapped[bool]
    border_thickness: Mapped[int]
    border_color: Mapped[hex_color]
    fill: Mapped[bool]
    fill_opacity: Mapped[str] = mapped_column(String(3))
    fill_color: Mapped[hex_color]

    scheme_id: Mapped[scheme_fk]
    scheme: Mapped['SchemeORM'] = relationship(back_populates='figures')

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; width: {self.width}; height: {self.height}; figure_type: {self.figure_type}; ' \
               f'border: {self.border}; border_thickness: {self.border_thickness}; border_color: {self.border_color}; ' \
               f'fill: {self.fill}; fill_opacity: {self.fill_opacity}; fill_color: {self.fill_color}) at {hex(id(self))}>'