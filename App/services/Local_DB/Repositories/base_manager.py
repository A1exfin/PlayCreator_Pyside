from typing import TYPE_CHECKING
from contextlib import contextmanager

from ..session import session_factory

if TYPE_CHECKING:
    from sqlalchemy.orm import scoped_session


class BaseManager:
    def __init__(self):
        self._session_factory = session_factory
        self._session = None

    @property
    def session(self) -> 'scoped_session':
        if self._session is None:
            raise RuntimeError('Сессия не активна. Начните транзакцию.')
        return self._session

    @contextmanager
    def start_transaction(self) -> None:
        with self._session_factory.get_session() as session:
            self._session = session
            try:
                yield
            finally:
                self._session = None
