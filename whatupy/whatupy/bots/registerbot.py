from datetime import datetime
import re

import qrcode
import dataset

from .. import NotRegisteredError, UsernameInUseError, utils
from . import BaseBot
from . import BotCommandArgs, MediaType
from ..protos import whatupcore_pb2 as wuc
from ..connection import create_whatupcore_clients
from ..credentials_manager import CredentialsManager, Credential


VALID_ALIAS = re.compile(r"^[a-zA-Z0-9_-]+$")


class RegisterBot(BaseBot):
    def __init__(
        self,
        credentials_manager: CredentialsManager,
        database_url: str,
        *args,
        **kwargs,
    ):
        self.connection_params = {f: kwargs[f] for f in ("host", "port", "cert")}
        self.credentials_manager = credentials_manager
        self.db: dataset.Database = dataset.connect(database_url)
        kwargs["read_historical_messages"] = False
        kwargs["mark_messages_read"] = True
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

        alias = str(params.alias) or "-".join(utils.random_words(5))
        if not alias or VALID_ALIAS.match(alias) is None:
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
        core_client, authenticator = create_whatupcore_clients(**self.connection_params)
        try:
            async for qrcode in authenticator.register(
                username, passphrase, default_group_permission
            ):
                content = utils.qrcode_gen_bytes(qrcode, kind="png")
                await self.send_media_message(
                    handler_jid,
                    MediaType.MediaImage,
                    content=content,
                    caption=f"Registration QR code for {username}",
                    mimetype="image/png",
                    filename=f"register-{username}",
                )
        except NotRegisteredError:
            logger.exception(f"Could not register user {username}")
            return
        except UsernameInUseError:
            logger.error("Tried to register with existing username: %s", username)
            return await self.send_text_message(
                handler_jid,
                f'Alias "{username}" is already in use. Please select a different one',
            )
        logger.info(f"User {username} registered")

        meta = {
            "registerbot__timestamp": datetime.now().isoformat(),
            "registerbot__triggered_by": handler_jid,
            "registerbot__default_permission": wuc.GroupPermission.Name(
                default_group_permission
            ),
        }
        credential = Credential(username=username, passphrase=passphrase, meta=meta)
        self.credentials_manager.write_credential(credential)

        connection_status = await core_client.GetConnectionStatus(
            wuc.ConnectionStatusOptions()
        )
        self.db["registered_users"].delete(username=username)
        self.db["registered_users"].insert(
            {
                "username": username,
                "is_bot": is_bot,
                "jid_anon": utils.jid_to_str(connection_status.JIDAnon),
            }
        )
        # now how to trigger user services.... ?
        await self.send_text_message(
            handler_jid,
            f"User {username} registered",
        )
        await self.send_text_message(
            connection_status.JID,
            "Welcome to the WhatsApp Watch system! You have been added to our first trial which will last until Dec 1, 2023",
        )
