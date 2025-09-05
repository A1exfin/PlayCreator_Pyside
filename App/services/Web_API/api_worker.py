import json
from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass, field

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PySide6.QtCore import QObject, Signal

import Core
from Core.settings import WebAppUrls
from Core.Enums import RequestMethods

if TYPE_CHECKING:
    pass


@dataclass
class ApiRequest:
    url: str
    method: RequestMethods
    cookies: Optional[dict[str, str]] = field(default_factory=dict)
    headers: Optional[dict[str, str]] = field(default_factory=dict)
    data: Optional[dict[str, Any]] = field(default_factory=dict)


@dataclass
class ApiResponse:
    success: bool
    data: Optional[dict[str, Any]] = None
    errors: Optional[str] = None
    status_code: Optional[int] = None


class ApiWorker(QObject):
    requestStarted = Signal()
    requestFinished = Signal(dict)
    requestFailed = Signal(str)
    requestProgress = Signal()

    def __init__(self):
        super().__init__()
        self._session = self._setup_session()

    def _setup_session(self) -> 'requests.Session':
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.verify = not Core.DEBUG
        if Core.DEBUG:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return session

    def _execute_request(self, request: 'ApiRequest') -> 'ApiResponse':
        try:
            if request.data:
                response = self._session.request(request.method, request.url, json=request.data)
            else:
                response = self._session.request(request.method, request.url)

            response.raise_for_status()

            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {'text': response.text}
            return ApiResponse(True, data=result, status_code=response.status_code)
        except requests.exceptions.RequestException as e:
            error_message = f'Ошибка запроса: {str(e)}.'
            return ApiResponse(False, errors=error_message,
                               status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
        except Exception as e:
            self.requestFailed.emit(f'Неизвестная ошибка: {str(e)}')

    def send_request(self, request: 'ApiRequest') -> None:
        result = self._execute_request(request)
        if result.success:
            self.requestFinished.emit(result)
        else:
            self.requestFailed.emit(result.errors)
