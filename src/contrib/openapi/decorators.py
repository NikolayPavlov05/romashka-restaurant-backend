"""Модуль кастомных Actions для ViewSet

Functions:
    action: Отмечает метод ViewSet как маршрутизируемое действие (action)
    endpoint_permissions: Навешивает разрешения на декорируемую функцию

"""
from __future__ import annotations

from collections.abc import Callable
from collections.abc import Sequence
from functools import wraps
from typing import Any
from typing import get_type_hints

from contrib.clean_architecture.interfaces import RequestDTO
from contrib.inspect.services import sequence_type_check
from contrib.pydantic.model import PydanticModel
from contrib.pydantic.model import ResultIdDTO
from django.core.files import File
from django.http import HttpRequest
from django.http import HttpResponse
from pydantic import BaseModel
from rest_framework.decorators import action as rest_action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response


def _dump_response_model_function(
    response: Response | HttpResponse, response_type: Any = None
) -> Response | HttpResponse:
    """Получить словарь из модели при формировании ответа

    Args:
        response:
        response_type: Тип отпета

    Returns:
        response

    """
    is_response = False
    content_attr = None
    if isinstance(response, (Response, HttpResponse)):
        content_attr = "data" if isinstance(response, Response) else "content"
        is_response = True

    data = getattr(response, content_attr) if is_response else response

    if isinstance(data, (int, str)) and response_type is ResultIdDTO:
        data = ResultIdDTO(id=data)

    if isinstance(data, BaseModel):
        data = data.model_dump()
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        data = map(
            lambda item: item.model_dump() if isinstance(item, BaseModel) else item,
            data,
        )

    if is_response:
        setattr(response, content_attr, data)
    else:
        response = Response(data)

    return response


def _extract_payload(request: Request, request_model: type[PydanticModel]):
    """Получить данные

    Args:
        request: Запрос
        request_model: Модель

    Returns:
        PydanticModel
    """
    if request.method in ("GET", "DELETE"):
        return request_model(**request.query_params.dict())
    return request_model(**request.data.copy())


def _get_payload_attr(hints: dict, request_model: type[PydanticModel]) -> str:
    """Получить атрибут, в который нужно записать данные запроса

    Args:
        hints: Аннотации типов
        request_model: Модель

    Returns:
        arg_name

    """
    for arg_name, hint in hints.items():
        if hint is request_model or hint is RequestDTO:
            return arg_name


def _extract_files(request: Request, files_schema):
    """Получить файл из запроса

    Args:
        request: Запрос
        files_schema: Схема для медиафайлов

    Returns:

    """
    files = {}
    files_keys = request.FILES.keys()
    files_data = {**request.FILES}
    for name, value in files_schema["properties"].items():
        if name not in files_keys:
            files[name] = None
        elif value["type"] == "array":
            files[name] = files_data[name]
        elif isinstance(files_data[name], Sequence):
            files[name] = files_data[name][0]
        else:
            files[name] = files_data[name]
    return files


def _get_files_schema(hints: dict) -> dict | None:
    """Получить схему для медиафайлов

    Args:
        hints: Аннотации типов

    Returns:
        schema
    """
    schema = {"properties": {}, "type": "object"}

    for arg_name, hint in hints.items():
        is_sequence, origin_type = sequence_type_check(hint)
        if not isinstance(origin_type, type) or not issubclass(origin_type, File):
            continue

        if is_sequence:
            schema["properties"][arg_name] = {
                "type": "array",
                "items": {"type": "string", "format": "binary"},
            }
        else:
            schema["properties"][arg_name] = {"type": "string", "format": "binary"}

    if not schema["properties"]:
        return

    return schema


