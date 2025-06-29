from django.db import models

from django.utils.translation import gettext_lazy as l_

from contrib.mixins.model import NameMixin, CreatedDatetimeMixin


class OrderStatus(NameMixin):
    """Статус заказа."""

    id: int

    is_default = models.BooleanField(
        verbose_name=l_("Стандартный"),
        default=False,
    )
    is_completed = models.BooleanField(
        verbose_name=l_("Заказ выполнен"),
        default=False,
    )

    class Meta:
        verbose_name = l_("Статус заказа")
        verbose_name_plural = l_("Статусы заказа")

    def __str__(self) -> str:
        return self.name


class Order(CreatedDatetimeMixin):
    """Заказ."""

    id: int

    status = models.ForeignKey(
        OrderStatus,
        verbose_name=l_("Статус"),
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    hash = models.CharField(
        verbose_name=l_("Хэш"),
        max_length=32,
        blank=False,
        null=False,
    )
    total = models.DecimalField(
        verbose_name=l_("Итог"),
        decimal_places=2,
        max_digits=14,
    )
    delivery_address = models.CharField(
        verbose_name=l_("Адрес доставки"),
        max_length=255,
        blank=False,
        default="",
    )
    delivery_time = models.CharField(
        verbose_name=l_("Время доставки"),
        max_length=255,
        blank=False,
        default="",
    )
    additional_info = models.CharField(
        verbose_name=l_("Пожелания"),
        max_length=255,
        blank=False,
        default="",
    )

    class Meta:
        verbose_name = l_("Заказ")
        verbose_name_plural = l_("Заказ")

    def __str__(self) -> str:
        return f"Заказ №{self.id}"


class OrderItem(models.Model):
    """Позиция заказа."""

    id: int

    order = models.ForeignKey(
        Order,
        verbose_name=l_("Заказ"),
        on_delete=models.CASCADE,
        related_name="items",
        null=False,
        blank=False,
    )
    product = models.ForeignKey(
        "catalog.Product",
        verbose_name=l_("Товар"),
        on_delete=models.CASCADE,
        related_name="order_items",
        null=False,
        blank=False,
    )
    count = models.IntegerField(
        verbose_name=l_("Кол-во"),
        default=0,
    )
    price = models.DecimalField(
        verbose_name=l_("Цена"),
        decimal_places=2,
        max_digits=12,
    )

    class Meta:
        verbose_name = l_("Позиция заказа")
        verbose_name_plural = l_("Позиции заказа")

    def __str__(self) -> str:
        return f"{self.product.name}. Кол-во {self.count}. Цена {self.price}"
