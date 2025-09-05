from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject

if TYPE_CHECKING:
    pass


class UserModel(QObject):
    def __init__(self, user_id: int, name: str, email: str):
        super().__init__()
        self._user_id = user_id
        self._name = name
        self._email = email

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email


