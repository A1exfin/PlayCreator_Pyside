from typing import TYPE_CHECKING, Optional

from PySide6.QtGui import QUndoCommand

from Models import PlayerModel, ActionModel, ActionLineModel, FinalActionModel

if TYPE_CHECKING:
    from Config.Enums import FillType, SymbolType


__all__ = ('MovePlayerCommand', 'ChangePlayerStyleCommand', 'AddActionCommand', 'RemoveActionCommand')


class MovePlayerCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, player_model: 'PlayerModel',
                 new_pos_x: float, new_pos_y: float):
        super().__init__('Перемещение игрока.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._player_model = player_model
        self._last_pos_x, self._last_pos_y = self._player_model.x, self._player_model.y
        self._new_pos_x, self._new_pos_y = new_pos_x, new_pos_y
        self._actions_dict: dict[int: 'ActionModel'] = {}
        self._line_models_dict: dict[int: list['ActionLineModel']] = {}
        self._final_action_models_dict: dict[int, list['FinalActionModel']] = {}
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._player_model.set_pos(self._new_pos_x, self._new_pos_y)
        for i, action in enumerate(self._player_model.actions):
            self._actions_dict[i] = action
            self._line_models_dict[i] = action.lines
            self._final_action_models_dict[i] = action.final_actions
            action.remove_action_parts(action.lines, action.final_actions)
        self._deleted_item_ids = self._player_model.remove_all_actions()

    def undo(self) -> None:
        self._player_model.set_pos(self._last_pos_x, self._last_pos_y)
        for i, action in self._actions_dict.items():
            self._player_model.add_action(action)
            action.add_action_parts(self._line_models_dict[i], self._final_action_models_dict[i])
        self._actions_dict.clear()
        self._line_models_dict.clear()
        self._final_action_models_dict.clear()
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)

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

    def redo(self) -> None:
        self._player_model.set_player_style(self._new_text, self._new_text_color, self._new_player_color,
                                            fill_type=self._new_fill_type, symbol_type=self._new_symbol_type)

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
        self._new_text, self._new_text_color, self._new_player_color, self._new_fill_type, self._new_symbol_type = \
            other._new_text, other._new_text_color, other._new_player_color, other._new_fill_type, other._new_symbol_type
        return True


class AddActionCommand(QUndoCommand):
    def __init__(self, player_model: 'PlayerModel', action_data: dict[str, list[dict]]):
        super().__init__('Добавление нового действия.')
        self._player_model = player_model
        self._line_models_lst = [ActionLineModel(**action_line_data) for action_line_data in action_data['lines']]
        self._final_action_models_lst = [FinalActionModel(**final_action_data) for final_action_data in action_data['final_actions']]
        self._new_action = ActionModel()

    def redo(self) -> None:
        self._player_model.add_action(self._new_action)
        self._new_action.add_action_parts(self._line_models_lst, self._final_action_models_lst)

    def undo(self) -> None:
        self._player_model.remove_action(self._new_action)
        self._new_action.remove_action_parts(self._line_models_lst, self._final_action_models_lst)


class RemoveActionCommand(QUndoCommand):
    def __init__(self, remove_deleted_item_ids_func: callable, player_model: 'PlayerModel', action_model: 'ActionModel'):
        super().__init__('Удаление действия.')
        self._remove_deleted_item_ids_func = remove_deleted_item_ids_func
        self._player_model = player_model
        self._action_model = action_model
        self._line_models_lst = self._action_model.lines
        self._final_action_models_lst = self._action_model.final_actions
        self._deleted_item_ids = None

    def redo(self) -> None:
        self._deleted_item_ids = self._player_model.remove_action(self._action_model)
        self._action_model.remove_action_parts(self._line_models_lst, self._final_action_models_lst)

    def undo(self) -> None:
        for storage_type, deleted_ids in self._deleted_item_ids.items():
            self._remove_deleted_item_ids_func('actions', storage_type, deleted_ids)
        self._player_model.add_action(self._action_model)
        self._action_model.add_action_parts(self._line_models_lst, self._final_action_models_lst)
