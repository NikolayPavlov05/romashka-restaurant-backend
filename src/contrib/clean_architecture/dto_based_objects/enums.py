"""Модуль с Enums репозиториев

Classes:
    RelatedTypes: Типы relations

"""
from __future__ import annotations

from enum import auto
from enum import Enum


class RelatedTypes(Enum):
    """Типы relations"""

    SELECT_RELATED = auto()
    PREFETCH_RELATED = auto()
