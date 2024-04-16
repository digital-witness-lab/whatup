import asyncio
import random
import typing as T
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .user_bot import UserBot


@dataclass
class UserJobStatus:
    name: T.Optional[str] = field(default=None)
    job_type: T.Optional[str] = field(default="UserJob")
    tasks_total: int = field(default=0)
    tasks_done: int = field(default=0)
    start_time: T.Optional[datetime] = field(default=None)
    end_time: T.Optional[datetime] = field(default=None)

    def __str__(self):
        status = ""
        if self.name:
            status = f"{status}{self.name}: "
        if not self.start_time:
            return f"{status}Unstarted {self.job_type}. {self.tasks_total} tasks"
        tasks_left = self.tasks_total - self.tasks_done
        now = datetime.now()
        status = f"{status}Running {self.job_type}: Progress {self.tasks_done}/{self.tasks_total}: Started at {self.start_time}. "
        try:
            eta: timedelta = (now - self.start_time) / self.tasks_done * tasks_left
            return f"{status}Finished in {eta} ({(now + eta).isoformat()}). "
        except ZeroDivisionError:
            return f"{status}Unknown ETA. "


@dataclass
class UserTask:
    user: UserBot
    params: T.Dict[str, T.Any] = field(default_factory=dict)

    def __str__(self):
        return f"<UserTask {self.user.username}:{self.params}>"

    def __hash__(self):
        return hash((self.user,) + tuple(self.params.items()))


class UserJob:
    def __init__(self, name=None, timeout=20):
        self.running = False
        self.tasks: T.Set[UserTask] = set()
        self.timeout = timeout
        self.task: T.Optional[asyncio.Task] = None
        self.status: UserJobStatus = UserJobStatus(
            name=name, job_type=self.__class__.__name__
        )

    async def start(self):
        self.status.start_time = datetime.now()
        self.task = asyncio.create_task(self.run_job())
        return self.task

    def stop(self):
        self.status.end_time = datetime.now()
        if self.task is None:
            return
        self.task.cancel()

    def add_task(self, user: UserBot, **kwargs):
        task = UserTask(user, kwargs)
        self.tasks.add(task)

    async def run_job(self):
        results = []
        while True:
            try:
                task = random.choice(tuple(self.tasks))
                self.tasks.discard(task)
            except IndexError:
                break
            try:
                result = await self.process_task(task)
                if result:
                    results.append(result)
            except Exception as e:
                task.user.logger.exception("Could not process task: %s: %s", task, e)
            self.status.tasks_done += 1
            if not self.tasks:
                break
            await asyncio.sleep(self.timeout)
        await self.on_complete(results)
        return self.stop()

    async def process_task(self, task: UserTask) -> T.Any:
        raise NotImplementedError()

    async def on_complete(self, results: T.List):
        pass


class UserGroupJob(UserJob):
    async def add_groups(
        self, users: T.List[UserBot], groups: T.Set[str]
    ) -> T.Tuple[set, set]:
        raise NotImplementedError()

    async def add_user(self, user: UserBot) -> T.Tuple[set, set]:
        raise NotImplementedError()

    @classmethod
    def create_command(cls, parser, name, description):
        job = parser.add_parser(name, description=description)
        job.add_argument(
            "--username",
            action="append",
            help="User to run against",
            default=None,
        )
        job.add_argument(
            "--jid",
            action="append",
            help="JID to run against",
            default=None,
        )
        job.add_argument(
            "--all",
            action="store_true",
            help="Run against all users and groups",
            default=False,
        )
        job.add_argument(
            "--timeout",
            type=int,
            help="Time between each task in seconds",
            default=20,
        )
        job.add_argument(
            "job_name",
            metavar="job-name",
            type=str,
            help="Name of the job for tracking",
            nargs="?",
            default=None,
        )
        return job
