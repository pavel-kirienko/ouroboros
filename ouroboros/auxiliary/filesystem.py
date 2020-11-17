# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import os
import sys
import typing
import pathlib


AnyPath = typing.Union[str, pathlib.Path]


def get_user_data_dir() -> pathlib.Path:
    if sys.platform.startswith('win32'):
        _appdata = pathlib.Path(os.getenv('LOCALAPPDATA') or os.getenv('APPDATA'))
        return _prepare(_appdata / 'UAVCAN' / 'Ouroboros')
    else:
        return _prepare(pathlib.Path('~/.uavcan/ouroboros').expanduser())


def get_log_dir() -> pathlib.Path:
    return _prepare(get_user_data_dir() / 'log')


def get_version_specific_dir() -> pathlib.Path:
    from ouroboros import __version__
    return _prepare(get_user_data_dir() / f'v{__version__}')


def get_dsdl_generated_dir() -> pathlib.Path:
    return _prepare(get_version_specific_dir() / 'dsdl_generated')


def get_package_root_dir() -> pathlib.Path:
    import ouroboros
    return pathlib.Path(ouroboros.__file__).parent


def get_public_regulated_data_types_dir() -> pathlib.Path:
    # TODO: this currently only works when running from sources, obviously.
    return get_package_root_dir().parent / 'submodules' / 'public_regulated_data_types'


def get_ipc_dsdl_dir() -> pathlib.Path:
    # TODO: this currently only works when running from sources, obviously.
    return get_package_root_dir().parent / 'ouroboros_ipc'


def _prepare(directory: AnyPath) -> pathlib.Path:
    directory = pathlib.Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory
