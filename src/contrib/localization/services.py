from __future__ import annotations

from django.conf import settings
from contrib.imports.services import import_by_string

gettext = import_by_string(settings.LOCALE_GETTEXT_SERVICE)
gettext_lazy = import_by_string(settings.LOCALE_LAZY_GETTEXT_SERVICE)
