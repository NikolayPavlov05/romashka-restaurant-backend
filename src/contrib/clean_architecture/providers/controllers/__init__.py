"""Модуль с миксинами и базовыми классами для контроллеров

Modules:
    bases: Базовые реализации

Examples:
    ```python
    >>> from contrib.clean_architecture.providers.controllers.bases import Controller, ReadControllerMixin
    >>> from contrib.module_manager import Depend
    >>>
    >>> from app import BusinessPriorityInteractor
    >>>
    >>> class BusinessPriorityInteractor(ReadControllerMixin, Controller):
    >>>     interactor: Depend[BusinessPriorityInteractor]
    ```
"""
from __future__ import annotations
