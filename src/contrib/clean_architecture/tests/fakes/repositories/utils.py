from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from functools import wraps

import contrib.clean_architecture
from contrib.clean_architecture.interfaces import IPrefetch
from contrib.clean_architecture.tests.fakes.general.managers import _fake_instances
from contrib.clean_architecture.tests.fakes.general.managers import FakeManager

BASE_REPLACES = {" ": "", "'": "", '"': "", "\t": "", "\n": "", "\\": ""}


def fake_search_filter(objects: FakeManager, search: str, *expressions, **extra_replaces):
    replaces = {**BASE_REPLACES, **extra_replaces}
    search = "".join(search.split())

    if not expressions:
        return objects

    for old, new in replaces.items():
        search = search.replace(old, new)

    def _search_filter(item):
        item_string = ""
        for _expression in expressions:
            item_string += str(getattr(item, _expression))
        for _old, _new in replaces.items():
            item_string = item_string.replace(old, new)

        return search in item_string

    return objects.search(_search_filter)


class FakeAtomic:
    _instances = None

    def __enter__(self):
        self._instances = deepcopy(_fake_instances)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            contrib.clean_architecture.tests.fakes.general.managers._fake_instances.clear()
            contrib.clean_architecture.tests.fakes.general.managers._fake_instances.update(self._instances)


def fake_atomic(target: Callable = None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with FakeAtomic():
                return function(*args, **kwargs)

        return wrapper

    if isinstance(target, Callable):
        return decorator(target)
    else:
        return decorator


class FakePrefetch(IPrefetch):
    def __init__(self, lookup, queryset=None):
        self.prefetch_through = lookup
        self.prefetch_to = lookup
        self.queryset = queryset

    def __eq__(self, other):
        if not isinstance(other, FakePrefetch):
            return NotImplemented
        return self.prefetch_to == other.prefetch_to

    def __hash__(self):
        return hash((self.__class__, self.prefetch_to))
