import logging
import random
import typing as T

from whatupy.whatupy import utils

from . import BaseBot

logger = logging.getLogger(__name__)

class ChatBot(BaseBot):
    __version__ = "1.0.0"
    
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


    def generate_message(self) -> str:
        n_words = random.randint(1, 20)
        return " ".join(utils.random_words(n_words))