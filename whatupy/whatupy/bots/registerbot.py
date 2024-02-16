import re
from datetime import datetime

import dataset

from .. import NotRegisteredError, UsernameInUseError, utils
from ..connection import create_whatupcore_clients
from ..credentials_manager import Credential, CredentialsManager
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot, BotCommandArgs, MediaType

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
            "--demo",
            action="store_true",
            default=False,
            help="Whether this is a demo account",
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

        is_bot: bool = False
        is_demo: bool = False
        if params.command == "register":
            is_bot = False
            if params.demo:
                is_demo = True
        elif params.command == "register-bot":
            is_bot = True
        else:
            return await self.send_text_message(
                sender,
                f"Unknown command: {params.command}",
            )

        user_params = {"is_bot": is_bot, "is_demo": is_demo}
        alias = str(params.alias) or "-".join(utils.random_words(5))
        if not alias or VALID_ALIAS.match(alias) is None:
            return await self.send_text_message(
                sender,
                f"Invalid alias... must only be alpha-numeric: {alias}",
            )

        return await self.start_registration(sender, alias, user_params)

    async def start_registration(
        self, handler_jid: wuc.JID, username: str, user_params: dict
    ):
        is_bot = user_params.get("is_bot", False)
        is_demo = user_params.get("is_demo", False)
        if is_bot and not is_demo:
            default_group_permission = wuc.GroupPermission.READWRITE
        else:
            default_group_permission = wuc.GroupPermission.DENIED

        logger = self.logger.getChild(username)
        logger.info("Registering user")
        passphrase = utils.random_passphrase()
        core_client, authenticator = create_whatupcore_clients(**self.connection_params)
        notes = []
        if is_bot:
            notes.append(
                "*NOTE*: the user is being registered as a bot and all their data will be collected on scanning"
            )
        elif is_demo:
            notes.append(
                "*NOTE*: this is a demo user and no data will be collected from the device"
            )
        try:
            async for qrcode in authenticator.register(
                username,
                passphrase,
                default_group_permission,
                get_history=is_bot,
            ):
                content = utils.qrcode_gen_bytes(qrcode, kind="png")
                await self.send_media_message(
                    handler_jid,
                    MediaType.MediaImage,
                    content=content,
                    caption=f"{username} can scan this QR code to link their device. A new code will be sent if the device is not linked in 30 seconds.\n"
                    + "\n".join(notes),
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
            "registerbot__triggered_by": utils.jid_to_str(handler_jid),
            "registerbot__default_permission": wuc.GroupPermission.Name(
                default_group_permission
            ),
        }

        logger.info(f"{username}: Getting connection status")
        connection_status = await core_client.GetConnectionStatus(
            wuc.ConnectionStatusOptions()
        )
        logger.info(f"{username}: Pinging users database")
        self.db["registered_users"].delete(username=username)
        self.db["registered_users"].insert(
            {
                "username": username,
                "is_bot": is_bot,
                "is_demo": is_demo,
                "jid_anon": utils.jid_to_str(connection_status.JIDAnon),
            }
        )

        logger.info(f"{username}: Saving credentials")
        credential = Credential(username=username, passphrase=passphrase, meta=meta)
        self.credentials_manager.write_credential(credential)

        logger.info(f"{username}: Messaging handler and user")

        # now how to trigger user services.... ?
        await self.send_text_message(
            handler_jid,
            f"User {username} registered",
        )

        user_messages = [
            "Welcome to the WhatsApp Watch system! One moment while we process your request.",
            # SM: Commenting out the hindi welcome message as we now ask them to set the language as the first step.
            # "व्हाट्सएप वॉच में आपका स्वागत है! हम आपके अकाउंट की जांच कर रहे हैं और जल्द ही ऑनबोर्डिंग प्रक्रिया अर्थात आपके अकाउंट को व्हाट्सएप वॉच सिस्टम में लाने की प्रक्रिया शुरू करेंगे। ऑनबोर्डिंग प्रक्रिया पूरी होने तक कोई डेटा एकत्रित नहीं किया जाएगा।",
            "Please add WhatsApp Watch to your contacts before continuing.",
        ]
        for message in user_messages:
            await self.send_text_message(
                connection_status.JID,
                message,
            )
