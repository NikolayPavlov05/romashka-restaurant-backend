from __future__ import annotations

from django.conf import settings
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied
from rest_framework.schemas.openapi import SchemaGenerator


class CustomSchemaGenerator(SchemaGenerator):
    def has_view_permissions(self, path, method, view):
        """
        Return `True` if the incoming request has the correct view permissions.
        """
        if view.request is None or settings.DEBUG:
            return True

        try:
            view.check_permissions(view.request)
        except (exceptions.APIException, Http404, PermissionDenied):
            return False
        return True
