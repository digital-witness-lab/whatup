from dataclasses import dataclass, field
import asyncio
import typing as T
from datetime import datetime, timedelta

from . import UserBot
from ... import utils
from ...protos import whatupcore_pb2 as wuc


@dataclass
class GroupRefreshStatus:
    tasks_total: int = field(default=0)
    tasks_done: int = field(default=0)
    start_time: T.Optional[datetime] = field(default=None)
    end_time: T.Optional[datetime] = field(default=None)

    def __str__(self):
        if not self.start_time:
            return f"Unstarted group refresh. {self.tasks_total} tasks"
        tasks_left = self.tasks_total - self.tasks_done
        now = datetime.now()
        status = f"Refreshing {self.tasks_done}/{self.tasks_total} groups. Started at {self.start_time}."
        try:
            eta: timedelta = (now - self.start_time) / self.tasks_done * tasks_left
            return f"{status} Finished in {eta} ({(now + eta).isoformat()})."
        except ZeroDivisionError:
            return f"{status} Unknown ETA."


class GroupRefreshTask:
    def __init__(self, timeout=20):
        self.running = False
        self.tasks: T.Set[T.Tuple[UserBot, str]] = set()
        self.timeout = timeout
        self.task: T.Optional[asyncio.Task] = None
        self.status: GroupRefreshStatus = GroupRefreshStatus()

    async def start(self):
        self.status.start_time = datetime.now()
        self.task = asyncio.create_task(self.process_tasks())
        return self.task

    def stop(self):
        self.status.end_time = datetime.now()
        if self.task is None:
            return
        self.task.cancel()

    async def add_task(self, user: UserBot, group: wuc.JID):
        self.status.tasks_total += 1
        jid_str = utils.jid_to_str(group)
        if jid_str:
            self.tasks.add((user, jid_str))

    async def add_user(self, user: UserBot):
        group: wuc.JoinedGroup
        async for group in user.iter_readable_groups():
            await self.add_task(user, group.groupInfo.JID)

    async def add_groups(self, users: T.List[UserBot], groups: T.Set[str]):
        groups_found = set()
        for user in users:
            async for user_group in user.iter_readable_groups():
                jid_str = utils.jid_to_str(user_group.groupInfo.JID)
                if jid_str in groups:
                    groups.remove(jid_str)
                    groups_found.add(jid_str)
                    await self.add_task(user, user_group.groupInfo.JID)
                    if not groups:
                        break
            if not groups:
                break
        return groups_found, groups

    async def process_tasks(self):
        while True:
            try:
                user, group_str = self.tasks.pop()
            except IndexError:
                break
            user.logger.info("Re-requesting history for group: %s", group_str)
            await user.core_client.RequestChatHistory(
                wuc.HistoryRequestOptions(chat=utils.str_to_jid(group_str))
            )
            self.status.tasks_done += 1
            if not self.tasks:
                break
            await asyncio.sleep(self.timeout)
        return self.stop()
