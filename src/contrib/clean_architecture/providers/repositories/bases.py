"""Модуль с базовым репозиторием и миксинами

## Базовый репозиторий

Classes:
    BaseRepository: Базовый репозитория

## Создание

Classes:
    CreateRepositoryMixin: Миксин репозитория создания
    BulkCreateRepositoryMixin: Миксин репозитория массового создания
    UpdateOrCreateRepositoryMixin: Миксин репозитория обновления или создания
    DetailOrCreateRepositoryMixin: Миксин репозитория получения деталей или создания

## Обновление

Classes:
    UpdateOrCreateRepositoryMixin: Миксин репозитория обновления или создания
    UpdateRepositoryMixin: Миксин репозитория обновления
    MultiUpdateRepositoryMixin: Миксин репозитория множественного обновления

## Удаление

Classes:
    DeleteRepositoryMixin: Миксин репозитория удаления
    BulkDeleteRepositoryMixin: Миксин репозитория множественного удаления

## Получение записи

Classes:
    DetailOrCreateRepositoryMixin: Миксин репозитория получения деталей или создания
    DetailRepositoryMixin: Миксин репозитория получения деталей
    DetailByPKRepositoryMixin: Миксин репозитория получения деталей по первичному ключу
    DetailByExternalCodeRepositoryMixin: Миксин репозитория получения деталей по внешнему коду

## Получение списка записей

Classes:
    GetByIdsRepositoryMixin: Миксин репозитория получения списка объектов по id
    RetrieveRepositoryMixin: Миксин репозитория получения списка объектов
    SearchRepositoryMixin: Миксин репозитория получения списка объектов по полнотекстовому поиску
    ExistsRepositoryMixin: Миксин репозитория проверки существования записи

## Прочее

Classes:
    ExistsRepositoryMixin: Миксин репозитория проверки существования записи

## Комбинации интерфейсов миксинов репозиториев

Classes:
    CreateUpdateRepositoryMixin: Миксин репозитория создания / обновления
    UpdateDeleteRepositoryMixin: Миксин репозитория обновления / удаления
    CreateDeleteRepositoryMixin: Миксин репозитория создания / удаления
    CreateUpdateDeleteRepositoryMixin: Миксин репозитория создания / обновления / удаления
    DetailsRepositoryMixin: Миксин репозитория получения деталей
    ListRepositoryMixin: Миксин репозитория получения списка объектов
    ReadRepositoryMixin: Миксин репозитория получения деталей / списка объектов
    CRUDRepositoryMixin: Миксин репозитория создание / чтение /обновление / удаление
    PatchListRepositoryMixin: Миксин репозитория модификации списка объектов

"""
from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from contextlib import suppress
from enum import Enum
from typing import Any

from contrib.clean_architecture.consts import CleanMethods
from contrib.clean_architecture.consts import RepositoryMethodAttrs
from contrib.clean_architecture.dto_based_objects.bases import BaseDTOBasedObjectsMixin
from contrib.clean_architecture.dto_based_objects.dtos import M2MUpdateAction
from contrib.clean_architecture.dto_based_objects.utils import convert_return
from contrib.clean_architecture.dto_based_objects.utils import ConvertPath
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import Entity
from contrib.clean_architecture.interfaces import Model
from contrib.clean_architecture.interfaces import ObjectId
from contrib.clean_architecture.providers.repositories.interfaces import IBulkCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IBulkDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IBulkUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICreateUpdateBaseRepository
from contrib.clean_architecture.providers.repositories.interfaces import IDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailByExternalCodeRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailByPKRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailOrCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IExistsRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IGetByIdsRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IGetSoloRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IMultiUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IRepository
from contrib.clean_architecture.providers.repositories.interfaces import IRetrieveRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ISearchRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IUpdateOrCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.utils import get_distinct_query
from contrib.clean_architecture.providers.repositories.utils import get_query_page
from contrib.clean_architecture.providers.repositories.utils import has_field
from contrib.clean_architecture.types import mixin_for
from contrib.clean_architecture.utils.exceptions import BaseExceptionRedirect
from contrib.clean_architecture.utils.exceptions import ExceptionRedirect
from contrib.clean_architecture.utils.method import clean_method
from contrib.clean_architecture.utils.method import CleanMethodMixin
from contrib.clean_architecture.utils.query_dict import parse_query_dict
from contrib.clean_architecture.utils.query_dict import Wrappers
from contrib.context import get_root_context
from contrib.exceptions.exceptions import DoesNotExist
from contrib.exceptions.exceptions import MultipleObjectsReturnedExist
from contrib.subclass_control.mixins import ImportedStringAttrsMixin


