import logging
import typing as T
import asyncio
from pathlib import Path

import click

from .bots import (
    ArchiveBot,
    ChatBot,
    DatabaseBot,
    OnboardBot,
    DebugBot,
    RegisterBot,
    UserServicesBot,
)
from .device_manager import run_multi_bots
from .utils import async_cli, str_to_jid
from .protos import whatupcore_pb2 as wuc


FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)


GROUP_PERMISSIONS = dict(wuc.GroupPermission.items())


@click.group()
@click.option("--debug", "-d", type=bool, is_flag=True, default=False)
@click.option(
    "--control-group",
    "-c",
    "control_groups",
    multiple=True,
    type=str,
    default=["c+c-prod@g.us"],
)
@click.option("--host", "-H", type=str, default="localhost")
@click.option("--port", "-p", type=int, default=3447)
@click.option(
    "--cert",
    type=click.Path(dir_okay=False, readable=True, path_type=Path),
    default=None,
)
@click.pass_context
def cli(ctx, debug, host, port, control_groups: list, cert: T.Optional[Path]):
    ctx.obj = {"debug": debug}
    if debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    control_groups_jid = [str_to_jid(cg) for cg in control_groups]
    ctx.obj["connection_params"] = {
        "host": host,
        "port": port,
        "cert": cert,
        "control_groups": control_groups_jid,
    }
    logger.debug(f"Command Context: {ctx.obj}")


@cli.command()
@async_cli
@click.option(
    "--response-time",
    type=float,
    default=60 * 60 * 4,
    help="Mean response time (seconds)",
)
@click.option(
    "--response-time-sigma",
    type=float,
    default=60 * 60 * 2,
    help="Response time sigma (seconds)",
)
@click.argument("credentials", type=click.Path(path_type=Path), nargs=-1)
@click.pass_context
async def chatbot(ctx, credentials, response_time, response_time_sigma):
    """
    Create a bot-evasion chat-bot. Multiple bots can be turned into this mode
    and they will communicate with one-another so as to simulate real users
    chatting.
    """
    params = {
        "response_time": response_time,
        "response_time_sigma": response_time_sigma,
        **ctx.obj["connection_params"],
    }
    await run_multi_bots(ChatBot, credentials, params)


@cli.command
@async_cli
@click.option(
    "--default-group-permission",
    type=click.Choice(list(GROUP_PERMISSIONS.keys())),
    default="DENIED",
)
@click.option(
    "--credentials-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./credentials/"),
)
@click.argument("name", type=str)
@click.pass_context
async def onboard(ctx, name, credentials_dir: Path, default_group_permission: str):
    """
    Creates a QR code for provided bot. The command will exit on a sucessful QR
    code scan. The credential file will be saved to <credential-dir>/<name>.json
    """
    credentials_dir.mkdir(parents=True, exist_ok=True)
    credential_file = credentials_dir / f"{name}.json"
    bot = OnboardBot(**ctx.obj["connection_params"])
    logger.info(
        "Registering user %s with default permission %s", name, default_group_permission
    )
    await bot.register(
        name,
        credential_file,
        default_group_permission=GROUP_PERMISSIONS[default_group_permission],
    )


@cli.command()
@async_cli
@click.option(
    "--credentials-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./credentials/"),
)
@click.pass_context
async def onboard_bulk(ctx, credentials_dir: Path):
    """
    Starts an interaction to simplify onboarding multiple bots. You will be
    prompted for a name to provide the bot and then be shown a QR code to scan.
    Once the scan is successful, the process will restart so you can onboard
    another bot. The credential file will be saved to the credentials-dir directory
    with the following format,

        \b
        <credentials-dir>/
        ├── <bot-name1>.json
        └── <bot-name2>.json
    """
    credentials_dir.mkdir(parents=True, exist_ok=True)
    while True:
        name: str = click.prompt(
            "Enter name for the next user to be onboarded", type=str
        )
        if not name:
            print("No name provided... exiting.")
            return
        default_group_permission_str: str = click.prompt(
            "Enter the default group permission level (default=DENIED)",
            type=click.Choice(list(GROUP_PERMISSIONS.keys())),
            default="DENIED",
        )
        credential_file = credentials_dir / f"{name}.json"
        bot = OnboardBot(**ctx.obj["connection_params"])
        await bot.register(
            name,
            credential_file,
            default_group_permission=GROUP_PERMISSIONS[default_group_permission_str],
        )


