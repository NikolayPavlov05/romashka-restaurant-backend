from __future__ import annotations

from catalog.application.interactors import ProductInteractor
from contrib.clean_architecture.providers.controllers.bases import Controller, SearchControllerMixin
from contrib.module_manager import Depend


class ProductController(SearchControllerMixin, Controller):
    interactor: Depend[ProductInteractor]
