from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooRetrieveController
from contrib.clean_architecture.tests.test_controllers.functional.mixins import (
    ListTestMixin,
)


class TestRetrieveController(ListTestMixin):
    def test_retrieve(
        self,
        create_controller: FooCreateController,
        retrieve_controller: FooRetrieveController,
    ):
        self._prepare(create_controller)
        self._test_result(retrieve_controller.retrieve(paginated=False))
        retrieve_controller.interactor.repository.objects.clear()

    def test_retrieve_paginated(
        self,
        create_controller: FooCreateController,
        retrieve_controller: FooRetrieveController,
    ):
        self._prepare(create_controller)
        self._test_paginated_result(retrieve_controller.retrieve())
        retrieve_controller.interactor.repository.objects.clear()
