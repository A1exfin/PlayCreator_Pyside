from typing import TYPE_CHECKING
from datetime import datetime
from typing_extensions import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, PositiveInt, PositiveFloat, NonNegativeInt,\
    NonNegativeFloat, ConfigDict

from Config import PlayerData
from Config.Enums import PlaybookType, PlayerPositionType, TeamType, FillType, SymbolType, ActionLineType, FinalActionType, FigureType
from .validators_DTO import validate_x, validate_y, validate_first_team_position, validate_right_border, validate_bot_border
from .mixins_DTO import ValidatePointCoordinatesMixin, ValidateLineCoordinatesMixin, ValidateWidthAndHeightMixin

if TYPE_CHECKING:
    pass


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PencilLineBaseDTO(BaseDTO, ValidateLineCoordinatesMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x1: NonNegativeFloat
    y1: NonNegativeFloat
    x2: NonNegativeFloat
    y2: NonNegativeFloat
    thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2}; ' \
               f'thickness: {self.thickness}; color: {self.color}) at {hex(id(self))}>'


class LabelBaseDTO(BaseDTO, ValidatePointCoordinatesMixin, ValidateWidthAndHeightMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: PositiveFloat
    height: PositiveFloat
    text: str
    font_type: str ################# ВАЛИДАТОР
    font_size: Annotated[PositiveInt, Field(ge=8, le=36)]
    font_bold: bool
    font_italic: bool
    font_underline: bool
    font_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; width: {self.width}; height: {self.height}; ' \
               f'text: {self.text}; font_type: {self.font_type}; font_size: {self.font_size}; ' \
               f'font_bold: {self.font_bold}; font_italic: {self.font_italic}; font_underline: {self.font_underline}; ' \
               f'font_color: {self.font_color}) at {hex(id(self))}>'


class FigureBaseDTO(BaseDTO, ValidatePointCoordinatesMixin, ValidateWidthAndHeightMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x: NonNegativeFloat
    y: NonNegativeFloat
    width: NonNegativeFloat
    height: NonNegativeFloat
    figure_type: FigureType
    border: bool
    border_thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    border_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    fill: bool
    fill_opacity: Annotated[str, Field(pattern=r'^#[a-f\d]{2}$')]
    fill_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    @field_validator('figure_type', mode='after')
    def validate_figure_type(cls, value, info):
        if value not in (FigureType.RECTANGLE, FigureType.ELLIPSE):
            raise ValueError('У фигуры тип должен быть прямоугольник или эллипс. Сейчас "{value}".'.format(value=value))
        return value

    @model_validator(mode='after')
    def validate_border_fill(self, info):
        if self.border is False and self.fill is False:
            raise ValueError('У фигуры не могут одновременно отсутствовать граница и заливка.')
        return self

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; width: {self.width}; height: {self.height}; figure_type: {self.figure_type}; ' \
               f'border: {self.border}; border_thickness: {self.border_thickness}; border_color: {self.border_color}; ' \
               f'fill: {self.fill}; fill_opacity: {self.fill_opacity}; fill_color: {self.fill_color}) at {hex(id(self))}>'


