import asyncio
import base64
import csv
import glob
import hashlib
import io
import json
import logging
import mimetypes
import random
import re
import string
import sys
import typing as T
import warnings
from collections import namedtuple
from datetime import timedelta
from functools import wraps
from pathlib import Path

import google.auth
import qrcode
from cloudpathlib import AnyPath, CloudPath, GSPath
from google.auth.transport.requests import Request
from google.protobuf.json_format import MessageToDict, ParseDict

from .protos import whatupcore_pb2 as wuc

logger = logging.getLogger(__name__)

WORDLIST_SIZE = None
RANDOM_SALT = random.randbytes(32)

CommandQuery = namedtuple("CommandQuery", "namespace command params".split(" "))
Generic = T.TypeVar("Generic")


def protobuf_fill_fields(proto_obj, skip_keys=None) -> T.Any:
    skip_keys = skip_keys or set()
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    for key in key_list:
        if key in skip_keys:
            continue
        obj = getattr(proto_obj, key)
        if hasattr(obj, "ByteSize"):
            protobuf_fill_fields(obj, skip_keys=skip_keys)
        else:
            t = type(obj)
            print(key, obj, t)
            try:
                fill_value = t(True)
                setattr(proto_obj, key, fill_value)
            except (TypeError, RuntimeError) as e:
                logger.debug("Could not set key in proto: %s: %s: %s", t, key, e)
    return proto_obj


def modify_for_antispam(message: str) -> str:
    identity = lambda x: x

    def random_spaces(group):
        return random.choice([" ", "  "])

    message = random.choice([str.lower, str.title, identity])(message)
    message = re.sub("[ ]+", random_spaces, message)
    h = short_hash(message + str(random.random()))
    message += f" (id: {h})"

    return message


def group_info_hash(group_info: wuc.GroupInfo) -> str:
    data = (
        group_info.createdAt.ToJsonString(),
        group_info.JID.user,
        group_info.JID.server,
        group_info.groupName.updatedAt.ToJsonString(),
        group_info.groupTopic.updatedAt.ToJsonString(),
        group_info.memberAddMode,
        group_info.isLocked,
        group_info.isAnnounce,
        group_info.isEphemeral,
        group_info.disappearingTimer,
        group_info.isCommunity,
        group_info.isCommunityDefaultGroup,
        group_info.isPartialInfo,
        group_info.isIncognito,
        group_info.parentJID.user,
        group_info.parentJID.server,
    )
    h = hashlib.new("sha256")
    for item in data:
        h.update(f"{item}".encode("utf8"))
    return h.hexdigest()[:16]


def gspath_to_self_signed_url(
    path: GSPath | CloudPath | Path, ttl: T.Optional[timedelta]
) -> str:
    if isinstance(path, GSPath):
        try:
            client = path.client.client
            bucket = client.bucket(path.bucket)
            blob = bucket.get_blob(path.blob)
            if blob is not None:
                credentials, project_id = google.auth.default()
                if credentials.token is None:
                    credentials.refresh(Request())
                return blob.generate_signed_url(
                    version="v4",
                    expiration=ttl,
                    service_account_email=credentials.service_account_email,
                    access_token=credentials.token,
                    method="GET",
                )
        except Exception:
            logger.exception("Could not create self signed url")
    return path.as_uri()


def expand_glob(path: CloudPath | Path) -> T.List[CloudPath | Path]:
    if isinstance(path, GSPath):
        for i, p in enumerate(path.parts):
            if "*" in p:
                break
        else:
            return [path]
        base_parts = "gs://" + "/".join(path.parts[1:i])
        glob_parts = "/".join(path.parts[i:])
        base = AnyPath(base_parts)
        return list(base.glob(glob_parts))
    else:
        return [AnyPath(p) for p in glob.glob(str(path))]


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


async def aiter_to_list(aiter: T.AsyncIterable) -> list:
    result = []
    async for item in aiter:
        result.append(item)
    return result


def jid_noad(jid: wuc.JID) -> wuc.JID:
    return wuc.JID(user=jid.user, server=jid.server)


def dict_to_csv_bytes(data: T.List[dict]) -> bytes:
    if not data:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    buffer.seek(0)
    return buffer.read().encode("utf8")


def random_string(length=6):
    return "".join(random.choices(string.ascii_letters, k=length))


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


def protobuf_to_json_list(proto_objs) -> str:
    data = [protobuf_to_dict(proto_obj) for proto_obj in proto_objs]
    return json.dumps(data, cls=WhatUpyJSONEncoder)


def jsons_to_protobuf(jsons: str, proto_type: Generic) -> Generic:
    data = json.loads(jsons, cls=WhatUpyJSONDecoder)
    return ParseDict(data, proto_type(), ignore_unknown_fields=True)


def json_list_to_protobuf_list(jsons: str, proto_type: Generic) -> T.List[Generic]:
    data = json.loads(jsons, cls=WhatUpyJSONDecoder)
    object_list: T.List[Generic] = []
    for item in data:
        item_object = proto_type()
        object_list.append(ParseDict(item, item_object, ignore_unknown_fields=True))
    return object_list


def protobuf_to_dict(proto_obj) -> dict[str, T.Any]:
    return MessageToDict(proto_obj, including_default_value_fields=False)


def jid_to_str(jid: wuc.JID) -> T.Optional[str]:
    if not (jid.user or jid.server):
        return None
    return f"{jid.user}@{jid.server}"


def str_to_jid(sjid: str) -> wuc.JID:
    user, server = sjid.split("@", 1)
    return wuc.JID(user=user, server=server)


def same_jid(a: wuc.JID | None, b: wuc.JID | None) -> bool:
    return (
        (a is not None)
        and (b is not None)
        and a.user == b.user
        and a.server == b.server
    )


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


def short_hash(item: str, N: T.Optional[int] = 5) -> str:
    h = hashlib.new("sha256", item.encode("utf8"))
    return h.hexdigest()[:N]


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


def qrcode_gen_bytes(data, kind="png", version=1) -> bytes:
    qr = qrcode.QRCode(version, error_correction=qrcode.ERROR_CORRECT_L)
    qr.add_data(data)
    img = qr.make_image()

    buffer = io.BytesIO()
    img.save(buffer, kind=kind)
    return buffer.getvalue()


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
