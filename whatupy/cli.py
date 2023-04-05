import json

import click

from .client import WhatUpBase
from .chatbot import ChatBot
from .utils import async_cli


@click.group()
def cli():
    pass


@cli.command()
@async_cli
@click.option("--locator", type=click.File())
@click.option("--friend", multiple=True)
@click.option("--response-time", type=float, default=60, help="Mean response time")
@click.option(
    "--response-time-sigma", type=float, default=15, help="Response time sigma"
)
async def chatbot(locator, response_time, response_time_sigma, friend):
    locator_data: dict | None = None
    if locator:
        locator_data = json.load(locator)
    await ChatBot.start(
        locator_data,
        response_time=response_time,
        response_time_sigma=response_time_sigma,
        friends=friend,
    )


@cli.command()
@async_cli
@click.argument("locator", type=click.File(mode="w+"))
async def create_locator(locator):

    pass


if __name__ == "__main__":
    cli()
