from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import TYPE_CHECKING

from contrib.clean_architecture.types import mixin_for

from ..inspect.services import get_params_values
from ..inspect.services import replace_args_values
from .context import Context

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.core.models import User

__all__ = [
    "get_root_context",
    "get_current_request",
    "get_current_user",
    "get_current_user_id",
    "bind_current",
    "CURRENT",
]

_root_context = Context[dict[str, Any]]()


def get_root_context():
    return _root_context


def get_current_request() -> HttpRequest | None:
    return _root_context.get("request")


def get_current_user() -> User | None:
    if request := get_current_request():
        return getattr(request, "user", None)


def get_current_user_id() -> int | None:
    user: User | None = get_current_user()
    return getattr(user, "id", None)


class CURRENT(mixin_for(Any)): ...


_CURRENT_MAPPING = {
    "user": get_current_user,
    "user_id": get_current_user_id,
    "request": get_current_request,
}


def bind_current(target: Callable = None, **mapping: str) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            parameters = inspect.signature(function).parameters
            for key, value in _CURRENT_MAPPING.items():
                if key in mapping:
                    key = mapping[key]

                if key in parameters and get_params_values(function, *args, params=[key], **kwargs)[0] is CURRENT:
                    args, kwargs = replace_args_values({key: value()}, function, *args, **kwargs)
            return function(*args, **kwargs)

        return wrapper

    if target is None:
        return decorator
    return decorator(target)
