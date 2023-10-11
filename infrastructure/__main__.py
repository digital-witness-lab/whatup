# Import this first to register the services first.
import gcp_services  # noqa: F401

from services import whatupcore2, bot_archive, bot_db  # noqa: F401
from jobs import bot_db_load_archive, bot_onboard_bulk, db_migrations  # noqa: E501,F401
