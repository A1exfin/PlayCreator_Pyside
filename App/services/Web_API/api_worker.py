from typing import TYPE_CHECKING, Optional, Any
import json

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PySide6.QtCore import QObject, Signal

import Core
from Core.settings import APIEndpoints

if TYPE_CHECKING:
    pass


class APIWorker(QObject):
    requestStarted = Signal()
    requestFinished = Signal()
    requestFailed = Signal()
    requestProgress = Signal()

    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

        if Core.DEBUG:
            self._session.verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def send_request(self, url: str, method: str, data: Optional[dict] = None):
        try:
            if data:
                response = self._session.request(method, url, data=data)
            else:
                response = self._session.request(method, url)
            response.raise_for_status()

            try:
                result = response.json()
            except result.JSONDecodeError:
                result = {'text': response.text}
            self.requestFinished.emit(result)
        except requests.exceptions.RequestException as e:
            self.requestFailed.emit(f'Ошибка запроса: {str(e)}')
        except Exception as e:
            self.requestFailed.emit(f'Неизвестная ошибка: {str(e)}')