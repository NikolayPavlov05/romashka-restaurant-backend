from __future__ import annotations

from contrib.clean_architecture.providers.controllers.bases import Controller
from contrib.clean_architecture.providers.controllers.bases import CreateControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DeleteControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailByExternalCodeControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailByPKControllerMixin
from contrib.clean_architecture.providers.controllers.bases import DetailControllerMixin
from contrib.clean_architecture.providers.controllers.bases import PatchListControllerMixin
from contrib.clean_architecture.providers.controllers.bases import RetrieveControllerMixin
from contrib.clean_architecture.providers.controllers.bases import SearchControllerMixin
from contrib.clean_architecture.providers.controllers.bases import UpdateControllerMixin
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDeleteInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByExternalCodeInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByPKInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooPatchListInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooRetrieveInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooSearchInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooUpdateInteractor


class FooCreateController(CreateControllerMixin, Controller):
    interactor: FooCreateInteractor


class FooUpdateController(UpdateControllerMixin, Controller):
    interactor: FooUpdateInteractor


class FooDeleteController(DeleteControllerMixin, Controller):
    interactor: FooDeleteInteractor


class FooDetailController(DetailControllerMixin, Controller):
    interactor: FooDetailInteractor


class FooDetailByPKController(DetailByPKControllerMixin, Controller):
    interactor: FooDetailByPKInteractor


class FooDetailByExternalCodeController(DetailByExternalCodeControllerMixin, Controller):
    interactor: FooDetailByExternalCodeInteractor


class FooRetrieveController(RetrieveControllerMixin, Controller):
    interactor: FooRetrieveInteractor


class FooSearchController(SearchControllerMixin, Controller):
    repository: FooSearchInteractor


class FooPatchListController(PatchListControllerMixin, Controller):
    interactor: FooPatchListInteractor
