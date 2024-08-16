import argparse
import asyncio
import enum
import logging
import os
import random
import shlex
import typing as T
from collections import defaultdict, deque, namedtuple
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import grpc
from cloudpathlib import AnyPath
from google.protobuf.timestamp_pb2 import Timestamp

from .. import utils
from ..connection import create_whatupcore_clients
from ..credentials_manager.credential import Credential
from ..protos import whatsappweb_pb2 as waw
from ..protos import whatupcore_pb2 as wuc
from ..protos.whatupcore_pb2_grpc import WhatUpCoreStub
from .static import format_lang_template

logger = logging.getLogger(__name__)
PinningEntry = namedtuple("PinningEntry", "bot_id expiration_time".split(" "))
ArchiveData = namedtuple(
    "ArchiveData", "WUMessage GroupInfo CommunityInfo MediaPath".split(" ")
)

COMMAND_PINNING_TTL = timedelta(seconds=60 * 60)
COMMAND_PINNING: T.Dict[bytes, PinningEntry] = {}
BOT_REGISTRY = defaultdict(dict)
CONTROL_CACHE = deque(maxlen=1028)

DownloadMediaCallback = T.Callable[
    [wuc.WUMessage, wuc.MediaContent, Exception | None], T.Awaitable[None]
]
MediaType = enum.Enum("MediaType", wuc.SendMessageMedia.MediaType.items())
TypeLanguages = T.Literal["hi"] | T.Literal["en"]


class InvalidCredentialsException(Exception):
    pass


class NotLoggedInException(Exception):
    pass


class StreamMissedHeartbeat(TimeoutError):
    pass


class BotCommandArgsException(Exception):
    def __init__(self, error_msg, help_text, *args, **kwargs):
        self.help_text = help_text
        self.error_msg = error_msg
        super().__init__(*args, **kwargs)

    def message(self):
        if self.error_msg:
            return f"{self.error_msg}\n\n{self.help_text}"
        return self.help_text


class BotCommandArgs(argparse.ArgumentParser):
    def error(self, message):
        help_text = self.format_help()
        raise BotCommandArgsException(message, help_text)

    def exit(self, status=0, message=None):
        help_text = self.format_help()
        raise BotCommandArgsException(message, help_text)


