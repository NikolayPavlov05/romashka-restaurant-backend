from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO


class ListTestMixin:
    @staticmethod
    def _prepare(create_controller):
        create_controller.repository.objects.clear()
        create_controller.create(FooDTO())
        create_controller.create(FooDTO())

    @staticmethod
    def _test_paginated_result(result, return_type):
        assert isinstance(result, return_type.paginated)
        assert result.count == 2
        assert len(result.results) == 2
        assert isinstance(result.results[0], return_type)
        assert isinstance(result.results[1], return_type)

    @staticmethod
    def _test_result(result, return_type):
        assert len(result) == 2
        assert isinstance(result[0], return_type)
        assert isinstance(result[1], return_type)
