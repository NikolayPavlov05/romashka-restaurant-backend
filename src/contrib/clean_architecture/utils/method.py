"""Модуль с утилитами для работы с методами репозиториев, интракторов, контроллеров и представлений

## классы

Classes:
    CleanMethodMixin: Миксин для работы с методами репозиториев, интракторов, контроллеров и представлений

## Функции

Functions:
    clean_method: Декоратор для методов репозиториев, интракторов, контроллеров и представлений

"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any


def clean_method(target: Callable = None, *, name: str = None, alias: str = None):
    """Декоратор для методов репозиториев, интракторов, контроллеров и представлений

    Args:
        target: Декорируемая функция
        name: Имя функции
        alias: псевдоним функции

    Returns:
        Callable

    """

    def decorator(function: Callable):
        _name = name or function.__name__
        function.__method_name__ = _name
        function.__method_alias__ = alias
        function.__is_clean_method__ = True

        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    if target and isinstance(target, Callable):
        return decorator(target)
    return decorator


class CleanMethodMixin:
    """Миксин для работы с методами репозиториев, интракторов, контроллеров и представлений"""

    clean_methods: dict[str, Any]
    """Маппинг методов"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        clean_methods = {}
        for _cls in reversed(cls.__mro__):
            for attr_name, attr in _cls.__dict__.items():
                if attr_name in clean_methods:
                    clean_methods[attr_name] = attr
                    continue
                if not getattr(attr, "__is_clean_method__", None):
                    continue
                clean_methods[attr_name] = attr

        cls.clean_methods = clean_methods

    @classmethod
    def get_clean_methods_names(cls):
        """Получить названия методов"""
        return [attr.__method_name__ for attr in cls.clean_methods.values()]

    @property
    def clean_methods_names(self):
        """Названия методов"""
        return self.get_clean_methods_names()
