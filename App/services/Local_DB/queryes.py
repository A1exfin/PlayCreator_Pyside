import os
from sqlalchemy import text

from Config import DB_URL
from services.Local_DB import engine
from services.Local_DB import Base, session_factory



# if TYPE_CHECKING:



def drop_tables() -> None:
    Base.metadata.drop_all(engine)  # для отладки


def check_db_is_created() -> bool:
    return os.path.exists(DB_URL)


def create_db_if_not_exists() -> None:
    if not check_db_is_created():
        Base.metadata.create_all(engine)

