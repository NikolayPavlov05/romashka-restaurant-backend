"""Модуль с утилитами для репозиториев

Functions:
    search_filter: Функция поиска подстроки для django

"""
from __future__ import annotations

from django.db.models import CharField
from django.db.models import Value
from django.db.models.functions import Cast
from django.db.models.functions import Concat
from django.db.models.functions import Replace

BASE_REPLACES = {" ": "", "'": "", '"': "", "\t": "", "\n": "", "\\": ""}
"""Стандартные замены"""


def search_filter(objects, search: str, *expressions, **extra_replaces):
    """Функция поиска подстроки для django

    Args:
        objects: QuerySet
        search: Строка поиска
        *expressions: Поля или выражения запроса ORM
        **extra_replaces: Дополнительные замены

    Returns:
        QuerySet

    """
    if not expressions:
        return objects

    replaces = {**BASE_REPLACES, **extra_replaces}
    search = "".join(search.split())

    if len(expressions) > 1:
        expression = Concat(*(Cast(expression, CharField()) for expression in expressions))
    else:
        expression = Cast(expressions[0], CharField())

    for old, new in replaces.items():
        search = search.replace(old, new)
        expression = Replace(expression, Value(old), Value(new))

    return objects.annotate(search=expression).filter(search__icontains=search)
