"""Модуль с DTO репозиториев

Classes:
    Relations: Набор relations для запроса
    MatchedRelation: Cматченные параметры relations
    M2MUpdateAction: Действие над m2m полем

"""
from __future__ import annotations

from contrib.clean_architecture.dto_based_objects.enums import RelatedTypes
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.interfaces import Model
from contrib.pydantic.model import PydanticModel
from pydantic import Field


class Relations(PydanticModel):
    """Набор relations для запроса"""

    select_related: set = Field(default_factory=set)
    prefetch_related: set = Field(default_factory=set)


class MatchedRelation(PydanticModel):
    """Cматченные параметры relations"""

    field_name: str
    related_type: RelatedTypes
    related_model: type[Model]
    related_dto: type[DTO] | None = None


class M2MUpdateAction(PydanticModel):
    """Действие над m2m полем"""

    id: int
    delete: bool = Field(default=False)
