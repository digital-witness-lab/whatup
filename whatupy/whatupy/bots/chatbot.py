import asyncio
import logging
import random
import typing as T

from .. import utils
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot

logger = logging.getLogger(__name__)
CHATBOT_FRIEND_JIDS: T.List[wuc.JID] = []

class ChatBot(BaseBot):
    __version__ = "1.0.0"
    
    def __init__( 
        self,
        response_time: float = 60,
        response_time_sigma: float = 15,
        *args,
        **kwargs,
    ):
        self.response_time = response_time
        self.response_time_sigma = response_time_sigma
        self.pending_messages: T.Dict[str, int] = {} 
        self.JID: wuc.JID = self.core_client.GetConnectionStatus(wuc.ConnectionStatusOptions()).JID
        super().__init__(*args, **kwargs)
        CHATBOT_FRIEND_JIDS.append(self.JID)

    async def start(self, **kwargs):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(super.start())
            tg.create_task(self.initiate_friend_chats)

    async def initiate_friend_chats(self, *args, **kwargs):
        self.logger.info("Greeting friends")
        for friend in CHATBOT_FRIEND_JIDS:
            if friend == self.JID: continue
            self.logger.info(f"Saying hello to: {friend}")
            await asyncio.sleep(5)
            await self.send_text_message(friend, {"text": self.generate_message()}) 

    async def on_message(self, message: wuc.WUMessage):
        if message.info.source.isFromMe or message.info.source.isGroup:
            return
    
        chat_JID = message.info.source.chat
        if chat_JID is None:
            self.logger.critical("Message has no chat_JID")
            return
        if chat_JID not in CHATBOT_FRIEND_JIDS:
            return

        if n_pending := self.pending_messages.get(chat_JID):
            if random.random() > 1 / n_pending:
                self.logger.info(
                    f"Not responding to this message because there are too many queued for chat {chat_JID}: {n_pending}"
                )
                return
        
        response = self.generate_message()
        wait_time = max(
            1.0, random.normalvariate(self.response_time, self.response_time_sigma)
        )
        self.logger.info(f"Sending message in {wait_time}seconds: {chat_JID}: {response}")

        self.pending_messages.setdefault(chat_JID, 0)
        self.pending_messages[chat_JID] += 1
        await asyncio.sleep(wait_time)
        self.pending_messages[chat_JID] -= 1

        status = await self.send_text_message(chat_JID, {"text": response})
        self.logger.info(f"Send status: {status}")
        return

    def generate_message(self) -> str:
        n_words = random.randint(1, 20)
        return " ".join(utils.random_words(n_words))
    
    def stop(self):
        CHATBOT_FRIEND_JIDS.remove(self.JID)
        self.stop()
