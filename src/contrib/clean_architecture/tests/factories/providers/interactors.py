from __future__ import annotations

from contrib.clean_architecture.providers.interactors.bases import CreateInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DeleteInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailByExternalCodeInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailByPKInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import DetailInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import Interactor
from contrib.clean_architecture.providers.interactors.bases import PatchListInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import RetrieveInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import SearchInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import UpdateInteractorMixin
from contrib.clean_architecture.providers.interactors.bases import ValidationInteractorMixin
from contrib.clean_architecture.tests.factories.general.dtos import FooDTO
from contrib.clean_architecture.tests.factories.providers.repositories import FooCreateRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDeleteRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByExternalCodeRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailByPKRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooDetailRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooPatchListRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooRetrieveRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooSearchRepository
from contrib.clean_architecture.tests.factories.providers.repositories import FooUpdateRepository
from contrib.context.mixins import ContextMixin
from contrib.context.utils import context_property


class FooCreateInteractor(CreateInteractorMixin, Interactor):
    repository: FooCreateRepository


class FooUpdateInteractor(UpdateInteractorMixin, Interactor):
    repository: FooUpdateRepository


class FooPatchListInteractor(PatchListInteractorMixin, Interactor):
    repository: FooPatchListRepository


class FooDeleteInteractor(DeleteInteractorMixin, Interactor):
    repository: FooDeleteRepository


class FooDetailInteractor(DetailInteractorMixin, Interactor):
    repository: FooDetailRepository
    return_type = FooDTO


class FooDetailByPKInteractor(DetailByPKInteractorMixin, Interactor):
    repository: FooDetailByPKRepository
    return_type = FooDTO


class FooDetailByExternalCodeInteractor(DetailByExternalCodeInteractorMixin, Interactor):
    repository: FooDetailByExternalCodeRepository
    return_type = FooDTO


class FooRetrieveInteractor(RetrieveInteractorMixin, Interactor):
    repository: FooRetrieveRepository
    return_type = FooDTO
    return_pagination_type = FooDTO.paginated


class FooSearchInteractor(SearchInteractorMixin, Interactor):
    repository: FooSearchRepository
    return_type = FooDTO
    return_pagination_type = FooDTO.paginated


class FooValidationInteractor(ValidationInteractorMixin, ContextMixin, Interactor):
    required_fields: set = {}
    context_requires_fields: set[str] = context_property(default_factory=set)

    validate_fields: list = []
    can_update_fields_with_external_codes: list = []
    m2m_fields: list = []
    exclude_fields: list = []
