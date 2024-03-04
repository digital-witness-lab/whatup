import asyncio
import json
import logging
import typing as T
from datetime import timedelta, datetime
from collections import defaultdict
from functools import partial

import dataset
from cloudpathlib import CloudPath

from .. import utils
from ..credentials_manager import CredentialsManager
from ..device_manager import DeviceManager
from ..protos import whatupcore_pb2 as wuc
from ..protos import whatsappweb_pb2 as waw
from .basebot import BaseBot, TypeLanguages
from .lib import UserBot, GroupRefreshTask
from . import static, BotCommandArgs

logger = logging.getLogger(__name__)


class UserServicesBot(BaseBot):
    def __init__(
        self,
        credentials_manager: CredentialsManager,
        database_url: str,
        public_path: CloudPath,
        demo_lifespan: timedelta = timedelta(hours=1),
        *args,
        **kwargs,
    ):
        kwargs["read_messages"] = True
        kwargs["read_historical_messages"] = False
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)

        self.public_path = public_path
        self.db: dataset.Database = dataset.connect(
            database_url,
        )
        self.users: T.Dict[str, UserBot] = {}
        self.demo_lifespan = demo_lifespan

        group_min_participants = 6
        if not self.is_prod():
            group_min_participants = 0

        bot_factory = partial(
            UserBot,
            connect_callback=self.new_device,
            logger=self.logger,
            db=self.db,
            group_min_participants=group_min_participants,
            **kwargs,
        )
        self.credentials_manager = credentials_manager
        self.device_manager = DeviceManager(
            bot_factory=bot_factory,
            credential_managers=[credentials_manager],
        )

        self.group_refresh_tasks = set()

    def setup_command_args(self):
        parser = BotCommandArgs(
            prog=self.__class__.__name__,
            description="Bot for user services",
        )
        sub_parser = parser.add_subparsers(dest="command")
        sub_parser.add_parser("status", description="Get current user services status")

        list_users = sub_parser.add_parser("list-users", description="Lists current users")
        list_users.add_argument(
            "--no-bots",
            action="store_true",
            help="Exclude bots",
            default=False,
        )
        list_users.add_argument(
            "--no-demo",
            action="store_true",
            help="Exclude demo accounts",
            default=False,
        )

        group_refresh = sub_parser.add_parser(
            "group-refresh", description="Refresh the history of a user or group"
        )
        group_refresh.add_argument(
            "--username",
            action="append",
            help="User to refresh",
            default=None,
        )
        group_refresh.add_argument(
            "--jid",
            action="append",
            help="JID to refresh",
            default=None,
        )
        return parser

    async def on_control(self, message):
        params = await self.parse_command(message)
        self.logger.info("Got command: %s", params)
        if params is None:
            return
        elif params.command == "status":
            await self._on_status(message, params)
        elif params.command == "group-refresh":
            await self._on_group_refresh(message, params)
        elif params.command == "list-users":
            await self._on_list_users(message, params)

    async def _on_list_users(self, message, params):
        users = list(self.users.values())
        if params.no_demo:
            users = {user for user in users if not user.state.get("is_demo")}
        if params.no_bots:
            users = {user for user in users if not user.state.get("is_bot")}
        users_str = "- " + "\n- ".join(user.username or "[unknown]" for user in users)
        return await self.send_text_message(
            message.info.source.sender, f"Registered users:\n{users_str}"
        )

    async def _on_group_refresh(self, message, params):
        refresh_task = GroupRefreshTask()
        sender = message.info.source.sender
        if params.username and not params.jid:
            n_added = 0
            for username in params.username:
                try:
                    user = next(user for user in self.users.values() if user.username == username)
                    await refresh_task.add_user(user)
                    n_added += 1
                except StopIteration:
                    await self.send_text_message(
                        sender, f"Could not find user: {username}"
                    )
            if not n_added:
                return
        elif params.jid:
            if params.username:
                users = [
                    user
                    for user in self.users.values()
                    if user.username in set(params.username)
                ]
            else:
                users = list(self.users.values())
            groups = set(jid for jid in params.jid)
            jids_found, jids_missing = await refresh_task.add_groups(users, groups)
            if jids_missing:
                await self.send_text_message(
                    sender,
                    f"Could not a valid user connected to group: {', '.join(jids_missing)}",
                )
                if not jids_found:
                    return await self.send_text_message(sender, "Aborting")
                else:
                    await self.send_text_message(
                        sender,
                        f"Continuing for JIDs: {' '.join(jids_found)}",
                    )
        else:
            return self.send_text_message(sender, "Must send username, jids or both")
        task = await refresh_task.start()
        self.group_refresh_tasks.add(refresh_task)
        task.add_done_callback(lambda t: self.group_refresh_tasks.discard(refresh_task))
        await self.send_text_message(message.info.source.sender, str(refresh_task.status))

    async def _on_status(self, message, params):
        n_devices = len(self.users)
        n_active_bots = sum(1 for u in self.users.values() if u.state.get("is_bot"))
        n_active_demo = sum(1 for u in self.users.values() if u.state.get("is_demo"))
        n_active_users = sum(
            1
            for u in self.users.values()
            if not (u.state.get("is_demo") or u.state.get("is_bot"))
        )
        refresh_status = "\n".join(str(gr.status) for gr in self.group_refresh_tasks)
        status = f"""
Number of active users: {n_active_users}
Number of bots: {n_active_bots}
Number of demo accounts: {n_active_demo}
Total devices: {n_devices}
{refresh_status}
        """.strip()
        await self.send_text_message(message.info.source.sender, status)

    async def post_start(self):
        self.connection_status = await self.core_client.GetConnectionStatus(
            wuc.ConnectionStatusOptions()
        )
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.device_manager.start())

    async def on_message(
        self,
        message: wuc.WUMessage,
        *args,
        is_history=False,
        is_archive=False,
        **kwargs,
    ):
        if is_history or is_archive:
            return

        now = datetime.now()
        if now - message.info.timestamp.ToDatetime() > timedelta(minutes=5):
            return

        sender = utils.jid_to_str(message.info.source.sender)
        if not sender:
            return
        user = self.users.get(sender)
        if user is None or user.username is None:
            return
        ulog = self.logger.getChild(user.username)

        text = message.content.text.lower().strip()
        if text == "restart_onboarding":
            self.reset_onboarding(user)
            return await self.onboard_user(user)
        elif user.active_workflow is not None:
            try:
                return await user.active_workflow(user, text)
            except asyncio.CancelledError:
                pass
        match text:
            case "1":
                ulog.debug("Starting ACL workflow")
                await self.acl_workflow(user)
            case "2":
                ulog.debug("Starting unregister workflow")
                await self.unregister_workflow(user)
            case "3":
                ulog.debug("Setting language preference")
                await self.langselect_workflow_start(user)
            case _:
                ulog.debug("Unrecognized command: %s", text)
                await self.help_text(user)

    async def new_device(self, user: UserBot):
        if not user.jid_anon:
            return
        user_jid_str = utils.jid_to_str(user.jid_anon)
        if not user_jid_str:
            return
        self.users[user_jid_str] = user
        if not user.state.get("finalize_registration", False):
            await self.onboard_user(user)
        if user.state.get("is_bot"):
            timestamp = user.state.get("timestamp") or datetime.min
            unregister_at = timestamp + self.demo_lifespan
            asyncio.get_running_loop().call_at(unregister_at.timestamp(), partial(self.unregister_demo, user))
        
    async def unregister_demo(self, user: UserBot):
        if not user.username:
            return
        await self.send_template_user(user, "unregister_demo")
        await self.device_manager.unregister(user.username)

    async def onboard_bot(self, user: UserBot):
        if not user.state.get("finalize_registration"):
            user.state.update(finalize_registration=True, lang="en")
            await self.send_template_user(user, "onboard_bot_welcome", lang="en")
        await self.help_text(user)

    async def onboard_user(self, user: UserBot):
        user.active_workflow = None
        if user.state.get("is_bot"):
            return await self.onboard_bot(user)
        elif not user.state.get("lang"):
            await self.langselect_workflow_start(user)
        elif not user.state.get("onboard_acl"):
            await self.acl_workflow(user)
        elif not user.state.get("finalize_registration"):
            await self.finish_registration(user)
        else:
            await self.help_text(user)

    def reset_onboarding(self, user: UserBot):
        user.active_workflow = None
        if user.unregistering_timer is not None:
            user.unregistering_timer.cancel()
        user.state.update(onboard_acl=False, finalize_registration=False, lang=None)

    async def acl_workflow_finalize(self, user: UserBot, text: str):
        try:
            body = text[len("setacl-") :]
            lang, base = body.split("-", 1)
            n_bytes_str, rest = base.strip().split("@")
            n_bytes = int(n_bytes_str)
            gids: T.Dict[str, bool] = {}
            if rest:
                for gid_spec in rest.split(":"):
                    gid, can_read_str = gid_spec.split("~")
                    gids[gid] = can_read_str == "1"
        except Exception:
            self.logger.exception("Could not decode ACL response: %s", text)
            await self.send_template_user(user, "acl_workflow_error_code")
            return await self.acl_workflow(user)

        user.state["lang"] = lang
        group_info_lookup = await user.group_acl_jid_lookup(n_bytes=n_bytes)
        summary = defaultdict(list)
        if user.state["is_demo"]:
            await self.send_text_message(
                user.jid,
                "(You are in demo mode. We are going to simulate changing your group preferences however no data will be collected)",
            )
        for gid, can_read in gids.items():
            permission = (
                wuc.GroupPermission.READONLY if can_read else wuc.GroupPermission.DENIED
            )
            data = group_info_lookup[gid]
            summary[can_read].append(data["name"])
            jid = data["jid"]
            if not user.state["is_demo"]:
                await user.core_client.SetACL(
                    wuc.GroupACL(JID=jid, permission=permission)
                )

        await self.send_template_user(user, "acl_workflow_finalize_header")
        if include := summary.get(True):
            group_list = " - " + "\n - ".join(include)
            await self.send_template_user(
                user, "acl_workflow_finalize_monitor", group_list=group_list
            )
        if exclude := summary.get(False):
            group_list = " - " + "\n - ".join(exclude)
            await self.send_template_user(
                user, "acl_workflow_finalize_ignore", group_list=group_list
            )
        user.state["onboard_acl"] = True
        await self.onboard_user(user)

    async def finish_registration(self, user: UserBot):
        await self.send_template_user(user, "finish_registration")
        user.state["finalize_registration"] = True
        await self.onboard_user(user)

    async def help_text(self, user: UserBot):
        await self.send_template_user(user, "help_text")

    async def acl_workflow(self, user: UserBot):
        n_bytes = 3
        groups_data = await user.group_acl_data(n_bytes=n_bytes)
        skip_intro = int(user.state.get("onboard_acl") or False)
        params = {
            "bot_number": f"+{self.connection_status.JID.user}",
            "gid_nbytes": n_bytes,
            "data_jsons": json.dumps(groups_data),
            "default_lang": user.state.get("lang", "en"),
            "skip_intro": skip_intro,
        }
        acl_html = static.substitute(
            static.static_files["group_selection"].read_text("utf8"), **params
        )
        acl_url = self.bytes_to_url(
            acl_html.encode("utf8"), suffix=".html", ttl=timedelta(days=1)
        )
        async with self.with_disappearing_messages(
            user.jid, wuc.DisappearingMessageOptions.TIMER_24HOUR
        ) as context_info:
            await self.send_template_user(
                user, "acl_workflow", context_info=context_info
            )
            msg = "Click the link above"
            spacer = (
                b"\xCD\x8F".decode("utf8") * 3060
            )  # Combining Grapheme Joiner, U+034F
            await self.send_raw_message(
                user.jid,
                waw.Message(
                    extendedTextMessage=waw.ExtendedTextMessage(
                        text=f"{msg}\n{spacer}\n{acl_url}",
                        matchedText=acl_url,
                        canonicalUrl=acl_url,
                        description="Click HERE to select the groups you would like to share. This link expires in 24 hours.",
                        title="WhatsApp Watch Group Selection",
                        jpegThumbnail=static.static_files[
                            "group_selection_thumbnail"
                        ].read_bytes(),
                        contextInfo=context_info,
                    )
                ),
            )
            if user.state["is_demo"]:
                await self.send_text_message(
                    user.jid,
                    "(You are in demo mode. We are going to simulate changing your group preferences however no data will be collected)",
                )
        user.active_workflow = self.acl_workflow_finalize

    def bytes_to_url(
        self,
        content: bytes,
        suffix: T.Optional[str] = None,
        ttl: T.Optional[timedelta] = None,
    ) -> str:
        filename = f"{utils.random_string(length=6)}{suffix or ''}"
        filepath: CloudPath = (
            self.public_path / filename[0] / filename[1] / filename[2:]
        )
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(content)
        return utils.gspath_to_self_signed_url(filepath, ttl=ttl)

    async def unregister_workflow(self, user: UserBot):
        await self.send_template_user(user, "unregister_workflow")
        user.unregistering_timer = asyncio.get_event_loop().call_later(
            60, asyncio.create_task, self.unregister_workflow_cancel(user)
        )
        user.active_workflow = self.unregister_workflow_continue

    async def unregister_workflow_cancel(self, user: UserBot):
        user.active_workflow = None
        await self.send_template_user(user, "unregister_timeout")
        await self.help_text(user)

    async def unregister_workflow_continue(self, user: UserBot, text: str):
        user.active_workflow = None
        if user.unregistering_timer is not None:
            user.unregistering_timer.cancel()
            is_expired = (
                user.unregistering_timer.when() < asyncio.get_running_loop().time()
            )
        else:
            is_expired = True
        user.unregistering_timer = None
        if is_expired:
            raise asyncio.CancelledError()
        elif text != "1":
            await self.send_template_user(user, "unregister_unrecognized")
            return await self.onboard_user(user)
        return await self.unregister_workflow_finalize(user)

    async def unregister_workflow_finalize(self, user: UserBot):
        await self.send_template_user(
            user, "unregister_final_message", anon_user=user.jid_anon.user
        )
        jid = utils.jid_to_str(user.jid_anon)
        if jid:
            self.users.pop(jid)
        if user.username:
            await self.device_manager.unregister(user.username)
        user.state.clear()

    async def send_template_user(
        self,
        user,
        template,
        lang: T.Optional[TypeLanguages | T.Literal["all"]] = None,
        context_info=None,
        **kwargs,
    ):
        lang = lang or user.state.get("lang") or "all"
        if lang == "all":
            await self.send_template_user(
                user, template, "en", context_info=context_info, **kwargs
            )
            await self.send_template_user(
                user, template, "hi", context_info=context_info, **kwargs
            )
            return
        await self.send_template(
            user.jid, template, lang, context_info=context_info, **kwargs
        )

    async def langselect_workflow_start(self, user: UserBot):
        await self.send_template_user(user, "langselect_start", lang="all")
        user.active_workflow = self.langselect_workflow_finalize

    async def langselect_workflow_finalize(self, user: UserBot, text: str):
        if text == "1":
            lang = "en"
        elif text == "2":
            lang = "hi"
        else:
            return await self.langselect_workflow_start(user)

        user.active_workflow = None
        user.state["lang"] = lang
        await self.send_template_user(user, "langselect_final")
        await self.onboard_user(user)
