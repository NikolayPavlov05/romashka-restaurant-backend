from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from functools import cached_property
from functools import wraps
from http import HTTPMethod
from inspect import unwrap
from typing import Any
from typing import TYPE_CHECKING
from typing import Unpack

from ..schemas import RestMethodResponse
from ..types import DEFAULT_REQUEST_KWARGS
from ..types import DefaultRequestKwargs
from ..types import MERGED_REQUEST_KWARGS
from ..types import MergedRequestKwargs
from ..types import RequestKwargs
from .utils import get_kwargs
from .utils import get_passed_kwargs
from .utils import get_request_parts
from .utils import set_request_parts

if TYPE_CHECKING:
    from contrib.rest.client.bases import RestClientService


class RestService:
    _path: str
    _merge_kwargs: MergedRequestKwargs
    _default_kwargs: DefaultRequestKwargs
    _extra_kwargs: dict

    description: str | None

    def __init_subclass__(
        cls,
        *,
        path: str = "",
        description: str | None = None,
        **kwargs: Unpack[RequestKwargs],
    ):
        cls._path = path
        cls._merge_kwargs = get_passed_kwargs(kwargs, MERGED_REQUEST_KWARGS)
        cls._default_kwargs = get_passed_kwargs(kwargs, DEFAULT_REQUEST_KWARGS)
        cls._extra_kwargs = kwargs.get("extra", {})

        cls.description = description

    @classmethod
    def get_merge_kwargs(cls):
        return deepcopy(cls._merge_kwargs)

    @classmethod
    def get_default_kwargs(cls):
        return deepcopy(cls._default_kwargs)

    @classmethod
    def get_extra_kwargs(cls):
        return deepcopy(cls._extra_kwargs)

    @classmethod
    def get_path(cls):
        return cls._path


class RestMethod[ResponseType: RestMethodResponse]:
    class _EmptyService(RestService):
        pass

    __orig_class__: Any

    _path: str
    _service: type[RestService] = _EmptyService
    _merge_kwargs: MergedRequestKwargs
    _default_kwargs: DefaultRequestKwargs
    _extra_kwargs: dict

    method: HTTPMethod
    validator: Callable[[ResponseType], Any] | None
    description: str | None

    def __init__(
        self,
        path: str = "",
        method: HTTPMethod = HTTPMethod.GET,
        validator: Callable[[ResponseType], bool] | None = None,
        description: str | None = None,
        **kwargs: Unpack[RequestKwargs],
    ):
        self._path = path
        self._merge_kwargs = get_passed_kwargs(kwargs, MERGED_REQUEST_KWARGS)
        self._default_kwargs = get_passed_kwargs(kwargs, DEFAULT_REQUEST_KWARGS)
        self._extra_kwargs = kwargs.get("extra", {})

        self.method = method
        self.validator = validator
        self.description = description

    def __set_name__(self, owner: type[RestService], name):
        self._service = owner

    def __call__[**P, R](
        self, function: Callable[P, R] | None = None, /, **kwargs: Unpack[RequestKwargs]
    ) -> Callable[P, ResponseType | None]:
        return self._decorate_function(function, **kwargs)

    @cached_property
    def _method_decorator(self):
        def decorator(function):
            set_request_parts(function)

            @wraps(function)
            def wrapper(_self: RestClientService, *args, **kwargs):
                request_parts = get_request_parts(function, "self", *args, **kwargs)
                request_params = function.__request_parts__.fields
                request_kwargs = {key: value for key, value in kwargs.items() if key not in request_params}

                kwargs = {**request_parts, **request_kwargs}
                merged_kwargs = get_passed_kwargs(kwargs, MERGED_REQUEST_KWARGS)
                default_kwargs = get_passed_kwargs(kwargs, DEFAULT_REQUEST_KWARGS)

                extra_kwargs = kwargs.pop("extra", {})
                for key in get_passed_kwargs(kwargs, MERGED_REQUEST_KWARGS | DEFAULT_REQUEST_KWARGS, True):
                    extra_kwargs[key] = request_kwargs.pop(key, None)

                merged_kwargs = get_kwargs(function.__merge_kwargs__, merged_kwargs, mode="merge")
                default_kwargs = get_kwargs(function.__default_kwargs__, default_kwargs)
                extra_kwargs = get_kwargs(function.__extra_kwargs__, extra_kwargs)

                kwargs = {**request_kwargs, **merged_kwargs, **default_kwargs}
                return _self.client.make_request(self, **kwargs, extra_kwargs=extra_kwargs)

            return wrapper

        return decorator

    def _decorate_function(self, function: Callable | None, /, **kwargs: Unpack[RequestKwargs]):
        merged_kwargs = get_passed_kwargs(kwargs, MERGED_REQUEST_KWARGS)
        default_kwargs = get_passed_kwargs(kwargs, DEFAULT_REQUEST_KWARGS)
        extra_kwargs = kwargs.get("extra", {})

        function.__merge_kwargs__ = get_kwargs(self.merged_kwargs, merged_kwargs, mode="merge")
        function.__default_kwargs__ = get_kwargs(self.default_kwargs, default_kwargs)
        function.__extra_kwargs__ = get_kwargs(self.extra_kwargs, extra_kwargs)

        if function:
            return self._method_decorator(function)
        return self._method_decorator

    def decorate[**P, R](
        self, function: Callable[P, R] | None = None, /, **kwargs: Unpack[RequestKwargs]
    ) -> Callable[P, ResponseType | None]:
        return self._decorate_function(function, **kwargs)

    def from_method[**P, R](
        self, method: Callable[P, R], /, **kwargs: Unpack[RequestKwargs]
    ) -> Callable[P, ResponseType | None]:
        return self._decorate_function(unwrap(method), **kwargs)

    @property
    def service(self):
        return self._service

    @cached_property
    def path(self):
        base_path = self.service.get_path()
        if not base_path:
            return self._path
        return f"{base_path}/{self._path}"

    @cached_property
    def merged_kwargs(self):
        return get_kwargs(self.service.get_merge_kwargs(), self._merge_kwargs, mode="merge")

    @cached_property
    def default_kwargs(self):
        return get_kwargs(self.service.get_default_kwargs(), self._default_kwargs)

    @cached_property
    def extra_kwargs(self):
        return get_kwargs(self.service.get_extra_kwargs(), self._extra_kwargs)

    @cached_property
    def response_type(self) -> type[ResponseType]:
        return self.__orig_class__.__args__[0]
