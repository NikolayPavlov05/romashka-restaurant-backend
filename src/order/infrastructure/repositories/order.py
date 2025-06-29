from __future__ import annotations

from order.application.boundaries.repositories import IOrderRepository
from contrib.clean_architecture.providers.repositories.bases import RetrieveRepositoryMixin, CreateRepositoryMixin, DetailByPKRepositoryMixin
from contrib.clean_architecture.providers.repositories.django.bases import DjangoRepository

from order.models import Order
from order.application.domain.entities import OrderEntity


class OrderRepository(
    IOrderRepository, DetailByPKRepositoryMixin, RetrieveRepositoryMixin, CreateRepositoryMixin, DjangoRepository
):
    """Репозиторий заказа."""

    entity = OrderEntity
    model = Order
