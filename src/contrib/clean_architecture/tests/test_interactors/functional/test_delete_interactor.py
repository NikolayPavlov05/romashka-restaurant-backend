from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDeleteInteractor


class TestDeleteInteractor:
    def test_delete(
        self,
        create_interactor: FooCreateInteractor,
        delete_interactor: FooDeleteInteractor,
    ):
        object_id = create_interactor.create(FooDTO())

        instance_count_before = delete_interactor.repository.objects.count()
        delete_interactor.delete(object_id)
        instance_count_after = delete_interactor.repository.objects.count()

        assert instance_count_before - 1 == instance_count_after
        delete_interactor.repository.objects.clear()
