import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import functools
import time
from typing import Callable, Optional, Any
from datetime import datetime

import Core
from Views.Dialog_windows import DialogInfo

__all__ = ('logger', 'log_method', 'log_performance')

LOG_DIR = Path.home() / '.PlayCreator_Pyside' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'PlayCreator_{datetime.now().strftime("%Y%m%d")}.log'


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('PlayCreator_PySide')
        self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        """Настройка логгера с обработчиками файла и консоли."""
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

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
        self.logger.addHandler(file_handler)

        if Core.DEBUG:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging_formatter)
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)

        sys.excepthook = self.handle_exception

        return self.logger

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Обработчик необработанных исключений."""
        self.logger.critical(
            'Необработанное исключение',
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        try:
            dialog_info = DialogInfo('Критическая ошибка', f'{exc_type.__name__}: {exc_value}', parent=None,
                                     check_box=False, decline_button=False, accept_button_text='ОК')
            dialog_info.exec()
        except Exception as e:
            self.logger.error(f'Ошибка при показе диалога: {e}')

    def log_method_call(self, func: Callable) -> Callable:
        """
        Декоратор для логирования вызовов методов.
        Автоматически логирует начало и конец выполнения методов,
        а также перехватывает и логирует исключения.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__ if args else 'UnknownClass'
            self.logger.debug(f'Вызов метода: {class_name}.{func.__name__}, args: {args[1:]}, kwargs: {kwargs}')
            result = func(*args, **kwargs)
            self.logger.debug(f'Метод {class_name}.{func.__name__} выполнен успешно')
            return result
        return wrapper

    def log_performance(self, func: Callable) -> Callable:
        """Декоратор для логирования времени выполнения методов."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            class_name = args[0].__class__.__name__ if args else 'UnknownClass'
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 0.1:  # Логируются только медленные методы
                self.logger.warning(f'Метод {class_name}.{func.__name__} выполнялся: {execution_time:.3f} сек')
            else:
                self.logger.debug(f'Метод {class_name}.{func.__name__} выполнялся: {execution_time:.3f} сек')
            return result
        return wrapper

    def log_signal(self, signal_name: str, *args) -> None:
        """Логирование сигналов PySide."""
        self.logger.debug(f'Сигнал испущен: {signal_name} - аргументы: {args}')

    def log_ui_action(self, widget_name: str, action: str, details: str = "") -> None:
        """Логирование действий пользователя в UI."""
        self.logger.info(f'UI действие: {widget_name} - {action} {details}')


my_logger = Logger()

logger = my_logger.logger
# Декораторы
log_method = my_logger.log_method_call
log_performance = my_logger.log_performance
