from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooBulkDeleteRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository


class TestBulkDeleteRepository:
    def test_bulk_delete(
        self,
        create_repository: FooCreateRepository,
        bulk_delete_repository: FooBulkDeleteRepository,
    ):
        object_id = create_repository.create()
        object_id_2 = create_repository.create()

        instance_count_before = bulk_delete_repository.objects.count()
        bulk_delete_repository.bulk_delete([object_id, object_id_2])
        instance_count_after = bulk_delete_repository.objects.count()
        assert instance_count_before - 2 == instance_count_after

        bulk_delete_repository.objects.clear()
