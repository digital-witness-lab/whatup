import asyncio
from pathlib import Path
from collections import defaultdict
from functools import partial
import typing as T
import logging
import hashlib
import json

import dataset

from . import BaseBot, MediaType
from .. import utils
from ..protos import whatupcore_pb2 as wuc
from ..device_manager import DeviceManager, CredentialsListenerFile
from .static import static_files


logger = logging.getLogger(__name__)


class _UserBot(BaseBot):
    def __init__(self, host, port, cert, services_bot, **kwargs):
        self.services_bot: UserServicesBot = services_bot
        self.unregistering_timer: T.Optional[asyncio.TimerHandle] = None
        super().__init__(
            host,
            port,
            cert,
            mark_messages_read=False,
            read_messages=False,
            read_historical_messages=False,
        )

    async def post_start(self):
        connection_status: wuc.ConnectionStatus = (
            await self.core_client.GetConnectionStatus(wuc.ConnectionStatusOptions())
        )
        self.username = self.authenticator.username
        self.jid = connection_status.JID
        self.jid_anon = connection_status.JIDAnon
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
    def __init__(self, sessions_dir: Path, database_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sessions_dir = sessions_dir
        self.db: dataset.Database = dataset.connect(database_url)
        self.users: T.Dict[str, _UserBot] = {}

        bot_factory = partial(_UserBot, services_bot=self, logger=self.logger, **kwargs)
        credential_listener = CredentialsListenerFile([sessions_dir])
        self.device_manager = DeviceManager(
            bot_factory=bot_factory,
            credential_listeners=[credential_listener],
        )

    async def post_start(self):
        self.connection_status = await self.core_client.GetConnectionStatus(
            wuc.ConnectionStatusOptions()
        )
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.device_manager.start())

    async def on_message(self, message: wuc.WUMessage, **kwargs):
        sender = utils.jid_to_str(message.info.source.sender)
        if not sender:
            return
        # TODO: make these expire and have a way to re-fetch when needed
        user = self.users.get(sender)
        if user is None:
            return
        ulog = self.logger.getChild(user.username)

        text = message.content.text.lower().strip()
        if text == "unregister":
            ulog.debug("Starting unregister workflow")
            await self.unregister_workflow(user)
        elif user.unregistering_timer is not None:
            ulog.debug("Continuing unregister workflow")
            try:
                return await self.unregister_workflow_continue(user, text)
            except asyncio.CancelledError:
                pass
        elif text.startswith("setacl-"):
            ulog.debug("Setting ACL")
            await self.acl_workflow_finalize(user, message)
        elif text == "set groups":
            ulog.debug("Starting ACL workflow")
            await self.acl_workflow(user)
        else:
            ulog.debug("Unrecognized command: %s", text)
            await self.send_text_message(
                user.jid, "i recognize you but not your message"
            )

    async def new_device(self, user: _UserBot):
        user_jid_str = utils.jid_to_str(user.jid_anon)
        if not user_jid_str:
            return
        self.users[user_jid_str] = user
        await self.onboard_user(user)

    async def onboard_user(self, user: _UserBot):
        user_state = self.db["registered_users"].find_one(username=user.username)
        if not user_state.get("onboard_acl"):
            await self.acl_workflow(user)

    async def acl_workflow_finalize(self, user: _UserBot, message: wuc.WUMessage):
        try:
            base = message.content.text[len("setacl-") :]
            n_bytes_str, rest = base.split("@")
            n_bytes = int(n_bytes_str)
            gids: T.Dict[str, bool] = {}
            for gid_spec in rest.split(":"):
                gid, can_read_str = gid_spec.split("|")
                gids[gid] = can_read_str == "1"
        except Exception:
            self.logger.exception(
                "Could not decode ACL response: %s", message.content.text
            )
            await self.send_text_message(
                user.jid,
                "I didn't understand that. Could you try again with the following message and if the problem persists please contact the research team",
            )
            return await self.acl_workflow(user)

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
            if can_read:
                asyncio.get_running_loop().call_soon(self._trigger_history, user, jid)
        summary_text = "Thank you for your selection! We will now:"
        if include := summary.get(True):
            summary_text += "\nMonitor the following groups:\n  -" + "\n  - ".join(
                include
            )
        if exclude := summary.get(False):
            summary_text += (
                "\nNo longer monitor the following groups:\n  -"
                + "\n  - ".join(exclude)
            )
        await self.send_text_message(
            user.jid,
            summary_text,
        )
        self.db["registered_users"].update(
            {"username": user.username, "onboard_acl": True}, ["username"]
        )
        await self.onboard_user(user)

    async def acl_workflow(self, user: _UserBot):
        n_bytes = 3
        groups_data = await user.group_acl_data(n_bytes=n_bytes)
        params = {
            "bot_number": f"+{self.connection_status.JID.user}",
            "gid_nbytes": n_bytes,
            "data_jsons": json.dumps(groups_data),
        }
        content = (
            static_files["group_selection"]
            .open()
            .read()
            .format_map(params)
            .encode("utf8")
        )
        async with self.with_disappearing_messages(
            user.jid, wuc.DisappearingMessageOptions.TIMER_24HOUR
        ):
            await self.send_media_message(
                user.jid,
                MediaType.MediaDocument,
                content=content,
                caption="Click the above attachment and open in Chrome to select the groups you would like to share",
                mimetype="text/html",
                filename="onboard-group-selection.html",
            )

    async def _trigger_history(self, user: _UserBot, jid: wuc.JID):
        self.logger.critical("_trigger_history called but not yet implemented")
        # TODO: this
        pass

    async def unregister_workflow(self, user: _UserBot):
        await self.send_text_message(
            user.jid,
            "Are you sure you want to unregister? Send 'yes' within 60 seconds to finalize your request.",
        )
        user.unregistering_timer = asyncio.get_event_loop().call_later(
            60,
            asyncio.create_task,
            self.send_text_message(user.jid, "Unregister request timed out."),
        )

    async def unregister_workflow_continue(self, user: _UserBot, text: str):
        is_expired = (
            user.unregistering_timer is None
            or user.unregistering_timer.when() < asyncio.get_running_loop().time()
        )
        if is_expired:
            user.unregistering_timer = None
            raise asyncio.CancelledError()
        elif text != "yes":
            user.unregistering_timer.cancel()
            user.unregistering_timer = None
            await self.send_text_message(
                user.jid,
                "Unrecognized response. Canceling unregister request. Please request to unregister again if you still desire to unregister",
            )
            raise asyncio.CancelledError()
        else:
            return await self.unregister_workflow_finalize(user)

    async def unregister_workflow_finalize(self, user: _UserBot):
        final_message = static_files["unregister_final_message"].open().read()
        await self.send_text_message(
            user.jid,
            final_message.format(anon_user=user.jid_anon.user),
        )
        await self.device_manager.unregister(user.username)
        self.db["registered_users"].delete(username=user.username)
