from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk
from .common import uuid_binary, EnumInt
from services.Local_DB import Base
from Config.Enums import TeamType

if TYPE_CHECKING:
    from .playbook_model import PlaybookORM
    from .player_model import PlayerORM
    from .figure_model import FigureORM
    from .label_model import LabelORM
    from .pencil_line_model import PencilLineORM

__all__ = ('SchemeORM',)


class SchemeORM(Base):
    __tablename__ = 'schemes'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    name: Mapped[str]
    row_index: Mapped[int]
    zoom: Mapped[int]
    view_point_x: Mapped[float]
    view_point_y: Mapped[float]
    first_team: Mapped[TeamType | None] = mapped_column(EnumInt(TeamType), nullable=True)
    # first_team: Mapped[TeamType | None]
    second_team: Mapped[TeamType | None] = mapped_column(EnumInt(TeamType), nullable=True)
    # second_team: Mapped[TeamType | None]
    first_team_position: Mapped[int | None]
    note: Mapped[str | None]

    playbook_id: Mapped[int] = mapped_column(ForeignKey('playbooks.id', ondelete='CASCADE'))
    playbook: Mapped['PlaybookORM'] = relationship(back_populates='schemes')

    players: Mapped[list['PlayerORM']] = relationship(back_populates='scheme', cascade='all, delete-orphan',
                                                      lazy='selectin')
    figures: Mapped[list['FigureORM']] = relationship(back_populates='scheme', cascade='all, delete-orphan',
                                                      lazy='selectin')
    labels: Mapped[list['LabelORM']] = relationship(back_populates='scheme', cascade='all, delete-orphan',
                                                    lazy='selectin')
    pencil_lines: Mapped[list['PencilLineORM']] = relationship(back_populates='scheme', cascade='all, delete-orphan',
                                                               lazy='selectin')

    def __repr__(self) -> str:
        return f'\n\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'name: {self.name}; row_index: {self.row_index}; zoom: {self.zoom}; ' \
               f'view_point_x: {self.view_point_x}, view_point_y: {self.view_point_y}; ' \
               f'first_team: {self.first_team}; second_team: {self.second_team}; ' \
               f'first_team_position: {self.first_team_position}; note: {self.note}; ' \
               f'\n\t\t\tfigures: {self.figures}' \
               f'\n\t\t\tlabels: {self.labels}' \
               f'\n\t\t\tpencil_lines: {self.pencil_lines}' \
               f'\n\t\t\tplayers: {self.players}>'
