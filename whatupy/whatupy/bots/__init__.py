from typing import TypeVar

from .archivebot import ArchiveBot
from .basebot import (ArchiveData, BaseBot, BotCommandArgs,
                      BotCommandArgsException, MediaType)
from .chatbot import ChatBot
from .databasebot import DatabaseBot
from .debugbot import DebugBot
from .onboardbot import OnboardBot

BotType = TypeVar("BotType", bound=BaseBot)
