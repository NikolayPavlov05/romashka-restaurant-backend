from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooRetrieveRepository
from contrib.pydantic.model import PydanticModel


class TestRetrieveRepository:
    class _FilterDTO(PydanticModel):
        foo_field1: str

    @staticmethod
    def _prepare_data(create_repository):
        create_repository.objects.clear()
        create_repository.create(foo_field1="foo", foo_field2="2")
        create_repository.create(foo_field1="foo", foo_field2="1")
        create_repository.create(foo_field1="bar")

    def test_retrieve_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)
        filter_dto = self._FilterDTO(foo_field1="foo")
        instances = retrieve_repository.retrieve(filter_dto=filter_dto)
        assert len(instances) == 2
        retrieve_repository.objects.clear()

    def test_retrieve_detail_with_filters(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)

        instances = retrieve_repository.retrieve(foo_field1="foo")

        assert len(instances) == 2
        retrieve_repository.objects.clear()

    def test_count_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)
        filter_dto = self._FilterDTO(foo_field1="foo")

        assert retrieve_repository.count(filter_dto=filter_dto) == 2
        retrieve_repository.objects.clear()

    def test_count_with_filters(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)

        assert retrieve_repository.count(foo_field1="foo") == 2
        retrieve_repository.objects.clear()

    def test_limit(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)
        instances = retrieve_repository.retrieve(foo_field1="foo", limit=1)
        assert len(instances) == 1
        retrieve_repository.objects.clear()

    def test_offset(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)
        instances = retrieve_repository.retrieve(foo_field1="foo", limit=1)
        instances_with_offset = retrieve_repository.retrieve(foo_field1="foo", limit=1, offset=1)
        assert instances[0].id != instances_with_offset[0].id
        retrieve_repository.objects.clear()

    def test_order_by(
        self,
        create_repository: FooCreateRepository,
        retrieve_repository: FooRetrieveRepository,
    ):
        self._prepare_data(create_repository)
        instances = retrieve_repository.retrieve(foo_field1="foo")
        instances_with_order_by = retrieve_repository.retrieve(foo_field1="foo", order_by=("foo_field2",))
        assert len(instances) == 2
        assert len(instances_with_order_by) == 2
        assert instances[0].id == instances_with_order_by[-1].id
        retrieve_repository.objects.clear()
