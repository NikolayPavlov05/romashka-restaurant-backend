"""Модуль с базовыми миксинами для кастомной модели Pydantic

Classes:
    BaseRequestModelMixin: Базовый миксин модели запроса
    BaseResponseModelMixin: Базовый миксин модели ответа
    BaseProxyModelMixin: Базовая прокси модели

"""
from __future__ import annotations

from abc import ABC

from contrib.pydantic.mixins.interfaces import IProxyModelMixin
from contrib.pydantic.mixins.interfaces import IRequestModelMixin
from contrib.pydantic.mixins.interfaces import IResponseModelMixin
from pydantic import BaseModel
from pydantic import model_validator
from pydantic import PrivateAttr
from pydantic_core.core_schema import ValidatorFunctionWrapHandler


class BaseRequestModelMixin(IRequestModelMixin, BaseModel, ABC):
    """Базовый миксин модели запроса"""

    __is_request_model__ = True


class BaseResponseModelMixin(IResponseModelMixin, BaseModel, ABC):
    """Базовый миксин модели ответа"""

    __is_response_model__ = True


class BaseProxyModelMixin(IProxyModelMixin, BaseModel, ABC):
    """Базовая прокси модели"""

    __is_proxy_model__ = True

    _original_object = PrivateAttr(default=None)
    _extra_data = PrivateAttr(default_factory=dict)

    def __init__(self, /, **kwargs):
        extra_data = {}
        for key in list(kwargs):
            if key not in self.model_fields:
                extra_data[key] = kwargs.pop(key)

        super().__init__(**kwargs)
        self.extra_data = extra_data

    def __getattr__(self, item, max_depth=0, depth=0):
        try:
            return super().__getattr__(item)
        except AttributeError:
            try:
                return self.extra_data[item]
            except KeyError:
                return getattr(self.original_object, item)

    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except (AttributeError, ValueError):
            self.extra_data[name] = value

    @property
    def extra_data(self):
        return self._extra_data

    @extra_data.setter
    def extra_data(self, value):
        self._extra_data = value

    @property
    def original_object(self):
        return self._original_object

    @original_object.setter
    def original_object(self, value):
        self._original_object = value

    @model_validator(mode="wrap")
    def save_original(self, handler: ValidatorFunctionWrapHandler):
        validated_self = handler(self)
        validated_self.original_object = self
        return validated_self
