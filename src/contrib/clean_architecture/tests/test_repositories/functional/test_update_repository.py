from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooUpdateRepository
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestUpdateRepository:
    def test_update_with_entity(
        self,
        create_repository: FooCreateRepository,
        update_repository: FooUpdateRepository,
    ):
        object_id = create_repository.create()
        entity = FooEntity(id=object_id, foo_field1="update_with_entity")
        update_repository.update(entity)

        assert update_repository.objects.last().foo_field1 == "update_with_entity"
        update_repository.objects.clear()

    def test_update_with_kwargs(
        self,
        create_repository: FooCreateRepository,
        update_repository: FooUpdateRepository,
    ):
        object_id = create_repository.create()
        update_repository.update(id=object_id, foo_field1="update_with_kwargs")

        assert update_repository.objects.last().foo_field1 == "update_with_kwargs"
        update_repository.objects.clear()

    def test_update_with_entity_and_kwargs(
        self,
        create_repository: FooCreateRepository,
        update_repository: FooUpdateRepository,
    ):
        object_id = create_repository.create()
        entity = FooEntity(foo_field1="update_with_entity")
        update_repository.update(entity, id=object_id, foo_field2="update_with_kwargs")

        instance = update_repository.objects.last()
        assert instance.foo_field1 == "update_with_entity"
        assert instance.foo_field2 == "update_with_kwargs"
        update_repository.objects.clear()

    def test_update_with_user_context(
        self,
        create_repository: FooCreateRepository,
        update_repository: FooUpdateRepository,
        creator: FooUserModel,
        updater: FooUserModel,
    ):
        set_user_context(creator)
        object_id = create_repository.create()
        set_user_context(updater)
        update_repository.update(id=object_id)

        assert creator.id != updater.id
        instance = update_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == updater.id
        update_repository.objects.clear()
        creator.objects.clear()
        clear_context()
