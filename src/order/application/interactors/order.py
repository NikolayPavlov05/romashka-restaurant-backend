from __future__ import annotations

import string
import random

from contrib.clean_architecture.providers.interactors.bases import Interactor, RetrieveInteractorMixin

from contrib.module_manager import Depend
from order.application.boundaries.dtos import OrderCreateDTO, OrderCreateResultDTO

from order.application.boundaries.repositories import IOrderRepository, IOrderItemRepository, IOrderStatusRepository
from catalog.application.boundaries.repositories import IProductRepository

from order.application.domain.entities import OrderItemEntity, OrderEntity


class OrderInteractor(RetrieveInteractorMixin, Interactor):

    repository: Depend[IOrderRepository]
    status_repository: Depend[IOrderStatusRepository]
    order_item_repository: Depend[IOrderItemRepository]
    product_repository: Depend[IProductRepository]

    def create(self, dto: OrderCreateDTO, *args, **kwargs) -> int:

        products = self.product_repository.retrieve()
        items: list[dict] = []
        total = 0

        for item in dto.items:
            product = [_product for _product in products if _product.id == item.product_id]
            if product:
                total_price = product[0].price * item.count
                total += total_price
                items.append(
                    dict(
                        product_id=item.product_id,
                        count=item.count,
                        price=total_price,
                    )
                )

        default_status = self.status_repository.detail(is_default=True)

        hash = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        orders_count: int = self.repository.count()

        order_id: int = self.repository.create(
            OrderEntity(
                status_id=default_status.id,
                hash=f"{orders_count+1}:{hash}",
                total=total,
                delivery_address=dto.delivery_address,
                delivery_time=dto.delivery_time,
                additional_info=dto.additional_info,
            )
        )
        self.order_item_repository.bulk_create(
            [OrderItemEntity(**item, order_id=order_id) for item in items],
        )

        order = self.repository.detail_by_pk(order_id)

        return OrderCreateResultDTO(hash=order.hash)
