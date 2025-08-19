from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field
from uuid import uuid4, UUID

from PySide6.QtCore import Signal
from Config.Enums import StorageType
from .playbook_access_settings_model import PlaybookAccessSettingsModel
from .base_model import BaseModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject
    from Config.Enums import PlaybookType, PlaybookAccessOptions
    from scheme_model import SchemeModel

__all__ = ('PlaybookModel', )


@dataclass
class DeletedPlaybookItems:
    schemes: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})
    figures: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})
    labels: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})
    pencil_lines: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})
    players: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})
    actions: dict[StorageType, list[int]] = field(default_factory=lambda: {t: [] for t in StorageType})

    def __repr__(self):
        return f'schemes:\n\tlocal_db: {self.schemes[StorageType.LOCAL_DB]}\n\tapi: {self.schemes[StorageType.API]}'\
               f'\nplayers: \n\tlocal_db: {self.players[StorageType.LOCAL_DB]}\n\tapi: {self.players[StorageType.API]}'\
               f'\nactions: \n\tlocal_db: {self.actions[StorageType.LOCAL_DB]}\n\tapi: {self.actions[StorageType.API]}'\
               f'\nfigures:\n\tlocal_db: {self.figures[StorageType.LOCAL_DB]}\n\tapi: {self.figures[StorageType.API]}'\
               f'\nlabels: \n\tlocal_db: {self.labels[StorageType.LOCAL_DB]}\n\tapi: {self.labels[StorageType.API]}'\
               f'\npencil_lines: \n\tlocal_db: {self.pencil_lines[StorageType.LOCAL_DB]}\n\tapi: {self.pencil_lines[StorageType.API]}'


