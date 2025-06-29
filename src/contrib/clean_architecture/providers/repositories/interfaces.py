"""Модуль с интерфейсами репозиториев

## Базовый интерфейс

Classes:
    IRepository: Абстрактный интерфейс для репозитория

## Создание

Classes:
    ICreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория создания
    IBulkCreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория массового создания
    IUpdateOrCreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория обновления или создания
    IDetailOrCreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей или создания

## Обновление

Classes:
    IUpdateOrCreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория обновления или создания
    IUpdateRepositoryMixin: Абстрактный интерфейс для миксина репозитория обновления
    IMultiUpdateRepositoryMixin: Абстрактный интерфейс для миксина репозитория множественного обновления

## Удаление

Classes:
    IDeleteRepositoryMixin: Абстрактный интерфейс для миксина репозитория удаления
    IBulkDeleteRepositoryMixin: Абстрактный интерфейс для миксина репозитория множественного удаления

## Получение записи

Classes:
    IDetailOrCreateRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей или создания
    IDetailRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей
    IDetailByPKRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей по первичному ключу
    IDetailByExternalCodeRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей по внешнему коду

## Получение списка записей

Classes:
    IGetByIdsRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения списка объектов по id
    IRetrieveRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения списка объектов
    ISearchRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения списка объектов по полнотекстовому поиску
    IExistsRepositoryMixin: Абстрактный интерфейс для миксина репозитория проверки существования записи

## Прочее

Classes:
    IExistsRepositoryMixin: Абстрактный интерфейс для миксина репозитория проверки существования записи

## Комбинации интерфейсов миксинов репозиториев

Classes:
    ICreateUpdateRepositoryMixin: Абстрактный интерфейс для миксина репозитория создания / обновления
    IUpdateDeleteRepositoryMixin: Абстрактный интерфейс для миксина репозитория обновления / удаления
    ICreateDeleteRepositoryMixin: Абстрактный интерфейс для миксина репозитория создания / удаления
    ICreateUpdateDeleteRepositoryMixin: Абстрактный интерфейс для миксина репозитория создания / обновления / удаления
    IDetailsRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей
    IListRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения списка объектов
    IReadRepositoryMixin: Абстрактный интерфейс для миксина репозитория получения деталей / списка объектов
    ICRUDRepositoryMixin: Абстрактный интерфейс для миксина репозитория создание / чтение /обновление / удаление
    IPatchListRepositoryMixin: Абстрактный интерфейс для миксина репозитория модификации списка объектов

"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from enum import Enum
from typing import Any

from contrib.clean_architecture.dto_based_objects.interfaces import (
    IDTOBasedObjectsMixin,
)
from contrib.clean_architecture.dto_based_objects.utils import ConvertPath
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import Entity
from contrib.clean_architecture.interfaces import ObjectId
from contrib.clean_architecture.interfaces import QuerySet
from contrib.clean_architecture.types import mixin_for
from contrib.clean_architecture.utils.exceptions import BaseExceptionRedirect


class IRepository(IDTOBasedObjectsMixin, ABC):
    """Абстрактный интерфейс для репозитория"""

    methods: set
    """Множество атрибутов, являющихся методами репозитория"""
    primary_key_attr: str | tuple[str]
    """Атрибут первичного ключа модели"""
    entity: type[Entity]
    """Класс Entity для конвертации в него моделей ORM"""
    atomic_decorator: Callable
    """Функция реализующая атомарность транзакции"""
    convert_return_decorator: Callable
    """Функция для конвертирования результата выполнения методов репозитория"""
    object_does_not_exist_exception: type[Exception]
    """Класс исключения, вызываемый при отсутствии записи в БД"""
    multiple_objects_returned_exception: type[Exception]
    """Класс исключения, вызываемый при наличии нескольких записи в БД"""
    exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж перенаправления ошибок"""
    external_code_model: Any
    """Кортеж перенаправления ошибок"""
    order_by_mapping: dict[str, str]
    """Маппинг сортировки"""
    condition_wrapper: Callable
    """Класс реализующий интерфейс вида django.db.models.Q"""
    find_wrapper: Callable
    """Класс реализующий интерфейс вида django.db.models.F"""

    @abstractmethod
    def get_ids(
        self,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> Sequence[int | str]:
        """Возвращает последовательность ids удовлетворяющих запросу

        Args:
            *conditions: Кортеж условий вида django.db.models.Q
            filter_dto: Pydantic модель с полями фильтрации запроса
            distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей
            **filters: Словарь фильтров запроса

        Returns:
            ids: Последовательность id удовлетворяющих параметрам запроса
        """


class ICreateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория создания"""

    create_atomic: bool
    """Выполнить в одной транзакции"""
    create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
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
        """Создает запись в БД

        Args:
            entity: экземпляр Entity
            *args: Позиционные аргументы
            exclude_unset: Исключить все не переданные поля
            exclude: Множество полей, которые необходимо исключить
            include: Множество полей, которые необходимо включить
            extra_dump_kwargs: Словарь параметров для передачи в PydanticModel.model_dump
            external_code: Значение кода во внешней системе
            external_code_type: Тип кода во внешней системе
            **kwargs: Дополнительные данные для создания записи

        Returns:
            Id созданного объекта
        """


class IBulkCreateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория массового создания"""

    bulk_create_atomic: bool
    """Выполнить в одной транзакции"""
    bulk_create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def bulk_create(
        self,
        entities: list[Entity] = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **kwargs,
    ) -> None:
        """Создает записи в БД

        Args:
            entities: Список экземпляров Entity
            *args: Позиционные аргументы
            exclude_unset: Исключить все не переданные поля
            exclude: Множество полей, которые необходимо исключить
            include: Множество полей, которые необходимо включить
            extra_dump_kwargs: Словарь параметров для передачи в PydanticModel.model_dump
            **kwargs: Дополнительные данные для обновления записи

        """


class IBulkUpdateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория массового обновления"""

    bulk_create_atomic: bool
    """Выполнить в одной транзакции"""
    bulk_create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def bulk_update(
        self,
        entities: list[Entity] = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **kwargs,
    ) -> None:
        """Обновляет записи в БД

        Args:
            entities: Список экземпляров Entity
            *args: Позиционные аргументы
            exclude_unset: Исключить все не переданные поля
            exclude: Множество полей, которые необходимо исключить
            include: Множество полей, которые необходимо включить
            extra_dump_kwargs: Словарь параметров для передачи в PydanticModel.model_dump
            **kwargs: Дополнительные данные для создания записи

        """


class IUpdateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория обновления"""

    update_atomic: bool
    """Выполнить в одной транзакции"""
    update_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def update(
        self,
        entity: Entity = None,
        *args,
        exclude_unset: bool = True,
        exclude: set = None,
        include: set = None,
        extra_dump_kwargs: dict = None,
        **kwargs,
    ) -> ObjectId:
        """Обновляет запись в БД

        Args:
            entity: Экземпляр Entity
            *args: Позиционные аргументы
            exclude_unset: Исключить все не переданные поля
            exclude: Множество полей, которые необходимо исключить
            include: Множество полей, которые необходимо включить
            extra_dump_kwargs: Словарь параметров для передачи в PydanticModel.model_dump
            **kwargs: Дополнительные данные для обновления записи

        Returns:
            Id обновленного объекта
        """


class IMultiUpdateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория множественного обновления"""

    multi_update_or_create_atomic: bool
    """Выполнить в одной транзакции"""
    multi_update_or_create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
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
        """Обновляет записи в БД, удовлетворяющие запросу

        Args:
            entity: Экземпляр Entity
            *args: Позиционные аргументы
            exclude_unset: Исключить все не переданные поля
            exclude: Множество полей, которые необходимо исключить
            include: Множество полей, которые необходимо включить
            extra_dump_kwargs: Словарь параметров для передачи в PydanticModel.model_dump
            **conditions: Условия фильтрации

        """


class IUpdateOrCreateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория обновления или создания"""

    update_or_create_atomic: bool
    """Выполнить в одной транзакции"""
    update_or_create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def update_or_create(
        self,
        *args,
        defaults: dict[str, Any] = None,
        external_code: str = None,
        external_code_type: Enum = None,
        from_external_code: bool = False,
        **kwargs,
    ) -> tuple[ObjectId, bool]:
        """Обновляет / создает запись в БД

        Args:
            *args: Позиционные аргументы
            defaults: Данные для создания / обновления
            external_code: Значение внешнего кода
            external_code_type: Тип внешнего кода
            from_external_code: Искать по внешнему коду
            **kwargs: Условия поиска

        Returns:
            Кортеж из ObjectId и признака создания объекта
        """


class IDetailOrCreateRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения деталей или создания"""

    detail_or_create_atomic: bool
    """Выполнить в одной транзакции"""
    detail_or_create_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""
    detail_or_create_convert_return: bool
    """Конвертировать ли результат функции"""
    detail_or_create_convert_path: ConvertPath
    """Путь до элемента, который нужно конвертировать"""

    @abstractmethod
    def detail_or_create(
        self,
        *args,
        defaults: dict[str, Any] = None,
        external_code: str = None,
        external_code_type: Enum = None,
        from_external_code: bool = False,
        **kwargs,
    ) -> tuple[Entity | DTO, bool]:
        """Получает / создает запись в БД

        Args:
            *args: Позиционные аргументы
            defaults: Данные для создания / обновления
            external_code: Значение внешнего кода
            external_code_type: Тип внешнего кода
            from_external_code: Искать по внешнему коду
            **kwargs: Условия поиска / данные для создания

        Returns:
            Кортеж из DTO или Entity и признака создания объекта

        """


class IDeleteRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория удаления"""

    delete_atomic: bool
    """Выполнить в одной транзакции"""
    delete_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def delete(self, pk: ObjectId) -> ObjectId:
        """Удаляет запись в БД по pk

        Args:
            pk: Первичный ключ

        Returns:
            Id объекта

        """


class IBulkDeleteRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория множественного удаления"""

    delete_atomic: bool
    """Выполнить в одной транзакции"""
    delete_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def bulk_delete(self, ids: list[ObjectId]) -> None:
        """Удаляет записи в БД по списку id

        Args:
            ids: Список id записей

        """


class IDetailRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения деталей"""

    detail_convert_return: bool
    """Конвертировать ли результат функции"""
    detail_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def detail(self, *conditions: Any, filter_dto: DTO = None, raise_exception=True, **filters) -> Entity | DTO:
        """Возвращает Entity или DTO записи, удовлетворяющей запросу

        Args:
            *conditions: Кортеж условий вида django.db.models.Q
            filter_dto: Pydantic модель с полями фильтрации запроса
            raise_exception: Вызывать ли ошибку
            **filters: Словарь фильтров запроса

        Returns:
            Entity или DTO записи, удовлетворяющей запросу
        """


class IDetailByPKRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения деталей по первичному ключу"""

    detail_by_pk_convert_return: bool
    """Конвертировать ли результат функции"""
    detail_by_pk_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def detail_by_pk(self, pk: ObjectId, raise_exception=True) -> Entity | DTO:
        """Возвращает Entity или DTO записи, по pk

        Args:
            pk: Первичный ключ
            raise_exception: Вызывать ли ошибку

        Returns:
            Entity или DTO записи, удовлетворяющей запросу
        """


class IDetailByExternalCodeRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения деталей по внешнему коду"""

    external_code_model: str | object
    """Путь или объект модели внешнего кода"""
    detail_by_external_code_convert_return: bool
    """Конвертировать ли результат функции"""
    detail_by_external_code_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    @abstractmethod
    def detail_by_external_code(self, code: str, code_type: str | Enum, raise_exception=True) -> Entity | DTO:
        """Возвращает Entity или DTO записи, по внешнему коду

        Args:
            code: значение кода
            code_type: тип кода
            raise_exception: Вызывать ли ошибку

        Returns:
            Entity или DTO записи, удовлетворяющей запросу
        """


class IGetByIdsRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения списка объектов по id"""

    get_by_ids_convert_return: bool
    """Конвертировать ли результат функции"""
    get_by_ids_exceptions_redirects: tuple[BaseExceptionRedirect]
    """Кортеж дополнительных перенаправлений исключений"""

    def get_by_ids(self, ids: list[ObjectId]) -> list[Entity | DTO]:
        """Возвращает список Entity или DTO записей, по списку их id

        Args:
            ids: Список id записей

        Returns:
            список Entity или DTO записи, удовлетворяющей запросу
        """


class IRetrieveRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения списка объектов"""

    retrieve_convert_return: bool
    """Конвертировать ли результат функции"""

    @abstractmethod
    def retrieve(
        self,
        *conditions: Any,
        limit: int = None,
        offset: int = None,
        order_by: tuple[str] = (),
        distinct: bool | tuple[str] = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[Entity | DTO] | QuerySet:
        """Возвращает последовательность Entity, DTO или QuerySet удовлетворяющих запросу

        Args:
            *conditions: Кортеж условий вида django.db.models.Q
            limit: Лимит количества записей
            offset: Смещение записей
            order_by: Кортеж сортировок записей
            distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность Entity, DTO или QuerySet удовлетворяющих запросу
        """

    @abstractmethod
    def count(
        self,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> int:
        """Возвращает последовательность Entity, DTO или QuerySet удовлетворяющих запросу

        Args:
            *conditions: Кортеж условий вида django.db.models.Q
            filter_dto: Pydantic модель с полями фильтрации запроса
            distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей
            **filters: Словарь фильтров запроса

        Returns:
            Количество записей
        """


class ISearchRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория получения списка объектов по полнотекстовому поиску"""

    search_expressions: Sequence[str]
    """Последовательность полей или выражений, по которым нужен полнотекстовый поиск"""
    search_extra_replaces: Mapping[str, str]
    """Дополнительные замены при поиске подстроки"""
    search_convert_return: bool
    """Конвертировать ли результат функции"""
    search_filter_function: Callable
    """функция, реализующая поиск подстроки"""

    @abstractmethod
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
    ) -> list[Entity | DTO | QuerySet]:
        """Возвращает последовательность Entity, DTO или QuerySet удовлетворяющих запросу

        Args:
            search: Текст запроса
            *conditions: Кортеж условий вида django.db.models.Q
            limit: Лимит количества записей
            offset: Смещение записей
            order_by: Кортеж сортировок записей
            distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность Entity, DTO или QuerySet удовлетворяющих запросу
        """

    @abstractmethod
    def search_count(
        self,
        search: str,
        *conditions: Any,
        filter_dto: DTO = None,
        distinct: bool | tuple[str] = None,
        **filters,
    ) -> int:
        """Возвращает последовательность Entity, DTO или QuerySet удовлетворяющих запросу

        Args:
            search: Текст запроса
            *conditions: Кортеж условий вида django.db.models.Q
            filter_dto: Pydantic модель с полями фильтрации запроса
            distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей
            **filters: Словарь фильтров запроса

        Returns:
            Количество записей
        """


class IExistsRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для миксина репозитория проверки существования записи"""

    @abstractmethod
    def exists(self, *conditions: Any, filter_dto: DTO = None, **filters) -> bool:
        """Возвращает bool существуют ли записи, удовлетворяющие условию

        Args:
            *conditions: Кортеж условий вида django.db.models.Q
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Существуют ли записи, удовлетворяющие условию
        """


class IGetSoloRepositoryMixin(ABC, mixin_for(IRepository)):
    """Абстрактный интерфейс для репозитория получения объекта модели Singleton"""

    def get_solo(self) -> Entity | DTO:
        """Возвращает [`Entity`][contrib.clean_architecture.interfaces.PydanticEntity] или [`DTO`][agora.clean_architecture.interfaces.PydanticDTO] записей, по списку их `id`

        Returns:
            список [`Entity`][contrib.clean_architecture.interfaces.PydanticEntity] или [`DTO`][agora.clean_architecture.interfaces.PydanticDTO] записи, удовлетворяющей запросу
        """


class ICreateUpdateRepositoryMixin(ICreateRepositoryMixin, IUpdateRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория создания / обновления"""


class IUpdateDeleteRepositoryMixin(IUpdateRepositoryMixin, IDeleteRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория обновления / удаления"""


class ICreateDeleteRepositoryMixin(ICreateRepositoryMixin, IDeleteRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория создания / удаления"""


class ICreateUpdateDeleteRepositoryMixin(ICreateRepositoryMixin, IUpdateRepositoryMixin, IDeleteRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория создания / обновления / удаления"""


class IDetailsRepositoryMixin(IDetailRepositoryMixin, IDetailByPKRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория получения деталей"""


class IListRepositoryMixin(IRetrieveRepositoryMixin, ISearchRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория получения списка объектов"""


class IReadRepositoryMixin(IListRepositoryMixin, IDetailsRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория получения деталей / списка объектов"""


class ICRUDRepositoryMixin(ICreateUpdateDeleteRepositoryMixin, IReadRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория создание / чтение /обновление / удаление"""


class IPatchListRepositoryMixin(IUpdateRepositoryMixin, IBulkCreateRepositoryMixin, IBulkDeleteRepositoryMixin):
    """Абстрактный интерфейс для миксина репозитория модификации списка объектов"""


class ICreateUpdateBaseRepository(ABC, mixin_for(IRepository)):
    """Базовый репозиторий создания и изменения"""
