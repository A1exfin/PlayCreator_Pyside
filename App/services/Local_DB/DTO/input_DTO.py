from datetime import datetime
from typing import Annotated
from pydantic import Field

from Services.Common.base_DTO import PlaybookBaseDTO, SchemeBaseDTO, FigureBaseDTO,\
    LabelBaseDTO, PencilLineBaseDTO, PlayerBaseDTO, ActionBaseDTO, ActionLineBaseDTO, FinalActionBaseDTO


class PencilLineInputDTO(PencilLineBaseDTO):
    pass


class LabelInputDTO(LabelBaseDTO):
    pass


class FigureInputDTO(FigureBaseDTO):
    pass


class FinalActionInputDTO(FinalActionBaseDTO):
    pass


class ActionLineInputDTO(ActionLineBaseDTO):
    pass


class ActionInputDTO(ActionBaseDTO):
    action_lines: Annotated[list[ActionLineInputDTO], Field(default_factory=list)]
    final_actions: Annotated[list[FinalActionInputDTO], Field(default_factory=list)]


class PlayerInputDTO(PlayerBaseDTO):
    actions: Annotated[list[ActionInputDTO], Field(default_factory=list)]


class SchemeInputDTO(SchemeBaseDTO):
    players: Annotated[list[PlayerInputDTO], Field(default_factory=list)]
    figures: Annotated[list[FigureInputDTO], Field(default_factory=list)]
    labels: Annotated[list[LabelInputDTO], Field(default_factory=list)]
    pencil_lines: Annotated[list[PencilLineInputDTO], Field(default_factory=list)]


class PlaybookInputDTO(PlaybookBaseDTO):
    schemes: Annotated[list[SchemeInputDTO], Field(default_factory=list)]

    # created_at: datetime
    # updated_at: datetime