class PlaybookModel(BaseModel):
    nameChanged = Signal(str)
    infoChanged = Signal(str)
    schemeAdded = Signal(object)  # SchemeModel
    schemeRemoved = Signal(object)  # removed SchemeModel
    schemeMoved = Signal(int, int)

    def __init__(self, name: str, playbook_type: 'PlaybookType', info: str = '', uuid: Optional['UUID'] = None,
                 id_local_db: Optional[int] = None, id_api: Optional[int] = None, team_fk: Optional[int] = None,
                 parent: Optional['QObject'] = None):
        super().__init__(parent, uuid, id_local_db, id_api)
        self._name = name
        self._playbook_type = playbook_type
        self._info = info
        self._team_fk = team_fk
        self._settings = PlaybookAccessSettingsModel()
        self._schemes: list['SchemeModel'] = list()
        self._deleted_items: 'DeletedPlaybookItems' = DeletedPlaybookItems()

    @property
    def team_fk(self) -> int:
        return self._team_fk

    @team_fk.setter
    def team_fk(self, team_fk: int) -> None:
        self._team_fk = team_fk

    def set_new_uuid_for_all_items(self) -> None:
        self.set_new_uuid()
        self._set_schemes_new_uuid()

    def _set_schemes_new_uuid(self) -> None:
        for scheme_model in self._schemes:
            scheme_model.set_new_uuid()

    def reset_id_for_all_items(self, storage_type: 'StorageType') -> None:
        self.reset_id(storage_type)
        self._reset_schemes_id(storage_type)

    def _reset_schemes_id(self, storage_type: 'StorageType') -> None:
        for scheme_model in self._schemes:
            scheme_model.reset_id(storage_type)

    def reset_changed_flag(self) -> None:
        super().reset_changed_flag()

    def _reset_schemes_changed_flag(self) -> None:
        for scheme in self._schemes:
            scheme.reset_changed_flag()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        self._changed = True
        self.nameChanged.emit(name)

    @property
    def info(self) -> str:
        return self._info

    @info.setter
    def info(self, info: str) -> None:
        self._info = info
        self._changed = True
        self.infoChanged.emit(info)

    @property
    def playbook_type(self) -> 'PlaybookType':
        return self._playbook_type

    @property
    def who_can_edit(self) -> 'PlaybookAccessOptions':
        return self._settings.who_can_edit

    @who_can_edit.setter
    def who_can_edit(self, value: 'PlaybookAccessOptions') -> None:
        self._settings.who_can_edit = value

    @property
    def who_can_see(self) -> 'PlaybookAccessOptions':
        return self._settings.who_can_see

    @who_can_see.setter
    def who_can_see(self, value: 'PlaybookAccessOptions') -> None:
        self._settings.who_can_see = value

    @property
    def settings(self) -> 'PlaybookAccessSettingsModel':
        return self._settings

    @property
    def schemes(self) -> list['SchemeModel']:
        return self._schemes.copy()

    def add_scheme(self, scheme_model: 'SchemeModel', row_index: Optional[int] = None) -> None:
        if row_index:
            self._schemes.insert(row_index, scheme_model)
        else:
            self._schemes.append(scheme_model)
        self._changed = True
        self.schemeAdded.emit(scheme_model)

    def remove_scheme(self, scheme_model: 'SchemeModel') -> None:
        if scheme_model.id_local_db:
            self.add_deleted_item_ids('schemes', StorageType.LOCAL_DB, scheme_model.id_local_db)
        if scheme_model.id_api:
            self.add_deleted_item_ids('schemes', StorageType.API, scheme_model.id_api)
        self._schemes.remove(scheme_model)
        self._changed = True
        self.schemeRemoved.emit(scheme_model)

    def move_up_scheme(self, view_index: int, scheme_model: 'SchemeModel') -> None:
        scheme_index = self._schemes.index(scheme_model)
        if view_index != scheme_index:
            raise ValueError('Индексы представления и модели не совпадают.')
        last_index = view_index
        if last_index > 0:
            new_index = last_index - 1
            self._schemes[last_index], self._schemes[new_index] = self._schemes[new_index], self._schemes[last_index]
        else:
            scheme = self._schemes.pop(last_index)
            self._schemes.append(scheme)
            new_index = self._schemes.index(scheme)
        self._changed = True
        self.schemeMoved.emit(last_index, new_index)

    def move_down_scheme(self, view_index: int, scheme_model: 'SchemeModel') -> None:
        scheme_index = self._schemes.index(scheme_model)
        if view_index != scheme_index:
            raise ValueError('Индексы представления и модели не совпадают.')
        last_index = view_index
        if last_index < len(self._schemes) - 1:
            new_index = last_index + 1
            self._schemes[last_index], self._schemes[new_index] = self._schemes[new_index], self._schemes[last_index]
        else:
            scheme_model = self._schemes.pop(last_index)
            self._schemes.insert(0, scheme_model)
            new_index = self._schemes.index(scheme_model)
        self._changed = True
        self.schemeMoved.emit(last_index, new_index)

    def add_deleted_item_ids(self, item_type: str, storage_type: 'StorageType', ids: list[int] | int) -> None:
        """
        Добавляет id удалённых итемов в хранилище для удаления этих итемов из БД при сохранении плейбука.
        Аргументы:
            item_type: Тип итема ('schemes', 'figures', 'labels', 'pencil_lines', 'players', 'actions')
            storage: Тип хранилища (StorageType.LOCAL_DB or StorageType.API)
            ids_lst: Список целых чисел, для добавления в список id удаляемых итемов
        """
        # print('add_deleted_item_ids')
        # print(f'{item_type = }, {storage_type = }, {ids = }')
        if not hasattr(self._deleted_items, item_type):
            raise ValueError(f'Unknown item type: {item_type}')
        if isinstance(ids, list):
            getattr(self._deleted_items, item_type)[storage_type].extend(ids)
        if isinstance(ids, int):
            getattr(self._deleted_items, item_type)[storage_type].append(ids)
        # print(f'{self.get_deleted_item_ids(item_type, storage_type) = }')

    def remove_deleted_item_ids(self, item_type: str, storage_type: 'StorageType', ids: list[int] | int) -> None:
        # print('remove_deleted_item_ids')
        # print(f'{item_type = }, {storage_type = }, {ids = }')
        if not hasattr(self._deleted_items, item_type):
            raise ValueError(f'Unknown item type: {item_type}')
        deleted_items_ids = getattr(self._deleted_items, item_type)[storage_type]
        if isinstance(ids, int):
            deleted_items_ids.remove(ids)
        if isinstance(ids, list):
            for id in ids:
                deleted_items_ids.remove(id)
        # print(f'{self.get_deleted_item_ids(item_type, storage_type) = }')

    @property
    def deleted_items(self) -> 'DeletedPlaybookItems':
        return self._deleted_items

    def get_deleted_item_ids(self, item_type: str, storage_type: 'StorageType') -> list[int]:
        return getattr(self._deleted_items, item_type)[storage_type].copy()

    def clear_all_deleted_item_ids(self) -> None:
        self._deleted_items = DeletedPlaybookItems()

    def clear_deleted_item_ids(self, storage_type: 'StorageType') -> None:
        self._deleted_items.schemes[storage_type].clear()
        self._deleted_items.figures[storage_type].clear()
        self._deleted_items.labels[storage_type].clear()
        self._deleted_items.pencil_lines[storage_type].clear()
        self._deleted_items.players[storage_type].clear()
        self._deleted_items.actions[storage_type].clear()

    def to_dict(self) -> dict:
        return {'uuid': self._uuid, 'name': self._name, 'playbook_type': self._playbook_type, 'info': self._info,
                'schemes': list(),
                'deleted_schemes': list(),
                'deleted_figures': list(),
                'deleted_labels': list(),
                'deleted_pencil_lines': list(),
                'deleted_players': list(),
                'deleted_actions': list()}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} (id_local_db: {self._id_local_db}; id_api: {self._id_api}; ' \
               f'uuid: {self._uuid}; name: {self._name}; playbook_type: {self._playbook_type}; ' \
               f'info: {self._info}) at {hex(id(self))}' \
               f'\n\t schemes: {self._schemes}>'