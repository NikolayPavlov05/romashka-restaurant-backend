"""Модуль с константами модуля

Classes:
    CleanMethods: Названия методов базовых миксинов модуля
    ViewActionAttrs: Названия основных атрибутов представления
    ReturnTypeAttrs: Типы возвращаемых DTO
    RepositoryMethodAttrs: Названия основных атрибутов методов репозиториев

"""
from __future__ import annotations


class CleanMethods:
    """Названия методов базовых миксинов модуля"""

    CREATE = "create"
    UPDATE = "update"
    UPDATE_OR_CREATE = "update_or_create"
    DETAIL_OR_CREATE = "detail_or_create"
    DELETE = "delete"
    DETAIL = "detail"
    DETAIL_BY_PK = "detail_by_pk"
    DETAIL_BY_EXTERNAL_CODE = "detail_by_external_code"
    RETRIEVE = "retrieve"
    SEARCH = "search"
    COUNT = "count"
    SEARCH_COUNT = "search_count"
    EXISTS = "exists"
    EXPORT_XLS = "export_xls"
    BULK_CREATE = "bulk_create"
    BULK_DELETE = "bulk_delete"
    BULK_UPDATE = "bulk_update"
    PATCH_LIST = "patch_list"
    MULTI_UPDATE = "multi_update"
    GET_SOLO = "get_solo"


class ViewActionAttrs:
    """Названия основных атрибутов представления"""

    METHODS = "methods"
    URL_PATH = "url_path"
    URL_NAME = "url_name"
    REQUEST_MODEL = "request_model"
    RESPONSE_SCHEMA = "response_schema"
    RESPONSES = "responses"
    STATUS_MAP = "status_map"
    DESCRIPTION = "description"
    SUMMARY = "summary"
    PERMISSIONS = "permissions"
    TAGS = "tags"
    EXTRA_KWARGS = "extra_kwargs"
    DECORATORS = "decorators"


class ReturnTypeAttrs:
    """Типы возвращаемых DTO"""

    RETURN_TYPE = "return_type"
    RETURN_DETAIL_TYPE = "return_detail_type"
    RETURN_PAGINATION_TYPE = "return_pagination_type"


class RepositoryMethodAttrs:
    """Названия основных атрибутов методов репозиториев"""

    ATOMIC = "atomic"
    CONVERT_RETURN = "convert_return"
    CONVERT_PATH = "convert_path"
    EXCEPTIONS_REDIRECTS = "exceptions_redirects"
