from __future__ import annotations

import http
from abc import ABCMeta
from typing import Any

from contrib.pydantic.schema_generator import AdaptedGenerateJsonSchema
from pydantic import BaseModel
from rest_framework.response import Response


class HTTPExceptionManager(ABCMeta):
    """Менеджер для кастомных исключений"""

    _registered: list[type[BaseHTTPException]] = []

    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)

        # Регистрируем новое исключение
        if cls.__base__ is not _BaseHTTPException:
            mcs._registered.append(cls)

        return cls

    @classmethod
    def get_objects(mcs):
        """Возвращает все зарегистрированные исключения"""
        return mcs._registered


class _BaseHTTPException(Exception):
    """Приватное базовое кастомное исключение"""

    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """

        Args:
            status_code: Код статуса
            detail: Детали ошибки
            headers: Заголовки
        """
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase

        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class BaseHTTPException(_BaseHTTPException, metaclass=HTTPExceptionManager):
    """Базовое кастомное исключение"""

    _existed_errors_codes: set = set()

    headers: dict = {"WWW-Authenticate": "Bearer"}
    """Заголовки"""
    openapi_description: str = ""
    """Описание в спецификации openapi"""

    _response_model: type[BaseModel] = None

    status_code: int = None
    """Код статуса"""
    error_code: str = None
    """Код ошибки"""
    error_item_type: Any = Any
    """Тип элемента списка ошибок"""
    contains_errors = False
    """Содержит ли список ошибок"""

    default_message: str = None
    """Сообщение по умолчанию"""

    detail: str = None
    """Детали ошибки"""
    data: Any = None
    """Дополнительные данные"""
    errors: Any = None
    """Список ошибок"""

    def __init_subclass__(cls):
        if cls.status_code is None:
            raise AttributeError("Атрибут status_code не может быть None")
        if cls.error_code is None:
            raise AttributeError("Атрибут error_code не может быть None")
        if cls.error_code in cls._existed_errors_codes:
            raise AttributeError(f"Код ошибки {cls.error_code} уже занят")

        cls._set_response_model()
        cls._existed_errors_codes.add(cls.error_code)

    def __init__(self, message: str = None, data: Any = None, errors: Any = None):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail or message,
            headers=self.headers,
        )

        self.errors = errors
        self.data = data
        self.detail = self.detail.format(message=message or self.default_message)

    @classmethod
    def _set_response_model(cls):
        """Записывает модель ошибки для дальнейшего получения схемы"""
        if cls._response_model:
            return

        class ResponseModel(BaseModel):
            detail: str = cls.detail.format(message=cls.default_message)
            error_code: str = cls.error_code
            if cls.contains_errors:
                errors: list[cls.error_item_type]

        cls._response_model = ResponseModel
        cls._response_model.__name__ = cls.__name__

    def model_dump(self):
        """Возвращает словарь с данными об ошибке"""
        return self._response_model.model_validate(self, from_attributes=True).model_dump()

    @property
    def response(self):
        """Возвращает HTTP ответ"""
        return Response(self.model_dump(), status=self.status_code)

    @classmethod
    def get_reference(cls):
        """Возвращает ссылку в спецификации openapi"""
        return {"$ref": f"#/components/schemas/{cls.__name__}"}

    @classmethod
    def get_schema(cls, schema_generator=AdaptedGenerateJsonSchema):
        """Возвращает схему в спецификации openapi"""
        ref_template = "#/components/schemas/{model}"
        return cls._response_model.model_json_schema(ref_template=ref_template, schema_generator=schema_generator)

    @classmethod
    def get_openapi_response(cls):
        """Возвращает ответы в спецификации openapi"""
        data = {
            "content": {"application/json": {"schema": cls.get_reference()}},
            "description": cls.openapi_description,
        }
        return cls.status_code, data
