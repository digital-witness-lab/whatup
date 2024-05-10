import asyncio
import logging
import os
import typing as T
from pathlib import Path

import click
from cloudpathlib import AnyPath
from dotenv import load_dotenv

from .bots import (
    ArchiveBot,
    ChatBot,
    DatabaseBot,
    DebugBot,
    OnboardBot,
    RegisterBot,
    UserServicesBot,
)
from .credentials_manager import CredentialsManager
from .device_manager import run_multi_bots
from .protos import whatupcore_pb2 as wuc
from .utils import async_cli, expand_glob, str_to_jid, short_hash

FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


GROUP_PERMISSIONS = dict(wuc.GroupPermission.items())

load_dotenv(dotenv_path=os.path.join("/", "tmp", "whatup", ".env"))


@click.group()
@click.option("--debug", "-d", type=bool, is_flag=True, default=False)
@click.option(
    "--control-group",
    "-c",
    "control_groups",
    multiple=True,
    type=str,
    default=["120363104970691776@g.us"],
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
        logger.info("Running with debug")
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
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
@click.argument("credentials", nargs=-1)
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
    "--credentials-url",
    default="./credentials/",
)
@click.argument("name", type=str)
@click.pass_context
async def onboard(
    ctx, name, credentials_url: CredentialsManager, default_group_permission: str
):
    """
    Creates a QR code for provided bot. The command will exit on a sucessful QR
    code scan. The credential file will be saved to <credential-dir>/<name>.json
    """
    credentials_manager = CredentialsManager.from_url(credentials_url)
    bot = OnboardBot(**ctx.obj["connection_params"])
    logger.info(
        "Registering user %s with default permission %s", name, default_group_permission
    )
    return await bot.register(
        name,
        credentials_manager,
        default_group_permission=GROUP_PERMISSIONS[default_group_permission],
    )


@cli.command()
@async_cli
@click.option(
    "--credentials-url",
    default="./credentials/",
)
@click.pass_context
async def onboard_bulk(ctx, credentials_url: str):
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
    credentials_manager = CredentialsManager.from_url(credentials_url)
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
        bot = OnboardBot(**ctx.obj["connection_params"])
        await bot.register(
            name,
            credentials_manager,
            default_group_permission=GROUP_PERMISSIONS[default_group_permission_str],
        )


@cli.command()
@async_cli
@click.option("--host", type=str, default="localhost", help="What host to serve on")
@click.option("--port", type=int, default=6666, help="What port to serve on")
@click.argument("credential")
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
    type=click.Path(path_type=AnyPath),
    default=Path("./archive/"),
)
@click.argument("credentials", nargs=-1)
@click.pass_context
async def archivebot(ctx, credentials, archive_dir: AnyPath):
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
    logger.info(
        "Starting archivebot with archive_dir: %s: %s", archive_dir, type(archive_dir)
    )
    archive_dir.mkdir(parents=True, exist_ok=True)
    params = {"archive_dir": archive_dir, **ctx.obj["connection_params"]}
    await run_multi_bots(ArchiveBot, credentials, params)


@cli.command()
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--media-base", type=click.Path(path_type=AnyPath), default=Path("./dbmedia/")
)
@click.argument("credentials", nargs=-1)
@click.pass_context
async def databasebot(
    ctx,
    credentials,
    database_url,
    media_base,
):
    # TODO: docstring

    params = {
        "database_url": database_url,
        "media_base_path": media_base,
        **ctx.obj["connection_params"],
    }
    await run_multi_bots(DatabaseBot, credentials, params)


