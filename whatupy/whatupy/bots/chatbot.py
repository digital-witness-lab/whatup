import asyncio
import logging
import math
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime, timedelta
import random
import typing as T

from .. import utils
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot


logger = logging.getLogger(__name__)
ChatBotType = T.TypeVar("ChatBot", bound=BaseBot)
CHATBOT_FRIEND_JIDS: T.Dict[str, ChatBotType] = {}


class ChatBot(BaseBot):
    __version__ = "1.0.0"

    def __init__(
        self,
        response_time: float,
        *args,
        **kwargs,
    ):
        self.response_time = response_time
        self.pending_messages = defaultdict(int)
        kwargs["read_historical_messages"] = False
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)

    async def post_start(self, **kwargs):
        jid_anon_str = utils.jid_to_str(self.jid_anon)
        CHATBOT_FRIEND_JIDS[jid_anon_str] = self
        self.logger.info("Logged self as an active chatbot.")
        await self.initiate_friend_chats()

    async def initiate_friend_chats(self, *args, **kwargs):
        self.logger.info("Greeting friends")
        for friend in CHATBOT_FRIEND_JIDS.values():
            if utils.same_jid(friend.jid, self.jid):
                continue
            self.logger.info(f"Saying hello to: {friend.username}")
            await asyncio.sleep(5)
            await self.send_text_message(friend.jid, self.generate_message())

    async def on_message(self, message: wuc.WUMessage, **kwargs):
        if message.info.source.isFromMe or message.info.source.isGroup:
            return

        friend_jid_anon: str = utils.jid_to_str(message.info.source.chat)
        if friend_jid_anon is None:
            self.logger.critical("Message has no chat_JID")
            return
        friend = CHATBOT_FRIEND_JIDS.get(friend_jid_anon)
        if friend is None:
            return
        await self.chat_with_friend(friend)

    async def chat_with_friend(self, friend: ChatBotType):
        if n_pending := self.pending_messages.get(friend.username):
            if random.random() > 1 / n_pending:
                self.logger.info(
                    f"Not responding to this message because there are too many queued for anon chat {friend.username}: {n_pending}"
                )
                return

        wait_time = random.expovariate(self.message_response_rate_local())
        self.logger.info(f"Sending message in {timedelta(seconds=wait_time)}: {friend.username}")

        self.pending_messages[friend.username] += 1
        await asyncio.sleep(wait_time)

        self.logger.info(f"Sending message to: {friend.username}")
        response = self.generate_message()
        status = await self.send_text_message(friend.jid, response)
        self.pending_messages[friend.username] -= 1

    def message_response_rate_local(self, scale=0.5):
        now = datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        seconds_per_day = 60 * 60 * 24

        # alpha is 1 at noon, -1 at midnight
        alpha = 2 * (math.sin(seconds_since_midnight / seconds_per_day * math.pi) - 0.5)
        # beta scales from 1 - scale to 1 + scale
        beta = alpha * scale + 1
        self.logger.info("alpha=%f,  beta=%f, response_time=%f", alpha, beta, self.response_time / beta)
        return beta / self.response_time

    def generate_message(self) -> str:
        n_words = random.randint(1, 24)
        return " ".join(utils.random_words(n_words))

    def stop(self):
        CHATBOT_FRIEND_JIDS.pop(self.strAnonJID)
        super().stop()
