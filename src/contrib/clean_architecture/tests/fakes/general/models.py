from __future__ import annotations

from typing import Any
from typing import ClassVar

from contrib.clean_architecture.tests.fakes.general.enums import FakeExternalCodeType
from contrib.clean_architecture.tests.fakes.general.managers import _fake_instances
from contrib.clean_architecture.tests.fakes.general.managers import FakeExternalCodeManager
from contrib.clean_architecture.tests.fakes.general.managers import FakeManager
from contrib.pydantic.model import PydanticModel
from pydantic import Field


class FakeModel(PydanticModel):
    objects: ClassVar[FakeManager]

    id: int | None = Field(default=None)
    pk: int | None = Field(default=None)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        if not getattr(cls, "objects", None):
            cls.objects = FakeManager()

    def save(self, *args, **kwargs):
        instance_list = self.objects.filter(id=self.id).all()
        if not instance_list:
            self.objects.create(**self.model_dump())
        else:
            index = _fake_instances[self.__class__].index(instance_list[0])
            _fake_instances[self.__class__][index] = self

    def delete(self):
        instance_list = list(filter(lambda item: item.id == self.id, _fake_instances[self.__class__]))
        if not instance_list:
            raise ValueError("No instance")
        index = _fake_instances[self.__class__].index(instance_list[0])
        _fake_instances[self.__class__].pop(index)
        return self.id, {self.__class__: 1}


class FakeExternalCode(FakeModel):
    objects = FakeExternalCodeManager()

    code: str
    code_type: FakeExternalCodeType

    object_id: int
    content_type: Any

    @property
    def content_object(self):
        return next(
            filter(
                lambda item: item.id == self.object_id,
                _fake_instances[self.content_type],
            )
        )
        return next(
            filter(
                lambda item: item.id == self.object_id,
                _fake_instances[self.content_type],
            )
        )


class FakeSingletonModel(FakeModel):
    def __new__(cls, *args, **kwargs):
        instance = cls.objects.first()
        if not instance:
            instance = super().__new__(cls, *args, **kwargs)
        return instance
