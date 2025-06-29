from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooUpdateController


class TestUpdateController:
    def test_update(
        self,
        create_controller: FooCreateController,
        update_controller: FooUpdateController,
    ):
        created_object_id = create_controller.create(FooDTO(foo_field1="created"))
        updates_object_id = update_controller.update(created_object_id, FooDTO(foo_field1="updated"))

        assert created_object_id == updates_object_id
        instance = create_controller.interactor.repository.objects.last()
        assert instance.foo_field1 == "updated"
        assert instance.id == updates_object_id
        update_controller.interactor.repository.objects.clear()
