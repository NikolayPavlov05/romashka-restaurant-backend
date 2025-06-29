"""Модуль с базовым интерактором и миксинами

## Базовый интерактор

Classes:
    Interactor: Базовый интерактор

## Создание

Classes:
    CreateInteractorMixin: Миксин интерактора создания

## Обновление

Classes:
    UpdateInteractorMixin: Миксин интерактора обновления
    PatchListInteractorMixin: Миксин интерактора обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}

## Удаление

Classes:
    DeleteInteractorMixin: Миксин интерактора удаления

## Получение записи

Classes:
    DetailInteractorMixin: Миксин интерактора получения деталей
    DetailByPKInteractorMixin: Миксин интерактора получения деталей по первичному ключу
    DetailByExternalCodeInteractorMixin: Миксин интерактора получения деталей по внешнему коду

## Получение списка записей

Classes:
    RetrieveInteractorMixin: Миксин интерактора получения списка объектов
    SearchInteractorMixin: Миксин интерактора получения списка объектов по полнотекстовому поиску

## Экспорт записей

Classes:
    ExportXLSInteractorMixin: Миксин интерактора экспорта списка объектов

## Комбинации интерфейсов миксинов интеракторов

Classes:
    CreateUpdateInteractorMixin: Миксин интерактора создания / обновления
    UpdateDeleteInteractorMixin: Миксин интерактора обновления / удаления
    CreateDeleteInteractorMixin: Миксин интерактора создания / удаления
    CreateUpdateDeleteInteractorMixin: Миксин интерактора создания / обновления / удаления
    DetailsInteractorMixin: Миксин интерактора получения деталей
    ListInteractorMixin: Миксин интерактора получения списка объектов
    ReadInteractorMixin: Миксин интерактора получения деталей / списка объектов
    CRUDInteractorMixin: Миксин интерактора создание / чтение /обновление / удаление

"""
from __future__ import annotations

import io
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from enum import Enum

import xlwt
from contrib.clean_architecture.consts import CleanMethods
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import Model
from contrib.clean_architecture.interfaces import ObjectId
from contrib.clean_architecture.providers.interactors.exceptions import (
    NothingToUpdateOrCreateException,
)
from contrib.clean_architecture.providers.interactors.utils import bind_return_type
from contrib.clean_architecture.providers.repositories.interfaces import ICreateDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICreateUpdateDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICreateUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ICRUDRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailByExternalCodeRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailByPKRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IDetailsRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IListRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IPatchListRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IReadRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IRepository
from contrib.clean_architecture.providers.repositories.interfaces import IRetrieveRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import ISearchRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IUpdateDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.interfaces import IUpdateRepositoryMixin
from contrib.clean_architecture.types import mixin_for
from contrib.clean_architecture.utils.method import clean_method
from contrib.clean_architecture.utils.method import CleanMethodMixin
from contrib.context.mixins import ContextMixin
from contrib.context.utils import context_property
from contrib.exceptions.exceptions import ValidationError
from contrib.localization.services import gettext as _
from contrib.pydantic.model import ExportXLSResponseDTO
from contrib.pydantic.model import PaginatedModel
from contrib.pydantic.model import ValidationErrorItemDTO


class Interactor(CleanMethodMixin):
    """Базовый интерактор"""

    repository: IRepository
    """Репозиторий"""
    return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""
    return_detail_type: type[DTO] = None
    """DTO деталей, которое нужно вернуть"""
    return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""


