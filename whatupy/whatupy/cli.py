import asyncio
import json
import logging
import typing as T
from importlib.resources import files
from pathlib import Path

import click

from .bots import BotType, ArchiveBot, ChatBot, OnboardBot, DatabaseBot
from .utils import async_cli, str_to_jid

FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEFAULT_CERT = Path(str(files("whatupy").joinpath("whatupcore/static/cert.pem")))


async def run_multi_bots(
    bot: T.Type[BotType], credentials: T.List[T.TextIO], bot_args: dict
):
    whatup_credentials: T.List[dict] = []
    for credential in credentials:
        try:
            whatup_credentials.append(json.load(credential))
        except ValueError:
            raise Exception(f"Could not parse credential: {credential}")
    async with asyncio.TaskGroup() as tg:
        for whatup_credential in whatup_credentials:
            b: BotType = await bot(**bot_args).login(**whatup_credential)
            coro = b.start()
            tg.create_task(coro)


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
    default=DEFAULT_CERT,
)
@click.pass_context
def cli(ctx, debug, host, port, control_groups: list, cert: Path):
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
@click.option("--friend", multiple=True, help="Which users to chat with")
@click.option(
    "--response-time", type=float, default=60, help="Mean response time (seconds)"
)
@click.option(
    "--response-time-sigma",
    type=float,
    default=15,
    help="Response time sigma (seconds)",
)
@click.argument("credentials", type=click.File(), nargs=-1)
@click.pass_context
async def chatbot(ctx, credentials, response_time, response_time_sigma, friend):
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
    "--credentials-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./credentials/"),
)
@click.argument("name", type=str)
@click.pass_context
async def onboard(ctx, name, credentials_dir: Path):
    """
    Creates a QR code for provided bot. The command will exit on a sucessful QR
    code scan. The credential file will be saved to <credential-dir>/<name>.json
    """
    credentials_dir.mkdir(parents=True, exist_ok=True)
    credential_file = credentials_dir / f"{name}.json"
    bot = OnboardBot(**ctx.obj["connection_params"])
    await bot.register(name, credential_file)


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
        credential_file = credentials_dir / f"{name}.json"
        bot = OnboardBot(**ctx.obj["connection_params"])
        await bot.register(name, credential_file)


@cli.command()
@async_cli
@click.option(
    "--archive-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./archive/"),
)
@click.argument("credentials", type=click.File(), nargs=-1)
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
@click.option("--postgres-host", type=str, default="db")
@click.option("--postgres-user", type=str, default="whatupdb")
@click.option("--postgres-password-file", type=click.File(), required=True)
@click.option("--postgres-database", type=str, default="messages")
@click.option(
    "--archive-files",
    type=str,
    default=None,
    help="File glob for archived messages to load. Will load the messages then quit",
)
@click.argument("credentials", type=click.File(), nargs=-1)
@click.pass_context
async def databasebot(
    ctx,
    credentials,
    postgres_host,
    postgres_user,
    postgres_password_file,
    postgres_database,
    archive_files,
):
    # TODO: docstring
    postgres_password = postgres_password_file.read().strip()
    postgres_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_database}"

    params = {"postgres_url": postgres_url, **ctx.obj["connection_params"]}
    if archive_files:
        db = DatabaseBot(connect=False, **params)
        await db.process_archive(archive_files)
        return
    await run_multi_bots(DatabaseBot, credentials, params)


@cli.command("databasebot-load-archive")
@async_cli
@click.option("--postgres-host", type=str, default="db")
@click.option("--postgres-user", type=str, default="whatupdb")
@click.option("--postgres-password-file", type=click.File(), required=True)
@click.option("--postgres-database", type=str, default="messages")
@click.argument(
    "archive-files",
    type=str,
    nargs=-1,
)
@click.pass_context
async def databasebot_load_archive(
    ctx,
    postgres_host,
    postgres_user,
    postgres_password_file,
    postgres_database,
    archive_files,
):
    """
    desc="File glob for archived messages to load. Will load the messages then quit",
    """
    postgres_password = postgres_password_file.read().strip()
    postgres_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_database}"

    params = {"postgres_url": postgres_url, **ctx.obj["connection_params"]}
    db = DatabaseBot(connect=False, **params)
    for archive_file in archive_files:
        await db.process_archive(archive_file)


def main():
    cli(auto_envvar_prefix="WHATUPY")
