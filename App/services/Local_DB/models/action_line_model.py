from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk, hex_color, action_fk
from .common import EnumInt, uuid_binary
from services.Local_DB import Base
from Config.Enums import ActionLineType

if TYPE_CHECKING:
    from .action_model import ActionORM

__all__ = ('ActionLineORM',)


class ActionLineORM(Base):
    __tablename__ = 'action_lines'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    x1: Mapped[float]
    y1: Mapped[float]
    x2: Mapped[float]
    y2: Mapped[float]
    line_type: Mapped[ActionLineType] = mapped_column(EnumInt(ActionLineType))
    # line_type: Mapped[ActionLineType]
    thickness: Mapped[int]
    color: Mapped[hex_color]

    action_id: Mapped[action_fk]
    action: Mapped['ActionORM'] = relationship(back_populates='action_lines')

    def __repr__(self) -> str:
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; ' \
               f'x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2}; line_type: {self.line_type}; ' \
               f'thickness: {self.thickness}; color: {self.color}) ' \
               f'at {hex(id(self))}>'