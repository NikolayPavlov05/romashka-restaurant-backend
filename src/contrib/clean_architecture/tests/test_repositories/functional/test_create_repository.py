from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooModel
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.repositories import (
    FooCreateRepository,
)
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import set_user_context


class TestCreateRepository:
    def test_create(self, create_repository: FooCreateRepository):
        instance_count_before = create_repository.objects.count()
        create_repository.create()
        instance_count_after = create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        create_repository.objects.clear()

    def test_create_with_entity(self, create_repository: FooCreateRepository):
        instance_count_before = create_repository.objects.count()
        entity = FooEntity(foo_field1="create_with_entity")
        create_repository.create(entity)
        instance_count_after = create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        assert create_repository.objects.last().foo_field1 == "create_with_entity"
        create_repository.objects.clear()

    def test_create_with_kwargs(self, create_repository: FooCreateRepository):
        instance_count_before = create_repository.objects.count()
        create_repository.create(foo_field1="create_with_kwargs")
        instance_count_after = create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        assert create_repository.objects.last().foo_field1 == "create_with_kwargs"
        create_repository.objects.clear()

    def test_create_with_entity_and_kwargs(self, create_repository: FooCreateRepository):
        instance_count_before = create_repository.objects.count()
        entity = FooEntity(foo_field1="create_with_entity")
        create_repository.create(entity, foo_field2="create_with_kwargs")
        instance_count_after = create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = create_repository.objects.last()
        assert instance.foo_field1 == "create_with_entity"
        assert instance.foo_field2 == "create_with_kwargs"
        create_repository.objects.clear()

    def test_create_with_external_code(self, create_repository: FooCreateRepository):
        instance_count_before = create_repository.objects.count()
        external_code_instance_count_before = create_repository.external_code_model.objects.count()
        object_id = create_repository.create(external_code="test", external_code_type=FakeExternalCodeType.FAKE)
        instance_count_after = create_repository.objects.count()
        external_code_instance_count_after = create_repository.external_code_model.objects.count()
        assert instance_count_before + 1 == instance_count_after
        assert external_code_instance_count_before + 1 == external_code_instance_count_after

        instance = create_repository.external_code_model.objects.get_object("test", FakeExternalCodeType.FAKE, FooModel)
        assert instance.id == object_id
        create_repository.objects.clear()
        create_repository.external_code_model.objects.clear()

    def test_create_with_user_context(self, create_repository: FooCreateRepository, creator: FooUserModel):
        set_user_context(creator)
        instance_count_before = create_repository.objects.count()
        create_repository.create()
        instance_count_after = create_repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = create_repository.objects.last()
        assert instance.created_by.id == creator.id
        assert instance.updated_by.id == creator.id
        create_repository.objects.clear()
        creator.objects.clear()
        clear_context()
