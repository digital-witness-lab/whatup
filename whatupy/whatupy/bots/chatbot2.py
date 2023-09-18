import asyncio
import logging
import random
import typing as T

from .. import utils
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot

logger = logging.getLogger(__name__)

# do not mark messages as read

class ChatBot2(BaseBot):
    __version__ = "1.0.0"
    
    def __init__( 
        self,
        response_time: float = 60,
        response_time_sigma: float = 15,
        friends: T.List[str] = [], # by name? Alice, Bob, etc? 
        *args,
        **kwargs,
    ):
        self.response_time = response_time
        self.response_time_sigma = response_time_sigma
        self.pending_messages: T.Dict[str, int] = {} 
        self.friends = friends
        super().__init__(*args, **kwargs)
        self.message_friends()

    async def initiate_friend_chats(self, *args, **kwargs):
        self.logger.info("Greeting friends")
        for friend in self.friends:
            self.logger.info(f"Saying hello to: {friend}")
            await asyncio.sleep(5)
            # get JIDs for friends - or will we give them directly? 
            await self.send_text_message(friend, {"text": self.generate_message()}) 

    async def on_message(self, message: wuc.WUMessage):
        if message.info.source.isFromMe or message.info.source.isGroup:
            return
    
        chat_id = utils.jid_to_str(message.info.source.chat)
        if chat_id is None:
            self.logger.critical("Message has no chat_id")
            return
        if chat_id not in self.friends:
            return

        if n_pending := self.pending_messages.get(chat_id):
            if random.random() > 1 / n_pending:
                self.logger.info(
                    f"Not responding to this message because there are too many queued for chat {chat_id}: {n_pending}"
                )
                return
        
        response = self.generate_message()
        wait_time = max(
            1.0, random.normalvariate(self.response_time, self.response_time_sigma)
        )
        self.logger.info(f"Sending message in {wait_time}seconds: {chat_id}: {response}")

        self.pending_messages.setdefault(chat_id, 0)
        self.pending_messages[chat_id] += 1
        await asyncio.sleep(wait_time)
        self.pending_messages[chat_id] -= 1

        status = await self.send_text_message(chat_id, {"text": response})
        self.logger.info(f"Send status: {status}")
        # any guarantee that this will never end? 
        return

    def generate_message(self) -> str:
        n_words = random.randint(1, 20)
        return " ".join(utils.random_words(n_words))
