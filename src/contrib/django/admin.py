from __future__ import annotations

from enum import Enum

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


def external_code_field(code_type: Enum, description: str):
    @admin.display(ordering="external_codes", description=description)
    def _field(self, obj):
        if not obj.external_codes:
            return
        external_code = obj.external_codes.filter(code_type=code_type).first()
        return external_code.code if external_code else "-"

    return _field


def admin_link(*instances):
    links = []
    for instance in instances:
        if not instance:
            continue
        app_label, model_name = instance._meta.app_label, instance._meta.model_name
        path = reverse(f"admin:{app_label}_{model_name}_change", args=(instance.id,))

        links.append(format_html("<a href='{url}'>{text}</a>", url=path, text=instance.__str__()))

    return format_html(", ".join(links))
