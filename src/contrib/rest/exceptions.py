from __future__ import annotations

from contrib.exceptions.bases import BaseHTTPException
from contrib.localization.services import gettext as _
from rest_framework import status


class RestMaxRetriesException(BaseHTTPException):
    """Превышено максимальное количество попыток запроса"""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = _("Превышено максимальное количество попыток запроса {message}")
    error_code = "rest_max_retries_exception"


class RestRequestException(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = _("Ошибка взаимодействия: {message}")
    error_code = "rest_request_error"
