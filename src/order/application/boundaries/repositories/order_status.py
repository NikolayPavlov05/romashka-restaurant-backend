from __future__ import annotations

from abc import ABC

from contrib.clean_architecture.providers.repositories.interfaces import (
    IRepository,
    IDetailRepositoryMixin,
)


class IOrderStatusRepository(IDetailRepositoryMixin, IRepository, ABC):
    """Репозиторий статуса заказа."""
