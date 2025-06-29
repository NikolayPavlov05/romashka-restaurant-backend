from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.models import FooModel
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooUpdateOrCreateRepository
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestUpdateOrCreateRepository:
    def test_update(
        self,
        create_repository: FooCreateRepository,
        update_or_create_repository: FooUpdateOrCreateRepository,
    ):
        created_object_id = create_repository.create(foo_field1="created")
        updated_object_id, created = update_or_create_repository.update_or_create(
            id=created_object_id, defaults={"foo_field1": "updated"}
        )

        assert created_object_id == updated_object_id
        assert created is False
        assert update_or_create_repository.objects.last().foo_field1 == "updated"
        update_or_create_repository.objects.clear()

    def test_update_with_user_context(
        self,
        create_repository: FooCreateRepository,
        update_or_create_repository: FooUpdateOrCreateRepository,
        creator: FooUserModel,
        updater: FooUserModel,
    ):
        set_user_context(creator)
        object_id = create_repository.create()
        set_user_context(updater)
        update_or_create_repository.update_or_create(id=object_id)

        assert creator.id != updater.id
        instance = update_or_create_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == updater.id
        update_or_create_repository.objects.clear()
        creator.objects.clear()
        clear_context()

    def test_update_from_external_code(
        self,
        create_repository: FooCreateRepository,
        update_or_create_repository: FooUpdateOrCreateRepository,
    ):
        created_object_id = create_repository.create(external_code="test", external_code_type=FakeExternalCodeType.FAKE)
        updated_object_id, created = update_or_create_repository.update_or_create(
            id=created_object_id,
            defaults={"foo_field1": "updated"},
            external_code="test",
            external_code_type=FakeExternalCodeType.FAKE,
            from_external_code=True,
        )
        assert created_object_id == updated_object_id
        assert created is False

        instance = update_or_create_repository.external_code_model.objects.get_object(
            "test", FakeExternalCodeType.FAKE, FooModel
        )
        assert instance.id == updated_object_id
        update_or_create_repository.objects.clear()
        update_or_create_repository.external_code_model.objects.clear()

    def test_create(self, update_or_create_repository: FooUpdateOrCreateRepository):
        instance_count_before = update_or_create_repository.objects.count()
        _, created = update_or_create_repository.update_or_create(defaults={"foo_field1": "created"})
        instance_count_after = update_or_create_repository.objects.count()

        assert created is True
        assert instance_count_before + 1 == instance_count_after
        assert update_or_create_repository.objects.last().foo_field1 == "created"
        update_or_create_repository.objects.clear()

    def test_create_with_user_context(
        self,
        update_or_create_repository: FooUpdateOrCreateRepository,
        creator: FooUserModel,
    ):
        set_user_context(creator)
        instance_count_before = update_or_create_repository.objects.count()
        update_or_create_repository.update_or_create()
        instance_count_after = update_or_create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = update_or_create_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == creator.id
        update_or_create_repository.objects.clear()
        creator.objects.clear()
        clear_context()
