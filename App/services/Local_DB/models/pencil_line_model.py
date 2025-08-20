from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .base import Base
from .common import pk, scheme_fk, hex_color
from .common import uuid_binary

if TYPE_CHECKING:
    from .scheme_model import SchemeORM

__all__ = ('PencilLineORM', )


class PencilLineORM(Base):
    __tablename__ = 'pencil_lines'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    x1: Mapped[float]
    y1: Mapped[float]
    x2: Mapped[float]
    y2: Mapped[float]
    thickness: Mapped[int]
    color: Mapped[hex_color]

    scheme_id: Mapped[scheme_fk]
    scheme: Mapped['SchemeORM'] = relationship(back_populates='pencil_lines')

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2}; ' \
               f'thickness: {self.thickness}; color: {self.color}) at {hex(id(self))}>'