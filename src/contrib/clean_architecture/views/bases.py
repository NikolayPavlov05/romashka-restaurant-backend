"""Модуль с базовым представлением и миксинами

## Базовые представления

Classes:
    CleanViewSetMeta: Мета класс базового представления
    CleanViewSet: Базовое представление

## Создание

Classes:
    CreateCleanViewSetMixin: Миксин представления создания

## Обновление

Classes:
    UpdateCleanViewSetMixin: Миксин представления обновления
    PatchListCleanViewSetMixin: Миксин представлени`я обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}

## Удаление

Classes:
    DeleteCleanViewSetMixin: Миксин представления удаления

## Получение записи

Classes:
    DetailCleanViewSetMixin: Миксин представления получения деталей
    DetailByPKCleanViewSetMixin: Миксин представления получения деталей по первичному ключу
    DetailByExternalCodeCleanViewSetMixin: Миксин представления получения деталей по внешнему коду

## Получение списка записей

Classes:
    RetrieveCleanViewSetMixin: Миксин представления получения списка объектов
    SearchCleanViewSetMixin: Миксин представления получения списка объектов по полнотекстовому поиску

## Экспорт записей

Classes:
    ExportXLSCleanViewSetMixin: Миксин представления экспорта списка объектов

## Комбинации интерфейсов миксинов представлений

Classes:
    CreateUpdateCleanViewSetMixin: Миксин представления создания / обновления
    UpdateDeleteCleanViewSetMixin: Миксин представления обновления / удаления
    CreateDeleteCleanViewSetMixin: Миксин представления создания / удаления
    CreateUpdateDeleteCleanViewSetMixin: Миксин представления создания / обновления / удаления
    DetailsCleanViewSetMixin: Миксин представления получения деталей
    ListCleanViewSetMixin: Миксин представления получения списка объектов
    ReadCleanViewSetMixin: Миксин представления получения деталей / списка объектов
    CRUDCleanViewSetMixin: Миксин представления создание / чтение /обновление / удаление

"""
from __future__ import annotations

import re
from abc import ABCMeta
from typing import Any

from contrib.clean_architecture.consts import CleanMethods
from contrib.clean_architecture.consts import ReturnTypeAttrs
from contrib.clean_architecture.consts import ViewActionAttrs
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import RequestDTO
from contrib.clean_architecture.providers.controllers.bases import Controller
from contrib.clean_architecture.providers.controllers.bases import CreateControllerMixin
from contrib.clean_architecture.providers.controllers.bases import CreateDeleteControllerMixin
from contrib.clean_architecture.providers.controllers.bases import CreateUpdateControllerMixin
from contrib.clean_architecture.providers.controllers.bases import CreateUpdateDeleteControllerMixin
from contrib.clean_architecture.providers.controllers.bases import CRUDControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DeleteControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailByExternalCodeControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailByPKControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailsControllerMixin
from contrib.clean_architecture.providers.controllers.bases import ExportXLSControllerMixin
from contrib.clean_architecture.providers.controllers.bases import ListControllerMixin
from contrib.clean_architecture.providers.controllers.bases import PatchListControllerMixin
from contrib.clean_architecture.providers.controllers.bases import ReadControllerMixin
from contrib.clean_architecture.providers.controllers.bases import RetrieveControllerMixin
from contrib.clean_architecture.providers.controllers.bases import SearchControllerMixin
from contrib.clean_architecture.providers.controllers.bases import UpdateControllerMixin
from contrib.clean_architecture.providers.controllers.bases import UpdateDeleteControllerMixin
from contrib.clean_architecture.renderers import XLSRenderer
from contrib.clean_architecture.types import mixin_for
from contrib.clean_architecture.utils.method import clean_method
from contrib.clean_architecture.utils.method import CleanMethodMixin
from contrib.clean_architecture.utils.names import to_snake_case
from contrib.clean_architecture.views.utils import exception_handler
from contrib.context import get_root_context
from contrib.exceptions.exceptions import ActionImpossible
from contrib.exceptions.utils import responses_from_exceptions
from contrib.localization.services import gettext_lazy as _
from contrib.module_manager.decorators import inject
from contrib.openapi.decorators import action
from contrib.openapi.decorators import endpoint_permissions
from contrib.openapi.views import AutoSchema
from contrib.pydantic.model import ExportXLSQueryDTO
from contrib.pydantic.model import FilterQueryDTO
from contrib.pydantic.model import PaginatedModel
from contrib.pydantic.model import ResultIdDTO
from contrib.pydantic.model import SearchQueryDTO
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin


