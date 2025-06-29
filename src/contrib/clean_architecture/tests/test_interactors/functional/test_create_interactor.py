from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import (
    FooCreateInteractor,
)


class TestCreateInteractor:
    def test_create(self, create_interactor: FooCreateInteractor):
        instance_count_before = create_interactor.repository.objects.count()
        object_id = create_interactor.create(FooDTO(foo_field1="created"))
        instance_count_after = create_interactor.repository.objects.count()

        assert instance_count_before + 1 == instance_count_after
        instance = create_interactor.repository.objects.last()
        assert instance.foo_field1 == "created"
        assert instance.id == object_id
        create_interactor.repository.objects.clear()