class BaseBot:
    core_client: WhatUpCoreStub

    def __init__(
        self,
        host: str,
        port: int,
        cert: Path,
        *,
        mark_messages_read: bool = False,
        read_messages: bool = True,
        read_historical_messages: bool = False,
        control_groups: T.List[wuc.JID] = [],
        archive_files: T.Optional[str] = None,
        connect: bool = True,
        stream_heartbeat_timeout: int = 10,
        healthcheck_timeout: int = 60,
        logger=logger,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.cert = cert
        self.meta: T.Dict = dict()
        self.logger = logger.getChild(self.__class__.__name__)
        self._stop_on_event: T.Optional[asyncio.Event] = None

        self.username: T.Optional[str] = None
        self.jid: T.Optional[wuc.JID] = None
        self.jid_anon: T.Optional[wuc.JID] = None

        self.control_groups = control_groups
        self.mark_messages_read = mark_messages_read
        self.read_messages = read_messages
        self.read_historical_messages = read_historical_messages
        self.archive_files = archive_files
        self.stream_heartbeat_timeout = stream_heartbeat_timeout
        self.healthcheck_timeout = healthcheck_timeout

        self.download_queue = asyncio.Queue()
        self.download_tasks = set()
        if connect:
            self.core_client, self.authenticator = create_whatupcore_clients(
                self.host, self.port, self.cert
            )
        self.arg_parser = self.setup_command_args()

    def is_prod(self) -> bool:
        return os.environ.get("IS_PROD", "").lower() == "true"

    def setup_command_args(self) -> T.Optional[BotCommandArgs]:
        return None

    async def parse_command(
        self, message: wuc.WUMessage
    ) -> T.Optional[argparse.Namespace]:
        if not self.arg_parser:
            return None
        try:
            text = message.content.text
            (_, *args) = shlex.split(text)
            return self.arg_parser.parse_args(args)
        except BotCommandArgsException as e:
            sender = message.info.source.sender
            await self.send_text_message(sender, e.message())
            return None

    async def login(self, credential: Credential, **kwargs) -> T.Self:
        self.logger = self.logger.getChild(credential.username)
        self.username = credential.username
        self.logger.info("Logging in")
        self.meta.update(dict(credential.meta or {}))
        try:
            await self.authenticator.login(credential.username, credential.passphrase)
        except grpc.aio._call.AioRpcError as e:
            if e.details() == "the store doesn't contain a device JID":
                raise InvalidCredentialsException
            raise e
        connection_status: wuc.ConnectionStatus = (
            await self.core_client.GetConnectionStatus(wuc.ConnectionStatusOptions())
        )
        self.jid = connection_status.JID
        self.jid_anon = connection_status.JIDAnon
        return self

    async def start(self, **kwargs):
        self.logger.info("Starting bot for user")
        BOT_REGISTRY[self.__class__.__name__][id(self)] = self
        self._stop_on_event = asyncio.Event()
        try:
            async with asyncio.TaskGroup() as tg:
                self.logger.info("Starting bot")
                tg.create_task(self.authenticator.start())
                tg.create_task(self._download_messages_background())
                if self.read_messages:
                    tg.create_task(self.listen_messages())
                if self.read_historical_messages:
                    tg.create_task(self.listen_historical_messages())
                tg.create_task(self._connection_healthcheck())
                tg.create_task(self.post_start())
                tg.create_task(self._throw_on_unlock(self._stop_on_event))
        except grpc.aio._call.AioRpcError:
            self.logger.exception("GRPC error in bot main loop: %s")
        except Exception:
            self.logger.exception("Exception in main run loop of bot")
        self.stop()

    async def _connection_healthcheck(self):
        while True:
            # sleep healthcheck_timeout +/- rand(10%)
            await asyncio.sleep(
                self.healthcheck_timeout * (1 + 0.1 * random.uniform(-1, 1))
            )
            conn: wuc.ConnectionStatus = await self.core_client.GetConnectionStatus(
                wuc.ConnectionStatusOptions()
            )
            if not conn.isLoggedIn:
                self.logger.critical("Bot failed health check")
                raise NotLoggedInException
            self.logger.debug("Bot still alive")

    async def _throw_on_unlock(self, cond: asyncio.Event):
        await cond.wait()
        raise Exception("Stopping bot from condition")

    def stop(self):
        if self._stop_on_event is not None:
            self._stop_on_event.set()
        self.logger.critical("Bot Stopping")
        BOT_REGISTRY[self.__class__.__name__].pop(id(self), None)

    async def post_start(self):
        pass

    async def listen_historical_messages(self):
        def stream_factory(last_timestamp):
            return self.core_client.GetPendingHistory(
                wuc.PendingHistoryOptions(
                    heartbeatTimeout=self.stream_heartbeat_timeout,
                    markMessagesRead=self.mark_messages_read,
                )
            )

        def callback(message):
            return self._dispatch_message(message, skip_control=True, is_history=True)

        await self._listen_messages(
            stream_factory, callback, self.logger.getChild("messages")
        )

    async def listen_messages(self):
        def stream_factory(last_timestamp):
            return self.core_client.GetMessages(
                wuc.MessagesOptions(
                    markMessagesRead=self.mark_messages_read,
                    lastMessageTimestamp=last_timestamp,
                    heartbeatTimeout=self.stream_heartbeat_timeout,
                ),
            )

        def callback(message):
            return self._dispatch_message(message)

        await self._listen_messages(
            stream_factory, callback, self.logger.getChild("history")
        )

    async def _listen_messages(
        self,
        stream_factory: T.Callable[[Timestamp | None], grpc.aio.UnaryStreamCall],
        callback: T.Callable[[wuc.WUMessage], T.Any],
        log: logging.Logger,
    ):
        log.info("Reading messages")
        last_timestamp: T.Optional[Timestamp] = None
        backoff = 0
        async with asyncio.TaskGroup() as tg:
            while True:
                messages: grpc.aio.UnaryStreamCall = stream_factory(last_timestamp)
                try:
                    message: wuc.WUMessage
                    async for message in self._read_stream_heartbeat(messages):
                        backoff = 0
                        last_timestamp = message.info.timestamp
                        tg.create_task(callback(message))
                    raise Exception("Message stream ended. Should try to reconnect")
                except StreamMissedHeartbeat:
                    log.info("Missed heartbeat")
                backoff += 1
                sleep_time = min(2**backoff, 60)
                log.info(
                    "Re-triggering after backoff: %ds: sleeping %f",
                    self.stream_heartbeat_timeout,
                    sleep_time,
                )
                await asyncio.sleep(sleep_time)

    async def _read_stream_heartbeat(
        self, stream: grpc.aio.UnaryStreamCall
    ) -> T.AsyncIterator[wuc.WUMessage]:
        while True:
            try:
                message: wuc.MessageStream | grpc.aio.EOF = await asyncio.wait_for(
                    stream.read(),
                    timeout=self.stream_heartbeat_timeout * (1 + 0.05),
                )
                if isinstance(message, grpc.aio._typing.EOFType):
                    return
                elif not message.isHeartbeat:
                    yield message.content
                else:
                    self.logger.debug("Got heartbeat")
            except TimeoutError as e:
                raise StreamMissedHeartbeat from e
            except grpc.aio._call.AioRpcError as e:
                if e.details() == "Stream removed":
                    raise StreamMissedHeartbeat from e
                raise e

    async def _dispatch_message(
        self,
        message: wuc.WUMessage,
        skip_control=False,
        is_history: bool = False,
        is_archive: bool = False,
        archive_data: T.Optional[ArchiveData] = None,
    ):
        now = datetime.now()
        jid_from: wuc.JID = message.info.source.chat
        source_hash = utils.random_hash(message.info.source.sender.user)
        is_control = any(
            utils.same_jid(jid_from, control) for control in self.control_groups
        ) or any(
            source_hash == sa and pb.expiration_time > now
            for sa, pb in COMMAND_PINNING.items()
        )
        self.logger.debug("Got message: %s: %s", jid_from, message.info.id)
        try:
            if is_control:
                message_age = now - message.info.timestamp.ToDatetime()
                if skip_control:
                    self.logger.debug(
                        "Skipping control message: %s: %s",
                        utils.jid_to_str(jid_from),
                        message.info.id,
                    )
                elif message_age > timedelta(seconds=60):
                    self.logger.debug(
                        "Skipping control message because it's >1min old: %s: %s: %s",
                        utils.jid_to_str(jid_from),
                        message.info.id,
                        message_age,
                    )
                else:
                    self.logger.info(
                        "Got control message: %s: %s",
                        utils.jid_to_str(jid_from),
                        message.info.id,
                    )
                    await self._dispatch_control(message, source_hash)
            else:
                self.logger.debug(
                    "Got normal message: %s: %s",
                    utils.jid_to_str(jid_from),
                    message.info.id,
                )
                await self.on_message(
                    message,
                    is_history=is_history,
                    is_archive=is_archive,
                    archive_data=archive_data,
                )
        except grpc.aio._call.AioRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                self.logger.critical("Bot unauthenticated. Disconnecting")
                raise e
            self.logger.exception(
                "Exception handling message... attempting to continue"
            )
        except Exception:
            self.logger.exception(
                "Exception handling message... attempting to continue"
            )

    async def _dispatch_control(self, message, source_hash):
        if message.info.source.isFromMe:
            return
        message_id = message.info.id
        if message_id in CONTROL_CACHE:
            return
        text = message.content.text
        if not text.startswith(f"@{self.__class__.__name__}"):
            return
        pinned_bot = COMMAND_PINNING.get(source_hash)
        registry = BOT_REGISTRY[self.__class__.__name__]
        t = datetime.now()
        new_pin = False
        if (
            pinned_bot is None
            or pinned_bot.bot_id not in registry
            or pinned_bot.expiration_time > t
        ):
            new_pin = True
            idx: int = int(
                message.info.timestamp.ToSeconds()
                // COMMAND_PINNING_TTL.total_seconds()
            ) % len(registry)
            bot_id = list(registry.keys())[idx]
            pinned_bot = PinningEntry(
                bot_id=bot_id, expiration_time=t + COMMAND_PINNING_TTL
            )
            COMMAND_PINNING[source_hash] = pinned_bot
        if id(self) == pinned_bot.bot_id:
            CONTROL_CACHE.append(message_id)
            if new_pin:
                await self.send_text_message(
                    message.info.source.sender,
                    f"In command mode for the next {COMMAND_PINNING_TTL.total_seconds()} seconds. I will respond to commands for the {self.__class__.__name__} bot until {t + COMMAND_PINNING_TTL} UTC",
                )
            return await self.on_control(message)

    async def download_message_media(self, message: wuc.WUMessage) -> wuc.MediaContent:
        # TODO: return bytes here but raise PhotoCop exception on match??
        mm = message.content.mediaMessage
        payload = mm.WhichOneof("payload")
        if payload is None:
            return b""
        media_message = utils.convert_protobuf(waw.Message, mm)
        media_content: wuc.MediaContent = await self.core_client.DownloadMedia(
            wuc.DownloadMediaOptions(
                mediaMessage=media_message,
                info=message.info,
            )
        )
        return media_content

    async def _download_messages_background(self):
        while True:
            message, callback, tries = await self.download_queue.get()
            self.logger.info(
                "Download queue processing message: %s: messages left: %d",
                message.info.id,
                self.download_queue.qsize(),
            )
            content = wuc.MediaContent()
            error = None
            try:
                content = await self.download_message_media(message)
                self.logger.debug(
                    "Got content for message: %s: len(content) = %d",
                    message.info.id,
                    len(content.Body),
                )
            except Exception as e:
                self.logger.exception(
                    "Could not download media content. Retries = %d: %s",
                    tries,
                    message.info.id,
                )
                task = asyncio.create_task(
                    self.download_message_media_eventually(
                        message, callback, tries + 1, error=e
                    )
                )
                self.download_tasks.add(task)
                task.add_done_callback(self.download_tasks.discard)
                error = e

            try:
                self.logger.info(
                    "Media callback: %s: %d: %s",
                    message.info.id,
                    len(content.Body),
                    error or "no error",
                )
                await callback(message, content, error=error)
            except Exception:
                self.logger.exception(
                    "Exception calling download_media_message_eventually callback: %s",
                    message.info.id,
                )

    async def download_message_media_eventually(
        self,
        message: wuc.WUMessage,
        callback: DownloadMediaCallback,
        retries: int = 0,
        error: Exception | None = None,
    ):
        if retries > 5:
            self.logger.info(
                "Out of retries... running callback with empty bytes: %s",
                message.info.id,
            )
            return await callback(
                message,
                b"",
                error or Exception("Ran out of retries trying to get media"),
            )
        elif retries > 0:
            t = min(2**retries, 60 * 60)
            self.logger.info(
                "Retrying media download: %s: %d tries / 5: t = %f",
                message.info.id,
                retries,
                t,
            )
            await asyncio.sleep(t)
        await self.download_queue.put((message, callback, retries))

    async def send_text_message(
        self, recipient: wuc.JID, text: str, composing_time: int = 2, context_info=None
    ) -> wuc.SendMessageReceipt:
        recipient_nonad = utils.jid_noad(recipient)
        message = waw.Message(
            extendedTextMessage=waw.ExtendedTextMessage(
                text=text,
                contextInfo=context_info,
            )
        )
        options = wuc.SendMessageOptions(
            recipient=recipient_nonad, rawMessage=message, composingTime=composing_time
        )
        return await self.core_client.SendMessage(options)

    async def send_raw_message(
        self, recipient: wuc.JID, message: waw.Message, composing_time: int = 2
    ) -> wuc.SendMessageReceipt:
        recipient_nonad = utils.jid_noad(recipient)
        options = wuc.SendMessageOptions(
            recipient=recipient_nonad,
            rawMessage=message,
            composingTime=composing_time,
        )
        return await self.core_client.SendMessage(options)

    async def send_media_message(
        self,
        recipient: wuc.JID,
        media_type: MediaType,
        content: bytes,
        title: T.Optional[str] = None,
        caption: T.Optional[str] = None,
        mimetype: T.Optional[str] = None,
        filename: T.Optional[str] = None,
        composing_time: int = 2,
    ) -> wuc.SendMessageReceipt:
        recipient_nonad = utils.jid_noad(recipient)
        options = wuc.SendMessageOptions(
            recipient=recipient_nonad,
            composingTime=composing_time,
            sendMessageMedia=wuc.SendMessageMedia(
                mediaType=media_type.name,
                caption=caption or "",
                content=content,
                mimetype=mimetype or "",
                title=title or "",
                filename=filename or "",
            ),
        )
        return await self.core_client.SendMessage(options)

    async def on_control(self, message: wuc.WUMessage):
        pass

    async def on_message(
        self,
        message: wuc.WUMessage,
        is_history: bool = False,
        is_archive: bool = False,
        archive_data: T.Optional[ArchiveData] = None,
    ):
        pass

    async def process_archive(self, filenames: T.List[Path]):
        # TODO: this is tightly coupled to ArchiveBot... decouple it somehow
        group_infos = {}
        community_infos = {}
        filenames.sort()
        for filename in filenames:
            try:
                await self._process_archive_file(filename, group_infos, community_infos)
            except Exception:
                self.logger.exception(
                    f"Could not load file: {filename}... trying to continue"
                )

    async def _process_archive_file(
        self,
        filename,
        group_infos: T.Dict[str, wuc.GroupInfo],
        community_infos: T.Dict[str, T.List[wuc.GroupInfo]],
    ):
        self.logger.debug("Loading archive file: %s", filename)
        filename_path = AnyPath(filename)
        with filename_path.open() as fd:
            message: wuc.WUMessage = utils.jsons_to_protobuf(fd.read(), wuc.WUMessage)
        chat_id = utils.jid_to_str(message.info.source.chat)
        metadata = {
            "WUMessage": message,
            "GroupInfo": None,
            "CommunityInfo": None,
            "MediaPath": None,
        }
        if chat_id:
            if group_info_filename := message.provenance.get(
                "archivebot__groupInfoPath"
            ):
                group_info_path = filename_path.parent / group_info_filename
                try:
                    with group_info_path.open() as fd:
                        group_info: wuc.GroupInfo = utils.jsons_to_protobuf(
                            fd.read(), wuc.GroupInfo
                        )
                    metadata["GroupInfo"] = group_info
                    group_infos[chat_id] = group_info
                except FileNotFoundError:
                    self.logger.critical(
                        "Could not find group info in path: %s", group_info_path
                    )
            elif chat_id in group_infos:
                metadata["GroupInfo"] = group_infos[chat_id]

            if community_info_filename := message.provenance.get(
                "archivebot__communityInfoPath"
            ):
                community_info_path = filename_path.parent / community_info_filename
                try:
                    with community_info_path.open() as fd:
                        community_info_list: T.List[wuc.GroupInfo] = (
                            utils.json_list_to_protobuf_list(fd.read(), wuc.GroupInfo)
                        )
                    metadata["CommunityInfo"] = community_info_list
                    community_infos[chat_id] = community_info_list
                except FileNotFoundError:
                    self.logger.critical(
                        "Could not find community info in path: %s", community_info_path
                    )
            elif chat_id in community_infos:
                metadata["CommunityInfo"] = community_infos[chat_id]

        if media_filename := message.provenance.get("archivebot__mediaPath"):
            media_path = filename_path.parent / media_filename
            if media_path.exists():
                metadata["MediaPath"] = media_path
            else:
                self.logger.critical("Could not find media in path: %s", media_path)
        archive_data = ArchiveData(**metadata)
        await self._dispatch_message(
            message,
            is_history=False,
            is_archive=True,
            archive_data=archive_data,
            skip_control=True,
        )

    @asynccontextmanager
    async def with_disappearing_messages(
        self,
        jid: wuc.JID,
        disappearing_time: wuc.DisappearingMessageOptions.DISAPPEARING_TIME.ValueType,
    ):
        jid_noad = utils.jid_noad(jid)
        await self.core_client.SetDisappearingMessageTime(
            wuc.DisappearingMessageOptions(
                recipient=jid_noad, disappearingTime=disappearing_time
            )
        )

        expiration_seconds = 0
        match wuc.DisappearingMessageOptions.DISAPPEARING_TIME.Name(disappearing_time):
            case "TIMER_OFF":
                expiration_seconds = 0
            case "TIMER_24HOUR":
                expiration_seconds = 60 * 60 * 24
            case "TIMER_7DAYS":
                expiration_seconds = 60 * 60 * 24 * 7
            case "TIMER_90DAYS":
                expiration_seconds = 60 * 60 * 24 * 90

        if expiration_seconds:
            context_info = waw.ContextInfo(expiration=expiration_seconds)
        else:
            context_info = waw.ContextInfo()
        yield context_info

        await self.core_client.SetDisappearingMessageTime(
            wuc.DisappearingMessageOptions(
                recipient=jid_noad,
                disappearingTime=wuc.DisappearingMessageOptions.TIMER_OFF,
            )
        )

    async def unregister(self):
        self.logger.warning("Calling unregister")
        self.logger.critical("Calling unregister")
        self.logger.error("Calling unregister")
        await self.core_client.Unregister(wuc.UnregisterOptions)

    async def send_template(
        self,
        jid: wuc.JID,
        template: str,
        lang: TypeLanguages,
        context_info=None,
        antispam=False,
        **kwargs,
    ):
        messages = format_lang_template(template, lang, **kwargs)
        for message in messages:
            message = random.choice(message.split("@@")).strip()
            if antispam:
                message = utils.modify_for_antispam(message)
            await self.send_text_message(
                jid, message.strip(), context_info=context_info
            )
