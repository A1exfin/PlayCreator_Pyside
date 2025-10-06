import json
from typing import TYPE_CHECKING, Optional, Any
from dataclasses import dataclass
from collections import namedtuple

from PySide6.QtNetwork import (QNetworkAccessManager, QAuthenticator, QNetworkRequest, QNetworkReply, QSslConfiguration,
                               QSslSocket)
from PySide6.QtCore import QUrl, QTimer, QByteArray, QObject, Signal

import Core
from Core.Enums import RequestMethod
from Core.settings import WebAppUrls

if TYPE_CHECKING:
    pass


request_info = namedtuple('RequestInfo', ('reply', 'method', 'retry_count', 'callback'))


@dataclass
class RetryStrategy:
    total_timeout: int = 30_000
    attempt_timeout: int = 10_000
    total_attempts: int = 3
    retry_delay: float = 1.5
    retry_errors_list = {
        QNetworkReply.NetworkError.ConnectionRefusedError,
        QNetworkReply.NetworkError.RemoteHostClosedError,
        QNetworkReply.NetworkError.HostNotFoundError,
        QNetworkReply.NetworkError.TimeoutError,
        QNetworkReply.NetworkError.TemporaryNetworkFailureError,
        QNetworkReply.NetworkError.NetworkSessionFailedError,
        QNetworkReply.NetworkError.ProxyConnectionRefusedError,
        QNetworkReply.NetworkError.ProxyConnectionClosedError,
        QNetworkReply.NetworkError.ProxyNotFoundError,
        QNetworkReply.NetworkError.ProxyTimeoutError,
        QNetworkReply.NetworkError.SslHandshakeFailedError,
        QNetworkReply.NetworkError.OperationCanceledError,
        QNetworkReply.NetworkError.UnknownNetworkError
    }
    retry_status_list = {429, 500, 502, 503, 504, 507, 508, 509, 529, 530}



@dataclass
class ApiResponse:
    success: bool
    status_code: int
    data: Optional[dict] = None
    error: Optional[str] = None


class ApiManager(QObject):
    requestFinished = Signal()
    requestFailed = Signal()

    def __init__(self, auth_token: Optional[str] = None, parent: Optional['QObject'] = None):
        super().__init__(parent=parent)
        self._api_worker = QNetworkAccessManager()
        self._endpoints = WebAppUrls()
        self._token = auth_token
        self._retry_strategy = RetryStrategy()
        self._active_requests: dict[int, 'request_info'] = {}
        self._total_timeout_timer = QTimer(parent=self)
        self._total_timeout_timer.setSingleShot(True)
        self._total_timeout_timer.setInterval(self._retry_strategy.total_timeout)
        self._total_timeout_timer.timeout.connect(self._cancel_all_requests)
        self._api_worker.finished.connect(self._handle_response)

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    def set_total_timeout(self, timeout: int) -> None:
        self._retry_strategy.total_timeout = timeout
        self._total_timeout_timer.setInterval(self._retry_strategy.total_timeout)

    def set_attempt_timeout(self, timeout: int) -> None:
        self._retry_strategy.attempt_timeout = timeout

    def set_total_attempts(self, total_attempts: int) -> None:
        self._retry_strategy.total_attempts = total_attempts

    def set_attempts_delay(self, delay: float | int) -> None:
        self._retry_strategy.retry_delay = delay

    def _create_request(self, endpoint: str) -> 'QNetworkRequest':
        request = QNetworkRequest(endpoint)
        request.setTransferTimeout(self._retry_strategy.attempt_timeout)
        request.setRawHeader(b'Content-Type', b'application/json')
        request.setRawHeader(b'Accept', b'application/json')
        request.setRawHeader(b'User-Agent', f'{Core.APP_NAME}/{Core.VERSION}'.encode('utf-8'))
        if self._token:
            request.setRawHeader(b'Authorization', f'Token {self._token}'.encode('utf-8'))

        ssl_config = QSslConfiguration.defaultConfiguration()
        if Core.DEBUG:
            ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyNone)
        else:
            ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyPeer)
        request.setSslConfiguration(ssl_config)

        request.setAttribute(QNetworkRequest.Attribute.SynchronousRequestAttribute, False)
        return request

    def _retry_request(self, request: 'QNetworkRequest', method: 'RequestMethod',
                       retry_count: int, callback: callable) -> None:
        retry_delay = self._retry_strategy.retry_delay * (2 ** retry_count)
        QTimer.singleShot(retry_delay, lambda: self._send_request(request, method, retry_count, callback))

    def _cancel_all_requests(self) -> None:
        for request_id in self._active_requests.keys():
            self._cancel_request(request_id)
        # self._active_requests.clear()

    def _cancel_request(self, request_id: int) -> None:
        if request_id in self._active_requests:
            request = self._active_requests.pop(request_id)
            if request.reply.isRunning():
                request.reply.abort()
            request.reply.deleteLater()

    def _is_retryable_error(self, error: 'QNetworkReply.NetworkError') -> bool:
        return error in self._retry_strategy.retry_errors_list

    def _is_retryable_code(self, status_code: int) -> bool:
        return status_code in self._retry_strategy.retry_status_list

    def _send_request(self, request: 'QNetworkRequest', method: 'RequestMethod', attempt_count: int = 0,
                      json_data: Optional[bytes] = None, callback: Optional[callable] = None) -> None:
        method_bytes = method.value.encode('utf-8')
        if json_data:
            reply = self._api_worker.sendCustomRequest(request, method_bytes, json_data)
        else:
            reply = self._api_worker.sendCustomRequest(request, method_bytes)
        # if method is RequestMethod.GET:
        #     reply = self._api_worker.get(request)
        # elif method is RequestMethod.POST:
        #     reply = self._api_worker.post(request, json_data)
        # elif method is RequestMethod.DELETE:
        #     reply = self._api_worker.deleteResource(request)
        # else:
        #     raise ValueError(f'Неправильный метод - {method.value}.')
        if reply:
            self._active_requests[id(reply)] = request_info(reply, method, attempt_count, callback)
            reply.errorOccurred.connect(self._handle_error)



    def _handle_response(self, reply: 'QNetworkReply') -> None:
        print(f'{reply.error() = }')
        if reply.error() == QNetworkReply.NetworkError.NoError:
            request = self._active_requests[id(reply)]
            response_data = json.loads(reply.readAll().data().decode())
            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            response = ApiResponse(success=True, status_code=status_code, data=response_data)
            request.callback(response)




    def _handle_error(self, reply: 'QNetworkReply') -> None:
        print(f'_handle_error, {reply = }')

    def login(self, username: str, password: str, callback: callable) -> None:
        request = self._create_request(self._endpoints.api_login)
        json_data = json.dumps({'username': username, 'password': password}).encode()
        self._send_request(request=request, method=RequestMethod.POST, json_data=json_data, callback=callback)

    def logout(self, callback: callable) -> None:
        request = self._create_request(self._endpoints.api_logout)
        self._send_request(request=request, method=RequestMethod.POST, callback=callback)

    def save_playbook(self):
        pass

    def update_playbook(self):
        pass

    def save_playbook_as(self):
        pass