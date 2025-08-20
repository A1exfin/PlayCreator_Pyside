from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from View_Models import ActionModel, ActionLineModel, FinalActionModel

__all__ = ('AddOptionalActionCommand', )


class AddOptionalActionCommand(QUndoCommand):
    def __init__(self, action_model: 'ActionModel', action_line_models_lst: list['ActionLineModel'],
                 final_action_models_lst: list['FinalActionModel']):
        super().__init__('Добавление опционального действия.')
        self._action_model = action_model
        self._optional_action_line_models = action_line_models_lst
        self._optional_action_final_actions_models = final_action_models_lst

    def redo(self) -> None:
        self._action_model.add_action_parts(self._optional_action_line_models, self._optional_action_final_actions_models)

    def undo(self) -> None:
        self._action_model.remove_action_parts(self._optional_action_line_models, self._optional_action_final_actions_models)