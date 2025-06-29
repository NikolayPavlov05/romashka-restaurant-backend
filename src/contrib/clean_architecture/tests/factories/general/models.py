from __future__ import annotations

from contrib.clean_architecture.tests.fakes.general.models import FakeModel
from contrib.clean_architecture.tests.fakes.general.models import FakeSingletonModel
from contrib.pydantic.model import PydanticModel
from pydantic import field_validator


class FooUserModel(FakeModel):
    username: str = "username"


class FooModel(FakeModel):
    foo_field1: str = "foo_field1"
    foo_field2: str = "foo_field2"
    foo_field3: str = "foo_field3"
    foo_field4: str = "foo_field4"
    created_by: FooUserModel | None = None
    updated_by: FooUserModel | None = None

    @field_validator("created_by", "updated_by", mode="before")
    @classmethod
    def validate_items(cls, value):
        if not value:
            return

        if isinstance(value, PydanticModel):
            return FooUserModel(**value.model_dump())
        return value


class FooSingletonModel(FakeSingletonModel):
    pass
