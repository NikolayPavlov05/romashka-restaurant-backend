from __future__ import annotations

from typing import Annotated
from typing import Any
from typing import NamedTuple
from typing import Protocol
from typing import runtime_checkable
from typing import TypeAlias
from typing import TypeVar

__all__ = ["Depend", "DependencyInjectorProto"]

_T = TypeVar("_T")


class _DEPEND_TYPE: ...


class _EMPTY: ...


class _STR_DEPEND_TYPE: ...


Depend: TypeAlias = Annotated[_T, _DEPEND_TYPE]


@runtime_checkable
class DependencyInjectorProto(Protocol):
    def __inject__(self, *args: type[Any], **kwargs: type[Any]): ...


class FabricProvider(NamedTuple):
    klass: type[Any]
    args: tuple[Any, ...] | None = None
    kwargs: dict[str, Any] | None = None
