from typing import TYPE_CHECKING, Union

from Commands import AddOptionalActionCommand
from .Mappers import ActionPartsMapper

if TYPE_CHECKING:
    from uuid import UUID
    from Models import ActionModel, ActionLineModel, FinalActionModel
    from Views import Graphics


__all__ = ('ActionPresenter', )


class ActionPresenter:
    def __init__(self, execute_command_func: callable, action_model: 'ActionModel', action_view: 'Graphics.ActionView'):
        self._execute_command_func = execute_command_func
        self._action_view = action_view
        self._model = action_model
        self._action_parts_mappers: dict['UUID', 'ActionPartsMapper'] = {}
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._action_view.optionalActionPainted.connect(self._handle_place_optional_action)
        self._model.actionPartsAdded.connect(self._place_optional_action_items)
        self._model.actionPartsRemoved.connect(self._remove_optional_action_items)

    def _handle_place_optional_action(self, action_data: dict[str, list[dict]]) -> None:
        add_action_command = AddOptionalActionCommand(self._model, action_data)
        self._execute_command_func(add_action_command)

    def _place_optional_action_items(self, line_models: list['ActionLineModel'],
                                     final_action_models: list['FinalActionModel']) -> None:
        for line_model in line_models:
            line_view = self._action_view.add_action_line(line_model.get_data_for_view())
            self._action_parts_mappers[line_model.uuid] = ActionPartsMapper(line_model, line_view)
        for final_action_model in final_action_models:
            final_action_view = self._action_view.add_final_action(final_action_model.get_data_for_view())
            self._action_parts_mappers[final_action_model.uuid] = ActionPartsMapper(final_action_model, final_action_view)

    def _remove_optional_action_items(self, line_models: list['ActionLineModel'],
                                      final_action_models: list['FinalActionModel']) -> None:
        for line_model in line_models:
            line_view = self._action_parts_mappers[line_model.uuid].view
            self._action_view.remove_action_line(line_view)
            mapper = self._action_parts_mappers.pop(line_model.uuid)
            del mapper.model
            del mapper.view
            del mapper
        for final_action_model in final_action_models:
            final_action_view = self._action_parts_mappers[final_action_model.uuid].view
            self._action_view.remove_final_action(final_action_view)
            mapper = self._action_parts_mappers.pop(final_action_model.uuid)
            del mapper.model
            del mapper.view
            del mapper
