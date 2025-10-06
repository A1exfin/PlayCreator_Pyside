from typing import Final

from PySide6.QtCore import QMutex

__all__ = ('ORGANIZATION', 'APP_NAME', 'VERSION', 'SECRET_KEY_NAME')

ORGANIZATION: Final[str] = 'alexfin_dev'

APP_NAME: Final[str] = 'PlayCreator_desktop'

VERSION: Final[str] = '4.0'

SECRET_KEY_NAME: Final[str] = 'local_DB_encryption_key'

API_MUTEX: Final['QMutex'] = QMutex()