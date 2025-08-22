from typing import TYPE_CHECKING, Optional
from itertools import chain
from uuid import UUID

from PySide6.QtCore import Signal

from Core.Enums import StorageType, PlaybookType, TeamType
from Core.settings import FIRST_TEAM_POSITION_MAX, ZOOM
from .base_model import BaseModel

if TYPE_CHECKING:
    from .playbook_model import PlaybookModel
    from .figure_model import FigureModel
    from .label_model import LabelModel
    from .pencil_line_model import PencilLineModel
    from .player_model import PlayerModel


class SchemeModel(BaseModel):
    nameChanged = Signal(str)
    noteChanged = Signal(str)
    zoomChanged = Signal(int)
    firstTeamPlayerAdded = Signal(object)  # PlayerModel
    firstTeamPlayersRemoved = Signal()
    firstTeamStateChanged = Signal(object, object)  # TeamType | None, self._first_team_position | None
    # object из-за того что None автоматически преобразуется в 0 при типе int
    secondTeamPlayerAdded = Signal(object)  # PlayerModel
    secondTeamPlayersRemoved = Signal()
    secondTeamStateChanged = Signal(object)  # TeamType | None
    # object из-за того что None автоматически преобразуется в 0 при типе int
    additionalPlayerAdded = Signal(object)  # PlayerModel
    additionalPlayerRemoved = Signal()
    figureAdded = Signal(object)  # FigureModel
    figureRemoved = Signal(object)  # removed FigureModel
    allFiguresRemoved = Signal()
    labelAdded = Signal(object)  # LabelModel
    labelRemoved = Signal(object)  # removed LabelModel
    allLabelsRemoved = Signal()
    pencilLinesAdded = Signal(list)  # list[PencilLineModel]
    pencilLinesRemoved = Signal(list)  # removed list[PencilLineModel]
    allPencilLinesRemoved = Signal()

    def __init__(self, playbook_model: 'PlaybookModel', name: str,
                 view_point_x: int, view_point_y: int, note: str = '', zoom: int = 60,
                 first_team: Optional['TeamType'] = None, second_team: Optional['TeamType'] = None,
                 first_team_position: Optional[int] = None, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['PlaybookModel'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._playbook_model = playbook_model
        self._playbook_type = self._playbook_model.playbook_type
        self._name = name
        self._note = note
        self._view_point_x = view_point_x
        self._view_point_y = view_point_y
        self._zoom = zoom
        self._first_team = None
        self._second_team = None
        self._first_team_position = None
        self._figures: list['FigureModel'] = list()
        self._labels: list['LabelModel'] = list()
        self._pencil_lines: list['PencilLineModel'] = list()
        self._first_team_players: list['PlayerModel'] = list()
        self._additional_player: Optional['PlayerModel'] = None
        self._second_team_players: list['PlayerModel'] = list()
        self.set_first_team_state(first_team, first_team_position)
        self.set_second_team_state(second_team)

    def _set_changed_flag(self) -> None:
        super().set_changed_flag()
        self._playbook_model.changed = True

    def reset_id(self, storage_type: 'StorageType') -> None:
        super().reset_id(storage_type)
        self._reset_scheme_items_id(storage_type)

    def _reset_scheme_items_id(self, storage_type: 'StorageType') -> None:
        for item_model in chain(
                self._first_team_players, self._second_team_players, [self._additional_player],
                self._figures, self._labels, self._pencil_lines
        ):
            if item_model:
                item_model.reset_id(storage_type)

    def set_new_uuid(self) -> None:
        super().set_new_uuid()
        self._set_scheme_items_new_uuid()

    def _set_scheme_items_new_uuid(self) -> None:
        for item_model in chain(
                self._first_team_players, self._second_team_players, [self._additional_player],
                self._figures, self._labels, self._pencil_lines
        ):
            if item_model:
                item_model.set_new_uuid()

    def reset_changed_flag(self) -> None:
        super().reset_changed_flag()
        self._reset_scheme_items_changed_flag()

    def _reset_scheme_items_changed_flag(self) -> None:
        for item_model in chain(
                self._first_team_players, self._second_team_players, [self._additional_player],
                self._figures, self._labels, self._pencil_lines
        ):
            if item_model:
                item_model.reset_changed_flag()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        self._set_changed_flag()
        self.nameChanged.emit(name)

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, note: str) -> None:
        self._note = note
        self._set_changed_flag()
        self.noteChanged.emit(note)

    @property
    def view_point_x(self) -> int:
        return self._view_point_x

    @view_point_x.setter
    def view_point_x(self, value: int) -> None:
        # self._set_changed_flag()
        self._view_point_x = value

    @property
    def view_point_y(self) -> int:
        return self._view_point_y

    @view_point_y.setter
    def view_point_y(self, value: int) -> None:
        # self._set_changed_flag()
        self._view_point_y = value

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    def zoom(self, value: int) -> None:
        if ZOOM.min <= value <= ZOOM.max:
            self._zoom = value
            # self._set_changed_flag()
            self.zoomChanged.emit(self.zoom)

    @property
    def first_team(self) -> Optional['TeamType']:
        return self._first_team

    @property
    def second_team(self) -> Optional['TeamType']:
        return self._second_team

    @property
    def first_team_position(self) -> Optional[int]:
        return self._first_team_position

    @property
    def first_team_players(self) -> list['PlayerModel']:
        return self._first_team_players.copy()

    def set_first_team_state(self, first_team_type: Optional['TeamType'], first_team_position: Optional[int]) -> None:
        if first_team_type and first_team_position:
            if self._playbook_type is PlaybookType.FOOTBALL:
                if first_team_type not in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
                    raise ValueError(f'Неверный тип первой команды - {first_team_type.name.capitalize()}.')
                if first_team_position > FIRST_TEAM_POSITION_MAX.football:
                    raise ValueError('Позиция первой команды не может превышать {position} ярдов.'.format(position=FIRST_TEAM_POSITION_MAX.football))
                # if len(self._first_team_players) != 11:
                #     raise ValueError('Игроков первой команды должно быть 11.')
            if self._playbook_type is PlaybookType.FLAG:
                if first_team_type is not TeamType.OFFENCE:
                    raise ValueError(f'Неверный тип первой команды - {first_team_type.name.capitalize()}.')
                if first_team_position > FIRST_TEAM_POSITION_MAX.flag:
                    raise ValueError('Позиция первой команды не может превышать {position} ярдов.'.format(position=FIRST_TEAM_POSITION_MAX.flag))
                # if len(self._first_team_players) != 5:
                #     raise ValueError('Игроков первой команды должно быть 5.')
        self._first_team = first_team_type
        self._first_team_position = first_team_position
        self._set_changed_flag()
        self.firstTeamStateChanged.emit(self._first_team, self._first_team_position)

    def add_first_team_player(self, player_model: 'PlayerModel') -> None:
        if self._playbook_type is PlaybookType.FOOTBALL:
            if player_model.team_type not in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
                raise ValueError(f'Неверный тип игрока первой команды - {player_model.team_type.name.capitalize()}.')
            if len(self._first_team_players) >= 11:
                raise ValueError('Количество игроков первой команды не должно превышать 11.')
        if self._playbook_type is PlaybookType.FLAG:
            if player_model.team_type is not TeamType.OFFENCE:
                raise ValueError(f'Неверный тип игрока первой команды - {player_model.team_type.name.capitalize()}.')
            if len(self._first_team_players) >= 5:
                raise ValueError('Количество игроков первой команды не должно превышать 5.')
        if self._first_team_players and player_model.team_type is not self._first_team_players[-1].team_type:
            raise ValueError('Игроки находящиеся в одной команде должны быть одного типа.')
        self._first_team_players.append(player_model)
        self.firstTeamPlayerAdded.emit(player_model)

    @property
    def second_team_players(self) -> list['PlayerModel']:
        return self._second_team_players.copy()

    def set_second_team_state(self, second_team_type: Optional['TeamType']) -> None:
        if second_team_type:
            if self._playbook_type is PlaybookType.FOOTBALL:
                if second_team_type not in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
                    raise ValueError(f'Неверный тип второй команды - {second_team_type.name.capitalize()}.')
                # if len(self._second_team_players) != 11:
                #     raise ValueError('Игроков вотрой команды должно быть 11.')
            if self._playbook_type is PlaybookType.FLAG:
                if second_team_type is not TeamType.DEFENCE:
                    raise ValueError(f'Неверный тип второй команды - {second_team_type.name.capitalize()}.')
                # if len(self._second_team_players) != 5:
                #     raise ValueError('Игроков второй команды должно быть 5.')
        self._second_team = second_team_type
        self._set_changed_flag()
        self.secondTeamStateChanged.emit(self._second_team)

    def add_second_team_player(self, player_model: 'PlayerModel') -> None:
        if self._playbook_type is PlaybookType.FOOTBALL and \
                player_model.team_type not in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
            raise ValueError(f'Неверный тип игрока второй команды - {player_model.team_type.name.capitalize()}.')
        if self._playbook_type is PlaybookType.FLAG and player_model.team_type is not TeamType.DEFENCE:
            raise ValueError(f'Неверный тип игрока второй команды - {player_model.team_type.name.capitalize()}.')
        if self._playbook_type is PlaybookType.FOOTBALL and len(self._second_team_players) >= 11:
            raise ValueError('Количество игроков второй команды не должно превышать 11.')
        if self._playbook_type is PlaybookType.FLAG and len(self._second_team_players) >= 5:
            raise ValueError('Количество игроков второй команды не должно превышать 5.')
        if self._second_team_players and player_model.team_type is not self._second_team_players[-1].team_type:
            raise ValueError('Игроки находящиеся в одной команде должны быть одного типа')
        self._second_team_players.append(player_model)
        self.secondTeamPlayerAdded.emit(player_model)

    @property
    def additional_player(self) -> Optional['PlayerModel']:
        return self._additional_player

    @additional_player.setter
    def additional_player(self, player_model: 'PlayerModel') -> None:
        if self._additional_player is not None:
            raise ValueError('Дополнительный игрок нападения уже добавлен.')
        if player_model.team_type is not TeamType.OFFENCE_ADD:
            raise ValueError(f'Неверный тип дополнительного игрока - {player_model.team_type.name.capitalize()}.')
        if self._first_team is not TeamType.OFFENCE:
            raise ValueError('Для добавления дополнительного игрока тип первой команды должен быть - нападение.')
        self._additional_player = player_model
        self._set_changed_flag()
        self.additionalPlayerAdded.emit(self.additional_player)

    def remove_first_team_players(self) -> None:
        self._first_team_players.clear()
        self.set_first_team_state(None, None)
        self.firstTeamPlayersRemoved.emit()

    def remove_second_team_players(self) -> None:
        self._second_team_players.clear()
        self.set_second_team_state(None)
        self.secondTeamPlayersRemoved.emit()

    def remove_additional_player(self) -> None:
        self._additional_player = None
        self._set_changed_flag()
        self.additionalPlayerRemoved.emit()

    def remove_all_players(self) -> None:
        # Порядок удаления команд важен для правильной установки GUI основного окна. Не менять.
        if self._additional_player:
            self.remove_additional_player()
        if self.second_team:
            self.remove_second_team_players()
            self.set_second_team_state(None)
        if self.first_team:
            self.remove_first_team_players()
            self.set_first_team_state(None, None)

    @property
    def figures(self) -> list['FigureModel']:
        return self._figures.copy()

    def add_figure(self, figure: 'FigureModel') -> None:
        self._figures.append(figure)
        self._set_changed_flag()
        self.figureAdded.emit(figure)

    def remove_figure(self, figure: 'FigureModel') -> None:
        self._figures.remove(figure)
        self._set_changed_flag()
        self.figureRemoved.emit(figure)

    def remove_all_figures(self) -> None:
        self._figures.clear()
        self._set_changed_flag()
        self.allFiguresRemoved.emit()

    @property
    def labels(self) -> list['LabelModel']:
        return self._labels.copy()

    def add_label(self, label: 'LabelModel') -> None:
        self._labels.append(label)
        self._set_changed_flag()
        self.labelAdded.emit(label)

    def remove_label(self, label: 'LabelModel') -> None:
        self._labels.remove(label)
        self._set_changed_flag()
        self.labelRemoved.emit(label)

    def remove_all_labels(self) -> None:
        self._labels.clear()
        self._set_changed_flag()
        self.allLabelsRemoved.emit()

    @property
    def pencil_lines(self) -> list['PencilLineModel']:
        return self._pencil_lines.copy()

    def add_pencil_lines(self, pencil_lines: list['PencilLineModel']) -> None:
        self._pencil_lines.extend(pencil_lines)
        self._set_changed_flag()
        self.pencilLinesAdded.emit(pencil_lines)

    def remove_pencil_lines(self, pencil_line_models: list['PencilLineModel']) -> None:
        self._pencil_lines = list(set(self._pencil_lines) - set(pencil_line_models))
        # self._set_changed_flag()
        self.pencilLinesRemoved.emit(pencil_line_models)

    def remove_all_pencil_lines(self) -> None:
        self._pencil_lines.clear()
        self._set_changed_flag()
        self.allPencilLinesRemoved.emit()

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'name': self._name, 'note': self._note,
                'view_point_x': self._view_point_x, 'view_point_y': self._view_point_y, 'zoom': self._zoom,
                'first_team': self._first_team, 'second_team': self._second_team,
                'first_team_position': self._first_team_position,
                'players': list(),
                'figures': list(),
                'labels': list(),
                'pencil_lines': list()}

    def __repr__(self) -> str:
        return f'\n\t\t<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self._uuid}; name: {self._name}; zoom: {self._zoom}; ' \
               f'view_point_x: {self._view_point_x}, view_point_y: {self._view_point_y}; ' \
               f'first_team: {self._first_team}; second_team: {self._second_team}; ' \
               f'first_team_position: {self._first_team_position}; note: {self._note}; ' \
               f'\n\t\t\tfigures: {self._figures}' \
               f'\n\t\t\tlabels: {self._labels}' \
               f'\n\t\t\tpencil_lines: {self._pencil_lines}' \
               f'\n\t\t\tfirst_team_players: {self._first_team_players}>' \
               f'\n\t\t\tsecond_team_players: {self._second_team_players}>' \
               f'\n\t\t\tadditional_player: {self._additional_player}>'
