from __future__ import annotations

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from .root_context import get_root_context


class ContextMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        ctx = get_root_context()
        ctx.init_context()
        ctx.set("request", request)