class CleanViewSetMeta(ABCMeta):
    """Мета класс базового представления"""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type[Any], ...],
        attrs: dict[str, Any],
        injects: tuple[str] = (),
    ):
        cls: type = super().__new__(mcs, name, bases, attrs)
        # Добавляем необходимые инжекты
        if injects:
            return inject(*injects)(cls)
        return cls


class CleanViewSet(CleanMethodMixin, ViewSetMixin, APIView, metaclass=CleanViewSetMeta):
    """Базовое представление"""

    processing_mapping: Controller
    """Контроллер"""
    permission_classes = [IsAuthenticated]
    """Классы разрешений"""
    schema: Any = None
    """Класс генератора схемы"""

    tags: list[str] = None
    """Теги openapi"""
    path_prefix: str = None
    """Префикс пути для url"""

    return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""
    return_detail_type: type[DTO] = None
    """DTO деталей, которое нужно вернуть"""
    return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    set_return_context: bool = True
    """Записывать return_type в контекст"""

    def __init_subclass__(cls, view_set_base: bool = False, **kwargs):
        # Добавляем генератор схемы в класс
        if not view_set_base:
            cls.schema = AutoSchema(
                tags=(cls.tags if cls.tags is not None else [cls.get_snake_view_name_by_class()]),
                operation_id_base=cls.get_camel_view_name_by_class(),
            )

        super().__init_subclass__(**kwargs)

        # Оборачивает все clean_methods требуемыми декораторами
        if not view_set_base:
            cls._wrap_methods()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Записываем все return_type в контекст
        if self.set_return_context:
            context = get_root_context()
            context.set(ReturnTypeAttrs.RETURN_TYPE, self.return_type)
            context.set(ReturnTypeAttrs.RETURN_DETAIL_TYPE, self.return_detail_type)
            context.set(ReturnTypeAttrs.RETURN_PAGINATION_TYPE, self.return_pagination_type)

            for method_name in self.clean_methods_names:
                method_return_type = getattr(self, f"{method_name}_{ReturnTypeAttrs.RETURN_TYPE}", None)
                method_return_pagination_type = getattr(
                    self,
                    f"{method_name}_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}",
                    None,
                )
                context.set(f"{method_name}_{ReturnTypeAttrs.RETURN_TYPE}", method_return_type)
                context.set(
                    f"{method_name}_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}",
                    method_return_pagination_type,
                )

    @classmethod
    def get_camel_view_name_by_class(cls) -> str:
        """Возвращает имя представления в camel case"""
        view_name = re.sub(r"ViewSet$", "", cls.__name__)
        return re.sub(r"View$", "", view_name)

    @classmethod
    def get_snake_view_name_by_class(cls) -> str:
        """Возвращает имя представления в snake case"""
        view_name = re.sub(r"_view_set$", "", to_snake_case(cls.__name__))
        view_name = re.sub(r"_view$", "", view_name)
        return view_name.replace("_", "-")

    @classmethod
    def get_path_prefix(cls):
        """Возвращает префикс пути"""
        return f"{cls.path_prefix if cls.path_prefix is not None else cls.get_snake_view_name_by_class()}"

    @classmethod
    def _get_method_attr(cls, method_name: str, attr_name: str):
        """Возвращает значение атрибута метода

        Args:
            method_name: Имя метода
            attr_name: Имя атрибута

        Returns:

        """
        get_method_attr = getattr(cls, f"get_{method_name}_{attr_name}", None)
        return get_method_attr() if get_method_attr else getattr(cls, f"{method_name}_{attr_name}", None)

    @classmethod
    def _wrap_methods(cls):
        """Оборачивает все clean_methods требуемыми декораторами"""
        for method_attr_name, method in cls.clean_methods.items():
            method_name = method.__method_name__
            methods = cls._get_method_attr(method_name, ViewActionAttrs.METHODS)
            url_path = cls._get_method_attr(method_name, ViewActionAttrs.URL_PATH)
            url_name = cls._get_method_attr(method_name, ViewActionAttrs.URL_NAME)
            request_model = cls._get_method_attr(method_name, ViewActionAttrs.REQUEST_MODEL)
            response_schema = cls._get_method_attr(method_name, ViewActionAttrs.RESPONSE_SCHEMA)
            responses = cls._get_method_attr(method_name, ViewActionAttrs.RESPONSES)
            status_map = cls._get_method_attr(method_name, ViewActionAttrs.STATUS_MAP)
            description = cls._get_method_attr(method_name, ViewActionAttrs.DESCRIPTION)
            summary = cls._get_method_attr(method_name, ViewActionAttrs.SUMMARY)
            tags = cls._get_method_attr(method_name, ViewActionAttrs.TAGS)
            permissions = cls._get_method_attr(method_name, ViewActionAttrs.PERMISSIONS)

            action_decorator = action(
                methods=methods,
                url_path=url_path,
                url_name=url_name,
                request_model=request_model,
                response_schema=response_schema,
                responses=responses,
                status_map=status_map,
                description=description,
                summary=summary,
                tags=tags,
            )

            method = action_decorator(method)
            if permissions:
                method = endpoint_permissions(*permissions)

            setattr(cls, method_attr_name, method)

    def get_exception_handler(self):
        """Возвращает хэндлер исключения"""
        return exception_handler


class CreateCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления создания"""

    controller: CreateControllerMixin

    create_methods = ["post"]
    """Список HTTP методов"""
    create_permissions = ()
    """Кортеж разрешений"""
    create_url_path = None
    """Путь URL"""
    create_url_name = None
    """Имя URL"""
    create_request_model = None
    """Модель запроса"""
    create_response_schema = ResultIdDTO
    """Модель ответа"""
    create_responses = responses_from_exceptions(ActionImpossible)
    """Возможные варианты ответа"""
    create_status_map = {"POST": status.HTTP_201_CREATED}
    """Маппинг HTTP методов и статусов ответа"""
    create_description = _("Создание записи")
    """Описание эндпоинта"""
    create_summary = None
    """Краткое описание эндпоинта"""
    create_tags = None
    """Список тегов"""
    create_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    @classmethod
    def get_create_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.create_methods

    @classmethod
    def get_create_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.create_permissions

    @classmethod
    def get_create_url_path(cls):
        """Возвращает путь URL"""
        if cls.create_url_path is not None:
            return cls.create_url_path
        return f"{cls.get_path_prefix()}/create"

    @classmethod
    def get_create_url_name(cls):
        """Возвращает имя URL"""
        if cls.create_url_name is not None:
            return cls.create_url_name
        return f"{cls.get_snake_view_name_by_class()}-create"

    @classmethod
    def get_create_request_model(cls):
        """Возвращает модель запроса"""
        return cls.create_request_model

    @classmethod
    def get_create_response_schema(cls):
        """Возвращает модель ответа"""
        return cls.create_response_schema

    @classmethod
    def get_create_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.create_responses

    @classmethod
    def get_create_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.create_status_map

    @classmethod
    def get_create_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.create_description

    @classmethod
    def get_create_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.create_summary

    @classmethod
    def get_create_tags(cls):
        """Возвращает список тегов"""
        return cls.create_tags

    @classmethod
    def get_create_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.create_controller_extra_kwargs

    @clean_method(name=CleanMethods.CREATE)
    def create_action(self, request: HttpRequest, payload: RequestDTO, *args, **kwargs):
        """Создает запись в БД

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_create_response_schema()
        """
        return self.controller.create(payload, **kwargs, **(self.get_create_controller_extra_kwargs() or {}))


class UpdateCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления обновления"""

    controller: UpdateControllerMixin

    update_methods = ["patch"]
    """Список HTTP методов"""
    update_permissions = ()
    """Кортеж разрешений"""
    update_url_path = None
    """Путь URL"""
    update_url_name = None
    """Имя URL"""
    update_request_model = None
    """Модель запроса"""
    update_response_schema = ResultIdDTO
    """Модель ответа"""
    update_responses = responses_from_exceptions(ActionImpossible)
    """Возможные варианты ответа"""
    update_status_map = {"PATCH": status.HTTP_202_ACCEPTED}
    """Маппинг HTTP методов и статусов ответа"""
    update_description = _("Обновление записи")
    """Описание эндпоинта"""
    update_summary = None
    """Краткое описание эндпоинта"""
    update_tags = None
    """Список тегов"""
    update_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    @classmethod
    def get_update_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.update_methods

    @classmethod
    def get_update_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.update_permissions

    @classmethod
    def get_update_url_path(cls):
        """Возвращает путь URL"""
        if cls.update_url_path is not None:
            return cls.update_url_path
        return rf"{cls.get_path_prefix()}/(?P<pk>[\d]+)/update"

    @classmethod
    def get_update_url_name(cls):
        """Возвращает имя URL"""
        if cls.update_url_name is not None:
            return cls.update_url_name
        return f"{cls.get_snake_view_name_by_class()}-update"

    @classmethod
    def get_update_request_model(cls):
        """Возвращает модель запроса"""
        return cls.update_request_model

    @classmethod
    def get_update_response_schema(cls):
        """Возвращает модель ответа"""
        return cls.update_response_schema

    @classmethod
    def get_update_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.update_responses

    @classmethod
    def get_update_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.update_status_map

    @classmethod
    def get_update_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.update_description

    @classmethod
    def get_update_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.update_summary

    @classmethod
    def get_update_tags(cls):
        """Возвращает список тегов"""
        return cls.update_tags

    @classmethod
    def get_update_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.update_controller_extra_kwargs

    @clean_method(name=CleanMethods.UPDATE)
    def update_action(self, request: HttpRequest, pk: int, payload: RequestDTO, *args, **kwargs):
        """Обновляет запись в БД

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_update_response_schema()
        """
        return self.controller.update(pk, payload, **(self.get_update_controller_extra_kwargs() or {}))


