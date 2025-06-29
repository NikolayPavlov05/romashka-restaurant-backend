from __future__ import annotations

from contrib.clean_architecture.tests.factories.dto_based_objects.dto_based_objects import (
    FooDTOBasedObjects,
)
from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import BarDTOWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import FooDTOWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.models import BarModelWithRelations
from contrib.clean_architecture.tests.factories.dto_based_objects.models import FooModelWithRelations


class TestGetObjects:
    def test_get_objects(self, dto_based_objects: FooDTOBasedObjects):
        FooModelWithRelations.objects.create()
        dto_based_objects.with_dto(FooDTOWithRelations)
        assert len(dto_based_objects.objects.all()) == 1
        FooModelWithRelations.objects.clear()
        assert len(dto_based_objects.objects.all()) == 0

    def test_get_objects_from_other_manager(self, dto_based_objects: FooDTOBasedObjects):
        FooModelWithRelations.objects.create()
        dto_based_objects.with_dto(FooDTOWithRelations, manager_attr="other_manager")

        assert dto_based_objects._models_managers_attrs[FooModelWithRelations] == "other_manager"
        assert len(dto_based_objects.objects.all()) == 1
        FooModelWithRelations.objects.clear()
        assert len(dto_based_objects.objects.all()) == 0

    def test_get_other_objects(self, dto_based_objects: FooDTOBasedObjects):
        BarModelWithRelations.objects.create()
        dto_based_objects.with_dto(FooDTOWithRelations, other_dtos={BarModelWithRelations: BarDTOWithRelations})

        assert len(dto_based_objects.get_objects(BarModelWithRelations).all()) == 1
        BarModelWithRelations.objects.clear()
        assert len(dto_based_objects.get_objects(BarModelWithRelations).all()) == 0

    def test_get_other_objects_from_other_manager(self, dto_based_objects: FooDTOBasedObjects):
        BarModelWithRelations.objects.create()
        dto_based_objects.with_dto(
            FooDTOWithRelations,
            other_dtos={BarModelWithRelations: BarDTOWithRelations},
            other_managers_attrs={BarModelWithRelations: "other_manager"},
        )

        assert dto_based_objects._models_managers_attrs[BarModelWithRelations] == "other_manager"
        assert len(dto_based_objects.get_objects(BarModelWithRelations).all()) == 1
        BarModelWithRelations.objects.clear()
        assert len(dto_based_objects.get_objects(BarModelWithRelations).all()) == 0
