import asyncio
import hashlib
import json
import logging
import typing as T
from datetime import timedelta
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
from . import static

logger = logging.getLogger(__name__)


class _UserBot(BaseBot):
    def __init__(self, host, port, cert, services_bot, db, **kwargs):
        self.services_bot: UserServicesBot = services_bot
        self.active_workflow: T.Optional[T.Callable] = None
        self.unregistering_timer: T.Optional[asyncio.TimerHandle] = None
        self.db = db
        self.lang: T.Optional[TypeLanguages] = None
        super().__init__(
            host,
            port,
            cert,
            mark_messages_read=False,
            read_messages=False,
            read_historical_messages=False,
        )

    def set_lang(self, lang):
        self.db["registered_users"].update(
            {
                "username": self.username,
                "lang": lang,
            },
            ["username"],
        )
        self.lang = lang

    async def post_start(self):
        connection_status: wuc.ConnectionStatus = (
            await self.core_client.GetConnectionStatus(wuc.ConnectionStatusOptions())
        )
        self.username = self.authenticator.username
        self.jid = connection_status.JID
        self.jid_anon = connection_status.JIDAnon

        user_state = self.db["registered_users"].find_one(username=self.username)
        self.lang = user_state.get("lang")
        await self.services_bot.new_device(self)

    @staticmethod
    def _hash_jid(jid: wuc.JID, n_bytes: int):
        return hashlib.sha1(jid.user.encode("utf8")).hexdigest()[:n_bytes]

    async def group_acl_jid_lookup(
        self, n_bytes, min_participants=6
    ) -> T.Dict[str, T.Dict]:
        joined_group_iter = self.core_client.GetJoinedGroups(
            wuc.GetJoinedGroupsOptions()
        )
        lookup = {}
        async for data in joined_group_iter:
            n_participants = len(data.groupInfo.participants)
            if n_participants < min_participants:
                continue
            gid = self._hash_jid(data.groupInfo.JID, n_bytes)
            lookup[gid] = {
                "jid": data.groupInfo.JID,
                "name": data.groupInfo.groupName.name,
            }
        return lookup

    async def group_acl_data(self, n_bytes=5, min_participants=6):
        joined_group_iter = self.core_client.GetJoinedGroups(
            wuc.GetJoinedGroupsOptions()
        )
        groups = []
        async for data in joined_group_iter:
            n_participants = len(data.groupInfo.participants)
            if n_participants < min_participants:
                continue
            permission = data.acl.permission
            can_read = permission in (
                wuc.GroupPermission.READONLY,
                wuc.GroupPermission.READWRITE,
            )
            gid = self._hash_jid(data.groupInfo.JID, n_bytes)
            item = {
                "name": data.groupInfo.groupName.name,
                "topic": data.groupInfo.groupTopic.topic,
                "can_read": can_read,
                "gid": gid,
                "n_participants": n_participants,
            }
            groups.append(item)
        groups.sort(key=lambda i: i["n_participants"], reverse=True)
        return groups


