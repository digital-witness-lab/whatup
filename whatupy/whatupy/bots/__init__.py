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
from .debugbot import DebugBot
from .registerbot import RegisterBot
from .userservicesbot import UserServicesBot

BotType = TypeVar("BotType", bound=BaseBot)
