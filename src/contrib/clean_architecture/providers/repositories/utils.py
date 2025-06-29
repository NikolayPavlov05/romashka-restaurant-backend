"""Модуль с утилитами для репозиториев

Functions:
    get_query_page: Возвращает QuerySet с лимитом, смещением и сортировкой
    get_distinct_query: Django базовый репозиторий
    has_field: Django базовый репозиторий

"""
from __future__ import annotations

from contrib.clean_architecture.interfaces import Model
from contrib.clean_architecture.interfaces import QuerySet
from contrib.pydantic.model import PydanticModel


def get_query_page(objects: QuerySet, limit: int = None, offset: int = None, order_by: tuple = None) -> QuerySet:
    """Возвращает QuerySet с лимитом, смещением и сортировкой

    Args:
        objects: QuerySet
        limit: Лимит количества записей
        offset: Смещение записей
        order_by: Кортеж сортировок записей

    Returns:
        QuerySet

    """
    if order_by:
        objects = objects.order_by(*order_by)
    if offset:
        objects = objects[offset:]
    if limit and limit != -1:
        objects = objects[:limit]

    return objects


def get_distinct_query(objects: QuerySet, distinct: bool | tuple[str] = None):
    """Вызывает distinct на QuerySet

    Args:
        objects: QuerySet
        distinct: Применять ли distinct на запросе  или кортеж полей для удаления дублей

    Returns:
        QuerySet

    """
    if isinstance(distinct, tuple):
        objects = objects.order_by(*distinct).distinct(*distinct)
    elif distinct:
        objects = objects.distinct()

    return objects


def has_field(model: Model, field: str):
    """Проверяет наличие поля в DTO, Entity или модели ORM

    Args:
        model: Модель
        field: Название поля

    Returns:
        Существует ли поле

    """
    if not model:
        return False
    if issubclass(model, PydanticModel):
        return field in model.model_fields
    return hasattr(model, field)
