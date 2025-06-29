from __future__ import annotations

import asyncio
import base64
import inspect
import pickle
from collections.abc import Callable
from functools import wraps
from typing import Any

from contrib.bases.decorators import BaseDecorator
from contrib.inspect.services import get_params_values
from contrib.redis.dtos import RedisContext
from contrib.redis.redis.bases import RedisManager


class _RedisClientDecorator(BaseDecorator):
    def __init__(
        self,
        function: Callable | None = None,
        /,
        *,
        namespace=None,
        expire=None,
        **kwargs,
    ):
        self.context = RedisContext(namespace=namespace, expire=expire)
        super().__init__(function, **kwargs)

    def get_decorated(self, function):
        def wrapper(*args, **kwargs):
            if self._instance and getattr(self._instance, "redis_client", None):
                kwargs["redis_client"] = self._instance.redis_client
                return function(*args, **kwargs)

            if kwargs.get("redis_client"):
                return function(*args, **kwargs)

            with RedisManager(context=self.context) as redis_client:
                return function(*args, **kwargs, redis_client=redis_client)

        return wrapper


bind_redis_client = _RedisClientDecorator


def _base_key_func(*args: Any, **kwargs: Any) -> str:
    key = args
    if kwargs:
        key += tuple(sorted(kwargs.items()))
    return base64.b64encode(pickle.dumps(key)).decode("utf-8")


def cache_decorator(
    key_func: Callable | None = None,
    ttl: int | None = None,
    params: list[str] | None = None,
) -> Callable:
    if not key_func:
        key_func = _base_key_func

    redis_context = RedisContext(namespace="cache_function", expire=ttl)

    def decorator(function):
        prefix = f"{function.__module__}.{function.__name__}"

        def get_key(*args, **kwargs):
            unwrapped = inspect.unwrap(function)
            args_values = get_params_values(unwrapped, *args, params=params, **kwargs)
            new_kwargs = dict(zip(params, args_values))
            return prefix + ":" + str(key_func(**new_kwargs))

        if asyncio.iscoroutinefunction(function):

            @wraps(function)
            async def wrapper(*args, **kwargs):
                with RedisManager(context=redis_context) as redis_client:
                    # type: ignore
                    key = get_key(*args, **kwargs)
                    if redis_client.exists(key):
                        return redis_client.get(key)
                    result = await function(*args, **kwargs)
                    redis_client.set(key, result)
                    return result

        else:

            @wraps(function)
            def wrapper(*args, **kwargs):
                with RedisManager(context=redis_context) as redis_client:
                    key = get_key(*args, **kwargs)
                    if redis_client.exists(key):
                        return redis_client.get(key)
                    result = function(*args, **kwargs)
                    redis_client.set(key, result)
                    return result

        return wrapper

    return decorator
