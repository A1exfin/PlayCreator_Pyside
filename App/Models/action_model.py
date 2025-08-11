from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from itertools import chain

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from .action_line_model import ActionLineModel
    from .final_action_model import FinalActionModel

__all__ = ('ActionModel', )


class ActionModel(QObject):
    actionPartsAdded = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]
    actionPartsRemoved = Signal(list, list)  # list[ActionLineModel], list[FinalActionModel]

    def __init__(self, uuid: Optional['UUID'] = None, id_local_db: Optional[int] = None, id_api: Optional[int] = None):
        super().__init__()
        self._lines = []
        self._final_actions = []
        self._uuid = uuid if uuid else uuid4()
        self._id_local_db = id_local_db
        self._id_api = id_api

    @property
    def id_local_db(self) -> int:
        return self._id_local_db

    @id_local_db.setter
    def id_local_db(self, value: int) -> None:
        self._id_local_db = value

    @property
    def id_api(self) -> int:
        return self._id_api

    @id_api.setter
    def id_api(self, value: int) -> None:
        self._id_api = value

    @property
    def uuid(self) -> 'UUID':
        return self._uuid

    def set_new_uuid(self) -> None:
        self._uuid = uuid4()
        self._set_lines_and_final_actions_new_uuid()

    def _set_lines_and_final_actions_new_uuid(self) -> None:
        for action_part_model in chain(self._lines, self._final_actions):
            if action_part_model:
                action_part_model.set_new_uuid()

    @property
    def lines(self) -> list['ActionLineModel']:
        return self._lines.copy()

    @property
    def final_actions(self) -> list['FinalActionModel']:
        return self._final_actions.copy()

    def add_action_parts(self, lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._lines.extend(lines)
        self._final_actions.extend(final_actions)
        self.actionPartsAdded.emit(lines, final_actions)

    def remove_action_parts(self, lines: list['ActionLineModel'], final_actions: list['FinalActionModel']) -> None:
        self._lines = list(set(self._lines) - set(lines))
        self._final_actions = list(set(self._final_actions) - set(final_actions))
        self.actionPartsRemoved.emit(lines, final_actions)

    def get_data_for_view(self) -> dict:
        return {'model_uuid': self._uuid,
                'lines_data': [line_data.get_data_for_view() for line_data in self._lines],
                'final_actions_data': [final_action_data.get_data_for_view() for final_action_data in self._final_actions]}

    def to_dict(self) -> dict:
        return {'uuid': self._uuid,
                'lines': [line.to_dict() for line in self._lines],
                'final_actions': [final_action.to_dict() for final_action in self._final_actions]}
