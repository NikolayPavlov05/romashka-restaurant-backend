from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailRepository
from contrib.exceptions.exceptions import DoesNotExist
from contrib.exceptions.exceptions import MultipleObjectsReturnedExist
from contrib.pydantic.model import PydanticModel


class TestDetailRepository:
    class _FilterDTO(PydanticModel):
        id: int

    def test_detail_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        detail_repository: FooDetailRepository,
    ):
        object_id = create_repository.create()
        filter_dto = self._FilterDTO(id=object_id)
        instance = detail_repository.detail(filter_dto=filter_dto)

        assert instance.id == object_id
        detail_repository.objects.clear()

    def test_detail_with_filters(
        self,
        create_repository: FooCreateRepository,
        detail_repository: FooDetailRepository,
    ):
        object_id = create_repository.create()
        instance = detail_repository.detail(id=object_id)

        assert instance.id == object_id
        detail_repository.objects.clear()

    def test_object_does_not_exist_exception_redirect(self, detail_repository: FooDetailRepository):
        try:
            detail_repository.detail(id=None)
        except Exception as err:
            assert isinstance(err, DoesNotExist)

    def test_multiple_objects_returned_exception_redirect(
        self,
        create_repository: FooCreateRepository,
        detail_repository: FooDetailRepository,
    ):
        create_repository.create(foo_field1="foo")
        create_repository.create(foo_field1="foo")
        try:
            detail_repository.detail(foo_field1="foo")
        except Exception as err:
            assert isinstance(err, MultipleObjectsReturnedExist)

        detail_repository.objects.clear()
