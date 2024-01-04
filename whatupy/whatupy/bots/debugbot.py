import logging
import typing as T
from datetime import datetime
from functools import partial

import aioconsole
from aioconsole.console import AsynchronousConsole
from google.protobuf.timestamp_pb2 import Timestamp

from .. import utils  # noqa
from ..protos import whatsappweb_pb2 as waw  # noqa
from ..protos import whatupcore_pb2 as wuc  # noqa
from . import BaseBot

logger = logging.getLogger(__name__)


async def aiter_to_list(aiter: T.AsyncIterable) -> list:
    result = []
    async for item in aiter:
        result.append(item)
    return result


def iso_to_timestampbb(iso):
    t = Timestamp()
    t.FromDatetime(datetime.fromisoformat(iso))
    return t


class DebugBot(BaseBot):
    __version__ = "1.0.0"

    def __init__(self, debug_host, debug_port, *args, **kwargs):
        self.debug_host = debug_host
        self.debug_port = debug_port
        super().__init__(*args, **kwargs)

    async def post_start(self):
        self.logger.info(
            "Starting debug server on port: %s:%d", self.debug_host, self.debug_port
        )
        c = self.core_client
        g = {**locals(), **globals()}
        factory = partial(AsynchronousConsole, locals=g)
        server = await aioconsole.start_interactive_server(
            factory=factory, host=self.debug_host, port=self.debug_port
        )
