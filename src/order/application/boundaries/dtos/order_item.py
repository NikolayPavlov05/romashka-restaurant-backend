from __future__ import annotations

from pydantic import Field

from decimal import Decimal

from contrib.mixins.pydantic_model import IdMixin

from catalog.application.boundaries.dtos import ProductInfoDTO

from django.utils.translation import gettext as _

from contrib.pydantic.model import PydanticModel


class OrderItemInfoDTO(IdMixin, response_model=True):

    product: ProductInfoDTO = Field(title=_("Товар"))
    price: Decimal = Field(title=_("Цена"))
    count: int = Field(title=_("Кол-во"))


class OrderItemCreateDTO(PydanticModel):

    product_id: int = Field(title=_("ID товара"))
    count: int = Field(title=_("Кол-во"))
