from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine

# from .repository.playbook_repository import PlaybookManager

# __all__ = ('get_session', 'PlaybookManager', 'Base')

from Config import DB_URL

engine = create_engine(
    url=DB_URL,
    echo=True
)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


session_factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


class Base(DeclarativeBase):
    pass


# @contextmanager
def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
