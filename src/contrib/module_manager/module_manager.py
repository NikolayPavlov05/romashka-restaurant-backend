from __future__ import annotations

import inspect
from abc import ABC
from abc import ABCMeta
from collections import defaultdict
from collections import OrderedDict
from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import Sequence
from copy import copy
from threading import RLock
from typing import Any
from typing import cast
from typing import TypeVar

from .exceptions import DependencyNotInstalledError
from .exceptions import DependencyTypeError
from .types import _EMPTY
from .types import DependencyInjectorProto
from .types import FabricProvider
from .utils import extract_hints_depends
from .utils import get_all_depends_types
from .utils import get_app_label
from .utils import get_safe_type_hints
from .utils import get_type
from .utils import is_class
from .utils import is_empty_type
from .utils import is_loaded_depend_type
from .utils import is_str_depend_type

_T = TypeVar("_T")

_modules_file_name = "module"


class ModuleManager(ABCMeta):
    _registered: dict[str, AppModule] = OrderedDict()
    _modules_by_app_label: dict[str, AppModule] = {}
    _installed_modules: tuple[str, ...] = ()
    _exports: dict[str, dict[type[Any], object]] = defaultdict(dict)
    _providers_by_module: dict[AppModule, dict[type[Any], object]] = defaultdict(dict)
    _modules_file_name: str = _modules_file_name

    loaded = False
    lock = RLock()

    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        if cls.__base__ is not BaseAppModule:
            app_module = cls()
            mcls._registered[app_module.package_name] = app_module
            mcls.loaded = False
        return cls

    @classmethod
    def ready(cls):
        return cls.loaded

    @classmethod
    def reload(cls):
        cls.loaded = False
        cls.load_modules(cls.installed_modules)

    @classmethod
    def get_app_module(cls, module_name: str) -> AppModule | None:
        return cls._modules_by_app_label.get(module_name) or ModuleManager._registered.get(module_name)

    @classmethod
    def get_dep_for_app_module(cls, app_module: AppModule, dep_type: type[_T]) -> _T:
        return cls._providers_by_module[app_module].get(dep_type) or cls._exports[app_module.app_label].get(dep_type)

    @classmethod
    def get_app_module_name_from_dep(cls, dep_type: type[Any]) -> str:
        return dep_type.__appmodule_name__

    @classmethod
    def get_app_module_from_dep(cls, dep_type: type[Any]):
        return cls.get_app_module(cls.get_app_module_name_from_dep(dep_type))

    @classmethod
    def get_dep_use_adapter(
        cls,
        app_module: AppModule,
        dep_type: type[Any],
        to_inject_entity: type[Any] | Callable[..., Any] | None,
        find_in_module: bool,
    ):
        dep_type = app_module.mapping.get(dep_type, dep_type)  # type: ignore
        if inspect.isfunction(dep_type):
            if not len(inspect.signature(dep_type).parameters):
                dep_type = dep_type()
            else:
                dep_type = dep_type(to_inject_entity)

        if find_in_module:
            return cls.get_dep_for_app_module(app_module, dep_type)
        return cls._exports[app_module.app_label].get(dep_type)

    @classmethod
    def get_depends(
        cls,
        app_modules_names: set[str],
        callable_: Callable[..., Any] | type[Any],
        extracted_dep_types: list[tuple[str, type]],
        find_in_module: bool = False,
        defaults: dict[str, Any] | None = None,
        check_all: bool = False,
    ):
        depends: dict[str, object] = {}
        _is_class = is_class(callable_)
        for name, _type in extracted_dep_types:
            dep = None
            if is_loaded_depend_type(_type):
                dep_module_name = cls.get_app_module_name_from_dep(_type)
                if dep_module_name not in app_modules_names:
                    raise DependencyNotInstalledError(
                        f"Dependency `{name}`:` Depend[{_type.__name__}] in {callable_.__module__}.{callable_.__name__}"
                        f" not found in modules {app_modules_names}"
                    )
                dep_module = cls.get_app_module_from_dep(_type)
                dep = cls.get_dep_use_adapter(dep_module, _type, callable_, find_in_module=find_in_module)

            if _is_class:
                if defaults:
                    default_value = defaults.get(name, _EMPTY)
                else:
                    default_value = getattr(callable_, name, _EMPTY)

                if all([dep is None, is_empty_type(default_value)]):
                    if (check_all and is_empty_type(_type)) or is_str_depend_type(_type):
                        raise DependencyTypeError(
                            f"Type error in the '{callable_.__module__}.{callable_.__name__}'\n"
                            f"Won't find the type in the local scope, for the `{name}` field, "
                            f"maybe you forgot to connect the application? "
                            f"or if it is not required, then specify the default value `None`"
                        )
                    elif not is_empty_type(_type):
                        raise DependencyTypeError(
                            f"Type error in the '{callable_.__module__}.{callable_.__name__}'"
                            f" property '{name}' with type: '{_type.__module__}.{_type.__name__}'"
                            f" not injected"
                        )
            else:
                signature = inspect.signature(callable_)
                param = signature.parameters[name]
                if all([dep is None, param.default is param.empty]):
                    raise DependencyTypeError(
                        f"Type error in the module '{callable_.__module__}' and func '{callable_.__qualname__}'"
                        f" parameter '{param.name}' with type: '{callable_.__module__}.{callable_.__name__}'"
                        f" not injected"
                    )
            depends[name] = dep
        return depends

    @classmethod
    def inject_to_obj(cls, app_modules_names: set[str], obj: object, find_in_module: bool = False):
        depends = cls.get_depends(
            app_modules_names,
            obj.__class__,
            extract_hints_depends(obj.__class__),
            find_in_module=find_in_module,
        )

        for name, dep in depends.items():
            setattr(obj, name, dep)

        if isinstance(obj, DependencyInjectorProto):
            inject_signature = inspect.signature(obj.__inject__)
            type_hints = get_safe_type_hints(obj.__inject__, localns=get_all_depends_types())
            _kind_args_kwargs = {"VAR_POSITIONAL", "VAR_KEYWORD"}
            extracted_dep_types = [
                (arg_name, get_type(type_hints[arg_name]))
                for arg_name, param in inject_signature.parameters.items()
                if param.kind.name not in _kind_args_kwargs
            ]
            defaults = {
                name: param.default
                for name, param in inject_signature.parameters.items()
                if param.default is not param.empty
            }
            depends = cls.get_depends(
                app_modules_names,
                obj.__class__,
                extracted_dep_types,
                find_in_module=find_in_module,
                defaults=defaults,
            )
            obj.__inject__(**depends)

    @classmethod
    def load_modules(
        cls,
        installed_modules: Sequence[str],
        modules_file_name: str = _modules_file_name,
    ):
        if cls.loaded:
            return
        with cls.lock:
            cls.modules_file_name = modules_file_name
            cls.installed_modules = tuple(installed_modules)
            all_apps_labels: set[str] = set()
            for package_name in cls.installed_modules:
                module_name = f"{package_name}.{cls.modules_file_name}"
                all_apps_labels.add(get_app_label(package_name))
                try:
                    __import__(module_name)
                except ImportError as e:
                    if e.name != module_name:
                        raise e

            all_providers: list[object] = []

            for package_name, app_module in cls._registered.items():
                cls._modules_by_app_label[app_module.app_label] = app_module
                for key in app_module.mapping.keys():
                    key.__appmodule_name__ = app_module.app_label

                for provider_type in app_module.providers:
                    klass = provider_type
                    if isinstance(provider_type, FabricProvider):
                        cls._providers_by_module[app_module][provider_type.klass] = provider_type.klass(
                            *(provider_type.args or ()),
                            **(provider_type.kwargs or {}),
                        )
                        klass = provider_type.klass
                    else:
                        cls._providers_by_module[app_module][provider_type] = provider_type()
                    klass.__appmodule_name__ = app_module.app_label

                for export_type in app_module.exports:
                    dep = cls.get_dep_for_app_module(app_module, export_type)
                    cls._exports[app_module.app_label][export_type] = dep or export_type
                    all_providers.append(cls._exports[app_module.app_label][export_type])
                    export_type.__appmodule_name__ = app_module.app_label

            for package_name, app_module in cls._registered.items():
                find_in_app_modules = {app_module.app_label} | set(app_module.imports)
                for app_label in app_module.dependencies:
                    if app_label not in all_apps_labels:
                        raise DependencyNotInstalledError(
                            f"Module `{app_module.app_label}` depends on module `{app_label}`"
                        )
                for dep_type in app_module.providers:
                    klass = dep_type.klass if isinstance(dep_type, FabricProvider) else dep_type
                    cls.inject_to_obj(
                        find_in_app_modules,
                        cls.get_dep_for_app_module(app_module, klass),
                        find_in_module=True,
                    )

            cls.loaded = True


