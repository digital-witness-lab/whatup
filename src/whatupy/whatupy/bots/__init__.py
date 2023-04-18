from typing import TypeVar

from .basebot import BaseBot
from .archivebot import ArchiveBot
from .chatbot import ChatBot
from .onboardbot import OnboardBot

BotType = TypeVar("BotType", bound=BaseBot)
