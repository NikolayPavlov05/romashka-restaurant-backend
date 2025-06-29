"""Модуль с базовым контроллером и миксинами

## Базовый контроллер

Classes:
    Controller: Базовый контроллер

## Создание

Classes:
    CreateControllerMixin: Миксин контроллера создания

## Обновление

Classes:
    UpdateControllerMixin: Миксин контроллера обновления
    PatchListControllerMixin: Миксин контроллера обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}

## Удаление

Classes:
    DeleteControllerMixin: Миксин контроллера удаления

## Получение записи

Classes:
    DetailControllerMixin: Миксин контроллера получения деталей
    DetailByPKControllerMixin: Миксин контроллера получения деталей по первичному ключу
    DetailByExternalCodeControllerMixin: Миксин контроллера получения деталей по внешнему коду

## Получение списка записей

Classes:
    RetrieveControllerMixin: Миксин контроллера получения списка объектов
    SearchControllerMixin: Миксин контроллера получения списка объектов по полнотекстовому поиску

## Экспорт записей

Classes:
    ExportXLSControllerMixin: Миксин контроллера экспорта списка объектов

## Комбинации интерфейсов миксинов контроллеров

Classes:
    CreateUpdateControllerMixin: Миксин контроллера создания / обновления
    UpdateDeleteControllerMixin: Миксин контроллера обновления / удаления
    CreateDeleteControllerMixin: Миксин контроллера создания / удаления
    CreateUpdateDeleteControllerMixin: Миксин контроллера создания / обновления / удаления
    DetailsControllerMixin: Миксин контроллера получения деталей
    ListControllerMixin: Миксин контроллера получения списка объектов
    ReadControllerMixin: Миксин контроллера получения деталей / списка объектов
    CRUDControllerMixin: Миксин контроллера создание / чтение /обновление / удаление

"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from contrib.clean_architecture.consts import CleanMethods
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import ObjectId
from contrib.clean_architecture.providers.interactors.bases import CreateDeleteInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import CreateInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import CreateUpdateDeleteInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import CreateUpdateInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import CRUDInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DeleteInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailByExternalCodeInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailByPKInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailsInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import ExportXLSInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import Interactor
from contrib.clean_architecture.providers.interactors.bases import ListInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import PatchListInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import ReadInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import RetrieveInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import SearchInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import UpdateDeleteInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import UpdateInteractorMixin
from contrib.clean_architecture.types import mixin_for
from contrib.clean_architecture.utils.method import clean_method
from contrib.clean_architecture.utils.method import CleanMethodMixin
from contrib.pydantic.model import ExportXLSResponseDTO
from contrib.pydantic.model import PaginatedModel

if TYPE_CHECKING:
    from contrib.clean_architecture.providers.controllers.utils import Permissions


class Controller(CleanMethodMixin):
    """Базовый контроллер"""

    __permissions__: list[Permissions]

    interactor: Interactor
    """Интерактор"""

    def __init__(self, *args, **kwargs):
        if hasattr(self, "__permissions__"):
            for permissions in self.__permissions__:
                permissions.initialize(self)
        super().__init__(*args, **kwargs)


class CreateControllerMixin(mixin_for(Controller)):
    """Миксин контроллера создания"""

    interactor: CreateInteractorMixin

    @clean_method(name=CleanMethods.CREATE)
    def create(self, dto: DTO = None, *args, **kwargs) -> ObjectId:
        """Создает запись в БД

        Args:
            dto: экземпляр DTO
            *args: Позиционные аргументы
            **kwargs: Дополнительные данные для создания записи

        Returns:
            Id созданного объекта

        """
        return self.interactor.create(dto, *args, **kwargs)


class UpdateControllerMixin(mixin_for(Controller)):
    """Миксин контроллера обновления"""

    interactor: UpdateInteractorMixin

    @clean_method(name=CleanMethods.UPDATE)
    def update(self, pk: ObjectId, dto: DTO | None = None, *args, **kwargs) -> ObjectId:
        """Обновляет запись в БД

        Args:
            pk: Первичный ключ
            dto: Экземпляр DTO
            *args: позиционные аргументы
            **kwargs: Дополнительные данные для обновления записи

        Returns:

        """
        return self.interactor.update(pk, dto, *args, **kwargs)


class PatchListControllerMixin(mixin_for(Controller)):
    """Обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}"""

    interactor: PatchListInteractorMixin

    @clean_method(name=CleanMethods.PATCH_LIST)
    def patch_list(self, dto: DTO, *args, **kwargs) -> None:
        """Обновляет модели списком

        Args:
            dto: DTO с телом patch запроса
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """
        return self.interactor.patch_list(dto, *args, **kwargs)


class DeleteControllerMixin(mixin_for(Controller)):
    """Миксин контроллера удаления"""

    interactor: DeleteInteractorMixin

    @clean_method(name=CleanMethods.DELETE)
    def delete(self, pk: ObjectId) -> ObjectId:
        """Удаляет запись в БД по pk

        Args:
            pk: Первичный ключ

        Returns:
            Id объекта

        """
        return self.interactor.delete(pk)


class DetailControllerMixin(mixin_for(Controller)):
    """Миксин контроллера получения деталей"""

    interactor: DetailInteractorMixin

    @clean_method(name=CleanMethods.DETAIL)
    def detail(self, filter_dto: DTO = None, **filters) -> DTO:
        """Возвращает DTO записи, удовлетворяющей запросу

        Args:
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.interactor.detail(filter_dto=filter_dto, **filters)


