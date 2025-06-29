from __future__ import annotations

from contrib.pydantic.model import PydanticModel


class FooExtraLayer(PydanticModel, proxy_model=True):
    @property
    def foo_from_extra_layer_field(self):
        return 1
