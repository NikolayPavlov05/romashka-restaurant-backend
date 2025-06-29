from __future__ import annotations

from order.application.boundaries.repositories import IOrderItemRepository
from contrib.clean_architecture.providers.repositories.bases import RetrieveRepositoryMixin, BulkCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository

from order.models import OrderItem
from order.application.domain.entities import OrderItemEntity


class OrderItemRepository(IOrderItemRepository, RetrieveRepositoryMixin, BulkCreateRepositoryMixin, DjangoRepository):
    """Репозиторий позиции заказа."""

    entity = OrderItemEntity
    model = OrderItem
