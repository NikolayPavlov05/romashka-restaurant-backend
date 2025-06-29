from __future__ import annotations

from contrib.pydantic.model import PydanticModel


class FooDTO(PydanticModel, with_paginated=True):
    id: int | None = None
    foo_field1: str = "foo_field1"
    foo_field2: str = "foo_field2"
    foo_field3: str = "foo_field3"
    foo_field4: str = "foo_field4"


class BarDTO(PydanticModel, with_paginated=True):
    id: int | None = None
    foo_field1: str = "foo_field1"
    foo_field2: str = "foo_field2"
    foo_field3: str = "foo_field3"
    foo_field4: str = "foo_field4"


class FooPatchListItemDTO(FooDTO):
    delete: bool | None = None


class FooPatchListDTO(PydanticModel):
    items: list[FooPatchListItemDTO] = []
