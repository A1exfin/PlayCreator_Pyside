from typing import TYPE_CHECKING, Union, Callable

from Core import log_method, logger
from Core.Enums import TeamType
from Commands import MovePlayerCommand, ChangePlayerStyleCommand, AddActionCommand, RemoveActionCommand
from Views.Dialog_windows import DialogEditFirstTeamPlayer, DialogEditSecondTeamPlayer
from .Mappers import ActionMapper
from .action_presenter import ActionPresenter

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtCore import QPointF
    from Core.Enums import FillType, SymbolType
    from PlayCreator_main import PlayCreatorApp
    from View_Models import PlayerModel, ActionModel
    from View_Models.Other import PlaybookModelsFabric, DeletionObserver
    from Views import Graphics


__all__ = ('PlayerPresenter', )


class PlayerPresenter:
    @log_method()
    def __init__(self, playbook_items_fabric: 'PlaybookModelsFabric', deletion_observer: 'DeletionObserver',
                 execute_command_func: Callable,
                 player_model: 'PlayerModel', view: 'PlayCreatorApp',
                 player_view: Union['Graphics.FirstTeamPlayerView', 'Graphics.SecondTeamPlayerView']):
        self._model = player_model
        self._view = view
        self._player_view = player_view
        self._playbook_items_fabric = playbook_items_fabric
        self._deletion_observer = deletion_observer
        self._execute_command_func = execute_command_func
        self._action_mappers: dict['UUID', 'ActionMapper'] = {}
        self._connect_signals()

    @log_method()
    def _connect_signals(self) -> None:
        self._player_view.signals.itemMoved.connect(self._handle_move_player)
        self._model.coordsChanged.connect(self._move_player_item)
        self._player_view.signals.itemDoubleClicked.connect(self._handle_edit_player)
        self._model.playerStyleChanged.connect(self._change_player_item_style)
        self._player_view.signals.actionPainted.connect(self._handle_place_action)
        self._model.actionAdded.connect(self._place_action_item)
        self._player_view.signals.actionRemoveClicked.connect(self._hande_remove_action)
        self._model.actionRemoved.connect(self._remove_action_item)
        self._model.allActionsRemoved.connect(self._remove_all_action_items)

    @log_method()
    def _handle_move_player(self, new_pos: 'QPointF') -> None:
        if self._model.x != new_pos.x() or self._model.y != new_pos.y():
            move_player_command = MovePlayerCommand(self._deletion_observer, self._model, new_pos.x(), new_pos.y())
            self._execute_command_func(move_player_command)

    def _move_player_item(self, new_pos: 'QPointF') -> None:
        self._player_view.setPos(new_pos)

    @log_method()
    def _handle_edit_player(self) -> None:
        if self._model.team_type in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT,
                                     TeamType.FIELD_GOAL_OFF, TeamType.OFFENCE_ADD):
            dialog_player_config = DialogEditFirstTeamPlayer(self._model.position, self._model.text,
                                                             self._model.player_color, self._model.text_color,
                                                             self._model.fill_type, parent=self._view)
            dialog_player_config.exec()
            if dialog_player_config.result():
                data = dialog_player_config.get_data()
                if self._model.text != data.text or self._model.text_color != data.text_color \
                        or self._model.player_color != data.player_color \
                        or self._model.fill_type != data.fill_type:
                    change_player_config_command = ChangePlayerStyleCommand(self._model,
                                                                            new_text=data.text,
                                                                            new_text_color=data.text_color,
                                                                            new_player_color=data.player_color,
                                                                            new_fill_type=data.fill_type)
                    self._execute_command_func(change_player_config_command)
        if self._model.team_type in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
            dialog_player_config = DialogEditSecondTeamPlayer(self._model.text, self._model.text_color,
                                                              self._model.player_color, self._model.symbol_type,
                                                              parent=self._view)
            dialog_player_config.exec()
            if dialog_player_config.result():
                data = dialog_player_config.get_data()
                if self._model.text != data.text or self._model.text_color != data.text_color \
                        or self._model.player_color != data.player_color \
                        or self._model.fill_type != data.symbol_type:
                    change_player_config_command = ChangePlayerStyleCommand(self._model,
                                                                            new_text=data.text,
                                                                            new_text_color=data.text_color,
                                                                            new_player_color=data.player_color,
                                                                            new_symbol_type=data.symbol_type)
                    self._execute_command_func(change_player_config_command)

    def _change_player_item_style(self, new_fill_symbol: Union['FillType', 'SymbolType'], new_text: str,
                                  new_text_color: str, new_player_color: str) -> None:
        self._player_view.set_player_style(new_fill_symbol, new_text, new_text_color, new_player_color)

    @log_method()
    def _handle_place_action(self, action_data) -> None:
        action_model = self._playbook_items_fabric.create_action_model(self._model)
        action_line_models_lst = [
            self._playbook_items_fabric.create_action_line_model(parent=action_model, **action_line_data)
            for action_line_data in action_data.action_lines
        ]
        final_action_models_lst = [
            self._playbook_items_fabric.create_final_action_model(parent=action_model, **final_action_data)
            for final_action_data in action_data.final_actions
        ]
        add_action_command = AddActionCommand(self._model, action_model, action_line_models_lst, final_action_models_lst)
        self._execute_command_func(add_action_command)

    def _place_action_item(self, action_model: 'ActionModel') -> None:
        action_view = self._player_view.add_action_item(action_model.get_data_for_view())
        action_presenter = ActionPresenter(self._playbook_items_fabric, self._deletion_observer,
                                           self._execute_command_func, action_model, action_view)
        self._action_mappers[action_model.uuid] = ActionMapper(action_presenter, action_model, action_view)

    @log_method()
    def _hande_remove_action(self, action_model_uuid: 'UUID') -> None:
        action_model = self._action_mappers[action_model_uuid].model
        remove_action_command = RemoveActionCommand(self._deletion_observer, self._model, action_model)
        self._execute_command_func(remove_action_command)

    def _remove_action_item(self, action_model: 'ActionModel') -> None:
        action_item = self._action_mappers[action_model.uuid].view
        self._player_view.remove_action_item(action_item)
        mapper = self._action_mappers.pop(action_model.uuid)

    def handle_remove_all_actions(self) -> None:
        pass

    def _remove_all_action_items(self) -> None:
        self._player_view.remove_all_action_items()
        self._action_mappers.clear()



