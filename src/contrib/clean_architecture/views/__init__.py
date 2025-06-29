"""Модуль с миксинами и базовыми классами для представлений

Modules:
    utils: Утилиты
    bases: Базовые реализации

Examples:
    ```python
    >>> from app import controllers
    >>> from app.boundraies import dtos
    >>> from contrib.clean_architecture.views.bases import CleanViewSet, ReadCleanViewSetMixin
    >>> from contrib.module_manager import Depend
    >>>
    >>> class BusinessPrioritiesViewSet(ReadCleanViewSetMixin, CleanViewSet, injects=("core", "ntz")):
    >>>     controller: Depend[controllers.BusinessPriorityController]
    >>>
    >>>     tags = ["business_priorities"]
    >>>     return_type = dtos.BusinessPriorityShortInfoDTO
    >>>     return_detail_type = dtos.BusinessPriorityInfoDTO
    >>>     return_pagination_type = dtos.BusinessPriorityShortInfoDTO.paginated
    ```
"""
from __future__ import annotations
