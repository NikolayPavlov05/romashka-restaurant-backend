from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.dtos import FooDTO


class ListTestMixin:
    @staticmethod
    def _prepare(create_controller):
        create_controller.interactor.repository.objects.clear()
        create_controller.create(FooDTO())
        create_controller.create(FooDTO())

    @staticmethod
    def _test_paginated_result(result):
        assert isinstance(result, FooDTO.paginated)
        assert result.count == 2
        assert len(result.results) == 2
        assert isinstance(result.results[0], FooDTO)
        assert isinstance(result.results[1], FooDTO)

    @staticmethod
    def _test_result(result):
        assert len(result) == 2
        assert isinstance(result[0], FooDTO)
        assert isinstance(result[1], FooDTO)
