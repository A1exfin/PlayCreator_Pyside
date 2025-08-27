from typing import TYPE_CHECKING, Callable, Optional, Any, Final
import sys
import functools
import traceback
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

import Core
from PySide6.QtWidgets import QMessageBox
# from Views.Dialog_windows import DialogInfo

if TYPE_CHECKING:
    pass

__all__ = ('logger', 'log_method')

LOG_DIR = Path.home() / '.PlayCreator_desktop' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'PlayCreator_{datetime.now().strftime("%d-%m-%Y")}.log'

DEBUG_1: Final = logging.DEBUG + 1
INFO_1: Final = logging.INFO + 1

logging.addLevelName(DEBUG_1, 'DEBUG_1')
logging.addLevelName(INFO_1, 'INFO_1')


class ConsoleFilter(logging.Filter):
    def filter(self, record: 'logging.LogRecord') -> bool:
        return record.levelno in (logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, INFO_1)


class FileFilter(logging.Filter):
    def filter(self, record: 'logging.LogRecord') -> bool:
        return record.levelno != INFO_1


class CustomLogger:
    def __init__(self):
        self._logger = logging.getLogger('PlayCreator_PySide')
        self._setup_logger()

    def _setup_logger(self):
        """Настройка логгера с обработчиками файла и консоли."""
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        message_format = '%(asctime)s - %(name)s - %(levelname)s'

        logging_formatter = logging.Formatter(
            f'{message_format:-<50} %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10_000_000,
            backupCount=10,
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
            # dialog_info = DialogInfo('Критическая ошибка', f'{exc_type.__name__}: {exc_value}', parent=None,
            #                          check_box=False, decline_button=False, accept_button_text='ОК')
            dialog_info = QMessageBox(QMessageBox.Icon.Critical,
                                      'Критическая ошибка', f'{exc_type.__name__}: {exc_value}', parent=None)
            dialog_info.addButton('ОК', QMessageBox.AcceptRole)
            dialog_info.exec()
        except Exception as e:
            self._logger.error(f'Ошибка при показе диалога: {e}')

    def log_method_to_file(self, extra_message: Optional[str] = None):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                instance = args[0]
                class_name = instance.__class__.__name__
                method_name = func.__name__
                start_method_message = f'-> {class_name}.{method_name} <- '
                self._logger.log(
                    INFO_1, f'{start_method_message} "{extra_message}"' if extra_message else start_method_message
                )
                self._logger.log(
                    DEBUG_1, f'{start_method_message} "{extra_message}" with\nargs: {args[1:]}\nkwargs: {kwargs}'
                    if extra_message else start_method_message + f'with\nargs: {args[1:]}\nkwargs: {kwargs}'
                )
                # self._logger.info(f'{start_method_message} "{extra_message}" with args: {args[1:]}; kwargs: {kwargs}')
                try:
                    start_time = datetime.now()
                    result = func(*args, **kwargs)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    success_message = f'SUCCESS: {class_name}.{method_name} completed in {execution_time: .3f}s'
                    if result:
                        success_message += f' returning {result}'
                    if execution_time > 0.1:
                        self._logger.warning(f'!!!SLOW {success_message}')
                    else:
                        self._logger.debug(success_message)
                    return result
                except Exception as e:
                    error_message = f'FAILED: {class_name}.{method_name} with args: {args[1:]}, kwargs: {kwargs}. {str(e)}'
                    self._logger.error(error_message)
                    self._logger.exception(e)
                    raise
            return wrapper
        return decorator


custom_logger = CustomLogger()

#Логгер
logger = custom_logger.get_logger()

# Декораторы
log_method = custom_logger.log_method_to_file
