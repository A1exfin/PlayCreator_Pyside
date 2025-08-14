from typing import TYPE_CHECKING, Optional
from itertools import chain
from uuid import UUID, uuid4

from PySide6.QtCore import QObject, Signal

from Config.Enums import StorageType, PlaybookType, TeamType

if TYPE_CHECKING:
    from .figure_model import FigureModel
    from .label_model import LabelModel
    from .pencil_line_model import PencilLineModel
    from .player_model import PlayerModel


class SchemeModel(QObject):
    nameChanged = Signal(str)
    noteChanged = Signal(str)
    zoomChanged = Signal(int)
    firstTeamPlayerAdded = Signal(object)  # PlayerModel
    firstTeamPlayersRemoved = Signal()
    firstTeamStateChanged = Signal(object, object)  # TeamType, self._first_team_position
    # object из-за того что None автоматически преобразуется в 0 при типе int
    secondTeamPlayerAdded = Signal(object)  # PlayerModel
    secondTeamPlayersRemoved = Signal()
    secondTeamStateChanged = Signal(object)  # TeamType
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

    def __init__(self, add_deleted_item_ids_func: callable, playbook_type: 'PlaybookType',
                 name: str, view_point_x: int, view_point_y: int, note: str = '', zoom: int = 60,
                 first_team: Optional['TeamType'] = None, second_team: Optional['TeamType'] = None,
                 first_team_position: Optional[int] = None, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__()
        self._add_deleted_item_ids_func = add_deleted_item_ids_func  # Метод из PlaybookModel
        self._playbook_type = playbook_type
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
        self._uuid = uuid if uuid else uuid4()
        self._id_local_db = id_local_db
        self._id_api = id_api
        self.set_first_team_state(first_team, first_team_position)
        self.set_second_team_state(second_team)

    @property
    def id_local_db(self) -> int:
        return self._id_local_db

    @id_local_db.setter
    def id_local_db(self, value: int) -> None:
        self._id_local_db = value

    @property
    def id_api(self) -> int:
        return self._id_api

    @id_api.setter
    def id_api(self, value: int) -> None:
        self._id_api = value

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()
        self._set_scheme_items_new_uuid()

    def _set_scheme_items_new_uuid(self) -> None:
        for item_model in chain(
                self._first_team_players, self._second_team_players, [self._additional_player],
                self._figures, self._labels, self._pencil_lines
        ):
            if item_model:
                item_model.set_new_uuid()

    def reset_id(self, storage_type: 'StorageType') -> None:
        if hasattr(self, f'_id_{storage_type.value}'):
            setattr(self, f'_id_{storage_type.value}', None)
        self._reset_scheme_items_id(storage_type)

    def _reset_scheme_items_id(self, storage_type: 'StorageType') -> None:
        for item_model in chain(
                self._first_team_players, self._second_team_players, [self._additional_player],
                self._figures, self._labels, self._pencil_lines
        ):
            if item_model:
                item_model.reset_id(storage_type)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        self.nameChanged.emit(name)

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, note: str) -> None:
        self._note = note
        self.noteChanged.emit(note)

    @property
    def view_point_x(self) -> int:
        return self._view_point_x

    @view_point_x.setter
    def view_point_x(self, x: int) -> None:
        self._view_point_x = x

    @property
    def view_point_y(self) -> int:
        return self._view_point_y

    @view_point_y.setter
    def view_point_y(self, y: int) -> None:
        self._view_point_y = y

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    def zoom(self, value: int) -> None:
        if 0 <= value <= 200:
            self._zoom = value
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
        if first_team_type and self._playbook_type is PlaybookType.FOOTBALL and \
                first_team_type not in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
            raise ValueError(f'Неверный тип первой команды - {first_team_type.name.capitalize()}.')
        if first_team_type and self._playbook_type is PlaybookType.FLAG and first_team_type is not TeamType.OFFENCE:
            raise ValueError(f'Неверный тип первой команды - {first_team_type.name.capitalize()}.')
        if first_team_position and self._playbook_type is PlaybookType.FOOTBALL and first_team_position > 100:
            raise ValueError('Позиция первой команды не может превышать 100 ярдов.')
        if first_team_position and self._playbook_type is PlaybookType.FLAG and first_team_position > 50:
            raise ValueError('Позиция первой команды не может превышать 50 ярдов.')
        self._first_team = first_team_type
        self._first_team_position = first_team_position
        self.firstTeamStateChanged.emit(self._first_team, self._first_team_position)

    def add_first_team_player(self, player_model: 'PlayerModel') -> None:
        if self._playbook_type is PlaybookType.FOOTBALL and \
                player_model.team_type not in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
            raise ValueError(f'Неверный тип игрока первой команды - {player_model.team_type.name.capitalize()}.')
        if self._playbook_type is PlaybookType.FLAG and player_model.team_type is not TeamType.OFFENCE:
            raise ValueError(f'Неверный тип игрока первой команды - {player_model.team_type.name.capitalize()}.')
        if self._playbook_type is PlaybookType.FOOTBALL and len(self._first_team_players) >= 11:
            raise ValueError('Количество игроков первой команды не должно превышать 11.')
        if self._playbook_type is PlaybookType.FLAG and len(self._first_team_players) >= 5:
            raise ValueError('Количество игроков первой команды не должно превышать 5.')
        self._first_team_players.append(player_model)
        self.firstTeamPlayerAdded.emit(player_model)

    @property
    def second_team_players(self) -> list['PlayerModel']:
        return self._second_team_players.copy()

    def set_second_team_state(self, second_team_type: Optional['TeamType']) -> None:
        if second_team_type and self._playbook_type is PlaybookType.FOOTBALL and second_team_type not in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
            raise ValueError(f'Неверный тип второй команды - {second_team_type.name.capitalize()}.')
        if second_team_type and self._playbook_type is PlaybookType.FLAG and second_team_type is not TeamType.DEFENCE:
            raise ValueError(f'Неверный тип второй команды - {second_team_type.name.capitalize()}.')
        self._second_team = second_team_type
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
            raise ValueError('Количество игроков второй команды не должно превышать 11.')
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
        self.additionalPlayerAdded.emit(self.additional_player)

    def remove_first_team_players(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        for player in self._first_team_players:
            if player.id_local_db:
                self._add_deleted_item_ids_func('players', StorageType.LOCAL_DB, player.id_local_db)
                deleted_item_ids[StorageType.LOCAL_DB].append(player.id_local_db)
            if player.id_api:
                self._add_deleted_item_ids_func('players', StorageType.API, player.id_api)
                deleted_item_ids[StorageType.API].append(player.id_api)
        self._first_team_players.clear()
        self.set_first_team_state(None, None)
        self.firstTeamPlayersRemoved.emit()
        return deleted_item_ids

    def remove_second_team_players(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        for player in self._second_team_players:
            if player.id_local_db:
                self._add_deleted_item_ids_func('players', StorageType.LOCAL_DB, player.id_local_db)
                deleted_item_ids[StorageType.LOCAL_DB].append(player.id_local_db)
            if player.id_api:
                self._add_deleted_item_ids_func('players', StorageType.API, player.id_api)
                deleted_item_ids[StorageType.API].append(player.id_api)
        self._second_team_players.clear()
        self.set_second_team_state(None)
        self.secondTeamPlayersRemoved.emit()
        return deleted_item_ids

    def remove_additional_player(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        if self._additional_player.id_local_db:
            self._add_deleted_item_ids_func('players', StorageType.LOCAL_DB, self._additional_player.id_local_db)
            deleted_item_ids[StorageType.LOCAL_DB].append(self._additional_player.id_local_db)
        if self._additional_player.id_api:
            self._add_deleted_item_ids_func('players', StorageType.API, self._additional_player.id_api)
            deleted_item_ids[StorageType.API].append(self._additional_player.id_api)
        self._additional_player = None
        self.additionalPlayerRemoved.emit()
        return deleted_item_ids

    def remove_all_players(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        # Порядок удаления команд важен для правильной установки GUI основного окна. Не менять.
        if self._additional_player:
            additional_player_deleted_item_ids = self.remove_additional_player()
        if self.second_team:
            second_team_deleted_item_ids = self.remove_second_team_players()
            self.set_second_team_state(None)
        if self.first_team:
            first_team_deleted_item_ids = self.remove_first_team_players()
            self.set_first_team_state(None, None)
        for storage_type in deleted_item_ids:
            try:
                deleted_item_ids[storage_type].extend(first_team_deleted_item_ids[storage_type])
                deleted_item_ids[storage_type].extend(second_team_deleted_item_ids[storage_type])
                deleted_item_ids[storage_type].extend(additional_player_deleted_item_ids[storage_type])
            except UnboundLocalError:
                pass
        return deleted_item_ids

    @property
    def figures(self) -> list['FigureModel']:
        return self._figures.copy()

    def add_figure(self, figure: 'FigureModel') -> None:
        self._figures.append(figure)
        self.figureAdded.emit(figure)

    def remove_figure(self, figure: 'FigureModel') -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        if figure.id_local_db:
            self._add_deleted_item_ids_func('figures', StorageType.LOCAL_DB, figure.id_local_db)
            deleted_item_ids[StorageType.LOCAL_DB].append(figure.id_local_db)
        if figure.id_api:
            self._add_deleted_item_ids_func('figures', StorageType.API, figure.id_api)
            deleted_item_ids[StorageType.API].append(figure.id_api)
        self._figures.remove(figure)
        self.figureRemoved.emit(figure)
        return deleted_item_ids

    def remove_all_figures(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        for figure in self._figures:
            if figure.id_local_db:
                self._add_deleted_item_ids_func('figures', StorageType.LOCAL_DB, figure.id_local_db)
                deleted_item_ids[StorageType.LOCAL_DB].append(figure.id_local_db)
            if figure.id_api:
                self._add_deleted_item_ids_func('figures', StorageType.API, figure.id_api)
                deleted_item_ids[StorageType.API].append(figure.id_api)
        self._figures.clear()
        self.allFiguresRemoved.emit()
        return deleted_item_ids

    @property
    def labels(self) -> list['LabelModel']:
        return self._labels.copy()

    def add_label(self, label: 'LabelModel') -> None:
        self._labels.append(label)
        self.labelAdded.emit(label)

    def remove_label(self, label: 'LabelModel') -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        if label.id_local_db:
            self._add_deleted_item_ids_func('labels', StorageType.LOCAL_DB, label.id_local_db)
            deleted_item_ids[StorageType.LOCAL_DB].append(label.id_local_db)
        if label.id_api:
            self._add_deleted_item_ids_func('labels', StorageType.API, label.id_api)
            deleted_item_ids[StorageType.API].append(label.id_api)
        self._labels.remove(label)
        self.labelRemoved.emit(label)
        return deleted_item_ids

    def remove_all_labels(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        for label in self._labels:
            if label.id_local_db:
                self._add_deleted_item_ids_func('labels', StorageType.LOCAL_DB, label.id_local_db)
                deleted_item_ids[StorageType.LOCAL_DB].append(label.id_local_db)
            if label.id_api:
                self._add_deleted_item_ids_func('labels', StorageType.API, label.id_api)
                deleted_item_ids[StorageType.API].append(label.id_api)
        self._labels.clear()
        self.allLabelsRemoved.emit()
        return deleted_item_ids

    @property
    def pencil_lines(self) -> list['PencilLineModel']:
        return self._pencil_lines.copy()

    def add_pencil_lines(self, pencil_lines: list['PencilLineModel']) -> None:
        self._pencil_lines.extend(pencil_lines)
        self.pencilLinesAdded.emit(pencil_lines)

    def remove_pencil_lines(self, pencil_line_models: list['PencilLineModel']) -> None:
        '''Не добавляются id удалённых итемов потому что этот метод применяется только для undo-метода в
         классе команды размещения линий карандаша.'''
        self._pencil_lines = list(set(self._pencil_lines) - set(pencil_line_models))
        self.pencilLinesRemoved.emit(pencil_line_models)

    def remove_all_pencil_lines(self) -> dict['StorageType', list[int]]:
        deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        for pencil_line in self._pencil_lines:
            if pencil_line.id_local_db:
                self._add_deleted_item_ids_func('pencil_lines', StorageType.LOCAL_DB, pencil_line.id_local_db)
                deleted_item_ids[StorageType.LOCAL_DB].append(pencil_line.id_local_db)
            if pencil_line.id_api:
                self._add_deleted_item_ids_func('pencil_lines', StorageType.API, pencil_line.id_api)
                deleted_item_ids[StorageType.API].append(pencil_line.id_api)
        self._pencil_lines.clear()
        self.allPencilLinesRemoved.emit()
        return deleted_item_ids

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
