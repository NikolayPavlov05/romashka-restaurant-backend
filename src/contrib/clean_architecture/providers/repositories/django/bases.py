"""Модуль с реализацией репозитория для django

Classes:
    DjangoRepository: Django базовый репозиторий

"""
from __future__ import annotations

from django.conf import settings
from contrib.clean_architecture.dto_based_objects.django.bases import (
    DjangoDTOBasedObjectsMixin,
)
from contrib.clean_architecture.providers.repositories.bases import BaseRepository
from contrib.clean_architecture.providers.repositories.django.utils import search_filter
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F
from django.db.models import Q


class DjangoRepository(
    DjangoDTOBasedObjectsMixin,
    BaseRepository,
    required_attrs_base=True,
    repository_base=True,
):
    atomic_decorator = transaction.atomic
    external_code_model = settings.EXTERNAL_CODE_MODEL

    object_does_not_exist_exception = ObjectDoesNotExist
    multiple_objects_returned_exception = MultipleObjectsReturned

    search_filter_function = search_filter
    condition_wrapper = Q
    find_wrapper = F

    def _get_m2m_fields(self) -> list[str]:
        model_fields = self.model._meta.get_fields()
        return [field.name for field in model_fields if field.many_to_many]