@cli.command()
@async_cli
@click.option("--host", type=str, default="localhost", help="What host to serve on")
@click.option("--port", type=int, default=6666, help="What port to serve on")
@click.argument("credential", type=click.Path(path_type=Path))
@click.pass_context
async def debugbot(ctx, host, port, credential):
    """
    Bot that takes a single session file and creates an interactive shell accessible on the specified port. You can connect to this shell using nc and optionally rlwrap,

    $ rlwrap nc localhost <port>
    """
    await run_multi_bots(
        DebugBot,
        [credential],
        {"debug_host": host, "debug_port": port, **ctx.obj["connection_params"]},
    )


@cli.command()
@async_cli
@click.option(
    "--archive-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./archive/"),
)
@click.argument("credentials", type=click.Path(path_type=Path), nargs=-1)
@click.pass_context
async def archivebot(ctx, credentials, archive_dir: Path):
    """
    Bot to archive all the data the provided bots have access to. Give as many
    credentials to specify which bots should be listened to. Data gets saved in
    the archive-dir with the following structure,

        \b
        <archive-dir>/
        └── <chat-id>/
            ├── <message-id>.json
            ├── media/
            │   └── <message-id>_imageMessage.jpg
            └── metadata.json
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    params = {"archive_dir": archive_dir, **ctx.obj["connection_params"]}
    await run_multi_bots(ArchiveBot, credentials, params)


@cli.command()
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--archive-files",
    type=str,
    default=None,
    help="File glob for archived messages to load. Will load the messages then quit",
)
@click.argument("credentials", type=click.Path(path_type=Path), nargs=-1)
@click.pass_context
async def databasebot(
    ctx,
    credentials,
    database_url,
    archive_files,
):
    # TODO: docstring

    params = {"database_url": database_url, **ctx.obj["connection_params"]}
    if archive_files:
        db = DatabaseBot(connect=False, **params)
        await db.process_archive(archive_files)
        return
    await run_multi_bots(DatabaseBot, credentials, params)


@cli.command("databasebot-load-archive")
@async_cli
@click.option("--database-url", type=str)
@click.argument(
    "archive-files",
    type=str,
    nargs=-1,
)
@click.pass_context
async def databasebot_load_archive(
    ctx,
    database_url,
    archive_files,
):
    """
    desc="File glob for archived messages to load. Will load the messages then quit",
    """
    params = {"database_url": database_url, **ctx.obj["connection_params"]}
    db = DatabaseBot(connect=False, **params)

    filenames = []
    for archive_blob in archive_files:
        filenames.extend(
            Path(p)
            for p in glob.glob(archive_blob, recursive=True)
            if p.endswith(".json")
        )
    filenames.sort()
    await db.process_archive(filenames)


@cli.command()
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--sessions-dir",
    type=click.Path(path_type=Path, file_okay=False, writable=True),
    help="Directory to store sessions for newly registered users",
)
@click.argument(
    "credential", type=click.Path(path_type=Path, dir_okay=False, exists=True), nargs=1
)
@click.pass_context
async def userservices(
    ctx,
    credential,
    database_url,
    sessions_dir,
):
    """
    Start a registration bot and a userservices bot that will manage
    registering new users completely through the WhatsApp interface. The
    database URI specifies where newly registered user metadata and state
    should be stored. The sessions directory specifies where newly registered
    user's session file should be stored.
    """
    params = {
        "database_url": database_url,
        "sessions_dir": sessions_dir,
        **ctx.obj["connection_params"],
    }
    async with asyncio.TaskGroup() as tg:
        # NOTE: it may be better ro run these as two separate commands so that
        # only the register bot get write access to the sessions directory.
        tg.create_task(run_multi_bots(RegisterBot, [credential], params))
        tg.create_task(run_multi_bots(UserServicesBot, [credential], params))


def main():
    cli(auto_envvar_prefix="WHATUPY")
