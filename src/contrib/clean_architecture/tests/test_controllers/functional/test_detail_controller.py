from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailController


class TestDetailController:
    def test_detail(
        self,
        create_controller: FooCreateController,
        detail_controller: FooDetailController,
    ):
        object_id = create_controller.create(FooDTO())

        instance = detail_controller.detail(id=object_id)
        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_controller.interactor.repository.objects.clear()
