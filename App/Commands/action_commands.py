from typing import TYPE_CHECKING, Optional

from PySide6.QtGui import QUndoCommand

from Models import ActionModel, ActionLineModel, FinalActionModel


__all__ = ('AddOptionalActionCommand', )


class AddOptionalActionCommand(QUndoCommand):
    def __init__(self, action_model: 'ActionModel', action_data: dict[str, list[dict]]):
        super().__init__('Добавление опционального действия.')
        self._action_model = action_model
        self._optional_action_line_models = [ActionLineModel(**action_line_data) for action_line_data in action_data['lines']]
        self._optional_action_final_actions_models = [FinalActionModel(**final_action_data) for final_action_data in action_data['final_actions']]

    def redo(self) -> None:
        self._action_model.add_action_parts(self._optional_action_line_models, self._optional_action_final_actions_models)

    def undo(self) -> None:
        self._action_model.remove_action_parts(self._optional_action_line_models, self._optional_action_final_actions_models)