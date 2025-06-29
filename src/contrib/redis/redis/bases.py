from __future__ import annotations

from typing import Any

import redis
from config.redis import redis_pool
from contrib.redis.bases import BaseRedisClient
from contrib.redis.bases import BaseRedisManager
from contrib.redis.types import RedisName
from contrib.redis.utils import redis_decode
from contrib.redis.utils import redis_encode


class RedisClient(BaseRedisClient):
    def get_client(self, *args, **kwargs) -> redis.Redis:
        return redis.Redis(*args, **kwargs)

    def expire(self, name: RedisName, expire_time: int = None, **kwargs) -> None:
        expire_time = self.context.expire_time or expire_time
        if expire_time:
            self.client.expire(self.get_name(name), expire_time, **kwargs)

    def hset(
        self,
        name: RedisName,
        key: str = None,
        value: Any = None,
        mapping: dict = None,
        items: list = None,
        expire_time: int = None,
    ) -> None:
        value = redis_encode(value)
        mapping = redis_encode(mapping, mapping=True)
        items = redis_encode(items, items=True)

        self.client.hset(self.get_name(name), key, value, mapping, items)
        self.expire(name, expire_time)

    def hget(self, name: RedisName, *keys: str, default: Any = None) -> Any:
        if len(keys) == 1:
            data: bytes | None = self.client.hget(self.get_name(name), keys[0])
        else:
            data: list = self.client.hmget(self.get_name(name), list(keys))
        return redis_decode(data) if data else default

    def hgetall(self, name: RedisName) -> dict:
        return redis_decode(self.client.hgetall(self.get_name(name)))

    def hdel(self, name: RedisName, *keys: str) -> None:
        self.client.hdel(self.get_name(name), *keys)

    def hexists(self, name: RedisName, key: str) -> bool:
        return self.client.hexists(self.get_name(name), key)

    def set(self, name: RedisName, value: Any, expire_time: bool | int = True, **kwargs) -> None:
        self.client.set(self.get_name(name), redis_encode(value), **kwargs)
        self.expire(name, expire_time)

    def get(self, name: RedisName, default: Any = None) -> Any:
        value: bytes | None = self.client.get(self.get_name(name))
        return redis_decode(value) if value else default

    def delete(self, name: RedisName) -> None:
        self.client.delete(self.get_name(name))

    def exists(self, name: RedisName) -> bool:
        return self.client.exists(self.get_name(name))


class RedisManager(BaseRedisManager):
    client: RedisClient

    def get_client(self) -> RedisClient:
        return RedisClient(connection_pool=redis_pool, decode_responses=True, context=self.context)
