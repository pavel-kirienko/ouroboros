# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import pathlib
import logging
import importlib
import pyuavcan
from ouroboros.auxiliary import filesystem


with open(pathlib.Path(__file__).parent / 'VERSION') as _version:
    __version__ = _version.read().strip()
__version_info__ = tuple(map(int, __version__.split('.')[:3]))
__license__ = 'MIT'
__author__ = 'UAVCAN Development Team'


LOGGING_LEVEL = 'INFO'
logging.basicConfig(stream=sys.stderr,
                    level=LOGGING_LEVEL,
                    format='%(asctime)s %(levelname)s: %(name)s: %(message)s')


CORE_DSDL_GENERATED_DIR = filesystem.get_dsdl_generated_dir() / 'core'
sys.path.insert(0, str(CORE_DSDL_GENERATED_DIR))


try:
    import uavcan
    import ouroboros_ipc
except (ImportError, AttributeError):
    pyuavcan.dsdl.generate_package(
        root_namespace_directory=filesystem.get_ipc_dsdl_dir(),
        lookup_directories=[filesystem.get_public_regulated_data_types_dir() / 'uavcan'],
        output_directory=CORE_DSDL_GENERATED_DIR,
    )
    pyuavcan.dsdl.generate_package(
        root_namespace_directory=filesystem.get_public_regulated_data_types_dir() / 'uavcan',
        output_directory=CORE_DSDL_GENERATED_DIR,
    )
    importlib.invalidate_caches()
    import uavcan
    import ouroboros_ipc
