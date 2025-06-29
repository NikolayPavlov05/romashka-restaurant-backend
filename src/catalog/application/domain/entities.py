from __future__ import annotations

from contrib.pydantic.model import PydanticModel, NestedEntity

from django.conf import settings


class CategoryEntity(PydanticModel, proxy_model=True):
    """Категория."""


class ProductEntity(PydanticModel, proxy_model=True):
    """Товар."""

    category = NestedEntity(CategoryEntity)

    @property
    def image_url(self) -> str:
        return f"{settings.PROJECT_URL}{self.image.url}" if self.image else ""
