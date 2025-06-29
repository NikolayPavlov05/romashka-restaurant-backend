from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByPKInteractor


class TestDetailByPkInteractor:
    def test_detail_by_pk(
        self,
        create_interactor: FooCreateInteractor,
        detail_by_pk_interactor: FooDetailByPKInteractor,
    ):
        object_id = create_interactor.create(FooDTO())

        instance = detail_by_pk_interactor.detail_by_pk(object_id)
        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_by_pk_interactor.repository.objects.clear()

    def test_detail_by_pk_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        detail_by_pk_interactor: FooDetailByPKInteractor,
    ):
        object_id = create_interactor.create(FooDTO())

        instance = detail_by_pk_interactor.detail_by_pk(object_id, return_type=BarDTO)
        assert isinstance(instance, BarDTO)
        assert instance.id == object_id
        detail_by_pk_interactor.repository.objects.clear()
