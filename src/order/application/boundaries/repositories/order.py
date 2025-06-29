from __future__ import annotations

from abc import ABC

from contrib.clean_architecture.providers.repositories.interfaces import (
    IRepository,
    IRetrieveRepositoryMixin,
    ICreateRepositoryMixin,
    IDetailByPKRepositoryMixin,
)


class IOrderRepository(IDetailByPKRepositoryMixin, IRetrieveRepositoryMixin, ICreateRepositoryMixin, IRepository, ABC):
    """Репозиторий заказа."""
