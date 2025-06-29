from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailInteractor


class TestDetailInteractor:
    def test_detail(
        self,
        create_interactor: FooCreateInteractor,
        detail_interactor: FooDetailInteractor,
    ):
        object_id = create_interactor.create(FooDTO())

        instance = detail_interactor.detail(id=object_id)
        assert isinstance(instance, FooDTO)
        assert instance.id == object_id
        detail_interactor.repository.objects.clear()

    def test_detail_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        detail_interactor: FooDetailInteractor,
    ):
        object_id = create_interactor.create(FooDTO())

        instance = detail_interactor.detail(return_type=BarDTO, id=object_id)
        assert isinstance(instance, BarDTO)
        assert instance.id == object_id
        detail_interactor.repository.objects.clear()
