from __future__ import annotations

import re
from collections.abc import Sequence
from contextlib import suppress
from typing import Any
from typing import Literal

from contrib.clean_architecture.utils.names import to_pascale_case
from contrib.exceptions.bases import HTTPExceptionManager
from contrib.pydantic.schema_generator import AdaptedGenerateJsonSchema
from django.shortcuts import render
from django.utils.encoding import smart_str
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from rest_framework import exceptions
from rest_framework import renderers
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import coreapi
from rest_framework.schemas.openapi import AutoSchema as AutoSchemaBase
from rest_framework.schemas.utils import is_list_view
from rest_framework.settings import api_settings
from rest_framework.utils import formatting
from rest_framework.views import APIView

_MAX_SUMMARY_LENGTH = 100


class DefaultAutoSchema(AutoSchemaBase):
    def get_method_attr(self, method_name, attr, default=None):
        view = self.view

        method_name = getattr(view, "action", method_name.lower())
        method = getattr(view, method_name, None)
        return getattr(method, attr, None) if method else default

    def get_tags(self, path, method):
        tags = self.get_method_attr(method, "tags")
        if tags:
            return list(map(lambda tag: str(tag), tags))

        if self._tags:
            return self._tags

        if path.startswith("/api/v"):
            path = re.sub(r"/api/v\d+/", "", path)
        elif path.startswith("/"):
            path = path[1:]

        return [path.split("/")[0].replace("_", "-")]


class AutoSchema(DefaultAutoSchema):
    def __init__(self, tags=None, operation_id_base=None, component_name=None):
        if tags:
            tags = list(map(lambda tag: str(tag), tags))
        super().__init__(
            tags=tags,
            operation_id_base=operation_id_base,
            component_name=component_name,
        )

    def _get_action(self):
        view = self.view
        method_name = getattr(view, "action", None)
        if method_name is not None:
            return getattr(view, method_name, None)

    @property
    def _create_dto_name_from_action(self):
        view_name = re.sub(r"ViewSet$", "", self.view.__class__.__name__)
        view_name = re.sub(r"View$", "", view_name)
        return f"{view_name}{to_pascale_case(getattr(self.view, 'action', None))}DTO"

    def get_request_schema_files(self):
        action = self._get_action()
        if action:
            return getattr(action, "request_schema_files", None)

    def _get_action_serializer(self, type_serializer: Literal["request", "response"]):
        action = self._get_action()
        if action:
            if type_serializer == "request":
                serializer = getattr(action, "request_schema", None)
            elif type_serializer == "response":
                serializer = getattr(action, "response_schema", None)
            else:
                raise ValueError("Request type is not supports")
            return serializer

    def map_serializer(self, serializer: BaseModel):
        required = []
        properties = {}

        for field_name, field in serializer.model_fields.items():
            if field_name.startswith("_"):
                continue

            schema = self.map_field(field)

            is_field_required = field.is_required()
            if is_field_required:
                required.append(field_name)

            schema["nullable"] = not is_field_required

            if field.default is not None and field.default != PydanticUndefined and not callable(field.default):
                schema["default"] = field.default
            if field.title:
                schema["description"] = str(field.title)

            properties[field_name] = schema

        result = {"type": "object", "properties": properties}
        if required:
            result["required"] = required

        return result

    def _get_model_schema(self, model: BaseModel) -> dict[str, Any]:
        return model.model_json_schema(
            ref_template="#/components/schemas/{model}",
            schema_generator=AdaptedGenerateJsonSchema,
        )

    def get_operation_parameters_from_request_schema(self, request_schema: BaseModel):
        schema = self._get_model_schema(request_schema)
        required = set(schema.get("required", []))
        return [
            {
                "name": name,
                "required": name in required,
                "in": "query",
                "description": prop.get("title", ""),
                "schema": prop,
            }
            for name, prop in schema["properties"].items()
        ]

    def get_serializer(self, path, method, type_serializer: Literal["request", "response"] = "request"):
        return self._get_action_serializer(type_serializer)

    def get_summary(self, method):
        summary = self.get_method_attr(method, "summary")
        if summary:
            return self._get_description_section(self.view, method.lower(), formatting.dedent(smart_str(summary)))[
                :_MAX_SUMMARY_LENGTH
            ]

    def get_security(self):
        action = self._get_action()
        if action.permission_classes and AllowAny not in action.permission_classes:
            return True
        if self.view.__class__.permission_classes and AllowAny not in self.view.__class__.permission_classes:
            return True
        return False

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation["summary"] = self.get_summary(method) or operation["description"][:_MAX_SUMMARY_LENGTH]
        if method.lower() in {"get", "delete"}:
            request_serializer = self._get_action_serializer("request")
            if request_serializer:
                operation["parameters"].extend(self.get_operation_parameters_from_request_schema(request_serializer))
        if self.get_security():
            operation["security"] = [{"Token Auth": []}]

        return operation

    def _build_components(self, components: dict, serializer, extra_schema=None):
        component_name = self.get_component_name(serializer)
        schema = self._get_model_schema(serializer)
        if extra_schema:
            schema["properties"].update(extra_schema["properties"])

        components.setdefault(component_name, schema)
        for item_name, def_item in schema.pop("$defs", {}).items():
            components.setdefault(item_name, def_item)

    def get_components(self, path, method):
        if method.lower() == "delete":
            return {}

        request_serializer = self.get_request_serializer(path, method)
        response_serializer = self.get_response_serializer(path, method)

        request_schema_files = self.get_request_schema_files()

        components = {}
        if request_serializer and issubclass(request_serializer, BaseModel):
            self._build_components(components, request_serializer, extra_schema=request_schema_files)
        elif request_schema_files:
            components[self._create_dto_name_from_action] = request_schema_files

        if getattr(response_serializer, "__args__", None) and issubclass(response_serializer.__origin__, Sequence):
            response_serializer = response_serializer.__args__[0]
        if response_serializer and issubclass(response_serializer, BaseModel):
            self._build_components(components, response_serializer)

        return components

    def get_component_name(self, serializer) -> str:
        return serializer.__name__

    def get_request_body(self, path, method):
        if method not in ("PUT", "PATCH", "POST"):
            return {}

        has_files = bool(self.get_request_schema_files())

        request_media_types = self.map_parsers(path, method)
        if has_files:
            with suppress(ValueError):
                request_media_types.remove("multipart/form-data")
            request_media_types.insert(0, "multipart/form-data")

        self.request_media_types = request_media_types
        component_name = None
        serializer = self.get_request_serializer(path, method)

        if not serializer:
            if not has_files:
                return {}
            component_name = self._create_dto_name_from_action
        item_schema = self.get_reference(serializer, component_name)
        return {"content": {ct: {"schema": item_schema} for ct in self.request_media_types}}

    def get_reference(self, serializer=None, component_name=None):
        component_name = component_name or self.get_component_name(serializer)
        return {"$ref": f"#/components/schemas/{component_name}"}

    def get_request_serializer(self, path, method):
        return self.get_serializer(path, method, "request")

    def get_response_serializer(self, path, method):
        return self.get_serializer(path, method, "response")

    def get_status_map(self):
        default_status_map = {
            "DELETE": status.HTTP_204_NO_CONTENT,
            "POST": status.HTTP_201_CREATED,
        }
        action = self._get_action()
        if action:
            status_map = getattr(action, "status_map", None)
        else:
            status_map = getattr(self.view, "status_map", None)

        if status_map:
            status_map = {k.upper(): v for k, v in dict(status_map).items()}
            default_status_map.update(status_map)
        return default_status_map

    def get_response_status_code(self, method):
        status_map = self.get_status_map()
        return status_map.get(method, status.HTTP_200_OK)

    def get_responses(self, path, method):
        responses = self.get_method_attr(method, "responses", {}) or {}
        if method == "DELETE":
            return {"204": {"description": ""}, **responses}
        self.response_media_types = self.map_renderers(path, method)
        serializer = self.get_response_serializer(path, method)

        is_sequence_response = False
        if getattr(serializer, "__args__", None) and issubclass(serializer.__origin__, Sequence):
            serializer = serializer.__args__[0]
            is_sequence_response = True

        if serializer and issubclass(serializer, BaseModel):
            item_schema = self.get_reference(serializer)
        else:
            item_schema = {}
        if is_list_view(path, method, self.view) or is_sequence_response:
            response_schema = {"type": "array", "items": item_schema}
            paginator = self.get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(response_schema)
        else:
            response_schema = item_schema
        status_code = self.get_response_status_code(method)
        return {
            str(status_code): {
                "content": {ct: {"schema": response_schema} for ct in self.response_media_types},
                # description is a mandatory property,
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#responseObject
                # TODO: put something meaningful into it
                "description": "",
            },
            **responses,
        }


