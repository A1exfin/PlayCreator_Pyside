import json
import logging
from typing import Optional, Dict, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass

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

@dataclass
class ApiConfig:
    """Конфигурация API"""
    base_url: str = ""
    timeout: int = 30000  # 30 секунд
    max_retries: int = 3
    retry_delay: int = 1000  # 1 секунда задержки между попытками
    auth_token: str = None

class ApiResponse:
    def __init__(self, success: bool, data: Any = None, error: str = None, 
                 status_code: int = None, headers: Dict[str, str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
        self.headers = headers or {}

    def __str__(self):
        return f"ApiResponse(success={self.success}, status={self.status_code}, error={self.error})"

class ApiManager(QObject):
    """Менеджер для работы с API с поддержкой Djoser аутентификации"""
    
    # Сигналы для асинхронных запросов
    request_finished = Signal(ApiResponse)
    request_failed = Signal(str)
    auth_required = Signal()  # Сигнал когда требуется аутентификация
    
    def __init__(self, config: ApiConfig = None, parent=None):
        super().__init__(parent)
        self.config = config or ApiConfig()
        self.network_manager = QNetworkAccessManager(self)
        self.active_requests = {}
        
        # Настройка заголовков по умолчанию для JSON
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ApiManager/1.0"
        }
        
        # Обновляем заголовки аутентификации если токен есть
        if self.config.auth_token:
            self._update_auth_header()

    def update_config(self, config: ApiConfig):
        """Обновление конфигурации"""
        self.config = config
        if config.auth_token:
            self._update_auth_header()

    def set_auth_token(self, token: str):
        """Установка токена аутентификации для Djoser"""
        self.config.auth_token = token
        self._update_auth_header()

    def _update_auth_header(self):
        """Обновление заголовка аутентификации для Djoser"""
        if self.config.auth_token:
            self.default_headers["Authorization"] = f"Token {self.config.auth_token}"
        elif "Authorization" in self.default_headers:
            del self.default_headers["Authorization"]

    def clear_auth_token(self):
        """Очистка токена аутентификации"""
        self.config.auth_token = None
        if "Authorization" in self.default_headers:
            del self.default_headers["Authorization"]

    def _create_request(self, endpoint: str, method: RequestMethod) -> QNetworkRequest:
        """Создание сетевого запроса с правильным URL"""
        # Убираем ведущий слеш у endpoint если base_url уже имеет trailing slash
        endpoint = endpoint.lstrip('/')
        url = QUrl(f"{self.config.base_url.rstrip('/')}/{endpoint}")
        
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
                logger.warning(f"Request timeout for {reply.url().toString()}")
                
                # Повторная попытка
                if retry_count < self.config.max_retries:
                    logger.info(f"Retrying request (attempt {retry_count + 1}/{self.config.max_retries})")
                    self._retry_request(reply.request(), retry_count + 1, callback)
                else:
                    error_msg = "Request timeout after maximum retries"
                    if callback:
                        callback(ApiResponse(False, None, error_msg))
                    self.request_failed.emit(error_msg)

    def _retry_request(self, request: QNetworkRequest, retry_count: int, callback: Callable):
        """Повторный запрос с экспоненциальной задержкой"""
        delay = self.config.retry_delay * (2 ** retry_count)  # Экспоненциальная backoff
        QTimer.singleShot(delay, lambda: self._send_request(
            request, retry_count, callback
        ))

    def _send_request(self, request: QNetworkRequest, retry_count: int = 0, 
                     callback: Callable = None, data: Any = None) -> Optional[int]:
        """Отправка запроса"""
        method = request.attribute(QNetworkRequest.Attribute.HttpMethodAttribute)
        if not method:
            method = RequestMethod.GET.value
            
        reply = None
        try:
            if method == RequestMethod.POST.value:
                json_data = json.dumps(data).encode('utf-8') if data is not None else b''
                reply = self.network_manager.post(request, json_data)
            elif method == RequestMethod.PUT.value:
                json_data = json.dumps(data).encode('utf-8') if data is not None else b''
                reply = self.network_manager.put(request, json_data)
            elif method == RequestMethod.DELETE.value:
                reply = self.network_manager.deleteResource(request)
            else:
                reply = self.network_manager.get(request)
                
            if reply:
                # Создаем таймер для таймаута
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: self._handle_timeout(id(reply)))
                timer.start(self.config.timeout)
                
                # Сохраняем информацию о запросе
                self.active_requests[id(reply)] = (reply, timer, retry_count, callback)
                
                # Подключаем сигналы
                reply.finished.connect(lambda: self._handle_response(reply))
                reply.errorOccurred.connect(lambda error: self._handle_error(reply, error))
                
                return id(reply)
                
        except Exception as e:
            error_msg = f"Error sending request: {str(e)}"
            logger.error(error_msg)
            if callback:
                callback(ApiResponse(False, None, error_msg))
            self.request_failed.emit(error_msg)
            
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
            
            # Получаем заголовки ответа
            headers = {}
            for header in reply.rawHeaderList():
                headers[header.data().decode()] = reply.rawHeader(header).decode()
            
            response_data = reply.readAll().data()
            
            # Проверяем статус аутентификации
            if status_code == 401:
                logger.warning("Authentication required (401)")
                self.auth_required.emit()
                response = ApiResponse(False, None, "Authentication required", status_code, headers)
            elif 200 <= status_code < 300:
                # Успешный ответ
                try:
                    json_data = json.loads(response_data.decode('utf-8')) if response_data else {}
                    response = ApiResponse(True, json_data, None, status_code, headers)
                    logger.info(f"Request successful: {status_code} - {reply.url().toString()}")
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON response: {str(e)}"
                    logger.error(error_msg)
                    response = ApiResponse(False, None, error_msg, status_code, headers)
            else:
                # Ошибка сервера
                error_msg = self._parse_error_response(response_data, status_code)
                logger.error(f"Server error: {status_code} - {error_msg}")
                response = ApiResponse(False, None, error_msg, status_code, headers)
                
            # Вызываем колбэк и emit сигналов
            if callback:
                callback(response)
                
            if response.success:
                self.request_finished.emit(response)
            else:
                self.request_failed.emit(response.error)
                
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            logger.error(error_msg)
            response = ApiResponse(False, None, error_msg)
            if callback:
                callback(response)
            self.request_failed.emit(error_msg)
            
        finally:
            reply.deleteLater()

    def _parse_error_response(self, response_data: bytes, status_code: int) -> str:
        """Парсинг ошибок из JSON response"""
        try:
            error_data = json.loads(response_data.decode('utf-8'))
            
            # Стандартные форматы ошибок Djoser/DRF
            if isinstance(error_data, dict):
                if 'detail' in error_data:
                    return error_data['detail']
                elif 'error' in error_data:
                    return error_data['error']
                elif 'message' in error_data:
                    return error_data['message']
                elif 'non_field_errors' in error_data:
                    return ', '.join(error_data['non_field_errors'])
                
            return str(error_data)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            return f"HTTP error {status_code}"

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
        if retry_count < self.config.max_retries and self._is_retryable_error(error):
            logger.info(f"Retrying request (attempt {retry_count + 1}/{self.config.max_retries})")
            self._retry_request(reply.request(), retry_count + 1, callback)
        else:
            response = ApiResponse(False, None, error_msg)
            if callback:
                callback(response)
            self.request_failed.emit(error_msg)

    def _is_retryable_error(self, error: QNetworkReply.NetworkError) -> bool:
        """Определяет, является ли ошибка временной и подходящей для повторной попытки"""
        retryable_errors = [
            QNetworkReply.NetworkError.ConnectionRefusedError,
            QNetworkReply.NetworkError.RemoteHostClosedError,
            QNetworkReply.NetworkError.TimeoutError,
            QNetworkReply.NetworkError.TemporaryNetworkFailureError,
            QNetworkReply.NetworkError.ProxyConnectionRefusedError,
            QNetworkReply.NetworkError.ProxyConnectionClosedError,
            QNetworkReply.NetworkError.ProxyTimeoutError
        ]
        return error in retryable_errors

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

    def cancel_request(self, request_id: int):
        """Отмена конкретного запроса"""
        if request_id in self.active_requests:
            reply, timer, _, _ = self.active_requests.pop(request_id)
            timer.stop()
            if reply.isRunning():
                reply.abort()
            reply.deleteLater()

    def cancel_all_requests(self):
        """Отмена всех активных запросов"""
        for reply_id, (reply, timer, _, _) in list(self.active_requests.items()):
            timer.stop()
            if reply.isRunning():
                reply.abort()
            reply.deleteLater()
        self.active_requests.clear()

