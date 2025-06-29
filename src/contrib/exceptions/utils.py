from __future__ import annotations

from contrib.exceptions.bases import BaseHTTPException
from contrib.exceptions.exceptions import InvalidCredentials
from contrib.exceptions.exceptions import NotHandledError
from contrib.exceptions.exceptions import PermissionDenied
from contrib.exceptions.exceptions import ValidationError


def responses_from_exceptions(*exceptions: type[BaseHTTPException], with_default_errors=True) -> dict:
    """Возвращает схемы ответа ошибки для отображения в документации API

    Args:
        *exceptions: Кортеж исключений
        with_default_errors: Добавить стандартные ошибки

    Returns:
        Маппинг исключений и схем ответов

    """
    if with_default_errors:
        exceptions = (
            *exceptions,
            ValidationError,
            InvalidCredentials,
            PermissionDenied,
            NotHandledError,
        )
    return dict(map(lambda exception: exception.get_openapi_response(), exceptions))