class PatchListCleanViewSetMixin(UpdateCleanViewSetMixin):
    """Миксин представления обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}"""

    controller: PatchListControllerMixin

    @clean_method(name=CleanMethods.UPDATE)
    def update_action(self, request: HttpRequest, payload: RequestDTO, *args, **kwargs):
        """Обновляет модели списком

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        """
        return self.controller.patch_list(payload, **(self.get_update_controller_extra_kwargs() or {}))


class DeleteCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления удаления"""

    controller: DeleteControllerMixin

    delete_methods = ["delete"]
    """Список HTTP методов"""
    delete_permissions = ()
    """Кортеж разрешений"""
    delete_url_path = None
    """Путь URL"""
    delete_url_name = None
    """Имя URL"""
    delete_request_model = None
    """Модель запроса"""
    delete_response_schema = ResultIdDTO
    """Модель ответа"""
    delete_responses = responses_from_exceptions(ActionImpossible)
    """Возможные варианты ответа"""
    delete_status_map = {"DELETE": status.HTTP_202_ACCEPTED}
    """Маппинг HTTP методов и статусов ответа"""
    delete_description = _("Удаление записи")
    """Описание эндпоинта"""
    delete_summary = None
    """Краткое описание эндпоинта"""
    delete_tags = None
    """Список тегов"""
    delete_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    @classmethod
    def get_delete_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.delete_methods

    @classmethod
    def get_delete_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.delete_permissions

    @classmethod
    def get_delete_url_path(cls):
        """Возвращает путь URL"""
        if cls.delete_url_path is not None:
            return cls.delete_url_path
        return rf"{cls.get_path_prefix()}/(?P<pk>[\d]+)/delete"

    @classmethod
    def get_delete_url_name(cls):
        """Возвращает имя URL"""
        if cls.delete_url_name is not None:
            return cls.delete_url_name
        return f"{cls.get_snake_view_name_by_class()}-delete"

    @classmethod
    def get_delete_request_model(cls):
        """Возвращает модель запроса"""
        return cls.delete_request_model

    @classmethod
    def get_delete_response_schema(cls):
        """Возвращает модель ответа"""
        return cls.delete_response_schema

    @classmethod
    def get_delete_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.delete_responses

    @classmethod
    def get_delete_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.delete_status_map

    @classmethod
    def get_delete_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.delete_description

    @classmethod
    def get_delete_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.delete_summary

    @classmethod
    def get_delete_tags(cls):
        """Возвращает список тегов"""
        return cls.delete_tags

    @classmethod
    def get_delete_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.delete_controller_extra_kwargs

    @clean_method(name=CleanMethods.DELETE)
    def delete_action(self, request: HttpRequest, pk: int, *args, **kwargs):
        """Удаляет запись в БД по pk

        Args:
            request: Экземпляр HTTP запроса
            pk: Первичный ключ
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_delete_response_schema()
        """
        return self.controller.delete(pk, **(self.get_delete_controller_extra_kwargs() or {}))


class DetailCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления получения деталей"""

    controller: DetailControllerMixin

    detail_methods = ["get"]
    """Список HTTP методов"""
    detail_permissions = ()
    """Кортеж разрешений"""
    detail_url_path = None
    """Путь URL"""
    detail_url_name = None
    """Имя URL"""
    detail_request_model = None
    """Модель запроса"""
    detail_response_schema = None
    """Модель ответа"""
    detail_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    detail_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    detail_description = _("Получение записи")
    """Описание эндпоинта"""
    detail_summary = None
    """Краткое описание эндпоинта"""
    detail_tags = None
    """Список тегов"""
    detail_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    detail_return_type: type[DTO] = None
    """DTO которое, нужно вернуть для метода"""

    @classmethod
    def get_detail_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.detail_methods

    @classmethod
    def get_detail_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.detail_permissions

    @classmethod
    def get_detail_url_path(cls):
        """Возвращает путь URL"""
        if cls.detail_url_path is not None:
            return cls.detail_url_path
        return f"{cls.get_path_prefix()}/detail"

    @classmethod
    def get_detail_url_name(cls):
        """Возвращает имя URL"""
        if cls.detail_url_name is not None:
            return cls.detail_url_name
        return f"{cls.get_snake_view_name_by_class()}-detail"

    @classmethod
    def get_detail_request_model(cls):
        """Возвращает модель запроса"""
        return cls.detail_request_model

    @classmethod
    def get_detail_response_schema(cls):
        """Возвращает модель ответа"""
        return cls.detail_response_schema or cls.detail_return_type or cls.return_detail_type or cls.return_type

    @classmethod
    def get_detail_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.detail_responses

    @classmethod
    def get_detail_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.detail_status_map

    @classmethod
    def get_detail_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.detail_description

    @classmethod
    def get_detail_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.detail_summary

    @classmethod
    def get_detail_tags(cls):
        """Возвращает список тегов"""
        return cls.detail_tags

    @classmethod
    def get_detail_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.detail_controller_extra_kwargs

    @clean_method(name=CleanMethods.DETAIL)
    def detail_action(self, request: HttpRequest, payload: RequestDTO = None, *args, **kwargs):
        """Возвращает DTO записи, удовлетворяющей запросу

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_detail_response_schema()
        """
        return self.controller.detail(
            **(payload.model_dump(exclude_none=True) if payload else {}),
            **(self.get_detail_controller_extra_kwargs() or {}),
        )


class DetailByPKCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления получения деталей по первичному ключу"""

    controller: DetailByPKControllerMixin

    detail_by_pk_methods = ["get"]
    """Список HTTP методов"""
    detail_by_pk_permissions = ()
    """Кортеж разрешений"""
    detail_by_pk_url_path = None
    """Путь URL"""
    detail_by_pk_url_name = None
    """Имя URL"""
    detail_by_pk_request_model = None
    """Модель запроса"""
    detail_by_pk_response_schema = None
    """Модель ответа"""
    detail_by_pk_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    detail_by_pk_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    detail_by_pk_description = _("Получение записи по ID")
    """Описание эндпоинта"""
    detail_by_pk_summary = None
    """Краткое описание эндпоинта"""
    detail_by_pk_tags = None
    """Список тегов"""
    detail_by_pk_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    detail_by_pk_return_type: type[DTO] = None
    """DTO которое, нужно вернуть для метода"""

    @classmethod
    def get_detail_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.detail_by_pk_methods

    @classmethod
    def get_detail_by_pk_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.detail_by_pk_permissions

    @classmethod
    def get_detail_by_pk_url_path(cls):
        """Возвращает путь URL"""
        if cls.detail_by_pk_url_path is not None:
            return cls.detail_by_pk_url_path
        return rf"{cls.get_path_prefix()}/(?P<pk>[\d]+)"

    @classmethod
    def get_detail_by_pk_url_name(cls):
        """Возвращает имя URL"""
        if cls.detail_by_pk_url_name is not None:
            return cls.detail_by_pk_url_name
        return f"{cls.get_snake_view_name_by_class()}-detail-by-pk"

    @classmethod
    def get_detail_by_pk_request_model(cls):
        """Возвращает модель запроса"""
        return cls.detail_by_pk_request_model

    @classmethod
    def get_detail_by_pk_response_schema(cls):
        """Возвращает модель ответа"""
        return (
            cls.detail_by_pk_response_schema
            or cls.detail_by_pk_return_type
            or cls.return_detail_type
            or cls.return_type
        )

    @classmethod
    def get_detail_by_pk_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.detail_by_pk_responses

    @classmethod
    def get_detail_by_pk_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.detail_by_pk_status_map

    @classmethod
    def get_detail_by_pk_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.detail_by_pk_description

    @classmethod
    def get_detail_by_pk_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.detail_by_pk_summary

    @classmethod
    def get_detail_by_pk_tags(cls):
        """Возвращает список тегов"""
        return cls.detail_by_pk_tags

    @classmethod
    def get_detail_by_pk_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.detail_by_pk_controller_extra_kwargs

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def detail_by_pk_action(self, request: HttpRequest, pk: int, *args, **kwargs):
        """Возвращает DTO записи, по первичному ключу

        Args:
            request: Экземпляр HTTP запроса
            pk: Первичный ключ
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_detail_by_pk_response_schema()
        """
        return self.controller.detail_by_pk(pk, **(self.get_detail_by_pk_controller_extra_kwargs() or {}))


class DetailByExternalCodeCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления получения деталей по внешнему коду"""

    controller: DetailByExternalCodeControllerMixin

    detail_by_external_code_methods = ["get"]
    """Список HTTP методов"""
    detail_by_external_code_permissions = ()
    """Кортеж разрешений"""
    detail_by_external_code_url_path = None
    """Путь URL"""
    detail_by_external_code_url_name = None
    """Имя URL"""
    detail_by_external_code_request_model = None
    """Модель запроса"""
    detail_by_external_code_response_schema = None
    """Модель ответа"""
    detail_by_external_code_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    detail_by_external_code_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    detail_by_external_code_description = _("Получение записи по коду во внешней системе")
    """Описание эндпоинта"""
    detail_by_external_code_summary = None
    """Краткое описание эндпоинта"""
    detail_by_external_code_tags = None
    """Список тегов"""
    detail_by_external_code_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    detail_by_external_code_return_type: type[DTO] = None
    """DTO которое, нужно вернуть для метода"""

    @classmethod
    def get_detail_by_external_code_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.detail_by_external_code_methods

    @classmethod
    def get_detail_by_external_code_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.detail_by_external_code_permissions

    @classmethod
    def get_detail_by_external_code_url_path(cls):
        """Возвращает путь URL"""
        if cls.detail_by_external_code_url_path is not None:
            return cls.detail_by_external_code_url_path
        return rf"{cls.get_path_prefix()}/(?P<code>[\d]+)/(?P<code_type>[\w]+)"

    @classmethod
    def get_detail_by_external_code_url_name(cls):
        """Возвращает имя URL"""
        if cls.detail_by_external_code_url_name is not None:
            return cls.detail_by_external_code_url_name
        return f"{cls.get_snake_view_name_by_class()}-detail-by-external-code"

    @classmethod
    def get_detail_by_external_code_request_model(cls):
        """Возвращает модель запроса"""
        return cls.detail_by_external_code_request_model

    @classmethod
    def get_detail_by_external_code_response_schema(cls):
        """Возвращает модель ответа"""
        return (
            cls.detail_by_external_code_response_schema
            or cls.detail_by_external_code_return_type
            or cls.return_detail_type
            or cls.return_type
        )

    @classmethod
    def get_detail_by_external_code_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.detail_by_external_code_responses

    @classmethod
    def get_detail_by_external_code_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.detail_by_external_code_status_map

    @classmethod
    def get_detail_by_external_code_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.detail_by_external_code_description

    @classmethod
    def get_detail_by_external_code_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.detail_by_external_code_summary

    @classmethod
    def get_detail_by_external_code_tags(cls):
        """Возвращает список тегов"""
        return cls.detail_by_external_code_tags

    @classmethod
    def get_detail_by_external_code_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.detail_by_external_code_controller_extra_kwargs

    @clean_method(name=CleanMethods.DETAIL_BY_EXTERNAL_CODE)
    def detail_by_external_code_action(self, request: HttpRequest, code: str, code_type: str, *args, **kwargs):
        """Возвращает DTO записи, по внешнему коду

        Args:
            request: Экземпляр HTTP запроса
            code: значение кода
            code_type: тип кода
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        Returns:
            self.get_detail_by_pk_response_schema()
        """
        return self.controller.detail_by_external_code(
            code,
            code_type,
            **(self.get_detail_by_external_code_controller_extra_kwargs() or {}),
        )


class RetrieveCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления получения списка объектов"""

    controller: RetrieveControllerMixin

    retrieve_methods = ["get"]
    """Список HTTP методов"""
    retrieve_permissions = ()
    """Кортеж разрешений"""
    retrieve_url_path = None
    """Путь URL"""
    retrieve_url_name = None
    """Имя URL"""
    retrieve_request_model = FilterQueryDTO
    """Модель запроса"""
    retrieve_response_schema = None
    """Модель ответа"""
    retrieve_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    retrieve_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    retrieve_description = _("Получение записей")
    """Описание эндпоинта"""
    retrieve_summary = None
    """Краткое описание эндпоинта"""
    retrieve_tags = None
    """Список тегов"""
    retrieve_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    retrieve_paginated = True
    """Нужна ли пагинация"""
    retrieve_return_type: type[DTO] = None
    """DTO, которое нужно вернуть"""
    retrieve_return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    @classmethod
    def get_retrieve_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.retrieve_methods

    @classmethod
    def get_retrieve_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.retrieve_permissions

    @classmethod
    def get_retrieve_url_path(cls):
        """Возвращает путь URL"""
        if cls.retrieve_url_path is not None:
            return cls.retrieve_url_path
        return f"{cls.get_path_prefix()}/retrieve"

    @classmethod
    def get_retrieve_url_name(cls):
        """Возвращает имя URL"""
        if cls.retrieve_url_name is not None:
            return cls.retrieve_url_name
        return f"{cls.get_snake_view_name_by_class()}-retrieve"

    @classmethod
    def get_retrieve_request_model(cls):
        """Возвращает модель запроса"""
        return cls.retrieve_request_model

    @classmethod
    def get_retrieve_response_schema(cls):
        """Возвращает модель ответа"""
        if cls.retrieve_paginated:
            return (
                cls.retrieve_response_schema
                or cls.retrieve_return_pagination_type
                or cls.return_pagination_type
                or cls.retrieve_return_type
                or cls.return_type
            )
        return cls.retrieve_response_schema or cls.retrieve_return_type or cls.return_type

    @classmethod
    def get_retrieve_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.retrieve_responses

    @classmethod
    def get_retrieve_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.retrieve_status_map

    @classmethod
    def get_retrieve_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.retrieve_description

    @classmethod
    def get_retrieve_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.retrieve_summary

    @classmethod
    def get_retrieve_tags(cls):
        """Возвращает список тегов"""
        return cls.retrieve_tags

    @classmethod
    def get_retrieve_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.retrieve_controller_extra_kwargs

    @clean_method(name=CleanMethods.RETRIEVE)
    def retrieve_action(self, request: HttpRequest, payload: RequestDTO, *args, **kwargs):
        """Возвращает последовательность DTO удовлетворяющих запросу

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        """
        return self.controller.retrieve(
            paginated=self.retrieve_paginated,
            **kwargs,
            **payload.model_dump(exclude_none=True),
            **(self.get_retrieve_controller_extra_kwargs() or {}),
        )


class SearchCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления получения списка объектов по полнотекстовому поиску"""

    controller: SearchControllerMixin

    search_methods = ["get"]
    """Список HTTP методов"""
    search_permissions = ()
    """Кортеж разрешений"""
    search_url_path = None
    """Путь URL"""
    search_url_name = None
    """Имя URL"""
    search_request_model = SearchQueryDTO
    """Модель запроса"""
    search_response_schema = None
    """Модель ответа"""
    search_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    search_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    search_description = _("Поиск записей")
    """Описание эндпоинта"""
    search_summary = None
    """Краткое описание эндпоинта"""
    search_tags = None
    """Список тегов"""
    search_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    search_paginated = True
    """Нужна ли пагинация"""
    search_return_type: type[DTO] = None
    """DTO, которое нужно вернуть"""
    search_return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    @classmethod
    def get_search_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.search_methods

    @classmethod
    def get_search_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.search_permissions

    @classmethod
    def get_search_url_path(cls):
        """Возвращает путь URL"""
        if cls.search_url_path is not None:
            return cls.search_url_path
        return f"{cls.get_path_prefix()}/search"

    @classmethod
    def get_search_url_name(cls):
        """Возвращает имя URL"""
        if cls.search_url_name is not None:
            return cls.search_url_name
        return f"{cls.get_snake_view_name_by_class()}-search"

    @classmethod
    def get_search_request_model(cls):
        """Возвращает модель запроса"""
        return cls.search_request_model

    @classmethod
    def get_search_response_schema(cls):
        """Возвращает модель ответа"""
        if cls.search_paginated:
            return (
                cls.search_response_schema
                or cls.search_return_pagination_type
                or cls.return_pagination_type
                or cls.search_return_type
                or cls.return_type
            )
        return cls.search_response_schema or cls.search_return_type or cls.return_type

    @classmethod
    def get_search_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.search_responses

    @classmethod
    def get_search_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.search_status_map

    @classmethod
    def get_search_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.search_description

    @classmethod
    def get_search_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.search_summary

    @classmethod
    def get_search_tags(cls):
        """Возвращает список тегов"""
        return cls.search_tags

    @classmethod
    def get_search_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.search_controller_extra_kwargs

    @clean_method(name=CleanMethods.SEARCH)
    def search_action(self, request: HttpRequest, payload: RequestDTO, *args, **kwargs):
        """Возвращает последовательность DTO удовлетворяющих запросу

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        """
        return self.controller.search(
            paginated=self.search_paginated,
            **payload.model_dump(exclude_none=True),
            **(self.get_search_controller_extra_kwargs() or {}),
        )


