from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooRetrieveInteractor
from contrib.clean_architecture.tests.test_interactors.functional.mixins import (
    ListTestMixin,
)


class TestRetrieveInteractor(ListTestMixin):
    def test_retrieve(
        self,
        create_interactor: FooCreateInteractor,
        retrieve_interactor: FooRetrieveInteractor,
    ):
        self._prepare(create_interactor)
        self._test_result(retrieve_interactor.retrieve(paginated=False), FooDTO)
        retrieve_interactor.repository.objects.clear()

    def test_retrieve_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        retrieve_interactor: FooRetrieveInteractor,
    ):
        self._prepare(create_interactor)
        self._test_result(retrieve_interactor.retrieve(paginated=False, return_type=BarDTO), BarDTO)
        retrieve_interactor.repository.objects.clear()

    def test_retrieve_paginated(
        self,
        create_interactor: FooCreateInteractor,
        retrieve_interactor: FooRetrieveInteractor,
    ):
        self._prepare(create_interactor)
        self._test_paginated_result(retrieve_interactor.retrieve(paginated=True), FooDTO)
        retrieve_interactor.repository.objects.clear()

    def test_retrieve_paginated_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        retrieve_interactor: FooRetrieveInteractor,
    ):
        self._prepare(create_interactor)
        self._test_paginated_result(
            retrieve_interactor.retrieve(
                paginated=True,
                return_type=BarDTO,
                return_pagination_type=BarDTO.paginated,
            ),
            BarDTO,
        )
        retrieve_interactor.repository.objects.clear()
