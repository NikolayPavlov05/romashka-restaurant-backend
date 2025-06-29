from __future__ import annotations


class PostInitMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj
