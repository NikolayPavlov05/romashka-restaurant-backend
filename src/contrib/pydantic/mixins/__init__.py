"""Модуль с миксинами для кастомной модели Pydantic

Modules:
    interfaces: Абстрактные интерфейсы
    bases: Базовые реализации
    django.model: Реализация для django

Examples:
    ```python
    >>> from contrib.pydantic.model import PydanticModel
    >>> from contrib.pydantic.utils import translated_fields
    >>> from contrib.mixins.pydantic_model import IsActiveMixin, NameMixin, IdMixin, CreatedUpdatedMixin, DescriptionMixin
    >>>
    >>>
    >>> class BusinessPriorityEntity(PydanticModel, proxy_model=True):
    >>>     pass
    >>>
    >>>
    >>> @translated_fields("name")
    >>> class BusinessPriorityShortInfoDTO(IsActiveMixin, NameMixin, IdMixin, response_model=True, with_paginated=True):
    >>>     pass
    >>>
    >>>
    >>> @translated_fields("name", "description")
    >>> class BusinessPriorityInfoDTO(CreatedUpdatedMixin, DescriptionMixin, BusinessPriorityShortInfoDTO):
    >>>     pass
    >>>
    >>>
    >>> @translated_fields("name", "description")
    >>> class BusinessPriorityCreateDTO(DescriptionMixin, BusinessPriorityShortInfoDTO, request_model=True):
    >>>     pass
    ```
"""
from __future__ import annotations
