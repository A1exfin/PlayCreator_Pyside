import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from Views.Dialog_windows import DialogInfo

LOG_DIR = Path.home()/'.PlayCreator_Pyside'/'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'PlayCreator.log'


def setup_logger():
    logger = logging.getLogger('PlayCreator_PySide')
    logger.setLevel(logging.DEBUG)

    logging_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging_formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    sys.excepthook = handle_exception
    return logger


def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error(
        'Необработанное исключение', exc_info=(exc_type, exc_value, exc_traceback)
    )
    dialog_info = DialogInfo('Критическая ошибка', f'{exc_type.__name__}: {exc_value}', parent=None, check_box=False,
                             decline_button=False, accept_button_text='ОК')
    dialog_info.exec()


logger = setup_logger()