class DetailByPKControllerMixin(mixin_for(Controller)):
    """Миксин контроллера получения деталей по первичному ключу"""

    interactor: DetailByPKInteractorMixin

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def detail_by_pk(self, pk: ObjectId, *args, **kwargs) -> DTO:
        """Возвращает DTO записи, по первичному ключу

        Args:
            pk: Первичный ключ
            **kwargs: Дополнительные именованные аргументы

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.interactor.detail_by_pk(pk, *args, **kwargs)


class DetailByExternalCodeControllerMixin(mixin_for(Controller)):
    """Миксин контроллера получения деталей по внешнему коду"""

    interactor: DetailByExternalCodeInteractorMixin

    @clean_method(name=CleanMethods.DETAIL_BY_EXTERNAL_CODE)
    def detail_by_external_code(self, code: str, code_type: str | Enum) -> DTO:
        """Возвращает DTO записи, по внешнему коду

        Args:
            code: значение кода
            code_type: тип кода

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.interactor.detail_by_external_code(code, code_type)


class RetrieveControllerMixin(mixin_for(Controller)):
    """Миксин контроллера получения списка объектов"""

    interactor: RetrieveInteractorMixin

    @clean_method(name=CleanMethods.RETRIEVE)
    def retrieve(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        order_by: tuple[str] = (),
        paginated: bool = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[DTO] | PaginatedModel:
        """Возвращает последовательность DTO удовлетворяющих запросу

        Args:
            limit: Лимит количества записей
            offset: Смещение записей
            order_by: Кортеж сортировок записей
            paginated: Нужна ли пагинация
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность DTO удовлетворяющих запросу

        """
        return self.interactor.retrieve(
            limit=limit,
            offset=offset,
            order_by=order_by,
            paginated=paginated,
            filter_dto=filter_dto,
            **filters,
        )


class SearchControllerMixin(mixin_for(Controller)):
    """Миксин контроллера получения списка объектов по полнотекстовому поиску"""

    interactor: SearchInteractorMixin

    @clean_method(name=CleanMethods.SEARCH)
    def search(
        self,
        search: str,
        *,
        limit: int = 20,
        offset: int = 0,
        order_by: tuple[str] = (),
        paginated: bool = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[DTO] | PaginatedModel:
        """Возвращает последовательность DTO удовлетворяющих запросу

        Args:
            search: Текст запроса
            limit: Лимит количества записей
            offset: Смещение записей
            order_by: Кортеж сортировок записей
            paginated: Нужна ли пагинация
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность DTO удовлетворяющих запросу

        """
        return self.interactor.search(
            search,
            limit=limit,
            offset=offset,
            order_by=order_by,
            paginated=paginated,
            filter_dto=filter_dto,
            **filters,
        )


class ExportXLSControllerMixin(mixin_for(Controller)):
    """Миксин контроллера экспорта списка объектов"""

    interactor: ExportXLSInteractorMixin

    @clean_method(name=CleanMethods.EXPORT_XLS)
    def export_xls(self, *, ids: list[int] | None = None, fields: list[str], **filters) -> ExportXLSResponseDTO:
        """Возвращает ExportXLSResponseDTO

        Args:
            ids: Списой id объектов
            fields: Список полей
            **filters: Словарь фильтров запроса

        Returns:
            ExportXLSResponseDTO

        """
        return self.interactor.export_xls(ids=ids, fields=fields, **filters)


class CreateUpdateControllerMixin(CreateControllerMixin, UpdateControllerMixin):
    """Миксин контроллера создания / обновления"""

    interactor: CreateUpdateInteractorMixin


class UpdateDeleteControllerMixin(UpdateControllerMixin, DeleteControllerMixin):
    """Миксин контроллера обновления / удаления"""

    interactor: UpdateDeleteInteractorMixin


class CreateDeleteControllerMixin(CreateControllerMixin, DeleteControllerMixin):
    """Миксин контроллера создания / удаления"""

    interactor: CreateDeleteInteractorMixin


class CreateUpdateDeleteControllerMixin(CreateControllerMixin, UpdateControllerMixin, DeleteControllerMixin):
    """Миксин контроллера создания / обновления / удаления"""

    interactor: CreateUpdateDeleteInteractorMixin


class DetailsControllerMixin(DetailControllerMixin, DetailByPKControllerMixin):
    """Миксин контроллера получения деталей"""

    interactor: DetailsInteractorMixin


class ListControllerMixin(RetrieveControllerMixin, SearchControllerMixin):
    """Миксин контроллера получения списка объектов"""

    interactor: ListInteractorMixin


class ReadControllerMixin(ListControllerMixin, DetailsControllerMixin):
    """Миксин контроллера получения деталей / списка объектов"""

    interactor: ReadInteractorMixin


class CRUDControllerMixin(CreateUpdateDeleteControllerMixin, ReadControllerMixin):
    """Миксин контроллера создание / чтение /обновление / удаление"""

    interactor: CRUDInteractorMixin
