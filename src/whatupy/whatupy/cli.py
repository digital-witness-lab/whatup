import asyncio
import json
import logging
import typing as T
from importlib.resources import files
from pathlib import Path

import click

from .bots import BaseBot, BotType, ArchiveBot, ChatBot, OnboardBot
from .utils import async_cli

FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_CERT = Path(str(files("whatupy").joinpath("whatupcore/static/cert.pem")))


async def run_multi_bots(
    bot: T.Type[BotType], locators: T.List[T.TextIO], bot_args: dict
):
    session_locators: T.List[dict] = []
    for locator in locators:
        try:
            session_locators.append(json.load(locator))
        except ValueError:
            raise Exception(f"Could not parse locator: {locator}")
    async with asyncio.TaskGroup() as tg:
        for session_locator in session_locators:
            coro = bot.start(session_locator=session_locator, **bot_args)
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
@click.option("--port", "-p", type=int, default=3000)
@click.option(
    "--cert",
    type=click.Path(dir_okay=False, exists=True, readable=True, path_type=Path),
    default=DEFAULT_CERT,
)
@click.pass_context
def cli(ctx, debug, host, port, control_groups: list, cert: Path):
    ctx.obj = {"debug": debug}
    if debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    ctx.obj["connection_params"] = {
        "host": host,
        "port": port,
        "cert": cert,
        "control_groups": control_groups,
    }
    logger.info(f"Command Context: {ctx.obj}")


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
@click.argument("locators", type=click.File(), nargs=-1)
@click.pass_context
async def chatbot(ctx, locators, response_time, response_time_sigma, friend):
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
    await run_multi_bots(ChatBot, locators, params)


@cli.command
@async_cli
@click.option(
    "--session-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./sessions/"),
)
@click.argument("name", type=str)
@click.pass_context
async def onboard(ctx, name, session_dir: Path):
    """
    Creates a QR code for provided bot. The command will exit on a sucessful QR
    code scan. The session file will be saved to <session-dir>/<name>.json
    """
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{name}.json"
    await OnboardBot.start(name, session_file, **ctx.obj["connection_params"])


@cli.command()
@async_cli
@click.option(
    "--session-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./sessions/"),
)
@click.pass_context
async def onboard_bulk(ctx, session_dir: Path):
    """
    Starts an interaction to simplify onboarding multiple bots. You will be
    prompted for a name to provide the bot and then be shown a QR code to scan.
    Once the scan is successful, the process will restart so you can onboard
    another bot. The locator file will be saved to the session-dir directory
    with the following format,

        \b
        <session-dir>/
        ├── <bot-name1>.json
        └── <bot-name2>.json
    """
    session_dir.mkdir(parents=True, exist_ok=True)
    while True:
        name: str = click.prompt(
            "Enter name for the next user to be onboarded", type=str
        )
        if not name:
            print("No name provided... exiting.")
            return
        session_file = session_dir / f"{name}.json"
        await OnboardBot.start(name, session_file, **ctx.obj["connection_params"])


@cli.command()
@async_cli
@click.option(
    "--archive-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./archive/"),
)
@click.argument("locators", type=click.File(), nargs=-1)
@click.pass_context
async def archivebot(ctx, locators, archive_dir: Path):
    """
    Bot to archive all the data the provided bots have access to. Give as many
    locators to specify which bots should be listened to. Data gets saved in
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
    await run_multi_bots(ArchiveBot, locators, params)


def main():
    cli(auto_envvar_prefix="WHATUPY")
