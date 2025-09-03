from datetime import datetime
from io import BytesIO

from PySide6.QtGui import QImage
from typing_extensions import Annotated
from pydantic import PositiveInt, Field, field_validator

from Services.Common.base_DTO import PlaybookBaseDTO, SchemeBaseDTO, FigureBaseDTO, LabelBaseDTO, PencilLineBaseDTO,\
    PlayerBaseDTO, ActionBaseDTO, ActionLineBaseDTO, FinalActionBaseDTO


class PencilLineOutDTO(PencilLineBaseDTO):
    pass


class LabelOutDTO(LabelBaseDTO):
    pass


class FigureOutDTO(FigureBaseDTO):
    pass


class FinalActionOutDTO(FinalActionBaseDTO):
    pass


class ActionLineOutDTO(ActionLineBaseDTO):
    pass


class ActionOutDTO(ActionBaseDTO):
    action_lines: Annotated[list[ActionLineOutDTO], Field(default_factory=list)]
    final_actions: Annotated[list[FinalActionOutDTO], Field(default_factory=list)]


class PlayerOutDTO(PlayerBaseDTO):
    actions: Annotated[list[ActionOutDTO], Field(default_factory=list)]


class SchemeOutDTO(SchemeBaseDTO):
    image: bytes
    players: Annotated[list[PlayerOutDTO], Field(default_factory=list)]
    figures: Annotated[list[FigureOutDTO], Field(default_factory=list)]
    labels: Annotated[list[LabelOutDTO], Field(default_factory=list)]
    pencil_lines: Annotated[list[PencilLineOutDTO], Field(default_factory=list)]

    @field_validator('image')
    def validate_image(cls, value, info):
        image = QImage()
        if not image.loadFromData(value):
            raise ValueError('Неверные данные изображения.')
        if not value.startswith(b'\x89PNG\r\n\x1a\n') or value.startswith(b'\xff\xd8\xff'):
            raise ValueError('Поддерживаются только PNG и JPG форматы.')
        return value


class PlaybookOutDTO(PlaybookBaseDTO):
    schemes: Annotated[list[SchemeOutDTO], Field(default_factory=list)]

    deleted_schemes: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_figures: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_labels: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_pencil_lines: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_players: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_actions: Annotated[list[PositiveInt], Field(default_factory=list)]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'name: {self.name}; playbook_type: {self.playbook_type}; info: {self.info}; ' \
               f'deleted_schemes: {self.deleted_schemes}; deleted_figures: {self.deleted_figures}; ' \
               f'deleted_labels: {self.deleted_labels}; deleted_pencil_lines: {self.deleted_pencil_lines}; ' \
               f'deleted_players: {self.deleted_players}; deleted_actions: {self.deleted_actions}) at {hex(id(self))}' \
               f'\n\t schemes: {self.schemes}>'