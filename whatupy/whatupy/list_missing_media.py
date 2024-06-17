from logging import getLogger
from collections import defaultdict
from datetime import datetime, timedelta
import mimetypes

from dataset import Database, Table
from cloudpathlib import CloudPath

from .bots import DatabaseBot
from .bots.lib import UserBot
from .protos import whatupcore_pb2 as wuc
import utils


logger = getLogger(__name__)


class JobResults(defaultdict):
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
        return f"JobResults: {running_time}: {output}"


async def find_missing_media(
    db: Database,
    user: UserBot,
    archive_base_path: CloudPath,
    media_base_path: CloudPath,
):
    mimetypes.init()
    if not user.jid_anon:
        return None
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
        FROM "donor_messages" AS dm
        INNER JOIN "messages" AS msg
            ON msg.id = dm.message_id
        LEFT JOIN "media" AS media
            ON msg."mediaFilename" = media.filename
        WHERE
            dm.donor_jid = :jid AND
            msg."mediaFilename" IS NOT NULL
        ORDER BY msg.timestamp DESC
    """,
        utils.jid_to_str(user.jid_anon),
    )
    media_table: Table | None = db.get_table("media")
    if media_table is None:
        logger.error("Can't get reference to media table")
        return

    job_results = JobResults()
    # Turn this fxn into a UserGroupJob and add each db_media_messages as a `task`. The result of the process will be the `JobResults` (in CSV?)
    for db_media_message in db_media_messages:
        if db_media_message is None:
            continue

        job_results.maybe_output(print=logger.info)

        message_id: str = db_media_message.get("id")
        media_filename: str = db_media_message.get("mediaFilename")

        job_results.ping("db_message")
        chat_jid = db_media_message["chat_jid"]
        conversation_dir: CloudPath = archive_base_path / chat_jid
        archive_media_path = db_media_message["provenance"].get("archivebot__mediaPath")
        file_extension = db_media_message.get("fileExtension")
        content_url = db_media_message.get("content_url")
        mimetype = db_media_message.get("mimetype")
        timestamp = db_media_message.get("timestamp")
        reciever_jid = db_media_message.get("reciever_jid")
        message_orig: wuc.WUMessage | None = None
        tried_finding_message = False

        if not archive_media_path:
            job_results.ping("no_archive_media_path")
            if file_extension and media_filename:
                job_results.ping("has_extension")
                archive_media_path = f"media/{media_filename}.{file_extension}"
            else:
                proposals = list(
                    (conversation_dir / "media").glob(f"{media_filename}.*")
                )
                if proposals:
                    job_results.ping("found_w_glob")
                    archive_media_path = str(proposals[0].relative_to(conversation_dir))
                elif timestamp and message_id:
                    tried_finding_message = True
                    message_orig = _get_archive_file(
                        conversation_dir,
                        timestamp,
                        message_id,
                        reciever_jid,
                        job_results,
                    )
                    if message_orig and (
                        filename := utils.media_message_filename(message_orig)
                    ):
                        archive_media_path = "media/" + filename
                    else:
                        archive_media_path = None

        if archive_media_path:
            if not file_extension:
                job_results.ping("filled_extension")
                file_extension = archive_media_path.split(".", 1)[-1]
            if not mimetype:
                job_results.ping("filled_mimetype")
                mimetype = mimetypes.types_map.get(file_extension)

            archive_media = conversation_dir / archive_media_path
            archive_media_exists = archive_media.exists()
            if archive_media.exists() and content_url:
                job_results.ping("has_all")
                continue
            if archive_media_exists and not content_url:
                job_results.ping("filled_content_url")
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
                job_results.ping("archive_media")
                CloudPath(content_url).copy(archive_media)
            else:
                if message_orig is None and not tried_finding_message:
                    message_orig = _get_archive_file(
                        conversation_dir,
                        timestamp,
                        message_id,
                        reciever_jid,
                        job_results,
                    )
                if message_orig is None:
                    job_results.ping("no_archive")
                else:
                    job_results.ping("needs_request")
    logger.info("Finished running: %s", job_results.status())


def _get_archive_file(
    conversation_dir, timestamp, message_id, reciever_jid, job_results
) -> wuc.WUMessage | None:
    t = int(timestamp.timestamp())
    archive_file = conversation_dir / f"{t}_{message_id}_{reciever_jid}.json"
    archive_file_old = conversation_dir / f"{t}_{message_id}.json"
    if archive_file.exists():
        job_results.ping("found_archive_file")
        return utils.jsons_to_protobuf(archive_file.read_text(), wuc.WUMessage)
    elif archive_file_old.exists():
        job_results.ping("found_archive_old_file")
        return utils.jsons_to_protobuf(archive_file_old.read_text(), wuc.WUMessage)
    job_results.ping("no_archive_file")
    return None
