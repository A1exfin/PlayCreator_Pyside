import json
import logging
from typing import Optional, Dict, Any, Callable
from enum import Enum

from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class ApiResponse:
    def __init__(self, success: bool, data: Any = None, error: str = None, status_code: int = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code

    def __str__(self):
        return f"ApiResponse(success={self.success}, status_code={self.status_code}, error={self.error})"

class ApiManager(QObject):
    """Менеджер для работы с API с таймаутами и повторными попытками"""
    
    # Сигналы для асинхронных запросов
    request_finished = Signal(ApiResponse)
    request_failed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.active_requests = {}
        self.max_retries = 3
        self.request_timeout = 30000  # 30 секунд
        self.base_url = ""
        
        # Настройка заголовков по умолчанию
        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "ApiManager/1.0"
        }

    def set_base_url(self, base_url: str):
        """Установка базового URL для всех запросов"""
        self.base_url = base_url.rstrip('/')

    def set_auth_token(self, token: str):
        """Установка токена аутентификации"""
        self.default_headers["Authorization"] = f"Bearer {token}"

    def set_default_headers(self, headers: Dict[str, str]):
        """Установка заголовков по умолчанию"""
        self.default_headers.update(headers)

    def _create_request(self, endpoint: str, method: RequestMethod) -> QNetworkRequest:
        """Создание сетевого запроса"""
        url = QUrl(f"{self.base_url}/{endpoint.lstrip('/')}")
        request = QNetworkRequest(url)
        
        # Установка заголовков
        for key, value in self.default_headers.items():
            request.setRawHeader(key.encode(), value.encode())
            
        # Настройка атрибутов запроса
        request.setAttribute(QNetworkRequest.Attribute.FollowRedirectsAttribute, True)
        request.setAttribute(QNetworkRequest.Attribute.Http2AllowedAttribute, True)
        
        return request

    def _handle_timeout(self, reply_id: int):
        """Обработка таймаута запроса"""
        if reply_id in self.active_requests:
            reply, timer, retry_count, callback = self.active_requests.pop(reply_id)
            if reply.isRunning():
                reply.abort()
                logger.warning(f"Request timeout for reply ID: {reply_id}")
                
                # Повторная попытка
                if retry_count < self.max_retries:
                    logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                    self._retry_request(reply.request(), retry_count + 1, callback)
                else:
                    self.request_failed.emit("Request timeout after maximum retries")

    def _retry_request(self, request: QNetworkRequest, retry_count: int, callback: Callable):
        """Повторный запрос"""
        # Добавляем небольшую задержку перед повторной попыткой
        QTimer.singleShot(1000 * retry_count, lambda: self._send_request(
            request, retry_count, callback
        ))

    def _send_request(self, request: QNetworkRequest, retry_count: int = 0, 
                     callback: Callable = None, data: Any = None):
        """Отправка запроса"""
        method = request.attribute(QNetworkRequest.Attribute.HttpMethodAttribute)
        if not method:
            method = RequestMethod.GET.value
            
        reply = None
        if method == RequestMethod.POST.value:
            json_data = json.dumps(data).encode() if data else b''
            reply = self.network_manager.post(request, json_data)
        elif method == RequestMethod.PUT.value:
            json_data = json.dumps(data).encode() if data else b''
            reply = self.network_manager.put(request, json_data)
        elif method == RequestMethod.DELETE.value:
            reply = self.network_manager.deleteResource(request)
        else:
            reply = self.network_manager.get(request)
            
        if reply:
            # Создаем таймер для таймаута
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._handle_timeout(reply))
            timer.start(self.request_timeout)
            
            # Сохраняем информацию о запросе
            self.active_requests[id(reply)] = (reply, timer, retry_count, callback)
            
            # Подключаем сигналы
            reply.finished.connect(lambda: self._handle_response(reply))
            reply.errorOccurred.connect(lambda error: self._handle_error(reply, error))
            
            return id(reply)
        return None

    def _handle_response(self, reply: QNetworkReply):
        """Обработка успешного ответа"""
        reply_id = id(reply)
        if reply_id not in self.active_requests:
            return
            
        _, timer, _, callback = self.active_requests.pop(reply_id)
        timer.stop()
        
        try:
            status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            response_data = reply.readAll().data()
            
            if 200 <= status_code < 300:
                # Успешный ответ
                try:
                    json_data = json.loads(response_data.decode()) if response_data else {}
                    response = ApiResponse(True, json_data, None, status_code)
                except json.JSONDecodeError:
                    response = ApiResponse(True, response_data.decode(), None, status_code)
                
                logger.info(f"Request successful: {status_code}")
                if callback:
                    callback(response)
                self.request_finished.emit(response)
            else:
                # Ошибка сервера
                error_msg = f"HTTP error {status_code}"
                try:
                    error_data = json.loads(response_data.decode())
                    error_msg = error_data.get('error', error_data.get('message', error_msg))
                except:
                    pass
                    
                response = ApiResponse(False, None, error_msg, status_code)
                logger.error(f"Server error: {status_code} - {error_msg}")
                if callback:
                    callback(response)
                self.request_failed.emit(error_msg)
                
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            logger.error(error_msg)
            response = ApiResponse(False, None, error_msg)
            if callback:
                callback(response)
            self.request_failed.emit(error_msg)
            
        finally:
            reply.deleteLater()

    def _handle_error(self, reply: QNetworkReply, error: QNetworkReply.NetworkError):
        """Обработка ошибок сети"""
        reply_id = id(reply)
        if reply_id not in self.active_requests:
            return
            
        _, timer, retry_count, callback = self.active_requests.pop(reply_id)
        timer.stop()
        
        error_msg = reply.errorString()
        logger.error(f"Network error: {error_msg} (code: {error})")
        
        # Повторная попытка для временных ошибок
        if retry_count < self.max_retries and error in [
            QNetworkReply.NetworkError.ConnectionRefusedError,
            QNetworkReply.NetworkError.RemoteHostClosedError,
            QNetworkReply.NetworkError.TimeoutError,
            QNetworkReply.NetworkError.TemporaryNetworkFailureError
        ]:
            logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
            self._retry_request(reply.request(), retry_count + 1, callback)
        else:
            response = ApiResponse(False, None, error_msg)
            if callback:
                callback(response)
            self.request_failed.emit(error_msg)

    def make_request(self, endpoint: str, method: RequestMethod = RequestMethod.GET,
                    data: Any = None, callback: Callable = None) -> Optional[int]:
        """Основной метод для выполнения запросов"""
        try:
            request = self._create_request(endpoint, method)
            request.setAttribute(QNetworkRequest.Attribute.HttpMethodAttribute, method.value)
            
            return self._send_request(request, 0, callback, data)
            
        except Exception as e:
            error_msg = f"Error creating request: {str(e)}"
            logger.error(error_msg)
            if callback:
                callback(ApiResponse(False, None, error_msg))
            self.request_failed.emit(error_msg)
            return None

    # Удобные методы для разных типов запросов
    def get(self, endpoint: str, callback: Callable = None) -> Optional[int]:
        return self.make_request(endpoint, RequestMethod.GET, None, callback)

    def post(self, endpoint: str, data: Any = None, callback: Callable = None) -> Optional[int]:
        return self.make_request(endpoint, RequestMethod.POST, data, callback)

    def put(self, endpoint: str, data: Any = None, callback: Callable = None) -> Optional[int]:
        return self.make_request(endpoint, RequestMethod.PUT, data, callback)

    def delete(self, endpoint: str, callback: Callable = None) -> Optional[int]:
        return self.make_request(endpoint, RequestMethod.DELETE, None, callback)

    def cancel_all_requests(self):
        """Отмена всех активных запросов"""
        for reply_id, (reply, timer, _, _) in list(self.active_requests.items()):
            timer.stop()
            if reply.isRunning():
                reply.abort()
            reply.deleteLater()
        self.active_requests.clear()

