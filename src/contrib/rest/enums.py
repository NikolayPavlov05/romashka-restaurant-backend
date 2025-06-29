from __future__ import annotations

from enum import auto
from enum import Enum


class TokenTypes(Enum):
    JWT = auto()
    BEARER = auto()
