__version__ = "1.0.0"

from . import utils
from .connection import (NotRegisteredError, WhatUpAuthentication,
                         create_whatupcore_clients)
