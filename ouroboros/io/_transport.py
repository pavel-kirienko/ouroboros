# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import inspect
import logging
import pyuavcan


_logger = logging.getLogger(__name__)


def evaluate_transport_initialization_expression(expression: str) -> pyuavcan.transport.Transport:
    context = _make_evaluation_context()
    out = eval(expression, context)
    _logger.debug('Expression %r yields %r', expression, out)
    if isinstance(out, pyuavcan.transport.Transport):
        return out
    elif isinstance(out, list) and all(isinstance(x, pyuavcan.transport.Transport) for x in out):
        raise NotImplementedError('Redundant IPC transport is not supported')
    else:
        raise ValueError(f'The expression {expression!r} yields an instance of {type(out).__name__!r}. '
                         f'Expected an instance of pyuavcan.transport.Transport or a list thereof.')


def _make_evaluation_context() -> typing.Dict[str, typing.Any]:
    """
    This is basically copied from PyUAVCAN CLI.
    """
    def handle_import_error(parent_module_name: str, ex: ImportError) -> None:
        try:
            tr = parent_module_name.split('.')[2]
        except LookupError:
            tr = parent_module_name
        _logger.warning('Transport %r is not available due to the missing dependency %r', tr, ex.name)

    # noinspection PyTypeChecker
    pyuavcan.util.import_submodules(pyuavcan.transport, error_handler=handle_import_error)

    context: typing.Dict[str, typing.Any] = {
        'pyuavcan': pyuavcan,
    }

    # Expose pre-imported transport modules for convenience.
    for name, module in inspect.getmembers(pyuavcan.transport, inspect.ismodule):
        if not name.startswith('_'):
            context[name] = module

    # Pre-import transport classes for convenience.
    transport_base = pyuavcan.transport.Transport
    # Suppressing MyPy false positive: https://github.com/python/mypy/issues/5374
    for cls in pyuavcan.util.iter_descendants(transport_base):  # type: ignore
        if not cls.__name__.startswith('_') and cls is not transport_base:
            name = cls.__name__.rpartition(transport_base.__name__)[0]
            assert name
            context[name] = cls

    _logger.debug('Transport expression evaluation context (on the next line):\n%r', context)
    return context
