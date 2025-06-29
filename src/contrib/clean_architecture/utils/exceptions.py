"""Модуль с утилитами для работы с исключениями

## классы

Classes:
    BaseExceptionRedirect: Базовый класс перенаправления исключения
    ExceptionRedirect: Перенаправление исключений
    NotFoundExceptionRedirect: Перенаправление исключений model.DoesNotExist
    MessageExceptionRedirect: Перенаправление исключений по его тексту

## Функции

Functions:
    with_exception_redirect: Перенаправляет исключение, вызванное во время выполнения декорируемой функции
    with_message_exception_redirect: Перенаправляет исключение по тексту ошибки, вызванное во время выполнения декорируемой функции
    with_not_found_exception_redirect: Перенаправляет исключение model.DoesNotExist, вызванное во время выполнения декорируемой функции

"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import ClassVar

from pydantic import BaseModel


def with_exception_redirect(from_exception: type[Exception], to_exception: type[Exception]) -> Callable:
    """Перенаправляет исключение, вызванное во время выполнения декорируемой функции

    Args:
        from_exception: Ожидаемое исключения
        to_exception: Целевое исключение

    Returns:
        Callable

    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except from_exception:
                raise to_exception

        return wrapper

    return decorator


def with_message_exception_redirect(exception_message: str, to_exception: type[Exception]) -> Callable:
    """Перенаправляет исключение по тексту ошибки, вызванное во время выполнения декорируемой функции

    Args:
        exception_message: Ожидаемое сообщение исключения
        to_exception: Целевое исключение

    Returns:
        Callable

    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exc:
                if exception_message in str(exc):
                    raise to_exception
                raise

        return wrapper

    return decorator


def with_not_found_exception_redirect(model: Any, to_exception: type[Exception]) -> Callable:
    """Перенаправляет исключение model.DoesNotExist, вызванное во время выполнения декорируемой функции

    Args:
        model: Модель ORM
        to_exception: Целевое исключение

        Returns:
            Callable

    """

    return with_exception_redirect(model.DoesNotExist, to_exception)


class BaseExceptionRedirect(BaseModel):
    """Базовый класс перенаправления исключения"""

    exception_redirect_decorator: ClassVar[Callable]
    """Декоратор функции перенаправления исключения"""

    def decorate(self, function: Callable) -> Callable:
        """Задекорировать `function` декоратором `self.exception_redirect_decorator`

        Args:
            function: Декорируемая функция

        Returns:
            Callable

        """
        return self.__class__.exception_redirect_decorator(**self.model_dump())(function)


class ExceptionRedirect(BaseExceptionRedirect):
    """Перенаправление исключений"""

    exception_redirect_decorator = with_exception_redirect

    from_exception: type[Exception]
    """Ожидаемое исключения"""
    to_exception: type[Exception]
    """Целевое исключение"""


class NotFoundExceptionRedirect(BaseExceptionRedirect):
    """Перенаправление исключений model.DoesNotExist"""

    exception_redirect_decorator = with_not_found_exception_redirect

    model: type[Any]
    """Модель ORM"""
    to_exception: type[Exception]
    """Целевое исключение"""


class MessageExceptionRedirect(BaseExceptionRedirect):
    """Перенаправление исключений по его тексту"""

    exception_redirect_decorator = with_message_exception_redirect

    exception_message: str
    """Ожидаемое сообщение исключения"""
    to_exception: type[Exception]
    """Целевое исключение"""
