from __future__ import annotations

from order.application.boundaries.repositories import IOrderStatusRepository
from contrib.clean_architecture.providers.repositories.bases import DetailRepositoryMixin
from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository

from order.models import OrderStatus
from order.application.domain.entities import OrderStatusEntity


class OrderStatusRepository(IOrderStatusRepository, DetailRepositoryMixin, DjangoRepository):
    """Репозиторий статуса заказа."""

    entity = OrderStatusEntity
    model = OrderStatus
