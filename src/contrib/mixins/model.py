from __future__ import annotations

from django.utils.translation import gettext_lazy as l_
from django.db import models

from .enums import LoggingStatuses


class MetaFieldsMixin(models.Model):
    meta_title = models.CharField(max_length=255, verbose_name=l_("Meta-title"), default="", blank=True)
    meta_keywords = models.CharField(max_length=255, verbose_name=l_("Meta-keywords"), default="", blank=True)
    meta_description = models.TextField(verbose_name=l_("Meta-description"), default="", blank=True)

    seo_header = models.CharField(max_length=255, verbose_name=l_("Заголовок страницы"), default="", blank=True)
    seo_caption = models.CharField(max_length=300, verbose_name=l_("Подпись страницы"), default="", blank=True)
    seo_text = models.TextField(verbose_name=l_("Сео текст"), default="", blank=True)
    extra_info = models.CharField(verbose_name=l_("Доп. информация"), max_length=255, default="", blank=True)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(l_("Наименование"), max_length=255, default="", blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or "--"

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)


class DescriptionMixin(models.Model):
    description = models.TextField(l_("Описание"), default="", blank=True)

    class Meta:
        abstract = True


class IsActiveMixin(models.Model):
    is_active = models.BooleanField(l_("Признак активности записи"), default=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.is_active:
            return super().__str__()
        return f"{super().__str__()} ({l_('Неактивна')})"


class ProtectedMixin(models.Model):
    protected = models.BooleanField(verbose_name=l_("Защищенная запись"), default=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if self.protected:
            raise ValueError(l_("Защищенная запись не может быть удалена."))
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.protected and getattr(self, "is_active", None):
            raise ValueError(l_("Защищенная запись не может не активной."))
        super().save(*args, **kwargs)


class ExtraDataMixin(models.Model):
    extra_data = models.JSONField(verbose_name=l_("Дополнительные данные"), default=dict, blank=True)

    class Meta:
        abstract = True


class DictionaryMixin(DescriptionMixin, NameMixin):
    class Meta:
        abstract = True


class CreatedDatetimeMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=l_("Дата и время создания"),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class UpdatedDatetimeMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True, verbose_name=l_("Дата и время обновления"), null=True, blank=True)

    class Meta:
        abstract = True


class CreatedUpdatedDatetimeMixin(CreatedDatetimeMixin, UpdatedDatetimeMixin):
    class Meta:
        abstract = True


class CreatedUserMixin(models.Model):
    created_by = models.ForeignKey(
        "core.User",
        verbose_name=l_("Пользователь, создавший запись"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(model_name)s_creators",
    )

    class Meta:
        abstract = True


class UpdatedUserMixin(models.Model):
    updated_by = models.ForeignKey(
        "core.User",
        verbose_name=l_("Последний пользователь изменивший запись"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(model_name)s_updaters",
    )

    class Meta:
        abstract = True


class CreatedUpdatedUserMixin(CreatedUserMixin, UpdatedUserMixin):
    class Meta:
        abstract = True


class CreatedMixin(CreatedDatetimeMixin, CreatedUserMixin):
    class Meta:
        abstract = True


class UpdatedMixin(UpdatedDatetimeMixin, UpdatedUserMixin):
    class Meta:
        abstract = True


class CreatedUpdatedMixin(CreatedMixin, UpdatedMixin):
    class Meta:
        abstract = True


class LoggingStatusMixin(models.Model):
    status = models.CharField(
        verbose_name=l_("Статус"),
        blank=False,
        null=False,
        choices=LoggingStatuses.choices,
        default=LoggingStatuses.WAITING,
        max_length=32,
    )

    class Meta:
        abstract = True


class HashMixin(models.Model):
    hash = models.SlugField(verbose_name=l_("Хэш"), unique=True, max_length=100)

    class Meta:
        abstract = True


class HTTPLoggingMixin(LoggingStatusMixin):
    request_at = models.DateTimeField(verbose_name=l_("Дата запроса"), auto_now_add=True)
    request_body = models.TextField(verbose_name=l_("Тело запроса"), blank=True, null=True)
    request_headers = models.TextField(verbose_name=l_("Заголовки запроса"), blank=True, null=True)
    response_at = models.DateTimeField(verbose_name=l_("Дата получения ответа"), null=True, blank=True)
    response_body = models.TextField(verbose_name=l_("Тело ответа"), null=True, blank=True)
    response_code = models.IntegerField(verbose_name=l_("Код ответа"), null=True, blank=True)

    class Meta:
        abstract = True
