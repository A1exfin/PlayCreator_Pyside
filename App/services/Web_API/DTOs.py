from datetime import datetime
from typing_extensions import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator, PositiveInt, PositiveFloat, NonNegativeInt, NonNegativeFloat, \
    ConfigDict

from Config import PlayerData
from Core.Enums import PlaybookType, PlaybookAccessOptions, Mode, TeamType, FillType, SymbolType
from Services.Common.validators_DTO import validate_x, validate_y, validate_first_team_position, validate_right_border, \
    validate_bot_border
from Services.Common.mixins_DTO import ValidatePointCoordinatesMixin, ValidateLineCoordinatesMixin, ValidateWidthAndHeightMixin


class SerializersBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PencilSerializer(SerializersBase, ValidateLineCoordinatesMixin):
    id: PositiveInt | None = None
    x1: NonNegativeFloat
    y1: NonNegativeFloat
    x2: NonNegativeFloat
    y2: NonNegativeFloat
    thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]


class LabelSerializer(SerializersBase, ValidatePointCoordinatesMixin, ValidateWidthAndHeightMixin):
    id: PositiveInt | None = None
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: PositiveFloat
    height: PositiveFloat
    text: str
    font_type: str #################
    font_size: Annotated[PositiveInt, Field(ge=8, le=36)]
    font_bold: bool
    font_italic: bool
    font_underline: bool
    font_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]


class FigureSerializer(SerializersBase, ValidatePointCoordinatesMixin, ValidateWidthAndHeightMixin):
    id: PositiveInt | None = None
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: PositiveFloat
    height: PositiveFloat
    figure_type: Mode
    border: bool
    border_thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    border_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    fill: bool
    fill_opacity: Annotated[str, Field(pattern=r'^#[a-f\d]{2}$')]
    fill_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    @field_validator('figure_type', mode='after')
    def validate_figure_type(cls, value, info):
        if value not in (Mode.RECTANGLE, Mode.ELLIPSE):
            raise ValueError('У фигуры тип должен быть прямоугольник или эллипс. Сейчас "{value}".'.format(value=value))
        return value

    @model_validator(mode='after')
    def validate_border_fill(self, info):
        if self.border is False and self.fill is False:
            raise ValueError('У фигуры не могут одновременно отсутствовать граница и заливка.')
        return self


class FinalActionSerializer(SerializersBase, ValidatePointCoordinatesMixin):
    id: PositiveInt | None = None
    x: NonNegativeFloat
    y: NonNegativeFloat
    action_type: Mode
    angle: Annotated[NonNegativeFloat, Field(ge=0, le=360)]
    line_thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    action_number: NonNegativeInt

    @field_validator('action_type', mode='after')
    def validate_action_type(cls, value, info):
        if value not in (Mode.ROUTE, Mode.BLOCK):
            raise ValueError('Тип финального действия должен быть маршрут или блок. Сейчас "{value}".'.format(value=value))
        return value


class LineSerializer(SerializersBase, ValidateLineCoordinatesMixin):
    id: PositiveInt | None = None
    x1: NonNegativeFloat
    y1: NonNegativeFloat
    x2: NonNegativeFloat
    y2: NonNegativeFloat
    action_type: Mode
    action_number: NonNegativeInt
    thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    @field_validator('action_type')
    def validate_action_type(cls, value, info):
        if value not in (Mode.ROUTE, Mode.BLOCK, Mode.MOTION):
            raise ValueError('У линии должен быть тип: маршрут, блок, моушен. Сейчас "{value}".'.format(value=value))
        return value


class PlayerSerializer(SerializersBase, ValidatePointCoordinatesMixin):
    id: PositiveInt | None = None
    x: NonNegativeFloat
    y: NonNegativeFloat
    team_type: TeamType
    player_position: str###################################
    current_action_number: NonNegativeInt
    text: str
    text_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    player_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    fill_type: FillType | None
    symbol_type: SymbolType | None
    lines: Annotated[list[LineSerializer], Field(default_factory=list)]
    final_actions: Annotated[list[FinalActionSerializer], Field(default_factory=list)]
    deleted_lines: Annotated[list[int], Field(default_factory=list)]
    deleted_final_actions: Annotated[list[int], Field(default_factory=list)]

    @model_validator(mode='after')
    def validate_right_border(self, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_right_border(self.x, PlayerData.size, playbook_type)
        return self

    @model_validator(mode='after')
    def validate_bot_border(self, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_bot_border(self.y, PlayerData.size, playbook_type)
        return self

    @model_validator(mode='after')
    def validate_fill_and_symbol(self):
        if self.fill_type is None and self.symbol_type is None:
            raise ValueError('У игрока одновременно не могут отсутствовать заливка и символ.')
        if self.team_type in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF) \
                and self.symbol_type is not None:
            raise ValueError('Для игроков команд нападения, пробития кикофа, пробития панта, и пробития филд-гола символ должен быть None. Сейчас "{symbol_type}".'.format(symbol_type=self.symbol_type))
        if self.team_type in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF) \
                and self.fill_type is not None:
            raise ValueError('Для игроков команд защиты, возврата кикофа, возврата панта и защиты от филд-гола заливка должна быть None. Сейчас "{fill_type}".'.format(fill_type=self.fill_type))
        return self


