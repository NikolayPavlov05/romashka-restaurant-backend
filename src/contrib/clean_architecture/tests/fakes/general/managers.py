from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any
from typing import TYPE_CHECKING

from contrib.clean_architecture.interfaces import IM2MManager
from contrib.clean_architecture.interfaces import IManager
from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType
from contrib.clean_architecture.tests.fakes.repositories.exceptions import FakeMultipleObjectsReturned
from contrib.clean_architecture.tests.fakes.repositories.exceptions import FakeObjectDoesNotExist
from contrib.subclass_control.mixins import ImportedStringAttrsMixin

if TYPE_CHECKING:
    from contrib.clean_architecture.dto_based_objects.dtos import M2MUpdateAction
    from contrib.clean_architecture.tests.fakes.general.models import FakeModel

_fake_ids = {}
_fake_instances = {}


class FakeManager(IManager):
    _model = None

    class _Query(IManager._IQuery):
        def __init__(self):
            self.select_related = {}

    def __init__(self):
        self._prefetch_related_lookups = ()
        self._query = self._Query()
        self._filters = {}
        self._exclude_filters = {}
        self._order_by = set()
        self._search_filter = None

    def __get__(self, instance, owner):
        if not self._model:
            self._model = owner
        if self._model not in _fake_ids:
            _fake_ids[self._model] = 0
        if self._model not in _fake_instances:
            _fake_instances[self._model] = []

        return deepcopy(self)

    def __getitem__(self, item):
        return self.all()[item]

    def __iter__(self):
        return iter(self.all())

    def _set_id(self, instance):
        _fake_ids[self._model] += 1
        instance.id = instance.pk = _fake_ids[self._model]
        return instance

    def _get_result(self):
        result = _fake_instances[self._model]
        for key, value in self._filters.items():
            if key == "pk__in":
                result = filter(lambda item: item.id in value, result)
            else:
                result = filter(lambda item: getattr(item, key) == value, result)

        for key, value in self._exclude_filters.items():
            result = filter(lambda item: getattr(item, key) != value, result)

        if self._search_filter:
            result = filter(self._search_filter, result)

        if self._order_by:
            result = sorted(
                result,
                key=lambda item: tuple(getattr(item, field) for field in self._order_by),
            )

        return list(result)

    def clear(self):
        _fake_instances[self._model] = []

    def all(self):
        return self._get_result()

    def create(self, **kwargs):
        instance = self._model(**kwargs)
        self._set_id(instance)
        _fake_instances[self._model].append(instance)
        return instance

    def bulk_create(self, objects: list[FakeModel]) -> None:
        for instance in objects:
            self._set_id(instance)
            _fake_instances[self._model].append(instance)

    def bulk_update(self, objects: list[FakeModel], fields: list[str]) -> None:
        for instance in objects:
            _object = self.get(id=instance.id)
            for field in fields:
                value = getattr(instance, field, None)
                setattr(_object, field, value)

    def update(self, **kwargs):
        results = self._get_result()
        for result in results:
            _object = self.get(id=result.id)
            for k, v in kwargs.items():
                setattr(_object, k, v)

    def delete(self) -> None:
        results = self._get_result()
        for result in results:
            _fake_instances[self._model].remove(result)

    def first(self):
        result = self._get_result()
        return result[0] if result else None

    def last(self):
        result = self._get_result()
        return result[-1] if result else None

    def filter(self, *args, **kwargs):
        self._filters.update(**kwargs)
        try:
            self._exclude_filters.update(**next(iter(args or {}), {}))
        except StopIteration:
            pass
        return self

    def search(self, search_filter: Callable):
        self._search_filter = search_filter
        return self

    def order_by(self, *args):
        self._order_by |= set(args)
        return self

    def get(self, *args, **kwargs):
        result = self.filter(**kwargs)._get_result()
        if not result:
            raise FakeObjectDoesNotExist
        elif len(result) != 1:
            raise FakeMultipleObjectsReturned

        return result[0]

    def get_or_create(self, defaults=None, **kwargs):
        defaults = defaults or {}
        try:
            return self.get(**kwargs), False
        except FakeObjectDoesNotExist:
            return self.create(**{**kwargs, **defaults}), True

    def update_or_create(self, defaults=None, **kwargs):
        defaults = defaults or {}
        try:
            instance = self.get(**kwargs)
        except FakeObjectDoesNotExist:
            return self.create(**{**kwargs, **defaults}), True

        for k, v in defaults.items():
            setattr(instance, k, v)
        return instance, False

    def exists(self):
        return bool(self._get_result())

    def count(self):
        return len(self._get_result())

    @classmethod
    def _set_select_related(cls, root, *keys):
        current_key, *keys = keys
        if not keys:
            if current_key not in root:
                root[current_key] = {}
        else:
            if current_key not in root:
                root[current_key] = {}
            cls._set_select_related(root[current_key], *keys)

    def select_related(self, *args):
        for arg in args:
            self._set_select_related(self._query.select_related, *arg.split("__"))
        return self

    def prefetch_related(self, *args):
        for arg in args:
            if arg not in self._prefetch_related_lookups:
                self._prefetch_related_lookups += (arg,)
        return self


class FakeExternalCodeManager(FakeManager, ImportedStringAttrsMixin):
    imported_string_attrs = ("fake_model",)

    fake_model: FakeModel = "contrib.clean_architecture.tests.fakes.general.models.FakeModel"

    def _get(
        self,
        code: str,
        code_type: FakeExternalCodeType,
        model_type: type[FakeModel] | FakeModel,
    ):
        if isinstance(model_type, self.fake_model):
            model_type = model_type.__class__

        kwargs = {"code": code, "code_type": code_type, "content_type": model_type}
        return self.get(**kwargs)

    def get_object(
        self,
        code: str,
        code_type: FakeExternalCodeType,
        model_type: type[FakeModel] | FakeModel,
    ):
        return self._get(code=code, code_type=code_type, model_type=model_type).content_object

    def get_object_id(
        self,
        code: str,
        code_type: FakeExternalCodeType,
        model_type: type[FakeModel] | FakeModel,
    ):
        return self._get(code=code, code_type=code_type, model_type=model_type).object_id

    def create(self, content_object: Any = None, **kwargs):
        if content_object:
            kwargs["object_id"] = content_object.id
            kwargs["content_type"] = content_object.__class__
        return super().create(**kwargs)


class FakeM2MManager(IM2MManager):
    @classmethod
    def execute(cls, instance: FakeModel, field: str, actions: list[M2MUpdateAction]) -> None:
        pass
