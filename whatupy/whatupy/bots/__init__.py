from typing import TypeVar

from .basebot import (
    ArchiveData,
    BaseBot,
    BotCommandArgs,
    BotCommandArgsException,
    MediaType,
)
from .archivebot import ArchiveBot
from .chatbot2 import ChatBot2
from .databasebot import DatabaseBot
from .onboardbot import OnboardBot

BotType = TypeVar("BotType", bound=BaseBot)
