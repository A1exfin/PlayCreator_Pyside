import threading
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine

from Config import DB_URL
from .Models.base import Base

__all__ = ('session_factory', )


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


class LocalDBSessionFactory:
    def __init__(self, echo: bool = False):
        self._engine = create_engine(DB_URL, echo=echo)
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.ScopedSession = scoped_session(
            self._session_factory,
            scopefunc=threading.get_ident
        )

    @contextmanager
    def get_session(self) -> 'scoped_session':
        session = self.ScopedSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self) -> None:
        if not os.path.exists(DB_URL):
            Base.metadata.create_all(self._engine)

    def drop_tables(self) -> None:
        Base.metadata.drop_all(self._engine)


session_factory = LocalDBSessionFactory(echo=False)