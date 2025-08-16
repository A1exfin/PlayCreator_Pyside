from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from itertools import chain

from PySide6.QtCore import Signal

from .base_model import BaseModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject
    from Config.Enums import StorageType
    from .action_line_model import ActionLineModel
    from .final_action_model import FinalActionModel

__all__ = ('ActionModel', )


class ActionModel(BaseModel):
    actionPartsAdded = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]
    actionPartsRemoved = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]

    def __init__(self, uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None,
                 parent: Optional['QObject'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._action_lines = []
        self._final_actions = []

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()
        self._set_lines_and_final_actions_new_uuid()

    def _set_lines_and_final_actions_new_uuid(self) -> None:
        for action_part_model in chain(self._action_lines, self._final_actions):
            if action_part_model:
                action_part_model.set_new_uuid()

    def reset_id(self, storage_type: 'StorageType') -> None:
        if hasattr(self, f'_id_{storage_type.value}'):
            setattr(self, f'_id_{storage_type.value}', None)

    @property
    def action_lines(self) -> list['ActionLineModel']:
        return self._action_lines.copy()

    @property
    def final_actions(self) -> list['FinalActionModel']:
        return self._final_actions.copy()

    def add_action_parts(self, action_lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._action_lines.extend(action_lines)
        self._final_actions.extend(final_actions)
        self.actionPartsAdded.emit(action_lines, final_actions)

    def remove_action_parts(self, action_lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._action_lines = list(set(self._action_lines) - set(action_lines))
        self._final_actions = list(set(self._final_actions) - set(final_actions))
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
