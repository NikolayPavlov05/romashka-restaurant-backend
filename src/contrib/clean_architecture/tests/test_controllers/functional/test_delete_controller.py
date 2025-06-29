from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDeleteController


class TestDeleteController:
    def test_delete(
        self,
        create_controller: FooCreateController,
        delete_controller: FooDeleteController,
    ):
        object_id = create_controller.create(FooDTO())

        instance_count_before = delete_controller.interactor.repository.objects.count()
        delete_controller.delete(object_id)
        instance_count_after = delete_controller.interactor.repository.objects.count()

        assert instance_count_before - 1 == instance_count_after
        delete_controller.interactor.repository.objects.clear()
