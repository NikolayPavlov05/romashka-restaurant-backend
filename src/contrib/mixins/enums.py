from __future__ import annotations

from contrib.bases.enums import CaseInsensitiveEnumMixin
from contrib.bases.enums import TextChoices
from django.utils.translation import gettext_lazy as l_


class LoggingStatuses(CaseInsensitiveEnumMixin, TextChoices):
    SUCCESS = "success", l_("Успешно")
    ERROR = "error", l_("Ошибка")
    WAITING = "waiting", l_("Ожидание")
