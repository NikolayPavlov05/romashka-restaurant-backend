"""Модуль с миксинами и базовыми классами для репозиториев

Modules:
    utils: Утилиты
    interfaces: Абстрактные интерфейсы
    bases: Базовые реализации
    django.bases: Реализация для django моделей

Examples:
    ```python
    >>> from app.repositories import IBusinessPriorityRepository
    >>> from app.entities import BusinessPriorityEntity
    >>> from app.models import BusinessPriority
    >>> from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository
    >>> from contrib.pydantic.utils import translated_fields
    >>> from contrib.clean_architecture.providers.repositories.bases import ReadRepositoryMixin
    >>>
    >>> class BusinessPriorityRepository(ReadRepositoryMixin, DjangoRepository, IBusinessPriorityRepository):
    >>>     model = BusinessPriority
    >>>     entity = BusinessPriorityEntity
    >>>     search_expressions = translated_fields("name")
    ```
"""
from __future__ import annotations
