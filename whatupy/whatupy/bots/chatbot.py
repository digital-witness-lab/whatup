import asyncio
import logging
import random
import typing as T

from .. import utils
from . import BaseBot

logger = logging.getLogger(__name__)


class ChatBot(BaseBot):
    def __init__(
        self,
        *args,
        response_time: float = 60,
        response_time_sigma: float = 15,
        friends: T.List[str] = [],
        **kwargs,
    ):
        self.response_time = response_time
        self.response_time_sigma = response_time_sigma
        self.pending_messages: T.Dict[str, int] = {}
        self.friends = friends
        super().__init__(*args, **kwargs)

    async def on_connection_ready(self, *args, **kwargs):
        self.logger.info(f"Subscribing to messages: {args}: {kwargs}")
        await self.messages_subscribe()

        self.logger.info("Greeting friends")
        for friend in self.friends:
            self.logger.info(f"Saying hello to: {friend}")
            await asyncio.sleep(5)
            await self.send_message(friend, {"text": self.generate_message()})

    def generate_message(self) -> str:
        n_words = random.randint(1, 20)
        return " ".join(utils.random_words(n_words))

    async def on_read_messages(self, message):
        if message["key"]["fromMe"] or utils.is_groupchat(message):
            return

        chatid: str = message["key"]["remoteJid"]
        if n_pending := self.pending_messages.get(chatid):
            if random.random() > 1 / n_pending:
                self.logger.info(
                    f"Not responding to this message... too many queued: {chatid}: {n_pending}"
                )
                return

        response = self.generate_message()
        wait_time = max(
            1.0, random.normalvariate(self.response_time, self.response_time_sigma)
        )
        self.logger.info(f"Sending message: {wait_time}seconds: {chatid}: {response}")

        self.pending_messages.setdefault(chatid, 0)
        self.pending_messages[chatid] += 1
        await asyncio.sleep(wait_time)
        self.pending_messages[chatid] -= 1

        status = await self.send_message(chatid, {"text": response})
        self.logger.info(f"Send status: {status}")
