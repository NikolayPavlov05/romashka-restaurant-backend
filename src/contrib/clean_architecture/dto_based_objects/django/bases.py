"""Модуль с реализацией DTO based objects для django

Classes:
    DjangoDTOBasedObjectsMixin: Миксин для django для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model
    DjangoM2MManager: Класс для управления зависимостями m2m

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from contrib.clean_architecture.dto_based_objects.bases import BaseDTOBasedObjectsMixin
from contrib.clean_architecture.dto_based_objects.dtos import MatchedRelation
from contrib.clean_architecture.dto_based_objects.enums import RelatedTypes
from contrib.clean_architecture.interfaces import IM2MManager
from contrib.pydantic.model import PydanticModel
from django.db.models import Model
from django.db.models import Prefetch
from django.db.models import QuerySet
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.db.models.fields.related_descriptors import ForwardOneToOneDescriptor
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor

if TYPE_CHECKING:
    from django.db.models.manager import ManyToManyRelatedManager

    from contrib.clean_architecture.dto_based_objects.dtos import M2MUpdateAction
    from contrib.clean_architecture.interfaces import DTO, M2MManager


class DjangoDTOBasedObjectsMixin(BaseDTOBasedObjectsMixin, required_attrs_base=True):
    """Миксин для django для автоматического присоединения зависимостей для запроса в бд на основании DTO и Model"""

    _select_related_descriptor_classes = (
        ForwardOneToOneDescriptor,
        ReverseOneToOneDescriptor,
        ForwardManyToOneDescriptor,
    )
    _prefetch_related_descriptor_classes = (
        ReverseManyToOneDescriptor,
        ManyToManyDescriptor,
    )

    prefetch_class = Prefetch
    sequence_classes = (QuerySet,)
    model: type[Model]

    @classmethod
    def _match_relations(cls, model: type[Model], dto: type[DTO]):
        # Получаем поля модели
        model_fields = {field.name: field.related_model for field in model._meta.get_fields()}

        # Получаем поля dto
        dto_fields = {field_name: cls._extract_annotation(field) for field_name, field in dto.model_fields.items()}

        # Матчим relations
        matched_relations = []
        for field_name in dto_fields:
            # Если нет поля, пропускаем
            model_field_descriptor = getattr(model, field_name, None)
            if not model_field_descriptor:
                continue

            # Определяем тип relation
            related_type = None
            if isinstance(model_field_descriptor, cls._select_related_descriptor_classes):
                related_type = RelatedTypes.SELECT_RELATED
            elif isinstance(model_field_descriptor, cls._prefetch_related_descriptor_classes):
                related_type = RelatedTypes.PREFETCH_RELATED

            if not related_type:
                continue

            # Ищем вложенные /зависимые dto
            related_dto = dto_fields[field_name] if issubclass(dto_fields[field_name], PydanticModel) else None

            # Добавляем relation
            matched_relations.append(
                MatchedRelation(
                    field_name=field_name,
                    related_type=related_type,
                    related_model=model_fields[field_name],
                    related_dto=related_dto,
                )
            )

        return matched_relations

    @property
    def m2m_manager(self) -> type[M2MManager]:
        return DjangoM2MManager


class DjangoM2MManager(IM2MManager):
    """Класс для управления зависимостями m2m"""

    @classmethod
    def execute(cls, instance: Model, field: str, actions: list[M2MUpdateAction]) -> None:
        """

        Args:
            instance: Экземпляр модели ORM
            field: название атрибута дескриптора поля
            actions: список действий к выполнению

        """
        relation: ManyToManyRelatedManager = getattr(instance, field)

        add_actions = filter(lambda a: not a.delete, actions)
        if add_actions:
            relation.add(*[action.id for action in add_actions])

        delete_actions = filter(lambda a: a.delete, actions)
        if delete_actions:
            relation.remove(*[action.id for action in delete_actions])
