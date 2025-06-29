from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailByPKController


class TestDetailByPkController:
    def test_detail_by_pk(
        self,
        create_controller: FooCreateController,
        detail_by_pk_controller: FooDetailByPKController,
    ):
        object_id = create_controller.create(FooDTO())

        instance = detail_by_pk_controller.detail_by_pk(object_id)
        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_by_pk_controller.interactor.repository.objects.clear()
