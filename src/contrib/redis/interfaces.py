from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Awaitable
from typing import Any

from contrib.redis.types import RedisName


class IRedisClient(ABC):
    client: Any

    @abstractmethod
    def get_client(self, *args, **kwargs) -> Any: ...

    @abstractmethod
    def expire(self, name: RedisName, expire_time: int = None, **kwargs) -> Awaitable[None] | None: ...

    @abstractmethod
    def hset(
        self,
        name: RedisName,
        key: str = None,
        value: Any = None,
        mapping: dict = None,
        items: list = None,
        expire_time: int = None,
    ) -> Awaitable[None] | None: ...

    @abstractmethod
    def hget(self, name: RedisName, *keys: str, default: Any = None) -> Any: ...

    @abstractmethod
    def hgetall(self, name: RedisName) -> dict: ...

    @abstractmethod
    def hdel(self, name: RedisName, *keys: str) -> None: ...

    @abstractmethod
    def hexists(self, name: RedisName, key: str) -> bool: ...

    @abstractmethod
    def set(self, name: RedisName, value: Any, expire_time: bool | int = True, **kwargs) -> None: ...

    @abstractmethod
    def get(self, name: RedisName, default: Any = None) -> Any: ...

    @abstractmethod
    def delete(self, name: RedisName) -> None: ...

    @abstractmethod
    def exists(self, name: RedisName) -> bool: ...


class IRedisManager(ABC):
    client: IRedisClient

    def __enter__(self) -> client: ...

    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def get_client(self) -> IRedisClient:
        """Возвращает redis клиент"""
