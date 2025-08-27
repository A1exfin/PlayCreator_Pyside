from typing import TYPE_CHECKING, Optional, Union
from itertools import chain

from PySide6.QtCore import QObject, Signal

from Core.logger_settings import log_method, logger
from Core.Enums import FinalActionType
from Views import Graphics

if TYPE_CHECKING:
    from uuid import UUID
    from .field_view import tmp_painted_action_data

__all__ = ('ActionView',)


class ActionView(QObject):
    optionalActionPainted = Signal(object)  # PaintedActionData

    def __init__(self, player: 'Graphics.PlayerView', scene: 'Graphics.Field',
                 lines_data: list[dict], final_actions_data: list[dict],
                 model_uuid: 'UUID'):
        super().__init__()
        self._scene = scene
        self._player = player
        self._model_uuid = model_uuid
        self._lines = []
        self._final_actions = []
        for line_data in lines_data:
            self.add_action_line(line_data)
        for final_action_data in final_actions_data:
            self.add_final_action(final_action_data)

    @property
    def player(self) -> 'Graphics.PlayerView':
        return self._player

    @property
    def model_uuid(self) -> Optional['UUID']:
        return self._model_uuid

    @property
    def action_lines(self) -> list['Graphics.ActionLineView']:
        return self._lines.copy()

    @property
    def final_actions(self) -> list[Union['Graphics.FinalActionRouteView', 'Graphics.FinalActionBlockView']]:
        return self._final_actions.copy()

    def _add_action_part_to_scene(self, action_part: Union['Graphics.ActionLineView', 'Graphics.FinalActionRouteView',
                                                           'Graphics.FinalActionBlockView']) -> None:
        self._scene.addItem(action_part)

    @log_method()
    def add_action_line(self, line_data: dict) -> 'Graphics.ActionLineView':
        line_item = Graphics.ActionLineView(**line_data, action=self)
        self._add_action_part_to_scene(line_item)
        self._lines.append(line_item)
        return line_item

    @log_method()
    def add_final_action(self, final_action_data: dict) -> Union['Graphics.FinalActionRouteView',
                                                                 'Graphics.FinalActionBlockView']:
        if final_action_data['action_type'] is FinalActionType.ARROW:
            final_action_item = Graphics.FinalActionRouteView(**final_action_data, action=self)
        if final_action_data['action_type'] is FinalActionType.LINE:
            final_action_item = Graphics.FinalActionBlockView(**final_action_data, action=self)
        self._add_action_part_to_scene(final_action_item)
        self._final_actions.append(final_action_item)
        return final_action_item

    @log_method()
    def remove_action_line(self, line_item: 'Graphics.ActionLineView') -> None:
        self._lines.remove(line_item)
        self._scene.removeItem(line_item)

    @log_method()
    def remove_final_action(self, final_action_item: Union['Graphics.FinalActionRouteView',
                                                           'Graphics.FinalActionBlockView']) -> None:
        self._final_actions.remove(final_action_item)
        self._scene.removeItem(final_action_item)

    @log_method()
    def remove_all_action_parts(self) -> None:
        lines_group = self._scene.createItemGroup(self._lines)
        self._scene.removeItem(lines_group)
        self._lines.clear()
        final_actions_group = self._scene.createItemGroup(self._final_actions)
        self._scene.removeItem(final_actions_group)
        self._final_actions.clear()

    def get_all_action_parts(self) \
            -> list[Union['Graphics.ActionLineView', 'Graphics.FinalActionRouteView', 'Graphics.FinalActionBlockView']]:
        return [item for item in chain(self._lines, self._final_actions)]

    def set_hover_state(self, hover_state: bool) -> None:
        self._player.hover_state = hover_state
        for action_part in self._lines:
            action_part.hover_state = hover_state
        for final_action in self._final_actions:
            final_action.hover_state = hover_state

    @log_method()
    def emit_optional_action_painted(self, action_data: 'tmp_painted_action_data') -> None:
        self.optionalActionPainted.emit(action_data)

    def get_data(self) -> dict:
        return {'lines': [line.get_data() for line in self._lines],
                'final_actions': [final_action.get_data() for final_action in self._final_actions]}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} (model_uuid: {self._model_uuid}) at {hex(id(self))}'
