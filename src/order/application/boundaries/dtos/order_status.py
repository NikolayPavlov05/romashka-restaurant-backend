from __future__ import annotations

from pydantic import Field

from django.utils.translation import gettext as _

from contrib.mixins.pydantic_model import IdMixin, NameMixin


class OrderStatusInfoDTO(IdMixin, NameMixin, response_model=True):
    is_completed: bool = Field(title=_("Выполнен"))
