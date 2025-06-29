from __future__ import annotations

from contrib.exceptions.bases import BaseHTTPException
from contrib.localization.services import gettext_lazy as _
from contrib.pydantic.model import ValidationErrorItemDTO
from rest_framework import status


class InvalidCredentials(BaseHTTPException):
    """Неверные учетные данные"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = _("Неверные учетные данные")
    error_code = "invalid_credentials"


class PermissionDenied(BaseHTTPException):
    """Доступ запрещен"""

    status_code = status.HTTP_403_FORBIDDEN
    detail = _("Доступ запрещен")
    error_code = "permission_denied"


class ThrottledRequest(BaseHTTPException):
    """Запрос отклонён."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = _("Запрос был отклонен. Повторный запрос возможен через {message} сек.")
    error_code = "throttled"


class DoesNotExist(BaseHTTPException):
    """Запись не найдена"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = _("Запись не найдена")
    error_code = "does_not_exists"


class MultipleObjectsReturnedExist(BaseHTTPException):
    """Найдено более одной записи"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = _("Найдено более одной записи")
    error_code = "multiple_objects_return"


class ActionImpossible(BaseHTTPException):
    """Действие невозможно"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = _("Действие невозможно: {message}")
    error_code = "action_impossible"


class WrongValue(ActionImpossible):
    detail = _("Неверное значение")
    error_code = "wrong_value"


class InactiveUser(ActionImpossible):
    detail = _("Пользователь не активен")
    error_code = "inactive_user"


class ValidationError(BaseHTTPException):
    """Ошибка валидации"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = _("Ошибка валидации")
    error_code = "validation_error"
    error_item_type = ValidationErrorItemDTO
    contains_errors = True


class SimpleValidationError(BaseHTTPException):
    """Не корректные данные"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = _("Не корректные данные")
    error_code = "simple_validation_error"


class NotHandledError(BaseHTTPException):
    """Ошибка на сервере"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = _("Ошибка на сервере: {message}")
    error_code = "not_handled_error"
