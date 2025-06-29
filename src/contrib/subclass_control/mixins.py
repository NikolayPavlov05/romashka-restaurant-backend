"""Модуль с миксинами для контроля дочерних классов

Classes:
    RequiredAttrsMixin: Добавляет обязательные атрибуты для дочерних классов
    CopiedAttrsMixin: Копирует атрибуты из родительского класса в дочерние
    ExtendedAttrsMixin: Расширяет и перезаписывает атрибуты в дочерних классах
    ImportedStringAttrsMixin: Импортирует атрибуты из строки при обращении к ним
    SingletonMixin: Миксин singleton принимающий аргументы, на основе которых необходимо держать единственный экземпляр

"""
from __future__ import annotations

import inspect
from copy import copy
from copy import deepcopy
from typing import ClassVar

from contrib.imports.services import import_by_string
from contrib.inspect.services import get_params_values


class RequiredAttrsMixin:
    """Добавляет обязательные атрибуты для дочерних классов

    Examples:
        >>> class Foo(RequiredAttrsMixin):
        >>>     required_attrs = ("model", "prefetch_class", "m2m_manager")

    """

    required_attrs: ClassVar[tuple] = ()
    """Кортеж обязательных аргументов"""
    required_attrs_check_abstract: ClassVar[bool] = False
    """Проверять ли обязательные атрибуты у абстрактных классов"""

    def __init_subclass__(cls, required_attrs_base=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if not required_attrs_base:
            cls.check_required_attrs()

    @classmethod
    def check_required_attrs(cls):
        """Проверяет наличие обязательных атрибутов"""
        if not cls.required_attrs_check_abstract and inspect.isabstract(cls):
            return

        for _cls in reversed(cls.__mro__):
            if not hasattr(_cls, "required_attrs"):
                continue

            for attr in _cls.required_attrs:
                if not hasattr(cls, attr):
                    raise AttributeError(f"Атрибут {attr} обязательно должен быть определен для класса {cls.__name__}")


class CopiedAttrsMixin:
    """Копирует атрибуты из родительского класса в дочерние

    Examples:
        >>> class Foo(CopiedAttrsMixin):
        >>>     copied_attrs = ("model", "prefetch_class")
        >>>     copied_attrs_deep = ("m2m_manager", )

    """

    copied_attrs: ClassVar[tuple] = ()
    """Кортеж копируемых атрибутов"""
    copied_attrs_deep: ClassVar[tuple] = ()
    """Кортеж глубоко копируемых атрибутов"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.copy_attrs()

    @classmethod
    def copy_attrs(cls):
        """Копирует атрибуты в дочерние классы"""
        for _cls in reversed(cls.__mro__):
            if hasattr(_cls, "copied_attrs"):
                for attr in _cls.copied_attrs:
                    setattr(cls, attr, copy(getattr(cls, attr)))

            if hasattr(_cls, "deep_copied_attrs"):
                for attr in _cls.copied_attrs_deep:
                    setattr(cls, attr, deepcopy(getattr(cls, attr)))


class ExtendedAttrsMixin:
    """Расширяет и перезаписывает атрибуты в дочерних классах

    Examples:
        >>>
        >>> class Foo(ExtendedAttrsMixin):
        >>>     extended_attrs = {
        >>>         "raw_id_fields",
        >>>         "search_fields",
        >>>     }

    """

    _extended_attrs_available_types: ClassVar[tuple] = (set, dict, tuple, list)

    extended_attrs: ClassVar[set] = {"extended_attrs"}
    """Список расширяемых атрибутов"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._extend_attrs()

    @classmethod
    def _extend_attrs(cls):
        """Расширяет атрибуты дочерних классов"""
        attrs = {}
        for _cls in reversed(cls.__mro__):
            for attr in (
                "extended_attrs",
                *getattr(_cls, "extended_attrs", ()),
                *attrs.keys(),
            ):
                if getattr(_cls, attr, None) is None:
                    continue

                value = getattr(_cls, attr)
                if type(value) not in cls._extended_attrs_available_types:
                    cls._raise_value_error(attr, _cls)

                if attr not in attrs:
                    attrs[attr] = deepcopy(value)
                    continue

                if isinstance(value, set) and isinstance(attrs[attr], set):
                    attrs[attr] |= value
                elif isinstance(value, dict) and isinstance(attrs[attr], dict):
                    attrs[attr].update(value)
                elif isinstance(value, (tuple, list)):
                    for element in value:
                        if element not in attrs[attr]:
                            attrs[attr] += (element,)
                else:
                    cls._raise_inheritance_value_error(attr, cls)

        for attr, value in attrs.items():
            setattr(cls, attr, value)

    @classmethod
    def _raise_value_error(cls, attr: str, _cls: type):
        """Вызвать ValueError"""
        raise ValueError(
            f"Тип атрибут {attr} класса {_cls.__name__} " f"должен быть одним из {cls._extended_attrs_available_types}"
        )

    @classmethod
    def _raise_inheritance_value_error(cls, attr: str, _cls: type):
        """Вызвать ValueError для несовпадающих типов атрибутов"""
        raise ValueError(
            f"Тип атрибут {attr} класса {_cls.__name__} "
            f"должен совпадать с типами этого атрибута в родительских классах"
        )


class ImportedStringAttrsMixin:
    """Импортирует атрибуты из строки при обращении к ним

    Examples:
        >>> class Foo(ImportedStringAttrsMixin):
        >>>     imported_string_attrs = ("external_code_model",)
    """

    class _ImportedStringDescriptor:
        """Дескриптор для импорта атрибута"""

        def __init__(self, string_import: str, class_attr: bool = False):
            self.string_import = string_import
            self.class_attr = class_attr
            self.value = None

        def __get__(self, instance, class_obj):
            if instance or self.class_attr and class_obj and self.value is None:
                self.value = import_by_string(self.string_import)

            return self.value

    extended_attrs: ClassVar[set] = {
        "imported_string_attrs",
        "imported_string_class_attrs",
    }

    imported_string_attrs: ClassVar[tuple] = ()
    """Кортеж атрибутов ожидающих импорта"""
    imported_string_class_attrs: ClassVar[tuple] = ()
    """Кортеж атрибутов класса ожидающих импорта"""

    def __init_subclass__(cls, string_imported_base=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if not string_imported_base:
            cls.wrap_string_imported_attrs()

    @classmethod
    def _wrap_string_imported_attr(cls, attr: str, class_attr: bool = False):
        """Присвоить аргументу значение дескриптора

        Args:
            attr: Имя атрибута
            class_attr: Импортировать при обращении к классу

        """
        value = getattr(cls, attr, None)
        if isinstance(value, str):
            descriptor = cls._ImportedStringDescriptor(value, class_attr=class_attr)
            setattr(cls, attr, descriptor)

    @classmethod
    def wrap_string_imported_attrs(cls):
        """Присвоить аргументам значения дескрипторов"""
        for attr in cls.imported_string_attrs:
            cls._wrap_string_imported_attr(attr)
        for attr in cls.imported_string_class_attrs:
            cls._wrap_string_imported_attr(attr, True)


class SingletonMixin:
    """Миксин singleton принимающий аргументы, на основе которых необходимо держать единственный экземпляр

    Examples:
        >>> class HasPermission(SingletonMixin, singleton_args=("permission_name",)):
        >>>     def __init__(self, permission_name: str):
        >>>         self.permission_name = permission_name
    """

    _instances = None
    _singleton_args = None

    def __init_subclass__(cls, singleton_args: tuple | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if singleton_args is not None:
            cls._singleton_args = singleton_args
            cls._instances = {}

    def __new__(cls, *args, **kwargs):
        if cls._instances is None:
            cls._instances = super().__new__(cls)
        if cls._instances and not cls._singleton_args:
            return cls._instances

        args_values = get_params_values(cls.__init__, "self", *args, params=cls._singleton_args, **kwargs)
        if args_values not in cls._instances:
            cls._instances[args_values] = super().__new__(cls)
        return cls._instances[args_values]
