from typing import TYPE_CHECKING, Optional

from Config.Enums import PlaybookAccessOptions


__all__ = ('PlaybookAccessSettingsModel', )


class PlaybookAccessSettingsModel:
    def __init__(self, who_can_edit: 'PlaybookAccessOptions' = PlaybookAccessOptions.TEAM_MANAGEMENT,
                 who_can_see: 'PlaybookAccessOptions' = PlaybookAccessOptions.REGULAR_TEAM_PLAYERS):
        self._who_can_edit = who_can_edit
        self._who_can_see = who_can_see

    @property
    def who_can_edit(self) -> 'PlaybookAccessOptions':
        return self._who_can_edit

    @who_can_edit.setter
    def who_can_edit(self, value: 'PlaybookAccessOptions') -> None:
        self._who_can_edit = value

    @property
    def who_can_see(self) -> 'PlaybookAccessOptions':
        return self._who_can_see

    @who_can_see.setter
    def who_can_see(self, value: 'PlaybookAccessOptions') -> None:
        self._who_can_see = value

    def to_dict(self):
        return {'who_can_edit': self._who_can_edit,
                'who_can_see': self._who_can_see}