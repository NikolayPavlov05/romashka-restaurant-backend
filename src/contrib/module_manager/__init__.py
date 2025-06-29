from __future__ import annotations

from .decorators import inject
from .module_manager import AppModule
from .module_manager import ModuleManager
from .types import Depend
from .types import DependencyInjectorProto
from .types import FabricProvider

get_app_module = ModuleManager.get_app_module
load_modules = ModuleManager.load_modules
get_app_module_name = ModuleManager.get_app_module_name_from_dep

__all__ = [
    "ModuleManager",
    "AppModule",
    "inject",
    "load_modules",
    "get_app_module",
    "get_app_module_name",
    "Depend",
    "DependencyInjectorProto",
    "FabricProvider",
]
