from typing import TypeVar

from ..protos.photo_cop_pb2 import PhotoCopDecision

from .basebot import (
    ArchiveData,
    BaseBot,
    PhotoCopMatchException,
    BotCommandArgs,
    BotCommandArgsException,
    InvalidCredentialsException,
    MediaType,
)

BotType = TypeVar("BotType", bound=BaseBot)

from .archivebot import ArchiveBot
from .basebot import (
    ArchiveData,
    BaseBot,
    BotCommandArgs,
    BotCommandArgsException,
    MediaType,
)
from .chatbot import ChatBot
from .databasebot import DatabaseBot
from .debugbot import DebugBot
from .onboardbot import OnboardBot
from .registerbot import RegisterBot
from .userservicesbot import UserServicesBot
