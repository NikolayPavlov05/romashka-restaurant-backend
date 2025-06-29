from __future__ import annotations

from catalog.application.domain.entities import ProductEntity
from contrib.pydantic.model import PydanticModel, NestedEntity


class OrderStatusEntity(PydanticModel, proxy_model=True):
    """Статус заказа."""


class OrderEntity(PydanticModel, proxy_model=True):
    """Заказ."""

    class _OrderItemEntity(PydanticModel, proxy_model=True):
        product = NestedEntity(ProductEntity)

    items = NestedEntity(_OrderItemEntity, multiple=True)
    status = NestedEntity(OrderStatusEntity)


class OrderItemEntity(PydanticModel, proxy_model=True):
    """Позиция заказа."""

    order = NestedEntity(OrderEntity)
    product = NestedEntity(ProductEntity)
