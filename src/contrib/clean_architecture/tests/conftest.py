from __future__ import annotations

import pytest
from contrib.clean_architecture.tests.factories.dto_based_objects.dto_based_objects import (
    FooDTOBasedObjects,
)
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.controllers import FooCreateController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDeleteController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailByExternalCodeController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailByPKController
from contrib.clean_architecture.tests.factories.providers.controllers import FooDetailController
from contrib.clean_architecture.tests.factories.providers.controllers import FooPatchListController
from contrib.clean_architecture.tests.factories.providers.controllers import FooRetrieveController
from contrib.clean_architecture.tests.factories.providers.controllers import FooSearchController
from contrib.clean_architecture.tests.factories.providers.controllers import FooUpdateController
from contrib.clean_architecture.tests.factories.providers.interactors import FooCreateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDeleteInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByExternalCodeInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailByPKInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooDetailInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooPatchListInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooRetrieveInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooSearchInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooUpdateInteractor
from contrib.clean_architecture.tests.factories.providers.interactors import FooValidationInteractor
from contrib.clean_architecture.tests.factories.providers.repositories import FooBulkCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooBulkDeleteRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooBulkUpdateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDeleteRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByExternalCodeRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByPKRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailOrCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooExistsRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooGetBetIdsRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooGetSoloRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooMultiUpdateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooPatchListRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooRetrieveRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooSearchRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooUpdateOrCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooUpdateRepository


@pytest.fixture(name="dto_based_objects")
def get_dto_based_objects():
    return FooDTOBasedObjects()


@pytest.fixture(name="creator")
def get_creator():
    return FooUserModel.objects.create()


@pytest.fixture(name="updater")
def get_updater():
    return FooUserModel.objects.create()


@pytest.fixture(name="create_repository")
def get_create_repository():
    return FooCreateRepository()


@pytest.fixture(name="patch_list_repository")
def get_patch_list_repository():
    return FooPatchListRepository()


@pytest.fixture(name="bulk_create_repository")
def get_bulk_create_repository():
    return FooBulkCreateRepository()


@pytest.fixture(name="bulk_update_repository")
def get_bulk_update_repository():
    return FooBulkUpdateRepository()


@pytest.fixture(name="get_by_ids_repository")
def get_by_ids_repository():
    return FooGetBetIdsRepository()


@pytest.fixture(name="update_repository")
def get_update_repository():
    return FooUpdateRepository()


@pytest.fixture(name="update_or_create_repository")
def get_update_or_create_repository():
    return FooUpdateOrCreateRepository()


@pytest.fixture(name="detail_or_create_repository")
def get_detail_or_create_repository():
    return FooDetailOrCreateRepository()


@pytest.fixture(name="delete_repository")
def get_delete_repository():
    return FooDeleteRepository()


@pytest.fixture(name="multi_update_repository")
def multi_update_repository():
    return FooMultiUpdateRepository()


@pytest.fixture(name="bulk_delete_repository")
def get_bulk_delete_repository():
    return FooBulkDeleteRepository()


@pytest.fixture(name="detail_repository")
def get_detail_repository():
    return FooDetailRepository()


@pytest.fixture(name="detail_by_pk_repository")
def get_by_pk_repository():
    return FooDetailByPKRepository()


@pytest.fixture(name="detail_by_external_code_repository")
def get_by_external_code_repository():
    return FooDetailByExternalCodeRepository()


@pytest.fixture(name="retrieve_repository")
def get_retrieve_repository():
    return FooRetrieveRepository()


@pytest.fixture(name="search_repository")
def get_search_repository():
    return FooSearchRepository()


@pytest.fixture(name="solo_repository")
def solo_repository():
    return FooGetSoloRepository()


@pytest.fixture(name="exists_repository")
def get_exists_repository():
    return FooExistsRepository()


@pytest.fixture(name="create_interactor")
def get_create_interactor(create_repository):
    interactor = FooCreateInteractor()
    interactor.repository = create_repository
    return interactor


@pytest.fixture(name="patch_list_interactor")
def get_patch_list_interactor(patch_list_repository):
    interactor = FooPatchListInteractor()
    interactor.repository = patch_list_repository
    return interactor


@pytest.fixture(name="validation_interactor")
def get_validation_interactor():
    interactor = FooValidationInteractor()
    return interactor


@pytest.fixture(name="update_interactor")
def get_update_interactor(update_repository):
    interactor = FooUpdateInteractor()
    interactor.repository = update_repository
    return interactor


@pytest.fixture(name="delete_interactor")
def get_delete_interactor(delete_repository):
    interactor = FooDeleteInteractor()
    interactor.repository = delete_repository
    return interactor


@pytest.fixture(name="detail_interactor")
def get_detail_interactor(detail_repository):
    interactor = FooDetailInteractor()
    interactor.repository = detail_repository
    return interactor


@pytest.fixture(name="detail_by_pk_interactor")
def get_detail_by_pk_interactor(detail_by_pk_repository):
    interactor = FooDetailByPKInteractor()
    interactor.repository = detail_by_pk_repository
    return interactor


@pytest.fixture(name="detail_by_external_code_interactor")
def get_detail_by_external_code_interactor(detail_by_external_code_repository):
    interactor = FooDetailByExternalCodeInteractor()
    interactor.repository = detail_by_external_code_repository
    return interactor


@pytest.fixture(name="retrieve_interactor")
def get_retrieve_interactor(retrieve_repository):
    interactor = FooRetrieveInteractor()
    interactor.repository = retrieve_repository
    return interactor


@pytest.fixture(name="search_interactor")
def get_search_interactor(search_repository):
    interactor = FooSearchInteractor()
    interactor.repository = search_repository
    return interactor


@pytest.fixture(name="create_controller")
def get_create_controller(create_interactor):
    controller = FooCreateController()
    controller.interactor = create_interactor
    return controller


@pytest.fixture(name="update_controller")
def get_update_controller(update_interactor):
    controller = FooUpdateController()
    controller.interactor = update_interactor
    return controller


@pytest.fixture(name="delete_controller")
def get_delete_controller(delete_interactor):
    controller = FooDeleteController()
    controller.interactor = delete_interactor
    return controller


@pytest.fixture(name="detail_controller")
def get_detail_controller(detail_interactor):
    controller = FooDetailController()
    controller.interactor = detail_interactor
    return controller


@pytest.fixture(name="detail_by_pk_controller")
def get_detail_by_pk_controller(detail_by_pk_interactor):
    controller = FooDetailByPKController()
    controller.interactor = detail_by_pk_interactor
    return controller


@pytest.fixture(name="detail_by_external_code_controller")
def get_detail_by_external_code_controller(detail_by_external_code_interactor):
    controller = FooDetailByExternalCodeController()
    controller.interactor = detail_by_external_code_interactor
    return controller


@pytest.fixture(name="retrieve_controller")
def get_retrieve_controller(retrieve_interactor):
    controller = FooRetrieveController()
    controller.interactor = retrieve_interactor
    return controller


@pytest.fixture(name="search_controller")
def get_search_controller(search_interactor):
    controller = FooSearchController()
    controller.interactor = search_interactor
    return controller


@pytest.fixture(name="patch_list_controller")
def get_patch_list_controller(patch_list_interactor):
    controller = FooPatchListController()
    controller.interactor = patch_list_interactor
    return controller
