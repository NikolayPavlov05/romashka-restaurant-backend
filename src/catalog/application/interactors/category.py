from __future__ import annotations

from contrib.clean_architecture.providers.interactors.bases import Interactor, RetrieveInteractorMixin

from contrib.module_manager import Depend

from catalog.application.boundaries.repositories import ICategoryRepository


class CategoryInteractor(RetrieveInteractorMixin, Interactor):

    repository: Depend[ICategoryRepository]
