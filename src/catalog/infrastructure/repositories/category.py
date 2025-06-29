from __future__ import annotations

from catalog.application.boundaries.repositories import ICategoryRepository
from contrib.clean_architecture.providers.repositories.bases import RetrieveRepositoryMixin
from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository

from catalog.models import Category
from catalog.application.domain.entities import CategoryEntity


class CategoryRepository(ICategoryRepository, RetrieveRepositoryMixin, DjangoRepository):
    """Репозиторий категории."""

    entity = CategoryEntity
    model = Category
