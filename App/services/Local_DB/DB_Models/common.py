import uuid
from abc import ABC
from typing import Annotated, Optional
from enum import Enum

from sqlalchemy import ForeignKey, String, TypeDecorator, BINARY, Dialect, Integer, UUID
from sqlalchemy.orm import mapped_column


# class UUIDBinary(TypeDecorator, ABC):
#     impl = BINARY(16)
#     cache_ok = True
#
#     def process_bind_param(self, value: Optional['UUID'], dialect: 'Dialect') -> Optional[bytes]:
#         return value.bytes if value else None
#
#     def process_result_value(self, value: Optional[bytes], dialect: 'Dialect') -> Optional['UUID']:
#         return UUID(bytes=value) if value else None


class EnumInt(TypeDecorator, ABC):
    impl = Integer
    cache_ok = True

    def __init__(self, enum_type: 'Enum', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value: Optional[Enum], dialect: 'Dialect') -> int:
        return value.value if value else None

    def process_result_value(self, value: Optional[int], dialect: 'Dialect') -> Optional['Enum']:
        return self._enum_type(value) if value is not None else value


pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
# uuid_binary = Annotated[UUID, mapped_column(UUIDBinary(), index=True)]
uuid_binary = Annotated[UUID, mapped_column(UUID(as_uuid=True))]
scheme_fk = Annotated[int, mapped_column(ForeignKey('schemes.id', ondelete='CASCADE'), nullable=False)]
player_fk = Annotated[int, mapped_column(ForeignKey('players.id', ondelete='CASCADE'), nullable=False)]
action_fk = Annotated[int, mapped_column(ForeignKey('actions.id', ondelete='CASCADE'), nullable=False)]
hex_color = Annotated[str, mapped_column(String(7))]