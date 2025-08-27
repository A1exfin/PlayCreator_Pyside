from typing import TYPE_CHECKING, Optional
from uuid import UUID
from itertools import chain

from PySide6.QtCore import Signal

from Core import log_method, logger
from .base_model import BaseModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject
    from Core.Enums import StorageType
    from .playbook_model import PlaybookModel
    from .action_line_model import ActionLineModel
    from .final_action_model import FinalActionModel

__all__ = ('ActionModel', )


class ActionModel(BaseModel):
    actionPartsAdded = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]
    actionPartsRemoved = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]

    def __init__(self, playbook_model: 'PlaybookModel', uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['QObject'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._playbook_model = playbook_model
        self._action_lines = []
        self._final_actions = []

    def set_changed_flag(self) -> None:
        super().set_changed_flag()
        self._playbook_model.set_changed_flag()

    def set_new_uuid(self) -> None:
        super().set_new_uuid()
        self._set_action_parts_new_uuid()

    def _set_action_parts_new_uuid(self) -> None:
        for action_part_model in chain(self._action_lines, self._final_actions):
            if action_part_model:
                action_part_model.set_new_uuid()

    def reset_id(self, storage_type: 'StorageType') -> None:
        super().reset_id(storage_type)
        self._reset_id_for_action_parts(storage_type)

    def _reset_id_for_action_parts(self, storage_type: 'StorageType') -> None:
        for action_part_model in chain(self._action_lines, self._final_actions):
            if action_part_model:
                action_part_model.reset_id(storage_type)

    def reset_changed_flag(self) -> None:
        super().reset_changed_flag()
        self._reset_action_parts_changed_flag()

    def _reset_action_parts_changed_flag(self) -> None:
        for action_part_model in chain(self._action_lines, self._final_actions):
            if action_part_model:
                action_part_model.reset_changed_flag()

    @property
    def action_lines(self) -> list['ActionLineModel']:
        return self._action_lines.copy()

    @property
    def final_actions(self) -> list['FinalActionModel']:
        return self._final_actions.copy()

    @log_method()
    def add_action_parts(self, action_lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._action_lines.extend(action_lines)
        self._final_actions.extend(final_actions)
        self.set_changed_flag()
        self.actionPartsAdded.emit(action_lines, final_actions)

    @log_method()
    def remove_action_parts(self, action_lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._action_lines = list(set(self._action_lines) - set(action_lines))
        self._final_actions = list(set(self._final_actions) - set(final_actions))
        self.set_changed_flag()
        self.actionPartsRemoved.emit(action_lines, final_actions)

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid,
                'lines_data': [line_data.get_data_for_view() for line_data in self._action_lines],
                'final_actions_data': [final_action_data.get_data_for_view() for final_action_data in self._final_actions]}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid,
                'action_lines': list(),
                'final_actions': list()}

    def __repr__(self) -> str:
        return f'\n\t\t\t\t\t\t<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self._uuid}) at {hex(id(self))}> ' \
               f'\n\t\t\t\t\t\t\taction_lines: {self._action_lines}\n\t\t\t\t\t\t\tfinal_actions: {self._final_actions}>'