def action(
    methods: list[str] | None = None,
    detail: bool | None = False,
    url_path: str | None = None,
    url_name: str | None = None,
    request_model: type[PydanticModel] = None,
    response_schema: type[PydanticModel] | None = None,
    responses: dict[int, dict] | None = None,
    status_map: dict[str, int] | None = None,
    description: str | None = None,
    summary: str | None = None,
    tags: list[str] = None,
    action_wrapper: Callable | None = rest_action,
    auto_validate: bool | None = True,
    dump_response_model: bool | None = True,
    permission_classes: list[type[BasePermission]] | None = None,
    mapped=False,
    **action_kwargs,
):
    """Отмечает метод ViewSet как маршрутизируемое действие (action).

    Notes:
        * Функции, декорируемые @action, будут наделены свойством `mapping`, `MethodMapper`,
        которое можно использовать для добавления дополнительных поведений на основе методов к маршрутизируемому действию.

        * По сути, декоратор расширяет функционал стандартного декоратора`rest_framework.decorators.action`
        (он используется по умолчанию и может быть переопределен).

    Notes:
        * Если в аргументах функции указан аргумент, типизированный аналогичной моделью `request_model`,
        то в этот аргумент будет помещен экземпляр провалидированной модели тела запроса.

    Args:
        methods: Список имен HTTP-методов, на которые реагирует это действие. По умолчанию только GET.
        detail: Определяет, применимо ли это действие к запросам экземпляров или коллекций
        url_path: Определить сегмент URL для этого действия. По умолчанию используется имя декорированного метода
        url_name: Определить внутренний («обратный») URL-адрес для этого действия. По умолчанию имя метода все знаки подчеркивания заменяются тире.
        request_model: Модель для валидации тела запроса и преобразования аргументов
        response_schema: Модель данных ответа. Используется для документации
        responses: Ответы по кодам
        status_map: Маппинг кодов http-статусов успешных ответов для различных входящих методов
        description: Описание роута
        summary: Краткое описание роута
        tags: Теги
        action_wrapper: Функция обертка для декорирования метода по умолчанию используется (rest_framework.decorators.action)
        auto_validate: Флаг переключения необходимости валидации данных
        dump_response_model: Вызывать model_dump если функция возвращает BaseModel | Sequence[BaseModel]
        permission_classes: Классы прав доступа
        mapped: Основан на другом методе
        **action_kwargs: Дополнительные свойства, которые можно установить в представлении

    Returns:
        Callable

    """

    def decorator(function):
        _action_kwargs = dict(
            methods=methods,
            detail=detail,
            url_path=url_path,
            url_name=url_name,
            **action_kwargs,
        )
        if permission_classes is not None:
            _action_kwargs["permission_classes"] = permission_classes

        if not mapped:
            function = action_wrapper(**_action_kwargs)(function)

        hints = get_type_hints(function)

        function.request_schema = request_model
        function.request_schema_files = _get_files_schema(hints)
        function.response_schema = response_schema
        function.status_map = status_map
        function.summary = summary
        function.tags = tags
        function.responses = responses
        function.permission_classes = permission_classes

        if not function.__doc__:
            function.__doc__ = description

        @wraps(function)
        def wrapper(self, request: Request, *args, **kwargs):
            if request_model is not None and auto_validate:
                payload = _extract_payload(request, request_model)
                if payload_attr := _get_payload_attr(hints, request_model):
                    kwargs[payload_attr] = payload

            if function.request_schema_files:
                kwargs.update(_extract_files(request, function.request_schema_files))

            if hints.get("response_schema"):
                kwargs["response_schema"] = response_schema

            result = function(self, request, *args, **kwargs)
            if dump_response_model:
                result = _dump_response_model_function(result, response_schema)

            if function.status_map and request.method in function.status_map:
                result.status_code = function.status_map[request.method]
            return result

        return wrapper

    return decorator


def endpoint_permissions(*permissions) -> Callable:
    """Навешивает разрешения на декорируемую функцию"""

    def decorator(endpoint: Callable) -> Callable:
        @wraps(endpoint)
        def wrapped(self, request: HttpRequest, *args, **kwargs):
            for permission_class in permissions:
                permission = permission_class()
                if not permission.has_permission(request, self):
                    self.permission_denied(
                        request,
                        message=getattr(permission, "message", None),
                        code=getattr(permission, "code", None),
                    )

            return endpoint(self, request, *args, **kwargs)

        return wrapped

    return decorator
