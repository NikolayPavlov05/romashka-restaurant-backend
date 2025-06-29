from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDeleteRepository


class TestDeleteRepository:
    def test_delete(
        self,
        create_repository: FooCreateRepository,
        delete_repository: FooDeleteRepository,
    ):
        object_id = create_repository.create()

        instance_count_before = delete_repository.objects.count()
        delete_repository.delete(object_id)
        instance_count_after = delete_repository.objects.count()
        assert instance_count_before - 1 == instance_count_after

        delete_repository.objects.clear()
