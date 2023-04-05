import json
import asyncio
import logging
from pathlib import Path
import typing as T

import click

from .chatbot import ChatBot
from .onboardbot import OnboardBot
from .archivebot import ArchiveBot
from .utils import async_cli

FORMAT = f"[%(levelname)s][%(asctime)s][%(name)s] %(module)s:%(funcName)s:%(lineno)d - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


@click.group()
@click.option("--debug/-d", type=bool, is_flag=True, default=False)
def cli(debug):
    if debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)


@cli.command()
@async_cli
@click.option("--locator", type=click.File())
@click.option("--friend", multiple=True)
@click.option("--response-time", type=float, default=60, help="Mean response time")
@click.option(
    "--response-time-sigma", type=float, default=15, help="Response time sigma"
)
async def chatbot(locator, response_time, response_time_sigma, friend):
    session_locator: dict = json.load(locator)
    await ChatBot.start(
        session_locator,
        response_time=response_time,
        response_time_sigma=response_time_sigma,
        friends=friend,
    )


@cli.command
@async_cli
@click.option(
    "--session-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./sessions/"),
)
@click.argument("name", type=str)
async def onboard(name, session_dir: Path):
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{name}.json"
    await OnboardBot.start(name, session_file)


@cli.command()
@async_cli
@click.option(
    "--session-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./sessions/"),
)
async def onboard_bulk(session_dir: Path):
    session_dir.mkdir(parents=True, exist_ok=True)
    while True:
        name: str = click.prompt(
            "Enter name for the next user to be onboarded", type=str
        )
        if not name:
            print("No name provided... exiting.")
            return
        session_file = session_dir / f"{name}.json"
        await OnboardBot.start(name, session_file)


@cli.command()
@async_cli
@click.option("--locator", "locators", type=click.File(), multiple=True)
@click.option(
    "--archive-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("./archive/"),
)
async def archivebot(locators, archive_dir: Path):
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
                archive_dir=archive_dir, session_locator=session_locator
            )
            tg.create_task(coro)


if __name__ == "__main__":
    cli()
