import asyncio
import hashlib
import typing as T

from . import UserState
from ..basebot import BaseBot
from ...protos import whatupcore_pb2 as wuc
from ... import utils


class UserBot(BaseBot):
    def __init__(
        self,
        host,
        port,
        cert,
        connect_callback: T.Callable[[T.Self], None],
        db,
        group_min_participants: int = 6,
        **kwargs,
    ):
        self.connect_callback: T.Callable[[T.Self], None] = connect_callback
        self.active_workflow: T.Optional[T.Callable] = None
        self.unregistering_timer: T.Optional[asyncio.TimerHandle] = None
        self.db = db
        self.state: UserState = UserState()

        self.group_min_participants = group_min_participants
        super().__init__(
            host,
            port,
            cert,
            mark_messages_read=False,
            read_messages=False,
            read_historical_messages=False,
        )

    def __hash__(self):
        if not self.username:
            raise TypeError
        return hash(self.username)

    async def login(self, *args, **kwargs):
        await super().login(*args, **kwargs)
        self.state.connect(self.username, self.db["registered_users"])
        if self.state.get("is_bot"):
            self.mark_messages_read = True
            self.read_historical_messages = True
            self.read_messages = True
        else:
            # TODO: this is for migration purposes. REMOVE THE FOLLOWING LINE
            self.state["n_groups"] = len(
                await utils.aiter_to_list(self.iter_readable_groups())
            )
            # END TODO
        return self

    async def post_start(self):
        await self.connect_callback(self)

    @staticmethod
    def _hash_jid(jid: wuc.JID, n_bytes: int):
        return hashlib.sha1(jid.user.encode("utf8")).hexdigest()[:n_bytes]

    async def iter_readable_groups(self) -> T.AsyncIterable[wuc.JoinedGroup]:
        async for group in self.iter_groups():
            can_read = group.acl.permission in (
                wuc.GroupPermission.READONLY,
                wuc.GroupPermission.READWRITE,
            )
            if can_read:
                yield group

    async def iter_groups(self) -> T.AsyncIterable[wuc.JoinedGroup]:
        joined_group_iter = self.core_client.GetJoinedGroups(
            wuc.GetJoinedGroupsOptions()
        )
        data: wuc.JoinedGroup
        async for data in joined_group_iter:
            if data.groupInfo.isCommunity or data.groupInfo.isPartialInfo:
                continue
            n_participants = len(data.groupInfo.participants)
            if n_participants < self.group_min_participants:
                continue
            yield data

    async def group_acl_jid_lookup(self, n_bytes) -> T.Dict[str, T.Dict]:
        lookup = {}
        data: wuc.JoinedGroup
        async for data in self.iter_groups():
            gid = self._hash_jid(data.groupInfo.JID, n_bytes)
            lookup[gid] = {
                "jid": data.groupInfo.JID,
                "name": data.groupInfo.groupName.name,
            }
        return lookup

    async def group_acl_data(self, n_bytes=5):
        groups = []
        async for data in self.iter_groups():
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
                "n_participants": len(data.groupInfo.participants),
            }
            groups.append(item)
        groups.sort(key=lambda i: i["n_participants"], reverse=True)
        return groups
