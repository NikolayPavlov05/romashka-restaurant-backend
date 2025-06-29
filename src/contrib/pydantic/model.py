"""Модуль с кастомной моделью Pydantic

## Базовые модели

Classes:
    PaginatedModel: Базовая модель с пагинацией
    PydanticModelMeta: Мета класс для базовой модели
    PydanticModel: Базовая модель

## Базовые миксины и DTO

Classes:
    SearchMixin: Миксин поиска
    LimitMixin: Миксин лимита
    OffsetMixin: Миксин смещения
    OrderByMixin: DTO сортировки
    FilterQueryDTO: DTO фильтрации
    SearchQueryDTO: DTO поиска
    ExportXLSQueryDTO: DTO запроса экспорта xls
    ExportXLSResponseDTO: DTO ответа экспорта xls
    ValidationErrorItemDTO: DTO ошибки валидации
    ResultIdDTO: DTO ответа с id

"""
from __future__ import annotations

import sys
from math import ceil
from typing import Any
from typing import ClassVar
from typing import Literal

from django.conf import settings
from contrib.clean_architecture.dto_based_objects.fields import NestedEntity
from contrib.imports.services import import_by_string
from contrib.localization.services import gettext as _
from contrib.pydantic.mixins.interfaces import IProxyModelMixin
from contrib.pydantic.mixins.interfaces import IRequestModelMixin
from contrib.pydantic.mixins.interfaces import IResponseModelMixin
from contrib.subclass_control.mixins import ExtendedAttrsMixin
from contrib.subclass_control.mixins import ImportedStringAttrsMixin
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic._internal._model_construction import ModelMetaclass
from pydantic.fields import FieldInfo


class PydanticIgnore:
    pass


class PaginatedModel(BaseModel):
    """Базовая модель с пагинацией"""

    __is_paginated_model__: ClassVar[bool] = True

    current_page: int = Field(title=_("Текущая страница"))
    """Текущая страница"""
    max_pages: int = Field(title=_("Количество страниц"))
    """Количество страниц"""
    count: int = Field(title=_("Количество записей"))
    """Количество записей"""
    size: int = Field(title=_("Размер страницы"))
    """Размер страницы"""
    results: list[BaseModel] = Field(title=_("Записи"))
    """Записи"""

    @classmethod
    def create(cls, results: Any, count: int, limit: int = 20, offset: int = 0):
        """Создать экземпляр класса

        Args:
            results: Записи
            count: Количество записей
            limit: Лимит записей
            offset: Смещение записей

        Returns:

        """
        return cls(
            current_page=ceil(offset / limit) + 1,
            max_pages=ceil(count / limit),
            count=count,
            size=limit,
            results=results,
        )

    @classmethod
    def build_class(cls, result_class: type[PydanticModel]) -> type[PaginatedModel]:
        """Создать класс пагинации для конкретной модели

        Args:
            result_class: Модель для которой нужна пагинация

        Returns:
            new_class: Новый класс
        """
        name = f"Paginated{result_class.__name__}"
        bases = (PaginatedModel, *PaginatedModel.__bases__)
        attrs = {"__annotations__": {"results": list[result_class]}}
        new_class = type(name, bases, attrs)

        setattr(sys.modules[new_class.__module__], name, new_class)

        return new_class


