from __future__ import annotations

from contrib.mixins.pydantic_model import IdMixin, NameMixin


class CategoryInfoDTO(IdMixin, NameMixin, response_model=True):
    ...
