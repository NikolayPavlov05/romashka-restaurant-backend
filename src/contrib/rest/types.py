from __future__ import annotations

from typing import Any
from typing import TypedDict

from requests.auth import AuthBase

MERGED_REQUEST_KWARGS = {
    "paths",
    "body",
    "headers",
    "params",
    "files",
    "cookies",
    "proxies",
    "hooks",
}
DEFAULT_REQUEST_KWARGS = {
    "json",
    "data",
    "auth",
    "timeout",
    "allow_redirects",
    "raise_exceptions",
    "stream",
    "verify",
    "cert",
}


class MergedRequestKwargs(TypedDict, total=False):
    paths: dict[str, Any] | None
    body: dict[str, Any] | None
    headers: dict[str, Any] | None
    params: dict[str, Any] | None
    files: dict[str, Any] | None
    cookies: dict[str, str] | None
    proxies: dict[str, str] | None
    hooks: dict[str, str] | None


class DefaultRequestKwargs(TypedDict, total=False):
    data: Any | None
    json: str | None
    auth: tuple[str, str] | AuthBase | None
    timeout: int | tuple[int, int] | None
    allow_redirects: bool | None
    raise_exceptions: bool | None
    stream: bool | None
    verify: bool | None
    cert: str | tuple[str, str] | None


class RequestKwargs(MergedRequestKwargs, DefaultRequestKwargs, total=False):
    extra: dict | None
