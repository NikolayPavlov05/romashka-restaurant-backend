from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from contrib.redis.dtos import RedisContext
from contrib.redis.interfaces import IRedisClient
from contrib.redis.interfaces import IRedisManager
from contrib.redis.types import RedisName


class BaseRedisClient(IRedisClient, ABC):
    def __init__(self, *args, context: RedisContext = None, **kwargs):
        self.context = context or RedisContext()
        self.client = self.get_client(*args, **kwargs)

    def get_name(self, name: RedisName):
        if isinstance(name, (tuple, list)):
            name = ":".join(map(lambda x: str(x), name))
        if not self.context.namespace:
            return name
        return f"{self.context.namespace}:{name}"


class BaseRedisManager(IRedisManager, ABC):
    """Класс для управления подключению к redis"""

    client: BaseRedisClient

    def __init__(self, context: RedisContext = None):
        self.context = context or RedisContext()

    def __enter__(self) -> BaseRedisClient:
        self.client = self.get_client()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.client.close()

    @abstractmethod
    def get_client(self) -> BaseRedisClient:
        """Возвращает redis клиент"""
