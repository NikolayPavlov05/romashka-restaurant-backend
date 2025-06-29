from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import (
    FooCreateController,
)


class TestCreateController:
    def test_create(self, create_controller: FooCreateController):
        instance_count_before = create_controller.interactor.repository.objects.count()
        object_id = create_controller.create(FooDTO(foo_field1="created"))
        instance_count_after = create_controller.interactor.repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = create_controller.interactor.repository.objects.last()
        assert instance.foo_field1 == "created"
        assert instance.id == object_id
        create_controller.interactor.repository.objects.clear()
