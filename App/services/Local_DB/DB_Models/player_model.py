from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from Core.Enums import TeamType, FillType, SymbolType, PlayerPositionType
from .base import Base
from .common import pk, scheme_fk, hex_color
from .common import uuid_binary, EnumInt

if TYPE_CHECKING:
    from .scheme_model import SchemeORM
    from .action_line_model import ActionORM

__all__ = ('PlayerORM', )


class PlayerORM(Base):
    __tablename__ = 'players'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    x: Mapped[float]
    y: Mapped[float]
    team_type: Mapped[TeamType] = mapped_column(EnumInt(TeamType))
    # team_type: Mapped[TeamType]
    position: Mapped[PlayerPositionType] = mapped_column(EnumInt(PlayerPositionType))
    # position: Mapped[PlayerPositionType]
    text: Mapped[str]
    text_color: Mapped[hex_color]
    player_color: Mapped[hex_color]
    fill_type: Mapped[FillType | None] = mapped_column(EnumInt(FillType))
    # fill_type: Mapped[FillType | None]
    symbol_type: Mapped[SymbolType | None] = mapped_column(EnumInt(SymbolType))
    # symbol_type: Mapped[SymbolType | None]

    scheme_id: Mapped[scheme_fk]
    scheme: Mapped['SchemeORM'] = relationship(back_populates='players')

    actions: Mapped[list['ActionORM']] = relationship(back_populates='player', cascade='all, delete-orphan',
                                                      lazy='selectin')

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; team_type: {self.team_type}; player_position: {self.position}; ' \
               f'text: {self.text}; text_color: {self.text_color}; player_color: {self.player_color}; ' \
               f'fill_type: {self.fill_type}; symbol_type: {self.symbol_type}; at {hex(id(self))}' \
               f'\n\t\t\t\t\tactions: {self.actions}>'