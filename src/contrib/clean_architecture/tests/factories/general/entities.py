from __future__ import annotations

from contrib.pydantic.model import PydanticModel


class FooEntity(PydanticModel, proxy_model=True):
    pass
