import json
from pathlib import Path

import qrcode
import dataset

from .. import NotRegisteredError, utils
from . import BaseBot
from . import BotCommandArgs, MediaType
from ..protos import whatupcore_pb2 as wuc
from ..connection import WhatUpAuthentication


class RegisterBot(BaseBot):
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)
        kwargs["read_historical_messages"] = False
        super().__init__(*args, **kwargs)

    def setup_command_args(self):
        parser = BotCommandArgs(
            prog=self.__class__.__name__,
            description="Bot for onboarding users doing data donations",
        )
        sub_parser = parser.add_subparsers(dest="command")

        register = sub_parser.add_parser(
            "register",
            description="Register a given user as a user",
        )
        register.add_argument(
            "alias",
            type=str,
            help="Alias for user in data records",
            default=None,
        )

        register_bot = sub_parser.add_parser(
            "register-bot",
            description="Register a given user as a user",
        )
        register_bot.add_argument(
            "alias",
            type=str,
            help="Alias for bot in data records",
            default=None,
        )
        return parser

    async def on_control(self, message):
        params = await self.parse_command(message)
        self.logger.info("Got command: %s", params)
        if params is None:
            return
        sender: wuc.JID = message.info.source.sender

        is_bot: bool
        if params.command == "register":
            is_bot = False
        elif params.command == "register-bot":
            is_bot = True
        else:
            return await self.send_text_message(
                sender,
                f"Unknown command: {params.command}",
            )

        alias = params.alias or "-".join(utils.random_words(5))
        if not alias.isalnum():
            return await self.send_text_message(
                sender,
                f"Invalid alias... must only be alpha-numeric: {alias}",
            )

        return await self.start_registration(sender, alias, is_bot=is_bot)

    async def start_registration(
        self,
        handler_jid: wuc.JID,
        username: str,
        is_bot: bool,
    ):
        if is_bot:
            default_group_permission = wuc.GroupPermission.READWRITE
        else:
            default_group_permission = wuc.GroupPermission.DENIED

        logger = self.logger.getChild(username)
        logger.info("Registering user")
        passphrase = utils.random_passphrase()
        authenticator = WhatUpAuthentication()
        try:
            async for qrcode in authenticator.register(
                username, passphrase, default_group_permission
            ):
                content = utils.qrcode_gen_bytes(qrcode, kind="png")
                await self.send_media_message(
                    handler_jid,
                    MediaType.MediaImage,
                    content=content,
                    caption=f"Registration QR code",
                    mimetype="image/png",
                    filename=f"register-{username}",
                )

        except NotRegisteredError:
            logger.exception("Could not register user")
            return
        logger.info("User registered")
        credentials = {"username": username, "passphrase": passphrase}
        credentials_file = self.sessions_dir / f"{username}.json"
        with credentials_file.open("w+") as fd:
            json.dump(credentials, fd)

        self.db["registered_users"].insert(
            {
                "username": username,
                "is_bot": is_bot,
            }
        )
        # now how to trigger user services.... ?
        await self.send_text_message(
            handler_jid,
            "User registered",
        )
