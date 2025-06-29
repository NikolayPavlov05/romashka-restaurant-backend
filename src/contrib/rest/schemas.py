from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from json import JSONDecodeError
from typing import ClassVar
from typing import Generic
from typing import TypeVar

import xmltodict
from contrib.pydantic.model import PydanticModel
from pydantic import Field
from pydantic import HttpUrl
from pydantic import model_validator
from requests import Response

DataType = TypeVar("DataType")


class RestMethodResponse(PydanticModel, Generic[DataType], proxy_model=True):
    result: ClassVar[DataType | HttpUrl | None]

    ok: bool
    status_code: int

    @cached_property
    def text(self) -> str:
        return self.original_object.text

    @cached_property
    def content(self) -> bytes:
        return self.original_object.content


class RestDataMixin(Generic[DataType]):
    data: DataType | None = Field(None, alias="_data")

    @property
    def result(self) -> DataType | None:
        return self.data

    @classmethod
    @abstractmethod
    def extract_data(cls, response: Response) -> Response: ...


class RestRedirectMixin:
    ok: bool | None = None
    status_code: int | None = None

    url: HttpUrl | None = None

    @property
    def result(self) -> HttpUrl | None:
        return str(self.url) if self.url else None


class JsonResponse(RestMethodResponse[DataType], RestDataMixin[DataType], Generic[DataType]):
    @model_validator(mode="before")
    @classmethod
    def extract_data(cls, response: Response | dict) -> Response | dict:
        if isinstance(response, dict):
            return response

        data = None
        try:
            data = response.json()
        except (JSONDecodeError, TypeError):
            pass

        response._data = data
        return response


class JsonRedirectResponse(RestRedirectMixin, JsonResponse[DataType], Generic[DataType]): ...


class XmlResponse(RestMethodResponse[DataType], RestDataMixin[DataType], Generic[DataType]):
    @model_validator(mode="before")
    @classmethod
    def extract_data(cls, response: Response | dict) -> Response | dict:
        if isinstance(response, dict):
            return response

        data = None
        try:
            data = xmltodict.parse(response.content)
        except (JSONDecodeError, TypeError):
            pass

        response._data = data
        return response


class XmlRedirectResponse(RestRedirectMixin, XmlResponse[DataType], Generic[DataType]): ...