class SchemeSerializer(SerializersBase):
    id: PositiveInt | None = None
    name: str
    row_number: NonNegativeInt
    view_point_x: NonNegativeFloat
    view_point_y: NonNegativeFloat
    first_team: TeamType | None = None
    second_team: TeamType | None = None
    first_team_position: NonNegativeInt | None = None
    comment: str | None
    players: Annotated[list[PlayerSerializer], Field(default_factory=list)]
    figures: Annotated[list[FigureSerializer], Field(default_factory=list)]
    labels: Annotated[list[LabelSerializer], Field(default_factory=list)]
    pencil_lines: Annotated[list[PencilSerializer], Field(default_factory=list)]
    # image: str
    deleted_players: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_figures: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_labels: Annotated[list[PositiveInt], Field(default_factory=list)]
    deleted_pencil_lines: Annotated[list[PositiveInt], Field(default_factory=list)]

    @field_validator('view_point_x', mode='after')
    def validate_view_point_x(cls, value, info):
        # print(f'SchemeSerializer model_validator validate_view_point_x {info = }')
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_x(value, playbook_type)
        return value

    @field_validator('view_point_y', mode='after')
    def validate_view_point_y(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_y(value, playbook_type)
        return value

    @field_validator('first_team', mode='after')
    def validate_first_team_type(cls, value, info):
        if value and info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            if playbook_type is PlaybookType.FOOTBALL and value not in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
                raise ValueError('Для плейбука с типом "футбол" тип первой команды должен быть: надение, пробитие кикофа, пробитие панта, пробитие филдгола. Сейчас "{value}".'.format(value=value))
            elif playbook_type is PlaybookType.FLAG and value is not TeamType.OFFENCE:
                raise ValueError('Для плейбука с типом "флаг-футбол" тип первой команды должен быть: надение. Сейчас "{value}".'.format(value=value))
        return value

    @field_validator('second_team', mode='before')
    def validate_second_team_type(cls, value, info):
        if value and info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            if playbook_type is PlaybookType.FOOTBALL and value not in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
                raise ValueError('Для плейбука с типом "футбол" тип второй команды должен быть: защита, возврат кикофа, возврат панта, защита от филдгола. Сейчас "{value}".'.format(value=value))
            elif playbook_type is PlaybookType.FLAG and not value is TeamType.DEFENCE:
                raise ValueError('Для плейбука с типом "флаг-футбол" тип второй команды должен быть: защита. Сейчас "{value}".'.format(value=value))
        return value

    @field_validator('first_team_position', mode='after')
    def validate_first_team_position(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_first_team_position(value, playbook_type)
        return value

    @model_validator(mode='after')
    def validate_first_team_and_second_team_matching(self, info):
        if self.first_team is None and self.second_team:
            raise ValueError('При отсутствующей первой команде должна отсутствовать и вторая.')
        if self.first_team is None and self.first_team_position:
            raise ValueError('При отсутствии первой команды должно отсутствовать положение первой команды на поле.')
        if self.first_team and self.second_team:
            if self.first_team == TeamType.OFFENCE and self.second_team != TeamType.DEFENCE:
                raise ValueError('Против команды нападения должна быть команда защиты. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team == TeamType.KICKOFF and self.second_team != TeamType.KICK_RET:
                raise ValueError('Против команды пробития кикофа должна быть команда возврата кикофа. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team == TeamType.PUNT and self.second_team != TeamType.PUNT_RET:
                raise ValueError('Против команды пробития панта должна быть команда возврата панта. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team == TeamType.FIELD_GOAL_OFF and self.second_team != TeamType.FIELD_GOAL_DEF:
                raise ValueError('Против команды пробития филд-гола должна быть команда защиты от филд-гола. Сейчас "{second_team}".'.format(second_team=self.second_team))
        return self


class PlaybookAccessSettingsSerializer(SerializersBase):
    who_can_edit: PlaybookAccessOptions
    who_can_see: PlaybookAccessOptions


class PlaybookSerializer(SerializersBase):
    id: PositiveInt | None = None
    # settings: PlaybookAccessSettingsSerializer
    team_id: PositiveInt
    name: str
    playbook_type: PlaybookType
    info: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    schemes: Annotated[list[SchemeSerializer], Field(default_factory=list)]
    deleted_schemes: Annotated[list[PositiveInt], Field(default_factory=list)]

