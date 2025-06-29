from __future__ import annotations

import inspect
from collections.abc import Hashable
from collections.abc import Mapping
from functools import wraps
from typing import Any
from typing import TYPE_CHECKING

from contrib.inspect.services import get_params_with_values
from contrib.localization.services import gettext_lazy as _

if TYPE_CHECKING:
    from contrib.clean_architecture.providers.controllers.bases import Controller


class _MissingParameterError(Exception):
    """Ошибка при декорировании функции без параметра, необходимого для работы декоратора."""

    def __init__(self, parameter_name: str):
        super().__init__(
            _("Декоратору требуется параметр {parameter_name} для корректной работы").format(
                parameter_name=parameter_name
            )
        )


class Permission:
    bind: tuple[str, ...]
    args: tuple[Any, ...]
    mapping: dict[str, str]
    kwargs: dict[str, Any]
    method: str | None

    def __init__(
        self,
        method: str,
        *bind: str,
        mapping: Mapping[str, str] = None,
        args: tuple[Any, ...] = None,
        **kwargs: Any,
    ):
        self.bind = bind
        self.args = args or ()
        self.mapping = mapping or {}
        self.kwargs = kwargs
        self.method = method


class Permissions:
    _registered: dict[Hashable, type[Permissions]] = {}

    _name: str
    _owner: type[Controller]
    _controller: Controller
    _interactor: interactor
    _permissions: dict[str, Permission]

    def __init__(self, **permissions: Permission):
        self._permissions = permissions

    def __set_name__(self, owner: type[Controller], name):
        self._name = name
        if not hasattr(owner, "__permissions__"):
            owner.__permissions__ = []

        owner.__permissions__.append(self)

    def initialize(self, controller: Controller) -> None:
        self._controller = controller
        for method_name, permission in self._permissions.items():
            self.decorate(method_name, permission)

    def decorate(self, method_name: str, permission: Permission):
        method = getattr(self.controller, method_name)
        original_method = inspect.unwrap(method)

        @wraps(method)
        def wrapper(*args, **kwargs):
            params = [*permission.bind, *permission.mapping.keys()]
            bind_kwargs = get_params_with_values(original_method, "self", *args, params=params, **kwargs)
            for key, value in permission.mapping.items():
                bind_kwargs[value] = bind_kwargs[key]
                del bind_kwargs[key]

            getattr(self.interactor, permission.method)(*permission.args, **bind_kwargs, **permission.kwargs)
            return method(*args, **kwargs)

        setattr(self.controller, method_name, wrapper)

    @property
    def controller(self):
        return self._controller

    @property
    def interactor(self):
        return getattr(self._controller, self._name)
