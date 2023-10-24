from typing import TypeVar

from .basebot import (
    ArchiveData,
    BaseBot,
    BotCommandArgs,
    BotCommandArgsException,
    MediaType,
)

BotType = TypeVar("BotType", bound=BaseBot)

from .archivebot import ArchiveBot
from .basebot import (ArchiveData, BaseBot, BotCommandArgs,
                      BotCommandArgsException, MediaType)
from .chatbot import ChatBot
from .databasebot import DatabaseBot
from .debugbot import DebugBot
from .onboardbot import OnboardBot
from .debugbot import DebugBot
from .registerbot import RegisterBot
from .userservicesbot import UserServicesBot
