from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooExistsRepository
from contrib.pydantic.model import PydanticModel


class TestExistsRepository:
    class _FilterDTO(PydanticModel):
        id: int | None

    def test_exists_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        exists_repository: FooExistsRepository,
    ):
        object_id = create_repository.create()
        filter_dto = self._FilterDTO(id=object_id)
        assert exists_repository.exists(filter_dto=filter_dto) is True

        exists_repository.objects.clear()

    def test_exists_with_filters(
        self,
        create_repository: FooCreateRepository,
        exists_repository: FooExistsRepository,
    ):
        object_id = create_repository.create()
        assert exists_repository.exists(id=object_id) is True

        exists_repository.objects.clear()

    def test_does_not_exists_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        exists_repository: FooExistsRepository,
    ):
        filter_dto = self._FilterDTO(id=None)
        assert exists_repository.exists(filter_dto=filter_dto) is False

        exists_repository.objects.clear()

    def test_does_not_exists_with_filters(
        self,
        create_repository: FooCreateRepository,
        exists_repository: FooExistsRepository,
    ):
        assert exists_repository.exists(id=None) is False

        exists_repository.objects.clear()
