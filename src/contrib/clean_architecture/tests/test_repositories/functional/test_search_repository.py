from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooSearchRepository
from contrib.pydantic.model import PydanticModel


class TestSearchRepository:
    class _FilterDTO(PydanticModel):
        foo_field1: str

    @staticmethod
    def _prepare_data(create_repository):
        create_repository.objects.clear()
        create_repository.create(
            foo_field1="foo",
            foo_field2="2",
            foo_field3="search",
            foo_field4="other_search",
        )
        create_repository.create(foo_field1="foo", foo_field2="2")
        create_repository.create(
            foo_field1="foo",
            foo_field2="1",
            foo_field3="search",
            foo_field4="other_search",
        )
        create_repository.create(foo_field1="foo", foo_field2="1")
        create_repository.create(foo_field1="bar")

    def test_search_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        filter_dto = self._FilterDTO(foo_field1="foo")
        instances = search_repository.search("search", filter_dto=filter_dto)
        assert len(instances) == 2
        search_repository.objects.clear()

    def test_search_with_exclude_filter_dto(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        instances = search_repository.search("search", **{"~foo_field2": "2"})
        assert len(instances) == 1
        search_repository.objects.clear()

    def test_search_detail_with_filters(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)

        instances = search_repository.search("search", foo_field1="foo")

        assert len(instances) == 2
        search_repository.objects.clear()

    def test_search_with_other_field_substring(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)

        instances = search_repository.search("other", foo_field1="foo")

        assert len(instances) == 2
        search_repository.objects.clear()

    def test_search_count_with_filter_dto(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        filter_dto = self._FilterDTO(foo_field1="foo")

        assert search_repository.search_count("search", filter_dto=filter_dto) == 2
        search_repository.objects.clear()

    def test_search_count_with_filters(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)

        assert search_repository.search_count("search", foo_field1="foo") == 2
        search_repository.objects.clear()

    def test_search_count_with_other_field_substring(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)

        assert search_repository.search_count("other", foo_field1="foo") == 2
        search_repository.objects.clear()

    def test_limit(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        instances = search_repository.search("search", foo_field1="foo", limit=1)
        assert len(instances) == 1
        search_repository.objects.clear()

    def test_offset(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        instances = search_repository.search("search", foo_field1="foo", limit=1)
        instances_with_offset = search_repository.search("search", foo_field1="foo", limit=1, offset=1)
        assert instances[0].id != instances_with_offset[0].id
        search_repository.objects.clear()

    def test_order_by(
        self,
        create_repository: FooCreateRepository,
        search_repository: FooSearchRepository,
    ):
        self._prepare_data(create_repository)
        instances = search_repository.search("search", foo_field1="foo")
        instances_with_order_by = search_repository.search("search", foo_field1="foo", order_by=("foo_field2",))
        assert len(instances) == 2
        assert len(instances_with_order_by) == 2
        assert instances[0].id == instances_with_order_by[-1].id
        search_repository.objects.clear()
