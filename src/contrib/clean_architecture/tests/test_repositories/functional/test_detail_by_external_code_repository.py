from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByExternalCodeRepository
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType


class TestDetailByExternalCodeRepository:
    def test_detail_by_external_code(
        self,
        create_repository: FooCreateRepository,
        detail_by_external_code_repository: FooDetailByExternalCodeRepository,
    ):
        object_id = create_repository.create(external_code="test", external_code_type=FakeExternalCodeType.FAKE)
        instance = detail_by_external_code_repository.detail_by_external_code("test", FakeExternalCodeType.FAKE)

        assert instance.id == object_id
        detail_by_external_code_repository.objects.clear()
        detail_by_external_code_repository.external_code_model.objects.clear()
