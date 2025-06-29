from __future__ import annotations

from contrib.clean_architecture.providers.repositories.bases import BulkCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import BulkDeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import BulkUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import CreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import DeleteRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import DetailByExternalCodeRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import DetailByPKRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import DetailOrCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import DetailRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import ExistsRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import GetByIdsRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import GetSoloRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import MultiUpdateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import RetrieveRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import SearchRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import UpdateOrCreateRepositoryMixin
from contrib.clean_architecture.providers.repositories.bases import UpdateRepositoryMixin
from contrib.clean_architecture.tests.factories.general.entities import FooEntity
from contrib.clean_architecture.tests.factories.general.models import FooModel
from contrib.clean_architecture.tests.factories.general.models import FooSingletonModel
from contrib.clean_architecture.tests.fakes.repositories.bases import FakeRepository


class FooCreateRepository(CreateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooBulkCreateRepository(BulkCreateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooBulkUpdateRepository(BulkUpdateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooUpdateRepository(UpdateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooUpdateOrCreateRepository(UpdateOrCreateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooDetailOrCreateRepository(DetailOrCreateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooDeleteRepository(DeleteRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooBulkDeleteRepository(BulkDeleteRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooDetailRepository(DetailRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooDetailByPKRepository(DetailByPKRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooDetailByExternalCodeRepository(DetailByExternalCodeRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooRetrieveRepository(RetrieveRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooSearchRepository(SearchRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity

    search_expressions = ("foo_field3", "foo_field4")


class FooExistsRepository(ExistsRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooPatchListRepository(
    FooUpdateRepository,
    FooBulkCreateRepository,
    FooBulkDeleteRepository,
    FakeRepository,
):
    model = FooModel
    entity = FooEntity


class FooGetBetIdsRepository(GetByIdsRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooMultiUpdateRepository(MultiUpdateRepositoryMixin, FakeRepository):
    model = FooModel
    entity = FooEntity


class FooGetSoloRepository(GetSoloRepositoryMixin, FakeRepository):
    model = FooSingletonModel
    entity = FooEntity
