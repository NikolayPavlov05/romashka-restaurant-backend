from __future__ import annotations

from pydantic import Field
from decimal import Decimal

from contrib.mixins.pydantic_model import IdMixin, CreatedDatetimeMixin
from contrib.pydantic.model import PydanticModel, FilterQueryDTO

from .order_status import OrderStatusInfoDTO
from .order_item import OrderItemInfoDTO, OrderItemCreateDTO

from django.utils.translation import gettext as _


class OrderInfoDTO(IdMixin, CreatedDatetimeMixin, response_model=True):

    status: OrderStatusInfoDTO = Field(title=_("Статус"))
    items: list[OrderItemInfoDTO] = Field(title=_("Позиции"))
    total: Decimal = Field(title=_("Итоговая цена"))
    hash: str = Field(title=_("Хэш"))
    delivery_address: str = Field(title=_("Адрес доставки"))
    delivery_time: str = Field(title=_("Время доставки"))
    additional_info: str = Field(title=_("Дополнительная информация"))


class OrderCreateDTO(PydanticModel):

    items: list[OrderItemCreateDTO] = Field(title=_("Позиции"), default_factory=list)
    delivery_address: str = Field(title=_("Адрес доставки"))
    delivery_time: str = Field(title=_("Время доставки"))
    additional_info: str = Field(title=_("Дополнительная информация"))


class OrderFilterDTO(FilterQueryDTO):
    hash__in: list[str] | str = Field(title=_("Спишек хэшей"))


class OrderCreateResultDTO(PydanticModel, response_model=True):

    hash: str = Field(title=_("Хэш заказа"))
