from __future__ import annotations

from contrib.clean_architecture.tests.factories.dto_based_objects.dto_based_objects import (
    FooDTOBasedObjects,
)
from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import BarDTOWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import FooDTOWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.models import BarModelWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.models import FooModelWithRelations


class TestWithDTO:
    def test_clean_with_dto_context(self, dto_based_objects: FooDTOBasedObjects):
        dto_based_objects.with_dto(FooDTOWithRelations)
        dto_based_objects.clean_with_dto_context()
        assert dto_based_objects._models_managers_attrs == {}
        assert dto_based_objects._models_dtos_related == {}
        assert dto_based_objects._models_dtos == {}
        assert dto_based_objects._extra_select_related == {}
        assert dto_based_objects._extra_prefetch_related == {}

    def test_with_dto_relations(self, dto_based_objects: FooDTOBasedObjects):
        dto_based_objects.with_dto(FooDTOWithRelations)

        relations = dto_based_objects._models_dtos_related[(FooModelWithRelations, FooDTOWithRelations)]
        select_related = relations.select_related
        assert len(select_related) == 2
        assert "foo_select_relation" in select_related
        assert "foo_select_relation__foo_nested_select_relation" in select_related

        prefetch_related = relations.prefetch_related
        assert len(prefetch_related) == 2

        foo_prefetch_relation = next(
            filter(
                lambda relation: relation.prefetch_to == "foo_prefetch_relation",
                prefetch_related,
            )
        )
        assert len(foo_prefetch_relation.queryset._query.select_related) == 1
        assert len(foo_prefetch_relation.queryset._prefetch_related_lookups) == 1
        assert "foo_nested_select_relation" in foo_prefetch_relation.queryset._query.select_related
        assert foo_prefetch_relation.queryset._query.select_related["foo_nested_select_relation"] == {}
        assert foo_prefetch_relation.queryset._prefetch_related_lookups[0].prefetch_to == "foo_nested_prefetch_relation"
        assert foo_prefetch_relation.queryset._prefetch_related_lookups[0].queryset._query.select_related == {}
        assert foo_prefetch_relation.queryset._prefetch_related_lookups[0].queryset._prefetch_related_lookups == ()

        foo_nested_prefetch_relation = next(
            filter(
                lambda relation: relation.prefetch_to == "foo_select_relation__foo_nested_prefetch_relation",
                prefetch_related,
            )
        )
        assert foo_nested_prefetch_relation.queryset._prefetch_related_lookups == ()
        assert foo_nested_prefetch_relation.queryset._query.select_related == {}

    def test_with_dto_extra(self, dto_based_objects: FooDTOBasedObjects):
        dto_based_objects.with_dto(
            FooDTOWithRelations,
            extra_select_related={"extra_select_related"},
            extra_prefetch_related={"extra_prefetch_related"},
        )

        relations = dto_based_objects._models_dtos_related[(FooModelWithRelations, FooDTOWithRelations)]
        select_related = relations.select_related
        assert "extra_select_related" in select_related
        assert len(select_related) == 3

        prefetch_related = relations.prefetch_related
        assert "extra_prefetch_related" in prefetch_related
        assert len(prefetch_related) == 3

    def test_with_dto_other_dtos(self, dto_based_objects):
        dto_based_objects.with_dto(FooDTOWithRelations, other_dtos={BarModelWithRelations: BarDTOWithRelations})

        assert FooModelWithRelations in dto_based_objects._models_dtos
        assert (
            FooModelWithRelations,
            FooDTOWithRelations,
        ) in dto_based_objects._models_dtos_related
        assert (
            FooModelWithRelations,
            FooDTOWithRelations,
        ) in dto_based_objects._extra_select_related
        assert (
            FooModelWithRelations,
            FooDTOWithRelations,
        ) in dto_based_objects._extra_prefetch_related

        assert BarModelWithRelations in dto_based_objects._models_dtos
        assert (
            BarModelWithRelations,
            BarDTOWithRelations,
        ) in dto_based_objects._models_dtos_related
        assert (
            BarModelWithRelations,
            BarDTOWithRelations,
        ) in dto_based_objects._extra_select_related
        assert (
            BarModelWithRelations,
            BarDTOWithRelations,
        ) in dto_based_objects._extra_prefetch_related

        relations = dto_based_objects._models_dtos_related[(BarModelWithRelations, BarDTOWithRelations)]
        assert len(relations.select_related) == 1
        assert "bar_select_relation" in relations.select_related

    def test_with_dto_other_extra(self, dto_based_objects):
        dto_based_objects.with_dto(
            FooDTOWithRelations,
            other_dtos={BarModelWithRelations: BarDTOWithRelations},
            other_extra_select_related={BarModelWithRelations: {"extra_select_related"}},
            other_extra_prefetch_related={BarModelWithRelations: {"extra_prefetch_related"}},
        )

        relations = dto_based_objects._models_dtos_related[(BarModelWithRelations, BarDTOWithRelations)]
        assert len(relations.select_related) == 2
        assert "extra_select_related" in relations.select_related
        assert len(relations.prefetch_related) == 1
        assert "extra_prefetch_related" in relations.prefetch_related
