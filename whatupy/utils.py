import mimetypes


def is_media_message(message) -> bool:
    return any('mediaKey' in m for m in message['message'].values())


def is_groupchat(message) -> bool:
    return message['key'].get('remoteJid', '').endswith('@g.us')


def mimetype_to_ext(mtype: str) -> str | None:
    if not mimetypes.inited:
        mimetypes.init()
        mimetypes.add_type("image/webp", ".webp")
    return mimetypes.guess_extension(mtype)

def media_message_filename(message) -> str | None:
    mid = message['key']['id']
    for media_type, media in message['message'].items():
        if ext := mimetype_to_ext(media.get('mimetype', '')):
            return f'{mid}_{media_type}{ext}'
    return None
