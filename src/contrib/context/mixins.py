from __future__ import annotations

from .root_context import get_root_context


class ContextMixin:
    def __init__(self):
        self.context = get_root_context().new_child_context()
