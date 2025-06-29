from __future__ import annotations

from contrib.pydantic.model import PydanticModel
from pydantic import Field


class FooDTOWithRelations(PydanticModel):
    class _FooRelation(PydanticModel):
        class _FooNestedRelation(PydanticModel):
            foo_field: int = 1

        foo_nested_select_relation: _FooNestedRelation = Field(default_factory=_FooNestedRelation)
        foo_nested_prefetch_relation: list[_FooNestedRelation] = Field(default_factory=list)

    foo_select_relation: _FooRelation = Field(default_factory=_FooRelation)
    foo_prefetch_relation: list[_FooRelation] = Field(default_factory=list)

    foo_from_extra_layer_field: int = Field(default=0)


class BarDTOWithRelations(PydanticModel):
    class _BarRelation(PydanticModel):
        bar_field: int = 1

    bar_select_relation: _BarRelation = Field(default_factory=_BarRelation)
