from typing import TYPE_CHECKING, Optional
from itertools import chain
from uuid import UUID, uuid4

from PySide6.QtCore import QObject, Signal

from Config.Enums import StorageType

if TYPE_CHECKING:
    from Config.Enums import TeamType
    from .figure_model import FigureModel
    from .label_model import LabelModel
    from .pencil_line_model import PencilLineModel
    from .player_model import PlayerModel


class SchemeModel(QObject):
    nameChanged = Signal(str)
    noteChanged = Signal(str)
    zoomChanged = Signal(int)
    firstTeamAdded = Signal(object, object, bool)  # list[PlayerModel], _first_team, has_additional_player()
    firstTeamRemoved = Signal()
    secondTeamAdded = Signal(object)  # list[PlayerModel]
    secondTeamRemoved = Signal()
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

    def __init__(self, add_deleted_item_ids_func: callable, name: str, view_point_x: int, view_point_y: int,
                 note: str = '', zoom: int = 60,
                 first_team: Optional['TeamType'] = None, second_team: Optional['TeamType'] = None,
                 first_team_position: Optional[int] = None, uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__()
        self._add_deleted_item_ids_func = add_deleted_item_ids_func  # Метод из PlaybookModel
        self._name = name
        self._note = note
        self._view_point_x = view_point_x
        self._view_point_y = view_point_y
        self._zoom = zoom
        self._first_team = first_team
        self._second_team = second_team
        self._first_team_position = first_team_position
        self._figures: list['FigureModel'] = list()
        self._labels: list['LabelModel'] = list()
        self._pencil_lines: list['PencilLineModel'] = list()
        self._first_team_players: list['PlayerModel'] = list()
        self._additional_player: Optional['PlayerModel'] = None
        self._second_team_players: list['PlayerModel'] = list()
        self._uuid = uuid if uuid else uuid4()
        self._id_local_db = id_local_db
        self._id_api = id_api

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

    @first_team.setter
    def first_team(self, first_team: 'TeamType') -> None:
        self._first_team = first_team

    @property
    def second_team(self) -> Optional['TeamType']:
        return self._second_team

    @second_team.setter
    def second_team(self, second_team: 'TeamType') -> None:
        self._second_team = second_team

    @property
    def first_team_position(self) -> Optional[int]:
        return self._first_team_position

    @first_team_position.setter
    def first_team_position(self, position: int) -> None:
        self._first_team_position = position

    @property
    def first_team_players(self) -> list['PlayerModel']:
        return self._first_team_players.copy()

    def add_first_team_players(self, player_models_lst: list['PlayerModel'], team_type: 'TeamType', first_team_position: int) -> None:
        self._first_team_players.extend(player_models_lst)
        self.first_team = team_type
        self.first_team_position = first_team_position
        self.firstTeamAdded.emit(player_models_lst, self._first_team, self.has_additional_player())

    @property
    def second_team_players(self) -> list['PlayerModel']:
        return self._second_team_players.copy()

    def add_second_team_players(self, player_models_lst: list['PlayerModel'], team_type: 'TeamType') -> None:
        self._second_team_players.extend(player_models_lst)
        self.second_team = team_type
        self.secondTeamAdded.emit(player_models_lst)

    @property
    def additional_player(self) -> Optional['PlayerModel']:
        return self._additional_player

    @additional_player.setter
    def additional_player(self, player_model: 'PlayerModel') -> None:
        self._additional_player = player_model
        self.additionalPlayerAdded.emit(self.additional_player)

    def has_additional_player(self) -> bool:
        if self._additional_player:
            return True
        return False

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
        self.first_team = None
        self.first_team_position = None
        self.firstTeamRemoved.emit()
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
        self.second_team = None
        self.secondTeamRemoved.emit()
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
        if self.first_team:
            first_team_deleted_item_ids = self.remove_first_team_players()
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
