from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import TypeVar

from pydantic import TypeAdapter

if TYPE_CHECKING:
    from contrib.pydantic.mixins.interfaces import IProxyModelMixin
    from contrib.pydantic.model import PydanticModel

    T = TypeVar("T", bound=PydanticModel)


class NestedEntity:
    def __init__(self, entity: type[T], multiple=False, default=None, default_factory=list):
        self._entity = entity
        self._multiple = multiple
        self._default = default
        self._default_factory = default_factory

    def __set_name__(self, owner: type[IProxyModelMixin], name: str):
        self._name = name

    def _validate_entity(self, instance, value) -> T | Iterable[T] | None:
        _value = instance.get_or_retrieve_field_value(value)
        if self._multiple:
            type_adapter = TypeAdapter(self._default_factory[self._entity])
            return type_adapter.validate_python(_value, from_attributes=True)
        return self._entity.model_validate(_value, from_attributes=True)

    def __get__(self, instance: IProxyModelMixin, owner: type[IProxyModelMixin]) -> T | list[T] | None | NestedEntity:
        if instance is None:
            return self

        _value = self._default_factory() if self._multiple else self._default

        try:
            _value = instance.extra_data[self._name]

        except KeyError:
            try:
                _value = getattr(instance.original_object, self._name)
            except AttributeError:
                instance.extra_data[self._name] = None

        if _value is not None and not isinstance(_value, self._entity):
            _value = self._validate_entity(instance, _value)

        instance.extra_data[self._name] = _value

        return _value

    def __set__(self, instance: IProxyModelMixin, value):
        if value is not None and not isinstance(value, self._entity):
            value = self._validate_entity(instance, value)

        instance.extra_data[self._name] = value
