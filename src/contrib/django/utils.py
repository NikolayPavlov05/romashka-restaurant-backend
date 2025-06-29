from __future__ import annotations

from django.conf import settings


def is_app_installed(app):
    return app in settings.INSTALLED_APPS
