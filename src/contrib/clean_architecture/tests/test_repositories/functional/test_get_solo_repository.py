from __future__ import annotations

from contrib.clean_architecture.tests.factories.providers.repositories import (
    FooGetSoloRepository,
)


class TestGetSoloRepository:
    def test_get_solo(self, solo_repository: FooGetSoloRepository):
        instance = solo_repository.get_solo()
        assert instance
