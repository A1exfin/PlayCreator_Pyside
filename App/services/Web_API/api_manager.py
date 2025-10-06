from typing import TYPE_CHECKING, Optional, Any
from contextlib import contextmanager

from PySide6.QtCore import QObject, Signal, QThread, QMetaObject, Qt, Q_ARG, QGenericArgumentHolder, QMutex, QWaitCondition, QMutexLocker, QByteArray

import Core
from Core.Enums import RequestMethod
from Core.settings import WebAppUrls
from .api_worker import ApiWorker, ApiRequest

if TYPE_CHECKING:
    pass


class RequestsManager(QObject):
    requestStarted = Signal()
    requestFinished = Signal(object)  # ApiResponse
    requestFailed = Signal(str)
    requestProgress = Signal()

    def __init__(self, api_mutex: 'QMutex'):
        super().__init__()
        self._wait_condition = QWaitCondition()  ################
        # self._worker = Worker()
        self._worker = ApiWorker(api_mutex)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._connect_worker_signals()
        self._thread.start()
        print(f'{self._thread.isRunning() = }')

    @property
    def thread(self) -> 'QThread':
        return self._thread

    def _connect_worker_signals(self):
        ...
        self._worker.requestFinished.connect(lambda data: print(f'1111{data = }'))
        self._worker.requestFinished.connect(lambda data: self.requestFinished.emit(data))
        self._worker.requestFailed.connect(lambda error_message: print(f'1111{error_message = }'))
        self._worker.requestFailed.connect(lambda error_message: self.requestFailed.emit(error_message))

    # def _send_request(self, request: 'ApiRequest') -> None:
    #     QMetaObject.invokeMethod(
    #         self._worker,
    #         'send_request',
    #         Qt.ConnectionType.DirectConnection,
    #         Q_ARG(object, request)
    #     )

    def _send_request(self, request: 'ApiRequest') -> None:
        self._worker.sendRequest.emit(request)

    def _get_headers(self, token: Optional[str] = None,) -> dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'{Core.APP_NAME}/{Core.VERSION}'
        }
        if token:
            headers['Authorization'] = f'Token {token}'
        return headers

    def _get_cookies(self) -> dict[str, str]:
        pass

    def get(self, endpoint: str, token: Optional[str] = None) -> None:
        request = ApiRequest(
            endpoint,
            method=RequestMethod.GET,
            headers=self._get_headers(token=token)
        )
        self._send_request(request)

    def post(self, endpoint: str, token: Optional[str] = None, data: Optional[dict] = None) -> None:
        request = ApiRequest(endpoint, method=RequestMethod.POST, headers=self._get_headers(token), data=data)
        self._send_request(request)

    def login(self, username_email: str, password: str) -> None:
        self.post(WebAppUrls.api_login, data={'username': username_email, 'password': password})

    def logout(self, token: str) -> None:
        self.post(WebAppUrls.api_logout, token=token)

    def get_current_user_info(self, token: str) -> None:
        self.get(WebAppUrls.api_user_info, token=token)

    def get_playbook(self, token: str) -> None:
        pass

    def delete_playbook(self, token: str, playbook_id: int) -> None:
        pass

    def save_playbook(self, token: str, playbook_data) -> None:
        pass

    def save_playbook_as(self, token: str, playbook_data) -> None:
        pass