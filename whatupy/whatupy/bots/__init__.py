from typing import TypeVar

from .basebot import (
    ArchiveData,
    BaseBot,
    BotCommandArgs,
    BotCommandArgsException,
    MediaType,
)
from .archivebot import ArchiveBot
from .chatbot import ChatBot
from .databasebot import DatabaseBot
from .onboardbot import OnboardBot

BotType = TypeVar("BotType", bound=BaseBot)
