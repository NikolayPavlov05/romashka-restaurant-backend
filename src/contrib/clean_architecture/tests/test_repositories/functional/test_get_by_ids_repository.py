from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooGetBetIdsRepository
from contrib.pydantic.model import PydanticModel


class TestGetByIdsRepository:
    def test_get_by_ids(
        self,
        get_by_ids_repository: FooGetBetIdsRepository,
        create_repository: FooCreateRepository,
    ) -> None:
        """Тестируем метод get_by_ids."""
        entity = FooEntity(foo_field1="create_with_entity")
        create_repository.create(entity)

        result: list[PydanticModel] = get_by_ids_repository.get_by_ids([create_repository.objects.last().id])

        assert result is not None
        assert result.count() == 1
        assert result[0].id == create_repository.objects.last().id
