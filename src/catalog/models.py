from django.db import models

from django.utils.translation import gettext_lazy as l_

from contrib.mixins.model import NameMixin, DescriptionMixin, IsActiveMixin


class Category(NameMixin, IsActiveMixin):
    """Категория."""

    id: int

    class Meta:
        verbose_name = l_("Категория")
        verbose_name_plural = l_("Категория")

    def __str__(self) -> str:
        return self.name


class Product(NameMixin, DescriptionMixin, IsActiveMixin):
    """Товар."""

    id: int

    category = models.ForeignKey(
        Category,
        verbose_name=l_("Категория"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    image = models.ImageField(
        verbose_name=l_("Изображение"),
        upload_to='product'
    )
    price = models.DecimalField(
        verbose_name=l_("Цена"),
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        verbose_name = l_("Товар")
        verbose_name_plural = l_("Товары")

    def __str__(self) -> str:
        return self.name