class BaseRepository(
    BaseDTOBasedObjectsMixin,
    ImportedStringAttrsMixin,
    CleanMethodMixin,
    IRepository,
    ABC,
    required_attrs_base=True,
):
    """Базовый репозиторий"""

    imported_string_attrs = ("external_code_model",)
    required_attrs = (
        "entity",
        "atomic_decorator",
        "external_code_model",
        "object_does_not_exist_exception",
        "multiple_objects_returned_exception",
    )

    methods = set()
    primary_key_attr = "id"
    convert_return_decorator = convert_return
    exceptions_redirects: tuple[BaseExceptionRedirect] = ()
    order_by_mapping: dict[str, str] = {}

    def __init_subclass__(cls, repository_base: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)
        if not repository_base:
            cls._wrap_methods()

    def _prepare_filters(
        self, *conditions: Any, filter_dto: DTO = None, **filters
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """Подготавливает позиционные и именованные аргументы фильтрации

        Args:
            **conditions: Условия фильтрации
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Кортеж из (conditions), filters
        """
        wrappers = Wrappers(condition=self.condition_wrapper, find=self.find_wrapper)
        results = parse_query_dict("", filters, wrappers=wrappers)
        return (results, *conditions), {**(filter_dto.model_dump() if filter_dto else {})}

    @classmethod
    def _wrap_methods(cls):
        """Оборачивает все clean_methods требуемыми декораторами"""
        for method_attr_name, method in cls.clean_methods.items():
            method_name = method.__method_name__

            # Вешаем декоратор атомарности транзакции
            if getattr(cls, f"{method_name}_{RepositoryMethodAttrs.ATOMIC}", False):
                method = cls.atomic_decorator(method)

            # Вешаем декоратор конвертации результата метода
            if getattr(cls, f"{method_name}_{RepositoryMethodAttrs.CONVERT_RETURN}", False):
                convert_path = getattr(cls, f"{method_name}_{RepositoryMethodAttrs.CONVERT_PATH}", None)
                method = cls.convert_return_decorator(cls.model, cls.entity, convert_path=convert_path)(method)

            # Вешаем декораторы перенаправления исключений
            exceptions_redirects = getattr(cls, f"{method_name}_{RepositoryMethodAttrs.EXCEPTIONS_REDIRECTS}", ())
            for exception_redirect in (
                *exceptions_redirects,
                *cls._get_exceptions_redirects(),
            ):
                method = exception_redirect.decorate(method)

            # Переопределяем метод
            setattr(cls, method_attr_name, method)

    @classmethod
    def _get_exceptions_redirects(cls):
        """Возвращает кортеж перенаправлений исключений"""
        return (
            *cls.exceptions_redirects,
            ExceptionRedirect(
                from_exception=cls.object_does_not_exist_exception,
                to_exception=DoesNotExist,
            ),
            ExceptionRedirect(
                from_exception=cls.multiple_objects_returned_exception,
                to_exception=MultipleObjectsReturnedExist,
            ),
        )

    def _filter(self, *conditions: Any, filter_dto: DTO = None, **filters):
        """Формирует неоцененный QuerySet

        Args:
            **conditions: Условия фильтрации
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Неоцененный QuerySet

        """
        objects = self.objects
        filter_args, filter_kwargs = self._prepare_filters(*conditions, filter_dto=filter_dto, **filters)
        return objects.filter(*filter_args, **filter_kwargs)

    def _get(self, *conditions: Any, filter_dto: DTO = None, **filters):
        """Возвращает экземпляр модели ORM

        Args:
            **conditions: Условия фильтрации
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            экземпляр модели ORM
        """
        objects = self.objects
        filter_args, filter_kwargs = self._prepare_filters(*conditions, filter_dto=filter_dto, **filters)
        return objects.get(*filter_args, **filter_kwargs)

    def _match_order_by_fields(self, fields: Sequence[str]) -> tuple[str, ...]:
        """Матчит сортировки с полями

        Args:
            fields: последовательность имен полей

        Returns:
            кортеж сматченных значений
        """
        return tuple(self.order_by_mapping[field] if field in self.order_by_mapping else field for field in fields)

    def _get_object_id_from_external_code(self, code: str, code_type: Enum) -> ObjectId:
        """Возвращает id объекта по его внешнему коду

        Args:
            code: Внешний код
            code_type: Тип внешнего кода

        Returns:

        """
        with suppress(self.object_does_not_exist_exception):
            return self.external_code_model.objects.get_object_id(code=code, code_type=code_type, model_type=self.model)

    def _get_m2m_fields(self) -> list[str]:
        """Возвращает список полей m2m"""
        return []

    def get_ids(
        self,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> Sequence[int | str]:
        filter_args, filter_kwargs = self._prepare_filters(*conditions, filter_dto=filter_dto, **filters)
        objects = self.model.objects.filter(*filter_args, **filter_kwargs)
        return get_distinct_query(objects, distinct).values_list(self.primary_key_attr, flat=True)


class CreateUpdateBaseRepository(ICreateUpdateBaseRepository, ABC, mixin_for(BaseRepository)):
    """Базовый репозиторий создания и изменения"""

    def _update_m2m_relations(self, instance: Model, data: dict[str, Any]) -> set[str]:
        """Обновляет значения связей m2m

        Args:
            instance: экземпляр модели ORM
            data: Словарь m2m полей с последовательностью M2MUpdateAction

        Returns:
            Множество названий полей для обновления
        """
        m2m_fields = self._get_m2m_fields()

        # Ищем совпадения по переданным полям и обновляем m2m связи
        fields_to_process = set(m2m_fields) & set(data.keys())
        for field in fields_to_process:
            m2m_actions: list[dict[str, Any]] | None = data.get(field)
            if m2m_actions is None:
                continue

            actions = [M2MUpdateAction.model_validate(action) for action in m2m_actions]
            self.m2m_manager.execute(instance, field, actions)

        return fields_to_process


class CreateRepositoryMixin(ICreateRepositoryMixin, CreateUpdateBaseRepository, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория создания"""

    create_atomic: bool = True
    create_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.CREATE)
    def create(
        self,
        entity: Entity = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        external_code: str = None,
        external_code_type: Enum = None,
        **kwargs,
    ) -> ObjectId:
        # Агрегируем данные для создания
        extra_dump_kwargs = extra_dump_kwargs if extra_dump_kwargs else {}
        dump_kwargs = dict(
            exclude_unset=exclude_unset,
            exclude=exclude,
            include=include,
            **extra_dump_kwargs,
        )
        create_data = dict(**(entity.model_dump(**dump_kwargs) if entity else {}), **kwargs)

        # Записываем текущего пользователя и время
        context = get_root_context()
        if has_field(self.model, "created_by") and context.initialized and context.current_user.pk:
            create_data["created_by"] = context.current_user
        if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
            create_data["updated_by"] = context.current_user

        # Создаем необходимые модели
        instance = self.objects.create(**{k: v for k, v in create_data.items() if k not in self._get_m2m_fields()})
        self._update_m2m_relations(
            instance,
            {k: v for k, v in create_data.items() if k in self._get_m2m_fields()},
        )

        if external_code and external_code_type:
            external_code_data = {
                "code": external_code,
                "code_type": external_code_type,
                "content_object": instance,
            }
            self.external_code_model.objects.create(**external_code_data)
        return instance.pk


class BulkCreateRepositoryMixin(IBulkCreateRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория массового создания"""

    bulk_create_atomic: bool = True
    bulk_create_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.BULK_CREATE)
    def bulk_create(
        self,
        entities: list[Entity] = None,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **kwargs,
    ) -> None:
        # Агрегируем данные для создания
        extra_dump_kwargs = extra_dump_kwargs if extra_dump_kwargs else {}
        dump_kwargs = dict(
            exclude_unset=exclude_unset,
            exclude=exclude,
            include=include,
            **extra_dump_kwargs,
        )
        context = get_root_context()

        bulk_create_content: list[Model] = []
        for entity in entities:
            # Записываем текущего пользователя и время
            create_data = dict(**(entity.model_dump(**dump_kwargs) if entity else {}), **kwargs)
            if has_field(self.model, "created_by") and context.initialized and context.current_user.pk:
                create_data["created_by"] = context.current_user
            if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
                create_data["updated_by"] = context.current_user
            bulk_create_content.append(self.model(**create_data))

        # Создаем необходимые модели
        self.objects.bulk_create(bulk_create_content)


class UpdateRepositoryMixin(IUpdateRepositoryMixin, CreateUpdateBaseRepository, mixin_for(BaseRepository)):
    """Миксин репозитория обновления"""

    update_atomic: bool = True
    update_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.UPDATE)
    def update(
        self,
        entity: Entity = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        primary_key_attr: str = None,
        **kwargs,
    ) -> ObjectId:
        # Агрегируем данные для обновления
        extra_dump_kwargs = extra_dump_kwargs if extra_dump_kwargs else {}
        dump_kwargs = dict(
            exclude_unset=exclude_unset,
            exclude=exclude,
            include=include,
            **extra_dump_kwargs,
        )
        updated_data = dict(**(entity.model_dump(**dump_kwargs) if entity else {}), **kwargs)

        primary_key_attr = primary_key_attr or self.primary_key_attr
        # Получаем экземпляр целевой модели
        primary_key = updated_data.pop(primary_key_attr)
        instance = self._get(**{primary_key_attr: primary_key})

        # Записываем текущего пользователя и время
        context = get_root_context()
        if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
            updated_data["updated_by"] = context.current_user

        # Обновляем переданные значения
        processed_fields = self._update_m2m_relations(instance, updated_data)
        for field in processed_fields:
            updated_data.pop(field, None)

        for k, v in updated_data.items():
            setattr(instance, k, v)

        # Сохраняем модель
        if updated_data:
            instance.save(update_fields=updated_data.keys())

        return instance.pk


class BulkUpdateRepositoryMixin(IBulkUpdateRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория массового обновления"""

    bulk_update_atomic: bool = True
    bulk_update_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.BULK_UPDATE)
    def bulk_update(
        self,
        entities: list[Entity] = None,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **kwargs,
    ) -> None:
        # Агрегируем данные для обновления
        exclude = exclude or set()
        exclude.add("id")

        extra_dump_kwargs = extra_dump_kwargs if extra_dump_kwargs else {}
        dump_kwargs = dict(
            exclude_unset=exclude_unset,
            exclude=exclude,
            include=include,
            **extra_dump_kwargs,
        )
        context = get_root_context()

        entities_with_ids = {item.id: item for item in entities}
        bulk_update_content: list[Model] = []
        objects = self.model.objects.filter(pk__in=entities_with_ids.keys())

        fields = set()
        extra_updated_fileds = {}
        if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
            extra_updated_fileds["updated_by"] = context.current_user
        for item in objects:
            # Записываем текущего пользователя и время
            entity = entities_with_ids[item.pk]
            update_data = dict(**(entity.model_dump(**dump_kwargs) if entity else {}), **kwargs)
            update_data.update(extra_updated_fileds)
            for key, value in update_data.items():
                setattr(item, key, value)
            bulk_update_content.append(item)
            fields.update(update_data.keys())

        # Обновляем модели
        self.objects.bulk_update(bulk_update_content, list(fields))


class MultiUpdateRepositoryMixin(IMultiUpdateRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория множественного обновления"""

    update_atomic: bool = True
    update_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.MULTI_UPDATE)
    def multi_update(
        self,
        entity: Entity = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **conditions,
    ) -> None:
        """Множественное обновление."""
        # Агрегируем данные для обновления
        extra_dump_kwargs = extra_dump_kwargs if extra_dump_kwargs else {}
        dump_kwargs = dict(
            exclude_unset=exclude_unset,
            exclude=exclude,
            include=include,
            **extra_dump_kwargs,
        )
        updated_data = dict(**(entity.model_dump(**dump_kwargs) if entity else {}))

        # Записываем текущего пользователя и время
        context = get_root_context()
        if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
            updated_data["updated_by"] = context.current_user

        # Обновляем значения
        if updated_data:
            self._filter(**conditions).update(**updated_data)


class _BaseOrCreate:
    """Базовый класс для миксинов репозитория, использующие *_or_create методы"""

    def _base_or_create(
        self: BaseRepository,
        method_name: str,
        defaults: dict[str, Any] = None,
        external_code: str = None,
        external_code_type: Enum = None,
        from_external_code: bool = False,
        return_instance: bool = False,
        **kwargs,
    ):
        """Вызывает метод объектного менеджера вида *_or_create

        Args:
            method_name: Имя вызываемого метода
            defaults: Данные для создания / обновления
            external_code: Значение внешнего кода
            external_code_type: Тип внешнего кода
            from_external_code: Искать по внешнему коду
            return_instance: Возвращать ли экземпляр модели ORM
            **kwargs: Условия поиска / данные для создания

        Returns:
            Кортеж из DTO или Entity и признака создания объекта или самого объекта

        """
        defaults = defaults if defaults else {}

        # Записываем текущего пользователя и время
        context = get_root_context()
        if has_field(self.model, "updated_by") and context.initialized and context.current_user.pk:
            defaults["updated_by"] = context.current_user

        # Ищем по внешнему ключу и обновляем данные
        if from_external_code:
            object_id = self._get_object_id_from_external_code(external_code, external_code_type)
            if object_id:
                kwargs[self.primary_key_attr] = object_id
            else:
                kwargs.update(defaults)

        # Вызываем оригинальный метод
        instance, created = getattr(self.objects, method_name)(**kwargs, defaults=defaults)

        # Создаем необходимые модели
        if created:
            if external_code and external_code_type:
                external_code_data = {
                    "code": external_code,
                    "code_type": external_code_type,
                    "content_object": instance,
                }
                self.external_code_model.objects.create(**external_code_data)
            # Записываем текущего пользователя и время
            if has_field(self.model, "created_by") and context.initialized and context.current_user.pk:
                instance.created_by = context.current_user
                instance.save()

        if return_instance:
            return instance, created
        return instance.pk, created


class UpdateOrCreateRepositoryMixin(IUpdateOrCreateRepositoryMixin, _BaseOrCreate, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория обновления или создания"""

    update_or_create_atomic: bool = True
    update_or_create_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.UPDATE_OR_CREATE)
    def update_or_create(
        self,
        *args,
        defaults: dict[str, Any] = None,
        external_code: str = None,
        external_code_type: Enum = None,
        from_external_code: bool = False,
        **kwargs,
    ) -> tuple[ObjectId, bool]:
        return self._base_or_create(
            "update_or_create",
            defaults=defaults,
            external_code=external_code,
            external_code_type=external_code_type,
            from_external_code=from_external_code,
            **kwargs,
        )


class DetailOrCreateRepositoryMixin(IDetailOrCreateRepositoryMixin, _BaseOrCreate, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения деталей или создания"""

    detail_or_create_convert_return: bool = True
    detail_or_create_convert_path: ConvertPath = ConvertPath(0)
    detail_or_create_atomic: bool = True
    detail_or_create_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.DETAIL_OR_CREATE)
    def detail_or_create(
        self,
        *args,
        defaults: dict[str, Any] = None,
        external_code: str = None,
        external_code_type: Enum = None,
        from_external_code: bool = False,
        **kwargs,
    ) -> tuple[Entity | DTO, bool]:
        return self._base_or_create(
            "get_or_create",
            defaults=defaults,
            external_code=external_code,
            external_code_type=external_code_type,
            from_external_code=from_external_code,
            return_instance=True,
            **kwargs,
        )


class DeleteRepositoryMixin(IDeleteRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория удаления"""

    delete_atomic: bool = True
    delete_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.DELETE)
    def delete(self, pk: ObjectId, raise_exception=True) -> ObjectId:
        try:
            return self._get(**{self.primary_key_attr: pk}).delete()[0]
        except (
            self.object_does_not_exist_exception,
            self.multiple_objects_returned_exception,
        ) as error:
            if raise_exception:
                raise error


class BulkDeleteRepositoryMixin(IBulkDeleteRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория множественного удаления"""

    delete_atomic: bool = True
    delete_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.BULK_DELETE)
    def bulk_delete(self, ids: list[ObjectId]) -> None:
        self.model.objects.filter(pk__in=ids).delete()


class DetailRepositoryMixin(IDetailRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения деталей"""

    detail_convert_return: bool = True
    detail_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.DETAIL)
    def detail(self, *conditions: Any, filter_dto: DTO = None, raise_exception=True, **filters) -> Entity | DTO:
        try:
            return self._get(*conditions, filter_dto=filter_dto, **filters)
        except (
            self.object_does_not_exist_exception,
            self.multiple_objects_returned_exception,
        ) as error:
            if raise_exception:
                raise error


class DetailByPKRepositoryMixin(IDetailByPKRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения деталей по первичному ключу"""

    detail_by_pk_convert_return: bool = True
    detail_by_pk_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def detail_by_pk(self, pk: ObjectId, raise_exception=True, **filters) -> Entity | DTO:
        try:
            return self._get(**{self.primary_key_attr: pk}, **filters)
        except (
            self.object_does_not_exist_exception,
            self.multiple_objects_returned_exception,
        ) as error:
            if raise_exception:
                raise error


class DetailByExternalCodeRepositoryMixin(IDetailByExternalCodeRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения деталей по внешнему коду"""

    external_code_model: BaseRepository.external_code_model
    detail_by_external_code_convert_return: bool = True
    detail_by_external_code_exceptions_redirects: tuple[BaseExceptionRedirect] = ()

    @clean_method(name=CleanMethods.DETAIL_BY_EXTERNAL_CODE)
    def detail_by_external_code(self, code: str, code_type: str | Enum, raise_exception=True) -> Entity | DTO:
        try:
            return self.external_code_model.objects.get_object(code=code, code_type=code_type, model_type=self.model)
        except (
            self.object_does_not_exist_exception,
            self.multiple_objects_returned_exception,
        ) as error:
            if raise_exception:
                raise error


class GetByIdsRepositoryMixin(IGetByIdsRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения списка объектов по id"""

    def get_by_ids(self, ids: list[ObjectId]) -> list[Entity | DTO]:
        """Получить позиции по id."""
        return self._filter(pk__in=ids)


class RetrieveRepositoryMixin(IRetrieveRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения списка объектов"""

    retrieve_convert_return: bool = True

    @clean_method(name=CleanMethods.RETRIEVE)
    def retrieve(
        self,
        *conditions: Any,
        limit: int = None,
        offset: int = None,
        order_by: tuple[str] = (),
        distinct: bool | tuple[str] = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[Entity | DTO]:
        objects = self._filter(*conditions, filter_dto=filter_dto, **filters)
        order_by = self._match_order_by_fields(order_by)
        objects = get_distinct_query(objects, distinct)
        return get_query_page(objects, limit, offset, order_by)

    @clean_method(name=CleanMethods.COUNT)
    def count(
        self,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> int:
        objects = self._filter(*conditions, filter_dto=filter_dto, **filters)
        return get_distinct_query(objects, distinct).count()


class SearchRepositoryMixin(ISearchRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения списка объектов по полнотекстовому поиску"""

    required_attrs = ("search_expressions", "search_filter_function")

    search_expressions: Sequence[str]
    search_extra_replaces: Mapping[str, str] = {}
    search_convert_return: bool = True
    search_filter_function: Callable

    @clean_method(name=CleanMethods.SEARCH)
    def search(
        self,
        search: str,
        *conditions: Any,
        limit: int = None,
        offset: int = None,
        order_by: tuple[str] = (),
        distinct: bool | tuple[str] = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[Entity | DTO]:
        objects = self._filter(*conditions, filter_dto=filter_dto, **filters)
        objects = self.__class__.search_filter_function(
            objects, search, *self.search_expressions, **self.search_extra_replaces
        )
        objects = get_distinct_query(objects, distinct)
        order_by = self._match_order_by_fields(order_by)
        return get_query_page(objects, limit, offset, order_by)

    @clean_method(name=CleanMethods.SEARCH_COUNT)
    def search_count(
        self,
        search: str,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> int:
        objects = self._filter(*conditions, filter_dto=filter_dto, **filters)
        objects = self.__class__.search_filter_function(
            objects, search, *self.search_expressions, **self.search_extra_replaces
        )
        return get_distinct_query(objects, distinct).count()


class ExistsRepositoryMixin(IExistsRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория проверки существования записи"""

    @clean_method(name=CleanMethods.EXISTS)
    def exists(self, *conditions: Any, filter_dto: DTO = None, **filters) -> bool:
        return self._filter(*conditions, filter_dto=filter_dto, **filters).exists()


class GetSoloRepositoryMixin(IGetSoloRepositoryMixin, ABC, mixin_for(BaseRepository)):
    """Миксин репозитория получения объекта модели Singleton"""

    @clean_method(name=CleanMethods.GET_SOLO)
    def get_solo(self, raise_exception=True) -> PydanticEntity | PydanticDTO:
        try:
            return self.model()
        except (
            self.object_does_not_exist_exception,
            self.multiple_objects_returned_exception,
        ) as error:
            if raise_exception:
                raise error


class CreateUpdateRepositoryMixin(CreateRepositoryMixin, UpdateRepositoryMixin, ABC):
    """Миксин репозитория создания / обновления"""


class UpdateDeleteRepositoryMixin(UpdateRepositoryMixin, DeleteRepositoryMixin, ABC):
    """Миксин репозитория обновления / удаления"""


class CreateDeleteRepositoryMixin(CreateRepositoryMixin, DeleteRepositoryMixin, ABC):
    """Миксин репозитория создания / удаления"""


class CreateUpdateDeleteRepositoryMixin(CreateRepositoryMixin, UpdateRepositoryMixin, DeleteRepositoryMixin, ABC):
    """Миксин репозитория создания / обновления / удаления"""


class DetailsRepositoryMixin(DetailRepositoryMixin, DetailByPKRepositoryMixin, ABC):
    """Миксин репозитория получения деталей"""


class ListRepositoryMixin(RetrieveRepositoryMixin, SearchRepositoryMixin, ABC):
    """Миксин репозитория получения списка объектов"""


class ReadRepositoryMixin(ListRepositoryMixin, DetailsRepositoryMixin, ABC):
    """Миксин репозитория получения деталей / списка объектов"""


class CRUDRepositoryMixin(CreateUpdateDeleteRepositoryMixin, ReadRepositoryMixin, ABC):
    """Миксин репозитория создание / чтение /обновление / удаление"""


class PatchListRepositoryMixin(UpdateRepositoryMixin, BulkCreateRepositoryMixin, BulkDeleteRepositoryMixin, ABC):
    """Миксин репозитория модификации списка объектов"""
