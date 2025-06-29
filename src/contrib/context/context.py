from __future__ import annotations

import uuid
from collections.abc import Hashable
from collections.abc import MutableMapping
from contextvars import ContextVar
from copy import deepcopy
from typing import Any
from typing import Generic
from typing import TypeVar

T = TypeVar("T", bound=dict[Hashable, Any], covariant=True)


class Context(Generic[T]):
    parent: Context | None

    __slots__ = [
        "_context_var",
        "_initial_data",
        "_child_context",
        "_initialized",
        "parent",
    ]

    def __init__(self, **initial_data: dict[Hashable, Any]) -> None:
        self._context_var = ContextVar[T](uuid.uuid4().hex)
        self._initial_data = initial_data
        self._child_context: list[Context[Any]] = []
        self._initialized: bool = None
        self.parent: Context | None = None

    def _check_initialized(self):
        if not self.initialized:
            raise RuntimeError("Context is not initialized")

    @property
    def initialized(self):
        return self._initialized

    def init_context(self) -> None:
        self._context_var.set(deepcopy(self._initial_data))  # type: ignore
        for ctx in self._child_context:
            ctx.init_context()
        self._initialized = True

    def new_child_context(self, **initial_data: dict[Hashable, Any]):
        ctx = type(self)(**initial_data)
        ctx.parent = self
        self._child_context.append(ctx)
        if self.initialized:
            ctx.init_context()
        return ctx

    def get(self, key: Hashable, default: Any = None):
        self._check_initialized()
        return self._context_var.get().get(key, default)

    def set(self, key: Hashable, value: Any):
        self._check_initialized()
        self._context_var.get()[key] = value

    def pop(self, key: Hashable, default: Any = None):
        self._check_initialized()
        return self._context_var.get().pop(key, default)

    def popitem(self):
        self._check_initialized()
        return self._context_var.get().popitem()

    def clear(self):
        self._check_initialized()
        for key in list(self._context_var.get().keys()):
            self._context_var.get().pop(key)

    def update(self, data: dict[Hashable, Any] | list[tuple[Hashable, Any]]):
        self._check_initialized()
        self._context_var.get().update(data)

    def has_key(self, key: Hashable):
        self._check_initialized()
        return key in self._context_var.get()

    def setdefault(self, key: Hashable, default: Any = None):
        self._check_initialized()
        return self._context_var.get().setdefault(key, default)

    def items(self):
        self._check_initialized()
        return self._context_var.get().items()

    def keys(self):
        self._check_initialized()
        return self._context_var.get().keys()

    def values(self):
        self._check_initialized()
        return self._context_var.get().values()

    @property
    def current_user(self):
        return getattr(self.get("request"), "user", None)

    def __contains__(self, key: Hashable):
        return self.has_key(key)

    def __len__(self):
        return len(self._context_var.get())

    def __iter__(self):
        return iter(self._context_var.get())

    def __getitem__(self, key: Hashable):
        return self.get(key)

    def __setitem__(self, key: Hashable, value: Any):
        self.set(key, value)

    def __delitem__(self, key: Hashable):
        self.pop(key)

    def __bool__(self):
        return bool(self._context_var.get())


MutableMapping.register(Context)  # type: ignore
