from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any
from typing import Self

from contrib.clean_architecture.types import mixin_for
from contrib.localization.services import gettext_lazy as _
from django.db.models import Choices as _Choices
from django.db.models.enums import ChoicesType


class CustomChoicesMeta(ChoicesType):
    def __new__(mcs, name, bases, attrs, safe=False, **kwds):
        if safe:
            attrs["_NOT_EXPECTED"] = (-99999 if IntegerChoices in bases else "NOT_EXPECTED"), _("Не ожидаемое значение")
        cls = super().__new__(mcs, name, bases, attrs, **kwds)
        cls.__safe__ = safe
        return cls

    @property
    def codes_choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, "__empty__") else []
        return empty + [(member.name, member.value) for member in cls]

    def to_dicts(cls, label_type: Callable = str):
        result = []
        for item in cls:
            _item = {"name": item.name, "value": item.value}
            if hasattr(item, "label"):
                _item["label"] = label_type(item.label)
            result.append(_item)
        return result


class Choices(_Choices, metaclass=CustomChoicesMeta):
    _NOT_EXPECTED: Choices

    __safe__: bool
    __descriptions__: dict[Self, Any]

    @classmethod
    def to_vue_selected(cls):
        return [{"id": code, "name": label} for code, label in cls.choices]

    @classmethod
    def add_descriptions(cls, descriptions: dict[Choices, Any]):
        if not hasattr(cls, "__descriptions__"):
            cls.__descriptions__ = descriptions
        else:
            cls.__descriptions__.update(descriptions)

    @property
    def description(self):
        if not hasattr(self, "__descriptions__"):
            return self.label
        return self.__descriptions__.get(self._value_, self.label)

    @classmethod
    def _missing_(cls, value: str | int):
        _value = super()._missing_(value)
        if not _value and getattr(cls, "__safe__", False):
            _value = deepcopy(cls._NOT_EXPECTED)
            _value._value_ = value
            return _value


class IntegerChoices(int, Choices): ...


class TextChoices(str, Choices):
    def _generate_next_value_(name, start, count, last_values):
        return name


class CaseInsensitiveEnumMixin(mixin_for(TextChoices)):
    @classmethod
    def _missing_(cls, value: str):
        value = value.upper()
        for member in cls:
            if member.upper() == value:
                return member
        return super()._missing_(value)