class ExportXLSCleanViewSetMixin(mixin_for(CleanViewSet)):
    """Миксин представления экспорта списка объектов"""

    controller: ExportXLSControllerMixin
    renderer_classes = [JSONRenderer, XLSRenderer]
    """Классы для рендеринга"""

    export_xls_methods = ["get"]
    """Список HTTP методов"""
    export_xls_permissions = ()
    """Кортеж разрешений"""
    export_xls_url_path = None
    """Путь URL"""
    export_xls_url_name = None
    """Имя URL"""
    export_xls_request_model = ExportXLSQueryDTO
    """Модель запроса"""
    export_xls_responses = responses_from_exceptions()
    """Возможные варианты ответа"""
    export_xls_status_map = {"GET": status.HTTP_200_OK}
    """Маппинг HTTP методов и статусов ответа"""
    export_xls_description = _("Экспорт записей в Excel")
    """Описание эндпоинта"""
    export_xls_summary = None
    """Краткое описание эндпоинта"""
    export_xls_tags = None
    """Список тегов"""
    export_xls_controller_extra_kwargs = None
    """Дополнительные параметры, передаваемые в контроллер"""

    @classmethod
    def get_export_xls_methods(cls):
        """Возвращает список HTTP методов"""
        return cls.export_xls_methods

    @classmethod
    def get_export_xls_permissions(cls):
        """Возвращает кортеж разрешений"""
        return cls.export_xls_permissions

    @classmethod
    def get_export_xls_url_path(cls):
        """Возвращает путь URL"""
        if cls.export_xls_url_path is not None:
            return cls.export_xls_url_path
        return f"{cls.get_path_prefix()}/export/xls"

    @classmethod
    def get_export_xls_url_name(cls):
        """Возвращает имя URL"""
        if cls.export_xls_url_name is not None:
            return cls.export_xls_url_name
        return f"{cls.get_snake_view_name_by_class()}-export-xls"

    @classmethod
    def get_export_xls_request_model(cls):
        """Возвращает модель запроса"""
        return cls.export_xls_request_model

    @classmethod
    def get_export_xls_responses(cls):
        """Возвращает возможные варианты ответа"""
        return cls.export_xls_responses

    @classmethod
    def get_export_xls_status_map(cls):
        """Возвращает маппинг HTTP методов и статусов ответа"""
        return cls.export_xls_status_map

    @classmethod
    def get_export_xls_description(cls):
        """Возвращает описание эндпоинта"""
        return cls.export_xls_description

    @classmethod
    def get_export_xls_summary(cls):
        """Возвращает краткое описание эндпоинта"""
        return cls.export_xls_summary

    @classmethod
    def get_export_xls_tags(cls):
        """Возвращает список тегов"""
        return cls.export_xls_tags

    @classmethod
    def get_export_xls_controller_extra_kwargs(cls):
        """Возвращает дополнительные параметры, передаваемые в контроллер"""
        return cls.export_xls_controller_extra_kwargs

    @clean_method(name=CleanMethods.EXPORT_XLS)
    def export_xls_action(self, request: HttpRequest, payload: RequestDTO, *args, **kwargs):
        """Возвращает ExportXLSResponseDTO

        Args:
            request: Экземпляр HTTP запроса
            payload: Данные запроса
            *args: позиционные аргументы
            **kwargs: именованные аргументы

        """
        result = self.controller.export_xls(
            **payload.model_dump(exclude_none=True),
            **(self.get_export_xls_controller_extra_kwargs() or {}),
        )

        response = HttpResponse(result.file_content)
        response["Content-Type"] = "application/xls"
        response["Content-Disposition"] = f"attachment; filename={escape_uri_path(result.file_name)}.xls"
        response["Content-Transfer-Encoding"] = "binary"

        return response