@cli.command("databasebot-load-archive")
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--media-base", type=click.Path(path_type=AnyPath), default=Path("./dbmedia/")
)
@click.option(
    "--run-lock-path", type=click.Path(path_type=AnyPath), default=Path("/tmp/")
)
@click.option("--run-name", type=str)
@click.argument(
    "archive-files",
    type=str,
    nargs=-1,
)
@click.pass_context
async def databasebot_load_archive(
    ctx, database_url, archive_files, media_base, run_lock_path, run_name
):
    """
    desc="File glob for archived messages to load. Will load the messages then quit",
    """
    params = {
        "database_url": database_url,
        "media_base_path": media_base,
        **ctx.obj["connection_params"],
    }
    db = DatabaseBot(connect=False, **params)

    filenames = []
    filenames_lock = []
    for archive_blob in archive_files:
        blob_hash = short_hash(str(archive_blob))
        filename_lock = run_lock_path / f"{run_name}-{blob_hash}.lock"
        if not filename_lock.exists():
            filenames.extend(expand_glob(AnyPath(archive_blob)))
            filenames_lock.append(filename_lock)
        else:
            logger.info(
                "Skipping blob because it is already completed: %s: %s",
                archive_blob,
                filename_lock,
            )
    filenames.sort()
    await db.process_archive(filenames)

    logger.info("Done processing archive files")
    for lock in filenames_lock:
        lock.write_text("DONE")


@cli.command("databasebot-delete-groups")
@async_cli
@click.option("--database-url", type=str)
@click.option("--no-delete-media", type=bool, default=False, is_flag=True)
@click.option(
    "--media-base", type=click.Path(path_type=AnyPath), default=Path("./dbmedia/")
)
@click.argument("group-jid", nargs=-1)
@click.pass_context
async def database_delete_groups(
    ctx,
    group_jid,
    database_url,
    no_delete_media,
    media_base,
):
    """
    desc="File glob for archived messages to load. Will load the messages then quit",
    """
    group_jid = [jid for gj in group_jid for jid in gj.split(" ")]
    params = {
        "database_url": database_url,
        "media_base_path": media_base,
        **ctx.obj["connection_params"],
    }
    db = DatabaseBot(connect=False, **params)
    db.delete_groups(group_jid, delete_media=not no_delete_media)


@cli.command()
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--sessions-url",
    required=True,
    type=str,
    help="Credentials manager URL to store sessions for newly registered users",
)
@click.option(
    "--public-path",
    required=True,
    type=click.Path(path_type=AnyPath),
    help="URL to store temporary HTML files for public use",
)
@click.argument("credential", nargs=1)
@click.pass_context
async def userservicesbot(
    ctx,
    credential,
    public_path,
    database_url,
    sessions_url,
):
    """
    Start a userservices bot that will manage onboarding new users completely
    through the WhatsApp interface. The database URI specifies where newly
    registered user metadata and state should be stored. The sessions directory
    specifies where newly registered user's session file should be stored.
    """
    credentials_manager = CredentialsManager.from_url(sessions_url, timeout=30)
    params = {
        "database_url": database_url,
        "credentials_manager": credentials_manager,
        "public_path": public_path,
        **ctx.obj["connection_params"],
    }
    async with asyncio.TaskGroup() as tg:
        # NOTE: it may be better ro run these as two separate commands so that
        # only the register bot get write access to the sessions directory.
        # tg.create_task(run_multi_bots(RegisterBot, [credential], params))
        tg.create_task(run_multi_bots(UserServicesBot, [credential], params))


@cli.command()
@async_cli
@click.option("--database-url", type=str)
@click.option(
    "--sessions-url",
    type=str,
    help="Credentials manager URL to store sessions for newly registered users",
)
@click.argument("credential", nargs=1)
@click.pass_context
async def registerbot(
    ctx,
    credential,
    database_url,
    sessions_url,
):
    """
    Start a registration bot that will manage registering new users completely
    through the WhatsApp interface. The database URI specifies where newly
    registered user metadata and state should be stored. The sessions directory
    specifies where newly registered user's session file should be stored.
    """
    credentials_manager = CredentialsManager.from_url(sessions_url)
    params = {
        "database_url": database_url,
        "credentials_manager": credentials_manager,
        **ctx.obj["connection_params"],
    }
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_multi_bots(RegisterBot, [credential], params))


@cli.command()
@click.argument("paths", type=str, nargs=-1)
def gs_ls(paths):
    for path in paths:
        path = AnyPath(path)
        for item in path.glob("*"):
            click.echo(str(item).strip("/"))


def main():
    cli(auto_envvar_prefix="WHATUPY")


if __name__ == "__main__":
    main()
