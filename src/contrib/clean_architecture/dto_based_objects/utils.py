"""Модуль с утилитами для взаимодействия между моделями БД и DTO

Classes:
    ConvertPath: Класс, определяющий, путь до объекта, который нужно конвертировать

Functions:
    convert_return: Декоратор, преобразующий модель или последовательность моделей в DTO или список DTO

"""
from __future__ import annotations

from collections.abc import Callable
from collections.abc import Sequence
from typing import Any

from contrib.clean_architecture.dto_based_objects.interfaces import (
    IDTOBasedObjectsMixin,
)
from contrib.clean_architecture.interfaces import Entity
from contrib.clean_architecture.interfaces import Model


class ConvertPath:
    """Класс, определяющий, путь до объекта, который нужно конвертировать

    Examples:
        * Обратится к индексу
        >>> ConvertPath(0)

        * Обратится к ключу
        >>> ConvertPath("key")

        * Обратится к атрибуту
        >>> ConvertPath("attr")

        * Можно выстраивать любую комбинацию аргументов
        >>> ConvertPath(0, "key", "attr", 1)

        * Результат `self.objects.create()` конвертируется в FooEntity, но сама структура результата
        foo_convert_return_with_mixed_convert_path_mixed_method не изменится
        >>> from contrib.clean_architecture.tests.fakes.dto_based_objects.bases import FakeDTOBasedObjectsMixin
        >>> from contrib.clean_architecture.tests.factories.dto_based_objects.models import FooModelWithRelations
        >>> from contrib.clean_architecture.tests.factories.general.entities import FooEntity
        >>>
        >>> class FooDTOBasedObjects(FakeDTOBasedObjectsMixin):
        >>>     @convert_return(FooModelWithRelations, FooEntity, convert_path=ConvertPath(0, "key"))
        >>>     def foo_convert_return_with_mixed_convert_path_mixed_method(self):
        >>>         return [{"key": self.objects.create()}]
        >>>
        >>> result = FooDTOBasedObjects().foo_convert_return_with_mixed_convert_path_mixed_method()
        >>> type(result[0]["key"]) == FooEntity
        True

    """

    def __init__(self, *args: str | int):
        """

        Args:
            *args: набор индексов (если int) и/или ключей, или имен аттрибутов
        """
        self._path_args = args

    def __call__(self, value: Any, convert_function: Callable):
        """Вызывает convert_function на объекте, до которого определен путь

        Args:
            value: Любой объект, поддерживающий индексацию или маппинг
            convert_function: Функция для конвертации объекта

        Returns:
            value: модифицированный объект
        """
        if not self._path_args:
            return convert_function

        if isinstance(value, tuple):
            value = list(value)

        item_container = value
        for path_arg in self._path_args[:-1]:
            if isinstance(path_arg, int):
                item_container = item_container[path_arg]
            elif isinstance(path_arg, str) and isinstance(item_container, dict):
                item_container = item_container.get(path_arg)
            elif isinstance(path_arg, str):
                item_container = getattr(item_container, path_arg, None)
            else:
                raise ValueError(f"Unsupported path argument: {path_arg} for {item_container}")

        path_arg = self._path_args[-1]
        if isinstance(path_arg, int) or isinstance(path_arg, str) and isinstance(item_container, dict):
            item_container[path_arg] = convert_function(item_container[path_arg])
        elif isinstance(path_arg, str):
            setattr(
                item_container,
                path_arg,
                convert_function(getattr(item_container, path_arg, None)),
            )
        else:
            raise ValueError(f"Unsupported path argument: {path_arg} for {item_container}")

        return value


def convert_return(
    model: type[Model],
    entity: type[Entity],
    *extra_layers,
    convert_path: ConvertPath = None,
):
    """Декоратор, преобразующий модель или последовательность моделей в DTO или список DTO

    Args:
        model: Класс модели ORM для которой нужно применить конвертацию
        entity: Класс pydantic модели, служащей первым слоем преобразования экземпляров моделей ORM
        *extra_layers: Последовательность слоев конвертации (классов pydantic моделей) после entity
        convert_path: Путь до объекта, который нужно конвертировать

    Examples:
        * Результат `self.objects.create()` конвертируется в FooEntity, а затем в FooDTOWithRelations
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

        * Результат `self.objects.create()` конвертируется в FooEntity
        >>> result = FooDTOBasedObjects().with_dto(FooDTOWithRelations).foo(return_entity=True)
        >>> type(result) == FooEntity
        True

        * Результат `self.objects.create()` не конвертируется
        >>> result = FooDTOBasedObjects().with_dto(FooDTOWithRelations).foo(return_original=True)
        >>> type(result) == FooModelWithRelations
        True

        * Результат `self.objects.create()` конвертируется в FooEntity, а затем в FooDTOWithRelations
        >>> class FooDTOBasedObjects(FakeDTOBasedObjectsMixin):
        >>>     @convert_return(FooModelWithRelations, FooEntity, FooDTOWithRelations)
        >>>     def foo(self):
        >>>         return self.objects.create()
        >>>
        >>> result = FooDTOBasedObjects().foo()
        >>> type(result) == FooDTOWithRelations
        True

        * Использование параметра convert_path отражено в примерах [`ConvertPath`][contrib.clean_architecture.dto_based_objects.utils.ConvertPath]
    """

    def decorator(function):
        """Декоратор для функций классов расширенных классом IDTOBasedObjectsMixin

        Args:
            function: набор индексов (если int) и/или ключей, или имен аттрибутов
        """

        def wrapper(
            self: IDTOBasedObjectsMixin,
            *args,
            return_entity=False,
            return_original: bool = False,
            **kwargs,
        ):
            """

            Args:
                self: Экземпляр класса расширенного классом IDTOBasedObjectsMixin
                *args: Аргументы декорируемой функции
                return_entity: Возвращать ли Entity
                return_original: Возвращать ли оригинальный результат функции
                **kwargs: kw аргументы декорируемой функции
            """
            if (return_type := self._models_dtos.get(model)) and not return_entity:
                layers = [entity, *extra_layers]
            else:
                return_type = entity
                layers = [*extra_layers]

            result = function(self, *args, **kwargs)
            if return_original:
                return result
            if result is None:
                return

            def _convert_function(value):
                """Функция для конвертации результата декорируемой функции

                Args:
                    value: результата декорируемой функции
                """
                if not isinstance(value, (Sequence, *self.sequence_classes)):
                    return return_type.layered_model_validate(value, *layers)
                return [return_type.layered_model_validate(instance, *layers) for instance in value]

            if convert_path:
                return convert_path(result, _convert_function)
            return _convert_function(result)

        return wrapper

    return decorator
