import asyncio
import json
from pathlib import Path
import random

import click

from . import actions
from .client import WhatUpBase
from .utils import is_groupchat, is_media_message, media_message_filename


WORDS = [w.strip() for w in open('/usr/share/dict/american-english-huge')]


class ChatBot(WhatUpBase):
    async def on_connection_ready(self, *args, **kwargs):
        print(f"Subscribing to messages: {args}: {kwargs}")
        await self.emit(actions.read_messages_subscribe)
    
    async def on_read_messages(self, message):
        if message['key']['fromMe'] or is_groupchat(message):
            return

        chatId = message['key']['remoteJid']
        n_words = random.randint(1, 20)
        response = " ".join(random.sample(WORDS, n_words))
        print(f"Sending message: {chatId}: {response}")

        data = {
            'chatId': chatId,
            'message': response,
            'clearChatStatus': True,
            'vampMaxSeconds': 60,
        }
        response = await self.call(actions.write_send_message, data)
        print(f"Response: {response}")
    


async def main(locator):
    print("Opening connection")
    sio = await ChatBot.connect("ws://localhost:3000/", session_locator=locator)
    try:
        print("Waiting")
        await sio.wait()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        await sio.disconnect()


@click.command()
@click.option("--locator", type=click.File())
def cli(locator):
    locator_data = json.load(locator)
    asyncio.run(main(locator_data))


if __name__ == "__main__":
    cli()

