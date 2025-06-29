from __future__ import annotations

from catalog.application.interactors import CategoryInteractor
from contrib.clean_architecture.providers.controllers.bases import Controller, RetrieveControllerMixin
from contrib.module_manager import Depend


class CategoryController(RetrieveControllerMixin, Controller):
    interactor: Depend[CategoryInteractor]
