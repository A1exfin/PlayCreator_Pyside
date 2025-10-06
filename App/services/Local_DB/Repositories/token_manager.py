from typing import TYPE_CHECKING, Optional

from sqlalchemy import text

from Core.logger_settings import log_method, logger
from .base_manager import BaseManager
from ..cipher import Cipher

if TYPE_CHECKING:
    pass

__all__ = ('AuthTokenManager',)


class AuthTokenManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._cipher = Cipher.get_cipher()

    def check_token(self) -> bool:
        with self.start_transaction():
            query = text('SELECT EXISTS(SELECT 1 FROM auth_token);')
            result = self.session.execute(query).first()
            return bool(result[0])

    def get_token(self) -> Optional[str]:
        with self.start_transaction():
            query = text('SELECT token FROM auth_token LIMIT 1;')
            result = self.session.execute(query).first()
            if result:
                auth_token = self._cipher.decrypt(result[0]).decode()
                return auth_token
            return None

    def save_token(self, token: str) -> None:
        with self.start_transaction():
            query = text('DELETE from auth_token;')
            self.session.execute(query)
            query = text('INSERT OR IGNORE INTO auth_token (token) VALUES (:token);')
            self.session.execute(query, {'token': self._cipher.encrypt(token.encode())})

    def delete_token(self) -> None:
        with self.start_transaction():
            query = text('DELETE from auth_token;')
            self.session.execute(query)

