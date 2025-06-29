from __future__ import annotations

from contrib.context import get_root_context


class _FooRequest:
    def __init__(self, user):
        self.user = user


def set_user_context(user):
    context = get_context()
    request = _FooRequest(user)
    context.set("request", request)


def get_context():
    context = get_root_context()
    if not context.initialized:
        context.init_context()
    return context


def clear_context():
    context = get_root_context()
    if context.initialized:
        context.clear()
