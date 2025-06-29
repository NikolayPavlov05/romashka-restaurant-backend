from __future__ import annotations

from pydantic import Field
from decimal import Decimal

from contrib.mixins.pydantic_model import IdMixin, NameMixin, DescriptionMixin

from django.utils.translation import gettext as _

from contrib.pydantic.model import SearchQueryDTO


class ProductSearchDTO(SearchQueryDTO):
    category_id: int | None = Field(title=_("ID категории"), default=None)


class ProductInfoDTO(IdMixin, NameMixin, DescriptionMixin, response_model=True, with_paginated=True):

    price: Decimal = Field(title=_("Цена"))
    currency: str = Field(title=_("Валюта"), default="RUB")
    image_url: str = Field(title=_("Изображение URL"))
