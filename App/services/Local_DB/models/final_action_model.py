from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk, hex_color, action_fk, EnumInt, uuid_binary
from services.Local_DB import Base
from services.Local_DB.DTO.output_DTO import FinalActionOutDTO
from Config.Enums import FinalActionType

if TYPE_CHECKING:
    from .action_model import ActionORM


__all__ = ('FinalActionORM',)


class FinalActionORM(Base):
    __tablename__ = 'final_actions'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    x: Mapped[float]
    y: Mapped[float]
    action_type: Mapped[FinalActionType] = mapped_column(EnumInt(FinalActionType))
    # action_type: Mapped[FinalActionType]
    angle: Mapped[float]
    line_thickness: Mapped[int]
    color: Mapped[hex_color]

    action_id: Mapped[action_fk]
    action: Mapped['ActionORM'] = relationship(back_populates='final_actions')

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, FinalActionOutDTO) else super().__eq__(other)

    def __repr__(self):
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; ' \
               f'x: {self.x}; y: {self.y}; action_type: {self.action_type}; angle: {self.angle}; ' \
               f'line_thickness: {self.line_thickness}; color: {self.color}; ' \
               f'at {hex(id(self))}>'
