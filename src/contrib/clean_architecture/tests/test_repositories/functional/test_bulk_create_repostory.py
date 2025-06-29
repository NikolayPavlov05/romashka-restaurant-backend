from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import (
    FooBulkCreateRepository,
)
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestBulkCreateRepository:
    def test_bulk_create_with_kwargs(self, bulk_create_repository: FooBulkCreateRepository):
        instance_count_before = bulk_create_repository.objects.count()
        bulk_create_repository.bulk_create([FooEntity(), FooEntity()], foo_field1="create_with_kwargs")
        instance_count_after = bulk_create_repository.objects.count()

        assert instance_count_before + 2 == instance_count_after

        assert bulk_create_repository.objects.last().foo_field1 == "create_with_kwargs"
        assert bulk_create_repository.objects.first().foo_field1 == "create_with_kwargs"
        bulk_create_repository.objects.clear()

    def test_bulk_create_with_entity_and_kwargs(self, bulk_create_repository: FooBulkCreateRepository):
        instance_count_before = bulk_create_repository.objects.count()
        bulk_create_repository.bulk_create(
            [
                FooEntity(foo_field1="create_with_entity"),
                FooEntity(foo_field1="create_with_entity"),
            ],
            foo_field2="create_with_kwargs",
        )
        instance_count_after = bulk_create_repository.objects.count()

        assert instance_count_before + 2 == instance_count_after

        assert bulk_create_repository.objects.last().foo_field1 == "create_with_entity"
        assert bulk_create_repository.objects.last().foo_field2 == "create_with_kwargs"
        assert bulk_create_repository.objects.first().foo_field1 == "create_with_entity"
        assert bulk_create_repository.objects.first().foo_field2 == "create_with_kwargs"
        bulk_create_repository.objects.clear()

    def test_bulk_create_with_user_context(
        self, bulk_create_repository: FooBulkCreateRepository, creator: FooUserModel
    ):
        set_user_context(creator)
        instance_count_before = bulk_create_repository.objects.count()
        bulk_create_repository.bulk_create([FooEntity(id=1), FooEntity(id=2)])
        instance_count_after = bulk_create_repository.objects.count()

        assert instance_count_before + 2 == instance_count_after

        assert bulk_create_repository.objects.last().created_by.id == creator.id
        assert bulk_create_repository.objects.last().updated_by.id == creator.id
        assert bulk_create_repository.objects.first().created_by.id == creator.id
        assert bulk_create_repository.objects.first().updated_by.id == creator.id
        bulk_create_repository.objects.clear()
        creator.objects.clear()
        clear_context()
