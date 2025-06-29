from __future__ import annotations

from contrib.clean_architecture.consts import ReturnTypeAttrs
from contrib.clean_architecture.providers.interactors.utils import bind_return_type
from contrib.clean_architecture.tests.factories.general.dtos import BarDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.utils import clear_context
from contrib.clean_architecture.tests.utils import get_context


class TestBindReturnType:
    class _SelfWithReturnType:
        return_type = FooDTO

    class _SelfWithReturnDetailType:
        return_detail_type = FooDTO

    class _SelfWithReturnPaginationType:
        return_pagination_type = FooDTO.paginated

    class _SelfWithMethodReturnType:
        return_detail_type = FooDTO
        _test_function_return_type = BarDTO

    class _SelfWithMethodReturnPaginationType:
        return_pagination_type = FooDTO.paginated
        _test_function_return_pagination_type = BarDTO.paginated

    @staticmethod
    def _test_function(_self, *, paginated=None, return_type=None, return_pagination_type=None):
        return paginated, return_type, return_pagination_type

    def test_bind_paginated(self):
        paginated, _, _ = bind_return_type(paginated=True)(self._test_function)(self._SelfWithReturnType)
        assert paginated is True

    def test_bind_paginated_in_args(self):
        paginated, _, _ = bind_return_type(paginated=True)(self._test_function)(
            self._SelfWithReturnType, paginated=False
        )
        assert paginated is False

    def test_bind_return_type_from_self(self):
        _, return_type, _ = bind_return_type(self._test_function)(self._SelfWithReturnType)
        assert issubclass(return_type, FooDTO)

    def test_bind_return_type_from_context(self):
        context = get_context()
        context.set(ReturnTypeAttrs.RETURN_TYPE, BarDTO)

        _, return_type, _ = bind_return_type(self._test_function)(self._SelfWithReturnType)
        assert issubclass(return_type, BarDTO)
        clear_context()

    def test_bind_return_type_from_self_detail(self):
        context = get_context()
        context.set(ReturnTypeAttrs.RETURN_TYPE, BarDTO)

        _, return_type, _ = bind_return_type(detail=True)(self._test_function)(self._SelfWithReturnDetailType)
        assert issubclass(return_type, FooDTO)
        clear_context()

    def test_bind_return_type_from_context_detail(self):
        context = get_context()
        context.set(ReturnTypeAttrs.RETURN_DETAIL_TYPE, BarDTO)

        _, return_type, _ = bind_return_type(detail=True)(self._test_function)(self._SelfWithReturnDetailType)
        assert issubclass(return_type, BarDTO)
        clear_context()

    def test_bind_return_type_from_self_method(self):
        _, return_type, _ = bind_return_type(detail=True)(self._test_function)(self._SelfWithMethodReturnType)
        assert issubclass(return_type, BarDTO)

    def test_bind_return_type_from_context_method(self):
        context = get_context()
        context.set(f"_test_function_{ReturnTypeAttrs.RETURN_TYPE}", FooDTO)

        _, return_type, _ = bind_return_type(detail=True)(self._test_function)(self._SelfWithMethodReturnType)
        assert issubclass(return_type, FooDTO)
        clear_context()

    def test_bind_return_type_from_args(self):
        context = get_context()
        context.set(f"_test_function_{ReturnTypeAttrs.RETURN_TYPE}", FooDTO)

        _, return_type, _ = bind_return_type(detail=True)(self._test_function)(
            self._SelfWithMethodReturnType, return_type=BarDTO
        )
        assert issubclass(return_type, BarDTO)
        clear_context()

    def test_bind_return_pagination_type_from_self(self):
        _, _, return_pagination_type = bind_return_type(self._test_function, paginated=True)(
            self._SelfWithReturnPaginationType
        )
        assert issubclass(return_pagination_type, FooDTO.paginated)

    def test_bind_return_pagination_type_from_context(self):
        context = get_context()
        context.set(ReturnTypeAttrs.RETURN_PAGINATION_TYPE, BarDTO.paginated)

        _, _, return_pagination_type = bind_return_type(self._test_function, paginated=True)(
            self._SelfWithReturnPaginationType
        )
        assert issubclass(return_pagination_type, BarDTO.paginated)
        clear_context()

    def test_bind_return_pagination_type_from_self_method(self):
        context = get_context()
        context.set(ReturnTypeAttrs.RETURN_PAGINATION_TYPE, FooDTO.paginated)

        _, _, return_pagination_type = bind_return_type(self._test_function, paginated=True)(
            self._SelfWithMethodReturnPaginationType
        )
        assert issubclass(return_pagination_type, BarDTO.paginated)
        clear_context()

    def test_bind_return_pagination_type_from_context_method(self):
        context = get_context()
        context.set(f"_test_function_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}", FooDTO.paginated)

        _, _, return_pagination_type = bind_return_type(self._test_function, paginated=True)(
            self._SelfWithMethodReturnPaginationType
        )
        assert issubclass(return_pagination_type, FooDTO.paginated)
        clear_context()

    def test_bind_return_pagination_type_from_args(self):
        context = get_context()
        context.set(f"_test_function_{ReturnTypeAttrs.RETURN_PAGINATION_TYPE}", FooDTO.paginated)

        _, _, return_pagination_type = bind_return_type(self._test_function, paginated=True)(
            self._SelfWithMethodReturnPaginationType,
            return_pagination_type=BarDTO.paginated,
        )
        assert issubclass(return_pagination_type, BarDTO.paginated)
        clear_context()
