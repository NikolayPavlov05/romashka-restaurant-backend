from __future__ import annotations

import pickle
from typing import Any


def redis_decode(data: dict | tuple | list | bytes) -> Any:
    if isinstance(data, bytes):
        try:
            value = pickle.loads(data)
        except (KeyError, pickle.UnpicklingError):
            value = data.decode()
        return value

    if isinstance(data, dict):
        return dict(map(redis_decode, data.items()))

    if isinstance(data, (tuple, list)):
        return map(redis_decode, data)

    return data


def redis_encode(data: Any, mapping=False, items=False):
    if data is None:
        return
    if mapping:
        return dict(zip(data, map(lambda x: pickle.dumps(x), data.values())))
    if items:
        return map(lambda x: (x[0], redis_encode(x[1])), data)

    return pickle.dumps(data)
