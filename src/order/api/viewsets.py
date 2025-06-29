from __future__ import annotations

from contrib.module_manager import Depend
from contrib.clean_architecture.views.bases import CleanViewSet, CreateCleanViewSetMixin, RetrieveCleanViewSetMixin

from order.application.controllers import OrderController
from order.application.boundaries.dtos.order import OrderCreateDTO, OrderFilterDTO, OrderInfoDTO, OrderCreateResultDTO


class OrderViewSet(CreateCleanViewSetMixin, RetrieveCleanViewSetMixin, CleanViewSet, injects=("order", "catalog",)):

    controller: Depend[OrderController]
    permission_classes = []

    create_request_model = OrderCreateDTO
    create_response_model = OrderCreateResultDTO

    retrieve_request_model = OrderFilterDTO
    retrieve_paginated = False
    retrieve_return_type = OrderInfoDTO
    retrieve_return_pagination_type = OrderInfoDTO.paginated
