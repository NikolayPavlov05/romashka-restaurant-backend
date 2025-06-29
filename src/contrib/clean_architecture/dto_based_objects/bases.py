"""Модуль с базовыми классами DTO based objects

Classes:
    BaseDTOBasedObjectsMixin: Базовы миксин для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model

"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping
from typing import Self

from contrib.clean_architecture.dto_based_objects.dtos import MatchedRelation
from contrib.clean_architecture.dto_based_objects.dtos import Relations
from contrib.clean_architecture.dto_based_objects.enums import RelatedTypes
from contrib.clean_architecture.dto_based_objects.interfaces import (
    IDTOBasedObjectsMixin,
)
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import Manager
from contrib.clean_architecture.interfaces import Model
from contrib.pydantic.model import PydanticModel
from contrib.subclass_control.mixins import RequiredAttrsMixin
from pydantic import Field


class BaseDTOBasedObjectsMixin(RequiredAttrsMixin, IDTOBasedObjectsMixin, ABC):
    """Базовы миксин для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model"""

    required_attrs = ("model", "prefetch_class", "m2m_manager")

    sequence_classes = ()
    manager_attr = "objects"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._models_managers_attrs = {}
        self._models_dtos = {}
        self._models_dtos_related = {}
        self._extra_select_related = {}
        self._extra_prefetch_related = {}

    def clean_with_dto_context(self):
        self._models_managers_attrs = {}
        self._models_dtos = {}
        self._models_dtos_related = {}
        self._extra_select_related = {}
        self._extra_prefetch_related = {}

    def with_dto(
        self,
        dto: type[DTO],
        manager_attr: str = None,
        extra_select_related: set = None,
        extra_prefetch_related: set = None,
        other_dtos: Mapping[type[Model], type[PydanticModel]] = None,
        other_managers_attrs: Mapping[type[Model], str] = None,
        other_extra_select_related: Mapping[type[Model], set] = None,
        other_extra_prefetch_related: Mapping[type[Model], set] = None,
    ) -> Self:
        # Подготавливаем входные параметры
        extra_select_related = extra_select_related or set()
        extra_prefetch_related = extra_prefetch_related or set()
        other_dtos = other_dtos or {}
        other_managers_attrs = other_managers_attrs or {}
        other_extra_select_related = other_extra_select_related or {}
        other_extra_prefetch_related = other_extra_prefetch_related or {}

        # Записываем маппинг моделей и dto
        self._models_dtos[self.model] = dto
        self._models_dtos.update(other_dtos)

        # Записываем маппинг моделей и атрибутов объектных менеджеров
        self._models_managers_attrs[self.model] = manager_attr or self.manager_attr
        self._models_managers_attrs.update(other_managers_attrs)

        # Записываем дополнительные relations
        self._extra_select_related[(self.model, dto)] = extra_select_related | dto.extra_select_related
        self._extra_prefetch_related[(self.model, dto)] = extra_prefetch_related | dto.extra_prefetch_related

        # Записываем дополнительные relations для дополнительных моделей и dto
        for other_model, other_dto in other_dtos.items():
            if other_model in self._extra_select_related:
                self._extra_select_related[(other_model, other_dto)] |= other_dto.extra_select_related
            else:
                self._extra_select_related[(other_model, other_dto)] = other_dto.extra_select_related
            self._extra_select_related[(other_model, other_dto)] |= other_extra_select_related.get(other_model, set())

            if other_model in self._extra_prefetch_related:
                self._extra_prefetch_related[(other_model, other_dto)] |= other_dto.extra_prefetch_related
            else:
                self._extra_prefetch_related[(other_model, other_dto)] = other_dto.extra_prefetch_related
            self._extra_prefetch_related[(other_model, other_dto)] |= other_extra_prefetch_related.get(
                other_model, set()
            )

        # Собираем relations для всех моделей и dto
        for model, dto in self._models_dtos.items():
            if (model, dto) not in self._models_dtos_related:
                relations = self._collect_relations(model, dto)
                relations.select_related |= self._extra_select_related.get((model, dto), set())
                relations.prefetch_related |= self._extra_prefetch_related.get((model, dto), set())
                self._models_dtos_related[(model, dto)] = relations

        return self

    def _get_base_manager(self, model: type[Model]) -> Manager:
        """Возвращает базовый объектный менеджер запрашиваемой модели

        Args:
            model: Класс модели ORM

        Returns:
            Manager

        """
        manager_attr = self._models_managers_attrs.get(model, self.manager_attr)
        return getattr(model, manager_attr)

    @staticmethod
    def _extract_annotation(field: Field):
        """Получает оригинальную аннотацию из Field pydantic моделей

        Args:
            field: дескриптор поля, аннотацию которого нужно получить

        Returns:
            Аннотация

        """
        annotation = field.annotation
        while hasattr(annotation, "__args__"):
            annotation = annotation.__args__[0]

        return annotation

    @classmethod
    def _add_relations(cls, relations: Relations, matched_relation: MatchedRelation):
        """Добавляет select_related и prefetch_related

        Args:
            relations: Контейнер с relations
            matched_relation: Сматченные relations

        """
        is_prefetch = matched_relation.related_type == RelatedTypes.PREFETCH_RELATED

        # Добавляем строковый select_related
        if not is_prefetch:
            relations.select_related.add(matched_relation.field_name)

        # Добавляем строковый prefetch_related
        if not matched_relation.related_dto:
            if is_prefetch:
                relations.prefetch_related.add(matched_relation.field_name)
            return

        # Получаем вложенные select_related и prefetch_related
        nested_relations = cls._collect_relations(matched_relation.related_model, matched_relation.related_dto)

        # Добавляем комбинированный prefetch_related
        if is_prefetch:
            return relations.prefetch_related.add(
                cls.prefetch_class(
                    lookup=matched_relation.field_name,
                    queryset=(
                        matched_relation.related_model.objects.select_related(
                            *nested_relations.select_related
                        ).prefetch_related(*nested_relations.prefetch_related)
                    ),
                )
            )

        # Добавляем строковый select_related для вложенных relations
        for nested_relation in nested_relations.select_related:
            relations.select_related.add(f"{matched_relation.field_name}__{nested_relation}")

        # Добавляем prefetch_related для вложенных relations
        for nested_relation in nested_relations.prefetch_related:
            if not isinstance(nested_relation, cls.prefetch_class):
                # Добавляем строковый prefetch_related
                relations.prefetch_related.add(f"{matched_relation.field_name}__{nested_relation}")
                continue

            relations.prefetch_related.add(
                # Добавляем комбинированный prefetch_related
                cls.prefetch_class(
                    lookup=f"{matched_relation.field_name}__{nested_relation.prefetch_to}",
                    queryset=nested_relation.queryset,
                )
            )

    @classmethod
    def _collect_relations(cls, model: type[Model], dto: type[DTO]):
        """Рекурсивно собирает select_related и prefetch_related

        Args:
            model: Модель ORM
            dto: Целевое DTO

        Returns:
            Relations
        """
        matched_relations = cls._match_relations(model, dto)
        relations = Relations()
        for matched_relation in matched_relations:
            cls._add_relations(relations, matched_relation)

        return relations

    def get_objects(self, model: type[Model]) -> Manager:
        base_manager = self._get_base_manager(model)

        if model not in self._models_dtos:
            return base_manager

        dto = self._models_dtos[model]
        relations = self._models_dtos_related.get((model, dto), Relations())
        if relations.select_related:
            base_manager = base_manager.select_related(*relations.select_related)
        if relations.prefetch_related:
            base_manager = base_manager.prefetch_related(*relations.prefetch_related)

        return base_manager

    @property
    def objects(self) -> Manager:
        return self.extend_objects(self.get_objects(self.model))

    def extend_objects(self, objects) -> Manager:
        return objects

    @classmethod
    @abstractmethod
    def _match_relations(cls, model: type[Model], dto: type[DTO]) -> list[MatchedRelation]:
        """Сматчить relations между моделью ORM и DTO

        Args:
            model: Модель ORM
            dto: Целевое DTO

        Returns:
            Список MatchedRelation
        """