class PydanticModelMeta(ImportedStringAttrsMixin, ModelMetaclass):
    """Мета класс для базовой модели"""

    _default_request_model_mixin: ClassVar[str | IRequestModelMixin] = settings.DEFAULT_PYDANTIC_REQUEST_MODEL_MIXIN
    _default_response_model_mixin: ClassVar[str | IResponseModelMixin] = settings.DEFAULT_PYDANTIC_RESPONSE_MODEL_MIXIN
    _default_proxy_model_mixin: ClassVar[str | IProxyModelMixin] = settings.DEFAULT_PYDANTIC_PROXY_MODEL_MIXIN

    imported_string_class_attrs: ClassVar[tuple] = {
        "_default_request_model_mixin",
        "_default_response_model_mixin",
        "_default_proxy_model_mixin",
    }

    def __new__(
        mcs,
        name: str,
        bases: tuple[type[Any], ...],
        attrs: dict[str, Any],
        request_model: type[IRequestModelMixin] | bool | str = False,
        response_model: type[IResponseModelMixin] | bool | str = False,
        proxy_model: type[IProxyModelMixin] | bool | str = False,
        with_paginated: bool = False,
        **kwargs: Any,
    ):
        """

        Args:
            mcs: Мета класс
            name: Имя класса
            bases: Родительские классы
            attrs: Атрибуты класса
            request_model: Добавить IRequestModelMixin в bases
            response_model: Добавить IResponseModelMixin в bases
            proxy_model: Добавить IProxyModelMixin в bases
            with_paginated: Добавить класс пагинации
            **kwargs: Дополнительные именованные аргументы
        """
        # Получаем request_model
        if request_model is True:
            request_model = mcs._default_request_model_mixin
        elif isinstance(request_model, str):
            request_model = import_by_string(request_model)

        # Получаем response_model
        if response_model is True:
            response_model = mcs._default_response_model_mixin
        elif isinstance(response_model, str):
            response_model = import_by_string(response_model)

        # Получаем proxy_model
        if proxy_model is True:
            proxy_model = mcs._default_proxy_model_mixin
        elif isinstance(proxy_model, str):
            proxy_model = import_by_string(proxy_model)

        # Расширяем bases
        if request_model and IRequestModelMixin not in bases:
            bases = (request_model, *bases)
        if response_model and IResponseModelMixin not in bases:
            bases = (response_model, *bases)
        if proxy_model and IProxyModelMixin not in bases:
            bases = (proxy_model, *bases)

        # Создаем новый класс
        cls: type = super().__new__(mcs, name, bases, attrs, **kwargs)

        # Добавляем класс пагинации
        if with_paginated:
            cls.paginated = PaginatedModel.build_class(cls)
        elif hasattr(cls, "paginated"):
            cls.paginated = None

        return cls


