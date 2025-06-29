from __future__ import annotations

from contrib.clean_architecture.dto_based_objects.utils import convert_return
from contrib.clean_architecture.dto_based_objects.utils import ConvertPath
from contrib.clean_architecture.tests.factories.dto_based_objects.entities import (
    FooExtraLayer,
)
from contrib.clean_architecture.tests.factories.dto_based_objects.models import (
    FooModelWithRelations,
)
from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.fakes.dto_based_objects.bases import (
    FakeDTOBasedObjectsMixin,
)


class FooDTOBasedObjects(FakeDTOBasedObjectsMixin):
    model = FooModelWithRelations

    @convert_return(FooModelWithRelations, FooEntity)
    def foo_convert_return_method(self):
        return self.objects.create()

    @convert_return(FooModelWithRelations, FooEntity, FooExtraLayer)
    def foo_convert_return_with_extra_layer_method(self):
        return self.objects.create()

    @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath(0))
    def foo_convert_return_with_convert_path_index_method(self):
        return [self.objects.create()]

    @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath(0, 0))
    def foo_convert_return_few_with_index_convert_path_method(self):
        return [[self.objects.create()]]

    @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath("attr"))
    def foo_convert_return_with_attr_convert_path_method(self):
        return {"attr": self.objects.create()}

    @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath("attr1", "attr2"))
    def foo_convert_return_with_few_attr_convert_path_method(self):
        return {"attr1": {"attr2": self.objects.create()}}

    @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath(0, "attr"))
    def foo_convert_return_with_mixed_convert_path_mixed_method(self):
        return [{"attr": self.objects.create()}]
