from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooUpdateInteractor


class TestUpdateInteractor:
    def test_update(
        self,
        create_interactor: FooCreateInteractor,
        update_interactor: FooUpdateInteractor,
    ):
        created_object_id = create_interactor.create(FooDTO(foo_field1="created"))
        updates_object_id = update_interactor.update(created_object_id, FooDTO(foo_field1="updated"))

        assert created_object_id == updates_object_id
        instance = create_interactor.repository.objects.last()
        assert instance.foo_field1 == "updated"
        assert instance.id == updates_object_id
        update_interactor.repository.objects.clear()
