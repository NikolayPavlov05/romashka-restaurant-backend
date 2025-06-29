from __future__ import annotations

from abc import ABC

from contrib.clean_architecture.providers.repositories.interfaces import (
    IRepository,
    IRetrieveRepositoryMixin,
    IBulkCreateRepositoryMixin,
)


class IOrderItemRepository(IRetrieveRepositoryMixin, IBulkCreateRepositoryMixin, IRepository, ABC):
    """Репозиторий товара заказа."""
