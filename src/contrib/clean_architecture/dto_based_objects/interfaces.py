"""Модуль с интерфейсами DTO based objects

Classes:
    IDTOBasedObjectsMixin: Абстрактный интерфейс миксина для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model

"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping
from typing import Any
from typing import Self

from contrib.clean_architecture.dto_based_objects.dtos import Relations
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import IPrefetch
from contrib.clean_architecture.interfaces import M2MManager
from contrib.clean_architecture.interfaces import Manager
from contrib.clean_architecture.interfaces import Model


class IDTOBasedObjectsMixin(ABC):
    """Абстрактный интерфейс для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model"""

    _models_managers_attrs: dict[type[Model], str]
    _models_dtos: dict[type[Model], type[DTO]]
    _models_dtos_related: dict[tuple[type[Model], type[DTO]], Relations]
    _extra_select_related: dict[tuple[type[Model], type[DTO]], set]
    _extra_prefetch_related: dict[tuple[type[Model], type[DTO]], set]

    model: type[Model]
    """Класс модели ORM"""
    manager_attr: str
    """Атрибут объектного менеджера модели"""
    prefetch_class: type[IPrefetch, Any]
    """Класс для описания запроса на получение моделей со связью m2m"""
    sequence_classes: tuple
    """Кортеж классов коллекций связанных объектов"""
    m2m_manager: M2MManager
    """Класс для управления зависимостями m2m"""

    @abstractmethod
    def with_dto(
        self,
        dto: type[DTO],
        manager_attr: str = None,
        extra_select_related: tuple = (),
        extra_prefetch_related: tuple = (),
        other_dtos: Mapping[type[Model], type[DTO]] = None,
        other_managers_attrs: Mapping[type[Model], str] = None,
        other_extra_select_related: Mapping[type[Model], set] = None,
        other_extra_prefetch_related: Mapping[type[Model], set] = None,
    ) -> Self:
        """Добавляет DTO к репозиторию

        Добавляет необходимые select_related и prefetch_related к запросу при обращении к objects или get_objects
        Необходимые зависимости ищутся на основании рекурсивного прохода по связям в DTO и Model

        Args:
            dto: Класс DTO который ожидается при конвертации
            manager_attr: Атрибут модели для получения объектного менеджера
            extra_select_related: Дополнительные select_related для dto
            extra_prefetch_related: Дополнительные prefetch_related для dto
            other_dtos: Словарь с дополнительными моделями и DTO
            other_managers_attrs: Словарь с дополнительными моделями их атрибутами объектных менеджеров
            other_extra_select_related: Дополнительные select_related для dto моделей
            other_extra_prefetch_related: Дополнительные prefetch_related для dto моделей

        Returns:
            Self: Экземпляр класса
        """

    @abstractmethod
    def clean_with_dto_context(self) -> None:
        """Удаляет все DTO добавленные в контекст"""

    @abstractmethod
    def get_objects(self, model: type[Model]) -> Manager:
        """Возвращает объектный менеджер для конкретной модели

        Args:
            model: Модель, для которой нужно получить объектный менеджер

        Returns:
            Manager: Объектный менеджер
        """

    @property
    @abstractmethod
    def objects(self) -> Manager:
        """Объектный менеджер модели со всеми select_related и prefetch_related"""

    @abstractmethod
    def extend_objects(self, objects: Manager) -> Manager:
        """Функция, для расширения параметров запроса при вызове контекстного менеджера

        Args:
            objects: Объектный менеджер / QuerySet

        Returns:
            Manager: Объектный менеджер / QuerySet
        """
