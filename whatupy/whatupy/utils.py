import asyncio
import mimetypes
import random
import re
import string
import typing as T
import warnings
import hashlib
from functools import wraps

import qrcode
from .protos import whatupcore_pb2 as wuc

WORDLIST_SIZE = None
RANDOM_SALT = random.randbytes(32)


def protobuf_to_dict(proto_obj) -> dict[str, T.Any]:
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    d = {}
    for key in key_list:
        # d[key] = getattr(proto_obj, key)
        obj = getattr(proto_obj, key)
        if hasattr(obj, "DESCRIPTOR"):
            obj = protobuf_to_dict(obj)
        d[key] = obj
    return d


def jid_to_str(jid: wuc.JID) -> str:
    return f"{jid.user}@{jid.server}"


def same_jid(a: wuc.JID, b: wuc.JID) -> bool:
    return a.user == b.user and a.server == b.server


def random_words(n_words=3) -> T.List[str]:
    global WORDLIST_SIZE
    if WORDLIST_SIZE is None:
        with open("/usr/share/dict/words") as fd:
            WORDLIST_SIZE = len(fd.readlines())
    if not WORDLIST_SIZE:
        warnings.warn(
            "Could not use word-list file at /usr/share/dict/words. "
            "Using random ascii letters instead of random words"
        )
        return random.sample(string.ascii_lowercase, 12)
    idxs = [random.randint(0, WORDLIST_SIZE) for _ in range(n_words)]
    idxs.sort()
    words: T.List[str] = []
    with open("/usr/share/dict/words") as fd:
        for i, word in enumerate(fd):
            if i == idxs[len(words)]:
                match = re.search("^[a-zA-Z]+", word)
                if not match:
                    word = "".join(random.sample(string.ascii_lowercase, 4))
                else:
                    word = match[0]
                    words.append(word.strip().lower())
            if len(words) == n_words:
                break
    return words


def random_hash(item: str, iterations=1_000) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", item.encode("utf8"), salt=RANDOM_SALT, iterations=iterations
    )


def async_cli(fxn):
    @wraps(fxn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fxn(*args, **kwargs))

    return wrapper


def mimetype_to_ext(mtype: str) -> str | None:
    if not mimetypes.inited:
        mimetypes.init()
        mimetypes.add_type("image/webp", ".webp")
    return mimetypes.guess_extension(mtype)


def media_message_filename(message) -> str | None:
    # TODO: rewrite
    mid = message.info.id
    for media_type, media in message["message"].items():
        if ext := mimetype_to_ext(media.get("mimetype", "")):
            return f"{mid}_{media_type}{ext}"
    return None


def qrcode_gen(data, version=1) -> str:
    white_block = "\033[0;37;47m  "
    black_block = "\033[0;37;40m  "
    new_line = "\033[0m\n"

    qr = qrcode.QRCode(version, error_correction=qrcode.ERROR_CORRECT_L)
    qr.add_data(data)
    qr.make()
    output = white_block * (qr.modules_count + 2) + new_line
    for mn in qr.modules:
        output += white_block
        for m in mn:
            if m:
                output += black_block
            else:
                output += white_block
        output += white_block + new_line
    output += white_block * (qr.modules_count + 2) + new_line
    return output