class BaseAppModule(ABC):
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = cast(AppModule, super().__new__(cls, *args, **kwargs))
            cls.instance.dependencies = copy(cls.instance.dependencies)
            cls.instance.mapping = copy(cls.instance.mapping)
            cls.instance.imports = copy(cls.instance.imports)
            cls.instance.exports = copy(cls.instance.exports)
            cls.instance.providers = copy(cls.instance.providers)
        return cls.instance


class AppModule(BaseAppModule, metaclass=ModuleManager):
    name: str | None = None
    dependencies: Sequence[str] = []
    mapping: dict[Hashable, type[Any] | Callable[[type[Any]], type[Any]] | Callable[[], type[Any]]] = {}
    imports: Sequence[str] = []
    exports: Sequence[type[Any]] = []
    providers: Sequence[type[Any] | FabricProvider] = []
    __package_name = None

    @property
    def package_name(self):
        if not self.__package_name:
            self.__package_name = self.__module__.replace(f".{ModuleManager.modules_file_name}", "")
        return self.__package_name

    @property
    def app_label(self):
        if self.name is None:
            self.name = get_app_label(self.package_name)
        return self.name

    def get_service_instance(self, service_type: type[_T]) -> _T | None:
        # type: ignore
        return ModuleManager.get_dep_use_adapter(self, service_type, to_inject_entity=None, find_in_module=True)
