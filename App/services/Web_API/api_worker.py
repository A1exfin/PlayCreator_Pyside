import json
from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass, field

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PySide6.QtCore import QObject, Signal, QMutexLocker

import Core
from Core.settings import WebAppUrls
from Core.Enums import RequestMethod

if TYPE_CHECKING:
    from Core.constants import API_MUTEX


@dataclass
class ApiRequest:
    url: str
    method: RequestMethod
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
    requestFinished = Signal(object)  # ApiResponse
    requestFailed = Signal(str)
    requestProgress = Signal()
    sendRequest = Signal(object)

    def __init__(self, mutex: 'API_MUTEX'):
        super().__init__()
        self._mutex = mutex
        self._session = self._setup_session()
        self.sendRequest.connect(self.send_request)

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
                response = self._session.request(request.method.value, request.url,
                                                 headers=request.headers, json=request.data)
            else:
                response = self._session.request(request.method.value, request.url,
                                                 headers=request.headers)

            response.raise_for_status()

            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {'text': response.text}
            return ApiResponse(success=True, data=result, status_code=response.status_code)
        except requests.exceptions.RequestException as e:
            error_message = f'Ошибка запроса: {str(e)}.'
            return ApiResponse(success=False, errors=error_message,
                               status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
        except Exception as e:
            error_type = type(e).__name__
            error_message = repr(e)
            return ApiResponse(success=False, errors=f'Ошибка: {error_type}\n{error_message}.')

    def send_request(self, request: 'ApiRequest') -> None:
        with QMutexLocker(self._mutex):
            result = self._execute_request(request)
            if result.success:
                self.requestFinished.emit(result)
            else:
                self.requestFailed.emit(result.errors)

    # @Slot()
    # def _execute_request(self, url: str, method: 'RequestMethod', data: dict = None, headers: dict = None) -> 'ApiResponse':
    #     print(f'worker _execute_request {url= }, {method = }')
    #     try:
    #         if data:
    #             response = self._session.request(method, url, json=data)
    #         else:
    #             response = self._session.request(method, url)
    #
    #         response.raise_for_status()
    #
    #         try:
    #             result = response.json()
    #         except json.JSONDecodeError:
    #             result = {'text': response.text}
    #         return ApiResponse(True, data=result, status_code=response.status_code)
    #     except requests.exceptions.RequestException as e:
    #         error_message = f'Ошибка запроса: {str(e)}.'
    #         return ApiResponse(False, errors=error_message,
    #                            status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    #     except Exception as e:
    #         self.requestFailed.emit(f'Неизвестная ошибка: {str(e)}')

    # def send_request(self, url: str = WebAppUrls.api_login, method: 'RequestMethod' = 'POST', data: dict = None, headers: dict = None) -> None:
    #     result = self._execute_request(url, method, data, headers)
    #     print(f'{result = }')
    #     if result.success:
    #         self.requestFinished.emit(result)
    #     else:
    #         self.requestFailed.emit(result.errors)
