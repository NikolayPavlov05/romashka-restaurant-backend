from __future__ import annotations

from typing import Any

from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.providers.repositories.bases import BaseRepository
from contrib.clean_architecture.tests.fakes.dto_based_objects.bases import (
    FakeDTOBasedObjectsMixin,
)
from contrib.clean_architecture.tests.fakes.general.models import FakeExternalCode
from contrib.clean_architecture.tests.fakes.repositories.exceptions import FakeMultipleObjectsReturned
from contrib.clean_architecture.tests.fakes.repositories.exceptions import FakeObjectDoesNotExist
from contrib.clean_architecture.tests.fakes.repositories.utils import fake_atomic
from contrib.clean_architecture.tests.fakes.repositories.utils import fake_search_filter


class FakeRepository(
    FakeDTOBasedObjectsMixin,
    BaseRepository,
    required_attrs_base=True,
    repository_base=True,
):
    atomic_decorator = fake_atomic
    external_code_model = FakeExternalCode

    object_does_not_exist_exception = FakeObjectDoesNotExist
    multiple_objects_returned_exception = FakeMultipleObjectsReturned

    search_filter_function = fake_search_filter

    def _prepare_filters(self, *conditions: Any, filter_dto: DTO = None, **filters):
        exclude_conditions = {}
        for key in list(filters.keys()):
            if key.startswith("~"):
                exclude_conditions.update(**{key.replace("~", ""): filters.pop(key)})
        return (exclude_conditions, *conditions), {
            **(filter_dto.model_dump() if filter_dto else {}),
            **filters,
        }
