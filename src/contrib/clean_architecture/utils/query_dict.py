from __future__ import annotations

from collections.abc import Callable
from typing import TypedDict


class Wrappers(TypedDict):
    """Wrappers."""

    condition: Callable
    find: Callable


class BaseFilter:
    """Filter."""

    wrapper_name: str = ""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def parse(self, wrappers: Wrappers) -> any:
        return wrappers[self.wrapper_name](*self.args, **self.kwargs)


class FindFilter(BaseFilter):
    """Find."""

    wrapper_name: str = "find"


def parse_query_dict(ident: str, data: any, wrappers: Wrappers):
    """Метод для парсинга dict из запросов."""
    if type(data) is not dict:
        # Выход
        if isinstance(data, BaseFilter):
            data = data.parse(wrappers)
        if ident.startswith("~"):
            return ~wrappers["condition"](**{ident.replace("~", ""): data})
        return wrappers["condition"](**{ident: data})

    summary_query = wrappers["condition"]()
    for key in data:
        if ident.endswith("__or"):
            # OR
            summary_query |= wrappers["condition"](parse_query_dict(key, data[key], wrappers))
        else:
            # DEFAULT: AND
            summary_query &= wrappers["condition"](parse_query_dict(key, data[key], wrappers))

    if ident.startswith("~"):
        return ~wrappers["condition"](summary_query)
    return summary_query