class UserServicesBot(BaseBot):
    def __init__(
        self,
        credentials_manager: CredentialsManager,
        database_url: str,
        public_path: CloudPath,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.public_path = public_path
        self.db: dataset.Database = dataset.connect(database_url)
        self.users: T.Dict[str, _UserBot] = {}

        bot_factory = partial(
            _UserBot, services_bot=self, logger=self.logger, db=self.db, **kwargs
        )
        self.credentials_manager = credentials_manager
        self.device_manager = DeviceManager(
            bot_factory=bot_factory,
            credential_managers=[credentials_manager],
        )

    async def post_start(self):
        self.connection_status = await self.core_client.GetConnectionStatus(
            wuc.ConnectionStatusOptions()
        )
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.device_manager.start())

    async def on_message(self, message: wuc.WUMessage, *args, **kwargs):
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

    async def new_device(self, user: _UserBot):
        user_jid_str = utils.jid_to_str(user.jid_anon)
        if not user_jid_str:
            return
        self.users[user_jid_str] = user
        user_state = self.db["registered_users"].find_one(username=user.username)
        if not user_state.get("finalize_registration", False):
            await self.onboard_user(user)

    async def onboard_user(self, user: _UserBot):
        user.active_workflow = None
        user_state = self.db["registered_users"].find_one(username=user.username)
        if not user_state.get("lang"):
            await self.langselect_workflow_start(user)
        elif not user_state.get("onboard_acl"):
            await self.acl_workflow(user)
        elif not user_state.get("finalize_registration"):
            await self.finish_registration(user)
        else:
            await self.help_text(user)

    def reset_onboarding(self, user: _UserBot):
        user.active_workflow = None
        if user.unregistering_timer is not None:
            user.unregistering_timer.cancel()
        self.db["registered_users"].update(
            {
                "username": user.username,
                "onboard_acl": False,
                "finalize_registration": False,
                "lang": None,
            },
            ["username"],
        )

    async def acl_workflow_finalize(self, user: _UserBot, text: str):
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

        user.set_lang(lang)
        group_info_lookup = await user.group_acl_jid_lookup(n_bytes=n_bytes)
        summary = defaultdict(list)
        for gid, can_read in gids.items():
            permission = (
                wuc.GroupPermission.READONLY if can_read else wuc.GroupPermission.DENIED
            )
            data = group_info_lookup[gid]
            summary[can_read].append(data["name"])
            jid = data["jid"]
            await user.core_client.SetACL(wuc.GroupACL(JID=jid, permission=permission))

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
        self.db["registered_users"].update(
            {"username": user.username, "onboard_acl": True}, ["username"]
        )
        await self.onboard_user(user)

    async def finish_registration(self, user: _UserBot):
        await self.send_template_user(user, "finish_registration")
        self.db["registered_users"].update(
            {"username": user.username, "finalize_registration": True}, ["username"]
        )
        await self.onboard_user(user)

    async def help_text(self, user: _UserBot):
        await self.send_template_user(user, "help_text")

    async def acl_workflow(self, user: _UserBot):
        n_bytes = 3
        groups_data = await user.group_acl_data(n_bytes=n_bytes)
        user_state = self.db["registered_users"].find_one(username=user.username)
        skip_intro = int(user_state.get("onboard_acl", False))
        params = {
            "bot_number": f"+{self.connection_status.JID.user}",
            "gid_nbytes": n_bytes,
            "data_jsons": json.dumps(groups_data),
            "default_lang": user.lang,
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

    async def unregister_workflow(self, user: _UserBot):
        await self.send_template_user(user, "unregister_workflow")
        user.unregistering_timer = asyncio.get_event_loop().call_later(
            60, asyncio.create_task, self.unregister_workflow_cancel(user)
        )
        user.active_workflow = self.unregister_workflow_continue

    async def unregister_workflow_cancel(self, user: _UserBot):
        user.active_workflow = None
        await self.send_template_user(user, "unregister_timeout")
        await self.help_text(user)

    async def unregister_workflow_continue(self, user: _UserBot, text: str):
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

    async def unregister_workflow_finalize(self, user: _UserBot):
        await self.send_template_user(
            user, "unregister_final_message", anon_user=user.jid_anon.user
        )
        jid = utils.jid_to_str(user.jid_anon)
        if jid:
            self.users.pop(jid)
        if user.username:
            await self.device_manager.unregister(user.username)
        self.db["registered_users"].delete(username=user.username)

    async def send_template_user(
        self,
        user,
        template,
        lang: T.Optional[TypeLanguages | T.Literal["all"]] = None,
        context_info=None,
        **kwargs,
    ):
        lang = lang or user.lang or "all"
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

    async def langselect_workflow_start(self, user: _UserBot):
        await self.send_template_user(user, "langselect_start", lang="all")
        user.active_workflow = self.langselect_workflow_finalize

    async def langselect_workflow_finalize(self, user: _UserBot, text: str):
        if text == "1":
            lang = "en"
        elif text == "2":
            lang = "hi"
        else:
            return await self.langselect_workflow_start(user)

        user.active_workflow = None
        user.set_lang(lang)
        await self.send_template_user(user, "langselect_final")
        await self.onboard_user(user)
