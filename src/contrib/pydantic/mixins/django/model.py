"""Модуль с django миксинами для кастомной модели Pydantic

Classes:
    DjangoRequestModelMixin: Django миксин модели запроса
    DjangoResponseModelMixin: Django миксин модели ответа
    DjangoProxyModelMixin: Django миксин прокси модели

"""
from __future__ import annotations

from typing import Any

from contrib.inspect.services import sequence_type_check
from contrib.pydantic.mixins.bases import BaseProxyModelMixin
from contrib.pydantic.mixins.bases import BaseRequestModelMixin
from contrib.pydantic.mixins.bases import BaseResponseModelMixin
from contrib.pydantic.validators import csv_sequence
from django.core.files import File
from django.db.models.manager import BaseManager
from django.db.models.manager import Manager
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo


class DjangoRequestModelMixin(BaseRequestModelMixin):
    """Django миксин модели запроса"""

    @field_validator("*", mode="before")
    @classmethod
    def request_validator(cls, value: Any, info: ValidationInfo) -> Any:
        annotation = cls.model_fields[info.field_name].annotation
        is_sequence, origin_type = sequence_type_check(annotation)
        if is_sequence and not issubclass(origin_type, File):
            return csv_sequence(value)
        return value


class DjangoResponseModelMixin(BaseResponseModelMixin):
    """Django миксин модели ответа"""

    @field_validator("*", mode="before")
    @classmethod
    def response_validator(cls, value: str, info: ValidationInfo) -> Any:
        if isinstance(value, BaseManager):
            value = list(value.all())
        return value


class DjangoProxyModelMixin(BaseProxyModelMixin):
    """Django миксин модели"""

    def get_or_retrieve_field_value(self, value):
        """Вызывает all в случае если value является m2m или reverse m2o."""
        if isinstance(value, Manager):
            return value.all()
        return value
