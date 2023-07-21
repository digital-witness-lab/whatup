import asyncio
import base64
import csv
import hashlib
import io
import json
import mimetypes
import random
import re
import string
import typing as T
import warnings
from collections import namedtuple
from functools import wraps

import qrcode
from google.protobuf.json_format import MessageToDict, ParseDict

from .protos import whatupcore_pb2 as wuc

WORDLIST_SIZE = None
RANDOM_SALT = random.randbytes(32)

CommandQuery = namedtuple("CommandQuery", "namespace command params".split(" "))


class WhatUpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return {
                "encoding": "base64_urlsafe",
                "type": "bytes",
                "value": bytes_to_base64(obj),
            }
        return obj


class WhatUpyJSONDecoder(json.JSONDecoder):
    def object_hook(self, dct):
        if "type" in dct and dct["type"] == "bytes":
            return base64_to_bytes(dct)
        return dct


def dict_to_csv_bytes(data: T.List[dict]) -> bytes:
    if not data:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    buffer.seek(0)
    return buffer.read().encode("utf8")


def random_passphrase(words=5):
    words = random_words(words)
    return "-".join(f"{word.title()}{random.randint(10,99)}" for word in words)


def bytes_to_base64(b):
    return base64.urlsafe_b64encode(b).decode("utf8")


def base64_to_bytes(b64: str) -> bytes:
    return base64.urlsafe_b64decode(b64)


def is_pbuf(pbuf_obj) -> bool:
    return hasattr(pbuf_obj, "ByteSize")


def is_filled_pbuf(pbuf_obj):
    return bool(hasattr(pbuf_obj, "ByteSize") and pbuf_obj.ByteSize() > 0)


def is_empty_pbuf(pbuf_obj):
    return bool(hasattr(pbuf_obj, "ByteSize") and pbuf_obj.ByteSize() == 0)


def convert_protobuf(target_type, proto_obj):
    target_keys = set(target_type.DESCRIPTOR.fields_by_name.keys())
    obj_keys = set(proto_obj.DESCRIPTOR.fields_by_name.keys())
    params = {}
    for key in target_keys.intersection(obj_keys):
        value = getattr(proto_obj, key, None)
        if getattr(value, "DESCRIPTOR") and not is_filled_pbuf(value):
            continue
        params[key] = value
    return target_type(**params)


def protobuf_find_key(proto_obj, key_name) -> T.Any:
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    for key in key_list:
        obj = getattr(proto_obj, key)
        if key == key_name:
            return obj
        if is_filled_pbuf(obj):
            result = protobuf_find_key(obj, key_name)
            if result:
                return result
    return None


def protobuf_to_json(proto_obj) -> str:
    data = protobuf_to_dict(proto_obj)
    return json.dumps(data, cls=WhatUpyJSONEncoder)


def jsons_to_protobuf(jsons, proto_type):
    data = json.loads(jsons, cls=WhatUpyJSONDecoder)
    return ParseDict(data, proto_type)


def protobuf_to_dict(proto_obj) -> dict[str, T.Any]:
    return MessageToDict(proto_obj, including_default_value_fields=False)


def jid_to_str(jid: wuc.JID) -> T.Optional[str]:
    if not (jid.user or jid.server):
        return None
    return f"{jid.user}@{jid.server}"


def str_to_jid(sjid: str) -> wuc.JID:
    user, server = sjid.split("@", 1)
    return wuc.JID(user=user, server=server)


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


def mime_type_to_ext(mtype: str) -> str | None:
    if not mimetypes.inited:
        mimetypes.init()
        mimetypes.add_type("image/webp", ".webp")
    return mimetypes.guess_extension(mtype)


def media_message_mimetype(message: wuc.WUMessage) -> str | None:
    payload = message.content.mediaMessage.WhichOneof("payload")
    if payload is None:
        return None
    media = getattr(message.content.mediaMessage, payload)
    try:
        return media.mimetype
    except AttributeError:
        pass
    return None


def media_message_filename(message: wuc.WUMessage) -> str | None:
    payload = message.content.mediaMessage.WhichOneof("payload")
    if payload is None:
        return None
    media = getattr(message.content.mediaMessage, payload)
    try:
        fileShaBytes = media.fileSha256
        mime_type = media.mimetype
    except AttributeError:
        return None
    fileSha: str = bytes_to_base64(fileShaBytes)
    if ext := mime_type_to_ext(mime_type or ""):
        return f"{fileSha}{ext}"
    return f"{fileSha}.unk"


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
