from __future__ import annotations

from contrib.clean_architecture.types import mixin_for
from contrib.subclass_control.mixins import ExtendedAttrsMixin
from django.contrib import admin


class ExtendableAdmin(ExtendedAttrsMixin, admin.ModelAdmin):
    ordering = ()
    extended_attrs = {
        "raw_id_fields",
        "autocomplete_fields",
        "search_fields",
        "fields",
        "readonly_fields",
        "exclude",
        "fieldsets",
        "list_display",
        "list_display_links",
        "list_filter",
        "list_editable",
        "radio_fields",
        "prepopulated_fields",
        "filter_vertical",
        "filter_horizontal",
        "formfield_overrides",
        "inlines",
        "actions",
        "ordering",
    }

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs["exclude"] = [*kwargs.get("exclude", []), *self.readonly_fields]
        return super().get_form(request, obj, change=change, **kwargs)


class IdMixin(mixin_for(ExtendableAdmin)):
    list_display = ["id"]
    readonly_fields = ["id"]
    search_fields = ["id"]


class NameMixin(mixin_for(ExtendableAdmin)):
    search_fields = ["name"]


class HashMixin(mixin_for(ExtendableAdmin)):
    search_fields = ["hash"]


class DescriptionMixin(mixin_for(ExtendableAdmin)):
    list_display = ["description"]


class IsActiveMixin(mixin_for(ExtendableAdmin)):
    list_display = ["is_active"]


class ProtectedMixin(mixin_for(ExtendableAdmin)):
    readonly_fields = ["protected"]


class ExtraDataMixin(mixin_for(ExtendableAdmin)):
    pass


class DictionaryMixin(DescriptionMixin, NameMixin, mixin_for(ExtendableAdmin)):
    pass


class CreatedDatetimeMixin(mixin_for(ExtendableAdmin)):
    readonly_fields = ["created_at"]


class UpdatedDatetimeMixin(mixin_for(ExtendableAdmin)):
    readonly_fields = ["updated_at"]


class CreatedUpdatedDatetimeMixin(CreatedDatetimeMixin, UpdatedDatetimeMixin, mixin_for(ExtendableAdmin)):
    pass


class AuthoredObjectMixin(mixin_for(admin.ModelAdmin)):
    creator_field: str = None
    updater_field: str = None

    def get_form(self, request, obj=None, change=False, **kwargs):
        if change and self.creator_field:
            kwargs["exclude"] = kwargs.get("exclude", []) + [self.creator_field]
        if change and self.updater_field:
            kwargs["exclude"] = kwargs.get("exclude", []) + [self.updater_field]
        return super().get_form(request, obj, change=change, **kwargs)

    def save_form(self, request, form, change):
        if not change and self.creator_field:
            setattr(form.instance, self.creator_field, request.user)
        if self.updater_field:
            setattr(form.instance, self.updater_field, request.user)
        return super().save_form(request, form, change)


class CreatedUserMixin(AuthoredObjectMixin, mixin_for(ExtendableAdmin)):
    creator_field = "created_by"
    readonly_fields = ["created_by"]


class UpdatedUserMixin(AuthoredObjectMixin, mixin_for(ExtendableAdmin)):
    updater_field = "updated_by"
    readonly_fields = ["updated_by"]


class CreatedUpdatedUserMixin(CreatedUserMixin, UpdatedUserMixin, mixin_for(ExtendableAdmin)):
    pass


class CreatedMixin(CreatedDatetimeMixin, CreatedUserMixin, mixin_for(ExtendableAdmin)):
    pass


class UpdatedMixin(UpdatedDatetimeMixin, UpdatedUserMixin, mixin_for(ExtendableAdmin)):
    pass


class CreatedUpdatedMixin(CreatedMixin, UpdatedMixin, mixin_for(ExtendableAdmin)):
    pass


class ReadOnlyMixin(mixin_for(ExtendableAdmin)):
    def has_add_permission(self, request) -> bool:
        # Добавлять транзакции нельзя
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        # Обновлять транзакции нельзя
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        # Удалять транзакции нельзя
        return False
