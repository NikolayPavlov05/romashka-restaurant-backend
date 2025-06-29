from __future__ import annotations

from django.db import models


class SafeDeleteManager(models.Manager):
    """Менеджер для мягкого удаления."""

    def get_queryset(self):
        """Получаем queryset объектов"""
        return super().get_queryset().filter(deleted=False)
