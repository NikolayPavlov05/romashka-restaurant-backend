from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByExternalCodeInteractor
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType


class TestDetailByExternalCodeInteractor:
    def test_detail_by_external_code(
        self,
        create_interactor: FooCreateInteractor,
        detail_by_external_code_interactor: FooDetailByExternalCodeInteractor,
    ):
        object_id = create_interactor.create(
            FooDTO(), external_code="test", external_code_type=FakeExternalCodeType.FAKE
        )
        instance = detail_by_external_code_interactor.detail_by_external_code("test", FakeExternalCodeType.FAKE)

        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_by_external_code_interactor.repository.objects.clear()
        detail_by_external_code_interactor.repository.external_code_model.objects.clear()

    def test_detail_by_external_code_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        detail_by_external_code_interactor: FooDetailByExternalCodeInteractor,
    ):
        object_id = create_interactor.create(
            FooDTO(), external_code="test", external_code_type=FakeExternalCodeType.FAKE
        )
        instance = detail_by_external_code_interactor.detail_by_external_code(
            "test", FakeExternalCodeType.FAKE, return_type=BarDTO
        )

        assert isinstance(instance, BarDTO)
        assert instance.id == object_id
        detail_by_external_code_interactor.repository.objects.clear()
        detail_by_external_code_interactor.repository.external_code_model.objects.clear()
