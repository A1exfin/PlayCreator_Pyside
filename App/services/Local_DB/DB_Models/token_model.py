from typing import TYPE_CHECKING


from sqlalchemy import LargeBinary, CheckConstraint
from sqlalchemy.orm import mapped_column

from .base import Base

if TYPE_CHECKING:
    pass

__all__ = ('TokenORM',)


class TokenORM(Base):
    __tablename__ = 'auth_token'

    token = mapped_column(LargeBinary, primary_key=True, nullable=False)

    __table_args__ = (
        CheckConstraint('1=1', name='single_row_check'),
    )