class PydanticModel(ExtendedAttrsMixin, BaseModel, metaclass=PydanticModelMeta):
    """Базовая модель"""

    __is_request_model__: ClassVar[bool] = False
    """Является ли текущий класс дочерним для IRequestModelMixin"""
    __is_response_model__: ClassVar[bool] = False
    """Является ли текущий класс дочерним для IResponseModelMixin"""
    __is_proxy_model__: ClassVar[bool] = False
    """Является ли текущий класс дочерним для IProxyModelMixin"""
    __is_paginated_model__: ClassVar[bool] = False
    """Добавлен ли класс пагинации"""

    extended_attrs: ClassVar[set] = {
        "dump_fields_mapping",
        "extra_select_related",
        "extra_prefetch_related",
    }
    model_config = ConfigDict(
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        ignored_types=(NestedEntity, PydanticIgnore),
    )

    paginated: ClassVar[type[PaginatedModel] | None] = None
    """Класс пагинации"""
    dump_fields_mapping: ClassVar[dict] = {}
    """Маппинг полей при вызове `model_dump`"""

    extra_select_related: ClassVar[set] = set()
    """Дополнительные select_related"""
    extra_prefetch_related: ClassVar[set] = set()
    """Дополнительные prefetch_related"""

    @property
    def extra_data(self):
        """Дополнительные данные полученные при инициализации экземпляра класса"""
        raise NotImplementedError

    @extra_data.setter
    def extra_data(self, value):
        """Дополнительные данные полученные при инициализации экземпляра класса"""
        raise NotImplementedError

    @property
    def original_object(self):
        """Оригинальный объект, записанный при вызове model_validate"""
        raise NotImplementedError

    @original_object.setter
    def original_object(self, value):
        """Оригинальный объект, записанный при вызове model_validate"""
        raise NotImplementedError

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: set = None,
        exclude: set = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        """Возвращает словарь со значениями полей модели

        Args:
            mode: Тип преобразования
            include: Включить поля
            exclude: Исключить поля
            context: Дополнительный контекст, прокидываемый в сериализатор
            by_alias: Получить через псевдоним
            exclude_unset: Исключить не переданные поля
            exclude_defaults: Исключить дефолтные поля
            exclude_none: Исключить поля со значением None
            round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
            warnings: Вызывать предупреждения
            serialize_as_any: Следует ли сериализовать поля с помощью поведения сериализации «утиной типизации»

        Returns:
            Словарь с данными

        """
        data = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

        if self.__is_proxy_model__:
            extra_data = self.extra_data
            if exclude:
                extra_data = {k: v for k, v in extra_data.items() if k not in exclude}
            data = {**extra_data, **data}

        for from_key, to_key in self.dump_fields_mapping.items():
            value = data.pop(from_key, None)
            data[to_key] = value

        return data

    @classmethod
    def layered_model_validate(
        cls,
        obj: Any,
        *layers: type[PydanticModel],
        strict: bool | None = None,
        from_attributes: bool | None = True,
        context: dict[str, Any] | None = None,
        include_current_layer: bool = True,
    ):
        """Конвертировать модели по слоям

        Args:
            obj: Оригинальный объект
            *layers: Слои для конвертации
            strict: Следует ли строго соблюдать типы
            from_attributes: Получать значения из атрибутов
            context: Контекст
            include_current_layer: Включать текущий слой

        Returns:
            Конвертированный объект

        """
        if include_current_layer:
            layers = (*layers, cls)

        kwargs = dict(strict=strict, from_attributes=from_attributes, context=context)
        for layer in layers:
            obj = layer.model_validate(obj, **kwargs)

        return obj

    @classmethod
    def add_fields(cls, rebuild=True, **field_definitions: Any):
        """Добавить поля к модели

        Args:
            rebuild: Перестроить модель
            **field_definitions: Определения полей

        """
        new_fields: dict[str, FieldInfo] = {}
        new_annotations: dict[str, type | None] = {}

        # Создаем новые поля
        for field_name, field_definition in field_definitions.items():
            if isinstance(field_definition, FieldInfo):
                new_fields[field_name] = field_definition
                continue

            if isinstance(field_definition, tuple):
                try:
                    field_annotation, field_value = field_definition
                except ValueError as e:
                    raise Exception(
                        "field definitions should either be a tuple of (<type>, <default>) or just a "
                        "default value, unfortunately this means tuples as "
                        "default values are not allowed"
                    ) from e
            else:
                field_annotation, field_value = None, field_definition

            if field_annotation:
                new_annotations[field_name] = field_annotation

            new_fields[field_name] = FieldInfo(annotation=field_annotation, default=field_value)

        # Перестраиваем модель
        cls.model_fields.update(new_fields)
        if rebuild:
            cls.model_rebuild(force=True)

        # Перестраиваем модель пагинации
        if cls.paginated:
            cls.paginated = PaginatedModel.build_class(cls)


class SearchMixin(PydanticModel):
    """Миксин поиска"""

    search: str = Field(title=_("Поиск"), default="")


class LimitMixin(PydanticModel):
    """Миксин лимита"""

    limit: int = Field(title=_("Количество записей в выборке"), default=20)


class OffsetMixin(PydanticModel):
    """Миксин смещения"""

    offset: int = Field(title=_("Смещение записей в выборке"), default=0)


class OrderByMixin(PydanticModel):
    """DTO сортировки"""

    order_by: list[str] = Field(title=_("Сортировка"), default_factory=list)


class FilterQueryDTO(LimitMixin, OffsetMixin, OrderByMixin, request_model=True):
    """DTO фильтрации"""


class SearchQueryDTO(SearchMixin, FilterQueryDTO):
    """DTO поиска"""


class ExportXLSQueryDTO(PydanticModel, request_model=True):
    """DTO запроса экспорта xls"""

    ids: list[int] | None = Field(title=_("ID объектов"), default=None)
    fields: list[str] = Field(title=_("Список полей для экспорта"), default_factory=list)


class ExportXLSResponseDTO(PydanticModel):
    """DTO ответа экспорта xls"""

    file_content: bytes
    file_name: str


class ValidationErrorItemDTO(PydanticModel):
    """DTO ошибки валидации"""

    loc: list[str] | None = None
    msg: str | None = None
    if settings.DEBUG:
        type: str | None = None
        input: Any = None
        url: str | None = None


class ResultIdDTO(PydanticModel):
    """DTO ответа с id"""

    id: int | str = Field(title=_("ID объекта"))
    error_code: str | None = None
