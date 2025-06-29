from __future__ import annotations

from contrib.clean_architecture.providers.controllers.bases import Controller, CreateControllerMixin, \
    RetrieveControllerMixin

from contrib.module_manager import Depend

from order.application.interactors import OrderInteractor


class OrderController(CreateControllerMixin, RetrieveControllerMixin, Controller):

    interactor: Depend[OrderInteractor]
