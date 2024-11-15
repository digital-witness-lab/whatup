import typing as T

from google.protobuf.timestamp_pb2 import Timestamp

from ... import utils
from ...protos import whatupcore_pb2 as wuc

IGNORED_FIELDS = set(("originalMessage", "mediaMessage"))


def flatten_proto_message(
    proto_obj,
    preface_keys=False,
    prev_keys: T.Optional[T.Iterable[str]] = None,
    sep="_",
    skip_keys=None,
):
    prev_keys = prev_keys or []
    skip_keys = skip_keys or set()
    flat = {}
    key_list = proto_obj.DESCRIPTOR.fields_by_name.keys()
    key: str
    for key in key_list:
        key_proto = key
        if key_proto in skip_keys:
            continue
        if preface_keys:
            key = sep.join((*prev_keys, key))

        obj: T.Any = getattr(proto_obj, key_proto)
        if isinstance(obj, wuc.JID):
            jid_key = key
            if "jid" not in jid_key.lower():
                jid_key = f"{jid_key}_jid"
            flat[jid_key] = utils.jid_to_str(obj)
            flat[f"{key}_country_iso"] = obj.userGeocode
            continue
        elif isinstance(obj, Timestamp):
            obj = obj.ToDatetime()
        elif hasattr(obj, "items"):
            obj = dict(obj)
        elif hasattr(obj, "append"):
            new_obj = []
            for item in obj:
                if utils.is_filled_pbuf(item):
                    item = flatten_proto_message(
                        item,
                        preface_keys=preface_keys,
                        prev_keys=(*prev_keys, key_proto),
                        sep=sep,
                        skip_keys=skip_keys,
                    )
                elif utils.is_empty_pbuf(item):
                    continue
                if item:
                    new_obj.append(item)
            obj = new_obj
        elif key in IGNORED_FIELDS:
            continue

        if utils.is_filled_pbuf(obj):
            flat.update(
                flatten_proto_message(
                    obj,
                    preface_keys=preface_keys,
                    prev_keys=(*prev_keys, key_proto),
                    sep=sep,
                    skip_keys=skip_keys,
                )
            )
        elif utils.is_empty_pbuf(obj):
            continue
        elif obj:
            flat[key] = obj
    return flat
