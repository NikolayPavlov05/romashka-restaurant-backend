from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooSearchController
from contrib.clean_architecture.tests.test_controllers.functional.mixins import (
    ListTestMixin,
)


class TestSearchController(ListTestMixin):
    def test_search(
        self,
        create_controller: FooCreateController,
        search_controller: FooSearchController,
    ):
        self._prepare(create_controller)
        self._test_result(search_controller.search("", paginated=False))
        search_controller.interactor.repository.objects.clear()

    def test_search_paginated(
        self,
        create_controller: FooCreateController,
        search_controller: FooSearchController,
    ):
        self._prepare(create_controller)
        self._test_paginated_result(search_controller.search(""))
        search_controller.interactor.repository.objects.clear()
