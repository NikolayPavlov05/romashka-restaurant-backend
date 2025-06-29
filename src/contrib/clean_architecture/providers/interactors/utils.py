"""Модуль с утилитами для репозиториев

Functions:
    bind_return_type: Заполняет return_type и / или return_pagination_type и paginated при вызове декорируемой функции

"""
from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps

from contrib.clean_architecture.consts import ReturnTypeAttrs
from contrib.context import get_root_context
from contrib.inspect.services import replace_args_values


def bind_return_type(target: Callable = None, *, detail: bool = False, paginated: bool = False):
    """Заполняет `return_type` и / или `return_pagination_type` и `paginated` при вызове декорируемой функции

    Notes:
        В зависимости от контекста, атрибутов класса и переданных аргументов подставляет в сигнатуру функции значения
        `return_type` и / или `return_pagination_type` и `paginated`

        Со следующим приоритетом по передаче значений:

        * Переданное в функцию значение при ее вызове
        * Возвращаемый тип для метода из контекста
        * Возвращаемый тип для метода из атрибутов класса
        * Возвращаемый тип из контекста
        * Возвращаемый тип из аттрибута класса

        Со следующим приоритетом по типу возвращаемого значения

        * Пагинация
        * Детали
        * Общий

    Args:
        target: Декорируемая функция
        detail: Нужно ли вернуть детали
        paginated: Нужно ли вернуть DTO с пагинацией

    """

    def decorator(function: Callable):
        method_name = getattr(function, "__method_name__", function.__name__)

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            # получаем контекст
            context = get_root_context()
            if not context.initialized:
                context = {}

            # проверяем необходимость пагинации
            _paginated = kwargs.get("paginated")
            if _paginated is None:
                _paginated = paginated

            if "paginated" in inspect.signature(function).parameters:
                (self, *args), kwargs = replace_args_values({"paginated": _paginated}, function, self, *args, **kwargs)

            # подставляем тип пагинации
            if _paginated:
                kwargs[ReturnTypeAttrs.RETURN_PAGINATION_TYPE] = (
                    kwargs.get(ReturnTypeAttrs.RETURN_PAGINATION_TYPE, None)
                    or context.get(f"{method_name}_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}")
                    or getattr(
                        self,
                        f"{method_name}_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}",
                        None,
                    )
                    or context.get(ReturnTypeAttrs.RETURN_PAGINATION_TYPE)
                    or getattr(self, ReturnTypeAttrs.RETURN_PAGINATION_TYPE, None)
                )

            # подставляем return_type для метода
            return_type = (
                kwargs.get(ReturnTypeAttrs.RETURN_TYPE, None)
                or context.get(f"{method_name}_{ReturnTypeAttrs.RETURN_TYPE}")
                or getattr(self, f"{method_name}_{ReturnTypeAttrs.RETURN_TYPE}", None)
            )
            # подставляем return_type для detail
            if detail:
                return_type = (
                    return_type
                    or context.get(ReturnTypeAttrs.RETURN_DETAIL_TYPE)
                    or getattr(self, ReturnTypeAttrs.RETURN_DETAIL_TYPE, None)
                )
            # подставляем общий return_type
            return_type = (
                return_type
                or context.get(ReturnTypeAttrs.RETURN_TYPE)
                or getattr(self, ReturnTypeAttrs.RETURN_TYPE, None)
            )
            kwargs[ReturnTypeAttrs.RETURN_TYPE] = return_type
            return function(self, *args, **kwargs)

        return wrapper

    if target and isinstance(target, Callable):
        return decorator(target)
    return decorator


def with_repository_atomic(target: Callable | None = None, /, attr="repository", **atomic_kwargs):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            with getattr(self, attr).__class__.atomic_decorator(**atomic_kwargs):
                return function(self, *args, **kwargs)

        return wrapper

    if target and isinstance(target, Callable):
        return decorator(target)
    return decorator
