from typing import TYPE_CHECKING, Annotated

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Core.Enums import TeamType
from .base import Base
from .common import pk
from .common import uuid_binary, EnumInt

if TYPE_CHECKING:
    pass

__all__ = ('TokenORM',)


class TokenORM(Base):
    __tablename__ = 'auth_token'

    token = Annotated[String(255), mapped_column(primary_key=True, nullable=False)]

    __table_args__ = CheckConstraint('1=1', name='single_row_check')


