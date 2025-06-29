from __future__ import annotations

from unittest import mock

from contrib.clean_architecture.tests.factories.general.dtos import FooPatchListDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooPatchListItemDTO
from contrib.clean_architecture.tests.factories.providers.controllers import (
    FooPatchListController,
)


class TestPatchListController:
    def test_patch_list(self, patch_list_controller: FooPatchListController):
        with mock.patch.object(patch_list_controller, "patch_list") as patch:
            patch_list_controller.patch_list(FooPatchListDTO(objects=[FooPatchListItemDTO()]))

        assert patch.called
