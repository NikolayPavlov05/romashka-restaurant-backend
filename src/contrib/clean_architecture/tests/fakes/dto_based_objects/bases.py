from __future__ import annotations

from collections.abc import Sequence

from contrib.clean_architecture.dto_based_objects.bases import BaseDTOBasedObjectsMixin
from contrib.clean_architecture.dto_based_objects.dtos import MatchedRelation
from contrib.clean_architecture.dto_based_objects.enums import RelatedTypes
from contrib.clean_architecture.interfaces import DTO
from contrib.clean_architecture.tests.fakes.general.managers import FakeM2MManager
from contrib.clean_architecture.tests.fakes.general.managers import FakeManager
from contrib.clean_architecture.tests.fakes.general.models import FakeModel
from contrib.clean_architecture.tests.fakes.repositories.utils import FakePrefetch
from contrib.pydantic.model import PydanticModel


class FakeDTOBasedObjectsMixin(BaseDTOBasedObjectsMixin, required_attrs_base=True):
    prefetch_class = FakePrefetch
    model: type[FakeModel]
    sequence_classes = (FakeManager,)
    m2m_manager = FakeM2MManager

    @classmethod
    def _match_relations(cls, model: type[FakeModel], dto: type[DTO]):
        model_fields = {field_name: cls._extract_annotation(field) for field_name, field in model.model_fields.items()}
        dto_fields = {field_name: cls._extract_annotation(field) for field_name, field in dto.model_fields.items()}
        matched_relations = []
        for field_name in dto_fields:
            model_field = model_fields.get(field_name)
            if not model_field or not issubclass(model_field, PydanticModel):
                continue

            annotation = model.model_fields[field_name].annotation
            if getattr(annotation, "__args__", None) and issubclass(annotation.__origin__, Sequence):
                related_type = RelatedTypes.PREFETCH_RELATED
            else:
                related_type = RelatedTypes.SELECT_RELATED

            related_dto = dto_fields[field_name] if issubclass(dto_fields[field_name], PydanticModel) else None

            matched_relations.append(
                MatchedRelation(
                    field_name=field_name,
                    related_type=related_type,
                    related_model=model_fields[field_name],
                    related_dto=related_dto,
                )
            )

        return matched_relations
