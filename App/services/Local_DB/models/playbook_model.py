from typing import TYPE_CHECKING
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, Enum, Integer, Column, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import pk
from .common import uuid_binary, EnumInt
from services.Local_DB import Base
from services.Local_DB.DTO.output_DTO import PlaybookOutDTO
from Config.Enums import PlaybookType

if TYPE_CHECKING:
    from .scheme_model import SchemeORM

__all__ = ('PlaybookORM',)


class PlaybookORM(Base):
    __tablename__ = 'playbooks'

    id: Mapped[pk]
    uuid: Mapped[uuid_binary]
    name: Mapped[str]
    playbook_type: Mapped[PlaybookType] = mapped_column(EnumInt(PlaybookType))
    # playbook_type: Mapped[PlaybookType]
    # playbook_type: Mapped[int] = mapped_column(Enum(PlaybookType, impl=Integer, values_callable=lambda e: [t.value for t in e]))
    info: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=datetime.now())

    schemes: Mapped[list['SchemeORM']] = relationship(back_populates='playbook', lazy='selectin',
                                                      cascade='all, delete-orphan',
                                                      order_by='SchemeORM.row_index.asc()')

    deleted_schemes: list[int] = []
    deleted_figures: list[int] = []
    deleted_labels: list[int] = []
    deleted_pencil_lines: list[int] = []
    deleted_players: list[int] = []
    deleted_actions: list[int] = []

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, PlaybookOutDTO) else super().__eq__(other)

    def __repr__(self):
        return f'<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'name: {self.name}; playbook_type: {self.playbook_type}; info: {self.info}; ' \
               f'deleted_schemes: {self.deleted_schemes}; deleted_figures: {self.deleted_figures}; ' \
               f'deleted_labels: {self.deleted_labels}; deleted_pencil_lines: {self.deleted_pencil_lines}; ' \
               f'deleted_players: {self.deleted_players}; deleted_actions: {self.deleted_actions}) at {hex(id(self))}' \
               f'\n\t schemes: {self.schemes}>'