from __future__ import annotations

from abc import ABC

from contrib.clean_architecture.providers.repositories.interfaces import (
    IRepository,
    IRetrieveRepositoryMixin,
)


class ICategoryRepository(IRetrieveRepositoryMixin, IRepository, ABC):
    """Репозиторий категория."""
