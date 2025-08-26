from typing import TYPE_CHECKING, Optional

from PySide6.QtGui import QUndoCommand

from Core import log_method_decorator, logger
from View_Models import PlayerModel, ActionModel, ActionLineModel, FinalActionModel

if TYPE_CHECKING:
    from Core.Enums import FillType, SymbolType
    from View_Models.Other import DeletionObserver


__all__ = ('MovePlayerCommand', 'ChangePlayerStyleCommand', 'AddActionCommand', 'RemoveActionCommand')


class MovePlayerCommand(QUndoCommand):
    @log_method_decorator()
    def __init__(self, deletion_observer: 'DeletionObserver', player_model: 'PlayerModel',
                 new_pos_x: float, new_pos_y: float):
        super().__init__('Перемещение игрока.')
        self._deletion_observer = deletion_observer
        self._player_model = player_model
        self._last_pos_x, self._last_pos_y = self._player_model.x, self._player_model.y
        self._new_pos_x, self._new_pos_y = new_pos_x, new_pos_y
        self._actions_dict: dict[int: 'ActionModel'] = {}
        self._line_models_dict: dict[int: list['ActionLineModel']] = {}
        self._final_action_models_dict: dict[int, list['FinalActionModel']] = {}

    @log_method_decorator()
    def redo(self) -> None:
        self._player_model.set_pos(self._new_pos_x, self._new_pos_y)
        for i, action_model in enumerate(self._player_model.actions):
            self._actions_dict[i] = action_model
            self._line_models_dict[i] = action_model.action_lines
            self._final_action_models_dict[i] = action_model.final_actions
            action_model.remove_action_parts(action_model.action_lines, action_model.final_actions)
            self._deletion_observer.add_deleted_actions_ids(action_model)
        self._player_model.remove_all_actions()

    @log_method_decorator()
    def undo(self) -> None:
        self._player_model.set_pos(self._last_pos_x, self._last_pos_y)
        for i, action_model in self._actions_dict.items():
            self._player_model.add_action(action_model)
            action_model.add_action_parts(self._line_models_dict[i], self._final_action_models_dict[i])
            self._deletion_observer.remove_deleted_actions_ids(action_model)
        self._actions_dict.clear()
        self._line_models_dict.clear()
        self._final_action_models_dict.clear()

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, MovePlayerCommand):
            return False
        if other._player_model is not self._player_model:
            return False
        self._new_pos_x, self._new_pos_y = other._new_pos_x, other._new_pos_y
        return True


class ChangePlayerStyleCommand(QUndoCommand):
    @log_method_decorator()
    def __init__(self, player_model: 'PlayerModel', new_text: str,
                 new_text_color: str, new_player_color: str,
                 new_fill_type: Optional['FillType'] = None, new_symbol_type: Optional['SymbolType'] = None):
        super().__init__('Изменение игрока (текст, цвет и тд.')
        self._player_model = player_model
        self._last_text = self._player_model.text
        self._last_fill_type = self._player_model.fill_type
        self._last_symbol_type = self._player_model.symbol_type
        self._last_text_color = self._player_model.text_color
        self._last_player_color = self._player_model.player_color
        self._new_text = new_text
        self._new_fill_type = new_fill_type
        self._new_symbol_type = new_symbol_type
        self._new_text_color = new_text_color
        self._new_player_color = new_player_color

    @log_method_decorator()
    def redo(self) -> None:
        self._player_model.set_player_style(self._new_text, self._new_text_color, self._new_player_color,
                                            fill_type=self._new_fill_type, symbol_type=self._new_symbol_type)

    @log_method_decorator()
    def undo(self) -> None:
        self._player_model.set_player_style(self._last_text, self._last_text_color, self._last_player_color,
                                            fill_type=self._last_fill_type, symbol_type=self._last_symbol_type)

    def id(self) -> int:
        return 1

    def mergeWith(self, other: 'QUndoCommand') -> bool:
        if not isinstance(other, ChangePlayerStyleCommand):
            return False
        if other._player_model is not self._player_model:
            return False
        self._new_text, self._new_text_color, = other._new_text, other._new_text_color
        self._new_player_color = other._new_player_color
        self._new_fill_type, self._new_symbol_type = other._new_fill_type, other._new_symbol_type
        return True


class AddActionCommand(QUndoCommand):
    @log_method_decorator()
    def __init__(self, player_model: 'PlayerModel', action_model: 'ActionModel',
                 action_line_models_lst: list['ActionLineModel'], final_action_models_lst: list['FinalActionModel']):
        super().__init__('Добавление нового действия.')
        self._player_model = player_model
        self._new_action = action_model
        self._action_line_models_lst = action_line_models_lst
        self._final_action_models_lst = final_action_models_lst

    @log_method_decorator()
    def redo(self) -> None:
        self._player_model.add_action(self._new_action)
        self._new_action.add_action_parts(self._action_line_models_lst, self._final_action_models_lst)

    @log_method_decorator()
    def undo(self) -> None:
        self._player_model.remove_action(self._new_action)
        self._new_action.remove_action_parts(self._action_line_models_lst, self._final_action_models_lst)


class RemoveActionCommand(QUndoCommand):
    @log_method_decorator()
    def __init__(self, deletion_observer: 'DeletionObserver', player_model: 'PlayerModel', action_model: 'ActionModel'):
        super().__init__('Удаление действия.')
        self._deletion_observer = deletion_observer
        self._player_model = player_model
        self._action_model = action_model
        self._line_models_lst = self._action_model.action_lines
        self._final_action_models_lst = self._action_model.final_actions

    @log_method_decorator()
    def redo(self) -> None:
        self._player_model.remove_action(self._action_model)
        self._action_model.remove_action_parts(self._line_models_lst, self._final_action_models_lst)
        self._deletion_observer.add_deleted_actions_ids(self._action_model)

    @log_method_decorator()
    def undo(self) -> None:
        self._player_model.add_action(self._action_model)
        self._action_model.add_action_parts(self._line_models_lst, self._final_action_models_lst)
        self._deletion_observer.remove_deleted_actions_ids(self._action_model)