class CreateUpdateCleanViewSetMixin(CreateCleanViewSetMixin, UpdateCleanViewSetMixin):
    """Миксин представления создания / обновления"""

    controller: CreateUpdateControllerMixin


class UpdateDeleteCleanViewSetMixin(UpdateCleanViewSetMixin, DeleteCleanViewSetMixin):
    """Миксин представления обновления / удаления"""

    controller: UpdateDeleteControllerMixin


class CreateDeleteCleanViewSetMixin(CreateCleanViewSetMixin, DeleteCleanViewSetMixin):
    """Миксин представления создания / удаления"""

    controller: CreateDeleteControllerMixin


class CreateUpdateDeleteCleanViewSetMixin(CreateCleanViewSetMixin, UpdateCleanViewSetMixin, DeleteCleanViewSetMixin):
    """Миксин представления создания / обновления / удаления"""

    controller: CreateUpdateDeleteControllerMixin


class DetailsCleanViewSetMixin(DetailCleanViewSetMixin, DetailByPKCleanViewSetMixin):
    """Миксин представления получения деталей"""

    controller: DetailsControllerMixin


class ListCleanViewSetMixin(RetrieveCleanViewSetMixin, SearchCleanViewSetMixin):
    """Миксин представления получения списка объектов"""

    controller: ListControllerMixin


class ReadCleanViewSetMixin(ListCleanViewSetMixin, DetailsCleanViewSetMixin):
    """Миксин представления получения деталей / списка объектов"""

    controller: ReadControllerMixin


class CRUDCleanViewSetMixin(CreateUpdateDeleteCleanViewSetMixin, ReadCleanViewSetMixin):
    """Миксин представления создание / чтение /обновление / удаление"""

    controller: CRUDControllerMixin
