"""Модуль утилит для работы с [`PydanticModel`][agora.contrib.pydantic.model.PydanticModel]

Classes:
    validator_wrapper: Форматирует ошибки валидации
    csv_sequence: Преобразует типы

"""
from __future__ import annotations

from collections.abc import Buffer
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import AfterValidator
from pydantic import BeforeValidator
from pydantic import WrapValidator


class _ValidatorWrapper:
    _function: Callable
    _before: BeforeValidator | None = None
    _after: AfterValidator | None = None
    _wrap: WrapValidator | None = None

    def __init__(self, function):
        self._function = function

    @property
    def before(self):
        if self._before:
            return self._before
        self._before = BeforeValidator(self._function)
        return self._before

    @property
    def after(self):
        if self._after:
            return self._after
        self._after = AfterValidator(self._function)
        return self._after

    @property
    def wrap(self):
        if self._wrap:
            return self._wrap
        self._wrap = WrapValidator(self._function)
        return self._wrap

    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)


validator_wrapper = _ValidatorWrapper
"""Враппер для валидации

Examples:
    ``` py linenums="1" title="Пример создания класса и метода"
    @validator_wrapper
    def foo(value):
        pass
    ```
    ``` py linenums="1" title="Пример использования функционала"
    validator = foo
    before_validator = foo.before
    after_validator = foo.after
    wrap_validator = foo.wrap
    ```
"""


@validator_wrapper
def csv_sequence(value: Sequence[Any] | str | None) -> Sequence[Any]:
    """Преобразует значение в последовательность"""
    if not value:
        return []
    if isinstance(value, Sequence) and len(value) == 1:
        return str(value[0]).replace("[", "").replace("]", "").split(",")
    elif isinstance(value, str):
        return value.replace("[", "").replace("]", "").split(",")
    return value


def string_to_date(_format: str = "%Y.%m.%d"):
    @validator_wrapper
    def _date_from_string(value: str | date | None) -> date | None:
        if value is None:
            return
        if isinstance(value, date):
            return value
        return datetime.strptime(value, _format).date()

    return _date_from_string


def string_to_datetime(_format: str = "%Y.%m.%dT%H:%M:%S"):
    @validator_wrapper
    def _datetime_from_string(value: str | datetime | None) -> datetime | None:
        if value is None:
            return
        if isinstance(value, date):
            return value
        return datetime.strptime(value, _format)

    return _datetime_from_string


@validator_wrapper
def flag_validator(value: Any) -> Literal[0, 1] | None:
    if value is None:
        return
    return 1 if value else 0


@validator_wrapper
def list_validator(value: Any) -> list | None:
    if value is None:
        return

    if not isinstance(value, (list, tuple)):
        return [value]
    return value


@validator_wrapper
def force_list_validator(value: Any) -> list | None:
    if value is None:
        return
    if isinstance(value, (str, bytes, Mapping, Buffer)) or not isinstance(value, Iterable):
        return [value]
    return list(value)


@validator_wrapper
def file_url_validator(value: Any) -> str | None:
    try:
        return value.url
    except Exception:
        return
