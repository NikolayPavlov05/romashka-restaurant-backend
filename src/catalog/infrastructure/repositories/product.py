from __future__ import annotations

from catalog.application.boundaries.repositories import IProductRepository
from contrib.clean_architecture.providers.repositories.bases import SearchRepositoryMixin, RetrieveRepositoryMixin
from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository

from catalog.models import Product
from catalog.application.domain.entities import ProductEntity


class ProductRepository(IProductRepository, RetrieveRepositoryMixin, SearchRepositoryMixin, DjangoRepository):
    """Репозиторий товара."""

    entity = ProductEntity
    model = Product

    search_expressions = ["name", "description"]
