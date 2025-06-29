from __future__ import annotations

from django.conf import settings
from modeltranslation.utils import get_translation_fields as _get_translation_fields


def translated_fields(*fields, append_current=True) -> list[str]:
    result = []
    for field in fields:
        if settings.USE_I18N:
            result.extend(_get_translation_fields(field))
        if append_current:
            result.append(field)

    return result
