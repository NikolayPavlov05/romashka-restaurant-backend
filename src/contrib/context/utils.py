from __future__ import annotations

from copy import deepcopy
from typing import Any


class _ContextProperty:
    _name = None
    _prefix = None
    _default = None
    _default_factory = None

    def __init__(self, default=None, default_factory=None):
        self._default = default
        self._default_factory = default_factory

    def __set_name__(self, owner, name):
        self._name = name
        self._prefix = f"{owner.__module__}:{owner.__name__}"

    @property
    def default_value(self) -> Any:
        if self._default_factory:
            return self._default_factory()
        return deepcopy(self._default)

    def __get__(self, instance, owner):
        value = instance.context.get(self.context_key)
        if value is None:
            value = self.default_value
            instance.context.set(self.context_key, value)
        return value

    def __set__(self, instance, value):
        instance.context.set(self.context_key, value)

    @property
    def context_key(self):
        return f"{self._prefix}:{self._name}"


context_property = _ContextProperty
