from django.contrib import admin

from contrib.mixins.admin import NameMixin, CreatedDatetimeMixin, ExtendableAdmin

from .models import OrderStatus, OrderItem, Order


class OrderStatusAdmin(NameMixin, ExtendableAdmin):
    ...


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(CreatedDatetimeMixin, ExtendableAdmin):
    search_fields = [
        "id",
        "delivery_address",
    ]
    list_filter = [
        "status",
    ]

    list_display = [
        "id",
        "status",
        "total",
        "delivery_address",
        "delivery_time",
        "additional_info",
        "created_at",
    ]

    readonly_fields = ["total", "delivery_address", "delivery_time", "additional_info", "hash"]

    inlines = [OrderItemInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(Order, OrderAdmin)
