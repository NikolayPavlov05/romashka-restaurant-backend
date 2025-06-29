from __future__ import annotations

import importlib


def import_by_string(import_string: str):
    module, target = import_string.rsplit(".", 1)
    module = importlib.import_module(module)
    return getattr(module, target)
