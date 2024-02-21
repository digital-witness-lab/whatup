import json
import logging
import typing as T
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path

import grpc
from packaging import version

from .. import utils
from ..protos import whatsappweb_pb2 as waw
from ..protos import whatupcore_pb2 as wuc
from . import BaseBot

logger = logging.getLogger(__name__)


def to_message(mediaMessage: wuc.MediaMessage) -> waw.Message:
    msg = waw.Message()
    msg.ParseFromString(mediaMessage.SerializeToString())
    return msg


class ArchiveBot(BaseBot):
    __version__ = "1.1.0"

    def __init__(
        self,
        archive_dir: Path,
        group_info_refresh_time: timedelta = timedelta(hours=6),
        *args,
        **kwargs,
    ):
        self.archive_dir = archive_dir
        self.group_info_refresh_time = group_info_refresh_time
        kwargs["mark_messages_read"] = True
        kwargs["read_historical_messages"] = True
        self.group_info_last_attempt: T.Dict[str, int]
        super().__init__(*args, **kwargs)

    async def on_message(self, message: wuc.WUMessage, is_history: bool, **kwargs):
        chat_id = utils.jid_to_str(message.info.source.chat)
        if chat_id is None:
            self.logger.critical("Message has no chat_id")
            return
        conversation_dir: Path = self.archive_dir / chat_id
        conversation_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now()

        message_timestamp = message.info.timestamp.ToSeconds()
        message_id = message.info.id
        archive_id = f"{message_timestamp}_{message_id}"
        archive_filename = conversation_dir / f"{archive_id}.json"
        if archive_filename.exists():
            with archive_filename.open() as fd:
                data = json.load(fd)
            if version.parse(
                data["provenance"]["archivebot__version"]
            ) >= version.parse(self.__version__):
                self.logger.debug(
                    "Message already archived.. skipping: %s", archive_filename
                )
                return
            else:
                self.logger.debug(
                    "Re-processing message because of new archive version"
                )
        self.logger.debug("Archiving message to: %s", archive_id)

        provenance = {
            "archivebot__timestamp": now.isoformat(),
            "archivebot__version": self.__version__,
            "archivebot__archiveId": archive_id,
            "archivebot__isHistory": "true" if is_history else "false",
        }
        provenance.update({str(k): str(v) for k, v in self.meta.items()})
        message.provenance.update(provenance)

        refresh_dt = self.group_info_refresh_time.total_seconds()
        timestamp = int((now.timestamp() // refresh_dt) * refresh_dt)

        meta_group_path = (
            conversation_dir / "group-info" / f"group-info_{timestamp}.json"
        )
        meta_community_path = (
            conversation_dir / "community-info" / f"community-info_{timestamp}.json"
        )

        should_check_messages = (
            message.info.source.isGroup
            and not meta_group_path.exists()
            and not meta_community_path.exists()
        )
        if should_check_messages:
            group: wuc.JID = message.info.source.chat
            try:
                group_info: wuc.GroupInfo = await self.core_client.GetGroupInfo(group)
                meta_group_path.parent.mkdir(exist_ok=True, parents=True)
                meta_community_path.parent.mkdir(exist_ok=True, parents=True)

                if utils.jid_to_str(group_info.parentJID) is not None:
                    if (
                        not meta_community_path.exists()
                    ):  # this group is part of a community
                        self.logger.debug(
                            "Processing metadata for community with ID: %s",
                            group_info.parentJID,
                        )
                        try:
                            community_info_iterator: T.AsyncIterator[
                                wuc.GroupInfo
                            ] = self.core_client.GetCommunityInfo(group_info.parentJID)
                            community_info: T.List[
                                wuc.GroupInfo
                            ] = await utils.aiter_to_list(community_info_iterator)
                            for community_group in community_info:
                                community_group.provenance.update(provenance)
                                community_group.provenance[
                                    "archivebot__communityInfoRefreshTime"
                                ] = str(refresh_dt)
                            self.logger.debug("Got metadata for community: %s", chat_id)
                            with meta_community_path.open("w+") as fd:
                                fd.write(utils.protobuf_to_json_list(community_info))
                            message.provenance["archivebot__communityInfoPath"] = str(
                                meta_community_path.relative_to(archive_filename.parent)
                            )
                        except grpc.RpcError:
                            self.logger.exception("Could not get community info")

                elif not meta_group_path.exists():  # this is a standalone group
                    group_info.provenance.update(provenance)
                    group_info.provenance["archivebot__groupInfoRefreshTime"] = str(
                        refresh_dt
                    )
                    self.logger.debug("Got metadata for group: %s", chat_id)
                    with meta_group_path.open("w+") as fd:
                        fd.write(utils.protobuf_to_json(group_info))
                    message.provenance["archivebot__groupInfoPath"] = str(
                        meta_group_path.relative_to(archive_filename.parent)
                    )
            except grpc.RpcError:
                self.logger.exception("Could not get group info")

        if media_filename := utils.media_message_filename(message):
            media_dir: Path = conversation_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            media_path = media_dir / f"{media_filename}"
            message.provenance["archivebot__mediaPath"] = str(
                media_path.relative_to(archive_filename.parent)
            )

            if not media_path.exists():
                callback = partial(
                    self._handle_media_content,
                    media_path=media_path,
                    media_filename=media_filename,
                )
                await self.download_message_media_eventually(message, callback)

        message_dict = utils.protobuf_to_dict(message)
        with archive_filename.open("w+") as fd:
            json.dump(message_dict, fd, cls=utils.WhatUpyJSONEncoder)

    async def _handle_media_content(
        self,
        message: wuc.WUMessage,
        media_bytes: bytes,
        media_path: Path,
        media_filename: str,
    ):
        if not media_bytes:
            self.logger.critical(
                "Empty media body... skipping writing to archive: %s", media_filename
            )
            return
        self.logger.debug("Found media. Saving to %s", media_filename)
        with media_path.open("wb+") as fd:
            fd.write(media_bytes)
