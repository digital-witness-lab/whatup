import typing as T

from ... import utils
from ...protos import whatupcore_pb2 as wuc
from .user_job import UserGroupJob
from .user_bot import UserBot


class GroupRefreshJob(UserGroupJob):
    async def add_jid(self, user: UserBot, group: wuc.JID):
        self.status.tasks_total += 1
        jid_str = utils.jid_to_str(group)
        if jid_str:
            self.add_task(user, jid_str=jid_str)

    async def add_user(self, user: UserBot):
        group: wuc.JoinedGroup
        groups = set()
        async for group in user.iter_readable_groups():
            await self.add_jid(user, group.groupInfo.JID)
            groups.add(utils.jid_to_str(group.groupInfo.JID))
        return groups, set()

    async def add_groups(self, users: T.List[UserBot], groups: T.Set[str]):
        groups_found = set()
        for user in users:
            async for user_group in user.iter_readable_groups():
                jid_str = utils.jid_to_str(user_group.groupInfo.JID)
                if jid_str in groups:
                    groups.remove(jid_str)
                    groups_found.add(jid_str)
                    await self.add_jid(user, user_group.groupInfo.JID)
                    if not groups:
                        break
            if not groups:
                break
        return groups_found, groups

    async def process_task(self, task):
        user = task.user
        jid_str = task.params["jid_str"]
        user.logger.info("Re-requesting history for group: %s: %s", user, jid_str)
        await user.core_client.RequestChatHistory(
            wuc.HistoryRequestOptions(chat=utils.str_to_jid(jid_str))
        )
