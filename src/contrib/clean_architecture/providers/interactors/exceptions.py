"""Модуль с исключениями для репозиториев

Classes:
    NothingToUpdateOrCreateException: Не переданы поля с данными

"""
from __future__ import annotations

from contrib.exceptions.exceptions import BaseHTTPException
from contrib.localization.services import gettext as _
from rest_framework import status


class NothingToUpdateOrCreateException(BaseHTTPException):
    """Не переданы поля с данными"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = _("Нельзя обновить или создать объект без полей с данными")
    error_code = "nothing_to_update_or_create"
