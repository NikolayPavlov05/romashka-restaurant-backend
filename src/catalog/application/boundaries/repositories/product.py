from __future__ import annotations

from abc import ABC

from contrib.clean_architecture.providers.repositories.interfaces import (
    IRepository,
    ISearchRepositoryMixin, IRetrieveRepositoryMixin,
)


class IProductRepository(ISearchRepositoryMixin, IRetrieveRepositoryMixin, IRepository, ABC):
    """Репозиторий товара."""