# Пример использования с Djoser
class DjoserApiManager(QObject):
    def __init__(self):
        super().__init__()
        
        # Конфигурация для Djoser API
        config = ApiConfig(
            base_url="http://localhost:8000/api",
            timeout=30000,
            max_retries=3,
            retry_delay=1000
        )
        
        self.api = ApiManager(config)
        
        # Подключаем сигналы
        self.api.request_finished.connect(self.on_request_finished)
        self.api.request_failed.connect(self.on_request_failed)
        self.api.auth_required.connect(self.on_auth_required)
        
    def login(self, username: str, password: str):
        """Аутентификация через Djoser"""
        data = {
            "username": username,
            "password": password
        }
        self.api.post("/auth/login/", data, self.handle_login_response)
        
    def handle_login_response(self, response: ApiResponse):
        if response.success and response.data.get('auth_token'):
            token = response.data['auth_token']
            self.api.set_auth_token(token)
            print("Login successful, token saved")
        else:
            print("Login failed:", response.error)
            
    def get_users(self):
        """Получение списка пользователей"""
        self.api.get("/users/", self.handle_users_response)
        
    def handle_users_response(self, response: ApiResponse):
        if response.success:
            print("Users:", response.data)
        else:
            print("Error getting users:", response.error)
            
    @Slot(ApiResponse)
    def on_request_finished(self, response: ApiResponse):
        print(f"Request finished: {response.status_code}")
        
    @Slot(str)
    def on_request_failed(self, error: str):
        print(f"Request failed: {error}")
        
    @Slot()
    def on_auth_required(self):
        print("Authentication required! Please login again.")
        self.api.clear_auth_token()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Пример использования
    api_example = DjoserApiManager()
    
    # Симуляция запросов
    # api_example.login("username", "password")
    # api_example.get_users()
    
    sys.exit(app.exec())