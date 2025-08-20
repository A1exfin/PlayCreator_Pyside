from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .base import Base
from .common import pk, hex_color, scheme_fk
from .common import uuid_binary

if TYPE_CHECKING:
    from .scheme_model import SchemeORM

__all__ = ('LabelORM', )


class LabelORM(Base):
    __tablename__ = 'labels'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    text: Mapped[str]
    font_type: Mapped[str]
    font_size: Mapped[int]
    font_bold: Mapped[bool]
    font_italic: Mapped[bool]
    font_underline: Mapped[bool]
    font_color: Mapped[hex_color]
    x: Mapped[float]
    y: Mapped[float]
    width: Mapped[float]
    height: Mapped[float]

    scheme_id: Mapped[scheme_fk]
    scheme: Mapped['SchemeORM'] = relationship(back_populates='labels')

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; width: {self.width}; height: {self.height}; ' \
               f'text: {self.text}; font_type: {self.font_type}; font_size: {self.font_size}; ' \
               f'font_bold: {self.font_bold}; font_italic: {self.font_italic}; font_underline: {self.font_underline}; ' \
               f'font_color: {self.font_color}) at {hex(id(self))}>'