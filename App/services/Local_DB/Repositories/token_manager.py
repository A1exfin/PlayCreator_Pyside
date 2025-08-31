from typing import TYPE_CHECKING, Optional

import keyring
from cryptography.fernet import Fernet
from sqlalchemy import text, bindparam, inspect

import Core
from Core.logger_settings import log_method, logger
from .base_manager import BaseManager

if TYPE_CHECKING:
    pass

__all__ = ('AuthTokenManager',)


class AuthTokenManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._cipher = self._get_cipher()

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

    def _get_cipher(self) -> 'Fernet':
        secret_key = keyring.get_password(Core.APP_NAME, Core.SECRET_KEY_NAME)
        if secret_key is None:
            secret_key = self._get_new_secret_key()
            keyring.set_password(Core.APP_NAME, Core.SECRET_KEY_NAME, secret_key)
        return Fernet(secret_key)

    def _get_new_secret_key(self) -> str:
        return Fernet.generate_key().decode()