from __future__ import annotations

from contrib.clean_architecture.providers.interactors.bases import Interactor, SearchInteractorMixin

from contrib.module_manager import Depend

from catalog.application.boundaries.repositories import IProductRepository


class ProductInteractor(SearchInteractorMixin, Interactor):

    repository: Depend[IProductRepository]