class ValidationInteractorMixin(ContextMixin, mixin_for(Interactor)):
    """Миксин интерактора для валидации данных перед обновлением или созданием"""

    required_fields: set = {}
    """Обязательные поля"""
    context_requires_fields: set[str] = context_property(default_factory=set)
    """Обязательные поля в контексте"""

    validate_fields: list = []
    """Поля для валидации"""
    can_update_fields_with_external_codes: list = []
    """Поля, которые можно обновить после отправки во внешние сервисы"""
    m2m_fields: list = []
    exclude_fields: list = []

    def validate_required_fields(self, obj: DTO):
        """Проверяет заполненность обязательных полей

        Args:
            obj: Объект для проверки
        """
        errors = []
        missing_required_fields = []
        for required_field in self.required_fields | self.context_requires_fields:
            if not getattr(obj, required_field, None):
                missing_required_fields.append(required_field)

        if missing_required_fields:
            errors.append(ValidationErrorItemDTO(loc=missing_required_fields, msg=_("Обязательное поле")))

        if errors:
            raise ValidationError(errors=errors)

    def validate_changed_fields(self, initial_object: DTO, modified_object: DTO) -> None:
        """Проверяет измененные поля

        Args:
            initial_object: Текущие данные
            modified_object: Данные для изменения
        """
        errors = []
        cant_update_fields = []
        for field in self.validate_fields:
            if field in self.can_update_fields_with_external_codes or field in self.exclude_fields:
                continue

            # Проверка полей с m2m
            initial_data = getattr(initial_object, field, None)
            updated_data = getattr(modified_object, field, None)
            if field in self.m2m_fields:
                initial_data = {item.id for item in initial_data.all()}
                updated_data = set(updated_data)

            # Проверка остальных полей
            if not initial_data == updated_data:
                cant_update_fields.append(field)

        if cant_update_fields:
            errors.append(
                ValidationErrorItemDTO(
                    loc=cant_update_fields,
                    msg=_("Нет доступа к редактированию данных полей"),
                )
            )

        if errors:
            raise ValidationError(errors=errors)


class CreateInteractorMixin(ValidationInteractorMixin, mixin_for(Interactor)):
    """Миксин интерактора создания"""

    repository: ICreateRepositoryMixin

    @clean_method(name=CleanMethods.CREATE)
    def create(self, dto: DTO | None = None, *args, **kwargs) -> ObjectId:
        """Создает запись в БД

        Args:
            dto: экземпляр DTO
            *args: Позиционные аргументы
            **kwargs: Дополнительные данные для создания записи

        Returns:
            Id созданного объекта

        """
        entity = self.repository.entity(**dto.model_dump(exclude_unset=True)) if dto else None
        return self.repository.create(entity, *args, **kwargs)


class UpdateInteractorMixin(ValidationInteractorMixin, mixin_for(Interactor)):
    """Миксин интерактора обновления"""

    repository: IUpdateRepositoryMixin

    @clean_method(name=CleanMethods.UPDATE)
    def update(self, pk: ObjectId, dto: DTO, *args, **kwargs) -> ObjectId:
        """Обновляет запись в БД

        Args:
            pk: Первичный ключ
            dto: Экземпляр DTO
            *args: позиционные аргументы
            **kwargs: Дополнительные данные для обновления записи

        Returns:

        """
        data = {
            self.repository.primary_key_attr: pk,
            **(dto.model_dump(exclude_unset=True) if dto else {}),
        }
        entity = self.repository.entity(**data)
        return self.repository.update(entity, *args, **kwargs)


