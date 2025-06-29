"""Модуль типов для работы с кастомной моделью Pydantic

Classes:
    ErrorItem: Ошибка

"""
from __future__ import annotations

from typing import Annotated
from typing import Literal
from typing import TypedDict

from contrib.pydantic.validators import file_url_validator
from contrib.pydantic.validators import flag_validator
from contrib.pydantic.validators import force_list_validator
from pydantic import PlainSerializer
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber


class ErrorItem(TypedDict):
    """Ошибка"""

    code: str
    detail: str
    location: tuple[str | int] | None


class _PhoneNumber(PydanticPhoneNumber):
    phone_format = "INTERNATIONAL"


PhoneNumber = Annotated[_PhoneNumber, PlainSerializer(str, return_type=str)]

RequestIds = list[int] | str | None


Flag = Annotated[Literal[0, 1], flag_validator.before] | bool


type ForceList[T] = Annotated[list[T], force_list_validator.before]


type FileUrl = Annotated[str | None, file_url_validator.before]
