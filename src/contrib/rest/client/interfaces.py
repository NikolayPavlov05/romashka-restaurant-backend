from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Self

    from contrib.rest.client.bases import RestMethod
    from contrib.rest.config import RestConfig
    from contrib.rest.models import RestLog


class IRestClient(ABC):
    logger: logging.Logger = None
    model_logger: type[RestLog] = None

    @classmethod
    @abstractmethod
    def build_client(
        cls,
        config: RestConfig = None,
        *,
        logger: str | logging.Logger,
        model_logger: type[RestLog] = None,
        **kwargs: Any,
    ) -> Self: ...

    def make_request(
        self,
        method: RestMethod,
        *,
        raise_exceptions: bool = True,
        __retry_number: int = 0,
        **kwargs,
    ): ...

    @abstractmethod
    def logging(
        self,
        message: str = None,
        traceback: str = None,
        params: dict[str, Any] = None,
        response: Any = None,
        method: RestMethod = None,
    ): ...

    @property
    @abstractmethod
    def config(self) -> RestConfig | None: ...
