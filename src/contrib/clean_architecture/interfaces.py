from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Self
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import TypeVar

from contrib.pydantic.model import PydanticModel

if TYPE_CHECKING:
    from contrib.clean_architecture.dto_based_objects.dtos import M2MUpdateAction

ObjectId: TypeAlias = int | str

# новая реализация
RequestDTO = TypeVar("RequestDTO", bound=PydanticModel)
ResponseDTO = TypeVar("ResponseDTO", bound=PydanticModel)
DTO = TypeVar("DTO", bound=PydanticModel)
Entity = TypeVar("Entity", bound=PydanticModel)
Model = TypeVar("Model")


class IManager(ABC):
    class _IQuery:
        select_related: dict[str, dict]

    _prefetch_related_lookups: tuple[str | IPrefetch] | tuple
    _query: _IQuery
    _model: type[Model]

    @abstractmethod
    def all(self) -> QuerySet: ...

    @abstractmethod
    def create(self, **kwargs) -> Model: ...

    @abstractmethod
    def bulk_create(self, objects: list[Entity]) -> None: ...

    @abstractmethod
    def delete(self) -> None: ...

    @abstractmethod
    def first(self) -> Model: ...

    @abstractmethod
    def last(self) -> Model: ...

    @abstractmethod
    def filter(self, *args, **kwargs) -> Self: ...

    @abstractmethod
    def order_by(self, *args) -> Self: ...

    @abstractmethod
    def get(self, *args, **kwargs) -> Model: ...

    @abstractmethod
    def exists(self) -> bool: ...

    @abstractmethod
    def select_related(self, *args) -> Self: ...

    @abstractmethod
    def prefetch_related(self, *args) -> Self: ...


class IM2MManager(ABC):
    @classmethod
    @abstractmethod
    def execute(cls, instance: Model, field: str, actions: list[M2MUpdateAction]) -> None: ...


class IPrefetch(ABC):
    prefetch_through: str
    prefetch_to: str
    queryset: QuerySet


Manager = TypeVar("Manager", bound=IManager)
M2MManager = TypeVar("M2MManager", bound=IM2MManager)
# Абстрактная форма, без реализации методов объектного менеджера на уровне qs
QuerySet = TypeVar("QuerySet")
