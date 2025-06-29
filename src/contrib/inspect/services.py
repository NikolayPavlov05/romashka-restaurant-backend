from __future__ import annotations

import inspect
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from types import FunctionType
from typing import Any
from typing import Union


def get_params_values(function: Callable, *args, params: Iterable[str] | None, **kwargs):
    result = []
    function = inspect.unwrap(function)
    spec = inspect.getfullargspec(function)

    for param in params:
        if param in kwargs:
            result.append(kwargs[param])
        elif spec.kwonlydefaults and param in spec.kwonlydefaults:
            result.append(spec.kwonlydefaults[param])
        else:
            func_args = [arg for arg in spec.args if arg not in kwargs]
            func_argument_index = spec.args.index(param)
            argument_index = func_args.index(param)
            if len(args) > argument_index:
                result.append(args[argument_index])
            else:
                result.append(spec.defaults[func_argument_index - len(spec.args) + len(spec.defaults)])

    return tuple(result)


def get_params_with_values(function: Callable, *args, params: Iterable[str] | None, **kwargs):
    values = get_params_values(function, *args, params=params, **kwargs)
    return {param: value for param, value in zip(params, values)}


def replace_args_values(replaces: Mapping[str, Any], function: Callable, *args, none_only=False, **kwargs):
    spec = inspect.getfullargspec(function)
    args = list(args)
    for key, value in replaces.items():
        if none_only:
            if key in kwargs and kwargs[key] is not None:
                continue
            if key in spec.args:
                argument_index = spec.args.index(key)
                if argument_index < len(args) and args[argument_index] is not None:
                    continue

        if key in kwargs or spec.kwonlydefaults and key in spec.kwonlydefaults:
            kwargs[key] = value
        elif key not in spec.args:
            kwargs[key] = value
        else:
            argument_index = spec.args.index(key)
            if argument_index < len(args):
                args[argument_index] = value
            else:
                kwargs[key] = value

    return tuple(args), kwargs


def insert_parameter(
    function: FunctionType,
    parameter: inspect.Parameter,
    position: int,
    wrapper: Callable = None,
):
    original_signature = inspect.signature(function)
    parameters = list(original_signature.parameters.values())
    parameters.insert(position, parameter)
    overridden_signature = original_signature.replace(parameters=parameters)

    target = wrapper if wrapper else function
    target.__signature__ = overridden_signature
    if parameter.annotation:
        target.__annotations__[parameter.name] = parameter.annotation


def replace_signature(source: FunctionType, target: Callable = None):
    original_signature = inspect.signature(source)
    target.__signature__ = original_signature


def sequence_type_check(annotation: Any):
    is_sequence, origin_type = False, None

    try:
        if annotation.__origin__ is Union:
            annotation = annotation.__args__[0]

        is_sequence = issubclass(annotation.__origin__, Sequence)
        if is_sequence:
            origin_type = annotation.__args__[0]
        else:
            origin_type = annotation
    except (TypeError, AttributeError):
        try:
            is_sequence, origin_type = sequence_type_check(annotation.__args__[0])
        except AttributeError:
            origin_type = annotation

    return is_sequence, origin_type
