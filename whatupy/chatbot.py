import asyncio
import json
import random
import typing as T

import click

from . import actions
from .client import WhatUpBase
from .utils import is_groupchat


WORDS = [w.strip() for w in open('/usr/share/dict/words')]


class ChatBot(WhatUpBase):
    def __init__(self, *args, response_time: float=60, response_time_sigma: float=15, friends: T.List[str]=[], **kwargs):
        self.response_time = response_time
        self.response_time_sigma = response_time_sigma
        self.pending_messages: T.Dict[str, int] = {}
        self.friends = friends
        super().__init__(*args, **kwargs)

    async def on_connection_ready(self, *args, **kwargs):
        print(f"Subscribing to messages: {args}: {kwargs}")
        await self.messages_subscribe()

        print("Greeting friends")
        for friend in self.friends:
            print(f"Saying hello to: {friend}")
            await self.send_message(friend, self.generate_message())

    def generate_message(self) -> str:
        n_words = random.randint(1, 20)
        return " ".join(random.sample(WORDS, n_words))
    
    async def on_read_messages(self, message):
        if message['key']['fromMe'] or is_groupchat(message):
            return

        chatid: str = message['key']['remoteJid']
        if n_pending := self.pending_messages.get(chatid):
            if random.random() > 1 / n_pending:
                print(f"Not responding to this message... too many queued: {chatid}: {n_pending}")
                return

        response = self.generate_message()
        wait_time = max(1.0, random.normalvariate(self.response_time, self.response_time_sigma))
        print(f"Sending message: {wait_time}seconds: {chatid}: {response}")

        self.pending_messages.setdefault(chatid, 0)
        self.pending_messages[chatid] += 1
        await asyncio.sleep(wait_time)
        self.pending_messages[chatid] -= 1

        status = await self.send_message(chatid, response)
        print(f"Send status: {status}")
    


async def main(locator, **kwargs):
    print("Opening connection")
    sio = await ChatBot.connect("ws://localhost:3000/", session_locator=locator, **kwargs)
    try:
        print("Waiting")
        await sio.wait()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        await sio.disconnect()


@click.command()
@click.option("--locator", type=click.File())
@click.option("--friend", multiple=True)
@click.option("--response-time", type=float, default=60, help="Mean response time")
@click.option("--response-time-sigma", type=float, default=15, help="Response time sigma")
def cli(locator, response_time, response_time_sigma, friend):
    locator_data = json.load(locator)
    asyncio.run(main(locator_data, response_time=response_time, response_time_sigma=response_time_sigma, friends=friend))


if __name__ == "__main__":
    cli()

