from datetime import datetime
from typing import Annotated
from pydantic import Field, PositiveInt

from Config.Enums import PlaybookType
from services.common.base_DTOs import BaseDTO, PlaybookBaseDTO, SchemeBaseDTO, FigureBaseDTO,\
    LabelBaseDTO, PencilLineBaseDTO, PlayerBaseDTO, ActionLineBaseDTO, FinalActionBaseDTO


class PencilLineInputDTO(PencilLineBaseDTO):
    pass


class LabelInputDTO(LabelBaseDTO):
    pass


class FigureInputDTO(FigureBaseDTO):
    pass


class FinalActionInputDTO(FinalActionBaseDTO):
    pass


class ActionActionLineInputDTO(ActionLineBaseDTO):
    pass


class PlayerInputDTO(PlayerBaseDTO):
    action_lines: Annotated[list[ActionActionLineInputDTO], Field(default_factory=list)]
    final_actions: Annotated[list[FinalActionInputDTO], Field(default_factory=list)]


class SchemeInputDTO(SchemeBaseDTO):
    players: Annotated[list[PlayerInputDTO], Field(default_factory=list)]
    figures: Annotated[list[FigureInputDTO], Field(default_factory=list)]
    labels: Annotated[list[LabelInputDTO], Field(default_factory=list)]
    pencil_lines: Annotated[list[PencilLineInputDTO], Field(default_factory=list)]


class PlaybookInputDTO(PlaybookBaseDTO):
    schemes: Annotated[list[SchemeInputDTO], Field(default_factory=list)]


class SinglePlaybookInputDTO(BaseDTO):
    id: PositiveInt | None = None
    name: str
    playbook_type: PlaybookType
    created_at: datetime
    updated_at: datetime

