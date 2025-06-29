from __future__ import annotations

from contrib.clean_architecture.tests.factories.general.models import FooModel
from contrib.clean_architecture.tests.factories.general.models import FooUserModel
from contrib.clean_architecture.tests.factories.providers.interactors import (
    FooValidationInteractor,
)
from contrib.exceptions.exceptions import ValidationError


class TestValidationInteractor:
    def test_validate_required_fields(self, validation_interactor: FooValidationInteractor):
        validation_interactor.required_fields = {"updated_by"}
        validation_interactor.context_requires_fields = set()

        model = FooModel(created_by=None, updated_by=FooUserModel())
        try:
            validation_interactor.validate_required_fields(model)
            assert AssertionError("Проверка на обязательность полей работает некорректно")
        except ValidationError:
            pass

        model = FooModel(created_by=FooUserModel(), updated_by=FooUserModel())
        validation_interactor.validate_required_fields(model)

    def test_validate_changed_fields(self, validation_interactor: FooValidationInteractor):
        validation_interactor.validate_fields = [
            "foo_field1",
            "foo_field2",
            "foo_field3",
            "foo_field4",
        ]
        validation_interactor.can_update_fields_with_external_codes = []
        validation_interactor.context_requires_fields = set()

        model = FooModel()
        model1 = FooModel(foo_field1="test")
        try:
            validation_interactor.validate_changed_fields(model, model1)
            assert AssertionError("Проверка на изменение полей работает некорректно")
        except ValidationError:
            pass

        validation_interactor.can_update_fields_with_external_codes = ["foo_field1"]
        validation_interactor.validate_changed_fields(model, model1)
