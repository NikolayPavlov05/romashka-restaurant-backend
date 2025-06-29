"""Модуль с миксинами и базовыми классами для интеракторов

Modules:
    utils: Утилиты
    bases: Базовые реализации
    exceptions: Исключения

Examples:
    ```python
    >>> from contrib.clean_architecture.providers.interactors.bases import Interactor, ReadInteractorMixin
    >>> from contrib.module_manager import Depend
    >>> from app.repositories import IBusinessPriorityRepository
    >>>
    >>> class BusinessPriorityInteractor(ReadInteractorMixin, Interactor):
    >>>     repository: Depend[IBusinessPriorityRepository]
    ```
"""
from __future__ import annotations