class SchemaView(APIView):
    _ignore_model_permissions = True
    schema = None  # exclude from schema
    renderer_classes = None
    schema_generator = None
    public = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.renderer_classes is None:
            if coreapi.is_enabled():
                self.renderer_classes = [
                    renderers.CoreAPIOpenAPIRenderer,
                    renderers.CoreJSONRenderer,
                ]
            else:
                self.renderer_classes = [
                    renderers.OpenAPIRenderer,
                    renderers.JSONOpenAPIRenderer,
                ]
            if renderers.BrowsableAPIRenderer in api_settings.DEFAULT_RENDERER_CLASSES:
                self.renderer_classes += [renderers.BrowsableAPIRenderer]

    def get(self, request, *args, **kwargs):
        schema = self.schema_generator.get_schema(request, self.public)

        errors_components = {}
        for error in HTTPExceptionManager.get_objects():
            error_schema = error.get_schema()
            errors_components.setdefault(error.__name__, error_schema)
            for item_name, def_item in error_schema.pop("$defs", {}).items():
                errors_components.setdefault(item_name, def_item)

        if schema is None:
            raise exceptions.PermissionDenied()

        if schema.get("components"):
            schema["components"]["schemas"].update(errors_components)
            schema["components"]["securitySchemes"] = {
                "Token Auth": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                }
            }
        schema["paths"] = {path: methods for path, methods in sorted(schema["paths"].items(), key=lambda x: x[0])}
        return Response(schema)

    def handle_exception(self, exc):
        self.renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
        neg = self.perform_content_negotiation(self.request, force=True)
        self.request.accepted_renderer, self.request.accepted_media_type = neg
        return super().handle_exception(exc)


def redoc_view(request, schema_url):
    return render(request, "redoc_ui/redoc_ui.html", {"schema_url": schema_url})


def swagger_view(request, schema_url):
    return render(request, "swagger_ui/swagger_ui.html", {"schema_url": schema_url})
