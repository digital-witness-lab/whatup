from typing import TypeVar

from .basebot import BaseBot, BotCommandArgs, BotCommandArgsException
from .archivebot import ArchiveBot
from .chatbot import ChatBot
from .onboardbot import OnboardBot
from .databasebot import DatabaseBot

BotType = TypeVar("BotType", bound=BaseBot)
