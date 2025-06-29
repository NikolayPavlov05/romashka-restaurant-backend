"""Модуль утилит для работы с кастомной моделью Pydantic

Functions:
    validation_error_format: Форматирует ошибки валидации
    convert: Преобразует типы
    translated_fields: Возвращает поля с переводами

"""
from __future__ import annotations

from copy import deepcopy
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING

from django.conf import settings
from pydantic import Field
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from contrib.pydantic.model import PydanticModel


def convert(
    to_type: Any,
    obj: Any,
    *,
    strict: bool = None,
    from_attributes: bool = None,
    context: dict[str, Any] = None,
    mode: Literal["python", "json", "string"] = "python",
):
    """Преобразует типы

    Args:
        to_type: К какому типу нужно привести
        obj: Какой тип приводится
        strict: Следует ли строго соблюдать типы
        from_attributes: Получать значения из атрибутов
        context: Контекст
        mode: Тип преобразования

    Returns:

    """
    adapter = TypeAdapter(to_type)
    match mode:
        case "python":
            return adapter.validate_python(obj, from_attributes=from_attributes, strict=strict, context=context)
        case "json":
            return adapter.validate_json(obj, strict=strict, context=context)
        case "string":
            return adapter.validate_strings(obj, strict=strict, context=context)


def translated_fields(*attrs: str, languages: tuple[tuple[str, str]] = settings.LANGUAGES):
    """Возвращает поля с переводами

    Args:
        *attrs: Атрибуты полей с переводами
        languages: Кортеж языков

    Returns:
        Callable

    """

    def decorator(model: PydanticModel):
        if not settings.USE_I18N:
            return model

        field_definitions = {}
        for field_name, field_info in model.model_fields.items():
            if field_name not in attrs:
                continue

            for lang, _ in languages:
                field_info = deepcopy(field_info)
                new_field_info = Field()
                for slot_name in field_info.__slots__:
                    setattr(new_field_info, slot_name, getattr(field_info, slot_name))

                new_field_info.title += f" ({lang})"
                translated_field_name = f"{field_name}_{lang}"
                field_definitions[translated_field_name] = new_field_info

        model.add_fields(**field_definitions)
        return model

    return decorator
