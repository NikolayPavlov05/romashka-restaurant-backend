from __future__ import annotations

from pydantic import BaseModel


class RedisContext(BaseModel):
    namespace: str | None = None
    expire_time: int | None = None
