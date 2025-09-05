from typing import TYPE_CHECKING, Optional, Any

from PySide6.QtCore import QObject, Signal, QThread, QMetaObject, Qt, Q_ARG

import Core
from Core.Enums import RequestMethod
from Core.settings import WebAppUrls
from .api_worker import ApiWorker, ApiRequest

if TYPE_CHECKING:
    pass


class RequestsManager(QObject):
    requestStarted = Signal()
    requestFinished = Signal(dict)
    requestFailed = Signal(str)
    requestProgress = Signal()

    def __init__(self):
        super().__init__()
        self._worker = ApiWorker()
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._connect_worker_signals()
        self._thread.start()

    def _connect_worker_signals(self):
        self._worker.requestFinished.connect(lambda data: self.requestFinished.emit(data))
        self._worker.requestFailed.connect(lambda error_message: self.requestFinished.emit(error_message))

    def _send_request(self, request: 'ApiRequest') -> None:
        QMetaObject.invokeMethod(
            self._worker,
            'send_request',
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(ApiRequest, request)
        )

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
        request = ApiRequest(endpoint, method=RequestMethod.GET, headers=self._get_headers(token))
        self._send_request(request)

    def post(self, endpoint: str, token: Optional[str] = None, data: Optional[dict] = None) -> None:
        request = ApiRequest(endpoint, method=RequestMethod.POST, headers=self._get_headers(token), data=data)
        self._send_request(request)

