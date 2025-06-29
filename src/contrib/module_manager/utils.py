from __future__ import annotations

import inspect
import types
from collections.abc import Callable
from functools import lru_cache
from typing import Any
from typing import get_args
from typing import TypeGuard

from .types import _DEPEND_TYPE
from .types import _EMPTY
from .types import _STR_DEPEND_TYPE
from .types import Depend
from .types import FabricProvider


def get_app_label(app_name: str):
    return app_name.rsplit(".", 1)[-1]


def is_class(func: Callable[..., Any]) -> TypeGuard[type[Any]]:
    return inspect.isclass(func)


@lru_cache
def get_all_depends_types():
    from .module_manager import ModuleManager

    localns: dict[str, Any] = {"Depend": Depend}
    for module in ModuleManager._registered.values():
        for service in module.providers:
            service = service.klass if isinstance(service, FabricProvider) else service
            if service.__name__ in localns:
                raise ValueError(f"Duplicate service name {service.__name__} in {module.package_name}.providers")
            localns[service.__name__] = service
        for interface in module.mapping.keys():
            if interface.__name__ in localns:  # type: ignore
                raise ValueError(
                    # type: ignore
                    f"Duplicate mapping key {interface.__name__} in {module.package_name}.mapping"
                )
            localns[interface.__name__] = interface  # type: ignore
    return localns


def get_safe_type_hints(callable_: Callable[..., Any] | type[Any], localns: dict[str, type[Any]]):
    if hasattr(callable_, "__mro__"):
        all_annotations: dict[str, Any] = {}
        for cls in reversed(callable_.__mro__):
            if hasattr(cls, "__annotations__"):
                all_annotations.update(cls.__annotations__)
    else:
        all_annotations = callable_.__annotations__
    annotations: dict[str, Any] = {}
    for key, value in all_annotations.items():
        if isinstance(value, str):
            try:
                type_hint = eval(value, localns)
                annotations[key] = type_hint
            except NameError:
                if value.startswith("Depend["):
                    annotations[key] = _STR_DEPEND_TYPE
                else:
                    annotations[key] = _EMPTY
        else:
            annotations[key] = value
    return annotations


def get_type(type_: type[Any]):
    if type_args := get_args(type_):
        return next(filter(lambda x: not (x is None or x is types.NoneType), type_args))
    return type_


def is_empty_type(type_: type[Any]):
    return type_ is _EMPTY


def is_str_depend_type(type_: type[Any]):
    return type_ is _STR_DEPEND_TYPE


def is_loaded_depend_type(type_: type[Any]):
    return not (is_empty_type(type_) or is_str_depend_type(type_))


def extract_hints_depends(callable_: Callable[..., Any] | type[Any]):
    localns = get_all_depends_types()
    type_hints = get_safe_type_hints(callable_, localns)
    deps: list[Any] = []
    for name, type_hint in type_hints.items():
        if is_str_depend_type(type_hint):
            deps.append((name, type_hint))
            continue
        types_ = get_args(type_hint)
        if len(types_) == 2:
            _type, meta_data = types_
            if meta_data is _DEPEND_TYPE:
                deps.append((name, get_type(_type)))
    return deps
