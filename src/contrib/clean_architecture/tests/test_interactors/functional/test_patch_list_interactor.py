from __future__ import annotations

from unittest import mock

from contrib.clean_architecture.providers.interactors.exceptions import (
    NothingToUpdateOrCreateException,
)
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooPatchListDTO
from contrib.clean_architecture.tests.factories.general.dtos import FooPatchListItemDTO
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooPatchListInteractor


class TestPatchListInteractor:
    def test_patch_list_create(self, patch_list_interactor: FooPatchListInteractor):
        after_count: int = patch_list_interactor.repository.objects.count()

        patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO(foo_field1="test_field")]))

        new_count: int = patch_list_interactor.repository.objects.count()

        assert after_count + 1 == new_count

        last_object = patch_list_interactor.repository.objects.last()

        assert last_object.foo_field1 == "test_field"
        patch_list_interactor.repository.objects.clear()

    def test_patch_list_update(
        self,
        create_interactor: FooCreateInteractor,
        patch_list_interactor: FooPatchListInteractor,
    ):
        object_id = create_interactor.create(FooDTO(foo_field1="created"))

        after_count: int = patch_list_interactor.repository.objects.count()

        patch_list_interactor.patch_list(
            FooPatchListDTO(items=[FooPatchListItemDTO(id=object_id, foo_field1="updated")])
        )

        new_count: int = patch_list_interactor.repository.objects.count()

        assert after_count == new_count

        last_object = patch_list_interactor.repository.objects.last()

        assert last_object.foo_field1 == "updated"
        patch_list_interactor.repository.objects.clear()

    def test_patch_list_delete(
        self,
        create_interactor: FooCreateInteractor,
        patch_list_interactor: FooPatchListInteractor,
    ):
        object_id = create_interactor.create(FooDTO(foo_field1="created"))

        after_count: int = patch_list_interactor.repository.objects.count()

        patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO(id=object_id, delete=True)]))

        new_count: int = patch_list_interactor.repository.objects.count()

        assert after_count - 1 == new_count

        patch_list_interactor.repository.objects.clear()

    def test_patch_list_update_negative(
        self,
        create_interactor: FooCreateInteractor,
        patch_list_interactor: FooPatchListInteractor,
    ):
        patch_list_interactor.can_create_or_update_blank = False

        try:
            patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO(id=1)]))
            raise AssertionError("Необрабатывается случай для can_create_or_update_blank = False")
        except NothingToUpdateOrCreateException:
            pass

        try:
            patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO()]))
            raise AssertionError("Необрабатывается случай для can_create_or_update_blank = False")
        except NothingToUpdateOrCreateException:
            pass

    def test_patch_list_check_events(
        self,
        create_interactor: FooCreateInteractor,
        patch_list_interactor: FooPatchListInteractor,
    ):
        object_id = create_interactor.create(FooDTO(foo_field1="created"))

        with mock.patch.object(FooPatchListInteractor, "patch_list_validate_update_objects") as patch1:
            patch_list_interactor.patch_list(
                FooPatchListDTO(items=[FooPatchListItemDTO(id=object_id, foo_field1="updated")])
            )

        with mock.patch.object(FooPatchListInteractor, "patch_list_validate_create_objects") as patch2:
            patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO(foo_field1="updated")]))

        with mock.patch.object(FooPatchListInteractor, "patch_list_validate_delete_objects") as patch3:
            patch_list_interactor.patch_list(FooPatchListDTO(items=[FooPatchListItemDTO(id=object_id, delete=True)]))

        assert patch1.called
        assert patch2.called
        assert patch3.called
