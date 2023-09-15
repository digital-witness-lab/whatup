import logging
from functools import partial

import aioconsole
from aioconsole.console import AsynchronousConsole

from .. import utils
from ..protos import whatsappweb_pb2 as waw
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot

logger = logging.getLogger(__name__)


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
        g = {**locals(), **globals()}
        factory = partial(AsynchronousConsole, locals=g)
        server = await aioconsole.start_interactive_server(
            factory=factory, host=self.debug_host, port=self.debug_port
        )
