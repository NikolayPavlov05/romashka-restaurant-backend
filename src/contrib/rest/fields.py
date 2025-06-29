from __future__ import annotations

import typing
from typing import Any
from warnings import warn

import annotated_types
import typing_extensions
from pydantic import AliasChoices
from pydantic import AliasPath
from pydantic import PydanticUserError
from pydantic import types
from pydantic.config import JsonDict
from pydantic.fields import _EmptyKwargs
from pydantic.fields import _FromFieldInfoInputs
from pydantic.fields import Deprecated
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

_Unset: Any = PydanticUndefined


def _request_field(field_class: type[RequestFieldInfo]):
    def __request_field(
        default: Any = PydanticUndefined,
        *,
        default_factory: typing.Callable[[], Any] | None = _Unset,
        alias: str | None = _Unset,
        alias_priority: int | None = _Unset,
        validation_alias: str | AliasPath | AliasChoices | None = _Unset,
        title: str | None = _Unset,
        field_title_generator: (typing_extensions.Callable[[str, FieldInfo], str] | None) = _Unset,
        description: str | None = _Unset,
        examples: list[Any] | None = _Unset,
        exclude: bool | None = _Unset,
        discriminator: str | types.Discriminator | None = _Unset,
        deprecated: Deprecated | str | bool | None = _Unset,
        json_schema_extra: JsonDict | typing.Callable[[JsonDict], None] | None = _Unset,
        frozen: bool | None = _Unset,
        validate_default: bool | None = _Unset,
        repr: bool = _Unset,
        init: bool | None = _Unset,
        init_var: bool | None = _Unset,
        kw_only: bool | None = _Unset,
        pattern: str | typing.Pattern[str] | None = _Unset,
        strict: bool | None = _Unset,
        coerce_numbers_to_str: bool | None = _Unset,
        gt: annotated_types.SupportsGt | None = _Unset,
        ge: annotated_types.SupportsGe | None = _Unset,
        lt: annotated_types.SupportsLt | None = _Unset,
        le: annotated_types.SupportsLe | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        min_length: int | None = _Unset,
        max_length: int | None = _Unset,
        union_mode: typing.Literal["smart", "left_to_right"] = _Unset,
        fail_fast: bool | None = _Unset,
        **extra: typing.Unpack[_EmptyKwargs],
    ):
        serialization_alias = alias
        alias = _Unset

        const = extra.pop("const", None)  # type: ignore
        if const is not None:
            raise PydanticUserError("`const` is removed, use `Literal` instead", code="removed-kwargs")

        min_items = extra.pop("min_items", None)  # type: ignore
        if min_items is not None:
            warn(
                "`min_items` is deprecated and will be removed, use `min_length` instead",
                DeprecationWarning,
            )
            if min_length in (None, _Unset):
                min_length = min_items  # type: ignore

        max_items = extra.pop("max_items", None)  # type: ignore
        if max_items is not None:
            warn(
                "`max_items` is deprecated and will be removed, use `max_length` instead",
                DeprecationWarning,
            )
            if max_length in (None, _Unset):
                max_length = max_items  # type: ignore

        unique_items = extra.pop("unique_items", None)  # type: ignore
        if unique_items is not None:
            raise PydanticUserError(
                (
                    "`unique_items` is removed, use `Set` instead"
                    "(this feature is discussed in https://github.com/pydantic/pydantic-core/issues/296)"
                ),
                code="removed-kwargs",
            )

        allow_mutation = extra.pop("allow_mutation", None)  # type: ignore
        if allow_mutation is not None:
            warn(
                "`allow_mutation` is deprecated and will be removed. use `frozen` instead",
                DeprecationWarning,
            )
            if allow_mutation is False:
                frozen = True

        regex = extra.pop("regex", None)  # type: ignore
        if regex is not None:
            raise PydanticUserError("`regex` is removed. use `pattern` instead", code="removed-kwargs")

        if extra:
            warn(
                "Using extra keyword arguments on `Field` is deprecated and will be removed."
                " Use `json_schema_extra` instead."
                f' (Extra keys: {", ".join(k.__repr__() for k in extra.keys())})',
                DeprecationWarning,
            )
            if not json_schema_extra or json_schema_extra is _Unset:
                json_schema_extra = extra  # type: ignore

        if (
            validation_alias
            and validation_alias is not _Unset
            and not isinstance(validation_alias, (str, AliasChoices, AliasPath))
        ):
            raise TypeError("Invalid `validation_alias` type. it should be `str`, `AliasChoices`, or `AliasPath`")

        if validation_alias in (_Unset, None):
            validation_alias = alias

        include = extra.pop("include", None)  # type: ignore
        if include is not None:
            warn(
                "`include` is deprecated and does nothing. It will be removed, use `exclude` instead",
                DeprecationWarning,
            )

        return field_class.from_field(
            default,
            default_factory=default_factory,
            alias=alias,
            alias_priority=alias_priority,
            validation_alias=validation_alias,
            serialization_alias=serialization_alias,
            title=title,
            field_title_generator=field_title_generator,
            description=description,
            examples=examples,
            exclude=exclude,
            discriminator=discriminator,
            deprecated=deprecated,
            json_schema_extra=json_schema_extra,
            frozen=frozen,
            pattern=pattern,
            validate_default=validate_default,
            repr=repr,
            init=init,
            init_var=init_var,
            kw_only=kw_only,
            coerce_numbers_to_str=coerce_numbers_to_str,
            strict=strict,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            min_length=min_length,
            max_length=max_length,
            allow_inf_nan=allow_inf_nan,
            max_digits=max_digits,
            decimal_places=decimal_places,
            union_mode=union_mode,
            fail_fast=fail_fast,
        )

    return __request_field


class RequestFieldInfo(FieldInfo):
    @classmethod
    def from_field(
        cls,
        default: Any = PydanticUndefined,
        **kwargs: typing.Unpack[_FromFieldInfoInputs],
    ) -> FieldInfo:
        if "annotation" in kwargs:
            raise TypeError('"annotation" is not permitted as a Field keyword argument')
        return cls(default=default, **kwargs)


class PathFieldInfo(RequestFieldInfo):
    pass


class BodyFieldInfo(RequestFieldInfo):
    pass


class HeaderFieldInfo(RequestFieldInfo):
    pass


class ParamFieldInfo(RequestFieldInfo):
    pass


class FileFieldInfo(RequestFieldInfo):
    pass


class CookieFieldInfo(RequestFieldInfo):
    pass


Path = _request_field(PathFieldInfo)
Body = _request_field(BodyFieldInfo)
Header = _request_field(HeaderFieldInfo)
Param = _request_field(ParamFieldInfo)
File = _request_field(FileFieldInfo)
Cookie = _request_field(CookieFieldInfo)
