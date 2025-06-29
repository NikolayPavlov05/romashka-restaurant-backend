from __future__ import annotations

from contrib.module_manager import Depend
from contrib.clean_architecture.views.bases import CleanViewSet, RetrieveCleanViewSetMixin, SearchCleanViewSetMixin

from catalog.application.controllers import CategoryController, ProductController
from catalog.application.boundaries.dtos.category import CategoryInfoDTO
from catalog.application.boundaries.dtos.product import ProductSearchDTO, ProductInfoDTO


class CategoryViewSet(RetrieveCleanViewSetMixin, CleanViewSet, injects=("catalog",)):

    controller: Depend[CategoryController]
    permission_classes = []

    retrieve_paginated = False
    retrieve_return_type = CategoryInfoDTO
    retrieve_return_pagination_type = CategoryInfoDTO.paginated
    retrieve_controller_extra_kwargs = {"is_active": True}


class ProductViewSet(SearchCleanViewSetMixin, CleanViewSet, injects=("catalog",)):

    controller: Depend[ProductController]
    permission_classes = []

    search_paginated = False
    search_return_type = ProductInfoDTO
    search_return_pagination_type = ProductInfoDTO.paginated
    search_request_model = ProductSearchDTO
    search_controller_extra_kwargs = {"is_active": True}
