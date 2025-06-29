from __future__ import annotations

import inspect
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from copy import deepcopy
from types import MethodType


class BaseDecorator(ABC):
    __class__ = MethodType
    __func__ = None
    __doc__ = None

    _return_function = False
    _with_args = False
    _decorated = False
    _is_args_prepared = False
    _function_args = None
    _instance = None
    _owner = None

    def __init__(
        self,
        function: Callable | None = None,
        /,
        *,
        return_function: bool = False,
        **kwargs,
    ):
        self._return_function = return_function
        self.__dict__.update(kwargs)
        self.__post__init__(function)

    def __post__init__(self, function: Callable | None = None):
        if not function:
            self._with_args = True
        else:
            self._function_args = inspect.getfullargspec(function).args
            self.__doc__ = function.__doc__
            self.__func__ = self._get_decorated(function)

    def __call__(self, *args, **kwargs):
        if args:
            first, *args = args
        else:
            return self.__func__(**kwargs)

        if self._with_args:
            if self._return_function:
                return self._get_decorated(first)

            self._function_args = inspect.getfullargspec(first).args
            self.__doc__ = first.__doc__
            self.__func__ = first
            return self
        return self.__func__(first, *args, **kwargs)

    def __get__(self, instance=None, owner=None):
        self._instance = instance
        self._owner = owner

        if not self._decorated:
            self.__func__ = self._get_decorated(self.__func__)
        if not self._is_args_prepared:
            self._prepare_args()

        return self.__func__

    def _get_decorated(self, function):
        self._decorated = True
        return self.get_decorated(function)

    def _prepare_args(self):
        if not self._instance and not self._owner:
            return

        function = deepcopy(self.__func__)

        def wrapper(*args, **kwargs):
            first_arg = None
            if self._function_args and self._function_args[0] == "self":
                if not self._instance:
                    return
                first_arg = self._instance
            elif self._function_args and self._function_args[0] in ("cls", "mcs"):
                first_arg = self._owner

            if first_arg:
                args = (first_arg, *args)
            return function(*args, **kwargs)

        self._is_args_prepared = True
        self.__func__ = wrapper

    @abstractmethod
    def get_decorated(self, function):
        raise NotImplementedError
