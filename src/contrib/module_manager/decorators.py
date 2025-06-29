from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec
from typing import TypeVar
from typing import Union

from .module_manager import ModuleManager
from .utils import extract_hints_depends
from .utils import is_class

_T = TypeVar("_T")
_P = ParamSpec("_P")
_FuncOrType = TypeVar("_FuncOrType", bound=Union[Callable, type])


def inject(*modules: str) -> Callable[[_FuncOrType], _FuncOrType]:
    def decorator(func_or_cls: _FuncOrType) -> _FuncOrType:
        if is_class(func_or_cls):
            base_init = func_or_cls.__init__

            @wraps(base_init)
            def __init__(self, *args, **kwargs):
                ModuleManager.inject_to_obj(set(modules), self, find_in_module=False)
                base_init(self, *args, **kwargs)

            func_or_cls.__init__ = __init__
            return func_or_cls

        @wraps(func_or_cls)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            if hasattr(func_or_cls, "injected_kwargs"):
                inject_kwargs = func_or_cls.injected_kwargs
            else:
                inject_kwargs = ModuleManager.get_depends(
                    set(modules),
                    func_or_cls,
                    extract_hints_depends(func_or_cls),
                    find_in_module=False,
                )
                func_or_cls.injected_kwargs = inject_kwargs
            return func_or_cls(*args, **kwargs, **inject_kwargs)

        return wrapper

    return decorator
