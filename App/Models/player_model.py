from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID, uuid4

from PySide6.QtCore import Signal, QPointF

from Config.Enums import TeamType, StorageType
from .base_model import BaseModel
from .playbook_model import PlaybookModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject
    from Config.Enums import PlayerPositionType, FillType, SymbolType
    from .action_model import ActionModel


class PlayerModel(BaseModel):
    coordsChanged = Signal(object)  # QPointF
    playerStyleChanged = Signal(object, str, str, str)  # FillType | SymbolType, text, text_color, player_color
    actionAdded = Signal(object)  # ActionModel
    actionRemoved = Signal(object)  # removed ActionModel
    allActionsRemoved = Signal()

    def __init__(self, playbook_model: 'PlaybookModel', team_type: 'TeamType', position: 'PlayerPositionType',
                 text: str, x: int, y: int,
                 fill_type: Optional['FillType'] = None, symbol_type: Optional['SymbolType'] = None,
                 text_color: str = '#000000', player_color: str = '#000000',
                 uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['QObject'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._playbook_model = playbook_model
        self._x = x
        self._y = y
        self._team_type = team_type
        self._position = position
        self._text = text
        self._fill_type = fill_type
        self._symbol_type = symbol_type
        self._text_color = text_color
        self._player_color = player_color
        self._actions: list['ActionModel'] = list()

    def reset_id(self, storage_type: 'StorageType') -> None:
        if hasattr(self, f'_id_{storage_type.value}'):
            setattr(self, f'_id_{storage_type.value}', None)
        self._reset_actions_id(storage_type)

    def _reset_actions_id(self, storage_type: 'StorageType') -> None:
        for action_model in self._actions:
            if action_model:
                action_model.reset_id(storage_type)

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()
        self._set_actions_new_uuid()

    def _set_actions_new_uuid(self) -> None:
        for action_model in self._actions:
            if action_model:
                action_model.set_new_uuid()

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def set_pos(self, x: float, y: float) -> None:
        self._x, self._y = x, y
        self.coordsChanged.emit(QPointF(self.x, self.y))

    @property
    def team_type(self) -> 'TeamType':
        return self._team_type

    @property
    def position(self) -> 'PlayerPositionType':
        return self._position

    @property
    def text(self) -> str:
        return self._text

    @property
    def fill_type(self) -> 'FillType':
        return self._fill_type

    @property
    def symbol_type(self) -> 'SymbolType':
        return self._symbol_type

    @property
    def text_color(self) -> str:
        return self._text_color

    @property
    def player_color(self) -> str:
        return self._player_color

    def set_player_style(self, text: Optional[str], text_color: Optional[str], player_color: Optional[str],
                         fill_type: Optional['FillType'] = None, symbol_type: Optional['SymbolType'] = None) -> None:
        if fill_type and symbol_type:
            raise ValueError('Заливка и символ не могут быть заданы одновренно.')
        self._text, self._text_color, self._player_color, self._fill_type, self._symbol_type = \
            text, text_color, player_color, fill_type, symbol_type
        if self._team_type in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF, TeamType.OFFENCE_ADD):
            self.playerStyleChanged.emit(self._fill_type, self._text, self._text_color, self._player_color)
        if self._team_type in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
            self.playerStyleChanged.emit(self._symbol_type, self._text, self._text_color, self._player_color)

    @property
    def actions(self) -> list['ActionModel']:
        return self._actions.copy()

    def add_action(self, action_model: 'ActionModel') -> None:
        self._actions.append(action_model)
        self.actionAdded.emit(action_model)

    def remove_action(self, action: 'ActionModel') -> None:
        self._actions.remove(action)
        self.actionRemoved.emit(action)

    def remove_all_actions(self) -> None:
        self._actions.clear()
        self.allActionsRemoved.emit()

    def get_data_for_view(self) -> dict:
        data_for_view_dict = {'model_uuid': self._uuid, 'x': self._x, 'y': self._y, 'team_type': self._team_type,
                              'position': self._position, 'text': self._text, 'text_color': self._text_color,
                              'player_color': self._player_color}
        if self._team_type in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT,
                               TeamType.FIELD_GOAL_OFF, TeamType.OFFENCE_ADD):
            data_for_view_dict['fill_type'] = self._fill_type
        if self._team_type in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
            data_for_view_dict['symbol_type'] = self._symbol_type
        return data_for_view_dict

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'x': self._x, 'y': self._y, 'team_type': self._team_type, 'position': self._position,
                'text': self._text, 'text_color': self._text_color, 'player_color': self._player_color,
                'fill_type': self._fill_type, 'symbol_type': self._symbol_type,
                'actions': list()}

    def __repr__(self) -> str:
        return f'\n\t\t\t\t<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self._uuid}; x: {self._x}; y: {self._y}; team_type: {self._team_type}; ' \
               f'player_position: {self._position}; text: {self._text}; text_color: {self._text_color}; ' \
               f'player_color: {self._player_color}; fill_type: {self._fill_type}; symbol_type: {self._symbol_type}; ' \
               f'at {hex(id(self))}' \
               f'\n\t\t\t\t\tactions: {self._actions}>'
