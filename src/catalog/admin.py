from django.contrib import admin

from contrib.mixins.admin import NameMixin, DescriptionMixin, ExtendableAdmin, IsActiveMixin

from .models import Product, Category


class CategoryAdmin(NameMixin, IsActiveMixin, ExtendableAdmin):

    def has_delete_permission(self, request, obj = ...):
        return False


class ProductAdmin(NameMixin, DescriptionMixin, IsActiveMixin, ExtendableAdmin):

    def has_delete_permission(self, request, obj = ...):
        return False



admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
