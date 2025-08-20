from datetime import datetime
from typing_extensions import Annotated
from pydantic import PositiveInt, Field

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
    players: Annotated[list[PlayerOutDTO], Field(default_factory=list)]
    figures: Annotated[list[FigureOutDTO], Field(default_factory=list)]
    labels: Annotated[list[LabelOutDTO], Field(default_factory=list)]
    pencil_lines: Annotated[list[PencilLineOutDTO], Field(default_factory=list)]


class PlaybookOutDTO(PlaybookBaseDTO):
    schemes: Annotated[list[SchemeOutDTO], Field(default_factory=list)]

    deleted_schemes: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_figures: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_labels: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_pencil_lines: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_players: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_actions: Annotated[list[PositiveInt], Field(default_factory=list)]
