from __future__ import annotations


class BaseModuleManagerError(Exception): ...


class DependencyNotInstalledError(BaseModuleManagerError): ...


class DependencyTypeError(BaseModuleManagerError): ...
