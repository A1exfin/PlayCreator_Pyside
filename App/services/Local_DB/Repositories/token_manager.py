from typing import TYPE_CHECKING, Optional

from sqlalchemy import text, bindparam, inspect

from Core.logger_settings import log_method, logger
from .base_manager import BaseManager

if TYPE_CHECKING:
    pass

__all__ = ('AuthTokenManager',)


class AuthTokenManager(BaseManager):
    def __init__(self):
        super().__init__()

    def check_token(self) -> bool:
        with self.start_transaction():
            query = text('SELECT EXISTS(SELECT 1 FROM auth_token);')
            result = self.session.execute(query)
            return result

    def get_token(self) -> Optional[str]:
        with self.start_transaction():
            query = text('SELECT auth_token FROM auth_token LIMIT 1;')
            result = self.session.execute(query)
            return result.first()

    def save_token(self, token: str) -> None:
        with self.start_transaction():
            query = text('''DELETE from auth_token;
                         INSERT OR IGNORE INTO auth_token (token) VALUES (:token);''')
            self.session.execute(query, {'token': token})

    def delete_token(self) -> None:
        with self.start_transaction():
            query = text('DELETE from auth_token;')
            self.session.execute(query)


