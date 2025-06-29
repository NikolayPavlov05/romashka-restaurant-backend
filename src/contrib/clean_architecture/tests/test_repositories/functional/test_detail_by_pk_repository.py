from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByPKRepository


class TestDetailByPKRepository:
    def test_detail_by_pk(
        self,
        create_repository: FooCreateRepository,
        detail_by_pk_repository: FooDetailByPKRepository,
    ):
        object_id = create_repository.create()
        instance = detail_by_pk_repository.detail_by_pk(object_id)

        assert instance.id == object_id
        detail_by_pk_repository.objects.clear()
