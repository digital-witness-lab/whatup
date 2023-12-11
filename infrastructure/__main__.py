# flake8: noqa

# Import this first to register the services first.
import gcp_services
from jobs import (
    bot_db_load_archive,
    bot_onboard_bulk,
    db_migrations,
    whatupcore_remove_user,
)
from services import bot_archive, bot_db, bot_register, whatupcore2
