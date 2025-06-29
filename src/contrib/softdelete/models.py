from __future__ import annotations

from django.utils.translation import gettext_lazy as l_
from django.db import connection
from django.db import models
from django.db.models.signals import post_delete

from .managers import SafeDeleteManager


class SoftDeleteMixin(models.Model):
    """Миксин для мягкого удаления."""

    deleted = models.BooleanField(default=False, db_index=True, verbose_name=l_("Удален"))

    objects = SafeDeleteManager()
    all_objects = models.Manager()

    def delete(self, **kwargs):
        self.deleted = True
        super().save(**kwargs)
        post_delete.send(sender=self.__class__, instance=self, using=connection.alias)
        return [self.pk]

    def undelete(self, **kwargs):
        self.deleted = False
        super().save(**kwargs)

    class Meta:
        abstract = True
