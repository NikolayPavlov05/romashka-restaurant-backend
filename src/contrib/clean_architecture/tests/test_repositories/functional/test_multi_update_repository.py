from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooMultiUpdateRepository
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestBulkUpdateRepository:
    def test_multi_update_with_entity(
        self,
        create_repository: FooCreateRepository,
        multi_update_repository: FooMultiUpdateRepository,
    ):
        object_id = create_repository.create()
        entity = FooEntity(foo_field1="update_with_entity")
        multi_update_repository.multi_update(entity, id=object_id)

        assert multi_update_repository.objects.last().foo_field1 == "update_with_entity"
        multi_update_repository.objects.clear()

    def test_multi_update_with_user_context(
        self,
        create_repository: FooCreateRepository,
        multi_update_repository: FooMultiUpdateRepository,
        creator: FooUserModel,
        updater: FooUserModel,
    ):
        set_user_context(creator)
        object_id = create_repository.create()
        set_user_context(updater)
        entity = FooEntity(foo_field1="update_with_entity")
        multi_update_repository.multi_update(entity, id=object_id)

        assert creator.id != updater.id
        instance = multi_update_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == updater.id
        multi_update_repository.objects.clear()
        creator.objects.clear()
        clear_context()
