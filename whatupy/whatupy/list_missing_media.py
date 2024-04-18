from logging import getLogger
from collections import defaultdict
from datetime import datetime, timedelta
import mimetypes

from dataset import Database, Table
from cloudpathlib import CloudPath

from .bots import DatabaseBot
from .protos import whatupcore_pb2 as wuc
import utils


logger = getLogger(__name__)


class JobStats(defaultdict):
    def __init__(
        self, *args, output_delay: timedelta = timedelta(seconds=60), **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.output_delay = output_delay
        self.start_time = datetime.now()
        self.last_print: datetime = datetime.min

    def ping(self, key):
        self[key] += 1

    def maybe_output(self, print=print):
        now = datetime.now()
        if self.last_print is None or (now - self.last_print) > self.output_delay:
            self.last_print_time = now
            print(self.status())

    def status(self):
        output = ", ".join("{key}={value}" for key, value in self.items())
        running_time = datetime.now() - self.start_time
        return f"JobStats: {running_time}: {output}"


async def find_missing_media(
    db: Database, archive_base_path: CloudPath, media_base_path: CloudPath
):
    mimetypes.init()
    db_media_messages = db.query(
        """
        SELECT
            msg.id,
            msg.chat_jid,
            msg."mediaFilename",
            msg.reciever_jid,
            msg.timestamp,
            msg.provenance,
            media.content_url,
            media."fileExtension",
            media.mimetype
        FROM "messages" AS msg
        LEFT JOIN "media" AS media
            ON msg."mediaFilename" = media.filename
        WHERE
            msg."mediaFilename" IS NOT NULL
    """
    )
    media_table: Table | None = db.get_table("media")
    if media_table is None:
        logger.error("Can't get reference to media table")
        return

    job_stats = JobStats()
    for db_media_message in db_media_messages:
        if db_media_message is None:
            continue

        job_stats.maybe_output(print=logger.info)

        message_id: str | None = db_media_message.get("id")
        media_filename: str | None = db_media_message.get("mediaFilename")
        if not media_filename or not message_id:
            # This should never happen, but checking makes my types checker
            # happy
            continue

        job_stats.ping("db_message")
        chat_jid = db_media_message["chat_jid"]
        conversation_dir: CloudPath = archive_base_path / chat_jid
        archive_media_path = db_media_message["provenance"].get("archivebot__mediaPath")
        file_extension = db_media_message.get("fileExtension")
        content_url = db_media_message.get("content_url")
        mimetype = db_media_message.get("mimetype")
        timestamp = db_media_message.get("timestamp")
        reciever_jid = db_media_message.get("reciever_jid")

        if not archive_media_path:
            job_stats.ping("no_archive_media_path")
            if file_extension and media_filename:
                job_stats.ping("has_extension")
                archive_media_path = f"media/{media_filename}.{file_extension}"
            else:
                proposals = list(
                    (conversation_dir / "media").glob(f"{media_filename}.*")
                )
                if proposals:
                    job_stats.ping("found_w_glob")
                    archive_media_path = str(proposals[0].relative_to(conversation_dir))
                elif timestamp and message_id and reciever_jid:
                    t = int(timestamp.timestamp())
                    archive_file = (
                        conversation_dir / f"{t}_{message_id}_{reciever_jid}.json"
                    )
                    archive_file_old = conversation_dir / f"{t}_{message_id}.json"
                    if archive_file.exists():
                        job_stats.ping("found_archive_file")
                        archive_media_path = _archive_file_media_path(archive_file)
                    elif archive_file_old.exists():
                        job_stats.ping("found_archive_old_file")
                        archive_media_path = _archive_file_media_path(archive_file)
                    else:
                        job_stats.ping("no_archive_file")

        if archive_media_path:
            if not file_extension:
                job_stats.ping("filled_extension")
                file_extension = archive_media_path.split(".", 1)[-1]
            if not mimetype:
                job_stats.ping("filled_mimetype")
                mimetype = mimetypes.types_map.get(file_extension)

            archive_media = conversation_dir / archive_media_path
            archive_media_exists = archive_media.exists()
            if archive_media.exists() and content_url:
                job_stats.ping("has_all")
                continue
            if archive_media_exists and not content_url:
                job_stats.ping("filled_content_url")
                content_url = media_base_path / DatabaseBot.media_url_path(
                    [chat_jid, "media"], media_filename
                )
                archive_media.copy(content_url)
                media_table.upsert(
                    {
                        "content_url": str(content_url),
                        "filename": media_filename,
                        "fileExtension": file_extension,
                        "mimetype": mimetype,
                    },
                    ["filename"],
                )
            elif content_url and not archive_media_exists:
                job_stats.ping("archive_media")
                CloudPath(content_url).copy(archive_media)
            else:
                job_stats.ping("needs_request")
                yield message_id
    logger.info("Finished running: %s", job_stats.status())


def _archive_file_media_path(archive_file: CloudPath) -> str | None:
    message: wuc.WUMessage = utils.jsons_to_protobuf(
        archive_file.read_text(), wuc.WUMessage
    )
    if filename := utils.media_message_filename(message):
        return "media/" + filename
    return None
