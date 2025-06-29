from __future__ import annotations

import inspect
from copy import deepcopy
from typing import Any
from typing import ClassVar
from typing import Literal

from contrib.inspect.services import get_params_with_values
from contrib.pydantic.model import PydanticModel
from contrib.rest.fields import BodyFieldInfo
from contrib.rest.fields import CookieFieldInfo
from contrib.rest.fields import FileFieldInfo
from contrib.rest.fields import HeaderFieldInfo
from contrib.rest.fields import ParamFieldInfo
from contrib.rest.fields import PathFieldInfo
from contrib.rest.fields import RequestFieldInfo
from pydantic import PrivateAttr
from pydantic.fields import Field
from pydantic.fields import FieldInfo

_BindMode = Literal["default", "merge"]


def set_request_parts(function):
    params = inspect.signature(inspect.unwrap(function)).parameters

    request_parts = _RequestParts()
    for name, param in params.items():
        field = None
        annotation = param.annotation
        default = param.default

        if (
            hasattr(annotation, "__metadata__")
            and annotation.__metadata__
            and any(isinstance(item, FieldInfo) for item in annotation.__metadata__)
        ):
            field = next(filter(lambda x: isinstance(x, FieldInfo), annotation.__metadata__))
            annotation = annotation.__args__[0]
            if default != param.empty:
                field.default = default

        if isinstance(default, FieldInfo):
            field = default

        if not field:
            continue

        field.annotation = annotation
        request_parts.add_param(name, field)

    request_parts.set_validate_class()
    function.__request_parts__ = request_parts
    return request_parts, request_parts.fields


def get_request_parts(function, *args, **kwargs):
    request_parts: _RequestParts = function.__request_parts__
    data = get_params_with_values(function, *args, **kwargs, params=request_parts.fields)
    return request_parts.get_request_parts(data)


def get_passed_kwargs(kwargs: dict[str, Any], keys: set[str], reverse=False):
    if reverse:
        return {key: value for key, value in kwargs.items() if key not in keys}
    return {key: value for key, value in kwargs.items() if key in keys}


def get_kwargs(*kwargs_tuple: dict, mode: _BindMode = "default", copy: bool = True):
    result = {}
    if mode == "default":
        for kwargs in kwargs_tuple:
            result.update(kwargs)
    else:
        for kwargs in kwargs_tuple:
            for key, value in kwargs.items():
                if key in result:
                    result[key].update(value)
                else:
                    result[key] = value

    if copy:
        return deepcopy(result)
    return result


class _RequestPartsValues(PydanticModel):
    paths: dict[str, Any] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    files: dict[str, Any] = Field(default_factory=dict)
    cookies: dict[str, Any] = Field(default_factory=dict)


class _RequestParts(PydanticModel):
    _validate_class = PrivateAttr(None)
    _parts_mapping: ClassVar[dict[str, type[RequestFieldInfo]]] = dict(
        paths=PathFieldInfo,
        body=BodyFieldInfo,
        headers=HeaderFieldInfo,
        params=ParamFieldInfo,
        files=FileFieldInfo,
        cookies=CookieFieldInfo,
    )
    _types_mapping: ClassVar[dict[type[RequestFieldInfo], str]] = {value: key for key, value in _parts_mapping.items()}

    paths: dict[str, FieldInfo] = Field(default_factory=dict)
    body: dict[str, FieldInfo] = Field(default_factory=dict)
    headers: dict[str, FieldInfo] = Field(default_factory=dict)
    params: dict[str, FieldInfo] = Field(default_factory=dict)
    files: dict[str, FieldInfo] = Field(default_factory=dict)
    cookies: dict[str, FieldInfo] = Field(default_factory=dict)

    def add_param(self, name: str, field: FieldInfo = None):
        if name in self.registered:
            raise ValueError(f"Duplicate param name: {name}")

        part = self._types_mapping.get(field.__class__)
        if not part:
            raise ValueError(f"Unsupported field type: {field.__class__.__name__}")

        getattr(self, part)[name] = field

    def set_validate_class(self):
        class _ValidationClass:
            pass

        for name, field in self.fields.items():
            setattr(_ValidationClass, name, field)
            _ValidationClass.__annotations__[name] = field.annotation

        class ValidationClass(_ValidationClass, PydanticModel):
            pass

        self._validate_class = ValidationClass

    def get_request_parts(self, data: dict[str, Any]):
        data = {key: self.get_default(value) for key, value in data.items()}
        data = self._validate_class.model_validate(data, from_attributes=True)

        request_parts = _RequestPartsValues()
        for part_name in self._parts_mapping:
            part_params = getattr(self, part_name).keys()
            dump_kwargs = dict(include=part_params, exclude_none=True, by_alias=True, mode="json")
            setattr(request_parts, part_name, data.model_dump(**dump_kwargs))

        return request_parts.model_dump(exclude_defaults=True)

    @staticmethod
    def get_default(value: Any):
        return value.get_default(call_default_factory=True) if isinstance(value, FieldInfo) else value

    @property
    def registered(self):
        return (
            self.paths.keys()
            | self.body.keys()
            | self.headers.keys()
            | self.params.keys()
            | self.files.keys()
            | self.cookies.keys()
        )

    @property
    def fields(self):
        return self.paths | self.body | self.headers | self.params | self.files | self.cookies
