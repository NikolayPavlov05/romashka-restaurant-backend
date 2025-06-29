from __future__ import annotations

from typing import ClassVar

from contrib.clean_architecture.tests.fakes.general.managers import FakeManager
from contrib.clean_architecture.tests.fakes.general.models import FakeModel
from pydantic import Field


class FooModelWithRelations(FakeModel):
    class _FooRelation(FakeModel):
        class _FooNestedRelation(FakeModel):
            foo_field: int = 1

        foo_nested_select_relation: _FooNestedRelation = Field(default_factory=_FooNestedRelation)
        foo_nested_prefetch_relation: list[_FooNestedRelation] = Field(default_factory=list)

        foo_nested_missed_select_relation: _FooNestedRelation = Field(default_factory=_FooNestedRelation)
        foo_nested_missed_prefetch_relation: list[_FooNestedRelation] = Field(default_factory=list)

    other_manager: ClassVar[FakeManager] = FakeManager()

    foo_select_relation: _FooRelation = Field(default_factory=_FooRelation)
    foo_prefetch_relation: list[_FooRelation] = Field(default_factory=list)

    foo_missed_select_relation: _FooRelation = Field(default_factory=_FooRelation)
    foo_missed_prefetch_relation: list[_FooRelation] = Field(default_factory=list)


class BarModelWithRelations(FakeModel):
    class _BarRelation(FakeModel):
        bar_field: int = 1

    other_manager: ClassVar[FakeManager] = FakeManager()

    bar_select_relation: _BarRelation = Field(default_factory=_BarRelation)
