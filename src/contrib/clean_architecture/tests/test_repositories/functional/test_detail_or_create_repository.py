from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.models import FooModel
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailOrCreateRepository
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestDetailOrCreateRepository:
    def test_detail(
        self,
        create_repository: FooCreateRepository,
        detail_or_create_repository: FooDetailOrCreateRepository,
    ):
        created_object_id = create_repository.create(foo_field1="created")
        detailed_object, created = detail_or_create_repository.detail_or_create(
            id=created_object_id, defaults={"foo_field1": "updated"}
        )

        assert created_object_id == detailed_object.pk
        assert created is False
        assert detailed_object.foo_field1 == "created"

    def test_detail_with_user_context(
        self,
        create_repository: FooCreateRepository,
        detail_or_create_repository: FooDetailOrCreateRepository,
        creator: FooUserModel,
        updater: FooUserModel,
    ):
        set_user_context(creator)
        object_id = create_repository.create()
        set_user_context(updater)
        detailed_object, _ = detail_or_create_repository.detail_or_create(id=object_id)

        assert detailed_object.created_by.id == creator.id
        assert detailed_object.updated_by.id == creator.id
        detail_or_create_repository.objects.clear()
        creator.objects.clear()
        clear_context()

    def test_detail_from_external_code(
        self,
        create_repository: FooCreateRepository,
        detail_or_create_repository: FooDetailOrCreateRepository,
    ):
        created_object_id = create_repository.create(external_code="test", external_code_type=FakeExternalCodeType.FAKE)
        detailed_object, created = detail_or_create_repository.detail_or_create(
            id=created_object_id,
            external_code="test",
            external_code_type=FakeExternalCodeType.FAKE,
            from_external_code=True,
        )
        assert created_object_id == detailed_object.id
        assert created is False

        instance = detail_or_create_repository.external_code_model.objects.get_object(
            "test", FakeExternalCodeType.FAKE, FooModel
        )
        assert instance.id == detailed_object.id
        detail_or_create_repository.objects.clear()
        detail_or_create_repository.external_code_model.objects.clear()

    def test_create(self, detail_or_create_repository: FooDetailOrCreateRepository):
        instance_count_before = detail_or_create_repository.objects.count()
        _, created = detail_or_create_repository.detail_or_create(defaults={"foo_field1": "created"})
        instance_count_after = detail_or_create_repository.objects.count()

        assert created is True
        assert instance_count_before + 1 == instance_count_after
        assert detail_or_create_repository.objects.last().foo_field1 == "created"
        detail_or_create_repository.objects.clear()

    def test_create_with_user_context(
        self,
        detail_or_create_repository: FooDetailOrCreateRepository,
        creator: FooUserModel,
    ):
        set_user_context(creator)
        instance_count_before = detail_or_create_repository.objects.count()
        detail_or_create_repository.detail_or_create()
        instance_count_after = detail_or_create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = detail_or_create_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == creator.id
        detail_or_create_repository.objects.clear()
        creator.objects.clear()
        clear_context()

    def test_create_from_external_code(self, detail_or_create_repository: FooDetailOrCreateRepository):
        detailed_object, created = detail_or_create_repository.detail_or_create(
            external_code="test",
            external_code_type=FakeExternalCodeType.FAKE,
            from_external_code=True,
        )

        assert created is True
        instance = detail_or_create_repository.external_code_model.objects.get_object(
            "test", FakeExternalCodeType.FAKE, FooModel
        )
        assert instance.id == detailed_object.id
        detail_or_create_repository.objects.clear()
        detail_or_create_repository.external_code_model.objects.clear()
