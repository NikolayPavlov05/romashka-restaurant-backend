from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailByExternalCodeController
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType


class TestDetailByExternalCodeController:
    def test_detail_by_external_code(
        self,
        create_controller: FooCreateController,
        detail_by_external_code_controller: FooDetailByExternalCodeController,
    ):
        object_id = create_controller.create(
            FooDTO(), external_code="test", external_code_type=FakeExternalCodeType.FAKE
        )
        instance = detail_by_external_code_controller.detail_by_external_code("test", FakeExternalCodeType.FAKE)

        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_by_external_code_controller.interactor.repository.objects.clear()
        detail_by_external_code_controller.interactor.repository.external_code_model.objects.clear()
