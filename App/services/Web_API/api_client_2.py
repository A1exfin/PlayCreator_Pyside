import httpx
import asyncio
import json
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    total: int = 5
    backoff_factor: float = 1.5
    status_forcelist: List[int] = None

    def __post_init__(self):
        if self.status_forcelist is None:
            self.status_forcelist = [429, 500, 502, 503, 504]


class AsyncApiClient:
    def __init__(
            self,
            base_url: str,
            debug: bool = False,
            timeout: float = 10.0,
            default_retry: Optional[RetryConfig] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.timeout = timeout
        self.default_retry = default_retry or RetryConfig()

        # Авторизационные данные
        self.auth = None
        self.headers = {}

    def set_basic_auth(self, username: str, password: str):
        """Установка базовой авторизации"""
        self.auth = httpx.BasicAuth(username, password)

    def set_bearer_token(self, token: str):
        """Установка Bearer token"""
        self.headers['Authorization'] = f'Bearer {token}'

    def set_custom_header(self, key: str, value: str):
        """Установка кастомного заголовка"""
        self.headers[key] = value

    async def _calculate_backoff(self, attempt: int, backoff_factor: float) -> float:
        """Вычисление задержки для повторной попытки"""
        return backoff_factor * (2 ** (attempt - 1))

    async def _should_retry(
            self,
            response: Optional[httpx.Response],
            error: Optional[Exception],
            retry_config: RetryConfig,
            attempt: int
    ) -> bool:
        """Определяем, нужно ли повторять запрос"""
        # Проверяем лимит попыток
        if attempt >= retry_config.total:
            return False

        # Если была сетевя ошибка - повторяем
        if error is not None:
            if isinstance(error, (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout)):
                return True
            return False

        # Если есть ответ - проверяем статус код
        if response is not None:
            return response.status_code in retry_config.status_forcelist

        return False

    async def request(
            self,
            endpoint: str,
            method: str = "GET",
            data: Optional[Dict[str, Any]] = None,
            retry_config: Optional[RetryConfig] = None,
            timeout: Optional[float] = None,
            **kwargs
    ) -> httpx.Response:
        """Выполнение асинхронного запроса с поддержкой повторов"""
        retry_config = retry_config or self.default_retry
        timeout = timeout or self.timeout
        attempt = 0

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Подготавливаем заголовки
        headers = self.headers.copy()
        if data is not None and method in ["POST", "PUT", "PATCH"]:
            headers['Content-Type'] = 'application/json'

        async with httpx.AsyncClient(verify=not self.debug) as client:
            while attempt <= retry_config.total:
                attempt += 1
                response = None
                error = None

                try:
                    # Выполняем запрос
                    request_kwargs = {
                        'method': method,
                        'url': url,
                        'headers': headers,
                        'timeout': timeout,
                        'auth': self.auth,
                        **kwargs
                    }

                    if data is not None and method in ["POST", "PUT", "PATCH"]:
                        request_kwargs['json'] = data

                    response = await client.request(**request_kwargs)

                    # Проверяем нужно ли повторять
                    should_retry = await self._should_retry(
                        response, None, retry_config, attempt
                    )

                    if not should_retry:
                        return response

                except Exception as e:
                    error = e
                    logger.warning(f"Attempt {attempt} failed: {e}")

                    # Проверяем нужно ли повторять при ошибке
                    should_retry = await self._should_retry(
                        None, error, retry_config, attempt
                    )

                    if not should_retry:
                        raise e

                # Если нужно повторять - ждем перед следующей попыткой
                if attempt < retry_config.total:
                    backoff = await self._calculate_backoff(attempt, retry_config.backoff_factor)
                    logger.info(f"Retrying in {backoff:.2f}s (attempt {attempt}/{retry_config.total})")
                    await asyncio.sleep(backoff)

            # Если дошли до сюда - все попытки исчерпаны
            if error:
                raise error
            return response

    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """GET запрос"""
        return await self.request(endpoint, "GET", **kwargs)

    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """POST запрос с JSON данными"""
        return await self.request(endpoint, "POST", data, **kwargs)

    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """PUT запрос с JSON данными"""
        return await self.request(endpoint, "PUT", data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        """DELETE запрос"""
        return await self.request(endpoint, "DELETE", **kwargs)


# Пример использования
async def main():
    # Создаем клиент
    client = AsyncApiClient(
        base_url="https://jsonplaceholder.typicode.com",
        debug=False,  # В продакшене должно быть False
        timeout=10.0
    )

    # Настраиваем retry стратегию
    retry_strategy = RetryConfig(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    # Устанавливаем заголовки если нужно
    client.set_custom_header("User-Agent", "MyAsyncApp/1.0")

    try:
        # Пример GET запроса
        print("Sending GET request...")
        response = await client.get(
            "/posts/1",
            retry_config=retry_strategy
        )
        print(f"GET Response: {response.status_code}")
        print(f"Data: {response.json()}")

        # Пример POST запроса с JSON данными
        print("\nSending POST request...")
        json_data = {
            "title": "foo",
            "body": "bar",
            "userId": 1
        }

        response = await client.post(
            "/posts",
            data=json_data,
            retry_config=retry_strategy
        )

        print(f"POST Response: {response.status_code}")
        print(f"Created post: {response.json()}")

        # Обработка ошибок
        print("\nTesting error handling...")
        try:
            response = await client.get(
                "/nonexistent-endpoint",
                retry_config=RetryConfig(total=2, backoff_factor=0.1)
            )
        except httpx.HTTPStatusError as e:
            print(f"Expected error: {e.response.status_code}")

    except httpx.RequestError as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Альтернативная версия с декоратором для автоматического retry
def with_retry(retry_config: RetryConfig):
    """Декоратор для автоматического повторения запросов"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            attempt = 0
            last_error = None

            while attempt <= retry_config.total:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Проверяем нужно ли повторять
                    should_retry = attempt < retry_config.total
                    if isinstance(e, httpx.HTTPStatusError):
                        should_retry = e.response.status_code in retry_config.status_forcelist
                    elif isinstance(e, (httpx.ConnectError, httpx.ReadTimeout)):
                        should_retry = True

                    if not should_retry:
                        break

                    # Ждем перед следующей попыткой
                    backoff = retry_config.backoff_factor * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {backoff:.2f}s (attempt {attempt}/{retry_config.total})")
                    await asyncio.sleep(backoff)

            raise last_error

        return wrapper

    return decorator


# Пример использования с декоратором
class DecoratedApiClient(AsyncApiClient):
    @with_retry(RetryConfig(total=3, backoff_factor=1.0))
    async def safe_get(self, endpoint: str, **kwargs) -> httpx.Response:
        """GET запрос с автоматическим retry через декоратор"""
        async with httpx.AsyncClient(verify=not self.debug) as client:
            return await client.get(f"{self.base_url}/{endpoint}", headers=self.headers, **kwargs)


if __name__ == "__main__":
    # Запуск примера
    asyncio.run(main())