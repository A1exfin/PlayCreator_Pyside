from typing import Optional, Dict, Any, Callable
import json

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QSslConfiguration, QSslSocket, QAuthenticator
from PySide6.QtCore import QUrl, QTimer, QByteArray


class ApiClient:
    def __init__(self, base_url: str, debug: bool = False):
        self.nam = QNetworkAccessManager()
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.retry_attempts = {}  # Для отслеживания повторных попыток

        # Подключаем обработчики
        self.nam.finished.connect(self._handle_response)
        self.nam.authenticationRequired.connect(self._handle_auth)

    def set_credentials(self, username: str, password: str):
        """Установка учетных данных для базовой авторизации"""
        self.username = username
        self.password = password

    def set_bearer_token(self, token: str):
        """Установка Bearer token"""
        self.bearer_token = token

    def _handle_auth(self, reply: QNetworkReply, authenticator: QAuthenticator):
        """Обработка требования аутентификации"""
        if hasattr(self, 'username') and hasattr(self, 'password'):
            authenticator.setUser(self.username)
            authenticator.setPassword(self.password)
        elif hasattr(self, 'bearer_token'):
            # Для Bearer token обычно добавляем в заголовки, а не в authenticator
            pass

    def _create_request(self, endpoint: str, method: str = "GET") -> QNetworkRequest:
        """Создание запроса с настройками"""
        url = QUrl(f"{self.base_url}/{endpoint.lstrip('/')}")
        request = QNetworkRequest(url)

        # Устанавливаем заголовки для JSON
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # Добавляем Bearer token если есть
        if hasattr(self, 'bearer_token'):
            request.setRawHeader(b"Authorization", f"Bearer {self.bearer_token}".encode())

        # Настройка SSL
        ssl_config = QSslConfiguration.defaultConfiguration()
        if self.debug:
            # В режиме отладки отключаем проверку SSL
            ssl_config.setPeerVerifyMode(QSslSocket.VerifyNone)
        else:
            ssl_config.setPeerVerifyMode(QSslSocket.VerifyPeer)
        request.setSslConfiguration(ssl_config)

        # Устанавливаем атрибуты для таймаута (в миллисекундах)
        request.setAttribute(QNetworkRequest.Attribute.ConnectionTimeoutAttribute, 10000)  # 10 сек
        request.setAttribute(QNetworkRequest.Attribute.SynchronousRequestAttribute, False)

        return request

    def request(
            self,
            endpoint: str,
            method: str = "GET",
            data: Optional[Dict[str, Any]] = None,
            retry_total: int = 5,
            retry_backoff: float = 1.5,
            retry_statuses: list = [429, 500, 502, 503, 504],
            timeout: int = 10000
    ):
        """Выполнение запроса с поддержкой повторов"""
        request = self._create_request(endpoint, method)
        request.setAttribute(QNetworkRequest.Attribute.ConnectionTimeoutAttribute, timeout)

        # Сохраняем параметры для возможных повторов
        request_id = id(request)
        self.retry_attempts[request_id] = {
            'endpoint': endpoint,
            'method': method,
            'data': data,
            'retry_total': retry_total,
            'retry_backoff': retry_backoff,
            'retry_statuses': retry_statuses,
            'attempt': 0,
            'timeout': timeout
        }

        # Выполняем запрос
        json_data = json.dumps(data).encode('utf-8') if data else None

        if method == "GET":
            reply = self.nam.get(request)
        elif method == "POST":
            reply = self.nam.post(request, json_data)
        elif method == "PUT":
            reply = self.nam.put(request, json_data)
        elif method == "DELETE":
            reply = self.nam.deleteResource(request)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Сохраняем ID запроса в reply для отслеживания
        reply.setProperty("request_id", request_id)

        # Устанавливаем таймаут на ответ
        QTimer.singleShot(timeout, lambda: self._handle_timeout(reply))

    def _handle_timeout(self, reply: QNetworkReply):
        """Обработка таймаута"""
        if reply.isRunning():
            reply.abort()

    def _handle_response(self, reply: QNetworkReply):
        """Обработка ответа с поддержкой повторов"""
        request_id = reply.property("request_id")
        retry_info = self.retry_attempts.get(request_id, {})

        error = reply.error()
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)

        if error == QNetworkReply.NoError:
            # Успешный запрос
            data = reply.readAll().data()
            try:
                json_response = json.loads(data.decode('utf-8'))
                self.on_success(reply.url().toString(), json_response, status_code)
            except json.JSONDecodeError:
                self.on_success(reply.url().toString(), data, status_code)

            # Удаляем информацию о повторах
            if request_id in self.retry_attempts:
                del self.retry_attempts[request_id]

        else:
            # Обработка ошибок с повторами
            should_retry = self._should_retry(reply, retry_info)

            if should_retry:
                self._retry_request(reply, retry_info)
            else:
                self.on_error(reply.url().toString(), reply.errorString(), status_code)
                if request_id in self.retry_attempts:
                    del self.retry_attempts[request_id]

        reply.deleteLater()

    def _should_retry(self, reply: QNetworkReply, retry_info: dict) -> bool:
        """Определяем, нужно ли повторять запрос"""
        if not retry_info:
            return False

        current_attempt = retry_info.get('attempt', 0)
        max_attempts = retry_info.get('retry_total', 5)
        retry_statuses = retry_info.get('retry_statuses', [])

        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        error = reply.error()

        # Проверяем лимит попыток
        if current_attempt >= max_attempts:
            return False

        # Проверяем статусы для повтора
        if status_code in retry_statuses:
            return True

        # Проверяем сетевые ошибки
        if error in [QNetworkReply.ConnectionRefusedError,
                     QNetworkReply.RemoteHostClosedError,
                     QNetworkReply.TimeoutError,
                     QNetworkReply.OperationCanceledError,
                     QNetworkReply.SslHandshakeFailedError,
                     QNetworkReply.TemporaryNetworkFailureError]:
            return True

        return False

    def _retry_request(self, reply: QNetworkReply, retry_info: dict):
        """Повторный запрос с backoff"""
        request_id = id(reply)
        current_attempt = retry_info.get('attempt', 0)
        backoff_factor = retry_info.get('retry_backoff', 1.5)

        # Вычисляем задержку
        delay_ms = int((backoff_factor ** current_attempt) * 1000)

        # Увеличиваем счетчик попыток
        retry_info['attempt'] = current_attempt + 1
        self.retry_attempts[request_id] = retry_info

        # Запланировать повторный запрос
        QTimer.singleShot(delay_ms, lambda: self._execute_retry(retry_info))

    def _execute_retry(self, retry_info: dict):
        """Выполнение повторного запроса"""
        self.request(
            endpoint=retry_info['endpoint'],
            method=retry_info['method'],
            data=retry_info['data'],
            retry_total=retry_info['retry_total'],
            retry_backoff=retry_info['retry_backoff'],
            retry_statuses=retry_info['retry_statuses'],
            timeout=retry_info['timeout']
        )

    def on_success(self, url: str, data: Any, status_code: int):
        """Обработчик успешного запроса (переопределите в наследнике)"""
        print(f"Success: {url} - Status: {status_code}")
        print(f"Data: {data}")

    def on_error(self, url: str, error: str, status_code: int):
        """Обработчик ошибки (переопределите в наследнике)"""
        print(f"Error: {url} - {error} - Status: {status_code}")


# Пример использования
if __name__ == "__main__":
    from PySide6.QtCore import QCoreApplication
    import sys

    app = QCoreApplication(sys.argv)

    client = ApiClient("https://api.example.com", debug=False)
    client.set_bearer_token("your_token_here")


    # Переопределяем обработчики
    def on_success(url, data, status_code):
        print(f"Received data from {url}")
        app.quit()


    def on_error(url, error, status_code):
        print(f"Request failed: {error}")
        app.quit()


    client.on_success = on_success
    client.on_error = on_error

    # Отправляем JSON данные
    json_data = {"key": "value", "number": 42}
    client.request(
        endpoint="/data",
        method="POST",
        data=json_data,
        retry_total=5,
        retry_backoff=1.5,
        retry_statuses=[429, 500, 502, 503, 504],
        timeout=10000
    )

    sys.exit(app.exec())