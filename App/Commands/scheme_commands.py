from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field

from PySide6.QtGui import QUndoCommand

import Config
from Models import PlayerModel, FigureModel, LabelModel, PencilLineModel, ActionModel, ActionLineModel, FinalActionModel
from Config.Enums import TeamType, PlaybookType, StorageType

if TYPE_CHECKING:
    from Config.Enums import SymbolType
    from Models import SchemeModel

__all__ = ('PlaceFirstTeamCommand', 'PlaceSecondTeamCommand', 'RemoveSecondTeamCommand',
           'PlaceAdditionalPlayerCommand', 'RemoveAdditionalOffencePlayerCommand', 'RemoveAllPlayersCommand',
           'ChangeSecondTeamSymbolsCommand', 'RemoveAllActionsCommand',
           'PlaceFigureCommand', 'RemoveFigureCommand', 'RemoveAllFiguresCommand',
           'PlacePencilLinesCommand', 'RemovePencilLinesCommand',
           'PlaceLabelCommand', 'RemoveLabelCommand', 'RemoveAllLabelsCommand')


@dataclass
class PlayerActionsMapper:
    player: 'PlayerModel'
    action_models_dict: dict[int, 'ActionModel'] = field(default_factory=dict)
    lines_dict: dict[int, list['ActionLineModel']] = field(default_factory=dict)
    final_actions_dict: dict[int, list['FinalActionModel']] = field(default_factory=dict)


class PlaceFirstTeamCommand(QUndoCommand):
    def __init__(self, add_deleted_item_ids_func: callable, scheme_model: 'SchemeModel', playbook_type: 'PlaybookType',
                 team_type: 'TeamType', players_data: tuple[tuple], first_team_position: int, yards_to_top_border: int):
        super().__init__('Размещение игроков первой команды.')
        self._team_type = team_type
        self._scheme_model = scheme_model
        self._first_team_position = first_team_position
        self._players_lst = self._get_player_models(add_deleted_item_ids_func, playbook_type,
                                                    yards_to_top_border, players_data)

    def _get_player_models(self, add_deleted_item_ids_func: callable, playbook_type: 'PlaybookType',
                           yards_to_top_border: int, players_data: tuple[tuple]) -> list['PlayerModel']:
        player_models_lst = []
        vertical_one_yard = getattr(Config, f'{playbook_type.name}_field_data'.lower()).vertical_one_yard
        for i, player_data in enumerate(players_data):
            team_type, position, text, fill_type, x, y = player_data
            if team_type is TeamType.PUNT and i == 10 and yards_to_top_border >= 105 * vertical_one_yard:
                player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                           118 * vertical_one_yard, fill_type=fill_type)
            else:
                player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                           y + yards_to_top_border, fill_type=fill_type)
            player_models_lst.append(player_model)
        return player_models_lst

    def redo(self) -> None:
        self._scheme_model.add_first_team_players(self._players_lst, self._team_type, self._first_team_position)

    def undo(self) -> None:
        self._scheme_model.remove_first_team_players()


