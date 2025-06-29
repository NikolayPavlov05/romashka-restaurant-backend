"""Модуль с интерфейсами миксинов для кастомной модели Pydantic

Classes:
    IRequestModelMixin: Интерфейс миксина модели запроса
    IResponseModelMixin: Интерфейс миксина модели ответа
    IProxyModelMixin: Интерфейс прокси модели

"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import ClassVar

from pydantic_core.core_schema import ValidationInfo
from pydantic_core.core_schema import ValidatorFunctionWrapHandler


class IRequestModelMixin(ABC):
    """Интерфейс миксина модели запроса"""

    __is_request_model__: ClassVar[bool]
    """Является ли текущий класс дочерним для IRequestModelMixin"""

    @classmethod
    @abstractmethod
    def request_validator(cls, value: Any, info: ValidationInfo) -> Any:
        """Валидирует данные для запроса

        Args:
            value: Значение
            info: Контекст

        Returns:
            Any
        """


class IResponseModelMixin(ABC):
    """Интерфейс миксина модели ответа"""

    __is_response_model__: ClassVar[bool]
    """Является ли текущий класс дочерним для IResponseModelMixin"""

    @classmethod
    @abstractmethod
    def response_validator(cls, value: str, info: ValidationInfo) -> Any:
        """Валидирует данные для ответа

        Args:
            value: Значение
            info: Контекст

        Returns:
            Any
        """


class IProxyModelMixin(ABC):
    """Интерфейс прокси модели"""

    __is_proxy_model__: ClassVar[bool] = True
    """Является ли текущий класс дочерним для IProxyModelMixin"""

    _original_object: Any
    _extra_data: Any

    @property
    @abstractmethod
    def extra_data(self):
        """Дополнительные данные полученные при инициализации экземпляра класса"""

    @extra_data.setter
    @abstractmethod
    def extra_data(self, value):
        """Дополнительные данные полученные при инициализации экземпляра класса"""

    @property
    @abstractmethod
    def original_object(self):
        """Оригинальный объект, записанный при вызове model_validate"""

    @original_object.setter
    @abstractmethod
    def original_object(self, value):
        """Оригинальный объект, записанный при вызове model_validate"""

    @abstractmethod
    def save_original(self, handler: ValidatorFunctionWrapHandler):
        """Сохраняет оригинальный объект при вызове model_validate"""

    @abstractmethod
    def get_or_retrieve_field_value(self, value):
        """Вызывает all в случае если value является m2m или reverse m2o."""
