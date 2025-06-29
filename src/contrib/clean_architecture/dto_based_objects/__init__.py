"""Модуль для взаимодействия между моделями БД и DTO

Modules:
    utils: Утилиты
    interfaces: Абстрактные интерфейсы
    bases: Базовые реализации
    django.bases: Реализация для django моделей

Examples:
    * Результат `self.objects.create()` конвертируется в FooEntity, а затем в FooDTOWithRelations
    * При этом при запросе в бд будут добавлены все необходимые select_related и prefetch_related
    >>> from contrib.clean_architecture.dto_based_objects.utils import convert_return
    >>> from contrib.clean_architecture.tests.fakes.dto_based_objects.bases import FakeDTOBasedObjectsMixin
    >>> from contrib.clean_architecture.tests.factories.dto_based_objects.models import FooModelWithRelations
    >>> from contrib.clean_architecture.tests.factories.dto_based_objects.dtos import FooDTOWithRelations
    >>> from contrib.clean_architecture.tests.factories.general.entities import FooEntity
    >>>
    >>> class FooDTOBasedObjects(FakeDTOBasedObjectsMixin):
    >>>     @convert_return(FooModelWithRelations, FooEntity)
    >>>     def foo(self):
    >>>         return self.objects.create()
    >>>
    >>> result = FooDTOBasedObjects().with_dto(FooDTOWithRelations).foo()
    >>> type(result) == FooDTOWithRelations
    True

"""
from __future__ import annotations
