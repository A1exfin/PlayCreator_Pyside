from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk, player_fk, uuid_binary
from services.Local_DB import Base
from services.Local_DB.DTO.output_DTO import ActionOutDTO

if TYPE_CHECKING:
    from .player_model import PlayerORM
    from .action_line_model import ActionLineORM
    from .final_action_model import FinalActionORM

__all__ = ('ActionORM',)


class ActionORM(Base):
    __tablename__ = 'actions'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]

    player_id: Mapped[player_fk]
    player: Mapped['PlayerORM'] = relationship(back_populates='actions')

    action_lines: Mapped[list['ActionLineORM']] = relationship(
        back_populates='action', cascade='all, delete-orphan', lazy='selectin'
    )
    final_actions: Mapped[list['FinalActionORM']] = relationship(
        back_populates='action', cascade='all, delete-orphan', lazy='selectin'
    )

    def __eq__(self, other) -> bool:
        return self.id == other.id if isinstance(other, ActionOutDTO) else super().__eq__(other)

    def __repr__(self) -> str:
        return f'\n\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}) at {hex(id(self))}> ' \
               f'\n\t\t\t\t\t\t\taction_lines: {self.action_lines}\n\t\t\t\t\t\t\tfinal_actions: {self.final_actions}>'