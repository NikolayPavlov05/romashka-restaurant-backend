from __future__ import annotations

from django.contrib import admin
from django.urls import path, include

from rest_framework.renderers import OpenAPIRenderer
from contrib.openapi.utils import get_schema_view
from contrib.openapi.views import swagger_view

from django.conf.urls.static import static
from django.conf import settings


openapi_schema_urls = [
    path(r"", include("catalog.api.urls")),
    path(r"", include("order.api.urls")),
]

schema_urlpatterns = [
    path(
        "schema.yaml",
        get_schema_view(url="", renderer_classes=[OpenAPIRenderer], patterns=openapi_schema_urls),
        name="openapi-schema-yaml",
    ),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path("schema/", (schema_urlpatterns, "api-v1-schema", "api-v1-schema")),
    path(
        "schema/docs/",
        swagger_view,
        {"schema_url": "api-v1-schema:openapi-schema-yaml"},
        name="swagger-ui",
    ),
]

urlpatterns += openapi_schema_urls

urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
