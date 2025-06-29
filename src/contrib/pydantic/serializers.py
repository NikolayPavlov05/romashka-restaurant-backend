from datetime import date
from typing import Literal

from pydantic import PlainSerializer


def date_to_string(
    _format: str = "%Y.%m.%dT%H:%M:%S",
    when_used: Literal["always", "unless-none", "json", "json-unless-none"] = "always",
):
    def _string_from_datetime(value: date | None) -> str | None:
        if value is None:
            return
        return value.strftime(_format)

    return PlainSerializer(_string_from_datetime, return_type=str, when_used=when_used)


def _list_to_string(value: list | None):
    if value is None:
        return
    return ",".join(map(lambda x: str(x), value))


list_to_string = PlainSerializer(_list_to_string, return_type=str, when_used="always")
