from __future__ import annotations

import json
from typing import Any

from appconf import AppConf
from contrib.rest.enums import TokenTypes
from requests.hooks import default_hooks
from requests.models import DEFAULT_REDIRECT_LIMIT


class RestConfig(AppConf):
    # Протокол API
    PROTOCOL: str = "https"
    # Хост API
    HOST: str = "0.0.0.0"
    # Порт API
    PORT: str = None
    # Путь до API
    API_PATH: str = ""

    # Настройки авторизации
    # Логин для авторизации
    USERNAME: str = None
    # Пароль для авторизации
    PASSWORD: str = None
    # Токен для авторизации
    TOKEN: str = None
    # Тип токена авторизации
    TOKEN_TYPE: TokenTypes = None
    # Ключ API
    API_KEY: str = None

    # Настройки сессии
    # Заголовки
    HEADERS: dict[str, str] = {}
    # Прокси
    PROXIES: dict[str, str] = {}
    # Прокси
    HOOKS: dict[str, str] = default_hooks()
    # Прокси
    PARAMS: dict[str, Any] = {}
    # Стримить контент
    STREAM: bool = False
    # Верифицировать запрос
    VERIFY: bool = True
    # Путь до сертификата
    CERT: str = None
    # Максимальное количество редиректов
    MAX_REDIRECTS: int = DEFAULT_REDIRECT_LIMIT
    # Куки
    COOKIES: dict[str, str] = {}

    # Настройки клиента
    # Максимальное число повторений запросов
    MAX_RETRY_COUNT: int = 3
    # Нужна аутентификация
    NEED_AUTHENTICATION: bool = False
    # Пропускать при запуске тестов
    SKIP_FOR_TEST_MODE: bool = False
    # Таймаут запросов
    TIMEOUT: int | tuple[int, int] = 15

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(frozenset(json.dumps({**self.configured_data, **self.__dict__})))

    @property
    def url(self):
        url = f"{self.PROTOCOL}://{self.HOST}"

        if self.PORT:
            url = f"{url}:{self.PORT}"
        if self.API_PATH:
            url = f"{url}/{self.API_PATH}"

        return url
