from typing import TYPE_CHECKING, Optional

from Core import log_method_decorator, logger
from Core.Enums import StorageType

if TYPE_CHECKING:
    from ..playbook_model import PlaybookModel
    from ..scheme_model import SchemeModel
    from ..figure_model import FigureModel
    from ..label_model import LabelModel
    from ..pencil_line_model import PencilLineModel
    from ..player_model import PlayerModel
    from ..action_model import ActionModel


class DeletionObserver:
    def __init__(self, playbook_model: 'PlaybookModel'):
        self._playbook = playbook_model

    @property
    def playbook(self) -> Optional['PlaybookModel']:
        return self._playbook

    @log_method_decorator()
    def add_deleted_schemes_ids(self, scheme_model: 'SchemeModel') -> None:
        if scheme_model.id_local_db:
            self._playbook.add_deleted_item_ids('schemes', StorageType.LOCAL_DB, scheme_model.id_local_db)
        if scheme_model.id_api:
            self._playbook.add_deleted_item_ids('schemes', StorageType.API, scheme_model.id_api)

    @log_method_decorator()
    def remove_deleted_schemes_ids(self, scheme_model: 'SchemeModel') -> None:
        if scheme_model.id_local_db:
            self._playbook.remove_deleted_item_ids('schemes', StorageType.LOCAL_DB, scheme_model.id_local_db)
        if scheme_model.id_api:
            self._playbook.remove_deleted_item_ids('schemes', StorageType.API, scheme_model.id_api)

    @log_method_decorator()
    def add_deleted_figures_ids(self, figure_model: 'FigureModel') -> None:
        if figure_model.id_local_db:
            self._playbook.add_deleted_item_ids('figures', StorageType.LOCAL_DB, figure_model.id_local_db)
        if figure_model.id_api:
            self._playbook.add_deleted_item_ids('figures', StorageType.API, figure_model.id_api)

    @log_method_decorator()
    def remove_deleted_figures_ids(self, figure_model: 'FigureModel') -> None:
        if figure_model.id_local_db:
            self._playbook.remove_deleted_item_ids('figures', StorageType.LOCAL_DB, figure_model.id_local_db)
        if figure_model.id_api:
            self._playbook.remove_deleted_item_ids('figures', StorageType.API, figure_model.id_api)

    @log_method_decorator()
    def add_deleted_labels_ids(self, label_model: 'LabelModel') -> None:
        if label_model.id_local_db:
            self._playbook.add_deleted_item_ids('labels', StorageType.LOCAL_DB, label_model.id_local_db)
        if label_model.id_api:
            self._playbook.add_deleted_item_ids('labels', StorageType.API, label_model.id_api)

    @log_method_decorator()
    def remove_deleted_labels_ids(self, label_model: 'LabelModel') -> None:
        if label_model.id_local_db:
            self._playbook.remove_deleted_item_ids('labels', StorageType.LOCAL_DB, label_model.id_local_db)
        if label_model.id_api:
            self._playbook.remove_deleted_item_ids('labels', StorageType.API, label_model.id_api)

    @log_method_decorator()
    def add_deleted_pencil_lines_ids(self, pencil_line_model: 'PencilLineModel') -> None:
        if pencil_line_model.id_local_db:
            self._playbook.add_deleted_item_ids('pencil_lines', StorageType.LOCAL_DB, pencil_line_model.id_local_db)
        if pencil_line_model.id_api:
            self._playbook.add_deleted_item_ids('pencil_lines', StorageType.API, pencil_line_model.id_api)

    @log_method_decorator()
    def remove_deleted_pencil_lines_ids(self, pencil_line_model: 'PencilLineModel') -> None:
        if pencil_line_model.id_local_db:
            self._playbook.remove_deleted_item_ids('pencil_lines', StorageType.LOCAL_DB, pencil_line_model.id_local_db)
        if pencil_line_model.id_api:
            self._playbook.remove_deleted_item_ids('pencil_lines', StorageType.API, pencil_line_model.id_api)

    @log_method_decorator()
    def add_deleted_players_ids(self, player_model: 'PlayerModel') -> None:
        if player_model.id_local_db:
            self._playbook.add_deleted_item_ids('players', StorageType.LOCAL_DB, player_model.id_local_db)
        if player_model.id_api:
            self._playbook.add_deleted_item_ids('players', StorageType.API, player_model.id_api)

    @log_method_decorator()
    def remove_deleted_players_ids(self, player_model: 'PlayerModel') -> None:
        if player_model.id_local_db:
            self._playbook.remove_deleted_item_ids('players', StorageType.LOCAL_DB, player_model.id_local_db)
        if player_model.id_api:
            self._playbook.remove_deleted_item_ids('players', StorageType.API, player_model.id_api)

    @log_method_decorator()
    def add_deleted_actions_ids(self, action_model: 'ActionModel') -> None:
        if action_model.id_local_db:
            self._playbook.add_deleted_item_ids('actions', StorageType.LOCAL_DB, action_model.id_local_db)
        if action_model.id_api:
            self._playbook.add_deleted_item_ids('actions', StorageType.API, action_model.id_api)

    @log_method_decorator()
    def remove_deleted_actions_ids(self, action_model: 'ActionModel') -> None:
        if action_model.id_local_db:
            self._playbook.remove_deleted_item_ids('actions', StorageType.LOCAL_DB, action_model.id_local_db)
        if action_model.id_api:
            self._playbook.remove_deleted_item_ids('actions', StorageType.API, action_model.id_api)