class PlaceSecondTeamCommand(QUndoCommand):
    def __init__(self, add_deleted_item_ids_func: callable, scheme_model: 'SchemeModel', playbook_type: 'PlaybookType',
                 team_type: 'TeamType', players_data: tuple[tuple], yards_to_top_border: int):
        super().__init__('Размещение игроков второй команды.')
        self._team_type = team_type
        self._scheme_model = scheme_model
        self._players_lst = self._get_player_models(add_deleted_item_ids_func, playbook_type,
                                                    yards_to_top_border, players_data)

    def _get_player_models(self, add_deleted_item_ids_func: callable, playbook_type: 'PlaybookType',
                           yards_to_top_border: int, players_data: tuple[tuple]) -> list['PlayerModel']:
        player_models_lst = []
        vertical_one_yard = getattr(Config, f'{playbook_type.name}_field_data'.lower()).vertical_one_yard
        for i, player_data in enumerate(players_data):
            team_type, position, text, symbol_type, x, y = player_data
            if playbook_type is PlaybookType.FOOTBALL:
                if team_type in (TeamType.PUNT_RET, TeamType.KICK_RET) and i == 10:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x, y,
                                               symbol_type=symbol_type)
                elif team_type is TeamType.FIELD_GOAL_DEF and i == 10 and \
                        yards_to_top_border > vertical_one_yard * 11:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                               vertical_one_yard * 4, symbol_type=symbol_type)
                elif team_type is TeamType.DEFENCE and i == 10 and \
                        yards_to_top_border < vertical_one_yard * 13:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                               y + yards_to_top_border + 3 * vertical_one_yard,
                                               symbol_type=symbol_type)
                elif team_type is TeamType.KICK_RET and 4 < i <= 7 and \
                        yards_to_top_border == vertical_one_yard * 85:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                               y + yards_to_top_border - vertical_one_yard * 5,
                                               symbol_type=symbol_type)
                elif team_type is TeamType.KICK_RET and 7 < i <= 9 and \
                        yards_to_top_border == vertical_one_yard * 85:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                               y + yards_to_top_border - vertical_one_yard * 10,
                                               symbol_type=symbol_type)
                else:
                    player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                               y + yards_to_top_border, symbol_type=symbol_type)
            else:
                player_model = PlayerModel(add_deleted_item_ids_func, team_type, position, text, x,
                                           y + yards_to_top_border, symbol_type=symbol_type)
            player_models_lst.append(player_model)
        return player_models_lst

    def redo(self) -> None:
        self._scheme_model.add_second_team_players(self._players_lst, self._team_type)

    def undo(self) -> None:
        self._scheme_model.remove_second_team_players()


class PlaceAdditionalPlayerCommand(QUndoCommand):
    def __init__(self, add_deleted_item_ids_func: callable, scheme_model: 'SchemeModel',
                 player_data: tuple, yards_to_top_border: int):
        super().__init__('Размещение дополнительного игрока нападения.')
        self._scheme_model = scheme_model
        self._yards_to_top_border = yards_to_top_border
        self._additional_player = self._get_player_model(add_deleted_item_ids_func, yards_to_top_border, player_data)

    def _get_player_model(self, add_deleted_item_ids_func: callable, yards_to_top_border: int,
                          player_data: tuple) -> 'PlayerModel':
        team_type, position, text, fill_type, x, y = player_data
        return PlayerModel(add_deleted_item_ids_func, team_type, position, text, x, y + yards_to_top_border, fill_type=fill_type)

    def redo(self) -> None:
        self._scheme_model.additional_player = self._additional_player

    def undo(self) -> None:
        self._scheme_model.remove_additional_player()


class RemoveSecondTeamCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление игроков второй команды.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._players_lst = self._scheme_model.second_team_players
        self._deleted_team_type = self._scheme_model.second_team
        self._player_actions_mappers: list['PlayerActionsMapper'] = []
        self._deleted_player_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        self._deleted_action_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}

    def redo(self) -> None:
        for player_model in self._scheme_model.second_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._player_actions_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.lines_dict[i] = action_model.lines
                player_actions_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = player_model.remove_action(action_model)
                self._deleted_action_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_action_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        self._deleted_player_ids = self._scheme_model.remove_second_team_players()

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_player_ids.items():
            self._remove_deleted_item_ids_func('players', storage_type, deleted_ids)
        for storage_type, deleted_ids in self._deleted_action_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)
        self._scheme_model.add_second_team_players(self._players_lst, self._deleted_team_type)
        for player_actions_mapper in self._player_actions_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.lines_dict[i],
                                              player_actions_mapper.final_actions_dict[i])
        self._player_actions_mappers.clear()
        self._deleted_player_ids[StorageType.LOCAL_DB].clear()
        self._deleted_player_ids[StorageType.API].clear()
        self._deleted_action_ids[StorageType.LOCAL_DB].clear()
        self._deleted_action_ids[StorageType.API].clear()


class RemoveAdditionalOffencePlayerCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление дополнительного игрока нападения.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._additional_player = self._scheme_model.additional_player
        self._additional_player_actions_mapper: Optional['PlayerActionsMapper'] = None
        self._deleted_player_ids = None
        self._deleted_action_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}

    def redo(self) -> None:
        self._additional_player_actions_mapper = PlayerActionsMapper(self._additional_player)
        for i, action_model in enumerate(self._additional_player.actions):
            self._additional_player_actions_mapper.action_models_dict[i] = action_model
            self._additional_player_actions_mapper.lines_dict[i] = action_model.lines
            self._additional_player_actions_mapper.final_actions_dict[i] = action_model.final_actions
            action_model.remove_action_parts(action_model.lines, action_model.final_actions)
            deleted_item_ids = self._additional_player.remove_action(action_model)
            self._deleted_action_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
            self._deleted_action_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        self._deleted_player_ids = self._scheme_model.remove_additional_player()

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_player_ids.items():
            self._remove_deleted_item_ids_func('players', storage_type, deleted_ids)
        for storage_type, deleted_ids in self._deleted_action_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)
        self._scheme_model.additional_player = self._additional_player
        for i, action_model in self._additional_player_actions_mapper.action_models_dict.items():
            self._additional_player.add_action(action_model)
            action_model.add_action_parts(self._additional_player_actions_mapper.lines_dict[i],
                                          self._additional_player_actions_mapper.final_actions_dict[i])
        self._additional_player_actions_mapper = None
        self._deleted_player_ids[StorageType.LOCAL_DB].clear()
        self._deleted_player_ids[StorageType.API].clear()
        self._deleted_action_ids[StorageType.LOCAL_DB].clear()
        self._deleted_action_ids[StorageType.API].clear()


class RemoveAllPlayersCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех игроков.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._first_team_position = self._scheme_model.first_team_position
        self._first_team_players_lst = self._scheme_model.first_team_players
        self._first_team_players_mappers: list['PlayerActionsMapper'] = []
        self._second_team_players_lst = self._scheme_model.second_team_players
        self._second_team_players_mappers: list['PlayerActionsMapper'] = []
        self._additional_player = self._scheme_model.additional_player
        self._additional_player_mapper: Optional['PlayerActionsMapper'] = None
        self._deleted_first_team_type = self._scheme_model.first_team
        self._deleted_second_team_type = self._scheme_model.second_team
        self._deleted_player_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}
        self._deleted_action_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}

    def redo(self) -> None:
        for player_model in self._first_team_players_lst:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._first_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.lines_dict[i] = action_model.lines
                player_actions_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = player_model.remove_action(action_model)
                self._deleted_action_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_action_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        for player_model in self._second_team_players_lst:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._second_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.lines_dict[i] = action_model.lines
                player_actions_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = player_model.remove_action(action_model)
                self._deleted_action_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_action_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        if self._additional_player:
            self._additional_player_mapper = PlayerActionsMapper(self._additional_player)
            for i, action_model in enumerate(self._additional_player.actions):
                self._additional_player_mapper.action_models_dict[i] = action_model
                self._additional_player_mapper.lines_dict[i] = action_model.lines
                self._additional_player_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = self._additional_player.remove_action(action_model)
                self._deleted_action_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_action_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        self._deleted_player_ids = self._scheme_model.remove_all_players()

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_player_ids.items():
            self._remove_deleted_item_ids_func('players', storage_type, deleted_ids)
        for storage_type, deleted_ids in self._deleted_action_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)
        if self._first_team_players_lst:
            self._scheme_model.add_first_team_players(self._first_team_players_lst, self._deleted_first_team_type, self._first_team_position)
            for player_actions_mapper in self._first_team_players_mappers:
                for i, action_model in player_actions_mapper.action_models_dict.items():
                    player_actions_mapper.player.add_action(action_model)
                    action_model.add_action_parts(player_actions_mapper.lines_dict[i],
                                                  player_actions_mapper.final_actions_dict[i])
        if self._second_team_players_lst:
            self._scheme_model.add_second_team_players(self._second_team_players_lst, self._deleted_second_team_type)
            for player_actions_mapper in self._second_team_players_mappers:
                for i, action_model in player_actions_mapper.action_models_dict.items():
                    player_actions_mapper.player.add_action(action_model)
                    action_model.add_action_parts(player_actions_mapper.lines_dict[i],
                                                  player_actions_mapper.final_actions_dict[i])
        if self._additional_player:
            self._scheme_model.additional_player = self._additional_player
            for i, action_model in self._additional_player_mapper.action_models_dict.items():
                self._additional_player_mapper.player.add_action(action_model)
                action_model.add_action_parts(self._additional_player_mapper.lines_dict[i],
                                              self._additional_player_mapper.final_actions_dict[i])
        self._first_team_players_mappers.clear()
        self._second_team_players_mappers.clear()
        self._additional_player_mapper = None
        self._deleted_player_ids[StorageType.LOCAL_DB].clear()
        self._deleted_player_ids[StorageType.API].clear()
        self._deleted_action_ids[StorageType.LOCAL_DB].clear()
        self._deleted_action_ids[StorageType.API].clear()


class PlaceFigureCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', figure_data: dict):
        super().__init__('Размещение фигуры')
        self._scheme_model = scheme_model
        self._figure_model = FigureModel(**figure_data)

    def redo(self) -> None:
        self._scheme_model.add_figure(self._figure_model)

    def undo(self) -> None:
        self._scheme_model.remove_figure(self._figure_model)


class RemoveFigureCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel', figure_model: 'FigureModel'):
        super().__init__('Удаление фигуры.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._figure_model = figure_model
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._scheme_model.remove_figure(self._figure_model)

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('figures', storage_type, deleted_ids)
        self._scheme_model.add_figure(self._figure_model)


class RemoveAllFiguresCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех фигур.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._figures_models = scheme_model.figures
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._scheme_model.remove_all_figures()

    def undo(self) -> None:
        for figure_model in self._figures_models:
            self._scheme_model.add_figure(figure_model)
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('figures', storage_type, deleted_ids)


class PlacePencilLinesCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', pencil_lines_data: list[dict]):
        super().__init__('Размещение линий карандаша.')
        self._scheme_model = scheme_model
        self._pencil_line_models = [PencilLineModel(**pencil_line_data) for pencil_line_data in pencil_lines_data]

    def redo(self) -> None:
        self._scheme_model.add_pencil_lines(self._pencil_line_models)

    def undo(self) -> None:
        self._scheme_model.remove_pencil_lines(self._pencil_line_models)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, PlacePencilLinesCommand):
            return False
        if other._scheme_model is not self._scheme_model:
            return False
        self._pencil_line_models.extend(other._pencil_line_models)
        return True


class RemovePencilLinesCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление линий карандаша.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._pencil_line_models = self._scheme_model.pencil_lines
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._scheme_model.remove_all_pencil_lines()

    def undo(self) -> None:
        self._scheme_model.add_pencil_lines(self._pencil_line_models)
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('pencil_lines', storage_type, deleted_ids)


class PlaceLabelCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', label_data: dict):
        super().__init__('Размещение надписи.')
        self._scheme_model = scheme_model
        self._label_model = LabelModel(**label_data)

    def redo(self) -> None:
        self._scheme_model.add_label(self._label_model)

    def undo(self) -> None:
        self._scheme_model.remove_label(self._label_model)


class RemoveLabelCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel', label_model: 'LabelModel'):
        super().__init__('Удаление надписи.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._label_model = label_model
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._scheme_model.remove_label(self._label_model)

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('labels', storage_type, deleted_ids)
        self._scheme_model.add_label(self._label_model)


class RemoveAllLabelsCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех надписей.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._label_models = self._scheme_model.labels
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._scheme_model.remove_all_labels()

    def undo(self) -> None:
        for label_model in self._label_models:
            self._scheme_model.add_label(label_model)
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('labels', storage_type, deleted_ids)


class ChangeSecondTeamSymbolsCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', new_symbol_type: 'SymbolType'):
        super().__init__('Изменение символов игроков второй команды.')
        self._scheme_model = scheme_model
        self._new_symbol_type = new_symbol_type
        self._second_team_player_models = self._scheme_model.second_team_players
        self._second_team_last_symbols_dict: dict[int, 'SymbolType'] = {}  # {model_id: SymbolType}
        self._get_second_team_symbols(scheme_model)

    def _get_second_team_symbols(self, scheme_model: 'SchemeModel') -> None:
        for player_model in scheme_model.second_team_players:
            self._second_team_last_symbols_dict[id(player_model)] = player_model.symbol_type

    def redo(self) -> None:
        for player_model in self._second_team_player_models:
            player_model.set_player_style(player_model.text, player_model.text_color, player_model.player_color, None,
                                          self._new_symbol_type)

    def undo(self) -> None:
        for player_model in self._second_team_player_models:
            player_model.set_player_style(player_model.text, player_model.text_color, player_model.player_color, None,
                                          self._second_team_last_symbols_dict[id(player_model)])

    # def id(self) -> int:
    #     return 1

    # def mergeWith(self, other: 'QUndoCommand') -> bool:
    #     if not isinstance(other, ChangeSecondTeamSymbolsCommand):
    #         return False
    #     if other._scheme_model is not self._scheme_model:
    #         return False
    #     self._new_symbol_type = other._new_symbol_type
    #     return True


class RemoveAllActionsCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех действий игроков.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._scheme_model = scheme_model
        self._first_team_players_mappers: list['PlayerActionsMapper'] = []
        self._second_team_players_mappers: list['PlayerActionsMapper'] = []
        self._additional_player_mapper: Optional['PlayerActionsMapper'] = None
        self._deleted_item_ids = {StorageType.LOCAL_DB: [], StorageType.API: []}

    def redo(self) -> None:
        for player_model in self._scheme_model.first_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._first_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.lines_dict[i] = action_model.lines
                player_actions_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = player_model.remove_action(action_model)
                self._deleted_item_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_item_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        for player_model in self._scheme_model.second_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._second_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.lines_dict[i] = action_model.lines
                player_actions_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = player_model.remove_action(action_model)
                self._deleted_item_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_item_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])
        if self._scheme_model.has_additional_player():
            self._additional_player_mapper = PlayerActionsMapper(self._scheme_model.additional_player)
            for i, action_model in enumerate(self._scheme_model.additional_player.actions):
                self._additional_player_mapper.action_models_dict[i] = action_model
                self._additional_player_mapper.lines_dict[i] = action_model.lines
                self._additional_player_mapper.final_actions_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.lines, action_model.final_actions)
                deleted_item_ids = self._scheme_model.additional_player.remove_action(action_model)
                self._deleted_item_ids[StorageType.LOCAL_DB].extend(deleted_item_ids[StorageType.LOCAL_DB])
                self._deleted_item_ids[StorageType.API].extend(deleted_item_ids[StorageType.API])

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)
        for player_actions_mapper in self._first_team_players_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.lines_dict[i],
                                              player_actions_mapper.final_actions_dict[i])
        self._first_team_players_mappers.clear()
        for player_actions_mapper in self._second_team_players_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.lines_dict[i],
                                              player_actions_mapper.final_actions_dict[i])
        self._second_team_players_mappers.clear()
        if self._additional_player_mapper:
            for i, action_model in self._additional_player_mapper.action_models_dict.items():
                self._additional_player_mapper.player.add_action(action_model)
                action_model.add_action_parts(self._additional_player_mapper.lines_dict[i],
                                              self._additional_player_mapper.final_actions_dict[i])
            self._additional_player_mapper = None
        self._deleted_item_ids[StorageType.LOCAL_DB].clear()
        self._deleted_item_ids[StorageType.API].clear()
