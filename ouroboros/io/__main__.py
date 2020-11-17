# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import click
import typing
import logging
import asyncio
import pyuavcan
import pyuavcan.application
import uavcan.node
from ouroboros import io, __version_info__, get_ipc_node_name


SUBJECT_ID_TYPE = click.IntRange(0, pyuavcan.transport.MessageDataSpecifier.SUBJECT_ID_MASK)


_logger = logging.getLogger(__name__)


@click.command()
@click.argument('ipc-transport-expression',   required=True)
@click.option('--pub-frame-id-min-max', required=True, type=SUBJECT_ID_TYPE, nargs=2)
@click.option('--pub-status-id',        required=True, type=SUBJECT_ID_TYPE)
@click.option('--sub-config-id',        required=True, type=SUBJECT_ID_TYPE)
@click.option('--sub-transfer-id',      required=True, type=SUBJECT_ID_TYPE)
def main(ipc_transport_expression:  str,
         pub_frame_id_min_max:      typing.Tuple[int, int],
         pub_status_id:             int,
         sub_config_id:             int,
         sub_transfer_id:           int) -> None:
    transport = io.evaluate_transport_initialization_expression(ipc_transport_expression)
    if transport.local_node_id is None:
        raise ValueError('IPC transport configuration error: IO worker cannot be an anonymous node')

    pub_frame_id_set = set(range(pub_frame_id_min_max[0], pub_frame_id_min_max[-1] + 1))
    other_list = [pub_status_id, sub_config_id, sub_transfer_id]
    if not pub_frame_id_set:
        raise ValueError('Frame subject-ID set is empty')
    if pub_frame_id_set & set(other_list) or len(set(other_list)) != len(other_list):
        raise ValueError('Conflicting subject-ID values')

    presentation = pyuavcan.presentation.Presentation(transport)

    node_info = pyuavcan.application.NodeInfo(
        protocol_version=uavcan.node.Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
        software_version=uavcan.node.Version_1_0(*__version_info__[:2]),
        name=get_ipc_node_name('io'),
    )

    node = pyuavcan.application.Node(presentation,
                                     info=node_info,
                                     with_diagnostic_subscriber=False)

    from . import Frame, Configuration, Transfer, Status
    pubs_frame = [presentation.make_publisher(Frame, subject_id) for subject_id in pub_frame_id_set]
    pub_status = presentation.make_publisher(Status, pub_status_id)
    sub_config = presentation.make_subscriber(Configuration, sub_config_id)
    sub_transfer = presentation.make_subscriber(Transfer, sub_transfer_id)

    _logger.info(f'Starting IO worker on IPC node {node} using ports:')
    _logger.info(f'- {pubs_frame[0]}')
    _logger.info(f'...<{len(pubs_frame) - 2} instances not shown, {len(pubs_frame)} total>...')
    _logger.info(f'- {pubs_frame[-1]}')
    _logger.info(f'- {pub_status}')
    _logger.info(f'- {sub_config}')
    _logger.info(f'- {sub_transfer}')
    from ._worker import run
    try:
        asyncio.get_event_loop().run_until_complete(run(node, pubs_frame, pub_status, sub_config, sub_transfer))
    finally:
        node.close()


try:
    main()
except Exception as ex:
    _logger.exception(f'IO worker failed: {ex}')
    sys.exit(1)
else:
    sys.exit(0)
