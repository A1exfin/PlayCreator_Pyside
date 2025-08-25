from typing import TYPE_CHECKING, Callable, Optional, Any, Final
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import functools
from datetime import datetime

import Core
from Views.Dialog_windows import DialogInfo

if TYPE_CHECKING:
    from logging import LogRecord

__all__ = ('logger', 'log_method')

LOG_DIR = Path.home() / '.PlayCreator_Pyside' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'PlayCreator_{datetime.now().strftime("%Y%m%d")}.log'

FILE_ONLY: Final = logging.DEBUG + 1
CONSOLE_ONLY: Final = logging.INFO + 1

logging.addLevelName(FILE_ONLY, 'DEBUG_1')
logging.addLevelName(CONSOLE_ONLY, 'INFO_1')


class ConsoleFilter(logging.Filter):
    def filter(self, record: 'LogRecord') -> bool:
        return record.levelno in (logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, CONSOLE_ONLY)


class FileFilter(logging.Filter):
    def filter(self, record: 'LogRecord') -> bool:
        return record.levelno in (logging.DEBUG, logging.DEBUG, logging.INFO, logging.ERROR, logging.CRITICAL, FILE_ONLY)


class LoggerFactory:
    def __init__(self):
        self._logger = logging.getLogger('PlayCreator_PySide')
        self._setup_logger()

    def _setup_logger(self):
        """Настройка логгера с обработчиками файла и консоли."""
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        logging_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=5_000_000,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging_formatter)
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(FileFilter())
        self._logger.addHandler(file_handler)

        if Core.DEBUG:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging_formatter)
            console_handler.setLevel(logging.INFO)
            console_handler.addFilter(ConsoleFilter())
            self._logger.addHandler(console_handler)

        sys.excepthook = self.handle_exception

    def get_logger(self) -> logging.Logger:
        return self._logger

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Обработчик необработанных исключений."""
        self._logger.critical(
            'Необработанное исключение',
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        try:
            dialog_info = DialogInfo('Критическая ошибка', f'{exc_type.__name__}: {exc_value}', parent=None,
                                     check_box=False, decline_button=False, accept_button_text='ОК')
            dialog_info.exec()
        except Exception as e:
            self._logger.error(f'Ошибка при показе диалога: {e}')

    def log_method(self, extra_message: Optional[str] = None):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                instance = args[0]
                class_name = instance.__class__.__name__
                method_name = func.__name__
                start_method_message = f' -> {class_name}.{method_name}'
                self._logger.log(
                    FILE_ONLY, start_method_message + extra_message + f'with args: {args[1:]}, kwargs: {kwargs}'
                    if extra_message else start_method_message + f'with args: {args[1:]}, kwargs: {kwargs}'
                )
                self._logger.log(
                    CONSOLE_ONLY, start_method_message + extra_message if extra_message else start_method_message
                )
                try:
                    start_time = datetime.now()
                    result = func(*args, **kwargs)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    success_message = f'SUCCESS: {class_name}.{method_name} completed in {execution_time: .3f}s'
                    if execution_time > 0.1:
                        self._logger.warning('!!!SLOW ' + success_message)
                    else:
                        self._logger.log(FILE_ONLY, success_message)
                    return result
                except Exception as e:
                    error_message = f'FAILED: {class_name}.{method_name} with args: {args[1:]}, kwargs: {kwargs}. {str(e)}'
                    self._logger.error(error_message)
                    raise
            return wrapper
        return decorator


logger_factory = LoggerFactory()

logger = logger_factory.get_logger()

# Декораторы
log_method = logger_factory.log_method
