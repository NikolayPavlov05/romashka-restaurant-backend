"""Модуль с утилитами для представлений

Functions:
    exception_handler: Хэндлер для обработки ошибок

"""
from __future__ import annotations

import logging
import traceback

from django.conf import settings
from contrib.exceptions.bases import BaseHTTPException
from contrib.exceptions.exceptions import InvalidCredentials
from contrib.exceptions.exceptions import NotHandledError
from contrib.exceptions.exceptions import PermissionDenied
from contrib.exceptions.exceptions import ThrottledRequest
from contrib.exceptions.exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import NotAuthenticated as RestNotAuthenticated
from rest_framework.exceptions import PermissionDenied as RestPermissionDenied
from rest_framework.exceptions import Throttled
from rest_framework.response import Response


def exception_handler(exc: Exception, context) -> Response:
    """Хэндлер для обработки ошибок

    Args:
        exc: Экземпляр исключения
        context: Контекст ошибки

    Returns:
        Response

    """
    # Печатаем трассировку ошибки
    if settings.PRINT_API_EXCEPTIONS:
        traceback.print_tb(exc.__traceback__)
    # Производим маппинг дефолтных ошибок на кастомные
    if isinstance(exc, PydanticValidationError):
        exc = ValidationError(errors=exc.errors())
    elif isinstance(exc, RestNotAuthenticated):
        exc = InvalidCredentials()
    elif isinstance(exc, RestPermissionDenied):
        exc = PermissionDenied()
    elif isinstance(exc, Throttled):
        exc = ThrottledRequest(message=str(exc.wait))
    elif not isinstance(exc, BaseHTTPException):
        exc = NotHandledError(message=f"{exc.__class__.__name__}: {exc}")
        logging.error(exc, exc_info=True)

    return exc.response
