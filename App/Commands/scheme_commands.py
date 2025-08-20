from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field

from PySide6.QtGui import QUndoCommand

import Config
from View_Models import PlayerModel, FigureModel, LabelModel, PencilLineModel, ActionModel, ActionLineModel, FinalActionModel
from Config.Enums import TeamType, StorageType

if TYPE_CHECKING:
    from Config.Enums import SymbolType
    from View_Models import SchemeModel
    from View_Models.Other import DeletionObserver

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
    action_line_models_dict: dict[int, list['ActionLineModel']] = field(default_factory=dict)
    final_action_models_dict: dict[int, list['FinalActionModel']] = field(default_factory=dict)


class PlaceFirstTeamCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', first_team_player_models_list: list['PlayerModel'],
                 team_type: 'TeamType', first_team_position: int):
        super().__init__('Размещение игроков первой команды.')
        self._scheme_model = scheme_model
        self._players_lst = first_team_player_models_list
        self._team_type = team_type
        self._first_team_position = first_team_position

    def redo(self) -> None:
        for player_model in self._players_lst:
            self._scheme_model.add_first_team_player(player_model)
        self._scheme_model.set_first_team_state(self._team_type, self._first_team_position)

    def undo(self) -> None:
        self._scheme_model.remove_first_team_players()


class PlaceSecondTeamCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', second_team_player_models_list: list['PlayerModel'],
                 team_type: 'TeamType'):
        super().__init__('Размещение игроков второй команды.')
        self._scheme_model = scheme_model
        self._players_lst = second_team_player_models_list
        self._team_type = team_type

    def redo(self) -> None:
        for player_model in self._players_lst:
            self._scheme_model.add_second_team_player(player_model)
        self._scheme_model.set_second_team_state(self._team_type)

    def undo(self) -> None:
        self._scheme_model.remove_second_team_players()


class PlaceAdditionalPlayerCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', additional_player_model: 'PlayerModel'):
        super().__init__('Размещение дополнительного игрока нападения.')
        self._scheme_model = scheme_model
        self._additional_player_model = additional_player_model

    def redo(self) -> None:
        self._scheme_model.additional_player = self._additional_player_model

    def undo(self) -> None:
        self._scheme_model.remove_additional_player()


class RemoveSecondTeamCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление игроков второй команды.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._players_lst = self._scheme_model.second_team_players
        self._deleted_team_type = self._scheme_model.second_team
        self._player_actions_mappers: list['PlayerActionsMapper'] = []

    def redo(self) -> None:
        for player_model in self._scheme_model.second_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._player_actions_mappers.append(player_actions_mapper)
            self._deletion_observer.add_deleted_players_ids(player_model)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
                player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                player_model.remove_action(action_model)
        self._scheme_model.remove_second_team_players()

    def undo(self) -> None:
        for player_model in self._players_lst:
            self._scheme_model.add_second_team_player(player_model)
            self._deletion_observer.remove_deleted_players_ids(player_model)
        self._scheme_model.set_second_team_state(self._deleted_team_type)
        for player_actions_mapper in self._player_actions_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.action_line_models_dict[i],
                                              player_actions_mapper.final_action_models_dict[i])
        self._player_actions_mappers.clear()


class RemoveAdditionalOffencePlayerCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление дополнительного игрока нападения.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._additional_player = self._scheme_model.additional_player
        self._additional_player_actions_mapper: Optional['PlayerActionsMapper'] = None

    def redo(self) -> None:
        self._additional_player_actions_mapper = PlayerActionsMapper(self._additional_player)
        self._deletion_observer.add_deleted_players_ids(self._additional_player)
        for i, action_model in enumerate(self._additional_player.actions):
            self._additional_player_actions_mapper.action_models_dict[i] = action_model
            self._additional_player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
            self._additional_player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
            action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
            self._additional_player.remove_action(action_model)
        self._scheme_model.remove_additional_player()

    def undo(self) -> None:
        self._scheme_model.additional_player = self._additional_player
        self._deletion_observer.remove_deleted_players_ids(self._additional_player)
        for i, action_model in self._additional_player_actions_mapper.action_models_dict.items():
            self._additional_player.add_action(action_model)
            action_model.add_action_parts(self._additional_player_actions_mapper.action_line_models_dict[i],
                                          self._additional_player_actions_mapper.final_action_models_dict[i])
        self._additional_player_actions_mapper = None


class RemoveAllPlayersCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех игроков.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._first_team_position = self._scheme_model.first_team_position
        self._deleted_first_team_type = self._scheme_model.first_team
        self._deleted_second_team_type = self._scheme_model.second_team
        self._first_team_players_lst = self._scheme_model.first_team_players
        self._first_team_players_mappers: list['PlayerActionsMapper'] = []
        self._second_team_players_lst = self._scheme_model.second_team_players
        self._second_team_players_mappers: list['PlayerActionsMapper'] = []
        self._additional_player = self._scheme_model.additional_player
        self._additional_player_mapper: Optional['PlayerActionsMapper'] = None

    def redo(self) -> None:
        for player_model in self._first_team_players_lst:
            self._deletion_observer.add_deleted_players_ids(player_model)
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._first_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
                player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                player_model.remove_action(action_model)
        for player_model in self._second_team_players_lst:
            self._deletion_observer.add_deleted_players_ids(player_model)
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._second_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
                player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                player_model.remove_action(action_model)
        if self._additional_player:
            self._deletion_observer.add_deleted_players_ids(self._additional_player)
            self._additional_player_mapper = PlayerActionsMapper(self._additional_player)
            for i, action_model in enumerate(self._additional_player.actions):
                self._additional_player_mapper.action_models_dict[i] = action_model
                self._additional_player_mapper.action_line_models_dict[i] = action_model.action_lines
                self._additional_player_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                self._additional_player.remove_action(action_model)
        self._scheme_model.remove_all_players()

    def undo(self) -> None:
        if self._first_team_players_lst:
            for player_model in self._first_team_players_lst:
                self._scheme_model.add_first_team_player(player_model)
                self._deletion_observer.remove_deleted_players_ids(player_model)
            for player_actions_mapper in self._first_team_players_mappers:
                for i, action_model in player_actions_mapper.action_models_dict.items():
                    player_actions_mapper.player.add_action(action_model)
                    action_model.add_action_parts(player_actions_mapper.action_line_models_dict[i],
                                                  player_actions_mapper.final_action_models_dict[i])
            self._scheme_model.set_first_team_state(self._deleted_first_team_type, self._first_team_position)

        if self._second_team_players_lst:
            for player_model in self._second_team_players_lst:
                self._scheme_model.add_second_team_player(player_model)
                self._deletion_observer.remove_deleted_players_ids(player_model)
            for player_actions_mapper in self._second_team_players_mappers:
                for i, action_model in player_actions_mapper.action_models_dict.items():
                    player_actions_mapper.player.add_action(action_model)
                    action_model.add_action_parts(player_actions_mapper.action_line_models_dict[i],
                                                  player_actions_mapper.final_action_models_dict[i])
            self._scheme_model.set_second_team_state(self._deleted_second_team_type)

        if self._additional_player:
            self._scheme_model.additional_player = self._additional_player
            self._deletion_observer.remove_deleted_players_ids(self._additional_player)
            for i, action_model in self._additional_player_mapper.action_models_dict.items():
                self._additional_player_mapper.player.add_action(action_model)
                action_model.add_action_parts(self._additional_player_mapper.action_line_models_dict[i],
                                              self._additional_player_mapper.final_action_models_dict[i])
        self._first_team_players_mappers.clear()
        self._second_team_players_mappers.clear()
        self._additional_player_mapper = None


class PlaceFigureCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', figure_model: 'FigureModel'):
        super().__init__('Размещение фигуры')
        self._scheme_model = scheme_model
        self._figure_model = figure_model

    def redo(self) -> None:
        self._scheme_model.add_figure(self._figure_model)

    def undo(self) -> None:
        self._scheme_model.remove_figure(self._figure_model)


class RemoveFigureCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel', figure_model: 'FigureModel'):
        super().__init__('Удаление фигуры.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._figure_model = figure_model
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._scheme_model.remove_figure(self._figure_model)
        self._deletion_observer.add_deleted_figures_ids(self._figure_model)

    def undo(self) -> None:
        self._scheme_model.add_figure(self._figure_model)
        self._deletion_observer.remove_deleted_figures_ids(self._figure_model)


class RemoveAllFiguresCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех фигур.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._figures_models_lst = scheme_model.figures

    def redo(self) -> None:
        self._scheme_model.remove_all_figures()
        for figure_model in self._figures_models_lst:
            self._deletion_observer.add_deleted_figures_ids(figure_model)

    def undo(self) -> None:
        for figure_model in self._figures_models_lst:
            self._scheme_model.add_figure(figure_model)
            self._deletion_observer.remove_deleted_figures_ids(figure_model)


class PlacePencilLinesCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', pencil_line_models_lst: list['PencilLineModel']):
        super().__init__('Размещение линий карандаша.')
        self._scheme_model = scheme_model
        self._pencil_line_models_lst = pencil_line_models_lst

    def redo(self) -> None:
        self._scheme_model.add_pencil_lines(self._pencil_line_models_lst)

    def undo(self) -> None:
        self._scheme_model.remove_pencil_lines(self._pencil_line_models_lst)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, PlacePencilLinesCommand):
            return False
        if other._scheme_model is not self._scheme_model:
            return False
        self._pencil_line_models_lst.extend(other._pencil_line_models_lst)
        return True


class RemovePencilLinesCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление линий карандаша.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._pencil_line_models_lst = self._scheme_model.pencil_lines

    def redo(self) -> None:
        self._scheme_model.remove_all_pencil_lines()
        for pencil_line_model in self._pencil_line_models_lst:
            self._deletion_observer.add_deleted_pencil_lines_ids(pencil_line_model)

    def undo(self) -> None:
        self._scheme_model.add_pencil_lines(self._pencil_line_models_lst)
        for pencil_line_model in self._pencil_line_models_lst:
            self._deletion_observer.remove_deleted_pencil_lines_ids(pencil_line_model)


class PlaceLabelCommand(QUndoCommand):
    def __init__(self, scheme_model: 'SchemeModel', label_model: 'LabelModel'):
        super().__init__('Размещение надписи.')
        self._scheme_model = scheme_model
        self._label_model = label_model

    def redo(self) -> None:
        self._scheme_model.add_label(self._label_model)

    def undo(self) -> None:
        self._scheme_model.remove_label(self._label_model)


class RemoveLabelCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel', label_model: 'LabelModel'):
        super().__init__('Удаление надписи.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._label_model = label_model

    def redo(self) -> None:
        self._scheme_model.remove_label(self._label_model)
        self._deletion_observer.add_deleted_labels_ids(self._label_model)

    def undo(self) -> None:
        self._scheme_model.add_label(self._label_model)
        self._deletion_observer.remove_deleted_labels_ids(self._label_model)


class RemoveAllLabelsCommand(QUndoCommand):
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех надписей.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._label_models_lst = self._scheme_model.labels

    def redo(self) -> None:
        self._scheme_model.remove_all_labels()
        for label_model in self._label_models_lst:
            self._deletion_observer.add_deleted_labels_ids(label_model)

    def undo(self) -> None:
        for label_model in self._label_models_lst:
            self._scheme_model.add_label(label_model)
            self._deletion_observer.remove_deleted_labels_ids(label_model)


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
    def __init__(self, deletion_observer: 'DeletionObserver', scheme_model: 'SchemeModel'):
        super().__init__('Удаление всех действий игроков.')
        self._deletion_observer = deletion_observer
        self._scheme_model = scheme_model
        self._first_team_players_mappers: list['PlayerActionsMapper'] = []
        self._second_team_players_mappers: list['PlayerActionsMapper'] = []
        self._additional_player_mapper: Optional['PlayerActionsMapper'] = None

    def redo(self) -> None:
        for player_model in self._scheme_model.first_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._first_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
                player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                player_model.remove_action(action_model)
                self._deletion_observer.add_deleted_actions_ids(action_model)

        for player_model in self._scheme_model.second_team_players:
            player_actions_mapper = PlayerActionsMapper(player_model)
            self._second_team_players_mappers.append(player_actions_mapper)
            for i, action_model in enumerate(player_model.actions):
                player_actions_mapper.action_models_dict[i] = action_model
                player_actions_mapper.action_line_models_dict[i] = action_model.action_lines
                player_actions_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                player_model.remove_action(action_model)
                self._deletion_observer.add_deleted_actions_ids(action_model)

        if self._scheme_model.additional_player:
            self._additional_player_mapper = PlayerActionsMapper(self._scheme_model.additional_player)
            for i, action_model in enumerate(self._scheme_model.additional_player.actions):
                self._additional_player_mapper.action_models_dict[i] = action_model
                self._additional_player_mapper.action_line_models_dict[i] = action_model.action_lines
                self._additional_player_mapper.final_action_models_dict[i] = action_model.final_actions
                action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
                self._scheme_model.additional_player.remove_action(action_model)
                self._deletion_observer.add_deleted_actions_ids(action_model)

    def undo(self) -> None:
        for player_actions_mapper in self._first_team_players_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.action_line_models_dict[i],
                                              player_actions_mapper.final_action_models_dict[i])
                self._deletion_observer.remove_deleted_actions_ids(action_model)
        self._first_team_players_mappers.clear()
        for player_actions_mapper in self._second_team_players_mappers:
            for i, action_model in player_actions_mapper.action_models_dict.items():
                player_actions_mapper.player.add_action(action_model)
                action_model.add_action_parts(player_actions_mapper.action_line_models_dict[i],
                                              player_actions_mapper.final_action_models_dict[i])
                self._deletion_observer.remove_deleted_actions_ids(action_model)
        self._second_team_players_mappers.clear()
        if self._additional_player_mapper:
            for i, action_model in self._additional_player_mapper.action_models_dict.items():
                self._additional_player_mapper.player.add_action(action_model)
                action_model.add_action_parts(self._additional_player_mapper.action_line_models_dict[i],
                                              self._additional_player_mapper.final_action_models_dict[i])
                self._deletion_observer.remove_deleted_actions_ids(action_model)
            self._additional_player_mapper = None