class PatchListInteractorMixin(mixin_for(Interactor)):
    """Обновление для Patch метода списком. {items: [{delete: true, id: 1, ...}]}"""

    repository: IPatchListRepositoryMixin

    can_create_or_update_blank: bool = False
    """Могут ли данные для обновления быть пустыми"""
    items_list_field: str = "items"
    """Атрибут, содержащий данные для обновления"""

    def patch_list_validate_update_objects(self, objects: list[DTO], *args, **kwargs) -> None:
        """Валидация данных до обновления.

        Args:
            objects: Список экземпляров DTO
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """

    def patch_list_validate_create_objects(self, objects: list[DTO], *args, **kwargs) -> None:
        """Валидация данных до создания.

        Args:
            objects: Список экземпляров DTO
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """

    def patch_list_extra_validation(
        self,
        need_to_create: list[DTO],
        need_to_update: list[DTO],
        need_to_delete: list[int],
        *args,
        **kwargs,
    ) -> None:
        """Дополнительная валидация данных перед изменениями.

        Args:
            need_to_create: Список экземпляров DTO для создания
            need_to_update: Список экземпляров DTO для изменения
            need_to_delete: Список экземпляров DTO для удаления
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """

    def patch_list_validate_delete_objects(self, objects: list[int], *args, **kwargs) -> None:
        """Валидация данных до удаления.

        Args:
            objects: Список id объектов
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """

    @clean_method(name=CleanMethods.PATCH_LIST)
    def patch_list(
        self,
        dto: DTO,
        create_kwargs: dict | None = None,
        update_kwargs: dict | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Обновляет модели списком

        Args:
            dto: DTO с телом patch запроса
            create_kwargs: Словарь с данными для создания
            update_kwargs: Словарь с данными для обновления
            *args: позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        """
        if not hasattr(dto, self.items_list_field):
            return

        need_to_create: list[DTO] = []
        need_to_update: list[DTO] = []
        need_to_delete: list[int] = []

        for item in getattr(dto, self.items_list_field):
            data: dict = item.model_dump(exclude_unset=True)
            pk: int | None = data.get(self.repository.primary_key_attr, None)
            delete: bool = data.get("delete", False)
            if delete:
                if pk is None:
                    continue
                need_to_delete.append(pk)
                continue

            update_create_dict = {
                field: data[field] for field in data if field not in ["delete", self.repository.primary_key_attr]
            }
            if not self.can_create_or_update_blank and not update_create_dict:
                raise NothingToUpdateOrCreateException()

            if pk:
                if update_kwargs:
                    update_create_dict.update(update_kwargs)
                update_create_dict[self.repository.primary_key_attr] = pk
                need_to_update.append(self.repository.entity(**update_create_dict))
            else:
                if create_kwargs:
                    update_create_dict.update(create_kwargs)
                need_to_create.append(self.repository.entity(**update_create_dict))

        self.patch_list_extra_validation(need_to_create, need_to_update, need_to_delete, *args, **kwargs)
        if need_to_create:
            self.patch_list_validate_create_objects(need_to_create, *args, **kwargs)
            self.repository.bulk_create(need_to_create)
        if need_to_delete:
            self.patch_list_validate_delete_objects(need_to_delete, *args, **kwargs)
            self.repository.bulk_delete(need_to_delete)
        if need_to_update:
            self.patch_list_validate_update_objects(need_to_update, *args, **kwargs)
            for _object in need_to_update:
                self.repository.update(_object)


class DeleteInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора удаления"""

    repository: IDeleteRepositoryMixin

    @clean_method(name=CleanMethods.DELETE)
    def delete(self, pk: ObjectId) -> ObjectId:
        """Удаляет запись в БД по pk

        Args:
            pk: Первичный ключ

        Returns:
            Id объекта

        """
        return self.repository.delete(pk)


class DetailInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора получения деталей"""

    repository: IDetailRepositoryMixin
    detail_return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""

    @bind_return_type(detail=True)
    @clean_method(name=CleanMethods.DETAIL)
    def detail(self, *, return_type: type[DTO] = None, filter_dto: DTO = None, **filters) -> DTO:
        """Возвращает DTO записи, удовлетворяющей запросу

        Args:
            return_type: DTO экземпляр которого нужно вернуть
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.repository.with_dto(return_type).detail(filter_dto=filter_dto, **filters)


class DetailByPKInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора получения деталей по первичному ключу"""

    repository: IDetailByPKRepositoryMixin
    detail_by_pk_return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""

    @bind_return_type(detail=True)
    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def detail_by_pk(self, pk: ObjectId, *, return_type: type[DTO] = None, **kwargs) -> DTO:
        """Возвращает DTO записи, по первичному ключу

        Args:
            pk: Первичный ключ
            return_type: DTO экземпляр которого нужно вернуть
            **kwargs: Дополнительные именованные аргументы

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.repository.with_dto(return_type).detail_by_pk(pk, **kwargs)


class DetailByExternalCodeInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора получения деталей по внешнему коду"""

    repository: IDetailByExternalCodeRepositoryMixin
    detail_by_external_code_return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""

    @bind_return_type(detail=True)
    @clean_method(name=CleanMethods.DETAIL_BY_EXTERNAL_CODE)
    def detail_by_external_code(self, code: str, code_type: str | Enum, *, return_type: type[DTO] = None) -> DTO:
        """Возвращает DTO записи, по внешнему коду

        Args:
            code: значение кода
            code_type: тип кода
            return_type: DTO экземпляр которого нужно вернуть

        Returns:
            DTO записи, удовлетворяющей запросу

        """
        return self.repository.with_dto(return_type).detail_by_external_code(code, code_type)


class RetrieveInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора получения списка объектов"""

    repository: IRetrieveRepositoryMixin
    retrieve_return_type: type[DTO] = None
    """DTO которое, нужно вернуть"""
    retrieve_return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    @bind_return_type(paginated=True)
    @clean_method(name=CleanMethods.RETRIEVE)
    def retrieve(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        order_by: tuple[str] = (),
        paginated: bool = None,
        return_type: type[DTO] = None,
        return_pagination_type: type[PaginatedModel] = None,
        filter_dto: DTO = None,
        **filters,
    ) -> list[DTO] | PaginatedModel:
        """Возвращает последовательность DTO удовлетворяющих запросу

        Args:
            limit: Лимит количества записей
            offset: Смещение записей
            order_by: Кортеж сортировок записей
            paginated: Нужна ли пагинация
            return_type: DTO экземпляр которого нужно вернуть
            return_pagination_type: DTO с пагинацией экземпляр которого нужно вернуть
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность DTO удовлетворяющих запросу

        """
        results = self.repository.with_dto(return_type).retrieve(
            limit=limit,
            offset=offset,
            order_by=order_by,
            filter_dto=filter_dto,
            **filters,
        )
        if not paginated:
            return results

        count = self.repository.count(filter_dto=filter_dto, **filters)
        return return_pagination_type.create(results, count, limit, offset)


class SearchInteractorMixin(mixin_for(Interactor)):
    """Миксин интерактора получения списка объектов по полнотекстовому поиску"""

    repository: ISearchRepositoryMixin
    search_return_type: type[DTO] = None
    """DTO деталей, которое нужно вернуть"""
    search_return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    @bind_return_type(paginated=True)
    @clean_method(name=CleanMethods.SEARCH)
    def search(
        self,
        search: str,
        *,
        limit: int = 20,
        offset: int = 0,
        order_by: tuple[str] = (),
        paginated: bool = None,
        return_type: type[DTO] = None,
        return_pagination_type: type[PaginatedModel] = None,
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
            return_type: DTO экземпляр которого нужно вернуть
            return_pagination_type: DTO с пагинацией экземпляр которого нужно вернуть
            filter_dto: Pydantic модель с полями фильтрации запроса
            **filters: Словарь фильтров запроса

        Returns:
            Последовательность DTO удовлетворяющих запросу

        """
        results = self.repository.with_dto(return_type).search(
            search,
            limit=limit,
            offset=offset,
            order_by=order_by,
            filter_dto=filter_dto,
            **filters,
        )
        if not paginated:
            return results

        count = self.repository.search_count(search, filter_dto=filter_dto, **filters)
        return return_pagination_type.create(results, count, limit, offset)


class ExportXLSInteractorMixin(ABC, mixin_for(Interactor)):
    """Миксин интерактора экспорта списка объектов"""

    repository: ISearchRepositoryMixin | IRetrieveRepositoryMixin
    xls_file_name: str = None
    """Имя xls файла"""
    xls_sheet_name: str = None
    """Имя таблицы в xls файле"""

    export_xls_return_type: type[DTO] = None
    """DTO деталей, которое нужно вернуть"""
    export_xls_return_pagination_type: type[PaginatedModel] = None
    """DTO с пагинацией, которое нужно вернуть"""

    @bind_return_type(paginated=False)
    @clean_method(name=CleanMethods.EXPORT_XLS)
    def export_xls(
        self,
        *,
        ids: list[int] | None = None,
        fields: list[str],
        return_type: type[DTO] = None,
        **filters,
    ) -> ExportXLSResponseDTO:
        """Возвращает ExportXLSResponseDTO

        Args:
            ids: Списой id объектов
            fields: Список полей
            return_type: DTO экземпляр которого нужно вернуть
            **filters: Словарь фильтров запроса

        Returns:
            ExportXLSResponseDTO

        """
        repository = self.repository.with_dto(return_type) if return_type else self.repository
        objects = repository.retrieve(pk__in=ids) if ids else repository.search(**filters)

        workbook = xlwt.Workbook()
        worksheet: xlwt.Worksheet = workbook.add_sheet(str(self.xls_sheet_name))

        field_name_mapping = self._get_fields_mapping()
        if not fields:
            fields = field_name_mapping.keys()

        for i, field in enumerate(fields):
            verbose_name = field_name_mapping.get(field, None)
            worksheet.write(0, i, str(verbose_name if verbose_name is not None else field))

        formatters = self._formatter_mapping()
        for row_index, obj in enumerate(objects, start=1):
            for col_index, field in enumerate(fields):
                field_formatter = formatters.get(field)
                try:
                    if field_formatter is not None:
                        cell_value = field_formatter(obj)
                    else:
                        cell_value = getattr(obj, field)
                        if cell_value is None:
                            cell_value = ""
                        if type(cell_value) == bool:
                            cell_value = "Да" if cell_value else "Нет"
                except AttributeError:
                    cell_value = ""

                worksheet.write(row_index, col_index, cell_value)

        output = io.BytesIO()
        workbook.save(output)

        return ExportXLSResponseDTO(file_content=output.getvalue(), file_name=str(self.xls_file_name))

    @abstractmethod
    def _get_fields_mapping(self) -> dict[str, str]:
        """Получение названия колонок в файле XLS."""

    @abstractmethod
    def _formatter_mapping(self) -> dict[str, Callable[[Model], str]]:
        """Набор форматтеров для обработки отображаемого значения для поля."""


class CreateUpdateInteractorMixin(CreateInteractorMixin, UpdateInteractorMixin):
    """Миксин интерактора создания / обновления"""

    repository: ICreateUpdateRepositoryMixin


class UpdateDeleteInteractorMixin(UpdateInteractorMixin, DeleteInteractorMixin):
    """Миксин интерактора обновления / удаления"""

    repository: IUpdateDeleteRepositoryMixin


class CreateDeleteInteractorMixin(CreateInteractorMixin, DeleteInteractorMixin):
    """Миксин интерактора создания / удаления"""

    repository: ICreateDeleteRepositoryMixin


class CreateUpdateDeleteInteractorMixin(CreateInteractorMixin, UpdateInteractorMixin, DeleteInteractorMixin):
    """Миксин интерактора создания / обновления / удаления"""

    repository: ICreateUpdateDeleteRepositoryMixin


class DetailsInteractorMixin(DetailInteractorMixin, DetailByPKInteractorMixin):
    """Миксин интерактора получения деталей"""

    repository: IDetailsRepositoryMixin


class ListInteractorMixin(RetrieveInteractorMixin, SearchInteractorMixin):
    """Миксин интерактора получения списка объектов"""

    repository: IListRepositoryMixin


class ReadInteractorMixin(ListInteractorMixin, DetailsInteractorMixin):
    """Миксин интерактора получения деталей / списка объектов"""

    repository: IReadRepositoryMixin


class CRUDInteractorMixin(CreateUpdateDeleteInteractorMixin, ReadInteractorMixin):
    """Миксин интерактора создание / чтение /обновление / удаление"""

    repository: ICRUDRepositoryMixin
