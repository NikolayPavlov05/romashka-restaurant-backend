from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import FooBulkUpdateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByPKRepository
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestBulkCreateRepository:
    def test_bulk_update_with_kwargs(
        self,
        bulk_update_repository: FooBulkUpdateRepository,
        create_repository: FooCreateRepository,
        detail_by_pk_repository: FooDetailByPKRepository,
    ):
        object_id = create_repository.create()
        entity = FooEntity(id=object_id)

        object2_id = create_repository.create()
        entity2 = FooEntity(id=object2_id)

        bulk_update_repository.bulk_update([entity, entity2], foo_field2="update_with_entity3")

        instance1 = detail_by_pk_repository.detail_by_pk(object_id)
        instance2 = detail_by_pk_repository.detail_by_pk(object2_id)

        assert instance1.foo_field2 == "update_with_entity3"
        assert instance2.foo_field2 == "update_with_entity3"

    def test_bulk_create_with_entity_and_kwargs(
        self,
        bulk_update_repository: FooBulkUpdateRepository,
        create_repository: FooCreateRepository,
        detail_by_pk_repository: FooDetailByPKRepository,
    ):
        object_id = create_repository.create()
        entity = FooEntity(id=object_id, foo_field1="update_with_entity1")

        object2_id = create_repository.create()
        entity2 = FooEntity(id=object2_id, foo_field1="update_with_entity2")

        bulk_update_repository.bulk_update([entity, entity2], foo_field2="update_with_entity3")

        instance1 = detail_by_pk_repository.detail_by_pk(object_id)
        instance2 = detail_by_pk_repository.detail_by_pk(object2_id)

        assert instance1.foo_field1 == "update_with_entity1"
        assert instance1.foo_field2 == "update_with_entity3"

        assert instance2.foo_field1 == "update_with_entity2"
        assert instance1.foo_field2 == "update_with_entity3"

    def test_bulk_create_with_user_context(
        self,
        creator: FooUserModel,
        bulk_update_repository: FooBulkUpdateRepository,
        create_repository: FooCreateRepository,
        detail_by_pk_repository: FooDetailByPKRepository,
    ):
        set_user_context(creator)
        object_id = create_repository.create()
        entity = FooEntity(id=object_id, foo_field1="update_with_entity1")
        bulk_update_repository.bulk_update([entity])

        instance = detail_by_pk_repository.detail_by_pk(object_id)
        assert instance.updated_by.id == creator.id
        clear_context()
