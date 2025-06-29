from __future__ import annotations

from contrib.openapi.schema_generators import CustomSchemaGenerator
from contrib.openapi.views import SchemaView
from rest_framework.settings import api_settings


def get_schema_view(
    title=None,
    url=None,
    description=None,
    urlconf=None,
    renderer_classes=None,
    public=False,
    patterns=None,
    generator_class=None,
    authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
    permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES,
    version=None,
):
    if generator_class is None:
        generator_class = CustomSchemaGenerator

    generator = generator_class(
        title=title,
        url=url,
        description=description,
        urlconf=urlconf,
        patterns=patterns,
        version=version,
    )
    return SchemaView.as_view(
        renderer_classes=renderer_classes,
        schema_generator=generator,
        public=public,
        authentication_classes=authentication_classes,
        permission_classes=permission_classes,
    )