class FinalActionBaseDTO(BaseDTO, ValidatePointCoordinatesMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x: NonNegativeFloat
    y: NonNegativeFloat
    action_type: FinalActionType
    angle: Annotated[NonNegativeFloat, Field(ge=0, le=360)]
    line_thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    @field_validator('action_type', mode='after')
    def validate_action_type(cls, value, info):
        if value not in (FinalActionType.ARROW, FinalActionType.LINE):
            raise ValueError('Тип финального действия должен быть стрелка или линия. Сейчас "{value}".'.format(value=value))
        return value

    def __repr__(self):
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; ' \
               f'x: {self.x}; y: {self.y}; action_type: {self.action_type}; angle: {self.angle}; ' \
               f'line_thickness: {self.line_thickness}; color: {self.color}; ' \
               f'at {hex(id(self))}>'


class ActionLineBaseDTO(BaseDTO, ValidateLineCoordinatesMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x1: NonNegativeFloat
    y1: NonNegativeFloat
    x2: NonNegativeFloat
    y2: NonNegativeFloat
    line_type: ActionLineType
    thickness: Annotated[PositiveInt, Field(ge=2, le=6)]
    color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]

    @field_validator('line_type')
    def validate_line_type(cls, value, info):
        if value not in (ActionLineType.ROUTE, ActionLineType.BLOCK, ActionLineType.MOTION):
            raise ValueError('У линии должен быть тип: маршрут, блок, моушен. Сейчас "{value}".'.format(value=value))
        return value

    def __repr__(self) -> str:
        return f'\n\t\t\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; ' \
               f'x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2}; line_type: {self.line_type}; ' \
               f'thickness: {self.thickness}; color: {self.color}) ' \
               f'at {hex(id(self))}>'


class ActionBaseDTO(BaseDTO):
    id: PositiveInt | None = None
    uuid: UUID

    def __repr__(self) -> str:
        return f'\n\t\t\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}) at {hex(id(self))}> ' \
               f'\n\t\t\t\t\t\t\taction_lines: {self.action_lines}\n\t\t\t\t\t\t\tfinal_actions: {self.final_actions}>'


class PlayerBaseDTO(BaseDTO, ValidatePointCoordinatesMixin):
    id: PositiveInt | None = None
    uuid: UUID
    x: NonNegativeFloat
    y: NonNegativeFloat
    team_type: TeamType
    position: PlayerPositionType
    text: str
    text_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    player_color: Annotated[str, Field(pattern=r'^#[a-f\d]{6}$')]
    fill_type: FillType | None
    symbol_type: SymbolType | None

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

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'x: {self.x}; y: {self.y}; team_type: {self.team_type}; player_position: {self.position}; ' \
               f'text: {self.text}; text_color: {self.text_color}; player_color: {self.player_color}; ' \
               f'fill_type: {self.fill_type}; symbol_type: {self.symbol_type}; at {hex(id(self))}' \
               f'\n\t\t\t\t\tactions: {self.actions}>'


class SchemeBaseDTO(BaseDTO):
    id: PositiveInt | None = None
    uuid: UUID
    name: str
    note: str
    row_index: NonNegativeInt
    view_point_x: NonNegativeFloat
    view_point_y: NonNegativeFloat
    zoom: Annotated[NonNegativeInt, Field(ge=0, le=200)]
    first_team: TeamType | None = None
    second_team: TeamType | None = None
    first_team_position: NonNegativeInt | None = None

    @field_validator('view_point_x', mode='after')
    def validate_view_point_x(cls, value, info):
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
            elif playbook_type is PlaybookType.FLAG and value is not TeamType.DEFENCE:
                raise ValueError('Для плейбука с типом "флаг-футбол" тип второй команды должен быть: защита. Сейчас "{value}".'.format(value=value))
        return value

    @field_validator('first_team_position', mode='after')
    def validate_first_team_position(cls, value, info):
        if value and info.context and 'playbook_type' in info.context:
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
            if self.first_team is TeamType.OFFENCE and self.second_team is not TeamType.DEFENCE:
                raise ValueError('Против команды нападения должна быть команда защиты. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team is TeamType.KICKOFF and self.second_team is not TeamType.KICK_RET:
                raise ValueError('Против команды пробития кикофа должна быть команда возврата кикофа. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team is TeamType.PUNT and self.second_team is not TeamType.PUNT_RET:
                raise ValueError('Против команды пробития панта должна быть команда возврата панта. Сейчас "{second_team}".'.format(second_team=self.second_team))
            elif self.first_team is TeamType.FIELD_GOAL_OFF and self.second_team is not TeamType.FIELD_GOAL_DEF:
                raise ValueError('Против команды пробития филд-гола должна быть команда защиты от филд-гола. Сейчас "{second_team}".'.format(second_team=self.second_team))
        return self

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


class PlaybookBaseDTO(BaseDTO):
    id: PositiveInt | None = None
    uuid: UUID
    name: str
    playbook_type: PlaybookType
    info: str

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} (id: {self.id}; uuid: {self.uuid}; ' \
               f'name: {self.name}; playbook_type: {self.playbook_type}; info: {self.info}; ' \
               f'deleted_schemes: {self.deleted_schemes}; deleted_figures: {self.deleted_figures}; ' \
               f'deleted_labels: {self.deleted_labels}; deleted_pencil_lines: {self.deleted_pencil_lines}; ' \
               f'deleted_players: {self.deleted_players}; deleted_actions: {self.deleted_actions}) at {hex(id(self))}' \
               f'\n\t schemes: {self.schemes}>'