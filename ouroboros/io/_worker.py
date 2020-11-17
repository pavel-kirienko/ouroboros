# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import asyncio
from pyuavcan.application import Node
from pyuavcan.presentation import Publisher, Subscriber
from . import Frame, Configuration, Transfer, Status


async def run(node:         Node,
              pubs_frame:   typing.Sequence[Publisher[Frame]],
              pub_status:   Publisher[Status],
              sub_config:   Subscriber[Configuration],
              sub_transfer: Subscriber[Transfer]) -> None:
    node.close()
    await asyncio.wait(asyncio.all_tasks(), timeout=1)
