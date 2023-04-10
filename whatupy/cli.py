import asyncio
import json
import logging
import typing as T
from importlib.resources import files
from pathlib import Path

import click

from .bots import ArchiveBot, ChatBot, OnboardBot
from .utils import async_cli

FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
DEFAULT_CERT = Path(str(files("whatupy").joinpath("whatupcore/static/cert.pem")))


@click.group()
@click.option("--debug", "-d", type=bool, is_flag=True, default=False)
@click.option("--host", "-H", type=str, default="localhost")
@click.option("--port", "-p", type=int, default=3000)
@click.option(
    "--cert",
    type=click.Path(dir_okay=False, exists=True, readable=True, path_type=Path),
    default=DEFAULT_CERT,
)
@click.pass_context
def cli(ctx, debug, host, port, cert: Path):
    ctx.obj = {"debug": debug}
    if debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    ctx.obj["connection_params"] = {"host": host, "port": port, "cert": cert}


@cli.command()
@async_cli
@click.option("--locator", type=click.File())
@click.option("--friend", multiple=True)
@click.option("--response-time", type=float, default=60, help="Mean response time")
@click.option(
    "--response-time-sigma", type=float, default=15, help="Response time sigma"
)
@click.pass_context
async def chatbot(ctx, locator, response_time, response_time_sigma, friend):
    session_locator: dict = json.load(locator)
    await ChatBot.start(
        session_locator,
        response_time=response_time,
        response_time_sigma=response_time_sigma,
        friends=friend,
        **ctx.obj["connection_params"],
    )


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
    archive_dir.mkdir(parents=True, exist_ok=True)
    session_locators: T.List[dict] = []
    for locator in locators:
        try:
            session_locators.append(json.load(locator))
        except ValueError:
            raise Exception(f"Could not parse locator: {locator}")
    async with asyncio.TaskGroup() as tg:
        for session_locator in session_locators:
            coro = ArchiveBot.start(
                archive_dir=archive_dir,
                session_locator=session_locator,
                **ctx.obj["connection_params"],
            )
            tg.create_task(coro)


if __name__ == "__main__":
    cli()