# Пример использования
class ExampleUsage(QObject):
    def __init__(self):
        super().__init__()
        self.api_manager = ApiManager()
        self.api_manager.set_base_url("https://api.example.com")
        self.api_manager.set_auth_token("your-auth-token")
        
        # Подключаем сигналы
        self.api_manager.request_finished.connect(self.on_request_finished)
        self.api_manager.request_failed.connect(self.on_request_failed)
        
    def fetch_data(self):
        """Пример получения данных"""
        self.api_manager.get("/users", self.handle_users_response)
        
    def create_user(self, user_data):
        """Пример создания пользователя"""
        self.api_manager.post("/users", user_data, self.handle_create_user)
        
    def handle_users_response(self, response: ApiResponse):
        if response.success:
            print("Users data:", response.data)
        else:
            print("Error:", response.error)
            
    def handle_create_user(self, response: ApiResponse):
        if response.success:
            print("User created:", response.data)
        else:
            print("Error creating user:", response.error)
            
    @Slot(ApiResponse)
    def on_request_finished(self, response: ApiResponse):
        print(f"Request finished: {response}")
        
    @Slot(str)
    def on_request_failed(self, error: str):
        print(f"Request failed: {error}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    example = ExampleUsage()
    example.fetch_data()
    
    # Запускаем event loop
    sys.exit(app.exec())