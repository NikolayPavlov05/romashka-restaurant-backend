from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooSearchInteractor
from contrib.clean_architecture.tests.test_interactors.functional.mixins import (
    ListTestMixin,
)


class TestSearchInteractor(ListTestMixin):
    @staticmethod
    def _prepare(create_interactor):
        create_interactor.repository.objects.clear()
        create_interactor.create(FooDTO())
        create_interactor.create(FooDTO())

    def test_search(
        self,
        create_interactor: FooCreateInteractor,
        search_interactor: FooSearchInteractor,
    ):
        self._prepare(create_interactor)
        self._test_result(search_interactor.search("", paginated=False), FooDTO)
        search_interactor.repository.objects.clear()

    def test_search_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        search_interactor: FooSearchInteractor,
    ):
        self._prepare(create_interactor)
        self._test_result(search_interactor.search("", paginated=False, return_type=BarDTO), BarDTO)
        search_interactor.repository.objects.clear()

    def test_search_paginated(
        self,
        create_interactor: FooCreateInteractor,
        search_interactor: FooSearchInteractor,
    ):
        self._prepare(create_interactor)
        self._test_paginated_result(search_interactor.search("", paginated=True), FooDTO)
        search_interactor.repository.objects.clear()

    def test_search_paginated_with_return_type(
        self,
        create_interactor: FooCreateInteractor,
        search_interactor: FooSearchInteractor,
    ):
        self._prepare(create_interactor)
        self._test_paginated_result(
            search_interactor.search(
                "",
                paginated=True,
                return_type=BarDTO,
                return_pagination_type=BarDTO.paginated,
            ),
            BarDTO,
        )
        search_interactor.repository.objects.clear()
