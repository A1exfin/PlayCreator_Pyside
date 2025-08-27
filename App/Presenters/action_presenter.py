from typing import TYPE_CHECKING, Callable, Union

from Core import log_method, logger
from Commands import AddOptionalActionCommand
from .Mappers import ActionPartsMapper

if TYPE_CHECKING:
    from uuid import UUID
    from View_Models import ActionModel, ActionLineModel, FinalActionModel
    from Views import Graphics
    from View_Models.Other import PlaybookModelsFabric, DeletionObserver


__all__ = ('ActionPresenter', )


class ActionPresenter:
    @log_method()
    def __init__(self, playbook_items_fabric: 'PlaybookModelsFabric', deletion_observer: 'DeletionObserver',
                 execute_command_func: Callable, action_model: 'ActionModel', action_view: 'Graphics.ActionView'):
        self._model = action_model
        self._action_view = action_view
        self._playbook_items_fabric = playbook_items_fabric
        self._deletion_observer = deletion_observer
        self._execute_command_func = execute_command_func
        self._action_parts_mappers: dict['UUID', 'ActionPartsMapper'] = {}
        self._connect_signals()

    @log_method()
    def _connect_signals(self) -> None:
        self._action_view.optionalActionPainted.connect(self._handle_place_optional_action)
        self._model.actionPartsAdded.connect(self._place_optional_action_items)
        self._model.actionPartsRemoved.connect(self._remove_optional_action_items)

    @log_method()
    def _handle_place_optional_action(self, action_data) -> None:
        action_line_models_lst = [
            self._playbook_items_fabric.create_action_line_model(parent=self._model, **action_line_data)
            for action_line_data in action_data.action_lines
        ]
        final_action_models_lst = [
            self._playbook_items_fabric.create_final_action_model(parent=self._model, **final_action_data)
            for final_action_data in action_data.final_actions
        ]
        add_action_command = AddOptionalActionCommand(self._model, action_line_models_lst, final_action_models_lst)
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
        for final_action_model in final_action_models:
            final_action_view = self._action_parts_mappers[final_action_model.uuid].view
            self._action_view.remove_final_action(final_action_view)
            mapper = self._action_parts_mappers.pop(final_action_model.uuid)
