from __future__ import annotations

from django.utils.translation import gettext_lazy as l_
from contrib.mixins.model import CreatedDatetimeMixin
from django.db import models


class RestLog(CreatedDatetimeMixin):
    message = models.CharField(l_("Сообщение"), max_length=255)
    method = models.CharField(l_("Название метода"), max_length=255, blank=True, null=True)
    params = models.TextField(l_("Параметры запроса"), blank=True, null=True)
    response = models.TextField(l_("Ответ"), blank=True, null=True)
    traceback = models.TextField(l_("Трассировка ошибки"), blank=True, null=True)

    class Meta:
        abstract = True
