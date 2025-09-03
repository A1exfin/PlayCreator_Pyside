from typing import TYPE_CHECKING

import requests
from PySide6.QtCore import QThread

import Core
from Core.settings import APIEndpoints

if TYPE_CHECKING:
    pass


class APIWorker(QThread):
    pass