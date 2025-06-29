from __future__ import annotations

from contrib.clean_architecture.tests.factories.dto_based_objects.dto_based_objects import (
    FooDTOBasedObjects,
)
from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import (
    FooDTOWithRelations,
)
from contrib.clean_architecture.tests.factories.dto_based_objects.models import (
    FooModelWithRelations,
)


class TestConvertReturn:
    @staticmethod
    def _test_convert_return(instance, dto_based_objects):
        assert isinstance(instance, FooDTOWithRelations)
        assert instance.foo_prefetch_relation == []
        assert isinstance(instance.foo_select_relation, FooDTOWithRelations._FooRelation)
        assert instance.foo_select_relation.foo_nested_prefetch_relation == []

        assert len(dto_based_objects.objects.all()) == 1
        FooModelWithRelations.objects.clear()
        assert len(dto_based_objects.objects.all()) == 0

    def test_convert_return(self, dto_based_objects: FooDTOBasedObjects):
        instance = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_method()
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_with_extra_layer(self, dto_based_objects: FooDTOBasedObjects):
        instance = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_method()
        assert instance.foo_from_extra_layer_field == 0
        self._test_convert_return(instance, dto_based_objects)
        instance = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_with_extra_layer_method()
        assert instance.foo_from_extra_layer_field == 1
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_with_convert_path_index(self, dto_based_objects: FooDTOBasedObjects):
        result = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_with_convert_path_index_method()
        instance = result[0]
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_few_with_index_convert_path(self, dto_based_objects: FooDTOBasedObjects):
        result = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_few_with_index_convert_path_method()
        instance = result[0][0]
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_with_attr_convert_path(self, dto_based_objects: FooDTOBasedObjects):
        result = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_with_attr_convert_path_method()
        instance = result["attr"]
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_with_few_attr_convert_path(self, dto_based_objects: FooDTOBasedObjects):
        result = dto_based_objects.with_dto(FooDTOWithRelations).foo_convert_return_with_few_attr_convert_path_method()
        instance = result["attr1"]["attr2"]
        self._test_convert_return(instance, dto_based_objects)

    def test_convert_return_with_mixed_convert_path_mixed(self, dto_based_objects: FooDTOBasedObjects):
        result = dto_based_objects.with_dto(
            FooDTOWithRelations
        ).foo_convert_return_with_mixed_convert_path_mixed_method()
        instance = result[0]["attr"]
        self._test_convert_return(instance, dto_based_objects)
