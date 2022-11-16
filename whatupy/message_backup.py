import asyncio
import json
from pathlib import Path

import click

from . import actions
from .client import WhatUpBase
from .utils import is_groupchat, is_media_message, media_message_filename


class MessageBackup(WhatUpBase):
    def __init__(self, *args, data_path: Path | None =None, **kwargs):
        self.data_path = data_path
        super().__init__(*args, **kwargs)

    async def on_connection_ready(self, *args, **kwargs):
        print(f"Subscribing to messages: {args}: {kwargs}")
        await self.emit(actions.read_messages_subscribe)
    
    async def on_read_messages(self, message):
        chatId = message['key']['remoteJid']
        msgId = message['key']['id']
        print(f"Got a message: {chatId}: {msgId}")
    
        archive_path: Path = self.data_path / chatId / f'{msgId}.json'
        archive_path.parent.mkdir(exist_ok=True, parents=True)
        print(f"Archiving to: {archive_path}")
        with archive_path.open('w+') as fd:
            json.dump(message, fd)
        print("Done")
    
        meta_path = archive_path.parent / f'metadata.json'
        if is_groupchat(message) and not meta_path.exists():
            print("Getting metadata")
            metadata = await self.call(actions.read_group_metadata, dict(chatId=chatId))
            with meta_path.open("w+") as fd:
                json.dump(metadata, fd)
            print("Done")
    
        if is_media_message(message):
            media_filename = media_message_filename(message)
            print(f"Downloading media to: {media_filename}")
            media = await self.download_message_media(message)
            media_path: Path = self.data_path / chatId / 'media' / media_filename
            media_path.parent.mkdir(exist_ok=True, parents=True)
            with media_path.open('wb+') as fd:
                fd.write(media)
            print("Done")
        


async def main(locator, data_path):
    print("Opening connection")
    sio = await MessageBackup.connect("ws://localhost:3000/", session_locator=locator, data_path=data_path)
    try:
        print("Waiting")
        await sio.wait()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        await sio.disconnect()


@click.command()
@click.option("--locator", type=click.File())
@click.argument("data_path", type=click.Path(file_okay=False, writable=True, path_type=Path))
def cli(data_path: Path, locator):
    data_path.mkdir(parents=True, exist_ok=True)
    locator_data = json.load(locator)

    asyncio.run(main(locator_data, data_path))


if __name__ == "__main__":
    cli()
